# FinFlow 💸
> AI-Powered Personal Finance Platform · Singapore Fintech · Summer Learning Project

Upload your bank statement → Claude AI parses every transaction → get a personalised daily budget and financial health score. Live at [fin-flow-pi-eight.vercel.app](https://fin-flow-pi-eight.vercel.app).

---

## What It Does

FinFlow eliminates the biggest reason people abandon budgeting apps — manual expense entry. Upload your DBS, OCBC, or UOB bank statement and Claude AI (falling back to Gemini) automatically reads and categorises every transaction. The app analyses spending patterns, flags unusual transactions, and tracks month-over-month trends on an interactive dashboard.

**Daily Budget Formula:**
```
Daily Budget = (Income − Bills − Planned Expenses − Savings Goal) ÷ Days Remaining
```

Under the hood, every transaction is recorded using a **double-entry ledger** and moves through a payment state machine (`PENDING → CLEARED → FAILED`) — the same primitives used by Stripe and PayPal — with a nightly reconciliation job (2AM SGT) keeping the books balanced.

---

## Features

### 📄 Smart PDF / CSV Parsing
- Upload DBS, OCBC, and UOB statements
- Claude AI reads and categorises every transaction row (falls back to Gemini if no Anthropic key is set)
- Pandas cleans and normalises CSV exports
- Raw file deleted immediately after parsing

### 📊 Spending Dashboard
- Category breakdown (Food, Transport, Entertainment, etc.)
- Month-over-month trend charts
- Unusual transaction detection via 2σ deviation rule
- Interactive charts, responsive down to phone width

### 🗓️ Prescriptive Budget Planner
- Calendar view for upcoming planned expenses
- Daily budget with a spendable-pool breakdown

### 🏆 Financial Health Score
- Composite score (0–100), updated monthly
- Per-dimension breakdown, weakest dimension highlighted
- AI-generated tip targeting the weakest dimension

### 🎯 Savings Goal Tracker
- Set goal name, target amount, and deadline
- Visual progress bar per goal

### 🏦 Fintech-Grade Backend
- Double-entry ledger for every transaction (upload flow and manual add both write DR/CR pairs)
- Payment state machine (`PENDING → CLEARED → FAILED`)
- Nightly reconciliation job at 2AM SGT
- Same accounting model used by Stripe and PayPal

### 🤖 Telegram Bot
- Link your account from Settings, then query from Telegram directly: `/goal`, `/dbudget`, `/mbudget`, `/recommendation`
- `/recommendation` uses Claude/Gemini to suggest one or two concrete things to cut back on, based on this month's spending
- Pull-only by design — you ask, it answers. No proactive push notifications.

### 📱 Quick-Add iOS Shortcut
- Generate a personal access token from Settings, wire it into an iOS Shortcut, bind it to Back Tap
- Double-tap the back of your phone → pick a category → enter an amount → logged straight into FinFlow, no app needed
- The token can only create withdrawal transactions — it can't touch anything else in your account, even if leaked

---

## Tech Stack

### Frontend
| Technology | Role |
|---|---|
| Vue.js 3 | UI framework — Composition API, `<script setup>` |
| Tailwind CSS v4 | Utility-first styling |
| Pinia | Client state management |
| Supabase JS | Auth session and direct DB reads (RLS-protected) from the client |
| Axios | HTTP client for FastAPI calls |
| VueUse | Composables — dark mode, storage, etc. |
| Vercel Web Analytics | Visitor/page-view tracking |

### Backend
| Technology | Role |
|---|---|
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Pandas | CSV parsing, categorisation, analytics |
| pdfplumber | PDF table extraction before Claude parsing |
| Anthropic SDK | Claude API client for AI parsing (falls back to Gemini via Google Gen AI SDK) |
| Supabase Python | Server-side DB reads and writes (writes use the service role key) |
| APScheduler | Nightly 2AM SGT reconciliation cron job |
| slowapi | Rate limiting on upload, auth, and token endpoints |

### Database & Auth
| Component | Technology | Role |
|---|---|---|
| Primary DB | Supabase PostgreSQL | All app data — transactions, goals, scores, tokens |
| Row Level Security | Supabase RLS | Users can only query their own rows |
| Authentication | Supabase Auth | JWT sessions, email/password, OTP |
| Personal access tokens | `api_tokens` table (SHA-256 hashed) | Auth for the Quick-Add Shortcut, scoped to `POST /transactions` only |
| Ledger | PostgreSQL | Double-entry ledger entries per transaction |
| Cron Log | PostgreSQL | Nightly reconciliation run history |

### AI & Integrations
| Service | Provider | Role |
|---|---|---|
| AI Parsing | Claude API (Anthropic), falls back to Gemini | PDF statement reading and categorisation |
| AI Recommendations | Claude/Gemini | Telegram `/recommendation` spending tips |
| Bot | Telegram Bot API | Pull-based budget/goal queries from chat |

### Hosting & DevOps
| Layer | Technology | Role |
|---|---|---|
| Frontend | Vercel | Auto-deploy from GitHub on push to `main`, CDN, HTTPS |
| Backend | Railway | FastAPI container, auto-deploy from GitHub, env vars set in dashboard |
| Dev Proxy | Vite dev server | Proxies `/api` to FastAPI locally |

---

## Architecture Flow

```
Upload     →  User uploads PDF or CSV via Vue.js frontend (Vercel)
Parse      →  FastAPI validates file → Pandas cleans CSV or Claude API reads PDF → raw file deleted
Ledger     →  Each transaction creates two ledger entries (double-entry debit + credit) in Supabase
State      →  Transactions enter PENDING; 2AM SGT cron job moves balanced ones to CLEARED
Analytics  →  Pandas computes monthly trends, anomaly flags, and health score dimensions
Dashboard  →  Vue.js fetches JSON from FastAPI and renders charts
Chat       →  Telegram bot answers /goal, /dbudget, /mbudget, /recommendation on request
Quick-Add  →  iOS Shortcut (Back Tap) posts amount + category straight to /transactions via a personal access token
```

---

## Database Schema

| Table | Key Columns | Notes |
|---|---|---|
| `users` | id, email, created_at | Managed by Supabase Auth |
| `accounts` | id, user_id, name, currency | One user → many accounts |
| `transactions` | id, account_id, date, description, withdrawal, credit, category, state | Parsed from statements or added manually/via Quick-Add |
| `ledger_entries` | id, transaction_id, account, entry_type (DR/CR), amount | Double-entry rows |
| `planned_expenses` | id, user_id, name, amount, due_date, category | User-added future costs |
| `savings_goals` | id, user_id, name, target, saved, deadline | Goal tracking |
| `health_scores` | id, user_id, month, score, dimensions (JSONB) | Monthly computed score |
| `reconciliation_log` | id, run_date, total_processed, discrepancies | Nightly job output |
| `telegram_links` | id, user_id, chat_id, link_token, token_expires_at | Telegram account linking |
| `api_tokens` | id, user_id, token_hash, created_at, last_used_at | Quick-Add Shortcut personal access tokens |

---

## Security Model

| Layer | Implementation |
|---|---|
| Authentication | Supabase Auth with JWT sessions. |
| Row Level Security | RLS enforced on every table — users can only query their own rows, enforced at DB level. |
| Quick-Add tokens | Long-lived personal access token, SHA-256 hashed at rest, one active token per user, scoped to `POST /transactions` only and restricted to withdrawal-type transactions. Revocable from Settings. |
| File Handling | Statements stored in private Supabase buckets. Deleted immediately post-parse. |
| API Keys | All keys (Claude, Gemini, Supabase service role, Telegram) stored server-side in `.env` / Railway env vars only. Never sent to the client. |
| Logging Policy | No financial data (amounts, merchant names) or secrets (tokens) in server logs. |
| Rate Limiting | Upload, auth, and token endpoints rate-limited via slowapi. |
| PDPA Compliance | Data minimisation applied — only store what the app needs. |

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Supabase](https://supabase.com) project
- An [Anthropic API key](https://console.anthropic.com) (or a [Gemini API key](https://aistudio.google.com/apikey) as a free fallback)

### Backend Setup

```bash
git clone https://github.com/zacharyzai/FinFlow.git
cd FinFlow/backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Fill in your keys in .env

# Run the development server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd FinFlow/frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Fill in your Supabase URL and anon key

# Run the development server
npm run dev
```

### Environment Variables

```env
# Backend (backend/.env) — see backend/.env.example for the full list
CORS_ORIGINS=http://localhost:5173
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_SECRET=a_random_secret_you_choose
TELEGRAM_BOT_USERNAME=your_bot_username_without_the_at_sign

# Frontend (frontend/.env) — see frontend/.env.example
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
VITE_API_URL=  # leave blank in dev — Vite proxies /api to localhost:8000
```

### Deploying

Both deployments auto-deploy from GitHub on push to `main`:
- **Backend (Railway)**: set Root Directory to `backend`, add the same env vars as above in the Variables tab (Railway doesn't read `.env` files).
- **Frontend (Vercel)**: set Root Directory to `frontend`, add `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` / `VITE_API_URL` (pointed at your Railway URL) in Project Settings.
- Don't forget to add the Vercel domain to the backend's `CORS_ORIGINS`.

---

## Roadmap

### Phase 1 — MVP ✅
- [x] Statement upload (PDF + CSV) + Claude/Gemini AI parsing
- [x] Spending dashboard
- [x] Double-entry ledger + payment state machine
- [x] Daily budget calculator
- [x] Savings goal tracker
- [x] Supabase Auth + RLS security

### Phase 2 — Enrich
- [x] Financial Health Score (0–100)
- [x] Telegram bot (pull-based: `/goal`, `/dbudget`, `/mbudget`, `/recommendation`)
- [x] Quick-Add iOS Shortcut (personal access token auth)
- [x] Mobile-responsive dashboard
- [ ] Telegram proactive daily budget push (not built — bot is pull-only today)
- [ ] Monthly email report

### Phase 3 — Not Started
- [ ] Receipt photo scanning
- [ ] Multi-account aggregation
- [ ] PDF export of monthly report
- [ ] Multi-currency support

---

## Disclaimer

Raw bank statements are never stored — they are deleted immediately after parsing. This is a summer portfolio project and is not affiliated with DBS, OCBC, UOB, or the Monetary Authority of Singapore.
