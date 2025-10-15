#!/usr/bin/env python3
"""TPS19 Telegram Bot Integration - Real-time notifications and control"""

import requests
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import sys

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from trading_engine import trading_engine, OrderSide, OrderType, TradingMode
    from market_data import MarketData
    from siul.siul_core import siul_core
except ImportError as e:
    print(f"⚠️ Required modules not available: {e}")
    trading_engine = None
    MarketData = None
    siul_core = None

class TelegramBot:
    """Telegram Bot for TPS19 Trading System"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.running = False
        self.last_update_id = 0
        self.notification_queue = []
        self.lock = threading.Lock()
        
        if not self.bot_token or not self.chat_id:
            print("⚠️ Telegram bot token or chat ID not configured")
        
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send message to Telegram chat"""
        try:
            if not self.bot_token or not self.chat_id:
                print("⚠️ Telegram not configured, message not sent")
                return False
            
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False
    
    def send_trade_notification(self, trade_data: Dict) -> bool:
        """Send trade execution notification"""
        try:
            symbol = trade_data.get('symbol', 'Unknown')
            side = trade_data.get('side', 'Unknown')
            quantity = trade_data.get('quantity', 0)
            price = trade_data.get('price', 0)
            commission = trade_data.get('commission', 0)
            
            emoji = "🟢" if side == "BUY" else "🔴"
            
            message = f"""
{emoji} <b>TRADE EXECUTED</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>Symbol:</b> {symbol}
📈 <b>Side:</b> {side}
💰 <b>Quantity:</b> {quantity}
💵 <b>Price:</b> ${price:,.2f}
💸 <b>Commission:</b> ${commission:.4f}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"❌ Failed to send trade notification: {e}")
            return False
    
    def send_portfolio_update(self, portfolio_data: Dict) -> bool:
        """Send portfolio summary update"""
        try:
            balance = portfolio_data.get('balance', 0)
            total_value = portfolio_data.get('total_value', 0)
            total_pnl = portfolio_data.get('total_pnl', 0)
            positions = portfolio_data.get('positions', 0)
            
            pnl_emoji = "📈" if total_pnl >= 0 else "📉"
            pnl_color = "🟢" if total_pnl >= 0 else "🔴"
            
            message = f"""
📊 <b>PORTFOLIO UPDATE</b>
━━━━━━━━━━━━━━━━━━━━
💰 <b>Balance:</b> ${balance:,.2f}
💎 <b>Total Value:</b> ${total_value:,.2f}
{pnl_emoji} <b>P&L:</b> {pnl_color} ${total_pnl:,.2f}
📈 <b>Positions:</b> {positions}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"❌ Failed to send portfolio update: {e}")
            return False
    
    def send_siul_decision(self, decision_data: Dict) -> bool:
        """Send SIUL trading decision notification"""
        try:
            decision = decision_data.get('decision', 'HOLD')
            confidence = decision_data.get('confidence', 0)
            symbol = decision_data.get('symbol', 'Unknown')
            
            decision_emoji = {
                'BUY': '🟢',
                'SELL': '🔴',
                'HOLD': '🟡'
            }.get(decision, '❓')
            
            confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
            
            message = f"""
🧠 <b>SIUL DECISION</b>
━━━━━━━━━━━━━━━━━━━━
{decision_emoji} <b>Action:</b> {decision}
📊 <b>Symbol:</b> {symbol}
🎯 <b>Confidence:</b> {confidence:.1%}
{confidence_bar}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"❌ Failed to send SIUL decision: {e}")
            return False
    
    def send_alert(self, alert_type: str, message: str) -> bool:
        """Send system alert"""
        try:
            alert_emojis = {
                'ERROR': '🚨',
                'WARNING': '⚠️',
                'INFO': 'ℹ️',
                'SUCCESS': '✅'
            }
            
            emoji = alert_emojis.get(alert_type, '📢')
            
            formatted_message = f"""
{emoji} <b>{alert_type}</b>
━━━━━━━━━━━━━━━━━━━━
{message}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
            """.strip()
            
            return self.send_message(formatted_message)
            
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")
            return False
    
    def send_market_update(self, market_data: Dict) -> bool:
        """Send market data update"""
        try:
            symbol = market_data.get('symbol', 'Unknown')
            price = market_data.get('price', 0)
            change_24h = market_data.get('change_24h', 0)
            volume_24h = market_data.get('volume_24h', 0)
            
            change_emoji = "📈" if change_24h >= 0 else "📉"
            change_color = "🟢" if change_24h >= 0 else "🔴"
            
            message = f"""
