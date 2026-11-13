from datetime import date, datetime
from config import REMINDER_DAYS


def parse_date(date_string: str) -> date | None:
    """
    Converts a date string from Google Sheets into a Python date object.
    Accepts formats: 'YYYY-MM-DD' or 'MM/DD/YYYY'
    Returns None if the string is empty or unrecognisable.
    """
    if not date_string or not date_string.strip():
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_string.strip(), fmt).date()
        except ValueError:
            continue

    return None  # Couldn't parse — caller should handle this


def days_until_expiry(end_date: date) -> int:
    """
    Returns how many days remain until the subscription end date.
    - Positive number = days remaining
    - 0 = expires today
    - Negative number = already expired
    """
    return (end_date - date.today()).days


def get_reminder_stage(days_left: int) -> int | None:
    """
    Given how many days are left, returns the reminder stage number.

    Stages (defined in config.py REMINDER_DAYS = [7, 3, 1]):
    - 7 days left  → stage 1
    - 3 days left  → stage 2
    - 1 day left   → stage 3
    - 0 or less    → stage 4 (expired)
    - None         → no reminder needed yet

    The stage number is used to:
    1. Pick the right email template
    2. Check if this stage was already sent (duplicate protection)
    """
    if -30 <= days_left <= 0:
        return 4  # Recently expired (0–30 days ago)

    if -90 <= days_left < -30:
        return 5  # Win-back window (31–90 days ago)

    if days_left < -90:
        return 6  # Long-term win-back (90+ days ago)

    # Sort thresholds smallest first [1, 3, 7] so most urgent matches first
    sorted_thresholds = sorted(REMINDER_DAYS)
    total = len(sorted_thresholds)

    for index, threshold in enumerate(sorted_thresholds):
        if days_left <= threshold:
            return total - index  # 1 day→stage 3, 3 days→stage 2, 7 days→stage 1

    return None  # Too early — no reminder needed


def current_cycle_stage(sent_stage: int, last_sent_str: str, end_date: date) -> int:
    """
    Returns the reminder stage that was sent for the CURRENT subscription period.

    The sheet keeps reminder_stage after a customer renews, so an old stage
    (e.g. 4 or 5 from the previous period) would block every new reminder.
    The earliest reminder for the current period is sent max(REMINDER_DAYS)
    days before end_date, so anything sent before that belongs to an older
    period and counts as "nothing sent yet" (0).

    If last_reminder_sent is empty or unreadable we keep the stage as-is.
    """
    if not sent_stage:
        return 0
    last_sent = parse_date(last_sent_str)
    if last_sent is None:
        return sent_stage
    if (end_date - last_sent).days > max(REMINDER_DAYS):
        return 0
    return sent_stage
