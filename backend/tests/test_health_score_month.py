from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import app.api.health_score as hs
from app.api.dependencies import get_current_user
from main import app


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: {"id": "u1"}
    yield TestClient(app)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.parametrize("bad", ["2026-13", "abc", "2026-8"])
def test_rejects_malformed_month(client, bad):
    assert client.get(f"/health-score?month={bad}").status_code == 422


def test_past_month_skips_paid_ai_tip_current_month_keeps_it(client):
    tip = MagicMock(return_value="tip")
    with patch.object(hs, "fetch_all", return_value=[]), patch.object(hs, "supabase", MagicMock()), patch.object(hs, "_ai_tip", tip):
        past = client.get("/health-score?month=2020-01").json()
        assert past["month"] == "January 2020" and past["ai_tip"] is None
        tip.assert_not_called()

        cur = client.get(f"/health-score?month={date.today():%Y-%m}").json()
        assert cur["ai_tip"] == "tip"
