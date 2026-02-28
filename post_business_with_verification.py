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
• 24/7 automated business operations without breaks
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
    logger.info("Opening browser for business content automation...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://www.linkedin.com/login")
        
        # Wait for the page to load
        await page.wait_for_timeout(2000)
        
        # Fill in credentials
        await page.fill("input#username", email)
        await page.fill("input#password", password)
        
        # Click login button
        await page.click("button[type='submit']")
        
        logger.info("Login submitted. Browser will stay open for 5 minutes for security verification.")
        logger.info("Please complete any security checks that appear in the browser.")
        logger.info("After verification, the business post will be created automatically.")
        
        # Wait for 5 minutes to allow for manual verification
        await page.wait_for_timeout(300000)  # 5 minutes
        
        # Check if we're logged in after the wait period
        current_url = page.url
        logger.info(f"Current URL: {current_url}")
        
        if "feed" in current_url:
            logger.info("Still logged in, proceeding with post creation...")
            
            try:
                # Wait for page to load completely
                await page.wait_for_timeout(3000)
                
                # Look for the create post button
                try:
                    await page.wait_for_selector("button[aria-label='Create a post']", timeout=10000)
                    await page.click("button[aria-label='Create a post']")
                    logger.info("Clicked create post button")
                except:
                    # Try alternative selectors
                    try:
                        await page.click("button.share-creation-state__open-create-share-modal")
                        logger.info("Clicked alternative create post button")
                    except:
                        logger.error("Could not find create post button")
                        await browser.close()
                        return
                
                # Wait for editor and fill content
                try:
                    await page.wait_for_selector("div[contenteditable='true']", timeout=10000)
                    await page.fill("div[contenteditable='true']", content)
                    logger.info("Business content filled successfully")
                except:
                    logger.error("Could not find or fill content editor")
                    await browser.close()
                    return
                
                # Wait and click post button
                await page.wait_for_timeout(2000)
                
                try:
                    await page.click("button[aria-label='Post']")
                    logger.info("Post published successfully!")
                except:
                    # Try alternative post button
                    try:
                        await page.click("button:has-text('Post')")
                        logger.info("Post published with alternative button!")
                    except:
                        logger.error("Could not click post button")
                
                # Wait to see the result
                await page.wait_for_timeout(5000)
                
            except Exception as e:
                logger.error(f"Error during posting: {e}")
        else:
            logger.info("Still on verification page - manual verification may still be needed.")
        
        logger.info("Browser will stay open for 30 more seconds...")
        await page.wait_for_timeout(30000)
        await browser.close()
        logger.info("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())
