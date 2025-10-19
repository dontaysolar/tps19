#!/usr/bin/env python3
"""
Pattern Recognition Bot
Detects Fibonacci levels, RSI/MACD patterns, chart patterns
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
    import numpy as np
    import pandas as pd
except ImportError:
    os.system("pip3 install --break-system-packages ccxt numpy pandas -q")
    import ccxt
    import numpy as np
    import pandas as pd

class PatternRecognitionBot:
    """Identifies trading patterns and technical setups"""
    
    def __init__(self, exchange_config=None):
        self.name = "PatternRecognitionBot"
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
        
        self.patterns_detected = []
        self.metrics = {
            'patterns_found': 0,
            'signals_generated': 0,
            'accuracy': 0.0
        }
    
    def calculate_fibonacci_levels(self, symbol: str, lookback: int = 100) -> Dict:
        """Calculate Fibonacci retracement levels"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=lookback)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Find swing high and low
            high = df['high'].max()
            low = df['low'].min()
            diff = high - low
            
            # Fibonacci retracement levels
            levels = {
                '0.0': high,
                '0.236': high - (diff * 0.236),
                '0.382': high - (diff * 0.382),
                '0.500': high - (diff * 0.500),
                '0.618': high - (diff * 0.618),
                '0.786': high - (diff * 0.786),
                '1.0': low
            }
            
            current_price = df.iloc[-1]['close']
            
            # Find nearest level
            nearest = min(levels.items(), key=lambda x: abs(x[1] - current_price))
            
            return {
                'symbol': symbol,
                'swing_high': high,
                'swing_low': low,
                'current_price': current_price,
                'levels': levels,
                'nearest_level': nearest[0],
                'nearest_price': nearest[1],
                'distance_to_level': abs(current_price - nearest[1]),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Fibonacci calculation error: {e}")
            return {}
    
    def calculate_rsi(self, df: pd.DataFrame, periods: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD indicator"""
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def detect_rsi_macd_hybrid(self, symbol: str) -> Dict:
        """Detect RSI/MACD hybrid trading signals"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Calculate indicators
            df['RSI'] = self.calculate_rsi(df)
            macd = self.calculate_macd(df)
            df['MACD'] = macd['macd']
            df['MACD_Signal'] = macd['signal']
            df['MACD_Hist'] = macd['histogram']
            
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Detect patterns
            patterns = []
            
            # Bullish RSI/MACD Hybrid
            if latest['RSI'] < 30 and latest['MACD_Hist'] > 0 and prev['MACD_Hist'] <= 0:
                patterns.append({
                    'type': 'BULLISH_HYBRID',
                    'signal': 'BUY',
                    'confidence': 0.8,
                    'reason': 'RSI oversold + MACD bullish crossover'
                })
            
            # Bearish RSI/MACD Hybrid
            elif latest['RSI'] > 70 and latest['MACD_Hist'] < 0 and prev['MACD_Hist'] >= 0:
                patterns.append({
                    'type': 'BEARISH_HYBRID',
                    'signal': 'SELL',
                    'confidence': 0.8,
                    'reason': 'RSI overbought + MACD bearish crossover'
                })
            
            # Bullish Divergence
            elif latest['RSI'] > prev['RSI'] and latest['close'] < prev['close']:
                patterns.append({
                    'type': 'BULLISH_DIVERGENCE',
                    'signal': 'BUY',
                    'confidence': 0.6,
                    'reason': 'RSI rising while price falling'
                })
            
            # MACD Histogram Expansion
            elif abs(latest['MACD_Hist']) > abs(prev['MACD_Hist']) * 1.5:
                signal = 'BUY' if latest['MACD_Hist'] > 0 else 'SELL'
                patterns.append({
                    'type': 'MACD_EXPANSION',
                    'signal': signal,
                    'confidence': 0.7,
                    'reason': 'MACD histogram expanding'
                })
            
            self.metrics['patterns_found'] += len(patterns)
            if patterns:
                self.metrics['signals_generated'] += 1
            
            return {
                'symbol': symbol,
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'macd_signal': latest['MACD_Signal'],
                'macd_histogram': latest['MACD_Hist'],
                'patterns': patterns,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ RSI/MACD detection error: {e}")
            return {}
    
    def detect_volume_breakout(self, symbol: str) -> Dict:
        """Detect volume-confirmed breakouts"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=50)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Calculate volume average
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            
            # Get latest
            latest = df.iloc[-1]
            
            # Check for breakout
            is_breakout = False
            signal = None
            
            # Volume spike + price breakout
            if latest['volume'] > latest['volume_ma'] * 2:
                # Check if price broke recent high
                recent_high = df.iloc[-20:-1]['high'].max()
                if latest['close'] > recent_high:
                    is_breakout = True
                    signal = 'BUY'
                
                # Check if price broke recent low
                recent_low = df.iloc[-20:-1]['low'].min()
                if latest['close'] < recent_low:
                    is_breakout = True
                    signal = 'SELL'
            
            return {
                'symbol': symbol,
                'breakout_detected': is_breakout,
                'signal': signal,
                'current_volume': latest['volume'],
                'average_volume': latest['volume_ma'],
                'volume_ratio': latest['volume'] / latest['volume_ma'] if latest['volume_ma'] > 0 else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Volume breakout detection error: {e}")
            return {}
    
    def scan_all_patterns(self, symbol: str) -> Dict:
        """Comprehensive pattern scan"""
        fibonacci = self.calculate_fibonacci_levels(symbol)
        rsi_macd = self.detect_rsi_macd_hybrid(symbol)
        breakout = self.detect_volume_breakout(symbol)
        
        # Consolidate signals
        all_signals = rsi_macd.get('patterns', [])
        if breakout.get('breakout_detected'):
            all_signals.append({
                'type': 'VOLUME_BREAKOUT',
                'signal': breakout['signal'],
                'confidence': 0.75,
                'reason': f"Volume spike {breakout['volume_ratio']:.1f}x"
            })
        
        # Calculate consensus
        if all_signals:
            buy_signals = [s for s in all_signals if s['signal'] == 'BUY']
            sell_signals = [s for s in all_signals if s['signal'] == 'SELL']
            
            if len(buy_signals) > len(sell_signals):
                consensus = 'BUY'
                confidence = sum(s['confidence'] for s in buy_signals) / len(buy_signals)
            elif len(sell_signals) > len(buy_signals):
                consensus = 'SELL'
                confidence = sum(s['confidence'] for s in sell_signals) / len(sell_signals)
            else:
                consensus = 'HOLD'
                confidence = 0.5
        else:
            consensus = 'HOLD'
            confidence = 0.0
        
        return {
            'symbol': symbol,
            'fibonacci': fibonacci,
            'rsi_macd': rsi_macd,
            'breakout': breakout,
            'all_signals': all_signals,
            'consensus': consensus,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'metrics': self.metrics
        }

if __name__ == '__main__':
    bot = PatternRecognitionBot()
    print("📊 Pattern Recognition Bot - Test Mode\n")
    
    result = bot.scan_all_patterns('BTC/USDT')
    print(f"Symbol: {result['symbol']}")
    print(f"Consensus: {result['consensus']} ({result['confidence']*100:.0f}% confidence)")
    print(f"Patterns found: {len(result['all_signals'])}")
