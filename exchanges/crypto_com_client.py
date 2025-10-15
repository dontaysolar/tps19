"""
Crypto.com Exchange API Client
Production-ready implementation with proper error handling and rate limiting
"""

import time
import hmac
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.logging_config import get_logger
from config.settings import settings


logger = get_logger(__name__)


class CryptoComAPIError(Exception):
    """Base exception for Crypto.com API errors"""
    pass


class CryptoComRateLimitError(CryptoComAPIError):
    """Rate limit exceeded error"""
    pass


class CryptoComAuthError(CryptoComAPIError):
    """Authentication error"""
    pass


class CryptoComClient:
    """
    Crypto.com Exchange API Client
    
    Documentation: https://exchange-docs.crypto.com/spot/index.html
    """
    
    def __init__(
        self,
        api_key: str = None,
        api_secret: str = None,
        api_url: str = None,
        timeout: int = 30
    ):
        self.api_key = api_key or settings.crypto_com.api_key
        self.api_secret = api_secret or settings.crypto_com.api_secret
        self.api_url = api_url or settings.crypto_com.api_url
        self.timeout = timeout
        
        # Rate limiting
        self.rate_limit_per_second = settings.crypto_com.rate_limit_per_second
        self.last_request_time = 0
        self.request_count = 0
        
        # Session with retry strategy
        self.session = self._create_session()
        
        logger.info("CryptoComClient initialized", extra={"api_url": self.api_url})
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def _get_signature(self, params: Dict[str, Any], endpoint: str, method: str) -> str:
        """
        Generate signature for authenticated requests
        
        Args:
            params: Request parameters
            endpoint: API endpoint
            method: HTTP method
            
        Returns:
            Signature string
        """
        # Sort parameters by key
        param_str = ""
        if params:
            sorted_params = sorted(params.items())
            param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # Create signature payload
        req_id = str(int(time.time() * 1000))
        payload = f"{method}{endpoint}{req_id}{param_str}"
        
        # Generate signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, req_id
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        
        # Reset counter if a second has passed
        if current_time - self.last_request_time >= 1:
            self.request_count = 0
            self.last_request_time = current_time
        
        # Check if we've exceeded rate limit
        if self.request_count >= self.rate_limit_per_second:
            sleep_time = 1 - (current_time - self.last_request_time)
            if sleep_time > 0:
                logger.debug(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
                self.request_count = 0
                self.last_request_time = time.time()
        
        self.request_count += 1
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        authenticated: bool = False
    ) -> Dict[str, Any]:
        """
        Make API request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Request parameters
            authenticated: Whether request requires authentication
            
        Returns:
            Response data
            
        Raises:
            CryptoComAPIError: On API errors
        """
        # Rate limiting
        self._rate_limit()
        
        url = f"{self.api_url}{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        
        if authenticated:
            signature, req_id = self._get_signature(params, endpoint, method)
            headers.update({
                "API-KEY": self.api_key,
                "API-SIGN": signature,
                "API-TIMESTAMP": req_id,
                "API-NONCE": req_id
            })
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            elif method == "POST":
                response = self.session.post(url, json=params, headers=headers, timeout=self.timeout)
            elif method == "DELETE":
                response = self.session.delete(url, json=params, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check for rate limit
            if response.status_code == 429:
                raise CryptoComRateLimitError("Rate limit exceeded")
            
            # Check for auth errors
            if response.status_code in [401, 403]:
                raise CryptoComAuthError("Authentication failed")
            
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors in response
            if data.get("code") != "0":
                error_msg = data.get("msg", "Unknown error")
                raise CryptoComAPIError(f"API Error: {error_msg}")
            
            return data.get("result", data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}", extra={"url": url, "method": method})
            raise CryptoComAPIError(f"Request failed: {e}")
    
    # Public API Methods
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get ticker information
        
        Args:
            symbol: Trading pair (e.g., "BTC_USDT")
            
        Returns:
            Ticker data
        """
        endpoint = "/public/get-ticker"
        params = {"instrument_name": symbol}
        return self._request("GET", endpoint, params)
    
    def get_orderbook(self, symbol: str, depth: int = 50) -> Dict[str, Any]:
        """
        Get order book
        
        Args:
            symbol: Trading pair
            depth: Order book depth (max 150)
            
        Returns:
            Order book data
        """
        endpoint = "/public/get-book"
        params = {
            "instrument_name": symbol,
            "depth": min(depth, 150)
        }
        return self._request("GET", endpoint, params)
    
    def get_trades(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get recent trades
        
        Args:
            symbol: Trading pair
            
        Returns:
            List of recent trades
        """
        endpoint = "/public/get-trades"
        params = {"instrument_name": symbol}
        return self._request("GET", endpoint, params)
    
    def get_candlestick(
        self,
        symbol: str,
        timeframe: str = "1m",
        count: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Get candlestick/kline data
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 6h, 12h, 1D, 7D, 14D, 1M)
            count: Number of candles (max 1440)
            
        Returns:
            List of candlestick data
        """
        endpoint = "/public/get-candlestick"
        params = {
            "instrument_name": symbol,
            "timeframe": timeframe,
            "count": min(count, 1440)
        }
        return self._request("GET", endpoint, params)
    
    def get_instruments(self) -> List[Dict[str, Any]]:
        """
        Get all available trading instruments
        
        Returns:
            List of trading instruments
        """
        endpoint = "/public/get-instruments"
        return self._request("GET", endpoint)
    
    # Private API Methods (Authenticated)
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance
        
        Returns:
            Account balance information
        """
        endpoint = "/private/get-account-summary"
        return self._request("POST", endpoint, {}, authenticated=True)
    
    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        client_order_id: Optional[str] = None,
        time_in_force: str = "GTC",
        exec_inst: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new order
        
        Args:
            symbol: Trading pair
            side: "BUY" or "SELL"
            order_type: "LIMIT", "MARKET", "STOP_LIMIT", "STOP_LOSS"
            quantity: Order quantity
            price: Order price (required for limit orders)
            client_order_id: Client order ID
            time_in_force: Time in force (GTC, IOC, FOK)
            exec_inst: Execution instruction (POST_ONLY)
            
        Returns:
            Order creation response
        """
        endpoint = "/private/create-order"
        
        params = {
            "instrument_name": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": str(quantity)
        }
        
        if price is not None:
            params["price"] = str(price)
        
        if client_order_id:
            params["client_oid"] = client_order_id
        
        if time_in_force:
            params["time_in_force"] = time_in_force
        
        if exec_inst:
            params["exec_inst"] = exec_inst
        
        return self._request("POST", endpoint, params, authenticated=True)
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            order_id: Order ID
            symbol: Trading pair
            
        Returns:
            Cancellation response
        """
        endpoint = "/private/cancel-order"
        params = {
            "instrument_name": symbol,
            "order_id": order_id
        }
        return self._request("POST", endpoint, params, authenticated=True)
    
    def cancel_all_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel all orders
        
        Args:
            symbol: Trading pair (optional, cancels all if not specified)
            
        Returns:
            Cancellation response
        """
        endpoint = "/private/cancel-all-orders"
        params = {}
        if symbol:
            params["instrument_name"] = symbol
        return self._request("POST", endpoint, params, authenticated=True)
    
    def get_order_history(
        self,
        symbol: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get order history
        
        Args:
            symbol: Trading pair (optional)
            start_time: Start timestamp (milliseconds)
            end_time: End timestamp (milliseconds)
            limit: Number of records (max 100)
            
        Returns:
            List of historical orders
        """
        endpoint = "/private/get-order-history"
        params = {"count": min(limit, 100)}
        
        if symbol:
            params["instrument_name"] = symbol
        if start_time:
            params["start_ts"] = start_time
        if end_time:
            params["end_ts"] = end_time
        
        return self._request("POST", endpoint, params, authenticated=True)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open orders
        
        Args:
            symbol: Trading pair (optional)
            
        Returns:
            List of open orders
        """
        endpoint = "/private/get-open-orders"
        params = {}
        if symbol:
            params["instrument_name"] = symbol
        
        return self._request("POST", endpoint, params, authenticated=True)
    
    def get_trade_history(
        self,
        symbol: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get trade history
        
        Args:
            symbol: Trading pair (optional)
            start_time: Start timestamp (milliseconds)
            end_time: End timestamp (milliseconds)
            limit: Number of records (max 100)
            
        Returns:
            List of historical trades
        """
        endpoint = "/private/get-trades"
        params = {"count": min(limit, 100)}
        
        if symbol:
            params["instrument_name"] = symbol
        if start_time:
            params["start_ts"] = start_time
        if end_time:
            params["end_ts"] = end_time
        
        return self._request("POST", endpoint, params, authenticated=True)


# Example usage and testing
if __name__ == "__main__":
    # Initialize client
    client = CryptoComClient()
    
    try:
        # Test public endpoints
        print("Testing public endpoints...")
        
        # Get ticker
        ticker = client.get_ticker("BTC_USDT")
        print(f"BTC/USDT Ticker: {ticker}")
        
        # Get instruments
        instruments = client.get_instruments()
        print(f"Available instruments: {len(instruments)}")
        
        # Test authenticated endpoints (will fail without valid API keys)
        if settings.crypto_com.api_key != "your_api_key_here":
            print("\nTesting authenticated endpoints...")
            
            # Get account balance
            balance = client.get_account_balance()
            print(f"Account balance: {balance}")
            
            # Get open orders
            open_orders = client.get_open_orders()
            print(f"Open orders: {len(open_orders)}")
    
    except CryptoComAPIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Error: {e}")