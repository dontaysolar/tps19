#!/usr/bin/env python3
"""TPS19 Market Data - Real-time market data functionality"""

import json
import requests
import sqlite3
import time
import os
import sys
from datetime import datetime

# Add exchanges to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from exchanges.crypto_com import CryptoComAPI
    from exchanges.alpha_vantage import AlphaVantageAPI
except ImportError:
    print("Warning: Exchange modules not found, using fallback")
    CryptoComAPI = None
    AlphaVantageAPI = None

class MarketData:
    def __init__(self):
        self.db_path = "/opt/tps19/data/databases/market_data.db"
        self.init_database()
        
        # Initialize exchange APIs
        self.crypto_com = CryptoComAPI() if CryptoComAPI else None
        self.alpha_vantage = AlphaVantageAPI() if AlphaVantageAPI else None
        
        # Default to crypto.com for crypto data
        self.primary_exchange = "crypto.com"
        
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
        
    def get_price(self, symbol="BTC_USDT"):
        """Get current price for a symbol"""
        try:
            price = None
            volume = 0
            
            # Try crypto.com first for crypto pairs
            if self.crypto_com and "_" in symbol:
                ticker = self.crypto_com.get_ticker(symbol)
                price = ticker.get('price', 0)
                volume = ticker.get('volume', 0)
            
            # Try Alpha Vantage for other symbols or as fallback
            elif self.alpha_vantage:
                # Convert symbol format
                if "_" in symbol:
                    base, quote = symbol.split("_")
                else:
                    base, quote = symbol, "USD"
                    
                rate_data = self.alpha_vantage.get_crypto_exchange_rate(base, quote)
                price = rate_data.get('exchange_rate', 0)
            
            # Fallback to mock data
            if not price or price == 0:
                price = self._get_mock_price(symbol)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO price_data (symbol, price, volume)
                VALUES (?, ?, ?)
            ''', (symbol, price, volume))
            conn.commit()
            conn.close()
            
            return price
            
        except Exception as e:
            print(f"Error getting price: {e}")
            return self._get_mock_price(symbol)
    
    def _get_mock_price(self, symbol):
        """Generate mock price for testing"""
        base_prices = {
            "BTC_USDT": 45000.0,
            "ETH_USDT": 3000.0,
            "bitcoin": 45000.0,
            "ethereum": 3000.0
        }
        base = base_prices.get(symbol, 100.0)
        return base + (time.time() % 1000)
            
    def get_market_stats(self, symbol="BTC_USDT"):
        """Get market statistics"""
        try:
            stats = {}
            
            # Try crypto.com for crypto pairs
            if self.crypto_com and "_" in symbol:
                ticker = self.crypto_com.get_ticker(symbol)
                stats = {
                    "price": ticker.get('price', 0),
                    "high_24h": ticker.get('high_24h', 0),
                    "low_24h": ticker.get('low_24h', 0),
                    "change_24h": ticker.get('change_24h', 0),
                    "volume": ticker.get('volume', 0)
                }
            
            # Try Alpha Vantage as fallback
            elif self.alpha_vantage:
                if "_" in symbol:
                    base, _ = symbol.split("_")
                else:
                    base = symbol
                    
                daily_data = self.alpha_vantage.get_crypto_daily(base)
                stats = {
                    "price": daily_data.get('close', 0),
                    "high_24h": daily_data.get('high', 0),
                    "low_24h": daily_data.get('low', 0),
                    "change_24h": ((daily_data.get('close', 0) / daily_data.get('open', 1)) - 1) * 100,
                    "volume": daily_data.get('volume', 0)
                }
            
            # Return mock data if all APIs fail
            if not stats or stats.get('price', 0) == 0:
                return self._get_mock_stats(symbol)
                
            return stats
            
        except Exception as e:
            print(f"Error getting market stats: {e}")
            return self._get_mock_stats(symbol)
    
    def _get_mock_stats(self, symbol):
        """Generate mock market stats"""
        price = self._get_mock_price(symbol)
        return {
            "price": price,
            "high_24h": price * 1.05,
            "low_24h": price * 0.95,
            "change_24h": 2.5,
            "volume": 1000000.0
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

    def get_candlestick_data(self, symbol="BTC_USDT", timeframe="1h", count=100):
        """Get candlestick/OHLC data"""
        try:
            if self.crypto_com and "_" in symbol:
                return self.crypto_com.get_candlestick(symbol, timeframe, count)
            else:
                # Fallback to mock data
                return self._get_mock_candlestick(symbol, timeframe, count)
        except Exception as e:
            print(f"Error getting candlestick data: {e}")
            return self._get_mock_candlestick(symbol, timeframe, count)
    
    def _get_mock_candlestick(self, symbol, timeframe, count):
        """Generate mock candlestick data"""
        candles = []
        base_price = self._get_mock_price(symbol)
        current_time = int(time.time() * 1000)
        
        # Timeframe to milliseconds
        tf_ms = {
            "1m": 60000,
            "5m": 300000,
            "15m": 900000,
            "30m": 1800000,
            "1h": 3600000,
            "4h": 14400000,
            "1d": 86400000
        }
        
        interval_ms = tf_ms.get(timeframe, 3600000)
        
        for i in range(count):
            timestamp = current_time - (i * interval_ms)
            open_price = base_price * (1 + (i % 20 - 10) * 0.001)
            high_price = open_price * 1.002
            low_price = open_price * 0.998
            close_price = base_price * (1 + ((i + 5) % 20 - 10) * 0.001)
            
            candles.append({
                "timestamp": timestamp,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": 10000 + (i % 100) * 100
            })
            
        return list(reversed(candles))

    def get_technical_indicators(self, symbol="BTC_USDT", indicator="RSI"):
        """Get technical indicators"""
        try:
            if self.alpha_vantage:
                # Convert symbol format for Alpha Vantage
                if "_" in symbol:
                    base, _ = symbol.split("_")
                else:
                    base = symbol
                    
                return self.alpha_vantage.get_technical_indicators(base, indicator)
            else:
                # Return mock indicator
                return {
                    "symbol": symbol,
                    "indicator": indicator,
                    "value": 50 + (time.time() % 30) - 15,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            print(f"Error getting technical indicator: {e}")
            return {"symbol": symbol, "indicator": indicator, "value": 50}

if __name__ == "__main__":
    market = MarketData()
    price = market.get_price("BTC_USDT")
    print(f"Market Data initialized successfully. Current BTC/USDT price: ${price:.2f}")
    
    # Test market stats
    stats = market.get_market_stats("BTC_USDT")
    print(f"24h High: ${stats['high_24h']:.2f}, 24h Low: ${stats['low_24h']:.2f}")
