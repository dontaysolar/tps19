#!/usr/bin/env python3
"""TPS19 AI Council - AI decision making system"""

import json
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

from modules.utils.config import config
from modules.utils.logger import get_logger
from modules.utils.database import get_db_connection

logger = get_logger(__name__)


class AICouncil:
    def __init__(self):
        self.db_name = 'ai_decisions.db'
        self.init_database()
        
    def init_database(self):
        """Initialize AI decisions database"""
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ai_decisions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_type TEXT NOT NULL,
                        input_data TEXT,
                        decision TEXT NOT NULL,
                        confidence REAL DEFAULT 0.0,
                        outcome TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ai_learning (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern TEXT NOT NULL,
                        success_rate REAL DEFAULT 0.0,
                        total_occurrences INTEGER DEFAULT 0,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
            logger.info("AI Council database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Council database: {e}")
        
    def make_trading_decision(self, market_data, portfolio_data):
        """Make AI-powered trading decision"""
        # Simple AI logic (would be more sophisticated in production)
        price = market_data.get('price', 50000)
        change_24h = market_data.get('change_24h', 0)
        
        # Decision logic
        if change_24h > 5:
            decision = "strong_buy"
            confidence = 0.8
        elif change_24h > 2:
            decision = "buy"
            confidence = 0.6
        elif change_24h < -5:
            decision = "strong_sell"
            confidence = 0.8
        elif change_24h < -2:
            decision = "sell"
            confidence = 0.6
        else:
            decision = "hold"
            confidence = 0.5
            
        # Add some randomness to simulate AI uncertainty
        confidence *= random.uniform(0.8, 1.2)
        confidence = min(1.0, max(0.0, confidence))
        
        # Store decision
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ai_decisions (decision_type, input_data, decision, confidence)
                    VALUES (?, ?, ?, ?)
                ''', ("trading", json.dumps(market_data), decision, confidence))
        except Exception as e:
            logger.error(f"Failed to store AI decision: {e}")
        
        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": f"Based on 24h change of {change_24h}%"
        }
        
    def analyze_pattern(self, data_points):
        """Analyze market patterns"""
        # Simple pattern analysis
        if len(data_points) < 3:
            return {"pattern": "insufficient_data", "confidence": 0.0}
            
        # Check for trend
        recent_trend = sum(data_points[-3:]) / 3
        older_trend = sum(data_points[-6:-3]) / 3 if len(data_points) >= 6 else recent_trend
        
        if recent_trend > older_trend * 1.02:
            pattern = "uptrend"
            confidence = 0.7
        elif recent_trend < older_trend * 0.98:
            pattern = "downtrend"
            confidence = 0.7
        else:
            pattern = "sideways"
            confidence = 0.5
            
        return {"pattern": pattern, "confidence": confidence}
        
    def get_decision_history(self, limit: int = 50) -> List[tuple]:
        """Get AI decision history"""
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT decision_type, decision, confidence, timestamp
                    FROM ai_decisions
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get decision history: {e}")
            return []
        
    def update_learning(self, pattern: str, success: bool):
        """Update AI learning based on outcomes"""
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Check if pattern exists
                cursor.execute('SELECT * FROM ai_learning WHERE pattern = ?', (pattern,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing pattern
                    new_total = existing[3] + 1
                    new_success_rate = (existing[2] * existing[3] + (1 if success else 0)) / new_total
                    
                    cursor.execute('''
                        UPDATE ai_learning 
                        SET success_rate = ?, total_occurrences = ?, last_updated = ?
                        WHERE pattern = ?
                    ''', (new_success_rate, new_total, datetime.now(), pattern))
                else:
                    # Create new pattern
                    cursor.execute('''
                        INSERT INTO ai_learning (pattern, success_rate, total_occurrences)
                        VALUES (?, ?, 1)
                    ''', (pattern, 1.0 if success else 0.0))
        except Exception as e:
            logger.error(f"Failed to update AI learning: {e}")

if __name__ == "__main__":
    ai = AICouncil()
    logger.info("AI Council initialized successfully")
