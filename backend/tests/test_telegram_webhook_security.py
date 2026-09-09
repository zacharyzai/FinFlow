from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import telegram
from app.api.dependencies import get_current_user


def test_valid_secret_rejects_mismatch(monkeypatch):
    monkeypatch.setattr(telegram, "TELEGRAM_WEBHOOK_SECRET", "correct-secret")
    assert telegram._valid_secret("wrong") is False


def test_valid_secret_accepts_match(monkeypatch):
    monkeypatch.setattr(telegram, "TELEGRAM_WEBHOOK_SECRET", "correct-secret")
    assert telegram._valid_secret("correct-secret") is True


def test_valid_secret_rejects_when_unconfigured(monkeypatch):
    monkeypatch.setattr(telegram, "TELEGRAM_WEBHOOK_SECRET", None)
    assert telegram._valid_secret("anything") is False


def test_valid_secret_rejects_non_ascii_header_without_raising(monkeypatch):
    # Starlette decodes headers as latin-1, so a non-ASCII byte can reach here.
    # str-vs-str hmac.compare_digest raises TypeError on that; bytes comparison
    # must not.
    monkeypatch.setattr(telegram, "TELEGRAM_WEBHOOK_SECRET", "correct-secret")
    assert telegram._valid_secret("\xff\xfe") is False


def test_webhook_returns_200_on_malformed_json_body(monkeypatch):
    monkeypatch.setattr(telegram, "TELEGRAM_WEBHOOK_SECRET", "correct-secret")
    app = FastAPI()
    app.include_router(telegram.router)
    client = TestClient(app)

    response = client.post(
        "/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "correct-secret", "Content-Type": "application/json"},
        content=b"not valid json",
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_webhook_skips_dispatch_on_incorrect_secret(monkeypatch):
    monkeypatch.setattr(telegram, "TELEGRAM_WEBHOOK_SECRET", "correct-secret")
    called = []
    monkeypatch.setattr(telegram, "handle_update", lambda update: called.append(update))
    app = FastAPI()
    app.include_router(telegram.router)
    client = TestClient(app)

    response = client.post(
        "/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret", "Content-Type": "application/json"},
        json={"message": {"chat": {"id": 1}, "text": "/goal"}},
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert called == []


def test_link_token_503s_when_bot_username_unconfigured(monkeypatch):
    monkeypatch.setattr(telegram, "TELEGRAM_BOT_USERNAME", None)
    app = FastAPI()
    app.include_router(telegram.router)
    app.dependency_overrides[get_current_user] = lambda: {"id": "user-1", "email": "a@b.com"}
    client = TestClient(app)

    response = client.post("/telegram/link-token")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "server_error"
