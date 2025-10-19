#!/usr/bin/env python3
"""Reddit Sentiment Bot - Track WSB and crypto subreddits"""
from datetime import datetime
from typing import Dict, List

class RedditSentimentBot:
    def __init__(self):
        self.name = "Reddit_Sentiment"
        self.version = "1.0.0"
        self.enabled = True
        
        self.subreddits = ['wallstreetbets', 'cryptocurrency', 'bitcoin', 'ethereum']
        self.metrics = {'posts_analyzed': 0, 'comments_analyzed': 0}
    
    def analyze_post(self, post: Dict) -> Dict:
        """Analyze Reddit post sentiment"""
        title = post.get('title', '').lower()
        upvotes = post.get('upvotes', 0)
        comments = post.get('num_comments', 0)
        
        # Sentiment keywords
        bullish_keywords = ['buy', 'calls', 'moon', 'bullish', 'pump', 'long', 'to the moon']
        bearish_keywords = ['sell', 'puts', 'bearish', 'dump', 'short', 'crash']
        
        bullish_score = sum([1 for kw in bullish_keywords if kw in title])
        bearish_score = sum([1 for kw in bearish_keywords if kw in title])
        
        # Weight by engagement
        engagement_weight = min(upvotes / 1000, 10) + min(comments / 100, 5)
        
        sentiment = (bullish_score - bearish_score) / max(bullish_score + bearish_score, 1)
        weighted_sentiment = sentiment * engagement_weight
        
        self.metrics['posts_analyzed'] += 1
        
        return {'sentiment': sentiment, 'weighted_sentiment': weighted_sentiment, 'engagement': engagement_weight}
    
    def aggregate_subreddit_sentiment(self, posts: List[Dict]) -> Dict:
        """Aggregate sentiment from subreddit"""
        sentiments = [self.analyze_post(p) for p in posts]
        avg_sentiment = sum([s['weighted_sentiment'] for s in sentiments]) / len(sentiments) if sentiments else 0
        
        if avg_sentiment > 2:
            signal, confidence = 'BUY', 0.75
        elif avg_sentiment < -2:
            signal, confidence = 'SELL', 0.75
        else:
            signal, confidence = 'HOLD', 0.50
        
        return {
            'sentiment_score': avg_sentiment,
            'posts_analyzed': len(posts),
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'subreddits': self.subreddits, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = RedditSentimentBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
