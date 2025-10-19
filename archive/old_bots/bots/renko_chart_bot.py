#!/usr/bin/env python3
"""Renko Chart Bot - Time-independent price movement charts"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class RenkoChartBot:
    def __init__(self):
        self.name = "Renko_Chart"
        self.version = "1.0.0"
        self.enabled = True
        self.brick_size = 10  # Default brick size
        self.renko_bricks = []
        self.metrics = {'bricks_created': 0, 'trend_changes': 0}
    
    def calculate_renko(self, ohlcv: List, brick_size: float = None) -> Dict:
        """Generate Renko bricks from price data"""
        if not ohlcv:
            return {'error': 'No data'}
        
        brick_size = brick_size or self.brick_size
        self.renko_bricks = []
        
        # Initialize first brick
        current_brick = {
            'open': ohlcv[0][1],
            'close': ohlcv[0][4],
            'direction': 'UP' if ohlcv[0][4] > ohlcv[0][1] else 'DOWN'
        }
        
        for candle in ohlcv[1:]:
            close = candle[4]
            
            # Check if price moved enough for new brick
            if current_brick['direction'] == 'UP':
                if close >= current_brick['close'] + brick_size:
                    # New up brick
                    n_bricks = int((close - current_brick['close']) / brick_size)
                    for i in range(n_bricks):
                        new_brick = {
                            'open': current_brick['close'] + i * brick_size,
                            'close': current_brick['close'] + (i + 1) * brick_size,
                            'direction': 'UP'
                        }
                        self.renko_bricks.append(new_brick)
                        self.metrics['bricks_created'] += 1
                    current_brick = self.renko_bricks[-1]
                    
                elif close <= current_brick['close'] - 2 * brick_size:
                    # Reversal to down
                    n_bricks = int((current_brick['close'] - close) / brick_size)
                    for i in range(n_bricks):
                        new_brick = {
                            'open': current_brick['close'] - i * brick_size,
                            'close': current_brick['close'] - (i + 1) * brick_size,
                            'direction': 'DOWN'
                        }
                        self.renko_bricks.append(new_brick)
                        self.metrics['bricks_created'] += 1
                    current_brick = self.renko_bricks[-1]
                    self.metrics['trend_changes'] += 1
            
            else:  # DOWN
                if close <= current_brick['close'] - brick_size:
                    # New down brick
                    n_bricks = int((current_brick['close'] - close) / brick_size)
                    for i in range(n_bricks):
                        new_brick = {
                            'open': current_brick['close'] - i * brick_size,
                            'close': current_brick['close'] - (i + 1) * brick_size,
                            'direction': 'DOWN'
                        }
                        self.renko_bricks.append(new_brick)
                        self.metrics['bricks_created'] += 1
                    current_brick = self.renko_bricks[-1]
                    
                elif close >= current_brick['close'] + 2 * brick_size:
                    # Reversal to up
                    n_bricks = int((close - current_brick['close']) / brick_size)
                    for i in range(n_bricks):
                        new_brick = {
                            'open': current_brick['close'] + i * brick_size,
                            'close': current_brick['close'] + (i + 1) * brick_size,
                            'direction': 'UP'
                        }
                        self.renko_bricks.append(new_brick)
                        self.metrics['bricks_created'] += 1
                    current_brick = self.renko_bricks[-1]
                    self.metrics['trend_changes'] += 1
        
        # Analyze trend
        if len(self.renko_bricks) >= 3:
            recent = self.renko_bricks[-3:]
            up_bricks = sum([1 for b in recent if b['direction'] == 'UP'])
            
            if up_bricks >= 2:
                signal, confidence = 'BUY', 0.75
            elif up_bricks <= 1:
                signal, confidence = 'SELL', 0.75
            else:
                signal, confidence = 'HOLD', 0.50
        else:
            signal, confidence = 'HOLD', 0.50
        
        return {
            'total_bricks': len(self.renko_bricks),
            'current_direction': current_brick['direction'],
            'recent_bricks': self.renko_bricks[-5:] if len(self.renko_bricks) >= 5 else self.renko_bricks,
            'signal': signal,
            'confidence': confidence,
            'brick_size': brick_size,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'brick_size': self.brick_size, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = RenkoChartBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
