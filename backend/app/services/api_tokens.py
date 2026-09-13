"""
Quick-Add Shortcut personal access tokens: generation, hashing, and
resolution. One active token per user — generating a new one replaces
the old row, so a leaked/old token stops working immediately.

The raw token is never stored — only its SHA-256 hash. SHA-256 (not a
slow password hash like bcrypt) is correct here because the token is
already high-entropy random data, not a human-guessable password.
"""
import hashlib
import secrets
from datetime import datetime, timezone

from app.core.database import supabase


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_token(user_id: str) -> str:
    """Create (or replace) this user's single active quick-add token.

    Returns the raw token — this is the only time it is ever visible;
    only its hash is persisted.
    """
    token = secrets.token_urlsafe(32)
    token_hash = _hash_token(token)

    supabase.table("api_tokens").delete().eq("user_id", user_id).execute()
    supabase.table("api_tokens").insert({"user_id": user_id, "token_hash": token_hash}).execute()
    return token


def resolve_token(raw_token: str) -> str | None:
    """Look up the user_id for a raw token, or None if invalid/revoked."""
    token_hash = _hash_token(raw_token)
    result = supabase.table("api_tokens").select("id", "user_id").eq("token_hash", token_hash).execute()
    if not result.data:
        return None

    row = result.data[0]
    supabase.table("api_tokens").update(
        {"last_used_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", row["id"]).execute()
    return row["user_id"]


def revoke_token(user_id: str) -> None:
    supabase.table("api_tokens").delete().eq("user_id", user_id).execute()


def has_token(user_id: str) -> bool:
    result = supabase.table("api_tokens").select("id").eq("user_id", user_id).execute()
    return bool(result.data)
