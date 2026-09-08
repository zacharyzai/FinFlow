#!/usr/bin/env python3
"""
FinFlow seed script — creates three demo users with 6 months of realistic
Singapore spending data.

    demo@finflow.dev    — intern / young professional (~$2,500/mo)
    student@finflow.dev — uni student with part-time F&B job (~$1,100/mo)
    adult@finflow.dev   — working adult, full-time salary (~$4,800/mo)

Usage:
    cd backend
    source venv/bin/activate
    python seed.py

Credentials printed at the end. Re-running will error on duplicate emails —
delete the users in Supabase Auth → Users first.
"""

import random
import sys
from calendar import monthrange
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from supabase import create_client

from app.core.config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL

SEED_PASSWORD = "Finflow123!"
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ── Shared helpers ────────────────────────────────────────────────────────────

def jitter(base: float, pct: float = 0.12) -> float:
    return round(base * (1 + random.uniform(-pct, pct)), 2)

def clamp_day(year: int, month: int, day: int) -> int:
    return min(day, monthrange(year, month)[1])

def make_tx(account_id, user_id, description, amount, category, is_credit, tx_date) -> dict:
    return {
        "account_id":  account_id,
        "user_id":     user_id,
        "date":        tx_date,
        "description": description,
        "withdrawal":  None if is_credit else amount,
        "credit":      amount if is_credit else None,
        "category":    category,
        "state":       "CLEARED",
    }

def month_window(today: date, month_offset: int):
    """Return (month_start, month_end, days_in_range) for a given offset."""
    start = today.replace(day=1) + relativedelta(months=month_offset)
    end   = today if month_offset == 0 else (start + relativedelta(months=1)) - timedelta(days=1)
    return start, end, (end - start).days + 1

def create_user(email: str) -> str:
    res = supabase.auth.admin.create_user({
        "email":         email,
        "password":      SEED_PASSWORD,
        "email_confirm": True,
    })
    return res.user.id

def create_account(user_id: str, name: str, bank: str) -> str:
    res = supabase.table("accounts").insert({
        "user_id":  user_id,
        "name":     name,
        "bank":     bank,
        "currency": "SGD",
    }).execute()
    return res.data[0]["id"]

def insert_transactions(records: list[dict]) -> list[dict]:
    inserted = []
    for i in range(0, len(records), 50):
        res = supabase.table("transactions").insert(records[i:i + 50]).execute()
        inserted.extend(res.data)
    return inserted

def insert_ledger_entries(user_id: str, transactions: list[dict]) -> int:
    entries = []
    for tx in transactions:
        tx_id = tx["id"]
        if tx.get("withdrawal"):
            amt  = tx["withdrawal"]
            slug = tx.get("category", "Other").lower().replace(" & ", ":").replace(" ", "_")
            entries += [
                {"transaction_id": tx_id, "user_id": user_id, "account": f"expenses:{slug}", "entry_type": "DR", "amount": amt},
                {"transaction_id": tx_id, "user_id": user_id, "account": "assets:checking",  "entry_type": "CR", "amount": amt},
            ]
        elif tx.get("credit"):
            amt = tx["credit"]
            entries += [
                {"transaction_id": tx_id, "user_id": user_id, "account": "assets:checking", "entry_type": "DR", "amount": amt},
                {"transaction_id": tx_id, "user_id": user_id, "account": "income:salary",   "entry_type": "CR", "amount": amt},
            ]
    for i in range(0, len(entries), 50):
        supabase.table("ledger_entries").insert(entries[i:i + 50]).execute()
    return len(entries)

def seed_user(label: str, email: str, build_fn, goals: list, expenses: list, account_name: str, bank: str):
    print(f"\n── {label} ({email})")
    try:
        user_id = create_user(email)
    except Exception as e:
        print(f"  ERROR creating user: {e}")
        print("  Tip: delete them in Supabase Auth and re-run.")
        sys.exit(1)
    print(f"  user_id: {user_id}")

    account_id = create_account(user_id, account_name, bank)
    print(f"  account: {account_name}")

    records  = build_fn(user_id, account_id)
    inserted = insert_transactions(records)
    n_ledger = insert_ledger_entries(user_id, inserted)
    print(f"  {len(inserted)} transactions, {n_ledger} ledger entries")

    if goals:
        supabase.table("savings_goals").insert([{**g, "user_id": user_id} for g in goals]).execute()
        print(f"  {len(goals)} savings goals")

    if expenses:
        supabase.table("planned_expenses").insert([{**e, "user_id": user_id} for e in expenses]).execute()
        print(f"  {len(expenses)} planned expenses")

    return email

