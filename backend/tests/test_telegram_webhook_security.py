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
