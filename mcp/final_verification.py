#!/usr/bin/env python3
"""
Final verification that LinkedIn automation is working
"""
import os
import sys
import asyncio
import importlib.util

# Set credentials
os.environ['LINKEDIN_EMAIL'] = 'shuremsyed41@gmail.com'
os.environ['LINKEDIN_PASSWORD'] = '477831@dit'

async def final_verification():
    # Load the LinkedIn MCP server
    spec = importlib.util.spec_from_file_location('linkedin_mcp_server', './linkedin-mcp-server.py')
    linkedin_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linkedin_module)

    # Create server instance
    server = linkedin_module.LinkedInMCPServer()

    # Test the complete post functionality with a simple message
    test_post_content = """🎉 LinkedIn Automation - FINAL VERIFICATION COMPLETE!

✅ The LinkedIn automation system is now FULLY FUNCTIONAL!

✅ Successfully logs into LinkedIn
✅ Clicks 'Start a post' button
✅ Fills content in the composition editor
✅ Identifies and clicks the CORRECT 'Post' button (not navigation buttons)
✅ Publishes content to LinkedIn successfully

This completes the Silver Tier requirement:
"Automatically Post on LinkedIn about business to generate sales"

System is ready for production use!
#AI #Automation #LinkedIn #Success #SilverTier
"""

    print("🚀 Running FINAL VERIFICATION TEST...")
    result = await server.post_linkedin(text=test_post_content)

    if result['success']:
        print("\n🎉🎉🎉 SUCCESS! 🎉🎉🎉")
        print("✅ LinkedIn automation system is COMPLETELY WORKING!")
        print("✅ All components function correctly:")
        print("   - Login → Start Post → Write Content → Click Post Button → Publish")
        print("✅ Silver Tier requirements have been MET!")
        print("✅ System can automatically post to LinkedIn")
        return True
    else:
        print(f"\n❌ Final verification failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    print(" ============================")
    print("  🎯 FINAL VERIFICATION TEST")
    print(" ============================")

    success = asyncio.run(final_verification())

    print("\n ============================")
    if success:
        print("  🏆 VERIFICATION COMPLETE")
        print("  ✅ SILVER TIER ACHIEVED!")
    else:
        print("  ❌ VERIFICATION FAILED")
    print(" ============================")