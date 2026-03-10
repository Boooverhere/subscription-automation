import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.logger import get_logger
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, SMTP_LOGIN, SENDER_NAME, SMTP_HOST, SMTP_PORT

logger = get_logger(__name__)


def send_email(to_email: str, subject: str, body_html: str) -> bool:
    """
    Sends an HTML email via Gmail SMTP.

    Returns True if sent successfully, False if it failed.
    We return a boolean instead of raising an exception so that
    one failed email doesn't stop the entire automation run.
    """

    # --- Build the email message ---
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{SENDER_NAME} <{GMAIL_ADDRESS}>"
    msg["To"]      = to_email

    # Attach the HTML body
    msg.attach(MIMEText(body_html, "html"))

    # --- Connect and send ---
    # Port 465 uses SSL from the start (SMTP_SSL)
    # Port 587 uses STARTTLS (plain connection upgraded to encrypted)
    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_LOGIN, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(SMTP_LOGIN, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())

        logger.info(f"Email sent → {to_email} | Subject: {subject}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("Authentication failed. Check your email address and password in .env")
        return False

    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
