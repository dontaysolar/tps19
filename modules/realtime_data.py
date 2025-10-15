#!/usr/bin/env python3
"""
Real-time Market Data Feed
Primary source: Crypto.com public API
Fallback: Alpha Vantage (requires ALPHA_VANTAGE_API_KEY)
"""

import json
import os
import requests
from services.path_config import path
import sqlite3
import threading
import time
import os
from datetime import datetime
import logging

class RealtimeDataFeed:
    def __init__(self):
        self.db_path = path('data/market_data.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
        self.active = False
        self.data_thread = None
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        
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
    
    def ensure_schema_exists(self):
        """Idempotently ensure the market_data table exists for connectivity tests."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM market_data LIMIT 1")
            conn.close()
        except Exception:
            # Re-init if missing
            self.init_database()
        
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
                # Fetch data from Crypto.com (preferred)
                instruments = ['BTC_USDT', 'ETH_USDT', 'ADA_USDT', 'SOL_USDT', 'LINK_USDT']
                for instrument in instruments:
                    data = self.fetch_price_data(instrument)
                    if data:
                        self.store_market_data(data)
                        
                time.sleep(60)  # Update every minute (API rate limit friendly)
                
            except Exception as e:
                print(f"❌ Data feed error: {e}")
                time.sleep(120)  # Wait longer on error
                
    def fetch_price_data(self, instrument_name):
        """Fetch price data from Crypto.com, fallback to Alpha Vantage"""
        # Primary: Crypto.com public ticker
        try:
            url = "https://api.crypto.com/v2/public/get-ticker"
            params = {"instrument_name": instrument_name}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
            if payload.get("result") and payload["result"].get("data"):
                entry = payload["result"]["data"][0]
                price_str = entry.get("k") or entry.get("c") or entry.get("a") or entry.get("b")
                price = float(price_str) if price_str is not None else None
                if price is not None:
                    return {
                        'symbol': instrument_name,
                        'price': price,
                        'volume': float(entry.get('v', 0) or 0),
                        'market_cap': 0.0,
                        'price_change_24h': float(entry.get('chg_pct', 0) or 0),
                        'source': 'crypto.com'
                    }
        except Exception as e:
            print(f"❌ Crypto.com API fetch error for {instrument_name}: {e}")

        # Fallback: Alpha Vantage
        try:
            if not self.alpha_vantage_key:
                raise RuntimeError("Alpha Vantage API key not set")
            symbol_base = instrument_name.split("_")[0].replace("USD", "BTC").replace("USDT", "BTC") if instrument_name.endswith("BTC") else instrument_name.split("_")[0]
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "CRYPTO_INTRADAY",
                "symbol": symbol_base,
                "market": "USD",
                "interval": "5min",
                "apikey": self.alpha_vantage_key,
            }
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            series = data.get("Time Series Crypto (5min)") or {}
            latest_ts = next(iter(series.keys())) if series else None
            if latest_ts:
                bar = series[latest_ts]
                price = float(bar.get("4. close") or bar.get("1. open"))
                volume = float(bar.get("5. volume", 0)) if "5. volume" in bar else 0.0
                return {
                    'symbol': instrument_name,
                    'price': price,
                    'volume': volume,
                    'market_cap': 0.0,
                    'price_change_24h': 0.0,
                    'source': 'alpha_vantage'
                }
        except Exception as e:
            print(f"❌ Alpha Vantage API fetch error for {instrument_name}: {e}")

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

    # Test data fetch using Crypto.com instrument naming
    instrument = 'BTC_USDT'
    data = feed.fetch_price_data(instrument)
    if data:
        feed.store_market_data(data)
        print(f"✅ Test data stored: {data}")

    # Test latest price
    latest = feed.get_latest_price(instrument)
    if latest:
        print(f"✅ Latest {instrument} price: ${latest['price']:,.2f}")
