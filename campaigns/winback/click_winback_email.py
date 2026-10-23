"""
Click Win-Back Campaign — Segmented Email Templates
-----------------------------------------------------
Three variants based on how many times the customer clicked
but didn't complete their purchase.

Segment A (1 click)      : Soft nudge — offer expires in 24h
Segment B (2–3 clicks)   : Warmer — "you kept coming back"
Segment C (4+ clicks)    : Personal — WhatsApp first, something blocked them
"""

CHECKOUT_12M       = "https://www.iptvsup.com/checkout/?add-to-cart=2711&utm_source=brevo&utm_medium=email&utm_campaign=winback"
CHECKOUT_12M_PREM  = "https://www.iptvsup.com/checkout/?add-to-cart=728&utm_source=brevo&utm_medium=email&utm_campaign=winback"
IMAGE_12M          = "https://iptvsup.com/wp-content/uploads/2023/05/4489506467.png"
IMAGE_12M_PREM     = "https://iptvsup.com/wp-content/uploads/2022/10/1-year.webp"
WHATSAPP_LINK      = "https://wa.me/212600974091?text=Hi%2C%20I%27m%20interested%20in%20subscribing%20to%20IPTV%20Sup.%20Can%20you%20help%20me%3F"
LOGO_URL           = "https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"
WEBSITE_URL        = "https://www.iptvsup.com"


