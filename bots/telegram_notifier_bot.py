#!/usr/bin/env python3
"""Telegram Notifier - Send alerts via Telegram"""
from datetime import datetime
from typing import Dict

class TelegramNotifierBot:
    def __init__(self):
        self.name = "Telegram_Notifier"
        self.version = "1.0.0"
        self.enabled = True
        
        self.bot_token = None
        self.chat_id = None
        
        self.metrics = {'messages_sent': 0, 'errors': 0}
    
    def configure(self, bot_token: str, chat_id: str):
        """Configure Telegram credentials"""
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    def send_alert(self, message: str, priority: str = 'NORMAL') -> Dict:
        """Send alert message"""
        if not self.bot_token or not self.chat_id:
            return {'error': 'Telegram not configured', 'sent': False}
        
        # Format message with emoji based on priority
        emoji = '🔔' if priority == 'NORMAL' else '🚨' if priority == 'HIGH' else '⚠️'
        formatted_message = f"{emoji} {message}"
        
        # Simulate sending (would use requests library in production)
        try:
            # requests.post(f"https://api.telegram.org/bot{self.bot_token}/sendMessage", ...)
            self.metrics['messages_sent'] += 1
            
            return {
                'sent': True,
                'message': formatted_message,
                'priority': priority,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.metrics['errors'] += 1
            return {'sent': False, 'error': str(e)}
    
    def send_trade_alert(self, trade_data: Dict) -> Dict:
        """Send formatted trade alert"""
        symbol = trade_data.get('symbol', 'UNKNOWN')
        side = trade_data.get('side', 'UNKNOWN')
        price = trade_data.get('price', 0)
        quantity = trade_data.get('quantity', 0)
        
        message = f"Trade Executed\n" \
                 f"Symbol: {symbol}\n" \
                 f"Side: {side}\n" \
                 f"Price: ${price:,.2f}\n" \
                 f"Quantity: {quantity:.8f}"
        
        return self.send_alert(message, priority='NORMAL')
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'configured': bool(self.bot_token and self.chat_id),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = TelegramNotifierBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
