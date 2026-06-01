# CLAUDE.md — FinFlow

> AI-Powered Personal Finance Platform · Singapore Fintech · Summer Learning Project

This file tells Claude how to assist on FinFlow. Read it before helping with any code, explanation, or review.

---

## About Me

- **Experience level:** Intermediate — comfortable with JavaScript and Python, but new to Vue.js and FastAPI
- **This is a summer learning project.** I want to actually understand what I'm building, not just ship code.
- **Learning goals this summer:**
  - AI/Claude API integration
  - Fintech patterns (double-entry ledger, payment state machine)
  - Full-stack architecture (Vue 3 + FastAPI)
  - Security & auth (Supabase RLS, JWT)
  - DevOps (CI/CD with GitHub Actions, Railway, Vercel)

---

## How Claude Should Help Me

### Always do this

1. **Explain the concept before writing code.** What is it? Why does it exist? What problem does it solve?
2. **Give a simple analogy or real-world example** — then connect it back to how it applies to FinFlow specifically.
3. **Point out security and fintech best practices** as they come up. Flag anything that would be done differently in a production fintech app vs. a quick prototype.
4. **Suggest improvements and do light code review.** If you spot something that could be cleaner, more secure, or more idiomatic — say so, briefly.

### Teaching style I want

- Assume I understand programming fundamentals — skip "what is a variable" basics.
- Don't assume I know Vue, FastAPI, or fintech patterns — explain these from scratch with analogies.
- Keep explanations concise. One good analogy beats three paragraphs of theory.
- After explaining, connect it to FinFlow: *"In our case, this means..."*

### Don't do this

- Don't just hand me complete files without explanation.
- Don't skip the "why" — I want to understand, not copy-paste.
- Don't be overly cautious with security warnings to the point of paralysis — flag risks clearly but keep moving.

---

## Project Overview

FinFlow eliminates manual expense entry. Users upload a DBS/OCBC/UOB bank statement → Claude AI parses and categorises every transaction → the app produces a daily budget and a Financial Health Score (0–100).

**The formula at the heart of it:**
```
Daily Budget = (Income − Bills − Planned Expenses − Savings Goal) ÷ Days Remaining
```

**Three fintech primitives under the hood (key learning goals):**
- Double-entry ledger — every transaction creates two entries (debit + credit)
- Payment state machine — `PENDING → CLEARED → FAILED`
- Nightly reconciliation job — runs at 2AM, checks books balance

---

## Tech Stack

### Frontend (Vue 3 on Vercel)
| Technology | Version | Role |
|---|---|---|
| Vue.js 3 | ^3.4 | UI framework |
| Tailwind CSS | ^3.4 | Utility-first styling |
| Vue-ChartJS | ^5.3 | Spending charts |
| Pinia | ^2.1 | State management |
| Supabase JS | latest | Auth + direct DB queries |
| Axios | ^1.7 | HTTP client for FastAPI |
| VueUse | ^10 | Composables |

### Backend (FastAPI on Railway)
| Technology | Version | Role |
|---|---|---|
| FastAPI | 0.111 | REST API |
| Uvicorn | standard | ASGI server |
| Pandas | 2.2 | CSV parsing + analytics |
| pdfplumber | 0.11 | PDF table extraction |
| Anthropic SDK | 0.28 | Claude API client |
| Supabase Python | 2.4 | Server-side DB |
| APScheduler | 3.10 | 2AM reconciliation cron |
| slowapi | 0.1 | Rate limiting |

### Database & Auth (Supabase)
- PostgreSQL for all app data
- Row Level Security (RLS) — users only see their own rows
- Supabase Auth — JWT sessions, Google OAuth, optional MFA
- Supabase Storage — temporary statement uploads (private bucket, deleted post-parse)

### AI & Integrations
| Service | Provider |
|---|---|
| AI parsing | Claude API (Anthropic) |
| SGD FX rates | MAS API |
| Multi-currency | Exchange Rates API |
| Calendar sync | Google Calendar API |
| Daily alerts | Telegram Bot API |
| Monthly report | Resend |

---

## Architecture Flow

```
User uploads PDF/CSV (Vue.js on Vercel)
        ↓
FastAPI (Railway) validates → Pandas cleans CSV OR Claude API reads PDF → raw file deleted
        ↓
Each transaction → 2 ledger entries (double-entry debit + credit) written to Supabase
        ↓
Transactions enter PENDING state → 2AM cron job reconciles → CLEARED
        ↓
Pandas computes trends, anomaly flags (2σ rule), health score
        ↓
Vue.js fetches JSON from FastAPI → renders charts via Vue-ChartJS
        ↓
Telegram Bot: daily budget reminder | Resend: monthly email report
```

---

## Database Schema

```
users              → id, email, created_at
accounts           → id, user_id, name, currency
transactions       → id, account_id, date, description, withdrawal, credit, category, state
ledger_entries     → id, transaction_id, account, entry_type (DR/CR), amount
planned_expenses   → id, user_id, name, amount, due_date, category
savings_goals      → id, user_id, name, target, saved, deadline
health_scores      → id, user_id, month, score, dimensions (JSONB)
reconciliation_log → id, run_date, total_processed, discrepancies
```

---

## Security Model (Important — refer to this often)

