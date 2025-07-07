#!/bin/bash
#
# Test MCPs via Claude CLI
#

echo "🧪 Testing MCPs via Claude CLI"
echo "=============================="
echo ""

# Function to test an MCP
test_mcp() {
    local mcp_name=$1
    local command=$2
    local expected=$3
    
    echo -n "Testing $mcp_name... "
    
    # Create test command
    echo "$command" > /tmp/claude_test.txt
    
    # Run through Claude
    if timeout 30 claude --no-chat < /tmp/claude_test.txt > /tmp/claude_output.txt 2>&1; then
        if grep -q "$expected" /tmp/claude_output.txt; then
            echo "✅ Success"
        else
            echo "⚠️  No expected output"
            echo "  Got: $(head -50 /tmp/claude_output.txt | tr '\n' ' ')"
        fi
    else
        echo "❌ Failed"
        echo "  Error: $(head -50 /tmp/claude_output.txt)"
    fi
}

# Test each MCP with simple commands
echo "Testing Financial MCPs..."
echo ""

test_mcp "SEC" \
    'Use SEC to get current price for ticker "AAPL"' \
    "price"

test_mcp "NEWS-SENTIMENT" \
    'Use NEWS-SENTIMENT to analyze sentiment for ticker "TSLA"' \
    "sentiment"

test_mcp "X-SENTIMENT" \
    'Use X-SENTIMENT to analyze ticker sentiment for ticker "BTC"' \
    "sentiment"

test_mcp "ANALYST-RATINGS" \
    'Use ANALYST-RATINGS to get consensus rating for ticker "NVDA"' \
    "rating"

test_mcp "INSTITUTIONAL" \
    'Use INSTITUTIONAL to get top holders for ticker "AAPL"' \
    "holder"

test_mcp "ALTERNATIVE-DATA" \
    'Use ALTERNATIVE-DATA to get reddit sentiment for query "GME stock"' \
    "sentiment"

test_mcp "INDUSTRY-ASSUMPTIONS-ENGINE" \
    'Use INDUSTRY-ASSUMPTIONS-ENGINE to calculate WACC for ticker "MSFT"' \
    "wacc"

test_mcp "ECONOMIC-DATA-COLLECTOR" \
    'Use ECONOMIC-DATA-COLLECTOR to get economic indicators' \
    "indicator"

test_mcp "RESEARCH-ADMINISTRATOR" \
    'Use RESEARCH-ADMINISTRATOR to create research summary for ticker "GOOGL"' \
    "research"

echo ""
echo "=============================="
echo "✅ Tests complete!"