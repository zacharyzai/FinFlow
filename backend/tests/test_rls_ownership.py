"""
Regression guard for the RLS-bypass risk: the backend talks to Supabase with
the SERVICE ROLE key everywhere (app/core/database.py), which skips Postgres
Row Level Security entirely. That means every UPDATE/DELETE against a
per-user table has no database-level backstop — user_id filtering in Python
IS the security boundary. If a future change adds a mutation that forgets
the filter, this test should be the thing that catches it, not a security
review after the fact.

Scope: app/api/*.py only (user-request handlers). Two directories are
intentionally excluded, not just unscanned:

- app/jobs/* — the reconciliation job intentionally updates transactions
  across ALL users, since it's a trusted system process, not a per-request
  handler acting on behalf of one user.
- app/services/telegram_bot.py — handle_start's `.update()` on
  telegram_links has no `.eq("user_id", ...)` by design. The webhook caller
  has no authenticated FinFlow session at that point (Telegram, not our
  frontend, is calling), so there is no `current_user["id"]` to filter on.
  Ownership there comes from the single-use link_token looked up earlier in
  the same function, not from a user_id filter on the mutation itself. Do
  not "fix" this by adding a fake `.eq("user_id", ...)` — it would be wrong.

This is a static source scan, not a live-DB test — there's no pytest/DB
fixture setup in this project yet, so a lightweight AST check is the
pragmatic first guard rather than blocking on building out that
infrastructure. See Group 4 item 23 for real test coverage of the pure
functions.
"""
import ast
from pathlib import Path

import pytest

API_DIR = Path(__file__).resolve().parent.parent / "app" / "api"
MUTATION_METHODS = ("update", "delete")


def _find_unsafe_mutations(path: Path) -> list[str]:
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))
    unsafe = []

    for stmt in ast.walk(tree):
        if not isinstance(stmt, ast.stmt):
            continue
        segment = ast.get_source_segment(source, stmt)
        if not segment or "supabase.table(" not in segment:
            continue
        if not any(f".{m}(" in segment for m in MUTATION_METHODS):
            continue
        if '.eq("user_id"' not in segment and ".eq('user_id'" not in segment:
            unsafe.append(segment.strip().splitlines()[0])

    return unsafe


@pytest.mark.parametrize("path", sorted(API_DIR.glob("*.py")), ids=lambda p: p.name)
def test_every_update_delete_filters_user_id(path):
    unsafe = _find_unsafe_mutations(path)
    assert not unsafe, (
        f"{path.name}: found supabase .update()/.delete() call(s) without a "
        f'.eq("user_id", ...) filter chained on directly. RLS is bypassed via the '
        f"service role key, so this filter is the only thing preventing one user's "
        f"request from mutating another user's row: {unsafe}"
    )
