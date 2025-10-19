#!/usr/bin/env python3
"""Slack Notifier - Team notifications via Slack"""
from datetime import datetime
from typing import Dict

class SlackNotifierBot:
    def __init__(self):
        self.name = "Slack_Notifier"
        self.version = "1.0.0"
        self.enabled = True
        
        self.webhook_url = None
        self.channel = None
        
        self.metrics = {'messages_sent': 0, 'errors': 0}
    
    def configure(self, webhook_url: str, channel: str = '#trading-alerts'):
        """Configure Slack webhook"""
        self.webhook_url = webhook_url
        self.channel = channel
    
    def send_message(self, text: str, blocks: list = None) -> Dict:
        """Send Slack message"""
        if not self.webhook_url:
            return {'error': 'Slack not configured', 'sent': False}
        
        payload = {
            'channel': self.channel,
            'text': text,
            'blocks': blocks or []
        }
        
        # Simulate sending
        try:
            self.metrics['messages_sent'] += 1
            return {
                'sent': True,
                'channel': self.channel,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.metrics['errors'] += 1
            return {'sent': False, 'error': str(e)}
    
    def send_trade_summary(self, summary: Dict) -> Dict:
        """Send formatted trade summary"""
        text = f"*Trading Summary* 📊\n" \
               f"Total P&L: ${summary.get('pnl', 0):,.2f}\n" \
               f"Trades: {summary.get('trades', 0)}\n" \
               f"Win Rate: {summary.get('win_rate', 0):.1f}%"
        
        return self.send_message(text)
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'configured': bool(self.webhook_url),
            'channel': self.channel,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = SlackNotifierBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
