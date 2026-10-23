"""
WooCommerce → Subscription Tracker sync
----------------------------------------
Runs before the reminder pass. For every completed WooCommerce order:
- new customer  → appends a row (plan, start date, end date, status active)
- known customer → extends their end date by the plan length (a renewal)

Each processed order is tagged in the notes column as "wc#<order id>" so it is
never applied twice. If a row for that customer already starts within a couple
of days of the order (entered by hand), the order is only tagged, not applied.
"""

import base64
import json
import re
import urllib.parse
import urllib.request
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone

from gspread.utils import rowcol_to_a1

from utils.logger import get_logger
from utils.date_helpers import parse_date
from config import (
    WC_STORE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET, SYNC_LOOKBACK_DAYS, SYNC_EXCLUDED_EMAIL_PATTERN,
    COL_NAME, COL_EMAIL, COL_PLAN, COL_START_DATE, COL_END_DATE, COL_STATUS,
    COL_LAST_REMINDER, COL_STAGE, COL_NOTES, COL_PHONE,
)

logger = get_logger(__name__)

SHEET_DATE_FORMAT = "%d/%m/%Y"   # matches the rows entered by hand
MANUAL_ENTRY_TOLERANCE_DAYS = 2


def _add_months(start: date, months: int) -> date:
    year  = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


def _plan_from_item(item_name: str) -> tuple[str, int] | None:
    """'12 Months Premium Television Subscription' → ('12 Months Premium Subscription', 12)."""
    match = re.search(r"(\d+)\s*months?", item_name, re.IGNORECASE)
    if not match:
        return None  # e.g. Free Trial
    months  = int(match.group(1))
    unit    = "Month" if months == 1 else "Months"
    premium = " Premium" if "premium" in item_name.lower() else ""
    return f"{months} {unit}{premium} Subscription", months


