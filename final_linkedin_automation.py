#!/usr/bin/env python3
"""
Final LinkedIn Automation Script
This script is designed to work with the current LinkedIn interface
"""
import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def run_final_linkedin_automation():
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

    print(f"Starting LinkedIn automation for account: {email}")
    print("This script uses the most common/working selectors for LinkedIn's current interface...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Set viewport to ensure proper rendering
        await page.set_viewport_size({"width": 1280, "height": 1024})
        
        # Go to LinkedIn
        await page.goto("https://www.linkedin.com/login")
        print("Navigated to LinkedIn login page")
        
        # Fill credentials
        await page.fill("input#username", email)
        await page.fill("input#password", password)
        
        # Click login
        await page.click("button[type='submit']")
        print("Submitted login credentials")
        
        # Wait for login with timeout
        try:
            await page.wait_for_url("**/feed**", timeout=60000)
            print("✅ Successfully logged into LinkedIn feed")
        except:
            current_url = page.url
            print(f"Current URL: {current_url}")
            if "checkpoint" in current_url or "challenge" in current_url:
                print("⚠️ Security verification required. Please complete in browser.")
                print("Waiting 3 minutes for manual verification...")
                await page.wait_for_timeout(180000)
                
                # Check again after manual verification
                current_url = page.url
                if "feed" in current_url or "home" in current_url:
                    print("✅ Verified and on feed page!")
                else:
                    print(f"Still on: {current_url}")
            else:
                print("⚠️ Login may have taken longer, continuing with automation...")
        
        # Wait for page to fully load
        await page.wait_for_timeout(5000)
        
        print("Looking for the post creation area...")
        
        # Try the most common selectors for the post box in LinkedIn's current UI
        # The main post box is often in the main feed area
        selectors_to_try = [
            # Current LinkedIn design - look for the main post creation area
            "div.share-create-originally-shared-unchanged h2:has-text('Start a post')",
            "button:has-text('Start a post')",
            "button:has-text('Create a post')",
            "button:has-text('Post')",
            "[data-test-shares-create-destination-type='FEED']",
            ".share-box-feed-entry__trigger",
            "[data-test-id='share-box-feed-entry']",
            "button[aria-label='Create a post']",
            "button[aria-label='Share an update']",
            "button[aria-label='Post']",
            # LinkedIn's newer selectors
            "div.feed-shared-update-v2__container",
            "div.share-box-feed-entry__container",
            "div.global-rail-v2__feed-content div.share-box-feed-entry",
            # General selectors for post-like elements
            "button:has-text('Share an update')",
            "button:has-text('Write an article')",
        ]
        
        post_area_found = False
        for i, selector in enumerate(selectors_to_try):
            try:
                print(f"Trying selector {i+1}/{len(selectors_to_try)}: {selector}")
                
                # Wait for element to be visible
                await page.wait_for_selector(selector, state="visible", timeout=10000)
                
                # Scroll element into view and click it
                element = await page.query_selector(selector)
                await element.scroll_into_view_if_needed()
                await element.click()
                
                print(f"✅ Successfully clicked: {selector}")
                post_area_found = True
                
                # Wait for the editor to appear after clicking
                await page.wait_for_timeout(4000)
                
                print("Looking for the content editor...")
                
                # Look for the content editor - this is where we'll write the post
                editor_selectors = [
                    "div[contenteditable='true'][data-test-id*='share-content']",
                    "div[contenteditable='true'][data-test-id*='share']",
                    "div[contenteditable='true'][role='textbox']",
                    "div[contenteditable='true']",
                    "[data-test-id='share-content-textarea'] div[contenteditable='true']",
                    "div[role='textbox'][contenteditable='true']",
                    "div.share-creation-state__share-textarea div[contenteditable='true']",
                    "div.artdeco-text-editor__content-editable[contenteditable='true']",
                ]
                
                editor_found = False
                for editor_selector in editor_selectors:
                    try:
                        await page.wait_for_selector(editor_selector, timeout=5000)
                        await page.fill(editor_selector, content)
                        print(f"✅ Content filled using editor: {editor_selector}")
                        editor_found = True
                        
                        # Wait for content to be processed
                        await page.wait_for_timeout(2000)
                        
                        # Look for the post button
                        print("Looking for the post button...")
                        post_button_selectors = [
                            "button:has-text('Post'):not(:has-text('Save')):not(:has-text('Apply')):not(:has-text('Cancel')):not(:has-text('Preview'))",
                            "button[aria-label='Post']",
                            "[data-test-id='share-content-post-button']",
                            "button:has-text('Share'):not(:has-text('Share to')):not(:has-text('Share via'))",
                            "button[data-test-id='share-content-post-button']",
                            "button[type='submit'][value='post']",
                        ]
                        
                        post_clicked = False
                        for post_selector in post_button_selectors:
                            try:
                                await page.wait_for_selector(post_selector, timeout=3000)
                                await page.click(post_selector)
                                print(f"✅ Clicked post button: {post_selector}")
                                post_clicked = True
                                break
                            except:
                                continue
                        
                        if not post_clicked:
                            print("⚠️ Could not find final post button, trying alternative methods...")
                            # Try to find any button that says 'Post' or 'Share'
                            try:
                                buttons = await page.query_selector_all("button")
                                for button in buttons:
                                    try:
                                        text = await button.text_content()
                                        aria_label = await button.get_attribute('aria-label')
                                        # Check if this is a post-related button
                                        if text and ('post' in text.lower() or 'share' in text.lower()) and \
                                           not any(exclude in text.lower() for exclude in ['save', 'draft', 'cancel', 'preview', 'apply']):
                                            await button.click()
                                            print(f"✅ Clicked potential post button: {text}")
                                            post_clicked = True
                                            break
                                    except:
                                        continue
                            except:
                                print("❌ Could not find any suitable post button")
                        
                        # At this point, we have either clicked the post button or not
                        if post_clicked:
                            print("🎉 SUCCESS: LinkedIn post has been created!")
                            print("Check your LinkedIn feed to verify the post was published.")
                        else:
                            print("⚠️ Content was filled but post button could not be found/clicked")
                        
                        break  # Exit editor selection loop
                        
                    except Exception as e:
                        print(f"   Editor selector failed: {editor_selector} - {e}")
                        continue
                
                if not editor_found:
                    print("❌ Could not find content editor")
                    # Try typing directly using keyboard
                    try:
                        await page.click("div[contenteditable='true']")
                        await page.wait_for_timeout(1000)
                        await page.keyboard.type(content)
                        print("✅ Content entered via keyboard instead of fill")
                        
                        # Then look for the post button as before
                        # Look for the post button
                        print("Looking for the post button...")
                        post_button_selectors = [
                            "button:has-text('Post'):not(:has-text('Save')):not(:has-text('Apply')):not(:has-text('Cancel')):not(:has-text('Preview'))",
                            "button[aria-label='Post']",
                            "[data-test-id='share-content-post-button']",
                            "button:has-text('Share'):not(:has-text('Share to'))",
                        ]
                        
                        post_clicked = False
                        for post_selector in post_button_selectors:
                            try:
                                await page.wait_for_selector(post_selector, timeout=3000)
                                await page.click(post_selector)
                                print(f"✅ Clicked post button: {post_selector}")
                                post_clicked = True
                                break
                            except:
                                continue
                                
                        if post_clicked:
                            print("🎉 SUCCESS: LinkedIn post has been created!")
                        else:
                            print("⚠️ Content entered via keyboard but post button could not be found")
                        
                    except Exception as kb_error:
                        print(f"❌ Could not enter content via keyboard either: {kb_error}")
                
                break  # Exit selector loop once we find and click a post area
                
            except Exception as e:
                print(f"   Selector failed: {selector} - {e}")
                continue
        
        if not post_area_found:
            print("❌ Could not find any post creation area on the page")
            print("This might be due to LinkedIn interface changes.")
            print("The browser will stay open so you can inspect the page elements manually.")
            
            # Let's try to identify what elements are actually on the page
            print("\n--- DEBUG INFO ---")
            try:
                # Get the HTML of the page to help understand the structure
                page_content = await page.content()
                print("Page loaded. Looking for potential post elements...")
                
                # Try to find elements with common LinkedIn post area class names
                possible_elements = await page.query_selector_all("*:has-text('post'), *:has-text('share'), *[aria-label*='post' i], *[aria-label*='share' i], .share-box*, .post-*")
                print(f"Found {len(possible_elements)} elements that might be related to posting")
                
                for i, element in enumerate(possible_elements[:10]):  # Show first 10
                    try:
                        text = await element.text_content()
                        aria_label = await element.get_attribute('aria-label')
                        tag_name = await element.evaluate('el => el.tagName')
                        class_name = await element.get_attribute('class')
                        print(f"  {i+1}. {tag_name}: text='{text[:50]}...', aria-label='{aria_label}', class='{class_name[:50]}...'")
                    except:
                        continue
            except:
                print("Could not gather debug information")
        
        print("\nThe LinkedIn automation process is complete!")
        print("Browser will stay open for 3 minutes so you can verify results or inspect elements...")
        await page.wait_for_timeout(180000)  # 3 minutes
        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_final_linkedin_automation())
