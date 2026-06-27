from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.dependencies import get_current_user, limiter
from app.core.database import supabase

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ----------------------------------------------------------------
# Category breakdown
# ----------------------------------------------------------------

@router.get("/categories")
@limiter.limit("30/minute")
async def spending_by_category(
    request: Request,
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]

    query = (
        supabase.table("transactions")
        .select("category, withdrawal")
        .eq("user_id", user_id)
    )

    if date_from:
        query = query.gte("date", date_from)
    if date_to:
        query = query.lte("date", date_to)

    result = query.execute()

    if not result.data:
        return {"categories": [], "total_spent": 0}

    df = pd.DataFrame(result.data)
    df["withdrawal"] = pd.to_numeric(df["withdrawal"], errors="coerce").fillna(0)

    breakdown = (
        df.groupby("category")["withdrawal"]
        .sum()
        .reset_index()
        .rename(columns={"withdrawal": "total"})
        .sort_values("total", ascending=False)
    )

    total_spent = breakdown["total"].sum()
    breakdown["percentage"] = (breakdown["total"] / total_spent * 100).round(1)

    return {
        "categories": breakdown.to_dict(orient="records"),
        "total_spent": round(total_spent, 2),
    }



# ----------------------------------------------------------------
# Spending over time
# ----------------------------------------------------------------

@router.get("/spending-over-time")
@limiter.limit("30/minute")
async def spending_over_time(
    request: Request,
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    granularity: str = Query("daily", description="daily | weekly | monthly"),
    current_user: dict = Depends(get_current_user),
):
    if granularity not in ("daily", "weekly", "monthly"):
        raise HTTPException(status_code=400, detail="granularity must be daily, weekly, or monthly")

    user_id = current_user["id"]

    query = (
        supabase.table("transactions")
        .select("date, withdrawal")
        .eq("user_id", user_id)
    )

    if date_from:
        query = query.gte("date", date_from)
    if date_to:
        query = query.lte("date", date_to)

    result = query.execute()

    if not result.data:
        return {"data_points": []}

    df = pd.DataFrame(result.data)
    df["date"] = pd.to_datetime(df["date"])
    df["withdrawal"] = pd.to_numeric(df["withdrawal"], errors="coerce").fillna(0)

    freq_map = {"daily": "D", "weekly": "W", "monthly": "ME"}
    freq = freq_map[granularity]

    series = (
        df.set_index("date")["withdrawal"]
        .resample(freq)
        .sum()
        .asfreq(freq, fill_value=0)
    )

    return {
        "data_points": [
            {"date": str(ts.date()), "total": round(amount, 2)}
            for ts, amount in series.items()
        ]
    }

# ----------------------------------------------------------------
# Anomaly detection (2σ (S.D) rule) 
# ----------------------------------------------------------------

@router.get("/anomalies")
@limiter.limit("30/minute")
async def detect_anomalies(
    request: Request,
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]

    query = (
        supabase.table("transactions")
        .select("id, date, description, category, withdrawal")
        .eq("user_id", user_id)
    )

    if date_from:
        query = query.gte("date", date_from)
    if date_to:
        query = query.lte("date", date_to)

    result = query.execute()

    if not result.data:
        return {"anomalies": []}

    df = pd.DataFrame(result.data)
    df["withdrawal"] = pd.to_numeric(df["withdrawal"], errors="coerce")
    df = df[df["withdrawal"].notna() & (df["withdrawal"] > 0)]

    if df.empty:
        return {"anomalies": []}

    # Compute mean and std per category
    stats = df.groupby("category")["withdrawal"].agg(["mean", "std"]).fillna(0)
    df["mean"] = df["category"].map(stats["mean"])
    df["std"] = df["category"].map(stats["std"])
    df["threshold"] = df["mean"] + 2 * df["std"]

    # A category needs at least 3 transactions to have a meaningful threshold
    category_counts = df.groupby("category")["withdrawal"].count()
    valid_categories = category_counts[category_counts >= 3].index
    df = df[df["category"].isin(valid_categories)]

    anomalies = df[df["withdrawal"] > df["threshold"]].copy()
    anomalies["amount_above"] = (anomalies["withdrawal"] - anomalies["mean"]).round(2)

    return {
        "anomalies": anomalies[["id", "date", "description", "category", "withdrawal", "amount_above"]]
        .sort_values("withdrawal", ascending=False)
        .to_dict(orient="records")
    }
