#!/usr/bin/env python3
"""Log Manager - Centralized logging system"""
import json
from datetime import datetime
from typing import Dict
from collections import deque

class LogManagerBot:
    def __init__(self):
        self.name = "Log_Manager"
        self.version = "1.0.0"
        self.enabled = True
        
        self.log_buffer = deque(maxlen=1000)
        self.log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        self.metrics = {'logs_written': 0, 'errors_logged': 0}
    
    def log(self, level: str, message: str, bot_name: str = None, data: Dict = None):
        """Write log entry"""
        if level not in self.log_levels:
            level = 'INFO'
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'bot': bot_name or 'SYSTEM',
            'message': message,
            'data': data or {}
        }
        
        self.log_buffer.append(entry)
        self.metrics['logs_written'] += 1
        
        if level in ['ERROR', 'CRITICAL']:
            self.metrics['errors_logged'] += 1
        
        # In production, write to file/database
        return entry
    
    def debug(self, message: str, bot_name: str = None, data: Dict = None):
        return self.log('DEBUG', message, bot_name, data)
    
    def info(self, message: str, bot_name: str = None, data: Dict = None):
        return self.log('INFO', message, bot_name, data)
    
    def warning(self, message: str, bot_name: str = None, data: Dict = None):
        return self.log('WARNING', message, bot_name, data)
    
    def error(self, message: str, bot_name: str = None, data: Dict = None):
        return self.log('ERROR', message, bot_name, data)
    
    def critical(self, message: str, bot_name: str = None, data: Dict = None):
        return self.log('CRITICAL', message, bot_name, data)
    
    def get_recent_logs(self, n: int = 100, level: str = None) -> list:
        """Get recent log entries"""
        logs = list(self.log_buffer)
        
        if level:
            logs = [log for log in logs if log['level'] == level]
        
        return logs[-n:]
    
    def get_error_summary(self) -> Dict:
        """Get summary of errors"""
        errors = [log for log in self.log_buffer if log['level'] in ['ERROR', 'CRITICAL']]
        
        error_types = {}
        for error in errors:
            bot = error['bot']
            error_types[bot] = error_types.get(bot, 0) + 1
        
        return {
            'total_errors': len(errors),
            'by_bot': error_types,
            'recent_errors': errors[-10:],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'buffer_size': len(self.log_buffer),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = LogManagerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
