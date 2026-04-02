"""
Win-Back Campaign — Email Template
------------------------------------
25% discount pre-applied at checkout — valid on 6-month and 12-month plans only.
Includes logo header and offer card for credibility.
Signed by Nathalie.
"""

CHECKOUT_6M  = "https://www.iptvsup.com/checkout/?add-to-cart=723"   # 6 months Premium
CHECKOUT_12M = "https://www.iptvsup.com/checkout/?add-to-cart=728"   # 12 months Premium

WINBACK_SUBJECT = "Your account expired — quick fix (limited)"


def get_winback_email(customer_name: str, plan: str = "") -> dict:
    """
    Returns {'subject': ..., 'body': ...} for the win-back campaign.
    Uses first name only, falls back to 'There'.
    """
    first_name = customer_name.strip().split()[0] if customer_name.strip() else "There"

    body = f"""
    <html>
    <body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif; color: #333;">

    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 30px 0;">
    <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">

        <!-- LOGO HEADER -->
        <tr>
            <td style="background-color: #1a1a2e; padding: 24px; text-align: center;">
                <a href="https://www.iptvsup.com">
                    <img src="https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"
                         alt="IPTVSup" style="max-height: 70px; max-width: 220px;">
                </a>
            </td>
        </tr>

        <!-- HERO BANNER -->
        <tr>
            <td style="background-color: #ffffff; padding: 28px 40px 4px 40px; text-align: center;">
                <p style="margin: 0 0 6px 0; color: #555; font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase;">🎁 Exclusive Reactivation Offer</p>
                <h1 style="margin: 0; color: #e02020; font-size: 30px; font-weight: bold; line-height: 1.3;">
                    🔥 25% Off — Just for You
                </h1>
                <p style="margin: 10px 0 0 0; color: #888; font-size: 14px;">Valid on 6-month &amp; 12-month plans only</p>
            </td>
        </tr>

        <!-- BODY -->
        <tr>
            <td style="padding: 36px 40px;">

                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 16px 0;">
                    Hey {first_name},
                </p>
                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 16px 0;">
                    I noticed your subscription expired recently. I wanted to reach out personally
                    because we've made real improvements since you left — upgraded servers,
                    better stability, and no more buffering issues.
                </p>
                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 28px 0;">
                    To make it easy to come back, I've set aside a <strong>25% reactivation discount</strong>
                    on our longer plans. This is only available to previous customers like you.
                </p>

                <!-- OFFER CARDS -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 28px;">
                    <tr>
                        <!-- 6 months card -->
                        <td width="48%" style="background-color: #f8f9ff; border: 1px solid #dde2f5; border-radius: 8px; padding: 20px; vertical-align: top; text-align: center;">
                            <img src="https://iptvsup.com/wp-content/uploads/2022/10/6-months.webp"
                                 alt="6 Months Premium" style="width: 100%; max-width: 180px; margin-bottom: 14px; display: block; margin-left: auto; margin-right: auto;">
                            <p style="margin: 0 0 4px 0; font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 1px;">6 Months</p>
                            <p style="margin: 0 0 8px 0; font-size: 18px; font-weight: bold; color: #1a1a2e;">Premium Plan</p>
                            <p style="margin: 0 0 16px 0; font-size: 13px; color: #c0392b; font-weight: bold;">25% OFF applied at checkout</p>
                            <a href="{CHECKOUT_6M}"
                               style="display: block; background-color: #1a1a2e; color: white; padding: 11px 0;
                                      text-decoration: none; border-radius: 5px; font-weight: bold;
                                      font-size: 14px; text-align: center;">
                                Get 6 Months
                            </a>
                        </td>
                        <td width="4%"></td>
                        <!-- 12 months card -->
                        <td width="48%" style="background-color: #ffffff; border: 2px solid #1a1a2e; border-radius: 8px; padding: 20px; vertical-align: top; text-align: center;">
                            <img src="https://iptvsup.com/wp-content/uploads/2022/10/1-year.webp"
                                 alt="12 Months Premium" style="width: 100%; max-width: 180px; margin-bottom: 14px; display: block; margin-left: auto; margin-right: auto;">
                            <p style="margin: 0 0 2px 0; font-size: 11px; color: #1a1a2e; text-transform: uppercase; letter-spacing: 1px;">Best Value ★</p>
                            <p style="margin: 0 0 4px 0; font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 1px;">12 Months</p>
                            <p style="margin: 0 0 8px 0; font-size: 18px; font-weight: bold; color: #1a1a2e;">Premium Plan</p>
                            <p style="margin: 0 0 16px 0; font-size: 13px; color: #c0392b; font-weight: bold;">25% OFF + 1 FREE month today</p>
                            <a href="{CHECKOUT_12M}"
                               style="display: block; background-color: #1a1a2e; color: #ffffff; padding: 11px 0;
                                      text-decoration: none; border-radius: 5px; font-weight: bold;
                                      font-size: 14px; text-align: center;">
                                Get 12 Months
                            </a>
                        </td>
                    </tr>
                </table>

                <!-- TRUST LINE -->
                <p style="font-size: 13px; color: #888; text-align: center; margin: 0 0 28px 0;">
                    ✓ No contract &nbsp;·&nbsp; ✓ All devices &nbsp;·&nbsp; ✓ 20,000+ channels
                </p>

                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 8px 0;">
                    If you have any questions, just reply to this email — I read every reply.
                </p>
                <p style="font-size: 15px; margin: 0;">– Nathalie</p>

            </td>
        </tr>

        <!-- FOOTER -->
        <tr>
            <td style="background-color: #1a1a2e; padding: 30px 40px; text-align: center;">

                <!-- Nathalie signature block -->
                <p style="margin: 0 0 2px 0; color: #ffffff; font-size: 15px; font-weight: bold;">Nathalie</p>
                <p style="margin: 0 0 16px 0; color: #aab4ff; font-size: 12px; letter-spacing: 0.5px;">Customer Service — IPTVSup</p>

                <hr style="border: none; border-top: 1px solid #2d2d5e; margin: 0 0 20px 0;">

                <!-- Contact links -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center;">
                            <a href="https://www.iptvsup.com"
                               style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 12px;">
                                🌐 iptvsup.com
                            </a>
                            <a href="mailto:contact@iptvsup.com"
                               style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 12px;">
                                ✉️ contact@iptvsup.com
                            </a>
                            <a href="https://wa.me/message/KYISERSGPOL5K1"
                               style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 12px;">
                                💬 WhatsApp
                            </a>
                        </td>
                    </tr>
                </table>

                <p style="font-size: 11px; color: #555e8a; margin: 20px 0 0 0;">
                    You are receiving this email because you previously had a subscription with IPTV Sup.
                </p>
            </td>
        </tr>

    </table>
    </td></tr>
    </table>

    </body>
    </html>
    """

    return {"subject": WINBACK_SUBJECT, "body": body}
