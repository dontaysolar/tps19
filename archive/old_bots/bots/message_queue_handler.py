#!/usr/bin/env python3
"""
Message Queue Handler
Event-driven architecture with pub/sub
Asynchronous bot communication
"""

from datetime import datetime
from typing import Dict, List, Callable
import json

class MessageQueueHandler:
    def __init__(self):
        self.name = "Message_Queue_Handler"
        self.version = "1.0.0"
        self.enabled = True
        
        self.queues = {}
        self.subscribers = {}
        self.metrics = {'messages_sent': 0, 'messages_received': 0, 'queues_created': 0}
    
    def create_queue(self, queue_name: str) -> Dict:
        """Create message queue"""
        self.queues[queue_name] = []
        self.subscribers[queue_name] = []
        self.metrics['queues_created'] += 1
        return {'created': True, 'queue': queue_name}
    
    def publish(self, queue_name: str, message: Dict):
        """Publish message to queue"""
        if queue_name not in self.queues:
            self.create_queue(queue_name)
        
        msg = {
            'data': message,
            'timestamp': datetime.now().isoformat(),
            'id': self.metrics['messages_sent']
        }
        
        self.queues[queue_name].append(msg)
        self.metrics['messages_sent'] += 1
        
        # Notify subscribers
        for callback in self.subscribers.get(queue_name, []):
            try:
                callback(msg)
            except:
                pass
    
    def subscribe(self, queue_name: str, callback: Callable):
        """Subscribe to queue"""
        if queue_name not in self.subscribers:
            self.subscribers[queue_name] = []
        self.subscribers[queue_name].append(callback)
    
    def consume(self, queue_name: str, n: int = 1) -> List[Dict]:
        """Consume messages from queue"""
        if queue_name not in self.queues or not self.queues[queue_name]:
            return []
        
        messages = self.queues[queue_name][:n]
        self.queues[queue_name] = self.queues[queue_name][n:]
        self.metrics['messages_received'] += len(messages)
        
        return messages
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'queues': len(self.queues), 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    handler = MessageQueueHandler()
    print(f"✅ {handler.name} v{handler.version} initialized")
