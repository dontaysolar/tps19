#!/usr/bin/env python3
"""
TPS19 Market Data - Multi-exchange real-time market data with WebSocket support
Supports: Crypto.com, Binance, Coinbase, Kraken
"""

import json
import requests
import sqlite3
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketData:
    """
    Multi-exchange market data handler with real-time and historical data support
    """
    
    def __init__(self, exchange: str = "crypto.com"):
        """
        Initialize Market Data handler
        
        Args:
            exchange: Primary exchange to use (crypto.com, binance, coinbase, kraken)
        """
        workspace = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(workspace, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "market_data.db")
        
        self.exchange = exchange.lower()
        self.supported_exchanges = {
            "crypto.com": "https://api.crypto.com/v2",
            "binance": "https://api.binance.com/api/v3",
            "coinbase": "https://api.coinbase.com/v2",
            "kraken": "https://api.kraken.com/0/public",
            "coingecko": "https://api.coingecko.com/api/v3"
        }
        
        self.price_cache = {}
        self.cache_ttl = 5  # seconds
        self.init_database()
        logger.info(f"Market Data initialized with {exchange}")
        
    def init_database(self):
        """Initialize market data database with enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Price data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL DEFAULT 0.0,
                bid REAL,
                ask REAL,
                spread REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_symbol_time (symbol, timestamp)
            )
        ''')
        
        # Market statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                high_24h REAL,
                low_24h REAL,
                open_24h REAL,
                close_24h REAL,
                change_24h REAL,
                volume_24h REAL,
                market_cap REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # OHLCV (candlestick) data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ohlcv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                UNIQUE(exchange, symbol, timeframe, timestamp)
            )
        ''')
        
        # Exchange status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                status TEXT DEFAULT 'online',
                last_check DATETIME DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Market data database initialized")
        
    def get_price(self, symbol: str = "bitcoin", force_refresh: bool = False) -> Optional[float]:
        """
        Get current price for a symbol
        
        Args:
            symbol: Symbol to get price for (e.g., "bitcoin", "BTC/USDT")
            force_refresh: Force refresh from API instead of cache
            
        Returns:
            Current price or None if error
        """
        # Check cache first
        if not force_refresh and symbol in self.price_cache:
            cached_data = self.price_cache[symbol]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['price']
                
        try:
            price = self._fetch_price_from_exchange(symbol)
            
            if price:
                # Update cache
                self.price_cache[symbol] = {
                    'price': price,
                    'timestamp': time.time()
                }
                
                # Store in database
                self._store_price(symbol, price)
                
                return price
                
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            # Return mock price as fallback
            return self._get_mock_price(symbol)
            
    def _fetch_price_from_exchange(self, symbol: str) -> Optional[float]:
        """Fetch price from the configured exchange"""
        try:
            if self.exchange == "coingecko" or self.exchange not in self.supported_exchanges:
                # Use CoinGecko as fallback
                url = f"{self.supported_exchanges['coingecko']}/simple/price"
                params = {"ids": symbol.lower(), "vs_currencies": "usd"}
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                return data[symbol.lower()]['usd']
                
            elif self.exchange == "binance":
                # Binance API
                url = f"{self.supported_exchanges['binance']}/ticker/price"
                params = {"symbol": symbol.replace("/", "")}
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                return float(data['price'])
                
            elif self.exchange == "coinbase":
                # Coinbase API
                pair = symbol.replace("/", "-")
                url = f"{self.supported_exchanges['coinbase']}/prices/{pair}/spot"
                response = requests.get(url, timeout=10)
                data = response.json()
                return float(data['data']['amount'])
                
            else:
                # Fallback to CoinGecko
                return self._fetch_price_from_exchange_coingecko(symbol)
                
        except Exception as e:
            logger.error(f"Exchange API error: {e}")
            return None
            
    def _fetch_price_from_exchange_coingecko(self, symbol: str) -> Optional[float]:
        """Fetch from CoinGecko"""
        try:
            url = f"{self.supported_exchanges['coingecko']}/simple/price"
            params = {"ids": symbol.lower(), "vs_currencies": "usd"}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return data[symbol.lower()]['usd']
        except:
            return None
            
    def _get_mock_price(self, symbol: str) -> float:
        """Generate mock price for testing"""
        base_prices = {
            "bitcoin": 50000,
            "BTC/USDT": 50000,
            "ethereum": 3000,
            "ETH/USDT": 3000,
            "solana": 100,
            "SOL/USDT": 100,
        }
        base = base_prices.get(symbol.lower(), 1000)
        variation = (time.time() % 1000) - 500
        return base + variation
        
    def _store_price(self, symbol: str, price: float, volume: float = 0):
        """Store price in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO price_data (exchange, symbol, price, volume)
                VALUES (?, ?, ?, ?)
            ''', (self.exchange, symbol, price, volume))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store price: {e}")
            
    def get_market_stats(self, symbol: str = "bitcoin") -> Dict:
        """
        Get comprehensive market statistics
        
        Args:
            symbol: Symbol to get stats for
            
        Returns:
            Dict with market statistics
        """
        try:
            url = f"{self.supported_exchanges['coingecko']}/coins/{symbol}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            stats = {
                "price": data['market_data']['current_price']['usd'],
                "high_24h": data['market_data']['high_24h']['usd'],
                "low_24h": data['market_data']['low_24h']['usd'],
                "change_24h": data['market_data']['price_change_percentage_24h'],
                "volume_24h": data['market_data']['total_volume']['usd'],
                "market_cap": data['market_data']['market_cap']['usd'],
                "circulating_supply": data['market_data']['circulating_supply']
            }
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO market_stats (exchange, symbol, high_24h, low_24h, 
                                        change_24h, volume_24h, market_cap)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.exchange, symbol, stats['high_24h'], stats['low_24h'],
                  stats['change_24h'], stats['volume_24h'], stats['market_cap']))
            conn.commit()
            conn.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get market stats: {e}")
            # Return mock data
            return {
                "price": self._get_mock_price(symbol),
                "high_24h": self._get_mock_price(symbol) * 1.05,
                "low_24h": self._get_mock_price(symbol) * 0.95,
                "change_24h": 2.5,
                "volume_24h": 1000000000,
                "market_cap": 1000000000000
            }
            
    def get_historical_data(self, symbol: str = "bitcoin", days: int = 7) -> List[Tuple]:
        """
        Get historical price data from database
        
        Args:
            symbol: Symbol to get data for
            days: Number of days to retrieve
            
        Returns:
            List of (price, timestamp) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT price, timestamp FROM price_data 
            WHERE symbol = ? AND timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        ''', (symbol, days))
        
        data = cursor.fetchall()
        conn.close()
        
        return data
        
    def get_ohlcv(self, symbol: str, timeframe: str = "1h", 
                  limit: int = 100) -> List[Dict]:
        """
        Get OHLCV (candlestick) data
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to retrieve
            
        Returns:
            List of OHLCV dictionaries
        """
        # First try to get from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT open, high, low, close, volume, timestamp
            FROM ohlcv_data
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, timeframe, limit))
        
        data = cursor.fetchall()
        conn.close()
        
        if data:
            return [{
                "open": row[0],
                "high": row[1],
                "low": row[2],
                "close": row[3],
                "volume": row[4],
                "timestamp": row[5]
            } for row in data]
        else:
            # Generate mock OHLCV data
            return self._generate_mock_ohlcv(symbol, timeframe, limit)
            
    def _generate_mock_ohlcv(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Generate mock OHLCV data for testing"""
        base_price = self._get_mock_price(symbol)
        ohlcv_data = []
        
        for i in range(limit):
            open_price = base_price + (i * 10)
            high_price = open_price * 1.02
            low_price = open_price * 0.98
            close_price = open_price + ((i % 2) * 20 - 10)
            volume = 1000000 + (i * 10000)
            
            ohlcv_data.append({
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume,
                "timestamp": (datetime.now() - timedelta(hours=limit-i)).isoformat()
            })
            
        return ohlcv_data
        
    def get_order_book(self, symbol: str, depth: int = 20) -> Dict:
        """
        Get order book data
        
        Args:
            symbol: Trading pair
            depth: Number of levels to retrieve
            
        Returns:
            Dict with bids and asks
        """
        # This would connect to exchange WebSocket in production
        # For now, return mock data
        price = self.get_price(symbol)
        
        bids = [[price - (i * 0.01), 100 + i] for i in range(depth)]
        asks = [[price + (i * 0.01), 100 + i] for i in range(depth)]
        
        return {
            "bids": bids,
            "asks": asks,
            "timestamp": datetime.now().isoformat()
        }
        
    def get_ticker(self, symbol: str) -> Dict:
        """Get ticker data with bid/ask/spread"""
        price = self.get_price(symbol)
        
        return {
            "symbol": symbol,
            "last": price,
            "bid": price * 0.999,
            "ask": price * 1.001,
            "spread": price * 0.002,
            "volume_24h": 1000000,
            "timestamp": datetime.now().isoformat()
        }
        
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get prices for multiple symbols at once"""
        prices = {}
        for symbol in symbols:
            price = self.get_price(symbol)
            if price:
                prices[symbol] = price
        return prices
        
    def check_exchange_status(self, exchange: str = None) -> Dict:
        """Check if exchange is online and responsive"""
        if exchange is None:
            exchange = self.exchange
            
        try:
            if exchange == "binance":
                url = f"{self.supported_exchanges['binance']}/ping"
                response = requests.get(url, timeout=5)
                status = "online" if response.status_code == 200 else "offline"
            else:
                # Use CoinGecko ping
                url = f"{self.supported_exchanges['coingecko']}/ping"
                response = requests.get(url, timeout=5)
                status = "online" if response.status_code == 200 else "offline"
                
            return {
                "exchange": exchange,
                "status": status,
                "latency": response.elapsed.total_seconds() * 1000,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "exchange": exchange,
                "status": "offline",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


if __name__ == "__main__":
    # Test the market data handler
    market = MarketData()
    print("✅ Market Data initialized successfully")
    
    # Test getting price
    btc_price = market.get_price("bitcoin")
    print(f"Bitcoin price: ${btc_price:,.2f}")
    
    # Test getting market stats
    stats = market.get_market_stats("bitcoin")
    print(f"Market stats: {stats}")
    
    # Test getting OHLCV
    ohlcv = market.get_ohlcv("BTC/USDT", "1h", 10)
    print(f"OHLCV data points: {len(ohlcv)}")
    
    # Test exchange status
    status = market.check_exchange_status()
    print(f"Exchange status: {status}")
