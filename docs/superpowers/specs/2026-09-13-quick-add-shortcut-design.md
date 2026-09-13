# Quick-Add Expense Shortcut — Design

## Problem

The user wants near-zero-friction expense logging at the moment of purchase — the stated trigger is "double-tap my phone to record it" — because manual entry via statement upload or the Transactions page happens too far after the spend to actually curb mindless spending.

## Non-goals

- No automatic/passive expense detection (reading bank SMS or push notifications). Not feasible on iOS; heavily restricted on Android. Out of scope.
- No PWA, no new frontend page, no service worker/manifest. Considered and dropped — see "Rejected approach" below.
- No offline queue/retry if the phone has no signal when the Shortcut runs. The HTTP request simply fails; the user re-triggers later. Real complexity for a personal tool with little payoff.
- No support for logging `credit` (income) transactions via this path — the Shortcut only creates `withdrawal` transactions, matching its purpose (catching spending, not income).

## Rejected approach: PWA + "Open URL" Shortcut

Originally scoped as a PWA (installable Vue page) opened via an iOS Back Tap Shortcut's "Open URL" action. Rejected because:
1. iOS Shortcuts' "Open URL" action opens Safari, not the standalone installed PWA window, even when the PWA is added to the home screen — undermining the "instant, app-like popup" goal.
2. It requires an entire new frontend surface (manifest, service worker, a `/quick-add` route) for something a native iOS mechanism already does better.

## Chosen approach: native Shortcuts UI + existing backend endpoint

iOS Shortcuts has its own native input UI (`Choose from Menu`, `Ask for Input`) that appears as a small system popup — no browser, no app switch. Back Tap triggers the Shortcut directly.

### Flow

