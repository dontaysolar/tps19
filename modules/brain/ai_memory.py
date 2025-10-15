import os, json, sqlite3, threading, time
from datetime import datetime
from modules.common.config import get_db_path

class CryptoComAIMemoryManager:
    def __init__(self, db_path: str | None = None):
        # Centralized database location
        self.db_path = db_path or get_db_path('ai_memory.db')
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

    def get_performance_summary(self):
        """Return a summary compatible with UI expectations."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), AVG(confidence), MAX(created_at) FROM ai_decisions WHERE exchange = 'crypto.com'")
            row = cursor.fetchone() or (0, 0.0, None)
            conn.close()
            return {
                'total_decisions': row[0] or 0,
                'average_confidence': float(row[1] or 0.0),
                'last_updated': row[2] or 'N/A',
                'exchange': 'crypto.com',
                'personality_breakdown': {},
            }
        except Exception as e:
            return {
                'total_decisions': 0,
                'average_confidence': 0.0,
                'last_updated': 'N/A',
                'exchange': 'crypto.com',
                'error': str(e),
            }

    def test_functionality(self) -> bool:
        """Basic self-test used by the test suite."""
        try:
            decision_id = f"ai_mem_test_{int(time.time())}"
            ok = self.store_decision(decision_id, "Tester", "self_test", {"note": "ok"}, 0.9)
            stats = self.get_stats()
            return bool(ok and isinstance(stats.get('total_decisions', 0), int))
        except Exception:
            return False

ai_memory = CryptoComAIMemoryManager()
