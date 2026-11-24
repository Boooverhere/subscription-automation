"""
Create (or update) the Black Friday abandoned-cart email as a Brevo template.
Brevo only accepts API calls from the VPS:

  K=$(docker exec iptvsup-deploy-payment-1 printenv BREVO_API_KEY)
  docker exec -u appuser -e BREVO_API_KEY="$K" iptvsup-deploy-subscription-1 \\
      python3 campaigns/blackfriday/brevo_cart_template.py            # create, prints the template id
  ... python3 campaigns/blackfriday/brevo_cart_template.py --update ID  # replace an existing one

The automation is switched to this template in the Brevo editor on Nov 26
and back to template #42 after Nov 30.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from campaigns.blackfriday.bf_email import get_abandoned_cart_template

NAME = "BF26 abandoned cart (Nov 26-30)"


def call(method: str, path: str, key: str, body: dict):
    req = urllib.request.Request("https://api.brevo.com/v3" + path, method=method,
                                 data=json.dumps(body).encode(),
                                 headers={"api-key": key, "content-type": "application/json", "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw else {}


def main():
    key = os.getenv("BREVO_API_KEY", "").strip()
    if not key:
        sys.exit("BREVO_API_KEY not set (see usage at the top).")
    t = get_abandoned_cart_template()
    body = {"templateName": NAME, "subject": t["subject"], "htmlContent": t["html"],
            "sender": {"name": "IPTVSup", "email": "contact@iptvsup.com"},
            "replyTo": "contact@iptvsup.com", "isActive": True}
    try:
        if "--update" in sys.argv:
            tid = int(sys.argv[sys.argv.index("--update") + 1])
            call("PUT", f"/smtp/templates/{tid}", key, body)
            print(f"Updated template #{tid}: {NAME}")
        else:
            res = call("POST", "/smtp/templates", key, body)
            print(f"Created template #{res.get('id')}: {NAME}")
    except urllib.error.HTTPError as e:
        sys.exit(f"Brevo refused ({e.code}): {e.read().decode()[:300]}")


if __name__ == "__main__":
    main()
