#!/usr/bin/env python3
"""
Dynamic Stop-Loss Bot
Adjusts stop-losses based on ATR (Average True Range) and volatility
Part of APEX AI Trading System
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
    import numpy as np
except ImportError:
    print("Installing dependencies...")
    os.system("pip3 install --break-system-packages ccxt numpy -q")
    import ccxt
    import numpy as np

class DynamicStopLossBot:
    """
    Dynamically adjusts stop-losses based on market volatility
    
    Features:
    - ATR-based stop-loss calculation
    - Volatility clustering detection
    - Adaptive distance adjustment
    - Position-specific SL management
    - Real-time price monitoring
    """
    
    def __init__(self, exchange_config=None):
        """
        Initialize Dynamic Stop-Loss Bot
        
        Args:
            exchange_config: Exchange API credentials
        """
        self.name = "DynamicStopLossBot"
        self.version = "1.0.0"
        
        # Exchange setup
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({
                'apiKey': os.getenv('EXCHANGE_API_KEY'),
                'secret': os.getenv('EXCHANGE_API_SECRET'),
                'enableRateLimit': True
            })
        
        # Configuration
        self.config = {
            'base_stop_percent': 2.0,      # Base stop-loss: 2%
            'atr_multiplier': 1.5,          # ATR multiplier for volatility adjustment
            'min_stop_percent': 0.5,        # Minimum stop-loss: 0.5%
            'max_stop_percent': 5.0,        # Maximum stop-loss: 5%
            'update_interval': 60,          # Update every 60 seconds
            'atr_period': 14                # ATR calculation period
        }
        
        # State
        self.positions = {}
        self.atr_cache = {}
        self.last_update = {}
        
        # Metrics
        self.metrics = {
            'total_adjustments': 0,
            'stops_hit': 0,
            'capital_saved': 0.0,
            'last_calculation': None
        }
    
    def calculate_atr(self, symbol: str, timeframe: str = '1h', periods: int = 14) -> float:
        """
        Calculate Average True Range (ATR) for volatility measurement
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candlestick timeframe
            periods: Number of periods for ATR calculation
            
        Returns:
            ATR value as float
        """
        try:
            # Prefer cached ATR if it is fresh; enables deterministic testing and reduces API calls
            if symbol in self.atr_cache:
                cached = self.atr_cache[symbol]
                cached_ts = cached.get('timestamp')
                if cached_ts is not None:
                    age_seconds = (datetime.now() - cached_ts).total_seconds()
                    if age_seconds < 300:  # 5 minutes freshness window
                        return float(cached.get('value', 0.0))

            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=periods + 1)
            
            if len(ohlcv) < periods + 1:
                raise ValueError(f"Insufficient data: {len(ohlcv)} candles")
            
            # Calculate True Range for each period
            true_ranges = []
            for i in range(1, len(ohlcv)):
                high = ohlcv[i][2]
                low = ohlcv[i][3]
                prev_close = ohlcv[i-1][4]
                
                # True Range = max(high - low, abs(high - prev_close), abs(low - prev_close))
                tr = max(
                    high - low,
                    abs(high - prev_close),
                    abs(low - prev_close)
                )
                true_ranges.append(tr)
            
            # ATR = Simple Moving Average of True Range
            atr = np.mean(true_ranges[-periods:])
            
            # Cache result
            self.atr_cache[symbol] = {
                'value': atr,
                'timestamp': datetime.now(),
                'timeframe': timeframe
            }
            
            return atr
            
        except Exception as e:
            print(f"❌ ATR calculation error for {symbol}: {e}")
            
            # Return cached value if available
            if symbol in self.atr_cache:
                cached = self.atr_cache[symbol]
                age = (datetime.now() - cached['timestamp']).seconds
                if age < 3600:  # Use cache if less than 1 hour old
                    return cached['value']
            
            return 0.0
    
    def calculate_dynamic_stop(self, symbol: str, entry_price: float, side: str = 'long') -> float:
        """
        Calculate dynamic stop-loss based on ATR and volatility
        
        Args:
            symbol: Trading pair
            entry_price: Entry price of position
            side: 'long' or 'short'
            
        Returns:
            Stop-loss price
        """
        try:
            # Get ATR
            atr = self.calculate_atr(symbol)
            
            if atr == 0:
                # Fallback to base stop-loss if ATR unavailable
                stop_distance = self.config['base_stop_percent'] / 100
            else:
                # Calculate ATR as percentage of price
                atr_percent = (atr / entry_price) * 100
                
                # Adjust stop-loss distance based on volatility
                stop_distance = (self.config['base_stop_percent'] + (atr_percent * self.config['atr_multiplier'])) / 100
                
                # Clamp to min/max
                min_stop = self.config['min_stop_percent'] / 100
                max_stop = self.config['max_stop_percent'] / 100
                stop_distance = max(min_stop, min(stop_distance, max_stop))
            
            # Calculate stop price
            if side == 'long':
                stop_price = entry_price * (1 - stop_distance)
            else:  # short
                stop_price = entry_price * (1 + stop_distance)
            
            return stop_price
            
        except Exception as e:
            print(f"❌ Dynamic stop calculation error for {symbol}: {e}")
            
            # Fallback to base stop-loss
            if side == 'long':
                return entry_price * (1 - self.config['base_stop_percent'] / 100)
            else:
                return entry_price * (1 + self.config['base_stop_percent'] / 100)
    
    def add_position(self, symbol: str, entry_price: float, amount: float, side: str = 'long') -> str:
        """
        Add a position to monitor
        
        Args:
            symbol: Trading pair
            entry_price: Entry price
            amount: Position size
            side: 'long' or 'short'
            
        Returns:
            Position ID
        """
        position_id = f"{symbol}_{datetime.now().timestamp()}"
        
        # Calculate initial stop-loss
        stop_price = self.calculate_dynamic_stop(symbol, entry_price, side)
        
        self.positions[position_id] = {
            'symbol': symbol,
            'entry_price': entry_price,
            'amount': amount,
            'side': side,
            'stop_price': stop_price,
            'created_at': datetime.now().isoformat(),
            'last_adjusted': datetime.now().isoformat(),
            'adjustments': 0
        }
        
        print(f"✅ Position added: {position_id}")
        print(f"   Entry: ${entry_price:.2f}, Stop: ${stop_price:.2f}")
        
        return position_id
    
    def update_stop_loss(self, position_id: str, current_price: float) -> Optional[Dict]:
        """
        Update stop-loss for a position based on current price
        
        Args:
            position_id: Position identifier
            current_price: Current market price
            
        Returns:
            Position close data if stop hit, None otherwise
        """
        if position_id not in self.positions:
            return None
        
        pos = self.positions[position_id]
        
        # First: Check if stop already hit regardless of update interval
        stop_hit = False
        if pos['side'] == 'long' and current_price <= pos['stop_price']:
            stop_hit = True
        elif pos['side'] == 'short' and current_price >= pos['stop_price']:
            stop_hit = True

        if stop_hit:
            profit = (current_price - pos['entry_price']) * pos['amount']
            if pos['side'] == 'short':
                profit = -profit
            profit_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
            if pos['side'] == 'short':
                profit_pct = -profit_pct
            self.metrics['stops_hit'] += 1
            if profit > 0:
                self.metrics['capital_saved'] += profit
            close_data = {
                'position_id': position_id,
                'symbol': pos['symbol'],
                'side': pos['side'],
                'entry': pos['entry_price'],
                'exit': current_price,
                'amount': pos['amount'],
                'profit': profit,
                'profit_pct': profit_pct,
                'reason': 'DYNAMIC_SL'
            }
            print(f"🛑 Stop-loss hit: {pos['symbol']}")
            print(f"   P&L: ${profit:.2f} ({profit_pct:+.2f}%)")
            return close_data

        # If not hit, enforce update interval before recalculating
        last_update = datetime.fromisoformat(pos['last_adjusted'])
        if (datetime.now() - last_update).seconds < self.config['update_interval']:
            return None
        
        # Recalculate stop-loss
        new_stop = self.calculate_dynamic_stop(pos['symbol'], pos['entry_price'], pos['side'])
        
        # For long positions, only move stop up
        # For short positions, only move stop down
        should_update = False
        if pos['side'] == 'long' and new_stop > pos['stop_price']:
            should_update = True
        elif pos['side'] == 'short' and new_stop < pos['stop_price']:
            should_update = True
        
        if should_update:
            old_stop = pos['stop_price']
            pos['stop_price'] = new_stop
            pos['last_adjusted'] = datetime.now().isoformat()
            pos['adjustments'] += 1
            
            self.metrics['total_adjustments'] += 1
            
            print(f"📈 {pos['symbol']} stop adjusted: ${old_stop:.2f} → ${new_stop:.2f}")
        
        # Re-check hit after potential adjustment on next iterations handled at function start
        return None
    
    def monitor_positions(self):
        """Monitor all positions and update stop-losses"""
        for pos_id, pos in list(self.positions.items()):
            try:
                # Get current price
                ticker = self.exchange.fetch_ticker(pos['symbol'])
                current_price = ticker['last']
                
                # Update stop-loss
                close_data = self.update_stop_loss(pos_id, current_price)
                
                if close_data:
                    # Position closed, remove from tracking
                    del self.positions[pos_id]
                    
            except Exception as e:
                print(f"❌ Monitor error for {pos_id}: {e}")
    
    def get_status(self) -> Dict:
        """Get bot status and metrics"""
        return {
            'name': self.name,
            'version': self.version,
            'active_positions': len(self.positions),
            'metrics': self.metrics,
            'config': self.config
        }
    
    def save_state(self, filepath: str = 'data/dynamic_stoploss_state.json'):
        """Save bot state to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        state = {
            'positions': self.positions,
            'metrics': self.metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str = 'data/dynamic_stoploss_state.json'):
        """Load bot state from file"""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.positions = state.get('positions', {})
        self.metrics = state.get('metrics', self.metrics)

