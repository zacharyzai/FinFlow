import io
import json
import tempfile
import os

import anthropic
import pandas as pd
import pdfplumber
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.dependencies import get_current_user
from app.core.config import ANTHROPIC_API_KEY
from app.core.database import supabase

router = APIRouter(prefix="/statements", tags=["statements"])
limiter = Limiter(key_func=get_remote_address)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

ALLOWED_MIME_TYPES = {"application/pdf", "text/csv", "application/vnd.ms-excel"}
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB

VALID_CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Bills & Utilities",
    "Healthcare", "Entertainment", "Travel", "Education",
    "Income", "Transfer", "Other",
]

# ----------------------------------------------------------------
# Parsing helpers
# ----------------------------------------------------------------

def _extract_pdf_text(content: bytes) -> str:
    """Return all text extracted from every page of a PDF."""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = []
        for page in pdf.pages:
            # Try table extraction first; fall back to raw text
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        pages.append("\t".join(str(c or "") for c in row))
            else:
                text = page.extract_text()
                if text:
                    pages.append(text)
    return "\n".join(pages)


def _parse_csv(content: bytes) -> list[dict]:
    """
    Normalise a DBS / OCBC / UOB CSV export into a list of raw row dicts.
    Column names are lowercased and stripped so minor bank differences are smoothed out.
    """
    df = pd.read_csv(io.BytesIO(content), thousands=",")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Map common bank column names to our canonical names
    rename = {
        # DBS
        "transaction_date": "date", "debit_amount": "withdrawal",
        "credit_amount": "credit", "running_balance": "balance",
        # OCBC
        "value_date": "date", "withdrawals": "withdrawal", "deposits": "credit",
        # UOB
        "txn_date": "date", "debit": "withdrawal", "credit_(sgd)": "credit",
        # generic
        "amount": "withdrawal",
    }
    df.rename(columns={k: v for k, v in rename.items() if k in df.columns}, inplace=True)

    # Drop rows with no description or date
    for col in ("date", "description"):
        if col in df.columns:
            df = df[df[col].notna()]

    # Fill missing numeric columns with NaN so JSON serialisation is clean
    for col in ("withdrawal", "credit", "balance"):
        if col not in df.columns:
            df[col] = None

    return df.to_dict(orient="records")


# ----------------------------------------------------------------
# Claude categorisation
# ----------------------------------------------------------------

def _categorise_with_claude(rows: list[dict]) -> list[dict]:
    """
    Send all transaction rows to Claude in a single API call.
    Returns the same rows with a 'category' key added to each.
    """
    rows_json = json.dumps(rows, default=str)
    prompt = f"""You are a financial transaction categoriser for a Singapore personal finance app.

Categorise each transaction below into exactly one of these categories:
{", ".join(VALID_CATEGORIES)}

Rules:
- Hawker centres, restaurants, cafes, GrabFood, Deliveroo → "Food & Dining"
- MRT, bus, Grab, Gojek, petrol, ERP → "Transport"
- Retail, online shopping, Lazada, Shopee → "Shopping"
- Utilities (SP Group, StarHub, Singtel), rent, insurance → "Bills & Utilities"
- Hospitals, clinics, pharmacies, Guardian → "Healthcare"
- Movies, streaming, concerts → "Entertainment"
- Flights, hotels, Airbnb → "Travel"
- Schools, tuition, courses → "Education"
- Salary, interest, dividends, refunds → "Income"
- Bank transfers, PayNow, PayLah → "Transfer"
- Anything else → "Other"

Input (JSON array):
{rows_json}

Respond with ONLY a JSON array of objects, one per input row, each with:
  "index": (same position as input, 0-based)
  "category": (one of the categories above)

No explanation, no markdown, just the JSON array."""

    message = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if Claude adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    categorised = json.loads(raw)
    category_map = {item["index"]: item["category"] for item in categorised}

    for i, row in enumerate(rows):
        cat = category_map.get(i, "Other")
        row["category"] = cat if cat in VALID_CATEGORIES else "Other"

    return rows


# ----------------------------------------------------------------
# Database writes
# ----------------------------------------------------------------

