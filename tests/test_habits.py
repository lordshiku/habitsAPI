import asyncio
from datetime import date, timedelta
import pytest
import httpx
import respx
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import create_app
from app.database import Base, get_session

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_app() -> FastAPI:
    app = create_app()
    return app

@pytest.fixture
def test_db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()

@pytest.fixture
def client(test_app: FastAPI, test_db_session):
    def _override_get_session():
        try:
            yield test_db_session
        finally:
            pass

    test_app.dependency_overrides[get_session] = _override_get_session
    transport = httpx.ASGITransport(app=test_app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")

@pytest.mark.asyncio
async def test_health(client: httpx.AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.mark.asyncio
@respx.mock
async def test_create_habit_fetches_quote(client: httpx.AsyncClient):
    respx.get("https://api.quotable.io/random").mock(
        return_value=httpx.Response(200, json={"content": "Stay consistent."})
    )
    payload = {"name": "Workout", "description": "30 minutes daily"}
    r = await client.post("/habits", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Workout"
    assert "motivational_quote" in data
    assert data["motivational_quote"] == "Stay consistent."

@pytest.mark.asyncio
async def test_create_duplicate_habit_fails(client: httpx.AsyncClient):
    payload = {"name": "Read", "description": "Read 10 pages"}
    r1 = await client.post("/habits", json=payload)
    assert r1.status_code == 201
    r2 = await client.post("/habits", json=payload)
    assert r2.status_code == 409

@pytest.mark.asyncio
async def test_add_logs_and_stats(client: httpx.AsyncClient):
    r = await client.post("/habits", json={"name": "Meditate"})
    habit_id = r.json()["id"]

    today = date.today()
    for d in [today - timedelta(days=2), today - timedelta(days=1), today]:
        resp = await client.post(f"/habits/{habit_id}/logs", json={"log_date": d.isoformat()})
        assert resp.status_code == 201

    stats = await client.get(f"/habits/{habit_id}/stats")
    assert stats.status_code == 200
    s = stats.json()
    assert s["total_days"] == 3
    assert s["streak_current"] == 3
    assert s["streak_longest"] >= 3

@pytest.mark.asyncio
async def test_unique_log_per_day(client: httpx.AsyncClient):
    r = await client.post("/habits", json={"name": "Journal"})
    habit_id = r.json()["id"]
    payload = {"log_date": date.today().isoformat()}
    first = await client.post(f"/habits/{habit_id}/logs", json=payload)
    assert first.status_code == 201
    dup = await client.post(f"/habits/{habit_id}/logs", json=payload)
    assert dup.status_code == 409