from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.dependencies import get_current_user
from app.core.database import supabase

router = APIRouter(prefix="/transactions", tags=["transactions"])
limiter = Limiter(key_func=get_remote_address)

VALID_CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Bills & Utilities",
    "Healthcare", "Entertainment", "Travel", "Education",
    "Income", "Transfer", "Other",
]

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

    

