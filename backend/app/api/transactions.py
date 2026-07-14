from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.api.dependencies import VALID_CATEGORIES, get_current_user, limiter
from app.api.statements import _get_or_create_account, _insert_ledger_entries
from app.core.database import supabase

router = APIRouter(prefix="/transactions", tags=["transactions"])


class TransactionIn(BaseModel):
    date: str
    description: str
    amount: float = Field(gt=0)
    type: Literal["withdrawal", "credit"]
    category: str = "Other"


@router.post('')
@limiter.limit("30/minute")
async def create_transaction(
    request: Request,
    body: TransactionIn,
    current_user: dict = Depends(get_current_user),
):
    if body.category not in VALID_CATEGORIES:
        body.category = "Other"

    user_id = current_user["id"]
    account_id = _get_or_create_account(user_id, "Manual")

    record = {
        "account_id": account_id,
        "user_id": user_id,
        "date": body.date,
        "description": body.description[:500],
        "withdrawal": body.amount if body.type == "withdrawal" else None,
        "credit": body.amount if body.type == "credit" else None,
        "category": body.category,
        "state": "PENDING",
    }

    result = supabase.table("transactions").insert(record).execute()
    tx = result.data[0]
    _insert_ledger_entries(user_id, [tx])

    return {"transaction": tx}

#Transactions List
@router.get('')
@limiter.limit("30/minute")
async def list_transactions(
    request: Request,
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to:   Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category:  Optional[str] = Query(None, description="Filter by category"),
    page:  int = Query(1,  ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    current_user: dict = Depends(get_current_user)
):
    if category and category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}")

    user_id = current_user["id"]
    offset = (page - 1) * limit # Pagination

    query = (supabase.table("transactions").select("*", count="exact").eq("user_id", user_id))

    # For filtering by categories or date
    if date_from:
        query = query.gte("date", date_from)
    if date_to:
        query = query.lte("date", date_to)
    if category:
        query = query.eq("category", category)

    result = (
        query
        .order("date", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    total = result.count or 0
    total_pages = (total + limit - 1) // limit

    return {
        "data": result.data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        },
    }

    

