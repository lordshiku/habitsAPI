from __future__ import annotations
from fastapi import FastAPI
from .database import init_db
from .routers import habits

def create_app() -> FastAPI:
    app = FastAPI(title="Habit Tracker API", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(habits.router)
    return app

# create tables on startup (simple approach for demo)
init_db()
app = create_app()