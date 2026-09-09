import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/").removesuffix("/rest/v1")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
# Comma-separated allowed frontend origins, e.g. "http://localhost:5173,https://finflow.vercel.app"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
# AI parsing: Claude is used when ANTHROPIC_API_KEY is set; otherwise falls back to Gemini.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Secret Telegram echoes back on every webhook call via the
# X-Telegram-Bot-Api-Secret-Token header — set when registering the webhook,
# checked on every incoming request so randoms can't POST fake updates.
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")
# Used to build the t.me/<username>?start=<token> deep link.
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
