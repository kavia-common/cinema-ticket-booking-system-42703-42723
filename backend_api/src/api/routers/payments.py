import uuid

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import (
    PaymentConfirmRequest,
    PaymentConfirmResponse,
    PaymentIntentRequest,
    PaymentIntentResponse,
)
from src.api.store import DB

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/intent",
    response_model=PaymentIntentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create mock payment intent",
    description="Create a mock payment intent and return a client secret-like ID.",
)
# PUBLIC_INTERFACE
def create_payment_intent(req: PaymentIntentRequest):
    """Create a mock payment intent."""
    if req.amount_cents <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    intent_id = f"pi_{uuid.uuid4().hex[:24]}"
    intent = {
        "id": intent_id,
        "amount_cents": req.amount_cents,
        "currency": req.currency,
        "status": "requires_confirmation",
        "metadata": req.metadata or {},
    }
    DB.payment_intents[intent_id] = intent
    return {
        "client_secret": intent_id,
        "amount_cents": intent["amount_cents"],
        "currency": intent["currency"],
        "status": intent["status"],
    }


@router.post(
    "/confirm",
    response_model=PaymentConfirmResponse,
    summary="Confirm mock payment",
    description="Confirm a mock payment intent; sets its status to succeeded.",
)
# PUBLIC_INTERFACE
def confirm_payment(req: PaymentConfirmRequest):
    """Confirm a mock payment intent."""
    intent = DB.payment_intents.get(req.payment_intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Payment intent not found")
    intent["status"] = "succeeded"
    return {"payment_intent_id": intent["id"], "status": intent["status"]}
