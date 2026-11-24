"""
Black Friday as Brevo campaigns (reports, open/click rates and segments in Brevo)
---------------------------------------------------------------------------------
For one wave it:
  1. works out who gets which version, exactly like send_bf.py: one email per
     person, unsubscribed/blocked left out, people who already ordered left out,
     optional old-contact split (last seen before 2024)
  2. fills one Brevo list per group, so nobody is in two of them:
       "BF26 <wave> · active · <date time>" / "· churned" / "· subscriber" / "· notify"
       (with --only-old: "BF26 <wave> · old churned · <date time>" etc.)
  3. creates one DRAFT campaign per non-empty list with the right design, subject,
     preview text and Brevo's first-name + unsubscribe placeholders
Nothing is sent: open Brevo > Campaigns, check the drafts, then Send or Schedule.

Brevo only accepts calls from the VPS:

  K=$(docker exec iptvsup-deploy-payment-1 printenv BREVO_API_KEY)
  docker exec -u appuser -e BREVO_API_KEY="$K" iptvsup-deploy-subscription-1 \\
      python3 campaigns/blackfriday/brevo_campaigns.py --wave teaser --list-id 10 --past-list-id 26 \\
      --contacts-file /tmp/bf26_local_contacts.csv --skip-old            # counts only
  ... same + --create          # fill the lists and create the draft campaigns
  ... --only-old instead of --skip-old for the second batch
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.logger import get_logger
from campaigns.blackfriday.bf_email import get_bf_email
from campaigns.blackfriday.send_bf import (WAVES, RANK, arg, build_targets, transactional_blocked,
                                           marketing_blacklisted, bf_buyers, old_contacts)

logger = get_logger(__name__)
BREVO = "https://api.brevo.com/v3"
SENDER = {"name": "IPTVSup", "email": "contact@iptvsup.com"}


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
            raise RuntimeError(f"Brevo {method} {path} -> {e.code}: {e.read().decode()[:300]}")


def all_brevo_emails(key: str) -> set:
    emails, offset = set(), 0
    while True:
        rows = brevo("GET", f"/contacts?limit=1000&offset={offset}", key).get("contacts", [])
        emails |= {c["email"].lower() for c in rows}
        if len(rows) < 1000:
            return emails
        offset += 1000


def fill_list(name: str, people: list, known: set, key: str) -> int:
    """Create a new list called `name` and put exactly these people in it.
    (A fresh list per run: emptying a Brevo list happens in the background and
    could race with the adds.)"""
    folders = brevo("GET", "/contacts/folders?limit=10", key).get("folders", [])
    list_id = brevo("POST", "/contacts/lists", key, {"name": name, "folderId": folders[0]["id"]})["id"]

    existing = [p["email"].lower() for p in people if p["email"].lower() in known]
    new = [p for p in people if p["email"].lower() not in known]
    for i in range(0, len(existing), 150):
        brevo("POST", f"/contacts/lists/{list_id}/contacts/add", key, {"emails": existing[i:i + 150]})
        time.sleep(1)
    if new:
        body = [{"email": p["email"].lower(),
                 "attributes": {"FIRSTNAME": p["name"].split(" ")[0].capitalize()} if p.get("name") else {}}
                for p in new]
        brevo("POST", "/contacts/import", key, {"jsonBody": body, "listIds": [list_id],
                                               "updateExistingContacts": False, "emailBlacklist": False})
    return list_id


def main():
    args = sys.argv[1:]
    key = os.getenv("BREVO_API_KEY", "").strip()
    wave = arg(args, "--wave")
    if not key or wave not in WAVES:
        sys.exit(f"Usage: see the top of this file (BREVO_API_KEY and --wave {WAVES} are required).")

    list_ids = [int(x) for x in (arg(args, "--list-id") or "").split(",") if x.strip()]
    past_ids = [int(x) for x in (arg(args, "--past-list-id") or "").split(",") if x.strip()]
    targets = build_targets(list_ids, key, wave, past_ids)
    blocked = transactional_blocked(key)
    buyers = bf_buyers()

    final, skipped, bought = [], 0, 0
    for t in targets:
        e = t["email"].lower()
        if e in buyers:
            bought += 1
        elif e in blocked or marketing_blacklisted(e, key):
            skipped += 1
        else:
            final.append(t)

    old_tag = ""
    if "--skip-old" in args or "--only-old" in args:
        old = old_contacts(arg(args, "--contacts-file"))
        is_old = lambda t: t["email"].lower() in old and t["audience"] != "active"
        final = [t for t in final if (is_old(t) if "--only-old" in args else not is_old(t))]
        old_tag = "old " if "--only-old" in args else ""

    groups = {a: [t for t in final if t["audience"] == a] for a in RANK}
    logger.info(f"Wave {wave} {'(old contacts only) ' if old_tag else ''}| {len(final)} people: "
                + ", ".join(f"{a} {len(g)}" for a, g in groups.items())
                + f" | unsubscribed/blocked {skipped} | already bought {bought}")

    if "--create" not in args:
        logger.info("Counts only. Add --create to fill the Brevo lists and create the draft campaigns.")
        return

    known = all_brevo_emails(key)
    stamp = time.strftime("%b %d %H:%M")
    for aud, people in groups.items():
        if not people:
            continue
        name = f"BF26 {wave} · {old_tag}{aud} · {stamp}"
        list_id = fill_list(name, people, known, key)
        c = get_bf_email("", wave, aud, brevo=True)
        camp = brevo("POST", "/emailCampaigns", key, {
            "name": name,
            "subject": c["subject"],
            "previewText": c["preview"],
            "sender": SENDER,
            "replyTo": SENDER["email"],
            "htmlContent": c["body"],
            "recipients": {"listIds": [list_id]},
            "inlineImageActivation": False,
        })
        logger.info(f"Draft campaign #{camp.get('id')} '{name}' -> list #{list_id} ({len(people)} people)")
    logger.info("Done. Nothing was sent. Open Brevo > Campaigns, check the drafts, then Send or Schedule.")


if __name__ == "__main__":
    main()
