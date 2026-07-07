
-- FinFlow — Initial Schema

drop view  if exists public.monthly_spending;
drop table if exists public.reconciliation_log cascade;
drop table if exists public.health_scores      cascade;
drop table if exists public.savings_goals      cascade;
drop table if exists public.planned_expenses   cascade;
drop table if exists public.ledger_entries     cascade;
drop table if exists public.transactions       cascade;
drop table if exists public.accounts           cascade;

drop type if exists transaction_state;
drop type if exists entry_type;
drop type if exists expense_category;

-- extension
create extension if not exists "uuid-ossp";

-- Enums

create type transaction_state as enum ('PENDING', 'CLEARED', 'FAILED');
create type entry_type        as enum ('DR', 'CR');
create type expense_category  as enum (
  'Food & Dining',
  'Transport',
  'Shopping',
  'Bills & Utilities',
  'Healthcare',
  'Entertainment',
  'Travel',
  'Education',
  'Income',
  'Transfer',
  'Other'
);

-- Helper function: auto-update updated_at column

create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;


-- 1. accounts
--    One user → many accounts (DBS, OCBC, UOB …)

create table public.accounts (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  name       text not null,
  bank       text,
  currency   char(3) not null default 'SGD',
  created_at timestamptz not null default now()
);

create index accounts_user_id_idx on public.accounts(user_id);


-- 2. transactions
--    Parsed from uploaded statements; moves through state machine

create table public.transactions (
  id          uuid primary key default uuid_generate_v4(),
  account_id  uuid not null references public.accounts(id) on delete cascade,
  user_id     uuid not null references auth.users(id) on delete cascade,
  date        date not null,
  description text not null,
  withdrawal  numeric(14, 2),
  credit      numeric(14, 2),
  balance     numeric(14, 2),
  category    expense_category not null default 'Other',
  state       transaction_state not null default 'PENDING',
  raw_text    text,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  constraint chk_one_direction check (
    (withdrawal is null) != (credit is null)
  ),
  constraint chk_positive_amounts check (
    (withdrawal is null or withdrawal > 0) and
    (credit     is null or credit     > 0)
  )
);

create index transactions_user_id_idx    on public.transactions(user_id);
create index transactions_account_id_idx on public.transactions(account_id);
create index transactions_date_idx       on public.transactions(date desc);
create index transactions_state_idx      on public.transactions(state);
create index transactions_category_idx   on public.transactions(category);

create trigger transactions_updated_at
  before update on public.transactions
  for each row execute procedure public.set_updated_at();

-- 3. ledger_entries
--    Double-entry bookkeeping — every transaction produces DR + CR
create table public.ledger_entries (
  id             uuid primary key default uuid_generate_v4(),
  transaction_id uuid not null references public.transactions(id) on delete cascade,
  user_id        uuid not null references auth.users(id) on delete cascade,
  account        text not null,
  entry_type     entry_type not null,
  amount         numeric(14, 2) not null check (amount > 0),
  created_at     timestamptz not null default now()
);

create index ledger_entries_transaction_id_idx on public.ledger_entries(transaction_id);
create index ledger_entries_user_id_idx        on public.ledger_entries(user_id);


-- 4. planned_expenses
--    User-added upcoming costs fed into the daily budget calculator

create table public.planned_expenses (
  id              uuid primary key default uuid_generate_v4(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  name            text not null,
  amount          numeric(14, 2) not null check (amount > 0),
  due_date        date not null,
  category        expense_category not null default 'Other',
  is_recurring    boolean not null default false,
  recurrence_days int,
  gcal_event_id   text,
  created_at      timestamptz not null default now()
);

create index planned_expenses_user_id_idx  on public.planned_expenses(user_id);
create index planned_expenses_due_date_idx on public.planned_expenses(due_date);


-- 5. savings_goals

create table public.savings_goals (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  name       text not null,
  target     numeric(14, 2) not null check (target > 0),
  saved      numeric(14, 2) not null default 0 check (saved >= 0),
  deadline   date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index savings_goals_user_id_idx on public.savings_goals(user_id);

create trigger savings_goals_updated_at
  before update on public.savings_goals
  for each row execute procedure public.set_updated_at();

-- 6. health_scores
--    Monthly composite score (0–100) with dimension breakdown

create table public.health_scores (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  month      date not null,
  score      smallint not null check (score between 0 and 100),
  dimensions jsonb not null default '{}',
  ai_tips    text,
  created_at timestamptz not null default now(),
  constraint health_scores_user_month_unique unique (user_id, month)
);

create index health_scores_user_id_idx on public.health_scores(user_id);
create index health_scores_month_idx   on public.health_scores(month desc);


-- 7. reconciliation_log
--    Nightly 2AM cron audit trail (service role only)

create table public.reconciliation_log (
  id              uuid primary key default uuid_generate_v4(),
  run_date        timestamptz not null default now(),
  total_processed int not null default 0,
  total_cleared   int not null default 0,
  discrepancies   int not null default 0,
  notes           text,
  created_at      timestamptz not null default now()
);


-- Grants (lock #1: may this role touch the table at all?)
-- RLS policies below (lock #2) then filter WHICH rows.
-- service_role (FastAPI) gets full access and bypasses RLS.

grant usage on schema public to anon, authenticated, service_role;
grant all    on all tables in schema public to service_role;
grant select on all tables in schema public to authenticated;
grant insert, update, delete
  on public.planned_expenses, public.savings_goals to authenticated;

-- Row Level Security

alter table public.accounts           enable row level security;
alter table public.transactions       enable row level security;
alter table public.ledger_entries     enable row level security;
alter table public.planned_expenses   enable row level security;
alter table public.savings_goals      enable row level security;
alter table public.health_scores      enable row level security;
alter table public.reconciliation_log enable row level security;

-- Financial tables: browser may READ own rows only.
-- Writes go through FastAPI (service role key, bypasses RLS) so the server
-- enforces the double-entry ledger and state machine — a DevTools user
-- cannot insert unbalanced or pre-CLEARED rows.

create policy "accounts: owner read"
  on public.accounts for select
  using (auth.uid() = user_id);

create policy "transactions: owner read"
  on public.transactions for select
  using (auth.uid() = user_id);

create policy "ledger_entries: owner read"
  on public.ledger_entries for select
  using (auth.uid() = user_id);

create policy "health_scores: owner read"
  on public.health_scores for select
  using (auth.uid() = user_id);

-- User-preference tables: no ledger invariants, browser may read and write own rows.

create policy "planned_expenses: owner access"
  on public.planned_expenses for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "savings_goals: owner access"
  on public.savings_goals for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "reconciliation_log: no user access"
  on public.reconciliation_log for all
  using (false);

-- Dashboard view: monthly spending by category

create view public.monthly_spending as
select
  t.user_id,
  date_trunc('month', t.date)::date as month,
  t.category,
  sum(t.withdrawal)                 as total_spent,
  count(*)                          as tx_count
from public.transactions t
where t.withdrawal is not null
  and t.state = 'CLEARED'
group by t.user_id, date_trunc('month', t.date), t.category;

-- View is created after the bulk grants above, so grant it separately
grant select on public.monthly_spending to authenticated, service_role;