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



class EconomicDataCollector:
    """Collector for macroeconomic data from government sources"""
    
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
    
    async def scrape_fred_data(self, series_id: str) -> Dict[str, Any]:
        """Scrape data from Federal Reserve Economic Data (FRED)"""
        url = f"https://fred.stlouisfed.org/series/{series_id}"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                fred_data = {
                    'series_id': series_id,
                    'source': 'fred',
                    'metadata': {},
                    'recent_values': [],
                    'timestamp': datetime.now().isoformat()
                }
                
                # Extract series metadata
                title_elem = soup.find('h1', {'class': 'series-title'})
                if title_elem:
                    fred_data['metadata']['title'] = title_elem.text.strip()
                
                # Extract units and frequency
                meta_items = soup.find_all('div', {'class': 'series-meta-item'})
                for item in meta_items:
                    label = item.find('div', {'class': 'series-meta-label'})
                    value = item.find('div', {'class': 'series-meta-value'})
                    if label and value:
                        label_text = label.text.strip().lower()
                        if 'units' in label_text:
                            fred_data['metadata']['units'] = value.text.strip()
                        elif 'frequency' in label_text:
                            fred_data['metadata']['frequency'] = value.text.strip()
                
                # Extract recent data points
                data_table = soup.find('table', {'class': 'series-obs-table'})
                if data_table:
                    rows = data_table.find_all('tr')[1:11]  # Last 10 observations
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            fred_data['recent_values'].append({
                                'date': cells[0].text.strip(),
                                'value': cells[1].text.strip()
                            })
                
                return fred_data
        
        except Exception as e:
            return {'error': f"Failed to scrape FRED data: {str(e)}"}
    
    async def get_treasury_yields(self) -> Dict[str, Any]:
        """Get current Treasury yield curve data"""
        url = "https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/textview.aspx?data=yield"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                yield_data = {
                    'source': 'us_treasury',
                    'yield_curve': {},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Find the yield table
                table = soup.find('table', {'class': 't-chart'})
                if table:
                    # Get headers (maturities)
                    headers = []
                    header_row = table.find('tr')
                    if header_row:
                        for th in header_row.find_all('th')[1:]:  # Skip date column
                            headers.append(th.text.strip())
                    
                    # Get most recent yields
                    data_rows = table.find_all('tr')[1:]
                    if data_rows:
                        latest_row = data_rows[-1]  # Most recent data
                        cells = latest_row.find_all('td')
                        
                        if cells:
                            yield_data['date'] = cells[0].text.strip()
                            for i, header in enumerate(headers, 1):
                                if i < len(cells):
                                    yield_data['yield_curve'][header] = cells[i].text.strip()
                
                # Calculate spread metrics
                if '2 yr' in yield_data['yield_curve'] and '10 yr' in yield_data['yield_curve']:
                    try:
                        two_year = float(yield_data['yield_curve']['2 yr'])
                        ten_year = float(yield_data['yield_curve']['10 yr'])
                        yield_data['spreads'] = {
                            '2s10s': f"{ten_year - two_year:.2f}",
                            'inverted': ten_year < two_year
                        }
                    except:
                        pass
                
                return yield_data
        
        except Exception as e:
            return {'error': f"Failed to scrape Treasury yields: {str(e)}"}
    
    async def get_bls_employment_data(self) -> Dict[str, Any]:
        """Get employment data from Bureau of Labor Statistics"""
        url = "https://www.bls.gov/news.release/empsit.nr0.htm"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                employment_data = {
                    'source': 'bls',
                    'unemployment_rate': {},
                    'nonfarm_payrolls': {},
                    'wage_growth': {},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Extract key employment metrics from the text
                text_content = soup.get_text()
                
                # Unemployment rate
                unemployment_match = re.search(r'unemployment rate.*?(\d+\.\d+)\s*percent', text_content, re.I)
                if unemployment_match:
                    employment_data['unemployment_rate']['current'] = unemployment_match.group(1)
                
                # Nonfarm payrolls
                payrolls_match = re.search(r'nonfarm payroll employment.*?(\d+,?\d*)\s*(?:thousand|,000)', text_content, re.I)
                if payrolls_match:
                    employment_data['nonfarm_payrolls']['change'] = payrolls_match.group(1)
                
                # Average hourly earnings
                wage_match = re.search(r'average hourly earnings.*?(\d+\.\d+)\s*percent', text_content, re.I)
                if wage_match:
                    employment_data['wage_growth']['year_over_year'] = wage_match.group(1)
                
                return employment_data
        
        except Exception as e:
            return {'error': f"Failed to scrape BLS data: {str(e)}"}
    
    async def get_inflation_data(self) -> Dict[str, Any]:
        """Get inflation data (CPI) from BLS"""
        url = "https://www.bls.gov/news.release/cpi.nr0.htm"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                inflation_data = {
                    'source': 'bls_cpi',
                    'headline_cpi': {},
                    'core_cpi': {},
                    'categories': {},
                    'timestamp': datetime.now().isoformat()
                }
                
                text_content = soup.get_text()
                
                # Headline CPI
                headline_match = re.search(r'Consumer Price Index.*?(\d+\.\d+)\s*percent.*?12 months', text_content, re.I)
                if headline_match:
                    inflation_data['headline_cpi']['year_over_year'] = headline_match.group(1)
                
                # Core CPI (excluding food and energy)
                core_match = re.search(r'excluding food and energy.*?(\d+\.\d+)\s*percent.*?12 months', text_content, re.I)
                if core_match:
                    inflation_data['core_cpi']['year_over_year'] = core_match.group(1)
                
                # Category breakdowns
                categories = ['food', 'energy', 'shelter', 'medical', 'transportation']
                for category in categories:
                    cat_match = re.search(rf'{category}.*?(\d+\.\d+)\s*percent', text_content, re.I)
                    if cat_match:
                        inflation_data['categories'][category] = cat_match.group(1)
                
                return inflation_data
        
        except Exception as e:
            return {'error': f"Failed to scrape inflation data: {str(e)}"}
    
    async def get_gdp_data(self) -> Dict[str, Any]:
        """Get GDP data from Bureau of Economic Analysis"""
        url = "https://www.bea.gov/news/current-releases"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                gdp_data = {
                    'source': 'bea',
                    'real_gdp': {},
                    'nominal_gdp': {},
                    'gdp_components': {},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Find GDP release
                gdp_link = soup.find('a', text=re.compile('Gross Domestic Product', re.I))
                if gdp_link:
                    gdp_url = 'https://www.bea.gov' + gdp_link.get('href', '')
                    
                    async with self.session.get(gdp_url) as gdp_response:
                        gdp_html = await gdp_response.text()
                        gdp_soup = BeautifulSoup(gdp_html, 'html.parser')
                        
                        text_content = gdp_soup.get_text()
                        
                        # Real GDP growth
                        real_gdp_match = re.search(r'real.*?GDP.*?(\d+\.\d+)\s*percent.*?annual rate', text_content, re.I)
                        if real_gdp_match:
                            gdp_data['real_gdp']['quarterly_annualized'] = real_gdp_match.group(1)
                        
                        # Components
                        components = {
                            'consumption': 'personal consumption',
                            'investment': 'gross private.*?investment',
                            'government': 'government.*?expenditures',
                            'net_exports': 'net exports'
                        }
                        
                        for key, pattern in components.items():
                            comp_match = re.search(rf'{pattern}.*?(\d+\.\d+)\s*percent', text_content, re.I)
                            if comp_match:
                                gdp_data['gdp_components'][key] = comp_match.group(1)
                
                return gdp_data
        
        except Exception as e:
            return {'error': f"Failed to scrape GDP data: {str(e)}"}
    
    async def get_fed_policy_data(self) -> Dict[str, Any]:
        """Get Federal Reserve policy data and meeting minutes"""
        url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                fed_data = {
                    'source': 'federal_reserve',
                    'current_rate': {},
                    'meeting_dates': [],
                    'recent_decisions': [],
                    'timestamp': datetime.now().isoformat()
                }
                
                # Extract current fed funds rate
                rate_elem = soup.find(text=re.compile('federal funds rate', re.I))
                if rate_elem:
                    rate_text = rate_elem.parent.get_text()
                    rate_match = re.search(r'(\d+\.?\d*)\s*to\s*(\d+\.?\d*)\s*percent', rate_text)
                    if rate_match:
                        fed_data['current_rate'] = {
                            'lower_bound': rate_match.group(1),
                            'upper_bound': rate_match.group(2),
                            'midpoint': f"{(float(rate_match.group(1)) + float(rate_match.group(2))) / 2:.2f}"
                        }
                
                # Extract meeting dates
                meeting_divs = soup.find_all('div', {'class': 'fomc-meeting'})
                for meeting in meeting_divs[:5]:  # Next 5 meetings
                    date_elem = meeting.find('div', {'class': 'fomc-date'})
                    if date_elem:
                        fed_data['meeting_dates'].append(date_elem.text.strip())
                
                return fed_data
        
        except Exception as e:
            return {'error': f"Failed to scrape Fed data: {str(e)}"}
    
    async def get_housing_data(self) -> Dict[str, Any]:
        """Get housing market data from various sources"""
        housing_data = {
            'source': 'multiple',
            'home_prices': {},
            'sales_data': {},
            'mortgage_rates': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Get mortgage rates from Freddie Mac
        mortgage_url = "http://www.freddiemac.com/pmms/"
        
        try:
            async with self.session.get(mortgage_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract 30-year mortgage rate
                rate_elem = soup.find(text=re.compile('30-year', re.I))
                if rate_elem:
                    rate_text = rate_elem.parent.parent.get_text()
                    rate_match = re.search(r'(\d+\.\d+)%', rate_text)
                    if rate_match:
                        housing_data['mortgage_rates']['30_year'] = rate_match.group(1)
        except:
            pass
        
        # Get housing starts from Census
        starts_url = "https://www.census.gov/construction/nrc/index.html"
        
        try:
            async with self.session.get(starts_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract housing starts data
                text_content = soup.get_text()
                starts_match = re.search(r'housing starts.*?(\d+,?\d*)\s*thousand', text_content, re.I)
                if starts_match:
                    housing_data['sales_data']['housing_starts'] = starts_match.group(1)
        except:
            pass
        
        return housing_data
    
    async def get_consumer_confidence(self) -> Dict[str, Any]:
        """Get consumer confidence indicators"""
        confidence_data = {
            'source': 'multiple_indicators',
            'michigan_sentiment': {},
            'conference_board': {},
            'retail_sales': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # This would typically scrape from Conference Board and U Michigan sites
        # For demonstration, using available public data
        
        # Retail sales from Census
        retail_url = "https://www.census.gov/retail/index.html"
        
        try:
            async with self.session.get(retail_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                text_content = soup.get_text()
                retail_match = re.search(r'retail.*?sales.*?(\d+\.\d+)\s*percent', text_content, re.I)
                if retail_match:
                    confidence_data['retail_sales']['monthly_change'] = retail_match.group(1)
        except:
            pass
        
        return confidence_data
    
    async def get_comprehensive_economic_data(self) -> Dict[str, Any]:
        """Get comprehensive economic indicators dashboard"""
        # Key FRED series IDs
        fred_series = {
            'gdp': 'GDP',
            'unemployment': 'UNRATE',
            'inflation': 'CPIAUCSL',
            'fed_funds': 'DFF',
            'ten_year_yield': 'DGS10',
            'vix': 'VIXCLS',
            'dollar_index': 'DTWEXBGS',
            'oil_price': 'DCOILWTICO'
        }
        
        economic_dashboard = {
            'timestamp': datetime.now().isoformat(),
            'indicators': {},
            'yield_curve': {},
            'labor_market': {},
            'inflation': {},
            'growth': {},
            'policy': {},
            'market_conditions': {}
        }
        
        # Gather all data
        # Treasury yields
        yields = await self.get_treasury_yields()
        if not yields.get('error'):
            economic_dashboard['yield_curve'] = yields.get('yield_curve', {})
            economic_dashboard['yield_curve']['spreads'] = yields.get('spreads', {})
        
        # Employment
        employment = await self.get_bls_employment_data()
        if not employment.get('error'):
            economic_dashboard['labor_market'] = employment
        
        # Inflation
        inflation = await self.get_inflation_data()
        if not inflation.get('error'):
            economic_dashboard['inflation'] = inflation
        
        # GDP
        gdp = await self.get_gdp_data()
        if not gdp.get('error'):
            economic_dashboard['growth'] = gdp
        
        # Fed Policy
        fed = await self.get_fed_policy_data()
        if not fed.get('error'):
            economic_dashboard['policy'] = fed
        
        # Housing
        housing = await self.get_housing_data()
        if not housing.get('error'):
            economic_dashboard['market_conditions']['housing'] = housing
        
        # Consumer
        consumer = await self.get_consumer_confidence()
        if not consumer.get('error'):
            economic_dashboard['market_conditions']['consumer'] = consumer
        
        # Add economic outlook summary
        economic_dashboard['outlook_summary'] = self._generate_outlook_summary(economic_dashboard)
        
        return economic_dashboard
    
    def _generate_outlook_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate economic outlook summary based on indicators"""
        summary = {
            'growth_outlook': 'neutral',
            'inflation_pressure': 'moderate',
            'labor_market_strength': 'solid',
            'policy_stance': 'neutral',
            'key_risks': []
        }
        
        # Analyze yield curve
        if data.get('yield_curve', {}).get('spreads', {}).get('inverted'):
            summary['key_risks'].append('Inverted yield curve signals recession risk')
            summary['growth_outlook'] = 'weakening'
        
        # Analyze unemployment
        try:
            unemployment = float(data.get('labor_market', {}).get('unemployment_rate', {}).get('current', '4.0'))
            if unemployment < 4.0:
                summary['labor_market_strength'] = 'very strong'
            elif unemployment > 5.0:
                summary['labor_market_strength'] = 'weakening'
        except:
            pass
        
        # Analyze inflation
        try:
            core_cpi = float(data.get('inflation', {}).get('core_cpi', {}).get('year_over_year', '2.0'))
            if core_cpi > 3.0:
                summary['inflation_pressure'] = 'elevated'
                summary['key_risks'].append('Persistent inflation may require tighter policy')
            elif core_cpi < 2.0:
                summary['inflation_pressure'] = 'low'
        except:
            pass
        
        # Analyze Fed policy
        try:
            fed_rate = float(data.get('policy', {}).get('current_rate', {}).get('midpoint', '5.0'))
            if fed_rate > 5.0:
                summary['policy_stance'] = 'restrictive'
            elif fed_rate < 2.0:
                summary['policy_stance'] = 'accommodative'
        except:
            pass
        
        return summary


# Initialize server
server = Server("economic-data-collector")
collector = EconomicDataCollector()

# Define tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="get_treasury_yields",
            description="Get current US Treasury yield curve data",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_employment_data",
            description="Get latest employment statistics from BLS",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_inflation_data",
            description="Get latest CPI inflation data",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_gdp_data",
            description="Get latest GDP growth data from BEA",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_fed_policy",
            description="Get Federal Reserve policy rates and meeting schedule",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_fred_series",
            description="Get specific economic data series from FRED",
            inputSchema={
                "type": "object",
                "properties": {
                    "series_id": {
                        "type": "string",
                        "description": "FRED series ID (e.g., GDP, UNRATE, CPIAUCSL)"
                    }
                },
                "required": ["series_id"]
            }
        ),
        Tool(
            name="get_housing_market_data",
            description="Get housing market indicators including prices and mortgage rates",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_economic_dashboard",
            description="Get comprehensive economic indicators dashboard",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    await collector.setup()
    
    try:
        if name == "get_treasury_yields":
            yield_data = await collector.get_treasury_yields()
            
            return [TextContent(
                type="text",
                text=json.dumps(yield_data, indent=2)
            )]
        
        elif name == "get_employment_data":
            employment_data = await collector.get_bls_employment_data()
            
            return [TextContent(
                type="text",
                text=json.dumps(employment_data, indent=2)
            )]
        
        elif name == "get_inflation_data":
            inflation_data = await collector.get_inflation_data()
            
            return [TextContent(
                type="text",
                text=json.dumps(inflation_data, indent=2)
            )]
        
        elif name == "get_gdp_data":
            gdp_data = await collector.get_gdp_data()
            
            return [TextContent(
                type="text",
                text=json.dumps(gdp_data, indent=2)
            )]
        
        elif name == "get_fed_policy":
            fed_data = await collector.get_fed_policy_data()
            
            return [TextContent(
                type="text",
                text=json.dumps(fed_data, indent=2)
            )]
        
        elif name == "get_fred_series":
            series_id = arguments["series_id"].upper()
            fred_data = await collector.scrape_fred_data(series_id)
            
            return [TextContent(
                type="text",
                text=json.dumps(fred_data, indent=2)
            )]
        
        elif name == "get_housing_market_data":
            housing_data = await collector.get_housing_data()
            
            return [TextContent(
                type="text",
                text=json.dumps(housing_data, indent=2)
            )]
        
        elif name == "get_economic_dashboard":
            dashboard = await collector.get_comprehensive_economic_data()
            
            return [TextContent(
                type="text",
                text=json.dumps(dashboard, indent=2)
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
    
    finally:
        await collector.cleanup()

async def main():
    async with stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="economic-data-collector",
                server_version="0.1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())