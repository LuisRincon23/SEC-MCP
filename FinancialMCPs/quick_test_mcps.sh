#!/bin/bash
#
# Quick MCP Verification Script
# Tests each MCP with a simple command through Claude Code
#

echo "🧪 Quick MCP Verification Test"
echo "============================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test function
test_mcp() {
    local mcp_name=$1
    local test_command=$2
    
    echo -n "Testing $mcp_name... "
    
    # Create test file
    echo "$test_command" > /tmp/test_mcp_command.txt
    
    # Run through Claude and capture output
    if timeout 30 claude --no-chat < /tmp/test_mcp_command.txt > /tmp/test_mcp_output.txt 2>&1; then
        if grep -q "error" /tmp/test_mcp_output.txt; then
            echo -e "${YELLOW}⚠️  Warning - Check output${NC}"
            echo "  Output: $(head -1 /tmp/test_mcp_output.txt)"
        else
            echo -e "${GREEN}✅ Success${NC}"
        fi
    else
        echo -e "${RED}❌ Failed${NC}"
    fi
}

echo "📋 Testing Financial MCPs..."
echo ""

# Test each MCP
test_mcp "SEC" 'Use SEC to get current price for ticker "AAPL"'
test_mcp "NEWS-SENTIMENT" 'Use NEWS-SENTIMENT to analyze sentiment for ticker "TSLA"'
test_mcp "X-SENTIMENT" 'Use X-SENTIMENT to analyze ticker sentiment for ticker "BTC"'
test_mcp "ANALYST-RATINGS" 'Use ANALYST-RATINGS to get consensus rating for ticker "NVDA"'
test_mcp "INSTITUTIONAL" 'Use INSTITUTIONAL to get top holders for ticker "AAPL"'
test_mcp "ALTERNATIVE-DATA" 'Use ALTERNATIVE-DATA to get reddit sentiment for query "GME stock"'
test_mcp "INDUSTRY-ASSUMPTIONS" 'Use INDUSTRY-ASSUMPTIONS-ENGINE to calculate WACC for ticker "MSFT"'
test_mcp "ECONOMIC-DATA" 'Use ECONOMIC-DATA-COLLECTOR to get economic indicators'
test_mcp "RESEARCH-ADMIN" 'Use RESEARCH-ADMINISTRATOR to create research summary for ticker "GOOGL"'

echo ""
echo "============================"
echo "✅ Quick test complete!"
echo ""
echo "For detailed testing, run:"
echo "  python test_all_mcps.py"