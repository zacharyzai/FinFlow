"""
Nightly reconciliation job — runs at 2AM Singapore time via APScheduler.

For every PENDING transaction, it checks whether the double-entry ledger balances:
  sum(DR entries) == sum(CR entries)

If balanced  → state moves to CLEARED (money confirmed)
If unbalanced → state moves to FAILED  (data integrity problem, needs investigation)

This is the same pattern used by Stripe and PayPal internally.
The result is written to reconciliation_log so you can audit every run.
"""

import logging
from datetime import datetime, timezone

from app.core.database import supabase

logger = logging.getLogger(__name__)


def run_reconciliation():
    logger.info("Reconciliation job started")

    pending = (
        supabase.table("transactions")
        .select("id")
        .eq("state", "PENDING")
        .execute()
    )

    if not pending.data:
        logger.info("No PENDING transactions — nothing to reconcile")
        _write_log(0, 0)
        return

    tx_ids = [r["id"] for r in pending.data]
    cleared = 0
    discrepancies = 0

    for tx_id in tx_ids:
        entries = (
            supabase.table("ledger_entries")
            .select("entry_type, amount")
            .eq("transaction_id", tx_id)
            .execute()
        )

        dr_total = sum(float(e["amount"]) for e in entries.data if e["entry_type"] == "DR")
        cr_total = sum(float(e["amount"]) for e in entries.data if e["entry_type"] == "CR")

        # Float tolerance: $0.01 covers rounding in multi-currency conversions
        balanced = abs(dr_total - cr_total) < 0.01

        new_state = "CLEARED" if balanced else "FAILED"
        supabase.table("transactions").update({"state": new_state}).eq("id", tx_id).execute()

        if balanced:
            cleared += 1
        else:
            discrepancies += 1
            logger.warning(
                f"Reconciliation FAILED for tx {tx_id}: DR={dr_total:.2f} CR={cr_total:.2f}"
            )

    _write_log(len(tx_ids), discrepancies)
    logger.info(f"Reconciliation done — {cleared} cleared, {discrepancies} discrepancies")


def _write_log(total_processed: int, discrepancies: int):
    try:
        supabase.table("reconciliation_log").insert({
            "run_date": datetime.now(timezone.utc).isoformat(),
            "total_processed": total_processed,
            "discrepancies": discrepancies,
        }).execute()
    except Exception as e:
        logger.error(f"Failed to write reconciliation log: {e}")
