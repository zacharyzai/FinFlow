# Quick-Add Expense Shortcut Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the user log a spend from an iOS Shortcut (triggered by Back Tap) straight into FinFlow's existing transaction pipeline, authenticated by a long-lived personal access token instead of a browser-refreshed Supabase JWT.

**Architecture:** A new `api_tokens` table + service module issues/hashes/validates a per-user token. A new dependency accepts that token as an *additional* auth path on `POST /transactions` only — every other endpoint keeps JWT-only auth. No new frontend page; Settings gets a Generate/Revoke UI block. The iOS Shortcut itself is built manually by the user in the Shortcuts app, not code.

**Tech Stack:** FastAPI (Python, backend), Vue 3 `<script setup>` (frontend), Supabase/Postgres, pytest, `hashlib`/`secrets` (stdlib) for token hashing/generation.

**Spec:** `docs/superpowers/specs/2026-09-13-quick-add-shortcut-design.md`

## Global Constraints

- Never store or log the raw token — only its SHA-256 hash persists; log lines must never include the `X-API-Token` header value or the token string.
- The token auth path is added ONLY to `POST /transactions`. Every other endpoint (`GET`/`PATCH /transactions`, budget, savings, analytics, telegram, statements) must continue to accept only the existing JWT (`get_current_user`), unmodified.
- One active token per user — generating a new token deletes any existing row for that user first, so old tokens stop working immediately.
- A request authenticated via API token may only create `"type": "withdrawal"` transactions — reject `"credit"` with a 403. This is what makes the security note in the spec ("bounded in impact... can only create withdrawal transactions") actually true, not just documented intent.
- Do not commit any files during this work (per explicit user instruction this session).
- Cap any fix→re-review cycle at 2 loops per task; if a task still has open issues after 2 rounds, stop and surface it rather than continuing to iterate.

---

## File Structure

- `supabase/migrations/schema.sql` — modified: add `api_tokens` table, RLS policy, grants (in the same style as the existing `telegram_links` block).
- `backend/app/services/api_tokens.py` — new: token hashing, generation, resolution, revocation. Pure functions over `supabase`, no HTTP concerns — mirrors `telegram_bot.py`'s separation of service logic from the router.
- `backend/tests/test_api_tokens_service.py` — new: unit tests for the service module.
- `backend/app/api/api_tokens.py` — new: `POST /api-tokens`, `GET /api-tokens/status`, `DELETE /api-tokens` — mirrors `telegram.py`'s shape (thin router calling the service module).
- `backend/tests/test_api_tokens_router.py` — new: endpoint tests via `TestClient` + `dependency_overrides`, mirroring `test_telegram_webhook_security.py`.
- `backend/app/api/dependencies.py` — modified: add `get_current_user_via_api_token` and `get_current_user_or_api_token`.
- `backend/tests/test_dependencies_api_token.py` — new: unit tests for the two new dependency functions.
- `backend/app/api/transactions.py` — modified: `POST ''` (create_transaction) swaps `Depends(get_current_user)` for `Depends(get_current_user_or_api_token)`, and rejects non-withdrawal transactions when authenticated via token.
- `backend/tests/test_transactions_api_token.py` — new: covers the dual-auth behavior on `create_transaction` (JWT path unaffected, valid token creates a withdrawal, token + credit type is rejected, invalid token is rejected).
- `backend/main.py` — modified: register the new `api_tokens` router.
- `frontend/src/services/api.js` — modified: add `apiTokensApi` (status/create/revoke).
- `frontend/src/views/SettingsView.vue` — modified: add a Quick-Add Token section below the existing Telegram block.

---

### Task 1: `api_tokens` table

**Files:**
- Modify: `supabase/migrations/schema.sql`

**Interfaces:**
- Produces: table `public.api_tokens(id, user_id, token_hash, created_at, last_used_at)`, unique index on `user_id`, RLS owner-access policy — consumed by Task 2's service module via the existing `supabase` client (`backend/app/core/database.py`, already imported project-wide).

- [ ] **Step 1: Add the table definition to `schema.sql`, right after the `telegram_links` block**

