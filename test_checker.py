from services.sheets_service import get_sheet, get_all_subscribers
from services.subscription_checker import process_subscribers

# Connect to sheet
worksheet   = get_sheet()
subscribers = get_all_subscribers(worksheet)

# Run in dry_run mode — no emails sent, nothing written to sheet
process_subscribers(worksheet, subscribers, dry_run=True)
