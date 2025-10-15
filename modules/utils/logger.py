#!/usr/bin/env python3
"""TPS19 Logging Configuration"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from .config import config


class TPS19Logger:
    """Centralized logging for TPS19"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """Get or create a logger
        
        Args:
            name: Logger name (usually module name)
            log_file: Optional specific log file
            
        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Get log level from environment or config
        log_level = os.getenv('LOG_LEVEL', 
                             config.get('logging.level', 'INFO'))
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_file is None:
            log_file = config.get('logging.file', 'system.log')
        
        log_path = config.get_log_path(log_file) if '/' not in log_file else Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        max_bytes = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB default
        backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger


def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Convenience function to get a logger
    
    Args:
        name: Logger name
        log_file: Optional log file
        
    Returns:
        Configured logger
    """
    return TPS19Logger.get_logger(name, log_file)
