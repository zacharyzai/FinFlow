"""
HTTP surface for the Quick-Add Shortcut's personal access token:
generate (shown once), check status, and revoke — all from FinFlow
Settings, all authenticated by the normal Supabase JWT (this is about
managing the token, not using it).
"""
from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_current_user, limiter
from app.services.api_tokens import generate_token, has_token, revoke_token

router = APIRouter(prefix="/api-tokens", tags=["api-tokens"])


@router.post("")
@limiter.limit("10/minute")
async def create_token(request: Request, current_user: dict = Depends(get_current_user)):
    token = generate_token(current_user["id"])
    return {"token": token}


@router.get("/status")
@limiter.limit("30/minute")
async def status(request: Request, current_user: dict = Depends(get_current_user)):
    return {"active": has_token(current_user["id"])}


@router.delete("")
@limiter.limit("10/minute")
async def delete_token(request: Request, current_user: dict = Depends(get_current_user)):
    revoke_token(current_user["id"])
    return {"revoked": True}
