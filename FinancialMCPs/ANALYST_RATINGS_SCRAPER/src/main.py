import time
#!/usr/bin/env python

import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

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

from financial_analysis import ComparativeAnalysis


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



class AnalystRatingsScraper:
    """Scraper for analyst ratings and price targets from free sources"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = {}

        # Initialize advanced components
        self.analysis_enhanced = True
        self.min_delay = 1.0  # Rate limiting
        self.headers = {
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
            self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def cleanup(self):
        """Cleanup aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def scrape_finviz_ratings(self, ticker: str) -> Dict[str, Any]:
        """Scrape analyst ratings from Finviz"""
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                ratings_data = {
                    'ticker': ticker,
                    'source': 'finviz',
                    'ratings': {},
                    'price_targets': {}
                }
                
                # Find the ratings table
                tables = soup.find_all('table', {'class': 'ratings-outer'})
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            # Parse rating data
                            date = cells[0].text.strip()
                            action = cells[1].text.strip()
                            analyst = cells[2].text.strip()
                            rating = cells[3].text.strip()
                            price_target = cells[4].text.strip()
                            
                            if 'ratings' not in ratings_data:
                                ratings_data['ratings'] = []
                            
                            ratings_data['ratings'].append({
                                'date': date,
                                'action': action,
                                'analyst': analyst,
                                'rating': rating,
                                'price_target': price_target
                            })
                
                # Get consensus data from the main table
                snapshot_table = soup.find('table', {'class': 'snapshot-table'})
                if snapshot_table:
                    for row in snapshot_table.find_all('tr'):
                        cells = row.find_all('td')
                        for i in range(0, len(cells), 2):
                            if i + 1 < len(cells):
                                label = cells[i].text.strip()
                                value = cells[i + 1].text.strip()
                                
                                if 'Target Price' in label:
                                    ratings_data['consensus_target'] = value
                                elif 'Recom' in label:
                                    ratings_data['consensus_rating'] = value
                
                return ratings_data
        
        except Exception as e:
            return {'error': f"Failed to scrape Finviz ratings: {str(e)}"}
    
    async def scrape_marketwatch_ratings(self, ticker: str) -> Dict[str, Any]:
        """Scrape analyst ratings from MarketWatch"""
        url = f"https://www.marketwatch.com/investing/stock/{ticker}/analystestimates"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                ratings_data = {
                    'ticker': ticker,
                    'source': 'marketwatch',
                    'consensus': {},
                    'distribution': {}
                }
                
                # Look for analyst consensus section
                consensus_section = soup.find('div', {'class': 'analyst-consensus'})
                if consensus_section:
                    rating = consensus_section.find('div', {'class': 'recommendation'})
                    if rating:
                        ratings_data['consensus']['rating'] = rating.text.strip()
                
                # Look for ratings distribution
                ratings_table = soup.find('table', {'class': 'ratings-distribution'})
                if ratings_table:
                    for row in ratings_table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            rating_type = cells[0].text.strip()
                            count = cells[1].text.strip()
                            ratings_data['distribution'][rating_type] = count
                
                return ratings_data
        
        except Exception as e:
            return {'error': f"Failed to scrape MarketWatch ratings: {str(e)}"}
    
    async def scrape_yahoo_analyst_info(self, ticker: str) -> Dict[str, Any]:
        """Scrape analyst information from Yahoo Finance"""
        url = f"https://finance.yahoo.com/quote/{ticker}/analysis"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                analyst_data = {
                    'ticker': ticker,
                    'source': 'yahoo_finance',
                    'price_targets': {},
                    'earnings_estimates': {},
                    'recommendation_trends': []
                }
                
                # Extract tables with analyst data
                tables = soup.find_all('table')
                
                for table in tables:
                    # Check table headers to identify content
                    headers = [th.text.strip() for th in table.find_all('th')]
                    
                    if 'Low' in headers and 'High' in headers and 'Average' in headers:
                        # Price target table
                        rows = table.find_all('tr')[1:]  # Skip header
                        for row in rows:
                            cells = row.find_all('td')
                            if cells:
                                period = cells[0].text.strip()
                                analyst_data['price_targets'][period] = {
                                    'low': cells[1].text.strip() if len(cells) > 1 else '',
                                    'high': cells[2].text.strip() if len(cells) > 2 else '',
                                    'average': cells[3].text.strip() if len(cells) > 3 else '',
                                    'current': cells[4].text.strip() if len(cells) > 4 else ''
                                }
                    
                    elif 'No. of Analysts' in headers:
                        # Earnings estimates table
                        rows = table.find_all('tr')[1:]
                        for row in rows:
                            cells = row.find_all('td')
                            if cells and len(cells) > 1:
                                metric = cells[0].text.strip()
                                analyst_data['earnings_estimates'][metric] = {
                                    'current_qtr': cells[1].text.strip() if len(cells) > 1 else '',
                                    'next_qtr': cells[2].text.strip() if len(cells) > 2 else '',
                                    'current_year': cells[3].text.strip() if len(cells) > 3 else '',
                                    'next_year': cells[4].text.strip() if len(cells) > 4 else ''
                                }
                
                return analyst_data
        
        except Exception as e:
            return {'error': f"Failed to scrape Yahoo analyst info: {str(e)}"}
    
    async def scrape_benzinga_ratings(self, ticker: str) -> List[Dict[str, Any]]:
        """Scrape recent analyst actions from Benzinga"""
        url = f"https://www.benzinga.com/quote/{ticker}/analyst-ratings"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                ratings = []
                
                # Look for analyst ratings in the content
                rating_items = soup.find_all('div', {'class': re.compile('analyst-rating-item')})
                
                for item in rating_items[:20]:  # Get recent 20 ratings
                    date_elem = item.find('span', {'class': 'date'})
                    firm_elem = item.find('span', {'class': 'firm'})
                    action_elem = item.find('span', {'class': 'action'})
                    rating_elem = item.find('span', {'class': 'rating'})
                    target_elem = item.find('span', {'class': 'price-target'})
                    
                    rating_data = {
                        'date': date_elem.text.strip() if date_elem else '',
                        'firm': firm_elem.text.strip() if firm_elem else '',
                        'action': action_elem.text.strip() if action_elem else '',
                        'rating': rating_elem.text.strip() if rating_elem else '',
                        'price_target': target_elem.text.strip() if target_elem else '',
                        'source': 'benzinga'
                    }
                    
                    if any(rating_data.values()):
                        ratings.append(rating_data)
                
                return ratings
        
        except aiohttp.ClientError as e:
            return [{'error': f'Network error: {str(e)}', 'retry_possible': True}]
        except Exception as e:
            return [{'error': f"Failed to scrape Benzinga ratings: {str(e)}"}]
    
    async def calculate_consensus(self, ticker: str) -> Dict[str, Any]:
        """Calculate consensus rating from multiple sources"""
        # Gather data from all sources
        finviz_data = await self.scrape_finviz_ratings(ticker)
        yahoo_data = await self.scrape_yahoo_analyst_info(ticker)
        marketwatch_data = await self.scrape_marketwatch_ratings(ticker)
        
        consensus = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'sources': {},
            'overall_consensus': {}
        }
        
        # Add source data
        if not finviz_data.get('error'):
            consensus['sources']['finviz'] = {
                'consensus_rating': finviz_data.get('consensus_rating', 'N/A'),
                'consensus_target': finviz_data.get('consensus_target', 'N/A'),
                'recent_actions': len(finviz_data.get('ratings', []))
            }
        
        if not yahoo_data.get('error'):
            consensus['sources']['yahoo'] = {
                'price_targets': yahoo_data.get('price_targets', {}),
                'earnings_estimates': yahoo_data.get('earnings_estimates', {})
            }
        
        if not marketwatch_data.get('error'):
            consensus['sources']['marketwatch'] = {
                'consensus': marketwatch_data.get('consensus', {}),
                'distribution': marketwatch_data.get('distribution', {})
            }
        
        # Calculate overall consensus
        rating_map = {
            'Strong Buy': 5, 'Buy': 4, 'Hold': 3, 'Sell': 2, 'Strong Sell': 1,
            'Outperform': 4, 'Market Perform': 3, 'Underperform': 2,
            'Overweight': 4, 'Equal Weight': 3, 'Underweight': 2
        }
        
        ratings = []
        if finviz_data.get('consensus_rating'):
            rating_text = finviz_data['consensus_rating'].split('(')[0].strip()
            for key, value in rating_map.items():
                if key.lower() in rating_text.lower():
                    ratings.append(value)
                    break
        
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating >= 4:
                consensus['overall_consensus']['rating'] = 'Buy'
            elif avg_rating >= 3:
                consensus['overall_consensus']['rating'] = 'Hold'
            else:
                consensus['overall_consensus']['rating'] = 'Sell'
            consensus['overall_consensus']['score'] = avg_rating
        
        return consensus


