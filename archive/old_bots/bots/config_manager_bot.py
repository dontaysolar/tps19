#!/usr/bin/env python3
"""Config Manager - Centralized configuration management"""
import json
from datetime import datetime
from typing import Dict, Any

class ConfigManagerBot:
    def __init__(self):
        self.name = "Config_Manager"
        self.version = "1.0.0"
        self.enabled = True
        
        self.configs = {}
        self.config_history = []
        
        self.metrics = {'configs_loaded': 0, 'configs_updated': 0}
    
    def set_config(self, key: str, value: Any, category: str = 'general'):
        """Set configuration value"""
        if category not in self.configs:
            self.configs[category] = {}
        
        old_value = self.configs[category].get(key)
        self.configs[category][key] = value
        
        # Track history
        self.config_history.append({
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'key': key,
            'old_value': old_value,
            'new_value': value
        })
        
        self.metrics['configs_updated'] += 1
        
        return {'success': True, 'key': key, 'value': value}
    
    def get_config(self, key: str, category: str = 'general', default: Any = None) -> Any:
        """Get configuration value"""
        if category not in self.configs:
            return default
        
        return self.configs[category].get(key, default)
    
    def get_all_configs(self, category: str = None) -> Dict:
        """Get all configurations"""
        if category:
            return self.configs.get(category, {})
        return self.configs
    
    def load_from_dict(self, config_dict: Dict, category: str = 'general'):
        """Load multiple configs from dictionary"""
        for key, value in config_dict.items():
            self.set_config(key, value, category)
        
        self.metrics['configs_loaded'] += 1
        
        return {'loaded': len(config_dict), 'category': category}
    
    def export_config(self, category: str = None) -> str:
        """Export configuration as JSON"""
        if category:
            export_data = {category: self.configs.get(category, {})}
        else:
            export_data = self.configs
        
        return json.dumps(export_data, indent=2)
    
    def get_config_history(self, n: int = 20) -> list:
        """Get recent configuration changes"""
        return self.config_history[-n:]
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'total_categories': len(self.configs),
            'total_configs': sum([len(cat) for cat in self.configs.values()]),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = ConfigManagerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
