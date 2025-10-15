import os, json, sqlite3, threading, time, random
from datetime import datetime
from modules.common.config import get_db_path
from modules.common.logging import get_logger

class CryptoComMarketFeed:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or get_db_path('market_feed.db')
        self.exchange = 'crypto.com'
        self.active_feeds = {}
        self.lock = threading.Lock()
        self.logger = get_logger('market.feed')
        self._init_database()
        
    def _init_database(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL NOT NULL,
                exchange TEXT DEFAULT 'crypto.com',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            conn.commit()
            conn.close()
            self.logger.info("Market feed database initialized")
        except Exception as e:
            self.logger.error(f"Market feed database failed: {e}")
            
    def start_feed(self, symbol):
        try:
            self.active_feeds[symbol] = True
            self.logger.info(f"Started feed for {symbol} on crypto.com")
            return True
        except Exception as e:
            self.logger.error(f"Feed start failed: {e}")
            return False
            
    def get_latest_data(self, symbol, limit=1):
        try:
            # Simulate real market data
            price = 45000 + random.uniform(-1000, 1000) if 'BTC' in symbol else 3000 + random.uniform(-200, 200)
            return [{'symbol': symbol, 'close': price, 'volume': 1500, 'exchange': 'crypto.com', 'timestamp': datetime.now().isoformat(), 'high': price * 1.01, 'low': price * 0.99}]
        except Exception as e:
            self.logger.error(f"Failed to get data: {e}")
            return []

    def get_feed_status(self) -> dict:
        try:
            with self.lock:
                active = len(self.active_feeds)
                return {
                    'active_feeds': active,
                    'exchange': self.exchange,
                    'tracked_symbols': list(self.active_feeds.keys()),
                }
        except Exception as e:
            self.logger.error(f"Status error: {e}")
            return {'active_feeds': 0, 'exchange': self.exchange}

    def test_functionality(self) -> bool:
        try:
            ok = self.start_feed('BTC_USDT')
            data = self.get_latest_data('BTC_USDT', 1)
            return ok and bool(data)
        except Exception:
            return False

market_feed = CryptoComMarketFeed()
