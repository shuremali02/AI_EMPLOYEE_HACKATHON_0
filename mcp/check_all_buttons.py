#!/usr/bin/env python3
"""
Script to check all buttons near the content area to identify the correct one
"""
import os
import asyncio
from playwright.async_api import async_playwright
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_all_buttons():
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

        # Fill content to trigger the post button
        test_content = "Testing button detection for LinkedIn automation"
        content_filled = False

        # Try to fill content with role-based selector first
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
            await browser.close()
            return

        # Wait for content to be processed and UI to update
        await page.wait_for_timeout(8000)

        # Now get information about all buttons that could be the post button
        logger.info("🔍 Getting detailed information about all potential post buttons...")

        # Use JavaScript to find all buttons and their positions relative to the content editor
        button_info = await page.evaluate("""
            () => {
                // Find the content editor first
                let contentEditor = document.querySelector('div[contenteditable="true"][role="textbox"]');

                if (!contentEditor) {
                    // Look for any reasonably-sized content editor
                    const editors = Array.from(document.querySelectorAll('div[contenteditable="true"]'));
                    for (const editor of editors) {
                        const rect = editor.getBoundingClientRect();
                        if (rect.width > 100 && rect.height > 30) {
                            contentEditor = editor;
                            break;
                        }
                    }
                }

                if (!contentEditor) {
                    console.log('No content editor found');
                    return { editor: null, buttons: [] };
                }

                const editorRect = contentEditor.getBoundingClientRect();
                console.log('Content editor found at: (' + editorRect.left + ', ' + editorRect.top + ') size: ' + editorRect.width + 'x' + editorRect.height);

                // Get all buttons
                const allButtons = Array.from(document.querySelectorAll('button'));
                const result = {
                    editor: {
                        left: editorRect.left,
                        top: editorRect.top,
                        right: editorRect.right,
                        bottom: editorRect.bottom,
                        width: editorRect.width,
                        height: editorRect.height
                    },
                    buttons: []
                };

                for (const btn of allButtons) {
                    // Get button text and attributes
                    const text = btn.textContent ? btn.textContent.trim() : '';
                    const ariaLabel = btn.getAttribute('aria-label') || '';
                    const type = btn.getAttribute('type') || '';
                    const classes = Array.from(btn.classList).join(' ');
                    const id = btn.getAttribute('id') || '';
                    const isDisabled = btn.disabled || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';
                    const isVisible = btn.offsetParent !== null;

                    // Get button position
                    const btnRect = btn.getBoundingClientRect();
                    const verticalDistance = btnRect.top - editorRect.bottom;  // Positive if below editor
                    const horizontalDistance = btnRect.left - editorRect.right; // Positive if right of editor

                    const isBelowEditor = verticalDistance >= -30 && verticalDistance <= 100;
                    const isRightOfEditor = horizontalDistance >= -50 && horizontalDistance <= 150;
                    const isNearEditor = isBelowEditor && isRightOfEditor;

                    // Check if this looks like a post-related button
                    const isPostRelated = text.toLowerCase().includes('post') ||
                                         text.toLowerCase().includes('share') ||
                                         text.toLowerCase().includes('publish') ||
                                         type === 'submit';

                    // Skip obvious navigation/utility buttons
                    const isNavigation = text.toLowerCase().includes('new posts') ||
                                        text.toLowerCase().includes('home') ||
                                        text.toLowerCase().includes('messaging') ||
                                        text.toLowerCase().includes('notifications');

                    const isUtility = text.toLowerCase().includes('emoji') ||
                                     text.toLowerCase().includes('image') ||
                                     text.toLowerCase().includes('photo') ||
                                     text.toLowerCase().includes('video') ||
                                     text.toLowerCase().includes('gif') ||
                                     text.toLowerCase().includes('mention') ||
                                     text.toLowerCase().includes('draft') ||
                                     text.toLowerCase().includes('save') ||
                                     text.toLowerCase().includes('cancel');

                    result.buttons.push({
                        text: text,
                        ariaLabel: ariaLabel,
                        type: type,
                        classes: classes,
                        id: id,
                        isDisabled: isDisabled,
                        isVisible: isVisible,
                        position: {
                            left: btnRect.left,
                            top: btnRect.top,
                            right: btnRect.right,
                            bottom: btnRect.bottom
                        },
                        distanceFromEditor: {
                            vertical: verticalDistance,
                            horizontal: horizontalDistance
                        },
                        isBelowEditor: isBelowEditor,
                        isRightOfEditor: isRightOfEditor,
                        isNearEditor: isNearEditor,
                        isPostRelated: isPostRelated,
                        isNavigation: isNavigation,
                        isUtility: isUtility,
                        isPotentialPostButton: isPostRelated && !isNavigation && !isUtility && !isDisabled && isVisible && isNearEditor
                    });
                }

                return result;
            }
        """)

        if button_info['editor']:
            logger.info(f"\n📝 Content Editor Position:")
            logger.info(f"  - Position: ({button_info['editor']['left']:.1f}, {button_info['editor']['top']:.1f})")
            logger.info(f"  - Size: {button_info['editor']['width']:.1f} x {button_info['editor']['height']:.1f}")
            logger.info(f"  - Bottom: {button_info['editor']['bottom']:.1f}, Right: {button_info['editor']['right']:.1f}")

        logger.info(f"\n🔍 Found {len(button_info['buttons'])} total buttons on page")

        # Count potential post buttons
        potential_post_buttons = [btn for btn in button_info['buttons'] if btn['isPotentialPostButton']]
        logger.info(f"🎯 Found {len(potential_post_buttons)} potential post buttons near editor:")

        for i, btn in enumerate(potential_post_buttons):
            logger.info(f"  Potential Post Button {i+1}:")
            logger.info(f"    - Text: '{btn['text']}'")
            logger.info(f"    - Type: {btn['type']}")
            logger.info(f"    - Position: ({btn['position']['left']:.1f}, {btn['position']['top']:.1f})")
            logger.info(f"    - Distance from Editor: V:{btn['distanceFromEditor']['vertical']:.1f}, H:{btn['distanceFromEditor']['horizontal']:.1f}")
            logger.info(f"    - Classes: {btn['classes'][:100]}...")
            logger.info(f"    - ID: {btn['id']}")
            logger.info(f"    - ARIA Label: {btn['ariaLabel']}")
            logger.info(f"    ---")

        # Also list all post-related buttons (even if not near editor)
        post_related_buttons = [btn for btn in button_info['buttons'] if btn['isPostRelated'] and not btn['isNavigation'] and not btn['isUtility']]
        logger.info(f"\n📋 All post-related buttons (not navigation/utility): {len(post_related_buttons)}")
        for i, btn in enumerate(post_related_buttons):
            logger.info(f"  Post-Related Button {i+1}:")
            logger.info(f"    - Text: '{btn['text']}'")
            logger.info(f"    - Position: ({btn['position']['left']:.1f}, {btn['position']['top']:.1f})")
            logger.info(f"    - Distance from Editor: V:{btn['distanceFromEditor']['vertical']:.1f}, H:{btn['distanceFromEditor']['horizontal']:.1f}")
            logger.info(f"    - Is near editor: {btn['isNearEditor']}")
            logger.info(f"    - Type: {btn['type']}")
            logger.info(f"    - Disabled: {btn['isDisabled']}")
            logger.info(f"    - Visible: {btn['isVisible']}")
            logger.info(f"    - Classes: {btn['classes'][:100]}...")
            logger.info(f"    ---")

        # Try to click the most likely post button (the one closest to bottom-right of editor that's not disabled)
        if potential_post_buttons:
            # Sort by how close they are to the bottom-right of the editor
            sorted_buttons = sorted(potential_post_buttons,
                                  key=lambda x: abs(x['distanceFromEditor']['vertical']) + abs(x['distanceFromEditor']['horizontal']))

            best_candidate = sorted_buttons[0]
            logger.info(f"\n🎯 Best candidate for Post button:")
            logger.info(f"  - Text: '{best_candidate['text']}'")
            logger.info(f"  - Position: ({best_candidate['position']['left']:.1f}, {best_candidate['position']['top']:.1f})")
            logger.info(f"  - Distance from Editor: V:{best_candidate['distanceFromEditor']['vertical']:.1f}, H:{best_candidate['distanceFromEditor']['horizontal']:.1f}")

            try:
                # Try to click this button - need to properly escape the text
                candidate_text = best_candidate['text'].replace("'", "\\'").replace('"', '\\"')

                # Build the JavaScript string manually to avoid f-string issues
                js_script = """
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const targetText = '{text}';
                        const targetLeft = {left};
                        const targetTop = {top};

                        for (const btn of buttons) {{
                            const text = btn.textContent ? btn.textContent.trim() : '';
                            const btnRect = btn.getBoundingClientRect();

                            // Match the best candidate by position and text
                            if (text === targetText &&
                                Math.abs(btnRect.left - targetLeft) < 10 &&
                                Math.abs(btnRect.top - targetTop) < 10) {{

                                console.log('Clicking best candidate: ' + text);

                                btn.scrollIntoView({{block: 'nearest', inline: 'nearest'}});
                                btn.focus();

                                // Click twice to ensure registration
                                btn.click();
                                setTimeout(() => btn.click(), 200);

                                return {{ clicked: true, text: text }};
                            }}
                        }}
                        return {{ clicked: false, text: targetText }};
                    }
                """.format(text=candidate_text, left=best_candidate['position']['left'], top=best_candidate['position']['top'])

                result = await page.evaluate(js_script)

                if result['clicked']:
                    logger.info(f"✅ Successfully clicked the best candidate: '{result['text']}'")
                    logger.info("Wait to see if post was published...")
                    await page.wait_for_timeout(10000)
                else:
                    logger.info("❌ Could not find the best candidate button to click")

            except Exception as e:
                logger.error(f"Error clicking best candidate: {e}")

        else:
            logger.info("\n❌ No potential post buttons found near the editor")

        logger.info("\n💡 The browser will stay open so you can manually inspect the UI.")
        await page.wait_for_timeout(300000)  # Wait 5 minutes

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_all_buttons())