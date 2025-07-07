# Claude Code MCP Setup Guide

## Quick Setup

The SEC scraper MCP has been configured for Claude Code. The `.mcp.json` file is already created in the project root.

## Using the SEC Scraper in Claude Code

1. **The MCP is already configured** in `.mcp.json`:
```json
{
  "mcpServers": {
    "sec-scraper": {
      "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/SEC_SCRAPER_MCP/start-mcp.sh",
      "args": [],
      "env": {}
    }
  }
}
```

2. **Available tools** once connected:
   - `scrape_10k_financials` - Get latest 10-K financial data
   - `scrape_10q_financials` - Get latest 10-Q quarterly data
   - `scrape_8k_events` - Get recent 8-K material events
   - `get_stock_price` - Get current stock price and changes
   - `search_companies` - Search for company CIK by name

## Alternative Manual Setup

If you need to add it manually to Claude Code:

```bash
# Add SEC scraper as a project-scoped server
claude mcp add -s project sec-scraper -- /Users/LuisRincon/SEC-MCP/FinancialMCPs/SEC_SCRAPER_MCP/start-mcp.sh
```

## Troubleshooting

1. **Check if MCP is loaded**:
```bash
claude mcp list
```

2. **View server details**:
```bash
claude mcp get sec-scraper
```

3. **If server isn't showing**, ensure you're in the project directory:
```bash
cd /Users/LuisRincon/SEC-MCP
```

## Usage Example

Once the MCP is loaded, you can use it in your Claude Code session:

```
"Use the SEC scraper to get Apple's latest 10-K financials"
"Search for Microsoft's CIK number"
"Get Tesla's current stock price"
```

The MCP will automatically be available when you start Claude Code in this project directory.