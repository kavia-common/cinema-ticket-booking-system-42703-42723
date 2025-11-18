from typing import List

from fastapi import APIRouter, HTTPException

from src.api.schemas import Movie
from src.api.store import DB

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("", response_model=List[Movie], summary="List movies", description="Return the list of available movies.")
# PUBLIC_INTERFACE
def list_movies():
    """List all movies."""
    return list(DB.movies.values())


@router.get("/{movie_id}", response_model=Movie, summary="Get movie", description="Get details for a specific movie by ID.")
# PUBLIC_INTERFACE
def get_movie(movie_id: str):
    """Get one movie by ID."""
    movie = DB.movies.get(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
