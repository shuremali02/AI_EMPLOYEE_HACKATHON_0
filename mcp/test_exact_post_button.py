#!/usr/bin/env python3
"""
Targeted test to find and click the exact "Post" button
"""
import os
import asyncio
from playwright.async_api import async_playwright
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_exact_post_button():
    email = os.getenv('LINKEDIN_EMAIL', 'shuremsyed41@gmail.com')
    password = os.getenv('LINKEDIN_PASSWORD', '477831@dit')

    if not email or not password:
        logger.error("LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables must be set")
        return

    async with async_playwright() as p:
        # Launch browser in non-headless mode
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
            current_url = page.url
            logger.info(f"Current URL after login: {current_url}")
            if "checkpoint" in current_url or "challenge" in current_url:
                logger.info("Security verification required. Please complete in browser.")
                await page.wait_for_timeout(300000)  # Wait 5 mins for manual verification
            elif "feed" not in current_url:
                logger.info("Login might have failed or took longer than expected.")
                await page.wait_for_timeout(10000)

        # Wait for page to fully load
        await page.wait_for_timeout(5000)

        # Wait a bit more for the full feed to load
        await page.wait_for_timeout(5000)

        # Click 'Start a post' button
        logger.info("🔍 Looking for and clicking 'Start a post' button...")
        button_clicked = False

        # Try to find the button by its visible text content
        try:
            start_post_button = await page.wait_for_selector("text='Start a post'", timeout=10000)
            if start_post_button:
                await start_post_button.click()
                logger.info("✅ Successfully clicked 'Start a post' button by text selector")
                button_clicked = True
        except Exception as e:
            logger.info(f"Could not find 'Start a post' button by text selector: {e}")

        if not button_clicked:
            logger.error("❌ Could not find 'Start a post' button")
            await browser.close()
            return

        # Wait for the share box to appear
        await page.wait_for_timeout(8000)

        # Fill content
        test_content = "Testing the exact post button functionality for LinkedIn automation"
        content_filled = False

        # Try to fill content with role-based selector first
        content_selectors = [
            "div[contenteditable='true'][role='textbox']",
            "div[contenteditable='true'][data-testid='orbit-textarea']",
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
            await browser.close()
            return

        # Wait for content to be processed and UI to update
        await page.wait_for_timeout(8000)

        # Now try multiple approaches to find and click the exact "Post" button
        logger.info("🔍 Attempting to find and click the exact 'Post' button...")

        # Method 1: Specific selector for the main post button
        post_selectors = [
            "button:has-text('Post'):not(:has-text('New posts')):not([disabled]):not([aria-disabled='true'])",
            "button.artdeco-button--primary:has-text('Post')",
            "button[data-control-name='share.publish']:has-text('Post')",
            "button[data-test-id='share-post-publish-button']:has-text('Post')",
            "button[type='submit']:has-text('Post')",
            "button:has-text('Post')[type='button']:not([disabled])"
        ]

        for selector in post_selectors:
            try:
                logger.info(f"Trying selector: {selector}")
                button = await page.wait_for_selector(selector, timeout=5000)
                if button:
                    await button.click()
                    await page.wait_for_timeout(500)  # Brief pause
                    await button.click()  # Click again to ensure registration
                    logger.info(f"✅ Successfully clicked Post button with selector: {selector}")

                    # Wait to see if the post was published
                    await page.wait_for_timeout(10000)
                    logger.info("✅ Post operation completed successfully!")
                    await browser.close()
                    return
            except Exception as e:
                logger.info(f"Selector failed: {selector} - {str(e)[:100]}...")

        # Method 2: JavaScript approach to find the exact "Post" button
        try:
            logger.info("🔍 Using JavaScript to find the exact 'Post' button...")
            result = await page.evaluate("""
                () => {
                    // Find all buttons
                    const buttons = Array.from(document.querySelectorAll('button'));

                    // Look for buttons that have exactly the text "Post" (not containing it)
                    for (const btn of buttons) {
                        const text = btn.textContent ? btn.textContent.trim() : '';

                        // Look for exact "Post" text (not "New posts", "Repost", etc.)
                        if (text === 'Post') {
                            const isDisabled = btn.disabled || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';

                            if (!isDisabled) {
                                console.log('Found exact "Post" button:', text);

                                // Scroll into view and click
                                btn.scrollIntoView({block: 'nearest', inline: 'nearest'});
                                btn.focus();

                                // Click twice to ensure it registers
                                btn.click();
                                setTimeout(() => btn.click(), 200);

                                return { found: true, text: text, clicked: true };
                            }
                        }
                    }

                    // If no exact "Post" found, look for buttons with "Post" that aren't navigation
                    for (const btn of buttons) {
                        const text = btn.textContent ? btn.textContent.trim().toLowerCase() : '';
                        const isDisabled = btn.disabled || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';

                        if (text.includes('post') &&
                            !text.includes('new posts') &&
                            !text.includes('repost') &&
                            !isDisabled) {

                            console.log('Found "Post" related button:', btn.textContent.trim());

                            btn.scrollIntoView({block: 'nearest', inline: 'nearest'});
                            btn.focus();
                            btn.click();
                            setTimeout(() => btn.click(), 200);

                            return { found: true, text: btn.textContent.trim(), clicked: true };
                        }
                    }

                    return { found: false, totalButtons: buttons.length };
                }
            """)

            if result['found'] and result['clicked']:
                logger.info(f"✅ Successfully clicked Post button via JavaScript: '{result['text']}'")

                # Wait to see if the post was published
                await page.wait_for_timeout(10000)
                logger.info("✅ Post operation completed successfully!")
                await browser.close()
                return
            else:
                logger.info(f"JavaScript approach: Not found (checked {result.get('totalButtons', 0)} buttons)")

        except Exception as e:
            logger.error(f"Error in JavaScript approach: {e}")

        # Method 3: If nothing else works, try to click the first submit button that's not navigation
        try:
            logger.info("🔍 Trying submit button approach...")
            result = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button[type="submit"]'));

                    for (const btn of buttons) {
                        const text = btn.textContent ? btn.textContent.trim().toLowerCase() : '';
                        const isDisabled = btn.disabled || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';

                        // Skip navigation submit buttons
                        if (!isDisabled && !text.includes('new posts') && !text.includes('home')) {
                            console.log('Found submit button to click:', btn.textContent.trim());

                            btn.scrollIntoView({block: 'nearest', inline: 'nearest'});
                            btn.focus();
                            btn.click();
                            setTimeout(() => btn.click(), 200);

                            return { found: true, text: btn.textContent.trim(), clicked: true };
                        }
                    }

                    return { found: false };
                }
            """)

            if result['found'] and result['clicked']:
                logger.info(f"✅ Successfully clicked submit button: '{result['text']}'")

                # Wait to see if the post was published
                await page.wait_for_timeout(10000)
                logger.info("✅ Post operation completed successfully!")
                await browser.close()
                return

        except Exception as e:
            logger.error(f"Error in submit button approach: {e}")

        logger.info("❌ Could not find or click the Post button")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_exact_post_button())