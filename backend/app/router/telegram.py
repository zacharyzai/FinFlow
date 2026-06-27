import uuid
from datetime import date
from calendar import monthrange

from fastapi import APIRouter, Request, Depends
from app.services.telegram import send_message
from app.core.database import supabase
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/telegram", tags=["telegram"])


# ----------------------------------------------------------------
# Called by the Vue frontend when user clicks "Connect Telegram".
# Generates a short token and saves it against the user's profile.
# ----------------------------------------------------------------

@router.post("/connect")
async def connect_telegram(current_user: dict = Depends(get_current_user)):
    token = str(uuid.uuid4())[:8]  # e.g. "a1b2c3d4"

    supabase.table("profiles").upsert({
        "id": current_user["id"],
        "link_token": token,
    }).execute()

    return {"token": token}


# ----------------------------------------------------------------
# Shared handler — used by both polling (local) and webhook (Railway).
# ----------------------------------------------------------------

async def handle_update(update: dict):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    # /start <token> — link this Telegram chat to a FinFlow account
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) < 2:
            await send_message(chat_id, "Open FinFlow and click *Connect Telegram* to get your link code.")
            return

        token = parts[1]
        result = supabase.table("profiles").select("id").eq("link_token", token).execute()

        if not result.data:
            await send_message(chat_id, "Invalid or expired token. Please try again from the app.")
            return

        user_id = result.data[0]["id"]

        supabase.table("profiles").update({
            "telegram_chat_id": chat_id,
            "telegram_enabled": True,
            "link_token": None,
        }).eq("id", user_id).execute()

        await send_message(chat_id, "Connected to FinFlow! Send /budget to see your daily budget.")
        return

    # /budget — calculate and return the user's daily budget
    if text == "/budget":
        result = supabase.table("profiles").select("id").eq("telegram_chat_id", chat_id).execute()

        if not result.data:
            await send_message(chat_id, "Account not linked. Open FinFlow and click *Connect Telegram*.")
            return

        user_id = result.data[0]["id"]
        today = date.today()
        month_start = today.replace(day=1)
        days_in_month = monthrange(today.year, today.month)[1]
        days_remaining = days_in_month - today.day + 1

        income_res = supabase.table("transactions").select("credit") \
            .eq("user_id", user_id).eq("category", "Income") \
            .gte("date", str(month_start)).lte("date", str(today)).execute()
        income = sum(float(r["credit"]) for r in income_res.data if r["credit"])

        bills_res = supabase.table("planned_expenses").select("amount") \
            .eq("user_id", user_id).eq("category", "Bills & Utilities") \
            .gte("due_date", str(month_start)) \
            .lte("due_date", str(today.replace(day=days_in_month))).execute()
        bills = sum(float(r["amount"]) for r in bills_res.data if r["amount"])

        planned_res = supabase.table("planned_expenses").select("amount") \
            .eq("user_id", user_id).neq("category", "Bills & Utilities") \
            .gte("due_date", str(month_start)) \
            .lte("due_date", str(today.replace(day=days_in_month))).execute()
        planned = sum(float(r["amount"]) for r in planned_res.data if r["amount"])

        available = income - bills - planned
        daily = max(0, available / days_remaining) if days_remaining > 0 else 0

        await send_message(chat_id, (
            f"*Your Daily Budget*\n\n"
            f"Income this month: ${income:,.2f}\n"
            f"Bills: -${bills:,.2f}\n"
            f"Planned expenses: -${planned:,.2f}\n"
            f"───────────────\n"
            f"*Today's budget: ${daily:,.2f}*\n"
            f"({days_remaining} days remaining)"
        ))
        return

    # unknown command
    await send_message(chat_id, "Available commands:\n/budget — see your daily budget")


# ----------------------------------------------------------------
# Webhook endpoint — only used in production (Railway).
# ----------------------------------------------------------------

@router.post("/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()
    await handle_update(body)
    return {"ok": True}
