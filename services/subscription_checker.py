import time
from datetime import date
from utils.logger import get_logger
from utils.date_helpers import parse_date, days_until_expiry, get_reminder_stage
from services.email_service import send_email
from templates.email_templates import get_email_content
from config import COL_NAME, COL_EMAIL, COL_PLAN, COL_END_DATE, COL_STATUS, COL_LAST_REMINDER, COL_STAGE

logger = get_logger(__name__)


def process_subscribers(worksheet, subscribers: list[dict], dry_run: bool = False):
    """
    Loops through every subscriber and sends reminder emails where needed.

    dry_run=True  → logs what WOULD happen but sends no emails and writes nothing to sheet.
                    Use this to safely test the logic before going live.
    dry_run=False → sends real emails and updates the sheet.
    """

    if dry_run:
        logger.info("=== DRY RUN MODE — no emails will be sent, sheet will not be updated ===")

    total       = len(subscribers)
    sent        = 0
    skipped     = 0
    errors      = 0

    for index, subscriber in enumerate(subscribers):
        # Row number in the sheet: +2 because index is 0-based and row 1 is headers
        row_number = index + 2

        name   = subscriber.get(COL_NAME, "").strip()
        email  = subscriber.get(COL_EMAIL, "").strip()
        plan   = subscriber.get(COL_PLAN, "").strip()
        status = subscriber.get(COL_STATUS, "").strip().lower()
        end_date_str      = subscriber.get(COL_END_DATE, "").strip()
        last_reminder     = str(subscriber.get(COL_LAST_REMINDER, "")).strip()
        reminder_stage_str = str(subscriber.get(COL_STAGE, "")).strip()

        logger.debug(f"Row {row_number} | {name or 'No name'} | {email}")

        # --- Guard: skip if no email ---
        if not email:
            logger.warning(f"Row {row_number} | Skipping — no email address")
            skipped += 1
            continue

        # --- Guard: skip if status is not active ---
        # We still process "expired" status via date logic below,
        # but we skip anything cancelled, paused, etc.
        if status not in ("active", "expired"):
            logger.info(f"Row {row_number} | {email} | Skipping — status is '{status}'")
            skipped += 1
            continue

        # --- Guard: skip if end date is missing ---
        if not end_date_str:
            logger.warning(f"Row {row_number} | {email} | Skipping — no end date")
            skipped += 1
            continue

        # --- Parse the end date ---
        end_date = parse_date(end_date_str)
        if end_date is None:
            logger.warning(f"Row {row_number} | {email} | Skipping — could not parse date: '{end_date_str}'")
            skipped += 1
            continue

        # --- Calculate days left and determine stage ---
        days_left = days_until_expiry(end_date)
        stage     = get_reminder_stage(days_left)

        if stage is None:
            logger.info(f"Row {row_number} | {email} | No reminder needed ({days_left} days left)")
            skipped += 1
            continue

        # Stage 5 = win-back window (31–90 days expired)
        # After sending, mark subscriber as churned so they are never emailed again

        # --- Duplicate protection: skip if this stage was already sent ---
        try:
            already_sent_stage = int(reminder_stage_str) if reminder_stage_str else 0
        except ValueError:
            already_sent_stage = 0

        if already_sent_stage >= stage:
            logger.info(f"Row {row_number} | {email} | Stage {stage} already sent — skipping")
            skipped += 1
            continue

        # --- Get email content ---
        content = get_email_content(stage=stage, customer_name=name, plan=plan)
        if content is None:
            logger.error(f"Row {row_number} | {email} | No template for stage {stage}")
            errors += 1
            continue

        logger.info(f"Row {row_number} | {email} | Sending stage {stage} reminder ({days_left} days left)")

        # --- Send email (or skip if dry run) ---
        if dry_run:
            logger.info(f"[DRY RUN] Would send: '{content['subject']}' → {email}")
            sent += 1
            continue

        success = send_email(
            to_email=email,
            subject=content["subject"],
            body_html=content["body"]
        )

        if success:
            today_str = date.today().strftime("%Y-%m-%d")
            update_reminder_info_safe(worksheet, row_number, stage, today_str)
            # Mark win-back subscribers as churned so they are never emailed again
            if stage in (5, 6):
                update_status_safe(worksheet, row_number, "churned")
            sent += 1
            time.sleep(1)  # Pause 1 second between writes to avoid API rate limit
        else:
            errors += 1

    # --- Summary ---
    logger.info(f"=== Run complete | Total: {total} | Sent: {sent} | Skipped: {skipped} | Errors: {errors} ===")


def update_reminder_info_safe(worksheet, row_number: int, stage: int, date_sent: str):
    """Wraps the sheet update in a try/except so one bad write doesn't crash the run."""
    try:
        from services.sheets_service import update_reminder_info
        update_reminder_info(worksheet, row_number, stage, date_sent)
    except Exception as e:
        logger.error(f"Failed to update sheet for row {row_number}: {e}")


def update_status_safe(worksheet, row_number: int, new_status: str):
    """Wraps the status update in a try/except so one bad write doesn't crash the run."""
    try:
        from services.sheets_service import update_status
        update_status(worksheet, row_number, new_status)
    except Exception as e:
        logger.error(f"Failed to update status for row {row_number}: {e}")
