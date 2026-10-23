"""
Subscription Reminder Automation
---------------------------------
Entry point. Run this file daily to process all subscribers
and send reminder emails automatically.

Usage:
    python3 app.py            # live run — sends real emails
    python3 app.py --dry-run  # test run — no emails sent, nothing written
"""

import sys
from utils.logger import get_logger
from services.sheets_service import get_sheet, get_all_subscribers
from services.subscription_checker import process_subscribers
from services.order_sync import sync_orders

logger = get_logger(__name__)


def main():
    # Check if --dry-run flag was passed in the terminal
    dry_run = "--dry-run" in sys.argv

    logger.info("=== Subscription Automation Started ===")

    # Step 1: Connect to Google Sheet
    worksheet = get_sheet()

    # Step 2: Add new customers / extend renewals from completed WooCommerce orders
    sync_orders(worksheet, dry_run=dry_run)

    # Step 3: Fetch all subscriber rows
    subscribers = get_all_subscribers(worksheet)

    # Step 4: Process each subscriber and send emails where needed
    process_subscribers(worksheet, subscribers, dry_run=dry_run)

    logger.info("=== Subscription Automation Finished ===")


if __name__ == "__main__":
    main()
