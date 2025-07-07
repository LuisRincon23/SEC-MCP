# Financial MCPs Quick Reference

## 🎉 All MCPs are now integrated into Claude Desktop!

**Restart Claude Desktop** to activate all 7 financial MCP servers.

## Quick Test Commands

Try these in Claude Desktop after restarting:

### 📊 Stock Analysis
```
"Get the latest 10-K filing for AAPL and analyze the sentiment from recent news"
```

### 🔍 Comprehensive Analysis  
```
"For MSFT, show me:
- Recent analyst ratings
- Institutional ownership changes
- Current hiring trends
- Industry DCF assumptions for technology sector"
```

### 📈 Market Overview
```
"Give me the economic dashboard with current Treasury yields and employment data"
```

### 🎯 Sector Analysis
```
"Compare sentiment across tech stocks: AAPL, GOOGL, META, AMZN"
```

## MCP Status Check

After restarting Claude Desktop:
1. Look for the 🔌 icon in the interface
2. Click it to see all connected MCPs
3. You should see 7 servers:
   - SEC-SCRAPER
   - NEWS-SENTIMENT
   - ANALYST-RATINGS
   - INSTITUTIONAL
   - ALTERNATIVE-DATA
   - INDUSTRY-ASSUMPTIONS
   - ECONOMIC-DATA

## Troubleshooting

If MCPs don't appear:
```bash
# Check logs
tail -f ~/Library/Logs/Claude/mcp*.log

# Test a specific MCP
cd /Users/LuisRincon/SEC-MCP/FinancialMCPs/SEC_SCRAPER_MCP
./start-mcp.sh
```

## 💡 Pro Tips

1. **Combine MCPs** for powerful analysis:
   ```
   "Analyze TSLA using alternative data (hiring, patents) and compare with analyst consensus"
   ```

2. **Industry comparisons**:
   ```
   "Generate DCF assumptions for retail industry and show current multiples"
   ```

3. **Economic context**:
   ```
   "How do current interest rates affect technology valuations?"
   ```

## Remember: All data is FREE! 
No API keys, no subscriptions - just web scraping from public sources.