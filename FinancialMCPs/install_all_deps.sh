#!/bin/bash

echo "📦 Installing dependencies for all Financial MCPs"
echo "=============================================="

# Use pip from venv directly
PIP=/Users/LuisRincon/SEC-MCP/.venv/bin/pip

# Install common dependencies
echo "Installing common dependencies..."
$PIP install --upgrade pip
$PIP install "mcp[cli]" aiohttp beautifulsoup4 lxml httpx anyio click starlette uvicorn numpy pandas

# Install dependencies for each MCP
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

for mcp in "${MCPS[@]}"; do
    echo ""
    echo "📌 Installing dependencies for $mcp..."
    
    if [ -f "$mcp/pyproject.toml" ]; then
        cd "$mcp"
        $PIP install -e .
        cd ..
    else
        echo "⚠️  No pyproject.toml found for $mcp"
    fi
done

echo ""
echo "✅ Installation complete!"
echo ""
echo "Testing imports..."
python -c "
import mcp.server
import aiohttp
import bs4
import numpy
import pandas
print('✅ All core imports successful!')
"