| Concern | Implementation |
|---|---|
| Auth | Supabase JWT sessions, Google OAuth, optional MFA |
| Data isolation | RLS on every table — enforced at DB level, not just app level |
| File handling | Private Supabase buckets, deleted immediately post-parse, signed URLs with short expiry |
| API keys | Server-side `.env` only — never sent to client |
| Logging | No financial data (amounts, merchant names) in logs — only event types + user IDs |
| Rate limiting | `slowapi` on upload/parse endpoints — prevents abuse and AI cost blowouts |
| PDPA compliance | Data minimisation — only store what's needed, user can delete all data on request |

> **Fintech rule of thumb:** In Singapore, PDPA applies. Any time we handle financial data, ask: "Do we need to store this, or can we derive what we need and discard the raw data?" FinFlow's answer: parse and discard the statement file immediately.

---

## Key Learning Concepts — How Claude Should Teach Them

When I ask about any of these, use the pattern: **concept → analogy → how it applies to FinFlow**.

### Double-Entry Ledger
Every transaction creates two entries. If I spend $10 on food, we debit my "Food Expenses" account and credit my "Bank Account". The books must always balance. This is how every bank, Stripe, and PayPal works internally.

*When helping here: explain why this matters for auditability and why single-entry is dangerous in financial apps.*

### Payment State Machine (`PENDING → CLEARED → FAILED`)
A transaction doesn't just "exist" — it moves through states. Think of it like a parcel: it's been sent (PENDING), delivered and signed for (CLEARED), or lost (FAILED). The state machine enforces valid transitions and prevents impossible states.

*When helping here: explain what happens if we skip state validation, and what the nightly reconciliation job is checking for.*

### Vue 3 Composition API
I'm new to Vue. When explaining Vue concepts, contrast with React if helpful — I have some React exposure. Key things to explain when they come up: `ref` vs `reactive`, composables (like React hooks), `<script setup>`, Pinia for state (like Zustand/Redux).

### FastAPI
I know Flask basics. When FastAPI concepts come up, briefly contrast with Flask. Key things to explain: async/await in Python, Pydantic models for validation, dependency injection, how FastAPI auto-generates OpenAPI docs.

### Supabase RLS
Row Level Security is PostgreSQL-level access control — the database itself enforces "you can only see your rows", not just the app. Think of it as a bouncer built into the database, not just the front door. Even if the app has a bug, the DB won't leak other users' data.

*When helping here: always flag if I'm writing a query that bypasses RLS (e.g. using the service role key client-side).*

### JWT Authentication
A JWT is a signed token the server issues after login. The client sends it with every request. The server verifies the signature without hitting the database. Think of it like a stamped wristband at an event — the bouncer checks the stamp, not a list.

### Claude API Integration (AI Parsing)
The most unique part of this project. When I ask about the parsing flow, explain: prompt engineering for structured output, how to handle malformed AI responses gracefully, cost control (tokens), and why we use `pdfplumber` to pre-extract tables before sending to Claude (reduces token cost and improves accuracy).

---

## Development Phases

### Phase 1 — MVP (Build first)
- [ ] Statement upload (PDF + CSV) + Claude AI parsing
- [ ] Spending dashboard with Vue-ChartJS
- [ ] Double-entry ledger + state machine
- [ ] Daily budget calculator
- [ ] Savings goal tracker
- [ ] Supabase Auth + RLS security

### Phase 2 — Enrich
- [ ] Financial Health Score (0–100)
- [ ] MAS API for live SGD rates
- [ ] Google Calendar sync
- [ ] Telegram daily budget alerts
- [ ] Monthly email report via Resend

### Phase 3 — Impress
- [ ] Receipt photo scanning (Veryfi)
- [ ] MyInfo / Singpass integration
- [ ] Multi-account aggregation
- [ ] PDF export of monthly report
- [ ] AI personalised saving tips

---

## Conventions & Preferences

### Code style
- Python: follow PEP 8, use type hints everywhere (FastAPI relies on them for Pydantic)
- JavaScript/Vue: use `<script setup>` syntax, Composition API only (not Options API)
- Keep functions small and single-purpose — especially in the parsing pipeline
- No financial data in `console.log` or `print()` statements

### File structure hints
```
frontend/
  src/
    views/          # Page-level Vue components
    components/     # Reusable UI components
    stores/         # Pinia stores
    composables/    # Reusable logic (like React hooks)
    api/            # Axios calls to FastAPI

backend/
  app/
    routers/        # FastAPI route handlers
    services/       # Business logic (parsing, ledger, scoring)
    models/         # Pydantic schemas
    db/             # Supabase client + queries
    jobs/           # APScheduler cron jobs
```

### Git hygiene
- Commit messages: `feat:`, `fix:`, `chore:`, `docs:` prefixes
- Never commit `.env` files — use `.env.example` with placeholder values
- GitHub Actions runs on every push — don't merge if CI is red

---

## Things to Flag Proactively

Whenever any of these come up in my code or questions, raise them without being asked:

- **Hardcoded secrets** — API keys, Supabase URLs in frontend code
- **Missing RLS** — any new table that doesn't have row-level security
- **Raw SQL with user input** — potential SQL injection
- **Logging financial data** — amounts, merchant names, account numbers in logs
- **Service role key misuse** — using the Supabase admin key on the client side bypasses RLS entirely
- **Unvalidated file uploads** — always validate MIME type and size before passing to Claude/pdfplumber
- **AI response not validated** — Claude's output should always be parsed defensively (it can hallucinate categories or miss rows)
- **Token cost spikes** — warn if a prompt design would send the entire raw PDF text to Claude unnecessarily

---

*FinFlow · Summer Portfolio Project · Singapore Fintech Focus*
*Raw bank statements are never stored — deleted immediately after parsing.*
