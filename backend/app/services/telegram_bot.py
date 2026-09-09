"""
Command router for the Telegram bot: parses incoming update payloads,
resolves the linked FinFlow user, and dispatches to the right handler.
"""
import logging
import secrets
from datetime import datetime, timedelta, timezone

from app.core.database import supabase
from app.services.telegram_client import send_message

logger = logging.getLogger(__name__)

LINK_TOKEN_TTL_MINUTES = 10


def generate_link_token(user_id: str) -> str:
    """Create (or replace) this user's single-use link token and return it."""
    token = secrets.token_urlsafe(24)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=LINK_TOKEN_TTL_MINUTES)

    existing = supabase.table("telegram_links").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("telegram_links").update({
            "link_token": token, "token_expires_at": expires_at.isoformat(),
        }).eq("user_id", user_id).execute()
    else:
        supabase.table("telegram_links").insert({
            "user_id": user_id, "link_token": token, "token_expires_at": expires_at.isoformat(),
        }).execute()
    return token


def _is_expired(expires_at_str: str) -> bool:
    expires_at = datetime.fromisoformat(expires_at_str)
    return datetime.now(timezone.utc) >= expires_at


def handle_start(chat_id: int, token: str) -> None:
    """Consume a /start <token> deep link: link chat_id to the token's user_id."""
    result = supabase.table("telegram_links").select("*").eq("link_token", token).execute()
    if not result.data or _is_expired(result.data[0]["token_expires_at"]):
        send_message(chat_id, "This link has expired — generate a new one from FinFlow Settings.")
        return

    row = result.data[0]
    supabase.table("telegram_links").update({
        "chat_id": chat_id, "link_token": None, "token_expires_at": None,
    }).eq("id", row["id"]).execute()
    send_message(chat_id, "✅ Connected to FinFlow.")
