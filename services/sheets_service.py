import gspread
from gspread.utils import rowcol_to_a1
from google.oauth2.service_account import Credentials
from utils.logger import get_logger
from config import GOOGLE_CREDENTIALS_FILE, SPREADSHEET_NAME, COL_LAST_REMINDER, COL_STAGE, COL_STATUS

logger = get_logger(__name__)

# The permissions our script needs to access Sheets and Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_sheet():
    """
    Authenticates with Google and returns the first worksheet
    of the spreadsheet named in config.py (SPREADSHEET_NAME).
    """
    try:
        creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.sheet1  # First sheet/tab
        logger.info(f"Connected to Google Sheet: '{SPREADSHEET_NAME}'")
        return worksheet
    except FileNotFoundError:
        logger.error(f"credentials.json not found. Expected at: {GOOGLE_CREDENTIALS_FILE}")
        raise
    except gspread.SpreadsheetNotFound:
        logger.error(f"Spreadsheet '{SPREADSHEET_NAME}' not found. Make sure it's shared with the service account.")
        raise


def get_all_subscribers(worksheet) -> list[dict]:
    """
    Reads all rows from the worksheet and returns them as a
    list of dictionaries, where each key is a column header.

    Example row:
    {
        "customer_name": "John Smith",
        "email": "john@example.com",
        "plan": "1 month",
        "subscription_end_date": "2026-03-15",
        "status": "active",
        "last_reminder_sent": "",
        "reminder_stage": "",
        "notes": ""
    }
    """
    records = worksheet.get_all_records()
    logger.info(f"Fetched {len(records)} subscriber(s) from sheet")
    return records


def update_reminder_info(worksheet, row_number: int, stage: int, date_sent: str):
    """
    After sending a reminder email, updates two columns in the sheet:
    - last_reminder_sent: today's date (so we know when we last emailed them)
    - reminder_stage: the stage number sent (so we don't send it again)

    row_number: the row in the sheet (2 = first data row, since row 1 is headers)
    stage: 1, 2, 3, or 4
    date_sent: today's date as a string e.g. "2026-03-08"
    """
    headers = worksheet.row_values(1)  # Get header row to find column positions

    # Find the column index for each field (gspread uses 1-based indexing)
    try:
        last_reminder_col = headers.index(COL_LAST_REMINDER) + 1
        stage_col = headers.index(COL_STAGE) + 1
    except ValueError as e:
        logger.error(f"Column not found in sheet headers: {e}")
        raise

    # Use batch_update to write both cells in a single API call
    worksheet.batch_update([
        {"range": rowcol_to_a1(row_number, last_reminder_col), "values": [[date_sent]]},
        {"range": rowcol_to_a1(row_number, stage_col),         "values": [[str(stage)]]},
    ])
    logger.info(f"Updated row {row_number} → stage={stage}, last_reminder_sent={date_sent}")


def update_status(worksheet, row_number: int, new_status: str):
    """
    Updates the status column for a subscriber.
    Used to mark win-back subscribers as 'churned' after sending
    so they are never emailed again.
    """
    headers = worksheet.row_values(1)

    try:
        status_col = headers.index(COL_STATUS) + 1
    except ValueError as e:
        logger.error(f"Status column not found in sheet headers: {e}")
        raise

    worksheet.update_cell(row_number, status_col, new_status)
    logger.info(f"Updated row {row_number} → status={new_status}")
