"""
Win-Back Discount Campaign — Email Template
--------------------------------------------
40% off on 6-month and 12-month plans.
One-time offer for expired subscribers.
"""

CHECKOUT_6M  = "https://whop.com/checkout/plan_3Qnybx8hD2IuR?utm_source=newsletter&utm_medium=email"
CHECKOUT_12M = "https://whop.com/checkout/plan_dQkSO1RvJLALh?utm_source=newsletter&utm_medium=email"

SUBJECT = "A special offer just for you — 40% off to come back"


def get_discount40_email(customer_name: str) -> dict:
    first_name = customer_name.strip().split()[0] if customer_name.strip() else "there"

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
            <td style="background-color: #fff8f0; padding: 32px 40px 8px 40px; text-align: center; border-bottom: 3px solid #e8a020;">
                <p style="margin: 0 0 6px 0; color: #c07010; font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase; font-weight: bold;">Limited Reactivation Offer</p>
                <h1 style="margin: 0; color: #c07010; font-size: 38px; font-weight: bold; line-height: 1.2;">
                    40% Off
                </h1>
                <p style="margin: 8px 0 0 0; color: #555; font-size: 15px;">Our biggest discount — only for previous customers</p>
            </td>
        </tr>

        <!-- BODY -->
        <tr>
            <td style="padding: 36px 40px;">

                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 16px 0;">
                    Hi {first_name},
                </p>
                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 16px 0;">
                    I wanted to personally reach out because your subscription with us has expired.
                    I know things come up, and I don't want price to be the reason you stay away.
                </p>
                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 28px 0;">
                    So I'm making you our <strong>best offer we've ever sent</strong> — <strong>40% off</strong>
                    when you reactivate today. This is going to only a small group of loyal past customers,
                    and it won't be extended again.
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
                            <p style="margin: 0 0 16px 0; font-size: 14px; color: #c07010; font-weight: bold;">40% OFF — applied at checkout</p>
                            <a href="{CHECKOUT_6M}"
                               style="display: block; background-color: #1a1a2e; color: white; padding: 12px 0;
                                      text-decoration: none; border-radius: 5px; font-weight: bold;
                                      font-size: 14px; text-align: center;">
                                Reactivate — 6 Months
                            </a>
                        </td>
                        <td width="4%"></td>
                        <!-- 12 months card -->
                        <td width="48%" style="background-color: #fff8f0; border: 2px solid #e8a020; border-radius: 8px; padding: 20px; vertical-align: top; text-align: center;">
                            <img src="https://iptvsup.com/wp-content/uploads/2022/10/1-year.webp"
                                 alt="12 Months Premium" style="width: 100%; max-width: 180px; margin-bottom: 14px; display: block; margin-left: auto; margin-right: auto;">
                            <p style="margin: 0 0 2px 0; font-size: 11px; color: #c07010; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Best Value ★</p>
                            <p style="margin: 0 0 4px 0; font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 1px;">12 Months</p>
                            <p style="margin: 0 0 8px 0; font-size: 18px; font-weight: bold; color: #1a1a2e;">Premium Plan</p>
                            <p style="margin: 0 0 16px 0; font-size: 14px; color: #c07010; font-weight: bold;">40% OFF + best price per month</p>
                            <a href="{CHECKOUT_12M}"
                               style="display: block; background-color: #c07010; color: #ffffff; padding: 12px 0;
                                      text-decoration: none; border-radius: 5px; font-weight: bold;
                                      font-size: 14px; text-align: center;">
                                Reactivate — 12 Months
                            </a>
                        </td>
                    </tr>
                </table>

                <!-- TRUST LINE -->
                <p style="font-size: 13px; color: #888; text-align: center; margin: 0 0 28px 0;">
                    ✓ No contract &nbsp;·&nbsp; ✓ All devices &nbsp;·&nbsp; ✓ 20,000+ channels &nbsp;·&nbsp; ✓ Instant activation
                </p>

                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 8px 0;">
                    Just reply to this email if you have any questions — I'll take care of you personally.
                </p>
                <p style="font-size: 15px; margin: 0;">– Nathalie</p>

            </td>
        </tr>

        <!-- FOOTER -->
        <tr>
            <td style="background-color: #1a1a2e; padding: 30px 40px; text-align: center;">

                <p style="margin: 0 0 2px 0; color: #ffffff; font-size: 15px; font-weight: bold;">Nathalie</p>
                <p style="margin: 0 0 16px 0; color: #aab4ff; font-size: 12px; letter-spacing: 0.5px;">Customer Service — IPTVSup</p>

                <hr style="border: none; border-top: 1px solid #2d2d5e; margin: 0 0 20px 0;">

                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center;">
                            <a href="https://www.iptvsup.com"
                               style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 12px;">
                                iptvsup.com
                            </a>
                            <a href="mailto:contact@iptvsup.com"
                               style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 12px;">
                                contact@iptvsup.com
                            </a>
                            <a href="https://wa.me/message/KYISERSGPOL5K1"
                               style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 12px;">
                                WhatsApp
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

    return {"subject": SUBJECT, "body": body}
