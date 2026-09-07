-- Run once in the Supabase SQL editor. Non-destructive — does not touch existing rows.
-- Prevents re-uploading the same statement from double-inserting transactions.
create unique index if not exists transactions_dedup_idx on public.transactions (
  account_id, date, description, coalesce(withdrawal, 0), coalesce(credit, 0)
);
