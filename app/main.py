from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import Resource
from app.routers import bookings, resources

DEMO_RESOURCES = ["Apartment 1", "Apartment 2", "Studio by the beach"]
INDEX_HTML = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")


def init_db() -> None:
    """Create tables and a few demo resources. Runs on import because serverless
    platforms don't always send ASGI lifespan events. Alembic is on the roadmap."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(Resource.id).limit(1)) is None:
            db.add_all(Resource(name=n) for n in DEMO_RESOURCES)
            db.commit()


init_db()

app = FastAPI(
    title="Booking API",
    description="Bookings for rooms, apartments or time slots, with double-booking protection.",
    version="0.2.0",
)
app.include_router(resources.router)
app.include_router(bookings.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return INDEX_HTML


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
