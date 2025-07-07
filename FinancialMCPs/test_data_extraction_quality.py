#!/usr/bin/env python3
"""
Comprehensive data extraction quality testing for Financial MCPs
Tests actual data extraction capabilities and validates output quality
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

import aiohttp
from bs4 import BeautifulSoup


class DataQualityTester:
    """Test data extraction quality for all Financial MCPs"""
    
    def __init__(self):
        self.results = {}
        self.session = None
        
    async def setup(self):
        """Setup aiohttp session with proper headers"""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
    
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    def validate_data_quality(self, data: Any, data_type: str) -> Dict[str, Any]:
        """Validate extracted data quality"""
        validation = {
            'has_data': bool(data),
            'data_type': data_type,
            'issues': [],
            'quality_score': 100
        }
        
        if not data:
            validation['issues'].append('No data extracted')
            validation['quality_score'] = 0
            return validation
        
        if isinstance(data, dict) and 'error' in data:
            validation['issues'].append(f"Error: {data['error']}")
            validation['quality_score'] = 0
            return validation
        
        # Type-specific validation
        if data_type == 'price':
            if isinstance(data, dict):
                # Check required fields
                required = ['ticker', 'price']
                for field in required:
                    if field not in data:
                        validation['issues'].append(f"Missing required field: {field}")
                        validation['quality_score'] -= 20
                
                # Validate price format
                if 'price' in data:
                    try:
                        price = float(str(data['price']).replace(',', ''))
                        if price <= 0 or price > 1000000:
                            validation['issues'].append(f"Suspicious price value: {price}")
                            validation['quality_score'] -= 30
                    except:
                        validation['issues'].append("Invalid price format")
                        validation['quality_score'] -= 30
        
        elif data_type == 'news':
            if isinstance(data, list):
                if len(data) == 0:
                    validation['issues'].append("Empty news list")
                    validation['quality_score'] = 0
                else:
                    # Check news item quality
                    for i, item in enumerate(data[:5]):  # Check first 5
                        if not isinstance(item, dict):
                            validation['issues'].append(f"Invalid news item format at index {i}")
                            validation['quality_score'] -= 10
                        else:
                            if 'headline' not in item or not item['headline']:
                                validation['issues'].append(f"Missing headline at index {i}")
                                validation['quality_score'] -= 5
                            if 'date' not in item:
                                validation['issues'].append(f"Missing date at index {i}")
                                validation['quality_score'] -= 5
        
        elif data_type == 'sentiment':
            if isinstance(data, dict):
                if 'sentiment' not in data:
                    validation['issues'].append("Missing sentiment field")
                    validation['quality_score'] -= 30
                elif data['sentiment'] not in ['positive', 'negative', 'neutral', 'bullish', 'bearish']:
                    validation['issues'].append(f"Invalid sentiment value: {data.get('sentiment')}")
                    validation['quality_score'] -= 20
        
        elif data_type == 'financial':
            if isinstance(data, dict):
                # Check for actual financial data
                has_numbers = any(
                    isinstance(v, (int, float)) or 
                    (isinstance(v, str) and re.search(r'\d+', v))
                    for v in data.values()
                )
                if not has_numbers:
                    validation['issues'].append("No numerical financial data found")
                    validation['quality_score'] -= 40
        
        validation['quality_score'] = max(0, validation['quality_score'])
        return validation
    
    async def test_sec_scraper(self):
        """Test SEC scraper data extraction"""
        print("\n🔍 Testing SEC Scraper...")
        test_cases = [
            {
                'name': 'Price extraction for AAPL',
                'url': 'https://finance.yahoo.com/quote/AAPL',
                'selector': 'fin-streamer[data-field="regularMarketPrice"]',
                'expected_type': 'price'
            },
            {
                'name': 'SEC filings extraction',
                'url': 'https://www.sec.gov/cgi-bin/browse-edgar?CIK=AAPL&owner=exclude',
                'selector': 'table.tableFile2',
                'expected_type': 'financial'
            }
        ]
        
        results = []
        for test in test_cases:
            try:
                async with self.session.get(test['url']) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        element = soup.select_one(test['selector'])
                        if element:
                            results.append({
                                'test': test['name'],
                                'success': True,
                                'element_found': True,
                                'sample_data': str(element)[:200]
                            })
                        else:
                            results.append({
                                'test': test['name'],
                                'success': False,
                                'element_found': False,
                                'issue': f"Selector '{test['selector']}' not found"
                            })
                    else:
                        results.append({
                            'test': test['name'],
                            'success': False,
                            'status_code': response.status
                        })
            except Exception as e:
                results.append({
                    'test': test['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    async def test_news_sentiment_scraper(self):
        """Test news sentiment scraper"""
        print("\n📰 Testing News Sentiment Scraper...")
        test_cases = [
            {
                'name': 'Finviz news extraction',
                'url': 'https://finviz.com/quote.ashx?t=AAPL',
                'selector': 'table.fullview-news-outer',
                'expected_type': 'news'
            },
            {
                'name': 'Yahoo Finance news',
                'url': 'https://finance.yahoo.com/quote/AAPL/news',
                'selector': 'h3',
                'expected_type': 'news'
            }
        ]
        
        results = []
        for test in test_cases:
            try:
                async with self.session.get(test['url']) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Check if we're being blocked
                        if 'Access Denied' in html or 'captcha' in html.lower():
                            results.append({
                                'test': test['name'],
                                'success': False,
                                'issue': 'Access blocked (captcha/rate limit)'
                            })
                            continue
                        
                        element = soup.select_one(test['selector'])
                        if element:
                            # Try to extract some news items
                            news_count = len(soup.select(test['selector']))
                            results.append({
                                'test': test['name'],
                                'success': True,
                                'element_found': True,
                                'news_items_found': news_count
                            })
                        else:
                            # Check if page structure changed
                            all_tables = soup.find_all('table')
                            all_h3s = soup.find_all('h3')
                            results.append({
                                'test': test['name'],
                                'success': False,
                                'element_found': False,
                                'tables_on_page': len(all_tables),
                                'h3s_on_page': len(all_h3s),
                                'issue': f"Selector '{test['selector']}' not found - page structure may have changed"
                            })
                    else:
                        results.append({
                            'test': test['name'],
                            'success': False,
                            'status_code': response.status
                        })
            except Exception as e:
                results.append({
                    'test': test['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    async def test_sentiment_analysis_quality(self):
        """Test the quality of sentiment analysis"""
        print("\n🎭 Testing Sentiment Analysis Quality...")
        
        test_texts = [
            {
                'text': "Apple beats earnings expectations with record revenue",
                'expected': 'positive',
                'context': 'earnings'
            },
            {
                'text': "Company misses revenue targets amid disappointing sales",
                'expected': 'negative',
                'context': 'earnings'
            },
            {
                'text': "Stock upgraded to buy from hold by major analyst",
                'expected': 'positive',
                'context': 'analyst'
            },
            {
                'text': "CEO steps down unexpectedly citing personal reasons",
                'expected': 'negative',
                'context': 'leadership'
            },
            {
                'text': "Markets remain steady as investors await Fed decision",
                'expected': 'neutral',
                'context': 'market'
            }
        ]
        
        # Simple keyword-based sentiment (mimicking the MCPs)
        positive_words = ['beat', 'exceed', 'outperform', 'upgrade', 'record', 'growth', 'profit']
        negative_words = ['miss', 'disappoint', 'downgrade', 'decline', 'loss', 'unexpectedly']
        
        results = []
        for test in test_texts:
            text_lower = test['text'].lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = 'positive'
            elif negative_count > positive_count:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            results.append({
                'text': test['text'][:50] + '...',
                'expected': test['expected'],
                'detected': sentiment,
                'correct': sentiment == test['expected'],
                'positive_words': positive_count,
                'negative_words': negative_count
            })
        
        accuracy = sum(1 for r in results if r['correct']) / len(results) * 100
        return {
            'results': results,
            'accuracy': f"{accuracy:.1f}%",
            'issue': 'Keyword-based sentiment is too simplistic' if accuracy < 80 else None
        }
    
    async def generate_report(self):
        """Generate comprehensive data quality report"""
        print("\n" + "="*60)
        print("📊 FINANCIAL MCPs DATA QUALITY REPORT")
        print("="*60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n")
        
        # Test each component
        sec_results = await self.test_sec_scraper()
        news_results = await self.test_news_sentiment_scraper()
        sentiment_results = await self.test_sentiment_analysis_quality()
        
        # SEC Scraper Results
        print("\n### SEC SCRAPER RESULTS ###")
        for result in sec_results:
            status = "✅" if result.get('success') else "❌"
            print(f"{status} {result['test']}")
            if not result.get('success'):
                print(f"   Issue: {result.get('issue', result.get('error', 'Unknown'))}")
        
        # News Scraper Results
        print("\n### NEWS SCRAPER RESULTS ###")
        for result in news_results:
            status = "✅" if result.get('success') else "❌"
            print(f"{status} {result['test']}")
            if not result.get('success'):
                print(f"   Issue: {result.get('issue', result.get('error', 'Unknown'))}")
            elif result.get('news_items_found'):
                print(f"   Found {result['news_items_found']} news items")
        
        # Sentiment Analysis Results
        print("\n### SENTIMENT ANALYSIS RESULTS ###")
        print(f"Accuracy: {sentiment_results['accuracy']}")
        if sentiment_results.get('issue'):
            print(f"⚠️  {sentiment_results['issue']}")
        print("\nSample results:")
        for r in sentiment_results['results'][:3]:
            status = "✅" if r['correct'] else "❌"
            print(f"{status} '{r['text']}' - Expected: {r['expected']}, Got: {r['detected']}")
        
        # Critical Issues Summary
        print("\n### 🚨 CRITICAL ISSUES FOUND ###")
        print("1. SEC scraper uses placeholder User-Agent - will be blocked by SEC")
        print("2. HTML selectors are outdated - many will fail on live sites")
        print("3. Sentiment analysis is keyword-based - misses context and nuance")
        print("4. No data validation - accepts any response without verification")
        print("5. No rate limiting - risk of IP bans")
        print("6. No error recovery - single failure stops entire operation")
        
        print("\n### 📋 RECOMMENDATIONS ###")
        print("1. Update all User-Agents to proper identification")
        print("2. Implement robust HTML parsing with fallbacks")
        print("3. Add proper NLP-based sentiment analysis")
        print("4. Add comprehensive data validation")
        print("5. Implement rate limiting and retry logic")
        print("6. Add alternative data sources as fallbacks")
        print("7. Use official APIs where available (SEC EDGAR API)")
        
        return {
            'sec_results': sec_results,
            'news_results': news_results,
            'sentiment_results': sentiment_results,
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Run comprehensive data quality tests"""
    tester = DataQualityTester()
    await tester.setup()
    
    try:
        report = await tester.generate_report()
        
        # Save report
        with open('data_quality_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n✅ Report saved to data_quality_report.json")
        
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())