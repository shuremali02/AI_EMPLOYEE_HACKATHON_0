#!/usr/bin/env python3
"""
Automated LinkedIn Poster
Generates and posts LinkedIn content about business activities to generate sales
"""

import os
import time
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkedInPoster:
    def __init__(self):
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')

        if not self.email or not self.password:
            raise ValueError("LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables must be set")

    def generate_business_post_content(self):
        """Generate engaging business-related LinkedIn post content"""
        business_topics = [
            "industry insights",
            "business growth strategies",
            "professional development tips",
            "market trends",
            "innovation in business",
            "leadership lessons",
            "entrepreneurship journey",
            "team building",
            "customer success stories",
            "product launches"
        ]

        call_to_action_phrases = [
            "What are your thoughts on this?",
            "How has this impacted your business?",
            "Would love to hear your perspective!",
            "Feel free to share your experience.",
            "Let's discuss in the comments!",
            "Would appreciate your input on this."
        ]

        hashtags = [
            "#BusinessGrowth", "#Entrepreneurship", "#Leadership",
            "#Innovation", "#Marketing", "#Sales", "#StartupLife",
            "#BusinessStrategy", "#ProfessionalDevelopment", "#IndustryInsights"
        ]

        # Generate a random business post
        topic = random.choice(business_topics)
        cta = random.choice(call_to_action_phrases)
        selected_hashtags = random.sample(hashtags, k=3)

        post_templates = [
            f" fascinating developments in {topic} are reshaping how we approach business.\n\n"
            f"Key takeaways:\n"
            f"• First important point\n"
            f"• Second key insight\n"
            f"• Third actionable tip\n\n"
            f"{cta}\n\n"
            f"{' '.join(selected_hashtags)}",

            f"Just experienced some incredible {topic} that reinforced the importance of staying adaptable in business.\n\n"
            f"What I learned:\n"
            f"- Lesson one with impact\n"
            f"- Lesson two with application\n"
            f"- Lesson three for future growth\n\n"
            f"{cta}\n\n"
            f"{' '.join(selected_hashtags)}",

            f"The landscape of {topic} continues to evolve at a rapid pace.\n\n"
            f"Three trends I'm observing:\n"
            f"๏ Trend one and implications\n"
            f"๏ Trend two and impact\n"
            f"๏ Trend three and opportunities\n\n"
            f"{cta}\n\n"
            f"{' '.join(selected_hashtags)}",

            f"Reflecting on recent {topic}, I've identified some patterns that might interest fellow professionals.\n\n"
            f"Key observations:\n"
            f"→ Observation one with context\n"
            f"→ Observation two with evidence\n"
            f"→ Observation three with implications\n\n"
            f"{cta}\n\n"
            f"{' '.join(selected_hashtags)}"
        ]

        return random.choice(post_templates)

    def login_to_linkedin(self, page):
        """Login to LinkedIn using provided credentials"""
        logger.info("Navigating to LinkedIn login page...")
        page.goto("https://www.linkedin.com/login")

        # Fill in login credentials
        logger.info("Entering login credentials...")
        page.fill("input#username", self.email)
        page.fill("input#password", self.password)

        # Click login button
        logger.info("Clicking login button...")
        page.click("button[type='submit']")

        # Wait for login to complete
        logger.info("Waiting for login to complete...")
        page.wait_for_url("https://www.linkedin.com/feed/", timeout=30000)

        logger.info("Successfully logged in to LinkedIn")

    def create_post(self, content):
        """Create and publish a LinkedIn post with the given content"""
        try:
            with sync_playwright() as p:
                # Launch browser
                logger.info("Launching browser...")
                browser = p.chromium.launch(headless=False)  # Set to True for headless mode
                page = browser.new_page()

                # Login to LinkedIn
                self.login_to_linkedin(page)

                # Click on the create post button
                logger.info("Clicking create post button...")
                page.wait_for_selector("button[aria-label='Create a post']", timeout=10000)
                page.click("button[aria-label='Create a post']")

                # Wait for the text area to be available
                logger.info("Waiting for post editor...")
                page.wait_for_selector("div[contenteditable='true']", timeout=10000)

                # Fill the post content
                logger.info("Filling post content...")
                page.fill("div[contenteditable='true']", content)

                # Wait a bit to ensure content is filled
                page.wait_for_timeout(2000)

                # Check if there's an image/video option and bypass it if needed
                try:
                    # Look for the post button (might be disabled initially)
                    post_button = page.wait_for_selector("button[aria-label='Post'][disabled=false]", timeout=5000)
                    post_button.click()
                except:
                    # If the above doesn't work, try clicking any enabled post button
                    page.click("button[aria-label='Post']")

                # Wait for post to be published
                logger.info("Waiting for post to publish...")
                page.wait_for_timeout(3000)

                # Verify post was made (optional - check if we're back on feed)
                current_url = page.url
                if "feed" in current_url:
                    logger.info("LinkedIn post created successfully!")
                else:
                    logger.warning("Post may not have been published - verify manually")

                browser.close()
                return True

        except Exception as e:
            logger.error(f"Failed to create LinkedIn post: {str(e)}")
            return False

    def run_posting_cycle(self):
        """Run one cycle of generating and posting LinkedIn content"""
        logger.info("Starting LinkedIn posting cycle...")

        # Generate post content
        content = self.generate_business_post_content()
        logger.info(f"Generated post content:\n{content[:100]}...")

        # Create and post to LinkedIn
        success = self.create_post(content)

        if success:
            logger.info("LinkedIn posting cycle completed successfully")
            return True
        else:
            logger.error("LinkedIn posting cycle failed")
            return False

def main():
    """Main function to run the automated LinkedIn poster"""
    try:
        poster = LinkedInPoster()

        # For now, just run one posting cycle
        # In a production environment, this could be scheduled to run periodically
        poster.run_posting_cycle()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()