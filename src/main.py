import anyio
import click
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
import uvicorn
from .edgar_client import EdgarClient

class EdgarMCPServer:
    def __init__(self):
        self.app = Server("edgar-mcp-server")
        self.edgar_client = None
        
    async def get_edgar_client(self) -> EdgarClient:
        """Get or create EDGAR client"""
        if self.edgar_client is None:
            self.edgar_client = EdgarClient()
            await self.edgar_client.__aenter__()
        return self.edgar_client
        
    async def search_companies(self, query: str, limit: int = 20) -> List[types.TextContent]:
        """Search for companies by name or ticker symbol"""
        try:
            client = await self.get_edgar_client()
            result = await client.search_companies(query, size=limit)
            
            if "hits" in result and "hits" in result["hits"]:
                companies = result["hits"]["hits"]
                
                if not companies:
                    return [types.TextContent(
                        type="text",
                        text=f"No companies found for query: {query}"
                    )]
                
                output = [f"Found {len(companies)} companies for '{query}':\\n\\n"]
                
                for company in companies:
                    source = company.get("_source", {})
                    entity_name = source.get("entity", "Unknown")
                    cik = source.get("cik", "Unknown")
                    ticker = source.get("tickers", [""])[0] if source.get("tickers") else "N/A"
                    
                    output.append(f"• **{entity_name}**")
                    output.append(f"  - CIK: {cik}")
                    output.append(f"  - Ticker: {ticker}")
                    output.append("")
                
                return [types.TextContent(
                    type="text",
                    text="\\n".join(output)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"No results found for query: {query}"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error searching companies: {str(e)}"
            )]
            
    async def get_company_submissions(self, cik: str, limit: int = 10) -> List[types.TextContent]:
        """Get recent filings for a company by CIK"""
        try:
            client = await self.get_edgar_client()
            result = await client.get_company_submissions(cik)
            
            company_name = result.get("name", "Unknown Company")
            filings = result.get("filings", {}).get("recent", {})
            
            if not filings.get("form"):
                return [types.TextContent(
                    type="text",
                    text=f"No recent filings found for CIK: {cik}"
                )]
            
            output = [f"Recent filings for **{company_name}** (CIK: {cik}):\\n\\n"]
            
            forms = filings.get("form", [])
            filing_dates = filings.get("filingDate", [])
            accession_numbers = filings.get("accessionNumber", [])
            descriptions = filings.get("items", [])
            
            for i in range(min(limit, len(forms))):
                form = forms[i] if i < len(forms) else "Unknown"
                date = filing_dates[i] if i < len(filing_dates) else "Unknown"
                accession = accession_numbers[i] if i < len(accession_numbers) else "Unknown"
                desc = descriptions[i] if i < len(descriptions) else ""
                
                output.append(f"**{form}** - {date}")
                output.append(f"  - Accession: {accession}")
                if desc:
                    output.append(f"  - Items: {desc}")
                output.append("")
                
            return [types.TextContent(
                type="text",
                text="\\n".join(output)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error getting company submissions: {str(e)}"
            )]
            
    async def get_company_facts(self, cik: str) -> List[types.TextContent]:
        """Get financial facts for a company"""
        try:
            client = await self.get_edgar_client()
            result = await client.get_company_facts(cik)
            
            company_name = result.get("entityName", "Unknown Company")
            facts = result.get("facts", {})
            
            if not facts:
                return [types.TextContent(
                    type="text",
                    text=f"No financial facts found for CIK: {cik}"
                )]
            
            output = [f"Financial Facts for **{company_name}** (CIK: {cik}):\\n\\n"]
            
            # Process US-GAAP facts
            us_gaap = facts.get("us-gaap", {})
            if us_gaap:
                output.append("**US-GAAP Facts:**\\n")
                
                # Show some key financial metrics
                key_metrics = [
                    "Assets", "AssetsCurrent", "Liabilities", "LiabilitiesCurrent",
                    "StockholdersEquity", "Revenues", "NetIncomeLoss", "CashAndCashEquivalents"
                ]
                
                for metric in key_metrics:
                    if metric in us_gaap:
                        metric_data = us_gaap[metric]
                        description = metric_data.get("description", metric)
                        units = list(metric_data.get("units", {}).keys())
                        
                        output.append(f"• **{description}**")
                        output.append(f"  - Available units: {', '.join(units[:3])}")
                        output.append("")
                        
                        if len(output) > 30:  # Limit output size
                            break
            
            # Add summary
            total_facts = sum(len(taxonomy.keys()) for taxonomy in facts.values())
            output.append(f"\\n**Summary:** {total_facts} total financial facts available")
            
            return [types.TextContent(
                type="text",
                text="\\n".join(output)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error getting company facts: {str(e)}"
            )]
            
    async def get_company_concept(self, cik: str, taxonomy: str, tag: str) -> List[types.TextContent]:
        """Get specific financial concept data for a company"""
        try:
            client = await self.get_edgar_client()
            result = await client.get_company_concept(cik, taxonomy, tag)
            
            company_name = result.get("entityName", "Unknown Company")
            concept_data = result.get("units", {})
            
            if not concept_data:
                return [types.TextContent(
                    type="text",
                    text=f"No data found for {taxonomy}:{tag} for CIK: {cik}"
                )]
            
            output = [f"**{tag}** data for **{company_name}** (CIK: {cik}):\\n\\n"]
            
            for unit, values in concept_data.items():
                output.append(f"**Unit: {unit}**\\n")
                
                # Show recent values (limit to 10)
                recent_values = values[-10:] if len(values) > 10 else values
                
                for value_data in recent_values:
                    val = value_data.get("val", "N/A")
                    end_date = value_data.get("end", "N/A")
                    form = value_data.get("form", "N/A")
                    
                    output.append(f"• {end_date}: {val:,} ({form})")
                
                output.append("")
                break  # Only show first unit to avoid too much data
                
            return [types.TextContent(
                type="text",
                text="\\n".join(output)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error getting company concept: {str(e)}"
            )]
            
    async def download_filing(self, cik: str, accession_number: str, save_path: Optional[str] = None) -> List[types.TextContent]:
        """Download a specific filing document"""
        try:
            client = await self.get_edgar_client()
            
            # Download the filing
            content = await client.download_filing(cik, accession_number)
            
            if save_path:
                # Save to file
                with open(save_path, 'wb') as f:
                    f.write(content)
                
                return [types.TextContent(
                    type="text",
                    text=f"Filing {accession_number} downloaded successfully to {save_path} ({len(content):,} bytes)"
                )]
            else:
                # Return preview of content
                text_content = content.decode('utf-8', errors='ignore')
                preview = text_content[:2000] + "..." if len(text_content) > 2000 else text_content
                
                return [types.TextContent(
                    type="text",
                    text=f"Filing {accession_number} content preview:\\n\\n```\\n{preview}\\n```\\n\\nTotal size: {len(content):,} bytes"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error downloading filing: {str(e)}"
            )]

    def setup_tools(self):
        """Register all EDGAR tools"""
        
        @self.app.list_tools()
        async def list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="search_companies",
                    description="Search for companies by name or ticker symbol",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Company name or ticker symbol to search for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 20)",
                                "default": 20
                            }
                        },
                        "required": ["query"],
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="get_company_submissions",
                    description="Get recent SEC filings for a company by CIK",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cik": {
                                "type": "string",
                                "description": "Company CIK (Central Index Key)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of filings to return (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["cik"],
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="get_company_facts",
                    description="Get all financial facts for a company by CIK",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cik": {
                                "type": "string",
                                "description": "Company CIK (Central Index Key)"
                            }
                        },
                        "required": ["cik"],
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="get_company_concept",
                    description="Get specific financial concept data for a company",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cik": {
                                "type": "string",
                                "description": "Company CIK (Central Index Key)"
                            },
                            "taxonomy": {
                                "type": "string",
                                "description": "Taxonomy (e.g., 'us-gaap', 'ifrs-full')",
                                "default": "us-gaap"
                            },
                            "tag": {
                                "type": "string",
                                "description": "Financial concept tag (e.g., 'Assets', 'Revenues', 'NetIncomeLoss')"
                            }
                        },
                        "required": ["cik", "taxonomy", "tag"],
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="download_filing",
                    description="Download a specific SEC filing document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cik": {
                                "type": "string",
                                "description": "Company CIK (Central Index Key)"
                            },
                            "accession_number": {
                                "type": "string",
                                "description": "Filing accession number (e.g., '0000320193-23-000006')"
                            },
                            "save_path": {
                                "type": "string",
                                "description": "Optional file path to save the document"
                            }
                        },
                        "required": ["cik", "accession_number"],
                        "additionalProperties": False
                    }
                )
            ]

        @self.app.call_tool()
        async def handle_tool(name: str, arguments: dict) -> List[types.TextContent]:
            if name == "search_companies":
                return await self.search_companies(
                    arguments["query"],
                    arguments.get("limit", 20)
                )
            elif name == "get_company_submissions":
                return await self.get_company_submissions(
                    arguments["cik"],
                    arguments.get("limit", 10)
                )
            elif name == "get_company_facts":
                return await self.get_company_facts(arguments["cik"])
            elif name == "get_company_concept":
                return await self.get_company_concept(
                    arguments["cik"],
                    arguments["taxonomy"],
                    arguments["tag"]
                )
            elif name == "download_filing":
                return await self.download_filing(
                    arguments["cik"],
                    arguments["accession_number"],
                    arguments.get("save_path")
                )
            else:
                raise ValueError(f"Unknown tool: {name}")

@click.command()
@click.option("--port", default=8080, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="sse",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    edgar_server = EdgarMCPServer()
    edgar_server.setup_tools()
    
    # Handle different transport types
    if transport == "sse":
        # Set up SSE transport
        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await edgar_server.app.run(
                    streams[0], 
                    streams[1], 
                    edgar_server.app.create_initialization_options()
                )

        # Create Starlette app
        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        # Run server
        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        # Handle stdio transport
        async def arun():
            from mcp.server.stdio import stdio_server
            async with stdio_server() as streams:
                await edgar_server.app.run(
                    streams[0], 
                    streams[1], 
                    edgar_server.app.create_initialization_options()
                )
        anyio.run(arun)

    return 0

if __name__ == "__main__":
    main()