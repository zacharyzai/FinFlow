import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api import analytics, budget, statements, transactions
from app.api import savings, health_score
from app.api.dependencies import limiter
from app.core.config import CORS_ORIGINS
from app.jobs.reconciliation import run_reconciliation
from app.router.auth import router as auth_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="FinFlow API")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    # Same {code, message} shape as app_error() elsewhere, instead of
    # slowapi's default plain-text body — one consistent error shape everywhere.
    return JSONResponse(
        status_code=429,
        content={"detail": {"code": "rate_limited", "message": f"Rate limit exceeded: {exc.detail}"}},
    )


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    # Safety net for the errors we didn't explicitly wrap in app_error() —
    # a raw Supabase/network exception would otherwise reach the client as an
    # unstructured 500 with no `code` field. This only fires for exceptions
    # FastAPI hasn't already handled more specifically (HTTPException still
    # goes through its own handler, unaffected by this).
    logging.exception("Unhandled exception in %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": {"code": "server_error", "message": "An unexpected error occurred. Please try again."}},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(statements.router)
app.include_router(auth_router, prefix="/auth")
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(budget.router)
app.include_router(savings.router)
app.include_router(health_score.router)

# Nightly reconciliation at 2AM Singapore time (UTC+8)
scheduler = BackgroundScheduler(timezone="Asia/Singapore")
scheduler.add_job(run_reconciliation, CronTrigger(hour=2, minute=0))
scheduler.start()


@app.get("/health")
def health():
    return {"status": "ok"}
