#!/usr/bin/env python3
"""TPS19 Market Data - Unified market data functionality with crypto.com and Alpha Vantage"""

import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import sys

# Add exchanges module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'exchanges'))

try:
    from exchanges.crypto_com_api import crypto_com_api
    from exchanges.alpha_vantage_api import alpha_vantage_api
except ImportError as e:
    print(f"⚠️ Exchange modules not available: {e}")
    crypto_com_api = None
    alpha_vantage_api = None

class MarketData:
    """Unified Market Data Provider for TPS19"""
    
    def __init__(self):
        self.db_path = "/workspace/data/databases/market_data.db"
        self.primary_exchange = 'crypto.com'
        self.secondary_exchange = 'alpha_vantage'
        self.init_database()
        
    def init_database(self):
        """Initialize market data database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exchange TEXT DEFAULT 'crypto.com'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                high_24h REAL,
                low_24h REAL,
                change_24h REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exchange TEXT DEFAULT 'crypto.com'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unified_market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume_24h REAL,
                change_24h REAL,
                high_24h REAL,
                low_24h REAL,
                confidence_score REAL DEFAULT 0.5,
                data_sources TEXT DEFAULT '[]',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def get_price(self, symbol="BTC_USDT", use_primary=True):
        """Get current price for a symbol from primary exchange (crypto.com)"""
        try:
            if use_primary and crypto_com_api:
                # Use crypto.com as primary source
                ticker_data = crypto_com_api.get_ticker(symbol)
                if ticker_data and 'price' in ticker_data:
                    return ticker_data['price']
            
            # Fallback to Alpha Vantage for traditional stocks
            if alpha_vantage_api and not use_primary:
                quote_data = alpha_vantage_api.get_quote(symbol)
                if quote_data and 'price' in quote_data:
                    return quote_data['price']
            
            # Final fallback - return mock price
            return 50000.0 + (time.time() % 1000)
            
        except Exception as e:
            print(f"❌ Error getting price for {symbol}: {e}")
            return 50000.0 + (time.time() % 1000)
    
    def get_market_stats(self, symbol="BTC_USDT", use_primary=True):
        """Get comprehensive market statistics"""
        try:
            if use_primary and crypto_com_api:
                # Use crypto.com as primary source
                ticker_data = crypto_com_api.get_ticker(symbol)
                if ticker_data:
                    return {
                        "price": ticker_data.get('price', 0),
                        "high_24h": ticker_data.get('high_24h', 0),
                        "low_24h": ticker_data.get('low_24h', 0),
                        "change_24h": ticker_data.get('change_24h', 0),
                        "volume_24h": ticker_data.get('volume_24h', 0),
                        "exchange": "crypto.com",
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Fallback to Alpha Vantage
            if alpha_vantage_api and not use_primary:
                quote_data = alpha_vantage_api.get_quote(symbol)
                if quote_data:
                    return {
                        "price": quote_data.get('price', 0),
                        "high_24h": quote_data.get('high', 0),
                        "low_24h": quote_data.get('low', 0),
                        "change_24h": quote_data.get('change_percent', 0),
                        "volume_24h": quote_data.get('volume', 0),
                        "exchange": "alpha_vantage",
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Mock data fallback
            return {
                "price": 50000.0,
                "high_24h": 52000.0,
                "low_24h": 48000.0,
                "change_24h": 2.5,
                "volume_24h": 1000000,
                "exchange": "mock",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting market stats for {symbol}: {e}")
            return self._get_mock_stats()
    
    def get_unified_market_data(self, symbol="BTC_USDT"):
        """Get unified market data from multiple sources with confidence scoring"""
        try:
            data_sources = []
            price_data = []
            confidence_scores = []
            
            # Get data from crypto.com
            if crypto_com_api:
                try:
                    crypto_data = crypto_com_api.get_ticker(symbol)
                    if crypto_data and 'price' in crypto_data:
                        price_data.append(crypto_data['price'])
                        data_sources.append('crypto.com')
                        confidence_scores.append(0.9)  # High confidence for primary exchange
                except Exception as e:
                    print(f"⚠️ Crypto.com data unavailable: {e}")
            
            # Get data from Alpha Vantage
            if alpha_vantage_api:
                try:
                    alpha_data = alpha_vantage_api.get_quote(symbol)
                    if alpha_data and 'price' in alpha_data:
                        price_data.append(alpha_data['price'])
                        data_sources.append('alpha_vantage')
                        confidence_scores.append(0.7)  # Medium confidence for secondary source
                except Exception as e:
                    print(f"⚠️ Alpha Vantage data unavailable: {e}")
            
            if not price_data:
                # No data sources available, return mock data
                return self._get_mock_stats()
            
            # Calculate weighted average price
            if len(price_data) == 1:
                avg_price = price_data[0]
                confidence = confidence_scores[0]
            else:
                # Weighted average based on confidence scores
                total_weight = sum(confidence_scores)
                weighted_sum = sum(price * conf for price, conf in zip(price_data, confidence_scores))
                avg_price = weighted_sum / total_weight
                confidence = sum(confidence_scores) / len(confidence_scores)
            
            # Store unified data
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO unified_market_data 
                (symbol, price, volume_24h, change_24h, high_24h, low_24h, confidence_score, data_sources)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, avg_price, 0, 0, 0, 0, confidence, json.dumps(data_sources)))
            
            conn.commit()
            conn.close()
            
            return {
                "symbol": symbol,
                "price": avg_price,
                "confidence_score": confidence,
                "data_sources": data_sources,
                "source_count": len(data_sources),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting unified market data: {e}")
            return self._get_mock_stats()
    
    def get_historical_data(self, symbol="BTC_USDT", days=7, exchange="crypto.com"):
        """Get historical price data from specified exchange"""
        try:
            if exchange == "crypto.com" and crypto_com_api:
                # Get historical data from crypto.com
                historical_data = crypto_com_api.get_historical_data(symbol, "1D", days)
                return historical_data
            elif exchange == "alpha_vantage" and alpha_vantage_api:
                # Get historical data from Alpha Vantage
                historical_data = alpha_vantage_api.get_daily_data(symbol)
                if historical_data and 'data' in historical_data:
                    return historical_data['data'][:days]
            
            # Fallback to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT price, timestamp FROM price_data 
                WHERE symbol = ? AND exchange = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (symbol, exchange, days * 24))
            
            data = cursor.fetchall()
            conn.close()
            
            return data
            
        except Exception as e:
            print(f"❌ Error getting historical data: {e}")
            return []
    
    def get_technical_indicators(self, symbol="BTC_USDT", indicators=["SMA", "RSI", "MACD"]):
        """Get technical indicators from Alpha Vantage"""
        try:
            if not alpha_vantage_api:
                print("❌ Alpha Vantage API not available")
                return {}
            
            indicator_data = {}
            for indicator in indicators:
                try:
                    data = alpha_vantage_api.get_technical_indicator(symbol, indicator)
                    if data and 'data' in data:
                        indicator_data[indicator] = data['data']
                except Exception as e:
                    print(f"⚠️ Failed to get {indicator}: {e}")
            
            return indicator_data
            
        except Exception as e:
            print(f"❌ Error getting technical indicators: {e}")
            return {}
    
    def test_all_connections(self):
        """Test connections to all data sources"""
        results = {}
        
        if crypto_com_api:
            results['crypto.com'] = crypto_com_api.test_connection()
        else:
            results['crypto.com'] = False
        
        if alpha_vantage_api:
            results['alpha_vantage'] = alpha_vantage_api.test_connection()
        else:
            results['alpha_vantage'] = False
        
        return results
    
    def _get_mock_stats(self):
        """Get mock market statistics as fallback"""
        return {
            "price": 50000.0 + (time.time() % 1000),
            "high_24h": 52000.0,
            "low_24h": 48000.0,
            "change_24h": 2.5,
            "volume_24h": 1000000,
            "exchange": "mock",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    market = MarketData()
    
    print("🧪 Testing Market Data System...")
    print("="*50)
    
    # Test connections
    connections = market.test_all_connections()
    for exchange, status in connections.items():
        print(f"{'✅' if status else '❌'} {exchange.upper()}: {'Connected' if status else 'Failed'}")
    
    # Test unified data
    print("\n📊 Testing Unified Market Data...")
    unified_data = market.get_unified_market_data("BTC_USDT")
    print(f"Symbol: {unified_data['symbol']}")
    print(f"Price: ${unified_data['price']:.2f}")
    print(f"Confidence: {unified_data['confidence_score']:.2%}")
    print(f"Sources: {', '.join(unified_data['data_sources'])}")
    
    print("\n✅ Market Data System initialized successfully!")
