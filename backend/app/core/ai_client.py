"""
AI text generation, preferring Claude and falling back to Gemini.

Claude is used whenever ANTHROPIC_API_KEY is configured. Otherwise we fall
back to Gemini (GEMINI_API_KEY) — handy while Claude API credits aren't set up.
"""
import logging

import anthropic
from google import genai
from google.genai import types

from app.core.config import ANTHROPIC_API_KEY, GEMINI_API_KEY

logger = logging.getLogger(__name__)

_claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
_gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def ai_generate(prompt: str, max_tokens: int, claude_model: str, gemini_model: str, search: bool = False) -> str:
    """
    Generate text with Claude if configured, otherwise Gemini.

    search=True lets the model use web search to resolve ambiguous names (e.g.
    an unfamiliar merchant) — it costs extra quota/latency, so only pass it for
    requests that actually need it, not every call.
    """
    if _claude:
        try:
            kwargs = {}
            if search:
                kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
            message = _claude.messages.create(
                model=claude_model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return "".join(b.text for b in message.content if b.type == "text").strip()
        except Exception:
            logger.exception("Claude request failed")
            raise RuntimeError("The AI provider (Claude) couldn't process this request. Please try again shortly.")
    if _gemini:
        try:
            # thinking_level=MINIMAL matters here: Gemini 3's reasoning tokens count
            # against max_output_tokens, and without capping them a multi-row prompt
            # can burn the whole budget on invisible thinking and return truncated JSON.
            config = types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
                tools=[types.Tool(google_search=types.GoogleSearch())] if search else None,
            )
            response = _gemini.models.generate_content(
                model=gemini_model,
                contents=prompt,
                config=config,
            )
            return response.text.strip()
        except Exception:
            logger.exception("Gemini request failed")
            raise RuntimeError("The AI provider (Gemini) couldn't process this request. Please try again shortly.")
    raise RuntimeError("No AI provider is configured. Please set an API key and restart the server.")
