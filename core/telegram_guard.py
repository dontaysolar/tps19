#!/usr/bin/env python3
"""
Telegram Command Guard
Security layer for Telegram bot commands
"""

import re
from typing import List, Dict, Any

class TelegramCommandGuard:
    """Security guard for Telegram bot commands"""
    
    def __init__(self):
        self.allowed_commands = [
            '/start', '/help', '/status', '/price', '/subscribe', 
            '/unsubscribe', '/summary', '/alerts', '/stats'
        ]
        
        self.admin_commands = [
            '/restart', '/shutdown', '/config', '/debug'
        ]
        
        self.admin_chat_ids = []  # Configure with authorized admin chat IDs
        
    def guard_command(self, command: str, chat_id: int = None) -> bool:
        """
        Validate if a command is allowed
        
        Args:
            command: Command string to validate
            chat_id: Chat ID of the user (for admin validation)
            
        Returns:
            bool: True if command is allowed, False otherwise
        """
        if not command:
            return False
        
        # Extract command from message
        cmd = command.split()[0].lower() if command else ""
        
        # Check if it's a standard allowed command
        if cmd in self.allowed_commands:
            return True
        
        # Check if it's an admin command
        if cmd in self.admin_commands:
            return self._is_admin(chat_id)
        
        # Unknown command
        return False
    
    def _is_admin(self, chat_id: int) -> bool:
        """Check if chat_id belongs to an admin"""
        if chat_id is None:
            return False
        return chat_id in self.admin_chat_ids
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent injection attacks
        
        Args:
            text: Input text to sanitize
            
        Returns:
            str: Sanitized text
        """
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>\"\'%;()&+]', '', text)
        
        # Limit length
        max_length = 500
        sanitized = sanitized[:max_length]
        
        return sanitized
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate cryptocurrency symbol
        
        Args:
            symbol: Symbol to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not symbol:
            return False
        
        # Allow only alphanumeric and underscore
        pattern = r'^[A-Z0-9_]{2,10}$'
        return bool(re.match(pattern, symbol.upper()))
    
    def add_admin(self, chat_id: int) -> bool:
        """Add an admin chat ID"""
        if chat_id not in self.admin_chat_ids:
            self.admin_chat_ids.append(chat_id)
            return True
        return False
    
    def remove_admin(self, chat_id: int) -> bool:
        """Remove an admin chat ID"""
        if chat_id in self.admin_chat_ids:
            self.admin_chat_ids.remove(chat_id)
            return True
        return False

# Global guard instance
guard = TelegramCommandGuard()

# Legacy function for backward compatibility
def guard_command(cmd: str) -> bool:
    """Legacy guard function"""
    return guard.guard_command(cmd)

if __name__ == "__main__":
    guard = TelegramCommandGuard()
    
    print("🛡️ Telegram Command Guard")
    print("=" * 60)
    
    # Test commands
    test_cases = [
        ('/start', None, True),
        ('/help', None, True),
        ('/status', None, True),
        ('/restart', None, False),  # Admin command without admin ID
        ('/restart', 12345, False),  # Admin command but not authorized
        ('/unknown', None, False),
        ('', None, False),
    ]
    
    for cmd, chat_id, expected in test_cases:
        result = guard.guard_command(cmd, chat_id)
        status = "✅" if result == expected else "❌"
        print(f"{status} Command: '{cmd}' (chat_id: {chat_id}) -> {result} (expected: {expected})")
    
    # Test input sanitization
    print("\n🧹 Input Sanitization:")
    dangerous_inputs = [
        '<script>alert("xss")</script>',
        'BTC"; DROP TABLE users; --',
        "Normal input text"
    ]
    
    for inp in dangerous_inputs:
        sanitized = guard.sanitize_input(inp)
        print(f"  Input: '{inp}'")
        print(f"  Sanitized: '{sanitized}'")
        print()
    
    # Test symbol validation
    print("🔍 Symbol Validation:")
    test_symbols = ['BTC', 'ETH_USDT', 'INVALID@SYMBOL', 'A', 'VERYLONGSYMBOL123']
    for symbol in test_symbols:
        valid = guard.validate_symbol(symbol)
        status = "✅" if valid else "❌"
        print(f"{status} Symbol: '{symbol}' -> {valid}")
    
    print("\n✅ Telegram Guard Module Ready")
