#!/usr/bin/env python3
import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def run_linkedin_post():
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

    print(f"Using LinkedIn account: {email}")
    print("Starting LinkedIn automation...")

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
        
        print("Login submitted. Waiting for security verification if needed...")
        
        # Wait for login to complete with extended timeout
        try:
            await page.wait_for_url("**/feed**", timeout=60000)
            print("✅ Successfully logged in!")
        except:
            current_url = page.url
            print(f"Security verification may be required. Current URL: {current_url}")
            print("Please complete any security checks in the browser.")
            print("Waiting 5 minutes for manual verification...")
            await page.wait_for_timeout(300000)  # 5 minutes
            
            # After waiting, try to proceed
            current_url = page.url
            print(f"Current URL after waiting: {current_url}")
            
            if "feed" in current_url:
                print("✅ Verified and on feed page!")
            else:
                print(f"Still on: {current_url}")
        
        # Wait for page to fully load
        await page.wait_for_timeout(5000)
        
        print("Looking for 'Start a post' button under the navbar...")
        
        # Look for the "Start a post" button (centered under navbar)
        selectors_to_try = [
            "button:has-text('Start a post')",
            "button:has-text('Create a post')",
            "button[aria-label='Create a post']",
            "[data-test-shares-create-destination-type='FEED']",
            ".share-box-feed-entry__trigger",
            "button:has-text('Post')",  # Sometimes just "Post" appears
        ]
        
        button_clicked = False
        for selector in selectors_to_try:
            try:
                # Wait for the element to be available and clickable
                await page.wait_for_selector(selector, state="visible", timeout=10000)
                await page.click(selector)
                print(f"✅ Clicked button: {selector}")
                button_clicked = True
                
                # Wait for editor to appear after clicking
                await page.wait_for_timeout(3000)
                
                # Now find the content editor
                editor_selectors = [
                    "div[contenteditable='true'][data-test-id*='share']",
                    "div[contenteditable='true']",
                    "div[role='textbox']",
                    "[data-test-id='share-content-textarea'] div[contenteditable='true']",
                ]
                
                editor_filled = False
                for editor_selector in editor_selectors:
                    try:
                        await page.fill(editor_selector, content)
                        print(f"✅ Content filled using editor: {editor_selector}")
                        editor_filled = True
                        break
                    except:
                        continue
                
                if not editor_filled:
                    print("⚠️ Trying alternative content entry method...")
                    # Try to click the editor first then fill
                    try:
                        await page.click("div[contenteditable='true']")
                        await page.wait_for_timeout(1000)
                        await page.keyboard.type(content)
                        print("✅ Content entered via keyboard")
                        editor_filled = True
                    except:
                        print("❌ Could not find or fill content editor")
                
                if editor_filled:
                    # Wait for content processing
                    await page.wait_for_timeout(2000)
                    
                    # Now find and click the final post button
                    post_button_selectors = [
                        "button:has-text('Post'):not(:has-text('Save')):not(:has-text('Apply')):not(:has-text('Cancel'))",
                        "button[aria-label='Post']",
                        "[data-test-id='share-content-post-button']",
                        "button:has-text('Share'):not(:has-text('Share to'))",
                        "button[type='submit']:has-text('Post')",
                    ]
                    
                    post_clicked = False
                    for post_selector in post_button_selectors:
                        try:
                            await page.click(post_selector)
                            print(f"✅ Clicked post button: {post_selector}")
                            post_clicked = True
                            break
                        except:
                            continue
                    
                    if not post_clicked:
                        print("⚠️ Could not find final post button, trying to find any post-related button...")
                        # Look for any button that might be the post button
                        try:
                            all_buttons = await page.query_selector_all("button")
                            for button in all_buttons:
                                try:
                                    text = await button.text_content()
                                    aria_label = await button.get_attribute('aria-label')
                                    if text and ('post' in text.lower() or 'share' in text.lower()) and \
                                       'save' not in text.lower() and 'draft' not in text.lower() and \
                                       'cancel' not in text.lower():
                                        await button.click()
                                        print(f"✅ Clicked potential post button: {text}")
                                        post_clicked = True
                                        break
                                except:
                                    continue
                        except:
                            print("❌ Could not find any post buttons")
                    
                    if post_clicked:
                        print("🎉 LinkedIn post created successfully!")
                    else:
                        print("⚠️ Content was filled but post button could not be clicked")
                
                break  # Exit the main loop after handling the post
            except Exception as e:
                print(f"⚠️ Could not click {selector}: {e}")
                continue
        
        if not button_clicked:
            print("❌ Could not find any post creation button")
            print("Let me show you the available buttons on the page:")
            
            # Show available elements that might be relevant
            try:
                elements = await page.query_selector_all("button, [role='button'], [data-test*='share'], [data-test*='post']")
                for i, element in enumerate(elements[:15]):  # Show first 15 elements
                    try:
                        aria_label = await element.get_attribute('aria-label')
                        text_content = await element.text_content()
                        class_name = await element.get_attribute('class')
                        print(f"  {i+1}. aria-label='{aria_label}', text='{text_content[:50]}...', class='{class_name[:50]}...'[:50]")
                    except:
                        continue
        
        print("LinkedIn posting process completed!")
        print("Browser will stay open for 3 minutes so you can verify...")
        await page.wait_for_timeout(180000)
        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_linkedin_post())
