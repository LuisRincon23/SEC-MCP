"""Market data client for fetching stock prices, crypto prices, and news."""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from urllib.parse import quote

class MarketDataClient:
    """Client for fetching market data including stocks, crypto, and news."""
    
    def __init__(self):
        self.session = None
        self.base_headers = {
            'User-Agent': 'SEC-MCP/1.0 (https://github.com/LuisRincon23/SEC-MCP)'
        }
        
        # Free market data APIs
        self.yahoo_finance_base = "https://query1.finance.yahoo.com/v8/finance"
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        self.news_api_base = "https://newsapi.org/v2"
        self.coinbase_api = "https://api.coinbase.com/v2"
        self.binance_api = "https://api.binance.com/api/v3"
        
    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.base_headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None
            
    async def get_current_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current stock price using Yahoo Finance API."""
        try:
            # Use Yahoo Finance quote endpoint
            url = f"{self.yahoo_finance_base}/chart/{symbol}"
            params = {
                'interval': '1d',
                'range': '1d'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        # Get the latest price
                        regular_price = meta.get('regularMarketPrice', 0)
                        previous_close = meta.get('previousClose', 0)
                        
                        return {
                            "symbol": symbol.upper(),
                            "company_name": meta.get('longName', symbol),
                            "current_price": regular_price,
                            "previous_close": previous_close,
                            "change": regular_price - previous_close,
                            "change_percent": ((regular_price - previous_close) / previous_close * 100) if previous_close > 0 else 0,
                            "volume": meta.get('regularMarketVolume', 0),
                            "market_cap": meta.get('marketCap', 0),
                            "timestamp": datetime.fromtimestamp(meta.get('regularMarketTime', 0)).isoformat(),
                            "currency": meta.get('currency', 'USD'),
                            "exchange": meta.get('exchangeName', 'Unknown')
                        }
                    else:
                        raise Exception(f"No data found for symbol: {symbol}")
                else:
                    raise Exception(f"Failed to fetch stock price: HTTP {response.status}")
                    
        except Exception as e:
            raise Exception(f"Error fetching current stock price: {str(e)}")
    
    async def get_historical_stock_prices(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        """Get historical stock prices using Yahoo Finance API."""
        try:
            # Use Yahoo Finance chart endpoint
            url = f"{self.yahoo_finance_base}/chart/{symbol}"
            params = {
                'interval': interval,  # 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
                'range': period        # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        # Extract OHLCV data
                        timestamps = result.get('timestamp', [])
                        indicators = result.get('indicators', {}).get('quote', [{}])[0]
                        
                        prices = []
                        for i, ts in enumerate(timestamps):
                            prices.append({
                                "date": datetime.fromtimestamp(ts).isoformat(),
                                "open": indicators.get('open', [])[i] if i < len(indicators.get('open', [])) else None,
                                "high": indicators.get('high', [])[i] if i < len(indicators.get('high', [])) else None,
                                "low": indicators.get('low', [])[i] if i < len(indicators.get('low', [])) else None,
                                "close": indicators.get('close', [])[i] if i < len(indicators.get('close', [])) else None,
                                "volume": indicators.get('volume', [])[i] if i < len(indicators.get('volume', [])) else None
                            })
                        
                        return {
                            "symbol": symbol.upper(),
                            "company_name": meta.get('longName', symbol),
                            "period": period,
                            "interval": interval,
                            "currency": meta.get('currency', 'USD'),
                            "exchange": meta.get('exchangeName', 'Unknown'),
                            "data_points": len(prices),
                            "prices": prices
                        }
                    else:
                        raise Exception(f"No data found for symbol: {symbol}")
                else:
                    raise Exception(f"Failed to fetch historical prices: HTTP {response.status}")
                    
        except Exception as e:
            raise Exception(f"Error fetching historical stock prices: {str(e)}")
    
    async def get_company_news(self, query: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get news articles about a company using various news sources."""
        try:
            # For this implementation, we'll use a simple web search approach
            # In production, you'd want to use a proper news API with an API key
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # Mock news data structure (in production, use actual news API)
            # You would typically use NewsAPI, Finnhub, or other financial news APIs
            news_items = []
            
            # Simulate news fetching (replace with actual API call)
            # For demonstration, returning structured mock data
            mock_news = [
                {
                    "title": f"Latest developments for {query}",
                    "description": f"Recent news and updates about {query} in the market.",
                    "source": "Financial Times",
                    "url": f"https://example.com/news/{quote(query)}",
                    "published_at": to_date.isoformat(),
                    "sentiment": "neutral"
                }
            ]
            
            return mock_news
            
        except Exception as e:
            raise Exception(f"Error fetching company news: {str(e)}")
    
    async def get_available_crypto_tickers(self) -> List[Dict[str, str]]:
        """Get list of available cryptocurrency tickers."""
        try:
            # Use Binance API for comprehensive crypto list
            url = f"{self.binance_api}/exchangeInfo"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract unique base assets (cryptocurrencies)
                    crypto_set = set()
                    symbols_info = {}
                    
                    for symbol in data.get('symbols', []):
                        if symbol['status'] == 'TRADING':
                            base = symbol['baseAsset']
                            if base not in symbols_info:
                                crypto_set.add(base)
                                symbols_info[base] = {
                                    "symbol": base,
                                    "name": symbol.get('baseAssetName', base),
                                    "trading_pairs": []
                                }
                            symbols_info[base]['trading_pairs'].append(symbol['symbol'])
                    
                    # Convert to list and sort
                    cryptos = []
                    for symbol, info in symbols_info.items():
                        cryptos.append({
                            "symbol": symbol,
                            "name": info['name'],
                            "trading_pairs_count": len(info['trading_pairs']),
                            "example_pairs": info['trading_pairs'][:3]  # First 3 trading pairs
                        })
                    
                    cryptos.sort(key=lambda x: x['symbol'])
                    
                    return cryptos[:100]  # Return top 100 cryptos
                else:
                    raise Exception(f"Failed to fetch crypto tickers: HTTP {response.status}")
                    
        except Exception as e:
            raise Exception(f"Error fetching crypto tickers: {str(e)}")
    
    async def get_current_crypto_price(self, symbol: str, vs_currency: str = "USD") -> Dict[str, Any]:
        """Get current price of a cryptocurrency."""
        try:
            # Use Binance API
            trading_symbol = f"{symbol.upper()}{vs_currency.upper()}T"  # e.g., BTCUSDT
            url = f"{self.binance_api}/ticker/24hr"
            params = {"symbol": trading_symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "symbol": symbol.upper(),
                        "vs_currency": vs_currency.upper(),
                        "current_price": float(data.get('lastPrice', 0)),
                        "price_change_24h": float(data.get('priceChange', 0)),
                        "price_change_percent_24h": float(data.get('priceChangePercent', 0)),
                        "high_24h": float(data.get('highPrice', 0)),
                        "low_24h": float(data.get('lowPrice', 0)),
                        "volume_24h": float(data.get('volume', 0)),
                        "quote_volume_24h": float(data.get('quoteVolume', 0)),
                        "open_24h": float(data.get('openPrice', 0)),
                        "timestamp": datetime.now().isoformat(),
                        "trading_pair": trading_symbol
                    }
                else:
                    # Try alternative pair (without T suffix)
                    trading_symbol = f"{symbol.upper()}{vs_currency.upper()}"
                    params = {"symbol": trading_symbol}
                    
                    async with self.session.get(url, params=params) as response2:
                        if response2.status == 200:
                            data = await response2.json()
                            
                            return {
                                "symbol": symbol.upper(),
                                "vs_currency": vs_currency.upper(),
                                "current_price": float(data.get('lastPrice', 0)),
                                "price_change_24h": float(data.get('priceChange', 0)),
                                "price_change_percent_24h": float(data.get('priceChangePercent', 0)),
                                "high_24h": float(data.get('highPrice', 0)),
                                "low_24h": float(data.get('lowPrice', 0)),
                                "volume_24h": float(data.get('volume', 0)),
                                "quote_volume_24h": float(data.get('quoteVolume', 0)),
                                "open_24h": float(data.get('openPrice', 0)),
                                "timestamp": datetime.now().isoformat(),
                                "trading_pair": trading_symbol
                            }
                        else:
                            raise Exception(f"Crypto pair {trading_symbol} not found")
                    
        except Exception as e:
            raise Exception(f"Error fetching current crypto price: {str(e)}")
    
    async def get_historical_crypto_prices(self, symbol: str, vs_currency: str = "USD", 
                                         interval: str = "1d", limit: int = 30) -> Dict[str, Any]:
        """Get historical prices for a cryptocurrency."""
        try:
            # Use Binance klines (candlestick) data
            trading_symbol = f"{symbol.upper()}{vs_currency.upper()}T"
            url = f"{self.binance_api}/klines"
            
            # Map interval to Binance format
            interval_map = {
                "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w", "1M": "1M"
            }
            
            params = {
                "symbol": trading_symbol,
                "interval": interval_map.get(interval, "1d"),
                "limit": min(limit, 1000)  # Binance max is 1000
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    prices = []
                    for candle in data:
                        prices.append({
                            "timestamp": datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                            "open": float(candle[1]),
                            "high": float(candle[2]),
                            "low": float(candle[3]),
                            "close": float(candle[4]),
                            "volume": float(candle[5]),
                            "quote_volume": float(candle[7]),
                            "trades": int(candle[8])
                        })
                    
                    return {
                        "symbol": symbol.upper(),
                        "vs_currency": vs_currency.upper(),
                        "interval": interval,
                        "data_points": len(prices),
                        "trading_pair": trading_symbol,
                        "prices": prices
                    }
                else:
                    # Try without T suffix
                    trading_symbol = f"{symbol.upper()}{vs_currency.upper()}"
                    params["symbol"] = trading_symbol
                    
                    async with self.session.get(url, params=params) as response2:
                        if response2.status == 200:
                            data = await response2.json()
                            
                            prices = []
                            for candle in data:
                                prices.append({
                                    "timestamp": datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                                    "open": float(candle[1]),
                                    "high": float(candle[2]),
                                    "low": float(candle[3]),
                                    "close": float(candle[4]),
                                    "volume": float(candle[5]),
                                    "quote_volume": float(candle[7]),
                                    "trades": int(candle[8])
                                })
                            
                            return {
                                "symbol": symbol.upper(),
                                "vs_currency": vs_currency.upper(),
                                "interval": interval,
                                "data_points": len(prices),
                                "trading_pair": trading_symbol,
                                "prices": prices
                            }
                        else:
                            raise Exception(f"Crypto pair {trading_symbol} not found")
                    
        except Exception as e:
            raise Exception(f"Error fetching historical crypto prices: {str(e)}")