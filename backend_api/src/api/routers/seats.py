from typing import List

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import HoldRequest, HoldResponse, SeatAvailability
from src.api.store import DB, HOLD_TTL_SECONDS, create_hold, cancel_hold, now_ts

router = APIRouter(prefix="", tags=["Seats"])


@router.get(
    "/showtimes/{showtime_id}/seats",
    response_model=List[SeatAvailability],
    summary="Seat availability",
    description="Get seat availability for a showtime (available|held|booked).",
)
# PUBLIC_INTERFACE
def get_seats(showtime_id: str):
    """Return seat availability for a showtime."""
    if showtime_id not in DB.showtimes:
        raise HTTPException(status_code=404, detail="Showtime not found")
    seat_states = DB.seats.get(showtime_id, {})
    return [{"seat_id": sid, "status": st} for sid, st in seat_states.items()]


@router.post(
    "/showtimes/{showtime_id}/hold",
    response_model=HoldResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create seat hold",
    description="Create a temporary seat hold for a showtime; expires after 5 minutes.",
)
# PUBLIC_INTERFACE
def create_seat_hold(showtime_id: str, req: HoldRequest):
    """Create a temporary hold for the requested seats."""
    hold, err = create_hold(showtime_id, req.seats, req.user_id)
    if err:
        if err == "Showtime not found":
            raise HTTPException(status_code=404, detail=err)
        # Seat conflict
        raise HTTPException(status_code=409, detail=err)
    ttl_remaining = HOLD_TTL_SECONDS - int(now_ts() - hold["created_at"])
    return {
        "id": hold["id"],
        "showtime_id": hold["showtime_id"],
        "seats": hold["seats"],
        "user_id": hold.get("user_id"),
        "status": hold["status"],
        "expires_in_seconds": max(0, ttl_remaining),
    }


@router.delete(
    "/holds/{hold_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel hold",
    description="Cancel a seat hold and release the seats if the hold is active.",
)
# PUBLIC_INTERFACE
def delete_hold(hold_id: str):
    """Cancel an existing hold."""
    ok, err = cancel_hold(hold_id)
    if not ok:
        if err == "Hold not found":
            raise HTTPException(status_code=404, detail=err)
        raise HTTPException(status_code=400, detail=err)
    return
