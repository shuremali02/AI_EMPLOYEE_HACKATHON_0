#!/usr/bin/env python3
"""
Updated diagnostic script to see what elements are available after clicking 'Start a post' and filling content
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

        # Wait for login to complete, allowing for security verification
        try:
            # Wait for either the feed page or a security verification page
            await page.wait_for_timeout(10000)  # Wait for navigation to occur

            current_url = page.url
            logger.info(f"Current URL after login: {current_url}")

            if "checkpoint" in current_url or "challenge" in current_url:
                logger.info("Security verification required. Please complete in browser.")
                logger.info("Waiting for manual verification for 5 minutes...")
                await page.wait_for_timeout(300000)  # Wait 5 mins for manual verification
            else:
                # Wait for feed if not redirected to checkpoint
                try:
                    await page.wait_for_url("https://www.linkedin.com/feed/", timeout=15000)
                    logger.info("✅ Successfully logged in!")
                except:
                    logger.info("Continuing with current page after login attempt")
        except Exception as e:
            logger.info(f"Login check completed. Current URL: {page.url}")

        # Wait for page to fully load
        await page.wait_for_timeout(5000)

        # Wait a bit more for the full feed to load
        await page.wait_for_timeout(5000)

        # Click 'Start a post' button using the working selector
        logger.info("🔍 Looking for and clicking 'Start a post' button...")
        button_clicked = False

        # First try: Find the button by its visible text content
        try:
            # Try to click an element that has "Start a post" as its text
            start_post_button = await page.wait_for_selector("text='Start a post'", timeout=10000)
            if start_post_button:
                await start_post_button.click()
                logger.info("✅ Successfully clicked 'Start a post' button by text selector")
                button_clicked = True
        except Exception as e:
            logger.info(f"Could not find 'Start a post' button by text selector: {e}")

        # If the above didn't work, try other approaches
        if not button_clicked:
            # Try to find the element containing the text and get its parent/ancestor buttons
            try:
                # First, find the element that contains "Start a post"
                elements_with_text = await page.query_selector_all("*:has-text('Start a post')")
                for element in elements_with_text:
                    try:
                        # Get the element's tag to better understand its structure
                        tag_name = await element.evaluate("el => el.tagName")

                        # If it's already a button or clickable element, try clicking it
                        if tag_name.lower() in ['button', 'div', 'span', 'a']:
                            await element.click()
                            logger.info(f"Clicked element containing 'Start a post' (tag: {tag_name})")
                            button_clicked = True
                            break
                    except Exception as e:
                        logger.info(f"Error clicking element: {e}")
                        continue
            except Exception as e:
                logger.info(f"Error in text-based search: {e}")

        if not button_clicked:
            logger.error("❌ Could not find 'Start a post' button")
            await browser.close()
            return

        # Wait for the share box to appear
        await page.wait_for_timeout(8000)

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
            except Exception as e:
                logger.info(f"Could not fill content with selector: {selector} - {e}")
                continue

        if not content_filled:
            logger.error("❌ Could not fill content area")

            # Try a JavaScript approach as fallback
            try:
                result = await page.evaluate("""
                    () => {
                        // Find any content editable area
                        const editors = Array.from(document.querySelectorAll('div[contenteditable="true"]'));

                        for (const editor of editors) {
                            // Check if this looks like the main post editor by examining its container
                            const rect = editor.getBoundingClientRect();
                            const isLargeEnough = rect.width > 200 && rect.height > 30; // Likely a content editor

                            if (isLargeEnough) {
                                // Focus the editor
                                editor.focus();

                                // Clear and set content
                                editor.innerHTML = '';
                                const textNode = document.createTextNode(arguments[0]);
                                editor.appendChild(textNode);

                                // Trigger input event to notify React/Vue frameworks
                                const inputEvent = new Event('input', { bubbles: true });
                                editor.dispatchEvent(inputEvent);

                                return { success: true, elementFound: true, method: 'javascript_fill' };
                            }
                        }

                        return { success: false, elementFound: false };
                    }
                """, test_content)

                if result['success']:
                    logger.info(f"✅ Successfully filled content using JavaScript")
                    content_filled = True
                else:
                    logger.error("❌ Could not find any content editor to fill")
            except Exception as e:
                logger.error(f"JavaScript content filling failed: {e}")

        if not content_filled:
            await browser.close()
            return

        # Wait for the content to be processed and post button to appear
        await page.wait_for_timeout(8000)

        # Now let's investigate the structure of the share box and find all potential post buttons
        logger.info("🔍 DIAGNOSIS: Examining the share composition UI structure after content is filled...")

        # Get all buttons on the page
        all_buttons = await page.query_selector_all("button")
        logger.info(f"Found {len(all_buttons)} buttons on the page:")

        # Get the content editor position to compare
        content_editor = await page.query_selector("div[contenteditable='true'][role='textbox']")
        if not content_editor:
            content_editor = await page.query_selector("div[contenteditable='true']")

        editor_info = None
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
                    editor_info = {
                        'x': editor_x, 'y': editor_y,
                        'width': editor_width, 'height': editor_height,
                        'bottom': editor_bottom, 'right': editor_right
                    }
                else:
                    editor_x, editor_y, editor_width, editor_height = 0, 0, 0, 0
                    editor_bottom, editor_right = 0, 0
                    editor_info = None

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

        # Get all button information with relative positioning to editor
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
                        btn_x, btn_y = bounding_box['x'], bounding_box['y']
                        btn_width, btn_height = bounding_box['width'], bounding_box['height']
                        btn_bottom = btn_y + btn_height
                        btn_right = btn_x + btn_width
                    else:
                        btn_x, btn_y = 0, 0
                        btn_bottom, btn_right = 0, 0
                except:
                    btn_x, btn_y = 0, 0
                    btn_bottom, btn_right = 0, 0

                # Calculate relative position to editor if available
                if editor_info:
                    vertical_distance = btn_y - editor_info['bottom']  # Positive if below editor
                    horizontal_distance = btn_x - editor_info['right']  # Positive if right of editor
                    is_below_editor = vertical_distance > -30  # Allow some overlap
                    is_right_of_editor = horizontal_distance > -50  # Allow some overlap
                    near_bottom_right = is_below_editor and is_right_of_editor
                else:
                    vertical_distance, horizontal_distance = 0, 0
                    is_below_editor, is_right_of_editor = False, False
                    near_bottom_right = False

                logger.info(f"\n  Button {i+1}:")
                logger.info(f"    - Text: '{text_content.strip()}'")
                logger.info(f"    - ID: {button_id}")
                logger.info(f"    - Class: {button_class}")
                logger.info(f"    - ARIA Label: {button_aria_label}")
                logger.info(f"    - Type: {button_type}")
                logger.info(f"    - Disabled: {is_disabled} / ARIA Disabled: {is_aria_disabled}")
                logger.info(f"    - Visible: {is_visible}")
                logger.info(f"    - Position: ({btn_x}, {btn_y}) to ({btn_right}, {btn_bottom})")
                if editor_info:
                    logger.info(f"    - Distance from Editor Bottom: {vertical_distance}, from Right: {horizontal_distance}")
                    logger.info(f"    - Below Editor: {is_below_editor}, Right of Editor: {is_right_of_editor}")
                    logger.info(f"    - Near Bottom-Right: {near_bottom_right}")
                logger.info(f"    ---")

                # Log if this is a potential post button
                text_lower = text_content.lower() if text_content else ""
                if "post" in text_lower or "share" in text_lower or button_type == "submit":
                    if not ("new posts" in text_lower or "home" in text_lower or "messaging" in text_lower):
                        logger.info(f"    🎯 POTENTIAL POST BUTTON FOUND: '{text_content.strip()}' at ({btn_x}, {btn_y})")

            except Exception as e:
                logger.info(f"  Button {i+1}: Error getting properties: {e}")

        # Run JavaScript to get all share-related elements
        try:
            logger.info("\n🔍 Running JavaScript to identify share-related elements...")
            js_result = await page.evaluate("""
                () => {
                    const elements = [];

                    // Get all divs, buttons, and other elements that might be related to sharing
                    const allElements = Array.from(document.querySelectorAll('div, button, span, p'));

                    for (const el of allElements) {
                        const text = el.textContent ? el.textContent.toLowerCase() : '';
                        const classes = el.className ? el.className.toLowerCase() : '';
                        const id = el.id ? el.id.toLowerCase() : '';
                        const tag = el.tagName.toLowerCase();

                        // Look for share-related elements
                        if (text.includes('post') || text.includes('share') || text.includes('publish') ||
                            classes.includes('share') || classes.includes('post') || classes.includes('create') ||
                            id.includes('share') || id.includes('post') || id.includes('create')) {

                            const rect = el.getBoundingClientRect();
                            elements.push({
                                tag: tag,
                                text: el.textContent ? el.textContent.substring(0, 50) : '',
                                classes: classes.substring(0, 100),
                                id: id,
                                position: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
                                isButton: el.tagName.toLowerCase() === 'button'
                            });
                        }
                    }

                    return elements;
                }
            """)

            logger.info(f"Found {len(js_result)} share-related elements:")
            for i, el in enumerate(js_result):
                logger.info(f"  Element {i+1}: {el['tag']} - '{el['text'][:30]}...' - isButton: {el['isButton']}")
                logger.info(f"    - Position: ({el['position']['x']}, {el['position']['y']})")
                logger.info(f"    - Classes: {el['classes'][:80]}")
        except Exception as e:
            logger.error(f"Error in JavaScript element search: {e}")

        logger.info("\n💡 The browser will stay open so you can manually inspect the UI elements.")
        logger.info("   Look for the post button near the bottom-right of the content area.")
        await page.wait_for_timeout(300000)  # Wait 5 minutes

        await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose_post_ui())