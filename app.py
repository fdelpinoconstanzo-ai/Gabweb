#!/usr/bin/env python3
import argparse
import json
import mimetypes
import sqlite3
from contextlib import closing
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse


DEFAULT_DB_PATH = Path.home() / ".copilot" / "session-store.db"
STATIC_DIR = Path(__file__).resolve().parent / "static"


class ConversationStore:
    def __init__(self, db_path):
        self.db_path = Path(db_path).expanduser().resolve()

    def _connect(self):
        if not self.db_path.is_file():
            raise FileNotFoundError("No se encontró la base de datos de Copilot.")
        uri = f"file:{quote(self.db_path.as_posix(), safe='/')}?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _search_pattern(value):
        escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        return f"%{escaped}%"

    def list_conversations(self, search=""):
        parameters = {}
        search_clause = ""
        if search:
            parameters["search"] = self._search_pattern(search)
            search_clause = """
                WHERE COALESCE(s.summary, '') LIKE :search ESCAPE '\\' COLLATE NOCASE
                   OR COALESCE(s.repository, '') LIKE :search ESCAPE '\\' COLLATE NOCASE
                   OR COALESCE(s.cwd, '') LIKE :search ESCAPE '\\' COLLATE NOCASE
                   OR EXISTS (
                       SELECT 1
                       FROM turns searched_turn
                       WHERE searched_turn.session_id = s.id
                         AND (
                             COALESCE(searched_turn.user_message, '')
                                 LIKE :search ESCAPE '\\' COLLATE NOCASE
                             OR COALESCE(searched_turn.assistant_response, '')
                                 LIKE :search ESCAPE '\\' COLLATE NOCASE
                         )
                   )
            """

        query = f"""
            SELECT
                s.id,
                s.cwd,
                s.repository,
                s.host_type,
                s.branch,
                s.summary,
                s.created_at,
                s.updated_at,
                COUNT(t.id) AS turn_count
            FROM sessions s
            LEFT JOIN turns t ON t.session_id = s.id
            {search_clause}
            GROUP BY s.id
            ORDER BY COALESCE(s.updated_at, s.created_at) DESC, s.id
        """
        with closing(self._connect()) as connection:
            return [dict(row) for row in connection.execute(query, parameters)]

    def get_conversation(self, session_id):
        with closing(self._connect()) as connection:
            session = connection.execute(
                """
                SELECT id, cwd, repository, host_type, branch, summary, created_at, updated_at
                FROM sessions
                WHERE id = ?
                """,
                (session_id,),
            ).fetchone()
            if session is None:
                return None

            turns = connection.execute(
                """
                SELECT turn_index, user_message, assistant_response, timestamp
                FROM turns
                WHERE session_id = ?
                ORDER BY turn_index
                """,
                (session_id,),
            ).fetchall()

        result = dict(session)
        result["turns"] = [dict(turn) for turn in turns]
        return result


class ConversationsHandler(BaseHTTPRequestHandler):
    store = None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/conversations":
            search = parse_qs(parsed.query).get("q", [""])[0].strip()
            self._serve_json({"conversations": self.store.list_conversations(search)})
            return

        prefix = "/api/conversations/"
        if parsed.path.startswith(prefix):
            session_id = unquote(parsed.path[len(prefix) :])
            if not session_id or "/" in session_id:
                self._serve_json({"error": "Identificador inválido"}, HTTPStatus.BAD_REQUEST)
                return
            conversation = self.store.get_conversation(session_id)
            if conversation is None:
                self._serve_json({"error": "Conversación no encontrada"}, HTTPStatus.NOT_FOUND)
                return
            self._serve_json({"conversation": conversation})
            return

        self._serve_static(parsed.path)

    def _serve_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, request_path):
        relative_path = "index.html" if request_path == "/" else unquote(request_path.lstrip("/"))
        candidate = (STATIC_DIR / relative_path).resolve()
        if STATIC_DIR not in candidate.parents or not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            body = candidate.read_bytes()
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        except OSError as error:
            self.log_error("No se pudo leer el archivo estático %s: %s", candidate, error)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, message, *args):
        print(f"{self.address_string()} - {message % args}")

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (FileNotFoundError, sqlite3.Error) as error:
            if not self.wfile.closed:
                self._serve_json({"error": str(error)}, HTTPStatus.SERVICE_UNAVAILABLE)


def create_server(host, port, db_path):
    handler = type(
        "ConfiguredConversationsHandler",
        (ConversationsHandler,),
        {"store": ConversationStore(db_path)},
    )
    return ThreadingHTTPServer((host, port), handler)


def main():
    parser = argparse.ArgumentParser(
        description="Explora las conversaciones locales de GitHub Copilot."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH))
    args = parser.parse_args()

    server = create_server(args.host, args.port, args.db)
    print(f"Conversaciones disponibles en http://{args.host}:{server.server_port}")
    print(f"Leyendo en modo solo lectura: {Path(args.db).expanduser()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
