# Financial MCPs Integration Guide for Claude Desktop

This guide will help you integrate all 7 financial MCP servers into Claude Desktop.

## Quick Setup (All MCPs at Once)

1. **Backup your current configuration** (if you have one):
   ```bash
   cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.backup.json
   ```

2. **Copy the complete configuration**:
   ```bash
   cp /Users/LuisRincon/SEC-MCP/FinancialMCPs/claude_desktop_config_all.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

3. **Restart Claude Desktop**:
   - Quit Claude Desktop completely (Cmd+Q)
   - Start Claude Desktop again

4. **Verify all MCPs are connected**:
   - Look for the 🔌 icon in Claude Desktop
   - You should see all 7 MCP servers listed

## Individual MCP Setup

If you prefer to add MCPs one by one or already have other MCPs configured:

1. **Open your existing config**:
   ```bash
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Add each MCP to the "mcpServers" section**:

### SEC Data Scraper
```json
"SEC-SCRAPER": {
  "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/SEC_SCRAPER_MCP/start-mcp.sh"
}
```

### News & Sentiment Analysis
```json
"NEWS-SENTIMENT": {
  "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/NEWS_SENTIMENT_SCRAPER/start-mcp.sh"
}
```

### Analyst Ratings
```json
"ANALYST-RATINGS": {
  "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/ANALYST_RATINGS_SCRAPER/start-mcp.sh"
}
```

### Institutional Holdings
```json
"INSTITUTIONAL": {
  "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/INSTITUTIONAL_SCRAPER/start-mcp.sh"
}
```

### Alternative Data
```json
"ALTERNATIVE-DATA": {
  "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/ALTERNATIVE_DATA_SCRAPER/start-mcp.sh"
}
```

### Industry Assumptions Engine
```json
"INDUSTRY-ASSUMPTIONS": {
  "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/INDUSTRY_ASSUMPTIONS_ENGINE/start-mcp.sh"
}
```

### Economic Data
```json
"ECONOMIC-DATA": {
  "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/ECONOMIC_DATA_COLLECTOR/start-mcp.sh"
}
```

## Available Tools by MCP

### 🏛️ SEC-SCRAPER
- `scrape_10k_financials` - Annual reports
- `scrape_10q_earnings` - Quarterly reports  
- `scrape_8k_events` - Material events
- `parse_xbrl_data` - Structured financial data
- `get_current_price` - Stock prices

### 📰 NEWS-SENTIMENT
- `scrape_stock_news` - News from multiple sources
- `analyze_news_sentiment` - Sentiment analysis
- `get_aggregate_sentiment` - Combined sentiment score
- `search_financial_news` - Custom news searches
- `get_sector_sentiment` - Sector-wide sentiment

### 📊 ANALYST-RATINGS
- `get_analyst_ratings` - Recent ratings
- `get_price_targets` - Price targets
- `get_consensus_rating` - Consensus view
- `get_rating_changes` - Upgrades/downgrades
- `compare_analyst_coverage` - Compare multiple stocks

### 🏦 INSTITUTIONAL
- `get_institutional_ownership` - Ownership percentages
- `get_insider_trading` - Insider transactions
- `get_13f_filings` - Institutional filings
- `track_institutional_changes` - Ownership changes
- `get_top_institutional_holders` - Major holders

### 🔍 ALTERNATIVE-DATA
- `analyze_hiring_trends` - Job posting analysis
- `get_web_traffic_data` - Website traffic
- `track_patent_activity` - Innovation metrics
- `analyze_employee_sentiment` - Glassdoor data
- `get_social_sentiment` - Reddit sentiment
- `get_app_metrics` - Mobile app data
- `comprehensive_alternative_data` - All data combined

### 📈 INDUSTRY-ASSUMPTIONS
- `calculate_wacc` - Cost of capital
- `get_growth_assumptions` - Growth rates
- `get_margin_assumptions` - Profitability metrics
- `get_capital_assumptions` - Capex & working capital
- `generate_full_dcf_assumptions` - Complete DCF inputs
- `get_valuation_multiples` - Industry multiples
- `get_industry_metrics` - Comprehensive metrics

### 🌍 ECONOMIC-DATA
- `get_treasury_yields` - Yield curve
- `get_employment_data` - Jobs data
- `get_inflation_data` - CPI data
- `get_gdp_data` - GDP growth
- `get_fed_policy` - Federal Reserve data
- `get_fred_series` - Any FRED series
- `get_housing_market_data` - Housing metrics
- `get_economic_dashboard` - Full economic overview

## Example Usage in Claude

Once integrated, you can ask Claude questions like:

- "Get me the latest 10-K filing data for AAPL"
- "What's the current sentiment for TSLA across news sources?"
- "Show me analyst price targets for MSFT"
- "What are the institutional ownership changes in NVDA?"
- "Analyze hiring trends at META"
- "Generate DCF assumptions for a technology company"
- "What's the current economic outlook based on government data?"

## Troubleshooting

If any MCP fails to connect:

1. **Check the logs**:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

2. **Test individual MCPs**:
   ```bash
   cd /Users/LuisRincon/SEC-MCP/FinancialMCPs/[MCP_NAME]
   ./start-mcp.sh
   ```

3. **Verify dependencies**:
   ```bash
   cd /Users/LuisRincon/SEC-MCP/FinancialMCPs/[MCP_NAME]
   uv pip install -e .
   ```

## Important Notes

- All MCPs use **100% free data sources** (web scraping)
- No API keys required
- Data is scraped in real-time
- Respect rate limits and robots.txt
- Some sources may block excessive requests

## Support

For issues or questions about these MCPs:
- Check individual MCP README files
- Review the error logs
- Ensure you have internet connectivity
- Verify the scraped websites haven't changed their structure