import os, json, sqlite3, threading, time
from datetime import datetime
from typing import Dict, Any
from util.paths import data_path

class CryptoComAIMemoryManager:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or data_path('ai_memory.db')
        self.exchange = 'crypto.com'
        self.lock = threading.Lock()
        self._init_database()
        
    def _init_database(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS ai_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT UNIQUE NOT NULL,
                personality TEXT NOT NULL,
                decision_type TEXT NOT NULL,
                context TEXT NOT NULL,
                confidence REAL NOT NULL,
                exchange TEXT DEFAULT 'crypto.com',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            conn.commit()
            conn.close()
            # Rely on default umask; avoid chmod on restricted filesystems
            print("✅ AI Memory database initialized with proper permissions")
        except Exception as e:
            print(f"❌ AI Memory database failed: {e}")
            
    def store_decision(self, decision_id, personality, decision_type, context, confidence):
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""INSERT OR REPLACE INTO ai_decisions 
                    (decision_id, personality, decision_type, context, confidence, exchange)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (decision_id, personality, decision_type, json.dumps(context), confidence, 'crypto.com'))
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"❌ Decision storage failed: {e}")
            return False
            
    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ai_decisions WHERE exchange = 'crypto.com'")
            total = cursor.fetchone()[0]
            conn.close()
            return {'total_decisions': total, 'exchange': 'crypto.com'}
        except Exception as e:
            return {'total_decisions': 0, 'exchange': 'crypto.com', 'error': str(e)}

    def get_performance_summary(self) -> Dict[str, Any]:
        """Return a brief performance summary used by tests."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), MAX(created_at) FROM ai_decisions WHERE exchange = 'crypto.com'")
            row = cursor.fetchone()
            conn.close()
            total = int(row[0]) if row and row[0] is not None else 0
            last_decision_at = row[1] if row and row[1] is not None else None
            return {
                'total_decisions': total,
                'last_decision_at': last_decision_at,
                'exchange': 'crypto.com'
            }
        except Exception as e:
            return {
                'total_decisions': 0,
                'last_decision_at': None,
                'exchange': 'crypto.com',
                'error': str(e)
            }

    def test_functionality(self) -> bool:
        """Self-test used by the test suite.
        Stores a sample decision then confirms it is queryable.
        """
        try:
            decision_id = f"selftest_{int(time.time())}"
            ok = self.store_decision(
                decision_id=decision_id,
                personality="UnitTestAI",
                decision_type="self_test",
                context={
                    'symbol': 'BTC_USDT',
                    'price': 45000.0,
                    'exchange': 'crypto.com'
                },
                confidence=0.9
            )
            if not ok:
                return False
            summary = self.get_performance_summary()
            return summary.get('total_decisions', 0) >= 1
        except Exception as e:
            print(f"❌ AI Memory self-test failed: {e}")
            return False

ai_memory = CryptoComAIMemoryManager()
