from typing import List

from fastapi import APIRouter, HTTPException

from src.api.schemas import Showtime
from src.api.store import DB

router = APIRouter(prefix="", tags=["Showtimes"])


@router.get("/movies/{movie_id}/showtimes", response_model=List[Showtime], summary="List showtimes for a movie", description="Return all showtimes associated with a given movie.")
# PUBLIC_INTERFACE
def list_showtimes_for_movie(movie_id: str):
    """List showtimes for a given movie."""
    if movie_id not in DB.movies:
        raise HTTPException(status_code=404, detail="Movie not found")
    return [s for s in DB.showtimes.values() if s["movie_id"] == movie_id]


@router.get("/showtimes/{showtime_id}", response_model=Showtime, summary="Get showtime", description="Get details for a specific showtime by ID.")
# PUBLIC_INTERFACE
def get_showtime(showtime_id: str):
    """Get one showtime by ID."""
    st = DB.showtimes.get(showtime_id)
    if not st:
        raise HTTPException(status_code=404, detail="Showtime not found")
    return st
