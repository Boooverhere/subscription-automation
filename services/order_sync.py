"""
WooCommerce → Subscription Tracker sync
----------------------------------------
Runs before the reminder pass. For every completed WooCommerce order:
- new customer  → adds a row (name, email, plan, Start Date, phone)
- known customer → a renewal: sets the new plan and Start Date on their row

The sheet computes subscription_end_date and status itself (formulas in E/F:
Start Date + 30/90/180/365 days), so only plan and Start Date are written.
New rows get the formulas and date format of the rows above them.

Each processed order is tagged in the notes column as "wc#<order id>" so it is
never applied twice. Purchases already entered by hand are only tagged.
"""

import base64
import json
import re
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

from gspread.utils import rowcol_to_a1

from utils.logger import get_logger
from utils.date_helpers import parse_date
from config import (
    WC_STORE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET, SYNC_LOOKBACK_DAYS, SYNC_EXCLUDED_EMAIL_PATTERN,
    COL_NAME, COL_EMAIL, COL_PLAN, COL_START_DATE, COL_END_DATE,
    COL_LAST_REMINDER, COL_STAGE, COL_NOTES, COL_PHONE,
)

logger = get_logger(__name__)

# Must match the end-date formula in the sheet (column E)
PLAN_DAYS = {1: 30, 3: 90, 6: 180, 12: 365}
MANUAL_ENTRY_TOLERANCE_DAYS = 2
SHEETS_EPOCH = date(1899, 12, 30)


def _serial(d: date) -> int:
    """Google Sheets date serial, so the cell is a real date the formulas can use."""
    return (d - SHEETS_EPOCH).days


def _plan_from_item(item_name: str) -> tuple[str, int] | None:
    """'12 Months Premium Television Subscription' → ('12 Months Premium Subscription', 365)."""
    match = re.search(r"(\d+)\s*months?", item_name, re.IGNORECASE)
    if not match or int(match.group(1)) not in PLAN_DAYS:
        return None  # e.g. Free Trial
    months  = int(match.group(1))
    unit    = "Month" if months == 1 else "Months"
    premium = " Premium" if "premium" in item_name.lower() else ""
    return f"{months} {unit}{premium} Subscription", PLAN_DAYS[months]


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


