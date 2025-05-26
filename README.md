# SEC MCP 📊

A Server-Sent Events (SSE) Model Context Protocol server for SEC EDGAR data access. Enables both remote and local connections to retrieve SEC filing data, company information, and financial facts.

## Overview

SEC MCP provides a streamlined interface to access SEC EDGAR data through the Model Context Protocol. It supports real-time data streaming via SSE, making it ideal for both local development and remote deployment scenarios.

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
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "-m", "main", "--port", "8000"]
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