#!/usr/bin/env python3
"""
NEWS API INTEGRATION
Real news sentiment analysis using multiple sources
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List
import os

class NewsAPIIntegration:
    """CryptoNews aggregation from multiple sources"""
    
    def __init__(self):
        self.name = "News_API"
        self.version = "1.0.0"
        
        # API keys from environment
        self.newsapi_key = os.getenv('NEWS_API_KEY', '')
        self.cryptopanic_key = os.getenv('CRYPTOPANIC_API_KEY', '')
        
        self.enabled = {
            'newsapi': bool(self.newsapi_key and self.newsapi_key != 'YOUR_NEWS_API_KEY'),
            'cryptopanic': bool(self.cryptopanic_key and self.cryptopanic_key != 'YOUR_CRYPTOPANIC_KEY')
        }
        
        if not any(self.enabled.values()):
            print("⚠️  No news APIs configured - using placeholder data")
    
    def get_crypto_news(self, symbol: str = 'BTC', limit: int = 10) -> List[Dict]:
        """Get latest crypto news from all sources"""
        all_news = []
        
        # Try NewsAPI
        if self.enabled['newsapi']:
            news = self._fetch_newsapi(symbol, limit)
            all_news.extend(news)
        
        # Try CryptoPanic
        if self.enabled['cryptopanic']:
            news = self._fetch_cryptopanic(symbol, limit)
            all_news.extend(news)
        
        # Fallback to placeholder
        if not all_news:
            all_news = self._placeholder_news(symbol, limit)
        
        # Sort by recency and limit
        all_news.sort(key=lambda x: x['published_at'], reverse=True)
        return all_news[:limit]
    
    def _fetch_newsapi(self, symbol: str, limit: int) -> List[Dict]:
        """Fetch from NewsAPI.org"""
        try:
            # Map crypto symbols to search terms
            search_terms = {
                'BTC': 'Bitcoin',
                'ETH': 'Ethereum',
                'SOL': 'Solana',
                'BNB': 'Binance',
                'XRP': 'Ripple',
                'ADA': 'Cardano'
            }
            
            query = search_terms.get(symbol.replace('/USDT', ''), symbol)
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': query,
                'apiKey': self.newsapi_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get('articles', []):
                    articles.append({
                        'source': 'NewsAPI',
                        'title': article['title'],
                        'description': article.get('description', ''),
                        'url': article['url'],
                        'published_at': article['publishedAt'],
                        'sentiment': self._analyze_sentiment(article['title'] + ' ' + article.get('description', ''))
                    })
                
                return articles
            else:
                print(f"⚠️  NewsAPI error: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"❌ NewsAPI error: {e}")
            return []
    
    def _fetch_cryptopanic(self, symbol: str, limit: int) -> List[Dict]:
        """Fetch from CryptoPanic API"""
        try:
            # CryptoPanic uses currency codes
            currency = symbol.replace('/USDT', '').lower()
            
            url = 'https://cryptopanic.com/api/v1/posts/'
            params = {
                'auth_token': self.cryptopanic_key,
                'currencies': currency,
                'kind': 'news',
                'public': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for post in data.get('results', [])[:limit]:
                    # CryptoPanic provides votes (positive/negative/important)
                    votes = post.get('votes', {})
                    sentiment_score = (
                        votes.get('positive', 0) - votes.get('negative', 0)
                    ) / max(votes.get('positive', 0) + votes.get('negative', 0), 1)
                    
                    articles.append({
                        'source': 'CryptoPanic',
                        'title': post['title'],
                        'description': '',
                        'url': post['url'],
                        'published_at': post['published_at'],
                        'sentiment': 'POSITIVE' if sentiment_score > 0.2 else 'NEGATIVE' if sentiment_score < -0.2 else 'NEUTRAL',
                        'sentiment_score': sentiment_score
                    })
                
                return articles
            else:
                print(f"⚠️  CryptoPanic error: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"❌ CryptoPanic error: {e}")
            return []
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        text = text.lower()
        
        # Positive keywords
        positive = ['bullish', 'surge', 'rally', 'gain', 'rise', 'soar', 'boom', 
                   'high', 'profit', 'success', 'growth', 'adoption', 'upgrade']
        
        # Negative keywords
        negative = ['bearish', 'crash', 'drop', 'fall', 'decline', 'plunge', 'loss',
                   'down', 'fail', 'hack', 'scam', 'regulation', 'ban']
        
        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)
        
        if pos_count > neg_count:
            return 'POSITIVE'
        elif neg_count > pos_count:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'
    
    def _placeholder_news(self, symbol: str, limit: int) -> List[Dict]:
        """Placeholder news when no APIs configured"""
        base_time = datetime.now()
        
        return [
            {
                'source': 'PLACEHOLDER',
                'title': f'{symbol} Market Analysis - Technical Indicators Show Mixed Signals',
                'description': 'Placeholder news - Configure NEWS_API_KEY for real data',
                'url': 'https://example.com',
                'published_at': (base_time - timedelta(hours=i)).isoformat(),
                'sentiment': 'NEUTRAL'
            }
            for i in range(limit)
        ]
    
    def get_sentiment_summary(self, symbol: str) -> Dict:
        """Get aggregated sentiment from recent news"""
        news = self.get_crypto_news(symbol, limit=20)
        
        if not news:
            return {
                'sentiment': 'NEUTRAL',
                'score': 0,
                'confidence': 0,
                'article_count': 0
            }
        
        # Count sentiments
        sentiments = [article['sentiment'] for article in news]
        positive = sentiments.count('POSITIVE')
        negative = sentiments.count('NEGATIVE')
        neutral = sentiments.count('NEUTRAL')
        
        total = len(sentiments)
        
        # Calculate score (-1 to +1)
        score = (positive - negative) / total
        
        # Determine overall sentiment
        if score > 0.2:
            overall = 'POSITIVE'
        elif score < -0.2:
            overall = 'NEGATIVE'
        else:
            overall = 'NEUTRAL'
        
        return {
            'sentiment': overall,
            'score': score,
            'confidence': abs(score),
            'article_count': total,
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'recent_headlines': [n['title'] for n in news[:5]]
        }


if __name__ == '__main__':
    # Test news API
    news_api = NewsAPIIntegration()
    
    print("🗞️  Testing News API Integration\n")
    
    symbols = ['BTC', 'ETH']
    
    for symbol in symbols:
        print(f"\n--- {symbol} News ---")
        
        # Get news
        articles = news_api.get_crypto_news(symbol, limit=5)
        
        for article in articles:
            print(f"\n{article['sentiment']} | {article['source']}")
            print(f"  {article['title']}")
            print(f"  {article['published_at']}")
        
        # Get sentiment summary
        summary = news_api.get_sentiment_summary(symbol)
        print(f"\n📊 Sentiment Summary:")
        print(f"  Overall: {summary['sentiment']}")
        print(f"  Score: {summary['score']:.2f}")
        print(f"  Articles: {summary['article_count']}")
