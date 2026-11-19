# Booking API

[![CI](https://github.com/muhammadusman200301-blip/booking-api/actions/workflows/ci.yml/badge.svg)](https://github.com/muhammadusman200301-blip/booking-api/actions/workflows/ci.yml)

**Live demo:** _coming soon_ · API docs at `/docs`

A FastAPI + PostgreSQL service for booking rooms, apartments or time slots. The first version focuses on the part that usually goes wrong in booking systems: **two guests getting the same slot**.

## What it does today

- Create bookable **resources** (a room, an apartment, a cleaner's time slot)
- Create, list and fetch **bookings**
- **Cancel** a booking and free the slot (cancelling twice is safe)
- **Blocks double bookings** for the same resource
- Allows **back-to-back** bookings (check-out at 10:00, next check-in at 10:00)
- Rejects bad input: end before start, times without a timezone, unknown resource
- Locks the resource row while checking (`SELECT ... FOR UPDATE`), so two simultaneous requests can't both win the same slot
- A small booking page at `/` and interactive API docs at `/docs`

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

## Deploy to Vercel

The repo deploys as-is: `api/index.py` exposes the FastAPI app and `vercel.json` routes every path to it.

- With no database configured, the demo uses SQLite in `/tmp` (data resets when the function restarts).
- For persistent data, add a Postgres database (e.g. Neon from the Vercel Marketplace). Its `DATABASE_URL` / `POSTGRES_URL` is picked up automatically.

## Tests

```bash
pytest
```

`tests/test_availability.py` covers the overlap rules; `tests/test_api.py` covers the endpoints end to end.

## Roadmap

- [x] Cancel a booking and free the slot
- [ ] Stripe test-mode payments and a payment webhook with idempotency keys
- [x] Protection against concurrent double bookings (row lock on the resource)
- [ ] Postgres exclusion constraint as a second safety net
- [ ] Alembic migrations
- [x] GitHub Actions CI
- [x] Simple booking web page
- [x] Deployable to Vercel (serverless Python)

## Stack

Python 3.12 · FastAPI · SQLAlchemy 2 · PostgreSQL · Pydantic v2 · Pytest · Docker
