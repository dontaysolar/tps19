#!/usr/bin/env python3
"""
SIUL - Smart Intelligent Unified Logic Engine
Advanced AI decision making system for TPS19
"""

import json
import sqlite3
import numpy as np
from datetime import datetime
import logging
import os

class SIULEngine:
    def __init__(self):
        self.db_path = "/opt/tps19/data/siul.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
        self.models = {}
        
    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    decision_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    reasoning TEXT,
                    market_data TEXT,
                    result TEXT
                )
            """)
            conn.commit()
            conn.close()
            print("✅ SIUL database initialized")
        except Exception as e:
            print(f"❌ SIUL database error: {e}")
        
    def analyze_market(self, market_data):
        """Analyze market conditions using AI"""
        try:
            # Advanced AI analysis
            price = market_data.get('price', 0)
            volume = market_data.get('volume', 0)
            prev_price = market_data.get('prev_price', price)
            
            # Calculate technical indicators
            price_change = (price - prev_price) / prev_price if prev_price > 0 else 0
            
            # AI decision logic
            if price_change > 0.02:  # 2% increase
                trend = "strong_bullish"
                confidence = 0.85
                reasoning = f"Strong upward momentum: {price_change:.2%} price increase"
            elif price_change > 0.005:  # 0.5% increase
                trend = "bullish"
                confidence = 0.7
                reasoning = f"Bullish trend: {price_change:.2%} price increase"
            elif price_change < -0.02:  # 2% decrease
                trend = "strong_bearish"
                confidence = 0.85
                reasoning = f"Strong downward momentum: {price_change:.2%} price decrease"
            elif price_change < -0.005:  # 0.5% decrease
                trend = "bearish"
                confidence = 0.7
                reasoning = f"Bearish trend: {price_change:.2%} price decrease"
            else:
                trend = "neutral"
                confidence = 0.6
                reasoning = "Sideways movement, no clear trend"
                
            decision = {
                'trend': trend,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'reasoning': reasoning,
                'price_change': price_change,
                'volume_analysis': 'high' if volume > 1000000 else 'normal'
            }
            
            # Store decision
            self.store_decision('market_analysis', confidence, reasoning, json.dumps(market_data))
            
            return decision
            
        except Exception as e:
            print(f"❌ SIUL analysis error: {e}")
            return {'trend': 'neutral', 'confidence': 0.5, 'error': str(e)}
            
    def store_decision(self, decision_type, confidence, reasoning, market_data):
        """Store AI decision in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ai_decisions (decision_type, confidence, reasoning, market_data)
                VALUES (?, ?, ?, ?)
            """, (decision_type, confidence, reasoning, market_data))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error storing decision: {e}")
            
    def get_decision_history(self, limit=10):
        """Get recent AI decisions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ai_decisions 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"❌ Error getting decision history: {e}")
            return []
            
    def get_ai_stats(self):
        """Get AI performance statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total decisions
            cursor.execute("SELECT COUNT(*) FROM ai_decisions")
            total_decisions = cursor.fetchone()[0]
            
            # Get average confidence
            cursor.execute("SELECT AVG(confidence) FROM ai_decisions")
            avg_confidence = cursor.fetchone()[0] or 0
            
            # Get decision types
            cursor.execute("""
                SELECT decision_type, COUNT(*) 
                FROM ai_decisions 
                GROUP BY decision_type
            """)
            decision_types = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_decisions': total_decisions,
                'average_confidence': round(avg_confidence, 3),
                'decision_types': dict(decision_types)
            }
        except Exception as e:
            print(f"❌ Error getting AI stats: {e}")
            return {}

if __name__ == "__main__":
    siul = SIULEngine()
    print("✅ SIUL Engine initialized successfully")
    
    # Test analysis
    test_data = {'price': 50000, 'prev_price': 49500, 'volume': 1500000}
    result = siul.analyze_market(test_data)
    print(f"✅ Test analysis: {result}")
    
    # Show stats
    stats = siul.get_ai_stats()
    print(f"✅ AI Stats: {stats}")
