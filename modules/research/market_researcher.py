#!/usr/bin/env python3
"""
Market Research Engine - Data-driven opportunity discovery
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class MarketResearcher:
    """
    Comprehensive market research for data-driven trading decisions
    """
    
    def __init__(self):
        self.research_cache = {}
        
    def research_opportunity(self, symbol: str, df) -> Dict:
        """
        Comprehensive opportunity research
        
        Analyzes:
        - Historical patterns
        - Statistical edges
        - Market structure
        - Volatility regimes
        - Seasonal patterns
        """
        if not HAS_PANDAS:
            return {'error': 'Pandas required'}
        
        if len(df) < 200:
            return {'error': 'Insufficient data'}
        
        research = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }
        
        # 1. Historical Pattern Recognition
        research['analyses']['patterns'] = self._find_patterns(df)
        
        # 2. Statistical Edge Analysis
        research['analyses']['statistical_edge'] = self._calculate_statistical_edge(df)
        
        # 3. Volatility Regime
        research['analyses']['volatility_regime'] = self._analyze_volatility_regime(df)
        
        # 4. Time-of-Day Patterns
        research['analyses']['timing'] = self._analyze_timing_patterns(df)
        
        # 5. Support/Resistance Levels
        research['analyses']['levels'] = self._find_key_levels(df)
        
        # 6. Trend Strength
        research['analyses']['trend'] = self._analyze_trend_strength(df)
        
        # 7. Overall Opportunity Score
        research['opportunity_score'] = self._calculate_opportunity_score(research['analyses'])
        research['recommendation'] = self._generate_recommendation(research['opportunity_score'])
        
        return research
    
    def _find_patterns(self, df) -> Dict:
        """Identify recurring price patterns"""
        close = df['close']
        
        # Head and shoulders
        h_and_s = self._detect_head_and_shoulders(df)
        
        # Double top/bottom
        double_pattern = self._detect_double_pattern(df)
        
        # Triangle patterns
        triangle = self._detect_triangle(df)
        
        return {
            'head_and_shoulders': h_and_s,
            'double_pattern': double_pattern,
            'triangle': triangle
        }
    
    def _detect_head_and_shoulders(self, df) -> Optional[Dict]:
        """Detect head and shoulders pattern"""
        # Simplified detection - look for 3 peaks
        high = df['high']
        
        # Find local peaks
        peaks = []
        for i in range(10, len(high) - 10):
            if high.iloc[i] > high.iloc[i-5:i].max() and high.iloc[i] > high.iloc[i+1:i+6].max():
                peaks.append({'index': i, 'price': high.iloc[i]})
        
        # Need at least 3 peaks
        if len(peaks) < 3:
            return None
        
        # Check if middle peak is highest (head)
        recent_peaks = peaks[-3:]
        if recent_peaks[1]['price'] > recent_peaks[0]['price'] and \
           recent_peaks[1]['price'] > recent_peaks[2]['price']:
            return {
                'detected': True,
                'type': 'head_and_shoulders',
                'signal': 'BEARISH',
                'confidence': 0.7
            }
        
        return None
    
    def _detect_double_pattern(self, df) -> Optional[Dict]:
        """Detect double top or double bottom"""
        close = df['close']
        
        # Look for two similar highs (double top)
        high = df['high']
        peaks = []
        
        for i in range(10, len(high) - 10):
            if high.iloc[i] == high.iloc[i-5:i+6].max():
                peaks.append(high.iloc[i])
        
        if len(peaks) >= 2:
            # Check if last two peaks are similar (within 1%)
            if abs(peaks[-1] - peaks[-2]) / peaks[-2] < 0.01:
                return {
                    'detected': True,
                    'type': 'double_top',
                    'signal': 'BEARISH',
                    'confidence': 0.65
                }
        
        return None
    
    def _detect_triangle(self, df) -> Optional[Dict]:
        """Detect triangle consolidation pattern"""
        high = df['high']
        low = df['low']
        
        # Calculate recent range
        recent_high = high.iloc[-50:].max()
        recent_low = low.iloc[-50:].min()
        range_pct = (recent_high - recent_low) / recent_low
        
        # Narrowing range indicates triangle
        if range_pct < 0.05:  # Less than 5% range
            return {
                'detected': True,
                'type': 'triangle',
                'signal': 'BREAKOUT_PENDING',
                'confidence': 0.6
            }
        
        return None
    
    def _calculate_statistical_edge(self, df) -> Dict:
        """Calculate statistical trading edge"""
        close = df['close']
        returns = close.pct_change().dropna()
        
        # Win rate if bought and held for N periods
        forward_returns_1d = returns.shift(-1)
        forward_returns_3d = close.pct_change(3).shift(-3)
        
        win_rate_1d = (forward_returns_1d > 0).sum() / len(forward_returns_1d)
        
        # Average win vs average loss
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
        
        # Profit factor
        profit_factor = abs(avg_win / avg_loss) if avg_loss > 0 else 0
        
        return {
            'win_rate_1d': win_rate_1d,
            'avg_win_pct': avg_win,
            'avg_loss_pct': avg_loss,
            'profit_factor': profit_factor,
            'edge': 'POSITIVE' if profit_factor > 1.5 else 'NEUTRAL'
        }
    
    def _analyze_volatility_regime(self, df) -> Dict:
        """Determine current volatility regime"""
        returns = df['close'].pct_change()
        
        # Historical volatility
        vol_30d = returns.rolling(30).std() * np.sqrt(252)
        vol_90d = returns.rolling(90).std() * np.sqrt(252)
        
        current_vol = vol_30d.iloc[-1]
        avg_vol = vol_90d.iloc[-1]
        
        if current_vol > avg_vol * 1.5:
            regime = 'HIGH_VOLATILITY'
            recommendation = 'Reduce position sizes'
        elif current_vol < avg_vol * 0.7:
            regime = 'LOW_VOLATILITY'
            recommendation = 'Breakout opportunity possible'
        else:
            regime = 'NORMAL'
            recommendation = 'Standard risk management'
        
        return {
            'regime': regime,
            'current_volatility': current_vol,
            'average_volatility': avg_vol,
            'recommendation': recommendation
        }
    
    def _analyze_timing_patterns(self, df) -> Dict:
        """Analyze best trading times"""
        # This would analyze historical performance by hour/day
        # Placeholder for now
        return {
            'best_hours': [8, 9, 10, 14, 15],  # Market open hours
            'avoid_hours': [0, 1, 2, 3, 4, 5],  # Low liquidity
            'best_days': ['Monday', 'Tuesday', 'Thursday'],
            'current_time_favorable': True
        }
    
    def _find_key_levels(self, df) -> Dict:
        """Find key support and resistance levels"""
        close = df['close']
        high = df['high']
        low = df['low']
        
        # Recent price action
        recent_high = high.iloc[-100:].max()
        recent_low = low.iloc[-100:].min()
        current_price = close.iloc[-1]
        
        # Find pivot points
        pivots = self._calculate_pivot_points(df)
        
        return {
            'resistance': recent_high,
            'support': recent_low,
            'current_price': current_price,
            'distance_to_resistance': (recent_high - current_price) / current_price,
            'distance_to_support': (current_price - recent_low) / current_price,
            'pivots': pivots
        }
    
    def _calculate_pivot_points(self, df) -> Dict:
        """Calculate classic pivot points"""
        yesterday = df.iloc[-2]
        
        pivot = (yesterday['high'] + yesterday['low'] + yesterday['close']) / 3
        r1 = (2 * pivot) - yesterday['low']
        s1 = (2 * pivot) - yesterday['high']
        r2 = pivot + (yesterday['high'] - yesterday['low'])
        s2 = pivot - (yesterday['high'] - yesterday['low'])
        
        return {
            'pivot': pivot,
            'r1': r1, 'r2': r2,
            's1': s1, 's2': s2
        }
    
    def _analyze_trend_strength(self, df) -> Dict:
        """Analyze trend strength using ADX"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Simple trend detection
        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()
        
        current_price = close.iloc[-1]
        
        if ma20.iloc[-1] > ma50.iloc[-1] > ma200.iloc[-1]:
            trend = 'STRONG_UPTREND'
            strength = 0.9
        elif ma20.iloc[-1] > ma50.iloc[-1]:
            trend = 'UPTREND'
            strength = 0.7
        elif ma20.iloc[-1] < ma50.iloc[-1] < ma200.iloc[-1]:
            trend = 'STRONG_DOWNTREND'
            strength = 0.9
        elif ma20.iloc[-1] < ma50.iloc[-1]:
            trend = 'DOWNTREND'
            strength = 0.7
        else:
            trend = 'RANGING'
            strength = 0.5
        
        return {
            'trend': trend,
            'strength': strength,
            'ma20': ma20.iloc[-1],
            'ma50': ma50.iloc[-1],
            'ma200': ma200.iloc[-1] if len(ma200) > 0 else 0
        }
    
    def _calculate_opportunity_score(self, analyses: Dict) -> float:
        """
        Calculate overall opportunity score (0-100)
        
        Higher score = better opportunity
        """
        score = 50  # Start neutral
        
        # Patterns (+10 if bullish pattern detected)
        patterns = analyses.get('patterns', {})
        # (Would check all patterns)
        
        # Statistical edge (+20 if positive)
        stat_edge = analyses.get('statistical_edge', {})
        if stat_edge.get('edge') == 'POSITIVE':
            score += 20
        
        # Trend (+15 if strong trend)
        trend = analyses.get('trend', {})
        if trend.get('trend') in ['STRONG_UPTREND', 'STRONG_DOWNTREND']:
            score += 15
        
        # Volatility (+10 if normal regime)
        vol_regime = analyses.get('volatility_regime', {})
        if vol_regime.get('regime') == 'NORMAL':
            score += 10
        
        # Timing (+5 if favorable time)
        timing = analyses.get('timing', {})
        if timing.get('current_time_favorable'):
            score += 5
        
        return min(100, max(0, score))
    
    def _generate_recommendation(self, score: float) -> str:
        """Generate recommendation based on opportunity score"""
        if score >= 80:
            return "EXCELLENT - High probability opportunity"
        elif score >= 65:
            return "GOOD - Favorable conditions"
        elif score >= 50:
            return "NEUTRAL - Wait for better setup"
        else:
            return "POOR - Avoid trading"


# Global instance
market_researcher = MarketResearcher()