# ── Profile 1: Intern / Young Professional ────────────────────────────────────
# Income ~$2,500/mo (internship + allowance). Moderate spend across all categories.

def build_professional(user_id: str, account_id: str) -> list[dict]:
    random.seed(42)
    today = date.today()
    records = []

    FOOD = [
        ("Ya Kun Kaya Toast", 5.80), ("Koufu Food Court", 5.20), ("Maxwell Chicken Rice", 4.50),
        ("Mala Xiang Guo", 17.50), ("KFC Singapore", 12.00), ("McDonald's Clementi", 9.80),
        ("LiHo Tea", 6.80), ("Koi Cafe", 7.20), ("Grab Food Delivery", 21.50),
        ("Foodpanda", 18.90), ("NTUC FairPrice", 44.00), ("Starbucks", 11.50),
        ("Toast Box", 7.80), ("Subway Singapore", 10.50), ("Wingstop", 18.00),
    ]
    TRANSPORT = [
        ("EZ-Link Top Up", 30.00), ("Grab Standard", 12.50), ("Grab Premium", 18.00),
        ("Gojek", 11.00), ("ComfortDelGro Taxi", 16.50),
    ]
    SHOPPING = [
        ("Shopee Singapore", 38.00), ("Lazada SG", 29.00), ("Uniqlo Orchard", 59.90),
        ("Zalora", 65.00), ("Daiso Japan", 12.00), ("MUJI VivoCity", 42.00),
        ("Popular Bookstore", 24.00),
    ]
    BILLS  = [("StarHub Mobile", 45.00), ("Netflix", 18.00), ("Spotify Premium", 9.90), ("SP Services", 76.00)]
    ENTERT = [("Golden Village", 15.50), ("Shaw Theatres", 14.00), ("Klook Activity", 42.00), ("K-Box KTV", 35.00)]
    EDUCAT = [("Coursera Plus", 59.00), ("Udemy Course", 24.90), ("Popular Bookstore", 28.00)]
    HEALTH = [("Guardian Pharmacy", 22.50), ("Watsons", 17.00), ("Raffles Medical", 45.00)]
    INCOME = [("Shopee SG Internship Stipend", 1800.00), ("Family Allowance Transfer", 700.00)]
    ANOMALIES = [
        (-4, "Shopee 11.11 Mega Sale",       298.00, "Shopping"),
        (-2, "Grab Surge Late Night",          84.00, "Transport"),
        (-1, "Taylor Swift Concert Tickets",  198.00, "Entertainment"),
    ]

    for mo in range(-5, 1):
        start, _, days = month_window(today, mo)
        rdate = lambda: str(start + timedelta(days=random.randint(0, days - 1)))
        t = lambda desc, amt, cat, credit=False, d=None: make_tx(account_id, user_id, desc, amt, cat, credit, d or rdate())

        income_d = str(start.replace(day=1))
        for desc, base in INCOME:
            records.append(t(desc, jitter(base, 0.02), "Income", credit=True, d=income_d))

        for _ in range(random.randint(8, 12)):
            d, b = random.choice(FOOD);   records.append(t(d, jitter(b), "Food & Dining"))
        for _ in range(random.randint(4, 7)):
            d, b = random.choice(TRANSPORT); records.append(t(d, jitter(b), "Transport"))
        for _ in range(random.randint(2, 3)):
            d, b = random.choice(SHOPPING);  records.append(t(d, jitter(b), "Shopping"))
        for desc, base in BILLS:
            bd = str(start.replace(day=clamp_day(start.year, start.month, random.randint(1, 7))))
            records.append(t(desc, jitter(base, 0.04), "Bills & Utilities", d=bd))
        for _ in range(random.randint(1, 2)):
            d, b = random.choice(ENTERT);  records.append(t(d, jitter(b), "Entertainment"))
        if random.random() > 0.30:
            d, b = random.choice(EDUCAT);  records.append(t(d, jitter(b), "Education"))
        if random.random() > 0.50:
            d, b = random.choice(HEALTH);  records.append(t(d, jitter(b), "Healthcare"))

    for mo, desc, amt, cat in ANOMALIES:
        am = today.replace(day=1) + relativedelta(months=mo)
        records.append(make_tx(account_id, user_id, desc, amt, cat, False,
                               str(am.replace(day=clamp_day(am.year, am.month, 15)))))
    return records

