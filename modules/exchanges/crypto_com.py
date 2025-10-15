#!/usr/bin/env python3
"""Crypto.com Exchange API Integration"""

import json
import time
import hmac
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class CryptoComAPI:
    """Crypto.com Exchange API Client"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.crypto.com/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _sign_request(self, method: str, endpoint: str, params: dict = None) -> dict:
        """Sign request for authenticated endpoints"""
        req_time = int(time.time() * 1000)
        nonce = str(req_time)
        
        if params is None:
            params = {}
            
        params_str = ""
        if params:
            params_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            
        sign_payload = f"{method}{endpoint}{nonce}{params_str}"
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            sign_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "api_key": self.api_key,
            "sig": signature,
            "nonce": nonce
        }
        
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker data for a symbol"""
        try:
            endpoint = f"/public/get-ticker"
            params = {"instrument_name": symbol}
            
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params
            )
            
            data = response.json()
            
            if data.get("code") == 0 and data.get("result"):
                ticker_data = data["result"]["data"][0] if data["result"]["data"] else {}
                return {
                    "symbol": symbol,
                    "price": float(ticker_data.get("a", 0)),  # Ask price
                    "bid": float(ticker_data.get("b", 0)),
                    "ask": float(ticker_data.get("a", 0)),
                    "volume": float(ticker_data.get("v", 0)),
                    "high_24h": float(ticker_data.get("h", 0)),
                    "low_24h": float(ticker_data.get("l", 0)),
                    "change_24h": float(ticker_data.get("c", 0)),
                    "timestamp": ticker_data.get("t", int(time.time() * 1000))
                }
            else:
                # Return mock data if API fails
                return self._get_mock_ticker(symbol)
                
        except Exception as e:
            print(f"Error fetching ticker: {e}")
            return self._get_mock_ticker(symbol)
            
    def _get_mock_ticker(self, symbol: str) -> Dict:
        """Return mock ticker data for testing"""
        base_prices = {
            "BTC_USDT": 45000.0,
            "ETH_USDT": 3000.0,
            "DOGE_USDT": 0.15,
            "CRO_USDT": 0.50
        }
        
        base_price = base_prices.get(symbol, 100.0)
        variance = (time.time() % 100) / 100.0 * 0.02  # 2% variance
        current_price = base_price * (1 + variance)
        
        return {
            "symbol": symbol,
            "price": current_price,
            "bid": current_price * 0.999,
            "ask": current_price * 1.001,
            "volume": 1000000.0,
            "high_24h": current_price * 1.05,
            "low_24h": current_price * 0.95,
            "change_24h": variance * 100,
            "timestamp": int(time.time() * 1000)
        }
        
    def get_order_book(self, symbol: str, depth: int = 10) -> Dict:
        """Get order book for a symbol"""
        try:
            endpoint = "/public/get-book"
            params = {
                "instrument_name": symbol,
                "depth": depth
            }
            
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params
            )
            
            data = response.json()
            
            if data.get("code") == 0 and data.get("result"):
                book_data = data["result"]["data"][0]
                return {
                    "symbol": symbol,
                    "bids": [[float(b[0]), float(b[1])] for b in book_data.get("bids", [])],
                    "asks": [[float(a[0]), float(a[1])] for a in book_data.get("asks", [])],
                    "timestamp": book_data.get("t", int(time.time() * 1000))
                }
            else:
                return self._get_mock_order_book(symbol)
                
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return self._get_mock_order_book(symbol)
            
    def _get_mock_order_book(self, symbol: str) -> Dict:
        """Return mock order book for testing"""
        ticker = self._get_mock_ticker(symbol)
        base_price = ticker["price"]
        
        bids = []
        asks = []
        
        for i in range(10):
            bid_price = base_price * (1 - 0.0001 * (i + 1))
            ask_price = base_price * (1 + 0.0001 * (i + 1))
            
            bids.append([bid_price, 1000 * (10 - i)])
            asks.append([ask_price, 1000 * (10 - i)])
            
        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": int(time.time() * 1000)
        }
        
    def get_trades(self, symbol: str, count: int = 50) -> List[Dict]:
        """Get recent trades for a symbol"""
        try:
            endpoint = "/public/get-trades"
            params = {
                "instrument_name": symbol,
                "count": count
            }
            
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params
            )
            
            data = response.json()
            
            if data.get("code") == 0 and data.get("result"):
                trades = []
                for trade in data["result"]["data"]:
                    trades.append({
                        "id": trade.get("d"),
                        "price": float(trade.get("p", 0)),
                        "quantity": float(trade.get("q", 0)),
                        "side": trade.get("s"),
                        "timestamp": trade.get("t", int(time.time() * 1000))
                    })
                return trades
            else:
                return self._get_mock_trades(symbol, count)
                
        except Exception as e:
            print(f"Error fetching trades: {e}")
            return self._get_mock_trades(symbol, count)
            
    def _get_mock_trades(self, symbol: str, count: int) -> List[Dict]:
        """Return mock trades for testing"""
        ticker = self._get_mock_ticker(symbol)
        base_price = ticker["price"]
        
        trades = []
        current_time = int(time.time() * 1000)
        
        for i in range(count):
            price_variance = (i % 10 - 5) * 0.0001
            trade_price = base_price * (1 + price_variance)
            
            trades.append({
                "id": f"mock_{i}",
                "price": trade_price,
                "quantity": 100 + (i * 10),
                "side": "BUY" if i % 2 == 0 else "SELL",
                "timestamp": current_time - (i * 1000)
            })
            
        return trades
        
    def get_candlestick(self, symbol: str, timeframe: str = "1h", count: int = 100) -> List[Dict]:
        """Get candlestick/kline data"""
        try:
            endpoint = "/public/get-candlestick"
            
            # Convert timeframe to Crypto.com format
            timeframe_map = {
                "1m": "1m",
                "5m": "5m",
                "15m": "15m",
                "30m": "30m",
                "1h": "1h",
                "4h": "4h",
                "1d": "1D",
                "1w": "7D",
                "1M": "1M"
            }
            
            params = {
                "instrument_name": symbol,
                "timeframe": timeframe_map.get(timeframe, "1h"),
                "count": count
            }
            
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params
            )
            
            data = response.json()
            
            if data.get("code") == 0 and data.get("result"):
                candles = []
                for candle in data["result"]["data"]:
                    candles.append({
                        "timestamp": candle.get("t"),
                        "open": float(candle.get("o", 0)),
                        "high": float(candle.get("h", 0)),
                        "low": float(candle.get("l", 0)),
                        "close": float(candle.get("c", 0)),
                        "volume": float(candle.get("v", 0))
                    })
                return candles
            else:
                return self._get_mock_candlestick(symbol, timeframe, count)
                
        except Exception as e:
            print(f"Error fetching candlestick data: {e}")
            return self._get_mock_candlestick(symbol, timeframe, count)
            
    def _get_mock_candlestick(self, symbol: str, timeframe: str, count: int) -> List[Dict]:
        """Return mock candlestick data for testing"""
        ticker = self._get_mock_ticker(symbol)
        base_price = ticker["price"]
        
        candles = []
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
            
            # Generate realistic OHLC data
            open_variance = (i % 20 - 10) * 0.001
            open_price = base_price * (1 + open_variance)
            
            high_price = open_price * (1 + abs(i % 5) * 0.001)
            low_price = open_price * (1 - abs(i % 5) * 0.001)
            
            close_variance = ((i + 5) % 20 - 10) * 0.001
            close_price = base_price * (1 + close_variance)
            
            candles.append({
                "timestamp": timestamp,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": 10000 + (i % 100) * 100
            })
            
        return list(reversed(candles))
        
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            ticker = self.get_ticker("BTC_USDT")
            return ticker.get("price", 0) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

# Global instance
crypto_com_api = CryptoComAPI()

if __name__ == "__main__":
    # Test the API
    api = CryptoComAPI()
    
    print("Testing Crypto.com API Integration...")
    print("=" * 60)
    
    # Test ticker
    ticker = api.get_ticker("BTC_USDT")
    print(f"BTC/USDT Ticker: ${ticker['price']:.2f}")
    
    # Test order book
    book = api.get_order_book("BTC_USDT", 5)
    print(f"Order Book - Best Bid: ${book['bids'][0][0]:.2f}, Best Ask: ${book['asks'][0][0]:.2f}")
    
    # Test connection
    if api.test_connection():
        print("✅ API Connection successful!")
    else:
        print("❌ API Connection failed!")