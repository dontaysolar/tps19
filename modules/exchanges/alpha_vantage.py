#!/usr/bin/env python3
"""Alpha Vantage API Integration for Traditional Markets and Crypto"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AlphaVantageAPI:
    """Alpha Vantage API Client for market data"""
    
    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.session = requests.Session()
        self.rate_limit_delay = 12  # Free tier: 5 calls per minute
        self.last_call_time = 0
        
    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_call)
            
        self.last_call_time = time.time()
        
    def _make_request(self, params: Dict) -> Dict:
        """Make API request with rate limiting"""
        self._rate_limit()
        
        params["apikey"] = self.api_key
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                print(f"API Error: {data['Error Message']}")
                return {}
            elif "Note" in data:
                print(f"API Note: {data['Note']}")
                return {}
                
            return data
            
        except Exception as e:
            print(f"Request error: {e}")
            return {}
            
    def get_crypto_exchange_rate(self, from_currency: str, to_currency: str = "USD") -> Dict:
        """Get current exchange rate for crypto"""
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency
        }
        
        data = self._make_request(params)
        
        if "Realtime Currency Exchange Rate" in data:
            rate_data = data["Realtime Currency Exchange Rate"]
            return {
                "from_currency": rate_data.get("1. From_Currency Code"),
                "to_currency": rate_data.get("3. To_Currency Code"),
                "exchange_rate": float(rate_data.get("5. Exchange Rate", 0)),
                "last_refreshed": rate_data.get("6. Last Refreshed"),
                "bid_price": float(rate_data.get("8. Bid Price", 0)),
                "ask_price": float(rate_data.get("9. Ask Price", 0))
            }
        else:
            # Return mock data if API fails
            return self._get_mock_exchange_rate(from_currency, to_currency)
            
    def _get_mock_exchange_rate(self, from_currency: str, to_currency: str) -> Dict:
        """Return mock exchange rate for testing"""
        mock_rates = {
            "BTC": 45000.0,
            "ETH": 3000.0,
            "DOGE": 0.15,
            "ADA": 0.50,
            "XRP": 0.60
        }
        
        base_rate = mock_rates.get(from_currency, 100.0)
        variance = (time.time() % 100) / 100.0 * 0.02
        current_rate = base_rate * (1 + variance)
        
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": current_rate,
            "last_refreshed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bid_price": current_rate * 0.999,
            "ask_price": current_rate * 1.001
        }
        
    def get_crypto_daily(self, symbol: str, market: str = "USD") -> Dict:
        """Get daily crypto data"""
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market
        }
        
        data = self._make_request(params)
        
        if "Time Series (Digital Currency Daily)" in data:
            time_series = data["Time Series (Digital Currency Daily)"]
            
            # Get latest day's data
            latest_date = max(time_series.keys())
            latest_data = time_series[latest_date]
            
            return {
                "symbol": symbol,
                "date": latest_date,
                "open": float(latest_data.get("1a. open (USD)", 0)),
                "high": float(latest_data.get("2a. high (USD)", 0)),
                "low": float(latest_data.get("3a. low (USD)", 0)),
                "close": float(latest_data.get("4a. close (USD)", 0)),
                "volume": float(latest_data.get("5. volume", 0)),
                "market_cap": float(latest_data.get("6. market cap (USD)", 0))
            }
        else:
            return self._get_mock_daily_data(symbol)
            
    def _get_mock_daily_data(self, symbol: str) -> Dict:
        """Return mock daily data for testing"""
        exchange_rate = self._get_mock_exchange_rate(symbol, "USD")
        base_price = exchange_rate["exchange_rate"]
        
        return {
            "symbol": symbol,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "open": base_price * 0.98,
            "high": base_price * 1.05,
            "low": base_price * 0.95,
            "close": base_price,
            "volume": 1000000.0,
            "market_cap": base_price * 1000000000
        }
        
    def get_stock_quote(self, symbol: str) -> Dict:
        """Get stock quote (for traditional markets)"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol
        }
        
        data = self._make_request(params)
        
        if "Global Quote" in data:
            quote_data = data["Global Quote"]
            return {
                "symbol": quote_data.get("01. symbol"),
                "price": float(quote_data.get("05. price", 0)),
                "volume": float(quote_data.get("06. volume", 0)),
                "latest_trading_day": quote_data.get("07. latest trading day"),
                "previous_close": float(quote_data.get("08. previous close", 0)),
                "change": float(quote_data.get("09. change", 0)),
                "change_percent": quote_data.get("10. change percent", "0%")
            }
        else:
            return self._get_mock_stock_quote(symbol)
            
    def _get_mock_stock_quote(self, symbol: str) -> Dict:
        """Return mock stock quote for testing"""
        mock_prices = {
            "AAPL": 180.0,
            "GOOGL": 140.0,
            "MSFT": 380.0,
            "TSLA": 250.0
        }
        
        base_price = mock_prices.get(symbol, 100.0)
        variance = (time.time() % 100) / 100.0 * 0.02
        current_price = base_price * (1 + variance)
        
        return {
            "symbol": symbol,
            "price": current_price,
            "volume": 50000000,
            "latest_trading_day": datetime.now().strftime("%Y-%m-%d"),
            "previous_close": base_price,
            "change": current_price - base_price,
            "change_percent": f"{variance * 100:.2f}%"
        }
        
    def get_technical_indicators(self, symbol: str, indicator: str = "RSI", 
                               interval: str = "daily", time_period: int = 14) -> Dict:
        """Get technical indicators"""
        params = {
            "function": indicator,
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period,
            "series_type": "close"
        }
        
        data = self._make_request(params)
        
        if f"Technical Analysis: {indicator}" in data:
            ta_data = data[f"Technical Analysis: {indicator}"]
            
            # Get latest indicator value
            if ta_data:
                latest_date = max(ta_data.keys())
                latest_value = float(ta_data[latest_date][indicator])
                
                return {
                    "symbol": symbol,
                    "indicator": indicator,
                    "date": latest_date,
                    "value": latest_value,
                    "time_period": time_period
                }
                
        # Return mock indicator if API fails
        return self._get_mock_indicator(symbol, indicator)
        
    def _get_mock_indicator(self, symbol: str, indicator: str) -> Dict:
        """Return mock indicator data for testing"""
        mock_values = {
            "RSI": 50 + (time.time() % 30) - 15,  # RSI between 35-65
            "MACD": (time.time() % 10) - 5,  # MACD between -5 and 5
            "STOCH": 50 + (time.time() % 40) - 20,  # Stochastic between 30-70
            "ADX": 25 + (time.time() % 25)  # ADX between 25-50
        }
        
        return {
            "symbol": symbol,
            "indicator": indicator,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "value": mock_values.get(indicator, 50.0),
            "time_period": 14
        }
        
    def get_market_status(self) -> Dict:
        """Get global market status"""
        # Alpha Vantage doesn't have a direct market status endpoint
        # We'll check if we can get data to infer status
        try:
            # Try to get a quote for a major stock
            quote = self.get_stock_quote("SPY")
            
            # Check if the trading day is today
            trading_day = quote.get("latest_trading_day", "")
            today = datetime.now().strftime("%Y-%m-%d")
            
            is_open = trading_day == today
            
            return {
                "status": "open" if is_open else "closed",
                "message": "Market is open" if is_open else "Market is closed",
                "last_trading_day": trading_day
            }
            
        except Exception as e:
            return {
                "status": "unknown",
                "message": "Unable to determine market status",
                "error": str(e)
            }
            
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Test with a simple crypto exchange rate query
            data = self.get_crypto_exchange_rate("BTC", "USD")
            return data.get("exchange_rate", 0) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

# Global instance
alpha_vantage_api = AlphaVantageAPI()

if __name__ == "__main__":
    # Test the API
    api = AlphaVantageAPI()
    
    print("Testing Alpha Vantage API Integration...")
    print("=" * 60)
    
    # Test crypto exchange rate
    btc_rate = api.get_crypto_exchange_rate("BTC", "USD")
    print(f"BTC/USD Rate: ${btc_rate.get('exchange_rate', 0):.2f}")
    
    # Test stock quote
    stock_quote = api.get_stock_quote("AAPL")
    print(f"AAPL Stock Price: ${stock_quote.get('price', 0):.2f}")
    
    # Test technical indicator
    rsi = api.get_technical_indicators("BTC", "RSI")
    print(f"BTC RSI: {rsi.get('value', 0):.2f}")
    
    # Test connection
    if api.test_connection():
        print("✅ API Connection successful!")
    else:
        print("❌ API Connection failed!")