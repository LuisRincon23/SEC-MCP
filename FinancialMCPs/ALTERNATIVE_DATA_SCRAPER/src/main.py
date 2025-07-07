import time
#!/usr/bin/env python

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urljoin, quote, urlparse

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



class AlternativeDataScraper:
    """Scraper for alternative data sources: job postings, web traffic, app rankings, patents, etc."""
    
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
    
    async def scrape_indeed_jobs(self, company: str) -> Dict[str, Any]:
        """Scrape job postings from Indeed to gauge hiring trends"""
        query = quote(f'company:"{company}"')
        url = f"https://www.indeed.com/jobs?q={query}&sort=date"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                job_data = {
                    'company': company,
                    'source': 'indeed',
                    'total_jobs': 0,
                    'recent_postings': [],
                    'job_categories': {},
                    'locations': {},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Extract job count
                count_elem = soup.find('div', {'id': 'searchCountPages'})
                if count_elem:
                    count_text = count_elem.text
                    match = re.search(r'of\s+([\d,]+)\s+jobs', count_text)
                    if match:
                        job_data['total_jobs'] = int(match.group(1).replace(',', ''))
                
                # Extract job listings
                job_cards = soup.find_all('div', {'class': re.compile('job_seen_beacon|jobsearch-SerpJobCard')})
                
                for card in job_cards[:20]:  # Get top 20 recent jobs
                    title_elem = card.find('h2', {'class': 'jobTitle'}) or card.find('a', {'data-testid': 'job-title'})
                    location_elem = card.find('div', {'data-testid': 'job-location'}) or card.find('span', {'class': 'locationsContainer'})
                    date_elem = card.find('span', {'class': 'date'})
                    
                    if title_elem:
                        job_title = title_elem.text.strip()
                        location = location_elem.text.strip() if location_elem else 'Unknown'
                        
                        job_data['recent_postings'].append({
                            'title': job_title,
                            'location': location,
                            'posted': date_elem.text.strip() if date_elem else 'Unknown'
                        })
                        
                        # Categorize jobs
                        job_category = self._categorize_job(job_title)
                        job_data['job_categories'][job_category] = job_data['job_categories'].get(job_category, 0) + 1
                        
                        # Track locations
                        job_data['locations'][location] = job_data['locations'].get(location, 0) + 1
                
                return job_data
        
        except Exception as e:
            return {'error': f"Failed to scrape Indeed jobs: {str(e)}"}
    
    def _categorize_job(self, job_title: str) -> str:
        """Categorize job based on title keywords"""
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ['engineer', 'developer', 'programmer', 'software']):
            return 'Engineering'
        elif any(word in title_lower for word in ['sales', 'account', 'business development']):
            return 'Sales'
        elif any(word in title_lower for word in ['marketing', 'brand', 'content', 'social media']):
            return 'Marketing'
        elif any(word in title_lower for word in ['data', 'analyst', 'scientist', 'analytics']):
            return 'Data/Analytics'
        elif any(word in title_lower for word in ['product', 'manager', 'pm']):
            return 'Product'
        elif any(word in title_lower for word in ['finance', 'accounting', 'controller']):
            return 'Finance'
        elif any(word in title_lower for word in ['hr', 'human resources', 'recruiting', 'talent']):
            return 'HR/Recruiting'
        elif any(word in title_lower for word in ['operations', 'supply chain', 'logistics']):
            return 'Operations'
        else:
            return 'Other'
    
    async def scrape_similarweb_traffic(self, domain: str) -> Dict[str, Any]:
        """Scrape web traffic estimates from SimilarWeb"""
        clean_domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        url = f"https://www.similarweb.com/website/{clean_domain}/"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                traffic_data = {
                    'domain': clean_domain,
                    'source': 'similarweb',
                    'metrics': {},
                    'traffic_sources': {},
                    'top_keywords': [],
                    'competitor_sites': []
                }
                
                # Extract traffic metrics
                metric_elements = soup.find_all('div', {'class': re.compile('engagement-list__item')})
                for elem in metric_elements:
                    title = elem.find('p', {'class': 'engagement-list__item-title'})
                    value = elem.find('p', {'class': 'engagement-list__item-value'})
                    
                    if title and value:
                        metric_name = title.text.strip()
                        metric_value = value.text.strip()
                        traffic_data['metrics'][metric_name] = metric_value
                
                # Extract traffic sources
                sources_section = soup.find('div', {'data-test': 'traffic-sources'})
                if sources_section:
                    source_items = sources_section.find_all('div', {'class': 'wa-traffic-sources__item'})
                    for item in source_items:
                        source_name = item.find('a', {'class': 'wa-traffic-sources__title'})
                        source_value = item.find('span', {'class': 'wa-traffic-sources__value'})
                        
                        if source_name and source_value:
                            traffic_data['traffic_sources'][source_name.text.strip()] = source_value.text.strip()
                
                return traffic_data
        
        except Exception as e:
            return {'error': f"Failed to scrape SimilarWeb data: {str(e)}"}
    
    async def scrape_app_rankings(self, app_name: str, company: str) -> Dict[str, Any]:
        """Scrape app store rankings and reviews"""
        # Using AppAnnie/data.ai style scraping (simplified)
        search_query = quote(app_name)
        
        app_data = {
            'app_name': app_name,
            'company': company,
            'source': 'app_stores',
            'rankings': {},
            'ratings': {},
            'review_sentiment': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Scrape from AlternativeTo for app alternatives and ratings
        alternative_url = f"https://alternativeto.net/software/{search_query.replace(' ', '-').lower()}/"
        
        try:
            async with self.session.get(alternative_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract ratings
                    rating_elem = soup.find('div', {'class': 'rating'})
                    if rating_elem:
                        app_data['ratings']['overall'] = rating_elem.text.strip()
                    
                    # Extract alternatives (competitors)
                    alternatives = []
                    alt_items = soup.find_all('div', {'class': 'alternative'})[:10]
                    for item in alt_items:
                        name = item.find('h3')
                        if name:
                            alternatives.append(name.text.strip())
                    
                    app_data['competitors'] = alternatives
        
        except Exception as e:
            app_data['error'] = f"Failed to scrape app data: {str(e)}"
        
        return app_data
    
    async def scrape_patent_activity(self, company: str) -> Dict[str, Any]:
        """Scrape patent filing activity from Google Patents"""
        query = quote(f'assignee:"{company}"')
        url = f"https://patents.google.com/?assignee={query}&sort=new"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                patent_data = {
                    'company': company,
                    'source': 'google_patents',
                    'recent_patents': [],
                    'technology_areas': {},
                    'filing_trend': {},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Extract patent listings
                patent_items = soup.find_all('search-result-item')[:20]
                
                for item in patent_items:
                    title_elem = item.find('h3', {'class': 'result-title'})
                    date_elem = item.find('span', {'class': 'result-date'})
                    abstract_elem = item.find('span', {'class': 'result-abstract'})
                    
                    if title_elem:
                        patent_info = {
                            'title': title_elem.text.strip(),
                            'date': date_elem.text.strip() if date_elem else '',
                            'abstract': abstract_elem.text.strip()[:200] if abstract_elem else ''
                        }
                        
                        patent_data['recent_patents'].append(patent_info)
                        
                        # Categorize by technology area
                        tech_area = self._categorize_patent(patent_info['title'], patent_info['abstract'])
                        patent_data['technology_areas'][tech_area] = patent_data['technology_areas'].get(tech_area, 0) + 1
                
                return patent_data
        
        except Exception as e:
            return {'error': f"Failed to scrape patent data: {str(e)}"}
    
    def _categorize_patent(self, title: str, abstract: str) -> str:
        """Categorize patent based on title and abstract"""
        text = (title + ' ' + abstract).lower()
        
        if any(word in text for word in ['ai', 'artificial intelligence', 'machine learning', 'neural']):
            return 'AI/ML'
        elif any(word in text for word in ['blockchain', 'cryptocurrency', 'distributed ledger']):
            return 'Blockchain'
        elif any(word in text for word in ['cloud', 'server', 'datacenter', 'infrastructure']):
            return 'Cloud/Infrastructure'
        elif any(word in text for word in ['mobile', 'smartphone', 'app', 'ios', 'android']):
            return 'Mobile'
        elif any(word in text for word in ['security', 'encryption', 'authentication', 'privacy']):
            return 'Security'
        elif any(word in text for word in ['iot', 'sensor', 'connected device', 'smart']):
            return 'IoT'
        elif any(word in text for word in ['biotech', 'pharma', 'medical', 'health']):
            return 'Healthcare'
        else:
            return 'Other'
    
    async def scrape_glassdoor_sentiment(self, company: str) -> Dict[str, Any]:
        """Scrape employee sentiment from Glassdoor"""
        search_query = quote(company)
        url = f"https://www.glassdoor.com/Search/results.htm?keyword={search_query}"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                sentiment_data = {
                    'company': company,
                    'source': 'glassdoor',
                    'ratings': {},
                    'pros_cons': {'pros': [], 'cons': []},
                    'review_highlights': [],
                    'employee_sentiment': 'neutral'
                }
                
                # Extract overall rating
                rating_elem = soup.find('div', {'class': 'v2__EIReviewsRatingsStylesV2__ratingNum'})
                if rating_elem:
                    sentiment_data['ratings']['overall'] = rating_elem.text.strip()
                    
                    # Determine sentiment based on rating
                    try:
                        rating_value = float(rating_elem.text.strip())
                        if rating_value >= 4.0:
                            sentiment_data['employee_sentiment'] = 'positive'
                        elif rating_value <= 3.0:
                            sentiment_data['employee_sentiment'] = 'negative'
                    except:
                        pass
                
                # Extract review snippets
                review_elements = soup.find_all('div', {'class': 'review'})[:5]
                for review in review_elements:
                    pros = review.find('span', {'data-test': 'pros'})
                    cons = review.find('span', {'data-test': 'cons'})
                    
                    if pros:
                        sentiment_data['pros_cons']['pros'].append(pros.text.strip()[:200])
                    if cons:
                        sentiment_data['pros_cons']['cons'].append(cons.text.strip()[:200])
                
                return sentiment_data
        
        except Exception as e:
            return {'error': f"Failed to scrape Glassdoor data: {str(e)}"}
    
    async def scrape_reddit_sentiment(self, company: str, ticker: str = None) -> Dict[str, Any]:
        """Scrape Reddit discussions for sentiment analysis"""
        search_term = ticker if ticker else company
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
        
        reddit_data = {
            'company': company,
            'ticker': ticker,
            'source': 'reddit',
            'mentions': [],
            'sentiment_summary': {},
            'trending': False,
            'timestamp': datetime.now().isoformat()
        }
        
        for subreddit in subreddits:
            url = f"https://www.reddit.com/r/{subreddit}/search.json?q={quote(search_term)}&sort=new&limit=25"
            
            try:
                async with self.session.get(url, headers={'User-Agent': 'Alternative Data Scraper 1.0'}) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for post in data['data']['children']:
                            post_data = post['data']
                            
                            reddit_data['mentions'].append({
                                'title': post_data['title'],
                                'score': post_data['score'],
                                'num_comments': post_data['num_comments'],
                                'created': datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                                'subreddit': post_data['subreddit'],
                                'url': f"https://reddit.com{post_data['permalink']}"
                            })
                            
                            # Simple sentiment based on title
                            sentiment = self._analyze_reddit_sentiment(post_data['title'])
                            reddit_data['sentiment_summary'][sentiment] = reddit_data['sentiment_summary'].get(sentiment, 0) + 1
            
            except Exception as e:
                continue
        
        # Check if trending
        if len(reddit_data['mentions']) > 10:
            reddit_data['trending'] = True
        
        return reddit_data
    
    def _analyze_reddit_sentiment(self, text: str) -> str:
        """Simple sentiment analysis for Reddit posts"""
        text_lower = text.lower()
        
        bullish_terms = ['moon', 'rocket', 'buy', 'calls', 'yolo', 'gains', 'tendies', 'bullish', 'long']
        bearish_terms = ['puts', 'short', 'crash', 'dump', 'bearish', 'sell', 'loss', 'bag']
        
        bullish_score = sum(1 for term in bullish_terms if term in text_lower)
        bearish_score = sum(1 for term in bearish_terms if term in text_lower)
        
        if bullish_score > bearish_score:
            return 'bullish'
        elif bearish_score > bullish_score:
            return 'bearish'
        else:
            return 'neutral'
    
    async def scrape_corporate_events(self, company: str) -> Dict[str, Any]:
        """Scrape corporate events, conferences, and presentations"""
        # Search for investor relations pages
        search_query = quote(f"{company} investor relations events")
        url = f"https://www.google.com/search?q={search_query}"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                events_data = {
                    'company': company,
                    'source': 'corporate_events',
                    'upcoming_events': [],
                    'recent_presentations': [],
                    'conference_participation': [],
                    'timestamp': datetime.now().isoformat()
                }
                
                # This is a simplified example - real implementation would
                # follow links to actual IR pages
                search_results = soup.find_all('div', {'class': 'g'})[:5]
                
                for result in search_results:
                    link = result.find('a')
                    title = result.find('h3')
                    
                    if link and title and 'investor' in title.text.lower():
                        events_data['recent_presentations'].append({
                            'title': title.text,
                            'url': link.get('href', ''),
                            'source': 'search_result'
                        })
                
                return events_data
        
        except Exception as e:
            return {'error': f"Failed to scrape corporate events: {str(e)}"}


# Initialize server
server = Server("alternative-data-scraper")
scraper = AlternativeDataScraper()

# Define tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="analyze_hiring_trends",
            description="Analyze company hiring trends through job postings",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "Company name to analyze"
                    }
                },
                "required": ["company"]
            }
        ),
        Tool(
            name="get_web_traffic_data",
            description="Get web traffic and engagement metrics for a domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain name (e.g., amazon.com)"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="track_patent_activity",
            description="Track patent filing activity and innovation trends",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "Company name"
                    }
                },
                "required": ["company"]
            }
        ),
        Tool(
            name="analyze_employee_sentiment",
            description="Analyze employee sentiment and company culture indicators",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "Company name"
                    }
                },
                "required": ["company"]
            }
        ),
        Tool(
            name="get_social_sentiment",
            description="Get social media sentiment from Reddit and other platforms",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "Company name"
                    },
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker (optional)"
                    }
                },
                "required": ["company"]
            }
        ),
        Tool(
            name="get_app_metrics",
            description="Get mobile app rankings and user engagement metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "App name"
                    },
                    "company": {
                        "type": "string",
                        "description": "Company that owns the app"
                    }
                },
                "required": ["app_name", "company"]
            }
        ),
        Tool(
            name="comprehensive_alternative_data",
            description="Get comprehensive alternative data analysis for a company",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "Company name"
                    },
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker (optional)"
                    },
                    "domain": {
                        "type": "string",
                        "description": "Company domain (optional)"
                    }
                },
                "required": ["company"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    await scraper.setup()
    
    try:
        if name == "analyze_hiring_trends":
            company = arguments["company"]
            job_data = await scraper.scrape_indeed_jobs(company)
            
            # Add trend analysis
            if not job_data.get('error'):
                total_jobs = job_data.get('total_jobs', 0)
                if total_jobs > 1000:
                    job_data['hiring_trend'] = 'aggressive expansion'
                elif total_jobs > 500:
                    job_data['hiring_trend'] = 'strong growth'
                elif total_jobs > 100:
                    job_data['hiring_trend'] = 'moderate growth'
                else:
                    job_data['hiring_trend'] = 'limited hiring'
            
            return [TextContent(
                type="text",
                text=json.dumps(job_data, indent=2)
            )]
        
        elif name == "get_web_traffic_data":
            domain = arguments["domain"]
            traffic_data = await scraper.scrape_similarweb_traffic(domain)
            
            return [TextContent(
                type="text",
                text=json.dumps(traffic_data, indent=2)
            )]
        
        elif name == "track_patent_activity":
            company = arguments["company"]
            patent_data = await scraper.scrape_patent_activity(company)
            
            return [TextContent(
                type="text",
                text=json.dumps(patent_data, indent=2)
            )]
        
        elif name == "analyze_employee_sentiment":
            company = arguments["company"]
            glassdoor_data = await scraper.scrape_glassdoor_sentiment(company)
            
            return [TextContent(
                type="text",
                text=json.dumps(glassdoor_data, indent=2)
            )]
        
        elif name == "get_social_sentiment":
            company = arguments["company"]
            ticker = arguments.get("ticker")
            reddit_data = await scraper.scrape_reddit_sentiment(company, ticker)
            
            return [TextContent(
                type="text",
                text=json.dumps(reddit_data, indent=2)
            )]
        
        elif name == "get_app_metrics":
            app_name = arguments["app_name"]
            company = arguments["company"]
            app_data = await scraper.scrape_app_rankings(app_name, company)
            
            return [TextContent(
                type="text",
                text=json.dumps(app_data, indent=2)
            )]
        
        elif name == "comprehensive_alternative_data":
            company = arguments["company"]
            ticker = arguments.get("ticker")
            domain = arguments.get("domain")
            
            # Gather all alternative data sources
            results = {
                'company': company,
                'ticker': ticker,
                'analysis_date': datetime.now().isoformat(),
                'data_points': {}
            }
            
            # Hiring trends
            job_data = await scraper.scrape_indeed_jobs(company)
            if not job_data.get('error'):
                results['data_points']['hiring'] = {
                    'total_openings': job_data.get('total_jobs', 0),
                    'trend': job_data.get('hiring_trend', 'unknown'),
                    'top_categories': list(job_data.get('job_categories', {}).keys())[:3]
                }
            
            # Web traffic (if domain provided)
            if domain:
                traffic_data = await scraper.scrape_similarweb_traffic(domain)
                if not traffic_data.get('error'):
                    results['data_points']['web_traffic'] = traffic_data.get('metrics', {})
            
            # Patent activity
            patent_data = await scraper.scrape_patent_activity(company)
            if not patent_data.get('error'):
                results['data_points']['innovation'] = {
                    'recent_patents': len(patent_data.get('recent_patents', [])),
                    'focus_areas': list(patent_data.get('technology_areas', {}).keys())[:3]
                }
            
            # Employee sentiment
            glassdoor_data = await scraper.scrape_glassdoor_sentiment(company)
            if not glassdoor_data.get('error'):
                results['data_points']['employee_sentiment'] = {
                    'rating': glassdoor_data.get('ratings', {}).get('overall', 'N/A'),
                    'sentiment': glassdoor_data.get('employee_sentiment', 'unknown')
                }
            
            # Social sentiment
            if ticker:
                reddit_data = await scraper.scrape_reddit_sentiment(company, ticker)
                if not reddit_data.get('error'):
                    results['data_points']['social_sentiment'] = {
                        'trending': reddit_data.get('trending', False),
                        'mention_count': len(reddit_data.get('mentions', [])),
                        'sentiment_breakdown': reddit_data.get('sentiment_summary', {})
                    }
            
            # Generate insights
            results['insights'] = []
            
            if results['data_points'].get('hiring', {}).get('trend') == 'aggressive expansion':
                results['insights'].append('Company showing strong growth signals through aggressive hiring')
            
            if results['data_points'].get('employee_sentiment', {}).get('sentiment') == 'positive':
                results['insights'].append('High employee satisfaction indicates healthy company culture')
            
            if results['data_points'].get('innovation', {}).get('recent_patents', 0) > 10:
                results['insights'].append('Active patent filing suggests strong R&D investment')
            
            if results['data_points'].get('social_sentiment', {}).get('trending'):
                results['insights'].append('High social media activity indicates increased retail investor interest')
            
            return [TextContent(
                type="text",
                text=json.dumps(results, indent=2)
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
                server_name="alternative-data-scraper",
                server_version="0.1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())