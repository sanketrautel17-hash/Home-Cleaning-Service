import os
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from commons.logger import logger

load_dotenv()

log = logger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# Match keys from .env
SMTP_USER = os.getenv("gmail_user")
SMTP_PASSWORD = os.getenv("gmail_app_password")

# Frontend URL - verify usually matches current running port
# Using 5174 as per recent context
FRONTEND_URL = "http://localhost:5174"


async def send_email(to_email: str, subject: str, body: str):
    """
    Send an email using Gmail SMTP.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        log.warning("Email credentials not set. Skipping email sending.")
        return

    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=False,
            start_tls=True,
        )
        log.info(f"Email sent to {to_email}")
    except Exception as e:
        log.error(f"Failed to send email to {to_email}: {str(e)}")
        # We catch exceptions so we don't crash the main flow if email fails


async def send_verification_link(to_email: str, token: str):
    """
    Send verification email with link.
    """
    link = f"{FRONTEND_URL}/verify-email?token={token}"
    subject = "Verify your email - Home Cleaning Service"
    body = f"""
Hello,

Thank you for registering with Home Cleaning Service. 
Please click the link below to verify your email address and activate your account:

{link}

If you did not create an account, please ignore this email.

Best regards,
Home Cleaning Team
"""
    await send_email(to_email, subject, body)