# ── Profile 2: Uni Student with Part-time F&B Job ────────────────────────────
# Income ~$1,100/mo (F&B wages $700 + allowance $400). Very tight budget.
# Hawker-heavy, minimal Grab, mostly EZ-Link, budget shopping only.

def build_student(user_id: str, account_id: str) -> list[dict]:
    random.seed(99)
    today = date.today()
    records = []

    FOOD = [
        ("Kopitiam Breakfast",     3.50), ("Koufu Set Meal",        4.80),
        ("Maxwell Chicken Rice",   3.80), ("Wonton Mee Stall",      4.20),
        ("Old Chang Kee",          2.80), ("NTUC FairPrice",        28.00),
        ("Sheng Siong",            22.50), ("Instant Noodles (NTUC)", 8.50),
        ("McDonald's Value Meal",   6.50), ("LiHo Tea",               4.80),
        ("Breadtalk",              3.20), ("7-Eleven",               4.50),
    ]
    TRANSPORT = [
        ("EZ-Link Top Up",    25.00),  # student concession
        ("EZ-Link Top Up",    25.00),  # appears twice — more likely to pick
        ("Grab Standard",     10.50),  # rare
        ("Bus Concession",    52.00),  # monthly concession pass
    ]
    SHOPPING = [
        ("Shopee Singapore",   18.50),  # budget items
        ("Taobao via EzBuy",   22.00),
        ("Daiso Japan",         8.00),
        ("Carousell Purchase",  15.00),  # second-hand
        ("Popular Bookstore",   16.00),
    ]
    BILLS  = [("Singtel SIM Only", 15.00), ("Spotify Student", 4.99)]
    ENTERT = [("Golden Village", 14.00), ("Shaw Theatres", 12.50), ("Netflix (shared)", 5.00)]
    EDUCAT = [
        ("NUS Co-op Bookstore",  48.00), ("Pearson eBook",       35.00),
        ("Campus Printing",       4.50), ("Coursera (free trial)", 0.00),
        ("School Supplies",      12.00),
    ]
    HEALTH = [("Watsons",  9.50), ("Guardian Pharmacy", 12.00), ("University Health Ctr", 5.00)]

    # F&B wages vary $600–900; allowance is stable $400
    ANOMALIES = [
        (-3, "NUS Textbook Bundle",         185.00, "Education"),   # textbook spike
        (-1, "Grab Surge (missed last MRT)", 32.00, "Transport"),   # transport spike
    ]

    for mo in range(-5, 1):
        start, _, days = month_window(today, mo)
        rdate = lambda: str(start + timedelta(days=random.randint(0, days - 1)))
        t = lambda desc, amt, cat, credit=False, d=None: make_tx(account_id, user_id, desc, amt, cat, credit, d or rdate())

        income_d = str(start.replace(day=1))
        # F&B wages: paid weekly or bi-weekly, irregular amount
        wages = round(random.uniform(600, 900), 2)
        records.append(t("F&B Part-Time Wages",    wages,  "Income", credit=True, d=income_d))
        records.append(t("Parents Monthly Allowance", 400.00, "Income", credit=True, d=income_d))

        # Food — 10–14 per month, mostly cheap hawker
        for _ in range(random.randint(10, 14)):
            d, b = random.choice(FOOD)
            if b == 0.00: continue  # skip free trials
            records.append(t(d, jitter(b, 0.08), "Food & Dining"))

        # Transport — EZ-Link heavy, rare Grab
        for _ in range(random.randint(2, 4)):
            d, b = random.choice(TRANSPORT)
            records.append(t(d, jitter(b, 0.05), "Transport"))

        # Shopping — 1–2 budget purchases per month
        for _ in range(random.randint(1, 2)):
            d, b = random.choice(SHOPPING)
            records.append(t(d, jitter(b, 0.10), "Shopping"))

        # Bills — minimal (SIM + Spotify student)
        for desc, base in BILLS:
            bd = str(start.replace(day=clamp_day(start.year, start.month, 5)))
            records.append(t(desc, base, "Bills & Utilities", d=bd))

        # Entertainment — ~50% chance, very cheap
        if random.random() > 0.50:
            d, b = random.choice(ENTERT)
            records.append(t(d, jitter(b, 0.05), "Entertainment"))

        # Education — frequent (uni student)
        if random.random() > 0.20:
            d, b = random.choice(EDUCAT)
            if b > 0:
                records.append(t(d, jitter(b, 0.05), "Education"))

        # Healthcare — occasional
        if random.random() > 0.65:
            d, b = random.choice(HEALTH)
            records.append(t(d, jitter(b, 0.05), "Healthcare"))

    for mo, desc, amt, cat in ANOMALIES:
        am = today.replace(day=1) + relativedelta(months=mo)
        records.append(make_tx(account_id, user_id, desc, amt, cat, False,
                               str(am.replace(day=clamp_day(am.year, am.month, 10)))))
    return records