Find this exact text in `schema.sql`:
```sql
create trigger telegram_links_updated_at
  before update on public.telegram_links
  for each row execute procedure public.set_updated_at();


-- Row Level Security
```
Replace it with:
```sql
create trigger telegram_links_updated_at
  before update on public.telegram_links
  for each row execute procedure public.set_updated_at();

-- 9. api_tokens
--    One row per user; holds a SHA-256 hash of a long-lived personal access
--    token used by the iOS Quick-Add Shortcut to authenticate POST /transactions
--    without a browser-refreshed Supabase JWT. Only one active token per user —
--    generating a new one deletes the old row first (see app/services/api_tokens.py).

create table public.api_tokens (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  token_hash    text not null,
  created_at    timestamptz not null default now(),
  last_used_at  timestamptz
);

create unique index api_tokens_user_id_idx on public.api_tokens(user_id);


-- Row Level Security
```

- [ ] **Step 2: Add RLS enable + owner policy**

Find:
```sql
alter table public.telegram_links     enable row level security;
```
Replace with:
```sql
alter table public.telegram_links     enable row level security;
alter table public.api_tokens         enable row level security;
```

Find:
```sql
create policy "telegram_links: owner access"
  on public.telegram_links for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);
```
Replace with:
```sql
create policy "telegram_links: owner access"
  on public.telegram_links for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "api_tokens: owner access"
  on public.api_tokens for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);
```

- [ ] **Step 3: Apply it to the live Supabase project**

`schema.sql` is not auto-applied (no linked Supabase CLI in this project — confirmed during Telegram verification). Give the user this exact SQL to paste into the Supabase Dashboard → SQL Editor (includes grants up front this time — the Telegram table needed a follow-up grant fix, so bake it in from the start here):

```sql
create table public.api_tokens (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  token_hash    text not null,
  created_at    timestamptz not null default now(),
  last_used_at  timestamptz
);

create unique index api_tokens_user_id_idx on public.api_tokens(user_id);

alter table public.api_tokens enable row level security;

create policy "api_tokens: owner access"
  on public.api_tokens for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

grant select, insert, update, delete on public.api_tokens to authenticated;
grant select, insert, update, delete on public.api_tokens to service_role;

notify pgrst, 'reload schema';
```

Wait for the user to confirm they've run it before proceeding to Task 2.

- [ ] **Step 4: Verify the table is reachable**

Run (from `backend/`, with the venv):
```bash
.venv/bin/python -c "
from app.core.database import supabase
r = supabase.table('api_tokens').select('id').limit(1).execute()
print('OK, table reachable:', r.data)
"
```
Expected: `OK, table reachable: []` — no `APIError` about a missing table (PGRST205) or permission denied (42501).

---

### Task 2: Token service module

**Files:**
- Create: `backend/app/services/api_tokens.py`
- Test: `backend/tests/test_api_tokens_service.py`

