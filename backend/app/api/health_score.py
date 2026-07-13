import json
import logging
from calendar import monthrange
from datetime import date

import anthropic
import pandas as pd
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.dependencies import get_current_user
from app.core.config import ANTHROPIC_API_KEY
from app.core.database import supabase

router = APIRouter(prefix="/health-score", tags=["health"])
limiter = Limiter(key_func=get_remote_address)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------
# Dimension scorers — each returns (score out of 25, detail dict)
# ----------------------------------------------------------------

def _savings_rate(user_id: str, month_start: str, today: str):
    income = sum(
        float(r["credit"])
        for r in supabase.table("transactions").select("credit")
        .eq("user_id", user_id).eq("category", "Income")
        .gte("date", month_start).lte("date", today).execute().data
        if r["credit"]
    )
    spend = sum(
        float(r["withdrawal"])
        for r in supabase.table("transactions").select("withdrawal")
        .eq("user_id", user_id).gte("date", month_start).lte("date", today).execute().data
        if r["withdrawal"]
    )
    if income <= 0:
        return 12.0, {"income": 0, "spend": round(spend, 2), "rate_pct": None}

    rate = max(0.0, (income - spend) / income)
    # 25% savings rate earns full marks; linear below that
    score = min(25.0, rate * 100)
    return round(score, 1), {
        "income": round(income, 2),
        "spend": round(spend, 2),
        "rate_pct": round(rate * 100, 1),
    }


def _expense_consistency(user_id: str, month_start: str, today: str):
    rows = (
        supabase.table("transactions").select("date, withdrawal")
        .eq("user_id", user_id).gte("date", month_start).lte("date", today).execute().data
    )
    if not rows:
        return 12.0, {"cv": None}

    df = pd.DataFrame(rows)
    df["withdrawal"] = pd.to_numeric(df["withdrawal"], errors="coerce").fillna(0)
    df["date"] = pd.to_datetime(df["date"])
    daily = df.set_index("date")["withdrawal"].resample("D").sum()

    if len(daily) < 3 or daily.mean() == 0:
        return 12.0, {"cv": None}

    cv = daily.std() / daily.mean()
    # CV < 0.3 = full marks; CV > 1.5 = 0 pts
    score = max(0.0, min(25.0, 25 * (1 - (cv - 0.3) / 1.2)))
    return round(score, 1), {"cv": round(float(cv), 2)}


def _bill_regularity(user_id: str, month_start: str, month_end: str):
    tx_count = len(
        supabase.table("transactions").select("id")
        .eq("user_id", user_id).eq("category", "Bills & Utilities")
        .gte("date", month_start).lte("date", month_end).execute().data
    )
    plan_count = len(
        supabase.table("planned_expenses").select("id")
        .eq("user_id", user_id).eq("category", "Bills & Utilities")
        .gte("due_date", month_start).lte("due_date", month_end).execute().data
    )
    if tx_count > 0 and plan_count > 0:
        score = 25.0
    elif tx_count > 0 or plan_count > 0:
        score = 18.0
    else:
        score = 10.0  # No bills tracked — can't assess
    return score, {"bill_transactions": tx_count, "planned_bills": plan_count}


def _budget_adherence(user_id: str, month_start: str, today: str, days_elapsed: int):
    days_in_month = monthrange(date.today().year, date.today().month)[1]

    income = sum(
        float(r["credit"])
        for r in supabase.table("transactions").select("credit")
        .eq("user_id", user_id).eq("category", "Income")
        .gte("date", month_start).lte("date", today).execute().data
        if r["credit"]
    )
    bills = sum(
        float(r["amount"])
        for r in supabase.table("planned_expenses").select("amount")
        .eq("user_id", user_id).eq("category", "Bills & Utilities")
        .gte("due_date", month_start).execute().data
        if r["amount"]
    )
    planned = sum(
        float(r["amount"])
        for r in supabase.table("planned_expenses").select("amount")
        .eq("user_id", user_id).neq("category", "Bills & Utilities")
        .gte("due_date", month_start).execute().data
        if r["amount"]
    )
    total_spend = sum(
        float(r["withdrawal"])
        for r in supabase.table("transactions").select("withdrawal")
        .eq("user_id", user_id).gte("date", month_start).lte("date", today).execute().data
        if r["withdrawal"]
    )

    if income <= 0 or days_elapsed <= 0:
        return 12.0, {"daily_budget": None, "actual_daily": None}

    daily_budget = max(0.0, (income - bills - planned) / days_in_month)
    actual_daily = total_spend / days_elapsed

    if actual_daily <= 0:
        return 20.0, {"daily_budget": round(daily_budget, 2), "actual_daily": 0}

    score = min(25.0, 25 * (daily_budget / actual_daily))
    return round(score, 1), {
        "daily_budget": round(daily_budget, 2),
        "actual_daily": round(actual_daily, 2),
    }


def _ai_tip(weakest: str, detail: dict) -> str:
    labels = {
        "savings_rate": "savings rate",
        "expense_consistency": "expense consistency (day-to-day spending variability)",
        "bill_regularity": "bill regularity (tracking and planning fixed costs)",
        "budget_adherence": "budget adherence (staying within your daily budget)",
    }
    try:
        msg = claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": (
                    f"You are a friendly personal finance advisor for a Singapore budgeting app.\n"
                    f"The user's weakest financial health dimension is: {labels.get(weakest, weakest)}.\n"
                    f"Data: {json.dumps(detail, default=str)}\n\n"
                    f"Write ONE short, specific, actionable tip (2-3 sentences) to help them improve. "
                    f"Be direct. Singapore context where relevant (CPF, hawker centres, EZ-Link). "
                    f"No generic platitudes."
                ),
            }],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        logger.error(f"AI tip generation failed: {e}")
        return "Keep tracking your expenses consistently — small daily habits compound into big results."


# ----------------------------------------------------------------
# Endpoint
# ----------------------------------------------------------------

@router.get("")
@limiter.limit("10/minute")
async def get_health_score(request: Request, current_user: dict = Depends(get_current_user)):
    today = date.today()
    month_start = str(today.replace(day=1))
    today_str = str(today)
    days_in_month = monthrange(today.year, today.month)[1]
    month_end = str(today.replace(day=days_in_month))

    user_id = current_user["id"]

    s_score, s_detail = _savings_rate(user_id, month_start, today_str)
    c_score, c_detail = _expense_consistency(user_id, month_start, today_str)
    b_score, b_detail = _bill_regularity(user_id, month_start, month_end)
    a_score, a_detail = _budget_adherence(user_id, month_start, today_str, today.day)

    dimensions = {
        "savings_rate":        {"score": s_score, "max": 25, "label": "Savings Rate",        "detail": s_detail},
        "expense_consistency": {"score": c_score, "max": 25, "label": "Expense Consistency", "detail": c_detail},
        "bill_regularity":     {"score": b_score, "max": 25, "label": "Bill Regularity",     "detail": b_detail},
        "budget_adherence":    {"score": a_score, "max": 25, "label": "Budget Adherence",    "detail": a_detail},
    }

    weakest = min(dimensions, key=lambda k: dimensions[k]["score"] / dimensions[k]["max"])
    total = round(s_score + c_score + b_score + a_score, 1)

    return {
        "score": total,
        "dimensions": dimensions,
        "weakest_dimension": weakest,
        "ai_tip": _ai_tip(weakest, dimensions[weakest]["detail"]),
        "month": today.strftime("%B %Y"),
    }
