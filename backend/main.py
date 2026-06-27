from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import analytics, budget, statements, transactions
from app.api.dependencies import limiter
from app.router.auth import router as auth_router

app = FastAPI(title="FinFlow API")
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


@app.get("/health")
def health():
    return {"status": "ok"}
