import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api import statements
from app.core.database import supabase
from app.router.auth import router as auth_router
from app.api import transactions
from app.api import analytics
from app.api import budget
from app.router import telegram
from app.services.telegram import poll_telegram
from app.router.telegram import handle_update

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(poll_telegram(handle_update))
    yield


app = FastAPI(title="FinFlow API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(statements.router)
app.include_router(auth_router, prefix='/auth')
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(budget.router)
app.include_router(telegram.router, prefix='/api')



@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test-db")
def test_db():
    result = supabase.table("accounts").select("*").limit(1).execute()
    return {"status": "connected", "sample": result.data}