class _Sheet:
    """Row-level writes that respect the sheet's formulas and formats."""

    def __init__(self, worksheet):
        self.ws      = worksheet
        self.headers = worksheet.row_values(1)
        self.col     = {name: self.headers.index(name) + 1 for name in self.headers}

    def last_row(self) -> int:
        return len(self.ws.col_values(self.col[COL_EMAIL]))

    def formula_template(self, column: int, before_row: int) -> tuple[str, int] | None:
        """Nearest formula above `before_row` in this column, with the row it came from."""
        start  = max(2, before_row - 30)
        letter = rowcol_to_a1(1, column)[:-1]
        cells  = self.ws.get(f"{letter}{start}:{letter}{before_row - 1}", value_render_option="FORMULA")
        for offset in range(len(cells) - 1, -1, -1):
            value = cells[offset][0] if cells[offset] else ""
            if isinstance(value, str) and value.startswith("="):
                return value, start + offset
        return None

    def formulas_for(self, row: int, columns: list[int]) -> list[dict]:
        updates = []
        for column in columns:
            template = self.formula_template(column, row)
            if template:
                formula, source_row = template
                formula = re.sub(rf"\b([A-Z]{{1,2}}){source_row}\b", rf"\g<1>{row}", formula)
                updates.append({"range": rowcol_to_a1(row, column), "values": [[formula]]})
        return updates

    def is_formula(self, row: int, column: int) -> bool:
        value = self.ws.get(rowcol_to_a1(row, column), value_render_option="FORMULA")
        return bool(value and value[0] and str(value[0][0]).startswith("="))

    def write(self, row: int, values: dict, restore_formula_columns: list[int]):
        raw = [{"range": rowcol_to_a1(row, self.col[name]), "values": [[value]]} for name, value in values.items()]
        self.ws.batch_update(raw, value_input_option="RAW")
        written  = {self.col[name] for name in values}
        formulas = self.formulas_for(row, [c for c in restore_formula_columns if c not in written])
        if formulas:
            self.ws.batch_update(formulas, value_input_option="USER_ENTERED")
        # Date columns keep the sheet's date format
        start_col, end_col = self.col[COL_START_DATE], self.col[COL_END_DATE]
        meta = self.ws.spreadsheet.fetch_sheet_metadata({
            "includeGridData": True,
            "ranges": [f"'{self.ws.title}'!{rowcol_to_a1(row - 1, start_col)}:{rowcol_to_a1(row - 1, end_col)}"],
        })
        cells = meta["sheets"][0]["data"][0].get("rowData", [{}])[0].get("values", [])
        number_format = next((c["userEnteredFormat"]["numberFormat"] for c in cells
                              if c.get("userEnteredFormat", {}).get("numberFormat")), None)
        if number_format:
            self.ws.format(f"{rowcol_to_a1(row, start_col)}:{rowcol_to_a1(row, end_col)}",
                           {"numberFormat": number_format})


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

    sheet = _Sheet(worksheet)
    # Every column that holds a per-row formula (end date, status, WhatsApp text/link)
    next_row = sheet.last_row() + 1
    formula_columns = [c for c in range(1, len(sheet.headers) + 1)
                       if sheet.formula_template(c, next_row)]
    rows  = worksheet.get_all_records()
    added = renewed = tagged = skipped = 0

    for order in orders:
        order_id = str(order["id"])
        tag      = f"wc#{order_id}"
        email    = (order.get("billing", {}).get("email") or "").strip().lower()

        if any(tag in str(r.get(COL_NOTES, "")) for r in rows):
            continue  # already applied
        if email and re.search(SYNC_EXCLUDED_EMAIL_PATTERN, email):
            continue  # owner's own test orders
        plans = [p for p in (_plan_from_item(i.get("name", "")) for i in order.get("line_items", [])) if p]
        if not email or not plans:
            logger.info(f"Order sync | Order {order_id} | No email or no subscription plan — skipping")
            skipped += 1
            continue

        plan_name, days = plans[0]
        start = _order_date(order)

        matches = [(i, r) for i, r in enumerate(rows) if str(r.get(COL_EMAIL, "")).strip().lower() == email]
        if matches:
            # The customer's current row = the one ending last
            index, row = max(matches, key=lambda m: parse_date(str(m[1].get(COL_END_DATE, ""))) or date.min)
            row_number  = index + 2
            row_start   = parse_date(str(row.get(COL_START_DATE, "")))
            current_end = parse_date(str(row.get(COL_END_DATE, "")))
            notes       = (str(row.get(COL_NOTES, "")) + f" {tag}").strip()

            # Already reflected when the row was (re)started around or after this
            # order, or its end date already covers this purchase.
            already_applied = (
                (row_start and row_start >= start - timedelta(days=MANUAL_ENTRY_TOLERANCE_DAYS))
                or (current_end and current_end >= start + timedelta(days=days - 7))
            )
            if already_applied:
                logger.info(f"Order sync | Order {order_id} | Row {row_number} already covers this purchase (ends {current_end}) — tagging only")
                values, restore = {COL_NOTES: notes}, []
                tagged += 1
            else:
                # Early renewal: the new period starts when the current one ends
                new_start = max(start, current_end) if current_end else start
                logger.info(f"Order sync | Order {order_id} | Renewal — row {row_number} {plan_name} from {new_start}, ends {new_start + timedelta(days=days)}")
                values = {COL_PLAN: plan_name, COL_START_DATE: _serial(new_start),
                          COL_LAST_REMINDER: "", COL_STAGE: "", COL_NOTES: notes}
                # Put back end-date/status formulas if the row had them overwritten (e.g. "churned")
                restore = [c for c in formula_columns if not dry_run and not sheet.is_formula(row_number, c)]
                renewed += 1
            if not dry_run:
                sheet.write(row_number, values, restore)
            row.update({k: v for k, v in values.items() if k != COL_START_DATE})
            continue

        billing = order.get("billing", {})
        logger.info(f"Order sync | Order {order_id} | New subscriber — {plan_name} from {start}, ends {start + timedelta(days=days)}")
        added += 1
        if not dry_run:
            row_number = sheet.last_row() + 1
            sheet.write(row_number, {
                COL_NAME: f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip(),
                COL_EMAIL: email, COL_PLAN: plan_name, COL_START_DATE: _serial(start),
                COL_NOTES: tag, COL_PHONE: billing.get("phone", ""),
            }, formula_columns)
        rows.append({COL_EMAIL: email, COL_NOTES: tag})

    logger.info(f"Order sync | Added: {added} | Renewed: {renewed} | Tagged: {tagged} | Skipped: {skipped}")
