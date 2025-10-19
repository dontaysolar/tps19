#!/usr/bin/env python3
"""
SENTIMENT ANALYSIS LAYER
All sentiment sources consolidated
"""

import re
from datetime import datetime
from typing import Dict, List
from collections import deque

class SentimentLayer:
    """Consolidated sentiment analysis from all sources"""
    
    def __init__(self):
        self.name = "Sentiment_Layer"
        self.version = "1.0.0"
        
        self.sources = {
            'news': NewsAnalyzer(),
            'social': SocialMediaAnalyzer(),
            'fear_greed': FearGreedIndex(),
            'funding_rate': FundingRateAnalyzer(),
            'whale_activity': WhaleActivityMonitor()
        }
        
    def analyze_all(self, symbol: str) -> Dict:
        """Get sentiment from all sources"""
        results = {}
        
        for source_name, analyzer in self.sources.items():
            try:
                results[source_name] = analyzer.analyze(symbol)
            except Exception as e:
                results[source_name] = {'error': str(e), 'sentiment': 'NEUTRAL', 'score': 0}
        
        # Aggregate all sentiments
        return self.aggregate_sentiment(results)
    
    def aggregate_sentiment(self, results: Dict) -> Dict:
        """Aggregate all sentiment sources"""
        scores = []
        weights = {
            'news': 0.25,
            'social': 0.20,
            'fear_greed': 0.20,
            'funding_rate': 0.20,
            'whale_activity': 0.15
        }
        
        weighted_score = 0
        total_weight = 0
        
        for source, data in results.items():
            if isinstance(data, dict) and 'error' not in data:
                score = data.get('score', 0)
                weight = weights.get(source, 0.10)
                weighted_score += score * weight
                total_weight += weight
        
        final_score = weighted_score / total_weight if total_weight > 0 else 0
        
        # Classify sentiment
        if final_score > 0.3:
            sentiment = 'BULLISH'
            confidence = min(final_score, 1.0)
        elif final_score < -0.3:
            sentiment = 'BEARISH'
            confidence = min(abs(final_score), 1.0)
        else:
            sentiment = 'NEUTRAL'
            confidence = 0.5
        
        return {
            'overall_sentiment': sentiment,
            'score': final_score,
            'confidence': confidence,
            'sources': results,
            'timestamp': datetime.now().isoformat()
        }

class NewsAnalyzer:
    """News sentiment analysis"""
    
    def __init__(self):
        self.bullish_keywords = ['surge', 'rally', 'bullish', 'adoption', 'institutional', 'breakthrough', 
                                 'upgrade', 'partnership', 'bullish', 'soaring', 'moon']
        self.bearish_keywords = ['crash', 'plunge', 'bearish', 'regulation', 'ban', 'hack', 'fraud',
                                 'investigation', 'collapse', 'dump', 'fear']
    
    def analyze(self, symbol: str) -> Dict:
        """Analyze news sentiment (placeholder - would use real API)"""
        # In production: fetch from NewsAPI, CryptoPanic, etc.
        
        # Simulated sentiment
        score = 0  # Neutral
        articles_analyzed = 0
        
        return {
            'sentiment': 'NEUTRAL' if score == 0 else 'BULLISH' if score > 0 else 'BEARISH',
            'score': score,
            'articles': articles_analyzed,
            'source': 'NEWS'
        }

class SocialMediaAnalyzer:
    """Social media sentiment (Twitter, Reddit, etc)"""
    
    def analyze(self, symbol: str) -> Dict:
        """Analyze social sentiment (placeholder)"""
        # In production: Twitter API, Reddit API, etc.
        
        return {
            'sentiment': 'NEUTRAL',
            'score': 0,
            'mentions': 0,
            'trending': False,
            'source': 'SOCIAL'
        }

class FearGreedIndex:
    """Crypto Fear & Greed Index"""
    
    def analyze(self, symbol: str) -> Dict:
        """Get Fear & Greed Index (placeholder)"""
        # In production: fetch from alternative.me API
        
        # Scale: 0-100 (0 = Extreme Fear, 100 = Extreme Greed)
        index = 50  # Neutral
        
        # Convert to sentiment score (-1 to 1)
        score = (index - 50) / 50
        
        if index < 25:
            sentiment = 'EXTREME_FEAR'
        elif index < 45:
            sentiment = 'FEAR'
        elif index < 55:
            sentiment = 'NEUTRAL'
        elif index < 75:
            sentiment = 'GREED'
        else:
            sentiment = 'EXTREME_GREED'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'index': index,
            'source': 'FEAR_GREED'
        }

class FundingRateAnalyzer:
    """Perpetual funding rate analysis"""
    
    def analyze(self, symbol: str) -> Dict:
        """Analyze funding rates (placeholder)"""
        # In production: fetch from exchange APIs
        
        funding_rate = 0.0001  # 0.01% (neutral)
        
        # Positive = longs pay shorts (bullish sentiment)
        # Negative = shorts pay longs (bearish sentiment)
        
        if funding_rate > 0.001:
            sentiment = 'BULLISH'
            score = min(funding_rate * 100, 1.0)
        elif funding_rate < -0.001:
            sentiment = 'BEARISH'
            score = max(funding_rate * 100, -1.0)
        else:
            sentiment = 'NEUTRAL'
            score = 0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'funding_rate': funding_rate,
            'source': 'FUNDING_RATE'
        }

class WhaleActivityMonitor:
    """Large transaction monitoring"""
    
    def __init__(self):
        self.recent_transactions = deque(maxlen=100)
    
    def analyze(self, symbol: str) -> Dict:
        """Monitor whale activity (placeholder)"""
        # In production: blockchain explorer APIs
        
        large_buys = 0
        large_sells = 0
        
        net_flow = large_buys - large_sells
        
        if net_flow > 10:
            sentiment = 'BULLISH'
            score = 0.7
        elif net_flow < -10:
            sentiment = 'BEARISH'
            score = -0.7
        else:
            sentiment = 'NEUTRAL'
            score = 0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'large_buys': large_buys,
            'large_sells': large_sells,
            'net_flow': net_flow,
            'source': 'WHALE_ACTIVITY'
        }

if __name__ == '__main__':
    layer = SentimentLayer()
    print(f"✅ {layer.name} v{layer.version} initialized")
