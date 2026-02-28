#!/usr/bin/env python3
"""
Email MCP Server
Model Context Protocol server for sending emails via SMTP
"""

import asyncio
import json
import logging
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailMCPServer:
    def __init__(self):
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')

        if not self.email_address or not self.email_password:
            logger.error("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set")
            sys.exit(1)

    async def send_email(self, to: str, subject: str, body: str, **kwargs) -> Dict[str, Any]:
        """Send an email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP session
            server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP
            server.starttls()  # Enable security
            server.login(self.email_address, self.email_password)

            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, to, text)
            server.quit()

            logger.info(f"Email sent successfully to {to}")

            return {
                "success": True,
                "message": f"Email sent successfully to {to}",
                "to": to,
                "subject": subject
            }

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_email_info(self) -> Dict[str, Any]:
        """Get information about the configured email account"""
        return {
            "email_address": self.email_address,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "supports_tls": True
        }

    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Return the server's capabilities"""
        return [
            {
                "name": "send_email",
                "description": "Send an email via SMTP",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body content"}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "get_email_info",
                "description": "Get information about the configured email account",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

async def handle_request(server: EmailMCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP requests"""
    request_id = request.get("request_id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "mcp.initialize":
        return {
            "request_id": request_id,
            "result": {
                "server_info": {
                    "name": "Email MCP Server",
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

        if tool_name == "send_email":
            result = await server.send_email(**tool_arguments)
        elif tool_name == "get_email_info":
            result = await server.get_email_info()
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
    server = EmailMCPServer()

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