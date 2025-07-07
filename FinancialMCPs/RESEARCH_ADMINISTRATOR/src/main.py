#!/usr/bin/env python

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import re
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

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


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("research-administrator")


class ResearchDepth(Enum):
    QUICK_CHECK = "quick"  # 5 minutes
    STANDARD = "standard"  # 15 minutes
    DEEP_DIVE = "deep"  # 45 minutes
    SECTOR_ANALYSIS = "sector"  # 2+ hours


@dataclass
class ResearchRequest:
    ticker: str
    depth: ResearchDepth
    focus_areas: List[str]
    compare_peers: bool = False
    sector: Optional[str] = None


class ResearchAdministrator:
    """Master orchestrator for financial research reports using multiple MCPs"""
    
    def __init__(self):
        self.mcp_tools = {
            'SEC_SCRAPER': [
                'scrape_10k_financials',
                'scrape_10q_earnings', 
                'scrape_8k_events',
                'get_current_price'
            ],
            'NEWS_SENTIMENT': [
                'get_aggregate_sentiment',
                'search_financial_news',
                'get_sector_sentiment'
            ],
            'ANALYST_RATINGS': [
                'get_consensus_rating',
                'get_price_targets',
                'get_rating_changes'
            ],
            'INSTITUTIONAL': [
                'get_institutional_ownership',
                'get_insider_trading',
                'track_institutional_changes'
            ],
            'ALTERNATIVE_DATA': [
                'analyze_hiring_trends',
                'get_web_traffic_data',
                'comprehensive_alternative_data'
            ],
            'INDUSTRY_ASSUMPTIONS': [
                'generate_full_dcf_assumptions',
                'get_valuation_multiples',
                'calculate_wacc'
            ],
            'ECONOMIC_DATA': [
                'get_economic_dashboard',
                'get_treasury_yields'
            ]
        }
        
        self.report_templates = {
            ResearchDepth.QUICK_CHECK: self._quick_check_template,
            ResearchDepth.STANDARD: self._standard_analysis_template,
            ResearchDepth.DEEP_DIVE: self._deep_dive_template,
            ResearchDepth.SECTOR_ANALYSIS: self._sector_analysis_template
        }
        
        # Initialize advanced components
        self.analysis_enhanced = True
    
    def _format_mcp_call(self, mcp: str, tool: str, params: Dict) -> str:
        """Format a call instruction for an MCP tool"""
        return f"Use {mcp} MCP's {tool} with parameters: {json.dumps(params)}"
    
    async def generate_research_plan(self, request: ResearchRequest) -> Dict[str, Any]:
        """Generate a research plan based on the request"""
        plan = {
            'ticker': request.ticker,
            'depth': request.depth.value,
            'timestamp': datetime.now().isoformat(),
            'data_collection_phases': [],
            'estimated_time': self._estimate_time(request.depth),
            'output_format': self._get_output_format(request.depth)
        }
        
        # Phase 1: Foundation Data (Always collected)
        phase1 = {
            'phase': 'Foundation Data',
            'parallel_execution': True,
            'mcp_calls': [
                self._format_mcp_call('SEC_SCRAPER', 'scrape_10k_financials', {'ticker': request.ticker}),
                self._format_mcp_call('SEC_SCRAPER', 'get_current_price', {'ticker': request.ticker}),
                self._format_mcp_call('INDUSTRY_ASSUMPTIONS', 'generate_full_dcf_assumptions', 
                                    {'ticker': request.ticker, 'industry': request.sector or 'technology'})
            ]
        }
        plan['data_collection_phases'].append(phase1)
        
        # Phase 2: Market Intelligence (Standard and above)
        if request.depth in [ResearchDepth.STANDARD, ResearchDepth.DEEP_DIVE, ResearchDepth.SECTOR_ANALYSIS]:
            phase2 = {
                'phase': 'Market Intelligence',
                'parallel_execution': True,
                'mcp_calls': [
                    self._format_mcp_call('NEWS_SENTIMENT', 'get_aggregate_sentiment', {'ticker': request.ticker}),
                    self._format_mcp_call('ANALYST_RATINGS', 'get_consensus_rating', {'ticker': request.ticker}),
                    self._format_mcp_call('INSTITUTIONAL', 'track_institutional_changes', {'ticker': request.ticker})
                ]
            }
            plan['data_collection_phases'].append(phase2)
        
        # Phase 3: Alternative Signals (Deep dive and above)
        if request.depth in [ResearchDepth.DEEP_DIVE, ResearchDepth.SECTOR_ANALYSIS]:
            phase3 = {
                'phase': 'Alternative Signals',
                'parallel_execution': True,
                'mcp_calls': [
                    self._format_mcp_call('ALTERNATIVE_DATA', 'comprehensive_alternative_data', 
                                        {'company': request.ticker, 'ticker': request.ticker}),
                    self._format_mcp_call('ECONOMIC_DATA', 'get_economic_dashboard', {})
                ]
            }
            plan['data_collection_phases'].append(phase3)
        
        # Phase 4: Sector Analysis (Sector depth only)
        if request.depth == ResearchDepth.SECTOR_ANALYSIS and request.compare_peers:
            phase4 = {
                'phase': 'Peer Comparison',
                'parallel_execution': False,
                'mcp_calls': [
                    self._format_mcp_call('ANALYST_RATINGS', 'compare_analyst_coverage', 
                                        {'tickers': [request.ticker, 'PEER1', 'PEER2']}),
                    self._format_mcp_call('NEWS_SENTIMENT', 'get_sector_sentiment', 
                                        {'sector': request.sector, 'top_stocks': [request.ticker, 'PEER1', 'PEER2']})
                ]
            }
            plan['data_collection_phases'].append(phase4)
        
        return plan
    
    def _estimate_time(self, depth: ResearchDepth) -> str:
        """Estimate research completion time"""
        times = {
            ResearchDepth.QUICK_CHECK: "5 minutes",
            ResearchDepth.STANDARD: "15 minutes",
            ResearchDepth.DEEP_DIVE: "45 minutes",
            ResearchDepth.SECTOR_ANALYSIS: "2+ hours"
        }
        return times.get(depth, "15 minutes")
    
    def _get_output_format(self, depth: ResearchDepth) -> List[str]:
        """Get expected output sections based on depth"""
        formats = {
            ResearchDepth.QUICK_CHECK: [
                "Executive Summary",
                "Current Valuation",
                "Basic DCF Analysis",
                "Analyst Consensus",
                "Investment Recommendation"
            ],
            ResearchDepth.STANDARD: [
                "Executive Summary",
                "Financial Overview",
                "DCF Valuation with Sensitivity",
                "Multi-Source Sentiment Analysis",
                "Institutional Activity",
                "Alternative Data Signals",
                "Wall Street Consensus",
                "Bull & Bear Cases",
                "Investment Thesis",
                "Risk Factors",
                "12-Month Price Target"
            ],
            ResearchDepth.DEEP_DIVE: [
                "Executive Summary",
                "Comprehensive Financial Analysis",
                "Multiple DCF Scenarios",
                "Historical Performance Patterns",
                "Competitive Positioning",
                "Management Assessment",
                "Detailed Risk Framework",
                "Alternative Data Deep Dive",
                "Technical Analysis",
                "Scenario Analysis",
                "Investment Recommendation with Conviction"
            ],
            ResearchDepth.SECTOR_ANALYSIS: [
                "Sector Overview",
                "Macro Trends Analysis",
                "Top 10 Companies Ranking",
                "Industry-Wide DCF Comparison",
                "Relative Value Analysis",
                "Sector Rotation Signals",
                "Thematic Opportunities",
                "Risk/Reward Matrix",
                "Portfolio Recommendations"
            ]
        }
        return formats.get(depth, formats[ResearchDepth.STANDARD])
    
    def _quick_check_template(self, data: Dict[str, Any]) -> str:
        """Generate quick check report template"""
        return f"""# Quick Investment Check: {data.get('company_name', 'N/A')} ({data.get('ticker', 'N/A')})
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Analysis Depth: Quick Check (5 minutes)*

## Current Snapshot
**Price:** ${data.get('current_price', 'N/A')}
**Market Cap:** ${data.get('market_cap', 'N/A')}
**P/E Ratio:** {data.get('pe_ratio', 'N/A')}

## Quick DCF Valuation
**Fair Value:** ${data.get('dcf_value', 'N/A')}
**Upside/Downside:** {data.get('valuation_delta', 'N/A')}%

## Analyst View
**Consensus:** {data.get('analyst_consensus', 'N/A')}
**Price Target:** ${data.get('analyst_target', 'N/A')}

## Investment Signal
**Recommendation:** {data.get('recommendation', 'HOLD')}
**Key Point:** {data.get('key_thesis', 'N/A')}
"""
    
    def _standard_analysis_template(self, data: Dict[str, Any]) -> str:
        """Generate standard analysis report template"""
        return f"""# Investment Analysis: {data.get('company_name', 'N/A')} ({data.get('ticker', 'N/A')})
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Analysis Depth: Standard (15 minutes)*

## Executive Summary
**Investment Recommendation:** {data.get('recommendation', 'HOLD')}
**Price Target:** ${data.get('price_target', 'N/A')} (vs current ${data.get('current_price', 'N/A')})
**Key Thesis:** {data.get('investment_thesis', 'N/A')}

## Financial Overview
**Current Valuation:**
- Market Cap: ${data.get('market_cap', 'N/A')}
- P/E Ratio: {data.get('pe_ratio', 'N/A')} (vs industry avg {data.get('industry_pe', 'N/A')})
- EV/Revenue: {data.get('ev_revenue', 'N/A')} (vs peers {data.get('peer_ev_revenue', 'N/A')})

**DCF Valuation:**
- Fair Value: ${data.get('dcf_value', 'N/A')}
- Industry Growth Assumption: {data.get('growth_rate', 'N/A')}%
- Discount Rate: {data.get('discount_rate', 'N/A')}%
- Sensitivity Range: ${data.get('dcf_low', 'N/A')} - ${data.get('dcf_high', 'N/A')}

## Data Synthesis
**Sentiment Analysis:**
- News Sentiment: {data.get('news_sentiment', 'N/A')} ({data.get('news_trend', 'N/A')})
- Social Media: {data.get('social_sentiment', 'N/A')} ({data.get('social_trend', 'N/A')})

**Institutional Activity:**
- Smart Money Flow: {data.get('institutional_flow', 'N/A')}
- Notable Moves: {data.get('institutional_changes', 'N/A')}
- Insider Trading: {data.get('insider_summary', 'N/A')}

**Alternative Data Signals:**
- Hiring Trends: {data.get('hiring_trend', 'N/A')}
- Web Traffic: {data.get('web_traffic_trend', 'N/A')}
- Patent Activity: {data.get('patent_activity', 'N/A')}

**Wall Street Consensus:**
- Rating: {data.get('analyst_rating', 'N/A')} ({data.get('num_analysts', 'N/A')} analysts)
- Average Target: ${data.get('avg_analyst_target', 'N/A')}
- Recent Changes: {data.get('rating_changes', 'N/A')}

## Investment Thesis

### Bull Case 🚀
{data.get('bull_case', 'N/A')}

### Bear Case 🐻
{data.get('bear_case', 'N/A')}

## Risk Factors
{data.get('risk_factors', 'N/A')}

## Recommendation
**Action:** {data.get('action', 'HOLD')}
**Conviction Level:** {data.get('conviction', 'Medium')}
**Time Horizon:** {data.get('time_horizon', '12 months')}
"""
    
    def _deep_dive_template(self, data: Dict[str, Any]) -> str:
        """Generate deep dive report template"""
        # This would be a much more comprehensive 10-15 page report
        return f"""# Comprehensive Research Report: {data.get('company_name', 'N/A')}
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Analysis Depth: Deep Dive (45 minutes)*

[Full 10-15 page report with detailed sections...]
"""
    
    def _sector_analysis_template(self, data: Dict[str, Any]) -> str:
        """Generate sector analysis report template"""
        return f"""# Sector Analysis: {data.get('sector', 'N/A')}
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Analysis Depth: Sector Analysis (2+ hours)*

[Comprehensive sector report with peer comparisons...]
"""
    
    async def coordinate_research(self, 
                                 ticker: str, 
                                 depth: str = "standard",
                                 focus_areas: Optional[List[str]] = None,
                                 sector: Optional[str] = None) -> Dict[str, Any]:
        """Main coordination function that orchestrates all MCPs"""
        
        # Parse research depth
        try:
            research_depth = ResearchDepth(depth)
        except ValueError:
            research_depth = ResearchDepth.STANDARD
        
        # Create research request
        request = ResearchRequest(
            ticker=ticker.upper(),
            depth=research_depth,
            focus_areas=focus_areas or [],
            compare_peers=depth == "sector",
            sector=sector
        )
        
        # Generate research plan
        plan = await self.generate_research_plan(request)
        
        # Create data collection instructions
        instructions = {
            'research_plan': plan,
            'execution_instructions': self._generate_execution_instructions(plan),
            'report_template': self._get_report_template_name(research_depth)
        }
        
        return instructions
    
    def _generate_execution_instructions(self, plan: Dict[str, Any]) -> List[str]:
        """Generate step-by-step execution instructions"""
        instructions = []
        
        instructions.append(f"Research Plan for {plan['ticker']} - Estimated Time: {plan['estimated_time']}")
        instructions.append("\nData Collection Phases:")
        
        for i, phase in enumerate(plan['data_collection_phases'], 1):
            instructions.append(f"\n{i}. {phase['phase']} {'(Parallel Execution)' if phase['parallel_execution'] else '(Sequential Execution)'}")
            for call in phase['mcp_calls']:
                instructions.append(f"   - {call}")
        
        instructions.append(f"\nExpected Output Sections: {', '.join(plan['output_format'])}")
        
        return instructions
    
    def _get_report_template_name(self, depth: ResearchDepth) -> str:
        """Get the appropriate report template name"""
        templates = {
            ResearchDepth.QUICK_CHECK: "Quick Check Template",
            ResearchDepth.STANDARD: "Standard Analysis Template", 
            ResearchDepth.DEEP_DIVE: "Deep Dive Template",
            ResearchDepth.SECTOR_ANALYSIS: "Sector Analysis Template"
        }
        return templates.get(depth, "Standard Analysis Template")
    
    async def generate_report_outline(self, ticker: str, collected_data: Dict[str, Any]) -> str:
        """Generate a report outline based on collected data"""
        outline = f"""# Research Report Outline: {ticker}

## Data Collection Summary
- SEC Filings: {'✓' if 'sec_data' in collected_data else '✗'}
- Market Sentiment: {'✓' if 'sentiment_data' in collected_data else '✗'}
- Analyst Ratings: {'✓' if 'analyst_data' in collected_data else '✗'}
- Institutional Data: {'✓' if 'institutional_data' in collected_data else '✗'}
- Alternative Data: {'✓' if 'alternative_data' in collected_data else '✗'}
- DCF Assumptions: {'✓' if 'dcf_data' in collected_data else '✗'}
- Economic Context: {'✓' if 'economic_data' in collected_data else '✗'}

## Key Findings to Highlight
1. Valuation: [DCF vs Market Price]
2. Sentiment: [Aggregate score and trend]
3. Institutional: [Smart money flow direction]
4. Alternative: [Key growth indicators]
5. Macro: [Economic tailwinds/headwinds]

## Report Sections to Generate
Based on the data collected, the report should include:
{self._suggest_sections(collected_data)}

## Investment Recommendation Framework
- Quantitative Score: [Based on DCF and multiples]
- Qualitative Score: [Based on sentiment and alternatives]
- Risk Assessment: [Based on macro and company-specific]
- Final Rating: [BUY/HOLD/SELL with conviction level]
"""
        return outline
    
    def _suggest_sections(self, data: Dict[str, Any]) -> str:
        """Suggest report sections based on available data"""
        sections = []
        
        if 'sec_data' in data:
            sections.append("- Financial Analysis and Trends")
        if 'dcf_data' in data:
            sections.append("- Valuation Analysis with DCF Model")
        if 'sentiment_data' in data:
            sections.append("- Market Sentiment and News Flow")
        if 'analyst_data' in data:
            sections.append("- Wall Street Perspective")
        if 'institutional_data' in data:
            sections.append("- Smart Money Analysis")
        if 'alternative_data' in data:
            sections.append("- Alternative Data Insights")
        if 'economic_data' in data:
            sections.append("- Macroeconomic Context")
        
        return '\n'.join(sections) if sections else "- Standard analysis sections"
    
    async def create_research_commands(self, request: str) -> List[Dict[str, Any]]:
        """Parse natural language request and create MCP commands"""
        commands = []
        
        # Extract ticker
        ticker_match = re.search(r'\b([A-Z]{1,5})\b', request.upper())
        if not ticker_match:
            return [{'error': 'No ticker symbol found in request'}]
        
        ticker = ticker_match.group(1)
        
        # Determine research depth
        depth = ResearchDepth.STANDARD
        if 'quick' in request.lower():
            depth = ResearchDepth.QUICK_CHECK
        elif 'deep' in request.lower() or 'comprehensive' in request.lower():
            depth = ResearchDepth.DEEP_DIVE
        elif 'sector' in request.lower():
            depth = ResearchDepth.SECTOR_ANALYSIS
        
        # Create command sequence based on depth
        if depth == ResearchDepth.QUICK_CHECK:
            commands = [
                {'mcp': 'SEC_SCRAPER', 'tool': 'get_current_price', 'params': {'ticker': ticker}},
                {'mcp': 'INDUSTRY_ASSUMPTIONS', 'tool': 'generate_full_dcf_assumptions', 'params': {'ticker': ticker, 'industry': 'technology'}},
                {'mcp': 'ANALYST_RATINGS', 'tool': 'get_consensus_rating', 'params': {'ticker': ticker}}
            ]
        else:
            # Standard or deeper analysis
            commands = [
                # Phase 1: Foundation
                {'mcp': 'SEC_SCRAPER', 'tool': 'scrape_10k_financials', 'params': {'ticker': ticker}},
                {'mcp': 'SEC_SCRAPER', 'tool': 'get_current_price', 'params': {'ticker': ticker}},
                {'mcp': 'INDUSTRY_ASSUMPTIONS', 'tool': 'generate_full_dcf_assumptions', 'params': {'ticker': ticker, 'industry': 'technology'}},
                # Phase 2: Market Intelligence
                {'mcp': 'NEWS_SENTIMENT', 'tool': 'get_aggregate_sentiment', 'params': {'ticker': ticker}},
                {'mcp': 'ANALYST_RATINGS', 'tool': 'get_consensus_rating', 'params': {'ticker': ticker}},
                {'mcp': 'INSTITUTIONAL', 'tool': 'track_institutional_changes', 'params': {'ticker': ticker}}
            ]
            
            if depth in [ResearchDepth.DEEP_DIVE, ResearchDepth.SECTOR_ANALYSIS]:
                # Phase 3: Alternative signals
                commands.extend([
                    {'mcp': 'ALTERNATIVE_DATA', 'tool': 'comprehensive_alternative_data', 'params': {'company': ticker, 'ticker': ticker}},
                    {'mcp': 'ECONOMIC_DATA', 'tool': 'get_economic_dashboard', 'params': {}}
                ])
        
        return commands


