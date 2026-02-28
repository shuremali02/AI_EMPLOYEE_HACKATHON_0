#!/usr/bin/env python3
"""
Diagnostic script to see what elements are available after clicking 'Start a post' and filling content
"""
import os
import asyncio
from playwright.async_api import async_playwright
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def diagnose_post_ui():
    email = os.getenv('LINKEDIN_EMAIL', 'shuremsyed41@gmail.com')
    password = os.getenv('LINKEDIN_PASSWORD', '477831@dit')

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

        # Fill some content to trigger the post button
        test_content = "Testing content to see post button positioning"
        content_filled = False

        # Try to fill content with multiple selectors
        content_selectors = [
            "div[contenteditable='true'][role='textbox']",
            "div[contenteditable='true']",
            "div[role='textbox']"
        ]

        for selector in content_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    await element.click()
                    await element.focus()
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Delete")
                    await element.fill(test_content)
                    logger.info(f"✅ Successfully filled content with selector: {selector}")
                    content_filled = True
                    break
            except:
                logger.info(f"Could not fill content with selector: {selector}")
                continue

        if not content_filled:
            logger.error("❌ Could not fill content area")
            await browser.close()
            return

        # Wait for the content to be processed and post button to appear
        await page.wait_for_timeout(5000)

        # Now let's investigate the structure of the share box and find all potential post buttons
        logger.info("🔍 DIAGNOSIS: Examining the share composition UI structure after content is filled...")

        # Get all buttons on the page
        all_buttons = await page.query_selector_all("button")
        logger.info(f"Found {len(all_buttons)} buttons on the page:")

        for i, button in enumerate(all_buttons):
            try:
                text_content = await button.text_content()
                button_id = await button.get_attribute("id")
                button_class = await button.get_attribute("class")
                button_aria_label = await button.get_attribute("aria-label")
                button_type = await button.get_attribute("type")
                is_disabled = await button.get_attribute("disabled")
                is_aria_disabled = await button.get_attribute("aria-disabled")
                is_visible = await button.is_visible()

                # Get button position
                try:
                    bounding_box = await button.bounding_box()
                    if bounding_box:
                        x, y = bounding_box['x'], bounding_box['y']
                    else:
                        x, y = 0, 0
                except:
                    x, y = 0, 0

                logger.info(f"  Button {i+1}:")
                logger.info(f"    - Text: '{text_content.strip()}'")
                logger.info(f"    - ID: {button_id}")
                logger.info(f"    - Class: {button_class}")
                logger.info(f"    - ARIA Label: {button_aria_label}")
                logger.info(f"    - Type: {button_type}")
                logger.info(f"    - Disabled: {is_disabled} / ARIA Disabled: {is_aria_disabled}")
                logger.info(f"    - Visible: {is_visible}")
                logger.info(f"    - Position: ({x}, {y})")
                logger.info(f"    ---")
            except Exception as e:
                logger.info(f"  Button {i+1}: Error getting properties: {e}")

        # Now get the content editor position to compare
        content_editor = await page.query_selector("div[contenteditable='true'][role='textbox']")
        if not content_editor:
            content_editor = await page.query_selector("div[contenteditable='true']")

        if content_editor:
            try:
                editor_text = await content_editor.text_content()
                editor_id = await content_editor.get_attribute("id")
                editor_class = await content_editor.get_attribute("class")

                # Get editor position
                bounding_box = await content_editor.bounding_box()
                if bounding_box:
                    editor_x, editor_y = bounding_box['x'], bounding_box['y']
                    editor_width, editor_height = bounding_box['width'], bounding_box['height']
                    editor_bottom = editor_y + editor_height
                    editor_right = editor_x + editor_width
                else:
                    editor_x, editor_y, editor_width, editor_height = 0, 0, 0, 0
                    editor_bottom, editor_right = 0, 0

                logger.info(f"\nContent Editor:")
                logger.info(f"  - ID: {editor_id}")
                logger.info(f"  - Class: {editor_class}")
                logger.info(f"  - Position: ({editor_x}, {editor_y})")
                logger.info(f"  - Size: {editor_width} x {editor_height}")
                logger.info(f"  - Bottom: {editor_bottom}, Right: {editor_right}")
                logger.info(f"  - Text content (first 100 chars): '{editor_text[:100]}...'")
            except Exception as e:
                logger.info(f"Error getting editor properties: {e}")
        else:
            logger.info("No content editor found")

        logger.info("\n💡 The browser will stay open so you can manually inspect the UI elements.")
        logger.info("   Look for the post button near the bottom-right of the content area.")
        await page.wait_for_timeout(300000)  # Wait 5 minutes

        await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose_post_ui())