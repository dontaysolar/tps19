#!/usr/bin/env python3
"""
Crypto.com Exchange Integration

Professional exchange integration with:
- Order execution
- Market data feeds
- Balance management
- Minimum order size handling
- Error recovery
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False

from modules.utils.logger import get_logger
from modules.utils.config import config
from .base_exchange import BaseExchange

logger = get_logger(__name__)


class CryptoComExchange(BaseExchange):
    """
    Crypto.com exchange integration
    
    Handles all interactions with Crypto.com exchange for:
    - Market data
    - Order placement
    - Balance queries
    - Position management
    """
    
    def __init__(self):
        super().__init__('crypto.com')
        
        # API credentials from environment
        self.api_key = os.getenv('CRYPTO_COM_API_KEY', '')
        self.api_secret = os.getenv('CRYPTO_COM_API_SECRET', '')
        
        # Exchange configuration
        self.is_simulation = config.is_simulation
        self.ccxt_exchange = None
        
        # Supported trading pairs
        self.supported_pairs = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'LINK/USDT',
            'ADA/USDT', 'MATIC/USDT', 'AVAX/USDT', 'DOT/USDT',
            'ATOM/USDT', 'UNI/USDT', 'XRP/USDT', 'ALGO/USDT',
            'LTC/USDT', 'XLM/USDT', 'SAND/USDT', 'MANA/USDT'
        ]
        
        # Minimum order sizes (USDT value)
        self.min_order_sizes = {
            'BTC/USDT': 10,
            'ETH/USDT': 10,
            'SOL/USDT': 10,
            'LINK/USDT': 10,
            'ADA/USDT': 10,
            # Default for others
            'default': 10
        }
        
        # Connection state
        self.connected = False
        self.last_api_call = None
        
        logger.info(f"Crypto.com exchange initialized - Mode: {'SIMULATION' if self.is_simulation else 'LIVE'}")
    
    def connect(self) -> bool:
        """
        Connect to exchange
        
        Returns:
            True if connected successfully
        """
        if self.is_simulation:
            logger.info("✅ Simulation mode - no API keys required")
            self.connected = True
            return True
        
        if not HAS_CCXT:
            logger.error("CCXT not installed - run: pip install ccxt")
            return False
        
        if not self.api_key or not self.api_secret:
            logger.error("Missing API credentials for live trading")
            return False
        
        try:
            # Initialize CCXT exchange
            self.ccxt_exchange = ccxt.cryptocom({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            
            # Test connection
            self.ccxt_exchange.load_markets()
            balance = self.ccxt_exchange.fetch_balance()
            
            self.connected = True
            logger.info("✅ Connected to Crypto.com (LIVE)")
            logger.info(f"Balance: {balance.get('total', {})}")
            
            return True
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """
        Get current market data for symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            
        Returns:
            Market data dict or None
        """
        if symbol not in self.supported_pairs:
            logger.warning(f"Pair {symbol} not in supported list")
            return None
        
        try:
            # TODO: Implement real market data fetch via CCXT
            # For now, simulated data
            return {
                'symbol': symbol,
                'price': 50000 if symbol == 'BTC/USDT' else 3000,
                'volume': 1000,
                'bid': 49990,
                'ask': 50010,
                'spread_pct': 0.0004,
                'volume_24h': 2_000_000,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Market data error for {symbol}: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, amount: float, 
                   order_type: str = 'market', price: Optional[float] = None) -> Dict:
        """
        Place order on exchange
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Amount in base currency
            order_type: 'market' or 'limit'
            price: Limit price (if order_type='limit')
            
        Returns:
            Order result
        """
        # Validate minimum order size
        min_size_usdt = self.min_order_sizes.get(symbol, self.min_order_sizes['default'])
        market_data = self.get_market_data(symbol)
        current_price = market_data['price'] if market_data else 50000
        order_value_usdt = amount * current_price
        
        if order_value_usdt < min_size_usdt:
            logger.error(f"Order value ${order_value_usdt:.2f} below minimum ${min_size_usdt:.2f}")
            return {
                'status': 'error',
                'reason': 'below_minimum_size',
                'min_required': min_size_usdt
            }
        
        if self.is_simulation:
            # Simulated order execution
            order_id = f"SIM_{int(datetime.now().timestamp())}"
            
            result = {
                'status': 'success',
                'order_id': order_id,
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price if order_type == 'limit' else current_price,
                'order_type': order_type,
                'filled': True,
                'timestamp': datetime.now(),
                'mode': 'simulation'
            }
            
            logger.info(f"✅ SIM: {side.upper()} {amount} {symbol} @ ${result['price']:.2f}")
            return result
        
        if not self.ccxt_exchange:
            logger.error("Not connected to exchange")
            return {'status': 'error', 'reason': 'not_connected'}
        
        try:
            self._rate_limit_wait()
            
            # Place order via CCXT
            if order_type == 'market':
                if side == 'buy':
                    order = self.ccxt_exchange.create_market_buy_order(symbol, amount)
                else:
                    order = self.ccxt_exchange.create_market_sell_order(symbol, amount)
            else:  # limit
                order = self.ccxt_exchange.create_limit_order(symbol, side, amount, price)
            
            logger.info(f"✅ LIVE: {side.upper()} {amount} {symbol} @ ${order.get('price', price):.2f}")
            
            return {
                'status': 'success',
                'order_id': order.get('id'),
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': order.get('price', price),
                'order_type': order_type,
                'filled': order.get('status') == 'closed',
                'timestamp': datetime.now(),
                'mode': 'live',
                'raw_order': order
            }
            
        except Exception as e:
            logger.error(f"Order placement error: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def get_balance(self) -> Dict[str, float]:
        """
        Get account balances
        
        Returns:
            Dict of balances by currency
        """
        if self.is_simulation:
            return {'USDT': 500.0, 'BTC': 0.0, 'ETH': 0.0}
        
        if not self.ccxt_exchange:
            logger.error("Not connected to exchange")
            return {}
        
        try:
            self._rate_limit_wait()
            balance = self.ccxt_exchange.fetch_balance()
            return balance.get('free', {})
        except Exception as e:
            logger.error(f"Balance fetch error: {e}")
            return {}
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker"""
        if self.is_simulation:
            return {
                'symbol': symbol,
                'last': 50000 if 'BTC' in symbol else 3000,
                'bid': 49990,
                'ask': 50010,
                'timestamp': datetime.now()
            }
        
        if not self.ccxt_exchange:
            return {}
        
        try:
            self._rate_limit_wait()
            ticker = self.ccxt_exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Ticker fetch error: {e}")
            return {}
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        if self.is_simulation:
            return []
        
        if not self.ccxt_exchange:
            return []
        
        try:
            self._rate_limit_wait()
            return self.ccxt_exchange.fetch_open_orders(symbol)
        except Exception as e:
            logger.error(f"Open orders error: {e}")
            return []
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order"""
        if self.is_simulation:
            return True
        
        if not self.ccxt_exchange:
            return False
        
        try:
            self._rate_limit_wait()
            self.ccxt_exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            logger.error(f"Cancel order error: {e}")
            return False
    
    def get_min_order_size(self, symbol: str) -> float:
        """
        Get minimum order size for symbol in USDT
        
        Args:
            symbol: Trading pair
            
        Returns:
            Minimum order size in USDT
        """
        return self.min_order_sizes.get(symbol, self.min_order_sizes['default'])
    
    def validate_order(self, symbol: str, amount_usdt: float) -> Tuple[bool, str]:
        """
        Validate if order meets requirements
        
        Args:
            symbol: Trading pair
            amount_usdt: Order value in USDT
            
        Returns:
            (valid: bool, reason: str)
        """
        min_size = self.get_min_order_size(symbol)
        
        if amount_usdt < min_size:
            return False, f"Below minimum ${min_size:.2f}"
        
        # Check if pair is supported
        if symbol not in self.supported_pairs:
            return False, f"Pair {symbol} not supported"
        
        # Check liquidity
        market_data = self.get_market_data(symbol)
        if market_data and market_data.get('volume_24h', 0) < 1_000_000:
            return False, "Insufficient liquidity"
        
        return True, "Order valid"


# Global exchange instance
crypto_com_exchange = CryptoComExchange()
