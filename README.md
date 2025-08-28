# Habit Tracker API (FastAPI · SQLAlchemy 2.0 · PyTest)

An intermediate **REST API** that lets you create habits, record daily logs, compute streaks, and enrich responses with a motivational quote from an **external REST service**—fully covered by a modern **pytest** suite (with async tests and mocked HTTP).

---

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

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
