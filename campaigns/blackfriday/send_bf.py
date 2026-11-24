"""
Black Friday 2026 sender: one script for all three waves
--------------------------------------------------------
Audiences (one email per address per wave, customers win over subscribers):
  active      tracker status active / expires soon
  churned     tracker status expired / churned
  notify      visitors who asked on iptvsup.com to be emailed when the sale starts
  churned     also: contacts in the lists given with --past-list-id (past customers gathered
              from Stripe/WooCommerce by gather_contacts.py)
  subscriber  contacts in the Brevo lists given with --list-id (comma-separated, e.g. 10,26)
              who are not in the tracker
Skips: Brevo blocklists (marketing unsubscribes + transactional blocks), SKIP_EMAILS,
addresses already sent this wave, and anyone who ordered on iptvsup.com since the
sale started (Nov 26), so buyers don't get the reminder or last-call emails.

Brevo only accepts calls from the VPS. Pass the API key from the payment container:

  K=$(docker exec iptvsup-deploy-payment-1 printenv BREVO_API_KEY)
  docker exec -u appuser -e BREVO_API_KEY="$K" iptvsup-deploy-subscription-1 \\
      python3 campaigns/blackfriday/send_bf.py --lists           # find the newsletter list id
  ... --wave launch --list-id N --count                         # audience sizes only
  ... --wave launch --test-email you@example.com                # all 3 versions, marked [TEST]
  ... --wave launch --list-id N --send                          # live
Waves: teaser (Tue Nov 24), launch (Fri Nov 27), lastcall (Mon Nov 30).

Old-contact split (bounce protection): with --contacts-file /tmp/bf26_local_contacts.csv
  --skip-old   leaves out people last seen before 2024 (send to everyone else first)
  --only-old   sends only to them (later, once the bounce rate looks fine)
Current customers (tracker "active") are never treated as old.
The teaser skips the site's notify signups (they asked for one email when it starts).
"""

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger import get_logger
from services.sheets_service import get_sheet, get_all_subscribers
from services.email_service import send_email
from config import COL_NAME, COL_EMAIL, COL_STATUS, WC_STORE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET
from campaigns.blackfriday.bf_email import get_bf_email

logger = get_logger(__name__)

WAVES = ("teaser", "launch", "lastcall")  # Nov 29 reminder dropped: max 3 emails per person
TRACKER_AUDIENCE = {"active": "active", "expires soon": "active", "expired": "churned", "churned": "churned"}
RANK = {"subscriber": 0, "notify": 1, "churned": 2, "active": 3}
SKIP_EMAILS = {"retardjews@gmail.com"}
SALE_START = "2026-11-26T00:00:00"
BREVO = "https://api.brevo.com/v3"


