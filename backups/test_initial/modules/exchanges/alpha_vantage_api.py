#!/usr/bin/env python3
"""Alpha Vantage API Integration Module for TPS19"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
import os

class AlphaVantageAPI:
    """Alpha Vantage API Integration for TPS19 Trading System"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
        self.db_path = "/workspace/data/databases/alpha_vantage_data.db"
        self.rate_limit_delay = 12  # Alpha Vantage free tier: 5 calls per minute
        self.last_request_time = 0
        
        self._init_database()
        
    def _init_database(self):
        """Initialize database for Alpha Vantage data"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Market data table
            cursor.execute("""CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL,
                change_percent REAL,
                high REAL,
                low REAL,
                open_price REAL,
                close_price REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exchange TEXT DEFAULT 'alpha_vantage'
            )""")
            
            # Technical indicators table
            cursor.execute("""CREATE TABLE IF NOT EXISTS technical_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                indicator_name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exchange TEXT DEFAULT 'alpha_vantage'
            )""")
            
            conn.commit()
            conn.close()
            print("✅ Alpha Vantage database initialized")
            
        except Exception as e:
            print(f"❌ Alpha Vantage database initialization failed: {e}")
    
    def _rate_limit(self):
        """Implement rate limiting for Alpha Vantage free tier"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict) -> Dict:
        """Make request to Alpha Vantage API"""
        try:
            self._rate_limit()
            
            params['apikey'] = self.api_key
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                print(f"❌ Alpha Vantage API error: {data['Error Message']}")
                return {}
            elif 'Note' in data:
                print(f"⚠️ Alpha Vantage API note: {data['Note']}")
                return {}
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Alpha Vantage API request failed: {e}")
            return {}
        except Exception as e:
            print(f"❌ Alpha Vantage API error: {e}")
            return {}
    
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote for a symbol"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol
            }
            
            response = self._make_request(params)
            
            if response and 'Global Quote' in response:
                quote = response['Global Quote']
                
                # Store in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""INSERT INTO market_data 
                    (symbol, price, volume, change_percent, high, low, open_price, close_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (symbol,
                     float(quote.get('05. price', 0)),
                     float(quote.get('06. volume', 0)),
                     float(quote.get('10. change percent', 0).replace('%', '')),
                     float(quote.get('03. high', 0)),
                     float(quote.get('04. low', 0)),
                     float(quote.get('02. open', 0)),
                     float(quote.get('08. previous close', 0))))
                
                conn.commit()
                conn.close()
                
                return {
                    'symbol': symbol,
                    'price': float(quote.get('05. price', 0)),
                    'volume': float(quote.get('06. volume', 0)),
                    'change_percent': float(quote.get('10. change percent', 0).replace('%', '')),
                    'high': float(quote.get('03. high', 0)),
                    'low': float(quote.get('04. low', 0)),
                    'open': float(quote.get('02. open', 0)),
                    'previous_close': float(quote.get('08. previous close', 0)),
                    'timestamp': datetime.now().isoformat(),
                    'exchange': 'alpha_vantage'
                }
            return {}
            
        except Exception as e:
            print(f"❌ Failed to get quote for {symbol}: {e}")
            return {}
    
    def get_daily_data(self, symbol: str, outputsize: str = 'compact') -> Dict:
        """Get daily time series data"""
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': outputsize
            }
            
            response = self._make_request(params)
            
            if response and 'Time Series (Daily)' in response:
                time_series = response['Time Series (Daily)']
                
                # Convert to list format
                daily_data = []
                for date, data in time_series.items():
                    daily_data.append({
                        'date': date,
                        'open': float(data['1. open']),
                        'high': float(data['2. high']),
                        'low': float(data['3. low']),
                        'close': float(data['4. close']),
                        'volume': float(data['5. volume']),
                        'symbol': symbol,
                        'exchange': 'alpha_vantage'
                    })
                
                return {
                    'symbol': symbol,
                    'data': daily_data,
                    'metadata': response.get('Meta Data', {}),
                    'timestamp': datetime.now().isoformat(),
                    'exchange': 'alpha_vantage'
                }
            return {}
            
        except Exception as e:
            print(f"❌ Failed to get daily data for {symbol}: {e}")
            return {}
    
    def get_technical_indicator(self, symbol: str, indicator: str, interval: str = 'daily', time_period: int = 20) -> Dict:
        """Get technical indicator data"""
        try:
            # Map indicator names to Alpha Vantage functions
            indicator_functions = {
                'SMA': 'SMA',
                'EMA': 'EMA',
                'RSI': 'RSI',
                'MACD': 'MACD',
                'BBANDS': 'BBANDS',
                'STOCH': 'STOCH'
            }
            
            if indicator not in indicator_functions:
                print(f"❌ Unsupported indicator: {indicator}")
                return {}
            
            params = {
                'function': indicator_functions[indicator],
                'symbol': symbol,
                'interval': interval,
                'time_period': time_period
            }
            
            # Add specific parameters for certain indicators
            if indicator == 'MACD':
                params.update({'series_type': 'close'})
            elif indicator == 'BBANDS':
                params.update({'series_type': 'close', 'nbdevup': 2, 'nbdevdn': 2})
            elif indicator == 'STOCH':
                params.update({'fastkperiod': 5, 'slowkperiod': 3, 'slowdperiod': 3})
            
            response = self._make_request(params)
            
            if response and f'Technical Analysis: {indicator}' in response:
                indicator_data = response[f'Technical Analysis: {indicator}']
                
                # Store in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                for date, data in indicator_data.items():
                    if indicator == 'MACD':
                        cursor.execute("""INSERT INTO technical_indicators 
                            (symbol, indicator_name, value, timestamp)
                            VALUES (?, ?, ?, ?)""",
                            (symbol, f"{indicator}_MACD", float(data.get('MACD', 0)), date))
                        cursor.execute("""INSERT INTO technical_indicators 
                            (symbol, indicator_name, value, timestamp)
                            VALUES (?, ?, ?, ?)""",
                            (symbol, f"{indicator}_Signal", float(data.get('MACD_Signal', 0)), date))
                        cursor.execute("""INSERT INTO technical_indicators 
                            (symbol, indicator_name, value, timestamp)
                            VALUES (?, ?, ?, ?)""",
                            (symbol, f"{indicator}_Hist", float(data.get('MACD_Hist', 0)), date))
                    elif indicator == 'BBANDS':
                        cursor.execute("""INSERT INTO technical_indicators 
                            (symbol, indicator_name, value, timestamp)
                            VALUES (?, ?, ?, ?)""",
                            (symbol, f"{indicator}_Upper", float(data.get('Real Upper Band', 0)), date))
                        cursor.execute("""INSERT INTO technical_indicators 
                            (symbol, indicator_name, value, timestamp)
                            VALUES (?, ?, ?, ?)""",
                            (symbol, f"{indicator}_Middle", float(data.get('Real Middle Band', 0)), date))
                        cursor.execute("""INSERT INTO technical_indicators 
                            (symbol, indicator_name, value, timestamp)
                            VALUES (?, ?, ?, ?)""",
                            (symbol, f"{indicator}_Lower", float(data.get('Real Lower Band', 0)), date))
                    else:
                        cursor.execute("""INSERT INTO technical_indicators 
                            (symbol, indicator_name, value, timestamp)
                            VALUES (?, ?, ?, ?)""",
                            (symbol, indicator, float(data.get(indicator, 0)), date))
                
                conn.commit()
                conn.close()
                
                return {
                    'symbol': symbol,
                    'indicator': indicator,
                    'data': indicator_data,
                    'timestamp': datetime.now().isoformat(),
                    'exchange': 'alpha_vantage'
                }
            return {}
            
        except Exception as e:
            print(f"❌ Failed to get {indicator} for {symbol}: {e}")
            return {}
    
    def get_crypto_quote(self, symbol: str, market: str = 'USD') -> Dict:
        """Get cryptocurrency quote"""
        try:
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': symbol,
                'to_currency': market
            }
            
            response = self._make_request(params)
            
            if response and 'Realtime Currency Exchange Rate' in response:
                exchange_rate = response['Realtime Currency Exchange Rate']
                
                return {
                    'from_currency': exchange_rate.get('1. From_Currency Code', ''),
                    'to_currency': exchange_rate.get('3. To_Currency Code', ''),
                    'exchange_rate': float(exchange_rate.get('5. Exchange Rate', 0)),
                    'last_refreshed': exchange_rate.get('6. Last Refreshed', ''),
                    'time_zone': exchange_rate.get('7. Time Zone', ''),
                    'timestamp': datetime.now().isoformat(),
                    'exchange': 'alpha_vantage'
                }
            return {}
            
        except Exception as e:
            print(f"❌ Failed to get crypto quote for {symbol}: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Test with a simple quote request
            response = self.get_quote('IBM')
            if response and 'price' in response:
                print("✅ Alpha Vantage API connection successful")
                return True
            else:
                print("❌ Alpha Vantage API connection failed")
                return False
        except Exception as e:
            print(f"❌ Alpha Vantage API connection test failed: {e}")
            return False

# Global instance
alpha_vantage_api = AlphaVantageAPI()
