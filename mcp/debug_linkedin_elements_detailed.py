#!/usr/bin/env python3
"""
Detailed debug script to identify LinkedIn elements after clicking 'Start a post'
"""
import os
import asyncio
from playwright.async_api import async_playwright
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def detailed_debug():
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
            logger.info("✅ Successfully logged in!")
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            current_url = page.url
            logger.info(f"Current URL after login attempt: {current_url}")
            await browser.close()
            return

        # Wait for page to fully load
        await page.wait_for_timeout(5000)

        # Click 'Start a post' button using the working selector
        logger.info("🔍 Looking for and clicking 'Start a post' button...")
        try:
            # Use the text selector that we know works
            start_post_button = await page.wait_for_selector("text='Start a post'", timeout=10000)
            if start_post_button:
                await start_post_button.click()
                logger.info("✅ Successfully clicked 'Start a post' button")
            else:
                logger.error("❌ Could not find 'Start a post' button by text selector")
                await browser.close()
                return
        except Exception as e:
            logger.error(f"❌ Error clicking 'Start a post' button: {e}")
            await browser.close()
            return

        # Wait for the share box to appear
        await page.wait_for_timeout(5000)

        # Get the content editor and fill it
        logger.info("🔍 Looking for content editor...")
        content_editor = None
        content_selectors = [
            "div[contenteditable='true'][role='textbox']",
            "div[contenteditable='true']",
            "div[role='textbox']",
            "div[aria-label*='post' i]"
        ]

        for selector in content_selectors:
            try:
                content_editor = await page.wait_for_selector(selector, timeout=5000)
                if content_editor:
                    logger.info(f"✅ Found content editor with selector: {selector}")
                    await content_editor.click()
                    await content_editor.fill("This is a test post to identify the correct post button")
                    logger.info("✅ Content filled successfully")
                    break
            except:
                logger.info(f"❌ Could not use content selector: {selector}")
                continue

        if not content_editor:
            logger.error("❌ Could not find any content editor")
            await browser.close()
            return

        # Wait for UI to update after content is entered
        await page.wait_for_timeout(5000)

        # Now let's get ALL buttons on the page and log their properties to identify the right one
        logger.info("🔍 Examining all buttons on the page to identify the correct Post button...")
        buttons = await page.query_selector_all("button")

        logger.info(f"Found {len(buttons)} buttons total:")

        # Let's look at the buttons that might be relevant
        for i, button in enumerate(buttons):
            try:
                text_content = await button.text_content()
                aria_label = await button.get_attribute("aria-label")
                class_name = await button.get_attribute("class")
                button_id = await button.get_attribute("id")
                is_disabled = await button.get_attribute("disabled")
                button_type = await button.get_attribute("type")
                tag_name = await button.evaluate("el => el.tagName")

                # Log all button properties
                logger.info(f"  {i+1:2d}. TEXT: '{text_content[:30]}...' | ARIA: '{aria_label}' | TYPE: {button_type} | DISABLED: {is_disabled} | TAG: {tag_name}")
                logger.info(f"     CLASS: {class_name[:80]}..." if class_name else "     CLASS: None")
                logger.info(f"     ID: {button_id}" if button_id else "     ID: None")
                logger.info("     ---")

                # Check if this might be the post button
                is_potential_post_btn = (
                    (text_content and 'post' in text_content.lower()) or
                    (aria_label and 'post' in aria_label.lower()) or
                    (button_type == 'submit') or
                    (text_content and 'share' in text_content.lower()) or
                    (text_content and len(text_content.strip()) > 0 and 'home' not in text_content.lower()
                     and 'cancel' not in text_content.lower() and 'draft' not in text_content.lower())
                )

                if is_potential_post_btn and is_disabled is None:  # Not disabled
                    logger.info(f"     💡 POTENTIAL POST BUTTON: '{text_content[:30]}...' (not disabled)")

            except Exception as e:
                logger.info(f"  {i+1:2d}. Error getting button properties: {e}")

        # Wait for user to inspect the page
        logger.info("Browser staying open for inspection. The correct post button should be visible and enabled now.")
        logger.info("Look for a button that says 'Post', 'Share', or is the primary action button after content is entered.")
        await page.wait_for_timeout(60000)  # Wait 1 minute

        await browser.close()

if __name__ == "__main__":
    asyncio.run(detailed_debug())