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
from datetime import datetime
import logging

class RealtimeDataFeed:
    def __init__(self):
        self.db_path = "/opt/tps19/data/market_data.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
        self.active = False
        self.data_thread = None
        
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
                # Fetch data from CoinGecko API (free tier)
                symbols = ['bitcoin', 'ethereum', 'cardano', 'solana', 'chainlink']
                
                for symbol in symbols:
                    data = self.fetch_price_data(symbol)
                    if data:
                        self.store_market_data(data)
                        
                time.sleep(60)  # Update every minute (API rate limit friendly)
                
            except Exception as e:
                print(f"❌ Data feed error: {e}")
                time.sleep(120)  # Wait longer on error
                
    def fetch_price_data(self, symbol):
        """Fetch price data from API"""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': symbol,
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if symbol in data:
                coin_data = data[symbol]
                return {
                    'symbol': symbol.upper(),
                    'price': coin_data['usd'],
                    'volume': coin_data.get('usd_24h_vol', 0),
                    'market_cap': coin_data.get('usd_market_cap', 0),
                    'price_change_24h': coin_data.get('usd_24h_change', 0),
                    'source': 'coingecko'
                }
                
        except Exception as e:
            print(f"❌ API fetch error for {symbol}: {e}")
            
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
    data = feed.fetch_price_data('bitcoin')
    if data:
        feed.store_market_data(data)
        print(f"✅ Test data stored: {data}")
        
    # Test latest price
    latest = feed.get_latest_price('BITCOIN')
    if latest:
        print(f"✅ Latest BTC price: ${latest['price']:,.2f}")