**Interfaces:**
- Consumes: `app.core.database.supabase` (existing client).
- Produces (used by Task 3's router and Task 4's dependency):
  - `generate_token(user_id: str) -> str` — returns the raw token (only time it's ever visible).
  - `resolve_token(raw_token: str) -> str | None` — returns `user_id` or `None`.
  - `revoke_token(user_id: str) -> None`
  - `has_token(user_id: str) -> bool`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_api_tokens_service.py`:
```python
import hashlib

from app.services import api_tokens as svc


class _FakeQuery:
    """Minimal stand-in for the supabase-py chainable query builder."""

    def __init__(self, rows, log):
        self._rows = rows
        self._log = log

    def select(self, *a, **k):
        return self

    def eq(self, *a, **k):
        self._log.append(("eq", a, k))
        return self

    def insert(self, data):
        self._log.append(("insert", data))
        return self

    def update(self, data):
        self._log.append(("update", data))
        return self

    def delete(self):
        self._log.append(("delete",))
        return self

    def execute(self):
        return type("Result", (), {"data": self._rows})()


class _FakeSupabase:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.log = []

    def table(self, name):
        assert name == "api_tokens"
        return _FakeQuery(self.rows, self.log)


def test_generate_token_deletes_existing_row_then_inserts_hash(monkeypatch):
    fake = _FakeSupabase()
    monkeypatch.setattr(svc, "supabase", fake)

    token = svc.generate_token("user-1")

    assert isinstance(token, str) and len(token) > 20
    assert fake.log[0] == ("delete",)
    assert fake.log[1][0] == "insert"
    inserted = fake.log[1][1]
    assert inserted["user_id"] == "user-1"
    assert inserted["token_hash"] == hashlib.sha256(token.encode("utf-8")).hexdigest()
    assert "token_hash" in inserted and inserted["token_hash"] != token  # never store the raw token


def test_resolve_token_returns_user_id_for_valid_token(monkeypatch):
    token = "raw-token-value"
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    fake = _FakeSupabase(rows=[{"id": "row-1", "user_id": "user-1"}])
    monkeypatch.setattr(svc, "supabase", fake)

    user_id = svc.resolve_token(token)

    assert user_id == "user-1"
    # last_used_at should have been updated
    assert any(entry[0] == "update" for entry in fake.log)


def test_resolve_token_returns_none_for_unknown_token(monkeypatch):
    fake = _FakeSupabase(rows=[])
    monkeypatch.setattr(svc, "supabase", fake)

    assert svc.resolve_token("no-such-token") is None


def test_revoke_token_deletes_the_row(monkeypatch):
    fake = _FakeSupabase()
    monkeypatch.setattr(svc, "supabase", fake)

    svc.revoke_token("user-1")

    assert fake.log[0] == ("delete",)


def test_has_token_true_when_row_exists(monkeypatch):
    fake = _FakeSupabase(rows=[{"id": "row-1"}])
    monkeypatch.setattr(svc, "supabase", fake)
    assert svc.has_token("user-1") is True


def test_has_token_false_when_no_row(monkeypatch):
    fake = _FakeSupabase(rows=[])
    monkeypatch.setattr(svc, "supabase", fake)
    assert svc.has_token("user-1") is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && .venv/bin/python -m pytest tests/test_api_tokens_service.py -v
```
Expected: `ModuleNotFoundError: No module named 'app.services.api_tokens'` (or import error) — the module doesn't exist yet.

- [ ] **Step 3: Implement the service module**

Create `backend/app/services/api_tokens.py`:
```python
"""
Quick-Add Shortcut personal access tokens: generation, hashing, and
resolution. One active token per user — generating a new one replaces
the old row, so a leaked/old token stops working immediately.

The raw token is never stored — only its SHA-256 hash. SHA-256 (not a
slow password hash like bcrypt) is correct here because the token is
already high-entropy random data, not a human-guessable password.
"""
import hashlib
import secrets
from datetime import datetime, timezone

from app.core.database import supabase


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_token(user_id: str) -> str:
    """Create (or replace) this user's single active quick-add token.

    Returns the raw token — this is the only time it is ever visible;
    only its hash is persisted.
    """
    token = secrets.token_urlsafe(32)
    token_hash = _hash_token(token)

    supabase.table("api_tokens").delete().eq("user_id", user_id).execute()
    supabase.table("api_tokens").insert({"user_id": user_id, "token_hash": token_hash}).execute()
    return token


def resolve_token(raw_token: str) -> str | None:
    """Look up the user_id for a raw token, or None if invalid/revoked."""
    token_hash = _hash_token(raw_token)
    result = supabase.table("api_tokens").select("id", "user_id").eq("token_hash", token_hash).execute()
    if not result.data:
        return None

    row = result.data[0]
    supabase.table("api_tokens").update(
        {"last_used_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", row["id"]).execute()
    return row["user_id"]


def revoke_token(user_id: str) -> None:
    supabase.table("api_tokens").delete().eq("user_id", user_id).execute()


def has_token(user_id: str) -> bool:
    result = supabase.table("api_tokens").select("id").eq("user_id", user_id).execute()
    return bool(result.data)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && .venv/bin/python -m pytest tests/test_api_tokens_service.py -v
```
Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

Per user instruction, do NOT commit. Skip this step — leave changes uncommitted in the working tree.

---

### Task 3: Token router (`/api-tokens` endpoints)

**Files:**
- Create: `backend/app/api/api_tokens.py`
- Test: `backend/tests/test_api_tokens_router.py`
- Modify: `backend/main.py` (register router)

**Interfaces:**
- Consumes: `generate_token`, `has_token`, `revoke_token` from Task 2; `get_current_user`, `limiter` from `app.api.dependencies` (existing).
- Produces: `POST /api-tokens` → `{"token": str}`; `GET /api-tokens/status` → `{"active": bool}`; `DELETE /api-tokens` → `{"revoked": True}`.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_api_tokens_router.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && .venv/bin/python -m pytest tests/test_api_tokens_router.py -v
```
Expected: `ModuleNotFoundError: No module named 'app.api.api_tokens'`.

- [ ] **Step 3: Implement the router**

Create `backend/app/api/api_tokens.py`:
```python
"""
HTTP surface for the Quick-Add Shortcut's personal access token:
generate (shown once), check status, and revoke — all from FinFlow
Settings, all authenticated by the normal Supabase JWT (this is about
managing the token, not using it).
"""
from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_current_user, limiter
from app.services.api_tokens import generate_token, has_token, revoke_token

router = APIRouter(prefix="/api-tokens", tags=["api-tokens"])


@router.post("")
@limiter.limit("10/minute")
async def create_token(request: Request, current_user: dict = Depends(get_current_user)):
    token = generate_token(current_user["id"])
    return {"token": token}


@router.get("/status")
@limiter.limit("30/minute")
async def status(request: Request, current_user: dict = Depends(get_current_user)):
    return {"active": has_token(current_user["id"])}


@router.delete("")
@limiter.limit("10/minute")
async def delete_token(request: Request, current_user: dict = Depends(get_current_user)):
    revoke_token(current_user["id"])
    return {"revoked": True}
```

- [ ] **Step 4: Register the router in `main.py`**

Find:
```python
from app.api import analytics, budget, statements, telegram, transactions
```
Replace with:
```python
from app.api import analytics, api_tokens, budget, statements, telegram, transactions
```

Find:
```python
app.include_router(telegram.router)
```
Replace with:
```python
app.include_router(telegram.router)
app.include_router(api_tokens.router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend && .venv/bin/python -m pytest tests/test_api_tokens_router.py -v
```
Expected: all 4 tests PASS.

- [ ] **Step 6: Commit**

Per user instruction, do NOT commit. Skip this step.

---

### Task 4: Dual-auth dependency

**Files:**
- Modify: `backend/app/api/dependencies.py`
- Test: `backend/tests/test_dependencies_api_token.py`

**Interfaces:**
- Consumes: `resolve_token` from Task 2 (`app.services.api_tokens`); existing `get_current_user`, `app_error`.
- Produces (used by Task 5): `get_current_user_via_api_token(x_api_token: str) -> dict` (raises `app_error(401, ...)` if invalid); `get_current_user_or_api_token(x_api_token: str = Header(default=""), authorization: str = Header(default="")) -> dict`. Both return a dict shaped `{"id": str, "email": str | None, "auth_method": "jwt" | "api_token"}`.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_dependencies_api_token.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && .venv/bin/python -m pytest tests/test_dependencies_api_token.py -v
```
Expected: `AttributeError: module 'app.api.dependencies' has no attribute 'get_current_user_via_api_token'`.

- [ ] **Step 3: Implement the dependencies**

In `backend/app/api/dependencies.py`, add the import and two functions. The existing `get_current_user` also needs `"auth_method": "jwt"` added to its return dict so both paths return the same shape:

Find:
```python
from fastapi import Header
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import supabase
from app.core.errors import app_error
```
Replace with:
```python
from fastapi import Header
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import supabase
from app.core.errors import app_error
from app.services.api_tokens import resolve_token
```

Find:
```python
    if response.user is None:
        raise app_error(401, "auth_error", "Invalid or expired token")
    return {"id": response.user.id, "email": response.user.email}
```
Replace with:
```python
    if response.user is None:
        raise app_error(401, "auth_error", "Invalid or expired token")
    return {"id": response.user.id, "email": response.user.email, "auth_method": "jwt"}


async def get_current_user_via_api_token(x_api_token: str) -> dict:
    """Resolve a Quick-Add Shortcut personal access token to a user."""
    user_id = resolve_token(x_api_token)
    if user_id is None:
        raise app_error(401, "auth_error", "Invalid or revoked API token")
    return {"id": user_id, "email": None, "auth_method": "api_token"}


async def get_current_user_or_api_token(
    x_api_token: str = Header(default=""),
    authorization: str = Header(default=""),
) -> dict:
    """
    Auth for POST /transactions only: accepts either the Quick-Add
    Shortcut's personal access token (X-API-Token header) or the normal
    Supabase JWT (Authorization header). Every other endpoint in this
    app continues to depend on get_current_user directly — this wrapper
    must not be substituted in anywhere else.
    """
    if x_api_token:
        return await get_current_user_via_api_token(x_api_token)
    return await get_current_user(authorization)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && .venv/bin/python -m pytest tests/test_dependencies_api_token.py -v
```
Expected: all 4 tests PASS.

- [ ] **Step 5: Run the full existing test suite to confirm nothing else broke**

```bash
cd backend && .venv/bin/python -m pytest -v
```
Expected: all tests PASS, including the pre-existing Telegram tests (the `auth_method` key added to `get_current_user`'s return dict is additive and must not break any test asserting the old two-key shape — if one does, update that assertion to include `"auth_method": "jwt"`).

- [ ] **Step 6: Commit**

Per user instruction, do NOT commit. Skip this step.

---

### Task 5: Wire the dependency into `POST /transactions`

**Files:**
- Modify: `backend/app/api/transactions.py`
- Test: `backend/tests/test_transactions_api_token.py`

**Interfaces:**
- Consumes: `get_current_user_or_api_token` from Task 4; existing `_get_or_create_account`, `_insert_ledger_entries` from `app.api.statements` (unchanged).
- Produces: `POST /transactions` now accepts either auth method; rejects `type: "credit"` with 403 when authenticated via API token.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_transactions_api_token.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && .venv/bin/python -m pytest tests/test_transactions_api_token.py -v
```
Expected: `test_create_transaction_via_api_token_rejects_credit_type` FAILS (endpoint currently accepts credit regardless of auth method) — the other two may pass already since the endpoint's behavior is otherwise unchanged; that's fine, the important one is the credit-rejection test.

- [ ] **Step 3: Implement the change**

In `backend/app/api/transactions.py`, find:
```python
from app.api.dependencies import VALID_CATEGORIES, get_current_user, limiter
```
Replace with:
```python
from app.api.dependencies import VALID_CATEGORIES, get_current_user, get_current_user_or_api_token, limiter
```

Find:
```python
@router.post('')
@limiter.limit("30/minute")
async def create_transaction(
    request: Request,
    body: TransactionIn,
    current_user: dict = Depends(get_current_user),
):
    if body.category not in VALID_CATEGORIES:
        body.category = "Other"
```
Replace with:
```python
@router.post('')
@limiter.limit("30/minute")
async def create_transaction(
    request: Request,
    body: TransactionIn,
    current_user: dict = Depends(get_current_user_or_api_token),
):
    if current_user.get("auth_method") == "api_token" and body.type != "withdrawal":
        raise app_error(403, "invalid_input", "The Quick-Add token can only log withdrawals.")

    if body.category not in VALID_CATEGORIES:
        body.category = "Other"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && .venv/bin/python -m pytest tests/test_transactions_api_token.py -v
```
Expected: all 3 tests PASS.

- [ ] **Step 5: Run the full backend suite one more time**

```bash
cd backend && .venv/bin/python -m pytest -v
```
Expected: all tests PASS (existing `PATCH`/`GET /transactions` tests, if any exist elsewhere, remain untouched since only the `POST ''` dependency changed).

- [ ] **Step 6: Commit**

Per user instruction, do NOT commit. Skip this step.

---

### Task 6: Settings UI — Generate/Revoke Quick-Add Token

**Files:**
- Modify: `frontend/src/services/api.js`
- Modify: `frontend/src/views/SettingsView.vue`

**Interfaces:**
- Consumes: `api` (axios instance), `apiErrorMessage` — both already exported from `api.js`.
- Produces: `apiTokensApi.status()`, `.create()`, `.revoke()` — same shape as the existing `telegramApi`.

- [ ] **Step 1: Add `apiTokensApi` to `api.js`**

Find:
```javascript
export const telegramApi = {
  linkUrl: () => api.post('/telegram/link-token'),
  status: () => api.get('/telegram/status'),
  disconnect: () => api.delete('/telegram/link'),
}
```
Replace with:
```javascript
export const telegramApi = {
  linkUrl: () => api.post('/telegram/link-token'),
  status: () => api.get('/telegram/status'),
  disconnect: () => api.delete('/telegram/link'),
}

export const apiTokensApi = {
  status: () => api.get('/api-tokens/status'),
  create: () => api.post('/api-tokens'),
  revoke: () => api.delete('/api-tokens'),
}
```

- [ ] **Step 2: Add the Quick-Add Token section to `SettingsView.vue`**

Find:
```html
          <p v-if="error" class="text-[var(--bad)] text-xs mt-3">{{ error }}</p>
        </div>
      </main>
```
Replace with:
```html
          <p v-if="error" class="text-[var(--bad)] text-xs mt-3">{{ error }}</p>
        </div>

        <div class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-5 mt-4">
          <h2 class="text-sm font-semibold text-[var(--text)] mb-1">Quick-Add Token</h2>
          <p class="text-xs text-[var(--text-3)] mb-4">
            A long-lived key for an iOS Shortcut to log expenses directly, without opening the app.
          </p>

          <div v-if="generatedToken" class="mb-3">
            <p class="text-xs text-[var(--bad)] mb-2">Copy this now — it won't be shown again.</p>
            <code class="block text-xs bg-[var(--surface-3)] rounded-lg p-3 break-all">{{ generatedToken }}</code>
          </div>

          <div v-else-if="tokenActive" class="flex items-center justify-between">
            <span class="text-sm text-[var(--good)] font-medium">Active</span>
            <button @click="revokeToken" :disabled="tokenBusy"
                    class="px-4 py-1.5 rounded-full border border-[var(--border)] text-[var(--text-2)] text-sm hover:bg-[var(--surface-3)] disabled:opacity-50 cursor-pointer transition-colors">
              {{ tokenBusy ? 'Revoking…' : 'Revoke' }}
            </button>
          </div>

          <div v-else>
            <button @click="generateToken" :disabled="tokenBusy"
                    class="px-4 py-2 rounded-full bg-[var(--brand)] hover:bg-[var(--brand-strong)] text-white text-sm font-semibold disabled:opacity-50 cursor-pointer transition-colors">
              {{ tokenBusy ? 'Generating…' : 'Generate Quick-Add Token' }}
            </button>
          </div>

          <p v-if="tokenError" class="text-[var(--bad)] text-xs mt-3">{{ tokenError }}</p>
        </div>
      </main>
```

Find:
```javascript
import { telegramApi, apiErrorMessage } from '@/services/api'
```
Replace with:
```javascript
import { telegramApi, apiTokensApi, apiErrorMessage } from '@/services/api'
```

Find:
```javascript
onMounted(refreshStatus)
```
Replace with:
```javascript
const tokenActive = ref(false)
const tokenBusy = ref(false)
const tokenError = ref('')
const generatedToken = ref('')

async function refreshTokenStatus() {
  tokenError.value = ''
  try {
    const { data } = await apiTokensApi.status()
    tokenActive.value = data.active
  } catch (e) {
    tokenError.value = apiErrorMessage(e)
  }
}

async function generateToken() {
  tokenBusy.value = true
  tokenError.value = ''
  try {
    const { data } = await apiTokensApi.create()
    generatedToken.value = data.token
    tokenActive.value = true
  } catch (e) {
    tokenError.value = apiErrorMessage(e)
  } finally {
    tokenBusy.value = false
  }
}

async function revokeToken() {
  tokenBusy.value = true
  tokenError.value = ''
  try {
    await apiTokensApi.revoke()
    tokenActive.value = false
    generatedToken.value = ''
  } catch (e) {
    tokenError.value = apiErrorMessage(e)
  } finally {
    tokenBusy.value = false
  }
}

onMounted(() => {
  refreshStatus()
  refreshTokenStatus()
})
```

(Add the necessary `ref` import if not already present — `ref` and `onMounted` are already imported at the top of this file from the existing Telegram block, so no import changes needed here.)

- [ ] **Step 3: Manual verification (no frontend test framework exists in this project)**

1. Start the backend (`cd backend && .venv/bin/python -m uvicorn main:app --reload`) and frontend (`cd frontend && npm run dev`).
2. Open Settings in the browser, logged in.
3. Click **Generate Quick-Add Token** — confirm a token string appears with the "won't be shown again" warning.
4. Refresh the page — confirm it now shows **Active** / **Revoke** (not the raw token again — it should not be re-displayed).
5. Click **Revoke** — confirm it flips back to the **Generate** button.
6. Check the backend terminal output during all of this — confirm the raw token value never appears in any log line.

- [ ] **Step 4: Commit**

Per user instruction, do NOT commit. Skip this step.

---

### Task 7: Manual end-to-end verification (the actual iOS Shortcut)

No code — this is the user building the Shortcut in the iOS Shortcuts app and confirming the whole chain works. Not a coding task, but the plan isn't done until this is confirmed.

- [ ] **Step 1:** Generate a token from Settings (Task 6) and copy it.
- [ ] **Step 2:** In the Shortcuts app, create a new Shortcut:
  - Action 1: **Choose from Menu** — list the categories from `VALID_CATEGORIES` minus Income/Transfer (Food & Dining, Transport, Shopping, Bills & Utilities, Healthcare, Entertainment, Travel, Education, Other).
  - Action 2: **Ask for Input** (Number) — the amount.
  - Action 3: **Get Contents of URL** — POST to `https://<your-backend-domain>/transactions`, headers `X-API-Token: <the copied token>` and `Content-Type: application/json`, JSON body `{"date": "<today>", "description": "Quick add", "amount": <the number input>, "type": "withdrawal", "category": "<the chosen menu item>"}` (use the Shortcuts "Current Date" and text-formatting actions to build the ISO date).
- [ ] **Step 3:** Settings → Accessibility → Touch → Back Tap → Double Tap → select this Shortcut.
- [ ] **Step 4:** Double-tap the back of the phone. Confirm the category menu and amount prompt appear with no app switch.
- [ ] **Step 5:** Check the FinFlow dashboard/transactions list — confirm the new transaction appears within seconds.
- [ ] **Step 6:** Revoke the token from Settings, trigger the Shortcut again — confirm it now fails (Shortcuts will show an HTTP error), proving revocation actually cuts off access.

---

## Self-Review Notes

- **Spec coverage:** every section of the spec maps to a task — `api_tokens` table → Task 1; token generation/hashing/revocation → Task 2; the three endpoints → Task 3; the dual-auth dependency → Task 4; wiring into `POST /transactions` + the credit-type restriction (which makes the spec's own security claim true) → Task 5; Settings UI → Task 6; the Shortcut itself → Task 7.
- **No placeholders:** every step has real code, not "add appropriate handling."
- **Type/signature consistency checked:** `get_current_user`'s return dict gained `"auth_method": "jwt"` in Task 4 — Task 5's tests and the transactions handler both rely on reading `current_user.get("auth_method")`, consistent with that shape. `resolve_token` returns `str | None` in Task 2 and is consumed exactly that way in Task 4.
