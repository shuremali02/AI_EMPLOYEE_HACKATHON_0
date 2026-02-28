import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys

def send_email(to, subject, body):
    # Get email credentials from environment variables
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')

    if not email_address or not email_password:
        print("Error: EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set")
        sys.exit(1)

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = to
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP
        server.starttls()  # Enable security
        server.login(email_address, email_password)

        # Send email
        text = msg.as_string()
        server.sendmail(email_address, to, text)
        server.quit()

        print(f"Email sent successfully to {to}")

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send email via SMTP")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body")

    args = parser.parse_args()

    send_email(args.to, args.subject, args.body)