# Habit Tracker API (FastAPI · SQLAlchemy 2.0 · PyTest)

An intermediate **REST API** that lets you create habits, record daily logs, compute streaks, and enrich responses with a motivational quote from an **external REST service**—fully covered by a modern **pytest** suite (with async tests and mocked HTTP).

runs locally using venv at http://127.0.0.1:8000/docs#/habits/create_habit_habits_post
Open the interactive docs: http://127.0.0.1:8000/docs
---

## TL;DR
- FastAPI habit-tracking REST API: create habits, add daily logs, compute streaks; enrich responses with an external quotes API.
- Stack: FastAPI, SQLAlchemy 2.0 (SQLite), Pydantic v2, httpx; tests with pytest, pytest-asyncio, respx (HTTP mocking).
- Run: `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`) → `pip install -r requirements.txt` → `uvicorn app.main:app --reload`.
- Docs: Open **http://127.0.0.1:8000/docs**; core endpoints include `/habits`, `/habits/{id}/logs`, `/habits/{id}/stats`, `/health`.
- Test: `pytest -q` (uses in-memory SQLite and mocked external HTTP).


## Table of Contents
- [Why This Project Matters](#why-this-project-matters)
- [Quickstart](#quickstart)
- [Architecture at a Glance](#architecture-at-a-glance)
- [Data Model](#data-model)
- [API Reference](#api-reference)
- [External Integration (httpx)](#external-integration-httpx)
- [Streak Algorithm (Business Logic)](#streak-algorithm-business-logic)
- [Testing Strategy (pytest)](#testing-strategy-pytest)
- [Design Choices & Trade-offs](#design-choices--trade-offs)
- [Extending the Project](#extending-the-project)
- [Requirements](#requirements)
- [License](#license)

---

## Why This Project Matters

**What a recruiter should notice:**
- **Clean architecture & typing**: FastAPI routers, Pydantic v2 schemas, SQLAlchemy 2.0 models, strong type hints.
- **Real-world constraints**: DB-level uniqueness (one log per day per habit) surfaced as proper HTTP **409** errors.
- **Async integration**: Calls an external API (`quotable.io`) via **httpx**; resilient to network failures.
- **Testability**: Dependency injection for DB sessions; **in-memory SQLite** during tests; **respx** to mock HTTP.
- **Maintainability**: Clear separation of concerns (routers ↔ schemas ↔ models ↔ external client), app factory, small surface area.

---

## Quickstart

bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload



Open the interactive docs: http://127.0.0.1:8000/docs

here onward, chat gpt was used to make the read me
## Run tests:

pytest -q

## Architecture at a Glance

Stack: FastAPI, SQLAlchemy 2.0 (SQLite), Pydantic v2, httpx, pytest, pytest-asyncio, respx

Structure

app/
  main.py            # app factory, router registration
  database.py        # engine, session factory, Base, init_db, DI session provider
  models.py          # SQLAlchemy models: Habit, HabitLog (+ unique constraints)
  schemas.py         # Pydantic v2 schemas (from_attributes=True)
  external.py        # httpx client for external quote API
  routers/
    habits.py        # REST endpoints for habits, logs, stats
tests/
  test_habits.py     # async API tests with in-memory DB & mocked HTTP

## Data Model

Entities

Habit

id, name (unique), description, created_at

HabitLog

id, habit_id, log_date

Unique: (habit_id, log_date) → one log per day per habit

Relationship

Habit 1 ─── * HabitLog

## API Reference
Method	Path	Purpose	Status codes
GET	/health	Liveness check	200
POST	/habits	Create a habit (+ external quote)	201 Created, 409
GET	/habits	List habits	200
GET	/habits/{habit_id}	Get a habit by id	200, 404
POST	/habits/{habit_id}/logs	Add a daily log (date optional)	201, 404, 409
GET	/habits/{habit_id}/stats	Streak stats (current/longest)	200, 404

Example — create a habit

curl -s -X POST http://127.0.0.1:8000/habits \
  -H "Content-Type: application/json" \
  -d '{"name":"Workout","description":"30 mins daily"}'


Response (201)

{
  "id": 1,
  "name": "Workout",
  "description": "30 mins daily",
  "created_at": "2025-08-27T01:23:45.123456",
  "motivational_quote": "Stay consistent."
}


Add today’s log

curl -s -X POST http://127.0.0.1:8000/habits/1/logs \
  -H "Content-Type: application/json" \
  -d '{"log_date":"2025-08-27"}'


Get streak stats

curl -s http://127.0.0.1:8000/habits/1/stats

## External Integration (httpx)

POST /habits calls https://api.quotable.io/random using httpx (async).

Failures/timeouts don’t break habit creation; the quote field becomes null.

Demonstrates async I/O, fault tolerance, and response enrichment.

# app/external.py (excerpt)
async def fetch_motivational_quote(timeout: float = 5.0) -> str | None:
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get("https://api.quotable.io/random")
        if r.status_code == 200:
            return r.json().get("content")
    return None

## Streak Algorithm (Business Logic)

Pull all logs for a habit, ordered by date.

Compute:

current streak: contiguous run ending at the last logged day,

longest streak: maximum contiguous run overall.

Linear-time scan (O(n)), leveraging DB sort for efficiency.

## Testing Strategy (pytest)

Goals covered

Validate REST interface (status codes, JSON contracts).

Verify DB behavior (unique constraints → 409 conflicts).

Exercise business logic (streaks).

Mock external HTTP for speed & determinism.

Techniques used

App in memory: httpx.ASGITransport calls FastAPI directly (no network).

Isolated DB: sqlite:///:memory: with dependency override of get_session.

Mocked HTTP: respx intercepts quote API calls.

Async tests: pytest-asyncio.

# tests/test_habits.py (snippets)

# Override DB dependency to use in-memory SQLite
test_app.dependency_overrides[get_session] = _override_get_session

# Mock the external REST call
@respx.mock
async def test_create_habit_fetches_quote(client):
    respx.get("https://api.quotable.io/random").mock(
        return_value=httpx.Response(200, json={"content": "Stay consistent."})
    )

## Design Choices & Trade-offs

SQLite for portability; easily swapped to Postgres by changing DATABASE_URL.

DB constraints enforce correctness; API maps DB errors to HTTP semantics (e.g., 409 Conflict).

Pydantic v2 (from_attributes=True) keeps schemas/ORM in sync without boilerplate.

App factory + DI simplify testing and future extension.

No auth (kept focused). JWT can be added behind a dependency.

## Extending the Project

Auth: JWT/OAuth2 with per-user habit ownership.

Full CRUD: PUT/PATCH/DELETE for habits and logs.

Query features: pagination, filtering, search on /habits.

Background jobs: reminders or summaries (APScheduler/Celery).

Observability: structured logging, metrics, tracing.

CI/CD: GitHub Actions to run tests on push/PR; add coverage badge.

## Requirements

Python 3.10–3.12

See requirements.txt for libraries:

fastapi, uvicorn[standard], sqlalchemy, httpx, pydantic

pytest, pytest-asyncio, respx
