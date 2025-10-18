#!/usr/bin/env python3
"""
Whale Monitor Bot
Detects large trades and unusual wallet activity
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

class WhaleMonitorBot:
    """Monitors large trades and whale activity"""
    
    def __init__(self, exchange_config=None):
        self.name = "WhaleMonitorBot"
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
            'whale_threshold_usd': 100000,  # $100k+ = whale
            'volume_spike_threshold': 3.0,   # 3x average = spike
            'monitoring_interval': 60        # Check every 60s
        }
        
        self.metrics = {
            'whales_detected': 0,
            'volume_spikes': 0,
            'alerts_sent': 0
        }
        
        self.whale_history = []
    
    def detect_large_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Detect large trades on exchange"""
        try:
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            
            large_trades = []
            for trade in trades:
                trade_value = trade['amount'] * trade['price']
                
                if trade_value >= self.config['whale_threshold_usd']:
                    large_trades.append({
                        'symbol': symbol,
                        'timestamp': trade['timestamp'],
                        'side': trade['side'],
                        'amount': trade['amount'],
                        'price': trade['price'],
                        'value_usd': trade_value,
                        'type': 'WHALE_TRADE'
                    })
                    
                    self.metrics['whales_detected'] += 1
            
            return large_trades
            
        except Exception as e:
            print(f"❌ Whale detection error: {e}")
            return []
    
    def detect_volume_spike(self, symbol: str) -> Dict:
        """Detect unusual volume spikes"""
        try:
            # Get recent volume data
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=24)
            
            if len(ohlcv) < 24:
                return {}
            
            # Calculate average volume
            volumes = [candle[5] for candle in ohlcv[:-1]]
            avg_volume = sum(volumes) / len(volumes)
            
            # Check current volume
            current_volume = ohlcv[-1][5]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            if volume_ratio >= self.config['volume_spike_threshold']:
                self.metrics['volume_spikes'] += 1
                
                return {
                    'symbol': symbol,
                    'current_volume': current_volume,
                    'average_volume': avg_volume,
                    'volume_ratio': volume_ratio,
                    'spike_detected': True,
                    'timestamp': datetime.now().isoformat()
                }
            
            return {
                'symbol': symbol,
                'current_volume': current_volume,
                'average_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'spike_detected': False
            }
            
        except Exception as e:
            print(f"❌ Volume spike detection error: {e}")
            return {}
    
    def monitor_symbol(self, symbol: str) -> Dict:
        """Full monitoring for a symbol"""
        large_trades = self.detect_large_trades(symbol)
        volume_data = self.detect_volume_spike(symbol)
        
        alert_level = "NORMAL"
        if large_trades:
            alert_level = "WHALE_DETECTED"
        elif volume_data.get('spike_detected'):
            alert_level = "VOLUME_SPIKE"
        
        if alert_level != "NORMAL":
            self.metrics['alerts_sent'] += 1
        
        return {
            'symbol': symbol,
            'alert_level': alert_level,
            'large_trades': large_trades,
            'volume_data': volume_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = WhaleMonitorBot()
    print("🐋 Whale Monitor Bot - Test Mode\n")
    
    result = bot.monitor_symbol('BTC/USDT')
    print(json.dumps(result, indent=2))
