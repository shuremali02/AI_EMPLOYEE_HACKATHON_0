#!/usr/bin/env python3
"""
LinkedIn MCP Server
Model Context Protocol server for creating LinkedIn posts via browser automation
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any, List
from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkedInMCPServer:
    def __init__(self):
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')

        if not self.email or not self.password:
            logger.error("LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables must be set")
            sys.exit(1)

    async def post_linkedin(self, text: str, **kwargs) -> Dict[str, Any]:
        """Create a LinkedIn post via browser automation"""
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=False)  # Changed to headless=False for better visibility
                page = await browser.new_page()

                # Go to LinkedIn login page
                await page.goto("https://www.linkedin.com/login")

                # Fill in login credentials
                await page.fill("input#username", self.email)
                await page.fill("input#password", self.password)

                # Click login button
                await page.click("button[type='submit']")

                # Wait for login to complete with extended timeout and check for verification
                try:
                    await page.wait_for_url("https://www.linkedin.com/feed/", timeout=30000)
                    logger.info("Successfully logged in!")
                except:
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

                # Search for the exact text "Start a post" which we know exists from debugging
                # Looking more carefully at the debug output, "Start a post" appears in the UI
                button_clicked = False

                # First try: Find the button by its visible text content
                try:
                    # Try to click an element that has "Start a post" as its text
                    start_post_button = await page.wait_for_selector("text='Start a post'", timeout=10000)
                    if start_post_button:
                        await start_post_button.click()
                        logger.info("Successfully clicked 'Start a post' button by text selector")
                        button_clicked = True
                except:
                    logger.info("Could not find 'Start a post' button by text selector")

                # If the above didn't work, try other approaches
                if not button_clicked:
                    # Try to find the element containing the text and get its parent/ancestor buttons
                    try:
                        # First, find the element that contains "Start a post"
                        elements_with_text = await page.query_selector_all("*")
                        for element in elements_with_text:
                            try:
                                text_content = await element.text_content()
                                if 'start a post' in text_content.lower():
                                    # Get the element's tag to better understand its structure
                                    tag_name = await element.evaluate("el => el.tagName")

                                    # If it's already a button or clickable element, try clicking it
                                    if tag_name.lower() in ['button', 'div', 'span', 'a']:
                                        await element.click()
                                        logger.info(f"Clicked element containing 'Start a post' (tag: {tag_name})")
                                        button_clicked = True
                                        break

                                    # Otherwise, look for clickable parent elements
                                    else:
                                        # Look for the closest parent that might be a clickable container
                                        try:
                                            parent = await element.evaluate_handle("el => el.closest('button, [role=\"button\"], div[onclick], a[role=\"button\"]')")
                                            if parent:
                                                await parent.click()
                                                logger.info("Clicked parent element of 'Start a post' text")
                                                button_clicked = True
                                                break
                                        except:
                                            continue
                            except:
                                continue
                    except Exception as e:
                        logger.info(f"Error in text-based search: {e}")

                # If still not found, try the traditional selectors
                if not button_clicked:
                    button_selectors = [
                        "button:has-text('Start a post')",
                        "button[aria-label='Create a post']",
                        "button[aria-label='Share an update']",
                        "[data-test-id='share-box-feed-entry']",
                        ".share-box-feed-entry__trigger",
                        "button[data-test='share-box-feed-entry']",
                        # New selectors based on common LinkedIn UI patterns
                        "button.share-box-feed-entry__trigger",
                        "[data-test-id='share-box-feed-entry'] button",
                        ".global-rail-v2__feed-content .share-box-feed-entry__container",
                        ".share-box-feed-entry__container button",
                        "button:has-text('Share an article')",
                        "button[data-test-shares-create-destination-type='FEED']",
                        ".share-box-feed-entry__container",
                        "div.share-box-feed-entry__container button:first-child"
                    ]

                    for selector in button_selectors:
                        try:
                            element = await page.wait_for_selector(selector, timeout=10000)
                            if element:
                                await element.click()
                                logger.info(f"Successfully clicked post button with selector: {selector}")
                                button_clicked = True
                                break
                        except:
                            logger.info(f"Could not click with selector: {selector}")
                            continue

                if not button_clicked:
                    logger.error("Could not find any post creation button")
                    # Let's use JavaScript to find and click the element based on text content
                    try:
                        # Execute JavaScript to find the element containing "Start a post" and click it
                        result = await page.evaluate("""
                            () => {
                                // Find all elements that might be clickable and contain the text
                                const elements = Array.from(document.querySelectorAll('button, [role="button"], div, span, a'));
                                const targetElement = elements.find(el =>
                                    el.textContent &&
                                    el.textContent.toLowerCase().includes('start a post') &&
                                    (el.tagName.toLowerCase() === 'button' ||
                                     el.getAttribute('role') === 'button' ||
                                     window.getComputedStyle(el).cursor === 'pointer')
                                );

                                if (targetElement) {
                                    // Try to click the found element
                                    targetElement.click();
                                    return { found: true, text: targetElement.textContent, tag: targetElement.tagName };
                                }
                                return { found: false };
                            }
                        """)

                        if result['found']:
                            logger.info(f"Clicked element via JavaScript: {result['text'][:50]}... (tag: {result['tag']})")
                            button_clicked = True
                        else:
                            logger.info("Could not find post creation element using JavaScript search")

                    except Exception as e:
                        logger.error(f"Error in JavaScript element search: {e}")

                if not button_clicked:
                    logger.error("Could not find any post creation element")
                    # As a last resort, try to find the main share text area directly
                    try:
                        # Sometimes the share box is already expanded - look for the content editor
                        content_editor = await page.query_selector("div[contenteditable='true'][data-test='share-content-editor']")
                        if content_editor:
                            logger.info("Found content editor directly, skipping button click")
                            button_clicked = True
                        else:
                            # Look for any content editable area in a share context
                            content_editables = await page.query_selector_all("div[contenteditable='true']")
                            for editor in content_editables:
                                parent = await editor.query_selector("xpath=../..")  # Go up two levels
                                if parent:
                                    parent_class = await parent.get_attribute("class")
                                    if parent_class and any(word in parent_class.lower() for word in ['share', 'post', 'create']):
                                        await editor.click()
                                        logger.info("Clicked content editor in share context")
                                        button_clicked = True
                                        break
                    except:
                        logger.info("Could not find content editor directly")

                if not button_clicked:
                    await browser.close()
                    return {
                        "success": False,
                        "error": "Could not find post creation button"
                    }

                # Wait for the editor to appear
                await page.wait_for_timeout(5000)

                # Fill the post content using multiple selector approaches
                content_filled = False
                content_selectors = [
                    "div[contenteditable='true'][role='textbox']",
                    "div[contenteditable='true'][data-test='share-content-editor']",
                    "div[contenteditable='true']:not([tabindex='-1'])",  # Exclude read-only contenteditables
                    "div[role='textbox']",
                    "div[contenteditable='true']",
                    # Broader selectors for current LinkedIn UI
                    "div[aria-label*='share' i]",
                    "div[aria-label*='post' i]",
                    "div[aria-label*='create' i]",
                    "div[data-test*='content' i]",
                    "div[aria-describedby*='content' i]"
                ]

                for selector in content_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=8000)
                        if element:
                            # Focus and interact with the content area
                            await element.click()
                            await element.focus()

                            # Select all and clear content
                            await page.keyboard.press("Control+A")
                            await page.keyboard.press("Delete")

                            # Fill content with increased timeout for longer posts
                            await element.fill(text)
                            logger.info(f"✅ Successfully filled content with selector: {selector}")
                            content_filled = True
                            break
                    except Exception as e:
                        logger.info(f"Could not fill content with selector: {selector} - {str(e)[:80]}...")
                        continue

                # Fallback approach if standard selectors fail
                if not content_filled:
                    try:
                        # Try to find any content editable area and use type method
                        content_editables = await page.query_selector_all("div[contenteditable='true']")

                        for editor in content_editables:
                            try:
                                # Check if this editor is in a likely share/post area
                                parent_element = await editor.query_selector("xpath=../..")
                                if parent_element:
                                    parent_class = await parent_element.get_attribute("class") or ""
                                    parent_id = await parent_element.get_attribute("id") or ""

                                    # Check if parent suggests this is a share area
                                    is_share_area = any(keyword in parent_class.lower() or keyword in parent_id.lower()
                                                      for keyword in ['share', 'post', 'create', 'editor'])

                                    if is_share_area:
                                        await editor.click()
                                        await editor.focus()
                                        await page.keyboard.press("Control+A")
                                        await page.keyboard.press("Delete")
                                        await editor.type(text)
                                        content_filled = True
                                        logger.info("✅ Successfully filled content using share-area detected editor")
                                        break
                            except:
                                continue
                    except Exception as e:
                        logger.info(f"Share-area detection method failed: {e}")

                # Last resort: try JavaScript to insert content
                if not content_filled:
                    try:
                        js_result = await page.evaluate("""
                            () => {
                                // Find the main content editor
                                const editors = Array.from(document.querySelectorAll('div[contenteditable="true"]'));

                                for (const editor of editors) {
                                    // Check if this looks like the main post editor by examining its container
                                    const rect = editor.getBoundingClientRect();
                                    const isLargeEnough = rect.width > 200 && rect.height > 50; // Likely a main editor
                                    const hasPlaceholder = editor.getAttribute('placeholder') ||
                                                         editor.getAttribute('aria-label');

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

                                        return { success: true, method: 'main_editor' };
                                    }
                                }

                                // If no main editor found, just use the first content editable
                                if (editors.length > 0) {
                                    const editor = editors[0];
                                    editor.focus();
                                    editor.innerHTML = '';
                                    const textNode = document.createTextNode(arguments[0]);
                                    editor.appendChild(textNode);

                                    const inputEvent = new Event('input', { bubbles: true });
                                    editor.dispatchEvent(inputEvent);

                                    return { success: true, method: 'fallback_editor' };
                                }

                                return { success: false, method: 'none' };
                            }
                        """, text)

                        if js_result['success']:
                            logger.info(f"✅ Successfully filled content using JavaScript: {js_result['method']}")
                            content_filled = True
                    except Exception as e:
                        logger.error(f"JavaScript content insertion failed: {e}")

                if not content_filled:
                    logger.error("❌ Could not find or fill content editor - post creation failed")
                    await browser.close()
                    return {
                        "success": False,
                        "error": "Could not find content editor to fill"
                    }

                # Wait for the content to be processed by the UI and for the post button to become enabled
                logger.info("⏳ Waiting for content to be processed and post button to become active...")
                await page.wait_for_timeout(8000)  # Increased timeout as per user's feedback about browser closing during typing

                if not content_filled:
                    await browser.close()
                    return {
                        "success": False,
                        "error": "Could not find content editor"
                    }

                # Wait for content to be processed
                await page.wait_for_timeout(3000)

                # Wait for the content to be processed and post button to appear/enabled
                await page.wait_for_timeout(7000)

                # Focused approach for the main post button - this is the final publish button
                post_clicked = False

                # According to user clarification: after "Start a post" is clicked, content is written in a popup,
                # and then there's a "Post" button in that same popup area - let's focus on that
                logger.info("🔍 Looking for the Post button in the share composition popup/box...")

                # Wait a bit more for the post button to become active/enabled after content is entered
                # The button typically starts as disabled and becomes enabled after text is entered
                await page.wait_for_timeout(3000)

                # Before looking for the post button, verify the content editor still exists
                content_editor_exists = await page.evaluate("""
                    () => {
                        const contentEditor = document.querySelector('div[contenteditable="true"][role="textbox"]');
                        if (contentEditor) {
                            console.log('Content editor found with text: ' + contentEditor.textContent.substring(0, 50));
                            const rect = contentEditor.getBoundingClientRect();
                            console.log('Content editor position: top=' + rect.top + ', left=' + rect.left + ', bottom=' + rect.bottom + ', right=' + rect.right);
                            return true;
                        }
                        console.log('Content editor NOT found');

                        // Look for any content editable elements
                        const allEditable = document.querySelectorAll('div[contenteditable="true"]');
                        console.log('Found ' + allEditable.length + ' content editable elements');
                        for (let i = 0; i < allEditable.length; i++) {
                            const el = allEditable[i];
                            const text = el.textContent.substring(0, 30);
                            const classes = el.className;
                            const rect = el.getBoundingClientRect();
                            console.log('Editable ' + i + ': "' + text + '..." class: ' + classes + ' at (' + rect.top + ',' + rect.left + ')');
                        }

                        // Look for share-related elements
                        const shareElements = document.querySelectorAll('div, button, span');
                        let foundShareElements = 0;
                        for (let i = 0; i < shareElements.length && foundShareElements < 5; i++) {
                            const el = shareElements[i];
                            const text = el.textContent ? el.textContent.toLowerCase() : '';
                            const classes = el.className ? el.className.toLowerCase() : '';
                            if (text.includes('post') || text.includes('share') || text.includes('publish') || classes.includes('share') || classes.includes('post')) {
                                const rect = el.getBoundingClientRect();
                                console.log('Share-related element: ' + text.substring(0, 30) + ' class: ' + classes.substring(0, 30) + ' at (' + rect.top + ',' + rect.left + ')');
                                foundShareElements++;
                            }
                        }

                        return false;
                    }
                """);

                if not content_editor_exists:
                    logger.info("⚠️ Content editor not found after waiting, trying to locate alternative editors...")
                    # Try to find alternative content editors
                    all_editors = await page.query_selector_all("div[contenteditable='true']")
                    for editor in all_editors:
                        is_share_related = await page.evaluate("""
                            (el) => {
                                // Check if this editor is in a share-related context
                                let parent = el.parentElement;
                                for (let i = 0; i < 5 && parent; i++) {  // Look up 5 levels
                                    const classes = parent.className ? parent.className.toLowerCase() : '';
                                    const id = parent.id ? parent.id.toLowerCase() : '';
                                    if (classes.includes('share') || classes.includes('post') || classes.includes('create') ||
                                        id.includes('share') || id.includes('post') || id.includes('create')) {
                                        return true;
                                    }
                                    parent = parent.parentElement;
                                }
                                return false;
                            }
                        """, editor)

                        if is_share_related:
                            # Found a share-related content editor, use this
                            logger.info("✅ Found share-related content editor")
                            content_editor_exists = True
                            break

                # Enhanced JavaScript approach to find the exact post button that appears directly in the content area
                try:
                    result = await page.evaluate("""
                        () => {
                            // Find the content editor where the post content is being written
                            let contentEditor = document.querySelector('div[contenteditable="true"][role="textbox"]');

                            // If not found, look for any content editor that might be the post editor
                            if (!contentEditor) {
                                const allEditors = Array.from(document.querySelectorAll('div[contenteditable="true"]'));
                                for (const editor of allEditors) {
                                    // Check if this editor is in the sharing context by looking at surrounding elements
                                    let parent = editor.parentElement;
                                    for (let i = 0; i < 5 && parent; i++) {  // Look up 5 levels
                                        const classes = parent.className ? parent.className.toLowerCase() : '';
                                        const id = parent.id ? parent.id.toLowerCase() : '';

                                        // Check if this is in a sharing/posting context
                                        if (classes.includes('share') || classes.includes('post') || classes.includes('create') ||
                                            classes.includes('editor') || classes.includes('compose') ||
                                            id.includes('share') || id.includes('post') || id.includes('create')) {
                                            contentEditor = editor;
                                            break;
                                        }
                                        parent = parent.parentElement;
                                    }
                                    if (contentEditor) break;
                                }
                            }

                            // If still not found, look for any editor with content
                            if (!contentEditor) {
                                const allEditors = Array.from(document.querySelectorAll('div[contenteditable="true"]'));
                                for (const editor of allEditors) {
                                    const text = editor.textContent ? editor.textContent.trim() : '';
                                    // Look for editor that has content (should match what we just entered)
                                    if (text && text.length > 10) {
                                        contentEditor = editor;
                                        break;
                                    }
                                }
                            }

                            if (!contentEditor) {
                                console.log('No content editor found');
                                return { found: false, reason: 'No content editor found' };
                            }

                            // Get content editor position and size
                            const editorRect = contentEditor.getBoundingClientRect();
                            console.log('Content editor found at: (' + editorRect.left + ', ' + editorRect.top + ') size: ' + editorRect.width + 'x' + editorRect.height);

                            // Find all buttons on the page
                            const allButtons = Array.from(document.querySelectorAll('button'));

                            // Look specifically for the "Post" button that appears above or within the same container as the content editor
                            let postButton = null;

                            for (const btn of allButtons) {
                                const text = btn.textContent ? btn.textContent.trim() : '';
                                const ariaLabel = btn.getAttribute('aria-label') || '';
                                const type = btn.getAttribute('type') || '';
                                const classes = Array.from(btn.classList || []);
                                const isDisabled = btn.disabled || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';
                                const isVisible = btn.offsetParent !== null;

                                // Skip navigation buttons and utility buttons
                                if (text.toLowerCase().includes('new posts') ||
                                    text.toLowerCase().includes('home') ||
                                    text.toLowerCase().includes('messaging') ||
                                    text.toLowerCase().includes('notifications') ||
                                    text.toLowerCase().includes('emoji') ||
                                    text.toLowerCase().includes('image') ||
                                    text.toLowerCase().includes('photo') ||
                                    text.toLowerCase().includes('video') ||
                                    text.toLowerCase().includes('gif') ||
                                    text.toLowerCase().includes('mention') ||
                                    text.toLowerCase().includes('draft') ||
                                    text.toLowerCase().includes('save') ||
                                    text.toLowerCase().includes('cancel') ||
                                    text.toLowerCase().includes('add')) {
                                    continue;
                                }

                                // Check if this is the main "Post" button that appears in the content area
                                if (text.toLowerCase() === 'post' && !isDisabled && isVisible) {
                                    const btnRect = btn.getBoundingClientRect();

                                    // The key insight from user feedback: Look for buttons that are directly
                                    // related to the content editor, often positioned nearby in the same panel
                                    const verticalDistance = Math.abs(btnRect.top - editorRect.top); // Same top area as editor
                                    const horizontalDistance = Math.abs(btnRect.left - editorRect.left); // Same left as editor area

                                    // Also check if button is below editor but still in the same panel
                                    const isBelowEditor = btnRect.top > editorRect.top && btnRect.top < (editorRect.bottom + 50);
                                    const isNearEditorHorizontally = Math.abs(btnRect.left - editorRect.left) < 200;

                                    console.log('Found "Post" button: "' + text + '" at (' + btnRect.left + ', ' + btnRect.top + ') vs editor at (' + editorRect.left + ', ' + editorRect.top + ') vertDist: ' + verticalDistance + ' belowEditor: ' + isBelowEditor);

                                    // Look for buttons in the same general vertical area as the editor or just below it
                                    if ((verticalDistance < 150 && horizontalDistance < 300) || (isBelowEditor && isNearEditorHorizontally)) {
                                        postButton = btn;
                                        break;
                                    }
                                }
                            }

                            // If we didn't find exact "Post" button, look for submit buttons in the same area
                            if (!postButton) {
                                for (const btn of allButtons) {
                                    const text = btn.textContent ? btn.textContent.trim() : '';
                                    const type = btn.getAttribute('type') || '';
                                    const isDisabled = btn.disabled || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';
                                    const isVisible = btn.offsetParent !== null;

                                    if (type === 'submit' && !isDisabled && isVisible) {
                                        const btnRect = btn.getBoundingClientRect();
                                        const verticalDistance = Math.abs(btnRect.top - editorRect.top);
                                        const isBelowEditor = btnRect.top > editorRect.top && btnRect.top < (editorRect.bottom + 50);

                                        // This submit button is likely the post button if it's near the editor
                                        if (verticalDistance < 150 || isBelowEditor) {
                                            console.log('Found submit button near editor: (' + btnRect.left + ', ' + btnRect.top + ')');
                                            postButton = btn;
                                            break;
                                        }
                                    }
                                }
                            }

                            if (postButton) {
                                console.log('Clicking post button: "' + postButton.textContent.trim() + '"');

                                // Scroll to ensure it's visible
                                postButton.scrollIntoView({block: 'nearest', inline: 'nearest'});
                                postButton.focus();

                                // Click twice to ensure it registers
                                postButton.click();
                                setTimeout(() => postButton.click(), 200);

                                return {
                                    found: true,
                                    text: postButton.textContent.trim(),
                                    ariaLabel: postButton.getAttribute('aria-label'),
                                    type: postButton.getAttribute('type'),
                                    classes: Array.from(postButton.classList).join(', '),
                                    clicked: true
                                };
                            }

                            return {
                                found: false,
                                reason: 'No "Post" button found in editor area, checked ' + allButtons.length + ' buttons'
                            };
                        }
                    """);

                    if result['found'] and result['clicked']:
                        logger.info(f"✅ Successfully clicked Post button IN EDITOR AREA: '{result['text']}'")
                        post_clicked = True
                    else:
                        logger.info(f"Editor-area JavaScript approach: {result['reason']}")

                except Exception as e:
                    logger.error(f"Error in position-based JavaScript post button search: {e}")

                # FINAL targeted approach specifically for the Post button in the bottom-right of content editor
                # This is the button that should actually publish the post as mentioned by the user
                if not post_clicked:
                    logger.info("🔍 Using FINAL targeted approach to find the Post button in bottom-right corner of editor...")

                    try:
                        result = await page.evaluate("""
                            () => {
                                // First find the content editor
                                let contentEditor = document.querySelector('div[contenteditable="true"][role="textbox"]');

                                if (!contentEditor) {
                                    // Look for any content editor that might be related to sharing
                                    const allEditors = Array.from(document.querySelectorAll('div[contenteditable="true"]'));
                                    for (const editor of allEditors) {
                                        const rect = editor.getBoundingClientRect();
                                        // Look for editors that have a reasonable size for content input
                                        if (rect.width > 100 && rect.height > 30) {
                                            contentEditor = editor;
                                            break;
                                        }
                                    }
                                }

                                if (!contentEditor) {
                                    console.log('Could not find a valid content editor');
                                    return { found: false, reason: 'No content editor found for position reference' };
                                }

                                // Get content editor position
                                const editorRect = contentEditor.getBoundingClientRect();
                                console.log('Content editor at: (' + editorRect.left + ', ' + editorRect.top + ') size: ' + editorRect.width + 'x' + editorRect.height);

                                // Now look for the "Post" button specifically - it should be:
                                // 1. A visible button with text "Post"
                                // 2. Located near the bottom-right of the content editor
                                // 3. Enabled (not disabled)
                                const allButtons = Array.from(document.querySelectorAll('button'));

                                // Look specifically for the "Post" button near the content editor
                                for (const btn of allButtons) {
                                    const text = btn.textContent ? btn.textContent.trim() : '';
                                    const isDisabled = btn.disabled || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';
                                    const isVisible = btn.offsetParent !== null; // Check if button is visible

                                    // This is the exact button we want - text "Post" (not "New posts", not "Share")
                                    if (text.toLowerCase() === 'post' && !isDisabled && isVisible) {
                                        const btnRect = btn.getBoundingClientRect();

                                        // Check if this button is near the bottom-right of the content editor
                                        const verticalDistance = btnRect.top - editorRect.bottom;  // Positive if below editor
                                        const horizontalDistance = btnRect.left - editorRect.right; // Positive if right of editor

                                        const isNearBottom = verticalDistance >= -20 && verticalDistance <= 80;  // Allow some flexibility
                                        const isNearRight = horizontalDistance >= -50 && horizontalDistance <= 100;  // Allow some flexibility

                                        console.log('Found "Post" button at: (' + btnRect.left + ', ' + btnRect.top + ') editor bottom: ' + editorRect.bottom + ' right: ' + editorRect.right + ' verticalDist: ' + verticalDistance + ' horizDist: ' + horizontalDistance);

                                        if (isNearBottom && isNearRight) {
                                            // This is likely the correct post button!
                                            console.log('Found target "Post" button near content editor!');

                                            // Scroll and click
                                            btn.scrollIntoView({block: 'nearest', inline: 'nearest'});
                                            btn.focus();
                                            btn.click();
                                            // Click again to make sure
                                            setTimeout(() => btn.click(), 200);

                                            return {
                                                found: true,
                                                text: text,
                                                type: btn.getAttribute('type'),
                                                classes: Array.from(btn.classList).join(', '),
                                                clicked: true,
                                                positionInfo: 'Near content editor bottom-right'
                                            };
                                        }
                                    }
                                }

                                // If we couldn't find "Post" button near editor, check for submit buttons near editor
                                for (const btn of allButtons) {
                                    const text = btn.textContent ? btn.textContent.trim() : '';
                                    const type = btn.getAttribute('type');
                                    const isDisabled = btn.disabled || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';
                                    const isVisible = btn.offsetParent !== null;

                                    if (type === 'submit' && !isDisabled && isVisible) {
                                        const btnRect = btn.getBoundingClientRect();
                                        const verticalDistance = btnRect.top - editorRect.bottom;
                                        const horizontalDistance = btnRect.left - editorRect.right;

                                        const isNearBottom = verticalDistance >= -20 && verticalDistance <= 80;
                                        const isNearRight = horizontalDistance >= -50 && horizontalDistance <= 100;

                                        if (isNearBottom && isNearRight) {
                                            console.log('Found submit button near content editor');

                                            btn.scrollIntoView({block: 'nearest', inline: 'nearest'});
                                            btn.focus();
                                            btn.click();
                                            setTimeout(() => btn.click(), 200);

                                            return {
                                                found: true,
                                                text: text,
                                                type: type,
                                                classes: Array.from(btn.classList).join(', '),
                                                clicked: true,
                                                positionInfo: 'Submit button near content editor'
                                            };
                                        }
                                    }
                                }

                                // If we still can't find it, try a direct click on any "Post" button that isn't navigation
                                for (const btn of allButtons) {
                                    const text = btn.textContent ? btn.textContent.trim().toLowerCase() : '';
                                    const isDisabled = btn.disabled || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';
                                    const isVisible = btn.offsetParent !== null;

                                    // Look specifically for the word "post" as a complete word, not part of "new posts"
                                    if (text === 'post' && !isDisabled && isVisible) {
                                        console.log('Found "Post" button by exact text match: ' + btn.textContent);

                                        btn.scrollIntoView({block: 'nearest'});
                                        btn.focus();
                                        btn.click();
                                        setTimeout(() => btn.click(), 200);

                                        return {
                                            found: true,
                                            text: btn.textContent.trim(),
                                            type: btn.getAttribute('type'),
                                            classes: Array.from(btn.classList).join(', '),
                                            clicked: true,
                                            positionInfo: 'Exact "Post" text match'
                                        };
                                    }
                                }

                                return {
                                    found: false,
                                    reason: 'No "Post" button found near content editor or with exact match, checked ' + allButtons.length + ' buttons',
                                    totalButtons: allButtons.length,
                                    editorPosition: {left: editorRect.left, top: editorRect.top, bottom: editorRect.bottom, right: editorRect.right}
                                };
                            }
                        """);

                        if result['found'] and result['clicked']:
                            position_info = result.get('positionInfo', '')
                            logger.info(f"✅ SUCCESSFULLY clicked the CORRECT Post button: '{result['text']}' - {position_info}")
                            post_clicked = True
                        else:
                            logger.info(f"Final targeted approach: {result['reason']}")

                    except Exception as e:
                        logger.error(f"Error in final targeted post button search: {e}")

                # If JavaScript still didn't work, try waiting longer and then scanning buttons
                if not post_clicked:
                    logger.info("⏳ Waiting longer for post button to become active...")
                    await page.wait_for_timeout(5000)  # Wait more time for UI to update

                # If JavaScript didn't work, try specific selectors for the post button
                # Avoid selectors that might catch navigation buttons like "New posts"
                if not post_clicked:
                    logger.info("🔍 Trying specific selectors for the post button...")
                    selectors = [
                        # More specific selector for the exact "Post" button in the editor panel
                        "button:has-text('Post'):not(:has-text('New posts')):not([disabled]):not([aria-disabled='true'])",
                        # LinkedIn-specific primary button in share context
                        "button.artdeco-button--primary:has-text('Post'):not([disabled])",
                        # Submit button that is specifically for sharing (not navigation)
                        "button[type='submit']:not([disabled]):not([aria-disabled='true']):not(:has-text('New posts'))",
                        # Buttons with exact "Post" text
                        "button:role('button'):has-text('Post'):not([disabled]):not([aria-disabled='true'])"
                    ]

                    for selector in selectors:
                        try:
                            button = await page.wait_for_selector(selector, timeout=4000)
                            if button:
                                # Verify this button is not a navigation button
                                text_content = await button.text_content()
                                if 'new posts' in text_content.lower() or 'home' in text_content.lower():
                                    logger.info(f"Skipping navigation button: {text_content}")
                                    continue

                                await button.click()
                                await page.wait_for_timeout(500)  # Brief pause
                                await button.click()  # Click again to ensure registration
                                logger.info(f"✅ Clicked post button with selector: {selector} (text: '{text_content}')")
                                post_clicked = True
                                break
                        except Exception as e:
                            logger.info(f"Selector '{selector}' failed: {str(e)}")
                            continue

                # Final attempt: manually search through buttons that might be the post button
                if not post_clicked:
                    try:
                        logger.info("🔍 Final attempt: manual search through enabled buttons...")
                        all_buttons = await page.query_selector_all("button:not([disabled]):not([aria-disabled='true'])")

                        for button in all_buttons:
                            try:
                                text_content = await button.text_content()
                                aria_label = await button.get_attribute("aria-label")
                                button_type = await button.get_attribute("type")

                                # Look for buttons with post/share intent that aren't utility buttons
                                has_post_intent = (
                                    text_content and (
                                        'post' in text_content.lower() or
                                        'share' in text_content.lower() or
                                        'publish' in text_content.lower()
                                    )
                                ) or button_type == 'submit'

                                is_utility = any(
                                    keyword in (text_content or '').lower() or
                                    keyword in (aria_label or '').lower()
                                    for keyword in [
                                        'emoji', 'image', 'photo', 'video', 'gif',
                                        'mention', 'draft', 'save', 'cancel', 'add'
                                    ]
                                )

                                if has_post_intent and not is_utility:
                                    await button.click()
                                    await page.wait_for_timeout(400)
                                    await button.click()  # Double click for reliability
                                    logger.info(f"✅ Clicked potential post button: '{text_content or aria_label}'")
                                    post_clicked = True
                                    break

                            except Exception as e:
                                logger.info(f"Error checking button: {e}")
                                continue

                    except Exception as e:
                        logger.error(f"Error in manual button search: {e}")

                if not post_clicked:
                    logger.error("❌ Could not find or click the Post button in the composition area")
                    logger.info("💡 The content was filled but the final post button was not identified.")
                    logger.info("📋 Please verify the LinkedIn interface manually to identify the correct post button.")

                    await browser.close()
                    return {
                        "success": False,
                        "error": "Could not find or click the Post button - post was not published"
                    }

                # Wait for post to be published
                logger.info("⏳ Waiting for post to be published...")
                await page.wait_for_timeout(10000)  # Wait 10 seconds to ensure post appears

                # Close the browser
                await browser.close()

                logger.info("✅ LinkedIn post published successfully!")

                return {
                    "success": True,
                    "message": "LinkedIn post created successfully",
                    "content": text
                }

        except Exception as e:
            logger.error(f"Failed to create LinkedIn post: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_profile_info(self) -> Dict[str, Any]:
        """Get information about the LinkedIn profile"""
        return {
            "email": self.email,
            "status": "ready"
        }

    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Return the server's capabilities"""
        return [
            {
                "name": "post_linkedin",
                "description": "Create a LinkedIn post via browser automation",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Content for the LinkedIn post"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "get_profile_info",
                "description": "Get information about the LinkedIn profile",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

async def handle_request(server: LinkedInMCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP requests"""
    request_id = request.get("request_id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "mcp.initialize":
        return {
            "request_id": request_id,
            "result": {
                "server_info": {
                    "name": "LinkedIn MCP Server",
                    "version": "1.0.0",
                    "capabilities": server.get_capabilities()
                }
            }
        }

    elif method == "mcp.list_resources":
        return {
            "request_id": request_id,
            "result": {
                "resources": []
            }
        }

    elif method == "mcp.list_prompts":
        return {
            "request_id": request_id,
            "result": {
                "prompts": []
            }
        }

    elif method == "tools/execute":
        tool_name = params.get("name")
        tool_arguments = params.get("arguments", {})

        if tool_name == "post_linkedin":
            result = await server.post_linkedin(**tool_arguments)
        elif tool_name == "get_profile_info":
            result = await server.get_profile_info()
        else:
            return {
                "request_id": request_id,
                "error": {
                    "code": "UNKNOWN_TOOL",
                    "message": f"Unknown tool: {tool_name}"
                }
            }

        return {
            "request_id": request_id,
            "result": result
        }

    else:
        return {
            "request_id": request_id,
            "error": {
                "code": "INVALID_METHOD",
                "message": f"Invalid method: {method}"
            }
        }

async def main():
    """Main function to run the MCP server"""
    server = LinkedInMCPServer()

    # Process requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = await handle_request(server, request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            error_response = {
                "request_id": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())