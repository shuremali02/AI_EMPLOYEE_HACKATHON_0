#!/usr/bin/env python3
"""
Script to run LinkedIn automation with credentials loaded properly
"""
import os
import sys
import asyncio
import importlib.util
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Set credentials directly in this script for testing
os.environ['LINKEDIN_EMAIL'] = 'shuremsyed41@gmail.com'
os.environ['LINKEDIN_PASSWORD'] = '477831@dit'

async def run_linkedin_test():
    print("🚀 Starting LinkedIn Automation Test...")
    print(f"Using LinkedIn account: {os.getenv('LINKEDIN_EMAIL')}")

    # Load the LinkedIn MCP server
    spec = importlib.util.spec_from_file_location('linkedin_mcp_server', './linkedin-mcp-server.py')
    linkedin_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linkedin_module)

    # Create server instance
    server = linkedin_module.LinkedInMCPServer()

    # Test profile info first
    try:
        profile_info = await server.get_profile_info()
        print(f"✅ Profile info retrieved: {profile_info['email']}")
    except Exception as e:
        print(f"❌ Failed to get profile info: {e}")
        return False

    # Test post creation
    test_content = """🚀 LinkedIn Automation Test Post!

Successfully implemented Silver Tier LinkedIn automation for the AI Employee Hackathon!

✅ Connected to LinkedIn successfully
✅ Logged in with provided credentials
✅ Created this automated post
✅ Used advanced browser automation techniques
✅ Implemented multiple fallback strategies

This demonstrates the Silver Tier requirement:
"Automatically Post on LinkedIn about business to generate sales"

#AI #Automation #LinkedIn #SilverTier #Hackathon2026
"""

    print("\n📝 Attempting to create LinkedIn post...")
    result = await server.post_linkedin(text=test_content)

    print(f"\n📋 Result: {result}")

    if result['success']:
        print("\n🎉 SUCCESS: LinkedIn post operation completed!")
        print("✅ The post should now be live on LinkedIn")
        print("✨ Silver Tier LinkedIn automation is working perfectly!")
        return True
    else:
        print(f"\n❌ FAILED: {result.get('error', 'Operation failed')}")
        return False

if __name__ == "__main__":
    print(" ============================")
    print("  LINKEDIN AUTOMATION TEST")
    print(" ============================")

    success = asyncio.run(run_linkedin_test())
    print("\n ============================")
    if success:
        print("  ✅ TEST PASSED")
    else:
        print("  ❌ TEST FAILED")
    print(" ============================")