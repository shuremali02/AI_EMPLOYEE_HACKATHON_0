#!/usr/bin/env python3
import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def run_targeted_linkedin_post():
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    content = """🚀 Transform Your Business with AI Automation

In today's fast-paced market, businesses that leverage AI automation are seeing 85-90% cost reductions compared to traditional human resources while maintaining consistent, predictable performance.

Key business transformations:
• 24/7 automated operations without breaks
• Significant cost savings with AI employees
• Consistent quality and performance
• Scalable solutions that grow with your business

The future of business is autonomous. Companies that embrace AI-powered automation today will dominate their markets tomorrow. Don't get left behind - start your automation journey now!

Ready to revolutionize your business operations?

#BusinessAutomation #ArtificialIntelligence #DigitalTransformation #BusinessGrowth #Innovation #FutureOfWork #AI #Entrepreneurship"""

    print(f"Starting targeted LinkedIn automation for account: {email}")
    print("Based on your description, targeting the center feed area...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Go to LinkedIn
        await page.goto("https://www.linkedin.com/login")
        
        # Fill credentials
        await page.fill("input#username", email)
        await page.fill("input#password", password)
        
        # Click login
        await page.click("button[type='submit']")
        print("Submitted login credentials")
        
        # Wait for login
        try:
            await page.wait_for_url("**/feed**", timeout=60000)
            print("✅ Successfully logged into LinkedIn feed")
        except:
            current_url = page.url
            print(f"Current URL: {current_url}")
            if "checkpoint" in current_url or "challenge" in current_url:
                print("⚠️ Security verification required. Please complete in browser.")
                await page.wait_for_timeout(180000)  # 3 minutes
            else:
                print("⚠️ Login may have taken longer, continuing...")
        
        # Wait for page to fully load
        await page.wait_for_timeout(5000)
        
        print("Looking for 'Start a post' button in the center feed area...")
        
        # According to your description, the post button is in the center feed area
        # Try specific selectors for the main feed post area
        selectors_to_try = [
            # The main feed area where "Start a post" button should be
            "div.global-rail-v2__feed-content button:has-text('Start a post')",
            "div.feed-content button:has-text('Start a post')",
            "div.scaffold-finite-scroll__content button:has-text('Start a post')",
            "div.core-rail button:has-text('Start a post')",
            "div.mr3 button:has-text('Start a post')",  # Left column has mr3 class
            "div.mr3 ~ div button:has-text('Start a post')",  # Adjacent to left column
            "div.center-rail button:has-text('Start a post')",  # Center rail
            "button:has-text('Start a post')",  # General search
            # Alternative text that might be used
            "button:has-text('Create a post')",
            "button:has-text('Share an update')",
            # Look for the element by aria-label
            "button[aria-label='Create a post']",
            "button[aria-label='Share an update']",
            # LinkedIn-specific class patterns for post creation
            "button.share-box-feed-entry__trigger",
            "[data-test-id='share-box-feed-entry']",
            # More specific targeting for the center area
            "div.feed-shared-update-v2__container button",
            "div.share-box-feed-entry__container button",
        ]
        
        button_clicked = False
        for i, selector in enumerate(selectors_to_try):
            try:
                print(f"Trying selector {i+1}/{len(selectors_to_try)}: {selector}")
                
                # Wait for the element to be available
                element = await page.wait_for_selector(selector, state="visible", timeout=10000)
                
                # Scroll into view and click
                await element.scroll_into_view_if_needed()
                await element.click()
                
                print(f"✅ Successfully clicked 'Start a post' button with selector: {selector}")
                button_clicked = True
                
                # Wait for the editor to appear
                await page.wait_for_timeout(4000)
                
                # Now find the content editor
                print("Looking for content editor...")
                
                editor_selectors = [
                    # Editor in the post creation modal/pop-up
                    "div[contenteditable='true'][data-test-id='share-content-textarea']",
                    "div[contenteditable='true'][data-test-id*='share']",
                    "div[contenteditable='true'][role='textbox']",
                    "div[contenteditable='true']",
                    # More specific selectors
                    "div.share-creation-state__share-textarea div[contenteditable='true']",
                    "div.artdeco-text-editor__content-editable div[contenteditable='true']",
                    "div.ql-editor",
                    # Find any contenteditable within the share box
                    ".share-box-feed-entry div[contenteditable='true']",
                    ".share-creation-state div[contenteditable='true']",
                ]
                
                editor_found = False
                for editor_selector in editor_selectors:
                    try:
                        editor_element = await page.wait_for_selector(editor_selector, timeout=5000)
                        await editor_element.fill(content)
                        print(f"✅ Content filled using editor: {editor_selector}")
                        editor_found = True
                        
                        # Wait for content to be processed
                        await page.wait_for_timeout(2000)
                        
                        # Now find and click the post button
                        print("Looking for final 'Post' button...")
                        
                        post_selectors = [
                            "button:has-text('Post'):not(:has-text('Save')):not(:has-text('Apply')):not(:has-text('Cancel'))",
                            "button[data-test-id='share-content-post-button']",
                            "button[aria-label='Post']",
                            "button:has-text('Share'):not(:has-text('Share to'))",
                            "button[type='submit'][value='post']",
                        ]
                        
                        post_clicked = False
                        for post_selector in post_selectors:
                            try:
                                post_element = await page.wait_for_selector(post_selector, timeout=3000)
                                await post_element.click()
                                print(f"✅ Clicked final post button: {post_selector}")
                                post_clicked = True
                                break
                            except:
                                continue
                        
                        if not post_clicked:
                            print("⚠️ Could not find the final post button, trying alternatives...")
                            # Try to find any button that contains 'Post' or 'Share'
                            try:
                                all_buttons = await page.query_selector_all("button")
                                for btn in all_buttons:
                                    try:
                                        text = await btn.text_content()
                                        aria_label = await btn.get_attribute('aria-label')
                                        if text and ('post' in text.lower() or 'share' in text.lower()) and \
                                           not any(exclude in text.lower() for exclude in ['save', 'draft', 'cancel', 'preview', 'apply', 'more']):
                                            if 'post' in text.lower() or 'share' in text.lower():
                                                await btn.click()
                                                print(f"✅ Clicked alternative post button: {text}")
                                                post_clicked = True
                                                break
                                    except:
                                        continue
                            except Exception as e:
                                print(f"Error finding alternative buttons: {e}")
                        
                        if post_clicked:
                            print("🎉 SUCCESS: LinkedIn post has been created and published!")
                        else:
                            print("⚠️ Content was filled but final post button could not be clicked")
                        
                        break  # Exit editor loop
                        
                    except Exception as e:
                        print(f"   Editor selector failed: {editor_selector} - {e}")
                        continue
                
                if not editor_found:
                    print("❌ Could not find content editor, trying keyboard input...")
                    # Try to click and type if filling doesn't work
                    try:
                        # Look for any content-editable div
                        editor_element = await page.wait_for_selector("div[contenteditable='true']", timeout=5000)
                        await editor_element.click()
                        await page.wait_for_timeout(1000)
                        await page.keyboard.type(content)
                        print("✅ Content entered via keyboard")
                        
                        # Then try to find and click post button as before
                        post_selectors = [
                            "button:has-text('Post'):not(:has-text('Save')):not(:has-text('Apply')):not(:has-text('Cancel'))",
                            "button[aria-label='Post']",
                            "button:has-text('Share'):not(:has-text('Share to'))",
                        ]
                        
                        post_clicked = False
                        for post_selector in post_selectors:
                            try:
                                post_element = await page.wait_for_selector(post_selector, timeout=3000)
                                await post_element.click()
                                print(f"✅ Clicked post button: {post_selector}")
                                post_clicked = True
                                break
                            except:
                                continue
                                
                        if post_clicked:
                            print("🎉 SUCCESS: LinkedIn post created via keyboard input!")
                        else:
                            print("⚠️ Content entered but post button not found")
                        
                    except Exception as kb_error:
                        print(f"❌ Could not enter content via keyboard: {kb_error}")
                
                break  # Exit main selector loop once we've clicked the start post button
                
            except Exception as e:
                print(f"   Selector failed: {selector} - {e}")
                continue
        
        if not button_clicked:
            print("❌ Could not find the 'Start a post' button in the feed area")
            print("According to your description, it should be at the top of the center feed area.")
            print("You may need to manually click it and let the script continue.")
            print("The browser will stay open for 5 minutes...")
            await page.wait_for_timeout(300000)  # 5 minutes
        else:
            print("\nThe LinkedIn post has been submitted!")
            print("Browser will stay open for 3 minutes so you can verify the post...")
        
        await page.wait_for_timeout(180000)  # 3 minutes
        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_targeted_linkedin_post())