def _get_or_create_account(user_id: str, bank: str) -> str:
    """Return existing account id for this user+bank, or create one."""
    result = (
        supabase.table("accounts")
        .select("id")
        .eq("user_id", user_id)
        .eq("bank", bank)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]["id"]

    new_account = (
        supabase.table("accounts")
        .insert({"user_id": user_id, "bank": bank, "name": f"{bank} Account"})
        .execute()
    )
    return new_account.data[0]["id"]


def _insert_transactions(account_id: str, user_id: str, rows: list[dict]) -> list[str]:
    """Bulk-insert transactions; return list of inserted IDs."""
    records = []
    for row in rows:
        withdrawal = row.get("withdrawal")
        credit = row.get("credit")

        # Skip rows where both are null or both are set (malformed)
        has_withdrawal = withdrawal is not None and str(withdrawal).strip() not in ("", "nan")
        has_credit = credit is not None and str(credit).strip() not in ("", "nan")
        if has_withdrawal == has_credit:
            continue

        records.append({
            "account_id": account_id,
            "user_id": user_id,
            "date": str(row.get("date", "")),
            "description": str(row.get("description", ""))[:500],
            "withdrawal": float(withdrawal) if has_withdrawal else None,
            "credit": float(credit) if has_credit else None,
            "balance": float(row["balance"]) if row.get("balance") not in (None, "", "nan") else None,
            "category": row.get("category", "Other"),
            "raw_text": json.dumps(row, default=str)[:1000],
            "state": "PENDING",
        })

    if not records:
        return []

    result = supabase.table("transactions").insert(records).execute()
    return [r["id"] for r in result.data]


def _insert_ledger_entries(user_id: str, transactions: list[dict]) -> None:
    """Create double-entry ledger rows for each transaction."""
    entries = []
    for tx in transactions:
        tx_id = tx["id"]
        if tx.get("withdrawal"):
            amount = tx["withdrawal"]
            category = tx.get("category", "Other")
            entries += [
                # Debit the expense account (money leaves)
                {"transaction_id": tx_id, "user_id": user_id,
                 "account": f"expenses:{category.lower().replace(' & ', ':').replace(' ', '_')}",
                 "entry_type": "DR", "amount": amount},
                # Credit the bank account (asset decreases)
                {"transaction_id": tx_id, "user_id": user_id,
                 "account": "assets:checking", "entry_type": "CR", "amount": amount},
            ]
        elif tx.get("credit"):
            amount = tx["credit"]
            entries += [
                # Debit the bank account (asset increases)
                {"transaction_id": tx_id, "user_id": user_id,
                 "account": "assets:checking", "entry_type": "DR", "amount": amount},
                # Credit income account (money arrives)
                {"transaction_id": tx_id, "user_id": user_id,
                 "account": "income:received", "entry_type": "CR", "amount": amount},
            ]

    if entries:
        supabase.table("ledger_entries").insert(entries).execute()


# ----------------------------------------------------------------
# Upload endpoint
# ----------------------------------------------------------------

@router.post("/upload")
@limiter.limit("5/minute")
async def upload_statement(
    request: Request,
    file: UploadFile = File(...),
    bank: str = Form(default="Unknown"),
    current_user: dict = Depends(get_current_user),
):
    # --- Validate ---
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and CSV files are accepted.")

    content = await file.read()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds 10 MB limit.")

    user_id = current_user["id"]

    # --- Parse ---
    try:
        if file.content_type == "application/pdf":
            raw_text = _extract_pdf_text(content)
            # Convert extracted PDF text into row dicts for Claude
            rows = [{"description": line.strip()} for line in raw_text.splitlines() if line.strip()]
        else:
            rows = _parse_csv(content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {e}")
    finally:
        # Raw file never stored beyond this point
        content = b""

    if not rows:
        raise HTTPException(status_code=422, detail="No transactions found in the uploaded file.")

    # --- Categorise with Claude ---
    try:
        rows = _categorise_with_claude(rows)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI categorisation failed: {e}")

    # --- Write to database ---
    account_id = _get_or_create_account(user_id, bank)
    tx_ids = _insert_transactions(account_id, user_id, rows)

    if tx_ids:
        inserted_txs = (
            supabase.table("transactions")
            .select("*")
            .in_("id", tx_ids)
            .execute()
            .data
        )
        _insert_ledger_entries(user_id, inserted_txs)

    return {
        "status": "ok",
        "account_id": account_id,
        "transactions_imported": len(tx_ids),
    }
