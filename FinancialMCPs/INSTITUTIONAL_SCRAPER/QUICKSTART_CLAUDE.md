# 🚀 Quick Start: Claude Desktop + MCP

Get your MCP server running with Claude Desktop in under 2 minutes!

## 📋 Prerequisites

- Python 3.8+ installed
- Claude Desktop app
- This template cloned/downloaded

## 🏃‍♂️ 3-Step Setup

### Step 1: Install Dependencies

```bash
cd Easy-MCP-Template
pip install uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Step 2: Configure Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "test-server": {
      "command": "/path/to/Easy-MCP-Template/start-mcp.sh"
    }
  }
}
```

> 💡 **Windows users**: Use `start-mcp.bat` and Windows-style paths

### Step 3: Restart Claude Desktop

Completely quit and restart Claude Desktop.

## ✅ Test Your Connection

In Claude Desktop, type:
```
Can you test the MCP connection?
```

Claude should be able to use the "test" tool and respond with "Tool is working! 🎉"

## 🎯 Next Steps

1. Modify `main.py` to add your custom tools
2. Read the [full integration guide](./CLAUDE_DESKTOP_GUIDE.md) for advanced features
3. Check the `context/` folder for implementation examples

## 🆘 Quick Troubleshooting

**Not working?** Check these first:

1. **Path is correct**: Use absolute paths in config
2. **Script is executable**: Run `chmod +x start-mcp.sh` (macOS/Linux)
3. **Python works**: Test with `python main.py --transport stdio`
4. **Check logs**: `~/Library/Logs/Claude/mcp-server-test-server.log`

---

🎉 **That's it!** You now have a working MCP server in Claude Desktop!