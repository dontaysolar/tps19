#!/usr/bin/env python3
"""Trend Strength Bot - Measures trend conviction"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class TrendStrengthBot:
    def __init__(self):
        self.name = "Trend_Strength"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'assessments': 0}
    
    def assess_trend_strength(self, ohlcv: List) -> Dict:
        """Assess trend strength using multiple factors"""
        if len(ohlcv) < 50:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # Linear regression slope
        x = np.arange(len(closes))
        slope, _ = np.polyfit(x, closes, 1)
        slope_normalized = slope / closes[0]
        
        # R-squared (trendiness)
        y_pred = slope * x + closes[0]
        ss_res = np.sum((closes - y_pred) ** 2)
        ss_tot = np.sum((closes - np.mean(closes)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Consecutive movements
        moves = np.diff(closes)
        positive_streak = 0
        negative_streak = 0
        
        for move in moves[::-1]:
            if move > 0:
                if negative_streak > 0:
                    break
                positive_streak += 1
            elif move < 0:
                if positive_streak > 0:
                    break
                negative_streak += 1
        
        max_streak = max(positive_streak, negative_streak)
        
        # Combine metrics
        trend_score = (abs(slope_normalized) * 50 + r_squared * 30 + min(max_streak, 10) * 2)
        
        if slope_normalized > 0.01 and r_squared > 0.7:
            direction = 'UPTREND'
            signal = 'BUY'
            strength = 'STRONG' if trend_score > 70 else 'MODERATE'
            confidence = min(0.90, 0.60 + trend_score / 100)
        elif slope_normalized < -0.01 and r_squared > 0.7:
            direction = 'DOWNTREND'
            signal = 'SELL'
            strength = 'STRONG' if trend_score > 70 else 'MODERATE'
            confidence = min(0.90, 0.60 + trend_score / 100)
        else:
            direction = 'SIDEWAYS'
            signal = 'HOLD'
            strength = 'WEAK'
            confidence = 0.50
        
        self.metrics['assessments'] += 1
        
        return {
            'direction': direction,
            'strength': strength,
            'trend_score': trend_score,
            'r_squared': r_squared,
            'slope': slope_normalized,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = TrendStrengthBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
