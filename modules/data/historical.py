#!/usr/bin/env python3
"""
Historical Data Manager - Multi-source with caching
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List
import pickle
import hashlib

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class HistoricalDataManager:
    """
    Multi-source historical data with intelligent caching
    """
    
    def __init__(self):
        self.cache_dir = 'data/historical'
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Data sources in priority order
        self.sources = ['binance', 'coinbase', 'kraken']
        self.exchanges = {}
        
        if HAS_CCXT:
            self._init_exchanges()
        
    def _init_exchanges(self):
        """Initialize CCXT exchanges"""
        try:
            self.exchanges['binance'] = ccxt.binance({'enableRateLimit': True})
            self.exchanges['coinbase'] = ccxt.coinbase({'enableRateLimit': True})
            self.exchanges['kraken'] = ccxt.kraken({'enableRateLimit': True})
            logger.info("Initialized CCXT exchanges for data")
        except Exception as e:
            logger.error(f"Exchange init error: {e}")
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '5m',
                    start: Optional[datetime] = None,
                    end: Optional[datetime] = None,
                    use_cache: bool = True) -> pd.DataFrame:
        """
        Fetch OHLCV data with fallback sources and caching
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle interval ('1m', '5m', '1h', '1d')
            start: Start datetime
            end: End datetime
            use_cache: Whether to use cached data
            
        Returns:
            DataFrame with OHLCV data
        """
        # Default to last 30 days
        if end is None:
            end = datetime.now()
        if start is None:
            start = end - timedelta(days=30)
        
        # Check cache first
        if use_cache:
            cached = self._load_from_cache(symbol, timeframe, start, end)
            if cached is not None and len(cached) > 0:
                logger.info(f"Loaded {len(cached)} candles from cache")
                return cached
        
        # Fetch from sources
        if not HAS_CCXT:
            logger.warning("CCXT not installed, generating synthetic data")
            return self._generate_synthetic_data(symbol, timeframe, start, end)
        
        for source in self.sources:
            try:
                logger.info(f"Fetching from {source}...")
                data = self._fetch_from_source(source, symbol, timeframe, start, end)
                
                if data is not None and len(data) > 0:
                    # Clean and validate
                    data = self.ensure_data_quality(data)
                    
                    # Cache for future use
                    self._save_to_cache(data, symbol, timeframe)
                    
                    logger.info(f"Fetched {len(data)} candles from {source}")
                    return data
                    
            except Exception as e:
                logger.warning(f"{source} failed: {e}, trying next source...")
        
        # All sources failed, generate synthetic
        logger.warning("All sources failed, generating synthetic data")
        return self._generate_synthetic_data(symbol, timeframe, start, end)
    
    def _fetch_from_source(self, source: str, symbol: str, timeframe: str,
                          start: datetime, end: datetime) -> pd.DataFrame:
        """Fetch from specific exchange"""
        if source not in self.exchanges:
            raise Exception(f"Exchange {source} not available")
        
        exchange = self.exchanges[source]
        
        # Convert to milliseconds
        since = int(start.timestamp() * 1000)
        
        all_candles = []
        while since < int(end.timestamp() * 1000):
            candles = exchange.fetch_ohlcv(symbol, timeframe, since, limit=1000)
            
            if not candles:
                break
            
            all_candles.extend(candles)
            since = candles[-1][0] + 1
        
        # Convert to DataFrame
        df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def _generate_synthetic_data(self, symbol: str, timeframe: str,
                                 start: datetime, end: datetime) -> pd.DataFrame:
        """Generate realistic synthetic data for testing"""
        # Determine number of candles
        timeframe_minutes = self._timeframe_to_minutes(timeframe)
        total_minutes = int((end - start).total_seconds() / 60)
        num_candles = total_minutes // timeframe_minutes
        
        # Generate timestamps
        timestamps = pd.date_range(start=start, end=end, periods=num_candles)
        
        # Base price
        base_price = 50000 if 'BTC' in symbol else 3000 if 'ETH' in symbol else 100
        
        # Generate realistic price movement
        returns = np.random.normal(0.0001, 0.015, num_candles)  # Mean return + volatility
        trend = np.linspace(0, 0.1, num_candles)  # Slight uptrend
        prices = base_price * np.exp(np.cumsum(returns + trend/num_candles))
        
        # Generate OHLCV
        data = []
        for i, (ts, close) in enumerate(zip(timestamps, prices)):
            # Realistic high/low based on volatility
            volatility = abs(returns[i])
            high = close * (1 + volatility * np.random.uniform(0.5, 2))
            low = close * (1 - volatility * np.random.uniform(0.5, 2))
            open_price = close * np.random.uniform(0.998, 1.002)
            volume = np.random.uniform(800, 1200)
            
            data.append({
                'timestamp': ts,
                'open': open_price,
                'high': max(open_price, close, high),
                'low': min(open_price, close, low),
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def ensure_data_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate data quality
        """
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        # Sort by timestamp
        df = df.sort_index()
        
        # Fill small gaps
        df = self._fill_gaps(df)
        
        # Remove outliers
        df = self._remove_outliers(df)
        
        # Validate data integrity
        self._validate_data(df)
        
        return df
    
    def _fill_gaps(self, df: pd.DataFrame, max_gap: int = 5) -> pd.DataFrame:
        """Fill small gaps in data"""
        # Forward fill for small gaps only
        return df.fillna(method='ffill', limit=max_gap)
    
    def _remove_outliers(self, df: pd.DataFrame, z_threshold: float = 5.0) -> pd.DataFrame:
        """Remove obvious outliers"""
        # Calculate z-scores for returns
        returns = df['close'].pct_change()
        z_scores = np.abs((returns - returns.mean()) / returns.std())
        
        # Remove extreme outliers
        mask = z_scores < z_threshold
        return df[mask]
    
    def _validate_data(self, df: pd.DataFrame):
        """Validate data integrity"""
        # Check for required columns
        required = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required):
            raise ValueError(f"Missing required columns. Need: {required}")
        
        # Check for negative values
        if (df[required] < 0).any().any():
            raise ValueError("Negative values found in OHLCV data")
        
        # Check high/low logic
        if ((df['high'] < df['low']) | 
            (df['high'] < df['close']) | 
            (df['high'] < df['open']) |
            (df['low'] > df['close']) | 
            (df['low'] > df['open'])).any():
            raise ValueError("Invalid OHLC relationships")
    
    def _load_from_cache(self, symbol: str, timeframe: str,
                        start: datetime, end: datetime) -> Optional[pd.DataFrame]:
        """Load from cache if available"""
        cache_key = self._get_cache_key(symbol, timeframe, start, end)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        if os.path.exists(cache_file):
            # Check if cache is recent (< 1 day old for recent data)
            cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
            if cache_age < timedelta(days=1):
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except Exception as e:
                    logger.warning(f"Cache load error: {e}")
        
        return None
    
    def _save_to_cache(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """Save to cache"""
        if len(df) == 0:
            return
        
        start = df.index[0].to_pydatetime()
        end = df.index[-1].to_pydatetime()
        
        cache_key = self._get_cache_key(symbol, timeframe, start, end)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)
        except Exception as e:
            logger.warning(f"Cache save error: {e}")
    
    def _get_cache_key(self, symbol: str, timeframe: str, 
                      start: datetime, end: datetime) -> str:
        """Generate cache key"""
        key_str = f"{symbol}_{timeframe}_{start.date()}_{end.date()}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        mapping = {'1m': 1, '5m': 5, '15m': 15, '1h': 60, '4h': 240, '1d': 1440}
        return mapping.get(timeframe, 5)


# Global instance
historical_data_manager = HistoricalDataManager()
