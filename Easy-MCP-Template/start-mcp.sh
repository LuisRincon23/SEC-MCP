#!/bin/bash
# MCP Server startup script for Claude Desktop
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the MCP server in stdio mode
python main.py --transport stdio