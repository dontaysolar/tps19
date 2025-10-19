#!/usr/bin/env python3
"""Twitter Sentiment Bot - Real-time social sentiment from Twitter/X"""
from datetime import datetime
from typing import Dict, List

class TwitterSentimentBot:
    def __init__(self):
        self.name = "Twitter_Sentiment"
        self.version = "1.0.0"
        self.enabled = True
        
        self.tracked_keywords = ['bitcoin', 'crypto', 'btc', 'eth', 'bullish', 'bearish']
        self.influencer_weights = {'elonmusk': 10, 'VitalikButerin': 8, 'cz_binance': 7}
        
        self.metrics = {'tweets_analyzed': 0, 'sentiment_shifts': 0}
    
    def analyze_tweet(self, tweet: Dict) -> Dict:
        """Analyze single tweet sentiment"""
        text = tweet.get('text', '').lower()
        author = tweet.get('author', '')
        
        # Simple sentiment scoring
        bullish_words = ['moon', 'bullish', 'buy', 'pump', 'up', 'breakout', 'surge']
        bearish_words = ['crash', 'bearish', 'sell', 'dump', 'down', 'breakdown', 'drop']
        
        bullish_count = sum([1 for word in bullish_words if word in text])
        bearish_count = sum([1 for word in bearish_words if word in text])
        
        sentiment = (bullish_count - bearish_count) / max(bullish_count + bearish_count, 1)
        
        # Apply influencer weight
        weight = self.influencer_weights.get(author, 1)
        weighted_sentiment = sentiment * weight
        
        self.metrics['tweets_analyzed'] += 1
        
        return {'sentiment': sentiment, 'weighted_sentiment': weighted_sentiment, 'weight': weight}
    
    def aggregate_sentiment(self, tweets: List[Dict]) -> Dict:
        """Aggregate sentiment from multiple tweets"""
        if not tweets:
            return {'sentiment_score': 0, 'signal': 'HOLD'}
        
        sentiments = [self.analyze_tweet(t) for t in tweets]
        avg_sentiment = sum([s['weighted_sentiment'] for s in sentiments]) / len(sentiments)
        
        if avg_sentiment > 0.3:
            signal, confidence = 'BUY', min(0.85, 0.60 + avg_sentiment * 0.25)
        elif avg_sentiment < -0.3:
            signal, confidence = 'SELL', min(0.85, 0.60 + abs(avg_sentiment) * 0.25)
        else:
            signal, confidence = 'HOLD', 0.50
        
        return {
            'sentiment_score': avg_sentiment,
            'tweets_analyzed': len(tweets),
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'keywords': self.tracked_keywords, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = TwitterSentimentBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
