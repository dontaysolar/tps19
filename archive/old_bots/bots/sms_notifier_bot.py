#!/usr/bin/env python3
"""SMS Notifier - Send urgent alerts via SMS (Twilio)"""
from datetime import datetime
from typing import Dict

class SMSNotifierBot:
    def __init__(self):
        self.name = "SMS_Notifier"
        self.version = "1.0.0"
        self.enabled = True
        
        self.account_sid = None
        self.auth_token = None
        self.from_number = None
        self.to_number = None
        
        self.metrics = {'sms_sent': 0, 'errors': 0}
    
    def configure(self, account_sid: str, auth_token: str, from_number: str, to_number: str):
        """Configure Twilio credentials"""
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.to_number = to_number
    
    def send_sms(self, message: str, urgent: bool = False) -> Dict:
        """Send SMS alert"""
        if not all([self.account_sid, self.auth_token, self.from_number, self.to_number]):
            return {'error': 'SMS not configured', 'sent': False}
        
        # Truncate to SMS limits
        max_length = 160
        if len(message) > max_length:
            message = message[:max_length-3] + '...'
        
        if urgent:
            message = f"🚨 URGENT: {message}"
        
        # Simulate sending
        try:
            self.metrics['sms_sent'] += 1
            return {
                'sent': True,
                'message': message,
                'urgent': urgent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.metrics['errors'] += 1
            return {'sent': False, 'error': str(e)}
    
    def send_critical_alert(self, alert_type: str, details: str) -> Dict:
        """Send critical system alert"""
        message = f"{alert_type}: {details}"
        return self.send_sms(message, urgent=True)
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'configured': bool(self.account_sid and self.auth_token),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = SMSNotifierBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
