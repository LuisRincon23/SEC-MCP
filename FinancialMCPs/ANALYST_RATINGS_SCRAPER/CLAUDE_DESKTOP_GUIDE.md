# 🖥️ Claude Desktop MCP Integration Guide

A comprehensive guide for integrating MCP servers with Claude Desktop, based on real-world implementation experience.

<div align="center">

![Claude Desktop](https://img.shields.io/badge/Claude_Desktop-Compatible-blue.svg)
![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-green.svg)
![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Windows-orange.svg)

</div>

## 📋 Table of Contents

- [Understanding MCP](#understanding-mcp)
- [How MCP Works with Claude Desktop](#how-mcp-works-with-claude-desktop)
- [Integration Methods](#integration-methods)
- [Step-by-Step Setup](#step-by-step-setup)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## 🧠 Understanding MCP

The Model Context Protocol (MCP) is a communication protocol that allows AI assistants like Claude to interact with external tools and services. Think of it as a bridge between Claude and your custom functionality.

### Key Concepts:

1. **Tools**: Functions that Claude can call to perform specific actions
2. **Transport**: How the communication happens (stdio or SSE)
3. **Server**: Your MCP implementation that provides the tools
4. **Client**: Claude Desktop acting as the MCP client

## 🔄 How MCP Works with Claude Desktop

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Claude Desktop │ <-----> │   MCP Protocol  │ <-----> │  Your MCP Server│
│   (MCP Client)  │  JSON   │  (stdio/SSE)    │  JSON   │    (Python)     │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

### Communication Flow:

1. **Initialization**: Claude Desktop starts your MCP server
2. **Tool Discovery**: Server tells Claude what tools are available
3. **Tool Invocation**: Claude calls tools when needed
4. **Response**: Server executes tools and returns results

## 🚀 Integration Methods

### Method 1: Shell Script Wrapper (Recommended) ✅

**Why it's best**: Handles environment setup automatically and avoids path issues.

1. Create `start-mcp.sh` (macOS/Linux) or `start-mcp.bat` (Windows):

```bash
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate  # or use 'uv run' if using uv
python main.py --transport stdio
```

2. Make it executable:
```bash
chmod +x start-mcp.sh
```

3. Configure Claude Desktop:
```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "/path/to/your-project/start-mcp.sh"
    }
  }
}
```

### Method 2: Direct Python Command

```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "python",
      "args": ["main.py", "--transport", "stdio"],
      "cwd": "/path/to/your-project"
    }
  }
}
```

### Method 3: Using uv

```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "/path/to/uv",
      "args": ["run", "python", "main.py", "--transport", "stdio"],
      "cwd": "/path/to/your-project"
    }
  }
}
```

## 📝 Step-by-Step Setup

### 1. Prepare Your MCP Server

Ensure your `main.py` supports stdio transport:

```python
import click
from mcp.server.stdio import stdio_server
import anyio

@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio")
def main(transport: str):
    if transport == "stdio":
        async def run():
            async with stdio_server() as streams:
                # Your server logic here
                await server.run(streams[0], streams[1])
        anyio.run(run)
```

### 2. Create Configuration File

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Example configuration:
```json
{
  "mcpServers": {
    "example-server": {
      "command": "/Users/yourname/projects/mcp-server/start-mcp.sh"
    },
    "another-server": {
      "command": "C:\\projects\\another-server\\start-mcp.bat"
    }
  }
}
```

### 3. Test Your Server

Before connecting to Claude Desktop, test standalone:

```bash
# Test stdio mode
echo '{"method": "initialize", "params": {"capabilities": {}}}' | python main.py --transport stdio
```

### 4. Restart Claude Desktop

After adding configuration, fully restart Claude Desktop:
- macOS: Cmd+Q, then reopen
- Windows: Close from system tray, then reopen

### 5. Verify Connection

In Claude Desktop, your tools should appear when you:
- Type "/" to see available commands
- Ask Claude to use your custom tools

## 🔧 Troubleshooting

### Common Issues and Solutions:

#### 1. "spawn ENOENT" Error
**Problem**: Claude Desktop can't find the command
**Solution**: 
- Use absolute paths in configuration
- Ensure scripts are executable (`chmod +x`)
- Check that Python/uv is in PATH

#### 2. "No module named..." Error
**Problem**: Python environment issues
**Solution**:
- Ensure virtual environment is activated in your script
- Use `cwd` to set working directory
- Install all dependencies

#### 3. Server Disconnects Immediately
**Problem**: Server crashes on startup
**Solution**:
- Check logs: `~/Library/Logs/Claude/mcp-server-*.log`
- Test server standalone first
- Add error handling and logging

#### 4. Tools Not Appearing
**Problem**: Server not registering tools properly
**Solution**:
- Verify `list_tools()` implementation
- Check tool schema format
- Enable developer mode for debugging

### Enable Developer Mode

Create `~/Library/Application Support/Claude/developer_settings.json`:
```json
{"allowDevTools": true}
```

Then use Cmd+Option+Shift+I to open DevTools.

### Check Logs

```bash
# View server logs
tail -f ~/Library/Logs/Claude/mcp-server-yourservername.log

# View general MCP logs
tail -f ~/Library/Logs/Claude/mcp.log
```

## 💡 Best Practices

### 1. Environment Management
- Always use virtual environments
- Include environment activation in startup scripts
- Document Python version requirements

### 2. Error Handling
```python
@server.call_tool()
async def handle_tool(name: str, arguments: dict) -> List[types.TextContent]:
    try:
        # Tool implementation
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        # Log to stderr for debugging
        print(f"Error in {name}: {str(e)}", file=sys.stderr)
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
```

### 3. Logging
```python
import sys

def log_debug(message: str):
    """Log to stderr for Claude Desktop debugging"""
    print(f"[DEBUG] {message}", file=sys.stderr)
```

### 4. Tool Design
- Keep tool names descriptive and unique
- Provide clear parameter descriptions
- Return structured, readable responses
- Handle edge cases gracefully

### 5. Testing Strategy
1. Test server standalone first
2. Test with simple tools before complex ones
3. Use Claude Desktop developer tools
4. Monitor logs during development

## 🎯 Example: Complete Setup

Here's a minimal working example:

```python
# main.py
import click
import anyio
from typing import List
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

class MyMCPServer:
    def __init__(self):
        self.server = Server("my-mcp-server")
        self.setup_tools()
    
    def setup_tools(self):
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="hello_world",
                    description="Says hello",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name to greet"}
                        },
                        "required": ["name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_tool(name: str, arguments: dict) -> List[types.TextContent]:
            if name == "hello_world":
                return [types.TextContent(
                    type="text",
                    text=f"Hello, {arguments['name']}!"
                )]

@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio")
def main(transport: str):
    server = MyMCPServer()
    
    if transport == "stdio":
        async def run():
            async with stdio_server() as streams:
                await server.server.run(
                    streams[0], 
                    streams[1],
                    server.server.create_initialization_options()
                )
        anyio.run(run)

if __name__ == "__main__":
    main()
```

```bash
# start-mcp.sh
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python main.py --transport stdio
```

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "my-server": {
      "command": "/path/to/project/start-mcp.sh"
    }
  }
}
```

## 📚 Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [Claude Desktop Docs](https://claude.ai/docs)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)

---

**Remember**: The key to successful MCP integration is understanding the communication flow and properly handling the stdio transport. Start simple, test thoroughly, and build up complexity gradually! 🚀