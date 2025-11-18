from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# Simple in-memory "database" with locks for thread-safety.
class InMemoryDB:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.movies: Dict[str, dict] = {}
        self.showtimes: Dict[str, dict] = {}
        # seat availability stored per showtime: seat_id -> "available"|"held"|"booked"
        self.seats: Dict[str, Dict[str, str]] = {}
        self.holds: Dict[str, dict] = {}
        self.bookings: Dict[str, dict] = {}
        self.users: Dict[str, dict] = {}
        self.payment_intents: Dict[str, dict] = {}

    def lock(self):
        return self._lock


DB = InMemoryDB()


def now_ts() -> float:
    return time.time()


@dataclass
class SeatMapSpec:
    rows: int
    cols: int
    vip_rows: Set[int] = field(default_factory=set)

    def generate_seats(self) -> List[str]:
        """
        Generate seat IDs in the format: <RowLetter><ColNumber> e.g., A1, A2...
        Rows start at 'A'.
        """
        seats = []
        for r in range(self.rows):
            row_letter = chr(ord("A") + r)
            for c in range(1, self.cols + 1):
                seats.append(f"{row_letter}{c}")
        return seats


def _seed_data():
    """Seed the in-memory DB with basic movies, showtimes, and seats."""
    with DB.lock():
        if DB.movies:
            return

        # Movies
        m1 = {
            "id": "m001",
            "title": "The Blue Horizon",
            "description": "An epic journey across the seas.",
            "duration_minutes": 125,
            "rating": "PG-13",
            "poster_url": "https://picsum.photos/300/450?random=1",
            "genres": ["Adventure", "Drama"],
        }
        m2 = {
            "id": "m002",
            "title": "City Lights",
            "description": "A heartfelt tale in the bustling city.",
            "duration_minutes": 98,
            "rating": "PG",
            "poster_url": "https://picsum.photos/300/450?random=2",
            "genres": ["Romance", "Comedy"],
        }
        DB.movies[m1["id"]] = m1
        DB.movies[m2["id"]] = m2

        # Showtimes for each movie
        st1 = {
            "id": "s001",
            "movie_id": "m001",
            "start_time": "2025-12-01T17:00:00Z",
            "auditorium": "Auditorium 1",
            "price_cents": 1200,
        }
        st2 = {
            "id": "s002",
            "movie_id": "m001",
            "start_time": "2025-12-01T20:00:00Z",
            "auditorium": "Auditorium 1",
            "price_cents": 1200,
        }
        st3 = {
            "id": "s003",
            "movie_id": "m002",
            "start_time": "2025-12-01T18:30:00Z",
            "auditorium": "Auditorium 2",
            "price_cents": 1000,
        }
        DB.showtimes[st1["id"]] = st1
        DB.showtimes[st2["id"]] = st2
        DB.showtimes[st3["id"]] = st3

        # Seats per showtime
        spec = SeatMapSpec(rows=6, cols=10, vip_rows={0, 1})  # Rows A-B VIP
        seats = spec.generate_seats()
        for st in (st1, st2, st3):
            DB.seats[st["id"]] = {seat_id: "available" for seat_id in seats}


# Hold expiration worker to clear stale holds after 5 minutes
HOLD_TTL_SECONDS = 5 * 60


def _expire_holds_worker():
    while True:
        time.sleep(5)
        with DB.lock():
            now = now_ts()
            expired: List[str] = []
            for hold_id, hold in DB.holds.items():
                if hold["status"] == "active" and (now - hold["created_at"]) >= HOLD_TTL_SECONDS:
                    # release seats
                    stid = hold["showtime_id"]
                    for seat in hold["seats"]:
                        # Only free seats that are still held
                        if DB.seats.get(stid, {}).get(seat) == "held":
                            DB.seats[stid][seat] = "available"
                    hold["status"] = "expired"
                    expired.append(hold_id)
            # Note: we keep expired holds for introspection; status marks them unusable.


# start the background expiration thread
_seed_data()
_t = threading.Thread(target=_expire_holds_worker, daemon=True)
_t.start()


def create_hold(showtime_id: str, seats: List[str], user_id: Optional[str]) -> Tuple[Optional[dict], Optional[str]]:
    with DB.lock():
        if showtime_id not in DB.showtimes:
            return None, "Showtime not found"

        # Validate availability
        seat_states = DB.seats.get(showtime_id, {})
        unavailable = [s for s in seats if seat_states.get(s) != "available"]
        if unavailable:
            return None, f"Seats not available: {', '.join(unavailable)}"

        # Mark as held
        for s in seats:
            seat_states[s] = "held"

        hold_id = str(uuid.uuid4())
        hold = {
            "id": hold_id,
            "showtime_id": showtime_id,
            "seats": seats,
            "user_id": user_id,
            "status": "active",
            "created_at": now_ts(),
        }
        DB.holds[hold_id] = hold
        return hold, None


def cancel_hold(hold_id: str) -> Tuple[bool, Optional[str]]:
    with DB.lock():
        hold = DB.holds.get(hold_id)
        if not hold:
            return False, "Hold not found"
        if hold["status"] != "active":
            return False, f"Hold is not active (status={hold['status']})"
        stid = hold["showtime_id"]
        for s in hold["seats"]:
            if DB.seats.get(stid, {}).get(s) == "held":
                DB.seats[stid][s] = "available"
        hold["status"] = "cancelled"
        return True, None


def confirm_booking(hold_id: str, payment_intent_id: Optional[str]) -> Tuple[Optional[dict], Optional[str], int]:
    with DB.lock():
        hold = DB.holds.get(hold_id)
        if not hold:
            return None, "Hold not found", 404
        if hold["status"] != "active":
            return None, f"Hold not active (status={hold['status']})", 400

        stid = hold["showtime_id"]
        # Ensure seats still held
        for s in hold["seats"]:
            if DB.seats.get(stid, {}).get(s) != "held":
                return None, f"Seat {s} no longer held", 409

        # Book seats
        for s in hold["seats"]:
            DB.seats[stid][s] = "booked"

        # Close hold
        hold["status"] = "consumed"

        booking_id = str(uuid.uuid4())
        showtime = DB.showtimes[stid]
        movie = DB.movies[showtime["movie_id"]]
        total_cents = showtime["price_cents"] * len(hold["seats"])

        booking = {
            "id": booking_id,
            "showtime_id": stid,
            "movie_id": movie["id"],
            "seats": hold["seats"],
            "user_id": hold.get("user_id"),
            "payment_intent_id": payment_intent_id,
            "status": "confirmed",
            "amount_cents": total_cents,
            "created_at": now_ts(),
        }
        DB.bookings[booking_id] = booking
        return booking, None, 200
