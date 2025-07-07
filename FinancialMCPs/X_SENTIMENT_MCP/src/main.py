#!/usr/bin/env python3
"""
X (Twitter) Financial Sentiment Analysis MCP
Real-time sentiment tracking for stocks and crypto
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
import sys
from pathlib import Path

# Add shared modules
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

import aiohttp
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
import mcp.server.stdio as stdio

from advanced_nlp import AdvancedSentimentAnalyzer
from data_cache import cache_result


class XSentimentAnalyzer:
    """Analyze X (Twitter) sentiment for financial instruments"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
        
        # Cashtag and trading patterns
        self.trading_patterns = {
            'bullish': [
                r'moon', r'rocket', r'🚀', r'bull', r'calls', r'long',
                r'buy', r'accumulate', r'breakout', r'ATH', r'squeeze',
                r'gamma', r'tendies', r'print', r'pump', r'🐂', r'📈'
            ],
            'bearish': [
                r'puts', r'short', r'dump', r'crash', r'sell', r'bear',
                r'overvalued', r'bubble', r'correction', r'red', r'🐻', r'📉',
                r'rug', r'exit', r'stop loss', r'capitulation'
            ],
            'neutral': [
                r'hold', r'wait', r'watch', r'sideways', r'range', r'consolidation'
            ]
        }
        
        # Influential accounts (for weighted sentiment)
        self.influential_accounts = {
            'high_influence': ['elonmusk', 'cathiedwood', 'jimcramer', 'carlicahn'],
            'medium_influence': ['marketwatch', 'benzinga', 'unusual_whales'],
            'news_accounts': ['reuters', 'bloomberg', 'wsj', 'ft']
        }
    
    async def setup(self):
        """Setup aiohttp session"""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(headers=self.headers, timeout=timeout)
    
    @cache_result('x_sentiment', ttl=timedelta(minutes=15))
    async def analyze_ticker_sentiment(self, ticker: str, 
                                     timeframe: str = '24h') -> Dict[str, Any]:
        """Analyze X sentiment for a specific ticker"""
        
        # Search for cashtag
        cashtag = f"${ticker.upper()}"
        
        # Note: X API requires authentication. This is a simplified version
        # In production, you'd use X API v2 with proper authentication
        
        # Simulated data structure (would be replaced with actual X API calls)
        tweets = await self._search_tweets(cashtag, timeframe)
        
        # Analyze sentiment
        sentiment_results = []
        volume_by_hour = {}
        influential_sentiment = []
        
        for tweet in tweets:
            # Analyze individual tweet
            sentiment = self._analyze_tweet_sentiment(tweet)
            sentiment_results.append(sentiment)
            
            # Track volume
            hour = tweet.get('created_at', datetime.now()).hour
            volume_by_hour[hour] = volume_by_hour.get(hour, 0) + 1
            
            # Track influential accounts
            if tweet.get('author') in self.influential_accounts['high_influence']:
                influential_sentiment.append({
                    'author': tweet['author'],
                    'sentiment': sentiment['sentiment'],
                    'reach': tweet.get('retweet_count', 0) + tweet.get('like_count', 0)
                })
        
        # Aggregate results
        total_tweets = len(sentiment_results)
        if total_tweets > 0:
            bullish_count = sum(1 for s in sentiment_results if s['sentiment'] == 'bullish')
            bearish_count = sum(1 for s in sentiment_results if s['sentiment'] == 'bearish')
            
            sentiment_score = (bullish_count - bearish_count) / total_tweets
            
            # Velocity (rate of change)
            recent_sentiment = sentiment_results[-20:] if len(sentiment_results) > 20 else sentiment_results
            recent_score = sum(1 if s['sentiment'] == 'bullish' else -1 if s['sentiment'] == 'bearish' else 0 
                             for s in recent_sentiment) / len(recent_sentiment)
            
            velocity = recent_score - sentiment_score
            
            results = {
                'ticker': ticker,
                'timeframe': timeframe,
                'total_tweets': total_tweets,
                'sentiment_distribution': {
                    'bullish': bullish_count / total_tweets,
                    'bearish': bearish_count / total_tweets,
                    'neutral': (total_tweets - bullish_count - bearish_count) / total_tweets
                },
                'sentiment_score': sentiment_score,
                'sentiment_label': self._score_to_label(sentiment_score),
                'momentum': {
                    'velocity': velocity,
                    'accelerating': velocity > 0.1,
                    'decelerating': velocity < -0.1
                },
                'volume_profile': volume_by_hour,
                'peak_hours': sorted(volume_by_hour.items(), key=lambda x: x[1], reverse=True)[:3],
                'influential_sentiment': influential_sentiment[:5],
                'trending_topics': self._extract_trending_topics(tweets),
                'risk_indicators': self._identify_risk_indicators(sentiment_results, tweets)
            }
        else:
            results = {
                'ticker': ticker,
                'error': 'No tweets found',
                'suggestion': 'Try a more popular ticker or increase timeframe'
            }
        
        return results
    
    async def analyze_multiple_tickers(self, tickers: List[str]) -> Dict[str, Any]:
        """Analyze sentiment for multiple tickers and compare"""
        
        results = {}
        for ticker in tickers:
            results[ticker] = await self.analyze_ticker_sentiment(ticker)
        
        # Comparative analysis
        comparison = {
            'tickers': tickers,
            'sentiment_ranking': sorted(
                [(t, r.get('sentiment_score', 0)) for t, r in results.items()],
                key=lambda x: x[1],
                reverse=True
            ),
            'volume_ranking': sorted(
                [(t, r.get('total_tweets', 0)) for t, r in results.items()],
                key=lambda x: x[1],
                reverse=True
            ),
            'momentum_leaders': [
                t for t, r in results.items() 
                if r.get('momentum', {}).get('accelerating', False)
            ],
            'detailed_results': results
        }
        
        return comparison
    
    async def track_sentiment_alerts(self, ticker: str) -> Dict[str, Any]:
        """Identify significant sentiment shifts and alerts"""
        
        current = await self.analyze_ticker_sentiment(ticker, '1h')
        historical = await self.analyze_ticker_sentiment(ticker, '24h')
        
        alerts = []
        
        # Check for sentiment reversal
        if current.get('sentiment_score', 0) * historical.get('sentiment_score', 0) < 0:
            alerts.append({
                'type': 'sentiment_reversal',
                'severity': 'high',
                'message': f"Sentiment reversed from {historical['sentiment_label']} to {current['sentiment_label']}"
            })
        
        # Check for volume spike
        current_volume = current.get('total_tweets', 0)
        avg_volume = historical.get('total_tweets', 0) / 24
        if current_volume > avg_volume * 3:
            alerts.append({
                'type': 'volume_spike',
                'severity': 'medium',
                'message': f"Tweet volume 3x above average ({current_volume} vs {avg_volume:.0f})"
            })
        
        # Check for influential activity
        if current.get('influential_sentiment'):
            alerts.append({
                'type': 'influential_activity',
                'severity': 'medium',
                'accounts': [s['author'] for s in current['influential_sentiment']],
                'message': "High-influence accounts discussing ticker"
            })
        
        return {
            'ticker': ticker,
            'alerts': alerts,
            'current_sentiment': current.get('sentiment_label'),
            'sentiment_score': current.get('sentiment_score'),
            'should_monitor': len(alerts) > 0
        }
    
    def _analyze_tweet_sentiment(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of individual tweet"""
        
        text = tweet.get('text', '').lower()
        
        # Count pattern matches
        bullish_score = sum(1 for pattern in self.trading_patterns['bullish'] 
                           if re.search(pattern, text))
        bearish_score = sum(1 for pattern in self.trading_patterns['bearish'] 
                           if re.search(pattern, text))
        
        # Use advanced NLP for more nuanced analysis
        nlp_result = self.sentiment_analyzer.analyze_sentiment(tweet.get('text', ''))
        
        # Combine pattern matching with NLP
        if bullish_score > bearish_score or nlp_result.sentiment_score > 0.3:
            sentiment = 'bullish'
        elif bearish_score > bullish_score or nlp_result.sentiment_score < -0.3:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'confidence': abs(nlp_result.sentiment_score),
            'patterns_found': {
                'bullish': bullish_score,
                'bearish': bearish_score
            },
            'engagement': tweet.get('retweet_count', 0) + tweet.get('like_count', 0)
        }
    
    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.3:
            return 'Very Bullish'
        elif score > 0.1:
            return 'Bullish'
        elif score < -0.3:
            return 'Very Bearish'
        elif score < -0.1:
            return 'Bearish'
        else:
            return 'Neutral'
    
    def _extract_trending_topics(self, tweets: List[Dict]) -> List[str]:
        """Extract trending topics from tweets"""
        topics = []
        
        # Extract hashtags and common phrases
        hashtags = {}
        for tweet in tweets:
            text = tweet.get('text', '')
            for tag in re.findall(r'#\w+', text):
                hashtags[tag] = hashtags.get(tag, 0) + 1
        
        # Return top trending
        return [tag for tag, count in sorted(hashtags.items(), 
                key=lambda x: x[1], reverse=True)[:5]]
    
    def _identify_risk_indicators(self, sentiment_results: List[Dict], 
                                tweets: List[Dict]) -> List[str]:
        """Identify potential risk indicators from sentiment"""
        risks = []
        
        # Check for extreme sentiment
        if len(sentiment_results) > 0:
            bullish_pct = sum(1 for s in sentiment_results 
                            if s['sentiment'] == 'bullish') / len(sentiment_results)
            if bullish_pct > 0.9:
                risks.append("Extreme bullish sentiment (potential top)")
            elif bullish_pct < 0.1:
                risks.append("Extreme bearish sentiment (potential bottom)")
        
        # Check for pump patterns
        pump_keywords = ['squeeze', 'moon', 'pump', '1000x']
        pump_count = sum(1 for tweet in tweets 
                        if any(keyword in tweet.get('text', '').lower() 
                              for keyword in pump_keywords))
        if pump_count > len(tweets) * 0.3:
            risks.append("High pump-related content")
        
        return risks
    
    async def _search_tweets(self, query: str, timeframe: str) -> List[Dict]:
        """Search tweets (placeholder - would use actual X API)"""
        # This is a placeholder. In production, you would:
        # 1. Use X API v2 with OAuth 2.0
        # 2. Search tweets with the query
        # 3. Filter by timeframe
        # 4. Return structured tweet data
        
        # Simulated response structure
        return [
            {
                'id': '1234567890',
                'text': f'{query} looking bullish! 🚀 Breaking out of resistance',
                'author': 'trader123',
                'created_at': datetime.now() - timedelta(hours=1),
                'retweet_count': 45,
                'like_count': 123,
                'reply_count': 12
            },
            {
                'id': '1234567891',
                'text': f'Bought more {query} on this dip. Long term hold 💎🙌',
                'author': 'investor456',
                'created_at': datetime.now() - timedelta(hours=2),
                'retweet_count': 23,
                'like_count': 67,
                'reply_count': 5
            }
            # In reality, this would return 100s of tweets
        ]


# Initialize server
server = Server("x-sentiment-analyzer")
analyzer = XSentimentAnalyzer()

# Define tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="analyze_ticker_sentiment",
            description="Analyze X (Twitter) sentiment for a specific stock or crypto ticker",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock or crypto ticker symbol (e.g., AAPL, BTC)"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe for analysis (1h, 4h, 24h, 7d)",
                        "default": "24h"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="compare_tickers_sentiment",
            description="Compare X sentiment across multiple tickers",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tickers to compare"
                    }
                },
                "required": ["tickers"]
            }
        ),
        Tool(
            name="sentiment_alerts",
            description="Check for significant sentiment shifts and alerts",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Ticker to monitor"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="trending_financial_topics",
            description="Get trending financial topics and tickers on X",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category to filter (stocks, crypto, forex, all)",
                        "default": "all"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    await analyzer.setup()
    
    try:
        if name == "analyze_ticker_sentiment":
            ticker = arguments["ticker"].upper()
            timeframe = arguments.get("timeframe", "24h")
            result = await analyzer.analyze_ticker_sentiment(ticker, timeframe)
            
        elif name == "compare_tickers_sentiment":
            tickers = [t.upper() for t in arguments["tickers"]]
            result = await analyzer.analyze_multiple_tickers(tickers)
            
        elif name == "sentiment_alerts":
            ticker = arguments["ticker"].upper()
            result = await analyzer.track_sentiment_alerts(ticker)
            
        elif name == "trending_financial_topics":
            # Placeholder for trending topics
            result = {
                'trending_tickers': ['NVDA', 'TSLA', 'BTC', 'SPY', 'AAPL'],
                'trending_topics': ['#earnings', '#Fed', '#AI', '#bitcoin', '#options'],
                'hot_discussions': [
                    {'ticker': 'NVDA', 'topic': 'AI chip demand', 'sentiment': 'bullish'},
                    {'ticker': 'TSLA', 'topic': 'Delivery numbers', 'sentiment': 'mixed'},
                    {'ticker': 'BTC', 'topic': 'ETF flows', 'sentiment': 'bullish'}
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
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
                server_name="x-sentiment-analyzer",
                server_version="1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())