#!/usr/bin/env python3
"""Webhook Dispatcher - Send events to custom webhooks"""
from datetime import datetime
from typing import Dict, List

class WebhookDispatcherBot:
    def __init__(self):
        self.name = "Webhook_Dispatcher"
        self.version = "1.0.0"
        self.enabled = True
        
        self.webhooks = {}
        self.metrics = {'dispatches': 0, 'errors': 0}
    
    def register_webhook(self, event_type: str, url: str, headers: Dict = None):
        """Register webhook for event type"""
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        
        self.webhooks[event_type].append({
            'url': url,
            'headers': headers or {},
            'registered_at': datetime.now().isoformat()
        })
    
    def dispatch_event(self, event_type: str, payload: Dict) -> Dict:
        """Dispatch event to registered webhooks"""
        if event_type not in self.webhooks:
            return {'dispatched': 0, 'message': 'No webhooks registered for event'}
        
        results = []
        
        for webhook in self.webhooks[event_type]:
            try:
                # Simulate dispatch (would use requests library)
                results.append({
                    'url': webhook['url'],
                    'success': True,
                    'status_code': 200
                })
                self.metrics['dispatches'] += 1
            except Exception as e:
                results.append({
                    'url': webhook['url'],
                    'success': False,
                    'error': str(e)
                })
                self.metrics['errors'] += 1
        
        return {
            'event_type': event_type,
            'dispatched': len(results),
            'successful': sum([1 for r in results if r['success']]),
            'failed': sum([1 for r in results if not r['success']]),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def dispatch_trade_event(self, trade_data: Dict) -> Dict:
        """Dispatch trade execution event"""
        return self.dispatch_event('trade_executed', trade_data)
    
    def dispatch_signal_event(self, signal_data: Dict) -> Dict:
        """Dispatch trading signal event"""
        return self.dispatch_event('signal_generated', signal_data)
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'registered_events': len(self.webhooks),
            'total_webhooks': sum([len(hooks) for hooks in self.webhooks.values()]),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = WebhookDispatcherBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
