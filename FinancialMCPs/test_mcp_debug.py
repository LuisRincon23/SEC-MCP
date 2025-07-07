#!/usr/bin/env python3
"""
Test script for debugging Financial MCPs
Run this to test individual functions
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the source to path
sys.path.append(str(Path(__file__).parent / "SEC_SCRAPER_MCP" / "src"))
sys.path.append(str(Path(__file__).parent / "shared"))

from main import SECScraper


async def test_sec_scraper():
    """Test SEC scraper functions"""
    print("🧪 Testing SEC Scraper Functions")
    print("=" * 50)
    
    scraper = SECScraper()
    await scraper.setup()
    
    ticker = "AAPL"
    
    # Test 1: Search filings
    print(f"\n1. Testing search_company_filings for {ticker}...")
    try:
        filings = await scraper.search_company_filings(ticker, "10-K")
        if filings and not any('error' in f for f in filings):
            print(f"✅ Found {len(filings)} filings")
            print(f"   Latest: {filings[0]['filing_date'] if filings else 'None'}")
        else:
            print(f"❌ Error: {filings}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Get current price
    print(f"\n2. Testing get_current_price for {ticker}...")
    try:
        price_data = await scraper.get_current_price(ticker)
        if 'error' not in price_data:
            print(f"✅ Current price: ${price_data.get('price', 'N/A')}")
        else:
            print(f"❌ Error: {price_data['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Parse XBRL
    print(f"\n3. Testing parse_xbrl_data for {ticker}...")
    try:
        xbrl_data = await scraper.parse_xbrl_data(ticker)
        if 'error' not in xbrl_data:
            print(f"✅ XBRL data parsed")
            if 'key_metrics' in xbrl_data:
                print(f"   Metrics found: {len(xbrl_data['key_metrics'])}")
        else:
            print(f"❌ Error: {xbrl_data['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    await scraper.cleanup()


async def test_with_debug():
    """Test with debug output"""
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    await test_sec_scraper()


if __name__ == "__main__":
    # Run normal test by default
    asyncio.run(test_sec_scraper())
