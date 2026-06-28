from calendar import monthrange
from datetime import date

import pandas as pd
from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_current_user, limiter
from app.core.database import supabase

router = APIRouter(prefix="/health", tags=["health"])


# ----------------------------------------------------------------
# Score computation (pure function — no I/O)
# ----------------------------------------------------------------

def _compute_score(
    txns: list[dict],
    planned: list[dict],
    goals: list[dict],
    today: date,
) -> dict:
    days_in_month = monthrange(today.year, today.month)[1]
    month_start = today.replace(day=1)
    days_elapsed = (today - month_start).days + 1

    # Build a DataFrame of this month's transactions
    if txns:
        df = pd.DataFrame(txns)
        df["withdrawal"] = pd.to_numeric(df["withdrawal"], errors="coerce").fillna(0)
        df["credit"] = pd.to_numeric(df["credit"], errors="coerce").fillna(0)
        df["date"] = pd.to_datetime(df["date"])
    else:
        df = pd.DataFrame(columns=["date", "withdrawal", "credit", "category"])
        df["withdrawal"] = df["withdrawal"].astype(float)
        df["credit"] = df["credit"].astype(float)

    income = float(df[df["category"] == "Income"]["credit"].sum())
    total_spending = float(df["withdrawal"].sum())

    # Daily spending series (used by two dimensions below)
    daily_spending = (
        df.set_index("date")["withdrawal"].resample("D").sum()
        if not df.empty else pd.Series(dtype=float)
    )

    # Planned split
    bills = sum(float(r["amount"]) for r in planned if r.get("category") == "Bills & Utilities")
    other_planned = sum(float(r["amount"]) for r in planned if r.get("category") != "Bills & Utilities")
    daily_budget = (income - bills - other_planned) / days_in_month if days_in_month > 0 else 0

    # ── 1. Savings rate (25 pts) ─────────────────────────────────
    # 20% savings rate earns full marks; scales linearly below that.
    if income > 0:
        rate = max(0.0, (income - total_spending) / income)
        savings_score = min(25.0, rate / 0.20 * 25)
    else:
        savings_score = 0.0

    # ── 2. Budget adherence (25 pts) ────────────────────────────
    # Fraction of elapsed days where you stayed under the daily budget.
    if daily_budget > 0 and not daily_spending.empty:
        days_over = int((daily_spending > daily_budget).sum())
        adherence_score = max(0.0, 25.0 * (1 - days_over / days_elapsed))
    else:
        adherence_score = 25.0  # ponytail: neutral when no data yet

    # ── 3. Spending stability (20 pts) ───────────────────────────
    # Coefficient of variation of daily spending; lower = more stable.
    if not daily_spending.empty and daily_spending.mean() > 0:
        cv = daily_spending.std() / daily_spending.mean()
        stability_score = max(0.0, 20.0 * (1 - min(float(cv), 1.0)))
    else:
        stability_score = 20.0

    # ── 4. Bills coverage (20 pts) ───────────────────────────────
    # How comfortably does income cover fixed bills? 2× = full marks.
    if bills > 0 and income > 0:
        coverage_score = min(20.0, (income / bills) / 2.0 * 20)
    else:
        coverage_score = 20.0  # no bills = no burden

    # ── 5. Goal progress (10 pts) ────────────────────────────────
    if goals:
        ratios = [
            min(1.0, float(g.get("saved") or 0) / float(g["target"]))
            for g in goals if float(g.get("target") or 0) > 0
        ]
        goal_score = (sum(ratios) / len(ratios) * 10) if ratios else 10.0
    else:
        goal_score = 10.0

    total = savings_score + adherence_score + stability_score + coverage_score + goal_score

    return {
        "score": round(total),
        "dimensions": {
            "savings_rate":       round(savings_score, 1),
            "budget_adherence":   round(adherence_score, 1),
            "spending_stability": round(stability_score, 1),
            "bills_coverage":     round(coverage_score, 1),
            "goal_progress":      round(goal_score, 1),
        },
    }


# ----------------------------------------------------------------
# GET /health/score  — compute this month's score and cache it
# ----------------------------------------------------------------

@router.get("/score")
@limiter.limit("30/minute")
async def get_health_score(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    today = date.today()
    month_key = today.strftime("%Y-%m")  # e.g. "2026-06"
    month_start = today.replace(day=1)

    # Fetch raw data in parallel (three independent Supabase queries)
    txns = (
        supabase.table("transactions")
        .select("date, withdrawal, credit, category")
        .eq("user_id", user_id)
        .gte("date", str(month_start))
        .lte("date", str(today))
        .execute()
    ).data

    planned = (
        supabase.table("planned_expenses")
        .select("amount, category")
        .eq("user_id", user_id)
        .gte("due_date", str(month_start))
        .lte("due_date", str(today.replace(day=monthrange(today.year, today.month)[1])))
        .execute()
    ).data

    goals = (
        supabase.table("savings_goals")
        .select("target, saved")
        .eq("user_id", user_id)
        .execute()
    ).data

    result = _compute_score(txns, planned, goals, today)

    # Upsert so re-calling this endpoint just refreshes the cached row
    supabase.table("health_scores").upsert(
        {
            "user_id":    user_id,
            "month":      month_key,
            "score":      result["score"],
            "dimensions": result["dimensions"],
        },
        on_conflict="user_id,month",
    ).execute()

    return {"month": month_key, **result}


# ----------------------------------------------------------------
# GET /health/history  — last 6 months of cached scores
# ----------------------------------------------------------------

@router.get("/history")
@limiter.limit("30/minute")
async def get_health_history(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    rows = (
        supabase.table("health_scores")
        .select("month, score, dimensions")
        .eq("user_id", current_user["id"])
        .order("month", desc=True)
        .limit(6)
        .execute()
    ).data

    return {"history": list(reversed(rows))}  # chronological order for charts
