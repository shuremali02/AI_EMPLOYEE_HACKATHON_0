#!/usr/bin/env python3
import os
import imaplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

email_address = os.getenv('EMAIL_ADDRESS')
email_password = os.getenv('EMAIL_PASSWORD')

print(f"Testing credentials:")
print(f"Email: {email_address}")
print(f"Password length: {len(email_password) if email_password else 0}")

if email_address and email_password:
    try:
        # Test IMAP connection
        print("\nTesting IMAP connection...")
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_address, email_password)
        print("✅ Login successful!")
        
        # Test fetching mailbox list
        status, mailboxes = mail.list()
        print(f"✅ Mailboxes accessible: {status}")
        
        # Check INBOX specifically
        mail.select('INBOX')
        status, messages = mail.search(None, 'ALL')
        email_count = len(messages[0].split()) if messages[0] else 0
        print(f"✅ INBOX accessible, emails found: {email_count}")
        
        mail.close()
        mail.logout()
        print("\n✅ Full test successful - credentials work!")
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
else:
    print("❌ Environment variables not loaded")
