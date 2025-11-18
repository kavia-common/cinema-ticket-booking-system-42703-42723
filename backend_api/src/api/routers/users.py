import uuid

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import LoginResponse, User, UserLoginRequest, UserRegisterRequest
from src.api.store import DB

router = APIRouter(prefix="", tags=["Users"])


@router.post(
    "/users",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Mock user registration; stores user data in memory (not secure).",
)
# PUBLIC_INTERFACE
def register_user(req: UserRegisterRequest):
    """Register a new mock user."""
    # Simple uniqueness check by email
    for u in DB.users.values():
        if u["email"].lower() == req.email.lower():
            raise HTTPException(status_code=400, detail="Email already registered")
    uid = str(uuid.uuid4())
    user = {"id": uid, "email": req.email, "name": req.name, "password": req.password}
    DB.users[uid] = user
    return {"id": uid, "email": req.email, "name": req.name}


@router.post(
    "/auth/login",
    response_model=LoginResponse,
    summary="Login",
    description="Mock login; returns a dummy bearer token if email/password match a registered user.",
)
# PUBLIC_INTERFACE
def login(req: UserLoginRequest):
    """Mock login: verify email/password and return a dummy token."""
    found = None
    for u in DB.users.values():
        if u["email"].lower() == req.email.lower():
            found = u
            break
    if not found or found.get("password") != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = f"mocktoken-{found['id']}"
    return {"access_token": token, "token_type": "bearer"}
