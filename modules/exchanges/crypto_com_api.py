#!/usr/bin/env python3
"""Crypto.com API Integration Module for TPS19"""

import requests
import json
import time
import hmac
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
import sqlite3
import os

class CryptoComAPI:
    """Crypto.com API Integration for TPS19 Trading System"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, sandbox: bool = True):
        self.api_key = api_key or os.getenv('CRYPTO_COM_API_KEY', '')
        self.secret_key = secret_key or os.getenv('CRYPTO_COM_SECRET_KEY', '')
        self.sandbox = sandbox
        self.base_url = "https://api.crypto.com/v2" if not sandbox else "https://sandbox-api.crypto.com/v2"
        self.db_path = "/workspace/data/databases/crypto_com_data.db"
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
        
        self._init_database()
        
    def _init_database(self):
        """Initialize database for crypto.com data"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Market data table
            cursor.execute("""CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume_24h REAL,
                change_24h REAL,
                high_24h REAL,
                low_24h REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exchange TEXT DEFAULT 'crypto.com'
            )""")
            
            conn.commit()
            conn.close()
            print("✅ Crypto.com database initialized")
            
        except Exception as e:
            print(f"❌ Crypto.com database initialization failed: {e}")
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None, method: str = 'GET') -> Dict:
        """Make authenticated request to crypto.com API"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}{endpoint}"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'TPS19-Trading-System/1.0'
            }
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            else:
                response = requests.post(url, headers=headers, json=params, timeout=10)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Crypto.com API request failed: {e}")
            return {}
        except Exception as e:
            print(f"❌ Crypto.com API error: {e}")
            return {}
    
    def get_ticker(self, symbol: str = 'BTC_USDT') -> Dict:
        """Get ticker data for a symbol"""
        try:
            params = {'instrument_name': symbol}
            response = self._make_request('/public/get-ticker', params)
            
            if response and 'result' in response:
                ticker_data = response['result']['data']
                
                # Store in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""INSERT INTO market_data 
                    (symbol, price, volume_24h, change_24h, high_24h, low_24h)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (symbol,
                     float(ticker_data.get('a', 0)),  # ask price
                     float(ticker_data.get('v', 0)),  # volume
                     float(ticker_data.get('c', 0)),  # change
                     float(ticker_data.get('h', 0)),  # high
                     float(ticker_data.get('l', 0))))  # low
                
                conn.commit()
                conn.close()
                
                return {
                    'symbol': symbol,
                    'price': float(ticker_data.get('a', 0)),
                    'volume_24h': float(ticker_data.get('v', 0)),
                    'change_24h': float(ticker_data.get('c', 0)),
                    'high_24h': float(ticker_data.get('h', 0)),
                    'low_24h': float(ticker_data.get('l', 0)),
                    'timestamp': datetime.now().isoformat(),
                    'exchange': 'crypto.com'
                }
            return {}
            
        except Exception as e:
            print(f"❌ Failed to get ticker for {symbol}: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self._make_request('/public/get-instruments')
            if response and 'result' in response:
                print("✅ Crypto.com API connection successful")
                return True
            else:
                print("❌ Crypto.com API connection failed")
                return False
        except Exception as e:
            print(f"❌ Crypto.com API connection test failed: {e}")
            return False

# Global instance
crypto_com_api = CryptoComAPI()
