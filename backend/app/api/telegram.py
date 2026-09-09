"""
Telegram bot HTTP surface: link-token issuance (authed, called from FinFlow
Settings), the webhook Telegram posts updates to, and status/disconnect for
the Settings page.
"""
import hmac
import logging

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_current_user, limiter
from app.core.config import TELEGRAM_BOT_USERNAME, TELEGRAM_WEBHOOK_SECRET
from app.core.database import supabase
from app.core.errors import app_error
from app.services.telegram_bot import generate_link_token, handle_update

router = APIRouter(prefix="/telegram", tags=["telegram"])
logger = logging.getLogger(__name__)


def _valid_secret(header_value: str) -> bool:
    if not TELEGRAM_WEBHOOK_SECRET:
        return False
    return hmac.compare_digest(
        header_value.encode("utf-8", "replace"), TELEGRAM_WEBHOOK_SECRET.encode("utf-8")
    )


@router.post("/link-token")
@limiter.limit("10/minute")
async def link_token(request: Request, current_user: dict = Depends(get_current_user)):
    if not TELEGRAM_BOT_USERNAME:
        raise app_error(503, "server_error", "Telegram bot is not configured on this server.")
    token = generate_link_token(current_user["id"])
    return {"link_url": f"https://t.me/{TELEGRAM_BOT_USERNAME}?start={token}"}


@router.get("/status")
@limiter.limit("30/minute")
async def status(request: Request, current_user: dict = Depends(get_current_user)):
    result = supabase.table("telegram_links").select("chat_id").eq("user_id", current_user["id"]).execute()
    connected = bool(result.data and result.data[0].get("chat_id"))
    return {"connected": connected}


@router.delete("/link")
@limiter.limit("10/minute")
async def disconnect(request: Request, current_user: dict = Depends(get_current_user)):
    supabase.table("telegram_links").delete().eq("user_id", current_user["id"]).execute()
    return {"disconnected": True}


@router.post("/webhook")
async def webhook(request: Request, x_telegram_bot_api_secret_token: str = Header(default="")):
    # Always 200 — Telegram retries on non-200, and we don't want retry storms
    # from either a bad secret or an internal error while handling the update.
    if not _valid_secret(x_telegram_bot_api_secret_token):
        logger.warning("Rejected Telegram webhook call with invalid secret token")
        return JSONResponse(status_code=200, content={"ok": True})

    try:
        update = await request.json()
        await run_in_threadpool(handle_update, update)
    except Exception:
        logger.exception("Error handling Telegram update")
    return JSONResponse(status_code=200, content={"ok": True})
