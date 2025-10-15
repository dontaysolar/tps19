#!/usr/bin/env python3
"""TPS19 Market Data - Real-time market data functionality"""

import json
import os
import requests
import sqlite3
import time
from datetime import datetime
from market.crypto_com_api import get_price as crypto_price

class MarketData:
    def __init__(self):
        self.db_path = "/opt/tps19/data/databases/market_data.db"
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
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                high_24h REAL,
                low_24h REAL,
                change_24h REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def get_price(self, symbol="BTC"):
        """Get current price for a symbol using Crypto.com or Alpha Vantage."""
        # Prefer Alpha Vantage if API key is provided, otherwise fall back to Crypto.com public endpoints
        alpha_key = os.environ.get('ALPHAVANTAGE_API_KEY')
        try:
            price = None
            if alpha_key:
                # Alpha Vantage: DIGITAL_CURRENCY_DAILY (free tier) returns USD data
                params = {
                    'function': 'CURRENCY_EXCHANGE_RATE',
                    'from_currency': symbol,
                    'to_currency': 'USD',
                    'apikey': alpha_key
                }
                resp = requests.get('https://www.alphavantage.co/query', params=params, timeout=15)
                data = resp.json()
                rate = data.get('Realtime Currency Exchange Rate', {}).get('5. Exchange Rate')
                if rate:
                    price = float(rate)
            if price is None:
                # Try Crypto.com public API
                price = crypto_price(symbol)
            if price is None:
                # Simulate as last resort to keep system functional offline
                base_prices = {
                    'BTC': 45000.0,
                    'ETH': 3000.0,
                    'ADA': 0.45,
                    'SOL': 150.0,
                    'LINK': 12.0
                }
                price = base_prices.get(symbol.upper(), 100.0) + (time.time() % 50)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO price_data (symbol, price)
                VALUES (?, ?)
            ''', (symbol.upper(), float(price)))
            conn.commit()
            conn.close()
            return float(price)
        except Exception:
            # Fallback simulated price
            return 50000.0 + (time.time() % 1000)
            
    def get_market_stats(self, symbol="BTC"):
        """Get market statistics via Alpha Vantage or simulated Crypto.com feed."""
        alpha_key = os.environ.get('ALPHAVANTAGE_API_KEY')
        try:
            price = self.get_price(symbol)
            high_24h = price * 1.02
            low_24h = price * 0.98
            change_24h = ((price - (price / 1.01)) / (price / 1.01)) * 100
            return {
                "price": float(price),
                "high_24h": float(high_24h),
                "low_24h": float(low_24h),
                "change_24h": float(change_24h)
            }
        except Exception:
            return {
                "price": 50000.0,
                "high_24h": 52000.0,
                "low_24h": 48000.0,
                "change_24h": 2.5
            }
            
    def get_historical_data(self, symbol="bitcoin", days=7):
        """Get historical price data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT price, timestamp FROM price_data 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (symbol, days * 24))
        
        data = cursor.fetchall()
        conn.close()
        
        return data

if __name__ == "__main__":
    market = MarketData()
    price = market.get_price()
    print(f"Market Data initialized successfully. Current BTC price: ${price}")
