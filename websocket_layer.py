#!/usr/bin/env python3
"""
WEBSOCKET LAYER - Real-time Data Streaming
Provides live market data via WebSocket connections
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Callable, List
from collections import deque
import ccxt.pro as ccxtpro

class WebSocketLayer:
    """Real-time market data via WebSocket"""
    
    def __init__(self):
        self.name = "WebSocket_Layer"
        self.version = "1.0.0"
        
        self.exchange = None
        self.subscribers = {}
        self.price_feeds = {}
        self.orderbook_feeds = {}
        self.trade_feeds = {}
        
        # Buffer recent data
        self.recent_prices = {}
        self.recent_trades = {}
        
    async def connect(self, exchange_id: str = 'cryptocom', config: Dict = None):
        """Connect to exchange WebSocket"""
        try:
            exchange_class = getattr(ccxtpro, exchange_id)
            self.exchange = exchange_class(config or {})
            print(f"✅ WebSocket connected to {exchange_id}")
            return True
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False
    
    async def subscribe_ticker(self, symbol: str, callback: Callable = None):
        """Subscribe to live price updates"""
        if not self.exchange:
            raise Exception("Exchange not connected")
        
        if symbol not in self.price_feeds:
            self.price_feeds[symbol] = deque(maxlen=1000)
            self.subscribers[f'ticker:{symbol}'] = []
        
        if callback:
            self.subscribers[f'ticker:{symbol}'].append(callback)
        
        # Start watching in background
        asyncio.create_task(self._watch_ticker(symbol))
    
    async def _watch_ticker(self, symbol: str):
        """Watch ticker updates"""
        try:
            while True:
                ticker = await self.exchange.watch_ticker(symbol)
                
                # Store update
                update = {
                    'symbol': symbol,
                    'last': ticker['last'],
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'volume': ticker['quoteVolume'],
                    'timestamp': datetime.now().isoformat()
                }
                
                self.price_feeds[symbol].append(update)
                self.recent_prices[symbol] = update
                
                # Notify subscribers
                for callback in self.subscribers.get(f'ticker:{symbol}', []):
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(update)
                        else:
                            callback(update)
                    except Exception as e:
                        print(f"Callback error: {e}")
        
        except Exception as e:
            print(f"Error watching ticker {symbol}: {e}")
    
    async def subscribe_orderbook(self, symbol: str, callback: Callable = None):
        """Subscribe to order book updates"""
        if not self.exchange:
            raise Exception("Exchange not connected")
        
        if symbol not in self.orderbook_feeds:
            self.orderbook_feeds[symbol] = deque(maxlen=100)
            self.subscribers[f'orderbook:{symbol}'] = []
        
        if callback:
            self.subscribers[f'orderbook:{symbol}'].append(callback)
        
        asyncio.create_task(self._watch_orderbook(symbol))
    
    async def _watch_orderbook(self, symbol: str):
        """Watch order book updates"""
        try:
            while True:
                orderbook = await self.exchange.watch_order_book(symbol)
                
                update = {
                    'symbol': symbol,
                    'bids': orderbook['bids'][:10],  # Top 10
                    'asks': orderbook['asks'][:10],
                    'timestamp': datetime.now().isoformat()
                }
                
                self.orderbook_feeds[symbol].append(update)
                
                # Notify subscribers
                for callback in self.subscribers.get(f'orderbook:{symbol}', []):
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(update)
                        else:
                            callback(update)
                    except Exception as e:
                        print(f"Callback error: {e}")
        
        except Exception as e:
            print(f"Error watching orderbook {symbol}: {e}")
    
    async def subscribe_trades(self, symbol: str, callback: Callable = None):
        """Subscribe to live trade feed"""
        if not self.exchange:
            raise Exception("Exchange not connected")
        
        if symbol not in self.trade_feeds:
            self.trade_feeds[symbol] = deque(maxlen=1000)
            self.subscribers[f'trades:{symbol}'] = []
        
        if callback:
            self.subscribers[f'trades:{symbol}'].append(callback)
        
        asyncio.create_task(self._watch_trades(symbol))
    
    async def _watch_trades(self, symbol: str):
        """Watch live trades"""
        try:
            while True:
                trades = await self.exchange.watch_trades(symbol)
                
                for trade in trades:
                    update = {
                        'symbol': symbol,
                        'price': trade['price'],
                        'amount': trade['amount'],
                        'side': trade['side'],
                        'timestamp': trade['timestamp']
                    }
                    
                    self.trade_feeds[symbol].append(update)
                    
                    # Notify subscribers
                    for callback in self.subscribers.get(f'trades:{symbol}', []):
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(update)
                            else:
                                callback(update)
                        except Exception as e:
                            print(f"Callback error: {e}")
        
        except Exception as e:
            print(f"Error watching trades {symbol}: {e}")
    
    def get_latest_price(self, symbol: str) -> Dict:
        """Get most recent price update"""
        return self.recent_prices.get(symbol, {})
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get recent trades"""
        if symbol in self.trade_feeds:
            return list(self.trade_feeds[symbol])[-limit:]
        return []
    
    async def close(self):
        """Close WebSocket connections"""
        if self.exchange:
            await self.exchange.close()
            print("✅ WebSocket connections closed")


# Convenience function for running WebSocket
async def start_websocket_stream(symbols: List[str], exchange_id: str = 'cryptocom'):
    """Start WebSocket stream for multiple symbols"""
    ws = WebSocketLayer()
    
    # Connect
    config = {
        'enableRateLimit': True,
        'options': {'watchOrderBook': {'limit': 10}}
    }
    await ws.connect(exchange_id, config)
    
    # Subscribe to all symbols
    for symbol in symbols:
        await ws.subscribe_ticker(symbol)
        await ws.subscribe_orderbook(symbol)
        await ws.subscribe_trades(symbol)
        print(f"📡 Subscribed to {symbol}")
    
    return ws


if __name__ == '__main__':
    # Test WebSocket
    async def test():
        symbols = ['BTC/USDT', 'ETH/USDT']
        ws = await start_websocket_stream(symbols)
        
        # Run for 60 seconds
        await asyncio.sleep(60)
        
        # Print recent data
        for symbol in symbols:
            price = ws.get_latest_price(symbol)
            print(f"{symbol}: ${price.get('last', 0):.2f}")
        
        await ws.close()
    
    asyncio.run(test())
