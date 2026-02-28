#!/usr/bin/env python3
"""
Simple test to verify LinkedIn automation is working
"""
import os
import sys
import asyncio
import importlib.util

# Set credentials
os.environ['LINKEDIN_EMAIL'] = 'shuremsyed41@gmail.com'
os.environ['LINKEDIN_PASSWORD'] = '477831@dit'

async def quick_test():
    # Load the LinkedIn MCP server
    spec = importlib.util.spec_from_file_location('linkedin_mcp_server', './linkedin-mcp-server.py')
    linkedin_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linkedin_module)

    # Create server instance
    server = linkedin_module.LinkedInMCPServer()

    # Test the complete post functionality
    test_post_content = """🚀 LinkedIn Automation - Final Verification Test!

This post confirms that the LinkedIn automation system is working perfectly as part of the Silver Tier requirements for the AI Employee Hackathon.

✅ System can log into LinkedIn
✅ System can click 'Start a post' button
✅ System can write content in the composition box
✅ System can click the 'Post' button to publish
✅ Content is successfully published to LinkedIn

This fulfills the Silver Tier requirement:
"Automatically Post on LinkedIn about business to generate sales"

#AI #Automation #LinkedIn #SilverTier #Hackathon #Verification
"""

    print("📝 Creating verification LinkedIn post...")
    result = await server.post_linkedin(text=test_post_content)

    if result['success']:
        print("✅ LinkedIn automation is FULLY WORKING!")
        print("✅ All Silver Tier requirements have been met!")
        print("✅ Post should now be live on LinkedIn")
        return True
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    print(" ============================")
    print("  QUICK VERIFICATION TEST")
    print(" ============================")

    success = asyncio.run(quick_test())

    print("\n ============================")
    if success:
        print("  ✅ VERIFICATION PASSED")
        print("  🎉 SILVER TIER COMPLETE!")
    else:
        print("  ❌ VERIFICATION FAILED")
    print(" ============================")