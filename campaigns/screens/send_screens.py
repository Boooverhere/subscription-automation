"""
Extra screens announcement: one-time send
-----------------------------------------
Audience (Subscription Tracker status):
  active, expires soon  -> "active" email
  expired               -> "expired" email      (churned is NOT included)
Skips: Brevo blocklisted contacts (marketing unsubscribes + transactional
blocks), duplicates, addresses already in the sent log, SKIP_EMAILS.

Brevo only accepts calls from the VPS. Pass the API key from the payment
container so the blocklist check works:

  K=$(docker exec iptvsup-deploy-payment-1 printenv BREVO_API_KEY)
  docker exec -u appuser -e BREVO_API_KEY="$K" iptvsup-deploy-subscription-1 \
      python3 campaigns/screens/send_screens.py --count
  ... --test-email you@example.com     # both versions, marked [TEST]
  ... --send                           # live
"""

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
from config import COL_NAME, COL_EMAIL, COL_STATUS
from campaigns.screens.screens_email import get_screens_email

logger = get_logger(__name__)

SENT_LOG = Path(__file__).resolve().parent / "screens_sent.log"
AUDIENCE = {"active": "active", "expires soon": "active", "expired": "expired"}
SKIP_EMAILS = {"retardjews@gmail.com"}
BREVO = "https://api.brevo.com/v3"


def brevo_get(path: str, key: str):
    req = urllib.request.Request(BREVO + path, headers={"api-key": key, "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode() or "{}")


def transactional_blocked(key: str) -> set:
    blocked, offset = set(), 0
    while True:
        data = brevo_get(f"/smtp/blockedContacts?limit=100&offset={offset}", key)
        rows = data.get("contacts", [])
        blocked |= {c["email"].lower() for c in rows if c.get("email")}
        if len(rows) < 100:
            return blocked
        offset += 100


def marketing_blacklisted(email: str, key: str) -> bool:
    try:
        return bool(brevo_get("/contacts/" + urllib.parse.quote(email), key).get("emailBlacklisted"))
    except urllib.error.HTTPError as e:
        if e.code == 404:  # not a Brevo contact, nothing to honour
            return False
        raise


def load_sent() -> set:
    return {l.strip().lower() for l in SENT_LOG.read_text().splitlines() if l.strip()} if SENT_LOG.exists() else set()


def build_targets() -> list:
    rows = get_all_subscribers(get_sheet())
    # A customer can have several rows (renewals): prefer the "active" version.
    best = {}
    for s in rows:
        aud = AUDIENCE.get(s.get(COL_STATUS, "").strip().lower())
        email = s.get(COL_EMAIL, "").strip()
        if not aud or "@" not in email or email.lower() in SKIP_EMAILS:
            continue
        cur = best.get(email.lower())
        if cur is None or (cur["audience"] == "expired" and aud == "active"):
            best[email.lower()] = {"email": email, "name": s.get(COL_NAME, "").strip(), "audience": aud}
    return list(best.values())


def main():
    args = sys.argv[1:]
    key = os.getenv("BREVO_API_KEY", "").strip()

    if "--test-email" in args:
        to = args[args.index("--test-email") + 1]
        for aud in ("active", "expired"):
            c = get_screens_email("Mehdi", aud)
            ok = send_email(to, f"[TEST {aud}] {c['subject']}", c["body"])
            logger.info(f"Test ({aud}) to {to}: {'sent' if ok else 'FAILED'}")
        return

    targets = build_targets()
    sent_before = load_sent()
    targets = [t for t in targets if t["email"].lower() not in sent_before]

    if not key:
        logger.error("BREVO_API_KEY not set: cannot check unsubscribes. See the usage at the top. Stopping.")
        sys.exit(1)
    try:
        blocked = transactional_blocked(key)
    except urllib.error.HTTPError as e:
        logger.error(f"Brevo API refused ({e.code}). Run this on the VPS. Stopping.")
        sys.exit(1)

    final, skipped = [], []
    for t in targets:
        e = t["email"].lower()
        if e in blocked or marketing_blacklisted(e, key):
            skipped.append(e)
        else:
            final.append(t)

    n_act = sum(t["audience"] == "active" for t in final)
    logger.info(f"Audience: {len(final)} to send ({n_act} active, {len(final) - n_act} expired) | "
                f"{len(skipped)} unsubscribed/blocked skipped | {len(sent_before)} already sent")

    if "--send" not in args:
        logger.info("Count only. Add --send to send for real.")
        return

    ok_n = err_n = 0
    for i, t in enumerate(final, 1):
        c = get_screens_email(t["name"], t["audience"])
        if send_email(t["email"], c["subject"], c["body"]):
            with open(SENT_LOG, "a") as f:
                f.write(t["email"].lower() + "\n")
            ok_n += 1
            logger.info(f"[{i}/{len(final)}] sent ({t['audience']}) -> {t['email']}")
            time.sleep(2)
        else:
            err_n += 1
            logger.error(f"[{i}/{len(final)}] FAILED -> {t['email']}")
    logger.info(f"=== Done | sent {ok_n} | failed {err_n} ===")


if __name__ == "__main__":
    main()
