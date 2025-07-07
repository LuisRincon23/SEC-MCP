import time
#!/usr/bin/env python

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
import mcp.server.stdio as stdio

import asyncio
from functools import wraps

# Import advanced modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))



def async_retry(max_attempts=3, delay=1):
    """Retry decorator for async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (attempt + 1))
                    continue
            raise last_exception
        return wrapper
    return decorator



class InstitutionalScraper:
    """Scraper for institutional holdings and insider trading data from free sources"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = {}

        # Initialize advanced components
        self.analysis_enhanced = True
        self.min_delay = 1.0  # Rate limiting
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.sec_headers = {
            'User-Agent': 'FinancialMCP/1.0 (Personal Research Tool; Contact: research@example.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

    async def rate_limit(self, url: str):
        """Implement rate limiting per domain"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.min_delay:
                await asyncio.sleep(self.min_delay - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    async def setup(self):
        """Setup aiohttp session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def scrape_finviz_institutional(self, ticker: str) -> Dict[str, Any]:
        """Scrape institutional ownership from Finviz"""
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        
        try:
            async with self.session.get(url, headers=self.headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                institutional_data = {
                    'ticker': ticker,
                    'source': 'finviz',
                    'ownership': {},
                    'recent_transactions': []
                }
                
                # Get ownership percentages from snapshot table
                snapshot_table = soup.find('table', {'class': 'snapshot-table'})
                if snapshot_table:
                    for row in snapshot_table.find_all('tr'):
                        cells = row.find_all('td')
                        for i in range(0, len(cells), 2):
                            if i + 1 < len(cells):
                                label = cells[i].text.strip()
                                value = cells[i + 1].text.strip()
                                
                                if 'Inst Own' in label:
                                    institutional_data['ownership']['institutional'] = value
                                elif 'Insider Own' in label:
                                    institutional_data['ownership']['insider'] = value
                                elif 'Float' in label:
                                    institutional_data['ownership']['float'] = value
                                elif 'Shares Outstanding' in label:
                                    institutional_data['ownership']['shares_outstanding'] = value
                
                # Get recent institutional transactions
                inst_table = soup.find('table', {'class': 'ratings-outer'})
                if inst_table:
                    for row in inst_table.find_all('tr')[1:]:  # Skip header
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            institutional_data['recent_transactions'].append({
                                'date': cells[0].text.strip(),
                                'institution': cells[1].text.strip(),
                                'action': cells[2].text.strip(),
                                'shares': cells[3].text.strip()
                            })
                
                return institutional_data
        
        except Exception as e:
            return {'error': f"Failed to scrape Finviz institutional data: {str(e)}"}
    
    async def scrape_nasdaq_institutional(self, ticker: str) -> Dict[str, Any]:
        """Scrape institutional holdings from NASDAQ"""
        url = f"https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}/institutional-holdings"
        
        try:
            async with self.session.get(url, headers=self.headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                holdings_data = {
                    'ticker': ticker,
                    'source': 'nasdaq',
                    'top_holders': [],
                    'summary': {}
                }
                
                # Look for institutional holdings table
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 1:
                        headers = [th.text.strip() for th in rows[0].find_all('th')]
                        
                        if 'HOLDER' in [h.upper() for h in headers]:
                            # This is the holdings table
                            for row in rows[1:11]:  # Top 10 holders
                                cells = row.find_all('td')
                                if len(cells) >= 3:
                                    holdings_data['top_holders'].append({
                                        'institution': cells[0].text.strip(),
                                        'shares': cells[1].text.strip(),
                                        'percentage': cells[2].text.strip()
                                    })
                
                return holdings_data
        
        except Exception as e:
            return {'error': f"Failed to scrape NASDAQ institutional data: {str(e)}"}
    
    async def scrape_sec_form13f(self, cik: str, ticker: str = None) -> Dict[str, Any]:
        """Scrape Form 13F filings from SEC EDGAR"""
        # Search for 13F filings
        search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F"
        
        try:
            async with self.session.get(search_url, headers=self.sec_headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                filings_data = {
                    'cik': cik,
                    'source': 'sec_13f',
                    'recent_filings': [],
                    'holdings': []
                }
                
                # Find filing links
                filing_table = soup.find('table', {'class': re.compile('tableFile')}) or soup.find('table', {'summary': re.compile('Document')})
                if filing_table:
                    rows = filing_table.find_all('tr')[1:6]  # Get recent 5 filings
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            filing_link = cells[1].find('a')
                            if filing_link:
                                filings_data['recent_filings'].append({
                                    'filing_date': cells[3].text.strip(),
                                    'form_type': cells[0].text.strip(),
                                    'description': cells[2].text.strip(),
                                    'link': 'https://www.sec.gov' + filing_link.get('href', '')
                                })
                
                # If ticker provided, try to find specific holdings
                if ticker and filings_data['recent_filings']:
                    # Get the most recent filing
                    latest_filing_url = filings_data['recent_filings'][0]['link']
                    async with self.session.get(latest_filing_url, headers=self.sec_headers) as filing_response:
                        filing_html = await filing_response.text()
                        filing_soup = BeautifulSoup(filing_html, 'html.parser')
                        
                        # Look for the information table link
                        info_table_link = filing_soup.find('a', text=re.compile('INFORMATION TABLE', re.I))
                        if info_table_link:
                            info_table_url = 'https://www.sec.gov' + info_table_link.get('href', '')
                            
                            async with self.session.get(info_table_url, headers=self.sec_headers) as table_response:
                                table_html = await table_response.text()
                                table_soup = BeautifulSoup(table_html, 'html.parser')
                                
                                # Parse holdings table
                                holdings_table = table_soup.find('table')
                                if holdings_table:
                                    for row in holdings_table.find_all('tr')[1:]:
                                        cells = row.find_all('td')
                                        if len(cells) >= 7:
                                            issuer_name = cells[0].text.strip()
                                            if ticker.upper() in issuer_name.upper():
                                                filings_data['holdings'].append({
                                                    'issuer': issuer_name,
                                                    'class': cells[1].text.strip(),
                                                    'cusip': cells[2].text.strip(),
                                                    'value': cells[3].text.strip(),
                                                    'shares': cells[4].text.strip(),
                                                    'type': cells[5].text.strip()
                                                })
                
                return filings_data
        
        except Exception as e:
            return {'error': f"Failed to scrape SEC 13F data: {str(e)}"}
    
    async def scrape_insider_trading(self, ticker: str) -> Dict[str, Any]:
        """Scrape insider trading data from multiple sources"""
        # OpenInsider
        openinsider_url = f"http://openinsider.com/search?q={ticker}"
        
        try:
            async with self.session.get(openinsider_url, headers=self.headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                insider_data = {
                    'ticker': ticker,
                    'source': 'openinsider',
                    'recent_transactions': [],
                    'summary': {
                        'total_bought': 0,
                        'total_sold': 0,
                        'net_activity': 0
                    }
                }
                
                # Find the insider trading table
                tables = soup.find_all('table', {'class': 'tinytable'})
                if tables:
                    for table in tables:
                        rows = table.find_all('tr')[1:]  # Skip header
                        for row in rows[:20]:  # Get recent 20 transactions
                            cells = row.find_all('td')
                            if len(cells) >= 10:
                                transaction = {
                                    'filing_date': cells[1].text.strip(),
                                    'trade_date': cells[2].text.strip(),
                                    'ticker': cells[3].text.strip(),
                                    'insider_name': cells[4].text.strip(),
                                    'title': cells[5].text.strip(),
                                    'trade_type': cells[6].text.strip(),
                                    'price': cells[7].text.strip(),
                                    'quantity': cells[8].text.strip(),
                                    'owned': cells[9].text.strip(),
                                    'value': cells[10].text.strip() if len(cells) > 10 else ''
                                }
                                
                                insider_data['recent_transactions'].append(transaction)
                                
                                # Update summary
                                try:
                                    qty = int(transaction['quantity'].replace(',', '').replace('+', ''))
                                    if 'Buy' in transaction['trade_type']:
                                        insider_data['summary']['total_bought'] += qty
                                    elif 'Sale' in transaction['trade_type']:
                                        insider_data['summary']['total_sold'] += qty
                                except:
                                    pass
                
                insider_data['summary']['net_activity'] = (
                    insider_data['summary']['total_bought'] - 
                    insider_data['summary']['total_sold']
                )
                
                return insider_data
        
        except Exception as e:
            return {'error': f"Failed to scrape insider trading data: {str(e)}"}
    
    async def get_institutional_changes(self, ticker: str) -> Dict[str, Any]:
        """Track institutional ownership changes over time"""
        # Combine data from multiple sources
        finviz_data = await self.scrape_finviz_institutional(ticker)
        nasdaq_data = await self.scrape_nasdaq_institutional(ticker)
        
        changes_data = {
            'ticker': ticker,
            'current_ownership': {},
            'top_institutions': [],
            'recent_changes': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Aggregate ownership data
        if not finviz_data.get('error'):
            changes_data['current_ownership'] = finviz_data.get('ownership', {})
            changes_data['recent_changes'] = finviz_data.get('recent_transactions', [])
        
        if not nasdaq_data.get('error'):
            changes_data['top_institutions'] = nasdaq_data.get('top_holders', [])
        
        return changes_data
    
    async def get_fund_holdings(self, fund_name: str) -> Dict[str, Any]:
        """Get holdings of a specific fund (e.g., ARK, Berkshire)"""
        # For demonstration, using WhaleWisdom-style scraping
        search_query = quote(fund_name)
        url = f"https://whalewisdom.com/filer/{search_query}"
        
        try:
            async with self.session.get(url, headers=self.headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                fund_data = {
                    'fund_name': fund_name,
                    'source': 'whalewisdom',
                    'top_holdings': [],
                    'recent_activity': []
                }
                
                # This is a simplified example - actual implementation would need
                # to handle the specific structure of the site
                holdings_table = soup.find('table', {'id': 'current_holdings_table'})
                if holdings_table:
                    rows = holdings_table.find_all('tr')[1:21]  # Top 20 holdings
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            fund_data['top_holdings'].append({
                                'stock': cells[0].text.strip(),
                                'shares': cells[1].text.strip(),
                                'value': cells[2].text.strip(),
                                'percentage': cells[3].text.strip(),
                                'change': cells[4].text.strip()
                            })
                
                return fund_data
        
        except Exception as e:
            return {'error': f"Failed to scrape fund holdings: {str(e)}"}


# Initialize server
server = Server("institutional-scraper")
scraper = InstitutionalScraper()

# Define tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="get_institutional_ownership",
            description="Get institutional and insider ownership percentages for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_insider_trading",
            description="Get recent insider trading transactions for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_13f_filings",
            description="Get Form 13F filings for an institutional investor",
            inputSchema={
                "type": "object",
                "properties": {
                    "cik": {
                        "type": "string",
                        "description": "CIK number of the institutional investor"
                    },
                    "ticker": {
                        "type": "string",
                        "description": "Optional: specific ticker to search for in holdings"
                    }
                },
                "required": ["cik"]
            }
        ),
        Tool(
            name="track_institutional_changes",
            description="Track changes in institutional ownership over time",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_top_institutional_holders",
            description="Get top institutional holders and their positions",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    await scraper.setup()
    
    try:
        if name == "get_institutional_ownership":
            ticker = arguments["ticker"].upper()
            
            # Get data from multiple sources
            finviz_data = await scraper.scrape_finviz_institutional(ticker)
            nasdaq_data = await scraper.scrape_nasdaq_institutional(ticker)
            
            combined_data = {
                'ticker': ticker,
                'ownership_summary': finviz_data.get('ownership', {}),
                'top_holders': nasdaq_data.get('top_holders', [])[:10],
                'data_sources': ['finviz', 'nasdaq'],
                'timestamp': datetime.now().isoformat()
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(combined_data, indent=2)
            )]
        
        elif name == "get_insider_trading":
            ticker = arguments["ticker"].upper()
            insider_data = await scraper.scrape_insider_trading(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(insider_data, indent=2)
            )]
        
        elif name == "get_13f_filings":
            cik = arguments["cik"]
            ticker = arguments.get("ticker")
            
            filings_data = await scraper.scrape_sec_form13f(cik, ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(filings_data, indent=2)
            )]
        
        elif name == "track_institutional_changes":
            ticker = arguments["ticker"].upper()
            changes_data = await scraper.get_institutional_changes(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(changes_data, indent=2)
            )]
        
        elif name == "get_top_institutional_holders":
            ticker = arguments["ticker"].upper()
            
            # Get comprehensive holder data
            nasdaq_data = await scraper.scrape_nasdaq_institutional(ticker)
            finviz_data = await scraper.scrape_finviz_institutional(ticker)
            
            holders_data = {
                'ticker': ticker,
                'top_institutions': nasdaq_data.get('top_holders', []),
                'ownership_breakdown': finviz_data.get('ownership', {}),
                'recent_institutional_activity': finviz_data.get('recent_transactions', [])[:10],
                'timestamp': datetime.now().isoformat()
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(holders_data, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

async def main():
    async with stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="institutional-scraper",
                server_version="0.1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())