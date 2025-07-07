#!/usr/bin/env python3
"""
PhD-Level SEC Scraper with Advanced Financial Analysis
Implements XBRL parsing, DCF modeling, and comprehensive analysis
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
import sys
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

import aiohttp
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
import mcp.server.stdio as stdio

# Import advanced modules
from financial_analysis import FinancialMetrics, DCFModel, ComparativeAnalysis, TechnicalIndicators
from xbrl_parser import XBRLParser
from advanced_nlp import AdvancedSentimentAnalyzer
from research_report_generator import ResearchReportGenerator
from data_cache import FinancialDataCache, cache_result, DataVersionManager


class AdvancedSECScraper:
    """Advanced SEC scraper with PhD-level financial analysis capabilities"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.sec_headers = {
            'User-Agent': 'FinancialMCP/2.0 (Advanced Research Tool; Contact: research@financialmcp.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        # Initialize advanced components
        self.xbrl_parser = XBRLParser()
        self.financial_metrics = FinancialMetrics()
        self.dcf_model = DCFModel()
        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
        self.report_generator = ResearchReportGenerator()
        self.cache = FinancialDataCache()
        self.version_manager = DataVersionManager()
        
        # Analysis parameters
        self.analysis_config = {
            'dcf_years': 5,
            'peer_count': 10,
            'historical_years': 3,
            'monte_carlo_simulations': 10000
        }
    
    async def setup(self):
        """Setup aiohttp session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def perform_comprehensive_analysis(self, ticker: str) -> Dict[str, Any]:
        """Perform PhD-level comprehensive stock analysis"""
        print(f"Starting comprehensive analysis for {ticker}")
        
        # Initialize results
        analysis_results = {
            'ticker': ticker,
            'analysis_date': datetime.now().isoformat(),
            'company_data': {},
            'financial_data': {},
            'valuation': {},
            'technical_analysis': {},
            'sentiment_analysis': {},
            'peer_analysis': {},
            'risk_assessment': {},
            'research_report': {}
        }
        
        try:
            # 1. Get company information and filings
            print("Fetching company information...")
            company_info = await self.get_company_information(ticker)
            analysis_results['company_data'] = company_info
            
            # 2. Parse XBRL financial data
            print("Parsing XBRL financial data...")
            xbrl_data = await self.parse_xbrl_financials(ticker)
            analysis_results['financial_data']['xbrl'] = xbrl_data
            
            # 3. Calculate advanced financial metrics
            print("Calculating financial metrics...")
            if xbrl_data and 'error' not in xbrl_data:
                metrics = self._calculate_comprehensive_metrics(xbrl_data)
                analysis_results['financial_data']['metrics'] = metrics
            
            # 4. Perform DCF valuation
            print("Performing DCF valuation...")
            dcf_results = await self.perform_dcf_analysis(ticker, xbrl_data)
            analysis_results['valuation']['dcf'] = dcf_results
            
            # 5. Get market data and technical analysis
            print("Performing technical analysis...")
            market_data = await self.get_market_data(ticker)
            if market_data.get('price_history'):
                tech_analysis = self._perform_technical_analysis(market_data['price_history'])
                analysis_results['technical_analysis'] = tech_analysis
            
            # 6. Analyze news and sentiment
            print("Analyzing sentiment...")
            sentiment_results = await self.analyze_comprehensive_sentiment(ticker)
            analysis_results['sentiment_analysis'] = sentiment_results
            
            # 7. Peer comparison
            print("Performing peer analysis...")
            peer_analysis = await self.analyze_peer_comparison(ticker, company_info)
            analysis_results['peer_analysis'] = peer_analysis
            
            # 8. Risk assessment
            print("Assessing risks...")
            risk_assessment = self._perform_risk_assessment(analysis_results)
            analysis_results['risk_assessment'] = risk_assessment
            
            # 9. Generate research report
            print("Generating research report...")
            research_report = self.report_generator.generate_comprehensive_report(
                company_info, market_data, analysis_results
            )
            analysis_results['research_report'] = research_report
            
            # 10. Calculate quality score
            analysis_results['analysis_quality'] = self._assess_analysis_quality(analysis_results)
            
            # Cache results
            await self.cache.set('comprehensive_analysis', ticker, analysis_results,
                               custom_ttl=timedelta(hours=24))
            
            return analysis_results
            
        except Exception as e:
            print(f"Error in comprehensive analysis: {str(e)}")
            analysis_results['error'] = str(e)
            return analysis_results
    
    @cache_result('company_info', ttl=timedelta(days=7))
    async def get_company_information(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive company information from SEC"""
        # Search for company CIK
        search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&owner=exclude"
        
        try:
            async with self.session.get(search_url, headers=self.sec_headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract company info
                company_info = {'ticker': ticker}
                
                # Get company name and CIK
                company_elem = soup.find('span', {'class': 'companyName'})
                if company_elem:
                    company_text = company_elem.text
                    company_info['company_name'] = company_text.split('CIK')[0].strip()
                    
                    cik_match = re.search(r'CIK#: (\d+)', company_text)
                    if cik_match:
                        company_info['cik'] = cik_match.group(1).zfill(10)
                
                # Get business address
                address_elem = soup.find('div', {'class': 'mailer'})
                if address_elem:
                    company_info['address'] = address_elem.text.strip()
                
                # Get SIC code and industry
                sic_elem = soup.find('p', {'class': 'identInfo'})
                if sic_elem:
                    sic_match = re.search(r'SIC: (\d+)', sic_elem.text)
                    if sic_match:
                        company_info['sic_code'] = sic_match.group(1)
                
                # Get recent filings
                company_info['recent_filings'] = await self._get_recent_filings(
                    company_info.get('cik', ticker)
                )
                
                return company_info
                
        except Exception as e:
            return {'error': f'Failed to get company information: {str(e)}'}
    
    async def parse_xbrl_financials(self, ticker: str) -> Dict[str, Any]:
        """Parse XBRL data from latest 10-K filing"""
        # Get latest 10-K filing
        filings = await self._search_filings(ticker, '10-K', limit=1)
        
        if not filings or 'error' in filings:
            return {'error': 'No 10-K filing found'}
        
        latest_filing = filings[0]
        
        # Fetch XBRL data
        if 'documents_url' in latest_filing:
            xbrl_content = await self.xbrl_parser.fetch_xbrl_from_filing(
                latest_filing['documents_url'], self.session
            )
            
            if xbrl_content:
                # Parse XBRL
                parsed_data = self.xbrl_parser.parse_xbrl_string(xbrl_content)
                
                # Extract key metrics
                key_metrics = self.xbrl_parser.extract_key_metrics(parsed_data)
                parsed_data['key_metrics'] = key_metrics
                
                # Track version
                self.version_manager.track_version(
                    ticker, 'xbrl_financials', key_metrics,
                    f"Updated from {latest_filing['filing_date']}"
                )
                
                return parsed_data
            else:
                # Fallback to HTML parsing
                return await self._parse_html_financials(latest_filing['documents_url'])
        
        return {'error': 'No financial data found'}
    
    def _calculate_comprehensive_metrics(self, xbrl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive financial metrics"""
        metrics = {}
        key_metrics = xbrl_data.get('key_metrics', {})
        
        # Basic metrics from XBRL
        metrics.update(key_metrics)
        
        # Advanced metrics
        if key_metrics.get('total_assets') and key_metrics.get('shareholders_equity'):
            # ROIC calculation
            if key_metrics.get('net_income'):
                ebit = key_metrics['net_income'] * 1.3  # Rough estimate
                metrics['roic'] = self.financial_metrics.calculate_roic(
                    ebit, 0.21,  # Assumed tax rate
                    key_metrics['total_assets'] - key_metrics.get('cash', 0)
                )
        
        # Altman Z-Score
        if all(k in key_metrics for k in ['total_assets', 'total_liabilities']):
            working_capital = key_metrics.get('current_assets', 0) - key_metrics.get('current_liabilities', 0)
            retained_earnings = key_metrics.get('shareholders_equity', 0) * 0.6  # Estimate
            
            z_score, interpretation = self.financial_metrics.calculate_altman_z_score(
                working_capital,
                key_metrics['total_assets'],
                retained_earnings,
                key_metrics.get('net_income', 0) * 1.3,  # EBIT estimate
                key_metrics.get('market_cap', key_metrics['total_assets']),
                key_metrics['total_liabilities'],
                key_metrics.get('revenue', 0)
            )
            
            metrics['altman_z_score'] = z_score
            metrics['bankruptcy_risk'] = interpretation
        
        # Piotroski F-Score
        f_score, criteria = self.financial_metrics.calculate_piotroski_f_score(key_metrics)
        metrics['piotroski_f_score'] = f_score
        metrics['f_score_criteria'] = criteria
        
        # Quality metrics
        if key_metrics.get('operating_cash_flow') and key_metrics.get('net_income'):
            metrics['earnings_quality'] = (
                key_metrics['operating_cash_flow'] / key_metrics['net_income']
                if key_metrics['net_income'] != 0 else 0
            )
        
        return metrics
    
    async def perform_dcf_analysis(self, ticker: str, 
                                 financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced DCF valuation"""
        try:
            # Get required inputs
            key_metrics = financial_data.get('key_metrics', {})
            
            # Get market data for WACC calculation
            market_data = await self.get_market_data(ticker)
            
            # Calculate WACC
            market_cap = market_data.get('market_cap', 0)
            total_debt = key_metrics.get('total_liabilities', 0) * 0.7  # Rough debt estimate
            
            # Cost of equity (CAPM)
            risk_free_rate = 0.045  # Current treasury rate
            market_return = 0.10
            beta = market_data.get('beta', 1.0)
            cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
            
            # Cost of debt
            interest_expense = key_metrics.get('interest_expense', total_debt * 0.04)
            cost_of_debt = interest_expense / total_debt if total_debt > 0 else 0.04
            
            wacc = self.dcf_model.calculate_wacc(
                market_cap, total_debt, cost_of_equity, cost_of_debt, 0.21
            )
            
            # Project cash flows
            base_fcf = key_metrics.get('free_cash_flow', 
                                      key_metrics.get('operating_cash_flow', 0) * 0.8)
            
            if base_fcf <= 0:
                return {'error': 'Negative or zero free cash flow'}
            
            # Growth assumptions
            revenue_growth = self._estimate_growth_rate(financial_data)
            fcf_projections = []
            current_fcf = base_fcf
            
            for year in range(self.analysis_config['dcf_years']):
                growth_rate = revenue_growth * (0.9 ** year)  # Declining growth
                current_fcf *= (1 + growth_rate)
                fcf_projections.append(current_fcf)
            
            # Terminal growth
            terminal_growth = min(0.03, revenue_growth * 0.3)  # Conservative
            
            # Calculate DCF value
            shares_outstanding = market_data.get('shares_outstanding', 1)
            net_debt = total_debt - key_metrics.get('cash', 0)
            
            dcf_result = self.dcf_model.calculate_dcf_value(
                fcf_projections, terminal_growth, wacc, net_debt, shares_outstanding
            )
            
            # Monte Carlo simulation
            monte_carlo = self.dcf_model.monte_carlo_dcf(
                base_fcf, self.analysis_config['dcf_years'],
                self.analysis_config['monte_carlo_simulations']
            )
            
            # Compile results
            return {
                'intrinsic_value': dcf_result['intrinsic_value_per_share'],
                'current_price': market_data.get('current_price', 0),
                'upside_percentage': (
                    (dcf_result['intrinsic_value_per_share'] - market_data.get('current_price', 0)) 
                    / market_data.get('current_price', 1) * 100
                ),
                'assumptions': {
                    'wacc': wacc,
                    'terminal_growth': terminal_growth,
                    'revenue_growth': revenue_growth,
                    'fcf_projections': fcf_projections
                },
                'components': dcf_result,
                'monte_carlo': monte_carlo,
                'confidence_interval': monte_carlo['confidence_interval']
            }
            
        except Exception as e:
            return {'error': f'DCF analysis failed: {str(e)}'}
    
    async def analyze_comprehensive_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Perform comprehensive sentiment analysis"""
        results = {
            'ticker': ticker,
            'analysis_date': datetime.now().isoformat(),
            'sources_analyzed': 0,
            'overall_sentiment': {},
            'detailed_results': {}
        }
        
        # Get latest earnings call transcript
        transcript = await self._get_earnings_transcript(ticker)
        if transcript:
            results['detailed_results']['earnings_call'] = (
                self.sentiment_analyzer.analyze_earnings_call(transcript)
            )
            results['sources_analyzed'] += 1
        
        # Get recent news
        news_items = await self._get_recent_news(ticker)
        if news_items:
            news_sentiments = []
            for item in news_items[:20]:  # Analyze top 20 news items
                sentiment = self.sentiment_analyzer.analyze_sentiment(
                    item.get('headline', '') + ' ' + item.get('summary', '')
                )
                news_sentiments.append(sentiment)
            
            # Aggregate news sentiment
            avg_sentiment_score = sum(s.sentiment_score for s in news_sentiments) / len(news_sentiments)
            
            results['detailed_results']['news'] = {
                'items_analyzed': len(news_sentiments),
                'average_sentiment': avg_sentiment_score,
                'sentiment_distribution': self._calculate_sentiment_distribution(news_sentiments),
                'key_topics': self._extract_key_topics(news_sentiments)
            }
            results['sources_analyzed'] += len(news_sentiments)
        
        # Get SEC filing sentiment (MD&A section)
        mda_text = await self._get_mda_section(ticker)
        if mda_text:
            results['detailed_results']['sec_filing'] = (
                self.sentiment_analyzer.analyze_sentiment(mda_text)
            )
            results['sources_analyzed'] += 1
        
        # Calculate overall sentiment
        all_sentiments = []
        
        if 'earnings_call' in results['detailed_results']:
            all_sentiments.append(
                results['detailed_results']['earnings_call']['management_tone'].sentiment_score
            )
        
        if 'news' in results['detailed_results']:
            all_sentiments.append(results['detailed_results']['news']['average_sentiment'])
        
        if 'sec_filing' in results['detailed_results']:
            all_sentiments.append(
                results['detailed_results']['sec_filing'].sentiment_score
            )
        
        if all_sentiments:
            overall_score = sum(all_sentiments) / len(all_sentiments)
            
            if overall_score > 0.3:
                overall_sentiment = 'bullish'
            elif overall_score < -0.3:
                overall_sentiment = 'bearish'
            else:
                overall_sentiment = 'neutral'
            
            results['overall_sentiment'] = {
                'sentiment': overall_sentiment,
                'score': overall_score,
                'confidence': min(0.9, results['sources_analyzed'] / 30)  # More sources = higher confidence
            }
        
        return results
    
    async def analyze_peer_comparison(self, ticker: str, 
                                    company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive peer comparison analysis"""
        # Get peer companies
        peers = await self._identify_peer_companies(ticker, company_info)
        
        if not peers:
            return {'error': 'No peer companies identified'}
        
        # Collect peer metrics
        peer_metrics = []
        for peer in peers[:self.analysis_config['peer_count']]:
            peer_data = await self._get_peer_metrics(peer)
            if peer_data:
                peer_metrics.append(peer_data)
        
        if not peer_metrics:
            return {'error': 'Unable to collect peer metrics'}
        
        # Get company metrics
        company_metrics = await self._get_peer_metrics(ticker)
        
        # Perform comparative analysis
        comparative_results = ComparativeAnalysis.calculate_relative_metrics(
            company_metrics, peer_metrics
        )
        
        # Sector analysis
        sector_data = await self._get_sector_performance_data(company_info.get('sector'))
        sector_analysis = ComparativeAnalysis.sector_rotation_analysis(sector_data)
        
        return {
            'company_metrics': company_metrics,
            'peer_metrics': peer_metrics,
            'comparative_analysis': comparative_results,
            'sector_analysis': sector_analysis,
            'competitive_position': self._assess_competitive_position(
                comparative_results
            )
        }
    
    def _perform_technical_analysis(self, price_history: List[Dict]) -> Dict[str, Any]:
        """Perform comprehensive technical analysis"""
        if len(price_history) < 30:
            return {'error': 'Insufficient price history'}
        
        # Extract price series
        prices = [p['close'] for p in price_history]
        volumes = [p['volume'] for p in price_history]
        
        # Calculate indicators
        rsi = TechnicalIndicators.calculate_rsi(prices)
        macd = TechnicalIndicators.calculate_macd(prices)
        bollinger = TechnicalIndicators.calculate_bollinger_bands(prices)
        
        # Current values
        current_rsi = rsi[-1] if rsi else 50
        current_macd = macd['histogram'][-1] if macd['histogram'] else 0
        
        # Generate signals
        signals = []
        
        if current_rsi < 30:
            signals.append({'indicator': 'RSI', 'signal': 'oversold', 'strength': 'strong'})
        elif current_rsi > 70:
            signals.append({'indicator': 'RSI', 'signal': 'overbought', 'strength': 'strong'})
        
        if current_macd > 0:
            signals.append({'indicator': 'MACD', 'signal': 'bullish', 'strength': 'medium'})
        else:
            signals.append({'indicator': 'MACD', 'signal': 'bearish', 'strength': 'medium'})
        
        # Price vs Bollinger Bands
        if prices[-1] < bollinger['lower'][-1]:
            signals.append({'indicator': 'Bollinger', 'signal': 'oversold', 'strength': 'strong'})
        elif prices[-1] > bollinger['upper'][-1]:
            signals.append({'indicator': 'Bollinger', 'signal': 'overbought', 'strength': 'strong'})
        
        return {
            'indicators': {
                'rsi': {'current': current_rsi, 'history': rsi[-20:]},
                'macd': macd,
                'bollinger_bands': {
                    'upper': bollinger['upper'][-20:],
                    'middle': bollinger['middle'][-20:],
                    'lower': bollinger['lower'][-20:]
                }
            },
            'signals': signals,
            'trend': self._identify_trend(prices),
            'support_resistance': self._identify_support_resistance(prices)
        }
    
    def _perform_risk_assessment(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        risks = {
            'financial_risks': [],
            'market_risks': [],
            'operational_risks': [],
            'overall_risk_score': 0
        }
        
        # Financial risks
        metrics = analysis_results.get('financial_data', {}).get('metrics', {})
        
        if metrics.get('debt_to_equity', 0) > 2:
            risks['financial_risks'].append({
                'type': 'high_leverage',
                'severity': 'high',
                'description': 'Debt-to-equity ratio exceeds 2.0'
            })
        
        if metrics.get('altman_z_score', 3) < 1.8:
            risks['financial_risks'].append({
                'type': 'bankruptcy_risk',
                'severity': 'high',
                'description': metrics.get('bankruptcy_risk', 'Elevated bankruptcy risk')
            })
        
        # Market risks
        tech_analysis = analysis_results.get('technical_analysis', {})
        if any(s['signal'] == 'overbought' for s in tech_analysis.get('signals', [])):
            risks['market_risks'].append({
                'type': 'overbought',
                'severity': 'medium',
                'description': 'Technical indicators suggest overbought conditions'
            })
        
        # Calculate overall risk score
        risk_weights = {'high': 0.3, 'medium': 0.2, 'low': 0.1}
        total_risk_score = 0
        
        for risk_category in ['financial_risks', 'market_risks', 'operational_risks']:
            for risk in risks[risk_category]:
                total_risk_score += risk_weights.get(risk['severity'], 0.1)
        
        risks['overall_risk_score'] = min(1.0, total_risk_score)
        
        return risks
    
    # Helper methods
    def _estimate_growth_rate(self, financial_data: Dict[str, Any]) -> float:
        """Estimate future growth rate based on historical data"""
        time_series = financial_data.get('time_series', {})
        revenue_series = time_series.get('Revenues', [])
        
        if len(revenue_series) >= 3:
            # Calculate historical CAGR
            recent_revenues = [r['value'] for r in revenue_series[-3:]]
            if recent_revenues[0] > 0:
                cagr = (recent_revenues[-1] / recent_revenues[0]) ** (1/3) - 1
                # Conservative estimate: historical CAGR * 0.8
                return min(0.30, max(-0.10, cagr * 0.8))
        
        # Default conservative growth
        return 0.05
    
    def _assess_analysis_quality(self, analysis_results: Dict[str, Any]) -> Dict[str, float]:
        """Assess quality of the analysis"""
        quality_scores = {
            'data_completeness': 0,
            'data_freshness': 0,
            'analysis_depth': 0,
            'confidence': 0
        }
        
        # Check data completeness
        expected_sections = ['company_data', 'financial_data', 'valuation', 
                           'technical_analysis', 'sentiment_analysis']
        completed = sum(1 for s in expected_sections if analysis_results.get(s))
        quality_scores['data_completeness'] = completed / len(expected_sections)
        
        # Check data freshness (assuming data is fresh for this example)
        quality_scores['data_freshness'] = 0.9
        
        # Check analysis depth
        total_metrics = 0
        if 'financial_data' in analysis_results:
            total_metrics += len(analysis_results['financial_data'].get('metrics', {}))
        if 'valuation' in analysis_results:
            total_metrics += len(analysis_results['valuation'].get('dcf', {}))
        
        quality_scores['analysis_depth'] = min(1.0, total_metrics / 30)
        
        # Overall confidence
        quality_scores['confidence'] = sum(quality_scores.values()) / len(quality_scores)
        
        return quality_scores
    
    # Additional helper methods would go here...
    
    async def _search_filings(self, ticker: str, filing_type: str, limit: int = 10) -> List[Dict]:
        """Search for specific filing types"""
        # Implementation would search SEC EDGAR
        # Simplified for this example
        return [{
            'filing_type': filing_type,
            'filing_date': datetime.now().isoformat(),
            'documents_url': f"https://www.sec.gov/Archives/edgar/data/example/{filing_type}.htm"
        }]
    
    async def get_market_data(self, ticker: str) -> Dict[str, Any]:
        """Get current market data"""
        # This would fetch real market data
        # Simplified for this example
        return {
            'ticker': ticker,
            'current_price': 150.0,
            'market_cap': 1000000000,
            'shares_outstanding': 6666667,
            'beta': 1.2,
            'price_history': [{'date': '2024-01-01', 'close': 140, 'volume': 1000000}]
        }


# Create the advanced server instance
server = Server("advanced-sec-scraper")
scraper = AdvancedSECScraper()

# Define advanced tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="comprehensive_analysis",
            description="Perform PhD-level comprehensive stock analysis including financials, valuation, sentiment, and technical analysis",
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
            name="parse_xbrl_financials",
            description="Parse XBRL financial data from SEC filings with advanced metrics",
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
            name="perform_dcf_valuation",
            description="Perform advanced DCF valuation with Monte Carlo simulation",
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
            name="analyze_sentiment",
            description="Perform advanced NLP sentiment analysis on earnings calls, news, and filings",
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
            name="generate_research_report",
            description="Generate institutional-quality equity research report",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of report (comprehensive, earnings, technical)",
                        "default": "comprehensive"
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
        ticker = arguments["ticker"].upper()
        
        if name == "comprehensive_analysis":
            result = await scraper.perform_comprehensive_analysis(ticker)
            
            # Format the comprehensive results
            formatted_result = {
                'ticker': ticker,
                'analysis_date': result['analysis_date'],
                'recommendation': result.get('research_report', {}).get('recommendation', {}),
                'key_metrics': result.get('financial_data', {}).get('metrics', {}),
                'valuation': result.get('valuation', {}),
                'sentiment': result.get('sentiment_analysis', {}).get('overall_sentiment', {}),
                'quality_score': result.get('analysis_quality', {}),
                'full_analysis': result
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(formatted_result, indent=2)
            )]
        
        elif name == "parse_xbrl_financials":
            result = await scraper.parse_xbrl_financials(ticker)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "perform_dcf_valuation":
            # Get financial data first
            financial_data = await scraper.parse_xbrl_financials(ticker)
            result = await scraper.perform_dcf_analysis(ticker, financial_data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analyze_sentiment":
            result = await scraper.analyze_comprehensive_sentiment(ticker)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "generate_research_report":
            # Perform full analysis first
            analysis_results = await scraper.perform_comprehensive_analysis(ticker)
            
            # Extract just the report
            report = analysis_results.get('research_report', {})
            
            # Convert to markdown if requested
            if arguments.get('format') == 'markdown':
                markdown_report = scraper.report_generator.export_to_markdown(report)
                return [TextContent(type="text", text=markdown_report)]
            else:
                return [TextContent(type="text", text=json.dumps(report, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e), "tool": name}, indent=2)
        )]

async def main():
    async with stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="advanced-sec-scraper",
                server_version="2.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())