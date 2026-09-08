from calendar import monthrange
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.api.dependencies import VALID_CATEGORIES, get_current_user, limiter
from app.core.database import supabase
from app.core.errors import app_error
from app.core.pagination import fetch_all

router = APIRouter(prefix="/budget", tags=["budget"])

DEFAULT_RECURRENCE_DAYS = 30  # "repeats monthly" — see PlannedExpenseIn.recurrence_days

class PlannedExpenseIn(BaseModel):
    name: str
    amount: float
    due_date: str # YYYY-MM-DD
    category: str
    is_recurring: bool = False
    recurrence_days: Optional[int] = None


def _next_occurrence(due_date: date, recurrence_days: int, on_or_after: date) -> date:
    """Project a recurring expense's due_date forward to the first occurrence on/after `on_or_after`."""
    if due_date >= on_or_after:
        return due_date
    days_behind = (on_or_after - due_date).days
    cycles = -(-days_behind // recurrence_days)  # ceil division, no float rounding
    return due_date + timedelta(days=cycles * recurrence_days)


def _effective_expenses(user_id: str, window_start: date, window_end: date) -> list[dict]:
    """
    Planned expenses whose EFFECTIVE due date falls within [window_start, window_end].

    Non-recurring expenses just need their due_date to land in the window. Recurring
    ones are fetched regardless of their original due_date and projected forward —
    otherwise a bill first entered months ago would silently stop appearing in any
    future month's budget the moment its original one-time due_date passed, even
    though it's marked is_recurring.
    """
    non_recurring = (
        supabase.table("planned_expenses")
        .select("id, name, amount, due_date, category")
        .eq("user_id", user_id).eq("is_recurring", False)
        .gte("due_date", str(window_start)).lte("due_date", str(window_end))
        .execute()
    ).data

    recurring = fetch_all(lambda: supabase.table("planned_expenses")
        .select("id, name, amount, due_date, category, recurrence_days")
        .eq("user_id", user_id).eq("is_recurring", True))

    projected = []
    for r in recurring:
        occurrence = _next_occurrence(
            date.fromisoformat(r["due_date"]),
            r.get("recurrence_days") or DEFAULT_RECURRENCE_DAYS,
            window_start,
        )
        if window_start <= occurrence <= window_end:
            projected.append({**r, "due_date": str(occurrence)})

    return sorted(non_recurring + projected, key=lambda e: e["due_date"])


# ----------------------------------------------------------------
# Upcoming expenses
# ----------------------------------------------------------------

@router.get("/upcoming")
@limiter.limit("30/minute")
async def upcoming_expenses(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    today = date.today()
    month_end = today.replace(day=monthrange(today.year, today.month)[1])

    expenses = _effective_expenses(current_user["id"], today, month_end)
    return {"expenses": expenses}


# ----------------------------------------------------------------
# Add a planned expense
# ----------------------------------------------------------------

@router.post("/expenses")
@limiter.limit("30/minute")
async def add_expense(
    request: Request,
    body: PlannedExpenseIn,
    current_user: dict = Depends(get_current_user),
):
    if body.amount <= 0:
        raise app_error(400, "invalid_input", "Amount must be greater than 0")

    # If category is not one of the preset options, default to "Other"
    category = body.category if body.category in VALID_CATEGORIES else "Other"
    recurrence_days = body.recurrence_days or (DEFAULT_RECURRENCE_DAYS if body.is_recurring else None)

    result = (
        supabase.table("planned_expenses")
        .insert({
            "user_id": current_user["id"],
            "name": body.name,
            "amount": body.amount,
            "due_date": body.due_date,
            "category": category,
            "is_recurring": body.is_recurring,
            "recurrence_days": recurrence_days,
        })
        .execute()
    )

    return {"expense": result.data[0]}


# ----------------------------------------------------------------
# Delete a planned expense
# ----------------------------------------------------------------

@router.delete("/expenses/{id}")
@limiter.limit("30/minute")
async def delete_expense(
    request: Request,
    id: str,
    current_user: dict = Depends(get_current_user),
):
    # Verify the expense belongs to this user before deleting
    existing = (
        supabase.table("planned_expenses")
        .select("id")
        .eq("id", id)
        .eq("user_id", current_user["id"])
        .execute()
    )

    if not existing.data:
        raise app_error(404, "not_found", "Expense not found")

    supabase.table("planned_expenses").delete().eq("id", id).eq("user_id", current_user["id"]).execute()

    return {"deleted": id}



# ----------------------------------------------------------------
# Daily budget
# ----------------------------------------------------------------

@router.get("/daily")
@limiter.limit("30/minute")
async def daily_budget(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    today = date.today()
    month_start = today.replace(day=1)
    days_in_month = monthrange(today.year, today.month)[1]
    days_remaining = days_in_month - today.day + 1

    user_id = current_user["id"]

    # --- Income: sum of all Income credits this month from transactions ---
    income_result = (
        supabase.table("transactions")
        .select("credit")
        .eq("user_id", user_id)
        .eq("category", "Income")
        .gte("date", str(month_start))
        .lte("date", str(today))
        .execute()
    )
    income = sum(float(r["credit"]) for r in income_result.data if r["credit"])

    # --- Planned Expenses (recurring bills projected forward into this month) ---
    all_planned = _effective_expenses(user_id, month_start, today.replace(day=days_in_month))
    bills = sum(float(r["amount"]) for r in all_planned if r["amount"] and r["category"] == "Bills & Utilities")
    planned = sum(float(r["amount"]) for r in all_planned if r["amount"] and r["category"] != "Bills & Utilities")

    # --- Formula ---
    available = income - bills - planned
    daily_budget = max(0, available / days_remaining) if days_remaining > 0 else 0

    return {
        "daily_budget": round(daily_budget, 2),
        "breakdown": {
            "income": round(income, 2),
            "fixed_bills": round(bills, 2),
            "planned_expenses": round(planned, 2),
            "available": round(available, 2),
            "days_remaining": days_remaining,
        }
    }
