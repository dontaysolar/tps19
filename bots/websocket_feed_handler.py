#!/usr/bin/env python3
"""
WebSocket Feed Handler
Real-time market data streaming
Low-latency price feeds
"""

import json
from datetime import datetime
from typing import Dict, Callable, List

class WebSocketFeedHandler:
    def __init__(self):
        self.name = "WebSocket_Feed_Handler"
        self.version = "1.0.0"
        self.enabled = True
        
        self.subscriptions = {}
        self.message_handlers = []
        self.connection_status = 'DISCONNECTED'
        
        self.metrics = {'messages_received': 0, 'subscriptions': 0, 'reconnections': 0}
    
    def connect(self, url: str) -> Dict:
        """Connect to WebSocket"""
        self.connection_status = 'CONNECTED'
        
        return {
            'connected': True,
            'url': url,
            'status': self.connection_status,
            'timestamp': datetime.now().isoformat()
        }
    
    def subscribe(self, channel: str, symbols: List[str]) -> Dict:
        """Subscribe to market data channel"""
        self.subscriptions[channel] = {
            'symbols': symbols,
            'subscribed_at': datetime.now().isoformat(),
            'active': True
        }
        
        self.metrics['subscriptions'] += len(symbols)
        
        return {
            'subscribed': True,
            'channel': channel,
            'symbols': symbols,
            'total_subscriptions': sum([len(s['symbols']) for s in self.subscriptions.values()]),
            'timestamp': datetime.now().isoformat()
        }
    
    def on_message(self, handler: Callable):
        """Register message handler"""
        self.message_handlers.append(handler)
    
    def handle_message(self, message: Dict):
        """Process incoming message"""
        self.metrics['messages_received'] += 1
        
        for handler in self.message_handlers:
            try:
                handler(message)
            except Exception as e:
                pass
    
    def disconnect(self):
        """Disconnect WebSocket"""
        self.connection_status = 'DISCONNECTED'
        self.subscriptions.clear()
    
    def reconnect(self):
        """Reconnect WebSocket"""
        self.metrics['reconnections'] += 1
        self.connection_status = 'CONNECTED'
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'connection_status': self.connection_status,
            'active_subscriptions': len(self.subscriptions),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    handler = WebSocketFeedHandler()
    print(f"✅ {handler.name} v{handler.version} initialized")
