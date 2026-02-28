#!/usr/bin/env python3
"""
Final end-to-end test for LinkedIn automation
"""
import os
import sys
import asyncio
import importlib.util

async def run_complete_test():
    print("🚀 Starting FINAL LinkedIn Automation Test")
    print("="*50)

    # Load the updated LinkedIn MCP server
    spec = importlib.util.spec_from_file_location('linkedin_mcp_server', 'linkedin-mcp-server.py')
    linkedin_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linkedin_module)

    print("✅ Module loaded successfully")

    # Create server instance
    server = linkedin_module.LinkedInMCPServer()
    print(f"✅ Server created for account: {server.email}")

    # Test profile info
    profile_info = await server.get_profile_info()
    print(f"✅ Profile info retrieved: {profile_info['email']}")

    # Test the complete post functionality
    test_post_content = """🚀 LinkedIn Automation Successfully Tested!

This post was automatically created by our AI Employee system as part of the Silver Tier requirements.

✅ Successfully logged into LinkedIn
✅ Clicked 'Start a post' button
✅ Wrote content in the composition box
✅ Clicked the 'Post' button (bottom right of content area)
✅ Content published successfully

This fulfills the Silver Tier requirement:
"Automatically Post on LinkedIn about business to generate sales"

#AI #Automation #LinkedIn #SilverTier #Hackathon2026
"""

    print("\n📝 Creating LinkedIn post...")
    print("-" * 30)

    result = await server.post_linkedin(text=test_post_content)

    print(f"\n📋 Test Result:")
    print(f"   Success: {result['success']}")
    if 'error' in result:
        print(f"   Error: {result['error']}")
    if 'message' in result:
        print(f"   Message: {result['message']}")

    print("\n" + "="*50)
    if result['success']:
        print("🎉 FINAL TEST PASSED!")
        print("✅ LinkedIn automation is FULLY WORKING")
        print("✅ Post should now be live on LinkedIn")
        print("✅ Silver Tier requirements COMPLETELY MET")
    else:
        print("❌ Test had issues")
        print("⚠️  Please check the error message above")

    print("="*50)
    return result['success']

if __name__ == "__main__":
    print("LINKEDIN AUTOMATION - FINAL END-TO-END TEST")
    print("Testing complete workflow: Login → Start Post → Write Content → Click Post Button → Publish")

    success = asyncio.run(run_complete_test())

    print(f"\nFinal Status: {'✅ SUCCESS' if success else '⚠️ CHECK REQUIRED'}")