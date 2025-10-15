#!/usr/bin/env python3
"""
TPS19 Environment Configuration
Handles path configuration for different deployment environments
"""

import os

# Determine base path based on environment
if os.path.exists('/opt/tps19') and os.access('/opt/tps19', os.W_OK):
    BASE_PATH = '/opt/tps19'
elif os.path.exists('/workspace'):
    BASE_PATH = '/workspace'
else:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Environment configuration
class Config:
    """Centralized configuration for TPS19"""
    
    BASE_PATH = BASE_PATH
    DATA_PATH = os.path.join(BASE_PATH, 'data')
    DATABASE_PATH = os.path.join(DATA_PATH, 'databases')
    CONFIG_PATH = os.path.join(BASE_PATH, 'config')
    LOGS_PATH = os.path.join(BASE_PATH, 'logs')
    MODULES_PATH = os.path.join(BASE_PATH, 'modules')
    
    # Database files
    MARKET_DATA_DB = os.path.join(DATABASE_PATH, 'market_data.db')
    TRADING_DB = os.path.join(DATABASE_PATH, 'trading.db')
    TELEGRAM_DB = os.path.join(DATABASE_PATH, 'telegram_bot.db')
    SIUL_DB = os.path.join(DATA_PATH, 'siul_core.db')
    
    # Configuration files
    SYSTEM_CONFIG = os.path.join(CONFIG_PATH, 'system.json')
    TRADING_CONFIG = os.path.join(CONFIG_PATH, 'trading.json')
    TELEGRAM_CONFIG = os.path.join(CONFIG_PATH, 'telegram_config.json')
    GOOGLE_CREDENTIALS = os.path.join(CONFIG_PATH, 'google_credentials.json')
    N8N_CONFIG = os.path.join(CONFIG_PATH, 'n8n_config.json')
    
    # API Keys (from environment variables)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '')
    
    # Exchange configuration
    EXCHANGE = 'crypto.com'
    
    @classmethod
    def ensure_directories(cls):
        """Create all required directories"""
        directories = [
            cls.DATA_PATH,
            cls.DATABASE_PATH,
            cls.CONFIG_PATH,
            cls.LOGS_PATH
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_info(cls):
        """Get environment information"""
        return {
            'base_path': cls.BASE_PATH,
            'data_path': cls.DATA_PATH,
            'database_path': cls.DATABASE_PATH,
            'config_path': cls.CONFIG_PATH,
            'logs_path': cls.LOGS_PATH,
            'exchange': cls.EXCHANGE,
            'writable': os.access(cls.BASE_PATH, os.W_OK)
        }

# Initialize directories on import
Config.ensure_directories()

if __name__ == "__main__":
    print("TPS19 Environment Configuration")
    print("=" * 60)
    info = Config.get_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    print("=" * 60)
    print("✅ Environment configured")
