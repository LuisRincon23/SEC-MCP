# 🚀 Easy MCP Template

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-Enabled-brightgreen.svg)
![Platform](https://img.shields.io/badge/Platform-Claude%20Desktop%20|%20Cursor%20|%20VS%20Code-orange.svg)

**Build MCP servers for Claude Desktop in minutes, not hours!**

[⚡ Quick Start](./QUICKSTART_CLAUDE.md) | [📖 Full Guide](./CLAUDE_DESKTOP_GUIDE.md) | [🛠️ Examples](./context/)

</div>

## 🎯 What is this?

A simple Python template that lets you create custom tools for Claude Desktop. No complex setup, no TypeScript compilation, just Python and go!

## 🏃 2-Minute Setup

```bash
# Clone and enter directory
git clone https://github.com/LuisRincon23/Easy-MCP-Template.git
cd Easy-MCP-Template

# Setup environment
pip install uv
uv venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# Configure Claude Desktop (see below)
# Restart Claude Desktop
# Done! 🎉
```

## ⚙️ Claude Desktop Configuration

Add to your config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "/absolute/path/to/Easy-MCP-Template/start-mcp.sh"
    }
  }
}
```

> 💡 **Windows**: Use `start-mcp.bat` and Windows paths (e.g., `C:\\path\\to\\...`)

## 🛠️ Building Your Tools

Edit `main.py` to add your custom tools:

```python
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="my_tool",
            description="What this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Tool input"}
                },
                "required": ["input"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "my_tool":
        # Your tool logic here
        result = f"Processed: {arguments['input']}"
        return [types.TextContent(type="text", text=result)]
```

## 📦 What's Included

```
Easy-MCP-Template/
├── main.py              # Your MCP server code
├── start-mcp.sh         # macOS/Linux starter
├── start-mcp.bat        # Windows starter
├── pyproject.toml       # Dependencies
└── context/             # Example implementations
```

## 🔧 Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| "spawn ENOENT" | Use absolute paths in config |
| "No module named..." | Activate venv in starter script |
| Tools not showing | Restart Claude Desktop completely |
| Server crashes | Check logs: `~/Library/Logs/Claude/mcp-*.log` |

## 🚀 Real Examples

- **[SEC-MCP](https://github.com/LuisRincon23/SEC-MCP)** - Financial data tools
- **Weather Tool** - See [Full Guide](./CLAUDE_DESKTOP_GUIDE.md#example-building-a-weather-tool)
- **Your Tool Here** - Build anything!

## 💡 Tips

- Start simple - get one tool working first
- Use descriptive tool names and descriptions
- Return formatted text with markdown
- Check logs when debugging
- Test standalone: `python main.py --transport stdio`

## 📚 Learn More

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Claude Desktop Docs](https://claude.ai/docs)
- [Full Integration Guide](./CLAUDE_DESKTOP_GUIDE.md)

---

<div align="center">

**Ready to build?** Start with the [Quick Start Guide](./QUICKSTART_CLAUDE.md) 🚀

</div>