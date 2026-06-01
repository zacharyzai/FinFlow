from fastapi import FastAPI, Depends
from app.core.database import supabase
from app.router.auth import router as auth_router

app = FastAPI()

@app.get("/test-db")
def test_db():
    result = supabase.table("accounts").select("*").execute()
    return {"status": "connected", "data": result.data}


# Mounting Routes
app.include_router(auth_router, prefix='/auth')
