#!/usr/bin/env python3
"""
Debug script to identify the correct LinkedIn UI elements for posting
"""
import os
import asyncio
from playwright.async_api import async_playwright
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_linkedin_ui():
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')

    if not email or not password:
        logger.error("LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables must be set")
        return

    async with async_playwright() as p:
        # Launch browser in non-headless mode so we can see what's happening
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

        # Look for the exact "Start a post" button
        logger.info("Looking for 'Start a post' button...")

        # Try to find elements with the exact text "Start a post"
        elements = await page.query_selector_all("*")

        for element in elements:
            try:
                text_content = await element.text_content()
                if 'start a post' in text_content.lower():
                    aria_label = await element.get_attribute("aria-label")
                    class_name = await element.get_attribute("class")
                    tag_name = await element.evaluate("el => el.tagName")
                    logger.info(f"Found 'start a post' element: tag={tag_name}, text='{text_content.strip()}', aria-label='{aria_label}', class='{class_name}'")
            except:
                continue

        # Also look for other common share-related elements
        logger.info("Looking for other share-related elements...")
        share_elements = await page.query_selector_all("*")

        for element in share_elements:
            try:
                text_content = await element.text_content()
                aria_label = await element.get_attribute("aria-label")
                class_name = await element.get_attribute("class")

                has_share_words = any(word in (text_content or '').lower() for word in ['post', 'share', 'create', 'start', 'write', 'update'])
                has_share_attributes = any(word in (aria_label or '').lower() for word in ['post', 'share', 'create', 'start', 'write', 'update'])

                if has_share_words or has_share_attributes:
                    tag_name = await element.evaluate("el => el.tagName")
                    logger.info(f"Share-related element: tag={tag_name}, text='{text_content[:50].strip()}', aria-label='{aria_label}', class='{class_name[:50]}'")
            except:
                continue

        # Wait for user to inspect the page
        logger.info("Browser staying open for 5 minutes for manual inspection...")
        await page.wait_for_timeout(300000)  # Wait 5 minutes

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_linkedin_ui())