def _fetch_completed_orders(since: datetime) -> list[dict]:
    auth = base64.b64encode(f"{WC_CONSUMER_KEY}:{WC_CONSUMER_SECRET}".encode()).decode()
    orders, page = [], 1
    while True:
        query = urllib.parse.urlencode({
            "status":         "completed",
            "modified_after": since.strftime("%Y-%m-%dT%H:%M:%S"),
            "orderby":        "date",
            "order":          "asc",
            "per_page":       100,
            "page":           page,
        })
        request = urllib.request.Request(
            f"{WC_STORE_URL}/wp-json/wc/v3/orders?{query}",
            headers={"Authorization": f"Basic {auth}", "User-Agent": "subscription-automation"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            batch = json.load(response)
        orders.extend(batch)
        if len(batch) < 100:
            return orders
        page += 1


def _order_date(order: dict) -> date:
    raw = order.get("date_paid") or order.get("date_completed") or order.get("date_created")
    return datetime.fromisoformat(raw).date()


def sync_orders(worksheet, dry_run: bool = False, since: datetime | None = None):
    if not (WC_CONSUMER_KEY and WC_CONSUMER_SECRET):
        logger.warning("Order sync | WC_CONSUMER_KEY / WC_CONSUMER_SECRET not set — skipping")
        return

    since = since or datetime.now(timezone.utc) - timedelta(days=SYNC_LOOKBACK_DAYS)
    try:
        orders = _fetch_completed_orders(since)
    except Exception as e:
        logger.error(f"Order sync | Could not fetch WooCommerce orders: {e}")
        return
    logger.info(f"Order sync | {len(orders)} completed order(s) since {since:%Y-%m-%d}")

    headers = worksheet.row_values(1)
    col     = {name: headers.index(name) + 1 for name in headers}
    rows    = worksheet.get_all_records()
    added = renewed = tagged = skipped = 0

    for order in orders:
        order_id = str(order["id"])
        tag      = f"wc#{order_id}"
        email    = (order.get("billing", {}).get("email") or "").strip().lower()

        if any(tag in str(r.get(COL_NOTES, "")) for r in rows):
            continue  # already applied
        plans = [_plan_from_item(i.get("name", "")) for i in order.get("line_items", [])]
        plans = [p for p in plans if p]
        if email and re.search(SYNC_EXCLUDED_EMAIL_PATTERN, email):
            continue  # owner's own test orders
        if not email or not plans:
            logger.info(f"Order sync | Order {order_id} | No email or no subscription plan — skipping")
            skipped += 1
            continue

        plan_name = plans[0][0]
        months    = sum(m for _, m in plans)   # several plans in one order stack up
        start     = _order_date(order)

        matches = [(i, r) for i, r in enumerate(rows) if str(r.get(COL_EMAIL, "")).strip().lower() == email]
        if matches:
            # The customer's current row = the one ending last
            index, row = max(matches, key=lambda m: parse_date(str(m[1].get(COL_END_DATE, ""))) or date.min)
            row_number = index + 2
            row_start  = parse_date(str(row.get(COL_START_DATE, "")))
            notes      = (str(row.get(COL_NOTES, "")) + f" {tag}").strip()

            current_end = parse_date(str(row.get(COL_END_DATE, "")))
            # Already reflected in the row when: the row was (re)started around or
            # after this order, or its end date already covers this purchase.
            already_applied = (
                (row_start and row_start >= start - timedelta(days=MANUAL_ENTRY_TOLERANCE_DAYS))
                or (current_end and current_end >= _add_months(start, months) - timedelta(days=7))
            )
            if already_applied:
                logger.info(f"Order sync | Order {order_id} | Row {row_number} already covers this purchase (ends {current_end}) — tagging only")
                updates = {COL_NOTES: notes}
                tagged += 1
            else:
                base        = max(current_end, start) if current_end else start
                new_end     = _add_months(base, months)
                logger.info(f"Order sync | Order {order_id} | Renewal — row {row_number} end {current_end} → {new_end}")
                updates = {
                    COL_PLAN: plan_name, COL_START_DATE: start.strftime(SHEET_DATE_FORMAT),
                    COL_END_DATE: new_end.strftime(SHEET_DATE_FORMAT), COL_STATUS: "active",
                    COL_LAST_REMINDER: "", COL_STAGE: "", COL_NOTES: notes,
                }
                renewed += 1
            if not dry_run:
                worksheet.batch_update([
                    {"range": rowcol_to_a1(row_number, col[name]), "values": [[value]]}
                    for name, value in updates.items()
                ])
            row.update(updates)
            continue

        billing = order.get("billing", {})
        end     = _add_months(start, months)
        new_row = {
            COL_NAME: f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip(),
            COL_EMAIL: email, COL_PLAN: plan_name,
            COL_START_DATE: start.strftime(SHEET_DATE_FORMAT), COL_END_DATE: end.strftime(SHEET_DATE_FORMAT),
            COL_STATUS: "active", COL_LAST_REMINDER: "", COL_STAGE: "", COL_NOTES: tag,
            COL_PHONE: billing.get("phone", ""),
        }
        logger.info(f"Order sync | Order {order_id} | New subscriber — {plan_name}, ends {end}")
        added += 1
        if not dry_run:
            _append_row(worksheet, headers, new_row, row_number=len(rows) + 2)
        rows.append(new_row)

    logger.info(f"Order sync | Added: {added} | Renewed: {renewed} | Tagged: {tagged} | Skipped: {skipped}")


def _append_row(worksheet, headers: list[str], values: dict, row_number: int):
    """Appends data as plain values, then copies the row-based formulas (WhatsApp columns) from the row above."""
    worksheet.append_row([values.get(h, "") for h in headers], value_input_option="RAW", table_range="A1")
    above = worksheet.row_values(row_number - 1, value_render_option="FORMULA")
    formulas = []
    for index, cell in enumerate(above):
        if isinstance(cell, str) and cell.startswith("="):
            formula = re.sub(r"\b([A-Z]{1,2})" + str(row_number - 1) + r"\b", rf"\g<1>{row_number}", cell)
            formulas.append({"range": rowcol_to_a1(row_number, index + 1), "values": [[formula]]})
    if formulas:
        worksheet.batch_update(formulas, value_input_option="USER_ENTERED")
