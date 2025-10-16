#!/usr/bin/env python3
"""
WebSocket Manager - Real-time market data streaming
"""

import asyncio
import json
from typing import Dict, List, Callable, Optional
from datetime import datetime
import websockets

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """
    Real-time market data via WebSockets with auto-reconnection
    """
    
    def __init__(self):
        self.connections = {}
        self.subscriptions = {}
        self.callbacks = {
            'ticker': [],
            'trade': [],
            'orderbook': []
        }
        self.is_running = False
        self.reconnect_delay = 5
        
    async def connect(self, exchange: str, symbols: List[str]):
        """
        Connect to exchange WebSocket and subscribe to symbols
        
        Args:
            exchange: Exchange name ('binance', 'coinbase', etc.)
            symbols: List of trading pairs
        """
        self.is_running = True
        
        if exchange == 'binance':
            await self._connect_binance(symbols)
        elif exchange == 'coinbase':
            await self._connect_coinbase(symbols)
        elif exchange == 'cryptocom':
            await self._connect_cryptocom(symbols)
        else:
            logger.error(f"Exchange {exchange} not supported for WebSocket")
    
    async def _connect_binance(self, symbols: List[str]):
        """Connect to Binance WebSocket"""
        # Binance uses combined streams
        streams = []
        for symbol in symbols:
            symbol_formatted = symbol.replace('/', '').lower()
            streams.append(f"{symbol_formatted}@ticker")
            streams.append(f"{symbol_formatted}@trade")
            streams.append(f"{symbol_formatted}@depth20@100ms")
        
        stream_path = '/'.join(streams)
        uri = f"wss://stream.binance.com:9443/stream?streams={stream_path}"
        
        await self._websocket_loop(uri, self._handle_binance_message)
    
    async def _connect_coinbase(self, symbols: List[str]):
        """Connect to Coinbase WebSocket"""
        uri = "wss://ws-feed.pro.coinbase.com"
        
        # Subscribe message
        subscribe_msg = {
            "type": "subscribe",
            "channels": [
                {"name": "ticker", "product_ids": symbols},
                {"name": "matches", "product_ids": symbols},
                {"name": "level2", "product_ids": symbols}
            ]
        }
        
        await self._websocket_loop(uri, self._handle_coinbase_message, subscribe_msg)
    
    async def _connect_cryptocom(self, symbols: List[str]):
        """Connect to Crypto.com WebSocket"""
        uri = "wss://stream.crypto.com/v2/market"
        
        # Subscribe to channels
        channels = []
        for symbol in symbols:
            symbol_formatted = symbol.replace('/', '_')
            channels.append(f"ticker.{symbol_formatted}")
            channels.append(f"trade.{symbol_formatted}")
            channels.append(f"book.{symbol_formatted}.10")
        
        subscribe_msg = {
            "id": 1,
            "method": "subscribe",
            "params": {"channels": channels}
        }
        
        await self._websocket_loop(uri, self._handle_cryptocom_message, subscribe_msg)
    
    async def _websocket_loop(self, uri: str, handler: Callable, 
                              subscribe_msg: Optional[Dict] = None):
        """
        Main WebSocket loop with auto-reconnection
        """
        while self.is_running:
            try:
                async with websockets.connect(uri) as ws:
                    logger.info(f"✅ Connected to {uri}")
                    
                    # Send subscribe message if needed
                    if subscribe_msg:
                        await ws.send(json.dumps(subscribe_msg))
                    
                    # Listen for messages
                    while self.is_running:
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=30)
                            await handler(json.loads(message))
                        except asyncio.TimeoutError:
                            # Send ping to keep connection alive
                            await ws.ping()
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Connection closed, reconnecting in {self.reconnect_delay}s...")
                await asyncio.sleep(self.reconnect_delay)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(self.reconnect_delay)
    
    async def _handle_binance_message(self, msg: Dict):
        """Handle Binance WebSocket message"""
        if 'data' not in msg:
            return
        
        data = msg['data']
        event_type = data.get('e')
        
        if event_type == '24hrTicker':
            # Ticker update
            ticker_data = {
                'symbol': data['s'],
                'price': float(data['c']),
                'volume_24h': float(data['v']),
                'price_change_pct': float(data['P']),
                'high_24h': float(data['h']),
                'low_24h': float(data['l']),
                'timestamp': datetime.fromtimestamp(data['E'] / 1000)
            }
            await self._notify_callbacks('ticker', ticker_data)
            
        elif event_type == 'trade':
            # Trade update
            trade_data = {
                'symbol': data['s'],
                'price': float(data['p']),
                'quantity': float(data['q']),
                'side': 'buy' if data['m'] else 'sell',
                'timestamp': datetime.fromtimestamp(data['T'] / 1000)
            }
            await self._notify_callbacks('trade', trade_data)
            
        elif event_type == 'depthUpdate':
            # Order book update
            orderbook_data = {
                'symbol': data['s'],
                'bids': [(float(b[0]), float(b[1])) for b in data['b']],
                'asks': [(float(a[0]), float(a[1])) for a in data['a']],
                'timestamp': datetime.fromtimestamp(data['E'] / 1000)
            }
            await self._notify_callbacks('orderbook', orderbook_data)
    
    async def _handle_coinbase_message(self, msg: Dict):
        """Handle Coinbase WebSocket message"""
        msg_type = msg.get('type')
        
        if msg_type == 'ticker':
            ticker_data = {
                'symbol': msg['product_id'],
                'price': float(msg['price']),
                'volume_24h': float(msg.get('volume_24h', 0)),
                'timestamp': datetime.fromisoformat(msg['time'].replace('Z', '+00:00'))
            }
            await self._notify_callbacks('ticker', ticker_data)
            
        elif msg_type == 'match':
            trade_data = {
                'symbol': msg['product_id'],
                'price': float(msg['price']),
                'quantity': float(msg['size']),
                'side': msg['side'],
                'timestamp': datetime.fromisoformat(msg['time'].replace('Z', '+00:00'))
            }
            await self._notify_callbacks('trade', trade_data)
    
    async def _handle_cryptocom_message(self, msg: Dict):
        """Handle Crypto.com WebSocket message"""
        if 'result' in msg and 'channel' in msg['result']:
            channel = msg['result']['channel']
            data = msg['result']['data']
            
            if 'ticker' in channel:
                ticker_data = {
                    'symbol': data['i'],
                    'price': float(data['a']),  # Last price
                    'volume_24h': float(data['v']),
                    'timestamp': datetime.fromtimestamp(data['t'] / 1000)
                }
                await self._notify_callbacks('ticker', ticker_data)
            
            elif 'trade' in channel:
                for trade in data:
                    trade_data = {
                        'symbol': trade['i'],
                        'price': float(trade['p']),
                        'quantity': float(trade['q']),
                        'side': trade['s'],
                        'timestamp': datetime.fromtimestamp(trade['t'] / 1000)
                    }
                    await self._notify_callbacks('trade', trade_data)
            
            elif 'book' in channel:
                orderbook_data = {
                    'symbol': data['i'],
                    'bids': [(float(b[0]), float(b[1])) for b in data['bids']],
                    'asks': [(float(a[0]), float(a[1])) for a in data['asks']],
                    'timestamp': datetime.fromtimestamp(data['t'] / 1000)
                }
                await self._notify_callbacks('orderbook', orderbook_data)
    
    async def _notify_callbacks(self, event_type: str, data: Dict):
        """Notify registered callbacks"""
        for callback in self.callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def on_ticker(self, callback: Callable):
        """Register ticker callback"""
        self.callbacks['ticker'].append(callback)
    
    def on_trade(self, callback: Callable):
        """Register trade callback"""
        self.callbacks['trade'].append(callback)
    
    def on_orderbook(self, callback: Callable):
        """Register orderbook callback"""
        self.callbacks['orderbook'].append(callback)
    
    async def stop(self):
        """Stop WebSocket connections"""
        self.is_running = False
        logger.info("WebSocket manager stopped")


# Global instance
websocket_manager = WebSocketManager()


# Example usage
async def example_usage():
    """Example of how to use WebSocket manager"""
    
    def handle_ticker(data):
        print(f"Ticker: {data['symbol']} @ ${data['price']:.2f}")
    
    def handle_trade(data):
        print(f"Trade: {data['symbol']} {data['side']} {data['quantity']} @ ${data['price']:.2f}")
    
    # Register callbacks
    websocket_manager.on_ticker(handle_ticker)
    websocket_manager.on_trade(handle_trade)
    
    # Connect
    await websocket_manager.connect('binance', ['BTC/USDT', 'ETH/USDT'])


if __name__ == "__main__":
    asyncio.run(example_usage())
