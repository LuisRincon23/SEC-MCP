import time
#!/usr/bin/env python

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urljoin, quote

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

from advanced_nlp import AdvancedSentimentAnalyzer


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



class NewsSentimentScraper:
    """Scraper for financial news and sentiment analysis from free sources"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = {}

        # Initialize advanced components
        self.analysis_enhanced = True
        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
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
    
    async def scrape_finviz_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Scrape news headlines and sentiment from Finviz"""
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                news_table = soup.find('table', {'class': 'news-table'})
                if not news_table:
                    return []
                
                news_items = []
                for row in news_table.find_all('tr'):
                    date_cell = row.find('td', {'align': 'right'})
                    news_cell = row.find('td', {'align': 'left'})
                    
                    if date_cell and news_cell:
                        date_text = date_cell.text.strip()
                        link_elem = news_cell.find('a')
                        
                        if link_elem:
                            news_items.append({
                                'date': date_text,
                                'headline': link_elem.text.strip(),
                                'url': link_elem.get('href', ''),
                                'source': 'finviz'
                            })
                
                return news_items[:20]  # Return top 20 news items
        
        except aiohttp.ClientError as e:
            return [{'error': f'Network error: {str(e)}', 'retry_possible': True}]
        except Exception as e:
            return [{'error': f"Failed to scrape Finviz news: {str(e)}"}]
    
    async def scrape_seeking_alpha_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Scrape news and analysis from Seeking Alpha"""
        url = f"https://seekingalpha.com/symbol/{ticker}/news"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                news_items = []
                articles = soup.find_all('article', limit=10)
                
                for article in articles:
                    title_elem = article.find('a', {'data-test-id': 'post-list-item-title'})
                    time_elem = article.find('time')
                    
                    if title_elem:
                        news_items.append({
                            'date': time_elem.get('datetime', '') if time_elem else '',
                            'headline': title_elem.text.strip(),
                            'url': urljoin('https://seekingalpha.com', title_elem.get('href', '')),
                            'source': 'seeking_alpha'
                        })
                
                return news_items
        
        except aiohttp.ClientError as e:
            return [{'error': f'Network error: {str(e)}', 'retry_possible': True}]
        except Exception as e:
            return [{'error': f"Failed to scrape Seeking Alpha: {str(e)}"}]
    
    async def scrape_yahoo_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Scrape news from Yahoo Finance"""
        url = f"https://finance.yahoo.com/quote/{ticker}/news"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                news_items = []
                # Look for news items in the main content area
                news_sections = soup.find_all('li', {'class': re.compile('js-stream-content')})
                
                for section in news_sections[:15]:
                    headline_elem = section.find('h3')
                    if headline_elem:
                        link = headline_elem.find('a')
                        if link:
                            news_items.append({
                                'headline': link.text.strip(),
                                'url': link.get('href', ''),
                                'source': 'yahoo_finance'
                            })
                
                return news_items
        
        except aiohttp.ClientError as e:
            return [{'error': f'Network error: {str(e)}', 'retry_possible': True}]
        except Exception as e:
            return [{'error': f"Failed to scrape Yahoo news: {str(e)}"}]
    
    async def analyze_sentiment_keywords(self, text: str) -> Dict[str, Any]:
        """Simple keyword-based sentiment analysis"""
        positive_words = [
            'beat', 'exceed', 'outperform', 'upgrade', 'positive', 'growth', 
            'profit', 'gain', 'bullish', 'buy', 'strong', 'success', 'rise',
            'surge', 'jump', 'rally', 'boom', 'recover', 'expand'
        ]
        
        negative_words = [
            'miss', 'disappoint', 'downgrade', 'negative', 'loss', 'decline',
            'fall', 'bearish', 'sell', 'weak', 'cut', 'risk', 'concern',
            'drop', 'plunge', 'crash', 'slump', 'recession', 'warning'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = -negative_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else -0.5
        else:
            sentiment = 'neutral'
            score = 0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    async def scrape_google_news(self, query: str) -> List[Dict[str, Any]]:
        """Scrape news from Google News RSS"""
        # Use Google News RSS feed for free access
        rss_url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            async with self.session.get(rss_url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'xml')
                
                news_items = []
                for item in soup.find_all('item')[:20]:
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    
                    if title and link:
                        news_items.append({
                            'headline': title.text,
                            'url': link.text,
                            'date': pub_date.text if pub_date else '',
                            'source': 'google_news'
                        })
                
                return news_items
        
        except aiohttp.ClientError as e:
            return [{'error': f'Network error: {str(e)}', 'retry_possible': True}]
        except Exception as e:
            return [{'error': f"Failed to scrape Google News: {str(e)}"}]
    
    async def aggregate_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Aggregate sentiment from multiple news sources"""
        # Gather news from multiple sources
        finviz_news = await self.scrape_finviz_news(ticker)
        yahoo_news = await self.scrape_yahoo_news(ticker)
        google_news = await self.scrape_google_news(f"{ticker} stock")
        
        all_news = finviz_news + yahoo_news + google_news
        
        # Analyze sentiment for each headline
        sentiments = []
        for news_item in all_news:
            if 'headline' in news_item and not news_item.get('error'):
                sentiment = await self.analyze_sentiment_keywords(news_item['headline'])
                news_item['sentiment'] = sentiment
                sentiments.append(sentiment['score'])
        
        # Calculate aggregate sentiment
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            if avg_sentiment > 0.1:
                overall_sentiment = 'positive'
            elif avg_sentiment < -0.1:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
        else:
            avg_sentiment = 0
            overall_sentiment = 'neutral'
        
        return {
            'ticker': ticker,
            'overall_sentiment': overall_sentiment,
            'sentiment_score': avg_sentiment,
            'total_articles': len(all_news),
            'sources': {
                'finviz': len(finviz_news),
                'yahoo': len(yahoo_news),
                'google': len(google_news)
            },
            'recent_news': all_news[:10],  # Top 10 most recent
            'timestamp': datetime.now().isoformat()
        }


# Initialize server
server = Server("news-sentiment-scraper")
scraper = NewsSentimentScraper()

# Define tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="scrape_stock_news",
            description="Scrape recent news articles for a stock ticker from multiple sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, MSFT)"
                    },
                    "source": {
                        "type": "string",
                        "description": "News source: finviz, yahoo, seeking_alpha, or all",
                        "default": "all"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="analyze_news_sentiment",
            description="Analyze sentiment of news headlines using keyword analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze for sentiment"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_aggregate_sentiment",
            description="Get aggregated sentiment analysis from multiple news sources for a stock",
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
            name="search_financial_news",
            description="Search for financial news using custom queries",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'Apple earnings', 'tech stocks 2024')"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_sector_sentiment",
            description="Get sentiment analysis for an entire sector",
            inputSchema={
                "type": "object",
                "properties": {
                    "sector": {
                        "type": "string",
                        "description": "Sector name (e.g., technology, healthcare, energy)"
                    },
                    "top_stocks": {
                        "type": "array",
                        "description": "List of top stock tickers in the sector",
                        "items": {"type": "string"}
                    }
                },
                "required": ["sector", "top_stocks"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    await scraper.setup()
    
    try:
        if name == "scrape_stock_news":
            ticker = arguments["ticker"].upper()
            source = arguments.get("source", "all").lower()
            
            results = {}
            if source == "all" or source == "finviz":
                results["finviz"] = await scraper.scrape_finviz_news(ticker)
            if source == "all" or source == "yahoo":
                results["yahoo"] = await scraper.scrape_yahoo_news(ticker)
            if source == "all" or source == "seeking_alpha":
                results["seeking_alpha"] = await scraper.scrape_seeking_alpha_news(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(results, indent=2)
            )]
        
        elif name == "analyze_news_sentiment":
            text = arguments["text"]
            sentiment = await scraper.analyze_sentiment_keywords(text)
            
            return [TextContent(
                type="text",
                text=json.dumps(sentiment, indent=2)
            )]
        
        elif name == "get_aggregate_sentiment":
            ticker = arguments["ticker"].upper()
            aggregate = await scraper.aggregate_sentiment(ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(aggregate, indent=2)
            )]
        
        elif name == "search_financial_news":
            query = arguments["query"]
            results = await scraper.scrape_google_news(query)
            
            # Add sentiment to each result
            for item in results:
                if 'headline' in item and not item.get('error'):
                    sentiment = await scraper.analyze_sentiment_keywords(item['headline'])
                    item['sentiment'] = sentiment
            
            return [TextContent(
                type="text",
                text=json.dumps(results, indent=2)
            )]
        
        elif name == "get_sector_sentiment":
            sector = arguments["sector"]
            stocks = arguments["top_stocks"]
            
            sector_sentiments = []
            for stock in stocks[:5]:  # Limit to top 5 to avoid rate limiting
                sentiment = await scraper.aggregate_sentiment(stock)
                sector_sentiments.append({
                    'ticker': stock,
                    'sentiment': sentiment['overall_sentiment'],
                    'score': sentiment['sentiment_score']
                })
            
            # Calculate sector average
            scores = [s['score'] for s in sector_sentiments]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            if avg_score > 0.1:
                sector_sentiment = 'positive'
            elif avg_score < -0.1:
                sector_sentiment = 'negative'
            else:
                sector_sentiment = 'neutral'
            
            result = {
                'sector': sector,
                'overall_sentiment': sector_sentiment,
                'average_score': avg_score,
                'stock_sentiments': sector_sentiments,
                'timestamp': datetime.now().isoformat()
            }
            
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
                server_name="news-sentiment-scraper",
                server_version="0.1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())