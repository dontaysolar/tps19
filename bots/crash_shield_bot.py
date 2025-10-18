#!/usr/bin/env python3
"""
Market Crash Shield Bot
Auto-pauses trading during extreme market drops
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class CrashShieldBot:
    """Protects capital during market crashes"""
    
    def __init__(self, exchange_config: Dict = None):
        self.name = "CrashShieldBot"
        self.version = "1.0.0"
        
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
        
        self.config = {
            'crash_threshold_pct': 10.0,     # 10% drop = crash
            'minor_drop_threshold': 5.0,      # 5% drop = warning
            'recovery_threshold_pct': 3.0,    # 3% recovery = resume
            'check_interval': 60              # Check every 60s
        }
        
        self.state = {
            'trading_paused': False,
            'pause_reason': None,
            'pause_timestamp': None,
            'last_prices': {}
        }
        
        self.metrics = {
            'crashes_detected': 0,
            'capital_protected': 0.0,
            'pause_count': 0,
            'resume_count': 0
        }
    
    def check_crash(self, symbol: str) -> Dict:
        """Check if market is crashing"""
        try:
            # Get recent price data
            ohlcv = self.exchange.fetch_ohlcv(symbol, '5m', limit=12)
            
            if len(ohlcv) < 2:
                return {'crash_detected': False}
            
            # Get high and current price from last hour
            highs = [candle[2] for candle in ohlcv]
            current_price = ohlcv[-1][4]
            high_price = max(highs)
            
            # Calculate drop percentage
            drop_pct = ((high_price - current_price) / high_price) * 100
            
            # Update last price
            self.state['last_prices'][symbol] = current_price
            
            # Determine crash level
            crash_level = "NORMAL"
            if drop_pct >= self.config['crash_threshold_pct']:
                crash_level = "CRASH"
                self.metrics['crashes_detected'] += 1
            elif drop_pct >= self.config['minor_drop_threshold']:
                crash_level = "WARNING"
            
            return {
                'symbol': symbol,
                'crash_detected': crash_level != "NORMAL",
                'crash_level': crash_level,
                'high_price': high_price,
                'current_price': current_price,
                'drop_pct': drop_pct,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Crash detection error: {e}")
            return {'crash_detected': False}
    
    def pause_trading(self, reason: str) -> None:
        """Pause all trading"""
        if not self.state['trading_paused']:
            self.state['trading_paused'] = True
            self.state['pause_reason'] = reason
            self.state['pause_timestamp'] = datetime.now().isoformat()
            self.metrics['pause_count'] += 1
            
            print(f"🛑 TRADING PAUSED: {reason}")
    
    def resume_trading(self) -> None:
        """Resume trading after recovery"""
        if self.state['trading_paused']:
            self.state['trading_paused'] = False
            self.state['pause_reason'] = None
            self.metrics['resume_count'] += 1
            
            print(f"✅ TRADING RESUMED")
    
    def check_recovery(self, symbol: str) -> bool:
        """Check if market has recovered"""
        if not self.state['trading_paused']:
            return False
        
        try:
            # Get recent price movement
            ohlcv = self.exchange.fetch_ohlcv(symbol, '5m', limit=6)
            
            if len(ohlcv) < 2:
                return False
            
            # Calculate recovery from low
            lows = [candle[3] for candle in ohlcv]
            current_price = ohlcv[-1][4]
            low_price = min(lows)
            
            recovery_pct = ((current_price - low_price) / low_price) * 100
            
            return recovery_pct >= self.config['recovery_threshold_pct']
            
        except Exception as e:
            print(f"❌ Recovery check error: {e}")
            return False
    
    def monitor_market(self, symbols: List[str]) -> Dict:
        """Monitor multiple symbols for crashes"""
        results = {}
        
        for symbol in symbols:
            crash_data = self.check_crash(symbol)
            results[symbol] = crash_data
            
            # Take action based on crash level
            if crash_data.get('crash_level') == 'CRASH':
                self.pause_trading(f"Market crash detected: {symbol} down {crash_data['drop_pct']:.2f}%")
            elif crash_data.get('crash_level') == 'WARNING':
                print(f"⚠️  Market warning: {symbol} down {crash_data['drop_pct']:.2f}%")
        
        # Check for recovery if paused
        if self.state['trading_paused']:
            recovered = all(self.check_recovery(symbol) for symbol in symbols)
            if recovered:
                self.resume_trading()
        
        return {
            'trading_paused': self.state['trading_paused'],
            'pause_reason': self.state['pause_reason'],
            'symbols': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'state': self.state,
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = CrashShieldBot()
    print("🛡️ Crash Shield Bot - Test Mode\n")
    
    result = bot.monitor_market(['BTC/USDT', 'ETH/USDT'])
    print(json.dumps(result, indent=2))
