#!/usr/bin/env python3
"""
DTCP - Distributed Trading Control Protocol
Signal Provider (SIGNALS ONLY - NO TRADING)
"""

import json
import sqlite3
import time
import os
from datetime import datetime
import logging
from modules.common.config import get_db_path

class DTCPSignalProvider:
    def __init__(self):
        self.db_path = get_db_path('dtcp_signals.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
        self.active = False
        
    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    signal_type TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    price REAL,
                    target_price REAL,
                    stop_loss REAL,
                    reasoning TEXT,
                    status TEXT DEFAULT 'active'
                )
            """)
            conn.commit()
            conn.close()
            print("✅ DTCP database initialized")
        except Exception as e:
            print(f"❌ DTCP database error: {e}")
        
    def generate_signal(self, symbol, market_data):
        """Generate trading signal (SIGNAL ONLY - NO EXECUTION)"""
        try:
            # Advanced signal generation logic
            price = market_data.get('price', 0)
            volume = market_data.get('volume', 0)
            sma_20 = market_data.get('sma_20', price)
            rsi = market_data.get('rsi', 50)
            
            # Multi-factor signal analysis
            signal_strength = 0
            reasoning_parts = []
            
            # Price vs SMA analysis
            if price > sma_20 * 1.02:  # 2% above SMA
                signal_strength += 0.3
                reasoning_parts.append("Price significantly above SMA-20")
            elif price > sma_20:
                signal_strength += 0.1
                reasoning_parts.append("Price above SMA-20")
            elif price < sma_20 * 0.98:  # 2% below SMA
                signal_strength -= 0.3
                reasoning_parts.append("Price significantly below SMA-20")
            else:
                signal_strength -= 0.1
                reasoning_parts.append("Price below SMA-20")
                
            # RSI analysis
            if rsi < 30:  # Oversold
                signal_strength += 0.2
                reasoning_parts.append("RSI oversold condition")
            elif rsi > 70:  # Overbought
                signal_strength -= 0.2
                reasoning_parts.append("RSI overbought condition")
                
            # Volume analysis
            if volume > 1000000:  # High volume
                signal_strength += 0.1
                reasoning_parts.append("High volume confirmation")
                
            # Determine action and confidence
            if signal_strength > 0.3:
                action = "STRONG_BUY"
                confidence = min(0.9, 0.6 + signal_strength)
                target_price = price * 1.05  # 5% target
                stop_loss = price * 0.97     # 3% stop loss
            elif signal_strength > 0.1:
                action = "BUY"
                confidence = min(0.8, 0.5 + signal_strength)
                target_price = price * 1.03  # 3% target
                stop_loss = price * 0.98     # 2% stop loss
            elif signal_strength < -0.3:
                action = "STRONG_SELL"
                confidence = min(0.9, 0.6 + abs(signal_strength))
                target_price = price * 0.95  # 5% target down
                stop_loss = price * 1.03     # 3% stop loss
            elif signal_strength < -0.1:
                action = "SELL"
                confidence = min(0.8, 0.5 + abs(signal_strength))
                target_price = price * 0.97  # 3% target down
                stop_loss = price * 1.02     # 2% stop loss
            else:
                action = "HOLD"
                confidence = 0.5
                target_price = price
                stop_loss = price
                reasoning_parts.append("No clear signal")
                
            signal = {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'price': price,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'timestamp': datetime.now().isoformat(),
                'reasoning': "; ".join(reasoning_parts),
                'signal_only': True,  # IMPORTANT: Signals only, no trading
                'signal_strength': signal_strength
            }
            
            # Store signal
            self.store_signal(signal)
            
            return signal
            
        except Exception as e:
            print(f"❌ DTCP signal generation error: {e}")
            return None
            
    def store_signal(self, signal):
        """Store generated signal"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO signals (signal_type, symbol, action, confidence, price, target_price, stop_loss, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ('dtcp', signal['symbol'], signal['action'], 
                  signal['confidence'], signal['price'], signal['target_price'], 
                  signal['stop_loss'], signal['reasoning']))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error storing signal: {e}")
            
    def get_active_signals(self, limit=10):
        """Get active signals"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM signals 
                WHERE status = 'active'
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"❌ Error getting signals: {e}")
            return []
            
    def get_signal_stats(self):
        """Get signal performance statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total signals
            cursor.execute("SELECT COUNT(*) FROM signals")
            total_signals = cursor.fetchone()[0]
            
            # Get signals by action
            cursor.execute("""
                SELECT action, COUNT(*) 
                FROM signals 
                GROUP BY action
            """)
            action_counts = cursor.fetchall()
            
            # Get average confidence
            cursor.execute("SELECT AVG(confidence) FROM signals")
            avg_confidence = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_signals': total_signals,
                'average_confidence': round(avg_confidence, 3),
                'action_distribution': dict(action_counts)
            }
        except Exception as e:
            print(f"❌ Error getting signal stats: {e}")
            return {}

if __name__ == "__main__":
    dtcp = DTCPSignalProvider()
    print("✅ DTCP Signal Provider initialized successfully")
    
    # Test signal generation
    test_data = {
        'price': 50000, 
        'sma_20': 49500, 
        'volume': 1500000,
        'rsi': 35
    }
    signal = dtcp.generate_signal('BTC/USD', test_data)
    print(f"✅ Test signal: {signal}")
    
    # Show stats
    stats = dtcp.get_signal_stats()
    print(f"✅ Signal Stats: {stats}")
