#!/usr/bin/env python3
"""
UI diagnosis script to see what elements are available after clicking 'Start a post'
"""
import os
import asyncio
from playwright.async_api import async_playwright
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def diagnose_ui():
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

        # Now let's investigate the structure of the share box
        logger.info("🔍 DIAGNOSIS: Examining the share composition UI structure...")

        # Get all contenteditable divs
        content_editors = await page.query_selector_all("div[contenteditable='true']")
        logger.info(f"Found {len(content_editors)} content editable elements:")

        for i, editor in enumerate(content_editors):
            try:
                editor_text = await editor.text_content()
                editor_id = await editor.get_attribute("id")
                editor_class = await editor.get_attribute("class")
                editor_aria_label = await editor.get_attribute("aria-label")
                editor_placeholder = await editor.get_attribute("placeholder")
                is_visible = await editor.is_visible()

                logger.info(f"  Editor {i+1}:")
                logger.info(f"    - ID: {editor_id}")
                logger.info(f"    - Class: {editor_class}")
                logger.info(f"    - ARIA Label: {editor_aria_label}")
                logger.info(f"    - Placeholder: {editor_placeholder}")
                logger.info(f"    - Visible: {is_visible}")
                logger.info(f"    - Text content (first 100 chars): '{editor_text[:100]}...'")
                logger.info("    ---")
            except Exception as e:
                logger.info(f"  Editor {i+1}: Error getting properties: {e}")

        # Get all elements with textbox role
        textbox_elements = await page.query_selector_all("[role='textbox']")
        logger.info(f"Found {len(textbox_elements)} elements with textbox role:")

        for i, textbox in enumerate(textbox_elements):
            try:
                text_content = await textbox.text_content()
                textbox_id = await textbox.get_attribute("id")
                textbox_class = await textbox.get_attribute("class")
                textbox_aria_label = await textbox.get_attribute("aria-label")
                is_visible = await textbox.is_visible()

                logger.info(f"  Textbox {i+1}:")
                logger.info(f"    - ID: {textbox_id}")
                logger.info(f"    - Class: {textbox_class}")
                logger.info(f"    - ARIA Label: {textbox_aria_label}")
                logger.info(f"    - Visible: {is_visible}")
                logger.info(f"    - Text content (first 100 chars): '{text_content[:100]}...'")
                logger.info("    ---")
            except Exception as e:
                logger.info(f"  Textbox {i+1}: Error getting properties: {e}")

        # Get the HTML structure of the main share area
        try:
            share_area_html = await page.evaluate("document.querySelector('body').outerHTML")
            # Look for elements that might contain the share box
            import re
            possible_share_elements = re.findall(r'<div[^>]*class="[^"]*?(?:share|post|create)[^"]*?"[^>]*>.*?</div>', share_area_html, re.IGNORECASE | re.DOTALL)
            logger.info(f"Found {len(possible_share_elements)} possible share-related elements in the HTML")

            for i, element in enumerate(possible_share_elements[-5:]):  # Show last 5 elements
                logger.info(f"  Possible share element {i+1}: {element[:200]}...")

        except Exception as e:
            logger.error(f"Error getting share area HTML: {e}")

        logger.info("\n💡 The browser will stay open so you can inspect the current LinkedIn UI manually.")
        logger.info("   Look for the text input area where you write the post content.")
        await page.wait_for_timeout(120000)  # Wait 2 minutes

        await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose_ui())