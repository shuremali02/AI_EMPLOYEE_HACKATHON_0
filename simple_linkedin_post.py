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
        
        print("Login submitted. Waiting to land on feed...")
        
        # Wait for login to complete with extended timeout
        try:
            await page.wait_for_url("**/feed**", timeout=60000)
            print("✅ Successfully logged in!")
        except:
            current_url = page.url
            print(f"Current URL: {current_url}")
            if "checkpoint" in current_url or "challenge" in current_url:
                print("Security verification required. Please complete in browser.")
                await page.wait_for_timeout(300000)  # Wait 5 mins for manual verification
            else:
                print("Login might have failed or took longer than expected.")
        
        # Wait for page to fully load
        await page.wait_for_timeout(5000)
        
        # Try to find and click "Start a post" button
        print("Looking for post creation button...")
        
        # Try multiple approaches to find the post button
        button_selectors = [
            "button:has-text('Start a post')",
            "button:has-text('Post')",
            "button[aria-label='Create a post']",
            "button[aria-label='Share an update']",
            "[data-test-id='share-box-feed-entry']",
            ".share-box-feed-entry__trigger"
        ]
        
        button_found_and_clicked = False
        for selector in button_selectors:
            try:
                print(f"Trying selector: {selector}")
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                print(f"✅ Clicked post button: {selector}")
                button_found_and_clicked = True
                break
            except:
                print(f"❌ Could not click with selector: {selector}")
                continue
        
        if not button_found_and_clicked:
            print("❌ Could not find any post creation button")
            print("Manually look for the 'Start a post' button in the browser")
            await page.wait_for_timeout(60000)  # Wait 1 min
            await browser.close()
            return
        
        # Wait for editor to appear
        await page.wait_for_timeout(3000)
        
        # Fill the content using the content-editable div
        try:
            await page.fill("div[contenteditable='true']", content)
            print("✅ Content filled successfully")
        except:
            print("❌ Could not fill content with main selector, trying alternatives...")
            try:
                await page.locator("div[role='textbox']").fill(content)
                print("✅ Content filled with alternative selector")
            except:
                print("❌ Could not find content editor")
                await browser.close()
                return
        
        # Wait for content to be processed
        await page.wait_for_timeout(2000)
        
        # Try to post
        try:
            # Look for the post button
            post_selectors = [
                "button:has-text('Post')",
                "button[aria-label='Post']",
                "button:has-text('Share')"
            ]
            
            post_clicked = False
            for post_selector in post_selectors:
                try:
                    await page.click(post_selector)
                    print(f"✅ Clicked post button: {post_selector}")
                    post_clicked = True
                    break
                except:
                    continue
            
            if not post_clicked:
                print("❌ Could not click post button")
                # As last resort, try to find any button that looks like post
                try:
                    buttons = await page.query_selector_all("button")
                    for button in buttons:
                        try:
                            text = await button.text_content()
                            if 'post' in text.lower() or 'share' in text.lower():
                                await button.click()
                                print(f"✅ Clicked potential post button: {text}")
                                post_clicked = True
                                break
                        except:
                            continue
                except:
                    print("❌ Could not find any potential post button")
        except Exception as e:
            print(f"❌ Error clicking post button: {e}")
        
        if post_clicked:
            print("🎉 LinkedIn post process initiated successfully!")
        else:
            print("⚠️ Content was filled but post button could not be clicked")
        
        print("Browser will stay open for 2 minutes so you can verify...")
        await page.wait_for_timeout(120000)
        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_linkedin_post())
