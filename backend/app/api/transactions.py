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


class TransactionUpdate(BaseModel):
    date: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["withdrawal", "credit"]] = None
    category: Optional[str] = None


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

@router.patch('/{transaction_id}')
@limiter.limit("30/minute")
async def update_transaction(
    request: Request,
    transaction_id: str,
    body: TransactionUpdate,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    existing = (
        supabase.table("transactions").select("*")
        .eq("id", transaction_id).eq("user_id", user_id).limit(1).execute().data
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction not found")
    tx = existing[0]

    patch = {}
    if body.date is not None:
        patch["date"] = body.date
    if body.description is not None:
        patch["description"] = body.description[:500]
    if body.category is not None:
        patch["category"] = body.category if body.category in VALID_CATEGORIES else "Other"

    # Amount/type move together — withdrawal and credit are mutually exclusive
    new_type = body.type or ("withdrawal" if tx["withdrawal"] is not None else "credit")
    if body.amount is not None or body.type is not None:
        amount = body.amount if body.amount is not None else (tx["withdrawal"] or tx["credit"])
        patch["withdrawal"] = amount if new_type == "withdrawal" else None
        patch["credit"] = amount if new_type == "credit" else None

    if not patch:
        return {"transaction": tx}

    result = (
        supabase.table("transactions").update(patch)
        .eq("id", transaction_id).eq("user_id", user_id).execute()
    )
    updated_tx = result.data[0]

    # Re-sync the double-entry ledger to match the edited amount/category.
    # ponytail: overwrites the old DR/CR pair rather than posting a reversing
    # entry — simplest option for a personal-use app; a production ledger would
    # keep the original entries and post a correction for auditability.
    supabase.table("ledger_entries").delete().eq("transaction_id", transaction_id).eq("user_id", user_id).execute()
    _insert_ledger_entries(user_id, [updated_tx])

    return {"transaction": updated_tx}


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

    