# ── Profile 3: Working Adult ──────────────────────────────────────────────────
# Income ~$4,800/mo salary. Full spending across all categories.
# Pays rent, gym, insurance. Occasional dining out + weekend trips.

def build_adult(user_id: str, account_id: str) -> list[dict]:
    random.seed(77)
    today = date.today()
    records = []

    FOOD = [
        ("Koufu Food Court",       7.50), ("Hawker Chan",           12.00),
        ("Burnt Ends",             85.00), ("Nando's VivoCity",     32.00),
        ("Tim Ho Wan",             28.00), ("Sushi Tei",            55.00),
        ("Grab Food Delivery",     32.00), ("Foodpanda",            28.50),
        ("Cold Storage",           68.00), ("NTUC FairPrice",       55.00),
        ("Starbucks Raffles Place",13.50), ("Shake Shack",          22.00),
        ("Ya Kun Kaya Toast",       6.50), ("Subway Singapore",     12.00),
        ("Jollibee",               14.00),
    ]
    TRANSPORT = [
        ("EZ-Link Top Up",      30.00), ("Grab Premium",          22.00),
        ("Grab Standard",       14.50), ("Gojek",                 13.00),
        ("Shell Petrol",       120.00), ("ERP / Season Parking",  85.00),
        ("ComfortDelGro Taxi",  28.00),
    ]
    SHOPPING = [
        ("Uniqlo Orchard",     89.00), ("Zara Singapore",       129.00),
        ("Charles & Keith",    95.00), ("Shopee Singapore",      65.00),
        ("IKEA Alexandra",    145.00), ("Harvey Norman",        220.00),
        ("Lazada SG",          48.00), ("Sephora",               78.00),
        ("Decathlon",          55.00),
    ]
    BILLS = [
        ("Singtel Postpaid",   65.00), ("Netflix",               18.00),
        ("Spotify Premium",     9.90), ("SP Services",          110.00),
        ("Apple One",          22.98), ("Disney+ Hotstar",       11.98),
        ("Room Rental",      1400.00),  # biggest fixed cost
    ]
    ENTERT = [
        ("Golden Village Suntec",  18.00), ("Klook Activity",       68.00),
        ("CÉ LA VI Rooftop Bar",   95.00), ("Timbre Music Bistro",  55.00),
        ("Shaw Theatres",          16.00), ("Sentosa Day Trip",     45.00),
    ]
    HEALTH = [
        ("Virgin Active Gym",  88.00), ("Raffles Medical",    65.00),
        ("Dental Clinic",     120.00), ("Guardian Pharmacy",  28.00),
        ("My Gym Supplement",  55.00),
    ]
    TRAVEL = [
        ("Scoot Airlines JB",   98.00), ("Agoda Hotel Batam",   145.00),
        ("Grab (Changi)",        35.00), ("Money Changer",        85.00),
    ]
    ANOMALIES = [
        (-4, "Singapore Airlines Bangkok",  650.00, "Travel"),
        (-2, "Tiffany & Co. (Birthday Gift)", 288.00, "Shopping"),
        (-1, "IKEA Bedroom Overhaul",        485.00, "Shopping"),
    ]

    for mo in range(-5, 1):
        start, _, days = month_window(today, mo)
        rdate = lambda: str(start + timedelta(days=random.randint(0, days - 1)))
        t = lambda desc, amt, cat, credit=False, d=None: make_tx(account_id, user_id, desc, amt, cat, credit, d or rdate())

        income_d = str(start.replace(day=1))
        records.append(t("OCBC Bank Salary Credit", jitter(4800.00, 0.02), "Income", credit=True, d=income_d))

        # Food — 10–14 per month, mix of hawker and restaurants
        for _ in range(random.randint(10, 14)):
            d, b = random.choice(FOOD)
            records.append(t(d, jitter(b), "Food & Dining"))

        # Transport — 5–8 per month (car + Grab)
        for _ in range(random.randint(5, 8)):
            d, b = random.choice(TRANSPORT)
            records.append(t(d, jitter(b, 0.08), "Transport"))

        # Shopping — 2–4 per month, higher amounts
        for _ in range(random.randint(2, 4)):
            d, b = random.choice(SHOPPING)
            records.append(t(d, jitter(b), "Shopping"))

        # Bills — all fixed, paid early month (rent on 1st)
        for desc, base in BILLS:
            day = 1 if "Rental" in desc else random.randint(3, 8)
            bd = str(start.replace(day=clamp_day(start.year, start.month, day)))
            records.append(t(desc, jitter(base, 0.03), "Bills & Utilities", d=bd))

        # Entertainment — 1–3 per month (more disposable income)
        for _ in range(random.randint(1, 3)):
            d, b = random.choice(ENTERT)
            records.append(t(d, jitter(b), "Entertainment"))

        # Healthcare — gym every month, medical occasionally
        records.append(t("Virgin Active Gym", jitter(88.00, 0.02), "Healthcare",
                          d=str(start.replace(day=clamp_day(start.year, start.month, 2)))))
        if random.random() > 0.60:
            d, b = random.choice(HEALTH[1:])
            records.append(t(d, jitter(b), "Healthcare"))

        # Travel — occasional (every 2nd month roughly)
        if random.random() > 0.55:
            d, b = random.choice(TRAVEL)
            records.append(t(d, jitter(b), "Travel"))

    for mo, desc, amt, cat in ANOMALIES:
        am = today.replace(day=1) + relativedelta(months=mo)
        records.append(make_tx(account_id, user_id, desc, amt, cat, False,
                               str(am.replace(day=clamp_day(am.year, am.month, 20)))))
    return records

