"""
One-Time 40% Discount Campaign
--------------------------------
Sends a 40% off reactivation offer to all subscribers with status 'Expired'.

Usage:
    python3 campaigns/winback/send_discount40.py            # live — sends real emails
    python3 campaigns/winback/send_discount40.py --dry-run  # test — no emails sent
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger import get_logger
from services.sheets_service import get_sheet, get_all_subscribers
from services.email_service import send_email
from config import COL_NAME, COL_EMAIL, COL_STATUS
from campaigns.winback.discount40_email import get_discount40_email

logger = get_logger(__name__)

SENT_LOG = Path(__file__).resolve().parent / "discount40_sent.log"

# Emails to always skip (bad/offensive addresses)
SKIP_EMAILS = {
    "retardjews@gmail.com",
}


def load_sent_log() -> set:
    if not SENT_LOG.exists():
        return set()
    with open(SENT_LOG, "r") as f:
        return {line.strip().lower() for line in f if line.strip()}


def mark_sent(email: str):
    with open(SENT_LOG, "a") as f:
        f.write(email.lower() + "\n")


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        logger.info("=== DRY RUN MODE — no emails will be sent ===")

    logger.info("=== 40% Discount Campaign Started ===")

    already_sent = load_sent_log()
    if already_sent:
        logger.info(f"Already sent to {len(already_sent)} address(es) — will skip those")

    worksheet   = get_sheet()
    subscribers = get_all_subscribers(worksheet)

    targets = []
    for s in subscribers:
        status = s.get(COL_STATUS, "").strip().lower()
        email  = s.get(COL_EMAIL, "").strip()

        if status != "expired":
            continue
        if not email:
            continue
        if email.lower() in SKIP_EMAILS:
            logger.info(f"Skipping blocked address: {email}")
            continue
        if email.lower() in already_sent:
            logger.info(f"Already sent — skipping: {email}")
            continue

        targets.append({
            "name":  s.get(COL_NAME, "").strip(),
            "email": email,
        })

    logger.info(f"Found {len(targets)} expired subscriber(s) to contact")

    sent   = 0
    errors = 0

    for subscriber in targets:
        email = subscriber["email"]
        name  = subscriber["name"]

        content = get_discount40_email(customer_name=name)

        logger.info(f"Sending → {email} ({name or 'no name'})")

        if dry_run:
            logger.info(f"[DRY RUN] Would send to {email}")
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
            time.sleep(2)
        else:
            logger.error(f"Failed to send to {email}")
            errors += 1

    logger.info(
        f"=== Campaign Finished | Sent: {sent} | Errors: {errors} | "
        f"Skipped (already sent or blocked): {len(already_sent) + len(SKIP_EMAILS)} ==="
    )


if __name__ == "__main__":
    main()
