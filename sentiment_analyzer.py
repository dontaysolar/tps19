#!/usr/bin/env python3
"""
Basic Sentiment Analyzer for Crypto Markets
Scrapes Twitter/Reddit for BTC, ETH sentiment
"""

import requests
import re
from datetime import datetime, timedelta
import time

class SentimentAnalyzer:
    """Analyzes market sentiment from social media"""
    
    def __init__(self):
        self.coins = ['BTC', 'ETH', 'SOL', 'ADA']
        self.sentiment_scores = {}
        
    def get_reddit_sentiment(self, coin):
        """Get sentiment from Reddit (using pushshift API)"""
        try:
            # Reddit search via pushshift (no auth needed)
            url = f"https://api.pushshift.io/reddit/search/comment/?q={coin}&size=100&sort=desc"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return 0.0
            
            data = response.json()
            comments = data.get('data', [])
            
            if not comments:
                return 0.0
            
            # Simple keyword-based sentiment
            positive_words = ['moon', 'bullish', 'buy', 'pump', 'up', 'gain', 'profit', 'long']
            negative_words = ['crash', 'bearish', 'sell', 'dump', 'down', 'loss', 'short', 'fear']
            
            pos_count = 0
            neg_count = 0
            
            for comment in comments:
                body = comment.get('body', '').lower()
                pos_count += sum(1 for word in positive_words if word in body)
                neg_count += sum(1 for word in negative_words if word in body)
            
            total = pos_count + neg_count
            if total == 0:
                return 0.0
            
            # Score: -1 (very bearish) to +1 (very bullish)
            score = (pos_count - neg_count) / total
            return score
            
        except Exception as e:
            print(f"Reddit sentiment error for {coin}: {e}")
            return 0.0
    
    def get_twitter_sentiment(self, coin):
        """Get sentiment from Twitter (using nitter scraping)"""
        try:
            # Use nitter (Twitter scraper, no API key needed)
            url = f"https://nitter.net/search?q={coin}%20crypto&f=tweets"
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code != 200:
                return 0.0
            
            # Simple keyword extraction
            text = response.text.lower()
            
            positive_words = ['moon', 'bullish', 'buy', 'pump', 'rocket', 'ath', 'breakout']
            negative_words = ['crash', 'bearish', 'sell', 'dump', 'rekt', 'fud', 'scam']
            
            pos_count = sum(text.count(word) for word in positive_words)
            neg_count = sum(text.count(word) for word in negative_words)
            
            total = pos_count + neg_count
            if total == 0:
                return 0.0
            
            score = (pos_count - neg_count) / total
            return score
            
        except Exception as e:
            print(f"Twitter sentiment error for {coin}: {e}")
            return 0.0
    
    def get_combined_sentiment(self, coin):
        """Combine Reddit + Twitter sentiment"""
        reddit_score = self.get_reddit_sentiment(coin)
        twitter_score = self.get_twitter_sentiment(coin)
        
        # Weight: 60% Reddit, 40% Twitter (Reddit more reliable)
        combined = (reddit_score * 0.6) + (twitter_score * 0.4)
        
        self.sentiment_scores[coin] = {
            'reddit': reddit_score,
            'twitter': twitter_score,
            'combined': combined,
            'timestamp': datetime.now().isoformat()
        }
        
        return combined
    
    def get_all_sentiments(self):
        """Get sentiment for all tracked coins"""
        results = {}
        for coin in self.coins:
            score = self.get_combined_sentiment(coin)
            results[coin] = score
            time.sleep(2)  # Rate limiting
        
        return results
    
    def get_signal(self, coin):
        """Get trading signal from sentiment"""
        score = self.sentiment_scores.get(coin, {}).get('combined', 0)
        
        if score > 0.3:
            return 'BUY', abs(score)
        elif score < -0.3:
            return 'SELL', abs(score)
        else:
            return 'HOLD', abs(score)

if __name__ == '__main__':
    analyzer = SentimentAnalyzer()
    
    print("🧠 Analyzing Market Sentiment...\n")
    
    sentiments = analyzer.get_all_sentiments()
    
    for coin, score in sentiments.items():
        signal, confidence = analyzer.get_signal(coin)
        emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
        
        print(f"{emoji} {coin}: {score:+.2f} → {signal} ({confidence:.1%} confidence)")