# ── Goals & planned expenses per profile ─────────────────────────────────────

def goals_professional(today):
    return [
        {"name": "Japan Trip",    "target": 3000.00, "saved":  820.00, "deadline": str(today + relativedelta(months=6))},
        {"name": "Emergency Fund","target": 5000.00, "saved": 1250.00, "deadline": str(today + relativedelta(months=12))},
        {"name": "New MacBook Pro","target":1599.00, "saved":  640.00, "deadline": str(today + relativedelta(months=4))},
    ]

def expenses_professional(today):
    y, m = today.year, today.month
    due = lambda d: str(date(y, m, clamp_day(y, m, d)))
    items = [
        {"name": "StarHub Mobile", "amount": 45.00, "due_date": due(5),  "category": "Bills & Utilities"},
        {"name": "Netflix",        "amount": 18.00, "due_date": due(1),  "category": "Entertainment"},
        {"name": "Spotify",        "amount":  9.90, "due_date": due(5),  "category": "Entertainment"},
        {"name": "SP Services",    "amount": 76.00, "due_date": due(20), "category": "Bills & Utilities"},
        {"name": "Gym Membership", "amount": 60.00, "due_date": due(15), "category": "Healthcare"},
    ]
    # All of these are real recurring bills — mark them so /budget/upcoming and
    # /budget/daily keep projecting them into future months instead of the
    # one seeded due_date going stale the moment this month ends.
    return [{**e, "is_recurring": True, "recurrence_days": 30} for e in items]

