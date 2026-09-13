from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import api_tokens
from app.api.dependencies import get_current_user


def _client_as(user_id="user-1"):
    app = FastAPI()
    app.include_router(api_tokens.router)
    app.dependency_overrides[get_current_user] = lambda: {"id": user_id, "email": "a@b.com"}
    return TestClient(app)


def test_create_token_returns_raw_token(monkeypatch):
    monkeypatch.setattr(api_tokens, "generate_token", lambda user_id: "raw-token-abc")
    client = _client_as()

    response = client.post("/api-tokens")

    assert response.status_code == 200
    assert response.json() == {"token": "raw-token-abc"}


def test_status_reports_active_when_token_exists(monkeypatch):
    monkeypatch.setattr(api_tokens, "has_token", lambda user_id: True)
    client = _client_as()

    response = client.get("/api-tokens/status")

    assert response.json() == {"active": True}


def test_status_reports_inactive_when_no_token(monkeypatch):
    monkeypatch.setattr(api_tokens, "has_token", lambda user_id: False)
    client = _client_as()

    response = client.get("/api-tokens/status")

    assert response.json() == {"active": False}


def test_delete_revokes_token(monkeypatch):
    revoked = []
    monkeypatch.setattr(api_tokens, "revoke_token", lambda user_id: revoked.append(user_id))
    client = _client_as(user_id="user-42")

    response = client.delete("/api-tokens")

    assert response.status_code == 200
    assert response.json() == {"revoked": True}
    assert revoked == ["user-42"]
