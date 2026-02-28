#!/usr/bin/env python3
"""
WhatsApp Watcher for AI Employee Vault

Monitors WhatsApp Web for new messages and creates markdown files in
the Needs_Action directory with appropriate metadata.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import argparse
from playwright.sync_api import sync_playwright


class BaseWatcher:
    """Base class for all watchers."""

    def __init__(self, vault_path: str, check_interval: int = 30):
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / 'Inbox'
        self.needs_action_path = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval

        # Ensure directories exist
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.needs_action_path.mkdir(parents=True, exist_ok=True)

    def create_action_file(self, title: str, content: str, metadata: Dict[str, Any] = None):
        """Create an action file in the Needs_Action directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title[:50]  # Limit length

        filename = f"whatsapp_action_{timestamp}_{len(os.listdir(self.needs_action_path)) + 1}.md"
        filepath = self.needs_action_path / filename

        action_content = f"""# WhatsApp Action Required

## Message Details
- **Title**: {title}
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content
{content}

## Metadata
{json.dumps(metadata or {}, indent=2)}

## Action Required
Review this WhatsApp message and take appropriate action.

## Priority
{metadata.get('urgency_level', 'Medium') if metadata else 'Medium'}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(action_content)

        print(f"Created action file: {filepath}")
        return filepath

    def run_continuous_monitoring(self):
        """Run continuous monitoring loop."""
        while True:
            updates = self.check_for_updates()

            for update in updates:
                self.create_action_file(
                    title=update['title'],
                    content=update['content'],
                    metadata=update.get('metadata', {})
                )

            print(f"Checked for updates, found {len(updates)} messages requiring action.")
            time.sleep(self.check_interval)


class WhatsappWatcher:
    """Class to handle WhatsApp Web monitoring and processing."""

    def __init__(self, vault_path: str, session_path: str = "./whatsapp_session", check_interval: int = 300):
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / 'Inbox'
        self.needs_action_path = self.vault_path / 'Needs_Action'
        self.session_path = Path(session_path)
        self.check_interval = check_interval
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'order', 'business', 'important', 'needed', 'required']

        # Ensure session directory exists
        self.session_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure directories exist
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.needs_action_path.mkdir(parents=True, exist_ok=True)

    def get_event_type(self) -> str:
        return "whatsapp"

    def initialize_browser_session(self):
        """Initialize the browser session and keep it open."""
        from playwright.sync_api import sync_playwright
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            str(self.session_path),
            headless=False,  # Set to False to see QR code for initial setup
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )

        # Load WhatsApp Web once and keep the session
        self.page = self.browser.new_page()
        self.page.goto('https://web.whatsapp.com')

        # Wait for WhatsApp Web to load
        start_time = time.time()
        max_wait_time = 300  # 5 minutes in seconds
        logged_in = False

        while time.time() - start_time < max_wait_time and not logged_in:
            try:
                # Check for multiple possible indicators of being logged in
                chat_list = self.page.query_selector('[data-testid="chat-list"]')
                if chat_list:
                    print("WhatsApp Web loaded successfully - chat list detected!")
                    logged_in = True
                    break

                # Check for the main chat area
                main_chat = self.page.query_selector('div[aria-label="Chat list"]')
                if main_chat:
                    print("WhatsApp Web loaded successfully - main chat area detected!")
                    logged_in = True
                    break

                # Check for QR code (indicating need to scan)
                qr_code = self.page.query_selector('canvas[aria-label="Scan me!"]')
                if not qr_code:
                    # No QR code means we might be logged in, wait a bit more to confirm
                    time.sleep(2)
                else:
                    print("QR code detected! Please scan it with your phone now.")
                    print("Waiting up to 5 minutes for QR code scan...")
                    time.sleep(2)

            except Exception as e:
                print(f"Error checking page elements: {e}")
                time.sleep(2)

        if not logged_in:
            print("Failed to load WhatsApp Web, possibly need to scan QR code")
            print("Make sure to scan QR code that appears in the browser with your phone's WhatsApp app")
            return False

        return True

    def monitor_realtime(self, needs_action_dir):
        """Monitor WhatsApp Web in real-time for keyword messages."""
        if not hasattr(self, 'page'):
            if not self.initialize_browser_session():
                return

        print("Starting real-time monitoring...")

        # Inject JavaScript to monitor for new messages
        self.page.evaluate("""
            // Create a function to watch for new messages
            window.whatsappMessageWatcher = {
                lastChecked: new Date(),
                watchedElements: new Set(),
                initiallyScanned: false, // Track if we've done the initial scan

                // Function to check for messages
                checkForMessages: function() {
                    // Look for all chat entries
                    const chatElements = document.querySelectorAll('div[data-testid="chat-list"] div[tabindex="-1"]');
                    const messages = [];

                    for (let chat of chatElements) {
                        // Get chat name
                        let chatName = 'Unknown';
                        const nameElement = chat.querySelector('div[aria-label] span[dir="auto"]') ||
                                          chat.querySelector('div[tabindex="-1"] span[dir="auto"]');
                        if (nameElement) {
                            chatName = nameElement.textContent;
                        }

                        // Get message preview
                        let messageText = 'No preview available';
                        const messageElement = chat.querySelector('span[dir="auto"][data-testid="conversation-snippet"]') ||
                                             chat.querySelector('span[dir="auto"]');
                        if (messageElement) {
                            messageText = messageElement.textContent;
                        }

                        // Create message object
                        messages.push({
                            chatName: chatName,
                            messageText: messageText,
                            elementId: chat.getAttribute('data-testid') || chat.textContent.substring(0, 20),
                            timestamp: new Date().toISOString()
                        });
                    }

                    return messages;
                },

                // Function to check for new/unprocessed messages
                checkForUnprocessedMessages: function() {
                    // Always get all current messages
                    const allMessages = this.checkForMessages();
                    const unprocessedMessages = [];

                    for (let msg of allMessages) {
                        if (!this.watchedElements.has(msg.elementId)) {
                            this.watchedElements.add(msg.elementId);
                            unprocessedMessages.push(msg);
                        }
                    }

                    return unprocessedMessages;
                },

                // Function to scan all existing messages on startup
                scanExistingMessages: function() {
                    console.log('Scanning existing messages...');
                    const allMessages = this.checkForMessages();

                    // Mark all current messages as watched so we don't process them again
                    for (let msg of allMessages) {
                        this.watchedElements.add(msg.elementId);
                    }

                    // But still return all current messages for initial processing
                    return allMessages;
                }
            };

            // On initial load, scan existing messages
            setTimeout(() => {
                // Get all existing messages and send them for processing
                const existingMessages = window.whatsappMessageWatcher.scanExistingMessages();
                if (existingMessages.length > 0) {
                    window.newMessagesAvailable = existingMessages;
                    console.log('Sent ' + existingMessages.length + ' existing messages for processing');
                }
            }, 3000); // Wait 3 seconds after page load to ensure messages are loaded

            // Set up an interval to check for new messages every 5 seconds
            window.whatsappMonitorInterval = setInterval(() => {
                const newMessages = window.whatsappMessageWatcher.checkForUnprocessedMessages();
                if (newMessages.length > 0) {
                    // Send the new messages to the Python side
                    window.newMessagesAvailable = newMessages;
                    console.log('Sent ' + newMessages.length + ' new messages for processing');
                }
            }, 5000); // Check every 5 seconds
        """)

        while True:
            try:
                # Check if there are new messages available from the JavaScript side
                new_messages_js = self.page.evaluate("window.newMessagesAvailable || []")

                if new_messages_js:
                    # Clear the new messages flag
                    self.page.evaluate("window.newMessagesAvailable = []")

                    for msg in new_messages_js:
                        # Check if message contains any keywords
                        message_lower = msg['messageText'].lower()
                        matched_keywords = [kw for kw in self.keywords if kw in message_lower]

                        if matched_keywords:
                            # Create update object
                            update = {
                                'id': f"whatsapp_{int(time.time())}_{datetime.now().strftime('%H%M%S')}",
                                'title': f"WhatsApp Urgent Message from {msg['chatName']}",
                                'content': f"Chat: {msg['chatName']}\nMessage: {msg['messageText']}\nMatched Keywords: {', '.join(matched_keywords)}",
                                'timestamp': datetime.now().isoformat(),
                                'metadata': {
                                    'contact': msg['chatName'],
                                    'message_text': msg['messageText'],
                                    'matched_keywords': matched_keywords,
                                    'urgency_level': 'high' if any(kw in matched_keywords for kw in ['urgent', 'asap']) else 'medium',
                                    'element_id': msg['elementId']
                                }
                            }

                            # Create action file
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            safe_title = "".join(c for c in update['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            safe_title = safe_title[:50]  # Limit length

                            filename = f"whatsapp_action_{timestamp}_{len(os.listdir(needs_action_dir)) + 1}.md"
                            filepath = needs_action_dir / filename

                            action_content = f"""# WhatsApp Action Required

