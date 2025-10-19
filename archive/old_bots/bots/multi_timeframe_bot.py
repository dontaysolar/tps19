#!/usr/bin/env python3
"""
Multi-Timeframe Analysis Bot
Analyzes multiple timeframes simultaneously:
- 5min, 15min, 1hr, 4hr, 1day
- Identifies trend alignment across timeframes
- Generates high-probability signals when all TFs align
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class MultiTimeframeBot:
    def __init__(self):
        self.name = "Multi_Timeframe"
        self.version = "1.0.0"
        self.enabled = True
        
        self.timeframes = ['5m', '15m', '1h', '4h', '1d']
        
        self.metrics = {
            'aligned_signals': 0,
            'divergent_signals': 0,
            'trend_reversals': 0
        }
    
    def analyze_multiple_timeframes(self, data_by_tf: Dict[str, List]) -> Dict:
        """
        Analyze multiple timeframes
        
        Args:
            data_by_tf: {' 5m': ohlcv, '15m': ohlcv, ...}
        """
        if not data_by_tf:
            return {'error': 'No timeframe data provided'}
        
        tf_analysis = {}
        
        # Analyze each timeframe
        for tf, ohlcv in data_by_tf.items():
            if len(ohlcv) < 20:
                continue
            
            closes = np.array([c[4] for c in ohlcv])
            
            # Calculate trend for this TF
            trend = self._calculate_trend(closes)
            strength = self._calculate_trend_strength(closes)
            momentum = self._calculate_momentum(closes)
            
            tf_analysis[tf] = {
                'trend': trend,
                'strength': strength,
                'momentum': momentum
            }
        
        # Check for alignment
        alignment = self._check_alignment(tf_analysis)
        
        # Generate master signal
        signal, confidence = self._generate_mtf_signal(tf_analysis, alignment)
        
        return {
            'timeframes': tf_analysis,
            'alignment': alignment,
            'signal': signal,
            'confidence': confidence,
            'strength': confidence * 100,
            'reason': self._get_reason(alignment, tf_analysis),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_trend(self, closes) -> str:
        """Determine trend direction"""
        sma_20 = np.mean(closes[-20:])
        sma_50 = np.mean(closes[-min(50, len(closes)):])
        current = closes[-1]
        
        if current > sma_20 > sma_50:
            return 'UPTREND'
        elif current < sma_20 < sma_50:
            return 'DOWNTREND'
        return 'SIDEWAYS'
    
    def _calculate_trend_strength(self, closes) -> float:
        """Calculate trend strength (0-100)"""
        if len(closes) < 20:
            return 0
        
        # Linear regression slope
        x = np.arange(len(closes[-20:]))
        y = closes[-20:]
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalize to 0-100
        strength = min(abs(slope) / np.mean(y) * 1000, 100)
        return strength
    
    def _calculate_momentum(self, closes) -> float:
        """Calculate momentum (ROC)"""
        if len(closes) < 10:
            return 0
        
        roc = ((closes[-1] - closes[-10]) / closes[-10]) * 100
        return roc
    
    def _check_alignment(self, tf_analysis: Dict) -> Dict:
        """Check if all timeframes align"""
        if not tf_analysis:
            return {'aligned': False, 'direction': None, 'score': 0}
        
        bullish = sum(1 for tf_data in tf_analysis.values() if tf_data['trend'] == 'UPTREND')
        bearish = sum(1 for tf_data in tf_analysis.values() if tf_data['trend'] == 'DOWNTREND')
        total = len(tf_analysis)
        
        if bullish >= total * 0.8:
            return {'aligned': True, 'direction': 'BULLISH', 'score': (bullish / total) * 100}
        elif bearish >= total * 0.8:
            return {'aligned': True, 'direction': 'BEARISH', 'score': (bearish / total) * 100}
        
        return {'aligned': False, 'direction': 'MIXED', 'score': max(bullish, bearish) / total * 100}
    
    def _generate_mtf_signal(self, tf_analysis: Dict, alignment: Dict) -> tuple:
        """Generate signal from MTF analysis"""
        
        # Perfect alignment = high confidence
        if alignment['aligned']:
            self.metrics['aligned_signals'] += 1
            
            if alignment['direction'] == 'BULLISH':
                return ('BUY', 0.90)
            elif alignment['direction'] == 'BEARISH':
                return ('SELL', 0.90)
        
        # Partial alignment
        if alignment['score'] >= 60:
            bullish = sum(1 for tf_data in tf_analysis.values() if tf_data['trend'] == 'UPTREND')
            bearish = sum(1 for tf_data in tf_analysis.values() if tf_data['trend'] == 'DOWNTREND')
            
            if bullish > bearish:
                return ('BUY', 0.70)
            elif bearish > bullish:
                return ('SELL', 0.70)
        
        self.metrics['divergent_signals'] += 1
        return ('HOLD', 0.0)
    
    def _get_reason(self, alignment: Dict, tf_analysis: Dict) -> str:
        """Get human-readable reason"""
        if alignment['aligned']:
            return f"All timeframes aligned {alignment['direction']} ({alignment['score']:.0f}%)"
        
        bullish = sum(1 for tf_data in tf_analysis.values() if tf_data['trend'] == 'UPTREND')
        bearish = sum(1 for tf_data in tf_analysis.values() if tf_data['trend'] == 'DOWNTREND')
        
        return f"Mixed signals: {bullish} bullish, {bearish} bearish TFs"
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'timeframes': self.timeframes,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = MultiTimeframeBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
