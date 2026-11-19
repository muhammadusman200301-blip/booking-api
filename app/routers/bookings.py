from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.availability import BookingError, validate_window
from app.db import get_db
from app.models import Booking, Resource
from app.schemas import BookingIn, BookingOut

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(body: BookingIn, db: Session = Depends(get_db)):
    try:
        validate_window(body.start, body.end)
    except BookingError as e:
        raise HTTPException(422, str(e))

    if not db.get(Resource, body.resource_id):
        raise HTTPException(404, "Resource not found")

    # Same rule as availability.overlaps(), pushed into SQL so we only load clashes.
    clash = db.scalar(
        select(Booking.id).where(
            Booking.resource_id == body.resource_id,
            Booking.status == "confirmed",
            Booking.start < body.end,
            body.start < Booking.end,
        )
    )
    if clash:
        raise HTTPException(409, f"Resource is already booked for this time (booking {clash})")

    booking = Booking(**body.model_dump())
    db.add(booking)
    db.commit()
    return booking


@router.get("", response_model=list[BookingOut])
def list_bookings(resource_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Booking).order_by(Booking.start)
    if resource_id is not None:
        query = query.where(Booking.resource_id == resource_id)
    return db.scalars(query).all()


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")
    return booking
