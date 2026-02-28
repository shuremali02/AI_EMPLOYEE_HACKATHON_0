#!/usr/bin/env python3
"""
Simple verification of LinkedIn automation status
"""
import os
import sys
import asyncio
import importlib.util

async def simple_verify():
    # Load the LinkedIn MCP server
    spec = importlib.util.spec_from_file_location('linkedin_mcp_server', './linkedin-mcp-server.py')
    linkedin_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linkedin_module)

    # Create server instance
    try:
        server = linkedin_module.LinkedInMCPServer()
        print("✅ LinkedInMCPServer created successfully")
    except Exception as e:
        print(f"❌ Failed to create server: {e}")
        return False

    # Test get_profile_info
    try:
        profile = await server.get_profile_info()
        print(f"✅ Profile info retrieved: {profile['email']}")
    except Exception as e:
        print(f"❌ Failed to get profile info: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Simple LinkedIn Server Verification")
    print("="*40)

    success = asyncio.run(simple_verify())

    if success:
        print("\n✅ Server structure is valid")
    else:
        print("\n❌ Server structure has issues")