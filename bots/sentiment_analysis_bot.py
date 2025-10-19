#!/usr/bin/env python3
"""
Market Sentiment Analysis Bot
Aggregates sentiment from multiple sources:
- Fear & Greed Index
- Social media trends
- News sentiment
- On-chain metrics
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class SentimentAnalysisBot:
    def __init__(self):
        self.name = "Sentiment_Analysis"
        self.version = "1.0.0"
        self.enabled = True
        
        self.sentiment_weights = {
            'fear_greed': 0.30,
            'social': 0.25,
            'news': 0.25,
            'onchain': 0.20
        }
        
        self.metrics = {
            'sentiment_checks': 0,
            'extreme_fear': 0,
            'extreme_greed': 0
        }
    
    def analyze_sentiment(self,
                         fear_greed_index: float = None,
                         social_sentiment: float = None,
                         news_sentiment: float = None,
                         onchain_sentiment: float = None) -> Dict:
        """
        Aggregate sentiment from multiple sources
        
        Args:
            All sentiment scores range 0-100
            <25 = Fear, 25-45 = Neutral-Bearish, 45-55 = Neutral,
            55-75 = Neutral-Bullish, >75 = Greed
        """
        
        # Use defaults if not provided
        fear_greed_index = fear_greed_index or 50
        social_sentiment = social_sentiment or 50
        news_sentiment = news_sentiment or 50
        onchain_sentiment = onchain_sentiment or 50
        
        # Calculate weighted composite sentiment
        composite = (
            fear_greed_index * self.sentiment_weights['fear_greed'] +
            social_sentiment * self.sentiment_weights['social'] +
            news_sentiment * self.sentiment_weights['news'] +
            onchain_sentiment * self.sentiment_weights['onchain']
        )
        
        # Categorize sentiment
        category = self._categorize_sentiment(composite)
        
        # Generate contrarian signal
        signal, confidence = self._generate_sentiment_signal(composite, category)
        
        # Update metrics
        self.metrics['sentiment_checks'] += 1
        if composite < 20:
            self.metrics['extreme_fear'] += 1
        elif composite > 80:
            self.metrics['extreme_greed'] += 1
        
        return {
            'composite_sentiment': composite,
            'category': category,
            'fear_greed_index': fear_greed_index,
            'social_sentiment': social_sentiment,
            'news_sentiment': news_sentiment,
            'onchain_sentiment': onchain_sentiment,
            'signal': signal,
            'confidence': confidence,
            'strength': confidence * 100,
            'reason': self._get_reason(category, composite),
            'contrarian_opportunity': composite < 25 or composite > 75,
            'timestamp': datetime.now().isoformat()
        }
    
    def _categorize_sentiment(self, score: float) -> str:
        """Categorize sentiment score"""
        if score < 20:
            return 'EXTREME_FEAR'
        elif score < 40:
            return 'FEAR'
        elif score < 50:
            return 'NEUTRAL_BEARISH'
        elif score < 60:
            return 'NEUTRAL_BULLISH'
        elif score < 80:
            return 'GREED'
        else:
            return 'EXTREME_GREED'
    
    def _generate_sentiment_signal(self, score: float, category: str) -> tuple:
        """
        Generate CONTRARIAN signals from sentiment
        Extreme fear = buy opportunity
        Extreme greed = sell/caution
        """
        
        # Extreme fear = BUY (contrarian)
        if score < 20:
            return ('BUY', 0.85)
        elif score < 35:
            return ('BUY', 0.70)
        
        # Extreme greed = SELL (contrarian)
        elif score > 80:
            return ('SELL', 0.85)
        elif score > 70:
            return ('SELL', 0.70)
        
        # Neutral sentiment = follow trend
        elif 45 < score < 55:
            return ('HOLD', 0.50)
        
        return ('HOLD', 0.0)
    
    def _get_reason(self, category: str, score: float) -> str:
        """Get human-readable reason"""
        reasons = {
            'EXTREME_FEAR': f"Extreme fear ({score:.0f}/100) - Strong contrarian BUY signal",
            'FEAR': f"Fear in market ({score:.0f}/100) - Potential buying opportunity",
            'NEUTRAL_BEARISH': f"Slight bearishness ({score:.0f}/100) - Cautious",
            'NEUTRAL_BULLISH': f"Slight optimism ({score:.0f}/100) - Normal conditions",
            'GREED': f"Greedy market ({score:.0f}/100) - Consider taking profits",
            'EXTREME_GREED': f"Extreme greed ({score:.0f}/100) - Strong contrarian SELL signal"
        }
        return reasons.get(category, f"Sentiment: {score:.0f}/100")
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'sentiment_sources': list(self.sentiment_weights.keys()),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = SentimentAnalysisBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
