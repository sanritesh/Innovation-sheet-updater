#!/usr/bin/env python3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

def send_notification():
    # Email configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    # Email content
    sender_email = f"Daily Innovation Bot <{smtp_username}>" if smtp_username else "Adtech Quality <ritesh.sanjay@timesinternet.in>"
    recipients = os.getenv('EMAIL_RECIPIENTS', "colombia.opsqc@timesinternet.in,ritesh.sanjay@timesinternet.in").split(',')

    # Get dates
    current_date = datetime.now().strftime("%Y-%m-%d")
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Google Sheet URL (from env or default to new sheet)
    google_sheet_url = os.getenv(
        'GOOGLE_SHEET_URL',
        'https://docs.google.com/spreadsheets/d/1dp5WINj0Urrvk8Ul2rR_q6HDzjdeAp7iuw5IsY3J3f8/edit?gid=754847217'
    )

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = f"Daily Innovation Update for {current_date}"

    body = f"Please find the link to the Automated Daily innovation sheet for {tomorrow_date} :\n\n{google_sheet_url}"
    msg.attach(MIMEText(body, 'plain'))

    server = None
    try:
        # Create SMTP session
        print(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipients, text)
        print("✅ Email notification sent successfully")

    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        raise

    finally:
        if server:
            server.quit()

if __name__ == "__main__":
    send_notification()