#!/usr/bin/env python3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

def send_notification():
    # Email configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.timesinternet.in')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    # Email content
    sender_email = "Adtech Quality <ritesh.sanjay@timesinternet.in>"
    recipients = ["colombia.opsqc@timesinternet.in", "ritesh.sanjay@timesinternet.in"]
    
    # Get dates
    current_date = datetime.now().strftime("%Y-%m-%d")
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = f"Daily Innovation Update for {current_date}"
    
    google_sheet_url = os.getenv('GOOGLE_SHEET_URL')
    body = f"Please find the link to daily innovation for tomorrow:\n\n{https://docs.google.com/spreadsheets/d/1U12VbADtQ8mQowRjEkEYgxy2bRXDBJwPNKu3OayswIg/edit?gid=1104720664#gid=1104720664}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Create SMTP session
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
        server.quit()

if __name__ == "__main__":
    send_notification()