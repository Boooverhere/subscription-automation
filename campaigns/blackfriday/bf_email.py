"""
Black Friday 2026 emails: bonus months, prices unchanged
---------------------------------------------------------
  3 months + 1 free, 6 months + 3 free, 12 months + 6 free (Nov 26 to Nov 30)

Waves:     teaser (Tue Nov 24), launch (Fri Nov 27), lastcall (Mon Nov 30)
           (the Nov 29 reminder was dropped: max 3 Black Friday emails per person)
Audiences: active      current customers (tracker: active / expires soon)
           churned     former customers (tracker: expired / churned)
           subscriber  newsletter contacts who never bought
Design: all-black email with a big "Black Friday / 6 MONTHS FREE" hero. Everything
is HTML text (the logo too), so it still reads when images are blocked.
"""

LANDING = "https://iptvsup.com/black-friday-iptv-deal/"
WHATSAPP_URL = "https://wa.me/message/KYISERSGPOL5K1"

ORANGE = "#FF6B35"   # IPTVSup accent
BLUE = "#3B8EDB"     # "sup" in the logo
BG = "#000000"
TEXT = "#FFFFFF"
MUTED = "#9A9AA6"
FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif"

SUBJECTS = {
    ("teaser", "active"): "Black Friday starts Thursday: up to 6 free months on your IPTVSup plan",
    ("teaser", "churned"): "Black Friday starts Thursday: up to 6 months of IPTVSup free",
    ("teaser", "subscriber"): "Black Friday starts Thursday: up to 6 months of IPTVSup free",
    ("launch", "active"): "Black Friday: up to 6 free months on your IPTVSup plan",
    ("launch", "churned"): "Come back to IPTVSup with up to 6 months free",
    ("launch", "subscriber"): "IPTVSup Black Friday starts now: up to 6 months free",
    ("reminder", "active"): "2 days left for your free IPTVSup months",
    ("reminder", "churned"): "2 days left: up to 6 months of IPTVSup free",
    ("reminder", "subscriber"): "2 days left: up to 6 months of IPTVSup free",
    ("lastcall", "active"): "Last day: your free IPTVSup months end tonight",
    ("lastcall", "churned"): "Last day to come back with up to 6 months free",
    ("lastcall", "subscriber"): "Last day: IPTVSup Black Friday ends tonight",
    # Visitors who asked on the site to be told when the deal starts
    ("launch", "notify"): "It's live: IPTVSup Black Friday, up to 6 months free",
    ("reminder", "notify"): "2 days left: up to 6 months of IPTVSup free",
    ("lastcall", "notify"): "Last day: IPTVSup Black Friday ends tonight",
}

# Line under "Black Friday" in the hero
KICKER = {"teaser": "STARTS THURSDAY", "launch": "STARTS NOW", "reminder": "2 DAYS LEFT", "lastcall": "LAST DAY"}
# Small line under "6 MONTHS FREE"
HERO_NOTE = {
    "teaser": "Thursday, Nov 26 to Monday, Nov 30",
    "launch": "Same prices, no code needed",
    "reminder": "Ends Monday at midnight",
    "lastcall": "Ends tonight at midnight",
}

P = (f'style="font-family: {FONT}; font-size: 18px; line-height: 1.55; color: {TEXT}; '
     f'margin: 0 0 18px 0;"')


def _link(wave: str, audience: str) -> str:
    return f"{LANDING}?utm_source=brevo&utm_medium=email&utm_campaign=bf26_{wave}&utm_content={audience}"


def _button(url: str, label: str) -> str:
    return f"""
    <table cellpadding="0" cellspacing="0" border="0" align="center" style="margin: 10px auto 6px auto;">
      <tr><td align="center" bgcolor="{ORANGE}"
              style="border-radius: 12px; background-color: {ORANGE};
                     background-image: linear-gradient(90deg, #E8413C 0%, #F2892A 100%);">
        <a href="{url}" target="_blank"
           style="display: inline-block; padding: 18px 44px; font-family: {FONT}; font-size: 19px;
                  font-weight: bold; color: #FFFFFF; text-decoration: none; border-radius: 12px;">{label}</a>
      </td></tr>
    </table>"""


