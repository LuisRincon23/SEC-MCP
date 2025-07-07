import time
#!/usr/bin/env python

import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urljoin

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

from xbrl_parser import XBRLParser
from financial_analysis import DCFModel, FinancialMetrics
from research_report_generator import ResearchReportGenerator


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



class SECScraper:
    """Scraper for SEC EDGAR filings and financial data"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = {}

        # Initialize advanced components
        self.analysis_enhanced = True
        self.xbrl_parser = XBRLParser()
        self.dcf_model = DCFModel()
        self.min_delay = 1.0  # Rate limiting
        self.sec_headers = {
            'User-Agent': 'FinancialMCP/1.0 (Personal Research Tool; Contact: research@example.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        self.yahoo_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
    
    async def search_company_filings(self, ticker: str, filing_type: str = None) -> List[Dict[str, Any]]:
        """Search for company filings on SEC EDGAR"""
        # First, get CIK from ticker
        cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&owner=exclude"
        
        try:
            async with self.session.get(cik_url, headers=self.sec_headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract CIK
                cik_elem = soup.find('span', {'class': re.compile('companyName')}) or soup.find(text=re.compile('CIK#:'))
                if not cik_elem:
                    return [{'error': f'Company not found for ticker {ticker}'}]
                
                cik_text = cik_elem.text
                cik_match = re.search(r'CIK#: (\d+)', cik_text)
                if not cik_match:
                    return [{'error': 'Could not extract CIK'}]
                
                cik = cik_match.group(1).zfill(10)  # Pad with zeros
                
                # Search for filings
                if filing_type:
                    search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={filing_type}&count=10"
                else:
                    search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&count=10"
                
                async with self.session.get(search_url, headers=self.sec_headers) as filing_response:
                    filing_html = await filing_response.text()
                    filing_soup = BeautifulSoup(filing_html, 'html.parser')
                    
                    filings = []
                    filing_table = filing_soup.find('table', {'class': re.compile('tableFile')}) or soup.find('table', {'summary': re.compile('Document')})
                    
                    if filing_table:
                        rows = filing_table.find_all('tr')[1:]  # Skip header
                        
                        for row in rows[:10]:  # Get latest 10 filings
                            cells = row.find_all('td')
                            if len(cells) >= 4:
                                filing_link = cells[1].find('a')
                                doc_link = cells[2].find('a', {'id': re.compile('documentsbutton')})
                                
                                filing = {
                                    'filing_type': cells[0].text.strip(),
                                    'filing_date': cells[3].text.strip(),
                                    'description': cells[2].text.strip(),
                                }
                                
                                if doc_link:
                                    filing['documents_url'] = urljoin('https://www.sec.gov', doc_link.get('href', ''))
                                
                                filings.append(filing)
                    
                    return filings
        
        except aiohttp.ClientError as e:
            return [{'error': f'Network error: {str(e)}', 'retry_possible': True}]
        except Exception as e:
            return [{'error': f'Failed to search filings: {type(e).__name__}: {str(e)}', 'retry_possible': True}]
    
    async def scrape_10k_financials(self, ticker: str) -> Dict[str, Any]:
        """Scrape financial statements from latest 10-K filing"""
        filings = await self.search_company_filings(ticker, '10-K')
        
        if not filings or 'error' in filings[0]:
            return {'error': 'No 10-K filings found'}
        
        latest_10k = filings[0]
        
        if 'documents_url' not in latest_10k:
            return {'error': 'No document URL found'}
        
        try:
            async with self.session.get(latest_10k['documents_url'], headers=self.sec_headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the main 10-K document
                doc_table = soup.find('table', {'class': 'tableFile'})
                if not doc_table:
                    return {'error': 'Document table not found'}
                
                main_doc_link = None
                for row in doc_table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if cells and '10-K' in cells[3].text:
                        link = cells[2].find('a')
                        if link:
                            main_doc_link = urljoin('https://www.sec.gov', link.get('href', ''))
                            break
                
                if not main_doc_link:
                    return {'error': '10-K document link not found'}
                
                # Get the 10-K content
                async with self.session.get(main_doc_link, headers=self.sec_headers) as doc_response:
                    doc_html = await doc_response.text()
                    doc_soup = BeautifulSoup(doc_html, 'html.parser')
                    
                    # Extract financial data (simplified - real implementation would parse XBRL)
                    financial_data = {
                        'ticker': ticker,
                        'filing_date': latest_10k['filing_date'],
                        'document_url': main_doc_link,
                        'sections': {}
                    }
                    
                    # Look for key sections
                    text_content = doc_soup.get_text()
                    
                    # Extract revenue mentions
                    revenue_matches = re.findall(r'(?:revenue|net sales).*?\$[\d,]+(?:\.\d+)?\s*(?:million|billion)', 
                                               text_content, re.IGNORECASE)
                    if revenue_matches:
                        financial_data['sections']['revenue_mentions'] = revenue_matches[:5]
                    
                    # Extract income mentions
                    income_matches = re.findall(r'net (?:income|loss).*?\$[\d,]+(?:\.\d+)?\s*(?:million|billion)', 
                                              text_content, re.IGNORECASE)
                    if income_matches:
                        financial_data['sections']['income_mentions'] = income_matches[:5]
                    
                    return financial_data
        
        except Exception as e:
            return {'error': f'Failed to scrape 10-K: {str(e)}'}
    
    async def scrape_10q_earnings(self, ticker: str) -> Dict[str, Any]:
        """Scrape quarterly earnings from latest 10-Q filing"""
        filings = await self.search_company_filings(ticker, '10-Q')
        
        if not filings or 'error' in filings[0]:
            return {'error': 'No 10-Q filings found'}
        
        latest_10q = filings[0]
        
        return {
            'ticker': ticker,
            'filing_type': '10-Q',
            'filing_date': latest_10q['filing_date'],
            'description': latest_10q.get('description', ''),
            'documents_url': latest_10q.get('documents_url', ''),
            'note': 'Full 10-Q parsing would extract detailed quarterly financials'
        }
    
    async def scrape_8k_events(self, ticker: str) -> List[Dict[str, Any]]:
        """Scrape recent 8-K material events"""
        filings = await self.search_company_filings(ticker, '8-K')
        
        if not filings or 'error' in filings[0]:
            return [{'error': 'No 8-K filings found'}]
        
        # Return the recent 8-K filings with their descriptions
        events = []
        for filing in filings[:5]:  # Get latest 5 events
            events.append({
                'ticker': ticker,
                'filing_type': '8-K',
                'filing_date': filing['filing_date'],
                'description': filing.get('description', ''),
                'documents_url': filing.get('documents_url', '')
            })
        
        return events
    
    async def parse_xbrl_data(self, ticker: str, filing_type: str = '10-K') -> Dict[str, Any]:
        """Parse XBRL structured data from filings using the XBRL parser"""
        try:
            # Get latest filing
            filings = await self.search_company_filings(ticker, filing_type)
            
            if not filings or 'error' in filings[0]:
                return {'error': f'No {filing_type} filings found'}
            
            latest_filing = filings[0]
            
            if 'documents_url' not in latest_filing:
                return {'error': 'No document URL found'}
            
            # Use XBRL parser to fetch and parse
            xbrl_content = await self.xbrl_parser.fetch_xbrl_from_filing(
                latest_filing['documents_url'], self.session
            )
            
            if xbrl_content:
                parsed_data = self.xbrl_parser.parse_xbrl_string(xbrl_content)
                key_metrics = self.xbrl_parser.extract_key_metrics(parsed_data)
                
                return {
                    'ticker': ticker,
                    'filing_type': filing_type,
                    'filing_date': latest_filing['filing_date'],
                    'parsed_data': parsed_data,
                    'key_metrics': key_metrics
                }
            else:
                return {
                    'ticker': ticker,
                    'filing_type': filing_type,
                    'note': 'XBRL data not available, using HTML extraction',
                    'filing_date': latest_filing['filing_date']
                }
                
        except Exception as e:
            return {'error': f'Failed to parse XBRL: {str(e)}'}
    
    async def get_current_price(self, ticker: str) -> Dict[str, Any]:
        """Get current stock price from Yahoo Finance"""
        url = f"https://finance.yahoo.com/quote/{ticker}"
        
        try:
            async with self.session.get(url, headers=self.yahoo_headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                price_data = {
                    'ticker': ticker,
                    'source': 'yahoo_finance',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Find price
                price_elem = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
                if price_elem:
                    price_data['price'] = price_elem.get('data-value', price_elem.text)
                
                # Find change
                change_elem = soup.find('fin-streamer', {'data-field': 'regularMarketChange'})
                if change_elem:
                    price_data['change'] = change_elem.get('data-value', change_elem.text)
                
                # Find change percent
                change_pct_elem = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'})
                if change_pct_elem:
                    price_data['change_percent'] = change_pct_elem.get('data-value', change_pct_elem.text)
                
                # Find volume
                volume_elem = soup.find('fin-streamer', {'data-field': 'regularMarketVolume'})
                if volume_elem:
                    price_data['volume'] = volume_elem.get('data-value', volume_elem.text)
                
                # Find market cap
                market_cap_elem = soup.find('td', {'data-test': 'MARKET_CAP-value'})
                if market_cap_elem:
                    price_data['market_cap'] = market_cap_elem.text
                
                return price_data
        
        except Exception as e:
            return {'error': f'Failed to get price: {str(e)}'}


# Initialize server
server = Server("sec-scraper")
scraper = SECScraper()

# Define tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="scrape_10k_financials",
            description="Scrape financial statements from the latest 10-K annual report",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, MSFT)"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="scrape_10q_earnings",
            description="Scrape quarterly earnings data from the latest 10-Q report",
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
            name="scrape_8k_events",
            description="Scrape recent 8-K material events and announcements",
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
            name="parse_xbrl_data",
            description="Parse XBRL structured financial data from SEC filings",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "filing_type": {
                        "type": "string",
                        "description": "Type of filing (10-K, 10-Q, etc.)",
                        "default": "10-K"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_current_price",
            description="Get current stock price and market data",
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
        if name == "scrape_10k_financials":
            ticker = arguments["ticker"].upper()
            result = await scraper.scrape_10k_financials(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "scrape_10q_earnings":
            ticker = arguments["ticker"].upper()
            result = await scraper.scrape_10q_earnings(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "scrape_8k_events":
            ticker = arguments["ticker"].upper()
            result = await scraper.scrape_8k_events(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "parse_xbrl_data":
            ticker = arguments["ticker"].upper()
            filing_type = arguments.get("filing_type", "10-K")
            result = await scraper.parse_xbrl_data(ticker, filing_type)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_current_price":
            ticker = arguments["ticker"].upper()
            result = await scraper.get_current_price(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
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
                server_name="sec-scraper",
                server_version="0.1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())