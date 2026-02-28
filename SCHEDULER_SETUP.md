# AI Employee Scheduler Setup

This document explains how to set up automatic execution of the AI Employee scheduler with automated LinkedIn posting.

## Linux/Mac: Cron Job Setup

### 1. Make the scripts executable:
```bash
chmod +x scripts/ai_employee_scheduler.py
chmod +x scripts/automated_linkedin_poster.py
```

### 2. Edit your crontab:
```bash
crontab -e
```

### 3. Add the following line to run every 5 minutes:
```bash
*/5 * * * * cd /path/to/your/project && /usr/bin/python3 scripts/ai_employee_scheduler.py --run-once >> /tmp/ai_employee.log 2>&1
```

### 4. Alternative: Run continuously as a service
For continuous operation, you may prefer to run the scheduler as a system service or with a process supervisor like systemd.

### Example systemd service file (create as `/etc/systemd/system/ai-employee.service`):
```ini
[Unit]
Description=AI Employee Scheduler
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/your/project
ExecStart=/usr/bin/python3 /path/to/your/project/scripts/ai_employee_scheduler.py --interval 5
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

To enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-employee.service
sudo systemctl start ai-employee.service
```

## Windows: Task Scheduler Setup

### 1. Open Task Scheduler
- Press `Win + R`, type `taskschd.msc`, and press Enter

### 2. Create a Basic Task
- Click "Create Basic Task" in the right panel
- Name: "AI Employee Scheduler"
- Description: "Automatically processes AI tasks and posts on LinkedIn every 5 minutes"

### 3. Set Trigger
- Select "Daily"
- Set the desired start time
- Next -> "Every 1 day"

### 4. Set Advanced Settings
- Click "Next" and select "Start a program"

### 5. Configure the Program
- Program/script: `python`
- Add arguments: `scripts/ai_employee_scheduler.py --run-once`
- Start in: `C:\path\to\your\project`

### 6. Configure Advanced Settings
- In the task properties, go to the "Settings" tab
- Check "Run task every" and set to 5 minutes
- Set "for a duration of" to "Indefinitely"

## Automated LinkedIn Posting

The scheduler includes automated LinkedIn posting functionality that:
- Posts business-related content to generate sales
- Runs according to a schedule (approximately once per day during business hours)
- Generates engaging content about industry trends, business insights, and professional development
- Uses hashtags to increase visibility

### Requirements for LinkedIn posting:
- LinkedIn account credentials (LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables)
- Playwright installed: `pip install playwright`
- Browser setup: `playwright install chromium`

## Manual Testing

To test the scheduler manually:
```bash
python3 scripts/ai_employee_scheduler.py --run-once
```

To run continuously in the foreground:
```bash
python3 scripts/ai_employee_scheduler.py --interval 5
```

To test LinkedIn posting separately:
```bash
python3 scripts/automated_linkedin_poster.py
```

## Environment Setup

Make sure your environment variables are properly set by creating a `.env` file at the project root with the necessary credentials:

```bash
# .env file contents:
EMAIL_ADDRESS=your_gmail_address@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
LINKEDIN_EMAIL=your_linkedin_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password
GMAIL_CREDENTIALS_PATH=gmail_credentials.json
WHATSAPP_SESSION_PATH=./whatsapp_session
```

For cron jobs, you might need to explicitly set environment variables in the crontab:
```bash
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

*/5 * * * * cd /path/to/your/project && /usr/bin/python3 scripts/ai_employee_scheduler.py --run-once >> /tmp/ai_employee.log 2>&1
```

## Troubleshooting

If the scheduler fails to run:
1. Check that Python 3 is available in the PATH
2. Verify all required dependencies are installed
3. Check that the AI_Employee_Vault directory structure exists
4. Ensure environment variables are properly set
5. Review log files for error details
6. For LinkedIn posting, ensure your credentials are correct and the account isn't rate-limited
5. For LinkedIn posting, ensure your credentials are correct and the account isn't rate-limited