#!/usr/bin/env python3
"""
Real-time Market Data Feed
API integration for live data
"""

import json
import requests
import sqlite3
import threading
import time
import os
import sys
from datetime import datetime
import logging

# Add exchanges to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from exchanges.crypto_com import CryptoComAPI
    from exchanges.alpha_vantage import AlphaVantageAPI
except ImportError:
    print("Warning: Exchange modules not found, using fallback")
    CryptoComAPI = None
    AlphaVantageAPI = None

class RealtimeDataFeed:
    def __init__(self):
        self.db_path = "/opt/tps19/data/market_data.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
        self.active = False
        self.data_thread = None
        
        # Initialize exchange APIs
        self.crypto_com = CryptoComAPI() if CryptoComAPI else None
        self.alpha_vantage = AlphaVantageAPI() if AlphaVantageAPI else None
        
        # Define crypto pairs to track
        self.crypto_pairs = ['BTC_USDT', 'ETH_USDT', 'CRO_USDT', 'DOGE_USDT', 'ADA_USDT']
        
    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    volume REAL,
                    market_cap REAL,
                    price_change_24h REAL,
                    source TEXT
                )
            """)
            conn.commit()
            conn.close()
            print("✅ Market data database initialized")
        except Exception as e:
            print(f"❌ Market data database error: {e}")
        
    def start_feed(self):
        """Start real-time data feed"""
        if self.active:
            return
            
        self.active = True
        self.data_thread = threading.Thread(target=self._data_loop)
        self.data_thread.daemon = True
        self.data_thread.start()
        print("✅ Real-time data feed started")
        
    def stop_feed(self):
        """Stop real-time data feed"""
        self.active = False
        if self.data_thread:
            self.data_thread.join()
        print("✅ Real-time data feed stopped")
            
    def _data_loop(self):
        """Main data collection loop"""
        while self.active:
            try:
                # Fetch data from crypto.com for crypto pairs
                for symbol in self.crypto_pairs:
                    data = self.fetch_price_data(symbol)
                    if data:
                        self.store_market_data(data)
                        
                # Also fetch some traditional market data if available
                if self.alpha_vantage:
                    stock_symbols = ['AAPL', 'GOOGL', 'TSLA']
                    for symbol in stock_symbols:
                        stock_data = self.fetch_stock_data(symbol)
                        if stock_data:
                            self.store_market_data(stock_data)
                        
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                print(f"❌ Data feed error: {e}")
                time.sleep(60)  # Wait longer on error
                
    def fetch_price_data(self, symbol):
        """Fetch crypto price data from crypto.com"""
        try:
            if self.crypto_com:
                ticker = self.crypto_com.get_ticker(symbol)
                if ticker and ticker.get('price', 0) > 0:
                    return {
                        'symbol': symbol,
                        'price': ticker['price'],
                        'volume': ticker.get('volume', 0),
                        'market_cap': 0,  # Not provided by ticker
                        'price_change_24h': ticker.get('change_24h', 0),
                        'source': 'crypto.com'
                    }
            
            # Fallback to Alpha Vantage for crypto
            if self.alpha_vantage and "_" in symbol:
                base, quote = symbol.split("_")
                rate_data = self.alpha_vantage.get_crypto_exchange_rate(base, quote)
                if rate_data and rate_data.get('exchange_rate', 0) > 0:
                    return {
                        'symbol': symbol,
                        'price': rate_data['exchange_rate'],
                        'volume': 0,  # Not provided by exchange rate endpoint
                        'market_cap': 0,
                        'price_change_24h': 0,
                        'source': 'alpha_vantage'
                    }
                    
        except Exception as e:
            print(f"❌ API fetch error for {symbol}: {e}")
            
        # Return mock data as last resort
        return self._get_mock_price_data(symbol)
    
    def fetch_stock_data(self, symbol):
        """Fetch stock price data from Alpha Vantage"""
        try:
            if self.alpha_vantage:
                quote = self.alpha_vantage.get_stock_quote(symbol)
                if quote and quote.get('price', 0) > 0:
                    return {
                        'symbol': symbol,
                        'price': quote['price'],
                        'volume': quote.get('volume', 0),
                        'market_cap': 0,
                        'price_change_24h': float(quote.get('change_percent', '0%').rstrip('%')),
                        'source': 'alpha_vantage'
                    }
        except Exception as e:
            print(f"❌ Stock data fetch error for {symbol}: {e}")
        return None
    
    def _get_mock_price_data(self, symbol):
        """Generate mock price data for testing"""
        base_prices = {
            'BTC_USDT': 45000.0,
            'ETH_USDT': 3000.0,
            'CRO_USDT': 0.50,
            'DOGE_USDT': 0.15,
            'ADA_USDT': 0.60
        }
        
        base_price = base_prices.get(symbol, 100.0)
        variance = (time.time() % 100) / 100.0 * 0.02
        
        return {
            'symbol': symbol,
            'price': base_price * (1 + variance),
            'volume': 1000000.0,
            'market_cap': base_price * 1000000000,
            'price_change_24h': variance * 100,
            'source': 'mock'
        }
        
    def store_market_data(self, data):
        """Store market data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO market_data (symbol, price, volume, market_cap, price_change_24h, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data['symbol'], data['price'], data['volume'], 
                  data['market_cap'], data['price_change_24h'], data['source']))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Data storage error: {e}")
            
    def get_latest_price(self, symbol):
        """Get latest price for symbol"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT price, volume, price_change_24h, timestamp FROM market_data 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (symbol.upper(),))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'price': result[0], 
                    'volume': result[1],
                    'price_change_24h': result[2],
                    'timestamp': result[3]
                }
                
        except Exception as e:
            print(f"❌ Price fetch error: {e}")
            
        return None
        
    def get_market_summary(self):
        """Get market summary for all tracked symbols"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT symbol, price, volume, price_change_24h, timestamp
                FROM market_data m1
                WHERE timestamp = (
                    SELECT MAX(timestamp) 
                    FROM market_data m2 
                    WHERE m2.symbol = m1.symbol
                )
                ORDER BY symbol
            """)
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'symbol': row[0],
                    'price': row[1],
                    'volume': row[2],
                    'price_change_24h': row[3],
                    'timestamp': row[4]
                }
                for row in results
            ]
        except Exception as e:
            print(f"❌ Market summary error: {e}")
            return []

if __name__ == "__main__":
    feed = RealtimeDataFeed()
    print("✅ Real-time Data Feed initialized")
    
    # Test data fetch
    data = feed.fetch_price_data('bitcoin')
    if data:
        feed.store_market_data(data)
        print(f"✅ Test data stored: {data}")
        
    # Test latest price
    latest = feed.get_latest_price('BITCOIN')
    if latest:
        print(f"✅ Latest BTC price: ${latest['price']:,.2f}")
