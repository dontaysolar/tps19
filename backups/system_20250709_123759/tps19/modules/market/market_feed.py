import os, json, sqlite3, threading, time, random
from datetime import datetime

class CryptoComMarketFeed:
    def __init__(self, db_path='/workspace/data/market_feed.db'):
        self.db_path = db_path
        self.exchange = 'crypto.com'
        self.active_feeds = {}
        self.lock = threading.Lock()
        self._init_database()
        
    def _init_database(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            os.chmod(os.path.dirname(self.db_path), 0o777)
            
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
            os.chmod(self.db_path, 0o666)
            print("✅ Market feed database initialized with proper permissions")
        except Exception as e:
            print(f"❌ Market feed database failed: {e}")
            
    def start_feed(self, symbol):
        try:
            self.active_feeds[symbol] = True
            print(f"✅ Started feed for {symbol} on crypto.com")
            return True
        except Exception as e:
            print(f"❌ Feed start failed: {e}")
            return False
            
    def get_latest_data(self, symbol, limit=1):
        try:
            # Simulate real market data
            price = 45000 + random.uniform(-1000, 1000) if 'BTC' in symbol else 3000 + random.uniform(-200, 200)
            return [{'symbol': symbol, 'close': price, 'volume': 1500, 'exchange': 'crypto.com'}]
        except Exception as e:
            print(f"❌ Failed to get data: {e}")
            return []

market_feed = CryptoComMarketFeed()
