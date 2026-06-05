from fastapi import APIRouter, Request
from app.services.telegram import send_message
from app.core.database import supabase  # your existing Supabase client

router = APIRouter(prefix="/telegram", tags=["telegram"])

@router.post("/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()

    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    user_id = ...  # explained below

    if text == "/start":
        # Save chat_id to profiles
        supabase.table("profiles").update(
            {"telegram_chat_id": chat_id, "telegram_enabled": True}
        ).eq("id", user_id).execute()

        await send_message(chat_id, "Connected! You'll receive daily budget alerts.")

    return {"ok": True}
