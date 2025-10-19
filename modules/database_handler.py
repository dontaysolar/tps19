#!/usr/bin/env python3
"""
Redis Database Handler for APEX Trading System
High-performance data storage and caching
"""

import os
import sys
import json
import time
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import threading
from collections import defaultdict

try:
    import redis
    from redis.exceptions import ConnectionError, TimeoutError
except ImportError:
    print("Installing Redis...")
    os.system("pip3 install --break-system-packages redis -q")
    import redis
    from redis.exceptions import ConnectionError, TimeoutError

class RedisDatabaseHandler:
    """
    High-performance Redis database handler
    Features:
    - Real-time data caching
    - Trade history storage
    - Performance metrics
    - Market data streaming
    - Bot state management
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        
        # Connection pool for better performance
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=20,
            retry_on_timeout=True
        )
        
        self.redis_client = None
        self.connected = False
        self.lock = threading.Lock()
        
        # Key prefixes for organization
        self.prefixes = {
            'market_data': 'market:',
            'trades': 'trades:',
            'positions': 'positions:',
            'bot_states': 'bots:',
            'metrics': 'metrics:',
            'alerts': 'alerts:',
            'cache': 'cache:',
            'config': 'config:'
        }
        
        # TTL settings (in seconds)
        self.ttl_settings = {
            'market_data': 3600,      # 1 hour
            'trades': 86400 * 30,     # 30 days
            'positions': 86400 * 7,   # 7 days
            'bot_states': 3600,       # 1 hour
            'metrics': 86400 * 7,     # 7 days
            'alerts': 86400 * 3,      # 3 days
            'cache': 300              # 5 minutes
        }
        
        self._connect()
    
    def _connect(self) -> bool:
        """Establish Redis connection"""
        try:
            self.redis_client = redis.Redis(connection_pool=self.pool)
            # Test connection
            self.redis_client.ping()
            self.connected = True
            print("✅ Redis connected successfully")
            return True
        except (ConnectionError, TimeoutError) as e:
            print(f"❌ Redis connection failed: {e}")
            self.connected = False
            return False
    
    def _get_key(self, prefix: str, identifier: str) -> str:
        """Generate Redis key with prefix"""
        return f"{self.prefixes[prefix]}{identifier}"
    
    def _set_ttl(self, key: str, prefix: str) -> None:
        """Set TTL for key based on prefix"""
        if prefix in self.ttl_settings:
            self.redis_client.expire(key, self.ttl_settings[prefix])
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.connected:
            return self._connect()
        return True
    
    def store_market_data(self, symbol: str, data: Dict) -> bool:
        """Store market data for symbol"""
        if not self.is_connected():
            return False
        
        try:
            key = self._get_key('market_data', symbol)
            
            # Add timestamp
            data['timestamp'] = datetime.now().isoformat()
            
            # Store as JSON
            self.redis_client.hset(key, mapping=data)
            self._set_ttl(key, 'market_data')
            
            return True
        except Exception as e:
            print(f"❌ Error storing market data: {e}")
            return False
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get market data for symbol"""
        if not self.is_connected():
            return None
        
        try:
            key = self._get_key('market_data', symbol)
            data = self.redis_client.hgetall(key)
            
            if not data:
                return None
            
            # Convert bytes to strings and parse JSON
            result = {}
            for k, v in data.items():
                try:
                    result[k.decode()] = json.loads(v.decode())
                except (json.JSONDecodeError, AttributeError):
                    result[k.decode()] = v.decode()
            
            return result
        except Exception as e:
            print(f"❌ Error getting market data: {e}")
            return None
    
    def store_trade(self, trade_id: str, trade_data: Dict) -> bool:
        """Store trade data"""
        if not self.is_connected():
            return False
        
        try:
            key = self._get_key('trades', trade_id)
            
            # Add timestamp
            trade_data['timestamp'] = datetime.now().isoformat()
            trade_data['trade_id'] = trade_id
            
            # Store as JSON
            self.redis_client.hset(key, mapping=trade_data)
            self._set_ttl(key, 'trades')
            
            # Add to trades list
            trades_list_key = self._get_key('trades', 'list')
            self.redis_client.lpush(trades_list_key, trade_id)
            self._set_ttl(trades_list_key, 'trades')
            
            return True
        except Exception as e:
            print(f"❌ Error storing trade: {e}")
            return False
    
    def get_trade(self, trade_id: str) -> Optional[Dict]:
        """Get trade data by ID"""
        if not self.is_connected():
            return None
        
        try:
            key = self._get_key('trades', trade_id)
            data = self.redis_client.hgetall(key)
            
            if not data:
                return None
            
            result = {}
            for k, v in data.items():
                try:
                    result[k.decode()] = json.loads(v.decode())
                except (json.JSONDecodeError, AttributeError):
                    result[k.decode()] = v.decode()
            
            return result
        except Exception as e:
            print(f"❌ Error getting trade: {e}")
            return None
    
    def get_recent_trades(self, limit: int = 100) -> List[Dict]:
        """Get recent trades"""
        if not self.is_connected():
            return []
        
        try:
            trades_list_key = self._get_key('trades', 'list')
            trade_ids = self.redis_client.lrange(trades_list_key, 0, limit - 1)
            
            trades = []
            for trade_id in trade_ids:
                trade = self.get_trade(trade_id.decode())
                if trade:
                    trades.append(trade)
            
            return trades
        except Exception as e:
            print(f"❌ Error getting recent trades: {e}")
            return []
    
    def store_position(self, position_id: str, position_data: Dict) -> bool:
        """Store position data"""
        if not self.is_connected():
            return False
        
        try:
            key = self._get_key('positions', position_id)
            
            # Add timestamp
            position_data['timestamp'] = datetime.now().isoformat()
            position_data['position_id'] = position_id
            
            # Store as JSON
            self.redis_client.hset(key, mapping=position_data)
            self._set_ttl(key, 'positions')
            
            return True
        except Exception as e:
            print(f"❌ Error storing position: {e}")
            return False
    
    def get_position(self, position_id: str) -> Optional[Dict]:
        """Get position data by ID"""
        if not self.is_connected():
            return None
        
        try:
            key = self._get_key('positions', position_id)
            data = self.redis_client.hgetall(key)
            
            if not data:
                return None
            
            result = {}
            for k, v in data.items():
                try:
                    result[k.decode()] = json.loads(v.decode())
                except (json.JSONDecodeError, AttributeError):
                    result[k.decode()] = v.decode()
            
            return result
        except Exception as e:
            print(f"❌ Error getting position: {e}")
            return None
    
    def get_all_positions(self) -> List[Dict]:
        """Get all active positions"""
        if not self.is_connected():
            return []
        
        try:
            pattern = self._get_key('positions', '*')
            keys = self.redis_client.keys(pattern)
            
            positions = []
            for key in keys:
                position_id = key.decode().split(':')[-1]
                position = self.get_position(position_id)
                if position:
                    positions.append(position)
            
            return positions
        except Exception as e:
            print(f"❌ Error getting all positions: {e}")
            return []
    
    def store_bot_state(self, bot_name: str, state_data: Dict) -> bool:
        """Store bot state"""
        if not self.is_connected():
            return False
        
        try:
            key = self._get_key('bot_states', bot_name)
            
            # Add timestamp
            state_data['timestamp'] = datetime.now().isoformat()
            state_data['bot_name'] = bot_name
            
            # Store as JSON
            self.redis_client.hset(key, mapping=state_data)
            self._set_ttl(key, 'bot_states')
            
            return True
        except Exception as e:
            print(f"❌ Error storing bot state: {e}")
            return False
    
    def get_bot_state(self, bot_name: str) -> Optional[Dict]:
        """Get bot state"""
        if not self.is_connected():
            return None
        
        try:
            key = self._get_key('bot_states', bot_name)
            data = self.redis_client.hgetall(key)
            
            if not data:
                return None
            
            result = {}
            for k, v in data.items():
                try:
                    result[k.decode()] = json.loads(v.decode())
                except (json.JSONDecodeError, AttributeError):
                    result[k.decode()] = v.decode()
            
            return result
        except Exception as e:
            print(f"❌ Error getting bot state: {e}")
            return None
    
    def store_metrics(self, metric_name: str, value: Union[float, int, str], tags: Dict = None) -> bool:
        """Store performance metrics"""
        if not self.is_connected():
            return False
        
        try:
            key = self._get_key('metrics', metric_name)
            
            metric_data = {
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'tags': json.dumps(tags or {})
            }
            
            # Store as JSON
            self.redis_client.hset(key, mapping=metric_data)
            self._set_ttl(key, 'metrics')
            
            return True
        except Exception as e:
            print(f"❌ Error storing metrics: {e}")
            return False
    
    def get_metrics(self, metric_name: str) -> Optional[Dict]:
        """Get performance metrics"""
        if not self.is_connected():
            return None
        
        try:
            key = self._get_key('metrics', metric_name)
            data = self.redis_client.hgetall(key)
            
            if not data:
                return None
            
            result = {}
            for k, v in data.items():
                try:
                    result[k.decode()] = json.loads(v.decode())
                except (json.JSONDecodeError, AttributeError):
                    result[k.decode()] = v.decode()
            
            return result
        except Exception as e:
            print(f"❌ Error getting metrics: {e}")
            return None
    
    def cache_data(self, cache_key: str, data: Any, ttl: int = None) -> bool:
        """Cache data with TTL"""
        if not self.is_connected():
            return False
        
        try:
            key = self._get_key('cache', cache_key)
            
            # Serialize data
            if isinstance(data, (dict, list)):
                serialized_data = json.dumps(data)
            else:
                serialized_data = str(data)
            
            # Store with TTL
            ttl = ttl or self.ttl_settings['cache']
            self.redis_client.setex(key, ttl, serialized_data)
            
            return True
        except Exception as e:
            print(f"❌ Error caching data: {e}")
            return False
    
    def get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get cached data"""
        if not self.is_connected():
            return None
        
        try:
            key = self._get_key('cache', cache_key)
            data = self.redis_client.get(key)
            
            if not data:
                return None
            
            # Try to deserialize as JSON
            try:
                return json.loads(data.decode())
            except (json.JSONDecodeError, AttributeError):
                return data.decode()
        except Exception as e:
            print(f"❌ Error getting cached data: {e}")
            return None
    
    def store_alert(self, alert_type: str, message: str, severity: str = 'info', data: Dict = None) -> bool:
        """Store alert"""
        if not self.is_connected():
            return False
        
        try:
            alert_id = f"{alert_type}_{int(time.time())}"
            key = self._get_key('alerts', alert_id)
            
            alert_data = {
                'alert_type': alert_type,
                'message': message,
                'severity': severity,
                'data': json.dumps(data or {}),
                'timestamp': datetime.now().isoformat()
            }
            
            # Store as JSON
            self.redis_client.hset(key, mapping=alert_data)
            self._set_ttl(key, 'alerts')
            
            return True
        except Exception as e:
            print(f"❌ Error storing alert: {e}")
            return False
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent alerts"""
        if not self.is_connected():
            return []
        
        try:
            pattern = self._get_key('alerts', '*')
            keys = self.redis_client.keys(pattern)
            
            # Sort by timestamp (newest first)
            alerts = []
            for key in keys:
                data = self.redis_client.hgetall(key)
                if data:
                    alert = {}
                    for k, v in data.items():
                        try:
                            alert[k.decode()] = json.loads(v.decode())
                        except (json.JSONDecodeError, AttributeError):
                            alert[k.decode()] = v.decode()
                    alerts.append(alert)
            
            # Sort by timestamp
            alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return alerts[:limit]
        except Exception as e:
            print(f"❌ Error getting recent alerts: {e}")
            return []
    
    def get_system_stats(self) -> Dict:
        """Get Redis system statistics"""
        if not self.is_connected():
            return {}
        
        try:
            info = self.redis_client.info()
            
            stats = {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0),
                'redis_version': info.get('redis_version', 'Unknown')
            }
            
            return stats
        except Exception as e:
            print(f"❌ Error getting system stats: {e}")
            return {}
    
    def cleanup_expired_data(self) -> int:
        """Clean up expired data (Redis handles this automatically, but we can force it)"""
        if not self.is_connected():
            return 0
        
        try:
            # Force Redis to clean up expired keys
            return self.redis_client.execute_command('MEMORY', 'PURGE')
        except Exception as e:
            print(f"❌ Error cleaning up data: {e}")
            return 0
    
    def backup_data(self, backup_file: str) -> bool:
        """Backup Redis data to file"""
        if not self.is_connected():
            return False
        
        try:
            # Get all keys
            all_keys = self.redis_client.keys('*')
            
            backup_data = {}
            for key in all_keys:
                key_str = key.decode()
                data_type = self.redis_client.type(key)
                
                if data_type == b'hash':
                    backup_data[key_str] = self.redis_client.hgetall(key)
                elif data_type == b'string':
                    backup_data[key_str] = self.redis_client.get(key)
                elif data_type == b'list':
                    backup_data[key_str] = self.redis_client.lrange(key, 0, -1)
                elif data_type == b'set':
                    backup_data[key_str] = self.redis_client.smembers(key)
            
            # Save to file
            with open(backup_file, 'wb') as f:
                pickle.dump(backup_data, f)
            
            return True
        except Exception as e:
            print(f"❌ Error backing up data: {e}")
            return False
    
    def close(self):
        """Close Redis connection"""
        if self.redis_client:
            self.redis_client.close()
            self.connected = False


