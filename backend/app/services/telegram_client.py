"""Thin wrapper around Telegram's Bot API sendMessage call."""
import logging

import requests

from app.core.config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)

_API_BASE = "https://api.telegram.org"


def send_message(chat_id: int, text: str) -> None:
    """
    Send a plain-text message to a Telegram chat.

    Never raises — a failed notification shouldn't take down the webhook
    handler that triggered it; a delivery failure just means the user
    doesn't get a reply, which is logged, not fatal.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not configured, skipping send_message")
        return
    try:
        requests.post(
            f"{_API_BASE}/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
    except Exception:
        logger.exception("Failed to send Telegram message to chat %s", chat_id)
