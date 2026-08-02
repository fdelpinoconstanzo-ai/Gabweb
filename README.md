# Conversaciones locales de GitHub Copilot

Aplicacion web local para consultar todas las sesiones guardadas por GitHub
Copilot CLI. La base `~/.copilot/session-store.db` se abre siempre en modo de
solo lectura.

## Ejecutar

Requiere Python 3.10 o posterior y no usa dependencias externas.

```bash
python3 app.py
```

Abre <http://127.0.0.1:8000>. Puedes indicar otra base o puerto:

```bash
python3 app.py --db /ruta/session-store.db --port 8080
```

## Pruebas

```bash
python3 -m unittest discover -s tests -v
```