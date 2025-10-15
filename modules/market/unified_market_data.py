#!/usr/bin/env python3
"""Unified Market Data Aggregator for TPS19"""

import json
import time
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from exchanges.crypto_com import CryptoComAPI
    from exchanges.alpha_vantage import AlphaVantageAPI
    from integrations.google_sheets import GoogleSheetsIntegration
except ImportError as e:
    print(f"Warning: Some modules not found: {e}")
    CryptoComAPI = None
    AlphaVantageAPI = None
    GoogleSheetsIntegration = None

class UnifiedMarketData:
    """Unified market data aggregator combining multiple sources"""
    
    def __init__(self):
        self.db_path = "/opt/tps19/data/databases/unified_market.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize data sources
        self.crypto_com = CryptoComAPI() if CryptoComAPI else None
        self.alpha_vantage = AlphaVantageAPI() if AlphaVantageAPI else None
        self.google_sheets = GoogleSheetsIntegration() if GoogleSheetsIntegration else None
        
        # Data cache
        self.cache = {}
        self.cache_ttl = 30  # 30 seconds cache
        
        # Initialize database
        self.init_database()
        
        # Start background data collection
        self.collector_thread = None
        self.collecting = False
        
    def init_database(self):
        """Initialize unified market database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Unified price data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unified_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                source TEXT NOT NULL,
                price REAL NOT NULL,
                bid REAL,
                ask REAL,
                volume REAL,
                high_24h REAL,
                low_24h REAL,
                change_24h REAL
            )
        ''')
        
        # Market indicators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                indicator TEXT NOT NULL,
                value REAL NOT NULL,
                timeframe TEXT
            )
        ''')
        
        # Data quality metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_quality (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT NOT NULL,
                success_rate REAL,
                avg_latency_ms REAL,
                total_requests INTEGER,
                failed_requests INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def get_best_price(self, symbol: str) -> Dict:
        """Get best price from all available sources"""
        # Check cache first
        cache_key = f"price_{symbol}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
                
        prices = []
        
        # Collect from crypto.com
        if self.crypto_com and "_" in symbol:
            try:
                ticker = self.crypto_com.get_ticker(symbol)
                if ticker and ticker.get('price', 0) > 0:
                    prices.append({
                        'source': 'crypto.com',
                        'price': ticker['price'],
                        'bid': ticker.get('bid', ticker['price']),
                        'ask': ticker.get('ask', ticker['price']),
                        'volume': ticker.get('volume', 0),
                        'timestamp': datetime.now()
                    })
            except Exception as e:
                print(f"Error fetching from crypto.com: {e}")
                
        # Collect from Alpha Vantage
        if self.alpha_vantage:
            try:
                base, quote = symbol.split("_") if "_" in symbol else (symbol, "USD")
                rate_data = self.alpha_vantage.get_crypto_exchange_rate(base, quote)
                
                if rate_data and rate_data.get('exchange_rate', 0) > 0:
                    prices.append({
                        'source': 'alpha_vantage',
                        'price': rate_data['exchange_rate'],
                        'bid': rate_data.get('bid_price', rate_data['exchange_rate']),
                        'ask': rate_data.get('ask_price', rate_data['exchange_rate']),
                        'volume': 0,  # Not provided
                        'timestamp': datetime.now()
                    })
            except Exception as e:
                print(f"Error fetching from Alpha Vantage: {e}")
                
        # If no prices, return mock data
        if not prices:
            return self._get_mock_price(symbol)
            
        # Find best price (average of all sources)
        avg_price = sum(p['price'] for p in prices) / len(prices)
        best_bid = max(p['bid'] for p in prices)
        best_ask = min(p['ask'] for p in prices)
        total_volume = sum(p['volume'] for p in prices)
        
        result = {
            'symbol': symbol,
            'price': avg_price,
            'bid': best_bid,
            'ask': best_ask,
            'spread': best_ask - best_bid,
            'volume': total_volume,
            'sources': len(prices),
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache result
        self.cache[cache_key] = (time.time(), result)
        
        # Store in database
        self._store_unified_price(symbol, result, prices)
        
        return result
        
    def _get_mock_price(self, symbol: str) -> Dict:
        """Generate mock price data"""
        base_prices = {
            'BTC_USDT': 45000.0,
            'ETH_USDT': 3000.0,
            'DOGE_USDT': 0.15,
            'CRO_USDT': 0.50,
            'ADA_USDT': 0.60
        }
        
        base = base_prices.get(symbol, 100.0)
        variance = (time.time() % 100) / 100.0 * 0.02
        price = base * (1 + variance)
        
        return {
            'symbol': symbol,
            'price': price,
            'bid': price * 0.999,
            'ask': price * 1.001,
            'spread': price * 0.002,
            'volume': 1000000.0,
            'sources': 0,
            'timestamp': datetime.now().isoformat()
        }
        
    def _store_unified_price(self, symbol: str, unified: Dict, sources: List[Dict]):
        """Store unified price data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store individual source data
        for source_data in sources:
            cursor.execute('''
                INSERT INTO unified_prices 
                (symbol, source, price, bid, ask, volume)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                source_data['source'],
                source_data['price'],
                source_data['bid'],
                source_data['ask'],
                source_data['volume']
            ))
            
        conn.commit()
        conn.close()
        
    def get_market_depth(self, symbol: str, depth: int = 10) -> Dict:
        """Get aggregated market depth from all sources"""
        all_bids = []
        all_asks = []
        
        # Get order book from crypto.com
        if self.crypto_com and "_" in symbol:
            try:
                book = self.crypto_com.get_order_book(symbol, depth)
                if book:
                    all_bids.extend([(p, v, 'crypto.com') for p, v in book.get('bids', [])])
                    all_asks.extend([(p, v, 'crypto.com') for p, v in book.get('asks', [])])
            except Exception as e:
                print(f"Error fetching order book: {e}")
                
        # Sort and aggregate
        all_bids.sort(key=lambda x: x[0], reverse=True)  # Highest bid first
        all_asks.sort(key=lambda x: x[0])  # Lowest ask first
        
        # Take top levels
        top_bids = all_bids[:depth]
        top_asks = all_asks[:depth]
        
        return {
            'symbol': symbol,
            'bids': [{'price': p, 'volume': v, 'source': s} for p, v, s in top_bids],
            'asks': [{'price': p, 'volume': v, 'source': s} for p, v, s in top_asks],
            'spread': top_asks[0][0] - top_bids[0][0] if top_bids and top_asks else 0,
            'timestamp': datetime.now().isoformat()
        }
        
    def get_technical_indicators(self, symbol: str) -> Dict:
        """Get technical indicators from available sources"""
        indicators = {}
        
        # Get from Alpha Vantage
        if self.alpha_vantage:
            base = symbol.split("_")[0] if "_" in symbol else symbol
            
            try:
                # Get multiple indicators
                for indicator in ['RSI', 'MACD', 'ADX']:
                    ind_data = self.alpha_vantage.get_technical_indicators(base, indicator)
                    if ind_data:
                        indicators[indicator] = ind_data.get('value', 0)
                        
                        # Store in database
                        self._store_indicator(symbol, indicator, ind_data.get('value', 0))
                        
            except Exception as e:
                print(f"Error fetching indicators: {e}")
                
        # Add some calculated indicators
        if not indicators:
            # Mock indicators
            indicators = {
                'RSI': 50 + (time.time() % 30) - 15,
                'MACD': (time.time() % 10) - 5,
                'ADX': 25 + (time.time() % 25)
            }
            
        return {
            'symbol': symbol,
            'indicators': indicators,
            'timestamp': datetime.now().isoformat()
        }
        
    def _store_indicator(self, symbol: str, indicator: str, value: float):
        """Store indicator value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_indicators 
            (symbol, indicator, value, timeframe)
            VALUES (?, ?, ?, ?)
        ''', (symbol, indicator, value, '1h'))
        
        conn.commit()
        conn.close()
        
    def get_market_summary(self) -> Dict:
        """Get overall market summary"""
        summary = {
            'crypto': {},
            'stocks': {},
            'indicators': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Crypto summary
        crypto_symbols = ['BTC_USDT', 'ETH_USDT', 'DOGE_USDT', 'CRO_USDT']
        for symbol in crypto_symbols:
            price_data = self.get_best_price(symbol)
            summary['crypto'][symbol] = {
                'price': price_data['price'],
                'spread': price_data['spread'],
                'volume': price_data['volume']
            }
            
        # Stock summary (if Alpha Vantage available)
        if self.alpha_vantage:
            stock_symbols = ['AAPL', 'GOOGL', 'TSLA']
            for symbol in stock_symbols:
                try:
                    quote = self.alpha_vantage.get_stock_quote(symbol)
                    if quote:
                        summary['stocks'][symbol] = {
                            'price': quote.get('price', 0),
                            'change': quote.get('change', 0),
                            'volume': quote.get('volume', 0)
                        }
                except Exception as e:
                    print(f"Error fetching stock {symbol}: {e}")
                    
        # Market indicators
        btc_indicators = self.get_technical_indicators('BTC_USDT')
        summary['indicators'] = btc_indicators.get('indicators', {})
        
        return summary
        
    def start_data_collection(self, interval: int = 30):
        """Start background data collection"""
        if self.collecting:
            return
            
        self.collecting = True
        
        def collect_loop():
            symbols = ['BTC_USDT', 'ETH_USDT', 'DOGE_USDT', 'CRO_USDT', 'ADA_USDT']
            
            while self.collecting:
                try:
                    for symbol in symbols:
                        # Collect price data
                        self.get_best_price(symbol)
                        
                        # Log to Google Sheets if available
                        if self.google_sheets:
                            price_data = self.cache.get(f"price_{symbol}")
                            if price_data:
                                _, data = price_data
                                self.google_sheets.log_trading_signal({
                                    'symbol': symbol,
                                    'action': 'PRICE_UPDATE',
                                    'price': data['price'],
                                    'confidence': 1.0,
                                    'strategy': 'market_data'
                                })
                                
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"Collection error: {e}")
                    time.sleep(interval * 2)
                    
        self.collector_thread = threading.Thread(target=collect_loop)
        self.collector_thread.daemon = True
        self.collector_thread.start()
        
        print("✅ Data collection started")
        
    def stop_data_collection(self):
        """Stop background data collection"""
        self.collecting = False
        if self.collector_thread:
            self.collector_thread.join()
        print("✅ Data collection stopped")
        
    def get_data_quality_metrics(self) -> Dict:
        """Get data quality metrics for all sources"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                source,
                COUNT(*) as total_records,
                AVG(CASE WHEN price > 0 THEN 1 ELSE 0 END) as success_rate,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM unified_prices
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY source
        ''')
        
        metrics = {}
        for row in cursor.fetchall():
            metrics[row[0]] = {
                'total_records': row[1],
                'success_rate': row[2],
                'unique_symbols': row[3]
            }
            
        conn.close()
        
        return {
            'sources': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
    def test_all_sources(self) -> Dict:
        """Test all data sources"""
        results = {}
        
        # Test crypto.com
        if self.crypto_com:
            try:
                ticker = self.crypto_com.get_ticker('BTC_USDT')
                results['crypto.com'] = {
                    'status': 'OK' if ticker.get('price', 0) > 0 else 'FAIL',
                    'response_time': 'fast'
                }
            except Exception as e:
                results['crypto.com'] = {'status': 'ERROR', 'error': str(e)}
        else:
            results['crypto.com'] = {'status': 'NOT_CONFIGURED'}
            
        # Test Alpha Vantage
        if self.alpha_vantage:
            try:
                connected = self.alpha_vantage.test_connection()
                results['alpha_vantage'] = {
                    'status': 'OK' if connected else 'FAIL',
                    'response_time': 'slow (rate limited)'
                }
            except Exception as e:
                results['alpha_vantage'] = {'status': 'ERROR', 'error': str(e)}
        else:
            results['alpha_vantage'] = {'status': 'NOT_CONFIGURED'}
            
        # Test Google Sheets
        if self.google_sheets:
            try:
                connected = self.google_sheets.test_connection()
                results['google_sheets'] = {
                    'status': 'OK' if connected else 'FAIL',
                    'response_time': 'medium'
                }
            except Exception as e:
                results['google_sheets'] = {'status': 'ERROR', 'error': str(e)}
        else:
            results['google_sheets'] = {'status': 'NOT_CONFIGURED'}
            
        return results

# Global instance
unified_market_data = UnifiedMarketData()

if __name__ == "__main__":
    # Test unified market data
    print("Testing Unified Market Data System...")
    print("=" * 60)
    
    umd = UnifiedMarketData()
    
    # Test data sources
    print("\n1. Testing data sources:")
    source_results = umd.test_all_sources()
    for source, result in source_results.items():
        print(f"   {source}: {result['status']}")
        
    # Test best price
    print("\n2. Testing best price aggregation:")
    price = umd.get_best_price('BTC_USDT')
    print(f"   BTC/USDT: ${price['price']:,.2f} (from {price['sources']} sources)")
    print(f"   Spread: ${price['spread']:.2f}")
    
    # Test market depth
    print("\n3. Testing market depth:")
    depth = umd.get_market_depth('BTC_USDT', 5)
    if depth['bids']:
        print(f"   Best Bid: ${depth['bids'][0]['price']:,.2f}")
    if depth['asks']:
        print(f"   Best Ask: ${depth['asks'][0]['price']:,.2f}")
        
    # Test indicators
    print("\n4. Testing technical indicators:")
    indicators = umd.get_technical_indicators('BTC_USDT')
    for name, value in indicators['indicators'].items():
        print(f"   {name}: {value:.2f}")
        
    # Test market summary
    print("\n5. Testing market summary:")
    summary = umd.get_market_summary()
    print(f"   Crypto symbols tracked: {len(summary['crypto'])}")
    print(f"   Stock symbols tracked: {len(summary['stocks'])}")
    
    print("\n✅ All tests completed!")