import io
import json
import tempfile
import os

import pandas as pd
import pdfplumber
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.api.dependencies import VALID_CATEGORIES, get_current_user, limiter
from app.core.ai_client import ai_generate
from app.core.database import supabase

router = APIRouter(prefix="/statements", tags=["statements"])

ALLOWED_MIME_TYPES = {"application/pdf", "text/csv", "application/vnd.ms-excel"}
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB

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
# Claude categorisation (CSV rows that already have amounts)
# ----------------------------------------------------------------

_CATEGORY_RULES = """Rules:
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
- Anything else → "Other" — only use this once you genuinely can't tell, not as a first guess"""


# Rows per categorisation call, and a token-per-row estimate for sizing max_tokens.
# A single big call risks the model's output getting cut off mid-JSON on large
# statements (25+ rows already flirts with this); batching keeps each call's
# output small and bounded regardless of how many transactions were uploaded.
_CATEGORISE_BATCH_SIZE = 40
_TOKENS_PER_ROW = 40


def _run_categorisation(items: list[dict], search: bool) -> dict:
    """
    Ask the model to categorise a batch of {"index", "description", ...} rows.
    Returns {index: category}. Each item carries its own true row index so a
    retry can send a subset without index/position getting out of sync.
    """
    items_json = json.dumps(items, default=str)
    search_note = (
        "\nYou have web search — use it for unfamiliar merchant names (SGP company "
        "codes, chain names you don't recognise) instead of guessing \"Other\"."
        if search else ""
    )
    prompt = f"""You are a financial transaction categoriser for a Singapore personal finance app.

Categorise each transaction below into exactly one of these categories:
{", ".join(VALID_CATEGORIES)}

{_CATEGORY_RULES}{search_note}

Input (JSON array), each row already has its "index" — echo that same index back:
{items_json}

Respond with ONE JSON object per line (JSON Lines format), one line per input row:
  {{"index": (same index as the input row), "category": (one of the categories above)}}

No array brackets, no commas between lines, no explanation, no markdown."""

    max_tokens = max(512, len(items) * _TOKENS_PER_ROW)
    raw = ai_generate(
        prompt, max_tokens=max_tokens,
        claude_model="claude-sonnet-4-6", gemini_model="gemini-3.6-flash",
        search=search,
    )
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json") or raw.startswith("jsonl"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw

    category_map = {}
    for line in raw.splitlines():
        line = line.strip().strip(",")
        if not line:
            continue
        try:
            item = json.loads(line)
            category_map[item["index"]] = item["category"]
        except (json.JSONDecodeError, KeyError, TypeError):
            continue  # skip malformed lines instead of failing the whole batch
    return category_map


def _categorise_batches(items: list[dict], search: bool) -> dict:
    """Run _run_categorisation in chunks of _CATEGORISE_BATCH_SIZE, merging the results."""
    category_map = {}
    for start in range(0, len(items), _CATEGORISE_BATCH_SIZE):
        batch = items[start:start + _CATEGORISE_BATCH_SIZE]
        category_map.update(_run_categorisation(batch, search=search))
    return category_map


def _categorise_with_claude(rows: list[dict]) -> list[dict]:
    """
    Categorise every row with Claude/Gemini, in batches of _CATEGORISE_BATCH_SIZE
    so a large statement can't blow a single call's output budget. Rows that come
    back "Other" get one retry with web search enabled, since that's usually an
    unfamiliar merchant name rather than a genuinely uncategorisable transaction —
    search is only spent on that smaller subset to keep the extra cost bounded.
    """
    items = [{"index": i, **row} for i, row in enumerate(rows)]
    category_map = _categorise_batches(items, search=False)

    unresolved = [
        items[i] for i in range(len(rows))
        if category_map.get(i, "Other") not in VALID_CATEGORIES or category_map.get(i) == "Other"
    ]
    if unresolved:
        category_map.update(_categorise_batches(unresolved, search=True))

    for i, row in enumerate(rows):
        cat = category_map.get(i, "Other")
        row["category"] = cat if cat in VALID_CATEGORIES else "Other"

    return rows


# ----------------------------------------------------------------
# Claude full extraction for PDFs (date + amounts + category in one call)
# ----------------------------------------------------------------

# Chars per page sent to the model, with overlap so a transaction line split
# across a page boundary still appears whole in at least one page. The overlap
# means the same transaction can get extracted twice from adjacent pages —
# _dedupe_extracted_rows() below collapses those back down.
_PDF_CHUNK_CHARS = 10_000
_PDF_CHUNK_OVERLAP = 500


