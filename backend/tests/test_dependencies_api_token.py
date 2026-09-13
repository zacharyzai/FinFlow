import pytest
from fastapi import HTTPException

from app.api import dependencies as deps


def test_get_current_user_via_api_token_returns_user_for_valid_token(monkeypatch):
    monkeypatch.setattr(deps, "resolve_token", lambda token: "user-1")
    import asyncio

    result = asyncio.run(deps.get_current_user_via_api_token("valid-token"))

    assert result == {"id": "user-1", "email": None, "auth_method": "api_token"}


def test_get_current_user_via_api_token_rejects_invalid_token(monkeypatch):
    monkeypatch.setattr(deps, "resolve_token", lambda token: None)
    import asyncio

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(deps.get_current_user_via_api_token("bad-token"))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["code"] == "auth_error"


def test_get_current_user_or_api_token_prefers_api_token_when_present(monkeypatch):
    monkeypatch.setattr(deps, "resolve_token", lambda token: "user-9")
    import asyncio

    result = asyncio.run(
        deps.get_current_user_or_api_token(x_api_token="tok", authorization="")
    )

    assert result == {"id": "user-9", "email": None, "auth_method": "api_token"}


def test_get_current_user_or_api_token_falls_back_to_jwt(monkeypatch):
    async def fake_get_current_user(authorization):
        assert authorization == "Bearer good-jwt"
        return {"id": "user-2", "email": "a@b.com", "auth_method": "jwt"}

    monkeypatch.setattr(deps, "get_current_user", fake_get_current_user)
    import asyncio

    result = asyncio.run(
        deps.get_current_user_or_api_token(x_api_token="", authorization="Bearer good-jwt")
    )

    assert result == {"id": "user-2", "email": "a@b.com", "auth_method": "jwt"}
