#!/usr/bin/env python3
"""
AEGIS v2.0 - Environment Variable Validator
Validates required environment variables are set and secure
"""

import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

class EnvValidator:
    """Validates required environment variables are set and secure"""
    
    REQUIRED_VARS = [
        'EXCHANGE_API_KEY',
        'EXCHANGE_API_SECRET',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'LIVE_MODE',
        'INITIAL_BALANCE',
        'MAX_POSITION_SIZE'
    ]
    
    OPTIONAL_VARS = [
        'REDIS_HOST',
        'REDIS_PORT',
        'GOOGLE_SHEETS_ID',
        'STOP_LOSS_PCT',
        'TAKE_PROFIT_PCT'
    ]
    
    INSECURE_VALUES = [
        'your_key_here',
        'your_exchange_api_key_here',
        'your_exchange_api_secret_here',
        'placeholder',
        'CHANGE_ME',
        'xxx',
        'test',
        '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890'  # Example token
    ]
    
    @staticmethod
    def validate() -> Dict[str, any]:
        """
        Validate all environment variables
        
        Returns:
            Dict with keys: 'valid' (bool), 'errors' (list), 'warnings' (list)
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required variables
        for var in EnvValidator.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                results['valid'] = False
                results['errors'].append(f"❌ Missing required variable: {var}")
            elif value.lower() in [v.lower() for v in EnvValidator.INSECURE_VALUES]:
                results['valid'] = False
                results['errors'].append(f"❌ {var} is set to insecure placeholder value")
        
        # Validate LIVE_MODE specifically
        live_mode = os.getenv('LIVE_MODE', '').lower()
        if live_mode not in ['true', 'false']:
            results['valid'] = False
            results['errors'].append("❌ LIVE_MODE must be 'True' or 'False'")
        elif live_mode == 'true':
            results['warnings'].append("⚠️  LIVE_MODE is TRUE - System will trade with REAL MONEY!")
        
        # Security checks on API key
        api_key = os.getenv('EXCHANGE_API_KEY', '')
        if len(api_key) < 10 and api_key:
            results['warnings'].append("⚠️  EXCHANGE_API_KEY seems too short (< 10 chars)")
        
        # Security checks on Telegram token
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        if telegram_token and ':' not in telegram_token:
            results['warnings'].append("⚠️  TELEGRAM_BOT_TOKEN format seems incorrect (should contain ':')")
        
        # Check for dangerous values
        max_position = os.getenv('MAX_POSITION_SIZE', '0')
        try:
            if float(max_position) > 100:
                results['warnings'].append(f"⚠️  MAX_POSITION_SIZE is very high: ${max_position}")
        except ValueError:
            results['errors'].append("❌ MAX_POSITION_SIZE must be a number")
            results['valid'] = False
        
        # Check optional vars
        for var in EnvValidator.OPTIONAL_VARS:
            value = os.getenv(var)
            if not value:
                results['warnings'].append(f"ℹ️  Optional variable not set: {var}")
        
        return results
    
    @staticmethod
    def print_results(results: Dict) -> None:
        """Pretty print validation results"""
        print("🔍 AEGIS Environment Validation")
        print("=" * 60)
        
        if results['errors']:
            print("\n❌ ERRORS (Must Fix):")
            for error in results['errors']:
                print(f"  {error}")
        
        if results['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in results['warnings']:
                print(f"  {warning}")
        
        if results['valid'] and not results['warnings']:
            print("\n✅ All environment variables are SECURE and VALID!")
        elif results['valid']:
            print("\n✅ Environment is VALID (but review warnings)")
        else:
            print("\n❌ Environment validation FAILED")
            print("   Fix all errors before running the trading system!")
        
        print("=" * 60)

def main():
    """Main entry point"""
    # Load .env file
    load_dotenv()
    
    # Run validation
    results = EnvValidator.validate()
    
    # Print results
    EnvValidator.print_results(results)
    
    # Return exit code
    if results['valid']:
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
