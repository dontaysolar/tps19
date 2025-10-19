#!/usr/bin/env python3
"""
Powers AI - Energy & Momentum Management
Manages system energy levels and trading intensity
Controls when to be aggressive vs conservative
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class PowersAI:
    def __init__(self):
        self.name = "Powers_AI"
        self.version = "1.0.0"
        self.enabled = True
        self.power_level = 91
        
        self.energy_level = 100  # 0-100
        self.momentum_state = 'NEUTRAL'
        
        self.metrics = {
            'energy_adjustments': 0,
            'momentum_shifts': 0,
            'peak_energy': 100,
            'low_energy': 100
        }
    
    def assess_market_energy(self, ohlcv: List, performance: Dict) -> Dict:
        """
        Assess market energy and momentum
        Determines trading intensity
        """
        if len(ohlcv) < 20:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv[-50:]])
        volumes = np.array([c[5] for c in ohlcv[-50:]])
        
        # Market momentum
        momentum = (closes[-1] - closes[-10]) / closes[-10] * 100
        
        # Volatility
        volatility = np.std(closes[-20:]) / np.mean(closes[-20:]) * 100
        
        # Volume trend
        recent_volume = np.mean(volumes[-10:])
        historical_volume = np.mean(volumes[-50:-10])
        volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 1
        
        # Performance factor
        win_rate = performance.get('win_rate', 0.5)
        recent_pnl = performance.get('recent_pnl', 0)
        
        # Calculate energy level
        energy_score = 50  # Base
        
        # Add momentum component
        if abs(momentum) > 5:
            energy_score += 20
        elif abs(momentum) > 2:
            energy_score += 10
        
        # Add volume component
        if volume_ratio > 1.5:
            energy_score += 15
        elif volume_ratio > 1.2:
            energy_score += 10
        
        # Add performance component
        if win_rate > 0.65:
            energy_score += 15
        elif win_rate > 0.55:
            energy_score += 10
        
        # Subtract for high volatility (uncertainty)
        if volatility > 5:
            energy_score -= 15
        elif volatility > 3:
            energy_score -= 10
        
        # Adjust for recent losses
        if recent_pnl < 0:
            energy_score -= 20
        
        energy_score = max(0, min(100, energy_score))
        
        # Update energy level (smoothed)
        self.energy_level = 0.7 * self.energy_level + 0.3 * energy_score
        
        # Determine momentum state
        if momentum > 3:
            new_state = 'BULLISH'
        elif momentum < -3:
            new_state = 'BEARISH'
        else:
            new_state = 'NEUTRAL'
        
        if new_state != self.momentum_state:
            self.metrics['momentum_shifts'] += 1
            self.momentum_state = new_state
        
        # Track extremes
        self.metrics['peak_energy'] = max(self.metrics['peak_energy'], self.energy_level)
        self.metrics['low_energy'] = min(self.metrics['low_energy'], self.energy_level)
        self.metrics['energy_adjustments'] += 1
        
        # Generate recommendations
        recommendations = self._generate_energy_recommendations(self.energy_level, self.momentum_state)
        
        return {
            'energy_level': self.energy_level,
            'momentum_state': self.momentum_state,
            'momentum_value': momentum,
            'volatility': volatility,
            'volume_ratio': volume_ratio,
            'trading_intensity': self._get_intensity_level(self.energy_level),
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_intensity_level(self, energy: float) -> str:
        """Convert energy to intensity level"""
        if energy >= 80:
            return 'MAXIMUM'
        elif energy >= 60:
            return 'HIGH'
        elif energy >= 40:
            return 'MEDIUM'
        elif energy >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _generate_energy_recommendations(self, energy: float, momentum: str) -> Dict:
        """Generate trading recommendations based on energy"""
        recommendations = {}
        
        if energy >= 80:
            recommendations['position_size'] = 'INCREASE'
            recommendations['trading_frequency'] = 'HIGH'
            recommendations['risk_level'] = 'AGGRESSIVE'
            recommendations['action'] = 'Scale up winning strategies'
        
        elif energy >= 60:
            recommendations['position_size'] = 'NORMAL'
            recommendations['trading_frequency'] = 'NORMAL'
            recommendations['risk_level'] = 'MODERATE'
            recommendations['action'] = 'Continue normal operations'
        
        elif energy >= 40:
            recommendations['position_size'] = 'REDUCE'
            recommendations['trading_frequency'] = 'SELECTIVE'
            recommendations['risk_level'] = 'CONSERVATIVE'
            recommendations['action'] = 'Be selective, reduce exposure'
        
        elif energy >= 20:
            recommendations['position_size'] = 'MINIMAL'
            recommendations['trading_frequency'] = 'LOW'
            recommendations['risk_level'] = 'DEFENSIVE'
            recommendations['action'] = 'Preserve capital, wait for better conditions'
        
        else:
            recommendations['position_size'] = 'NONE'
            recommendations['trading_frequency'] = 'PAUSE'
            recommendations['risk_level'] = 'STOP'
            recommendations['action'] = 'PAUSE TRADING - Market conditions unfavorable'
        
        # Momentum-based adjustments
        recommendations['momentum_alignment'] = momentum
        if momentum == 'BULLISH':
            recommendations['preferred_direction'] = 'LONG'
        elif momentum == 'BEARISH':
            recommendations['preferred_direction'] = 'SHORT'
        else:
            recommendations['preferred_direction'] = 'BOTH'
        
        return recommendations
    
    def adjust_energy(self, adjustment: float, reason: str = ''):
        """Manually adjust energy level"""
        old_energy = self.energy_level
        self.energy_level = max(0, min(100, self.energy_level + adjustment))
        self.metrics['energy_adjustments'] += 1
        
        return {
            'old_energy': old_energy,
            'new_energy': self.energy_level,
            'adjustment': adjustment,
            'reason': reason
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'power_level': self.power_level,
            'energy_level': self.energy_level,
            'momentum_state': self.momentum_state,
            'intensity': self._get_intensity_level(self.energy_level),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    ai = PowersAI()
    print(f"✅ {ai.name} v{ai.version} - Power Level: {ai.power_level}")
