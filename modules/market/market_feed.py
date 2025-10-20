import os, json, sqlite3, threading, time
from datetime import datetime

class CryptoComMarketFeed:
    def __init__(self, db_path='/opt/tps19/data/market_feed.db'):
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
        """Fetch latest data via REST fallback (ccxt), no simulation.

        Returns a list of OHLC-like dicts with 'close'. Falls back to LAST_PRICE env
        if REST is unavailable.
        """
        try:
            import ccxt  # lazy import
            ex = ccxt.cryptocom({'enableRateLimit': True})
            sym = symbol.replace('_', '/')
            ticker = ex.fetch_ticker(sym)
            price = float(ticker['last'])
            # Basic sanity checks
            if price <= 0 or price != price:  # NaN check
                return []
            return [{'symbol': sym, 'close': price, 'volume': float(ticker.get('baseVolume') or 0.0), 'exchange': 'crypto.com'}]
        except Exception:
            try:
                price_env = os.environ.get('LAST_PRICE')
                if price_env:
                    price = float(price_env)
                    return [{'symbol': symbol, 'close': price, 'volume': 0.0, 'exchange': 'crypto.com'}]
            except Exception:
                pass
            return []

market_feed = CryptoComMarketFeed()
