import argparse
import os
import sys
from playwright.sync_api import sync_playwright

def post_linkedin(text):
    # Get LinkedIn credentials from environment variables
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')

    if not email or not password:
        print("Error: LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables must be set")
        sys.exit(1)

    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Go to LinkedIn login page
            page.goto("https://www.linkedin.com/login")

            # Fill in login credentials
            page.fill("input#username", email)
            page.fill("input#password", password)

            # Click login button
            page.click("button[type='submit']")

            # Wait for login to complete
            page.wait_for_url("https://www.linkedin.com/feed/")

            # Click on the create post button
            page.wait_for_selector("button[aria-label='Create a post']")
            page.click("button[aria-label='Create a post']")

            # Wait for the text area to be available
            page.wait_for_selector("div[contenteditable='true']")

            # Fill the post content
            page.fill("div[contenteditable='true']", text)

            # Click the post button
            page.click("button[aria-label='Post']")

            # Wait for post to be published
            page.wait_for_timeout(3000)
            browser.close()

            print("LinkedIn post created successfully")
    except Exception as e:
        print(f"Failed to create LinkedIn post: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create LinkedIn post")
    parser.add_argument("--text", required=True, help="Content for the LinkedIn post")

    args = parser.parse_args()

    post_linkedin(args.text)