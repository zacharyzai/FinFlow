from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.dependencies import VALID_CATEGORIES, get_current_user, limiter
from app.core.database import supabase
from pydantic import BaseModel

from app.api.statements import _get_or_create_account

router = APIRouter(prefix="/transactions", tags=["transactions"])

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

# POST Request for Transaction (For the user to input their transactions)

class TransactionIn(BaseModel):
    date: str
    amount: float
    description: str
    category: str
    type: str # 'withdrawal' or 'credit'

@router.post('')
@limiter.limit("30/minute")
async def create_transaction(
    request: Request,
    body: TransactionIn,                    # the form data the user submitted
    current_user: dict = Depends(get_current_user),  # who is logged in
):
    # Step 1: validate category
    if body.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")

    # Step 2: decide which column gets the amount
    # Like a light switch — it's either withdrawal OR credit, never both
    withdrawal = body.amount if body.type == 'withdrawal' else None
    credit     = body.amount if body.type == 'credit'     else None

    # Step 3: build the record — like filling in a form before handing it to the database
    record = {
        "user_id":     current_user["id"],  # who owns this transaction
        "account_id":  _get_or_create_account(current_user["id"], "Manual"),                 # we'll talk about this
        "date":        body.date,
        "description": body.description,
        "category":    body.category,       
        "withdrawal":  withdrawal,      
        "credit":      credit,
        "state":       "PENDING",           # always starts as PENDING                                                                                                                                   
    }                                       
                                                                                                                                                                                                        
    # Step 4: insert into Supabase — same as mongoose's .save()                                                                                                                                        
    result = supabase.table("transactions").insert(record).execute()                                                                                                                                     

    return result.data[0]