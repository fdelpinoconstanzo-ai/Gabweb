import json
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen
from unittest.mock import patch

from app import ConversationStore, create_server


SCHEMA = """
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    cwd TEXT,
    repository TEXT,
    host_type TEXT,
    branch TEXT,
    summary TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE TABLE turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    turn_index INTEGER NOT NULL,
    user_message TEXT,
    assistant_response TEXT,
    timestamp TEXT
);
"""


class ConversationStoreTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temporary_directory.name) / "sessions.db"
        connection = sqlite3.connect(self.db_path)
        connection.executescript(SCHEMA)
        connection.executemany(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    "new",
                    "/tmp/new",
                    "owner/new",
                    "cli",
                    "feature",
                    "Sesión reciente",
                    "2026-08-02 10:00:00",
                    "2026-08-02 11:00:00",
                ),
                (
                    "old",
                    "/tmp/old",
                    "owner/old",
                    "cli",
                    "main",
                    None,
                    "2026-08-01 10:00:00",
                    "2026-08-01 11:00:00",
                ),
            ],
        )
        connection.executemany(
            """
            INSERT INTO turns (session_id, turn_index, user_message, assistant_response, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("new", 0, "Busca autenticación", "Revisé el login", "2026-08-02 10:01:00"),
                ("new", 1, "Corrige la prueba", "Prueba corregida", "2026-08-02 10:02:00"),
                ("old", 0, "Hola", "Hola", "2026-08-01 10:01:00"),
            ],
        )
        connection.commit()
        connection.close()
        self.store = ConversationStore(self.db_path)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_lists_every_session_with_turn_count(self):
        conversations = self.store.list_conversations()
        self.assertEqual(["new", "old"], [item["id"] for item in conversations])
        self.assertEqual(2, conversations[0]["turn_count"])

    def test_searches_messages_and_treats_wildcards_as_text(self):
        self.assertEqual("new", self.store.list_conversations("autenticación")[0]["id"])
        self.assertEqual([], self.store.list_conversations("%"))

    def test_returns_turns_in_order(self):
        conversation = self.store.get_conversation("new")
        self.assertEqual([0, 1], [turn["turn_index"] for turn in conversation["turns"]])
        self.assertIsNone(self.store.get_conversation("missing"))


class ConversationsApiTest(ConversationStoreTest):
    def setUp(self):
        super().setUp()
        self.server = create_server("127.0.0.1", 0, self.db_path)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        super().tearDown()

    def get_json(self, path):
        with urlopen(f"{self.base_url}{path}") as response:
            return json.load(response)

    def test_lists_and_filters_conversations(self):
        payload = self.get_json("/api/conversations?q=login")
        self.assertEqual(["new"], [item["id"] for item in payload["conversations"]])

    def test_returns_conversation_detail_and_not_found(self):
        payload = self.get_json("/api/conversations/new")
        self.assertEqual(2, len(payload["conversation"]["turns"]))
        with self.assertRaises(HTTPError) as error:
            self.get_json("/api/conversations/missing")
        self.assertEqual(404, error.exception.code)
        error.exception.close()

    def test_serves_the_web_application(self):
        with urlopen(f"{self.base_url}/") as response:
            page = response.read().decode("utf-8")
        self.assertIn("Tus conversaciones", page)

    def test_static_read_error_returns_500_without_stopping_server(self):
        with patch("app.Path.read_bytes", side_effect=PermissionError("sin permiso")):
            with self.assertRaises(HTTPError) as error:
                self.get_json("/")
            self.assertEqual(500, error.exception.code)
            error.exception.close()

        payload = self.get_json("/api/conversations")
        self.assertEqual(2, len(payload["conversations"]))


class MissingDatabaseApiTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temporary_directory.name) / "private" / "sessions.db"
        self.server = create_server("127.0.0.1", 0, self.db_path)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/api/conversations"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temporary_directory.cleanup()

    def test_missing_database_response_does_not_expose_its_path(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(self.url)
        body = json.load(error.exception)
        self.assertEqual(503, error.exception.code)
        self.assertEqual("No se encontró la base de datos de Copilot.", body["error"])
        self.assertNotIn(str(self.db_path), body["error"])
        error.exception.close()


if __name__ == "__main__":
    unittest.main()