# Initialize server
server = Server("analyst-ratings-scraper")
scraper = AnalystRatingsScraper()

# Define tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="get_analyst_ratings",
            description="Get recent analyst ratings and actions for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "source": {
                        "type": "string",
                        "description": "Data source: finviz, marketwatch, yahoo, benzinga, or all",
                        "default": "all"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_price_targets",
            description="Get analyst price targets and ranges",
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
            name="get_consensus_rating",
            description="Get consensus analyst rating from multiple sources",
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
            name="get_rating_changes",
            description="Get recent analyst rating changes and upgrades/downgrades",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "days": {
                        "type": "number",
                        "description": "Number of days to look back",
                        "default": 30
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="compare_analyst_coverage",
            description="Compare analyst coverage between multiple stocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "description": "List of stock ticker symbols to compare",
                        "items": {"type": "string"}
                    }
                },
                "required": ["tickers"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    await scraper.setup()
    
    try:
        if name == "get_analyst_ratings":
            ticker = arguments["ticker"].upper()
            source = arguments.get("source", "all").lower()
            
            results = {}
            if source == "all" or source == "finviz":
                results["finviz"] = await scraper.scrape_finviz_ratings(ticker)
            if source == "all" or source == "marketwatch":
                results["marketwatch"] = await scraper.scrape_marketwatch_ratings(ticker)
            if source == "all" or source == "yahoo":
                results["yahoo"] = await scraper.scrape_yahoo_analyst_info(ticker)
            if source == "all" or source == "benzinga":
                results["benzinga"] = await scraper.scrape_benzinga_ratings(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(results, indent=2)
            )]
        
        elif name == "get_price_targets":
            ticker = arguments["ticker"].upper()
            
            # Get price targets from multiple sources
            finviz_data = await scraper.scrape_finviz_ratings(ticker)
            yahoo_data = await scraper.scrape_yahoo_analyst_info(ticker)
            
            price_targets = {
                'ticker': ticker,
                'finviz_target': finviz_data.get('consensus_target', 'N/A'),
                'yahoo_targets': yahoo_data.get('price_targets', {}),
                'recent_changes': []
            }
            
            # Extract recent price target changes from Finviz
            if 'ratings' in finviz_data:
                for rating in finviz_data['ratings'][:10]:
                    if rating.get('price_target') and rating['price_target'] != '':
                        price_targets['recent_changes'].append({
                            'date': rating['date'],
                            'analyst': rating['analyst'],
                            'target': rating['price_target'],
                            'action': rating['action']
                        })
            
            return [TextContent(
                type="text",
                text=json.dumps(price_targets, indent=2)
            )]
        
        elif name == "get_consensus_rating":
            ticker = arguments["ticker"].upper()
            consensus = await scraper.calculate_consensus(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(consensus, indent=2)
            )]
        
        elif name == "get_rating_changes":
            ticker = arguments["ticker"].upper()
            days = arguments.get("days", 30)
            
            # Get recent ratings from Finviz
            finviz_data = await scraper.scrape_finviz_ratings(ticker)
            benzinga_data = await scraper.scrape_benzinga_ratings(ticker)
            
            changes = {
                'ticker': ticker,
                'period': f"Last {days} days",
                'upgrades': [],
                'downgrades': [],
                'initiations': [],
                'reiterations': []
            }
            
            # Process Finviz ratings
            if 'ratings' in finviz_data:
                for rating in finviz_data['ratings']:
                    action = rating.get('action', '').lower()
                    if 'upgrade' in action:
                        changes['upgrades'].append(rating)
                    elif 'downgrade' in action:
                        changes['downgrades'].append(rating)
                    elif 'initiat' in action:
                        changes['initiations'].append(rating)
                    elif 'reiterat' in action:
                        changes['reiterations'].append(rating)
            
            changes['summary'] = {
                'total_actions': len(changes['upgrades']) + len(changes['downgrades']) + 
                                len(changes['initiations']) + len(changes['reiterations']),
                'upgrades': len(changes['upgrades']),
                'downgrades': len(changes['downgrades']),
                'new_coverage': len(changes['initiations'])
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(changes, indent=2)
            )]
        
        elif name == "compare_analyst_coverage":
            tickers = [t.upper() for t in arguments["tickers"]]
            
            comparison = {
                'tickers': tickers,
                'coverage': {},
                'timestamp': datetime.now().isoformat()
            }
            
            for ticker in tickers[:5]:  # Limit to 5 to avoid rate limiting
                consensus = await scraper.calculate_consensus(ticker)
                finviz_data = await scraper.scrape_finviz_ratings(ticker)
                
                comparison['coverage'][ticker] = {
                    'consensus_rating': consensus.get('overall_consensus', {}).get('rating', 'N/A'),
                    'consensus_score': consensus.get('overall_consensus', {}).get('score', 0),
                    'price_target': finviz_data.get('consensus_target', 'N/A'),
                    'recent_actions': len(finviz_data.get('ratings', [])),
                    'sources': list(consensus.get('sources', {}).keys())
                }
            
            return [TextContent(
                type="text",
                text=json.dumps(comparison, indent=2)
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
                server_name="analyst-ratings-scraper",
                server_version="0.1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())