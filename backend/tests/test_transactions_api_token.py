from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import transactions
from app.api.dependencies import get_current_user_or_api_token


def _client_with_auth(user_dict):
    app = FastAPI()
    app.include_router(transactions.router)
    app.dependency_overrides[get_current_user_or_api_token] = lambda: user_dict
    return TestClient(app)


def _fake_insert(monkeypatch, tx_row):
    class _FakeInsertResult:
        data = [tx_row]

    class _FakeTable:
        def insert(self, record):
            return self

        def execute(self):
            return _FakeInsertResult()

    monkeypatch.setattr(transactions.supabase, "table", lambda name: _FakeTable())
    monkeypatch.setattr(transactions, "_get_or_create_account", lambda user_id, name: "account-1")
    monkeypatch.setattr(transactions, "_insert_ledger_entries", lambda user_id, txs: None)


def test_create_transaction_via_api_token_creates_withdrawal(monkeypatch):
    tx_row = {"id": "tx-1", "withdrawal": 12.5, "credit": None, "category": "Food & Dining"}
    _fake_insert(monkeypatch, tx_row)
    client = _client_with_auth({"id": "user-1", "email": None, "auth_method": "api_token"})

    response = client.post("/transactions", json={
        "date": "2026-09-13", "description": "Quick add", "amount": 12.5,
        "type": "withdrawal", "category": "Food & Dining",
    })

    assert response.status_code == 200
    assert response.json() == {"transaction": tx_row}


def test_create_transaction_via_api_token_rejects_credit_type(monkeypatch):
    _fake_insert(monkeypatch, {"id": "tx-2"})
    client = _client_with_auth({"id": "user-1", "email": None, "auth_method": "api_token"})

    response = client.post("/transactions", json={
        "date": "2026-09-13", "description": "Fake income", "amount": 500,
        "type": "credit", "category": "Income",
    })

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "invalid_input"


def test_create_transaction_via_jwt_still_allows_credit(monkeypatch):
    tx_row = {"id": "tx-3", "withdrawal": None, "credit": 500.0, "category": "Income"}
    _fake_insert(monkeypatch, tx_row)
    client = _client_with_auth({"id": "user-1", "email": "a@b.com", "auth_method": "jwt"})

    response = client.post("/transactions", json={
        "date": "2026-09-13", "description": "Paycheck", "amount": 500,
        "type": "credit", "category": "Income",
    })

    assert response.status_code == 200
    assert response.json() == {"transaction": tx_row}


def test_create_transaction_via_api_token_with_only_amount_and_category(monkeypatch):
    """The Quick-Add Shortcut only sends amount + category — date should
    default to today, description to 'Quick add', type to 'withdrawal'."""
    tx_row = {"id": "tx-defaults", "withdrawal": 4.5, "credit": None, "category": "Food & Dining"}
    captured = {}

    class _FakeInsertResult:
        data = [tx_row]

    class _FakeTable:
        def insert(self, record):
            captured["record"] = record
            return self

        def execute(self):
            return _FakeInsertResult()

    monkeypatch.setattr(transactions.supabase, "table", lambda name: _FakeTable())
    monkeypatch.setattr(transactions, "_get_or_create_account", lambda user_id, name: "account-1")
    monkeypatch.setattr(transactions, "_insert_ledger_entries", lambda user_id, txs: None)
    client = _client_with_auth({"id": "user-1", "email": None, "auth_method": "api_token"})

    response = client.post("/transactions", json={"amount": 4.5, "category": "Food & Dining"})

    assert response.status_code == 200
    assert captured["record"]["description"] == "Quick add"
    assert captured["record"]["withdrawal"] == 4.5
    assert captured["record"]["credit"] is None
    from datetime import datetime
    from zoneinfo import ZoneInfo
    assert captured["record"]["date"] == str(datetime.now(ZoneInfo("Asia/Singapore")).date())


def _real_client():
    """A TestClient wired to the real transactions router with no auth
    dependency override — requests go through the actual
    get_current_user_or_api_token → resolve_token chain."""
    app = FastAPI()
    app.include_router(transactions.router)
    return TestClient(app)


def test_real_dependency_chain_accepts_valid_api_token(monkeypatch):
    tx_row = {"id": "tx-4", "withdrawal": 9.0, "credit": None, "category": "Food & Dining"}
    _fake_insert(monkeypatch, tx_row)
    monkeypatch.setattr(
        "app.api.dependencies.resolve_token",
        lambda raw: "user-real" if raw == "fake-valid-token" else None,
    )
    client = _real_client()

    response = client.post(
        "/transactions",
        json={"date": "2026-09-13", "description": "Coffee", "amount": 9.0,
              "type": "withdrawal", "category": "Food & Dining"},
        headers={"X-API-Token": "fake-valid-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"transaction": tx_row}


def test_real_dependency_chain_rejects_unknown_api_token(monkeypatch):
    _fake_insert(monkeypatch, {"id": "tx-5"})
    monkeypatch.setattr(
        "app.api.dependencies.resolve_token",
        lambda raw: "user-real" if raw == "fake-valid-token" else None,
    )
    client = _real_client()

    response = client.post(
        "/transactions",
        json={"date": "2026-09-13", "description": "Coffee", "amount": 9.0,
              "type": "withdrawal", "category": "Food & Dining"},
        headers={"X-API-Token": "some-unknown-token"},
    )

    assert response.status_code == 401


def test_real_dependency_chain_rejects_credit_via_api_token(monkeypatch):
    _fake_insert(monkeypatch, {"id": "tx-6"})
    monkeypatch.setattr(
        "app.api.dependencies.resolve_token",
        lambda raw: "user-real" if raw == "fake-valid-token" else None,
    )
    client = _real_client()

    response = client.post(
        "/transactions",
        json={"date": "2026-09-13", "description": "Fake income", "amount": 500,
              "type": "credit", "category": "Income"},
        headers={"X-API-Token": "fake-valid-token"},
    )

    assert response.status_code == 403


def test_get_transactions_rejects_token_only_auth():
    """GET /transactions depends on get_current_user directly (not the
    dual-auth wrapper) — an X-API-Token header alone must not satisfy it.
    This guards the "token only works on POST /transactions" invariant."""
    client = _real_client()

    response = client.get("/transactions", headers={"X-API-Token": "fake-valid-token"})

    assert response.status_code == 422
