#!/usr/bin/env python3
"""
Wyckoff Market Cycle Analyzer Bot
Identifies accumulation, markup, distribution, markdown phases
Uses Volume Spread Analysis (VSA) principles
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

class WyckoffAnalyzerBot:
    def __init__(self):
        self.name = "Wyckoff_Analyzer"
        self.version = "1.0.0"
        self.enabled = True
        self.confidence_threshold = 0.70
        
        # Wyckoff phases
        self.phases = ['ACCUMULATION', 'MARKUP', 'DISTRIBUTION', 'MARKDOWN']
        self.current_phase = None
        
        # Key events in each phase
        self.accumulation_events = ['PS', 'SC', 'AR', 'ST', 'SPRING', 'LPS']
        self.distribution_events = ['PSY', 'BC', 'AR', 'ST', 'UTAD', 'LPSY']
        
        self.metrics = {
            'phases_detected': 0,
            'accumulation_zones': 0,
            'distribution_zones': 0,
            'springs_detected': 0,
            'last_phase': None
        }
    
    def analyze_wyckoff_phase(self, ohlcv: List, volume: List) -> Dict:
        """
        Analyze market phase using Wyckoff methodology
        
        Returns:
            phase: Current market phase
            event: Specific Wyckoff event detected
            confidence: 0-1 confidence score
            signal: BUY/SELL/HOLD
        """
        if len(ohlcv) < 100:
            return {'error': 'Insufficient data'}
        
        prices = np.array([candle[4] for candle in ohlcv])  # Close prices
        volumes = np.array(volume)
        highs = np.array([candle[2] for candle in ohlcv])
        lows = np.array([candle[3] for candle in ohlcv])
        
        # Calculate price and volume characteristics
        avg_volume = np.mean(volumes[-50:])
        recent_volume = volumes[-10:]
        
        price_range = highs[-50:] - lows[-50:]
        avg_range = np.mean(price_range)
        
        # Detect phase
        phase, event, confidence = self._detect_phase(prices, volumes, highs, lows)
        
        # Generate signal
        signal = self._generate_wyckoff_signal(phase, event, confidence)
        
        # Update metrics
        if phase:
            self.current_phase = phase
            self.metrics['phases_detected'] += 1
            self.metrics['last_phase'] = phase
            
            if phase == 'ACCUMULATION':
                self.metrics['accumulation_zones'] += 1
            elif phase == 'DISTRIBUTION':
                self.metrics['distribution_zones'] += 1
            
            if event == 'SPRING':
                self.metrics['springs_detected'] += 1
        
        return {
            'phase': phase,
            'event': event,
            'confidence': confidence,
            'signal': signal,
            'strength': self._calculate_signal_strength(phase, event, confidence),
            'reason': f"Wyckoff {phase} phase detected, event: {event}",
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_phase(self, prices, volumes, highs, lows) -> tuple:
        """Detect current Wyckoff phase and event"""
        
        # Trend analysis
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        current_price = prices[-1]
        
        # Volume analysis
        avg_vol = np.mean(volumes[-50:])
        recent_vol = np.mean(volumes[-10:])
        volume_surge = recent_vol > avg_vol * 1.5
        
        # Range analysis
        recent_range = np.max(highs[-20:]) - np.min(lows[-20:])
        consolidation = recent_range < (np.max(highs[-50:]) - np.min(lows[-50:])) * 0.3
        
        # Price position
        price_above_sma20 = current_price > sma_20
        price_above_sma50 = current_price > sma_50
        
        # ACCUMULATION PHASE
        if consolidation and not price_above_sma50:
            # Check for accumulation events
            
            # Spring detection (false breakdown with low volume)
            if self._detect_spring(prices, volumes, lows):
                return ('ACCUMULATION', 'SPRING', 0.85)
            
            # Sign of Strength (SOS) - breakout with volume
            if price_above_sma20 and volume_surge:
                return ('ACCUMULATION', 'SOS', 0.80)
            
            # Last Point of Support (LPS)
            if self._detect_lps(prices, volumes):
                return ('ACCUMULATION', 'LPS', 0.75)
            
            return ('ACCUMULATION', 'PHASE_A', 0.70)
        
        # MARKUP PHASE
        elif price_above_sma50 and sma_20 > sma_50:
            # Strong uptrend
            if volume_surge and prices[-1] > prices[-5]:
                return ('MARKUP', 'THRUST', 0.80)
            return ('MARKUP', 'CONTINUATION', 0.75)
        
        # DISTRIBUTION PHASE
        elif consolidation and price_above_sma50:
            # Check for distribution events
            
            # Upthrust After Distribution (UTAD)
            if self._detect_utad(prices, volumes, highs):
                return ('DISTRIBUTION', 'UTAD', 0.85)
            
            # Sign of Weakness (SOW)
            if not price_above_sma20 and volume_surge:
                return ('DISTRIBUTION', 'SOW', 0.80)
            
            return ('DISTRIBUTION', 'PHASE_C', 0.70)
        
        # MARKDOWN PHASE
        elif not price_above_sma50 and sma_20 < sma_50:
            # Strong downtrend
            if volume_surge and prices[-1] < prices[-5]:
                return ('MARKDOWN', 'SELLING_CLIMAX', 0.80)
            return ('MARKDOWN', 'CONTINUATION', 0.75)
        
        return (None, None, 0.0)
    
    def _detect_spring(self, prices, volumes, lows) -> bool:
        """Detect Spring (false breakdown in accumulation)"""
        recent_low = np.min(lows[-20:-5])
        latest_low = np.min(lows[-5:])
        
        # Price broke below recent low
        if latest_low < recent_low * 0.98:
            # But quickly recovered
            if prices[-1] > recent_low:
                # With declining volume (weak selling)
                if np.mean(volumes[-5:]) < np.mean(volumes[-20:-5]):
                    return True
        return False
    
    def _detect_lps(self, prices, volumes) -> bool:
        """Detect Last Point of Support"""
        # Price pullback to support after breakout
        sma_20 = np.mean(prices[-20:])
        recent_low = np.min(prices[-5:])
        
        if recent_low <= sma_20 and prices[-1] > sma_20:
            # Support held
            return True
        return False
    
    def _detect_utad(self, prices, volumes, highs) -> bool:
        """Detect Upthrust After Distribution"""
        recent_high = np.max(highs[-20:-5])
        latest_high = np.max(highs[-5:])
        
        # Price broke above recent high
        if latest_high > recent_high * 1.02:
            # But quickly rejected
            if prices[-1] < recent_high:
                # With high volume (distribution)
                if np.mean(volumes[-5:]) > np.mean(volumes[-20:-5]):
                    return True
        return False
    
    def _generate_wyckoff_signal(self, phase, event, confidence) -> str:
        """Generate trading signal from Wyckoff analysis"""
        if confidence < self.confidence_threshold:
            return 'HOLD'
        
        # Accumulation signals
        if phase == 'ACCUMULATION':
            if event in ['SPRING', 'LPS', 'SOS']:
                return 'BUY'
        
        # Markup signals
        elif phase == 'MARKUP':
            if event == 'THRUST':
                return 'BUY'
        
        # Distribution signals
        elif phase == 'DISTRIBUTION':
            if event in ['UTAD', 'SOW']:
                return 'SELL'
        
        # Markdown signals
        elif phase == 'MARKDOWN':
            if event == 'SELLING_CLIMAX':
                return 'HOLD'  # Wait for accumulation
        
        return 'HOLD'
    
    def _calculate_signal_strength(self, phase, event, confidence) -> float:
        """Calculate signal strength (0-100)"""
        base_strength = confidence * 100
        
        # Bonus for high-probability events
        if event in ['SPRING', 'UTAD']:
            base_strength += 10
        elif event in ['LPS', 'SOW']:
            base_strength += 5
        
        return min(base_strength, 100)
    
    def get_status(self) -> Dict:
        """Return bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'current_phase': self.current_phase,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = WyckoffAnalyzerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
    print(f"📊 Status: {bot.get_status()}")
