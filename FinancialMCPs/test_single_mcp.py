#!/usr/bin/env python3
"""
Simple test for a single MCP to debug issues
"""

import asyncio
import json
import subprocess
from pathlib import Path

async def test_mcp():
    """Test SEC MCP directly"""
    print("Testing SEC MCP...")
    
    # Path to MCP
    mcp_path = "/Users/LuisRincon/SEC-MCP/FinancialMCPs/SEC_SCRAPER_MCP/start-mcp.sh"
    
    # Start the MCP process
    process = await asyncio.create_subprocess_exec(
        mcp_path,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Send initialization
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "1.0",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    process.stdin.write((json.dumps(init_request) + '\n').encode())
    await process.stdin.drain()
    
    # Read initialization response
    init_response = await process.stdout.readline()
    print(f"Init response: {init_response.decode()}")
    
    # Wait a bit for initialization to complete
    await asyncio.sleep(0.5)
    
    # List tools
    list_tools_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    
    process.stdin.write((json.dumps(list_tools_request) + '\n').encode())
    await process.stdin.drain()
    
    # Read tools list response
    tools_response = await process.stdout.readline()
    print(f"Tools response: {tools_response.decode()}")
    
    # Call a tool
    tool_call_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_current_price",
            "arguments": {"ticker": "AAPL"}
        },
        "id": 3
    }
    
    process.stdin.write((json.dumps(tool_call_request) + '\n').encode())
    await process.stdin.drain()
    
    # Read tool response
    tool_response = await process.stdout.readline()
    print(f"Tool response: {tool_response.decode()}")
    
    # Terminate process
    process.terminate()
    await process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp())