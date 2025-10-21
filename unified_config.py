#!/usr/bin/env python3
"""
UNIFIED CONFIGURATION MANAGER
Central configuration for all APEX components
Validates settings, manages profiles, hot-reloads
"""

import os
import json
from datetime import datetime
from typing import Dict, Any

class UnifiedConfig:
    """Centralized configuration management"""
    
    def __init__(self, config_file: str = 'config/apex_config.json'):
        self.config_file = config_file
        self.config = self._load_default_config()
        self.profiles = {}
        
        # Try to load from file
        if os.path.exists(config_file):
            self._load_from_file()
    
    def _load_default_config(self) -> Dict:
        """Load default production-ready configuration"""
        return {
            'system': {
                'version': '2.0.0',
                'mode': 'PRODUCTION',
                'max_concurrent_bots': 10,
                'auto_restart': True,
                'log_level': 'INFO'
            },
            
            'trading': {
                'enabled': True,
                'max_position_size_usd': 0.50,
                'max_positions': 4,
                'max_trades_per_day': 50,
                'min_profit_target_pct': 2.0,
                'max_loss_per_trade_pct': 2.0,
                'default_stop_loss_pct': 2.0,
                'default_take_profit_pct': 5.0,
                'trading_pairs': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT']
            },
            
            'risk_management': {
                'max_daily_loss_usd': 1.0,
                'max_drawdown_pct': 10.0,
                'position_sizing_method': 'DYNAMIC',
                'use_trailing_stop': True,
                'emergency_stop_on_crash': True,
                'crash_threshold_pct': 10.0
            },
            
            'god_level_ai': {
                'god_bot_enabled': True,
                'king_bot_profile': 'GUARDIAN',  # GORILLA, FOX, SCHOLAR, GUARDIAN
                'oracle_ai_enabled': True,
                'prophet_ai_enabled': True,
                'hivemind_sync_interval_sec': 10,
                'strategy_evolution_interval_hours': 24
            },
            
            'council': {
                'enabled': True,
                'min_approvals_required': 3,  # 3 out of 5 council members must approve
                'roi_threshold': 2.0,
                'volatility_max': 0.15,
                'drawdown_max_pct': 5.0
            },
            
            'atn_traders': {
                'momentum_rider_enabled': True,
                'snipe_bot_enabled': True,
                'arbitrage_enabled': False,  # Disabled until cross-exchange support
                'flash_trade_enabled': True,
                'short_selling_enabled': False,  # Disabled for now
                'continuity_bots_enabled': True
            },
            
            'protection': {
                'rug_shield_enabled': True,
                'min_liquidity_usd': 100000,
                'profit_lock_enabled': True,
                'profit_lock_threshold_pct': 10.0,
                'liquidity_wave_enabled': True,
                'fee_optimization_enabled': True
            },
            
            'infrastructure': {
                'yield_farming_enabled': False,  # Disabled until staking API ready
                'api_guardian_enabled': True,
                'conflict_resolver_enabled': True,
                'emergency_pause_enabled': True,
                'crash_recovery_enabled': True,
                'bot_evolution_enabled': True
            },
            
            'notifications': {
                'telegram_enabled': True,
                'notify_on_trade': True,
                'notify_on_error': True,
                'notify_on_profit': True,
                'notify_on_loss': True,
                'daily_summary': True
            },
            
            'performance': {
                'target_daily_profit_usd': 1.0,
                'target_win_rate': 0.65,
                'max_slippage_pct': 1.0,
                'execution_timeout_sec': 30
            }
        }
    
    def _load_from_file(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
        except Exception as e:
            print(f"⚠️ Could not load config file: {e}")
    
    def save_to_file(self) -> bool:
        """Save current configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Could not save config: {e}")
            return False
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation path"""
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, path: str, value: Any) -> bool:
        """Set configuration value by dot-notation path"""
        keys = path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        return True
    
    def validate(self) -> Dict:
        """Validate configuration settings"""
        errors = []
        warnings = []
        
        # Check critical settings
        if self.get('trading.max_position_size_usd', 0) <= 0:
            errors.append('trading.max_position_size_usd must be > 0')
        
        if self.get('trading.max_position_size_usd', 0) > 10:
            warnings.append('trading.max_position_size_usd > $10 (high risk)')
        
        if self.get('risk_management.max_daily_loss_usd', 0) <= 0:
            errors.append('risk_management.max_daily_loss_usd must be > 0')
        
        if not self.get('trading.trading_pairs'):
            errors.append('No trading pairs configured')
        
        # Check API keys
        if not os.getenv('EXCHANGE_API_KEY'):
            errors.append('EXCHANGE_API_KEY not set in environment')
        
        if not os.getenv('TELEGRAM_BOT_TOKEN'):
            warnings.append('TELEGRAM_BOT_TOKEN not set - notifications disabled')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_profile(self, profile_name: str, overrides: Dict) -> bool:
        """Create a configuration profile (e.g., CONSERVATIVE, AGGRESSIVE)"""
        self.profiles[profile_name] = overrides
        return True
    
    def load_profile(self, profile_name: str) -> bool:
        """Load a configuration profile"""
        if profile_name not in self.profiles:
            return False
        
        for key, value in self.profiles[profile_name].items():
            self.set(key, value)
        
        return True
    
    def get_status(self) -> Dict:
        """Get configuration status"""
        validation = self.validate()
        
        return {
            'config_file': self.config_file,
            'version': self.config['system']['version'],
            'mode': self.config['system']['mode'],
            'valid': validation['valid'],
            'errors': validation['errors'],
            'warnings': validation['warnings'],
            'profiles_available': list(self.profiles.keys()),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    config = UnifiedConfig()
    print("⚙️ APEX Unified Configuration\n")
    
    # Show validation
    validation = config.validate()
    print(f"Valid: {validation['valid']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    
    # Show key settings
    print(f"\n🎯 Trading Settings:")
    print(f"  Max position: ${config.get('trading.max_position_size_usd')}")
    print(f"  Stop loss: {config.get('trading.default_stop_loss_pct')}%")
    print(f"  Take profit: {config.get('trading.default_take_profit_pct')}%")
    print(f"  Pairs: {config.get('trading.trading_pairs')}")
