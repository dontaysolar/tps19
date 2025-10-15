#!/usr/bin/env python3
"""
Real-time Market Data Feed
API integration for crypto.com and Alpha Vantage
"""

import json
import requests
import sqlite3
import threading
import time
import os
from datetime import datetime
import logging
from typing import Dict, List, Optional

class RealtimeDataFeed:
    def __init__(self):
        self.db_path = "/opt/tps19/data/market_data.db"
        self.config_path = "/workspace/config/api_config.json"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.load_config()
        self.init_database()
        self.active = False
        self.data_thread = None
        
    def load_config(self):
        """Load API configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            self.config = {
                "crypto_com": {"api_url": "https://api.crypto.com/v2"},
                "alpha_vantage": {"api_url": "https://www.alphavantage.co/query"}
            }
        
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
                # Fetch data from crypto.com API
                symbols = ['BTC_USDT', 'ETH_USDT', 'ADA_USDT', 'SOL_USDT', 'LINK_USDT']
                
                for symbol in symbols:
                    data = self.fetch_price_data(symbol)
                    if data:
                        self.store_market_data(data)
                        
                time.sleep(60)  # Update every minute (API rate limit friendly)
                
            except Exception as e:
                print(f"❌ Data feed error: {e}")
                time.sleep(120)  # Wait longer on error
                
    def fetch_price_data(self, symbol):
        """Fetch price data from crypto.com API"""
        try:
            url = f"{self.config['crypto_com']['api_url']}/public/get-ticker"
            params = {'instrument_name': symbol}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('code') == 0 and data.get('result'):
                ticker = data['result']['data'][0]
                return {
                    'symbol': symbol,
                    'price': float(ticker['a']),  # Ask price
                    'volume': float(ticker['v']),  # 24h volume
                    'market_cap': 0,  # Not available in ticker
                    'price_change_24h': float(ticker['c']),  # 24h change
                    'source': 'crypto.com'
                }
            else:
                # Fallback to Alpha Vantage
                return self.fetch_alpha_vantage_data(symbol)
                
        except Exception as e:
            print(f"❌ API fetch error for {symbol}: {e}")
            
        return None
        
    def fetch_alpha_vantage_data(self, symbol):
        """Fetch data from Alpha Vantage as fallback"""
        try:
            api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
            base_symbol = symbol.split('_')[0] if '_' in symbol else symbol
            
            url = self.config['alpha_vantage']['api_url']
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': base_symbol,
                'to_currency': 'USD',
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Realtime Currency Exchange Rate' in data:
                rate_data = data['Realtime Currency Exchange Rate']
                return {
                    'symbol': symbol,
                    'price': float(rate_data['5. Exchange Rate']),
                    'volume': 0,  # Not available
                    'market_cap': 0,  # Not available
                    'price_change_24h': 0,  # Not available in this endpoint
                    'source': 'alpha_vantage'
                }
                
        except Exception as e:
            print(f"❌ Alpha Vantage fetch error for {symbol}: {e}")
            
        return None
        
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
    data = feed.fetch_price_data('BTC_USDT')
    if data:
        feed.store_market_data(data)
        print(f"✅ Test data stored: {data}")
        
    # Test latest price
    latest = feed.get_latest_price('BTC_USDT')
    if latest:
        print(f"✅ Latest BTC price: ${latest['price']:,.2f}")