def goals_student(today):
    return [
        {"name": "Graduation Trip (Bali)", "target": 1200.00, "saved":  280.00, "deadline": str(today + relativedelta(months=8))},
        {"name": "Emergency Fund",         "target": 2000.00, "saved":  350.00, "deadline": str(today + relativedelta(months=18))},
        {"name": "New Laptop (entry)",     "target":  899.00, "saved":  210.00, "deadline": str(today + relativedelta(months=5))},
    ]

def expenses_student(today):
    y, m = today.year, today.month
    due = lambda d: str(date(y, m, clamp_day(y, m, d)))
    items = [
        {"name": "Singtel SIM Only", "amount": 15.00, "due_date": due(5),  "category": "Bills & Utilities"},
        {"name": "Spotify Student",  "amount":  4.99, "due_date": due(5),  "category": "Entertainment"},
        {"name": "Bus Concession",   "amount": 52.00, "due_date": due(1),  "category": "Transport"},
    ]
    return [{**e, "is_recurring": True, "recurrence_days": 30} for e in items]

def goals_adult(today):
    return [
        {"name": "BTO Down Payment",    "target": 50000.00, "saved": 12400.00, "deadline": str(today + relativedelta(months=24))},
        {"name": "Europe Holiday 2027", "target":  6000.00, "saved":  1800.00, "deadline": str(today + relativedelta(months=18))},
        {"name": "Wedding Fund",        "target": 30000.00, "saved":  8500.00, "deadline": str(today + relativedelta(months=30))},
    ]

def expenses_adult(today):
    y, m = today.year, today.month
    due = lambda d: str(date(y, m, clamp_day(y, m, d)))
    items = [
        {"name": "Room Rental",         "amount": 1400.00, "due_date": due(1),  "category": "Bills & Utilities"},
        {"name": "Singtel Postpaid",    "amount":   65.00, "due_date": due(5),  "category": "Bills & Utilities"},
        {"name": "SP Services",         "amount":  110.00, "due_date": due(18), "category": "Bills & Utilities"},
        {"name": "Virgin Active Gym",   "amount":   88.00, "due_date": due(2),  "category": "Healthcare"},
        {"name": "Netflix",             "amount":   18.00, "due_date": due(7),  "category": "Entertainment"},
        {"name": "Prudential Insurance","amount":  180.00, "due_date": due(10), "category": "Bills & Utilities"},
    ]
    return [{**e, "is_recurring": True, "recurrence_days": 30} for e in items]

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("FinFlow seed script — 3 profiles")
    print("=" * 42)

    today = date.today()
    seeded = []

    seeded.append(seed_user(
        label        = "Intern / Young Professional",
        email        = "demo@finflow.dev",
        build_fn     = build_professional,
        goals        = goals_professional(today),
        expenses     = expenses_professional(today),
        account_name = "DBS Multiplier",
        bank         = "DBS",
    ))

    seeded.append(seed_user(
        label        = "Uni Student (Part-time F&B)",
        email        = "student@finflow.dev",
        build_fn     = build_student,
        goals        = goals_student(today),
        expenses     = expenses_student(today),
        account_name = "POSB Savings",
        bank         = "DBS",
    ))

    seeded.append(seed_user(
        label        = "Working Adult",
        email        = "adult@finflow.dev",
        build_fn     = build_adult,
        goals        = goals_adult(today),
        expenses     = expenses_adult(today),
        account_name = "OCBC 360",
        bank         = "OCBC",
    ))

    print("\n" + "=" * 42)
    print("All done. Login credentials (password same for all):")
    print(f"  Password: {SEED_PASSWORD}\n")
    for email in seeded:
        print(f"  {email}")
