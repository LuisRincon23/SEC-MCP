import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
import uvicorn

async def test_tool() -> list[types.TextContent]:
    """Simple test tool that returns a success message"""
    return [types.TextContent(
        type="text",
        text="Tool is working! 🎉"
    )]

@click.command()
@click.option("--port", default=8080, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="sse",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    # Create MCP server
    app = Server("test-mcp-server")

    # Register tools
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="test",
                description="A test tool that confirms it's working",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            )
        ]

    @app.call_tool()
    async def handle_tool(name: str, arguments: dict) -> list[types.TextContent]:
        if name != "test":
            raise ValueError(f"Unknown tool: {name}")
        return await test_tool()

    # Handle different transport types
    if transport == "sse":
        # Set up SSE transport
        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], 
                    streams[1], 
                    app.create_initialization_options()
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
                await app.run(
                    streams[0], 
                    streams[1], 
                    app.create_initialization_options()
                )
        anyio.run(arun)

    return 0

if __name__ == "__main__":
    main()