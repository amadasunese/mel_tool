import os
import smtplib
from email.message import EmailMessage
from flask import url_for



def send_contact_email(name: str, sender_email: str, subject: str, message: str) -> None:
    """
    Sends a contact email to your admin/support inbox using SMTP credentials from env vars.

    Required env vars:
    - MAIL_HOST
    - MAIL_PORT (default 587)
    - MAIL_USERNAME
    - MAIL_PASSWORD
    - MAIL_TO (defaults to MAIL_USERNAME)
    - MAIL_USE_TLS (default true)
    """

    mail_host = os.getenv("MAIL_HOST", "").strip()
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    mail_user = os.getenv("MAIL_USERNAME", "").strip()
    mail_pass = os.getenv("MAIL_PASSWORD", "").strip()
    mail_use_tls = os.getenv("MAIL_USE_TLS", "true").lower() == "true"

    # Who receives contact form messages
    mail_to = os.getenv("MAIL_TO", mail_user).strip()

    if not mail_host or not mail_user or not mail_pass or not mail_to:
        raise RuntimeError("Email is not configured. Set MAIL_HOST, MAIL_USERNAME, MAIL_PASSWORD, MAIL_TO.")

    email_msg = EmailMessage()
    email_msg["Subject"] = f"[Contact] {subject}".strip()
    email_msg["From"] = mail_user
    email_msg["To"] = mail_to
    email_msg["Reply-To"] = sender_email

    body = f"""New contact form submission:

Name: {name}
Email: {sender_email}
Subject: {subject}

Message:
{message}
""".strip()

    email_msg.set_content(body)

    with smtplib.SMTP(mail_host, mail_port, timeout=20) as smtp:
        # If you want verbose SMTP debugging, set MAIL_DEBUG=true
        if os.getenv("MAIL_DEBUG", "false").lower() == "true":
            smtp.set_debuglevel(1)

        if mail_use_tls:
            smtp.starttls()

        smtp.login(mail_user, mail_pass)
        smtp.send_message(email_msg)





