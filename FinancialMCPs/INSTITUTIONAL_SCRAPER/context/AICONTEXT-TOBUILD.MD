# MCP Tool Development Guide

## Core Principles
1. Use SDK Transport
2. Keep Tools Simple
3. Let SDK Handle Complexity
4. Focus on Business Logic

## Quick Start

### 1. Server Setup
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport

app = Server("your-server-name")
sse = SseServerTransport("/messages/")

### 2. Basic Tool Pattern
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="your_tool",
            description="What your tool does",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]

@app.call_tool()
async def handle_tool(name: str, arguments: dict) -> list[types.TextContent]:
    return [types.TextContent(type="text", text="Response")]

## Tool Development Steps

### 1. Define Purpose
- What does the tool do?
- What inputs does it need?
- What output should it provide?

### 2. Create Schema
- Start minimal
- Add only required properties
- Always set additionalProperties: false
- Use clear property names

### 3. Implement Tool
- Use async functions
- Return TextContent
- Keep error handling simple
- Let SDK handle transport

### 4. Test Tool
- Verify registration
- Test basic functionality
- Check error cases
- Don't test transport layer

## Best Practices

### DO
- Use SDK transport
- Keep tools focused
- Use simple schemas
- Return TextContent
- Let SDK handle errors

### DON'T
- Implement manual SSE
- Overcomplicate schemas
- Handle transport manually
- Create complex error objects

## Common Patterns

### Basic Tool
async def your_tool() -> list[types.TextContent]:
    return [types.TextContent(
        type="text",
        text="Tool response"
    )]

### Tool with Parameters
# In list_tools():
types.Tool(
    name="tool_with_params",
    description="Tool description",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param"],
        "additionalProperties": False
    }
)

### Error Handling
try:
    result = await do_something()
    return [types.TextContent(type="text", text=result)]
except Exception as e:
    return [types.TextContent(type="text", text=f"Error: {str(e)}")]

## Testing Checklist

### Tool Registration
- [ ] Tool appears in list_tools
- [ ] Schema is correct
- [ ] Description is clear

### Tool Execution
- [ ] Works with valid input
- [ ] Handles invalid input
- [ ] Returns proper format
- [ ] Error messages are helpful

## Remember
1. SDK handles transport
2. Keep tools simple
3. Focus on logic
4. Use TextContent
5. Simple error handling

## Resources
- MCP SDK Documentation
- Example Implementations
- Tool Templates
- Testing Guides