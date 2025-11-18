from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.movies import router as movies_router
from src.api.routers.showtimes import router as showtimes_router
from src.api.routers.seats import router as seats_router
from src.api.routers.bookings import router as bookings_router
from src.api.routers.users import router as users_router
from src.api.routers.payments import router as payments_router

app = FastAPI(
    title="Cinema Ticket Booking API",
    description="Lightweight API for browsing movies, selecting showtimes, holding seats, creating bookings, and mock payments.",
    version="0.1.0",
    openapi_tags=[
        {"name": "Health", "description": "Health and status endpoints"},
        {"name": "Movies", "description": "Browse and retrieve movie information"},
        {"name": "Showtimes", "description": "Showtime listing and details"},
        {"name": "Seats", "description": "Seat availability and temporary holds"},
        {"name": "Bookings", "description": "Confirm and view bookings"},
        {"name": "Users", "description": "User registration and login"},
        {"name": "Payments", "description": "Mock payment intents and confirmations"},
    ],
)

# CORS for frontend running on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://0.0.0.0:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"], summary="Health Check", description="Simple health check endpoint to verify the service is running.")
# PUBLIC_INTERFACE
def health_check():
    """Return a JSON payload confirming the service is healthy."""
    return {"status": "ok"}


# Include routers
app.include_router(movies_router)
app.include_router(showtimes_router)
app.include_router(seats_router)
app.include_router(bookings_router)
app.include_router(users_router)
app.include_router(payments_router)
