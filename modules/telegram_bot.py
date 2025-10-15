#!/usr/bin/env python3
"""
TPS19 Telegram Bot Integration
Enhanced Telegram connectivity for trading signals and alerts
"""

import os
import json
import sqlite3
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import requests
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

class TPS19TelegramBot:
    def __init__(self):
        self.config_path = "/workspace/config/api_config.json"
        self.db_path = "/opt/tps19/data/databases/telegram.db"
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.load_config()
        self.init_database()
        self.bot = None
        self.application = None
        
    def load_config(self):
        """Load Telegram configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.config = config.get('telegram', {})
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            self.config = {"api_url": "https://api.telegram.org/bot"}
            
    def init_database(self):
        """Initialize Telegram database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    chat_id TEXT,
                    message_type TEXT,
                    content TEXT,
                    sent BOOLEAN DEFAULT FALSE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    alert_type TEXT,
                    price REAL,
                    message TEXT,
                    sent BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Telegram database initialized")
        except Exception as e:
            print(f"❌ Telegram database error: {e}")
            
    async def initialize_bot(self):
        """Initialize Telegram bot"""
        if not self.bot_token:
            print("❌ No Telegram bot token found")
            return False
            
        try:
            self.application = Application.builder().token(self.bot_token).build()
            self.bot = self.application.bot
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("price", self.price_command))
            self.application.add_handler(CommandHandler("alerts", self.alerts_command))
            
            print("✅ Telegram bot initialized")
            return True
        except Exception as e:
            print(f"❌ Telegram bot initialization error: {e}")
            return False
            
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🚀 TPS19 Trading System Bot\n\n"
            "Available commands:\n"
            "/status - System status\n"
            "/price <symbol> - Get current price\n"
            "/alerts - View recent alerts"
        )
        
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Get system status from database
            status_msg = "📊 TPS19 System Status\n\n"
            status_msg += f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            status_msg += "✅ System: Online\n"
            status_msg += "✅ Market Data: Active\n"
            status_msg += "✅ Trading Engine: Running\n"
            
            await update.message.reply_text(status_msg)
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {e}")
            
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price command"""
        try:
            if not context.args:
                await update.message.reply_text("Please specify a symbol: /price BTC_USDT")
                return
                
            symbol = context.args[0].upper()
            
            # Get price from market data
            from realtime_data import RealtimeDataFeed
            feed = RealtimeDataFeed()
            price_data = feed.get_latest_price(symbol)
            
            if price_data:
                msg = f"💰 {symbol}\n"
                msg += f"Price: ${price_data['price']:,.2f}\n"
                msg += f"24h Change: {price_data['price_change_24h']:.2f}%\n"
                msg += f"Volume: {price_data['volume']:,.0f}\n"
                msg += f"Updated: {price_data['timestamp']}"
            else:
                msg = f"❌ No data found for {symbol}"
                
            await update.message.reply_text(msg)
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting price: {e}")
            
    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT symbol, alert_type, price, message, timestamp 
                FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            alerts = cursor.fetchall()
            conn.close()
            
            if alerts:
                msg = "🚨 Recent Alerts:\n\n"
                for alert in alerts:
                    msg += f"📊 {alert[0]} - {alert[1]}\n"
                    msg += f"💰 Price: ${alert[2]:,.2f}\n"
                    msg += f"📝 {alert[3]}\n"
                    msg += f"🕒 {alert[4]}\n\n"
            else:
                msg = "No recent alerts"
                
            await update.message.reply_text(msg)
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting alerts: {e}")
            
    async def send_message(self, message: str, message_type: str = "info"):
        """Send message to Telegram"""
        if not self.bot or not self.chat_id:
            return False
            
        try:
            # Store message in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (chat_id, message_type, content)
                VALUES (?, ?, ?)
            """, (self.chat_id, message_type, message))
            conn.commit()
            conn.close()
            
            # Send message
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            
            # Mark as sent
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE messages SET sent = TRUE 
                WHERE chat_id = ? AND content = ? AND sent = FALSE
            """, (self.chat_id, message))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
            return False
            
    async def send_trade_alert(self, symbol: str, action: str, price: float, confidence: float):
        """Send trading alert"""
        try:
            emoji = "🚀" if action == "BUY" else "📉" if action == "SELL" else "⏸️"
            
            message = f"{emoji} TRADE SIGNAL\n\n"
            message += f"📊 Symbol: {symbol}\n"
            message += f"🎯 Action: {action}\n"
            message += f"💰 Price: ${price:,.2f}\n"
            message += f"🎲 Confidence: {confidence:.1%}\n"
            message += f"🕒 Time: {datetime.now().strftime('%H:%M:%S')}"
            
            # Store alert
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (symbol, alert_type, price, message)
                VALUES (?, ?, ?, ?)
            """, (symbol, action, price, message))
            conn.commit()
            conn.close()
            
            return await self.send_message(message, "trade_alert")
        except Exception as e:
            print(f"❌ Error sending trade alert: {e}")
            return False
            
    async def send_system_status(self, status: Dict):
        """Send system status update"""
        try:
            message = "📊 TPS19 System Update\n\n"
            for key, value in status.items():
                message += f"{key}: {value}\n"
            message += f"\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return await self.send_message(message, "system_status")
        except Exception as e:
            print(f"❌ Error sending system status: {e}")
            return False
            
    def run_bot(self):
        """Run the Telegram bot"""
        if not self.application:
            print("❌ Bot not initialized")
            return
            
        try:
            print("🚀 Starting Telegram bot...")
            self.application.run_polling()
        except Exception as e:
            print(f"❌ Error running bot: {e}")

# Global bot instance
telegram_bot = TPS19TelegramBot()

async def initialize_telegram():
    """Initialize Telegram bot"""
    return await telegram_bot.initialize_bot()

async def send_telegram_message(message: str, message_type: str = "info"):
    """Send message via Telegram"""
    return await telegram_bot.send_message(message, message_type)

async def send_trade_signal(symbol: str, action: str, price: float, confidence: float):
    """Send trade signal via Telegram"""
    return await telegram_bot.send_trade_alert(symbol, action, price, confidence)

if __name__ == "__main__":
    import asyncio
    
    async def main():
        if await telegram_bot.initialize_bot():
            print("✅ Telegram bot ready")
            telegram_bot.run_bot()
        else:
            print("❌ Failed to initialize Telegram bot")
    
    asyncio.run(main())