def _product_cards_html() -> str:
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 28px;">
        <tr>
            <!-- 12 Months card -->
            <td class="card-cell" width="48%" style="background-color: #f8f9ff; border: 1px solid #dde2f5;
                border-radius: 10px; padding: 20px; vertical-align: top; text-align: center;">

                <!-- Discount badge -->
                <table cellpadding="0" cellspacing="0" style="margin: 0 auto 14px auto;">
                    <tr>
                        <td style="background-color: #c0392b; border-radius: 50px;
                                   padding: 6px 18px; text-align: center;">
                            <span style="font-size: 26px; font-weight: 900; color: #ffffff;
                                         letter-spacing: -0.5px; line-height: 1;">-20%</span>
                        </td>
                    </tr>
                </table>

                <img src="{IMAGE_12M}" alt="12 Months"
                     style="width: 100%; max-width: 130px; margin: 0 auto 12px auto; display: block; border-radius: 6px;">
                <p style="margin: 0 0 4px 0; font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 1px;">12 Months</p>
                <p style="margin: 0 0 14px 0; font-size: 17px; font-weight: bold; color: #1a1a2e;">Standard Plan</p>
                <p style="margin: 0 0 16px 0; font-size: 11px; color: #999;">Applied at checkout — no code needed</p>
                <a href="{CHECKOUT_12M}"
                   style="display: block; background-color: #1a1a2e; color: #ffffff;
                          padding: 13px 0; text-decoration: none; border-radius: 6px;
                          font-weight: bold; font-size: 14px;">
                    Get 12 Months →
                </a>
            </td>

            <td class="card-spacer" width="4%" style="font-size: 0; line-height: 0;">&nbsp;</td>

            <!-- 12 Months Premium card -->
            <td class="card-cell" width="48%" style="background-color: #fff9f0; border: 2px solid #e67e22;
                border-radius: 10px; padding: 20px; vertical-align: top; text-align: center;">

                <!-- Discount badge -->
                <table cellpadding="0" cellspacing="0" style="margin: 0 auto 14px auto;">
                    <tr>
                        <td style="background-color: #e67e22; border-radius: 50px;
                                   padding: 6px 18px; text-align: center;">
                            <span style="font-size: 26px; font-weight: 900; color: #ffffff;
                                         letter-spacing: -0.5px; line-height: 1;">-25%</span>
                        </td>
                    </tr>
                </table>

                <img src="{IMAGE_12M_PREM}" alt="12 Months Premium"
                     style="width: 100%; max-width: 130px; margin: 0 auto 12px auto; display: block; border-radius: 6px;">
                <p style="margin: 0 0 4px 0; font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 1px;">12 Months</p>
                <p style="margin: 0 0 8px 0; font-size: 17px; font-weight: bold; color: #1a1a2e;">Premium Plan</p>
                <p style="margin: 0 0 16px 0; font-size: 12px; color: #27ae60; font-weight: bold;">+ 1 FREE month included</p>
                <a href="{CHECKOUT_12M_PREM}"
                   style="display: block; background-color: #e67e22; color: #ffffff;
                          padding: 13px 0; text-decoration: none; border-radius: 6px;
                          font-weight: bold; font-size: 14px;">
                    Get Premium →
                </a>
            </td>
        </tr>
    </table>
    """


def _base_layout(headline_html: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <style>
        @media only screen and (max-width: 600px) {{
            .email-wrapper  {{ padding: 16px 0 !important; }}
            .email-card     {{ border-radius: 0 !important; }}
            .section-pad    {{ padding-left: 18px !important; padding-right: 18px !important; }}
            .headline-pad   {{ padding: 24px 18px 14px 18px !important; }}
            .body-pad       {{ padding: 20px 18px 8px 18px !important; }}
            .cards-pad      {{ padding: 0 18px 24px 18px !important; }}
            .headline-h1    {{ font-size: 21px !important; }}

            /* Stack product cards vertically */
            .card-cell      {{ display: block !important; width: 100% !important;
                               box-sizing: border-box !important; margin-bottom: 14px !important; }}
            .card-spacer    {{ display: none !important; }}

            /* Countdown boxes */
            .cd-box         {{ width: 48px !important; height: 44px !important; }}
            .cd-num         {{ font-size: 22px !important; }}
            .cd-label       {{ font-size: 9px !important; }}
            .cd-sep         {{ font-size: 20px !important; }}

            /* Footer links — stack them */
            .footer-link    {{ display: block !important; margin: 6px 0 !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f0f0f0;
             font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333;">

<table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0"
       style="background-color: #f0f0f0; padding: 36px 0;">
<tr><td align="center">
<table class="email-card" width="100%" cellpadding="0" cellspacing="0"
       style="max-width: 620px; background-color: #ffffff;
              border-radius: 14px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">

    <!-- HEADER -->
    <tr>
        <td class="section-pad" style="background-color: #0d0d1a; padding: 24px 32px; text-align: center;">
            <a href="{WEBSITE_URL}">
                <img src="{LOGO_URL}" alt="IPTVSup"
                     style="max-height: 56px; max-width: 180px; border: 0; display: block; margin: 0 auto;">
            </a>
        </td>
    </tr>

    <!-- ACCENT LINE -->
    <tr>
        <td style="background: linear-gradient(90deg, #e67e22 0%, #1a1a2e 100%);
                   height: 3px; font-size: 0; line-height: 0;">&nbsp;</td>
    </tr>

    <!-- COUNTDOWN BANNER -->
    <tr>
        <td class="section-pad" style="padding: 20px 32px 8px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="text-align: center; padding-bottom: 12px;">
                        <span style="font-size: 12px; color: #e67e22; letter-spacing: 1.5px;
                                     text-transform: uppercase; font-weight: bold;">
                            ⏳ This offer expires in
                        </span>
                    </td>
                </tr>
                <tr>
                    <td align="center">
                        <table cellpadding="0" cellspacing="0">
                            <tr>
                                <!-- Hours -->
                                <td align="center" style="padding: 0 5px;">
                                    <table cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td class="cd-box" align="center"
                                                style="background-color: #e67e22; border-radius: 8px;
                                                       width: 58px; height: 52px; vertical-align: middle;">
                                                <span class="cd-num" style="font-size: 28px; font-weight: bold;
                                                             color: #ffffff; line-height: 1;">24</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="padding-top: 5px;">
                                                <span class="cd-label" style="font-size: 10px; color: #888;
                                                             letter-spacing: 1px; text-transform: uppercase;">Hours</span>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                                <td class="cd-sep" style="font-size: 26px; font-weight: bold; color: #e67e22;
                                           vertical-align: top; padding-top: 8px;">:</td>
                                <!-- Minutes -->
                                <td align="center" style="padding: 0 5px;">
                                    <table cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td class="cd-box" align="center"
                                                style="background-color: #1a1a2e; border-radius: 8px;
                                                       width: 58px; height: 52px; vertical-align: middle;">
                                                <span class="cd-num" style="font-size: 28px; font-weight: bold;
                                                             color: #ffffff; line-height: 1;">00</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="padding-top: 5px;">
                                                <span class="cd-label" style="font-size: 10px; color: #888;
                                                             letter-spacing: 1px; text-transform: uppercase;">Min</span>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                                <td class="cd-sep" style="font-size: 26px; font-weight: bold; color: #e67e22;
                                           vertical-align: top; padding-top: 8px;">:</td>
                                <!-- Seconds -->
                                <td align="center" style="padding: 0 5px;">
                                    <table cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td class="cd-box" align="center"
                                                style="background-color: #1a1a2e; border-radius: 8px;
                                                       width: 58px; height: 52px; vertical-align: middle;">
                                                <span class="cd-num" style="font-size: 28px; font-weight: bold;
                                                             color: #ffffff; line-height: 1;">00</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="padding-top: 5px;">
                                                <span class="cd-label" style="font-size: 10px; color: #888;
                                                             letter-spacing: 1px; text-transform: uppercase;">Sec</span>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- HEADLINE -->
    {headline_html}

    <!-- BODY -->
    <tr>
        <td class="body-pad" style="padding: 24px 32px 8px 32px;">
            {body_html}
        </td>
    </tr>

    <!-- PRODUCT CARDS -->
    <tr>
        <td class="cards-pad" style="padding: 0 32px 32px 32px;">
            {_product_cards_html()}

            <!-- TRUST LINE -->
            <p style="font-size: 13px; color: #999; text-align: center; margin: 0 0 22px 0;">
                ✓ No contract &nbsp;·&nbsp; ✓ Works on all devices &nbsp;·&nbsp; ✓ 20,000+ channels
            </p>

            <p style="font-size: 15px; line-height: 1.7; margin: 0 0 6px 0;">
                Any questions? Just reply or reach out on
                <a href="{WHATSAPP_LINK}" style="color: #27ae60; font-weight: bold;">WhatsApp</a> — I'll sort it for you.
            </p>
            <p style="font-size: 15px; margin: 0;">– Nathalie</p>
        </td>
    </tr>

    <!-- FOOTER -->
    <tr>
        <td class="section-pad" style="background-color: #0d0d1a; padding: 22px 32px; text-align: center;">
            <p style="margin: 0 0 2px 0; color: #ffffff; font-size: 14px; font-weight: bold;">Nathalie</p>
            <p style="margin: 0 0 14px 0; color: #aab4ff; font-size: 12px;">Customer Service — IPTVSup</p>
            <hr style="border: none; border-top: 1px solid #2d2d5e; margin: 0 0 14px 0;">
            <p style="margin: 0;">
                <a class="footer-link" href="{WEBSITE_URL}" style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 8px;">🌐 iptvsup.com</a>
                <a class="footer-link" href="mailto:contact@iptvsup.com" style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 8px;">✉️ contact@iptvsup.com</a>
                <a class="footer-link" href="{WHATSAPP_LINK}" style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 8px;">💬 WhatsApp</a>
            </p>
            <p style="font-size: 11px; color: #555e8a; margin: 14px 0 0 0;">
                You are receiving this email because you previously had a subscription with IPTV Sup.
            </p>
        </td>
    </tr>

</table>
</td></tr>
</table>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Segment A — 1 click
# ---------------------------------------------------------------------------

def _segment_a(first_name: str) -> dict:
    headline = """
    <tr>
        <td class="headline-pad" style="padding: 28px 32px 14px 32px; text-align: center;">
            <p style="margin: 0 0 6px 0; font-size: 12px; color: #e67e22;
               letter-spacing: 1.5px; text-transform: uppercase; font-weight: bold;">
                ⏳ Limited-Time Offer — Expires in 24 Hours
            </p>
            <h1 class="headline-h1" style="margin: 0; color: #1a1a2e; font-size: 24px; font-weight: bold; line-height: 1.3;">
                Your discount is still waiting
            </h1>
        </td>
    </tr>
    """
    body = f"""
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 14px 0;">Hey {first_name},</p>
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 14px 0;">
            I noticed you checked out our subscription plans but didn't complete your order.
            No worries — I've kept your exclusive discount active for <strong>the next 24 hours</strong>.
        </p>
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 20px 0;">
            Pick the plan that works best for you below — the discount is already applied at checkout,
            no code needed.
        </p>
    """
    return {
        "subject": "Your discount expires in 24 hours — complete your order",
        "body": _base_layout(headline, body),
    }


# ---------------------------------------------------------------------------
# Segment B — 2–3 clicks
# ---------------------------------------------------------------------------

def _segment_b(first_name: str) -> dict:
    headline = """
    <tr>
        <td class="headline-pad" style="padding: 28px 32px 14px 32px; text-align: center;">
            <p style="margin: 0 0 6px 0; font-size: 12px; color: #e67e22;
               letter-spacing: 1.5px; text-transform: uppercase; font-weight: bold;">
                ⏳ Offer Expires in 24 Hours
            </p>
            <h1 class="headline-h1" style="margin: 0; color: #1a1a2e; font-size: 24px; font-weight: bold; line-height: 1.3;">
                You came back — we noticed
            </h1>
        </td>
    </tr>
    """
    body = f"""
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 14px 0;">Hey {first_name},</p>
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 14px 0;">
            You've visited our checkout a couple of times now. Something is holding you back —
            and I want to make sure it's not price.
        </p>
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 14px 0;">
            So I'm making the offer even better: <strong>25% off our Premium 12-month plan + 1 free month</strong>,
            or <strong>20% off the Standard 12-month</strong> — both already applied below.
            This offer is only valid for the next <strong>24 hours</strong>.
        </p>
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 20px 0;">
            If something else is stopping you — a question about the service, a payment issue,
            anything at all — just reply and I'll take care of it personally.
        </p>
    """
    return {
        "subject": "We noticed you came back — here's your best offer yet",
        "body": _base_layout(headline, body),
    }


# ---------------------------------------------------------------------------
# Segment C — 4+ clicks
# ---------------------------------------------------------------------------

def _segment_c(first_name: str) -> dict:
    headline = """
    <tr>
        <td class="headline-pad" style="padding: 28px 32px 14px 32px; text-align: center;">
            <h1 class="headline-h1" style="margin: 0 0 8px 0; color: #1a1a2e; font-size: 24px; font-weight: bold; line-height: 1.3;">
                Something is getting in the way — let us fix it
            </h1>
            <p style="margin: 0; font-size: 15px; color: #666;">We want to make sure you get your subscription today.</p>
        </td>
    </tr>
    """
    body = f"""
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 14px 0;">Hey {first_name},</p>
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 14px 0;">
            I can see you've tried to subscribe several times. That tells me you want this —
            something is just getting in the way, and I'd love to help you sort it out.
        </p>
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 20px 0;">
            Whether it's a payment issue, a question about the service, or anything else —
            reply to this email or reach out on <a href="{WHATSAPP_LINK}" style="color: #25d366; font-weight: bold;">WhatsApp</a>
            and I'll personally get it sorted in minutes.
        </p>
        <p style="font-size: 15px; line-height: 1.7; margin: 0 0 10px 0;">
            Or if you're ready to go right now — your <strong>best discount is below</strong>,
            already applied at checkout, valid for <strong>24 hours</strong>:
        </p>
    """
    return {
        "subject": "We want to help you get this done — 25% off inside",
        "body": _base_layout(headline, body),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def get_click_winback_email(first_name: str, click_count: int) -> dict:
    name = first_name.strip().split()[0] if first_name.strip() else "there"
    if click_count >= 4:
        return _segment_c(name)
    if click_count >= 2:
        return _segment_b(name)
    return _segment_a(name)
