import os
from dotenv import load_dotenv

# Load all variables from the .env file into os.environ
load_dotenv()

# --- Google Sheets ---
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Subscription Tracker")

# --- Email SMTP ---
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")       # The From address shown to recipients
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # SMTP password / API key
SMTP_LOGIN = os.getenv("SMTP_LOGIN", GMAIL_ADDRESS)   # SMTP login (may differ from From address)
SENDER_NAME = os.getenv("SENDER_NAME", "IPTV Sup")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# --- WooCommerce (order sync: completed orders → Subscription Tracker) ---
WC_STORE_URL       = os.getenv("WC_STORE_URL", "https://iptvsup.com")
WC_CONSUMER_KEY    = os.getenv("WC_CONSUMER_KEY")
WC_CONSUMER_SECRET = os.getenv("WC_CONSUMER_SECRET")
SYNC_LOOKBACK_DAYS = 7   # daily run re-reads a week of orders; tags in notes prevent repeats
# Owner/test orders are never added to the tracker (matched against the billing email)
SYNC_EXCLUDED_EMAIL_PATTERN = r"elyouss|@iptvsup\.com$"

# --- Reminder thresholds (days before expiry) ---
REMINDER_DAYS = [7, 3, 1]

# --- Sheet column names (must match your Google Sheet headers exactly) ---
COL_NAME = "customer_name"
COL_EMAIL = "email"
COL_PLAN = "plan"
COL_START_DATE = "Start Date"
COL_END_DATE = "subscription_end_date"
COL_STATUS = "status"
COL_LAST_REMINDER = "last_reminder_sent"
COL_STAGE = "reminder_stage"
COL_NOTES = "notes"
COL_PHONE = "phone"
