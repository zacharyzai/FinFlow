from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import telegram


def test_valid_secret_rejects_mismatch(monkeypatch):
    monkeypatch.setattr(telegram, "TELEGRAM_WEBHOOK_SECRET", "correct-secret")
    assert telegram._valid_secret("wrong") is False


def test_valid_secret_accepts_match(monkeypatch):
    monkeypatch.setattr(telegram, "TELEGRAM_WEBHOOK_SECRET", "correct-secret")
    assert telegram._valid_secret("correct-secret") is True


def test_valid_secret_rejects_when_unconfigured(monkeypatch):
    monkeypatch.setattr(telegram, "TELEGRAM_WEBHOOK_SECRET", None)
    assert telegram._valid_secret("anything") is False


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
