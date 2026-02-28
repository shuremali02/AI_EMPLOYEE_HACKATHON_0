#!/usr/bin/env python3
import os
import imaplib

# Load your credentials
email_address = "aiemployeetesting@gmail.com"
email_password = "ipss htmo scdz ohre"

print(f"Testing connection to: {email_address}")

try:
    # Try to connect to Gmail IMAP
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email_address, email_password)
    print("✅ Gmail connection successful!")
    
    # Check inbox
    mail.select('inbox')
    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()
    print(f"Found {len(email_ids)} unread emails")
    
    mail.close()
    mail.logout()
except Exception as e:
    print(f"❌ Gmail connection failed: {e}")
