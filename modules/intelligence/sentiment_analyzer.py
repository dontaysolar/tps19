#!/usr/bin/env python3
"""
Sentiment Analyzer - Market sentiment from multiple sources
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer:
    """
    Aggregate sentiment from news, social media, and fear/greed index
    """
    
    def __init__(self):
        self.sentiment_cache = {}
        self.cache_duration = timedelta(minutes=15)
        
        # Weights for different sources
        self.source_weights = {
            'fear_greed': 0.40,
            'news': 0.30,
            'social': 0.20,
            'technical': 0.10
        }
        
    def get_market_sentiment(self, symbol: str = 'BTC') -> Dict:
        """
        Get aggregated market sentiment
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Sentiment analysis dict
        """
        # Check cache
        cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d%H%M')[:11]}"  # 15-min buckets
        if cache_key in self.sentiment_cache:
            logger.info(f"Using cached sentiment for {symbol}")
            return self.sentiment_cache[cache_key]
        
        sentiments = {}
        
        # 1. Fear & Greed Index (most reliable)
        sentiments['fear_greed'] = self._get_fear_greed_index()
        
        # 2. News sentiment (simplified)
        sentiments['news'] = self._analyze_news_sentiment(symbol)
        
        # 3. Social sentiment (Twitter/Reddit proxy)
        sentiments['social'] = self._analyze_social_sentiment(symbol)
        
        # 4. Technical sentiment
        sentiments['technical'] = self._analyze_technical_sentiment()
        
        # Aggregate
        overall = self._aggregate_sentiment(sentiments)
        
        result = {
            'overall_score': overall,  # -1 (extreme fear) to 1 (extreme greed)
            'direction': self._score_to_direction(overall),
            'confidence': self._calculate_confidence(sentiments),
            'by_source': sentiments,
            'timestamp': datetime.now().isoformat(),
            'recommendation': self._generate_recommendation(overall)
        }
        
        # Cache result
        self.sentiment_cache[cache_key] = result
        
        return result
    
    def _get_fear_greed_index(self) -> Dict:
        """
        Get Fear & Greed Index from Alternative.me
        """
        try:
            url = "https://api.alternative.me/fng/?limit=1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'data' in data and len(data['data']) > 0:
                    index_data = data['data'][0]
                    value = int(index_data['value'])
                    
                    # Convert 0-100 to -1 to 1 scale
                    # 0 = extreme fear (-1), 50 = neutral (0), 100 = extreme greed (1)
                    normalized = (value - 50) / 50
                    
                    return {
                        'score': normalized,
                        'value': value,
                        'classification': index_data['value_classification'],
                        'source': 'alternative.me'
                    }
        except Exception as e:
            logger.warning(f"Fear & Greed Index error: {e}")
        
        # Default to neutral
        return {
            'score': 0,
            'value': 50,
            'classification': 'Neutral',
            'source': 'default'
        }
    
    def _analyze_news_sentiment(self, symbol: str) -> Dict:
        """
        Analyze news sentiment (simplified - placeholder for real API)
        
        In production, integrate:
        - NewsAPI.org
        - CryptoPanic API
        - Google News API
        """
        # Placeholder logic - returns neutral with slight randomness
        import random
        
        # Simulate news sentiment based on recent price action
        base_sentiment = random.uniform(-0.3, 0.3)
        
        return {
            'score': base_sentiment,
            'article_count': random.randint(5, 20),
            'positive': random.randint(3, 12),
            'negative': random.randint(2, 8),
            'neutral': random.randint(5, 10),
            'source': 'simulated'
        }
    
    def _analyze_social_sentiment(self, symbol: str) -> Dict:
        """
        Analyze social media sentiment
        
        In production, integrate:
        - Twitter API (mentions, hashtags)
        - Reddit API (r/cryptocurrency, r/bitcoin)
        - Telegram groups
        - Discord channels
        """
        import random
        
        # Placeholder - simulate social sentiment
        social_score = random.uniform(-0.4, 0.4)
        
        return {
            'score': social_score,
            'mentions': random.randint(100, 1000),
            'positive_ratio': random.uniform(0.4, 0.7),
            'trending': random.choice([True, False]),
            'source': 'simulated'
        }
    
    def _analyze_technical_sentiment(self) -> Dict:
        """
        Derive sentiment from technical indicators
        """
        # This would typically analyze RSI, MACD, etc.
        # Placeholder for now
        return {
            'score': 0.1,  # Slightly bullish
            'indicators': {
                'rsi': 'neutral',
                'macd': 'bullish',
                'ma_trend': 'bullish'
            },
            'source': 'technical_indicators'
        }
    
    def _aggregate_sentiment(self, sentiments: Dict) -> float:
        """
        Aggregate sentiment from all sources using weighted average
        """
        total_score = 0
        total_weight = 0
        
        for source, weight in self.source_weights.items():
            if source in sentiments and 'score' in sentiments[source]:
                total_score += sentiments[source]['score'] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0
        
        return total_score / total_weight
    
    def _score_to_direction(self, score: float) -> str:
        """Convert sentiment score to direction"""
        if score > 0.3:
            return 'BULLISH'
        elif score < -0.3:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _calculate_confidence(self, sentiments: Dict) -> float:
        """Calculate confidence based on source agreement"""
        scores = [s['score'] for s in sentiments.values() if 'score' in s]
        
        if not scores:
            return 0.5
        
        # Calculate standard deviation (lower = more agreement = higher confidence)
        import statistics
        if len(scores) > 1:
            std = statistics.stdev(scores)
            # Convert to confidence (0 = low confidence, 1 = high confidence)
            confidence = max(0, 1 - (std * 2))
            return confidence
        
        return 0.7  # Single source
    
    def _generate_recommendation(self, score: float) -> str:
        """Generate trading recommendation"""
        if score > 0.5:
            return "Strong bullish sentiment - Consider LONG positions"
        elif score > 0.2:
            return "Moderately bullish - Cautiously optimistic"
        elif score < -0.5:
            return "Strong bearish sentiment - Avoid LONG, consider staying out"
        elif score < -0.2:
            return "Moderately bearish - Reduce exposure"
        else:
            return "Neutral sentiment - Wait for clearer signals"
    
    def get_sentiment_history(self, hours: int = 24) -> List[Dict]:
        """Get sentiment history (cached values)"""
        # Return cached sentiment values
        history = []
        for key, value in self.sentiment_cache.items():
            if 'timestamp' in value:
                history.append(value)
        
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)[:hours]


# Global instance
sentiment_analyzer = SentimentAnalyzer()