## Message Details
- **Title**: {update['title']}
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content
{update['content']}

## Metadata
{json.dumps(update.get('metadata', {}), indent=2)}

## Action Required
Review this WhatsApp message and take appropriate action.

## Priority
{update.get('metadata', {}).get('urgency_level', 'Medium')}
"""

                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(action_content)

                            print(f"Created action file: {filepath}")
                            print(f"Real-time alert: Urgent message from {msg['chatName']}: {msg['messageText'][:50]}...")

                # Small delay to prevent excessive CPU usage
                time.sleep(1)

            except KeyboardInterrupt:
                print("\nStopping real-time monitoring...")
                break
            except Exception as e:
                print(f"Error in real-time monitoring: {str(e)}")
                time.sleep(5)  # Wait before retrying


def main():
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee Vault')
    parser.add_argument('--vault-dir', default='./AI_Employee_Vault',
                       help='Vault directory containing Needs_Action folder (default: ./AI_Employee_Vault)')
    parser.add_argument('--session-path', default='./whatsapp_session',
                       help='Path to store WhatsApp Web session data (default: ./whatsapp_session)')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds (default: 300 for 5 minutes)')

    args = parser.parse_args()

    # Validate vault directory
    vault_dir = Path(args.vault_dir)
    needs_action_dir = vault_dir / 'Needs_Action'

    if not needs_action_dir.exists():
        print(f"Vault Needs_Action directory does not exist: {needs_action_dir}")
        return 1

    # Create the WhatsApp watcher
    whatsapp_watcher = WhatsappWatcher(str(vault_dir), args.session_path, args.interval)

    try:
        print("WhatsApp watcher initialized successfully!")
        print(f"Monitoring WhatsApp Web for new messages...")
        print(f"Session data stored in: {whatsapp_watcher.session_path}")
        print(f"Messages with keywords {whatsapp_watcher.keywords} will trigger action items")
        print(f"Action items will be created in: {needs_action_dir}")
        print("Press Ctrl+C to stop.")

        # Initialize the browser session once and start real-time monitoring
        if not whatsapp_watcher.initialize_browser_session():
            print("Failed to initialize browser session")
            return 1

        # Start real-time monitoring
        whatsapp_watcher.monitor_realtime(needs_action_dir)

    except KeyboardInterrupt:
        print("\nStopping WhatsApp watcher...")
        # Clean up browser resources
        if hasattr(whatsapp_watcher, 'browser'):
            whatsapp_watcher.browser.close()
        if hasattr(whatsapp_watcher, 'playwright'):
            whatsapp_watcher.playwright.stop()
    except Exception as e:
        print(f"Error initializing WhatsApp watcher: {str(e)}")
        # Clean up browser resources
        if hasattr(whatsapp_watcher, 'browser'):
            try:
                whatsapp_watcher.browser.close()
            except:
                pass
        if hasattr(whatsapp_watcher, 'playwright'):
            try:
                whatsapp_watcher.playwright.stop()
            except:
                pass
        return 1

    return 0


if __name__ == "__main__":
    main()