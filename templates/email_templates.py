"""
Email Templates
---------------
All email subject lines and body content live here.
To update copy, edit this file only — no need to touch any other file.

Stages:
    1 → 7 days before expiry
    2 → 3 days before expiry
    3 → 1 day before expiry
    4 → already expired
"""

from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Plan → Checkout URL mapping
# To add or change a link, edit this dictionary only.
# Matching is case-insensitive and checks if the key appears in the plan name.
# ---------------------------------------------------------------------------

PLAN_LINKS = {
    "1 month premium":  "https://www.iptvsup.com/checkout/?add-to-cart=714",
    "3 months premium": "https://www.iptvsup.com/checkout/?add-to-cart=719",
    "6 months premium": "https://www.iptvsup.com/checkout/?add-to-cart=723",
    "12 months premium":"https://www.iptvsup.com/checkout/?add-to-cart=728",
    "1 month":          "https://www.iptvsup.com/checkout/?add-to-cart=2708",
    "3 months":         "https://www.iptvsup.com/checkout/?add-to-cart=2709",
    "6 months":         "https://www.iptvsup.com/checkout/?add-to-cart=2710",
    "12 months":        "https://www.iptvsup.com/checkout/?add-to-cart=2711",
}

# Fallback if no plan matches
DEFAULT_LINK = "https://www.iptvsup.com"


def get_plan_link(plan: str) -> str:
    """
    Matches the plan string from the sheet to a checkout URL.
    Premium plans are checked first so '1 Month Premium' doesn't
    accidentally match the plain '1 Month' entry.
    """
    plan_lower = plan.lower()
    for key, url in PLAN_LINKS.items():
        if key in plan_lower:
            return url
    logger.warning(f"No checkout link found for plan: '{plan}' — using default link")
    return DEFAULT_LINK


def _base_html(customer_name: str, headline: str, body_paragraphs: list[str], cta_text: str, cta_url: str) -> str:
    """
    Builds a clean, consistent HTML email layout.
    All templates share this same structure so the emails look uniform.
    """
    name_display = customer_name if customer_name else "there"
    paragraphs_html = "".join(f"<p>{p}</p>" for p in body_paragraphs)

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 0; color: #333;">

        <!-- Header with logo -->
        <div style="padding: 20px; text-align: center; border-bottom: 1px solid #eeeeee;">
            <a href="https://www.iptvsup.com">
                <img src="https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"
                     alt="IPTVSup" style="max-height: 100px; max-width: 300px;">
            </a>
        </div>

        <!-- Email body -->
        <div style="padding: 30px 20px;">
            <h2 style="color: #1a1a2e;">{headline}</h2>
            <p>Hi {name_display},</p>
            {paragraphs_html}
            <div style="margin: 30px 0;">
                <a href="{cta_url}" style="background-color: #1a1a2e; color: white; padding: 12px 24px;
                   text-decoration: none; border-radius: 5px; font-weight: bold;">
                    {cta_text}
                </a>
            </div>
            <p style="font-size: 12px; color: #999;">
                If you have any questions, reply to this email and we will get back to you.
            </p>
            <p>Best regards,<br><strong>The IPTVSup Team</strong></p>
        </div>

        <!-- Footer with website link -->
        <div style="background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; color: #999;">
            <a href="https://www.iptvsup.com" style="color: #1a1a2e; text-decoration: none; font-weight: bold;">
                www.iptvsup.com
            </a>
            <br><br>
            You are receiving this email because you have an active or recent subscription with IPTV Sup.
        </div>

    </body>
    </html>
    """


# ---------------------------------------------------------------------------
# STAGE 1 — 7 days before expiry
# ---------------------------------------------------------------------------

def _stage1_content(customer_name: str, plan: str) -> dict:
    return {
        "subject": "Your IPTV Sup subscription expires in 7 days",
        "body": _base_html(
            customer_name=customer_name,
            headline="Your subscription is expiring soon",
            body_paragraphs=[
                f"Your <strong>{plan}</strong> will expire in <strong>7 days</strong>.",
                "We want to make sure you don't lose access to all the channels and features you rely on.",
                "Renew now to keep everything running without interruption.",
            ],
            cta_text="Renew My Subscription",
            cta_url=get_plan_link(plan)
        )
    }


# ---------------------------------------------------------------------------
# STAGE 2 — 3 days before expiry
# ---------------------------------------------------------------------------

def _stage2_content(customer_name: str, plan: str) -> dict:
    return {
        "subject": "3 days left on your IPTV Sup subscription",
        "body": _base_html(
            customer_name=customer_name,
            headline="Only 3 days left",
            body_paragraphs=[
                f"Your <strong>{plan}</strong> expires in <strong>3 days</strong>.",
                "After expiry, you will lose access to your channels immediately.",
                "Don't let your subscription lapse — renew today and stay uninterrupted.",
            ],
            cta_text="Renew Now",
            cta_url=get_plan_link(plan)
        )
    }


# ---------------------------------------------------------------------------
# STAGE 3 — 1 day before expiry
# ---------------------------------------------------------------------------

def _stage3_content(customer_name: str, plan: str) -> dict:
    return {
        "subject": "Final reminder: Your IPTV Sup subscription expires tomorrow",
        "body": _base_html(
            customer_name=customer_name,
            headline="Last chance — expires tomorrow",
            body_paragraphs=[
                f"Your <strong>{plan}</strong> expires <strong>tomorrow</strong>.",
                "This is your final reminder. After tomorrow, your access will be suspended.",
                "Renew right now to avoid any disruption to your service.",
            ],
            cta_text="Renew Before It Expires",
            cta_url=get_plan_link(plan)
        )
    }


# ---------------------------------------------------------------------------
# STAGE 4 — Already expired
# ---------------------------------------------------------------------------

def _stage4_content(customer_name: str, plan: str) -> dict:
    return {
        "subject": "Your IPTV Sup subscription has expired",
        "body": _base_html(
            customer_name=customer_name,
            headline="Your subscription has expired",
            body_paragraphs=[
                f"Your <strong>{plan}</strong> has expired and your access has been suspended.",
                "We would love to have you back. Renew your subscription to restore full access immediately.",
                "If you have any questions or need help choosing a plan, just reply to this email.",
            ],
            cta_text="Reactivate My Subscription",
            cta_url=get_plan_link(plan)
        )
    }


# ---------------------------------------------------------------------------
# STAGE 5 — Win-back (expired 31–90 days ago)
# ---------------------------------------------------------------------------

def _stage5_content(customer_name: str, plan: str) -> dict:
    return {
        "subject": "A special offer just for you — come back to IPTV Sup",
        "body": _base_html(
            customer_name=customer_name,
            headline="We'd love to have you back",
            body_paragraphs=[
                f"It's been a while since your <strong>{plan}</strong> expired and we miss having you.",
                "As a thank you for being a previous customer, we are offering you an exclusive <strong>15% discount</strong> on any plan.",
                "Use code <strong style='font-size: 18px; color: #1a1a2e;'>RNW15S</strong> at checkout — this offer is just for you.",
            ],
            cta_text="Claim My 15% Discount",
            cta_url=get_plan_link(plan)
        )
    }


# ---------------------------------------------------------------------------
# STAGE 6 — Long-term win-back (expired 90+ days ago)
# ---------------------------------------------------------------------------

def _stage6_content(customer_name: str, plan: str) -> dict:
    return {
        "subject": "Are you still paying too much for TV?",
        "body": _base_html(
            customer_name=customer_name,
            headline="Just a honest message from us",
            body_paragraphs=[
                "We are not going to pretend this is just a routine email.",
                "You subscribed to IPTV Sup before and we genuinely want you to know what you are missing — not to sell you something, but because we think it matters.",
                "Netflix charges you more every year for less content. Cable companies lock you into contracts and bill you for channels you never watch. You already know this.",
                "With <strong>IPTVSup</strong> you get thousands of live channels, sports, movies and shows — for a fraction of the price, no contract, cancel anytime.",
                "Because you were with us before, we want to offer you <strong>20% off</strong> to come back. Use code <strong style='font-size: 18px; color: #1a1a2e;'>RENEW20</strong> at checkout.",
                "If you have any questions or want to know what has changed since you left, just reply to this email. We read every reply.",
            ],
            cta_text="Come Back — 20% Off",
            cta_url=get_plan_link(plan)
        )
    }


# ---------------------------------------------------------------------------
# Main function — call this from subscription_checker.py
# ---------------------------------------------------------------------------

STAGE_FUNCTIONS = {
    1: _stage1_content,
    2: _stage2_content,
    3: _stage3_content,
    4: _stage4_content,
    5: _stage5_content,
    6: _stage6_content,
}


def get_email_content(stage: int, customer_name: str, plan: str) -> dict | None:
    """
    Returns a dict with 'subject' and 'body' for the given stage and plan.
    Returns None if the stage is not recognised.

    Usage:
        content = get_email_content(stage=1, customer_name="John", plan="6 Months Premium Subscription")
        subject = content["subject"]
        body    = content["body"]
    """
    fn = STAGE_FUNCTIONS.get(stage)

    if fn is None:
        logger.warning(f"No template found for stage {stage}")
        return None

    return fn(customer_name=customer_name, plan=plan)
