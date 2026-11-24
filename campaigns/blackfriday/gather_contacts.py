"""
Gather every past customer / lead into one Brevo list for Black Friday
---------------------------------------------------------------------
Sources:
  1. a CSV made on the owner's Mac (Stripe exports, old WooCommerce exports,
     merged customer files, Subscription Tracker): EMAIL, FIRSTNAME, LAST_SEEN, SOURCES
  2. every WooCommerce order of all time (any status) and every WooCommerce customer
Then it compares with Brevo:
  - contacts that unsubscribed or are blocked are NEVER added or emailed
  - addresses not in Brevo yet are created
  - everyone eligible is put in the list "BF26 past customers & leads"

Brevo only accepts calls from the VPS:

  docker cp /root/bf26_local_contacts.csv iptvsup-deploy-subscription-1:/tmp/bf26_local_contacts.csv
  K=$(docker exec iptvsup-deploy-payment-1 printenv BREVO_API_KEY)
  docker exec -u appuser -e BREVO_API_KEY="$K" iptvsup-deploy-subscription-1 \\
      python3 campaigns/blackfriday/gather_contacts.py /tmp/bf26_local_contacts.csv          # dry run: counts only
  ... python3 campaigns/blackfriday/gather_contacts.py /tmp/bf26_local_contacts.csv --apply  # create list + add contacts
"""

import base64
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import WC_STORE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET

LIST_NAME = "BF26 past customers & leads"
BREVO = "https://api.brevo.com/v3"
EM = re.compile(r"^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$")
SKIP = re.compile(r"(@example\.|@test\.|^test@|@m\.com$|@iptvsup\.com$|@iptvwatchhub|elyoussefimehdi|noreply|no-reply)")


def brevo(method: str, path: str, key: str, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BREVO + path, data=data, method=method,
                                 headers={"api-key": key, "accept": "application/json",
                                          "content-type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise


def wc_get(path: str, params: dict) -> list:
    auth = base64.b64encode(f"{WC_CONSUMER_KEY}:{WC_CONSUMER_SECRET}".encode()).decode()
    out, page = [], 1
    while True:
        q = urllib.parse.urlencode({**params, "per_page": 100, "page": page})
        req = urllib.request.Request(f"{WC_STORE_URL}/wp-json/wc/v3/{path}?{q}",
                                     headers={"Authorization": f"Basic {auth}", "User-Agent": "subscription-automation"})
        with urllib.request.urlopen(req, timeout=60) as r:
            batch = json.load(r)
        out.extend(batch)
        if len(batch) < 100:
            return out
        page += 1


def clean(email: str) -> str:
    e = (email or "").strip().lower().strip(".,;<>\"'")
    return e if EM.match(e) and not SKIP.search(e) else ""


def main():
    args = sys.argv[1:]
    key = os.getenv("BREVO_API_KEY", "").strip()
    if not key or not args or args[0].startswith("--"):
        sys.exit("Usage: see the top of this file (BREVO_API_KEY and the CSV path are required).")
    apply = "--apply" in args

    people = {}  # email -> {"first": str, "sources": set}

    def add(email, first, source):
        e = clean(email)
        if not e:
            return
        p = people.setdefault(e, {"first": "", "sources": set()})
        f = (first or "").strip().split(" ")[0].capitalize()
        if f and not p["first"] and re.match(r"^[A-Za-zÀ-ÿ'\-]{2,}$", f):
            p["first"] = f
        p["sources"].add(source)

    with open(args[0], newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            add(r["EMAIL"], r.get("FIRSTNAME"), "mac_file")
    n_file = len(people)

    for o in wc_get("orders", {"status": "any"}):
        b = o.get("billing") or {}
        add(b.get("email"), b.get("first_name"), "woocommerce_orders")
    for c in wc_get("customers", {"role": "all"}):
        add(c.get("email"), c.get("first_name") or (c.get("billing") or {}).get("first_name"), "woocommerce_customers")
    print(f"Gathered {len(people)} unique addresses ({n_file} from the Mac file, "
          f"{len(people) - n_file} more from live WooCommerce)")

    # Everything Brevo already knows
    brevo_contacts, offset = {}, 0
    while True:
        rows = brevo("GET", f"/contacts?limit=1000&offset={offset}", key).get("contacts", [])
        for c in rows:
            brevo_contacts[c["email"].lower()] = c
        if len(rows) < 1000:
            break
        offset += 1000
    blocked, offset = set(), 0
    while True:
        rows = brevo("GET", f"/smtp/blockedContacts?limit=100&offset={offset}", key).get("contacts", [])
        blocked |= {c["email"].lower() for c in rows if c.get("email")}
        if len(rows) < 100:
            break
        offset += 100

    unsub = {e for e, c in brevo_contacts.items() if c.get("emailBlacklisted")} | blocked
    eligible = {e: p for e, p in people.items() if e not in unsub}
    new = [e for e in eligible if e not in brevo_contacts]
    existing = [e for e in eligible if e in brevo_contacts]
    src = Counter(s for e in new for s in people[e]["sources"])
    print(f"Brevo has {len(brevo_contacts)} contacts | unsubscribed/blocked among ours: {len(people) - len(eligible)}")
    print(f"Eligible: {len(eligible)} = {len(existing)} already in Brevo + {len(new)} NEW")
    print(f"New contacts come from: {dict(src)}")

    if not apply:
        print("Dry run. Add --apply to create the list and add the contacts.")
        return

    lists = brevo("GET", "/contacts/lists?limit=50", key).get("lists", [])
    lst = next((l for l in lists if l["name"] == LIST_NAME), None)
    if lst:
        list_id = lst["id"]
    else:
        folders = brevo("GET", "/contacts/folders?limit=10", key).get("folders", [])
        list_id = brevo("POST", "/contacts/lists", key, {"name": LIST_NAME, "folderId": folders[0]["id"]})["id"]
    print(f"List #{list_id}: {LIST_NAME}")

    for i in range(0, len(new), 100):
        chunk = new[i:i + 100]
        body = [{"email": e, "attributes": {"FIRSTNAME": eligible[e]["first"]} if eligible[e]["first"] else {}}
                for e in chunk]
        brevo("POST", "/contacts/import", key, {"jsonBody": body, "listIds": [list_id],
                                               "updateExistingContacts": False, "emailBlacklist": False})
        time.sleep(1)
    for i in range(0, len(existing), 150):
        brevo("POST", f"/contacts/lists/{list_id}/contacts/add", key, {"emails": existing[i:i + 150]})
        time.sleep(1)
    print(f"Done: {len(new)} new contacts imported and {len(existing)} existing contacts added to list #{list_id}. "
          f"Brevo processes imports in the background (a minute or two).")


if __name__ == "__main__":
    main()
