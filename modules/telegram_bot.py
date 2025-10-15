#!/usr/bin/env python3
"""
TPS19 Telegram Bot Integration
Real-time trading alerts and system monitoring via Telegram
"""

import os
import json
import time
import sqlite3
import threading
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

class TPS19TelegramBot:
    """Complete Telegram Bot for TPS19 Trading System"""
    
    def __init__(self, config_path='/opt/tps19/config/telegram_config.json'):
        self.config_path = config_path
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_ids = []
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
        self.db_path = "/opt/tps19/data/databases/telegram_bot.db"
        self.running = False
        self.update_offset = 0
        
        self._load_config()
        self._init_database()
        
    def _load_config(self):
        """Load Telegram bot configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.bot_token = config.get('bot_token', self.bot_token)
                    self.chat_ids = config.get('chat_ids', [])
                    self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
            else:
                self._create_default_config()
        except Exception as e:
            print(f"❌ Telegram config error: {e}")
    
    def _create_default_config(self):
        """Create default Telegram configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            default_config = {
                "bot_token": "",
                "chat_ids": [],
                "alerts_enabled": True,
                "notification_settings": {
                    "trade_signals": True,
                    "price_alerts": True,
                    "system_status": True,
                    "error_alerts": True
                },
                "rate_limits": {
                    "messages_per_minute": 20,
                    "messages_per_hour": 100
                }
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                
            print(f"✅ Created default Telegram config at {self.config_path}")
            print("⚠️ Please set TELEGRAM_BOT_TOKEN environment variable or edit config file")
            
        except Exception as e:
            print(f"❌ Config creation error: {e}")
    
    def _init_database(self):
        """Initialize Telegram bot database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT,
                    sent BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL UNIQUE,
                    username TEXT,
                    subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT 1
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Telegram bot database initialized")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = 'HTML') -> bool:
        """Send a message to a specific chat"""
        if not self.bot_token:
            print("⚠️ Telegram bot token not configured")
            return False
        
        try:
            url = f"{self.api_base}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                self._log_message(chat_id, 'text', text, 'sent')
                return True
            else:
                self._log_message(chat_id, 'text', text, 'failed')
                print(f"❌ Message send failed: {response.text}")
                return False
                
        except Exception as e:
            self._log_message(chat_id, 'text', text, 'error')
            print(f"❌ Telegram send error: {e}")
            return False
    
    def broadcast_message(self, text: str, parse_mode: str = 'HTML') -> int:
        """Broadcast message to all subscribed chats"""
        if not self.chat_ids:
            print("⚠️ No chat IDs configured")
            return 0
        
        sent_count = 0
        for chat_id in self.chat_ids:
            if self.send_message(chat_id, text, parse_mode):
                sent_count += 1
            time.sleep(0.1)  # Rate limiting
        
        return sent_count
    
    def send_trade_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Send trading signal alert"""
        try:
            symbol = signal_data.get('symbol', 'UNKNOWN')
            action = signal_data.get('action', 'UNKNOWN').upper()
            price = signal_data.get('price', 0)
            confidence = signal_data.get('confidence', 0) * 100
            
            # Determine emoji based on action
            emoji = "🟢" if action == "BUY" else "🔴" if action == "SELL" else "🟡"
            
            message = f"""
{emoji} <b>TRADING SIGNAL</b> {emoji}

<b>Symbol:</b> {symbol}
<b>Action:</b> {action}
<b>Price:</b> ${price:,.2f}
<b>Confidence:</b> {confidence:.1f}%
<b>Exchange:</b> crypto.com
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚡ TPS19 AI Trading System
"""
            
            sent = self.broadcast_message(message.strip())
            self._log_alert('trade_signal', 'info', message, json.dumps(signal_data))
            
            return sent > 0
            
        except Exception as e:
            print(f"❌ Trade signal error: {e}")
            return False
    
    def send_price_alert(self, symbol: str, price: float, change_24h: float) -> bool:
        """Send price alert"""
        try:
            emoji = "🚀" if change_24h > 5 else "📉" if change_24h < -5 else "📊"
            change_emoji = "⬆️" if change_24h > 0 else "⬇️"
            
            message = f"""
{emoji} <b>PRICE ALERT</b> {emoji}

<b>Symbol:</b> {symbol}
<b>Current Price:</b> ${price:,.2f}
<b>24h Change:</b> {change_emoji} {change_24h:+.2f}%
<b>Exchange:</b> crypto.com
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚡ TPS19 Price Monitor
"""
            
            sent = self.broadcast_message(message.strip())
            
            return sent > 0
            
        except Exception as e:
            print(f"❌ Price alert error: {e}")
            return False
    
    def send_system_status(self, status_data: Dict[str, Any]) -> bool:
        """Send system status update"""
        try:
            status = status_data.get('status', 'unknown')
            emoji = "✅" if status == 'healthy' else "⚠️" if status == 'warning' else "❌"
            
            message = f"""
{emoji} <b>SYSTEM STATUS</b> {emoji}

<b>Status:</b> {status.upper()}
<b>Uptime:</b> {status_data.get('uptime', 0)} hours
<b>Active Feeds:</b> {status_data.get('active_feeds', 0)}
<b>AI Decisions:</b> {status_data.get('ai_decisions', 0)}
<b>Exchange:</b> crypto.com
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚡ TPS19 System Monitor
"""
            
            sent = self.broadcast_message(message.strip())
            self._log_alert('system_status', 'info', message, json.dumps(status_data))
            
            return sent > 0
            
        except Exception as e:
            print(f"❌ System status error: {e}")
            return False
    
    def send_error_alert(self, error_type: str, error_message: str) -> bool:
        """Send error alert"""
        try:
            message = f"""
🚨 <b>ERROR ALERT</b> 🚨

<b>Type:</b> {error_type}
<b>Message:</b> {error_message}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚡ TPS19 Error Monitor
"""
            
            sent = self.broadcast_message(message.strip())
            self._log_alert('error', 'critical', message, error_message)
            
            return sent > 0
            
        except Exception as e:
            print(f"❌ Error alert send failed: {e}")
            return False
    
    def send_daily_summary(self, summary_data: Dict[str, Any]) -> bool:
        """Send daily trading summary"""
        try:
            total_trades = summary_data.get('total_trades', 0)
            profit = summary_data.get('profit', 0)
            profit_emoji = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"
            
            message = f"""
📊 <b>DAILY SUMMARY</b> 📊

<b>Total Trades:</b> {total_trades}
<b>Profit/Loss:</b> {profit_emoji} ${profit:,.2f}
<b>Win Rate:</b> {summary_data.get('win_rate', 0):.1f}%
<b>Best Trade:</b> ${summary_data.get('best_trade', 0):,.2f}
<b>Worst Trade:</b> ${summary_data.get('worst_trade', 0):,.2f}
<b>Exchange:</b> crypto.com
<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}

⚡ TPS19 Daily Report
"""
            
            sent = self.broadcast_message(message.strip())
            
            return sent > 0
            
        except Exception as e:
            print(f"❌ Daily summary error: {e}")
            return False
    
    def _log_message(self, chat_id: int, msg_type: str, content: str, status: str):
        """Log sent messages"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (chat_id, message_type, content, status)
                VALUES (?, ?, ?, ?)
            """, (chat_id, msg_type, content, status))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Message log error: {e}")
    
    def _log_alert(self, alert_type: str, severity: str, message: str, data: str):
        """Log alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (alert_type, severity, message, data, sent)
                VALUES (?, ?, ?, ?, 1)
            """, (alert_type, severity, message, data))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Alert log error: {e}")
    
    def subscribe_chat(self, chat_id: int, username: str = None) -> bool:
        """Subscribe a chat to receive alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_subscriptions (chat_id, username, active)
                VALUES (?, ?, 1)
            """, (chat_id, username))
            conn.commit()
            conn.close()
            
            if chat_id not in self.chat_ids:
                self.chat_ids.append(chat_id)
            
            print(f"✅ Chat {chat_id} subscribed")
            return True
            
        except Exception as e:
            print(f"❌ Subscription error: {e}")
            return False
    
    def unsubscribe_chat(self, chat_id: int) -> bool:
        """Unsubscribe a chat from alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_subscriptions SET active = 0
                WHERE chat_id = ?
            """, (chat_id,))
            conn.commit()
            conn.close()
            
            if chat_id in self.chat_ids:
                self.chat_ids.remove(chat_id)
            
            print(f"✅ Chat {chat_id} unsubscribed")
            return True
            
        except Exception as e:
            print(f"❌ Unsubscribe error: {e}")
            return False
    
    def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """Get bot information"""
        if not self.bot_token:
            return None
        
        try:
            url = f"{self.api_base}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('result', {})
            
            return None
            
        except Exception as e:
            print(f"❌ Bot info error: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        if not self.bot_token:
            print("❌ Bot token not configured")
            return False
        
        bot_info = self.get_bot_info()
        if bot_info:
            print(f"✅ Bot connected: @{bot_info.get('username', 'unknown')}")
            return True
        else:
            print("❌ Bot connection failed")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bot statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Message stats
            cursor.execute("""
                SELECT COUNT(*), status
                FROM messages
                WHERE sent_at > datetime('now', '-24 hours')
                GROUP BY status
            """)
            message_stats = dict(cursor.fetchall())
            
            # Alert stats
            cursor.execute("""
                SELECT COUNT(*), alert_type
                FROM alerts
                WHERE created_at > datetime('now', '-24 hours')
                GROUP BY alert_type
            """)
            alert_stats = dict(cursor.fetchall())
            
            # Subscriber count
            cursor.execute("SELECT COUNT(*) FROM user_subscriptions WHERE active = 1")
            subscriber_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'message_stats': message_stats,
                'alert_stats': alert_stats,
                'subscriber_count': subscriber_count,
                'chat_ids': self.chat_ids
            }
            
        except Exception as e:
            print(f"❌ Statistics error: {e}")
            return {}

