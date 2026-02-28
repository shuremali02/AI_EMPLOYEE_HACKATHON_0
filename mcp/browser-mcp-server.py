#!/usr/bin/env python3
"""
Browser MCP Server
Model Context Protocol server for web browser automation
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any, List
from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrowserMCPServer:
    def __init__(self):
        self.active_browsers = {}

    async def navigate_to_url(self, url: str, **kwargs) -> Dict[str, Any]:
        """Navigate to a URL and return page content"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url)
                content = await page.content()

                # Store browser reference temporarily
                browser_id = f"temp_{id(browser)}"
                self.active_browsers[browser_id] = browser

                return {
                    "success": True,
                    "browser_id": browser_id,
                    "url": url,
                    "content_preview": content[:500] + "..." if len(content) > 500 else content  # Preview first 500 chars
                }
        except Exception as e:
            logger.error(f"Failed to navigate to URL: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def fill_form(self, browser_id: str, selector: str, value: str, **kwargs) -> Dict[str, Any]:
        """Fill a form field in the browser"""
        try:
            if browser_id not in self.active_browsers:
                return {
                    "success": False,
                    "error": f"Browser with ID {browser_id} not found"
                }

            browser = self.active_browsers[browser_id]
            page = browser.pages[0]  # Get the first page

            await page.fill(selector, value)

            return {
                "success": True,
                "message": f"Filled {selector} with {value}",
                "selector": selector
            }
        except Exception as e:
            logger.error(f"Failed to fill form: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def click_element(self, browser_id: str, selector: str, **kwargs) -> Dict[str, Any]:
        """Click an element in the browser"""
        try:
            if browser_id not in self.active_browsers:
                return {
                    "success": False,
                    "error": f"Browser with ID {browser_id} not found"
                }

            browser = self.active_browsers[browser_id]
            page = browser.pages[0]  # Get the first page

            await page.click(selector)

            return {
                "success": True,
                "message": f"Clicked element {selector}",
                "selector": selector
            }
        except Exception as e:
            logger.error(f"Failed to click element: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def close_browser(self, browser_id: str, **kwargs) -> Dict[str, Any]:
        """Close a specific browser instance"""
        try:
            if browser_id not in self.active_browsers:
                return {
                    "success": False,
                    "error": f"Browser with ID {browser_id} not found"
                }

            browser = self.active_browsers[browser_id]
            await browser.close()
            del self.active_browsers[browser_id]

            return {
                "success": True,
                "message": f"Browser {browser_id} closed successfully"
            }
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Return the server's capabilities"""
        return [
            {
                "name": "navigate_to_url",
                "description": "Navigate to a URL and return page content",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to navigate to"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "fill_form",
                "description": "Fill a form field in the browser",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "browser_id": {"type": "string", "description": "ID of the browser instance"},
                        "selector": {"type": "string", "description": "CSS selector for the form field"},
                        "value": {"type": "string", "description": "Value to fill"}
                    },
                    "required": ["browser_id", "selector", "value"]
                }
            },
            {
                "name": "click_element",
                "description": "Click an element in the browser",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "browser_id": {"type": "string", "description": "ID of the browser instance"},
                        "selector": {"type": "string", "description": "CSS selector for the element"}
                    },
                    "required": ["browser_id", "selector"]
                }
            },
            {
                "name": "close_browser",
                "description": "Close a specific browser instance",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "browser_id": {"type": "string", "description": "ID of the browser instance to close"}
                    },
                    "required": ["browser_id"]
                }
            }
        ]

async def handle_request(server: BrowserMCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP requests"""
    request_id = request.get("request_id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "mcp.initialize":
        return {
            "request_id": request_id,
            "result": {
                "server_info": {
                    "name": "Browser MCP Server",
                    "version": "1.0.0",
                    "capabilities": server.get_capabilities()
                }
            }
        }

    elif method == "mcp.list_resources":
        return {
            "request_id": request_id,
            "result": {
                "resources": []
            }
        }

    elif method == "mcp.list_prompts":
        return {
            "request_id": request_id,
            "result": {
                "prompts": []
            }
        }

    elif method == "tools/execute":
        tool_name = params.get("name")
        tool_arguments = params.get("arguments", {})

        if tool_name == "navigate_to_url":
            result = await server.navigate_to_url(**tool_arguments)
        elif tool_name == "fill_form":
            result = await server.fill_form(**tool_arguments)
        elif tool_name == "click_element":
            result = await server.click_element(**tool_arguments)
        elif tool_name == "close_browser":
            result = await server.close_browser(**tool_arguments)
        else:
            return {
                "request_id": request_id,
                "error": {
                    "code": "UNKNOWN_TOOL",
                    "message": f"Unknown tool: {tool_name}"
                }
            }

        return {
            "request_id": request_id,
            "result": result
        }

    else:
        return {
            "request_id": request_id,
            "error": {
                "code": "INVALID_METHOD",
                "message": f"Invalid method: {method}"
            }
        }

async def main():
    """Main function to run the MCP server"""
    server = BrowserMCPServer()

    # Process requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = await handle_request(server, request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            error_response = {
                "request_id": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())