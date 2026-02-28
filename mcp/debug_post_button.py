#!/usr/bin/env python3
"""
Simple debug script to identify the post button in LinkedIn after clicking 'Start a post'
"""
import os
import asyncio
from playwright.async_api import async_playwright
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def simple_debug_linkedin_post():
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')

    if not email or not password:
        logger.error("LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables must be set")
        return

    async with async_playwright() as p:
        # Launch browser in non-headless mode so we can see the interface
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go to LinkedIn login page
        await page.goto("https://www.linkedin.com/login")

        # Fill in login credentials
        await page.fill("input#username", email)
        await page.fill("input#password", password)

        # Click login button
        await page.click("button[type='submit']")

        # Wait for login to complete
        try:
            await page.wait_for_url("https://www.linkedin.com/feed/", timeout=30000)
            logger.info("Successfully logged in!")
        except:
            current_url = page.url
            logger.info(f"Current URL after login: {current_url}")
            if "checkpoint" in current_url or "challenge" in current_url:
                logger.info("Security verification required. Please complete in browser.")
                await page.wait_for_timeout(300000)  # Wait 5 mins for manual verification
            else:
                logger.info("Login might have taken longer than expected.")

        # Wait for page to fully load
        await page.wait_for_timeout(5000)

        # Try to click 'Start a post' button using the working selector
        logger.info("Clicking 'Start a post' button...")
        try:
            # Use the text selector that we know works
            start_post_button = await page.wait_for_selector("text='Start a post'", timeout=10000)
            if start_post_button:
                await start_post_button.click()
                logger.info("Successfully clicked 'Start a post' button")
            else:
                # Fallback
                await page.click("button:has-text('Start a post')")
                logger.info("Clicked 'Start a post' button using alternative selector")
        except Exception as e:
            logger.error(f"Error clicking 'Start a post' button: {e}")
            await browser.close()
            return

        # Wait for the share box to appear
        await page.wait_for_timeout(5000)

        # Now examine what buttons are available
        logger.info("Examining available buttons after clicking 'Start a post'...")

        # Get the content editor (the text box where we would type)
        content_editor = await page.query_selector("div[contenteditable='true'][role='textbox']")
        if content_editor:
            logger.info("Found content editor")
            # Fill it with a simple test text to trigger the post button to appear
            await content_editor.fill("Testing post button detection")
            await page.wait_for_timeout(2000)  # Wait for UI to update
        else:
            logger.info("No content editor found")

        # Get all buttons currently on the page
        buttons = await page.query_selector_all("button")
        logger.info(f"Found {len(buttons)} buttons on the page")

        for i, button in enumerate(buttons[-10:], 1):  # Look at the last 10 buttons (likely post-related)
            try:
                text_content = await button.text_content()
                aria_label = await button.get_attribute("aria-label")
                class_name = await button.get_attribute("class")
                button_id = await button.get_attribute("id")
                is_disabled = await button.get_attribute("disabled")

                logger.info(f"Button {i}: text='{text_content[:30]}...', aria-label='{aria_label}', class='{class_name[:40]}...', id='{button_id}', disabled={is_disabled}")
            except Exception as e:
                logger.info(f"Button {i}: error getting properties - {e}")

        # Wait for user to inspect the page manually
        logger.info("Browser staying open for manual inspection. Look for the actual 'Post' button!")
        await page.wait_for_timeout(120000)  # Wait 2 minutes

        await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_debug_linkedin_post())