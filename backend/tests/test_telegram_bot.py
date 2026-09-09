from datetime import datetime, timedelta, timezone

from app.services import telegram_bot as bot


def test_is_expired_true_for_past_timestamp():
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    assert bot._is_expired(past) is True


def test_is_expired_false_for_future_timestamp():
    future = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    assert bot._is_expired(future) is False
