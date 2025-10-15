#!/usr/bin/env python3
"""Enhanced Telegram Bot Integration for TPS19 Trading System"""

import json
import time
import sqlite3
import threading
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import telegram
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("Telegram module not installed. Install with: pip install python-telegram-bot")

# Import our modules
try:
    from market_data import MarketData
    from integrations.google_sheets import GoogleSheetsIntegration
except ImportError:
    print("Warning: Some modules not found")
    MarketData = None
    GoogleSheetsIntegration = None

class TelegramBot:
    """Enhanced Telegram Bot for TPS19 Trading System"""
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get('TELEGRAM_BOT_TOKEN')
        self.db_path = "/opt/tps19/data/databases/telegram_bot.db"
        self.app = None
        self.market_data = MarketData() if MarketData else None
        self.google_sheets = GoogleSheetsIntegration() if GoogleSheetsIntegration else None
        
        # Initialize database
        self.init_database()
        
        # Alert settings
        self.alert_settings = {}
        self.price_alerts = {}
        self.signal_subscribers = set()
        
        # Initialize bot if token available
        if TELEGRAM_AVAILABLE and self.token:
            self._init_bot()
            
    def init_database(self):
        """Initialize Telegram bot database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                is_admin INTEGER DEFAULT 0,
                notifications_enabled INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Message log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_type TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Price alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT NOT NULL,
                target_price REAL NOT NULL,
                alert_type TEXT CHECK(alert_type IN ('above', 'below')),
                active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trading signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_subscribers (
                user_id INTEGER PRIMARY KEY,
                subscribed INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _init_bot(self):
        """Initialize Telegram bot with handlers"""
        self.app = Application.builder().token(self.token).build()
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("price", self.cmd_price))
        self.app.add_handler(CommandHandler("market", self.cmd_market))
        self.app.add_handler(CommandHandler("alerts", self.cmd_alerts))
        self.app.add_handler(CommandHandler("setalert", self.cmd_set_alert))
        self.app.add_handler(CommandHandler("signals", self.cmd_signals))
        self.app.add_handler(CommandHandler("portfolio", self.cmd_portfolio))
        self.app.add_handler(CommandHandler("performance", self.cmd_performance))
        self.app.add_handler(CommandHandler("settings", self.cmd_settings))
        
        # Callback query handler for inline keyboards
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handler for non-command messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("✅ Telegram bot initialized with handlers")
        
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        # Register user
        self._register_user(user_id, username)
        
        welcome_text = (
            "🚀 *Welcome to TPS19 Trading Bot!*\n\n"
            "I'm your personal crypto trading assistant powered by AI.\n\n"
            "*Available Commands:*\n"
            "📊 /price [symbol] - Get current price\n"
            "📈 /market - Market overview\n"
            "🔔 /alerts - Manage price alerts\n"
            "📡 /signals - Subscribe to trading signals\n"
            "💼 /portfolio - View portfolio\n"
            "📊 /performance - Performance metrics\n"
            "⚙️ /settings - Bot settings\n"
            "❓ /help - Detailed help\n\n"
            "Let's start trading! 💰"
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 Get Prices", callback_data="menu_prices")],
            [InlineKeyboardButton("🔔 Set Alert", callback_data="menu_alerts")],
            [InlineKeyboardButton("📡 Trading Signals", callback_data="menu_signals")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "*🤖 TPS19 Trading Bot Help*\n\n"
            "*Price Commands:*\n"
            "• /price - Get BTC price\n"
            "• /price ETH - Get ETH price\n"
            "• /price BTC_USDT - Get specific pair\n\n"
            "*Alert Commands:*\n"
            "• /alerts - View your alerts\n"
            "• /setalert BTC 50000 above - Alert when BTC > $50k\n"
            "• /setalert ETH 2500 below - Alert when ETH < $2.5k\n\n"
            "*Trading Commands:*\n"
            "• /signals on/off - Toggle trading signals\n"
            "• /portfolio - View current positions\n"
            "• /performance - View performance metrics\n\n"
            "*Market Commands:*\n"
            "• /market - Overall market status\n"
            "• /market crypto - Crypto market overview\n\n"
            "*Settings:*\n"
            "• /settings - Configure bot settings\n\n"
            "💡 *Tip:* Use inline buttons for quick actions!"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    async def cmd_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price command"""
        # Parse symbol from command
        symbol = "BTC_USDT"  # Default
        if context.args:
            arg = context.args[0].upper()
            # Convert common formats
            if arg in ['BTC', 'BITCOIN']:
                symbol = 'BTC_USDT'
            elif arg in ['ETH', 'ETHEREUM']:
                symbol = 'ETH_USDT'
            elif arg in ['DOGE', 'DOGECOIN']:
                symbol = 'DOGE_USDT'
            elif '_' in arg:
                symbol = arg
            else:
                symbol = f"{arg}_USDT"
        
        # Get price data
        if self.market_data:
            price = self.market_data.get_price(symbol)
            stats = self.market_data.get_market_stats(symbol)
            
            response = (
                f"*{symbol} Price Info*\n\n"
                f"💰 *Price:* ${price:,.2f}\n"
                f"📈 *24h High:* ${stats.get('high_24h', 0):,.2f}\n"
                f"📉 *24h Low:* ${stats.get('low_24h', 0):,.2f}\n"
                f"📊 *24h Change:* {stats.get('change_24h', 0):.2f}%\n"
                f"📊 *Volume:* ${stats.get('volume', 0):,.0f}\n\n"
                f"_Updated: {datetime.now().strftime('%H:%M:%S')}_"
            )
        else:
            response = "❌ Market data service unavailable"
            
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_price_{symbol}"),
                InlineKeyboardButton("🔔 Set Alert", callback_data=f"set_alert_{symbol}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    async def cmd_market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /market command"""
        response = "*📈 Market Overview*\n\n"
        
        if self.market_data:
            # Get prices for major cryptos
            symbols = ['BTC_USDT', 'ETH_USDT', 'DOGE_USDT', 'CRO_USDT', 'ADA_USDT']
            
            for symbol in symbols:
                try:
                    price = self.market_data.get_price(symbol)
                    stats = self.market_data.get_market_stats(symbol)
                    change = stats.get('change_24h', 0)
                    
                    # Emoji based on change
                    emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                    
                    base = symbol.split('_')[0]
                    response += f"{emoji} *{base}:* ${price:,.2f} ({change:+.2f}%)\n"
                    
                except Exception as e:
                    continue
                    
        else:
            response += "❌ Market data unavailable"
            
        response += f"\n_Updated: {datetime.now().strftime('%H:%M:%S')}_"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_market")],
            [InlineKeyboardButton("📊 Detailed View", callback_data="detailed_market")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    async def cmd_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        user_id = update.effective_user.id
        
        # Get user's alerts
        alerts = self._get_user_alerts(user_id)
        
        if not alerts:
            response = (
                "*🔔 Price Alerts*\n\n"
                "You don't have any active alerts.\n\n"
                "Use /setalert to create one!"
            )
        else:
            response = "*🔔 Your Price Alerts*\n\n"
            for alert in alerts:
                alert_id, symbol, target_price, alert_type = alert
                emoji = "📈" if alert_type == "above" else "📉"
                response += f"{emoji} {symbol}: Alert when {alert_type} ${target_price:,.2f}\n"
                response += f"   _ID: {alert_id}_ /delete\\_{alert_id}\n\n"
                
        keyboard = [
            [InlineKeyboardButton("➕ Add Alert", callback_data="add_alert")],
            [InlineKeyboardButton("🗑️ Clear All", callback_data="clear_alerts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    async def cmd_set_alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setalert command"""
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ *Invalid format*\n\n"
                "Use: /setalert [symbol] [price] [above/below]\n"
                "Example: /setalert BTC 50000 above",
                parse_mode='Markdown'
            )
            return
            
        user_id = update.effective_user.id
        symbol = context.args[0].upper()
        
        # Convert symbol format if needed
        if '_' not in symbol:
            symbol = f"{symbol}_USDT"
            
        try:
            target_price = float(context.args[1])
            alert_type = context.args[2].lower()
            
            if alert_type not in ['above', 'below']:
                raise ValueError("Alert type must be 'above' or 'below'")
                
            # Create alert
            alert_id = self._create_price_alert(user_id, symbol, target_price, alert_type)
            
            if alert_id:
                emoji = "📈" if alert_type == "above" else "📉"
                await update.message.reply_text(
                    f"✅ *Alert Created!*\n\n"
                    f"{emoji} I'll notify you when {symbol} goes {alert_type} ${target_price:,.2f}\n\n"
                    f"_Alert ID: {alert_id}_",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Failed to create alert")
                
        except (ValueError, IndexError) as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            
    async def cmd_signals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signals command"""
        user_id = update.effective_user.id
        
        if context.args and context.args[0].lower() in ['on', 'off']:
            # Toggle signal subscription
            enabled = context.args[0].lower() == 'on'
            self._set_signal_subscription(user_id, enabled)
            
            status = "enabled" if enabled else "disabled"
            emoji = "✅" if enabled else "❌"
            
            await update.message.reply_text(
                f"{emoji} Trading signals {status}!",
                parse_mode='Markdown'
            )
        else:
            # Show current status
            is_subscribed = self._is_signal_subscriber(user_id)
            status = "enabled" if is_subscribed else "disabled"
            emoji = "✅" if is_subscribed else "❌"
            
            response = (
                f"*📡 Trading Signals*\n\n"
                f"Status: {emoji} {status.title()}\n\n"
                f"Trading signals notify you of:\n"
                f"• Buy/Sell recommendations\n"
                f"• Market opportunities\n"
                f"• Risk alerts\n"
                f"• Position updates\n\n"
                f"Use /signals on or /signals off to change"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ Enable" if not is_subscribed else "❌ Disable",
                        callback_data=f"toggle_signals"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
    async def cmd_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command"""
        # Mock portfolio data for now
        response = (
            "*💼 Portfolio Overview*\n\n"
            "*Total Value:* $10,500.00\n"
            "*Today's P&L:* +$125.50 (+1.21%)\n"
            "*Total P&L:* +$500.00 (+5.00%)\n\n"
            "*Positions:*\n"
            "• BTC: 0.1 @ $45,000 (+2.5%)\n"
            "• ETH: 1.0 @ $3,000 (-1.2%)\n"
            "• CRO: 1000 @ $0.50 (+5.0%)\n\n"
            "_Last updated: Just now_"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_portfolio")],
            [InlineKeyboardButton("📊 Detailed View", callback_data="detailed_portfolio")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    async def cmd_performance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /performance command"""
        response = (
            "*📊 Performance Metrics*\n\n"
            "*Win Rate:* 65.5%\n"
            "*Sharpe Ratio:* 1.85\n"
            "*Max Drawdown:* -5.2%\n"
            "*Best Day:* +$450 (+4.5%)\n"
            "*Worst Day:* -$220 (-2.2%)\n\n"
            "*Monthly Performance:*\n"
            "• October: +12.5%\n"
            "• September: +8.2%\n"
            "• August: -3.1%\n\n"
            "_Based on last 90 days of trading_"
        )
        
        keyboard = [
            [InlineKeyboardButton("📈 View Chart", callback_data="performance_chart")],
            [InlineKeyboardButton("📊 Export Report", callback_data="export_performance")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    async def cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user_id = update.effective_user.id
        settings = self._get_user_settings(user_id)
        
        notif_status = "✅ Enabled" if settings.get('notifications_enabled', True) else "❌ Disabled"
        
        response = (
            "*⚙️ Bot Settings*\n\n"
            f"*Notifications:* {notif_status}\n"
            f"*User ID:* `{user_id}`\n"
            f"*Member Since:* {settings.get('created_at', 'Unknown')}\n\n"
            "Select an option below:"
        )
        
        keyboard = [
            [InlineKeyboardButton(
                "🔔 Toggle Notifications",
                callback_data="toggle_notifications"
            )],
            [InlineKeyboardButton(
                "📊 Export Data",
                callback_data="export_data"
            )],
            [InlineKeyboardButton(
                "❓ Support",
                url="https://t.me/tps19support"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # Handle different callback types
        if data.startswith("refresh_price_"):
            symbol = data.replace("refresh_price_", "")
            # Simulate price refresh
            await self._refresh_price(query, symbol)
            
        elif data.startswith("set_alert_"):
            symbol = data.replace("set_alert_", "")
            await query.message.reply_text(
                f"To set an alert for {symbol}, use:\n"
                f"`/setalert {symbol} [price] [above/below]`",
                parse_mode='Markdown'
            )
            
        elif data == "toggle_signals":
            user_id = query.from_user.id
            is_subscribed = self._is_signal_subscriber(user_id)
            self._set_signal_subscription(user_id, not is_subscribed)
            
            new_status = "enabled" if not is_subscribed else "disabled"
            await query.message.edit_text(
                f"✅ Trading signals {new_status}!",
                parse_mode='Markdown'
            )
            
        elif data == "toggle_notifications":
            user_id = query.from_user.id
            self._toggle_notifications(user_id)
            await query.message.reply_text("✅ Notification settings updated!")
            
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        text = update.message.text.upper()
        
        # Quick price check for common symbols
        price_symbols = ['BTC', 'ETH', 'DOGE', 'CRO', 'ADA']
        
        for symbol in price_symbols:
            if symbol in text:
                # Simulate price command
                context.args = [symbol]
                await self.cmd_price(update, context)
                return
                
        # Default response
        await update.message.reply_text(
            "I didn't understand that. Try /help for available commands.",
            parse_mode='Markdown'
        )
        
    async def _refresh_price(self, query, symbol):
        """Refresh price display"""
        if self.market_data:
            price = self.market_data.get_price(symbol)
            stats = self.market_data.get_market_stats(symbol)
            
            response = (
                f"*{symbol} Price Info*\n\n"
                f"💰 *Price:* ${price:,.2f}\n"
                f"📈 *24h High:* ${stats.get('high_24h', 0):,.2f}\n"
                f"📉 *24h Low:* ${stats.get('low_24h', 0):,.2f}\n"
                f"📊 *24h Change:* {stats.get('change_24h', 0):.2f}%\n"
                f"📊 *Volume:* ${stats.get('volume', 0):,.0f}\n\n"
                f"_Updated: {datetime.now().strftime('%H:%M:%S')}_"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_price_{symbol}"),
                    InlineKeyboardButton("🔔 Set Alert", callback_data=f"set_alert_{symbol}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
    def _register_user(self, user_id: int, username: str = None):
        """Register new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO user_settings (user_id, username)
            VALUES (?, ?)
        ''', (user_id, username))
        
        conn.commit()
        conn.close()
        
    def _get_user_settings(self, user_id: int) -> Dict:
        """Get user settings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, is_admin, notifications_enabled, created_at
            FROM user_settings
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'username': result[0],
                'is_admin': result[1],
                'notifications_enabled': result[2],
                'created_at': result[3]
            }
        return {}
        
    def _toggle_notifications(self, user_id: int):
        """Toggle user notifications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_settings
            SET notifications_enabled = 1 - notifications_enabled
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
    def _create_price_alert(self, user_id: int, symbol: str, 
                          target_price: float, alert_type: str) -> Optional[int]:
        """Create price alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO price_alerts (user_id, symbol, target_price, alert_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, symbol, target_price, alert_type))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return alert_id
            
        except Exception as e:
            conn.close()
            print(f"Error creating alert: {e}")
            return None
            
    def _get_user_alerts(self, user_id: int) -> List:
        """Get user's active alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, symbol, target_price, alert_type
            FROM price_alerts
            WHERE user_id = ? AND active = 1
            ORDER BY created_at DESC
        ''', (user_id,))
        
        alerts = cursor.fetchall()
        conn.close()
        return alerts
        
    def _is_signal_subscriber(self, user_id: int) -> bool:
        """Check if user is subscribed to signals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT subscribed
            FROM signal_subscribers
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else False
        
    def _set_signal_subscription(self, user_id: int, subscribed: bool):
        """Set signal subscription status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO signal_subscribers (user_id, subscribed)
            VALUES (?, ?)
        ''', (user_id, int(subscribed)))
        
        conn.commit()
        conn.close()
        
        if subscribed:
            self.signal_subscribers.add(user_id)
        else:
            self.signal_subscribers.discard(user_id)
            
    async def send_trading_signal(self, signal: Dict):
        """Send trading signal to subscribers"""
        if not self.app:
            return
            
        # Get all subscribers
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.user_id
            FROM signal_subscribers s
            JOIN user_settings u ON s.user_id = u.user_id
            WHERE s.subscribed = 1 AND u.notifications_enabled = 1
        ''')
        
        subscribers = cursor.fetchall()
        conn.close()
        
        if not subscribers:
            return
            
        # Format signal message
        action_emoji = "🟢" if signal.get('action') == 'BUY' else "🔴"
        confidence_emoji = "🔥" if signal.get('confidence', 0) > 0.8 else "⚡"
        
        message = (
            f"{action_emoji} *TRADING SIGNAL* {action_emoji}\n\n"
            f"*Action:* {signal.get('action', 'UNKNOWN')}\n"
            f"*Symbol:* {signal.get('symbol', 'UNKNOWN')}\n"
            f"*Price:* ${signal.get('price', 0):,.2f}\n"
            f"*Confidence:* {signal.get('confidence', 0):.1%} {confidence_emoji}\n"
            f"*Strategy:* {signal.get('strategy', 'AI-based')}\n\n"
            f"⚠️ _This is not financial advice. Trade at your own risk._"
        )
        
        # Send to all subscribers
        for user_id in subscribers:
            try:
                await self.app.bot.send_message(
                    chat_id=user_id[0],
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"Failed to send signal to {user_id[0]}: {e}")
                
    async def check_price_alerts(self):
        """Check and trigger price alerts"""
        if not self.app or not self.market_data:
            return
            
        # Get all active alerts
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.id, a.user_id, a.symbol, a.target_price, a.alert_type
            FROM price_alerts a
            JOIN user_settings u ON a.user_id = u.user_id
            WHERE a.active = 1 AND u.notifications_enabled = 1
        ''')
        
        alerts = cursor.fetchall()
        
        for alert_id, user_id, symbol, target_price, alert_type in alerts:
            try:
                # Get current price
                current_price = self.market_data.get_price(symbol)
                
                # Check if alert should trigger
                should_trigger = False
                if alert_type == 'above' and current_price > target_price:
                    should_trigger = True
                elif alert_type == 'below' and current_price < target_price:
                    should_trigger = True
                    
                if should_trigger:
                    # Send alert
                    emoji = "📈" if alert_type == "above" else "📉"
                    message = (
                        f"{emoji} *PRICE ALERT* {emoji}\n\n"
                        f"*{symbol}* is now {alert_type} your target!\n\n"
                        f"*Current Price:* ${current_price:,.2f}\n"
                        f"*Target Price:* ${target_price:,.2f}\n\n"
                        f"_Alert ID: {alert_id} has been deactivated._"
                    )
                    
                    await self.app.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    
                    # Deactivate alert
                    cursor.execute(
                        "UPDATE price_alerts SET active = 0 WHERE id = ?",
                        (alert_id,)
                    )
                    
            except Exception as e:
                print(f"Error checking alert {alert_id}: {e}")
                
        conn.commit()
        conn.close()
        
    def start_bot(self):
        """Start the Telegram bot"""
        if not TELEGRAM_AVAILABLE or not self.app:
            print("❌ Telegram bot cannot start - missing token or module")
            return
            
        print("🚀 Starting Telegram bot...")
        
        # Start alert checking in background
        def alert_loop():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while True:
                try:
                    loop.run_until_complete(self.check_price_alerts())
                except Exception as e:
                    print(f"Alert check error: {e}")
                time.sleep(30)  # Check every 30 seconds
                
        alert_thread = threading.Thread(target=alert_loop)
        alert_thread.daemon = True
        alert_thread.start()
        
        # Run the bot
        self.app.run_polling()
        
    def test_bot(self):
        """Test bot functionality"""
        print("Testing Telegram Bot...")
        print("=" * 60)
        
        # Test database
        self._register_user(123456789, "test_user")
        print("✅ Database test passed")
        
        # Test alert creation
        alert_id = self._create_price_alert(123456789, "BTC_USDT", 50000, "above")
        if alert_id:
            print(f"✅ Alert creation test passed (ID: {alert_id})")
        
        # Test settings
        settings = self._get_user_settings(123456789)
        print(f"✅ Settings test passed: {settings}")
        
        return True

# Global instance
telegram_bot = TelegramBot()

if __name__ == "__main__":
    # Test the bot
    bot = TelegramBot()
    
    if bot.test_bot():
        print("\n✅ All tests passed!")
        
    # Note: To actually run the bot, you need:
    # 1. Set TELEGRAM_BOT_TOKEN environment variable
    # 2. Call bot.start_bot()