#!/usr/bin/env python3
"""
Simple Gmail Watcher - Monitors Gmail for new emails using IMAP
"""
import os
import time
import email
import imaplib
import base64
from datetime import datetime
from pathlib import Path

# Set up logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleGmailWatcher:
    def __init__(self):
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()

        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')

        if not self.email_address or not self.email_password:
            logger.error("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set")
            raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set")

        self.vault_path = "AI_Employee_Vault"
        self.inbox_path = os.path.join(self.vault_path, "Inbox")

        # Create necessary directories
        os.makedirs(self.inbox_path, exist_ok=True)

        logger.info(f"Initialized Gmail watcher for account: {self.email_address}")

    def check_new_emails(self):
        """Check for new emails using IMAP"""
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email_address, self.email_password)

            # Select inbox
            mail.select('inbox')

            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()

            logger.info(f"Found {len(email_ids)} unread email(s)")

            new_emails = []

            for email_id in email_ids:
                # Fetch the email by ID
                status, msg_data = mail.fetch(email_id, '(RFC822)')

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        # Parse the email content
                        msg = email.message_from_bytes(response_part[1])

                        # Extract email details
                        subject = msg.get('Subject', 'No Subject')
                        sender = msg.get('From', 'Unknown Sender')
                        date = msg.get('Date', 'Unknown Date')

                        # Get email body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                                elif part.get_content_type() == "text/html" and not body:
                                    # Fallback to HTML if no plain text
                                    import html
                                    html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    # Convert HTML to plain text
                                    body = html.unescape(html_body.replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n'))
                        else:
                            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                        new_emails.append({
                            'id': email_id.decode(),
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'body': body[:2000]  # Limit body length
                        })

            mail.close()
            mail.logout()
            logger.info(f"Successfully retrieved {len(new_emails)} new email(s)")
            return new_emails

        except Exception as e:
            logger.error(f"Error checking emails via IMAP: {str(e)}")
            return []

    def create_action_file(self, email_data):
        """Create an action file in the vault for the new email"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create a safe filename
        safe_subject = "".join(c for c in email_data['subject'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_subject = safe_subject[:50]  # Limit length if too long

        filename = f"gmail_action_{timestamp}_{email_data['id'][:8]}.md"
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

    def run(self, interval=300):  # Default to 5 minutes
        """Main method to continuously check for new emails"""
        logger.info(f"Initialized Gmail watcher for account: {self.email_address}")

        while True:
            logger.info(f"Starting Gmail check for account: {self.email_address}")
            logger.info("Checking for new emails...")

            new_emails = self.check_new_emails()

            if new_emails:
                logger.info(f"Successfully retrieved {len(new_emails)} new email(s)")
                logger.info(f"Processing {len(new_emails)} new email(s)")

                for email_data in new_emails:
                    try:
                        action_file = self.create_action_file(email_data)
                        logger.info(f"Created action item for email: {email_data['subject'][:50]}...")
                    except Exception as e:
                        logger.error(f"Error creating action file for email {email_data['id']}: {str(e)}")
            else:
                logger.info("No new emails found")

            logger.info("Gmail check completed")
            logger.info(f"Waiting {interval} seconds before next check...")

            try:
                time.sleep(interval)  # Wait for specified interval before next check
            except KeyboardInterrupt:
                logger.info("Gmail watcher stopped by user")
                break

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee Vault')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds (default: 300 for 5 minutes)')

    args = parser.parse_args()

    try:
        watcher = SimpleGmailWatcher()
        watcher.run(interval=args.interval)
    except Exception as e:
        logger.error(f"Error running Gmail watcher: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()