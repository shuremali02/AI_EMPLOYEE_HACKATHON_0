#!/usr/bin/env python3
import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def debug_linkedin_elements():
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')

    print(f"Debugging LinkedIn elements for account: {email}")
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
                print("Login might have taken longer than expected.")
        
        # Wait for page to fully load
        await page.wait_for_timeout(5000)

        print("\n" + "="*60)
        print("DEBUGGING: Available elements related to posting on LinkedIn")
        print("="*60)
        
        # Find all potential posting-related elements
        possible_elements = [
            "button",
            "[role='button']",
            "*:has-text('Post')",
            "*:has-text('Share')", 
            "*:has-text('Start')",
            "*:has-text('Create')",
            "*:has-text('Write')",
            "[aria-label*='post' i]",
            "[aria-label*='share' i]",
            "[aria-label*='create' i]",
            "[data-test*='post' i]",
            "[data-test*='share' i]",
            "[data-test*='create' i]",
            ".share-box*", 
            "*[class*='post' i]",
            "*[class*='share' i]",
            "*[class*='create' i]"
        ]
        
        print("\n1. Looking for elements by various selectors...")
        for i, selector in enumerate(possible_elements):
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"\nFound {len(elements)} elements with selector: {selector}")
                    for j, element in enumerate(elements[:5]):  # Show first 5 matches
                        try:
                            text = await element.text_content()
                            aria_label = await element.get_attribute('aria-label')
                            class_name = await element.get_attribute('class')
                            tag_name = await element.evaluate('el => el.tagName')
                            print(f"  {j+1}. {tag_name}: text='{text[:50]}...', aria-label='{aria_label}', class='{class_name[:50]}...'")
                        except Exception as e:
                            print(f"  {j+1}. Error getting element details: {e}")
            except Exception as e:
                print(f"  Error with selector {selector}: {e}")
        
        print("\n2. Looking specifically for the main post area in the feed...")
        # Try to find the main share box area
        share_selectors = [
            ".share-box-feed-entry__container",
            "[data-test-id='share-box-feed-entry']",
            ".share-box-feed-entry__trigger",
            ".global-rail-v2__feed-content .share-box-feed-entry",
            "[data-test-shares-create-destination-type='FEED']"
        ]
        
        for selector in share_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"Found share box element: {selector}")
                    text = await element.text_content()
                    class_name = await element.get_attribute('class')
                    print(f"  Content: '{text[:100]}...'")
                    print(f"  Class: {class_name}")
                    
                    # Try to click this element
                    try:
                        await element.click()
                        print("  ✅ Successfully clicked the share box!")
                        print("  (If the post editor appeared, this is the correct element)")
                    except Exception as e:
                        print(f"  ⚠️ Could not click: {e}")
                    break
            except Exception as e:
                print(f"  Error with share selector {selector}: {e}")
        
        print("\n3. Looking for all buttons on the page...")
        try:
            all_buttons = await page.query_selector_all("button")
            print(f"Found {len(all_buttons)} total buttons on the page")
            
            # Filter for likely post-related buttons
            post_related = []
            for button in all_buttons:
                try:
                    text = await button.text_content()
                    aria_label = await button.get_attribute('aria-label')
                    if text and ('post' in text.lower() or 'share' in text.lower() or 
                               'create' in text.lower() or 'start' in text.lower()):
                        post_related.append((button, text, aria_label))
                except:
                    continue
            
            print(f"Found {len(post_related)} post-related buttons:")
            for i, (button, text, aria_label) in enumerate(post_related):
                print(f"  {i+1}. text='{text}', aria-label='{aria_label}'")
                
        except Exception as e:
            print(f"Error getting buttons: {e}")
        
        print("\n4. Manual step: Please identify the 'Start a post' button in the browser and note its position.")
        print("The browser will stay open for 5 minutes for inspection...")
        print("Look for a button that says 'Start a post', 'Create a post', or shows a text field with emoji/gif options.")
        
        await page.wait_for_timeout(300000)  # 5 minutes
        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_linkedin_elements())
