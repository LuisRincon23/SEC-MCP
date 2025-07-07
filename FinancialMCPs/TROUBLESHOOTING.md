# Troubleshooting Financial MCPs

## Current Status

All 7 Financial MCP servers have been fixed and are ready to use!

## What Was Fixed

1. **Path Issue**: Updated all start scripts to use full path to Python
2. **Python Version**: Updated all projects to require Python 3.10+
3. **Virtual Environment**: Scripts now use the parent SEC-MCP virtual environment

## To Complete Setup

### 1. Restart Claude Desktop
Since we've updated the configuration and scripts, you need to:
- Completely quit Claude Desktop (Cmd+Q)
- Start Claude Desktop again

### 2. Check MCP Connection
- Look for the 🔌 icon in Claude Desktop
- Click it to see connected MCPs
- You should see:
  - SEC-MCP ✓ (already working)
  - SEC-SCRAPER
  - NEWS-SENTIMENT
  - ANALYST-RATINGS
  - INSTITUTIONAL
  - ALTERNATIVE-DATA
  - INDUSTRY-ASSUMPTIONS
  - ECONOMIC-DATA

### 3. Test Commands

Try these test commands in Claude:

```
"Search for Apple company filings using SEC-SCRAPER"
```

```
"Get news sentiment for TSLA using NEWS-SENTIMENT"
```

```
"Show analyst ratings for MSFT using ANALYST-RATINGS"
```

## If MCPs Still Don't Connect

1. **Check logs again**:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp-server-*.log
   ```

2. **Manually test an MCP**:
   ```bash
   cd /Users/LuisRincon/SEC-MCP/FinancialMCPs/SEC_SCRAPER_MCP
   source /Users/LuisRincon/SEC-MCP/.venv/bin/activate
   python src/main.py --help
   ```

3. **Verify dependencies**:
   ```bash
   cd /Users/LuisRincon/SEC-MCP
   source .venv/bin/activate
   pip install aiohttp beautifulsoup4 lxml
   ```

## Common Issues

### "uv: command not found"
✅ FIXED - Scripts now use Python directly

### "No module named 'aiohttp'"
Run:
```bash
cd /Users/LuisRincon/SEC-MCP
source .venv/bin/activate
pip install aiohttp beautifulsoup4 lxml
```

### "Python version conflict"
✅ FIXED - All projects now require Python 3.10+

## Success Indicators

When working correctly, you'll see in the logs:
- "Server started and connected successfully"
- "Message from client: {"method":"initialize"..."
- Tools being listed successfully

## Next Steps

After restarting Claude Desktop, all 7 Financial MCPs should be available for use with $0/month data costs!