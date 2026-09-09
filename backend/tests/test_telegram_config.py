from app.core import config


def test_telegram_env_vars_exist():
    assert hasattr(config, "TELEGRAM_BOT_TOKEN")
    assert hasattr(config, "TELEGRAM_WEBHOOK_SECRET")
    assert hasattr(config, "TELEGRAM_BOT_USERNAME")
