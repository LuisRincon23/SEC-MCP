#!/usr/bin/env python3
"""
Advanced Financial Analysis Framework
PhD-level research tools for deep stock analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import statistics
from dataclasses import dataclass
from enum import Enum
import re


class FinancialMetrics:
    """Advanced financial metrics calculations"""
    
    @staticmethod
    def calculate_roic(ebit: float, tax_rate: float, invested_capital: float) -> float:
        """Calculate Return on Invested Capital (ROIC)"""
        nopat = ebit * (1 - tax_rate)
        return nopat / invested_capital if invested_capital > 0 else 0
    
    @staticmethod
    def calculate_roce(ebit: float, capital_employed: float) -> float:
        """Calculate Return on Capital Employed"""
        return ebit / capital_employed if capital_employed > 0 else 0
    
    @staticmethod
    def calculate_fcf_yield(fcf: float, market_cap: float) -> float:
        """Calculate Free Cash Flow Yield"""
        return fcf / market_cap if market_cap > 0 else 0
    
    @staticmethod
    def calculate_ev_to_ebitda(enterprise_value: float, ebitda: float) -> float:
        """Calculate EV/EBITDA ratio"""
        return enterprise_value / ebitda if ebitda > 0 else float('inf')
    
    @staticmethod
    def calculate_peg_ratio(pe_ratio: float, growth_rate: float) -> float:
        """Calculate PEG ratio"""
        return pe_ratio / growth_rate if growth_rate > 0 else float('inf')
    
    @staticmethod
    def calculate_altman_z_score(working_capital: float, total_assets: float, 
                                retained_earnings: float, ebit: float,
                                market_value_equity: float, total_liabilities: float,
                                sales: float) -> Tuple[float, str]:
        """
        Calculate Altman Z-Score for bankruptcy prediction
        Returns: (z_score, interpretation)
        """
        if total_assets == 0:
            return 0, "Cannot calculate - Invalid data"
        
        # Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
        A = working_capital / total_assets
        B = retained_earnings / total_assets
        C = ebit / total_assets
        D = market_value_equity / total_liabilities if total_liabilities > 0 else 0
        E = sales / total_assets
        
        z_score = 1.2 * A + 1.4 * B + 3.3 * C + 0.6 * D + 1.0 * E
        
        if z_score > 2.99:
            interpretation = "Safe Zone - Low bankruptcy risk"
        elif z_score > 1.81:
            interpretation = "Grey Zone - Moderate bankruptcy risk"
        else:
            interpretation = "Distress Zone - High bankruptcy risk"
        
        return z_score, interpretation
    
    @staticmethod
    def calculate_piotroski_f_score(financials: Dict[str, Any]) -> Tuple[int, Dict[str, bool]]:
        """
        Calculate Piotroski F-Score (0-9) for fundamental strength
        Returns: (score, detailed_criteria)
        """
        criteria = {}
        score = 0
        
        # Profitability Signals (4 points)
        # 1. Positive ROA
        if financials.get('roa', 0) > 0:
            criteria['positive_roa'] = True
            score += 1
        else:
            criteria['positive_roa'] = False
        
        # 2. Positive Operating Cash Flow
        if financials.get('operating_cash_flow', 0) > 0:
            criteria['positive_ocf'] = True
            score += 1
        else:
            criteria['positive_ocf'] = False
        
        # 3. Increasing ROA
        if financials.get('roa_change', 0) > 0:
            criteria['increasing_roa'] = True
            score += 1
        else:
            criteria['increasing_roa'] = False
        
        # 4. Quality of earnings (OCF > Net Income)
        if financials.get('operating_cash_flow', 0) > financials.get('net_income', 0):
            criteria['quality_earnings'] = True
            score += 1
        else:
            criteria['quality_earnings'] = False
        
        # Leverage/Liquidity Signals (3 points)
        # 5. Decreasing leverage
        if financials.get('leverage_change', 0) < 0:
            criteria['decreasing_leverage'] = True
            score += 1
        else:
            criteria['decreasing_leverage'] = False
        
        # 6. Increasing current ratio
        if financials.get('current_ratio_change', 0) > 0:
            criteria['increasing_liquidity'] = True
            score += 1
        else:
            criteria['increasing_liquidity'] = False
        
        # 7. No new shares issued
        if financials.get('shares_change', 0) <= 0:
            criteria['no_dilution'] = True
            score += 1
        else:
            criteria['no_dilution'] = False
        
        # Operating Efficiency Signals (2 points)
        # 8. Increasing gross margin
        if financials.get('gross_margin_change', 0) > 0:
            criteria['increasing_margin'] = True
            score += 1
        else:
            criteria['increasing_margin'] = False
        
        # 9. Increasing asset turnover
        if financials.get('asset_turnover_change', 0) > 0:
            criteria['increasing_efficiency'] = True
            score += 1
        else:
            criteria['increasing_efficiency'] = False
        
        return score, criteria


class DCFModel:
    """Discounted Cash Flow valuation model"""
    
    def __init__(self, risk_free_rate: float = 0.045):
        self.risk_free_rate = risk_free_rate
    
    def calculate_wacc(self, market_cap: float, total_debt: float, 
                      cost_of_equity: float, cost_of_debt: float, 
                      tax_rate: float) -> float:
        """Calculate Weighted Average Cost of Capital"""
        total_value = market_cap + total_debt
        if total_value == 0:
            return 0.10  # Default 10%
        
        equity_weight = market_cap / total_value
        debt_weight = total_debt / total_value
        
        wacc = (equity_weight * cost_of_equity + 
                debt_weight * cost_of_debt * (1 - tax_rate))
        return wacc
    
    def calculate_terminal_value(self, final_fcf: float, terminal_growth: float, 
                               wacc: float) -> float:
        """Calculate terminal value using perpetuity growth method"""
        if wacc <= terminal_growth:
            return 0  # Invalid scenario
        return final_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
    
    def calculate_dcf_value(self, fcf_projections: List[float], terminal_growth: float,
                           wacc: float, net_debt: float, shares_outstanding: float) -> Dict[str, float]:
        """
        Full DCF calculation
        Returns: {intrinsic_value_per_share, enterprise_value, equity_value}
        """
        # Discount projected FCFs
        pv_fcfs = sum(fcf / (1 + wacc) ** (i + 1) 
                     for i, fcf in enumerate(fcf_projections))
        
        # Terminal value
        terminal_fcf = fcf_projections[-1]
        terminal_value = self.calculate_terminal_value(terminal_fcf, terminal_growth, wacc)
        pv_terminal = terminal_value / (1 + wacc) ** len(fcf_projections)
        
        # Enterprise and equity value
        enterprise_value = pv_fcfs + pv_terminal
        equity_value = enterprise_value - net_debt
        intrinsic_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
        
        return {
            'intrinsic_value_per_share': intrinsic_value_per_share,
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'pv_fcfs': pv_fcfs,
            'pv_terminal': pv_terminal
        }
    
    def monte_carlo_dcf(self, base_fcf: float, num_years: int = 5, 
                       simulations: int = 10000) -> Dict[str, Any]:
        """
        Monte Carlo simulation for DCF uncertainty analysis
        """
        results = []
        
        # Parameter distributions
        growth_rates = np.random.normal(0.05, 0.02, simulations)  # 5% ± 2%
        terminal_growths = np.random.normal(0.025, 0.01, simulations)  # 2.5% ± 1%
        waccs = np.random.normal(0.10, 0.02, simulations)  # 10% ± 2%
        
        for i in range(simulations):
            # Project FCFs with uncertainty
            fcfs = []
            current_fcf = base_fcf
            for _ in range(num_years):
                growth = growth_rates[i] + np.random.normal(0, 0.01)  # Additional volatility
                current_fcf *= (1 + growth)
                fcfs.append(current_fcf)
            
            # Calculate DCF for this simulation
            dcf_result = self.calculate_dcf_value(
                fcfs, terminal_growths[i], waccs[i], 0, 1  # Simplified for per-share
            )
            results.append(dcf_result['intrinsic_value_per_share'])
        
        return {
            'mean_value': np.mean(results),
            'median_value': np.median(results),
            'std_dev': np.std(results),
            'percentile_5': np.percentile(results, 5),
            'percentile_95': np.percentile(results, 95),
            'confidence_interval': (np.percentile(results, 5), np.percentile(results, 95))
        }


class ComparativeAnalysis:
    """Advanced peer comparison and relative valuation"""
    
    @staticmethod
    def calculate_relative_metrics(company_metrics: Dict[str, float], 
                                 peer_metrics: List[Dict[str, float]]) -> Dict[str, Any]:
        """Calculate company's relative position vs peers"""
        results = {}
        
        for metric in company_metrics:
            if metric in ['ticker', 'company_name']:
                continue
                
            peer_values = [p.get(metric, 0) for p in peer_metrics if metric in p]
            if not peer_values:
                continue
            
            company_value = company_metrics[metric]
            
            # Calculate percentile ranking
            below_count = sum(1 for v in peer_values if v < company_value)
            percentile = (below_count / len(peer_values)) * 100 if peer_values else 50
            
            # Calculate z-score
            mean_val = statistics.mean(peer_values)
            std_val = statistics.stdev(peer_values) if len(peer_values) > 1 else 0
            z_score = (company_value - mean_val) / std_val if std_val > 0 else 0
            
            results[metric] = {
                'company_value': company_value,
                'peer_mean': mean_val,
                'peer_median': statistics.median(peer_values),
                'percentile_rank': percentile,
                'z_score': z_score,
                'interpretation': ComparativeAnalysis._interpret_z_score(z_score)
            }
        
        return results
    
    @staticmethod
    def _interpret_z_score(z_score: float) -> str:
        """Interpret z-score for relative positioning"""
        if z_score > 2:
            return "Significantly above peers"
        elif z_score > 1:
            return "Above peers"
        elif z_score > -1:
            return "In line with peers"
        elif z_score > -2:
            return "Below peers"
        else:
            return "Significantly below peers"
    
    @staticmethod
    def sector_rotation_analysis(sector_performance: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyze sector rotation patterns"""
        results = {}
        
        for sector, returns in sector_performance.items():
            if len(returns) < 2:
                continue
            
            # Calculate momentum indicators
            short_term_momentum = np.mean(returns[-5:]) if len(returns) >= 5 else np.mean(returns)
            long_term_momentum = np.mean(returns[-20:]) if len(returns) >= 20 else np.mean(returns)
            
            # Trend strength
            if len(returns) >= 10:
                x = np.arange(len(returns))
                slope, _ = np.polyfit(x, returns, 1)
                trend_strength = slope * 100  # Percentage points
            else:
                trend_strength = 0
            
            # Volatility
            volatility = np.std(returns) if len(returns) > 1 else 0
            
            results[sector] = {
                'short_term_momentum': short_term_momentum,
                'long_term_momentum': long_term_momentum,
                'trend_strength': trend_strength,
                'volatility': volatility,
                'risk_adjusted_momentum': short_term_momentum / volatility if volatility > 0 else 0,
                'rotation_signal': ComparativeAnalysis._get_rotation_signal(
                    short_term_momentum, long_term_momentum
                )
            }
        
        return results
    
    @staticmethod
    def _get_rotation_signal(short_momentum: float, long_momentum: float) -> str:
        """Determine sector rotation signal"""
        if short_momentum > long_momentum and short_momentum > 0:
            return "Bullish - Accelerating"
        elif short_momentum > long_momentum and short_momentum < 0:
            return "Recovery - Improving"
        elif short_momentum < long_momentum and long_momentum > 0:
            return "Caution - Decelerating"
        else:
            return "Bearish - Deteriorating"


class TechnicalIndicators:
    """Advanced technical analysis indicators"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return []
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        rsi_values = []
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        for i in range(period, len(gains)):
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
            
            # Update averages
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        return rsi_values
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, 
                      signal: int = 9) -> Dict[str, List[float]]:
        """Calculate MACD indicator"""
        if len(prices) < slow:
            return {'macd': [], 'signal': [], 'histogram': []}
        
        # Calculate EMAs
        ema_fast = TechnicalIndicators._calculate_ema(prices, fast)
        ema_slow = TechnicalIndicators._calculate_ema(prices, slow)
        
        # MACD line
        macd_line = [f - s for f, s in zip(ema_fast[slow-fast:], ema_slow)]
        
        # Signal line
        signal_line = TechnicalIndicators._calculate_ema(macd_line, signal)
        
        # Histogram
        histogram = [m - s for m, s in zip(macd_line[signal-1:], signal_line)]
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def _calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, 
                                 std_dev: float = 2) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {'upper': [], 'middle': [], 'lower': []}
        
        middle = []
        upper = []
        lower = []
        
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            sma = sum(window) / period
            std = statistics.stdev(window)
            
            middle.append(sma)
            upper.append(sma + std_dev * std)
            lower.append(sma - std_dev * std)
        
        return {'upper': upper, 'middle': middle, 'lower': lower}


