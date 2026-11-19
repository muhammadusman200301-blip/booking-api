from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Base, engine
from app.routers import bookings, resources


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Fine for a first version; Alembic migrations are on the roadmap.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Booking API",
    description="Bookings for rooms, apartments or time slots, with double-booking protection.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(resources.router)
app.include_router(bookings.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
