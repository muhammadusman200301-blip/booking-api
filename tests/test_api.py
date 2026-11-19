import os

os.environ["DATABASE_URL"] = "sqlite:///./test_booking.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


client = TestClient(app)


def make_resource(name="Apartment 1"):
    return client.post("/resources", json={"name": name}).json()["id"]


def book(resource_id, start, end, guest="Ali"):
    return client.post(
        "/bookings",
        json={"resource_id": resource_id, "guest_name": guest, "start": start, "end": end},
    )


def test_create_and_get_booking():
    rid = make_resource()
    r = book(rid, "2026-12-01T12:00:00Z", "2026-12-03T10:00:00Z")
    assert r.status_code == 201
    assert client.get(f"/bookings/{r.json()['id']}").json()["guest_name"] == "Ali"


def test_double_booking_is_blocked():
    rid = make_resource()
    assert book(rid, "2026-12-01T12:00:00Z", "2026-12-03T10:00:00Z").status_code == 201
    clash = book(rid, "2026-12-02T12:00:00Z", "2026-12-04T10:00:00Z", guest="Sara")
    assert clash.status_code == 409


def test_back_to_back_booking_is_allowed():
    rid = make_resource()
    assert book(rid, "2026-12-01T12:00:00Z", "2026-12-03T10:00:00Z").status_code == 201
    assert book(rid, "2026-12-03T10:00:00Z", "2026-12-05T10:00:00Z").status_code == 201


def test_invalid_window_is_rejected():
    rid = make_resource()
    assert book(rid, "2026-12-03T10:00:00Z", "2026-12-01T10:00:00Z").status_code == 422


def test_unknown_resource_returns_404():
    assert book(999, "2026-12-01T12:00:00Z", "2026-12-02T12:00:00Z").status_code == 404


def test_cancelled_slot_can_be_booked_again():
    rid = make_resource()
    first = book(rid, "2026-12-01T12:00:00Z", "2026-12-03T10:00:00Z").json()
    cancelled = client.post(f"/bookings/{first['id']}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert book(rid, "2026-12-01T12:00:00Z", "2026-12-03T10:00:00Z", guest="Sara").status_code == 201


def test_cancel_is_idempotent_and_404s_for_unknown():
    rid = make_resource()
    bid = book(rid, "2026-12-01T12:00:00Z", "2026-12-02T12:00:00Z").json()["id"]
    assert client.post(f"/bookings/{bid}/cancel").status_code == 200
    assert client.post(f"/bookings/{bid}/cancel").status_code == 200
    assert client.post("/bookings/999/cancel").status_code == 404

def test_home_page_and_health():
    assert "Booking" in client.get("/").text
    assert client.get("/health").json() == {"status": "ok"}
