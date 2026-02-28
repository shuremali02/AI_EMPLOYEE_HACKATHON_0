#!/usr/bin/env python3
"""
Comprehensive LinkedIn Automation Test
This script tests the complete LinkedIn automation workflow from login to post publishing
"""
import os
import sys
import importlib.util
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_linkedin_automation():
    """
    Comprehensive test of LinkedIn automation functionality
    """
    logger.info("="*60)
    logger.info("LINKEDIN AUTOMATION COMPREHENSIVE TEST")
    logger.info("="*60)

    # Load the LinkedIn MCP Server module
    spec = importlib.util.spec_from_file_location('linkedin_mcp_server', './linkedin-mcp-server.py')
    linkedin_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linkedin_module)

    logger.info("✅ LinkedIn MCP Server module loaded successfully")

    # Check if required environment variables are set
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')

    if not email or not password:
        logger.error("❌ LinkedIn credentials not found in environment variables")
        logger.error("Please ensure LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set")
        return False

    logger.info(f"✅ LinkedIn credentials found: {email}")

    try:
        # Create the server instance
        server = linkedin_module.LinkedInMCPServer()
        logger.info("✅ LinkedInMCPServer instance created successfully")

        # Test profile info method
        profile_info = await server.get_profile_info()
        logger.info(f"✅ Profile info retrieved: {profile_info}")

        # Test the post_linkedin method with a sample post
        sample_post = """
        🚀 Testing LinkedIn automation from AI Employee system!

        This post was automatically created by our Silver Tier automation system as part of the Personal AI Employee Hackathon.

        Key achievements:
        ✅ Connected to LinkedIn via browser automation
        ✅ Successfully logged in with provided credentials
        ✅ Identified and clicked 'Start a post' button
        ✅ Filled content in the post editor
        ✅ Attempting to publish this post

        #AI #Automation #LinkedIn #SilverTier #Hackathon
        """

        logger.info("Attempting to create LinkedIn post...")
        result = await server.post_linkedin(text=sample_post)

        logger.info(f"Post operation result: {result}")

        if result.get('success'):
            logger.info("🎉 SUCCESS: LinkedIn post created successfully!")
            logger.info("✅ LinkedIn automation is fully functional!")
            return True
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.warning(f"⚠️  Post creation partially successful or failed: {error_msg}")
            logger.info("⚠️  This may indicate the post content was filled but final publishing had issues")
            return False

    except Exception as e:
        logger.error(f"❌ Error during LinkedIn automation test: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def main():
    """
    Main function to run the LinkedIn automation test
    """
    logger.info("Starting LinkedIn Automation Test...")

    # Check if we're in the correct directory
    if not os.path.exists('./linkedin-mcp-server.py'):
        logger.error("❌ LinkedIn MCP Server file not found in current directory")
        logger.error("Please run this script from the MCP directory")
        return False

    # Run the async test
    success = asyncio.run(test_linkedin_automation())

    logger.info("="*60)
    if success:
        logger.info("🎉 LINKEDIN AUTOMATION TEST PASSED!")
        logger.info("✅ Silver Tier LinkedIn functionality is working correctly")
    else:
        logger.info("❌ LINKEDIN AUTOMATION TEST FAILED")
        logger.info("⚠️  Some components may need additional debugging")
    logger.info("="*60)

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)