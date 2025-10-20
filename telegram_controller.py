#!/usr/bin/env python3
"""
TPS19 TELEGRAM CONTROLLER - Full Bot Control via Chat
Control your trading bot with simple messages!
"""

import os
import sys
import json
import time
import requests
import threading
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
STATUS_FILE = 'data/bot_status.json'
TELEGRAM_CONFIGURED = bool(BOT_TOKEN and CHAT_ID)

class TelegramController:
    """Simple Telegram bot controller"""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.running = True
        self.last_update_id = 0
        self.status = self.load_status()
        
    def load_status(self):
        """Load bot status from file"""
        try:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            'trading_enabled': True,
            'max_position_size': 1.0,  # $1 max per trade for $3 balance
            'stop_loss_percent': 2.0,   # 2% stop loss
            'take_profit_percent': 5.0, # 5% take profit
            'ai_enabled': True,
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit': 0.0,
            'balance': 3.0,
            'last_update': datetime.now().isoformat()
        }
    
    def save_status(self):
        """Save bot status to file"""
        try:
            os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
            self.status['last_update'] = datetime.now().isoformat()
            with open(STATUS_FILE, 'w') as f:
                json.dump(self.status, f, indent=2)
        except Exception as e:
            print(f"Error saving status: {e}")
    
    def send_message(self, text, parse_mode='Markdown'):
        """Send message to Telegram"""
        if not TELEGRAM_CONFIGURED:
            return None
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def get_updates(self):
        """Get new messages from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30
            }
            response = requests.get(url, params=params, timeout=35)
            return response.json()
        except Exception as e:
            print(f"Error getting updates: {e}")
            return None
    
    def handle_command(self, message):
        """Handle incoming commands"""
        text = message.get('text', '').strip().lower()
        chat_id = message['chat']['id']
        
        # Only respond to authorized chat
        if str(chat_id) != str(self.chat_id):
            return
        
        # Command routing
        if text in ['/start', '/help', 'help', 'commands']:
            self.cmd_help()
        elif text in ['/status', 'status']:
            self.cmd_status()
        elif text in ['/balance', 'balance']:
            self.cmd_balance()
        elif text in ['start trading', 'start', 'enable']:
            self.cmd_start_trading()
        elif text in ['stop trading', 'stop', 'disable']:
            self.cmd_stop_trading()
        elif text.startswith('position size '):
            self.cmd_position_size(text)
        elif text.startswith('stop loss '):
            self.cmd_stop_loss(text)
        elif text.startswith('take profit '):
            self.cmd_take_profit(text)
        elif text in ['ai on', 'enable ai']:
            self.cmd_ai_toggle(True)
        elif text in ['ai off', 'disable ai']:
            self.cmd_ai_toggle(False)
        elif text in ['/stats', 'stats', 'statistics']:
            self.cmd_stats()
        elif text in ['mode paper', 'mode real']:
            self.cmd_mode(text)
        elif text in ['paper on', 'paper off', 'paper status']:
            self.cmd_paper(text)
        elif text in ['transformer status', 'kelly status']:
            self.cmd_models(text)
        elif text in ['reset', 'reset stats']:
            self.cmd_reset_stats()
        else:
            self.send_message(
                "❓ Unknown command\n\n"
                "Try: *help* or */commands* to see available commands"
            )
    
    def cmd_help(self):
        """Show help message"""
        help_text = """
🤖 *TPS19 Bot Commands*

📊 *Status & Info:*
• `status` - Current bot status
• `balance` - Account balance
• `stats` - Trading statistics

⚙️ *Trading Controls:*
• `start trading` - Enable trading
• `stop trading` - Disable trading
• `position size X` - Set max $ per trade
• `stop loss X` - Set stop loss %
• `take profit X` - Set take profit %

🧠 *AI Controls:*
• `ai on` - Enable AI predictions
• `ai off` - Disable AI predictions

🧪 *Paper Trading:*
• `paper on` - Enable paper trading
• `paper off` - Disable paper trading
• `paper status` - Show paper trading status

🔎 *Model Status:*
• `transformer status` - Last transformer direction/confidence
• `kelly status` - Last Kelly position suggestion

🛠️ *Mode & Config:*
• `mode paper` - Switch to paper mode (requires restart)
• `mode real` - Switch to real mode (requires restart)

