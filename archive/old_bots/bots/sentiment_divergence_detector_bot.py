#!/usr/bin/env python3
"""Sentiment Divergence Detector - Detect sentiment vs price divergences"""
from datetime import datetime
from typing import Dict

class SentimentDivergenceDetectorBot:
    def __init__(self):
        self.name = "Sentiment_Divergence_Detector"
        self.version = "1.0.0"
        self.enabled = True
        
        self.metrics = {'divergences': 0, 'signals': 0}
    
    def detect_divergence(self, price_trend: float, sentiment_score: float,
                         volume_trend: float) -> Dict:
        """Detect price vs sentiment divergence"""
        
        # Normalize inputs (-1 to 1)
        # price_trend: positive = uptrend, negative = downtrend
        # sentiment_score: positive = bullish, negative = bearish
        
        divergence_score = abs(price_trend - sentiment_score)
        
        # Strong divergence if score > 1.0
        if divergence_score > 1.0:
            self.metrics['divergences'] += 1
            
            # Bearish divergence: Price up but sentiment down
            if price_trend > 0 and sentiment_score < -0.3:
                divergence_type = 'BEARISH'
                signal = 'SELL'
                confidence = 0.75
                reason = "Bearish divergence: Price rising but sentiment declining"
            
            # Bullish divergence: Price down but sentiment up
            elif price_trend < 0 and sentiment_score > 0.3:
                divergence_type = 'BULLISH'
                signal = 'BUY'
                confidence = 0.75
                reason = "Bullish divergence: Price falling but sentiment improving"
            
            # Extreme fear (contrarian buy)
            elif price_trend < -0.5 and sentiment_score < -0.7:
                divergence_type = 'EXTREME_FEAR'
                signal = 'BUY'
                confidence = 0.80
                reason = "Extreme fear - contrarian buy opportunity"
            
            # Extreme greed (contrarian sell)
            elif price_trend > 0.5 and sentiment_score > 0.7:
                divergence_type = 'EXTREME_GREED'
                signal = 'SELL'
                confidence = 0.80
                reason = "Extreme greed - contrarian sell opportunity"
            
            else:
                divergence_type = 'UNCLEAR'
                signal = 'HOLD'
                confidence = 0.50
                reason = "Divergence detected but unclear direction"
            
            # Increase confidence with volume confirmation
            if volume_trend > 0.3 and signal == 'BUY':
                confidence = min(0.90, confidence + 0.10)
            elif volume_trend > 0.3 and signal == 'SELL':
                confidence = min(0.90, confidence + 0.10)
            
            self.metrics['signals'] += 1
            
            return {
                'divergence_detected': True,
                'divergence_type': divergence_type,
                'divergence_score': divergence_score,
                'price_trend': price_trend,
                'sentiment_score': sentiment_score,
                'volume_trend': volume_trend,
                'signal': signal,
                'confidence': confidence,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'divergence_detected': False,
            'divergence_score': divergence_score,
            'reason': 'No significant divergence'
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = SentimentDivergenceDetectorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
