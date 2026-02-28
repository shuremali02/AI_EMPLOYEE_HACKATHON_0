#!/usr/bin/env python3
"""
Gmail Watcher
Monitors Gmail for new emails and creates action files in the vault
"""
import os
import time
import base64
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from pathlib import Path

# Set up logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GmailWatcher:
    def __init__(self):
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH')

        if not self.email_address:
            logger.error("EMAIL_ADDRESS environment variable must be set")
            raise ValueError("EMAIL_ADDRESS environment variable must be set")

        self.vault_path = "AI_Employee_Vault"
        self.inbox_path = os.path.join(self.vault_path, "Inbox")

        # Create necessary directories
        os.makedirs(self.inbox_path, exist_ok=True)

        # Initialize Gmail service
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """Get authenticated Gmail service"""
        creds = None

        # Check if credentials file exists
        if self.credentials_path and os.path.exists(self.credentials_path):
            # Load from credentials file
            creds = Credentials.from_authorized_user_info(json.load(open(self.credentials_path)))
        else:
            logger.error("GMAIL_CREDENTIALS_PATH not set or file doesn't exist")
            logger.info("Falling back to SMTP-based email monitoring")
            return None

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    logger.error("Could not refresh credentials. Please re-authenticate.")
                    return None
            else:
                logger.error("Invalid credentials. Please set up proper Gmail API credentials.")
                return None

        return build('gmail', 'v1', credentials=creds)

    def _get_latest_email_id(self):
        """Get the ID of the most recently processed email"""
        latest_id_file = os.path.join(self.vault_path, "latest_email_id.txt")
        if os.path.exists(latest_id_file):
            with open(latest_id_file, 'r') as f:
                return f.read().strip()
        return None

    def _save_latest_email_id(self, email_id):
        """Save the ID of the most recently processed email"""
        latest_id_file = os.path.join(self.vault_path, "latest_email_id.txt")
        with open(latest_id_file, 'w') as f:
            f.write(email_id)

    def _extract_email_body(self, message):
        """Extract the body of the email from the message object"""
        import email
        from email.mime.text import MIMEText

        # Decode the message payload
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    return body
                elif part['mimeType'] == 'text/html':
                    # Fallback to HTML if plain text not available
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    return body
        else:
            # Handle messages without parts (simple messages)
            if 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
                return body

        return "Could not extract email body"

    def check_new_emails_smtp(self):
        """Alternative method using IMAP for SMTP-based email checking"""
        import imaplib
        import email

        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            email_address = os.getenv('EMAIL_ADDRESS')
            email_password = os.getenv('EMAIL_PASSWORD')

            if not email_password:
                logger.error("EMAIL_PASSWORD not set for IMAP access")
                return []

            mail.login(email_address, email_password)
            mail.select('inbox')

            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()

            new_emails = []

            for email_id in email_ids:
                # Fetch the email by ID
                status, msg_data = mail.fetch(email_id, '(RFC822)')

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Extract email details
                        subject = msg.get('Subject', 'No Subject')
                        sender = msg.get('From', 'Unknown Sender')
                        date = msg.get('Date', 'Unknown Date')

                        # Get email body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == 'text/plain':
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                        new_emails.append({
                            'id': email_id.decode(),
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'body': body[:1000]  # Limit body length
                        })

            mail.close()
            mail.logout()
            return new_emails

        except Exception as e:
            logger.error(f"Error checking emails via IMAP: {str(e)}")
            return []

    def check_new_emails(self):
        """Check for new emails using Gmail API or IMAP fallback"""
        if self.service:
            # Use Gmail API
            try:
                # Get messages from Gmail
                results = self.service.users().messages().list(
                    userId='me',
                    q='is:unread'
                ).execute()

                messages = results.get('messages', [])
                new_emails = []

                for message in messages:
                    msg_id = message['id']

                    # Get the full message
                    full_message = self.service.users().messages().get(
                        userId='me',
                        id=msg_id
                    ).execute()

                    # Extract headers and body
                    headers = full_message['payload']['headers']
                    subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                    sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
                    date = next((header['value'] for header in headers if header['name'] == 'Date'), 'Unknown Date')

                    # Extract body
                    body = self._extract_email_body(full_message)

                    new_emails.append({
                        'id': msg_id,
                        'subject': subject,
                        'sender': sender,
                        'date': date,
                        'body': body[:1000]  # Limit body length
                    })

                return new_emails
            except Exception as e:
                logger.error(f"Gmail API error: {str(e)}")
                logger.info("Falling back to SMTP/IMAP method")
                return self.check_new_emails_smtp()
        else:
            # Use SMTP/IMAP method
            return self.check_new_emails_smtp()

    def create_action_file(self, email_data):
        """Create an action file in the vault for the new email"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        email_id = email_data['id']

        # Create a safe filename
        safe_subject = "".join(c for c in email_data['subject'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_subject = safe_subject[:50]  # Limit length

        filename = f"gmail_action_{timestamp}_{email_id[:8]}.md"
        filepath = os.path.join(self.inbox_path, filename)

        # Create action file content
        action_content = f"""# New Email Action Required

## Email Details
- **From**: {email_data['sender']}
- **Subject**: {email_data['subject']}
- **Date**: {email_data['date']}
- **Email ID**: {email_data['id']}

## Email Content
{email_data['body']}

## Action Required
Review this email and take appropriate action.

## Priority
Medium

## Created
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(action_content)

        logger.info(f"Created action file: {filename}")

        return filepath

    def run(self):
        """Main loop to check for new emails"""
        logger.info(f"Starting Gmail watcher for account: {self.email_address}")
        logger.info("Checking for new emails...")

        new_emails = self.check_new_emails()

        if new_emails:
            logger.info(f"Found {len(new_emails)} new email(s)")

            for email_data in new_emails:
                try:
                    action_file = self.create_action_file(email_data)
                    # Mark as read by saving the ID (only if using API method)
                    if self.service:
                        self._save_latest_email_id(email_data['id'])
                except Exception as e:
                    logger.error(f"Error creating action file for email {email_data['id']}: {str(e)}")
        else:
            logger.info("No new emails found")

        logger.info("Gmail check completed")

def main():
    try:
        watcher = GmailWatcher()
        watcher.run()
    except Exception as e:
        logger.error(f"Error running Gmail watcher: {str(e)}")

if __name__ == "__main__":
    main()