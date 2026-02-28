#!/usr/bin/env python3
import os
import asyncio
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv

load_dotenv()

# Business content to post
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        logger.error("LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables must be set")
        return

    logger.info(f"Using LinkedIn account: {email}")
    logger.info("Launching browser for business content automation...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Go to LinkedIn
        await page.goto("https://www.linkedin.com/login")
        logger.info("Navigated to LinkedIn login page")
        
        # Wait for the page to load completely
        await page.wait_for_load_state('networkidle')
        
        # Try different selectors for the username field since the default one might not work
        try:
            # Try the standard selector first
            await page.fill("input#username", email)
        except:
            try:
                # Try alternative selectors
                await page.fill("input[name='login-email'] or input[data-test-id='auth-email'] or input[type='email']", email)
            except:
                # Use a more general selector
                await page.locator("input").nth(0).fill(email)
        
        try:
            # Try the standard selector for password
            await page.fill("input#password", password)
        except:
            # Use a more general selector for password
            await page.locator("input").nth(1).fill(password)
        
        # Click login - try different selectors if needed
        try:
            await page.click("button[type='submit']")
        except:
            try:
                await page.click("button:has-text('Sign in')")
            except:
                await page.click("button:has-text('Log In')")
        
        logger.info("Login submitted. Browser will stay open for 5 minutes for security verification...")
        
        # Wait 5 minutes (300 seconds) to allow for manual security verification
        await page.wait_for_timeout(300000)  # 5 minutes in milliseconds
        
        # After waiting, check if we're on the feed (logged in)
        current_url = page.url
        logger.info(f"Current URL after waiting: {current_url}")

        if "feed" in current_url or "mynetwork" in current_url or "notifications" in current_url:
            logger.info("Logged in successfully, proceeding with business post creation...")

            # Wait for page to stabilize after login
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)

            # Try multiple selectors for the create post button
            post_button_selectors = [
                "button[aria-label='Create a post']",
                "button.share-creation-state__open-create-share-modal",
                "button[data-test-id='share-create-artifact']",
                "button:has-text('Start a post')"
            ]
            
            post_button_clicked = False
            for selector in post_button_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    logger.info(f"Clicked post button with selector: {selector}")
                    post_button_clicked = True
                    break
                except:
                    continue
            
            if not post_button_clicked:
                logger.error("Could not find any create post button")
                await browser.close()
                return

            # Wait for the text area to be available and fill content
            try:
                await page.wait_for_selector("div[contenteditable='true']", timeout=10000)
                await page.fill("div[contenteditable='true']", content)
                logger.info("Business content filled successfully")
            except:
                try:
                    # Try alternative selector for content editor
                    await page.locator("div[role='textbox']").fill(content)
                    logger.info("Business content filled with alternative selector")
                except:
                    logger.error("Could not find content editor")
                    await browser.close()
                    return

            # Wait a bit and then click post
            await page.wait_for_timeout(2000)
            
            # Try multiple selectors for the post button
            post_confirm_selectors = [
                "button[aria-label='Post']",
                "button.share-actions__trigger",
                "button:has-text('Post')",
                "button:has-text('Share')"
            ]
            
            post_clicked = False
            for selector in post_confirm_selectors:
                try:
                    await page.click(selector)
                    logger.info(f"Clicked post confirmation with selector: {selector}")
                    post_clicked = True
                    break
                except:
                    continue
            
            if not post_clicked:
                logger.error("Could not click post button")
            
            logger.info("Business post process completed. Browser will stay open for 30 more seconds...")
            await page.wait_for_timeout(30000)
        else:
            logger.info("Still on verification page. You may need to complete verification manually.")
            logger.info("Browser will stay open for 30 more seconds...")
            await page.wait_for_timeout(30000)

        await browser.close()
        logger.info("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())