def _logo() -> str:
    return f"""
    <tr>
      <td align="center" style="padding: 34px 20px 8px 20px;">
        <a href="https://iptvsup.com" target="_blank" style="text-decoration: none; font-family: {FONT};
           font-size: 34px; font-weight: 800; letter-spacing: -0.5px; line-height: 1;">
          <span style="color: #FFFFFF;">IPTV</span><span style="color: {BLUE};">sup</span></a>
      </td>
    </tr>"""


def _hero(wave: str) -> str:
    return f"""
    <tr>
      <td align="center" bgcolor="#07070C" class="hero"
          style="padding: 34px 20px 38px 20px; text-align: center; background-color: #07070C;
                 background-image: radial-gradient(ellipse at 78% 35%, rgba(255,107,53,0.38) 0%, rgba(0,0,0,0) 55%),
                                   radial-gradient(ellipse at 18% 85%, rgba(59,142,219,0.30) 0%, rgba(0,0,0,0) 50%);">
        <div class="h-bf" style="font-family: {FONT}; font-size: 60px; line-height: 1.05; font-weight: 800;
             color: {ORANGE}; margin: 0;">Black Friday</div>
        <div style="font-family: {FONT}; font-size: 22px; font-weight: 700; letter-spacing: 1px; color: {TEXT};
             margin: 10px 0 28px 0;">{KICKER[wave]}</div>
        <div style="font-family: {FONT}; font-size: 24px; color: {TEXT}; margin: 0 0 4px 0;">Get up to</div>
        <div class="h-big" style="font-family: {FONT}; font-size: 64px; line-height: 1; font-weight: 800;
             letter-spacing: -1px; color: {TEXT}; margin: 0;">6 MONTHS FREE</div>
        <div style="font-family: {FONT}; font-size: 21px; color: {ORANGE}; margin: 14px 0 0 0;">{HERO_NOTE[wave]}</div>
      </td>
    </tr>"""


