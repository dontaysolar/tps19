#!/usr/bin/env python3
"""
Enhanced Telegram Notifications
Sends detailed alerts for EVERY trade
"""

import os
import sys
from datetime import datetime
import requests

class EnhancedNotifications:
    """Sends detailed trading notifications via Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '7289126201:AAHaWTLKxpddtbJ9oa4hGdvKaq0mypqU75Y')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '7517400013')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, text, parse_mode='Markdown'):
        """Send message to Telegram"""
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
            print(f"Telegram error: {e}")
            return None
    
    def trade_entry_alert(self, symbol, side, amount, price, sentiment=None, strategy=None):
        """Alert when entering a trade"""
        emoji = "🟢" if side == "buy" else "🔴"
        
        message = f"""
{emoji} *TRADE ENTRY*

*Symbol:* {symbol}
*Side:* {side.upper()}
*Amount:* {amount:.6f}
*Price:* ${price:.2f}
*Value:* ${amount * price:.2f}
"""
        
        if sentiment is not None:
            sentiment_emoji = "😊" if sentiment > 0 else "😟" if sentiment < 0 else "😐"
            message += f"*Sentiment:* {sentiment_emoji} {sentiment:+.2f}\n"
        
        if strategy:
            message += f"*Strategy:* {strategy}\n"
        
        message += f"\n*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.send_message(message)
    
    def trade_exit_alert(self, symbol, side, amount, entry_price, exit_price, profit, profit_pct, reason='MANUAL'):
        """Alert when exiting a trade"""
        profit_emoji = "💰" if profit > 0 else "💸" if profit < 0 else "💵"
        outcome_emoji = "✅" if profit > 0 else "❌" if profit < 0 else "➖"
        
        message = f"""
{outcome_emoji} *TRADE EXIT*

*Symbol:* {symbol}
*Side:* {side.upper()}
*Amount:* {amount:.6f}

*Entry:* ${entry_price:.2f}
*Exit:* ${exit_price:.2f}
*P&L:* {profit_emoji} ${profit:.2f} ({profit_pct:+.2f}%)

*Reason:* {reason}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.send_message(message)
    
    def stop_loss_alert(self, symbol, entry, exit, loss):
        """Alert when stop-loss is hit"""
        message = f"""
🛑 *STOP-LOSS HIT*

*Symbol:* {symbol}
*Entry:* ${entry:.2f}
*Exit:* ${exit:.2f}
*Loss:* -${abs(loss):.2f}

*Protection:* Capital preserved ✅
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.send_message(message)
    
    def take_profit_alert(self, symbol, entry, exit, profit):
        """Alert when take-profit is hit"""
        message = f"""
🎯 *TAKE-PROFIT HIT*

*Symbol:* {symbol}
*Entry:* ${entry:.2f}
*Exit:* ${exit:.2f}
*Profit:* +${profit:.2f}

*Status:* Target achieved! 🎉
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.send_message(message)
    
    def daily_summary(self, trades_count, wins, losses, total_profit, win_rate):
        """Send daily performance summary"""
        message = f"""
📊 *DAILY SUMMARY*

*Total Trades:* {trades_count}
*Wins:* {wins} ✅
*Losses:* {losses} ❌
*Win Rate:* {win_rate:.1f}%

*Total P&L:* ${total_profit:+.2f}

*Date:* {datetime.now().strftime('%Y-%m-%d')}
"""
        
        self.send_message(message)
    
    def error_alert(self, error_type, details):
        """Alert on system errors"""
        message = f"""
⚠️ *SYSTEM ERROR*

*Type:* {error_type}
*Details:* {details}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*Action:* Check logs immediately
"""
        
        self.send_message(message)
    
    def sentiment_alert(self, coin, score, signal):
        """Alert on sentiment changes"""
        emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
        
        message = f"""
🧠 *SENTIMENT UPDATE*

{emoji} *{coin}*
*Score:* {score:+.2f}
*Signal:* {signal}

*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.send_message(message)

if __name__ == '__main__':
    # Test notifications
    notif = EnhancedNotifications()
    
    # Test trade entry
    notif.trade_entry_alert('BTC/USDT', 'buy', 0.001, 50000, sentiment=0.5, strategy='Sentiment Breakout')
    
    # Test trade exit
    notif.trade_exit_alert('BTC/USDT', 'sell', 0.001, 50000, 51000, 1.0, 2.0, 'TAKE_PROFIT')
    
    # Test daily summary
    notif.daily_summary(10, 7, 3, 5.25, 70.0)
