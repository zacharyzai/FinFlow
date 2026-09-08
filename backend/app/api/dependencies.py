from fastapi import Header
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import supabase
from app.core.errors import app_error

limiter = Limiter(key_func=get_remote_address)

VALID_CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Bills & Utilities",
    "Healthcare", "Entertainment", "Travel", "Education",
    "Income", "Transfer", "Other",
]


async def get_current_user(authorization: str = Header(...)) -> dict:
    """Extract and verify the Supabase JWT from the Authorization header."""
    if not authorization.startswith("Bearer "):
        raise app_error(401, "auth_error", "Invalid authorization header")

    token = authorization.removeprefix("Bearer ")
    try:
        response = supabase.auth.get_user(token)
    except Exception:
        # Note: this used to sit in the same try as the "user is None" check
        # below, so that check's own HTTPException was being caught right
        # back here and replaced with this generic message. Narrowed the try
        # to just the network call so a genuinely invalid/expired token still
        # reports as such instead of a vague "could not validate credentials".
        raise app_error(401, "auth_error", "Could not validate credentials")

    if response.user is None:
        raise app_error(401, "auth_error", "Invalid or expired token")
    return {"id": response.user.id, "email": response.user.email}