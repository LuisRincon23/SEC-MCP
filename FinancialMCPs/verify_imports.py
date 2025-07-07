#!/usr/bin/env python3
"""
Verify all MCPs can import their dependencies
"""

import sys
from pathlib import Path

# Add shared to path
sys.path.append(str(Path(__file__).parent / "shared"))

def test_imports():
    errors = []
    
    print("Testing imports for all MCPs...")
    
    # Test shared modules
    print("\n1. Testing shared modules...")
    try:
        from xbrl_parser import XBRLParser
        print("  ✅ xbrl_parser")
    except Exception as e:
        errors.append(f"xbrl_parser: {e}")
        print(f"  ❌ xbrl_parser: {e}")
    
    try:
        from financial_analysis import DCFModel, FinancialMetrics
        print("  ✅ financial_analysis")
    except Exception as e:
        errors.append(f"financial_analysis: {e}")
        print(f"  ❌ financial_analysis: {e}")
    
    try:
        from research_report_generator import ResearchReportGenerator
        print("  ✅ research_report_generator")
    except Exception as e:
        errors.append(f"research_report_generator: {e}")
        print(f"  ❌ research_report_generator: {e}")
    
    try:
        from advanced_nlp import AdvancedNLPProcessor
        print("  ✅ advanced_nlp")
    except Exception as e:
        errors.append(f"advanced_nlp: {e}")
        print(f"  ❌ advanced_nlp: {e}")
    
    try:
        from data_cache import DataCache
        print("  ✅ data_cache")
    except Exception as e:
        errors.append(f"data_cache: {e}")
        print(f"  ❌ data_cache: {e}")
    
    # Test MCP server imports
    print("\n2. Testing MCP server imports...")
    try:
        from mcp.server import Server
        from mcp.server.models import InitializationOptions
        from mcp.types import Tool, TextContent
        import mcp.server.stdio as stdio
        print("  ✅ MCP server modules")
    except Exception as e:
        errors.append(f"MCP server: {e}")
        print(f"  ❌ MCP server: {e}")
    
    # Test other common imports
    print("\n3. Testing other dependencies...")
    try:
        import aiohttp
        print("  ✅ aiohttp")
    except Exception as e:
        errors.append(f"aiohttp: {e}")
        print(f"  ❌ aiohttp: {e}")
    
    try:
        from bs4 import BeautifulSoup
        print("  ✅ beautifulsoup4")
    except Exception as e:
        errors.append(f"beautifulsoup4: {e}")
        print(f"  ❌ beautifulsoup4: {e}")
    
    try:
        import numpy as np
        print("  ✅ numpy")
    except Exception as e:
        errors.append(f"numpy: {e}")
        print(f"  ❌ numpy: {e}")
    
    try:
        import pandas as pd
        print("  ✅ pandas")
    except Exception as e:
        errors.append(f"pandas: {e}")
        print(f"  ❌ pandas: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    if errors:
        print(f"❌ Found {len(errors)} import errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ All imports successful!")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)