🔧 *Other:*
• `reset stats` - Reset statistics
• `help` - Show this message

💡 *Examples:*
• `position size 0.5` (max $0.50 per trade)
• `stop loss 3` (3% stop loss)
• `take profit 10` (10% profit target)

_Reply with any command to control your bot!_
"""
        self.send_message(help_text)

    def cmd_mode(self, text):
        mode = 'paper' if 'paper' in text else 'real'
        try:
            os.environ['TRADING_MODE'] = mode
            self.send_message(f"🛠️ TRADING_MODE set to: {mode}\n\nRestart the bot to apply.")
        except Exception:
            self.send_message("❌ Failed to set mode")
    
    def cmd_status(self):
        """Show bot status"""
        status_emoji = "🟢" if self.status['trading_enabled'] else "🔴"
        ai_emoji = "🧠" if self.status['ai_enabled'] else "💤"
        
        text = f"""
{status_emoji} *Bot Status*

Trading: {'✅ ACTIVE' if self.status['trading_enabled'] else '🛑 STOPPED'}
AI Models: {ai_emoji} {'ON' if self.status['ai_enabled'] else 'OFF'}

⚙️ *Settings:*
• Max Position: ${self.status['max_position_size']:.2f}
• Stop Loss: {self.status['stop_loss_percent']}%
• Take Profit: {self.status['take_profit_percent']}%

💰 Balance: ${self.status['balance']:.2f}
📈 Total Trades: {self.status['total_trades']}

_Last updated: {self.status.get('last_update', 'Never')}_
"""
        self.send_message(text)

    def cmd_paper(self, text):
        """Toggle/show paper trading status (file-based flag)."""
        flag_path = 'data/paper_trading.enabled'
        os.makedirs('data', exist_ok=True)
        if text == 'paper on':
            with open(flag_path, 'w') as f:
                f.write('1')
            self.send_message("🧪 Paper trading: ENABLED")
        elif text == 'paper off':
            if os.path.exists(flag_path):
                os.remove(flag_path)
            self.send_message("🧪 Paper trading: DISABLED")
        else:
            enabled = os.path.exists(flag_path)
            self.send_message(f"🧪 Paper trading status: {'ENABLED' if enabled else 'DISABLED'}")

    def cmd_models(self, text):
        """Show last transformer and Kelly calculations from system status file."""
        status_file = 'data/system_status.json'
        try:
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    s = json.load(f)
            else:
                s = {}
        except Exception:
            s = {}

        if text == 'transformer status':
            t = s.get('transformer', {})
            self.send_message(
                f"🔎 Transformer\n\nDirection: {t.get('direction', 'UNKNOWN')}\nConfidence: {t.get('confidence', 0):.2f}"
            )
        else:
            k = s.get('kelly', {})
            self.send_message(
                f"💰 Kelly Sizing\n\nPosition Value: ${k.get('position_value', 0):.2f}\nWin Rate Proxy: {k.get('win_rate', 0):.2f}"
            )
    
    def cmd_balance(self):
        """Show balance info"""
        profit = self.status['total_profit']
        profit_emoji = "📈" if profit >= 0 else "📉"
        
        text = f"""
💰 *Account Balance*

Current: ${self.status['balance']:.2f}
Total P/L: {profit_emoji} ${profit:.2f}

📊 *Risk Settings:*
• Max per trade: ${self.status['max_position_size']:.2f}
• Risk per trade: {self.status['max_position_size'] / self.status['balance'] * 100:.1f}% of balance

