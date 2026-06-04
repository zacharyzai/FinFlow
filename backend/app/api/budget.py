from datetime import date
from calendar import monthrange

from fastapi import APIRouter, Depends, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.dependencies import get_current_user
from app.core.database import supabase

from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/budget", tags=["budget"])
limiter = Limiter(key_func=get_remote_address)

VALID_CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Bills & Utilities",
    "Healthcare", "Entertainment", "Travel", "Education",
    "Income", "Transfer", "Other",
]

class PlannedExpenseIn(BaseModel):
    name: str
    amount: float
    due_date: str # YYYY-MM-DD
    category: str
    is_recurring: bool = False
    recurrence_days: Optional[int] = None

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

    result = (
        supabase.table("planned_expenses")
        .select("id, name, amount, due_date, category")
        .eq("user_id", current_user["id"])
        .gte("due_date", str(today))        # from today onwards
        .lte("due_date", str(month_end))    # within this month only
        .order("due_date", desc=False)      # earliest due date first
        .execute()
    )

    return {"expenses": result.data}


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
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # If category is not one of the preset options, default to "Other"
    category = body.category if body.category in VALID_CATEGORIES else "Other"

    result = (
        supabase.table("planned_expenses")
        .insert({
            "user_id": current_user["id"],
            "name": body.name,
            "amount": body.amount,
            "due_date": body.due_date,
            "category": category,
            "is_recurring": body.is_recurring,
            "recurrence_days": body.recurrence_days,
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
        raise HTTPException(status_code=404, detail="Expense not found")

    supabase.table("planned_expenses").delete().eq("id", id).execute()

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

    # --- Fixed Bills: planned expenses categorised as Bills & Utilities ---
    bills_result = (
        supabase.table("planned_expenses")
        .select("amount")
        .eq("user_id", user_id)
        .eq("category", "Bills & Utilities")
        .gte("due_date", str(month_start))
        .lte("due_date", str(today.replace(day=days_in_month)))
        .execute()
    )
    bills = sum(float(r["amount"]) for r in bills_result.data if r["amount"])

    # --- Planned Expenses: everything else in planned_expenses this month ---
    planned_result = (
        supabase.table("planned_expenses")
        .select("amount, category")
        .eq("user_id", user_id)
        .neq("category", "Bills & Utilities")
        .gte("due_date", str(month_start))
        .lte("due_date", str(today.replace(day=days_in_month)))
        .execute()
    )
    planned = sum(float(r["amount"]) for r in planned_result.data if r["amount"])

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
