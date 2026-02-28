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
        
        # Click the create post button
        try:
            await page.click("button[aria-label='Create a post']")
            print("✅ Clicked create post button")
        except:
            # Try alternative selectors
            try:
                await page.click("button:has-text('Start a post')")
                print("✅ Clicked create post button (alternative)")
            except:
                print("⚠️ Could not find create post button")
                await page.wait_for_timeout(10000)
                await browser.close()
                return
        
        # Wait for editor and fill content
        await page.wait_for_timeout(3000)
        
        try:
            await page.fill("div[contenteditable='true']", content)
            print("✅ Content filled successfully")
        except:
            print("⚠️ Could not fill content, trying alternative selector...")
            try:
                await page.locator("div[role='textbox']").fill(content)
                print("✅ Content filled with alternative selector")
            except:
                print("❌ Could not find content editor")
                await browser.close()
                return
        
        # Wait and post
        await page.wait_for_timeout(2000)
        
        try:
            await page.click("button[aria-label='Post']")
            print("✅ Clicked post button - Content posted successfully!")
        except:
            try:
                await page.click("button:has-text('Post')")
                print("✅ Clicked post button (alternative) - Content posted successfully!")
            except:
                print("❌ Could not click post button")
        
        print("LinkedIn posting process completed!")
        print("Browser will stay open for 2 minutes so you can verify...")
        await page.wait_for_timeout(120000)
        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_linkedin_post())
