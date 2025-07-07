import time
#!/usr/bin/env python

import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import re
import statistics

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



class IndustryAssumptionsEngine:
    """Engine for extracting and calculating industry-specific DCF model assumptions"""
    
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
                
        # Industry-specific metrics mappings
        self.industry_metrics = {
            'technology': ['revenue_growth', 'r&d_expense', 'capex_ratio', 'gross_margin'],
            'retail': ['same_store_sales', 'inventory_turnover', 'gross_margin', 'store_count'],
            'finance': ['net_interest_margin', 'loan_loss_provision', 'tier1_capital', 'roe'],
            'healthcare': ['r&d_expense', 'patent_life', 'gross_margin', 'regulatory_risk'],
            'energy': ['production_growth', 'finding_costs', 'reserve_life', 'commodity_prices'],
            'industrial': ['capacity_utilization', 'capex_ratio', 'working_capital', 'backlog'],
            'consumer': ['organic_growth', 'marketing_expense', 'brand_value', 'market_share'],
            'telecom': ['arpu', 'churn_rate', 'capex_intensity', 'subscriber_growth'],
            'utilities': ['rate_base_growth', 'allowed_roe', 'capex_plan', 'regulatory_lag'],
            'realestate': ['occupancy_rate', 'rent_growth', 'cap_rate', 'ffo_growth']
        }
    
    async def setup(self):
        """Setup aiohttp session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def cleanup(self):
        """Cleanup aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def scrape_industry_metrics(self, industry: str) -> Dict[str, Any]:
        """Scrape industry-specific metrics and benchmarks"""
        # Use Damodaran's data as primary source
        damodaran_url = "http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/margin.html"
        
        try:
            async with self.session.get(damodaran_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                industry_data = {
                    'industry': industry,
                    'source': 'damodaran_nyu',
                    'metrics': {},
                    'peer_averages': {},
                    'historical_trends': {},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Find industry data in tables
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if cells and len(cells) > 1:
                            industry_name = cells[0].text.strip().lower()
                            if industry.lower() in industry_name:
                                # Extract metrics
                                if len(cells) >= 6:
                                    industry_data['metrics'] = {
                                        'gross_margin': cells[1].text.strip(),
                                        'operating_margin': cells[2].text.strip(),
                                        'net_margin': cells[3].text.strip(),
                                        'roe': cells[4].text.strip(),
                                        'roa': cells[5].text.strip()
                                    }
                                break
                
                return industry_data
        
        except Exception as e:
            return {'error': f"Failed to scrape industry metrics: {str(e)}"}
    
    async def calculate_wacc_components(self, ticker: str, industry: str) -> Dict[str, Any]:
        """Calculate WACC components using industry data"""
        wacc_data = {
            'ticker': ticker,
            'industry': industry,
            'components': {},
            'industry_averages': {},
            'calculated_wacc': None
        }
        
        # Scrape risk-free rate from Treasury
        treasury_url = "https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/textview.aspx?data=yield"
        
        try:
            async with self.session.get(treasury_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find 10-year treasury yield
                table = soup.find('table', {'class': 't-chart'})
                if table:
                    rows = table.find_all('tr')
                    for row in rows[-1:]:  # Get most recent
                        cells = row.find_all('td')
                        if len(cells) >= 10:
                            wacc_data['components']['risk_free_rate'] = cells[9].text.strip()  # 10-year column
        except:
            wacc_data['components']['risk_free_rate'] = '4.5%'  # Default
        
        # Get industry-specific metrics
        industry_betas = {
            'technology': 1.25,
            'retail': 1.10,
            'finance': 1.15,
            'healthcare': 0.95,
            'energy': 1.20,
            'industrial': 1.05,
            'consumer': 0.90,
            'telecom': 0.85,
            'utilities': 0.65,
            'realestate': 0.75
        }
        
        wacc_data['components']['beta'] = industry_betas.get(industry.lower(), 1.0)
        wacc_data['components']['market_risk_premium'] = 0.065  # Historical average
        
        # Handle risk-free rate safely
        risk_free_str = wacc_data['components'].get('risk_free_rate', '4.5%')
        try:
            risk_free_rate = float(risk_free_str.strip('%')) / 100
        except:
            risk_free_rate = 0.045  # Default 4.5%
        
        wacc_data['components']['cost_of_equity'] = (
            risk_free_rate +
            wacc_data['components']['beta'] * wacc_data['components']['market_risk_premium']
        )
        
        # Industry debt ratios
        industry_debt_ratios = {
            'technology': 0.20,
            'retail': 0.35,
            'finance': 0.70,
            'healthcare': 0.25,
            'energy': 0.40,
            'industrial': 0.30,
            'consumer': 0.35,
            'telecom': 0.50,
            'utilities': 0.60,
            'realestate': 0.55
        }
        
        debt_ratio = industry_debt_ratios.get(industry.lower(), 0.30)
        wacc_data['components']['debt_to_equity'] = debt_ratio / (1 - debt_ratio)
        wacc_data['components']['cost_of_debt'] = 0.04  # Approximate
        wacc_data['components']['tax_rate'] = 0.21  # US corporate tax rate
        
        # Calculate WACC
        equity_weight = 1 / (1 + wacc_data['components']['debt_to_equity'])
        debt_weight = 1 - equity_weight
        
        wacc_data['calculated_wacc'] = (
            equity_weight * wacc_data['components']['cost_of_equity'] +
            debt_weight * wacc_data['components']['cost_of_debt'] * (1 - wacc_data['components']['tax_rate'])
        )
        
        wacc_data['components']['wacc_percentage'] = f"{wacc_data['calculated_wacc'] * 100:.2f}%"
        
        return wacc_data
    
    async def get_growth_assumptions(self, ticker: str, industry: str) -> Dict[str, Any]:
        """Get revenue and earnings growth assumptions based on industry data"""
        growth_data = {
            'ticker': ticker,
            'industry': industry,
            'growth_rates': {},
            'industry_benchmarks': {},
            'growth_drivers': [],
            'risk_factors': []
        }
        
        # Industry growth rates
        industry_growth = {
            'technology': {'revenue': 0.15, 'earnings': 0.18, 'stage': 'growth'},
            'retail': {'revenue': 0.05, 'earnings': 0.06, 'stage': 'mature'},
            'finance': {'revenue': 0.06, 'earnings': 0.08, 'stage': 'mature'},
            'healthcare': {'revenue': 0.08, 'earnings': 0.10, 'stage': 'growth'},
            'energy': {'revenue': 0.04, 'earnings': 0.05, 'stage': 'cyclical'},
            'industrial': {'revenue': 0.06, 'earnings': 0.07, 'stage': 'mature'},
            'consumer': {'revenue': 0.04, 'earnings': 0.05, 'stage': 'mature'},
            'telecom': {'revenue': 0.03, 'earnings': 0.04, 'stage': 'mature'},
            'utilities': {'revenue': 0.03, 'earnings': 0.03, 'stage': 'stable'},
            'realestate': {'revenue': 0.05, 'earnings': 0.06, 'stage': 'cyclical'}
        }
        
        industry_rates = industry_growth.get(industry.lower(), {'revenue': 0.05, 'earnings': 0.06, 'stage': 'mature'})
        
        # Build growth assumptions
        growth_data['growth_rates'] = {
            'year_1': industry_rates['revenue'] * 1.2,  # Above industry initially
            'year_2': industry_rates['revenue'] * 1.1,
            'year_3': industry_rates['revenue'],
            'year_4': industry_rates['revenue'] * 0.9,
            'year_5': industry_rates['revenue'] * 0.8,
            'terminal_growth': 0.03  # GDP growth
        }
        
        growth_data['industry_benchmarks'] = industry_rates
        
        # Industry-specific growth drivers
        growth_drivers_map = {
            'technology': ['Cloud adoption', 'AI/ML integration', 'Digital transformation', 'SaaS conversion'],
            'retail': ['E-commerce growth', 'Omnichannel strategy', 'Market expansion', 'Customer loyalty'],
            'finance': ['Interest rate environment', 'Loan growth', 'Fee income', 'Digital banking'],
            'healthcare': ['Aging population', 'Drug pipeline', 'Market access', 'Pricing power'],
            'energy': ['Commodity prices', 'Production volumes', 'Reserve additions', 'Cost efficiency'],
            'industrial': ['Economic cycles', 'Infrastructure spending', 'Automation', 'Supply chain'],
            'consumer': ['Brand strength', 'Market share', 'Innovation', 'Demographics'],
            'telecom': ['5G rollout', 'Subscriber growth', 'ARPU trends', 'Network investment'],
            'utilities': ['Rate base growth', 'Regulatory support', 'Renewable transition', 'Efficiency'],
            'realestate': ['Occupancy trends', 'Rent growth', 'Development pipeline', 'Location quality']
        }
        
        growth_data['growth_drivers'] = growth_drivers_map.get(industry.lower(), ['Market growth', 'Operational efficiency'])
        
        # Industry-specific risk factors
        risk_factors_map = {
            'technology': ['Competition', 'Technology obsolescence', 'Regulatory changes', 'Cybersecurity'],
            'retail': ['Consumer spending', 'E-commerce disruption', 'Inventory management', 'Labor costs'],
            'finance': ['Credit risk', 'Interest rate risk', 'Regulatory changes', 'Economic cycles'],
            'healthcare': ['Regulatory approval', 'Pricing pressure', 'Patent expiration', 'R&D risk'],
            'energy': ['Commodity volatility', 'Environmental regulation', 'Geopolitical risk', 'Transition risk'],
            'industrial': ['Economic cycles', 'Raw material costs', 'Trade policies', 'Labor availability'],
            'consumer': ['Consumer preferences', 'Input costs', 'Brand relevance', 'Distribution'],
            'telecom': ['Competition', 'Capex requirements', 'Technology shifts', 'Regulation'],
            'utilities': ['Regulatory risk', 'Weather', 'Fuel costs', 'Infrastructure age'],
            'realestate': ['Interest rates', 'Economic cycles', 'Location risk', 'Construction costs']
        }
        
        growth_data['risk_factors'] = risk_factors_map.get(industry.lower(), ['Market risk', 'Operational risk'])
        
        return growth_data
    
    async def get_margin_assumptions(self, ticker: str, industry: str) -> Dict[str, Any]:
        """Get operating margin and profitability assumptions"""
        margin_data = {
            'ticker': ticker,
            'industry': industry,
            'margin_projections': {},
            'industry_averages': {},
            'margin_drivers': []
        }
        
        # Industry margin profiles
        industry_margins = {
            'technology': {'gross': 0.65, 'operating': 0.25, 'net': 0.20},
            'retail': {'gross': 0.35, 'operating': 0.08, 'net': 0.05},
            'finance': {'gross': 0.90, 'operating': 0.40, 'net': 0.25},
            'healthcare': {'gross': 0.70, 'operating': 0.20, 'net': 0.15},
            'energy': {'gross': 0.30, 'operating': 0.15, 'net': 0.10},
            'industrial': {'gross': 0.30, 'operating': 0.12, 'net': 0.08},
            'consumer': {'gross': 0.40, 'operating': 0.15, 'net': 0.10},
            'telecom': {'gross': 0.60, 'operating': 0.20, 'net': 0.12},
            'utilities': {'gross': 0.40, 'operating': 0.20, 'net': 0.12},
            'realestate': {'gross': 0.70, 'operating': 0.35, 'net': 0.20}
        }
        
        margins = industry_margins.get(industry.lower(), {'gross': 0.40, 'operating': 0.15, 'net': 0.10})
        margin_data['industry_averages'] = margins
        
        # Project margins with mean reversion
        current_year = margins['operating']
        margin_data['margin_projections'] = {
            'year_1': current_year * 1.05,  # Slight improvement
            'year_2': current_year * 1.03,
            'year_3': current_year * 1.01,
            'year_4': current_year,
            'year_5': current_year,
            'terminal': current_year * 0.98  # Slight compression
        }
        
        # Margin drivers by industry
        margin_drivers_map = {
            'technology': ['Scale economies', 'R&D leverage', 'Pricing power', 'Automation'],
            'retail': ['Supply chain efficiency', 'Private label', 'Store optimization', 'Digital sales'],
            'finance': ['Net interest margin', 'Fee income', 'Operating leverage', 'Credit quality'],
            'healthcare': ['Drug mix', 'Pricing', 'R&D efficiency', 'Manufacturing scale'],
            'energy': ['Commodity prices', 'Production efficiency', 'Cost discipline', 'Technology'],
            'industrial': ['Capacity utilization', 'Pricing', 'Productivity', 'Mix shift'],
            'consumer': ['Brand premium', 'Cost control', 'Distribution efficiency', 'Product mix'],
            'telecom': ['Network efficiency', 'Customer mix', 'Cost per subscriber', 'Pricing'],
            'utilities': ['Rate recovery', 'Operating efficiency', 'Fuel costs', 'Maintenance'],
            'realestate': ['Occupancy', 'Rental rates', 'Operating leverage', 'Property quality']
        }
        
        margin_data['margin_drivers'] = margin_drivers_map.get(industry.lower(), ['Efficiency', 'Scale', 'Pricing'])
        
        return margin_data
    
    async def get_capex_working_capital(self, ticker: str, industry: str) -> Dict[str, Any]:
        """Get capital expenditure and working capital assumptions"""
        capex_wc_data = {
            'ticker': ticker,
            'industry': industry,
            'capex_assumptions': {},
            'working_capital_assumptions': {},
            'industry_benchmarks': {}
        }
        
        # Industry capex intensity
        industry_capex = {
            'technology': 0.05,  # % of revenue
            'retail': 0.03,
            'finance': 0.02,
            'healthcare': 0.04,
            'energy': 0.15,
            'industrial': 0.04,
            'consumer': 0.03,
            'telecom': 0.15,
            'utilities': 0.20,
            'realestate': 0.02
        }
        
        # Working capital as % of revenue
        industry_wc = {
            'technology': 0.10,
            'retail': 0.15,
            'finance': 0.05,
            'healthcare': 0.20,
            'energy': 0.10,
            'industrial': 0.15,
            'consumer': 0.12,
            'telecom': 0.08,
            'utilities': 0.10,
            'realestate': 0.05
        }
        
        capex_rate = industry_capex.get(industry.lower(), 0.05)
        wc_rate = industry_wc.get(industry.lower(), 0.10)
        
        capex_wc_data['capex_assumptions'] = {
            'maintenance_capex': capex_rate * 0.7,
            'growth_capex': capex_rate * 0.3,
            'total_capex_rate': capex_rate,
            'depreciation_rate': capex_rate * 0.8  # Depreciation as % of capex
        }
        
        capex_wc_data['working_capital_assumptions'] = {
            'working_capital_pct': wc_rate,
            'days_sales_outstanding': 45 if industry.lower() != 'retail' else 5,
            'days_inventory': 60 if industry.lower() in ['retail', 'industrial', 'consumer'] else 30,
            'days_payable': 45
        }
        
        capex_wc_data['industry_benchmarks'] = {
            'capex_intensity': capex_rate,
            'working_capital_intensity': wc_rate,
            'asset_turnover': 1 / (capex_rate + wc_rate)
        }
        
        return capex_wc_data
    
    async def generate_dcf_assumptions(self, ticker: str, industry: str) -> Dict[str, Any]:
        """Generate comprehensive DCF model assumptions"""
        # Gather all components
        wacc = await self.calculate_wacc_components(ticker, industry)
        growth = await self.get_growth_assumptions(ticker, industry)
        margins = await self.get_margin_assumptions(ticker, industry)
        capex_wc = await self.get_capex_working_capital(ticker, industry)
        
        dcf_assumptions = {
            'ticker': ticker,
            'industry': industry,
            'generated_date': datetime.now().isoformat(),
            'valuation_assumptions': {
                'wacc': wacc['calculated_wacc'],
                'terminal_growth_rate': growth['growth_rates']['terminal_growth'],
                'projection_years': 5
            },
            'revenue_assumptions': {
                'growth_rates': growth['growth_rates'],
                'growth_drivers': growth['growth_drivers']
            },
            'profitability_assumptions': {
                'operating_margins': margins['margin_projections'],
                'tax_rate': 0.21
            },
            'capital_assumptions': {
                'capex_as_pct_revenue': capex_wc['capex_assumptions']['total_capex_rate'],
                'working_capital_pct': capex_wc['working_capital_assumptions']['working_capital_pct'],
                'depreciation_rate': capex_wc['capex_assumptions']['depreciation_rate']
            },
            'industry_context': {
                'industry_stage': growth['industry_benchmarks']['stage'],
                'key_risks': growth['risk_factors'],
                'margin_drivers': margins['margin_drivers']
            },
            'sensitivity_ranges': {
                'wacc_range': [wacc['calculated_wacc'] - 0.01, wacc['calculated_wacc'] + 0.01],
                'terminal_growth_range': [0.02, 0.04],
                'margin_range': [-0.02, 0.02]  # +/- 2% on margins
            }
        }
        
        return dcf_assumptions
    
    async def get_comparable_multiples(self, industry: str) -> Dict[str, Any]:
        """Get industry-specific valuation multiples"""
        multiples_data = {
            'industry': industry,
            'valuation_multiples': {},
            'peer_universe': [],
            'multiple_drivers': []
        }
        
        # Industry multiple ranges
        industry_multiples = {
            'technology': {'ev_revenue': 5.0, 'ev_ebitda': 20.0, 'pe': 25.0},
            'retail': {'ev_revenue': 0.8, 'ev_ebitda': 10.0, 'pe': 18.0},
            'finance': {'ev_revenue': 3.0, 'ev_ebitda': 12.0, 'pe': 15.0, 'p_book': 1.5},
            'healthcare': {'ev_revenue': 3.5, 'ev_ebitda': 15.0, 'pe': 20.0},
            'energy': {'ev_revenue': 1.5, 'ev_ebitda': 8.0, 'pe': 12.0},
            'industrial': {'ev_revenue': 1.5, 'ev_ebitda': 12.0, 'pe': 18.0},
            'consumer': {'ev_revenue': 2.0, 'ev_ebitda': 12.0, 'pe': 20.0},
            'telecom': {'ev_revenue': 2.0, 'ev_ebitda': 8.0, 'pe': 15.0},
            'utilities': {'ev_revenue': 2.5, 'ev_ebitda': 10.0, 'pe': 18.0},
            'realestate': {'ev_revenue': 5.0, 'ev_ebitda': 18.0, 'pe': 20.0, 'p_ffo': 15.0}
        }
        
        multiples_data['valuation_multiples'] = industry_multiples.get(
            industry.lower(), 
            {'ev_revenue': 2.0, 'ev_ebitda': 12.0, 'pe': 18.0}
        )
        
        # Multiple drivers by industry
        multiple_drivers_map = {
            'technology': ['Growth rate', 'Recurring revenue %', 'Market position', 'Profitability'],
            'retail': ['Same-store sales', 'E-commerce mix', 'Market share', 'Margins'],
            'finance': ['ROE', 'Asset quality', 'Capital ratios', 'Growth'],
            'healthcare': ['Pipeline', 'Patent life', 'Market size', 'Margins'],
            'energy': ['Reserve life', 'Production growth', 'Cost position', 'Commodity exposure'],
            'industrial': ['Cycle position', 'Market share', 'Margins', 'Growth'],
            'consumer': ['Brand strength', 'Growth', 'Margins', 'Market position'],
            'telecom': ['Subscriber growth', 'ARPU', 'Market share', 'Network quality'],
            'utilities': ['Rate base growth', 'Regulatory environment', 'Renewable mix', 'Dividend yield'],
            'realestate': ['Location quality', 'Occupancy', 'Rent growth', 'Development pipeline']
        }
        
        multiples_data['multiple_drivers'] = multiple_drivers_map.get(
            industry.lower(), 
            ['Growth', 'Profitability', 'Market position', 'Risk profile']
        )
        
        return multiples_data


# Initialize server
server = Server("industry-assumptions-engine")
engine = IndustryAssumptionsEngine()

# Define tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="calculate_wacc",
            description="Calculate Weighted Average Cost of Capital using industry data",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "industry": {
                        "type": "string",
                        "description": "Industry classification (technology, retail, finance, etc.)"
                    }
                },
                "required": ["ticker", "industry"]
            }
        ),
        Tool(
            name="get_growth_assumptions",
            description="Get revenue and earnings growth assumptions based on industry analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "industry": {
                        "type": "string",
                        "description": "Industry classification"
                    }
                },
                "required": ["ticker", "industry"]
            }
        ),
        Tool(
            name="get_margin_assumptions",
            description="Get operating margin and profitability assumptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "industry": {
                        "type": "string",
                        "description": "Industry classification"
                    }
                },
                "required": ["ticker", "industry"]
            }
        ),
        Tool(
            name="get_capital_assumptions",
            description="Get capital expenditure and working capital assumptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "industry": {
                        "type": "string",
                        "description": "Industry classification"
                    }
                },
                "required": ["ticker", "industry"]
            }
        ),
        Tool(
            name="generate_full_dcf_assumptions",
            description="Generate comprehensive DCF model assumptions for a company",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "industry": {
                        "type": "string",
                        "description": "Industry classification"
                    }
                },
                "required": ["ticker", "industry"]
            }
        ),
        Tool(
            name="get_valuation_multiples",
            description="Get industry-specific valuation multiples and comparable metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "industry": {
                        "type": "string",
                        "description": "Industry classification"
                    }
                },
                "required": ["industry"]
            }
        ),
        Tool(
            name="get_industry_metrics",
            description="Get comprehensive industry metrics and benchmarks",
            inputSchema={
                "type": "object",
                "properties": {
                    "industry": {
                        "type": "string",
                        "description": "Industry classification"
                    }
                },
                "required": ["industry"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    await engine.setup()
    
    try:
        if name == "calculate_wacc":
            ticker = arguments["ticker"].upper()
            industry = arguments["industry"].lower()
            
            wacc_data = await engine.calculate_wacc_components(ticker, industry)
            
            return [TextContent(
                type="text",
                text=json.dumps(wacc_data, indent=2)
            )]
        
        elif name == "get_growth_assumptions":
            ticker = arguments["ticker"].upper()
            industry = arguments["industry"].lower()
            
            growth_data = await engine.get_growth_assumptions(ticker, industry)
            
            return [TextContent(
                type="text",
                text=json.dumps(growth_data, indent=2)
            )]
        
        elif name == "get_margin_assumptions":
            ticker = arguments["ticker"].upper()
            industry = arguments["industry"].lower()
            
            margin_data = await engine.get_margin_assumptions(ticker, industry)
            
            return [TextContent(
                type="text",
                text=json.dumps(margin_data, indent=2)
            )]
        
        elif name == "get_capital_assumptions":
            ticker = arguments["ticker"].upper()
            industry = arguments["industry"].lower()
            
            capital_data = await engine.get_capex_working_capital(ticker, industry)
            
            return [TextContent(
                type="text",
                text=json.dumps(capital_data, indent=2)
            )]
        
        elif name == "generate_full_dcf_assumptions":
            ticker = arguments["ticker"].upper()
            industry = arguments["industry"].lower()
            
            dcf_assumptions = await engine.generate_dcf_assumptions(ticker, industry)
            
            return [TextContent(
                type="text",
                text=json.dumps(dcf_assumptions, indent=2)
            )]
        
        elif name == "get_valuation_multiples":
            industry = arguments["industry"].lower()
            
            multiples_data = await engine.get_comparable_multiples(industry)
            
            return [TextContent(
                type="text",
                text=json.dumps(multiples_data, indent=2)
            )]
        
        elif name == "get_industry_metrics":
            industry = arguments["industry"].lower()
            
            # Comprehensive industry analysis
            metrics = await engine.scrape_industry_metrics(industry)
            multiples = await engine.get_comparable_multiples(industry)
            
            # Sample company for assumptions
            sample_ticker = {
                'technology': 'MSFT',
                'retail': 'WMT',
                'finance': 'JPM',
                'healthcare': 'JNJ',
                'energy': 'XOM',
                'industrial': 'CAT',
                'consumer': 'PG',
                'telecom': 'VZ',
                'utilities': 'NEE',
                'realestate': 'SPG'
            }.get(industry, 'SPY')
            
            growth = await engine.get_growth_assumptions(sample_ticker, industry)
            margins = await engine.get_margin_assumptions(sample_ticker, industry)
            capital = await engine.get_capex_working_capital(sample_ticker, industry)
            
            comprehensive_data = {
                'industry': industry,
                'metrics_overview': metrics,
                'valuation_framework': multiples,
                'typical_assumptions': {
                    'growth_profile': growth['growth_rates'],
                    'margin_profile': margins['industry_averages'],
                    'capital_intensity': capital['industry_benchmarks']
                },
                'key_characteristics': {
                    'industry_stage': growth['industry_benchmarks']['stage'],
                    'growth_drivers': growth['growth_drivers'],
                    'risk_factors': growth['risk_factors'],
                    'margin_drivers': margins['margin_drivers'],
                    'valuation_drivers': multiples['multiple_drivers']
                },
                'dcf_guidelines': {
                    'recommended_projection_period': 5,
                    'terminal_growth_rate': growth['growth_rates']['terminal_growth'],
                    'key_sensitivities': ['WACC', 'Terminal Growth', 'Operating Margin']
                }
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(comprehensive_data, indent=2)
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
        await engine.cleanup()

async def main():
    async with stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="industry-assumptions-engine",
                server_version="0.1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())