class DatabaseManager:
    """
    High-level database manager
    Coordinates multiple database operations
    """
    
    def __init__(self):
        self.redis_handler = RedisDatabaseHandler()
        self.cache_stats = defaultdict(int)
    
    def store_trade_complete(self, trade_data: Dict) -> bool:
        """Store complete trade with all related data"""
        try:
            # Store trade
            trade_id = trade_data.get('trade_id', f"trade_{int(time.time())}")
            self.redis_handler.store_trade(trade_id, trade_data)
            
            # Store position if applicable
            if 'position_id' in trade_data:
                position_data = {
                    'symbol': trade_data.get('symbol'),
                    'side': trade_data.get('side'),
                    'amount': trade_data.get('amount'),
                    'price': trade_data.get('price'),
                    'status': 'open' if trade_data.get('side') == 'buy' else 'closed'
                }
                self.redis_handler.store_position(trade_data['position_id'], position_data)
            
            # Store metrics
            self.redis_handler.store_metrics('total_trades', 1)
            self.redis_handler.store_metrics('trade_volume', trade_data.get('amount', 0))
            
            return True
        except Exception as e:
            print(f"❌ Error storing complete trade: {e}")
            return False
    
    def get_trading_summary(self) -> Dict:
        """Get comprehensive trading summary"""
        try:
            recent_trades = self.redis_handler.get_recent_trades(100)
            positions = self.redis_handler.get_all_positions()
            
            # Calculate summary
            total_trades = len(recent_trades)
            open_positions = len([p for p in positions if p.get('status') == 'open'])
            
            total_volume = sum(float(t.get('amount', 0)) for t in recent_trades)
            total_profit = sum(float(t.get('profit', 0)) for t in recent_trades)
            
            return {
                'total_trades': total_trades,
                'open_positions': open_positions,
                'total_volume': total_volume,
                'total_profit': total_profit,
                'recent_trades': recent_trades[:10],  # Last 10 trades
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error getting trading summary: {e}")
            return {}
    
    def get_bot_performance(self) -> Dict:
        """Get bot performance metrics"""
        try:
            # Get all bot states
            pattern = self.redis_handler._get_key('bot_states', '*')
            bot_keys = self.redis_handler.redis_client.keys(pattern)
            
            bot_performance = {}
            for key in bot_keys:
                bot_name = key.decode().split(':')[-1]
                state = self.redis_handler.get_bot_state(bot_name)
                if state:
                    bot_performance[bot_name] = {
                        'last_update': state.get('timestamp'),
                        'status': state.get('status', 'unknown'),
                        'metrics': state.get('metrics', {})
                    }
            
            return bot_performance
        except Exception as e:
            print(f"❌ Error getting bot performance: {e}")
            return {}


if __name__ == '__main__':
    print("🗄️ Redis Database Handler Test\n")
    
    # Test Redis connection
    db = RedisDatabaseHandler()
    
    if db.is_connected():
        print("✅ Redis connection successful")
        
        # Test storing market data
        market_data = {
            'symbol': 'BTC/USDT',
            'price': 50000.0,
            'volume': 1000.0,
            'change_24h': 2.5
        }
        
        if db.store_market_data('BTC/USDT', market_data):
            print("✅ Market data stored")
            
            retrieved = db.get_market_data('BTC/USDT')
            if retrieved:
                print(f"✅ Market data retrieved: {retrieved}")
        
        # Test storing trade
        trade_data = {
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'amount': 0.001,
            'price': 50000.0,
            'profit': 0.0
        }
        
        if db.store_trade('test_trade_1', trade_data):
            print("✅ Trade stored")
            
            retrieved_trade = db.get_trade('test_trade_1')
            if retrieved_trade:
                print(f"✅ Trade retrieved: {retrieved_trade}")
        
        # Test system stats
        stats = db.get_system_stats()
        print(f"✅ System stats: {stats}")
        
        db.close()
    else:
        print("❌ Redis connection failed")
    
    print("\n✅ Database handler test completed!")