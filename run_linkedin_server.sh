#!/bin/bash
# Load environment variables from .env file
set -a
source .env
set +a

# Run the LinkedIn MCP server with the proper environment
exec python3 mcp/linkedin-mcp-server.py