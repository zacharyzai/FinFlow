from fastapi import APIRouter, Depends, Header
from app.api.dependencies import get_current_user
from app.core.database import supabase
from app.core.errors import app_error

router = APIRouter()

@router.get('/me')
def me(user = Depends(get_current_user)):
    return user

@router.post('/logout')
def logout(user = Depends(get_current_user), authorization: str = Header(...)):
    token = authorization.split("Bearer ")[1]
    try:
        supabase.auth.sign_out(token)
        return {"message": "Logged out successfully"}
    except Exception:
        raise app_error(401, "auth_error", "Logout failed")