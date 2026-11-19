# Booking API

A FastAPI + PostgreSQL service for booking rooms, apartments or time slots. The first version focuses on the part that usually goes wrong in booking systems: **two guests getting the same slot**.

## What it does today

- Create bookable **resources** (a room, an apartment, a cleaner's time slot)
- Create, list and fetch **bookings**
- **Blocks double bookings** for the same resource
- Allows **back-to-back** bookings (check-out at 10:00, next check-in at 10:00)
- Rejects bad input: end before start, times without a timezone, unknown resource

## How the double-booking check works

Bookings are treated as half-open intervals `[start, end)`. Two bookings clash when
`a.start < b.end and b.start < a.end`. The rule lives in `app/availability.py` as a pure
function (easy to unit test), and the same condition is pushed into the SQL query in
`app/routers/bookings.py`, so the API only loads a clashing row instead of every booking.

## Run it

```bash
docker compose up --build
# API:  http://localhost:8000
# Docs: http://localhost:8000/docs
```

Without Docker (uses a local SQLite file):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests

```bash
pytest
```

`tests/test_availability.py` covers the overlap rules; `tests/test_api.py` covers the endpoints end to end.

## Roadmap

- [ ] Cancel a booking and free the slot
- [ ] Stripe test-mode payments and a payment webhook with idempotency keys
- [ ] Database-level protection against race conditions (Postgres exclusion constraint)
- [ ] Alembic migrations
- [ ] GitHub Actions CI
- [ ] Simple booking web page and live deployment

## Stack

Python 3.12 · FastAPI · SQLAlchemy 2 · PostgreSQL · Pydantic v2 · Pytest · Docker
