# Habit Tracker API (FastAPI + SQLAlchemy + PyTest)

Local-only setup instructions are in the chat. Use this README if you want a quick reference:

## Quickstart
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## Tests
```bash
pytest -q
```