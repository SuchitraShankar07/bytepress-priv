# src/mailer/sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Toggle between mock SMTP (local server) and real Gmail
USE_MOCK_SMTP = os.getenv("USE_MOCK_SMTP", "1") == "1"

def send_email(recipient: str, subject: str, html_content: str):
    """
    Sends an email using SMTP with HTML content.
    - If USE_MOCK_SMTP=True, sends to local DebuggingServer AND prints a clean preview.
    - If USE_MOCK_SMTP=False, sends via real SMTP (Gmail).
    """
    sender_email = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
    sender_password = os.getenv("SENDER_PASSWORD", "your_app_password")

    # Construct MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient
    msg.attach(MIMEText(html_content, "html"))

    if USE_MOCK_SMTP:
        # ✅ Print nicely in Python
        print(f"\n[MOCK SMTP] --- Email Preview ---")
        print(f"From: {sender_email}")
        print(f"To: {recipient}")
        print(f"Subject: {subject}\n")
        print(html_content)
        print("[MOCK SMTP] --- End Email ---\n")

        # ✅ Send to local DebuggingServer so it prints there too
        smtp_server = "localhost"
        smtp_port = 1025

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(sender_email, recipient, msg.as_string())

        print(f"✅ Email sent to local DebuggingServer ({recipient})")
        return

    # Real Gmail SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())

    print(f"✅ Digest sent to {recipient} (REAL)")