# Global Telegram bot instance
telegram_bot = TPS19TelegramBot()

if __name__ == "__main__":
    bot = TPS19TelegramBot()
    
    print("🤖 TPS19 Telegram Bot")
    print("=" * 60)
    
    # Test connection
    print("\n🔍 Testing bot connection...")
    if bot.test_connection():
        bot_info = bot.get_bot_info()
        if bot_info:
            print(f"  Bot Name: {bot_info.get('first_name', 'Unknown')}")
            print(f"  Username: @{bot_info.get('username', 'Unknown')}")
            print(f"  Bot ID: {bot_info.get('id', 'Unknown')}")
    
    # Test signal (will only work if bot token is configured)
    if bot.bot_token and bot.chat_ids:
        print("\n📤 Sending test signal...")
        test_signal = {
            'symbol': 'BTC_USDT',
            'action': 'buy',
            'price': 45000,
            'confidence': 0.85
        }
        bot.send_trade_signal(test_signal)
    
    # Get statistics
    print("\n📊 Bot Statistics:")
    stats = bot.get_statistics()
    print(f"  Subscribers: {stats.get('subscriber_count', 0)}")
    print(f"  Message Stats: {stats.get('message_stats', {})}")
    print(f"  Alert Stats: {stats.get('alert_stats', {})}")
    
    print("\n✅ Telegram Bot Module Ready")
    print("⚠️ Configure TELEGRAM_BOT_TOKEN and chat IDs to enable notifications")
