# fintech-proj
summer project


# FinFlow 💸

**AI-Powered Personal Finance Platform**

FinFlow eliminates the biggest reason people abandon budgeting apps: manual expense entry. Simply upload your bank statement, and our AI automatically reads and categorises every transaction. 

Get a personalised daily budget, track your financial health, and achieve your savings goals with a fintech-grade double-entry ledger backend.

---

## 🌟 Key Features

* **Smart PDF/CSV Parsing:** Upload statements from DBS, OCBC, or UOB. Claude AI reads and categorizes every row, while Pandas cleans and normalizes CSV exports. (Raw files are deleted immediately after parsing for privacy).
* **Prescriptive Budget Planner:** Calculates a safe daily spending budget (Income - Bills - Planned Expenses - Savings Goal) / Days Remaining. Features a calendar view and Google Calendar sync for upcoming expenses.
* **Spending Dashboard:** Interactive Vue-ChartJS visualizations for category breakdowns, month-over-month trend charts, and unusual transaction detection.
* **Financial Health Score:** A 0-100 composite score updated monthly, grading savings rate, expense volatility, bill regularity, and budget adherence. Includes AI-generated tips on your weakest dimensions.
* **Fintech-Grade Backend:** Every transaction is recorded using a double-entry ledger and moves through a payment state machine (PENDING → CLEARED) with a nightly 2 AM reconciliation job.

---

## 🛠️ Tech Stack

### Frontend (Hosted on Vercel)
* **Vue.js 3** & **Pinia** (State Management)
* **Tailwind CSS** (Styling)
* **Vue-ChartJS** (Visualizations)
* **Supabase JS** (Auth & Client DB Queries)

### Backend (Hosted on Railway)
* **FastAPI** & **Uvicorn** (REST API)
* **Pandas** (CSV parsing & analytics)
* **pdfplumber** & **Anthropic SDK (Claude)** (PDF table extraction and AI categorization)
* **APScheduler** (Nightly reconciliation cron job)
* **slowapi** (Upload rate limiting)

### Database, Auth & Integrations
* **Supabase:** PostgreSQL (Primary DB), Supabase Auth (JWT, OAuth), Supabase Storage (Private Buckets)
* **External APIs:** Claude API, MAS API (SGD FX rates), Exchange Rates API, Google Calendar API, Telegram Bot API (Alerts), Resend (Monthly reports)

---

## 🏗️ Architecture Flow

1. **Upload:** User uploads a PDF or CSV statement via the Vue.js frontend.
2. **Parse:** FastAPI validates the file. Pandas cleans CSVs, or Claude API categorizes PDFs. The raw file is immediately deleted.
3. **Ledger Write:** Each transaction creates two ledger entries (double-entry debit + credit) in the Supabase DB.
4. **State Machine:** Transactions enter a `PENDING` state; a 2 AM cron job moves balanced ones to `CLEARED`.
5. **Analytics:** Pandas computes monthly trends, anomaly flags, and health score dimensions.
6. **Dashboard:** Vue.js fetches JSON from FastAPI and renders charts.
7. **Notify:** Telegram Bot sends daily budget reminders; Resend delivers a monthly email report.

---

## 🔒 Security Model

* **Authentication & RLS:** Supabase Auth with Row Level Security (RLS) ensures users can only query their own rows.
* **Data Minimization (PDPA Compliant):** Statements are stored in private buckets and deleted immediately post-parse. No financial data (amounts, merchant names) is kept in server logs.
* **Secure Keys:** All API keys are stored server-side in environment variables.

---

## 🚀 Getting Started

### Prerequisites
* Node.js (v18+)
* Python 3.10+
* Supabase CLI (optional, for local DB development)
* API Keys: Supabase, Anthropic (Claude), Telegram Bot, Resend

### Environment Variables
Create a `.env` file in the backend directory with the following:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
ANTHROPIC_API_KEY=your_claude_api_key
TELEGRAM_BOT_TOKEN=your_telegram_token
RESEND_API_KEY=your_resend_key