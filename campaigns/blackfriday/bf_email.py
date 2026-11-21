"""
Black Friday 2026 emails: bonus months, prices unchanged
---------------------------------------------------------
  3 months + 1 free, 6 months + 2 free, 12 months + 6 free (Nov 26 to Nov 30)

Waves:     teaser (Tue Nov 24), launch (Fri Nov 27), lastcall (Mon Nov 30)
           (the Nov 29 reminder was dropped: max 3 Black Friday emails per person)
Audiences: active      current customers (tracker: active / expires soon)
           churned     former customers (tracker: expired / churned)
           subscriber  newsletter contacts who never bought
The banner is HTML (no big image) so it shows even when images are blocked.
"""

LANDING = "https://iptvsup.com/black-friday-iptv-deal/"
WHATSAPP_URL = "https://wa.me/message/KYISERSGPOL5K1"
LOGO_URL = "https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"

GOLD = "#f5c451"
INK = "#0b0b0d"

SUBJECTS = {
    ("teaser", "active"): "Black Friday starts Thursday: up to 6 free months on your IPTVSup plan",
    ("teaser", "churned"): "Black Friday starts Thursday: up to 6 months of IPTVSup free",
    ("teaser", "subscriber"): "Black Friday starts Thursday: up to 6 months of IPTVSup free",
    ("launch", "active"): "Black Friday: up to 6 free months on your IPTVSup plan",
    ("launch", "churned"): "Come back to IPTVSup with up to 6 months free",
    ("launch", "subscriber"): "IPTVSup Black Friday: pay for 12 months, watch for 18",
    ("reminder", "active"): "2 days left for your free IPTVSup months",
    ("reminder", "churned"): "2 days left: up to 6 months of IPTVSup free",
    ("reminder", "subscriber"): "2 days left: 18 months of IPTVSup for the price of 12",
    ("lastcall", "active"): "Last day: your free IPTVSup months end tonight",
    ("lastcall", "churned"): "Last day to come back with up to 6 months free",
    ("lastcall", "subscriber"): "Last day: IPTVSup Black Friday ends tonight",
    # Visitors who asked on the site to be told when the deal starts
    ("launch", "notify"): "It's live: IPTVSup Black Friday, up to 6 months free",
    ("reminder", "notify"): "2 days left: 18 months of IPTVSup for the price of 12",
    ("lastcall", "notify"): "Last day: IPTVSup Black Friday ends tonight",
}

P = 'style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.65; color: #333333; margin: 0 0 16px 0;"'


def _link(wave: str, audience: str) -> str:
    return f"{LANDING}?utm_source=brevo&utm_medium=email&utm_campaign=bf26_{wave}&utm_content={audience}"


def _button(url: str, label: str) -> str:
    return f"""
    <table cellpadding="0" cellspacing="0" border="0" align="center" style="margin: 8px auto 4px auto;">
      <tr><td align="center" bgcolor="{GOLD}" style="border-radius: 8px;">
        <a href="{url}" target="_blank"
           style="display: inline-block; padding: 14px 30px; font-family: Arial, sans-serif; font-size: 16px;
                  font-weight: bold; color: #111111; text-decoration: none; border-radius: 8px;">{label}</a>
      </td></tr>
    </table>"""


def _banner(wave: str) -> str:
    kicker = {"teaser": "BLACK FRIDAY STARTS THURSDAY", "launch": "BLACK FRIDAY",
              "reminder": "2 DAYS LEFT", "lastcall": "LAST DAY"}[wave]
    sub = ("Same prices, free months on top. Thursday, November 26 to Monday, November 30."
           if wave == "teaser" else "Same prices, free months added automatically. Ends Monday, November 30.")
    return f"""
    <tr>
      <td bgcolor="{INK}" align="center" style="background-color: {INK}; padding: 20px 30px 26px 30px; text-align: center;">
        <a href="https://iptvsup.com"><img src="{LOGO_URL}" alt="IPTVSup" width="72"
           style="width: 72px; max-width: 72px; height: auto; border: 0; display: inline-block; margin-bottom: 12px;"></a>
        <div style="font-family: Arial, sans-serif; font-size: 13px; font-weight: bold; letter-spacing: 5px; color: {GOLD}; margin: 0 0 10px 0;">{kicker}</div>
        <div style="font-family: Arial, sans-serif; font-size: 28px; line-height: 1.25; font-weight: bold; color: #ffffff; margin: 0 0 6px 0;">
          Pay for 12 months.<br><span style="color: {GOLD};">Watch for 18.</span>
        </div>
        <div style="font-family: Arial, sans-serif; font-size: 15px; line-height: 1.5; color: #d8d4c8; margin: 0;">
          {sub}
        </div>
      </td>
    </tr>"""


