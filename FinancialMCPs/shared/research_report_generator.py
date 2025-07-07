#!/usr/bin/env python3
"""
PhD-Level Financial Research Report Generator
Produces institutional-quality equity research reports
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from enum import Enum


class RecommendationType(Enum):
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"


@dataclass
class InvestmentThesis:
    """Core investment thesis"""
    bull_case: List[str]
    bear_case: List[str]
    base_case_scenario: str
    key_catalysts: List[Dict[str, Any]]
    risk_factors: List[Dict[str, Any]]
    time_horizon: str


class ResearchReportGenerator:
    """Generate institutional-quality research reports"""
    
    def __init__(self):
        self.report_sections = [
            'executive_summary',
            'investment_thesis',
            'company_overview',
            'financial_analysis',
            'valuation',
            'competitive_analysis',
            'risk_assessment',
            'technical_analysis',
            'recommendation'
        ]
    
    def generate_comprehensive_report(self, 
                                    company_data: Dict[str, Any],
                                    market_data: Dict[str, Any],
                                    analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete equity research report"""
        
        report = {
            'metadata': self._generate_metadata(company_data),
            'executive_summary': self._generate_executive_summary(company_data, analysis_results),
            'investment_thesis': self._generate_investment_thesis(company_data, analysis_results),
            'company_overview': self._generate_company_overview(company_data),
            'financial_analysis': self._generate_financial_analysis(company_data, analysis_results),
            'valuation': self._generate_valuation_section(company_data, analysis_results),
            'competitive_analysis': self._generate_competitive_analysis(company_data, market_data),
            'risk_assessment': self._generate_risk_assessment(company_data, analysis_results),
            'technical_analysis': self._generate_technical_analysis(market_data),
            'recommendation': self._generate_recommendation(analysis_results),
            'appendix': self._generate_appendix(company_data, analysis_results)
        }
        
        # Add quality score
        report['quality_metrics'] = self._assess_report_quality(report)
        
        return report
    
    def _generate_metadata(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            'report_date': datetime.now().isoformat(),
            'ticker': company_data.get('ticker', 'N/A'),
            'company_name': company_data.get('company_name', 'N/A'),
            'sector': company_data.get('sector', 'N/A'),
            'industry': company_data.get('industry', 'N/A'),
            'report_type': 'Comprehensive Equity Research',
            'analyst': 'AI Research System',
            'version': '2.0'
        }
    
    def _generate_executive_summary(self, company_data: Dict[str, Any], 
                                  analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary section"""
        
        # Extract key metrics
        current_price = company_data.get('current_price', 0)
        target_price = analysis_results.get('valuation', {}).get('target_price', 0)
        upside = ((target_price - current_price) / current_price * 100) if current_price > 0 else 0
        
        # Determine recommendation
        recommendation = self._determine_recommendation(upside, analysis_results)
        
        summary = {
            'recommendation': recommendation.value,
            'current_price': current_price,
            'target_price': target_price,
            'upside_downside': f"{upside:+.1f}%",
            'investment_horizon': '12 months',
            'key_points': []
        }
        
        # Generate key investment points
        key_points = []
        
        # Financial performance
        financial_metrics = analysis_results.get('financial_metrics', {})
        if financial_metrics.get('revenue_growth', 0) > 0.15:
            key_points.append(f"Strong revenue growth of {financial_metrics['revenue_growth']*100:.1f}%")
        
        if financial_metrics.get('roe', 0) > 0.15:
            key_points.append(f"Attractive ROE of {financial_metrics['roe']*100:.1f}%")
        
        # Valuation
        if analysis_results.get('valuation', {}).get('pe_ratio', 0) < 15:
            key_points.append("Attractive valuation with P/E below market average")
        
        # Market position
        if analysis_results.get('competitive_position', {}).get('market_share_rank', 5) <= 3:
            key_points.append("Strong competitive position in the industry")
        
        # Risks
        risk_score = analysis_results.get('risk_assessment', {}).get('overall_risk_score', 0.5)
        if risk_score > 0.7:
            key_points.append("Elevated risk profile requires careful monitoring")
        
        summary['key_points'] = key_points[:5]  # Top 5 points
        
        # Add summary narrative
        summary['narrative'] = self._generate_summary_narrative(
            company_data, recommendation, upside, key_points
        )
        
        return summary
    
    def _generate_investment_thesis(self, company_data: Dict[str, Any],
                                  analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment thesis section"""
        
        thesis = InvestmentThesis(
            bull_case=[],
            bear_case=[],
            base_case_scenario="",
            key_catalysts=[],
            risk_factors=[],
            time_horizon="12 months"
        )
        
        # Bull case points
        financial_metrics = analysis_results.get('financial_metrics', {})
        
        if financial_metrics.get('revenue_growth', 0) > 0.10:
            thesis.bull_case.append(
                f"Revenue growing at {financial_metrics['revenue_growth']*100:.1f}% annually"
            )
        
        if financial_metrics.get('fcf_yield', 0) > 0.05:
            thesis.bull_case.append(
                f"Strong FCF yield of {financial_metrics['fcf_yield']*100:.1f}%"
            )
        
        if analysis_results.get('competitive_position', {}).get('moat_score', 0) > 0.7:
            thesis.bull_case.append("Wide economic moat protects competitive position")
        
        if analysis_results.get('sentiment', {}).get('overall_sentiment') == 'bullish':
            thesis.bull_case.append("Positive market sentiment and analyst coverage")
        
        # Bear case points
        if financial_metrics.get('debt_to_equity', 0) > 1.5:
            thesis.bear_case.append(
                f"High leverage with D/E ratio of {financial_metrics['debt_to_equity']:.1f}"
            )
        
        if analysis_results.get('risk_assessment', {}).get('regulatory_risk', 0) > 0.7:
            thesis.bear_case.append("Significant regulatory risks could impact operations")
        
        if financial_metrics.get('revenue_growth', 0) < 0:
            thesis.bear_case.append("Declining revenues indicate market challenges")
        
        # Base case scenario
        thesis.base_case_scenario = self._generate_base_case_scenario(
            company_data, financial_metrics
        )
        
        # Key catalysts
        thesis.key_catalysts = self._identify_catalysts(company_data, analysis_results)
        
        # Risk factors
        thesis.risk_factors = self._identify_key_risks(analysis_results)
        
        return {
            'bull_case': thesis.bull_case,
            'bear_case': thesis.bear_case,
            'base_case': thesis.base_case_scenario,
            'catalysts': thesis.key_catalysts,
            'risks': thesis.risk_factors,
            'conviction_level': self._calculate_conviction_level(thesis)
        }
    
    def _generate_financial_analysis(self, company_data: Dict[str, Any],
                                   analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed financial analysis section"""
        
        financial_analysis = {
            'income_statement_analysis': {},
            'balance_sheet_analysis': {},
            'cash_flow_analysis': {},
            'profitability_metrics': {},
            'efficiency_metrics': {},
            'trend_analysis': {}
        }
        
        metrics = analysis_results.get('financial_metrics', {})
        
        # Income statement analysis
        financial_analysis['income_statement_analysis'] = {
            'revenue_trend': self._analyze_trend(
                analysis_results.get('historical_data', {}).get('revenue', [])
            ),
            'margin_analysis': {
                'gross_margin': metrics.get('gross_margin', 0),
                'operating_margin': metrics.get('operating_margin', 0),
                'net_margin': metrics.get('net_margin', 0),
                'margin_trend': 'expanding' if metrics.get('margin_change', 0) > 0 else 'contracting'
            },
            'earnings_quality': self._assess_earnings_quality(metrics)
        }
        
        # Balance sheet analysis
        financial_analysis['balance_sheet_analysis'] = {
            'liquidity': {
                'current_ratio': metrics.get('current_ratio', 0),
                'quick_ratio': metrics.get('quick_ratio', 0),
                'cash_position': metrics.get('cash_per_share', 0)
            },
            'leverage': {
                'debt_to_equity': metrics.get('debt_to_equity', 0),
                'debt_to_assets': metrics.get('debt_to_assets', 0),
                'interest_coverage': metrics.get('interest_coverage', 0)
            },
            'asset_quality': self._assess_asset_quality(metrics)
        }
        
        # Cash flow analysis
        financial_analysis['cash_flow_analysis'] = {
            'operating_cash_flow': metrics.get('operating_cash_flow', 0),
            'free_cash_flow': metrics.get('free_cash_flow', 0),
            'fcf_conversion': metrics.get('fcf_conversion_rate', 0),
            'capex_intensity': metrics.get('capex_to_revenue', 0),
            'cash_flow_stability': self._assess_cash_flow_stability(
                analysis_results.get('historical_data', {})
            )
        }
        
        # Profitability metrics
        financial_analysis['profitability_metrics'] = {
            'roe': metrics.get('roe', 0),
            'roa': metrics.get('roa', 0),
            'roic': metrics.get('roic', 0),
            'dupont_analysis': self._perform_dupont_analysis(metrics)
        }
        
        # Efficiency metrics
        financial_analysis['efficiency_metrics'] = {
            'asset_turnover': metrics.get('asset_turnover', 0),
            'inventory_turnover': metrics.get('inventory_turnover', 0),
            'receivables_turnover': metrics.get('receivables_turnover', 0),
            'cash_conversion_cycle': metrics.get('cash_conversion_cycle', 0)
        }
        
        # Trend analysis
        financial_analysis['trend_analysis'] = {
            'revenue_cagr_3y': self._calculate_cagr(
                analysis_results.get('historical_data', {}).get('revenue', []), 3
            ),
            'earnings_cagr_3y': self._calculate_cagr(
                analysis_results.get('historical_data', {}).get('earnings', []), 3
            ),
            'fcf_cagr_3y': self._calculate_cagr(
                analysis_results.get('historical_data', {}).get('fcf', []), 3
            )
        }
        
        return financial_analysis
    
    def _generate_valuation_section(self, company_data: Dict[str, Any],
                                  analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive valuation analysis"""
        
        valuation = {
            'current_valuation': {},
            'dcf_analysis': {},
            'relative_valuation': {},
            'sum_of_parts': {},
            'target_price_calculation': {},
            'sensitivity_analysis': {}
        }
        
        current_price = company_data.get('current_price', 0)
        valuation_results = analysis_results.get('valuation', {})
        
        # Current valuation metrics
        valuation['current_valuation'] = {
            'market_cap': company_data.get('market_cap', 0),
            'enterprise_value': company_data.get('enterprise_value', 0),
            'pe_ratio': valuation_results.get('pe_ratio', 0),
            'ev_ebitda': valuation_results.get('ev_ebitda', 0),
            'price_to_book': valuation_results.get('price_to_book', 0),
            'peg_ratio': valuation_results.get('peg_ratio', 0)
        }
        
        # DCF analysis
        dcf_results = valuation_results.get('dcf', {})
        valuation['dcf_analysis'] = {
            'intrinsic_value': dcf_results.get('intrinsic_value', 0),
            'assumptions': {
                'wacc': dcf_results.get('wacc', 0.10),
                'terminal_growth': dcf_results.get('terminal_growth', 0.025),
                'fcf_growth_rate': dcf_results.get('fcf_growth_rate', 0.05)
            },
            'monte_carlo_results': dcf_results.get('monte_carlo', {})
        }
        
        # Relative valuation
        valuation['relative_valuation'] = {
            'peer_comparison': valuation_results.get('peer_comparison', {}),
            'sector_premium_discount': valuation_results.get('sector_premium', 0),
            'historical_valuation': valuation_results.get('historical_valuation', {})
        }
        
        # Target price calculation
        weights = {
            'dcf': 0.4,
            'relative': 0.3,
            'historical': 0.2,
            'technical': 0.1
        }
        
        target_prices = {
            'dcf': dcf_results.get('intrinsic_value', current_price),
            'relative': valuation_results.get('relative_target', current_price),
            'historical': valuation_results.get('historical_target', current_price),
            'technical': valuation_results.get('technical_target', current_price)
        }
        
        weighted_target = sum(
            target_prices[method] * weight 
            for method, weight in weights.items()
        )
        
        valuation['target_price_calculation'] = {
            'method_targets': target_prices,
            'weights': weights,
            'weighted_target_price': weighted_target,
            'upside_downside': ((weighted_target - current_price) / current_price * 100)
        }
        
        # Sensitivity analysis
        valuation['sensitivity_analysis'] = self._perform_sensitivity_analysis(
            dcf_results, current_price
        )
        
        return valuation
    
    def _generate_risk_assessment(self, company_data: Dict[str, Any],
                                analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment"""
        
        risk_assessment = {
            'systematic_risks': [],
            'company_specific_risks': [],
            'financial_risks': [],
            'operational_risks': [],
            'risk_matrix': {},
            'risk_mitigation': []
        }
        
        risk_data = analysis_results.get('risk_assessment', {})
        
        # Systematic risks
        if risk_data.get('market_beta', 1) > 1.2:
            risk_assessment['systematic_risks'].append({
                'risk': 'High market sensitivity',
                'impact': 'high',
                'probability': 'medium',
                'description': f'Beta of {risk_data["market_beta"]:.2f} indicates above-average market risk'
            })
        
        if risk_data.get('sector_correlation', 0) > 0.8:
            risk_assessment['systematic_risks'].append({
                'risk': 'Sector concentration',
                'impact': 'medium',
                'probability': 'high',
                'description': 'High correlation with sector performance'
            })
        
        # Company-specific risks
        if risk_data.get('customer_concentration', 0) > 0.3:
            risk_assessment['company_specific_risks'].append({
                'risk': 'Customer concentration',
                'impact': 'high',
                'probability': 'medium',
                'description': 'Significant revenue concentration in few customers'
            })
        
        if risk_data.get('key_person_risk', False):
            risk_assessment['company_specific_risks'].append({
                'risk': 'Key person dependency',
                'impact': 'high',
                'probability': 'low',
                'description': 'High dependency on founder/CEO'
            })
        
        # Financial risks
        financial_metrics = analysis_results.get('financial_metrics', {})
        
        if financial_metrics.get('debt_to_equity', 0) > 2:
            risk_assessment['financial_risks'].append({
                'risk': 'High leverage',
                'impact': 'high',
                'probability': 'medium',
                'description': 'Elevated debt levels increase financial risk'
            })
        
        if financial_metrics.get('interest_coverage', float('inf')) < 2:
            risk_assessment['financial_risks'].append({
                'risk': 'Interest coverage',
                'impact': 'high',
                'probability': 'medium',
                'description': 'Low interest coverage ratio indicates debt service risk'
            })
        
        # Create risk matrix
        risk_assessment['risk_matrix'] = self._create_risk_matrix(
            risk_assessment['systematic_risks'] +
            risk_assessment['company_specific_risks'] +
            risk_assessment['financial_risks'] +
            risk_assessment['operational_risks']
        )
        
        # Risk mitigation strategies
        risk_assessment['risk_mitigation'] = self._suggest_risk_mitigation(
            risk_assessment
        )
        
        return risk_assessment
    
    def _generate_recommendation(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment recommendation"""
        
        # Calculate composite score
        scores = {
            'valuation': analysis_results.get('valuation_score', 0.5),
            'financials': analysis_results.get('financial_score', 0.5),
            'momentum': analysis_results.get('momentum_score', 0.5),
            'quality': analysis_results.get('quality_score', 0.5),
            'sentiment': analysis_results.get('sentiment_score', 0.5)
        }
        
        # Weight the scores
        weights = {
            'valuation': 0.3,
            'financials': 0.25,
            'momentum': 0.15,
            'quality': 0.20,
            'sentiment': 0.10
        }
        
        composite_score = sum(
            scores[factor] * weight 
            for factor, weight in weights.items()
        )
        
        # Determine recommendation
        if composite_score >= 0.8:
            recommendation = RecommendationType.STRONG_BUY
        elif composite_score >= 0.65:
            recommendation = RecommendationType.BUY
        elif composite_score >= 0.35:
            recommendation = RecommendationType.HOLD
        elif composite_score >= 0.2:
            recommendation = RecommendationType.SELL
        else:
            recommendation = RecommendationType.STRONG_SELL
        
        return {
            'recommendation': recommendation.value,
            'composite_score': composite_score,
            'factor_scores': scores,
            'conviction_level': self._calculate_conviction(scores),
            'time_horizon': '12 months',
            'key_triggers': self._identify_triggers(analysis_results),
            'monitoring_points': self._identify_monitoring_points(analysis_results)
        }
    
    # Helper methods
    def _determine_recommendation(self, upside: float, 
                                analysis_results: Dict[str, Any]) -> RecommendationType:
        """Determine recommendation based on upside and other factors"""
        risk_score = analysis_results.get('risk_assessment', {}).get('overall_risk_score', 0.5)
        quality_score = analysis_results.get('quality_score', 0.5)
        
        # Adjust for risk and quality
        risk_adjusted_upside = upside * (1 - risk_score * 0.3) * (0.7 + quality_score * 0.3)
        
        if risk_adjusted_upside >= 30:
            return RecommendationType.STRONG_BUY
        elif risk_adjusted_upside >= 15:
            return RecommendationType.BUY
        elif risk_adjusted_upside >= -10:
            return RecommendationType.HOLD
        elif risk_adjusted_upside >= -25:
            return RecommendationType.SELL
        else:
            return RecommendationType.STRONG_SELL
    
    def _calculate_cagr(self, values: List[float], years: int) -> float:
        """Calculate Compound Annual Growth Rate"""
        if len(values) < years + 1 or values[0] <= 0:
            return 0
        
        start_value = values[-(years+1)]
        end_value = values[-1]
        
        if start_value <= 0 or end_value <= 0:
            return 0
        
        return (end_value / start_value) ** (1/years) - 1
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analyze trend in values"""
        if len(values) < 3:
            return "insufficient data"
        
        # Calculate simple linear regression slope
        x = np.arange(len(values))
        if np.std(values) == 0:
            return "stable"
        
        correlation = np.corrcoef(x, values)[0, 1]
        
        if correlation > 0.7:
            return "strong uptrend"
        elif correlation > 0.3:
            return "moderate uptrend"
        elif correlation > -0.3:
            return "sideways"
        elif correlation > -0.7:
            return "moderate downtrend"
        else:
            return "strong downtrend"
    
    def _assess_report_quality(self, report: Dict[str, Any]) -> Dict[str, float]:
        """Assess the quality of the generated report"""
        quality_metrics = {
            'completeness': 0,
            'depth': 0,
            'data_quality': 0,
            'consistency': 0
        }
        
        # Check completeness
        completed_sections = sum(
            1 for section in self.report_sections 
            if section in report and report[section]
        )
        quality_metrics['completeness'] = completed_sections / len(self.report_sections)
        
        # Check depth (amount of analysis)
        total_analysis_points = 0
        for section in ['financial_analysis', 'valuation', 'risk_assessment']:
            if section in report:
                total_analysis_points += len(str(report[section]))
        
        quality_metrics['depth'] = min(1.0, total_analysis_points / 10000)
        
        # Overall quality score
        quality_metrics['overall'] = np.mean(list(quality_metrics.values()))
        
        return quality_metrics
    
    def export_to_markdown(self, report: Dict[str, Any]) -> str:
        """Export report to markdown format"""
        md_lines = []
        
        # Title and metadata
        md_lines.append(f"# Equity Research Report: {report['metadata']['company_name']}")
        md_lines.append(f"**Ticker:** {report['metadata']['ticker']}")
        md_lines.append(f"**Date:** {report['metadata']['report_date']}")
        md_lines.append(f"**Sector:** {report['metadata']['sector']}")
        md_lines.append("")
        
        # Executive Summary
        md_lines.append("## Executive Summary")
        summary = report['executive_summary']
        md_lines.append(f"**Recommendation:** {summary['recommendation']}")
        md_lines.append(f"**Target Price:** ${summary['target_price']:.2f}")
        md_lines.append(f"**Upside/Downside:** {summary['upside_downside']}")
        md_lines.append("")
        
        # Key Points
        md_lines.append("### Key Investment Points")
        for point in summary['key_points']:
            md_lines.append(f"- {point}")
        md_lines.append("")
        
        # Continue with other sections...
        
        return "\n".join(md_lines)