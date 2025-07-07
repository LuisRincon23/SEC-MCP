#!/usr/bin/env python3
"""
Advanced NLP for Financial Text Analysis
PhD-level sentiment analysis and information extraction
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import Counter
import numpy as np


@dataclass
class SentimentResult:
    """Structured sentiment analysis result"""
    overall_sentiment: str  # bullish, bearish, neutral
    sentiment_score: float  # -1 to 1
    confidence: float  # 0 to 1
    key_phrases: List[str]
    entity_sentiments: Dict[str, float]
    topics: List[str]
    financial_indicators: Dict[str, Any]


class AdvancedSentimentAnalyzer:
    """Advanced NLP for financial sentiment analysis"""
    
    def __init__(self):
        # Financial sentiment lexicons
        self.financial_lexicon = {
            'strong_positive': [
                'beat expectations', 'record revenue', 'strong growth', 'outperform',
                'breakthrough', 'surpass', 'exceptional', 'robust', 'accelerating',
                'market leader', 'competitive advantage', 'pricing power', 'moat'
            ],
            'positive': [
                'growth', 'profit', 'increase', 'improve', 'gain', 'upside', 'recovery',
                'expansion', 'momentum', 'beat', 'exceed', 'positive', 'optimistic',
                'upgrade', 'buy', 'accumulate', 'opportunity'
            ],
            'negative': [
                'decline', 'loss', 'decrease', 'concern', 'risk', 'challenge', 'weak',
                'miss', 'disappointing', 'downgrade', 'sell', 'underperform', 'pressure',
                'headwind', 'slowdown', 'uncertain'
            ],
            'strong_negative': [
                'bankruptcy', 'default', 'collapse', 'crisis', 'scandal', 'fraud',
                'investigation', 'lawsuit', 'plunge', 'crash', 'severe', 'toxic',
                'liquidation', 'delisting'
            ]
        }
        
        # Context modifiers
        self.negation_words = ['not', 'no', 'never', 'neither', 'nor', 'none', 'nobody',
                               'nothing', 'nowhere', 'isn\'t', 'wasn\'t', 'weren\'t',
                               'hasn\'t', 'haven\'t', 'hadn\'t', 'doesn\'t', 'don\'t',
                               'didn\'t', 'won\'t', 'wouldn\'t', 'couldn\'t', 'shouldn\'t']
        
        self.amplifiers = {
            'increase': ['significantly', 'substantially', 'considerably', 'materially'],
            'decrease': ['slightly', 'marginally', 'somewhat', 'modestly']
        }
        
        # Financial entities patterns
        self.entity_patterns = {
            'revenue': re.compile(r'\b(revenue|sales|turnover)\b', re.I),
            'earnings': re.compile(r'\b(earnings|profit|income|ebitda|ebit)\b', re.I),
            'guidance': re.compile(r'\b(guidance|forecast|outlook|projection)\b', re.I),
            'margin': re.compile(r'\b(margin|profitability)\b', re.I),
            'debt': re.compile(r'\b(debt|leverage|borrowing|liquidity)\b', re.I),
            'growth': re.compile(r'\b(growth|expansion|increase)\b', re.I)
        }
        
        # Financial metrics extraction patterns
        self.metric_patterns = {
            'percentage': re.compile(r'(\d+(?:\.\d+)?)\s*%'),
            'currency': re.compile(r'\$\s*(\d+(?:\.\d+)?)\s*(million|billion|M|B)?', re.I),
            'multiplier': re.compile(r'(\d+(?:\.\d+)?)\s*[xX]'),
            'ratio': re.compile(r'(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)')
        }
    
    def analyze_sentiment(self, text: str, context: Optional[Dict[str, Any]] = None) -> SentimentResult:
        """Perform advanced sentiment analysis on financial text"""
        # Preprocess text
        sentences = self._split_sentences(text)
        
        # Extract entities and their sentiments
        entity_sentiments = self._analyze_entity_sentiments(sentences)
        
        # Extract financial indicators
        financial_indicators = self._extract_financial_indicators(text)
        
        # Topic extraction
        topics = self._extract_topics(text)
        
        # Calculate overall sentiment
        sentiment_scores = []
        key_phrases = []
        
        for sentence in sentences:
            score, phrases = self._analyze_sentence_sentiment(sentence)
            sentiment_scores.append(score)
            key_phrases.extend(phrases)
        
        # Aggregate sentiment
        if sentiment_scores:
            overall_score = np.mean(sentiment_scores)
            # Weight recent sentences more heavily
            weighted_score = np.average(sentiment_scores, 
                                      weights=np.linspace(0.5, 1.0, len(sentiment_scores)))
        else:
            overall_score = weighted_score = 0
        
        # Determine sentiment category
        if weighted_score > 0.3:
            overall_sentiment = 'bullish'
        elif weighted_score < -0.3:
            overall_sentiment = 'bearish'
        else:
            overall_sentiment = 'neutral'
        
        # Calculate confidence based on consistency
        if sentiment_scores:
            consistency = 1 - np.std(sentiment_scores)
            confidence = max(0, min(1, consistency * abs(weighted_score)))
        else:
            confidence = 0
        
        # Apply context adjustments
        if context:
            weighted_score, confidence = self._apply_context_adjustments(
                weighted_score, confidence, context, financial_indicators
            )
        
        return SentimentResult(
            overall_sentiment=overall_sentiment,
            sentiment_score=weighted_score,
            confidence=confidence,
            key_phrases=list(set(key_phrases))[:10],  # Top 10 unique phrases
            entity_sentiments=entity_sentiments,
            topics=topics,
            financial_indicators=financial_indicators
        )
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitter - could be enhanced with NLTK
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_sentence_sentiment(self, sentence: str) -> Tuple[float, List[str]]:
        """Analyze sentiment of a single sentence"""
        sentence_lower = sentence.lower()
        score = 0
        key_phrases = []
        
        # Check for negation
        has_negation = any(neg in sentence_lower for neg in self.negation_words)
        
        # Score based on lexicon
        for phrase in self.financial_lexicon['strong_positive']:
            if phrase in sentence_lower:
                score += 2.0 if not has_negation else -2.0
                key_phrases.append(phrase)
        
        for phrase in self.financial_lexicon['positive']:
            if phrase in sentence_lower:
                score += 1.0 if not has_negation else -1.0
                key_phrases.append(phrase)
        
        for phrase in self.financial_lexicon['negative']:
            if phrase in sentence_lower:
                score -= 1.0 if not has_negation else 1.0
                key_phrases.append(phrase)
        
        for phrase in self.financial_lexicon['strong_negative']:
            if phrase in sentence_lower:
                score -= 2.0 if not has_negation else 2.0
                key_phrases.append(phrase)
        
        # Check for amplifiers
        for amp_type, amplifiers in self.amplifiers.items():
            for amp in amplifiers:
                if amp in sentence_lower:
                    if amp_type == 'increase':
                        score *= 1.5
                    else:
                        score *= 0.7
        
        # Normalize score to [-1, 1]
        normalized_score = max(-1, min(1, score / 5))
        
        return normalized_score, key_phrases
    
    def _analyze_entity_sentiments(self, sentences: List[str]) -> Dict[str, float]:
        """Analyze sentiment for specific financial entities"""
        entity_sentiments = {}
        
        for entity_name, pattern in self.entity_patterns.items():
            entity_scores = []
            
            for sentence in sentences:
                if pattern.search(sentence):
                    score, _ = self._analyze_sentence_sentiment(sentence)
                    entity_scores.append(score)
            
            if entity_scores:
                entity_sentiments[entity_name] = np.mean(entity_scores)
        
        return entity_sentiments
    
    def _extract_financial_indicators(self, text: str) -> Dict[str, Any]:
        """Extract financial metrics and indicators from text"""
        indicators = {
            'percentages': [],
            'currency_amounts': [],
            'multipliers': [],
            'ratios': [],
            'comparisons': []
        }
        
        # Extract percentages
        for match in self.metric_patterns['percentage'].finditer(text):
            value = float(match.group(1))
            # Get context around the percentage
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]
            
            indicators['percentages'].append({
                'value': value,
                'context': context,
                'sentiment': self._get_metric_sentiment(context, value)
            })
        
        # Extract currency amounts
        for match in self.metric_patterns['currency'].finditer(text):
            amount = float(match.group(1))
            unit = match.group(2)
            if unit and unit.lower() in ['billion', 'b']:
                amount *= 1000
            
            indicators['currency_amounts'].append({
                'value': amount,
                'unit': 'million',
                'context': text[max(0, match.start()-30):min(len(text), match.end()+30)]
            })
        
        # Extract comparison words
        comparison_patterns = [
            (r'increase[d]?\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%', 'increase'),
            (r'decrease[d]?\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%', 'decrease'),
            (r'up\s+(\d+(?:\.\d+)?)\s*%', 'increase'),
            (r'down\s+(\d+(?:\.\d+)?)\s*%', 'decrease'),
            (r'grew\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%', 'growth'),
            (r'fell\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%', 'decline')
        ]
        
        for pattern, comparison_type in comparison_patterns:
            for match in re.finditer(pattern, text, re.I):
                indicators['comparisons'].append({
                    'type': comparison_type,
                    'value': float(match.group(1)),
                    'context': text[max(0, match.start()-30):min(len(text), match.end()+30)]
                })
        
        return indicators
    
    def _get_metric_sentiment(self, context: str, value: float) -> str:
        """Determine sentiment of a metric based on context"""
        context_lower = context.lower()
        
        # Positive contexts
        positive_contexts = ['growth', 'increase', 'gain', 'beat', 'exceed', 'revenue', 'profit']
        negative_contexts = ['loss', 'decline', 'debt', 'expense', 'cost', 'risk']
        
        if any(word in context_lower for word in positive_contexts):
            return 'positive' if value > 0 else 'negative'
        elif any(word in context_lower for word in negative_contexts):
            return 'negative' if value > 0 else 'positive'
        else:
            return 'neutral'
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        topics = []
        
        # Topic patterns
        topic_patterns = {
            'earnings': r'\b(?:earnings|eps|profit|quarter|results)\b',
            'guidance': r'\b(?:guidance|outlook|forecast|expect)\b',
            'product': r'\b(?:product|launch|innovation|technology)\b',
            'market': r'\b(?:market|competition|share|industry)\b',
            'expansion': r'\b(?:expansion|acquisition|merger|partnership)\b',
            'regulation': r'\b(?:regulation|compliance|fda|sec|government)\b',
            'macro': r'\b(?:economy|inflation|rate|recession|gdp)\b'
        }
        
        for topic, pattern in topic_patterns.items():
            if re.search(pattern, text, re.I):
                topics.append(topic)
        
        return topics
    
    def _apply_context_adjustments(self, score: float, confidence: float, 
                                  context: Dict[str, Any], 
                                  indicators: Dict[str, Any]) -> Tuple[float, float]:
        """Apply contextual adjustments to sentiment score"""
        # Adjust based on market conditions
        if context.get('market_sentiment'):
            market_adjustment = context['market_sentiment'] * 0.2
            score = score * 0.8 + market_adjustment
        
        # Adjust based on sector performance
        if context.get('sector_performance'):
            sector_adjustment = context['sector_performance'] * 0.1
            score = score * 0.9 + sector_adjustment
        
        # Adjust confidence based on data quality
        if indicators['comparisons']:
            # More quantitative data increases confidence
            confidence = min(1.0, confidence * 1.1)
        
        return score, confidence
    
    def analyze_earnings_call(self, transcript: str) -> Dict[str, Any]:
        """Specialized analysis for earnings call transcripts"""
        # Split into Q&A sections
        sections = self._split_earnings_sections(transcript)
        
        results = {
            'management_tone': self.analyze_sentiment(sections.get('management', '')),
            'analyst_sentiment': self.analyze_sentiment(sections.get('qa', '')),
            'key_topics': [],
            'guidance_sentiment': None,
            'highlighted_metrics': []
        }
        
        # Extract guidance specific sentiment
        guidance_text = self._extract_guidance_text(transcript)
        if guidance_text:
            results['guidance_sentiment'] = self.analyze_sentiment(guidance_text)
        
        # Extract highlighted metrics
        results['highlighted_metrics'] = self._extract_highlighted_metrics(transcript)
        
        return results
    
    def _split_earnings_sections(self, transcript: str) -> Dict[str, str]:
        """Split earnings transcript into sections"""
        sections = {
            'management': '',
            'qa': ''
        }
        
        # Simple heuristic - Q&A usually starts with "Question-and-Answer"
        qa_start = transcript.lower().find('question-and-answer')
        if qa_start == -1:
            qa_start = transcript.lower().find('q&a')
        
        if qa_start > 0:
            sections['management'] = transcript[:qa_start]
            sections['qa'] = transcript[qa_start:]
        else:
            sections['management'] = transcript
        
        return sections
    
    def _extract_guidance_text(self, transcript: str) -> Optional[str]:
        """Extract guidance-related text from transcript"""
        guidance_patterns = [
            r'(?:guidance|outlook|forecast|expect).*?(?:\.|$)',
            r'(?:fiscal|full.year|quarter).*?(?:guidance|outlook).*?(?:\.|$)'
        ]
        
        guidance_texts = []
        for pattern in guidance_patterns:
            matches = re.findall(pattern, transcript, re.I | re.S)
            guidance_texts.extend(matches)
        
        return ' '.join(guidance_texts) if guidance_texts else None
    
    def _extract_highlighted_metrics(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract metrics that are highlighted in the transcript"""
        highlighted = []
        
        # Look for emphasized metrics (e.g., "revenue grew 25%")
        metric_phrases = re.findall(
            r'([\w\s]+)\s+(?:grew|increased|decreased|fell|improved|declined)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%',
            transcript, re.I
        )
        
        for metric, value in metric_phrases:
            highlighted.append({
                'metric': metric.strip(),
                'change': float(value),
                'context': 'percentage_change'
            })
        
        return highlighted[:10]  # Top 10 metrics