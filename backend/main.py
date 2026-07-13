import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import analytics, budget, statements, transactions
from app.api import savings, health_score
from app.api.dependencies import limiter
from app.jobs.reconciliation import run_reconciliation
from app.router.auth import router as auth_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="FinFlow API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
