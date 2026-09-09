from datetime import datetime, timedelta, timezone

from app.services import telegram_bot as bot


def test_is_expired_true_for_past_timestamp():
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    assert bot._is_expired(past) is True


def test_is_expired_false_for_future_timestamp():
    future = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    assert bot._is_expired(future) is False


import time


def test_under_recommendation_limit_allows_up_to_limit_then_blocks():
    bot._recommendation_calls.clear()
    chat_id = 111
    for _ in range(bot.RECOMMENDATION_LIMIT):
        assert bot._under_recommendation_limit(chat_id) is True
    assert bot._under_recommendation_limit(chat_id) is False


def test_under_recommendation_limit_resets_after_window(monkeypatch):
    bot._recommendation_calls.clear()
    chat_id = 222
    fake_time = [1000.0]
    monkeypatch.setattr(time, "monotonic", lambda: fake_time[0])
    for _ in range(bot.RECOMMENDATION_LIMIT):
        assert bot._under_recommendation_limit(chat_id) is True
    fake_time[0] += bot.RECOMMENDATION_WINDOW_SECONDS + 1
    assert bot._under_recommendation_limit(chat_id) is True


def test_handle_update_ignores_updates_without_a_message():
    called = []
    bot.handle_update({"edited_message": {"chat": {"id": 1}, "text": "/goal"}})
    assert called == []  # no crash, no dispatch


def test_handle_update_routes_start_to_handle_start(monkeypatch):
    called = []
    monkeypatch.setattr(bot, "handle_start", lambda chat_id, token: called.append((chat_id, token)))
    bot.handle_update({"message": {"chat": {"id": 5}, "text": "/start abc123"}})
    assert called == [(5, "abc123")]


def test_handle_update_start_without_token_prompts_from_settings(monkeypatch):
    sent = []
    monkeypatch.setattr(bot, "send_message", lambda chat_id, text: sent.append((chat_id, text)))
    bot.handle_update({"message": {"chat": {"id": 5}, "text": "/start"}})
    assert sent == [(5, "Open this link from FinFlow Settings to connect your account.")]


def test_handle_update_routes_plain_command_to_handle_command(monkeypatch):
    called = []
    monkeypatch.setattr(bot, "handle_command", lambda chat_id, text: called.append((chat_id, text)))
    bot.handle_update({"message": {"chat": {"id": 5}, "text": "/dbudget"}})
    assert called == [(5, "/dbudget")]


def test_handle_command_not_linked_prompts_to_connect(monkeypatch):
    monkeypatch.setattr(bot, "_lookup_user_id", lambda chat_id: None)
    sent = []
    monkeypatch.setattr(bot, "send_message", lambda chat_id, text: sent.append((chat_id, text)))
    bot.handle_command(5, "/goal")
    assert sent == [(5, "Not linked yet — connect your account from FinFlow Settings.")]


def test_handle_command_unknown_command_replies_with_help(monkeypatch):
    monkeypatch.setattr(bot, "_lookup_user_id", lambda chat_id: "user-1")
    sent = []
    monkeypatch.setattr(bot, "send_message", lambda chat_id, text: sent.append((chat_id, text)))
    bot.handle_command(5, "/nonsense")
    assert sent == [(5, "Unknown command. Try /goal, /dbudget, /mbudget, /recommendation.")]


def test_handle_command_dbudget_calls_compute_daily_budget(monkeypatch):
    monkeypatch.setattr(bot, "_lookup_user_id", lambda chat_id: "user-1")
    monkeypatch.setattr(bot, "compute_daily_budget", lambda user_id: {
        "daily_budget": 42.5, "breakdown": {"available": 900.0}
    })
    sent = []
    monkeypatch.setattr(bot, "send_message", lambda chat_id, text: sent.append((chat_id, text)))
    bot.handle_command(5, "/dbudget")
    assert sent == [(5, "Daily budget remaining: $42.50")]


def test_handle_command_recommendation_respects_rate_limit(monkeypatch):
    bot._recommendation_calls.clear()
    monkeypatch.setattr(bot, "_lookup_user_id", lambda chat_id: "user-1")
    monkeypatch.setattr(bot, "_under_recommendation_limit", lambda chat_id: False)
    sent = []
    monkeypatch.setattr(bot, "send_message", lambda chat_id, text: sent.append((chat_id, text)))
    bot.handle_command(5, "/recommendation")
    assert sent == [(5, "You've hit the recommendation limit for now — try again in a bit.")]