📊 <b>MARKET UPDATE</b>
━━━━━━━━━━━━━━━━━━━━
💰 <b>Symbol:</b> {symbol}
💵 <b>Price:</b> ${price:,.2f}
{change_emoji} <b>24h Change:</b> {change_color} {change_24h:+.2f}%
📊 <b>Volume:</b> {volume_24h:,.0f}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"❌ Failed to send market update: {e}")
            return False
    
    def get_updates(self) -> List[Dict]:
        """Get updates from Telegram"""
        try:
            if not self.bot_token:
                return []
            
            url = f"{self.base_url}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30
            }
            
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            
            data = response.json()
            updates = data.get('result', [])
            
            if updates:
                self.last_update_id = updates[-1]['update_id']
            
            return updates
            
        except Exception as e:
            print(f"❌ Failed to get Telegram updates: {e}")
            return []
    
    def process_command(self, command: str, chat_id: str) -> str:
        """Process Telegram command"""
        try:
            command = command.lower().strip()
            
            if command == '/start':
                return "🚀 TPS19 Trading Bot Started!\n\nAvailable commands:\n/status - Portfolio status\n/balance - Account balance\n/positions - Current positions\n/orders - Open orders\n/help - Show help"
            
            elif command == '/status':
                if trading_engine:
                    portfolio = trading_engine.get_portfolio_summary()
                    return f"📊 Portfolio Status:\nBalance: ${portfolio.get('balance', 0):,.2f}\nTotal Value: ${portfolio.get('total_value', 0):,.2f}\nP&L: ${portfolio.get('total_pnl', 0):,.2f}\nPositions: {portfolio.get('positions', 0)}"
                return "❌ Trading engine not available"
            
            elif command == '/balance':
                if trading_engine:
                    portfolio = trading_engine.get_portfolio_summary()
                    return f"💰 Balance: ${portfolio.get('balance', 0):,.2f}"
                return "❌ Trading engine not available"
            
            elif command == '/positions':
                if trading_engine:
                    positions = trading_engine.positions
                    if positions:
                        pos_text = "📈 Current Positions:\n"
                        for symbol, pos in positions.items():
                            pos_text += f"{symbol}: {pos['quantity']} @ ${pos['average_price']:,.2f}\n"
                        return pos_text
                    return "📈 No open positions"
                return "❌ Trading engine not available"
            
            elif command == '/orders':
                if trading_engine:
                    orders = trading_engine.get_open_orders()
                    if orders:
                        orders_text = "📋 Open Orders:\n"
                        for order in orders[:5]:  # Show max 5 orders
                            orders_text += f"{order['symbol']} {order['side']} {order['quantity']} @ ${order.get('price', 'Market')}\n"
                        return orders_text
                    return "📋 No open orders"
                return "❌ Trading engine not available"
            
            elif command == '/help':
                return """🤖 TPS19 Trading Bot Help

Available Commands:
/start - Start the bot
/status - Portfolio overview
/balance - Account balance
/positions - Current positions
/orders - Open orders
/help - Show this help

The bot will automatically send:
• Trade notifications
• Portfolio updates
• SIUL decisions
• Market alerts
• System status updates"""
            
            else:
                return "❓ Unknown command. Type /help for available commands."
                
        except Exception as e:
            print(f"❌ Command processing error: {e}")
            return "❌ Error processing command"
    
    def start_bot(self):
        """Start the Telegram bot"""
        try:
            if not self.bot_token or not self.chat_id:
                print("❌ Telegram bot not configured")
                return False
            
            print("🤖 Starting Telegram Bot...")
            self.running = True
            
            # Send startup message
            self.send_message("🚀 TPS19 Trading Bot Started!\n\nBot is now monitoring your trading system.")
            
            # Start update polling in separate thread
            update_thread = threading.Thread(target=self._poll_updates, daemon=True)
            update_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Telegram bot: {e}")
            return False
    
    def _poll_updates(self):
        """Poll for Telegram updates"""
        while self.running:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    if 'message' in update:
                        message = update['message']
                        chat_id = str(message['chat']['id'])
                        text = message.get('text', '')
                        
                        if text.startswith('/'):
                            response = self.process_command(text, chat_id)
                            self.send_message(response)
                
                time.sleep(1)  # Poll every second
                
            except Exception as e:
                print(f"❌ Update polling error: {e}")
                time.sleep(5)
    
    def stop_bot(self):
        """Stop the Telegram bot"""
        self.running = False
        self.send_message("🛑 TPS19 Trading Bot Stopped")
    
    def test_telegram_bot(self) -> bool:
        """Test Telegram bot functionality"""
        try:
            print("🧪 Testing Telegram Bot...")
            
            # Test message sending
            test_message = "🧪 TPS19 Telegram Bot Test Message"
            if not self.send_message(test_message):
                print("❌ Message sending test failed")
                return False
            
            # Test alert sending
            if not self.send_alert("INFO", "This is a test alert"):
                print("❌ Alert sending test failed")
                return False
            
            print("✅ Telegram Bot test passed")
            return True
            
        except Exception as e:
            print(f"❌ Telegram Bot test error: {e}")
            return False

# Global instance
telegram_bot = TelegramBot()