1. Back Tap (configured in iOS Settings → Accessibility → Touch → Back Tap → Double Tap → this Shortcut) runs the Shortcut.
2. Shortcut action **"Choose from Menu"** — lists the same categories as `VALID_CATEGORIES` in `backend/app/api/dependencies.py:9-13` (Food & Dining, Transport, Shopping, Bills & Utilities, Healthcare, Entertainment, Travel, Education, Other — excluding Income/Transfer, which don't apply to a spend logger).
3. Shortcut action **"Ask for Input"** (Number) — amount.
4. Shortcut action **"Get Contents of URL"** — `POST` to `https://<backend-domain>/transactions` with:
   - Header `X-API-Token: <the user's quick-add token>`
   - JSON body: `{"date": "<today, ISO>", "description": "Quick add", "amount": <input>, "type": "withdrawal", "category": "<chosen>"}`
5. Backend's existing `create_transaction` handler (`backend/app/api/transactions.py:30-`) runs completely unchanged: validates `amount > 0`, validates/normalizes category, creates the account if needed, inserts the transaction, and writes the double-entry ledger pair via `_insert_ledger_entries` — identical to a manual add through the Transactions page. The new expense appears in the dashboard, transaction list, budget calculations, and health score immediately, since it's the same table.

No new business logic. The only new code is *how the request proves who's asking*.

## Auth: per-user quick-add token

### Why not the existing JWT auth
Supabase JWTs are short-lived (~1hr) and refreshed automatically by the browser's Supabase client during normal use. A Shortcut can't perform that refresh dance — it needs a credential that stays valid until the user explicitly revokes it.

### Design

**New table `api_tokens`** (same shape as the existing `telegram_links` pattern):
```sql
create table public.api_tokens (
  id          uuid primary key default uuid_generate_v4(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  token_hash  text not null,
  created_at  timestamptz not null default now(),
  last_used_at timestamptz
);

create unique index api_tokens_user_id_idx on public.api_tokens(user_id);
```
One active token per user (unique index on `user_id`) — generating a new token overwrites/deletes the old row, so old leaked tokens stop working the moment a new one is issued.

**Token generation:**
- Random token via `secrets.token_urlsafe(32)`, same technique already used for Telegram link tokens (`telegram_bot.py:22`).
- Hashed with SHA-256 before storage (`hashlib.sha256(token.encode()).hexdigest()`) — SHA-256 rather than a slow password hash (bcrypt/scrypt) because the token is already high-entropy random data, not a human-guessable password; slow hashing would add latency for no security benefit here.
- Shown to the user **exactly once** in the API response — never retrievable again, matching how GitHub/Stripe API keys work.

**New backend endpoints** (`backend/app/api/api_tokens.py`, mirroring `telegram.py`'s shape):
- `POST /api-tokens` (authed via existing JWT, rate-limited) — deletes any existing token row for the user, creates a new one, returns the raw token once.
- `DELETE /api-tokens` (authed via existing JWT, rate-limited) — deletes the user's token row. This is the revoke path — critical if the phone is lost or the token is suspected leaked.
- `GET /api-tokens/status` (authed via existing JWT) — returns whether a token currently exists (not the token itself), so Settings can show "Active" / "Not set up" without ever re-displaying the secret.

**Scoping the token narrowly (important):** the token is checked by a small new dependency, `get_current_user_via_api_token`, used **only** as an *additional* allowed auth method on `POST /transactions` — not as a global replacement for `get_current_user`. Every other endpoint (`GET /transactions`, `DELETE`, budget, savings, analytics, etc.) continues to accept only the normal Supabase JWT. This matters because the token is meant to authorize one narrow action (log a spend); if it worked everywhere, a leaked token would expose the user's entire financial history and allow deleting data, far beyond its intended purpose.

Concretely, `POST /transactions`'s dependency becomes:
```python
async def get_current_user_or_api_token(
    request: Request,
    x_api_token: str = Header(default=""),
) -> dict:
    if x_api_token:
        return await get_current_user_via_api_token(x_api_token)
    return await get_current_user(request)  # existing JWT path, untouched
```
(Exact signature to be finalized during implementation — the point is JWT-based auth on every other route is not touched.)

### Settings UI addition
New section in `SettingsView.vue`, alongside the existing Telegram connect/disconnect block:
- "Not set up" state → **Generate Quick-Add Token** button → shows the raw token once in a copyable box with a "you won't see this again" warning.
- "Active" state → shows generation date + **Revoke** button.

## Security notes (accepted, not fixed)

- **iCloud sync**: iOS Shortcuts sync via iCloud, so this token is effectively stored in Apple's cloud too — outside FinFlow's control. Same trust category as storing a password in Notes; the user should know this going in.
- **Physical device access**: anyone with the user's unlocked phone could trigger the Shortcut and log fake expenses. Same risk class as someone using the unlocked phone in the app directly — not a new hole this feature opens, and bounded in impact since it can only create `withdrawal` transactions, not read or delete anything.
- No token expiry (e.g. auto-expire after N days) in v1 — revocation is manual via the Settings button. Acceptable for a single-user personal tool; would need revisiting if this ever supported multiple household members.

## Testing

- `backend/tests/test_api_tokens.py`: token generation returns a token once and stores only its hash; regenerating invalidates the previous token; a valid token resolves to the correct `user_id`; an invalid/revoked token is rejected (401); the JWT auth path on every other endpoint remains completely unaffected.
- `backend/tests/test_transactions.py` (extend existing): `POST /transactions` accepts a valid `X-API-Token` in place of a JWT and creates the transaction + ledger entries identically to the JWT path.
- Manual: generate a token in Settings, build the Shortcut per the flow above, configure Back Tap, trigger it, and confirm the transaction appears in the dashboard within seconds. Revoke the token and confirm the Shortcut's next request gets rejected.
- Log scan: confirm the raw token value never appears in backend logs (request logging must not dump the `X-API-Token` header), consistent with the project's existing "no financial data or secrets in logs" rule.

## Files touched

- New: `backend/app/api/api_tokens.py` (endpoints), addition to `backend/app/api/dependencies.py` (token-lookup dependency), `supabase/migrations/schema.sql` (new `api_tokens` table — remember to also run this by hand against the live Supabase project, and grant `select/insert/update/delete` to `authenticated`/`service_role` same as `telegram_links` needed).
- Modified: `backend/app/api/transactions.py` (swap `Depends(get_current_user)` for the dual-auth dependency on `POST /transactions` only).
- Modified: `frontend/src/views/SettingsView.vue`, `frontend/src/services/api.js` (new `apiTokensApi` calls).
- User-side, no code: the iOS Shortcut itself, built manually in the Shortcuts app.
