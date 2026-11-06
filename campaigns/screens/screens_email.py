"""
Extra screens announcement (Nov 2026)
-------------------------------------
Two versions:
  - "active":  current customers, reply or WhatsApp to add a screen
  - "expired": recently expired customers, pick a plan with 1-3 screens
The banner is HTML (no big image) so it shows even when images are blocked.
"""

PLANS_URL = "https://iptvsup.com/iptv-plans/?utm_source=brevo&utm_medium=email&utm_campaign=screens_nov26"
WHATSAPP_URL = "https://wa.me/message/KYISERSGPOL5K1"
LOGO_URL = "https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"

SUBJECTS = {
    "active": "You can now watch IPTVSup on 2 or 3 TVs",
    "expired": "Your IPTVSup plan, now for the whole family",
}

ORANGE = "#FF6B35"
NAVY = "#1a1a2e"


def _button(url: str, label: str) -> str:
    return f"""
    <table cellpadding="0" cellspacing="0" border="0" align="center" style="margin: 8px auto 4px auto;">
      <tr><td align="center" bgcolor="{ORANGE}" style="border-radius: 8px;">
        <a href="{url}" target="_blank"
           style="display: inline-block; padding: 14px 30px; font-family: Arial, sans-serif; font-size: 16px;
                  font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 8px;">{label}</a>
      </td></tr>
    </table>"""


def _banner() -> str:
    return f"""
    <tr>
      <td bgcolor="{NAVY}" align="center"
          style="background-color: {NAVY}; background-image: linear-gradient(135deg, #1a1a2e 0%, #2b1d3a 60%, #4a2333 100%);
                 padding: 26px 30px 34px 30px; text-align: center;">
        <a href="https://iptvsup.com"><img src="{LOGO_URL}" alt="IPTVSup" width="170"
           style="max-width: 170px; height: auto; border: 0; display: inline-block; margin-bottom: 22px;"></a>
        <div style="font-size: 40px; line-height: 1; letter-spacing: 10px; margin: 0 0 16px 0;">📺📺📺</div>
        <div style="font-family: Arial, sans-serif; font-size: 28px; line-height: 1.25; font-weight: bold; color: #ffffff; margin: 0 0 10px 0;">
          Now on up to 3 TVs at once
        </div>
        <div style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.5; color: #f3d9cf; margin: 0;">
          One subscription for the whole home, with extra screens at
          <span style="color: {ORANGE}; font-weight: bold;">up to 20% off</span>
        </div>
      </td>
    </tr>"""


def _body(first_name: str, audience: str) -> str:
    p = 'style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.65; color: #333333; margin: 0 0 16px 0;"'
    if audience == "active":
        return f"""
        <p {p}>Hi {first_name},</p>
        <p {p}>Good news: your IPTVSup subscription can now cover more than one TV. Watch on 2 or 3 screens at the same time,
        so everyone at home can enjoy their own channel, and get the extra screens at up to 20% off.</p>
        <p {p}>Want it? Just reply <strong>"2 screens"</strong> or <strong>"3 screens"</strong> to this email, or message us on WhatsApp,
        and we will add it to your account.</p>
        {_button(WHATSAPP_URL, "Add a screen on WhatsApp")}
        """
    return f"""
        <p {p}>Hi {first_name},</p>
        <p {p}>Your IPTVSup subscription has ended, so here is what is new: you can now watch on up to 3 TVs at the same time,
        with extra screens at up to 20% off. Plans start at $5 a month on the 12-month plan.</p>
        <p {p}>Pick your plan and number of screens in a couple of clicks. Your login arrives within 5 to 10 minutes.</p>
        {_button(PLANS_URL, "See plans and screens")}
        """


def get_screens_email(customer_name: str, audience: str) -> dict:
    """audience: 'active' or 'expired'"""
    first_name = customer_name.strip().split()[0].capitalize() if customer_name and customer_name.strip() else "there"
    small = 'style="font-family: Arial, sans-serif; font-size: 12px; line-height: 1.6; color: #999999; margin: 0;"'
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
  {_banner()}
  <tr>
    <td class="pad" style="padding: 32px 40px 12px 40px;">
      {_body(first_name, audience)}
      <p style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.65; color: #333333; margin: 22px 0 6px 0;">
        IPTVSup Team</p>
    </td>
  </tr>
  <tr>
    <td style="background-color: #f7f7f9; padding: 16px 30px; text-align: center;">
      <p {small}><a href="https://iptvsup.com" style="color: {NAVY}; font-weight: bold; text-decoration: none;">iptvsup.com</a></p>
      <p {small}>You are receiving this because you have or had an IPTVSup subscription.
      Don't want these updates? Reply "unsubscribe" and we will remove you.</p>
    </td>
  </tr>
</table>
</td></tr>
</table>
</body>
</html>"""
    return {"subject": SUBJECTS[audience], "body": body}
