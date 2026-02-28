# WhatsApp Web Authentication for AI Employee

This guide will help you set up WhatsApp Web authentication for your AI Employee.

## Prerequisites
- A computer with GUI access (to see the QR code)
- WhatsApp installed on your phone
- Stable internet connection

## Step 1: Prepare the Environment
Make sure you're in the correct directory:
```bash
cd /mnt/e/AI_EMPLOYEE_HACKATHON_0
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
```

## Step 2: Authenticate WhatsApp Web Manually

### Option A: Using the Test Authentication Script (Recommended for first time)
```bash
# Run this in a terminal with GUI access (like WSL with GUI support or native Linux/Windows with Python GUI support)
python test_whatsapp_auth.py
```

### Option B: Run the WhatsApp Watcher in GUI Mode (For first time only)
```bash
# This will open the browser in non-headless mode so you can see the QR code
# Run this command in a GUI-enabled terminal
python whatsapp_watcher.py AI_Employee_Vault
```

## Step 3: Scan the QR Code
1. When you run either of the above commands, a Chromium browser will open
2. Open WhatsApp on your phone
3. Go to Settings (three dots on Android, bottom right on iPhone) → Linked Devices
4. Point your phone's camera at the QR code displayed in the browser
5. The QR code should automatically scan and authenticate your session

## Step 4: Session Storage
Once authenticated, your session will be stored in:
```
./whatsapp_session/
```
This includes your authentication tokens, so the next time you run the watcher, it won't need to show the QR code again.

## Step 5: Run the WhatsApp Watcher in Production Mode
After the first authentication, you can run the WhatsApp watcher in headless mode:
```bash
source .venv/bin/activate && export $(grep -v '^#' .env | xargs) && nohup python whatsapp_watcher.py AI_Employee_Vault > whatsapp_watcher.log 2>&1 &
```

## Troubleshooting

### If you get a "Failed to launch browser" error:
- Make sure Playwright Chromium is installed: `playwright install chromium`
- Make sure you have proper display access in your environment

### If the QR code doesn't appear or isn't scanning:
- Try refreshing the page (Ctrl+R in the browser)
- Make sure your phone's camera can focus on the QR code
- Ensure good lighting for your phone's camera

### If you get permission errors:
- Make sure the whatsapp_session directory has proper write permissions
- Check that your .env file has the correct path: `WHATSAPP_SESSION_PATH=./whatsapp_session`

### If the authentication keeps failing:
- Clear the session directory: `rm -rf ./whatsapp_session/`
- Re-authenticate following steps 2-3 above

## Security Note
⚠️ The session files contain authentication tokens. They are listed in .gitignore to prevent accidental commit, but make sure not to share them or store them insecurely.

## Next Steps
Once WhatsApp is authenticated, the AI Employee will continuously monitor your WhatsApp for messages containing the following keywords:
- urgent
- asap
- invoice
- payment
- help
- important

When such messages are detected, the system will create action files in your `AI_Employee_Vault/Needs_Action/` directory.