import httpx
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

async def send_message(chat_id: int, text: str) -> None:
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })

async def set_webhook(webhook_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/setWebhook", json={"url": webhook_url})
        return response.json()


async def poll_telegram(handle_update) -> None:
    offset = 0
    async with httpx.AsyncClient() as client:
        while True:
            r = await client.get(f"{BASE_URL}/getUpdates",
                                 params={"offset": offset, "timeout": 10})
            for update in r.json().get("result", []):
                await handle_update(update)
                offset = update["update_id"] + 1
