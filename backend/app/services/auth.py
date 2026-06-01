from fastapi import Header, HTTPException
from app.core.database import supabase

# Getting the Token
async def get_current_user(authorization: str = Header(...)):
    if authorization.startswith('Bearer '):
        token = authorization.split("Bearer ")[1]
        try:
            response = supabase.auth.get_user(token)
            return response.user
        except:
            raise HTTPException(status_code=401)
    else:
        raise HTTPException(status_code=401)