class MarketRegimeDetection:
    """Detect market regimes and conditions"""
    
    @staticmethod
    def detect_regime(returns: List[float], volume: List[float], 
                     volatility: List[float]) -> Dict[str, Any]:
        """Detect current market regime"""
        if len(returns) < 20:
            return {'regime': 'Insufficient data', 'confidence': 0}
        
        # Recent performance
        recent_return = np.mean(returns[-20:])
        recent_vol = np.mean(volatility[-20:])
        recent_volume = np.mean(volume[-20:])
        
        # Historical comparison
        hist_return = np.mean(returns[:-20])
        hist_vol = np.mean(volatility[:-20])
        hist_volume = np.mean(volume[:-20])
        
        # Regime detection logic
        if recent_return > hist_return * 1.2 and recent_vol < hist_vol * 1.2:
            regime = "Bull Market - Low Volatility"
            confidence = 0.8
        elif recent_return > hist_return and recent_vol > hist_vol:
            regime = "Bull Market - High Volatility"
            confidence = 0.7
        elif recent_return < hist_return * 0.8 and recent_vol > hist_vol * 1.2:
            regime = "Bear Market - High Volatility"
            confidence = 0.8
        elif recent_return < hist_return and recent_vol < hist_vol:
            regime = "Bear Market - Low Volatility"
            confidence = 0.7
        elif abs(recent_return) < 0.02 and recent_vol < hist_vol:
            regime = "Consolidation - Low Volatility"
            confidence = 0.6
        else:
            regime = "Transition - Mixed Signals"
            confidence = 0.5
        
        # Volume confirmation
        if recent_volume > hist_volume * 1.3:
            regime += " (High Volume)"
            confidence += 0.1
        elif recent_volume < hist_volume * 0.7:
            regime += " (Low Volume)"
            confidence -= 0.1
        
        return {
            'regime': regime,
            'confidence': min(max(confidence, 0), 1),
            'metrics': {
                'return_change': (recent_return - hist_return) / abs(hist_return) if hist_return != 0 else 0,
                'volatility_change': (recent_vol - hist_vol) / hist_vol if hist_vol != 0 else 0,
                'volume_change': (recent_volume - hist_volume) / hist_volume if hist_volume != 0 else 0
            }
        }


@dataclass
class ResearchQuality:
    """Assess quality of research data and analysis"""
    
    data_completeness: float  # 0-1
    data_freshness: float  # 0-1
    source_reliability: float  # 0-1
    analysis_depth: float  # 0-1
    
    @property
    def overall_quality(self) -> float:
        """Calculate overall research quality score"""
        return (self.data_completeness * 0.3 + 
                self.data_freshness * 0.2 + 
                self.source_reliability * 0.3 + 
                self.analysis_depth * 0.2)
    
    @property
    def quality_grade(self) -> str:
        """Convert quality score to letter grade"""
        score = self.overall_quality
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        else:
            return "D"
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for improving research quality"""
        recommendations = []
        
        if self.data_completeness < 0.8:
            recommendations.append("Gather more comprehensive financial data")
        if self.data_freshness < 0.8:
            recommendations.append("Update to more recent data sources")
        if self.source_reliability < 0.8:
            recommendations.append("Use more authoritative data sources")
        if self.analysis_depth < 0.8:
            recommendations.append("Perform deeper quantitative analysis")
        
        return recommendations