# Initialize server
server = Server("research-administrator")
administrator = ResearchAdministrator()

# Define tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="create_research_plan",
            description="Create a comprehensive research plan for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "depth": {
                        "type": "string",
                        "description": "Research depth: quick, standard, deep, or sector",
                        "enum": ["quick", "standard", "deep", "sector"],
                        "default": "standard"
                    },
                    "focus_areas": {
                        "type": "array",
                        "description": "Specific areas to focus on",
                        "items": {"type": "string"}
                    },
                    "sector": {
                        "type": "string",
                        "description": "Industry sector for the company"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="parse_research_request",
            description="Parse a natural language research request into MCP commands",
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "Natural language research request"
                    }
                },
                "required": ["request"]
            }
        ),
        Tool(
            name="generate_report_outline",
            description="Generate a report outline based on collected data",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "collected_data": {
                        "type": "object",
                        "description": "Summary of data collected from MCPs"
                    }
                },
                "required": ["ticker", "collected_data"]
            }
        ),
        Tool(
            name="list_available_mcps",
            description="List all available MCPs and their tools",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="generate_executive_summary",
            description="Generate an executive summary from research data",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "key_findings": {
                        "type": "object",
                        "description": "Key findings from research"
                    }
                },
                "required": ["ticker", "key_findings"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    
    try:
        if name == "create_research_plan":
            ticker = arguments["ticker"].upper()
            depth = arguments.get("depth", "standard")
            focus_areas = arguments.get("focus_areas", [])
            sector = arguments.get("sector")
            
            plan = await administrator.coordinate_research(ticker, depth, focus_areas, sector)
            
            return [TextContent(
                type="text",
                text=json.dumps(plan, indent=2)
            )]
        
        elif name == "parse_research_request":
            request = arguments["request"]
            commands = await administrator.create_research_commands(request)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    'original_request': request,
                    'mcp_commands': commands,
                    'execution_order': 'Execute in sequence as listed'
                }, indent=2)
            )]
        
        elif name == "generate_report_outline":
            ticker = arguments["ticker"].upper()
            collected_data = arguments["collected_data"]
            
            outline = await administrator.generate_report_outline(ticker, collected_data)
            
            return [TextContent(
                type="text",
                text=outline
            )]
        
        elif name == "list_available_mcps":
            mcp_list = {
                'available_mcps': administrator.mcp_tools,
                'total_tools': sum(len(tools) for tools in administrator.mcp_tools.values()),
                'research_depths': [d.value for d in ResearchDepth],
                'coordination_capability': 'Can orchestrate all MCPs in parallel or sequence'
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(mcp_list, indent=2)
            )]
        
        elif name == "generate_executive_summary":
            ticker = arguments["ticker"].upper()
            key_findings = arguments["key_findings"]
            
            summary = f"""## Executive Summary: {ticker}

**Investment Recommendation:** {key_findings.get('recommendation', 'HOLD')}
**Price Target:** ${key_findings.get('price_target', 'N/A')} ({key_findings.get('upside', 'N/A')}% upside)
**Conviction Level:** {key_findings.get('conviction', 'Medium')}

**Key Investment Points:**
1. **Valuation:** {key_findings.get('valuation_thesis', 'Stock appears fairly valued based on DCF analysis')}
2. **Momentum:** {key_findings.get('momentum_thesis', 'Mixed signals from sentiment and institutional flows')}
3. **Growth:** {key_findings.get('growth_thesis', 'Alternative data suggests stable growth trajectory')}

**Primary Risk:** {key_findings.get('main_risk', 'Macroeconomic uncertainty')}
**Catalyst:** {key_findings.get('catalyst', 'Next earnings report')}
"""
            
            return [TextContent(
                type="text",
                text=summary
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
                server_name="research-administrator",
                server_version="0.1.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())