def _dedupe_extracted_rows(rows: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for row in rows:
        key = (row.get("date"), row.get("description"), row.get("withdrawal"), row.get("credit"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _extract_transactions_from_pdf_text(raw_text: str) -> list[dict]:
    """
    Page through the PDF text so multi-page statements aren't silently truncated,
    and ask Claude (or Gemini fallback) to extract each page's transactions.
    """
    step = _PDF_CHUNK_CHARS - _PDF_CHUNK_OVERLAP
    all_rows = []
    for start in range(0, max(len(raw_text), 1), step):
        chunk = raw_text[start:start + _PDF_CHUNK_CHARS]
        if chunk.strip():
            all_rows.extend(_extract_transactions_from_chunk(chunk))
        if start + _PDF_CHUNK_CHARS >= len(raw_text):
            break
    return _dedupe_extracted_rows(all_rows)


def _extract_transactions_from_chunk(raw_text: str) -> list[dict]:
    """
    Ask Claude (or Gemini fallback) to extract fully-structured transactions
    from one page-sized slice of PDF bank statement text. This is used instead
    of _categorise_with_claude for PDFs because pdfplumber gives us raw
    text/tables that don't have cleanly separated amount columns yet — the
    model reads the statement text and returns structured rows directly.
    """
    prompt = f"""You are parsing a Singapore bank statement (DBS, OCBC, or UOB).

Extract every transaction from the text below and return a JSON array.
Each object must have exactly these fields:
  "date": "YYYY-MM-DD" (convert any date format to ISO)
  "description": "merchant or transaction description"
  "withdrawal": number or null (money going OUT, positive number)
  "credit": number or null (money coming IN, positive number)
  "category": one of {json.dumps(VALID_CATEGORIES)}

Categorisation rules:
- Hawker centres, restaurants, cafes, GrabFood, Deliveroo → "Food & Dining"
- MRT, bus, Grab, Gojek, petrol, ERP → "Transport"
- Retail, Lazada, Shopee → "Shopping"
- SP Group, StarHub, Singtel, rent, insurance → "Bills & Utilities"
- Hospitals, clinics, pharmacies → "Healthcare"
- Movies, streaming, concerts → "Entertainment"
- Flights, hotels, Airbnb → "Travel"
- Schools, tuition → "Education"
- Salary, dividends, interest, refunds → "Income"
- Bank transfers, PayNow, PayLah → "Transfer"
- Anything else → "Other"

Important:
- Only include rows that are actual transactions (skip headers, balances, account info).
- withdrawal and credit are mutually exclusive — a transaction is one or the other, never both.
- Amounts are always positive numbers.

Bank statement text:
---
{raw_text}
---

Respond with ONE JSON object per line (JSON Lines format) — one line per transaction.
No array brackets, no commas between lines, no explanation, no markdown fences."""

    raw = ai_generate(
        prompt, max_tokens=4096,
        claude_model="claude-sonnet-4-6", gemini_model="gemini-3.6-flash",
    )
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json") or raw.startswith("jsonl"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw

    rows = []
    for line in raw.splitlines():
        line = line.strip().strip(",")
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # skip malformed lines instead of failing the whole statement

    # Validate each row defensively — Claude can hallucinate
    clean = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        description = str(row.get("description", "")).strip()
        if not description:
            continue
        withdrawal = row.get("withdrawal")
        credit = row.get("credit")
        try:
            withdrawal = float(withdrawal) if withdrawal not in (None, "", "null") else None
        except (TypeError, ValueError):
            withdrawal = None
        try:
            credit = float(credit) if credit not in (None, "", "null") else None
        except (TypeError, ValueError):
            credit = None
        category = row.get("category", "Other")
        if category not in VALID_CATEGORIES:
            category = "Other"
        clean.append({
            "date": str(row.get("date", ""))[:10],
            "description": description[:500],
            "withdrawal": withdrawal,
            "credit": credit,
            "category": category,
        })

    return clean


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


# Must exactly match the expression list in the transactions_dedup_idx unique
# index (supabase/migrations/002_dedup_transactions.sql) — this is what tells
# Postgres which conflicts to treat as "already have this one, skip it".
_DEDUP_CONFLICT_TARGET = "account_id,date,description,coalesce(withdrawal,0),coalesce(credit,0)"


def _insert_transactions(account_id: str, user_id: str, rows: list[dict]) -> tuple[list[str], int]:
    """
    Bulk-insert transactions, skipping any that exactly match a transaction
    already on this account (same date/description/amount) — re-uploading the
    same statement should not double the ledger. Returns (inserted_ids, skipped_count).
    """
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
        return [], 0

    result = (
        supabase.table("transactions")
        .upsert(records, on_conflict=_DEDUP_CONFLICT_TARGET, ignore_duplicates=True)
        .execute()
    )
    inserted_ids = [r["id"] for r in result.data]
    skipped = len(records) - len(inserted_ids)
    return inserted_ids, skipped


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
    filename_lower = (file.filename or "").lower()
    is_csv_by_name = filename_lower.endswith(".csv")
    is_pdf_by_name = filename_lower.endswith(".pdf")
    if file.content_type not in ALLOWED_MIME_TYPES and not is_csv_by_name and not is_pdf_by_name:
        raise HTTPException(status_code=400, detail="Only PDF and CSV files are accepted.")

    content = await file.read()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds 10 MB limit.")

    user_id = current_user["id"]

    # --- Parse + categorise ---
    is_pdf = file.content_type == "application/pdf"
    try:
        if is_pdf:
            raw_text = _extract_pdf_text(content)
            content = b""  # discard immediately after extraction
            if not raw_text.strip():
                raise HTTPException(status_code=422, detail="Could not extract any text from the PDF.")
            # Claude does full extraction (date + amounts + category) in one shot for PDFs
            try:
                rows = _extract_transactions_from_pdf_text(raw_text)
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"AI extraction failed: {e}")
        else:
            rows = _parse_csv(content)
            content = b""
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {e}")
    finally:
        content = b""  # ensure raw bytes are cleared

    if not rows:
        raise HTTPException(status_code=422, detail="No transactions found in the uploaded file.")

    # --- Categorise with Claude/Gemini (CSV only — PDFs already have categories from extraction) ---
    if not is_pdf:
        try:
            rows = _categorise_with_claude(rows)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"AI categorisation failed: {e}")

    # --- Write to database ---
    account_id = _get_or_create_account(user_id, bank)
    tx_ids, skipped_duplicates = _insert_transactions(account_id, user_id, rows)

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
        "duplicates_skipped": skipped_duplicates,
    }
