#!/usr/bin/env python3
"""Redis Integration for TPS19 - High-Performance Real-Time Data Storage"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available. Install with: pip install redis")


class RedisIntegration:
    """Redis integration for real-time data storage and pub/sub"""
    
    def __init__(self, host='localhost', port=6379, db=0, password=None, use_ssl: bool = False):
        """Initialize Redis connection
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.use_ssl = use_ssl
        
        self.client = None
        self.pubsub = None
        self.connected = False
        
        if REDIS_AVAILABLE:
            self._connect()
        
    def _connect(self):
        """Connect to Redis server"""
        try:
            # Support TLS via rediss scheme/env handled by caller; enforce timeouts
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                ssl=self.use_ssl
            )
            
            # Test connection
            self.client.ping()
            self.connected = True
            print(f"✅ Connected to Redis at {self.host}:{self.port}")
            
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            self.connected = False
            
    def set_market_data(self, symbol: str, data: Dict, expiry: int = 3600):
        """Store market data with expiry
        
        Args:
            symbol: Trading pair symbol
            data: Market data dictionary
            expiry: Expiry time in seconds (default: 1 hour)
        """
        if not self.connected:
            return False
            
        try:
            key = f"market:{symbol}"
            value = json.dumps(data)
            self.client.setex(key, expiry, value)
            return True
        except Exception as e:
            print(f"❌ Error setting market data: {e}")
            return False
            
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get market data for symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Market data dictionary or None
        """
        if not self.connected:
            return None
            
        try:
            key = f"market:{symbol}"
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"❌ Error getting market data: {e}")
            return None
            
    def set_price(self, symbol: str, price: float):
        """Set current price for symbol
        
        Args:
            symbol: Trading pair symbol
            price: Current price
        """
        if not self.connected:
            return False
            
        try:
            # Store price with timestamp
            key = f"price:{symbol}"
            data = {
                'price': price,
                'timestamp': time.time()
            }
            self.client.setex(key, 60, json.dumps(data))  # 1 min expiry
            
            # Add to price history (sorted set)
            history_key = f"price_history:{symbol}"
            self.client.zadd(history_key, {str(price): time.time()})
            
            # Keep only last 1000 prices
            self.client.zremrangebyrank(history_key, 0, -1001)
            
            return True
        except Exception as e:
            print(f"❌ Error setting price: {e}")
            return False
            
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Current price or None
        """
        if not self.connected:
            return None
            
        try:
            key = f"price:{symbol}"
            value = self.client.get(key)
            if value:
                data = json.loads(value)
                return float(data['price'])
            return None
        except Exception as e:
            print(f"❌ Error getting price: {e}")
            return None
            
    def get_price_history(self, symbol: str, limit: int = 100) -> List[float]:
        """Get price history for symbol
        
        Args:
            symbol: Trading pair symbol
            limit: Number of recent prices
            
        Returns:
            List of recent prices
        """
        if not self.connected:
            return []
            
        try:
            key = f"price_history:{symbol}"
            prices = self.client.zrange(key, -limit, -1)
            return [float(p) for p in prices]
        except Exception as e:
            print(f"❌ Error getting price history: {e}")
            return []
            
    def set_order(self, order_id: str, order_data: Dict, expiry: int = 86400):
        """Store order data
        
        Args:
            order_id: Order ID
            order_data: Order details
            expiry: Expiry time in seconds (default: 24 hours)
        """
        if not self.connected:
            return False
            
        try:
            key = f"order:{order_id}"
            value = json.dumps(order_data)
            self.client.setex(key, expiry, value)
            
            # Add to active orders set
            self.client.sadd("active_orders", order_id)
            
            return True
        except Exception as e:
            print(f"❌ Error setting order: {e}")
            return False
            
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order data
        
        Args:
            order_id: Order ID
            
        Returns:
            Order data dictionary or None
        """
        if not self.connected:
            return None
            
        try:
            key = f"order:{order_id}"
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"❌ Error getting order: {e}")
            return None
            
    def get_active_orders(self) -> List[str]:
        """Get list of active order IDs
        
        Returns:
            List of order IDs
        """
        if not self.connected:
            return []
            
        try:
            return list(self.client.smembers("active_orders"))
        except Exception as e:
            print(f"❌ Error getting active orders: {e}")
            return []
            
    def remove_order(self, order_id: str):
        """Remove order from active orders
        
        Args:
            order_id: Order ID
        """
        if not self.connected:
            return False
            
        try:
            self.client.srem("active_orders", order_id)
            key = f"order:{order_id}"
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"❌ Error removing order: {e}")
            return False
            
    def set_strategy_signal(self, strategy: str, symbol: str, signal: Dict):
        """Store strategy signal
        
        Args:
            strategy: Strategy name
            symbol: Trading pair symbol
            signal: Signal data
        """
        if not self.connected:
            return False
            
        try:
            key = f"signal:{strategy}:{symbol}"
            value = json.dumps({
                **signal,
                'timestamp': time.time()
            })
            self.client.setex(key, 300, value)  # 5 min expiry
            return True
        except Exception as e:
            print(f"❌ Error setting signal: {e}")
            return False
            
    def get_strategy_signals(self, strategy: str) -> Dict[str, Dict]:
        """Get all signals for a strategy
        
        Args:
            strategy: Strategy name
            
        Returns:
            Dictionary of symbol -> signal data
        """
        if not self.connected:
            return {}
            
        try:
            pattern = f"signal:{strategy}:*"
            signals = {}
            
            for key in self.client.scan_iter(match=pattern):
                value = self.client.get(key)
                if value:
                    symbol = key.split(':')[2]
                    signals[symbol] = json.loads(value)
                    
            return signals
        except Exception as e:
            print(f"❌ Error getting signals: {e}")
            return {}
            
    def publish_event(self, channel: str, message: Dict):
        """Publish event to channel
        
        Args:
            channel: Channel name
            message: Message data
        """
        if not self.connected:
            return False
            
        try:
            payload = json.dumps(message)
            self.client.publish(channel, payload)
            return True
        except Exception as e:
            print(f"❌ Error publishing event: {e}")
            return False
            
    def subscribe(self, channels: List[str], callback):
        """Subscribe to channels
        
        Args:
            channels: List of channel names
            callback: Callback function for messages
        """
        if not self.connected:
            return False
            
        try:
            self.pubsub = self.client.pubsub()
            self.pubsub.subscribe(**{ch: callback for ch in channels})
            
            # Start listening thread
            thread = self.pubsub.run_in_thread(sleep_time=0.01)
            return thread
        except Exception as e:
            print(f"❌ Error subscribing: {e}")
            return False
            
    def cache_set(self, key: str, value: Any, expiry: int = 3600):
        """Set cache value
        
        Args:
            key: Cache key
            value: Value to cache
            expiry: Expiry time in seconds
        """
        if not self.connected:
            return False
            
        try:
            if not isinstance(value, str):
                value = json.dumps(value)
            self.client.setex(f"cache:{key}", expiry, value)
            return True
        except Exception as e:
            print(f"❌ Error setting cache: {e}")
            return False
            
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.connected:
            return None
            
        try:
            value = self.client.get(f"cache:{key}")
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            print(f"❌ Error getting cache: {e}")
            return None
            
    def increment_counter(self, key: str, amount: int = 1) -> int:
        """Increment counter
        
        Args:
            key: Counter key
            amount: Amount to increment
            
        Returns:
            New counter value
        """
        if not self.connected:
            return 0
            
        try:
            return self.client.incrby(f"counter:{key}", amount)
        except Exception as e:
            print(f"❌ Error incrementing counter: {e}")
            return 0
            
    def get_counter(self, key: str) -> int:
        """Get counter value
        
        Args:
            key: Counter key
            
        Returns:
            Counter value
        """
        if not self.connected:
            return 0
            
        try:
            value = self.client.get(f"counter:{key}")
            return int(value) if value else 0
        except Exception as e:
            print(f"❌ Error getting counter: {e}")
            return 0
            
    def flush_database(self):
        """Flush entire database (use with caution!)"""
        if not self.connected:
            return False
            
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            print(f"❌ Error flushing database: {e}")
            return False
            
    def get_stats(self) -> Dict:
        """Get Redis statistics
        
        Returns:
            Dictionary of stats
        """
        if not self.connected:
            return {'connected': False}
            
        try:
            info = self.client.info()
            return {
                'connected': True,
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {'connected': False}
            
    def close(self):
        """Close Redis connection"""
        if self.pubsub:
            self.pubsub.close()
        if self.client:
            self.client.close()
        self.connected = False


# Test functionality
def test_redis():
    """Test Redis integration"""
    print("🧪 Testing Redis Integration...")
    
    redis_client = RedisIntegration()
    
    if not redis_client.connected:
        print("⚠️ Redis not available, skipping tests")
        return
        
    # Test market data
    redis_client.set_market_data('BTC/USDT', {
        'price': 26500.0,
        'volume': 1500,
        'timestamp': time.time()
    })
    
    data = redis_client.get_market_data('BTC/USDT')
    print(f"✅ Market data: {data}")
    
    # Test price
    redis_client.set_price('BTC/USDT', 26500.0)
    price = redis_client.get_price('BTC/USDT')
    print(f"✅ Price: {price}")
    
    # Test cache
    redis_client.cache_set('test_key', {'test': 'value'})
    cached = redis_client.cache_get('test_key')
    print(f"✅ Cached value: {cached}")
    
    # Test counter
    count = redis_client.increment_counter('trades_today')
    print(f"✅ Counter: {count}")
    
    # Get stats
    stats = redis_client.get_stats()
    print(f"✅ Stats: {stats}")
    
    redis_client.close()


if __name__ == '__main__':
    test_redis()
