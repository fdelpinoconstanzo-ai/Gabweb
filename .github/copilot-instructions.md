# Copilot cloud agent instructions

## Repository overview

This is a small, dependency-free photography portfolio plus a local web
application for browsing and searching conversations saved by GitHub Copilot
CLI. Both UIs are Spanish. The portfolio is plain HTML/CSS/JavaScript suitable
for GitHub Pages. The conversation browser uses a Python standard-library
backend and a separate vanilla frontend. The target runtime for that tool is
Python 3.10 or newer (validated with Python 3.14.5).

The application reads `~/.copilot/session-store.db` as SQLite in **read-only**
mode. That private database exists on a user's machine but normally does not
exist on a cloud runner. Tests create an isolated compatible database, so they
do not require Copilot data or network access.

## Bootstrap, build, test, and run

There are no third-party dependencies, package manifests, generated files, or
bootstrap steps. Do not run `pip install`, `npm install`, or npm build commands.
Node is not part of the toolchain and both frontends are served as source
files.

Always validate changes from the repository root in this order:

```bash
python3 --version
python3 -m py_compile app.py tests/test_app.py
python3 -m unittest discover -s tests -v
git diff --check
```

`py_compile` takes under one second. The complete suite currently contains 9
tests and takes about 3 seconds. It exercises store queries, literal wildcard
search, ordering, API list/detail/404 responses, and serving the HTML entry
point. Tests may run before compilation and need no setup, but use the sequence
above before check-in. There is no configured formatter, linter, type checker,
GitHub Actions workflow, or other CI pipeline; do not invent a substitute.

Run locally with:

```bash
python3 app.py
# Then open http://127.0.0.1:8000
```

Useful options are shown by `python3 app.py --help`:

```bash
python3 app.py --db /path/to/session-store.db --port 8001
```

The default server can start without a database, but the first API request
returns HTTP 503 if `~/.copilot/session-store.db` is absent. This is expected on
a cloud runner, not a build failure; use the test suite for cloud validation.
If port 8000 is occupied, select another port. Keep the default
`127.0.0.1` binding: `--host 0.0.0.0` exposes private conversation content to
the local network and should be used only when explicitly requested.

## Architecture and layout

- `index.html`, `about.html`, `contact.html`, and `project.html` are the
  portfolio pages deployed directly as static files.
- `css/style.css` contains all portfolio styles; `js/main.js` contains its
  navigation and filtering behavior. Keep selectors synchronized with all
  portfolio pages.
- `app.py` is the complete conversation-browser backend and entry point.
  - `ConversationStore` opens SQLite with URI `mode=ro`, escapes user search
    wildcards, uses parameterized SQL, and maps rows to dictionaries.
  - The expected database has `sessions` and `turns` tables. Session fields
    used are `id`, `cwd`, `repository`, `host_type`, `branch`, `summary`,
    `created_at`, and `updated_at`. Turn fields used are `id`, `session_id`,
    `turn_index`, `user_message`, `assistant_response`, and `timestamp`.
  - `ConversationsHandler` provides `GET /api/conversations?q=...`,
    `GET /api/conversations/{session_id}`, and static files. Preserve JSON
    `no-store`, path traversal checks, explicit 400/404/503 responses, and the
    read-only database invariant.
  - `create_server()` is the test seam; `main()` parses `--host`, `--port`, and
    `--db` and starts `ThreadingHTTPServer`.
- `static/index.html` contains the responsive Spanish conversation-browser UI
  and reusable list/turn templates.
- `static/app.js` fetches both API endpoints, debounces search, renders session
  details, and inserts all database content with `textContent`. Never replace
  this with unescaped `innerHTML`, because conversation text is untrusted.
- `static/styles.css` contains all styling and the mobile breakpoint at 760px.
  There is no CSS preprocessor.
- `tests/test_app.py` uses `unittest`, a temporary SQLite database, and an
  ephemeral HTTP port. Extend its `SCHEMA` fixture when backend queries require
  new columns. Always shut down and close test servers and HTTP responses.
- `README.md` documents the user-facing purpose, Python requirement, run
  command, database override, and test command.
- `.gitignore` excludes Python bytecode and `__pycache__`.

The repository has no `CONTRIBUTING.md`, dependency file, build configuration,
or workflow under `.github/workflows/`. Root source files include the four
portfolio HTML pages, `app.py`, `README.md`, and `.gitignore`; implementation
subdirectories are `css/`, `js/`, `static/`, and `tests/`.

Keep changes dependency-free unless a requirement truly cannot be met with the
standard library. Preserve Spanish user-visible copy and test API changes at
both the store and HTTP layers. For portfolio changes, manually open the root
HTML pages and check navigation and filtering at desktop and mobile widths. For
conversation frontend changes, run the full suite and manually inspect the page
with a compatible local database when available.

Trust these instructions first. Search the repository only when the requested
work is not covered here or when these instructions are demonstrably outdated.
