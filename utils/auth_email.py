import os
import smtplib
from email.message import EmailMessage
from flask import url_for







def _smtp_send(to_email: str, subject: str, body: str) -> None:
    mail_host = os.getenv("MAIL_HOST", "")
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    mail_user = os.getenv("MAIL_USERNAME", "")
    mail_pass = os.getenv("MAIL_PASSWORD", "")
    mail_use_tls = os.getenv("MAIL_USE_TLS", "true").lower() == "true"

    if not mail_host or not mail_user or not mail_pass:
        raise RuntimeError("Email not configured. Set MAIL_HOST, MAIL_USERNAME, MAIL_PASSWORD.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = mail_user
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(mail_host, mail_port, timeout=20) as smtp:
        if mail_use_tls:
            smtp.starttls()
        smtp.login(mail_user, mail_pass)
        smtp.send_message(msg)

def send_verification_email(user_email: str, token: str) -> None:
    link = url_for("auth.verify_email", token=token, _external=True)
    subject = "Verify your email"
    body = f"""Hello,

Please verify your email to activate your account:

{link}

If you did not create this account, you can ignore this email.
"""
    _smtp_send(user_email, subject, body)

def send_password_reset_email(user_email: str, token: str) -> None:
    link = url_for("auth.reset_password", token=token, _external=True)
    subject = "Password reset request"
    body = f"""Hello,

We received a password reset request for your account.

Reset your password here:
{link}

If you did not request this, ignore this email.
"""
    _smtp_send(user_email, subject, body)