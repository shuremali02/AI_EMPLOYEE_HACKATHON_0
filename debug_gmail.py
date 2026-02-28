#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment variables:")
print(f"EMAIL_ADDRESS: {os.getenv('EMAIL_ADDRESS')}")
print(f"EMAIL_PASSWORD: {os.getenv('EMAIL_PASSWORD')}")
print(f"GMAIL_CREDENTIALS_PATH: {os.getenv('GMAIL_CREDENTIALS_PATH')}")

# Now test the GmailWatcher class directly
import sys
sys.path.insert(0, '.')

try:
    from gmail_watcher import GmailWatcher
    watcher = GmailWatcher()
    print("GmailWatcher initialized successfully")
    print(f"watcher.email_address: {watcher.email_address}")
except Exception as e:
    print(f"Error initializing GmailWatcher: {e}")
    import traceback
    traceback.print_exc()
