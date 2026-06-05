import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def check_bot():
    r = httpx.get(f"{BASE_URL}/getMe")
    print("Bot info:", r.json())

def poll_once():
    r = httpx.get(f"{BASE_URL}/getUpdates")
    updates = r.json().get("result", [])
    if not updates:
        print("No messages yet — send /start to your bot first")
        return
    for update in updates:
        msg = update.get("message", {})
        print(f"chat_id: {msg['chat']['id']}  text: {msg.get('text')}")

check_bot()
poll_once()
