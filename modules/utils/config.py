#!/usr/bin/env python3
"""TPS19 Configuration Management"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

class Config:
    """Centralized configuration management for TPS19"""
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize configuration"""
        # Load environment variables
        if HAS_DOTENV:
            load_dotenv()
        
        # Get base path - use workspace if /opt/tps19 not accessible
        default_path = '/opt/tps19'
        workspace_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        tps19_home = os.getenv('TPS19_HOME', default_path)
        
        # Check if path is writable, fall back to workspace
        test_path = Path(tps19_home)
        try:
            test_path.mkdir(parents=True, exist_ok=True)
            self.base_path = test_path
        except (PermissionError, OSError):
            # Fall back to workspace for development
            self.base_path = Path(workspace_path)
            print(f"⚠️  Using workspace path (no write access to {tps19_home}): {self.base_path}")
        
        # Load JSON configs
        self.config_dir = self.base_path / 'config'
        self._load_json_configs()
        
        # Set paths
        self.data_path = self.base_path / 'data'
        self.db_path = self.data_path / 'databases'
        self.logs_path = self.base_path / 'logs'
        self.backups_path = self.base_path / 'backups'
        
        # Ensure directories exist
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
    def _load_json_configs(self):
        """Load all JSON configuration files"""
        config_files = ['system.json', 'trading.json', 'n8n_config.json', 'mode.json']
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_name = config_file.replace('.json', '')
                    self._config[config_name] = json.load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support
        
        Args:
            key: Configuration key (supports dot notation like 'trading.mode')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Try environment variable first (uppercase, with TPS19_ prefix)
        env_key = f"TPS19_{key.upper().replace('.', '_')}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Try nested dictionary lookup
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
                
        return value if value is not None else default
    
    def get_database_path(self, db_name: str) -> Path:
        """Get full path for a database file
        
        Args:
            db_name: Database filename (e.g., 'trading.db')
            
        Returns:
            Full path to database file
        """
        return self.db_path / db_name
    
    def get_log_path(self, log_name: str) -> Path:
        """Get full path for a log file
        
        Args:
            log_name: Log filename (e.g., 'system.log')
            
        Returns:
            Full path to log file
        """
        return self.logs_path / log_name
    
    @property
    def is_simulation(self) -> bool:
        """Check if running in simulation mode"""
        mode = self.get('mode.mode', 'simulation')
        trading_mode = self.get('trading.trading.mode', 'simulation')
        return mode == 'simulation' or trading_mode == 'simulation'
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        mode = self.get('mode.mode', 'simulation')
        return mode == 'production'
    
    @property
    def exchange(self) -> str:
        """Get configured exchange"""
        return os.getenv('TPS19_EXCHANGE', 'crypto.com')
    
    @property
    def debug(self) -> bool:
        """Check if debug mode is enabled"""
        debug_env = os.getenv('TPS19_DEBUG', 'false').lower()
        debug_config = self.get('system.system.debug', False)
        return debug_env == 'true' or debug_config


# Global config instance
config = Config()
