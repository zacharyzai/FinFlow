from app.services import telegram_client


def test_send_message_posts_to_telegram_api(monkeypatch):
    monkeypatch.setattr(telegram_client, "TELEGRAM_BOT_TOKEN", "test-token")
    calls = []
    monkeypatch.setattr(
        telegram_client.requests, "post",
        lambda url, json, timeout: calls.append((url, json, timeout)),
    )

    telegram_client.send_message(42, "hello")

    assert len(calls) == 1
    url, payload, timeout = calls[0]
    assert url == "https://api.telegram.org/bottest-token/sendMessage"
    assert payload == {"chat_id": 42, "text": "hello"}
    assert timeout == 10


def test_send_message_skips_when_token_missing(monkeypatch):
    monkeypatch.setattr(telegram_client, "TELEGRAM_BOT_TOKEN", None)
    calls = []
    monkeypatch.setattr(telegram_client.requests, "post", lambda *a, **k: calls.append(1))

    telegram_client.send_message(42, "hello")

    assert calls == []


def test_send_message_never_raises_on_network_error(monkeypatch):
    monkeypatch.setattr(telegram_client, "TELEGRAM_BOT_TOKEN", "test-token")

    def boom(*a, **k):
        raise ConnectionError("network down")

    monkeypatch.setattr(telegram_client.requests, "post", boom)

    telegram_client.send_message(42, "hello")  # must not raise