💡 _Tip: Keep position size small!_
_For $3 balance, use $0.50-$1.00 max_
"""
        self.send_message(text)
    
    def cmd_start_trading(self):
        """Enable trading"""
        self.status['trading_enabled'] = True
        self.save_status()
        self.send_message(
            "✅ *Trading ENABLED*\n\n"
            "Bot will now execute trades automatically.\n"
            "_Reply 'stop trading' to pause_"
        )
    
    def cmd_stop_trading(self):
        """Disable trading"""
        self.status['trading_enabled'] = False
        self.save_status()
        self.send_message(
            "🛑 *Trading STOPPED*\n\n"
            "Bot will not execute new trades.\n"
            "_Reply 'start trading' to resume_"
        )
    
    def cmd_position_size(self, text):
        """Set position size"""
        try:
            size = float(text.split()[-1])
            if size <= 0 or size > self.status['balance']:
                self.send_message(
                    f"❌ Invalid size: ${size:.2f}\n\n"
                    f"Must be between $0.01 and ${self.status['balance']:.2f}"
                )
                return
            
            self.status['max_position_size'] = size
            self.save_status()
            
            risk_pct = size / self.status['balance'] * 100
            self.send_message(
                f"✅ *Position size updated*\n\n"
                f"Max per trade: ${size:.2f}\n"
                f"Risk per trade: {risk_pct:.1f}% of balance\n\n"
                f"{'⚠️ High risk!' if risk_pct > 30 else '✅ Safe risk level'}"
            )
        except:
            self.send_message(
                "❌ Invalid format\n\n"
                "Use: `position size 1.0`"
            )
    
    def cmd_stop_loss(self, text):
        """Set stop loss"""
        try:
            pct = float(text.split()[-1])
            if pct <= 0 or pct > 20:
                self.send_message("❌ Stop loss must be 0.1% - 20%")
                return
            
            self.status['stop_loss_percent'] = pct
            self.save_status()
            self.send_message(
                f"✅ *Stop loss set to {pct}%*\n\n"
                f"Trades will close if price drops {pct}%"
            )
        except:
            self.send_message(
                "❌ Invalid format\n\n"
                "Use: `stop loss 2.0`"
            )
    
    def cmd_take_profit(self, text):
        """Set take profit"""
        try:
            pct = float(text.split()[-1])
            if pct <= 0 or pct > 100:
                self.send_message("❌ Take profit must be 0.1% - 100%")
                return
            
            self.status['take_profit_percent'] = pct
            self.save_status()
            self.send_message(
                f"✅ *Take profit set to {pct}%*\n\n"
                f"Trades will close if price rises {pct}%"
            )
        except:
            self.send_message(
                "❌ Invalid format\n\n"
                "Use: `take profit 5.0`"
            )
    
    def cmd_ai_toggle(self, enabled):
        """Toggle AI"""
        self.status['ai_enabled'] = enabled
        self.save_status()
        
        if enabled:
            self.send_message(
                "🧠 *AI Models ENABLED*\n\n"
                "Using LSTM predictions and self-learning"
            )
        else:
            self.send_message(
                "💤 *AI Models DISABLED*\n\n"
                "Using basic trading logic only"
            )
    
    def cmd_stats(self):
        """Show statistics"""
        total = self.status['total_trades']
        wins = self.status['winning_trades']
        profit = self.status['total_profit']
        
        win_rate = (wins / total * 100) if total > 0 else 0
        avg_profit = (profit / total) if total > 0 else 0
        
        text = f"""
📊 *Trading Statistics*

Total Trades: {total}
Winning: {wins} ({win_rate:.1f}%)
Losing: {total - wins}

💰 Total P/L: ${profit:.2f}
📈 Avg per trade: ${avg_profit:.2f}

Starting Balance: $3.00
Current Balance: ${self.status['balance']:.2f}
ROI: {((self.status['balance'] - 3.0) / 3.0 * 100):.1f}%

_Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
"""
        self.send_message(text)
    
    def cmd_reset_stats(self):
        """Reset statistics"""
        self.status['total_trades'] = 0
        self.status['winning_trades'] = 0
        self.status['total_profit'] = 0.0
        self.save_status()
        
        self.send_message(
            "♻️ *Statistics Reset*\n\n"
            "All trade counters have been cleared.\n"
            "_Balance unchanged_"
        )
    
    def run(self):
        """Main bot loop"""
        print("🤖 Telegram Controller starting...")
        
        # Send startup message if configured
        if TELEGRAM_CONFIGURED:
            self.send_message(
                "🤖 *TPS19 Bot Online!*\n\n"
                "✅ Ready to receive commands\n\n"
                "_Reply with 'help' to see commands_"
            )
        else:
            print("⚠️ Telegram not configured (TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID missing). Running without messaging.")
        
        while self.running:
            try:
                if not TELEGRAM_CONFIGURED:
                    time.sleep(3)
                    continue
                updates = self.get_updates()
                
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update:
                            self.handle_command(update['message'])
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping Telegram Controller...")
                self.running = False
            except Exception as e:
                print(f"Error in bot loop: {e}")
                time.sleep(5)

if __name__ == '__main__':
    controller = TelegramController()
    controller.run()
