#!/usr/bin/env python3
"""Discord Notifier - Send alerts via Discord webhooks"""
from datetime import datetime
from typing import Dict

class DiscordNotifierBot:
    def __init__(self):
        self.name = "Discord_Notifier"
        self.version = "1.0.0"
        self.enabled = True
        
        self.webhook_url = None
        self.metrics = {'messages_sent': 0, 'errors': 0}
    
    def configure(self, webhook_url: str):
        """Configure Discord webhook"""
        self.webhook_url = webhook_url
    
    def send_embed(self, title: str, description: str, color: int = 0x00ff00, fields: list = None) -> Dict:
        """Send rich embed message"""
        if not self.webhook_url:
            return {'error': 'Discord not configured', 'sent': False}
        
        embed = {
            'title': title,
            'description': description,
            'color': color,
            'fields': fields or [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Simulate sending (would use requests library)
        try:
            self.metrics['messages_sent'] += 1
            return {
                'sent': True,
                'embed': embed,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.metrics['errors'] += 1
            return {'sent': False, 'error': str(e)}
    
    def send_trade_alert(self, trade_data: Dict) -> Dict:
        """Send formatted trade alert"""
        side = trade_data.get('side', 'UNKNOWN')
        color = 0x00ff00 if side == 'BUY' else 0xff0000
        
        fields = [
            {'name': 'Symbol', 'value': trade_data.get('symbol', 'UNKNOWN'), 'inline': True},
            {'name': 'Side', 'value': side, 'inline': True},
            {'name': 'Price', 'value': f"${trade_data.get('price', 0):,.2f}", 'inline': True},
            {'name': 'Quantity', 'value': f"{trade_data.get('quantity', 0):.8f}", 'inline': True},
            {'name': 'Total Value', 'value': f"${trade_data.get('value', 0):,.2f}", 'inline': True}
        ]
        
        return self.send_embed(
            title="🔔 Trade Executed",
            description=f"{side} order filled for {trade_data.get('symbol')}",
            color=color,
            fields=fields
        )
    
    def send_pnl_update(self, pnl_data: Dict) -> Dict:
        """Send P&L update"""
        pnl = pnl_data.get('total_pnl', 0)
        color = 0x00ff00 if pnl > 0 else 0xff0000
        
        fields = [
            {'name': 'Total P&L', 'value': f"${pnl:,.2f}", 'inline': True},
            {'name': 'Win Rate', 'value': f"{pnl_data.get('win_rate', 0):.1f}%", 'inline': True},
            {'name': 'Total Trades', 'value': str(pnl_data.get('total_trades', 0)), 'inline': True}
        ]
        
        return self.send_embed(
            title="📊 P&L Update",
            description="Daily performance summary",
            color=color,
            fields=fields
        )
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'configured': bool(self.webhook_url),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = DiscordNotifierBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
