#!/bin/bash

echo "🔧 Financial MCPs Fix Script"
echo "=========================="

# Define MCP directories
MCPS=(
    "SEC_SCRAPER_MCP"
    "NEWS_SENTIMENT_SCRAPER"
    "ANALYST_RATINGS_SCRAPER"
    "INSTITUTIONAL_SCRAPER"
    "ALTERNATIVE_DATA_SCRAPER"
    "INDUSTRY_ASSUMPTIONS_ENGINE"
    "ECONOMIC_DATA_COLLECTOR"
    "RESEARCH_ADMINISTRATOR"
)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check directory
cd /Users/LuisRincon/SEC-MCP/FinancialMCPs || exit 1

echo "📂 Checking MCPs directory..."
echo ""

# Step 1: Fix permissions
echo "1️⃣ Fixing permissions on all start scripts..."
for mcp in "${MCPS[@]}"; do
    if [ -f "$mcp/start-mcp.sh" ]; then
        chmod +x "$mcp/start-mcp.sh"
        echo -e "${GREEN}✓${NC} Fixed permissions for $mcp/start-mcp.sh"
    else
        echo -e "${RED}✗${NC} Missing start script for $mcp"
    fi
done
echo ""

# Step 2: Check Python virtual environment
echo "2️⃣ Checking Python virtual environment..."
if [ -f "/Users/LuisRincon/SEC-MCP/.venv/bin/python" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment found"
    /Users/LuisRincon/SEC-MCP/.venv/bin/python --version
else
    echo -e "${RED}✗${NC} Virtual environment not found!"
    echo "   Run: cd /Users/LuisRincon/SEC-MCP && python -m venv .venv"
fi
echo ""

# Step 3: Check dependencies
echo "3️⃣ Checking Python dependencies..."
/Users/LuisRincon/SEC-MCP/.venv/bin/python -c "
import sys
try:
    import mcp
    print('✓ mcp package installed')
except ImportError:
    print('✗ mcp package missing - run: pip install mcp')
    sys.exit(1)

try:
    import aiohttp
    print('✓ aiohttp package installed')
except ImportError:
    print('✗ aiohttp package missing - run: pip install aiohttp')

try:
    import bs4
    print('✓ beautifulsoup4 package installed')
except ImportError:
    print('✗ beautifulsoup4 package missing - run: pip install beautifulsoup4')

try:
    import numpy
    print('✓ numpy package installed')
except ImportError:
    print('✗ numpy package missing - run: pip install numpy')

try:
    import pandas
    print('✓ pandas package installed')
except ImportError:
    print('✗ pandas package missing - run: pip install pandas')
"
echo ""

# Step 4: Test each MCP
echo "4️⃣ Testing each MCP server..."
echo ""

test_mcp() {
    local mcp=$1
    echo -n "Testing $mcp... "
    
    cd "/Users/LuisRincon/SEC-MCP/FinancialMCPs/$mcp" 2>/dev/null || {
        echo -e "${RED}directory not found${NC}"
        return
    }
    
    # Send initialize request and check response
    response=$(echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "1.0", "capabilities": {}}, "id": 1}' | timeout 5 ./start-mcp.sh 2>&1)
    
    if echo "$response" | grep -q '"result".*"serverInfo"'; then
        echo -e "${GREEN}✓ Working${NC}"
    elif echo "$response" | grep -q "error"; then
        echo -e "${RED}✗ Error in response${NC}"
        echo "   Error: $(echo "$response" | grep -o '"message":"[^"]*"' | head -1)"
    else
        echo -e "${YELLOW}⚠ Unknown response${NC}"
    fi
    
    cd - > /dev/null
}

for mcp in "${MCPS[@]}"; do
    test_mcp "$mcp"
done
echo ""

# Step 5: Check Claude Desktop config
echo "5️⃣ Checking Claude Desktop configuration..."
CONFIG_FILE="/Users/LuisRincon/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✓${NC} Config file exists"
    
    # Check if all MCPs are configured
    missing_mcps=()
    for mcp in "${MCPS[@]}"; do
        mcp_key=$(echo "$mcp" | sed 's/_SCRAPER//g' | sed 's/_MCP//g' | sed 's/_/-/g')
        if ! grep -q "\"$mcp_key\"" "$CONFIG_FILE"; then
            missing_mcps+=("$mcp_key")
        fi
    done
    
    if [ ${#missing_mcps[@]} -eq 0 ]; then
        echo -e "${GREEN}✓${NC} All MCPs configured"
    else
        echo -e "${YELLOW}⚠${NC} Missing MCPs in config: ${missing_mcps[*]}"
    fi
else
    echo -e "${RED}✗${NC} Config file not found!"
fi
echo ""

# Step 6: Common fixes
echo "6️⃣ Applying common fixes..."

# Fix for session closed errors
echo -n "Checking for session management issues... "
session_issues=0
for mcp in "${MCPS[@]}"; do
    main_file="$mcp/src/main.py"
    if [ -f "$main_file" ]; then
        if grep -q "await.*cleanup()" "$main_file" 2>/dev/null; then
            ((session_issues++))
        fi
    fi
done

if [ $session_issues -eq 0 ]; then
    echo -e "${GREEN}✓ No session issues found${NC}"
else
    echo -e "${YELLOW}⚠ Found $session_issues files with potential session issues${NC}"
fi

echo ""
echo "🎯 Summary"
echo "========="
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop completely (Quit and start again)"
echo "2. Test each MCP using the Claude interface"
echo "3. If errors persist, check logs at: ~/Library/Logs/Claude/mcp-server-*.log"
echo ""
echo "Test command examples for Claude:"
echo '  Use SEC-SCRAPER to get current price for ticker "AAPL"'
echo '  Use NEWS-SENTIMENT to analyze sentiment for ticker "MSFT"'
echo ""