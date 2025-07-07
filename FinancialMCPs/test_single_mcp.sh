#!/bin/bash
# Test a single MCP server to verify it works

MCP_NAME=$1

if [ -z "$MCP_NAME" ]; then
    echo "Usage: ./test_single_mcp.sh <MCP_NAME>"
    echo "Example: ./test_single_mcp.sh SEC_SCRAPER_MCP"
    exit 1
fi

echo "Testing $MCP_NAME..."
cd "/Users/LuisRincon/SEC-MCP/FinancialMCPs/$MCP_NAME"

# Test if start script exists and is executable
if [ ! -x "./start-mcp.sh" ]; then
    echo "Error: start-mcp.sh not found or not executable"
    exit 1
fi

# Run the start script with a test input
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "1.0", "capabilities": {}}, "id": 1}' | ./start-mcp.sh 2>&1 | head -20

echo "If you see a response with 'result' and 'serverInfo', the MCP is working correctly."