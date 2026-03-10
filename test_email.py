from services.email_service import send_email
from templates.email_templates import get_email_content

# Preview the long-term win-back email (stage 6)
content = get_email_content(
    stage=6,
    customer_name="Mehdi",
    plan="6 Months Premium Subscription"
)

send_email(
    to_email="elyoussefimehdi@gmail.com",
    subject=content["subject"],
    body_html=content["body"]
)
