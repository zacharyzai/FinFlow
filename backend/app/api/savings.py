from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.dependencies import get_current_user
from app.core.database import supabase
from app.core.errors import app_error

router = APIRouter(prefix="/savings", tags=["savings"])
limiter = Limiter(key_func=get_remote_address)


class SavingsGoalIn(BaseModel):
    name: str
    target: float
    deadline: str  # YYYY-MM-DD
    saved: float = 0.0


class SavingsGoalPatch(BaseModel):
    saved: float


def _enrich_goal(goal: dict) -> dict:
    """Add progress_pct and monthly_required to a goal dict."""
    today = date.today()
    target = float(goal["target"])
    saved = float(goal["saved"] or 0)

    goal["progress_pct"] = min(100, round(saved / target * 100, 1)) if target > 0 else 0

    try:
        deadline = date.fromisoformat(goal["deadline"])
        months_remaining = max(1, (deadline.year - today.year) * 12 + (deadline.month - today.month))
    except Exception:
        months_remaining = 1

    remaining = max(0, target - saved)
    goal["monthly_required"] = round(remaining / months_remaining, 2)
    goal["months_remaining"] = months_remaining
    return goal


@router.get("")
@limiter.limit("30/minute")
async def list_goals(request: Request, current_user: dict = Depends(get_current_user)):
    result = (
        supabase.table("savings_goals")
        .select("*")
        .eq("user_id", current_user["id"])
        .order("deadline", desc=False)
        .execute()
    )
    return {"goals": [_enrich_goal(g) for g in result.data]}


@router.post("")
@limiter.limit("30/minute")
async def create_goal(
    request: Request,
    body: SavingsGoalIn,
    current_user: dict = Depends(get_current_user),
):
    if body.target <= 0:
        raise app_error(400, "invalid_input", "Target must be greater than 0")
    if body.saved < 0:
        raise app_error(400, "invalid_input", "Saved amount cannot be negative")

    result = (
        supabase.table("savings_goals")
        .insert({
            "user_id": current_user["id"],
            "name": body.name,
            "target": body.target,
            "saved": body.saved,
            "deadline": body.deadline,
        })
        .execute()
    )
    return {"goal": _enrich_goal(result.data[0])}


@router.patch("/{id}")
@limiter.limit("30/minute")
async def update_saved(
    request: Request,
    id: str,
    body: SavingsGoalPatch,
    current_user: dict = Depends(get_current_user),
):
    existing = (
        supabase.table("savings_goals")
        .select("*")
        .eq("id", id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    if not existing.data:
        raise app_error(404, "not_found", "Goal not found")
    if body.saved < 0:
        raise app_error(400, "invalid_input", "Saved amount cannot be negative")

    result = (
        supabase.table("savings_goals")
        .update({"saved": body.saved})
        .eq("id", id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    return {"goal": _enrich_goal(result.data[0])}


@router.delete("/{id}")
@limiter.limit("30/minute")
async def delete_goal(
    request: Request,
    id: str,
    current_user: dict = Depends(get_current_user),
):
    existing = (
        supabase.table("savings_goals")
        .select("id")
        .eq("id", id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    if not existing.data:
        raise app_error(404, "not_found", "Goal not found")

    supabase.table("savings_goals").delete().eq("id", id).eq("user_id", current_user["id"]).execute()
    return {"deleted": id}
