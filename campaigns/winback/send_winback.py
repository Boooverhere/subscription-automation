"""
Win-Back Campaign Sender — Smart Batch Mode
---------------------------------------------
Sends a hard-push win-back email to:
  1. All subscribers with status='churned' in the Subscription Tracker sheet
  2. Anyone listed in extra_subscribers.csv

Batching strategy (protects deliverability):
  - Sends 30–50 emails per batch (randomised)
  - Waits 1–2 hours between batches (randomised)
  - Tracks every sent address in winback_sent.log
  - Safe to stop and re-run — resumes exactly where it left off

Usage:
    python3 campaigns/winback/send_winback.py            # live — batched sending
    python3 campaigns/winback/send_winback.py --dry-run  # test — no emails sent
"""

import sys
import csv
import time
import random
import math
from pathlib import Path

# ── resolve project root so imports work when called from any directory ──────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger import get_logger
from services.sheets_service import get_sheet, get_all_subscribers
from services.email_service import send_email
from config import COL_NAME, COL_EMAIL, COL_PLAN, COL_STATUS
from campaigns.winback.winback_email import get_winback_email

logger = get_logger(__name__)

# ── batch settings ─────────────────────────────────────────────────────────
BATCH_MIN       = 30          # min emails per batch
BATCH_MAX       = 50          # max emails per batch
WAIT_MIN_HOURS  = 1.0         # min wait between batches
WAIT_MAX_HOURS  = 2.0         # max wait between batches

# ── paths ───────────────────────────────────────────────────────────────────
CAMPAIGN_DIR = Path(__file__).resolve().parent
EXTRA_CSV    = CAMPAIGN_DIR / "extra_subscribers.csv"
SENT_LOG     = CAMPAIGN_DIR / "winback_sent.log"


# ── helpers ─────────────────────────────────────────────────────────────────

def load_sent_log() -> set:
    if not SENT_LOG.exists():
        return set()
    with open(SENT_LOG, "r") as f:
        return {line.strip().lower() for line in f if line.strip()}


def mark_sent(email: str):
    with open(SENT_LOG, "a") as f:
        f.write(email.lower() + "\n")


def load_sheet_targets() -> tuple[list[dict], set]:
    worksheet   = get_sheet()
    subscribers = get_all_subscribers(worksheet)

    churned       = []
    active_emails = set()

    for s in subscribers:
        status = s.get(COL_STATUS, "").strip().lower()
        email  = s.get(COL_EMAIL, "").strip().lower()
        if status == "active" and email:
            active_emails.add(email)
        elif status == "churned":
            churned.append(s)

    logger.info(f"Sheet: {len(churned)} churned | {len(active_emails)} active (will be excluded)")
    return churned, active_emails


def load_csv_targets() -> list[dict]:
    if not EXTRA_CSV.exists():
        logger.info(f"No extra list found at {EXTRA_CSV} — skipping CSV source")
        return []

    targets = []
    with open(EXTRA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get("email", "").strip()
            if not email:
                continue
            first = row.get("name", "").strip()
            last  = row.get("last name", row.get("last_name", "")).strip()
            full_name = f"{first} {last}".strip() if last else first
            targets.append({
                "email": email,
                "name":  full_name,
                "plan":  row.get("plan", "").strip(),
            })

    logger.info(f"CSV: {len(targets)} subscriber(s) loaded from {EXTRA_CSV.name}")
    return targets


def merge_targets(sheet_rows: list[dict], csv_rows: list[dict]) -> list[dict]:
    seen   = set()
    merged = []

    for row in sheet_rows:
        email = row.get(COL_EMAIL, "").strip().lower()
        if not email or email in seen:
            continue
        seen.add(email)
        merged.append({
            "email": row.get(COL_EMAIL, "").strip(),
            "name":  row.get(COL_NAME, "").strip(),
            "plan":  row.get(COL_PLAN, "").strip(),
        })

    for row in csv_rows:
        email = row.get("email", "").strip().lower()
        if not email or email in seen:
            continue
        seen.add(email)
        merged.append(row)

    logger.info(f"Total unique targets after merge: {len(merged)}")
    return merged


def send_batch(batch: list[dict], batch_num: int, total_batches: int, dry_run: bool) -> tuple[int, int]:
    """Sends one batch. Returns (sent, errors)."""
    sent   = 0
    errors = 0

    logger.info(f"--- Batch {batch_num}/{total_batches} | {len(batch)} emails ---")

    for subscriber in batch:
        email = subscriber["email"].strip()
        name  = subscriber["name"].strip()
        plan  = subscriber["plan"].strip()

        content = get_winback_email(customer_name=name, plan=plan)

        if dry_run:
            logger.info(f"[DRY RUN] Would send → {email}")
            sent += 1
            continue

        success = send_email(
            to_email=email,
            subject=content["subject"],
            body_html=content["body"],
        )

        if success:
            mark_sent(email)
            sent += 1
            time.sleep(1)  # 1s between individual emails within a batch
        else:
            errors += 1

    return sent, errors


# ── main ────────────────────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        logger.info("=== DRY RUN MODE — no emails will be sent ===")

    logger.info("=== Win-Back Campaign Started (Batch Mode) ===")

    already_sent = load_sent_log()
    logger.info(f"Already sent to {len(already_sent)} address(es) — will skip those")

    sheet_targets, active_emails = load_sheet_targets()
    csv_targets = load_csv_targets()
    all_targets = merge_targets(sheet_targets, csv_targets)

    # Filter down to only those who still need the email
    pending = []
    for s in all_targets:
        email = s["email"].strip()
        if not email:
            continue
        if email.lower() in active_emails:
            continue
        if email.lower() in already_sent:
            continue
        pending.append(s)

    if not pending:
        logger.info("No pending targets — everyone has already been sent to. Done.")
        return

    # Split into batches of random size
    batches      = []
    i            = 0
    while i < len(pending):
        size = random.randint(BATCH_MIN, BATCH_MAX)
        batches.append(pending[i:i + size])
        i += size

    total_batches  = len(batches)
    total_pending  = len(pending)
    total_sent     = 0
    total_errors   = 0

    logger.info(
        f"{total_pending} emails to send across {total_batches} batch(es) "
        f"({BATCH_MIN}–{BATCH_MAX} per batch, {WAIT_MIN_HOURS}–{WAIT_MAX_HOURS}h wait between batches)"
    )

    for batch_num, batch in enumerate(batches, start=1):
        sent, errors = send_batch(batch, batch_num, total_batches, dry_run)
        total_sent   += sent
        total_errors += errors

        if batch_num < total_batches:
            wait_seconds = random.uniform(WAIT_MIN_HOURS * 3600, WAIT_MAX_HOURS * 3600)
            wait_minutes = round(wait_seconds / 60)
            logger.info(
                f"Batch {batch_num} done ({sent} sent). "
                f"Waiting {wait_minutes} minutes before next batch..."
            )
            if not dry_run:
                time.sleep(wait_seconds)

    logger.info(
        f"=== Campaign Finished | "
        f"Total sent: {total_sent} | Errors: {total_errors} | Batches: {total_batches} ==="
    )


if __name__ == "__main__":
    main()
