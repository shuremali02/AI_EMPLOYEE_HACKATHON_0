# LinkedIn Post Skill

Create real LinkedIn posts using browser automation. Requires LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables.

## Usage
```python
python scripts/post_linkedin.py --text "Your post content here"
```

## Inputs
- text: Content for the LinkedIn post

## Output
- Success: "LinkedIn post created successfully"
- Error: "Failed to create LinkedIn post: [error message]"

## Requirements
- Playwright: pip install playwright
- Run: playwright install chromium