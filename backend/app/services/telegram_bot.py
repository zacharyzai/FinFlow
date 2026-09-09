"""
Command router for the Telegram bot: parses incoming update payloads,
resolves the linked FinFlow user, and dispatches to the right handler.
"""
import logging
import secrets
import time
from datetime import date, datetime, timedelta, timezone

from app.api.analytics import category_breakdown_data
from app.api.budget import compute_daily_budget
from app.api.savings import list_goals_data
from app.core.ai_client import ai_generate
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

    # chat_id has a unique index (one Telegram chat -> one FinFlow user). If this
    # chat is already linked to a *different* row, the update below would hit a
    # unique-constraint violation and raise — caught by the webhook's generic
    # except, but silently, leaving the user with no reply. Check first instead.
    other = supabase.table("telegram_links").select("id").eq("chat_id", chat_id).execute()
    if other.data and other.data[0]["id"] != row["id"]:
        send_message(
            chat_id,
            "This Telegram account is already linked to a different FinFlow account. "
            "Disconnect it from that account's Settings first.",
        )
        return

    supabase.table("telegram_links").update({
        "chat_id": chat_id, "link_token": None, "token_expires_at": None,
    }).eq("id", row["id"]).execute()
    send_message(chat_id, "✅ Connected to FinFlow.")


RECOMMENDATION_LIMIT = 5          # calls per chat_id
RECOMMENDATION_WINDOW_SECONDS = 3600

_recommendation_calls: dict[int, list[float]] = {}


def _lookup_user_id(chat_id: int) -> str | None:
    result = supabase.table("telegram_links").select("user_id").eq("chat_id", chat_id).execute()
    return result.data[0]["user_id"] if result.data else None


def _under_recommendation_limit(chat_id: int) -> bool:
    """
    In-memory sliding-window limiter: RECOMMENDATION_LIMIT calls per chat_id
    per RECOMMENDATION_WINDOW_SECONDS.

    In-memory is fine for a single backend instance (Railway runs one here);
    would need a shared store (Redis) behind multiple instances.
    """
    now = time.monotonic()
    calls = [t for t in _recommendation_calls.get(chat_id, []) if now - t < RECOMMENDATION_WINDOW_SECONDS]
    _recommendation_calls[chat_id] = calls
    if len(calls) >= RECOMMENDATION_LIMIT:
        return False
    calls.append(now)
    return True


def _format_goals(user_id: str) -> str:
    goals = list_goals_data(user_id)
    if not goals:
        return "No savings goals yet — add one in FinFlow."
    lines = [f"{g['name']}: ${g['saved']:.0f}/${g['target']:.0f} ({g['progress_pct']:.0f}%)" for g in goals]
    return "\n".join(lines)


def _format_daily_budget(user_id: str) -> str:
    data = compute_daily_budget(user_id)
    return f"Daily budget remaining: ${data['daily_budget']:.2f}"


def _format_monthly_budget(user_id: str) -> str:
    data = compute_daily_budget(user_id)
    return f"Budget remaining this month: ${data['breakdown']['available']:.2f}"


def _format_recommendation(chat_id: int, user_id: str) -> str:
    if not _under_recommendation_limit(chat_id):
        return "You've hit the recommendation limit for now — try again in a bit."

    today = date.today()
    month_start = str(today.replace(day=1))
    categories = category_breakdown_data(user_id, month_start, str(today))
    budget = compute_daily_budget(user_id)

    if not categories["categories"]:
        return "Not enough spending data yet to make a recommendation."

    breakdown_text = "\n".join(f"{c['category']}: ${c['total']:.0f}" for c in categories["categories"])
    prompt = (
        "You are a personal finance assistant. Given this month's spending by "
        "category and the user's remaining daily budget, suggest ONE or TWO "
        "concrete, specific things they could cut back on. Be brief (2-3 sentences), "
        "no preamble.\n\n"
        f"Spending by category this month:\n{breakdown_text}\n\n"
        f"Daily budget remaining: ${budget['daily_budget']:.2f}\n"
    )
    try:
        return ai_generate(prompt, max_tokens=200, claude_model="claude-sonnet-4-6", gemini_model="gemini-3.6-flash")
    except RuntimeError:
        return "Couldn't generate a recommendation right now — try again shortly."


COMMANDS = {
    "/goal": _format_goals,
    "/dbudget": _format_daily_budget,
    "/mbudget": _format_monthly_budget,
}


def handle_command(chat_id: int, text: str) -> None:
    """Dispatch a non-/start command: look up the linked user, reply via Telegram."""
    user_id = _lookup_user_id(chat_id)
    if not user_id:
        send_message(chat_id, "Not linked yet — connect your account from FinFlow Settings.")
        return

    command = text.strip().split()[0].split("@")[0].lower() if text.strip() else ""

    if command == "/recommendation":
        logger.info("telegram command: /recommendation")
        send_message(chat_id, _format_recommendation(chat_id, user_id))
        return

    handler = COMMANDS.get(command)
    if handler is None:
        send_message(chat_id, "Unknown command. Try /goal, /dbudget, /mbudget, /recommendation.")
        return

    logger.info("telegram command: %s", command)
    send_message(chat_id, handler(user_id))


def handle_update(update: dict) -> None:
    """Entry point from the webhook route: parse a Telegram update, route it."""
    message = update.get("message")
    if not message or "text" not in message:
        return

    chat_id = message["chat"]["id"]
    text = message["text"]

    if text.startswith("/start"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_start(chat_id, parts[1].strip())
        else:
            send_message(chat_id, "Open this link from FinFlow Settings to connect your account.")
        return

    handle_command(chat_id, text)
