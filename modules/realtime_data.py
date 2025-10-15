#!/usr/bin/env python3
"""
Real-time Market Data Feed for TPS19
Integrated with crypto.com and Alpha Vantage APIs
"""

import json
import requests
import sqlite3
import threading
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

class RealtimeDataFeed:
    def __init__(self):
        self.db_path = "/opt/tps19/data/market_data.db"
        self.crypto_com_api = "https://api.crypto.com/v2"
        self.alpha_vantage_api = "https://www.alphavantage.co/query"
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
        self.active = False
        self.data_thread = None
        self.tracked_symbols = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT']
        
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
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_feed_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Real-time data database initialized")
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
        self._log_action("start_feed", "success", "Real-time data feed started")
        print("✅ Real-time data feed started")
        
    def stop_feed(self):
        """Stop real-time data feed"""
        self.active = False
        if self.data_thread:
            self.data_thread.join(timeout=5)
        self._log_action("stop_feed", "success", "Real-time data feed stopped")
        print("✅ Real-time data feed stopped")
            
    def _data_loop(self):
        """Main data collection loop"""
        while self.active:
            try:
                for symbol in self.tracked_symbols:
                    # Try crypto.com first
                    data = self.fetch_price_from_crypto_com(symbol)
                    
                    # Fallback to Alpha Vantage if crypto.com fails
                    if not data:
                        data = self.fetch_price_from_alpha_vantage(symbol)
                    
                    if data:
                        self.store_market_data(data)
                    else:
                        # Use simulated data if both APIs fail
                        data = self._generate_simulated_data(symbol)
                        self.store_market_data(data)
                        
                    time.sleep(2)  # Delay between symbols to avoid rate limits
                        
                time.sleep(60)  # Update cycle every 60 seconds
                
            except Exception as e:
                self._log_action("data_loop", "error", str(e))
                print(f"❌ Data feed error: {e}")
                time.sleep(120)  # Wait longer on error
                
    def fetch_price_from_crypto_com(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch price data from crypto.com API"""
        try:
            instrument_name = f"{symbol}_USDT"
            url = f"{self.crypto_com_api}/public/get-ticker"
            params = {'instrument_name': instrument_name}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('code') == 0 and 'result' in data:
                result = data['result']['data']
                if result:
                    ticker = result[0]
                    return {
                        'symbol': symbol,
                        'price': float(ticker.get('a', 0)),
                        'volume': float(ticker.get('v', 0)),
                        'market_cap': 0,  # crypto.com doesn't provide market cap
                        'price_change_24h': float(ticker.get('c', 0)),
                        'source': 'crypto.com'
                    }
            
            self._log_action("fetch_crypto_com", "failed", f"Failed to fetch {symbol}")
            return None
                
        except Exception as e:
            self._log_action("fetch_crypto_com", "error", f"{symbol}: {str(e)}")
            return None
    
    def fetch_price_from_alpha_vantage(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch price data from Alpha Vantage API"""
        try:
            url = self.alpha_vantage_api
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': symbol,
                'to_currency': 'USD',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Realtime Currency Exchange Rate' in data:
                rate_data = data['Realtime Currency Exchange Rate']
                return {
                    'symbol': symbol,
                    'price': float(rate_data['5. Exchange Rate']),
                    'volume': 0,  # Alpha Vantage crypto endpoint doesn't provide volume
                    'market_cap': 0,
                    'price_change_24h': 0,
                    'source': 'alpha_vantage'
                }
            elif 'Note' in data:
                # API rate limit
                self._log_action("fetch_alpha_vantage", "rate_limit", f"{symbol}: {data['Note']}")
                return None
            
            self._log_action("fetch_alpha_vantage", "failed", f"Failed to fetch {symbol}")
            return None
                
        except Exception as e:
            self._log_action("fetch_alpha_vantage", "error", f"{symbol}: {str(e)}")
            return None
    
    def _generate_simulated_data(self, symbol: str) -> Dict[str, Any]:
        """Generate simulated data for testing when APIs are unavailable"""
        base_prices = {
            'BTC': 45000,
            'ETH': 2500,
            'ADA': 0.5,
            'SOL': 100,
            'DOT': 7.5
        }
        
        base_price = base_prices.get(symbol, 100)
        variation = (time.time() % 1000) / 10
        price = base_price + variation
        
        return {
            'symbol': symbol,
            'price': price,
            'volume': 1500000 + (time.time() % 100000),
            'market_cap': price * 1000000,
            'price_change_24h': (variation / base_price) * 100,
            'source': 'simulated'
        }
        
    def store_market_data(self, data: Dict[str, Any]):
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
            self._log_action("store_data", "error", str(e))
            print(f"❌ Data storage error: {e}")
    
    def _log_action(self, action: str, status: str, details: str = ""):
        """Log feed actions to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO data_feed_log (action, status, details)
                VALUES (?, ?, ?)
            """, (action, status, details))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Log error: {e}")
            
    def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price for symbol"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT price, volume, price_change_24h, source, timestamp FROM market_data 
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
                    'source': result[3],
                    'timestamp': result[4]
                }
                
        except Exception as e:
            print(f"❌ Price fetch error: {e}")
            
        return None
        
    def get_market_summary(self) -> List[Dict[str, Any]]:
        """Get market summary for all tracked symbols"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT symbol, price, volume, price_change_24h, source, timestamp
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
                    'source': row[4],
                    'timestamp': row[5]
                }
                for row in results
            ]
        except Exception as e:
            print(f"❌ Market summary error: {e}")
            return []
    
    def get_feed_statistics(self) -> Dict[str, Any]:
        """Get statistics about data feed performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count data points by source
            cursor.execute("""
                SELECT source, COUNT(*) 
                FROM market_data 
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY source
            """)
            source_counts = dict(cursor.fetchall())
            
            # Get recent log entries
            cursor.execute("""
                SELECT action, status, COUNT(*) 
                FROM data_feed_log 
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY action, status
            """)
            log_stats = cursor.fetchall()
            
            conn.close()
            
            return {
                'source_counts': source_counts,
                'log_stats': [{'action': row[0], 'status': row[1], 'count': row[2]} for row in log_stats],
                'tracked_symbols': self.tracked_symbols,
                'feed_active': self.active
            }
        except Exception as e:
            print(f"❌ Statistics error: {e}")
            return {}

if __name__ == "__main__":
    feed = RealtimeDataFeed()
    print("✅ Real-time Data Feed initialized")
    
    print("\n🔍 Testing crypto.com API...")
    data = feed.fetch_price_from_crypto_com('BTC')
    if data:
        print(f"✅ crypto.com test: {data['symbol']} = ${data['price']:,.2f} (Source: {data['source']})")
    else:
        print("⚠️ crypto.com API not available")
    
    print("\n🔍 Testing Alpha Vantage API...")
    data = feed.fetch_price_from_alpha_vantage('BTC')
    if data:
        print(f"✅ Alpha Vantage test: {data['symbol']} = ${data['price']:,.2f} (Source: {data['source']})")
    else:
        print("⚠️ Alpha Vantage API not available or rate limited")
    
    print("\n📊 Market Summary:")
    summary = feed.get_market_summary()
    for item in summary:
        print(f"  {item['symbol']}: ${item['price']:,.2f} (Source: {item['source']})")
    
    print("\n✅ Real-time Data Feed Module Ready")
