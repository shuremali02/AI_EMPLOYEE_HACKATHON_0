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
        
        # Try to find the post button by various methods
        post_selectors = [
            "[data-test-id='share-box-feed-entry']",
            "button[aria-label='Create a post']",
            "button:has-text('Start a post')",
            "button:has-text('Post')",
            "[data-test-shares-create-destination-type='FEED']",
            ".share-box-feed-entry__trigger",
            "button[aria-label='Share an update']",
            "button[data-test='share-content-button']",
            ".global-nav__primary-link--current"
        ]
        
        post_button_found = False
        for selector in post_selectors:
            try:
                await page.wait_for_selector(selector, timeout=10000)
                await page.click(selector)
                print(f"✅ Clicked post button using selector: {selector}")
                post_button_found = True
                break
            except Exception as e:
                print(f"❌ Selector '{selector}' failed: {str(e)[:50]}...")
                continue
        
        if not post_button_found:
            print("❌ Could not find any post button. Available elements on page:")
            
            # Get all buttons and elements that might be related to posting
            elements = await page.query_selector_all("button, [role='button'], a")
            for i, element in enumerate(elements[:15]):  # First 15 elements
                try:
                    aria_label = await element.get_attribute('aria-label')
                    text_content = await element.text_content()
                    class_name = await element.get_attribute('class')
                    print(f"  {i+1}. aria-label='{aria_label}', text='{text_content[:30]}', class='{class_name[:20]}...'") 
                except:
                    continue
            
            await browser.close()
            return
        
        # Wait for editor and fill content
        await page.wait_for_timeout(5000)  # Wait longer for editor to load
        
        # Try multiple content editor selectors
        content_selectors = [
            "div[contenteditable='true'][data-test-id*='share']",
            "div[contenteditable='true'][role='textbox']",
            "div[role='textbox'][contenteditable='true']",
            "div[contenteditable='true']:not([aria-label*='search'])",
            "[data-test-id='share-content-textarea']",
            "div[contenteditable='true']"
        ]
        
        content_filled = False
        for selector in content_selectors:
            try:
                await page.wait_for_selector(selector, timeout=10000)
                await page.fill(selector, content)
                print(f"✅ Content filled using selector: {selector}")
                content_filled = True
                break
            except Exception as e:
                print(f"❌ Content selector '{selector}' failed: {str(e)[:50]}...")
                continue
        
        if not content_filled:
            print("❌ Could not fill content. Trying manual approach...")
            # Wait for any potential editor to appear
            await page.wait_for_timeout(5000)
            print("Please manually fill the content in the browser...")
            await page.wait_for_timeout(30000)  # Wait 30 seconds for manual input
        else:
            # Wait and post
            await page.wait_for_timeout(2000)
            
            # Try multiple selectors for the post button
            post_confirm_selectors = [
                "button[aria-label='Post']",
                "button:has-text('Post'):not(:has-text('Save')):not(:has-text('Draft'))",
                "[data-test-id='share-content-post-button']",
                "button.share-actions__primary-action-btn",
                "button:has-text('Share')",
                "button:has-text('Done')"
            ]
            
            post_clicked = False
            for selector in post_confirm_selectors:
                try:
                    await page.click(selector, timeout=5000)
                    print(f"✅ Clicked post confirmation using selector: {selector}")
                    post_clicked = True
                    break
                except Exception as e:
                    print(f"❌ Post button selector '{selector}' failed: {str(e)[:50]}...")
                    continue
            
            if not post_clicked:
                print("❌ Could not click post button. Available buttons:")
                buttons = await page.query_selector_all("button")
                for i, button in enumerate(buttons[:10]):
                    try:
                        text = await button.text_content()
                        aria_label = await button.get_attribute('aria-label')
                        print(f"  {i+1}. text='{text[:30]}...', aria-label='{aria_label}'")
                    except:
                        continue
        
        print("LinkedIn posting process completed!")
        print("Browser will stay open for 2 minutes so you can verify...")
        await page.wait_for_timeout(120000)
        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_linkedin_post())
