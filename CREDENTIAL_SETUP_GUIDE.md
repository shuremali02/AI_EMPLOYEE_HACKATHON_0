# Credential Setup Guide

This guide will help you set up the required credentials and environment variables for your Personal AI Employee.

## Gmail API Credentials Setup

### Step 1: Enable Gmail API
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to APIs & Services > Library
4. Search for "Gmail API" and click on it
5. Click "Enable" to enable the Gmail API for your project

### Step 2: Create OAuth 2.0 Credentials
1. Go to APIs & Services > Credentials
2. Click "Create Credentials" > OAuth 2.0 Client IDs
3. For Application Type, select "Desktop Application"
4. Give it a name like "AI Employee Gmail Access"
5. Click "Create"
6. Download the credentials JSON file
7. Rename the downloaded file to `gmail_credentials.json`
8. Place it in your project root directory

### Step 3: Configure OAuth Consent Screen (if needed)
1. Go to APIs & Services > OAuth consent screen
2. Select "External" and click "Create"
3. Fill in the required information:
   - App name: "AI Employee"
   - User support email: your email
   - Developer contact information: your email
4. In Scopes, add these Gmail scopes:
   - `.../auth/gmail.modify` - Read, compose, send, and permanently delete all your email from your Gmail account
   - `.../auth/gmail.readonly` - View your email messages and settings
5. Add test users (your Gmail address)
6. Save and continue until the consent screen is published

### Step 4: Set up Application-Specific Password (Alternative)
Instead of OAuth, you can use an application-specific password:
1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account settings > Security
3. Under "How you sign in to Google", select "App passwords"
4. Generate a new app password for "Mail"
5. Use this password in the `EMAIL_PASSWORD` environment variable

## LinkedIn Credentials Setup

### Step 1: LinkedIn Account Information
1. You'll need your LinkedIn email address and password
2. Note: LinkedIn may require additional verification steps
3. Be careful as LinkedIn has strict automation policies

### Step 2: Environment Variables
- `LINKEDIN_EMAIL`: Your LinkedIn email address
- `LINKEDIN_PASSWORD`: Your LinkedIn password

⚠️ **Important**: LinkedIn actively prevents automated access. Use this feature responsibly and in compliance with LinkedIn's Terms of Service.

## WhatsApp Session Setup

### Step 1: Initial WhatsApp Web Authentication
To authenticate WhatsApp Web for the first time, you need to run the authentication process in a GUI-enabled environment:

1. Run the authentication script:
   ```bash
   python test_whatsapp_auth.py
   ```

   OR run the WhatsApp watcher directly to see the QR code:
   ```bash
   python whatsapp_watcher.py AI_Employee_Vault
   ```

2. When the Chromium browser opens, scan the QR code with your phone:
   - Open WhatsApp on your phone
   - Go to Settings (three dots on Android, bottom right on iPhone) → Linked Devices
   - Point your phone's camera at the QR code displayed by the program

3. After successful authentication, the session will be saved to the path specified and can be reused

### Step 2: Environment Variables
- `WHATSAPP_SESSION_PATH`: Path where WhatsApp session data will be stored (default: `./whatsapp_session`)

### Step 3: Running in Production
After initial authentication, you can run the WhatsApp watcher in headless mode:
```bash
nohup python whatsapp_watcher.py AI_Employee_Vault > whatsapp_watcher.log 2>&1 &
```

⚠️ **Important**: The first run MUST be done in a GUI environment to scan the QR code. Subsequent runs can be headless.

For detailed instructions, see `WHATSAPP_SETUP_INSTRUCTIONS.md`.

## Environment Variables Setup

### Step 1: Create the .env File
Create a `.env` file in your project root with the following content:

```bash
# Gmail API Configuration
EMAIL_ADDRESS=your_actual_gmail@gmail.com
EMAIL_PASSWORD=your_app_password_or_oauth_token
GMAIL_CREDENTIALS_PATH=gmail_credentials.json

# LinkedIn Configuration
LINKEDIN_EMAIL=your_linkedin_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password

# WhatsApp Configuration
WHATSAPP_SESSION_PATH=./whatsapp_session

# Claude Code (if using API)
CLAUDE_CODE_API_KEY=your_claude_api_key_here
```

### Step 2: Security Best Practices
1. **Never commit your .env file** to version control (the .gitignore file should already prevent this)
2. Store the .env file in a secure location
3. Use application-specific passwords instead of your main account password when possible
4. Regularly rotate your credentials
5. Monitor your accounts for any unusual activity

## MCP Server Configuration

### Email MCP Server
The email MCP server uses the credentials above to send emails via SMTP.

### LinkedIn MCP Server
The LinkedIn MCP server uses your LinkedIn credentials to post updates.

### Browser MCP Server
The browser MCP server can be used for various web automation tasks.

## Testing Your Setup

### Step 1: Verify Environment Variables
Run this command to make sure your environment is properly configured:
```bash
source .venv/bin/activate && python -c "import os; print('EMAIL_ADDRESS:', os.getenv('EMAIL_ADDRESS') is not None)"
```

### Step 2: Test MCP Server Initialization
```bash
source .venv/bin/activate && python test_mcp_servers.py
```

### Step 3: Test Individual Components
1. Test the email functionality with a simple test email
2. Test the LinkedIn poster with a simple post
3. Ensure the WhatsApp session is properly authenticated

## Troubleshooting

### Gmail API Issues
- If you get authentication errors, verify your credentials file and OAuth setup
- Check that the Gmail API is enabled in the Google Cloud Console
- Make sure you've granted the necessary permissions

### LinkedIn Automation Issues
- LinkedIn may block automation attempts
- Monitor for rate limits or account restrictions
- Consider using manual posting for sensitive content

### WhatsApp Web Issues
- If the QR code doesn't appear, make sure you've installed Playwright browsers
- Run: `playwright install chromium`
- If authentication fails, delete the session directory and try again

## Security Recommendations

⚠️ **Critical Security Notes**:
1. Never share your credentials or .env file
2. Always use a dedicated email account for automation
3. Monitor your accounts for unauthorized access
4. Regularly rotate your credentials
5. Be aware of service-specific rate limits and terms of service
6. Implement proper error handling to prevent credential exposure in logs
7. Use environment-specific configurations (dev vs production)

Remember to always use these tools responsibly and in compliance with applicable terms of service.