import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def _database_url() -> str:
    url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    if not url:
        # Vercel functions can only write to /tmp. Without a Postgres URL the demo
        # still works there, it just resets when the function is recycled.
        return "sqlite:////tmp/booking.db" if os.getenv("VERCEL") else "sqlite:///./booking.db"
    # Hosted Postgres (Neon, Supabase, Vercel) hands out postgres:// URLs;
    # point SQLAlchemy at the psycopg 3 driver we install.
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


DATABASE_URL = _database_url()

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
