# SEC MCP 📊

A Server-Sent Events (SSE) Model Context Protocol server for SEC EDGAR data access. Enables both remote and local connections to retrieve SEC filing data, company information, and financial facts.

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
         "command": "/path/to/SEC-MCP/start-mcp.sh"
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