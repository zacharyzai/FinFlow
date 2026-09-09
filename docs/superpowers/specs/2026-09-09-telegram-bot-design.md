# Telegram Bot Integration — Design

Status: approved (pending spec review) · Date: 2026-09-09

## Goal

Let a FinFlow user link their Telegram account once, then query their
finances on demand via chat commands:

- `/goal` — list savings goals and progress
- `/dbudget` — today's remaining daily budget
- `/mbudget` — remaining budget for the rest of the month
- `/recommendation` — an AI-generated suggestion of what to cut back on

A proactive daily push reminder (CLAUDE.md Phase 2 item) is explicitly
out of scope for this pass — commands only. Fast follow-up once this works.

## Architecture

```
Telegram user → t.me/YourBot?start=<token>  (tap "Connect Telegram" in FinFlow Settings)
        ↓
Telegram → POST /telegram/webhook (FastAPI, no JWT — see Security)
        ↓
telegram_links: look up token → row exists? → save chat_id↔user_id, delete token
        ↓
User sends /goal, /dbudget, /mbudget, /recommendation
        ↓
Telegram → POST /telegram/webhook → look up user_id by chat_id
        ↓ (unknown chat_id → reply "not linked", stop)
Call existing service logic (budget / savings / analytics) → format reply
        ↓
Telegram sendMessage API → chat
```

New pieces:
- `telegram_links` table (Supabase)
- `backend/app/api/telegram.py` — router: `POST /telegram/link-token` (authed),
  `POST /telegram/webhook` (Telegram → us, no auth header)
- `backend/app/services/telegram_bot.py` — command router + Telegram
  `sendMessage` calls
- `frontend/src/views/SettingsView.vue` — new page, "Connect Telegram" button
  (no Settings page exists today, so this is new but intentionally minimal:
  one button, one connected/disconnected status, one disconnect button)

No changes to existing budget/savings/analytics logic — the bot calls the
same functions those routers already use.

## Linking flow

1. User clicks "Connect Telegram" in FinFlow Settings.
2. Frontend calls `POST /telegram/link-token` (authed via existing JWT dep).
   Backend generates a random 32-byte token, inserts a row into
   `telegram_links` with `user_id`, `link_token`, `token_expires_at = now() + 10min`,
   `chat_id = null`. Returns `https://t.me/<BOT_USERNAME>?start=<token>`.
3. Frontend opens that URL (new tab / redirect to Telegram app).
4. User taps "Start" in Telegram → Telegram sends `/start <token>` to the
   webhook.
5. Webhook looks up the row by `link_token`. If found and not expired: set
   `chat_id`, clear `link_token`/`token_expires_at`, reply "✅ Connected to
   FinFlow." If not found or expired: reply "This link has expired — generate
   a new one from FinFlow Settings," no row is written.
6. Settings page polls or refetches on focus to show "Connected" state once
   linking completes. A "Disconnect" button deletes the row.

One user ↔ one chat_id: linking again with a fresh token overwrites the
existing row's `chat_id` for that `user_id` (re-linking, not a second row).

## Commands

Webhook receives every Telegram update, extracts `message.chat.id` and
`message.text`. If `text` starts with `/start `, that's the linking flow above.
Otherwise, look up `user_id` from `telegram_links` by `chat_id`:

- Not found → reply "Not linked yet — connect your account from FinFlow
  Settings." Stop.
- Found → dispatch on the command text:
  - `/goal` → call the same query `savings.list_goals` uses, format each
    goal as one line: `<name>: $<saved>/$<target> (<pct>%)`.
  - `/dbudget` → call the same calc `budget.daily_budget` uses for "today",
    reply `Daily budget remaining: $<amount>`.
  - `/mbudget` → same budget calc summed across the rest of the current
    month, reply `Budget remaining this month: $<amount>`.
  - `/recommendation` → pull current-month category breakdown from the same
    query `analytics.spending_by_category` uses, build a short prompt with
    that breakdown + budget status, call
    `ai_generate(prompt, max_tokens=200, claude_model="claude-sonnet-4-6",
    gemini_model="gemini-3.6-flash")` (the existing shared helper in
    `app/core/ai_client.py` — Claude if `ANTHROPIC_API_KEY` is set, Gemini
    otherwise), reply with the model's text.
  - Anything else → "Unknown command. Try /goal, /dbudget, /mbudget,
    /recommendation."

To avoid duplicating query logic, the underlying data-fetch functions in
`budget.py`/`savings.py`/`analytics.py` get extracted into small plain
functions callable from both the HTTP route and the bot service (they
already mostly are — `_effective_expenses` etc. — this just does the same
for the couple of spots that currently inline logic straight in the route).

## Error handling

- Webhook always returns `200 OK` to Telegram immediately, even on internal
  errors — a non-200 makes Telegram retry the same update repeatedly.
  Failures are logged, not surfaced as HTTP errors.
- `/recommendation` is rate-limited (reuse `slowapi` `limiter`, same pattern
  as upload endpoints) since it's a paid AI call — e.g. 5/hour per chat_id.
- If `ai_generate` raises (both providers down/misconfigured), catch and
  reply "Couldn't generate a recommendation right now — try again shortly."
- No financial amounts or merchant names in logs, per existing project rule
  — log event types (`"telegram command: /dbudget"`) and user_id only.

## Security

- Webhook has no JWT (Telegram can't send one). Instead, when registering
  the webhook with Telegram, set a secret token; Telegram echoes it back on
  every request as the `X-Telegram-Bot-Api-Secret-Token` header. The
  endpoint rejects any request where this doesn't match
  `TELEGRAM_WEBHOOK_SECRET` (new env var) — stops randoms from POSTing fake
  updates.
- `telegram_links` gets RLS like every other table: policy restricts
  `select`/`update`/`delete` to `auth.uid() = user_id`. The webhook itself
  reads/writes via the service-role key (server-side only, same pattern as
  `statements.py`), same as every other backend-authored write in this repo.
- Link tokens: single-use (deleted on success), 10-minute expiry, generated
  with `secrets.token_urlsafe`.
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_WEBHOOK_SECRET` are server-side env
  vars only, never sent to the frontend (bot token is already stubbed in
  `.env.example`; webhook secret is new).

## Data model

```sql
create table public.telegram_links (
  id                uuid primary key default uuid_generate_v4(),
  user_id           uuid not null references auth.users(id) on delete cascade,
  chat_id           bigint,
  link_token        text,
  token_expires_at  timestamptz,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

create unique index telegram_links_user_id_idx on public.telegram_links(user_id);
create unique index telegram_links_chat_id_idx on public.telegram_links(chat_id) where chat_id is not null;

alter table public.telegram_links enable row level security;

create policy "telegram_links: owner access"
  on public.telegram_links for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
```

(Follows the same shape/trigger/grant conventions as the other tables in
`supabase/migrations/schema.sql` — updated_at trigger and GRANT block to be
added alongside the existing ones, not duplicated here.)

## Testing

- Unit: link-token generation/expiry, webhook signature validation, command
  parsing/dispatch (mock Telegram payloads), `/recommendation` prompt
  building.
- Manual: end-to-end via Telegram's test bot — connect, run all 4 commands,
  disconnect, confirm unlinked chat gets the "not linked" reply, confirm
  expired/reused token is rejected.

## Explicitly out of scope

- Proactive daily push reminders (separate future cron job, mirroring
  `reconciliation.py`'s APScheduler pattern).
- Group chats / multiple linked chats per user.
- Rich formatting (buttons, inline keyboards) — plain text replies only.