def _offer_table() -> str:
    rows = [("3 months", "+1 free", "4 months for $34.99"),
            ("6 months", "+2 free", "8 months for $49.99"),
            ("12 months", "+6 free", "18 months for $69.99")]
    cells = "".join(f"""
      <tr>
        <td style="padding: 10px 12px; border-bottom: 1px solid #eeeeee; font-family: Arial, sans-serif; font-size: 15px; color: #333333;">{a}</td>
        <td style="padding: 10px 12px; border-bottom: 1px solid #eeeeee; font-family: Arial, sans-serif; font-size: 15px; font-weight: bold; color: #b8860b;">{b}</td>
        <td style="padding: 10px 12px; border-bottom: 1px solid #eeeeee; font-family: Arial, sans-serif; font-size: 15px; color: #333333; text-align: right;">{c}</td>
      </tr>""" for a, b, c in rows)
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 20px 0; border: 1px solid #eeeeee; border-radius: 8px;">
      {cells}
    </table>"""


def _body(first: str, wave: str, audience: str) -> str:
    url = _link(wave, audience)
    if wave == "teaser":
        intro = f"""<p {P}>Hi {first},</p>
        <p {P}>A heads-up before the busiest week of the year: our Black Friday deal starts this <strong>Thursday,
        November 26</strong> and runs until the end of Monday, November 30. No discount codes: our prices stay the same,
        and you get free months on top.</p>"""
        if audience == "active":
            outro = f"""<p {P}><strong>Thinking of renewing this week? Wait until Thursday.</strong> Your new months are added to
            the time you still have left, plus the bonus, so renewing during the sale costs you nothing.</p>
            <p {P}>Not sure which plan or how many screens you have? Reply to this email and we will check for you.</p>"""
        else:
            outro = f"""<p {P}>Works on the TV, stick or phone you already have, on up to 3 screens, and your login arrives
            within 5 to 10 minutes of ordering. Want to test it before Thursday? Reply <strong>"test"</strong> and we will
            set up a free trial.</p>"""
        return (intro + _offer_table() + _button(url, "See the Black Friday deal")
                + '<div style="height: 18px;"></div>' + outro)
    if wave == "launch":
        if audience == "active":
            intro = f"""<p {P}>Hi {first},</p>
            <p {P}>For Black Friday we kept our prices the same and added free months instead. Choose your next plan
            before Monday night and the bonus months are added on top. Your current plan keeps running: the new months
            are added to the time you still have left, so renewing early costs you nothing.</p>"""
            outro = f"""<p {P}>Not sure which plan or how many screens you have now? Reply to this email or message us on
            <a href="{WHATSAPP_URL}" style="color: #b8860b;">WhatsApp</a> and we will sort it out for you.</p>"""
            cta = "Get my free months"
        elif audience == "churned":
            intro = f"""<p {P}>Hi {first},</p>
            <p {P}>It has been a while, so here is our best offer of the year. No discount codes this time: same prices,
            and up to 6 months free on top:</p>"""
            outro = f"""<p {P}>Your login arrives within 5 to 10 minutes of payment and works on the TV, stick or phone you
            already have. Want to test it first? Reply <strong>"test"</strong> and we will set up a free trial.</p>"""
            cta = "Come back with free months"
        else:
            intro = f"""<p {P}>Hi {first},</p>
            <p {P}>Our Black Friday deal is live: same prices, and free months added to every 3, 6 and 12 month plan:</p>"""
            outro = f"""<p {P}>25,000+ live channels, 150,000+ movies and series, on up to 3 screens. Your login arrives within
            5 to 10 minutes. Want to test it first? Reply <strong>"test"</strong> and we will set up a free trial.</p>"""
            cta = "See the Black Friday deal"
    elif wave == "reminder":
        intro = f"""<p {P}>Hi {first},</p>
        <p {P}>A quick reminder: the IPTVSup Black Friday bonus ends on Monday, November 30 at midnight.</p>"""
        if audience == "active":
            intro += f"""<p {P}>Your plan does not need to run out first: the new months are added to the time you still have left.</p>"""
        outro = f"""<p {P}>The 12 month plan works out to $3.89 a month with the bonus. No code needed, the free months
        show up under your plan at checkout.</p>"""
        cta = "Get my free months"
    else:
        intro = f"""<p {P}>Hi {first},</p>
        <p {P}>Today is the last day. At midnight tonight the free months go away and plans go back to normal terms.</p>"""
        outro = f"""<p {P}>Questions before you order? Reply to this email or message us on
        <a href="{WHATSAPP_URL}" style="color: #b8860b;">WhatsApp</a>, we answer fast.</p>"""
        cta = "Claim my free months now"
    return intro + _offer_table() + _button(url, cta) + '<div style="height: 18px;"></div>' + outro


def get_bf_email(customer_name: str, wave: str, audience: str) -> dict:
    first = customer_name.strip().split()[0].capitalize() if customer_name and customer_name.strip() else "there"
    small = 'style="font-family: Arial, sans-serif; font-size: 12px; line-height: 1.6; color: #999999; margin: 0;"'
    why = {"subscriber": "you subscribed to IPTVSup updates",
           "notify": "you asked us on iptvsup.com to email you when Black Friday starts"}.get(
        audience, "you have or had an IPTVSup subscription")
    subject = SUBJECTS[(wave, audience)]
    if audience == "notify":
        audience = "subscriber"  # same body as newsletter subscribers
    body = f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<style>
  @media only screen and (max-width: 620px) {{
    .wrap {{ width: 100% !important; }}
    .pad {{ padding: 26px 20px !important; }}
  }}
</style>
</head>
<body style="margin: 0; padding: 0; background-color: #f0f2f5;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f0f2f5; padding: 26px 0;">
<tr><td align="center">
<table class="wrap" width="600" cellpadding="0" cellspacing="0" border="0"
       style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 12px; overflow: hidden;">
  {_banner(wave)}
  <tr>
    <td class="pad" style="padding: 32px 40px 12px 40px;">
      {_body(first, wave, audience)}
      <p style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.65; color: #333333; margin: 22px 0 6px 0;">
        IPTVSup Team</p>
    </td>
  </tr>
  <tr>
    <td style="background-color: #f7f7f9; padding: 16px 30px; text-align: center;">
      <p {small}><a href="https://iptvsup.com" style="color: {INK}; font-weight: bold; text-decoration: none;">iptvsup.com</a></p>
      <p {small}>You are receiving this because {why}.
      Don't want these emails? Reply "unsubscribe" and we will remove you.</p>
    </td>
  </tr>
</table>
</td></tr>
</table>
</body>
</html>"""
    return {"subject": subject, "body": body}
