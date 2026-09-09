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


def test_handle_update_ignores_updates_without_a_message(monkeypatch):
    called = []
    monkeypatch.setattr(bot, "handle_start", lambda *a, **k: called.append("handle_start"))
    monkeypatch.setattr(bot, "handle_command", lambda *a, **k: called.append("handle_command"))
    bot.handle_update({"edited_message": {"chat": {"id": 1}, "text": "/goal"}})
    assert called == []  # dispatch was actually skipped, not just no exception


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


class _FakeQuery:
    """Minimal stand-in for the supabase-py chainable query builder."""

    def __init__(self, rows):
        self._rows = rows

    def select(self, *a, **k):
        return self

    def eq(self, *a, **k):
        return self

    def update(self, *a, **k):
        raise AssertionError("update() should not be called when chat_id belongs to another user")

    def execute(self):
        return type("Result", (), {"data": self._rows})()


class _FakeSupabase:
    """Returns canned rows keyed by table name, ignoring filters."""

    def __init__(self, rows_by_table):
        self._rows_by_table = rows_by_table

    def table(self, name):
        return _FakeQuery(self._rows_by_table.get(name, []))


def test_handle_start_refuses_to_relink_chat_already_owned_by_another_user(monkeypatch):
    # token row belongs to "row-b" (the linking user); the same chat_id is
    # already linked to a different row ("row-a") — both queries hit the same
    # fake table, so give it a row set that plausibly satisfies each .execute()
    # in call order via a stateful list instead of a static dict.
    calls = {"n": 0}

    class SequencedFakeSupabase:
        def table(self, name):
            calls["n"] += 1
            if calls["n"] == 1:
                # select by link_token -> the row currently being linked
                return _FakeQuery([{"id": "row-b", "token_expires_at": _future_iso()}])
            # select by chat_id -> already linked to a different row
            return _FakeQuery([{"id": "row-a"}])

    monkeypatch.setattr(bot, "supabase", SequencedFakeSupabase())
    sent = []
    monkeypatch.setattr(bot, "send_message", lambda chat_id, text: sent.append((chat_id, text)))

    bot.handle_start(chat_id=999, token="tok")

    assert len(sent) == 1
    assert "already linked to a different FinFlow account" in sent[0][1]


def _future_iso():
    return (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
