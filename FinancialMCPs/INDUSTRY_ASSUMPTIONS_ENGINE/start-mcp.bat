@echo off
REM MCP Server startup script for Claude Desktop (Windows)
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the MCP server in stdio mode
python main.py --transport stdio