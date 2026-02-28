# Gmail Send Skill

Send real emails via SMTP. Requires EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.

## Usage
```python
python scripts/send_email.py --to "recipient@example.com" --subject "Subject" --body "Email body"
```

## Inputs
- to: Recipient email address
- subject: Email subject line
- body: Email body content

## Output
- Success: "Email sent successfully to [recipient]"
- Error: "Failed to send email: [error message]"