import os, json, sqlite3, threading, time
from datetime import datetime
from modules.utils.paths import db_path

class CryptoComAIMemoryManager:
    def __init__(self, db_path_override=None):
        self.db_path = db_path_override or db_path('ai_memory.db')
        self.exchange = 'crypto.com'
        self.lock = threading.Lock()
        self._init_database()
        
    def _init_database(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            os.chmod(os.path.dirname(self.db_path), 0o777)
            
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
            os.chmod(self.db_path, 0o666)
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

    # Added for compatibility with test suite
    def get_performance_summary(self):
        stats = self.get_stats()
        return {
            'total_decisions': stats.get('total_decisions', 0),
            'exchange': stats.get('exchange', 'crypto.com')
        }

    def test_functionality(self):
        try:
            test_id = f"test_{int(time.time())}"
            ok = self.store_decision(test_id, 'TestAI', 'unit_test', {'foo': 'bar'}, 0.9)
            return bool(ok)
        except Exception:
            return False

ai_memory = CryptoComAIMemoryManager()
