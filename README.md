# SEC MCP 📊

A Server-Sent Events (SSE) Model Context Protocol server for SEC EDGAR data access. Enables both remote and local connections to retrieve SEC filing data, company information, and financial facts.

<div align="center">

[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Integrations:** [Claude Desktop](#-claude-desktop-integration) • [Cursor](#-cursor-ide-integration) • [Cline](#-cline-vs-code-extension-integration) • [Roo Coder](#-roo-coder-integration)

</div>

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#-claude-desktop-integration)
- [IDE Integrations](#-ide--code-assistant-integrations)
- [API Examples](#api-examples)
- [Development](#development)
- [Troubleshooting](#-troubleshooting)

## Overview

SEC MCP provides a streamlined interface to access SEC EDGAR data through the Model Context Protocol. It supports real-time data streaming via SSE, making it ideal for both local development and remote deployment scenarios.

Built with Python and the MCP framework, this server enables seamless integration with AI assistants and other tools that support the Model Context Protocol.

## Features

- 🔍 **Company Search** - Search for companies by name, CIK, or ticker
- 📄 **Filing Access** - Download and retrieve SEC filings  
- 📊 **Financial Data** - Access company facts and concept data
- 🚀 **SSE Support** - Real-time data streaming for remote connections
- ⚡ **Async Operations** - High-performance async API client
- 🔒 **Rate Limiting** - Built-in rate limiting for SEC compliance

## Installation

```bash
# Clone the repository
git clone https://github.com/LuisRincon23/SEC-MCP.git
cd SEC-MCP

# Install with uv
uv sync
```

## Usage

Run the MCP server using uv:

```bash
uv run -m run --port 8000
```

The server will start on the specified port, ready to accept both local and remote SSE connections.

## 🚀 Claude Desktop Integration

### ✨ Quick Setup (3 steps)

1. **Install SEC-MCP**
   ```bash
   git clone https://github.com/LuisRincon23/SEC-MCP.git
   cd SEC-MCP
   uv sync
   ```

2. **Configure Claude Desktop**
   
   Open your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

   Add this configuration:
   ```json
   {
     "mcpServers": {
       "SEC-MCP": {
         "command": "/path/to/SEC-MCP/start-mcp.sh"  // macOS/Linux
         // "command": "C:\\path\\to\\SEC-MCP\\start-mcp.bat"  // Windows
       }
     }
   }
   ```
   
   > 💡 **Important**: Replace `/path/to/SEC-MCP` with your actual installation path

3. **Restart Claude Desktop**
   
   That's it! The SEC EDGAR tools are now available in your conversations.

### 🎯 Verify Installation

Type any of these in Claude to see the tools in action:
- "Search for Apple's SEC filings"
- "Get Tesla's financial data"
- "Show me Microsoft's recent 10-K"

### 🛠️ Alternative Setup Methods

<details>
<summary><b>Method 1: Direct Python Command</b></summary>

If you prefer not to use the shell script, you can configure Claude Desktop directly:

```json
{
  "mcpServers": {
    "SEC-MCP": {
      "command": "/full/path/to/uv",
      "args": ["run", "python", "run.py", "--transport", "stdio"],
      "cwd": "/path/to/SEC-MCP"
    }
  }
}
```

> Find your `uv` path with: `which uv`
</details>

<details>
<summary><b>Method 2: SSE Server (Remote Access)</b></summary>

For remote access or advanced setups:

1. Start the server:
   ```bash
   uv run -m run --port 8000
   ```

2. Configure Claude Desktop:
   ```json
   {
     "mcpServers": {
       "SEC-MCP": {
         "url": "http://localhost:8000/sse"
       }
     }
   }
   ```
</details>

### 🔧 Troubleshooting

If you encounter issues:

1. **Enable Developer Mode** (for detailed logs):
   ```bash
   echo '{"allowDevTools": true}' > ~/Library/Application\ Support/Claude/developer_settings.json
   ```
   Then use `Cmd+Option+Shift+I` in Claude Desktop to see logs.

2. **Check Logs**:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp-server-SEC-MCP.log
   ```

3. **Common Issues**:
   - **"spawn ENOENT"**: The path to `uv` or the script is incorrect
   - **"No module named..."**: Working directory (`cwd`) is incorrect
   - **Server disconnects**: Check that all dependencies are installed with `uv sync`

## 🔌 IDE & Code Assistant Integrations

### 💻 Cursor IDE Integration

[Cursor](https://cursor.sh) is an AI-powered IDE that supports MCP servers natively.

<details>
<summary><b>📋 Cursor Setup Instructions</b></summary>

1. **Open Cursor Settings**
   - Press `Cmd+,` (macOS) or `Ctrl+,` (Windows/Linux)
   - Navigate to `Features` → `MCP Servers`

2. **Add SEC-MCP Configuration**
   ```json
   {
     "SEC-MCP": {
       "command": "/path/to/SEC-MCP/start-mcp.sh"  // macOS/Linux
       // "command": "C:\\path\\to\\SEC-MCP\\start-mcp.bat"  // Windows
     }
   }
   ```

3. **Restart Cursor**
   - The SEC tools will be available in Cursor's AI assistant
   - Type `@SEC-MCP` to access the tools directly

**Usage Example:**
```
@SEC-MCP search for Apple's latest 10-K filing
```
</details>

### 🤖 Cline (VS Code Extension) Integration

[Cline](https://github.com/saoudrizwan/claude-dev) is a powerful VS Code extension that brings Claude to your IDE.

<details>
<summary><b>📋 Cline Setup Instructions</b></summary>

1. **Install Cline Extension**
   - Open VS Code
   - Go to Extensions (Cmd+Shift+X)
   - Search for "Cline" and install

2. **Configure MCP Server**
   - Open VS Code settings (Cmd+,)
   - Search for "Cline MCP"
   - Add to `cline.mcpServers`:
   ```json
   {
     "SEC-MCP": {
       "command": "/path/to/SEC-MCP/start-mcp.sh"  // macOS/Linux
       // "command": "C:\\path\\to\\SEC-MCP\\start-mcp.bat"  // Windows
     }
   }
   ```

3. **Access SEC Tools**
   - Open Cline chat (Cmd+Shift+P → "Cline: Open Chat")
   - SEC tools are now available in your coding sessions

**Usage Example:**
```
Hey Cline, can you fetch Tesla's revenue data using SEC-MCP?
```
</details>

### 🦘 Roo Coder Integration

[Roo Coder](https://github.com/RooVetGit/Roo-Code) is an AI coding assistant that supports MCP protocol.

<details>
<summary><b>📋 Roo Coder Setup Instructions</b></summary>

1. **Install Roo Coder**
   ```bash
   npm install -g roo-coder
   ```

2. **Configure MCP Server**
   Create or edit `~/.roo-coder/config.json`:
   ```json
   {
     "mcpServers": {
       "SEC-MCP": {
         "command": "/path/to/SEC-MCP/start-mcp.sh",  // macOS/Linux
         // "command": "C:\\path\\to\\SEC-MCP\\start-mcp.bat",  // Windows
         "env": {
           "PYTHONPATH": "/path/to/SEC-MCP"
         }
       }
     }
   }
   ```

3. **Launch Roo Coder**
   ```bash
   roo-coder --enable-mcp
   ```

**Usage Example:**
```
@mcp SEC-MCP get_company_facts cik:0000320193
```
</details>

### 📊 Integration Comparison

| Feature | Claude Desktop | Cursor IDE | Cline (VS Code) | Roo Coder |
|---------|---------------|------------|-----------------|-----------|
| **Setup Difficulty** | ⭐ Easy | ⭐ Easy | ⭐⭐ Medium | ⭐⭐ Medium |
| **Native MCP Support** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Configuration Location** | JSON file | Settings UI | VS Code Settings | Config file |
| **Best For** | General AI chat | AI-powered coding | VS Code users | Terminal users |
| **Platform** | macOS, Windows | macOS, Windows, Linux | All platforms | All platforms |

### ⚡ Quick Integration Tips

- **All IDEs**: Ensure the full path to `start-mcp.sh` is used
- **Windows Users**: Use forward slashes in paths or escape backslashes
- **Permissions**: Make sure `start-mcp.sh` is executable (`chmod +x start-mcp.sh`)
- **Python Environment**: The shell script handles `uv` environment automatically
- **Testing**: Use the verification examples in each section to test your setup

### Available Tools

1. **search_companies** - Search for companies by name, CIK, or ticker
2. **get_company_submissions** - Retrieve all SEC submissions for a company
3. **get_company_facts** - Get standardized company facts data
4. **get_company_concept** - Access specific XBRL concepts for a company
5. **download_filing** - Download filing documents by URL

### Example Client Connection

```python
import asyncio
from mcp import ClientSession, StdioServerParameters

async def main():
    # For stdio connection
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "-m", "run", "--transport", "stdio"]
    )
    
    async with ClientSession(server_params) as session:
        # Search for a company
        result = await session.call_tool(
            "search_companies",
            {"query": "Apple Inc"}
        )
        print(result)

asyncio.run(main())
```

## API Examples

### Search Companies
```python
# Search by company name
result = await session.call_tool(
    "search_companies",
    {"query": "Tesla"}
)

# Search by CIK
result = await session.call_tool(
    "search_companies", 
    {"query": "0001318605"}
)
```

### Get Company Filings
```python
# Get all submissions for a company
filings = await session.call_tool(
    "get_company_submissions",
    {"cik": "0001318605"}
)
```

### Access Financial Data
```python
# Get company facts
facts = await session.call_tool(
    "get_company_facts",
    {"cik": "0000320193"}  # Apple Inc
)

# Get specific concept data
revenue = await session.call_tool(
    "get_company_concept",
    {
        "cik": "0000320193",
        "taxonomy": "us-gaap", 
        "tag": "Revenue"
    }
)
```

## Configuration

The server accepts the following command-line arguments:

- `--port` - Port number for the SSE server (default: 8000)
- `--host` - Host address to bind to (default: localhost)
- `--transport` - Transport type: `stdio` or `sse` (default: sse)

## Requirements

- Python 3.9+
- uv package manager
- Dependencies managed via `pyproject.toml`

## Development

```bash
# Run tests
uv run pytest

# Run with debug logging
uv run -m run --port 8000 --debug
```

## License

MIT License - see LICENSE file for details

## Author

Created by Luis Angel Rincon

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Built using the Model Context Protocol (MCP) and SEC EDGAR API.