def brevo_get(path: str, key: str):
    req = urllib.request.Request(BREVO + path, headers={"api-key": key, "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode() or "{}")


def transactional_blocked(key: str) -> set:
    blocked, offset = set(), 0
    while True:
        rows = brevo_get(f"/smtp/blockedContacts?limit=100&offset={offset}", key).get("contacts", [])
        blocked |= {c["email"].lower() for c in rows if c.get("email")}
        if len(rows) < 100:
            return blocked
        offset += 100


def list_contacts(list_id: int, key: str) -> list:
    out, offset = [], 0
    while True:
        rows = brevo_get(f"/contacts/lists/{list_id}/contacts?limit=500&offset={offset}", key).get("contacts", [])
        out.extend(rows)
        if len(rows) < 500:
            return out
        offset += 500


def marketing_blacklisted(email: str, key: str) -> bool:
    try:
        return bool(brevo_get("/contacts/" + urllib.parse.quote(email), key).get("emailBlacklisted"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def bf_buyers() -> set:
    """Emails with an order (not cancelled/failed) since the sale started."""
    if not (WC_CONSUMER_KEY and WC_CONSUMER_SECRET):
        logger.error("WC keys not set: cannot exclude Black Friday buyers. Stopping.")
        sys.exit(1)
    auth = base64.b64encode(f"{WC_CONSUMER_KEY}:{WC_CONSUMER_SECRET}".encode()).decode()
    buyers, page = set(), 1
    while True:
        q = urllib.parse.urlencode({"after": SALE_START, "per_page": 100, "page": page,
                                    "status": "pending,on-hold,processing,completed"})
        req = urllib.request.Request(f"{WC_STORE_URL}/wp-json/wc/v3/orders?{q}",
                                     headers={"Authorization": f"Basic {auth}", "User-Agent": "subscription-automation"})
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.load(r)
        buyers |= {(o.get("billing") or {}).get("email", "").strip().lower() for o in batch} - {""}
        if len(batch) < 100:
            return buyers
        page += 1


def wc_get(path: str):
    auth = base64.b64encode(f"{WC_CONSUMER_KEY}:{WC_CONSUMER_SECRET}".encode()).decode()
    req = urllib.request.Request(f"{WC_STORE_URL}/wp-json/{path}",
                                 headers={"Authorization": f"Basic {auth}", "User-Agent": "subscription-automation"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def notify_signups() -> list:
    """Emails left in the site's Black Friday "notify me" popup."""
    try:
        return wc_get("wc-iptvsup/v1/bf-notify")
    except urllib.error.HTTPError as e:
        logger.error(f"Could not read site signups ({e.code}). Stopping.")
        sys.exit(1)


def sent_log(wave: str) -> Path:
    return Path(__file__).resolve().parent / f"bf_{wave}_sent.log"


def load_sent(wave: str) -> set:
    p = sent_log(wave)
    return {l.strip().lower() for l in p.read_text().splitlines() if l.strip()} if p.exists() else set()


def build_targets(list_ids, key: str, wave: str, past_ids=()) -> list:
    best = {}

    def add(email, name, aud):
        e = email.strip().lower()
        if "@" not in e or e in SKIP_EMAILS or e.endswith("@example.com"):
            return
        cur = best.get(e)
        if cur is None or RANK[aud] > RANK[cur["audience"]]:
            best[e] = {"email": email.strip(), "name": name, "audience": aud}
        elif not cur["name"] and name:
            cur["name"] = name

    for s in get_all_subscribers(get_sheet()):
        aud = TRACKER_AUDIENCE.get(s.get(COL_STATUS, "").strip().lower())
        if aud:
            add(s.get(COL_EMAIL, ""), s.get(COL_NAME, "").strip(), aud)
    if wave != "teaser":
        for row in notify_signups():
            add(row.get("email", ""), "", "notify")
    for ids, aud in ((list_ids, "subscriber"), (past_ids, "churned")):
        for list_id in ids:
            for c in list_contacts(list_id, key):
                attrs = c.get("attributes") or {}
                name = (attrs.get("FIRSTNAME") or attrs.get("PRENOM") or "").strip()
                add(c.get("email", ""), name, aud)
    return list(best.values())


def old_contacts(path) -> set:
    """Emails last seen before 2024 in the merged contacts file (EMAIL, LAST_SEEN columns)."""
    if not path or not Path(path).exists():
        logger.error("--skip-old / --only-old need --contacts-file /tmp/bf26_local_contacts.csv. Stopping.")
        sys.exit(1)
    import csv
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["EMAIL"].strip().lower() for r in csv.DictReader(fh)
                if r.get("LAST_SEEN") and r["LAST_SEEN"] < "2024-01-01"}


def arg(args, flag):
    return args[args.index(flag) + 1] if flag in args else None


def main():
    args = sys.argv[1:]
    key = os.getenv("BREVO_API_KEY", "").strip()

    if "--lists" in args:
        for l in brevo_get("/contacts/lists?limit=50", key).get("lists", []):
            print(f"{l['id']:>4}  {l.get('uniqueSubscribers', l.get('totalSubscribers', '?')):>6}  {l['name']}")
        return

    wave = arg(args, "--wave")
    if wave not in WAVES:
        logger.error(f"--wave must be one of {WAVES}")
        sys.exit(1)

    if "--test-email" in args:
        to = arg(args, "--test-email")
        for aud in ("active", "churned", "subscriber") + (() if wave == "teaser" else ("notify",)):
            c = get_bf_email("Mehdi", wave, aud)
            ok = send_email(to, f"[TEST {wave}/{aud}] {c['subject']}", c["body"])
            logger.info(f"Test ({wave}/{aud}) to {to}: {'sent' if ok else 'FAILED'}")
        return

    if not key:
        logger.error("BREVO_API_KEY not set: cannot check unsubscribes. See the usage at the top. Stopping.")
        sys.exit(1)
    list_ids = [int(x) for x in arg(args, "--list-id").split(",") if x.strip()] if arg(args, "--list-id") else []
    if not list_ids:
        logger.warning("No --list-id: newsletter subscribers are NOT included.")

    try:
        past_ids = [int(x) for x in arg(args, "--past-list-id").split(",") if x.strip()] if arg(args, "--past-list-id") else []
        targets = build_targets(list_ids, key, wave, past_ids)
        blocked = transactional_blocked(key)
    except urllib.error.HTTPError as e:
        logger.error(f"Brevo API refused ({e.code}). Run this on the VPS. Stopping.")
        sys.exit(1)
    buyers = bf_buyers()
    sent_before = load_sent(wave)

    final, skipped, bought = [], 0, 0
    for t in targets:
        e = t["email"].lower()
        if e in sent_before:
            continue
        if e in buyers:
            bought += 1
        elif e in blocked or marketing_blacklisted(e, key):
            skipped += 1
        else:
            final.append(t)

    if "--skip-old" in args or "--only-old" in args:
        old = old_contacts(arg(args, "--contacts-file"))
        is_old = lambda t: t["email"].lower() in old and t["audience"] != "active"
        final = [t for t in final if (is_old(t) if "--only-old" in args else not is_old(t))]
        logger.info(f"Old-contact split: {'ONLY people last seen before 2024' if '--only-old' in args else 'skipping people last seen before 2024'}")

    counts = {a: sum(t["audience"] == a for t in final) for a in RANK}
    logger.info(f"Wave {wave} | to send {len(final)} (active {counts['active']}, churned {counts['churned']}, "
                f"notify {counts['notify']}, subscriber {counts['subscriber']}) | unsubscribed/blocked {skipped} | already bought {bought} | "
                f"already sent {len(sent_before)}")

    if "--send" not in args:
        logger.info("Count only. Add --send to send for real.")
        return

    ok_n = err_n = 0
    for i, t in enumerate(final, 1):
        c = get_bf_email(t["name"], wave, t["audience"])
        if send_email(t["email"], c["subject"], c["body"]):
            with open(sent_log(wave), "a") as f:
                f.write(t["email"].lower() + "\n")
            ok_n += 1
            logger.info(f"[{i}/{len(final)}] sent ({t['audience']}) -> {t['email']}")
            time.sleep(2)
        else:
            err_n += 1
            logger.error(f"[{i}/{len(final)}] FAILED -> {t['email']}")
    logger.info(f"=== Done | wave {wave} | sent {ok_n} | failed {err_n} ===")


if __name__ == "__main__":
    main()
