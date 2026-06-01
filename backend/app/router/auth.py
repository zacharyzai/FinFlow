from fastapi import APIRouter, Depends, Header, HTTPException
from app.services.auth import get_current_user
from app.core.database import supabase

router = APIRouter()

@router.get('/me')
def me(user = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email
    }

@router.post('/logout')
def logout(user = Depends(get_current_user), authorization: str = Header(...)):
    token = authorization.split("Bearer ")[1]
    try:
        supabase.auth.sign_out(token)
        return {"message": "Logged out successfully"}
    except:
        raise HTTPException(status_code=401)