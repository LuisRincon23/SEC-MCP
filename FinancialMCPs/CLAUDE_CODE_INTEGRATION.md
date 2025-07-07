# 🔧 Claude Code MCP Integration & Debugging Guide

## Overview

This guide helps you integrate and debug the Financial MCPs with Claude Code for better development and troubleshooting.

## ✅ Fixed Issues

1. **'operation' undefined error** - Fixed by replacing with proper error messages
2. **Missing yahoo_headers** - Fixed by moving headers to `__init__` method  
3. **XBRL parser integration** - Connected the parser to actually fetch and parse data
4. **Headers placement** - Fixed headers being defined in wrong methods across all MCPs

## 🚀 Quick Setup for Claude Code

### 1. Add MCPs to Claude Code Configuration

Create or update your Claude Code config file:

**Location:** `~/.config/claude-code/config.json` (or appropriate for your OS)

```json
{
  "mcpServers": {
    "SEC": {
      "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/SEC_SCRAPER_MCP/start-mcp.sh",
      "env": {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG"
      }
    },
    "NEWS-SENTIMENT": {
      "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/NEWS_SENTIMENT_SCRAPER/start-mcp.sh"
    },
    "ANALYST-RATINGS": {
      "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/ANALYST_RATINGS_SCRAPER/start-mcp.sh"
    },
    "INSTITUTIONAL": {
      "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/INSTITUTIONAL_SCRAPER/start-mcp.sh"
    },
    "ALTERNATIVE-DATA": {
      "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/ALTERNATIVE_DATA_SCRAPER/start-mcp.sh"
    },
    "INDUSTRY-ASSUMPTIONS": {
      "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/INDUSTRY_ASSUMPTIONS_ENGINE/start-mcp.sh"
    },
    "ECONOMIC-DATA": {
      "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/ECONOMIC_DATA_COLLECTOR/start-mcp.sh"
    },
    "RESEARCH-ADMIN": {
      "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/RESEARCH_ADMINISTRATOR/start-mcp.sh"
    }
  }
}
```

### 2. Enable Debug Mode

For debugging, add environment variables:

```json
"env": {
  "DEBUG": "true",
  "LOG_LEVEL": "DEBUG",
  "PYTHONUNBUFFERED": "1"
}
```

### 3. Test in Claude Code

After restarting Claude Code, test with:

```
/mcp SEC scrape_10k_financials {"ticker": "AAPL"}
/mcp SEC get_current_price {"ticker": "MSFT"}
/mcp NEWS-SENTIMENT analyze_sentiment {"ticker": "GOOGL"}
```

## 🐛 Debugging Tips

### 1. Check MCP Status

In Claude Code, use:
```
/mcp list
```

This shows all available MCPs and their status.

### 2. View Logs

Check logs for errors:
```bash
# Claude Code logs
tail -f ~/.local/share/claude-code/logs/*.log

# MCP-specific logs (if configured)
tail -f /tmp/mcp-*.log
```

### 3. Test Individual Functions

Use the test script:
```bash
cd /Users/LuisRincon/SEC-MCP/FinancialMCPs
python test_mcp_debug.py
```

### 4. Debug Mode

Create a debug wrapper script:

```bash
#!/bin/bash
# debug-mcp.sh
export DEBUG=true
export PYTHONUNBUFFERED=1
cd "$(dirname "$0")"
exec /Users/LuisRincon/SEC-MCP/.venv/bin/python -u src/main.py --transport stdio 2>&1 | tee /tmp/mcp-debug.log
```

## 📊 Working Examples

### Get Stock Price
```json
{
  "tool": "SEC",
  "function": "get_current_price",
  "arguments": {
    "ticker": "AAPL"
  }
}
```

### Scrape 10-K Filing
```json
{
  "tool": "SEC", 
  "function": "scrape_10k_financials",
  "arguments": {
    "ticker": "MSFT"
  }
}
```

### Parse XBRL Data
```json
{
  "tool": "SEC",
  "function": "parse_xbrl_data", 
  "arguments": {
    "ticker": "GOOGL",
    "filing_type": "10-K"
  }
}
```

## 🔍 Common Issues & Solutions

### Issue: "Session is closed"
**Solution:** The session management has been fixed. Headers are now properly initialized in `__init__`.

### Issue: "No module named 'shared'"
**Solution:** Ensure the shared directory exists and has `__init__.py`:
```bash
touch /Users/LuisRincon/SEC-MCP/FinancialMCPs/shared/__init__.py
```

### Issue: "XBRL parser returns empty data"
**Solution:** The XBRL parser now properly fetches data from SEC. If still empty, the filing might not have XBRL data.

### Issue: "Rate limit exceeded"
**Solution:** The MCPs now have 1-second delays between requests. For heavy usage, increase `self.min_delay`.

## 🎯 Advanced Usage

### 1. Comprehensive Analysis
```python
# In Claude Code
/mcp SEC scrape_10k_financials {"ticker": "AAPL"}
/mcp SEC parse_xbrl_data {"ticker": "AAPL"} 
/mcp NEWS-SENTIMENT analyze_sentiment {"ticker": "AAPL"}
/mcp ANALYST-RATINGS get_consensus_rating {"ticker": "AAPL"}
```

### 2. Batch Processing
Create a script to process multiple tickers:
```python
tickers = ["AAPL", "MSFT", "GOOGL"]
for ticker in tickers:
    # Process each ticker
```

### 3. Custom Analysis Pipeline
Combine multiple MCPs for comprehensive analysis:
1. Get financial data (SEC)
2. Analyze sentiment (NEWS-SENTIMENT)
3. Check analyst ratings (ANALYST-RATINGS)
4. Generate report (RESEARCH-ADMIN)

## 📝 Development Tips

1. **Use Type Hints**: All functions now have proper type annotations
2. **Error Handling**: Comprehensive try/except blocks with specific error messages
3. **Rate Limiting**: Built-in delays to avoid being blocked
4. **Caching**: Use the data_cache module for frequently accessed data
5. **Testing**: Run test_mcp_debug.py after any changes

## 🚨 Important Notes

1. **SEC Compliance**: The SEC scraper uses a proper User-Agent identifying it as a research tool
2. **Rate Limits**: Respect website rate limits to avoid IP bans
3. **Data Quality**: Always validate scraped data before using in analysis
4. **Error Recovery**: MCPs now have retry logic with exponential backoff

## 📚 Resources

- Test Script: `/Users/LuisRincon/SEC-MCP/FinancialMCPs/test_mcp_debug.py`
- Debug Config: `/Users/LuisRincon/SEC-MCP/FinancialMCPs/claude_debug_config.json`
- Shared Modules: `/Users/LuisRincon/SEC-MCP/FinancialMCPs/shared/`
- Documentation: `/Users/LuisRincon/SEC-MCP/FinancialMCPs/PHD_FEATURES_GUIDE.md`

---

With these fixes and integration steps, your Financial MCPs should work smoothly in Claude Code with proper debugging capabilities!