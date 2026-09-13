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