def _offer_table() -> str:
    rows = [("12 months", "$69.99", "+6 months free", True),
            ("6 months", "$49.99", "+3 months free", False),
            ("3 months", "$34.99", "+1 month free", False)]
    cells = ""
    for plan, price, bonus, top in rows:
        border = ORANGE if top else "#26262E"
        cells += f"""
      <tr><td style="padding: 0 0 10px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="border: 1px solid {border}; border-radius: 12px; background-color: #0E0E14;">
          <tr>
            <td style="padding: 16px 18px; font-family: {FONT}; font-size: 18px; color: {TEXT};">
              <strong>{plan}</strong> <span style="color: {MUTED};">&nbsp;{price}</span></td>
            <td align="right" style="padding: 16px 18px; font-family: {FONT}; font-size: 18px; font-weight: bold;
                color: {ORANGE}; white-space: nowrap;">{bonus}</td>
          </tr>
        </table>
      </td></tr>"""
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 6px 0 18px 0;">{cells}
    </table>"""


def _body(first: str, wave: str, audience: str) -> tuple:
    """Returns (paragraphs above the plans, button label, paragraphs below the button)."""
    if wave == "teaser":
        top = f"""<p {P}>Hi {first}, our best offer of the year starts this <strong>Thursday, November 26</strong>.
        Same prices, no codes, and up to 6 months free on top. It runs until the end of Monday, November 30.</p>"""
        if audience == "active":
            bottom = f"""<p {P}><strong>Thinking of renewing this week? Wait until Thursday.</strong> Your new months,
            plus the free ones, are added to the time you still have left.</p>"""
        else:
            bottom = f"""<p {P}>Want to test it before Thursday? Reply <strong>"test"</strong> and we will set up a free
            trial on your device.</p>"""
        return top, "See the Black Friday deal", bottom
    if wave == "launch":
        if audience == "active":
            top = f"""<p {P}>Hi {first}, Black Friday is live. Renew now and get up to 6 months free on top of your
            plan. Your new months are added to the time you still have left, so renewing early costs you nothing.</p>"""
            bottom = f"""<p {P}>Not sure which plan or how many screens you have? Reply to this email or message us on
            <a href="{WHATSAPP_URL}" style="color: {ORANGE};">WhatsApp</a>.</p>"""
            return top, "Get my free months", bottom
        if audience == "churned":
            top = f"""<p {P}>Hi {first}, it has been a while, so here is our best offer of the year: same prices and
            up to 6 months free. No codes, the free months are added at checkout.</p>"""
            bottom = f"""<p {P}>Your login arrives within 5 to 10 minutes. Want to test it first? Reply
            <strong>"test"</strong> and we will set up a free trial.</p>"""
            return top, "Come back with free months", bottom
        top = f"""<p {P}>Hi {first}, our Black Friday deal is live: same prices, and up to 6 months free on every
        3, 6 and 12 month plan. No code needed.</p>"""
        bottom = f"""<p {P}>25,000+ live channels and 150,000+ movies and series on up to 3 screens. Want to test it
        first? Reply <strong>"test"</strong> for a free trial.</p>"""
        return top, "Get this offer", bottom
    if wave == "reminder":
        top = f"""<p {P}>Hi {first}, a quick reminder: the IPTVSup Black Friday bonus ends on Monday, November 30
        at midnight.</p>"""
        bottom = f"""<p {P}>No code needed, the free months show up under your plan at checkout.</p>"""
        return top, "Get my free months", bottom
    top = f"""<p {P}>Hi {first}, today is the last day. At midnight the free months go away and plans go back to
    normal.</p>"""
    bottom = f"""<p {P}>Questions before you order? Reply to this email or message us on
    <a href="{WHATSAPP_URL}" style="color: {ORANGE};">WhatsApp</a>, we answer fast.</p>"""
    return top, "Claim my free months now", bottom


def get_bf_email(customer_name: str, wave: str, audience: str) -> dict:
    first = customer_name.strip().split()[0].capitalize() if customer_name and customer_name.strip() else "there"
    why = {"subscriber": "you subscribed to IPTVSup updates",
           "notify": "you asked us on iptvsup.com to email you when Black Friday starts"}.get(
        audience, "you have or had an IPTVSup subscription")
    subject = SUBJECTS[(wave, audience)]
    if audience == "notify":
        audience = "subscriber"  # same body as newsletter subscribers
    top, cta, bottom = _body(first, wave, audience)
    small = f'style="font-family: {FONT}; font-size: 13px; line-height: 1.6; color: {MUTED}; margin: 0;"'
    body = f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta name="color-scheme" content="dark">
<meta name="supported-color-schemes" content="dark">
<style>
  @media only screen and (max-width: 620px) {{
    .wrap {{ width: 100% !important; }}
    .pad {{ padding-left: 20px !important; padding-right: 20px !important; }}
    .h-bf {{ font-size: 44px !important; }}
    .h-big {{ font-size: 46px !important; }}
  }}
</style>
</head>
<body style="margin: 0; padding: 0; background-color: {BG};">
<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}" style="background-color: {BG};">
<tr><td align="center">
<table class="wrap" width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}"
       style="max-width: 600px; width: 100%; background-color: {BG};">
  {_logo()}
  {_hero(wave)}
  <tr>
    <td class="pad" style="padding: 32px 40px 8px 40px;">
      {top}
      {_offer_table()}
      {_button(_link(wave, audience), cta)}
      <div style="height: 22px; line-height: 22px;">&nbsp;</div>
      {bottom}
    </td>
  </tr>
  <tr>
    <td class="pad" style="padding: 8px 40px 0 40px;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top: 1px solid #2E2E36;">
        <tr>
          <td style="padding: 22px 0; font-family: {FONT}; font-size: 16px; line-height: 1.5; color: {MUTED};">
            Thanks for reading,<br>IPTVSup Team</td>
          <td align="right" style="padding: 22px 0; font-family: {FONT}; font-size: 16px; line-height: 1.5;">
            <a href="https://iptvsup.com" style="color: {MUTED}; text-decoration: none;">iptvsup.com</a></td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td class="pad" style="padding: 0 40px 34px 40px;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top: 1px solid #1E1E24;">
        <tr><td style="padding-top: 18px;">
          <p {small}>You are receiving this because {why}. Don't want these emails?
          Reply "unsubscribe" and we will remove you.</p>
        </td></tr>
      </table>
    </td>
  </tr>
</table>
</td></tr>
</table>
</body>
</html>"""
    return {"subject": subject, "body": body}
