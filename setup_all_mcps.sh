#!/bin/bash

echo "🚀 Setting up Financial MCPs for Claude Code CLI"
echo "=============================================="
echo ""

# Check if claude CLI is installed
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code CLI not found!"
    echo "Please install it first: npm install -g @anthropic-ai/claude-cli"
    exit 1
fi

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Define all MCPs
MCPS=(
    "SEC:SEC_SCRAPER_MCP"
    "NEWS-SENTIMENT:NEWS_SENTIMENT_SCRAPER"
    "ANALYST-RATINGS:ANALYST_RATINGS_SCRAPER"
    "INSTITUTIONAL:INSTITUTIONAL_SCRAPER"
    "ALTERNATIVE-DATA:ALTERNATIVE_DATA_SCRAPER"
    "INDUSTRY-ASSUMPTIONS:INDUSTRY_ASSUMPTIONS_ENGINE"
    "ECONOMIC-DATA:ECONOMIC_DATA_COLLECTOR"
    "RESEARCH-ADMIN:RESEARCH_ADMINISTRATOR"
)

echo "📦 Adding Financial MCPs to Claude Code..."
echo ""

SUCCESS=0
FAILED=0

for mcp_pair in "${MCPS[@]}"; do
    IFS=':' read -r name folder <<< "$mcp_pair"
    
    echo -n "Adding $name... "
    
    if claude mcp add "$name" "$DIR/FinancialMCPs/$folder/start-mcp.sh" --transport stdio 2>/dev/null; then
        echo "✅"
        ((SUCCESS++))
    else
        echo "❌"
        ((FAILED++))
    fi
done

echo ""
echo "======================================"
echo "✅ Successfully added: $SUCCESS MCPs"

if [ $FAILED -gt 0 ]; then
    echo "❌ Failed to add: $FAILED MCPs"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Restart your Claude Code session"
echo "2. Type /mcp to see all available MCPs"
echo "3. Test with: Use SEC to get current price for ticker \"AAPL\""
echo ""
echo "📚 For usage examples, see README.md"