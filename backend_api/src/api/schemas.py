from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Movie(BaseModel):
    id: str = Field(..., description="Movie ID")
    title: str = Field(..., description="Movie title")
    description: str = Field(..., description="Movie description")
    duration_minutes: int = Field(..., description="Duration in minutes")
    rating: str = Field(..., description="Content rating, e.g., PG-13")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    genres: Optional[List[str]] = Field(default_factory=list, description="List of genres")


class Showtime(BaseModel):
    id: str = Field(..., description="Showtime ID")
    movie_id: str = Field(..., description="Associated movie ID")
    start_time: str = Field(..., description="Start time (ISO8601)")
    auditorium: str = Field(..., description="Auditorium name")
    price_cents: int = Field(..., description="Ticket price in cents")


class SeatAvailability(BaseModel):
    seat_id: str = Field(..., description="Seat identifier (e.g., A1)")
    status: str = Field(..., description="Seat status: available|held|booked")


class HoldRequest(BaseModel):
    seats: List[str] = Field(..., description="List of seat IDs to hold")
    user_id: Optional[str] = Field(None, description="Optional user ID")


class HoldResponse(BaseModel):
    id: str = Field(..., description="Hold ID")
    showtime_id: str = Field(..., description="Showtime ID")
    seats: List[str] = Field(..., description="Seats held")
    user_id: Optional[str] = Field(None, description="User who created the hold")
    status: str = Field(..., description="Hold status")
    expires_in_seconds: int = Field(..., description="Approximate TTL remaining (seconds)")


class BookingCreateRequest(BaseModel):
    hold_id: str = Field(..., description="Active hold ID to convert into a booking")
    payment_intent_id: Optional[str] = Field(None, description="Mock payment intent ID")


class Booking(BaseModel):
    id: str = Field(..., description="Booking ID")
    showtime_id: str = Field(..., description="Showtime ID")
    movie_id: str = Field(..., description="Movie ID")
    seats: List[str] = Field(..., description="Booked seats")
    user_id: Optional[str] = Field(None, description="User who booked")
    payment_intent_id: Optional[str] = Field(None, description="Payment intent ID")
    status: str = Field(..., description="Booking status")
    amount_cents: int = Field(..., description="Total amount in cents")
    created_at: float = Field(..., description="Timestamp of creation")


class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password (stored as plain text in mock, do not use in prod)")
    name: Optional[str] = Field(None, description="Display name")


class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class User(BaseModel):
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="Display name")


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="Mock access token")
    token_type: str = Field("bearer", description="Token type")


class PaymentIntentRequest(BaseModel):
    amount_cents: int = Field(..., description="Amount in cents")
    currency: str = Field("usd", description="Currency code")
    metadata: Optional[dict] = Field(default_factory=dict, description="Optional metadata")


class PaymentIntentResponse(BaseModel):
    client_secret: str = Field(..., description="Mock client secret / intent ID")
    amount_cents: int = Field(..., description="Amount in cents")
    currency: str = Field(..., description="Currency code")
    status: str = Field(..., description="Status, e.g., requires_confirmation")


class PaymentConfirmRequest(BaseModel):
    payment_intent_id: str = Field(..., description="Intent to confirm")


class PaymentConfirmResponse(BaseModel):
    payment_intent_id: str = Field(..., description="Confirmed intent ID")
    status: str = Field(..., description="Status, e.g., succeeded")
