from fastapi import APIRouter, HTTPException, status

from src.api.schemas import Booking, BookingCreateRequest
from src.api.store import DB, confirm_booking

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=Booking,
    status_code=status.HTTP_201_CREATED,
    summary="Create booking",
    description="Confirm a booking from a valid active hold. Seats are booked if still held.",
)
# PUBLIC_INTERFACE
def create_booking(req: BookingCreateRequest):
    """Convert a hold into a confirmed booking."""
    booking, err, code = confirm_booking(req.hold_id, req.payment_intent_id)
    if err:
        raise HTTPException(status_code=code, detail=err)
    return booking


@router.get(
    "/{booking_id}",
    response_model=Booking,
    summary="Get booking",
    description="Get booking details by ID.",
)
# PUBLIC_INTERFACE
def get_booking(booking_id: str):
    """Retrieve booking by ID."""
    booking = DB.bookings.get(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
