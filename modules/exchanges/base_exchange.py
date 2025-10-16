#!/usr/bin/env python3
"""Base Exchange Interface"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import time
from modules.utils.logger import get_logger

logger = get_logger(__name__)


class BaseExchange(ABC):
    """Base class for exchange integrations"""
    
    def __init__(self, exchange_id: str):
        self.exchange_id = exchange_id
        self.connected = False
        self.rate_limit_delay = 0.5  # seconds between requests
        self.last_request_time = 0
        
    @abstractmethod
    def connect(self) -> bool:
        """Connect to exchange"""
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """Get account balances"""
        pass
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker for symbol"""
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, side: str, amount: float, 
                   order_type: str = 'market', price: Optional[float] = None) -> Dict:
        """Place order"""
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order"""
        pass
    
    def _rate_limit_wait(self):
        """Wait to respect rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def get_min_order_size(self, symbol: str) -> float:
        """Get minimum order size in USDT"""
        # Override in subclass with actual exchange limits
        return 10.0
    
    def validate_order_size(self, symbol: str, amount_usdt: float) -> Tuple[bool, str]:
        """Validate order meets minimum requirements"""
        min_size = self.get_min_order_size(symbol)
        
        if amount_usdt < min_size:
            return False, f"Order ${amount_usdt:.2f} below minimum ${min_size:.2f}"
        
        return True, "Size valid"