if __name__ == '__main__':
    # Test Dynamic Stop-Loss Bot
    print("🤖 Dynamic Stop-Loss Bot - Test Mode\n")
    
    bot = DynamicStopLossBot()
    
    # Test ATR calculation
    print("📊 Testing ATR calculation...")
    atr = bot.calculate_atr('BTC/USDT')
    print(f"   BTC/USDT ATR: {atr:.2f}\n")
    
    # Test dynamic stop calculation
    print("📈 Testing dynamic stop calculation...")
    entry_price = 50000
    stop_price = bot.calculate_dynamic_stop('BTC/USDT', entry_price, 'long')
    stop_distance = ((entry_price - stop_price) / entry_price) * 100
    print(f"   Entry: ${entry_price:.2f}")
    print(f"   Stop: ${stop_price:.2f}")
    print(f"   Distance: {stop_distance:.2f}%\n")
    
    # Test position management
    print("🎯 Testing position management...")
    pos_id = bot.add_position('BTC/USDT', 50000, 0.001, 'long')
    
    # Simulate price movements
    prices = [50000, 51000, 52000, 53000, 52500, 52000]
    print("\n📉 Simulating price movements...")
    for price in prices:
        print(f"\n💰 Current Price: ${price}")
        close_data = bot.update_stop_loss(pos_id, price)
        
        if close_data:
            print(f"\n🛑 POSITION CLOSED")
            print(f"   Final P&L: ${close_data['profit']:.2f} ({close_data['profit_pct']:+.2f}%)")
            break
        
        time.sleep(1)
    
    # Show final status
    print("\n" + "="*60)
    print("📊 Bot Status:")
    status = bot.get_status()
    print(json.dumps(status, indent=2))
