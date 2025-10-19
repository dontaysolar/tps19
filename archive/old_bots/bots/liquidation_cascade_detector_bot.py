#!/usr/bin/env python3
"""Liquidation Cascade Detector - Detect and profit from liquidation events"""
from datetime import datetime
from typing import Dict

class LiquidationCascadeDetectorBot:
    def __init__(self):
        self.name = "Liquidation_Cascade_Detector"
        self.version = "1.0.0"
        self.enabled = True
        
        self.liquidation_threshold = 5000000  # $5M in liquidations
        
        self.metrics = {'cascades_detected': 0, 'alerts': 0}
    
    def detect_cascade(self, recent_liquidations: float, price_change_1min: float,
                      volume_spike: float, open_interest_change: float) -> Dict:
        """Detect liquidation cascade"""
        
        cascade_score = 0
        signals = []
        
        # Large liquidation volume
        if recent_liquidations > self.liquidation_threshold:
            cascade_score += 40
            signals.append(f"${recent_liquidations/1e6:.1f}M liquidations")
        
        # Sharp price movement
        if abs(price_change_1min) > 0.02:  # 2% in 1min
            cascade_score += 30
            signals.append(f"{abs(price_change_1min)*100:.1f}% price move")
        
        # Volume spike
        if volume_spike > 5:  # 5x normal volume
            cascade_score += 20
            signals.append(f"{volume_spike:.1f}x volume spike")
        
        # Open interest drop (liquidations closing positions)
        if open_interest_change < -0.05:  # 5% OI drop
            cascade_score += 10
            signals.append(f"{abs(open_interest_change)*100:.1f}% OI drop")
        
        is_cascade = cascade_score >= 60
        
        if is_cascade:
            self.metrics['cascades_detected'] += 1
            self.metrics['alerts'] += 1
            
            # Determine direction
            if price_change_1min < 0:
                # Downward cascade (long liquidations)
                direction = 'LONG_LIQUIDATIONS'
                signal = 'BUY'  # Buy the dip after cascade
                confidence = 0.80
                reason = "Long liquidation cascade - potential bounce"
            else:
                # Upward cascade (short liquidations)
                direction = 'SHORT_LIQUIDATIONS'
                signal = 'SELL'  # Sell after short squeeze
                confidence = 0.75
                reason = "Short liquidation cascade - potential reversal"
            
            return {
                'cascade_detected': True,
                'cascade_score': cascade_score,
                'direction': direction,
                'signals': signals,
                'liquidation_volume': recent_liquidations,
                'price_change_pct': price_change_1min * 100,
                'signal': signal,
                'confidence': confidence,
                'reason': reason,
                'urgency': 'HIGH',
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'cascade_detected': False,
            'cascade_score': cascade_score,
            'reason': 'Cascade score below threshold'
        }
    
    def estimate_liquidation_levels(self, current_price: float, 
                                   leverage_distribution: Dict) -> Dict:
        """Estimate key liquidation price levels"""
        
        # Common leverage levels
        liquidation_levels = {}
        
        for leverage, position_size in leverage_distribution.items():
            # Long liquidation levels (below current price)
            long_liq_price = current_price * (1 - 1/leverage)
            
            # Short liquidation levels (above current price)
            short_liq_price = current_price * (1 + 1/leverage)
            
            liquidation_levels[f"{leverage}x_LONG"] = {
                'price': long_liq_price,
                'position_size': position_size.get('long', 0),
                'distance_pct': ((current_price - long_liq_price) / current_price) * 100
            }
            
            liquidation_levels[f"{leverage}x_SHORT"] = {
                'price': short_liq_price,
                'position_size': position_size.get('short', 0),
                'distance_pct': ((short_liq_price - current_price) / current_price) * 100
            }
        
        return {
            'current_price': current_price,
            'liquidation_levels': liquidation_levels,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'liquidation_threshold': self.liquidation_threshold,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = LiquidationCascadeDetectorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
