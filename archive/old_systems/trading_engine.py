#!/usr/bin/env python3
"""
UNIFIED TRADING ENGINE
All features integrated into proper layers - NO MORE ISOLATED BOTS
"""

import numpy as np
from datetime import datetime
from typing import Dict, List
import ccxt

class TradingEngine:
    """Unified trading engine with all features integrated"""
    
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
        self.name = "Unified_Trading_Engine"
        self.version = "3.0.0"
        
        # Initialize integrated layers
        self.analysis = MarketAnalysisLayer()
        self.signals = SignalGenerationLayer()
        self.execution = ExecutionLayer(exchange)
        self.risk = RiskManagementLayer()
        
        self.metrics = {'decisions': 0, 'trades': 0}
    
    def process_market_data(self, symbol: str, ohlcv: List) -> Dict:
        """Process market data through all layers"""
        
        # Layer 1: Market Analysis
        analysis = self.analysis.analyze_comprehensive(ohlcv)
        
        # Layer 2: Signal Generation
        signals = self.signals.generate_unified_signal(analysis)
        
        # Layer 3: Risk Check
        risk_check = self.risk.validate_trade(signals, analysis)
        
        # Layer 4: Execution (if approved)
        if risk_check['approved']:
            execution_plan = self.execution.plan_execution(symbol, signals, risk_check)
            return execution_plan
        
        return {'action': 'HOLD', 'reason': risk_check.get('reason', 'Risk check failed')}

class MarketAnalysisLayer:
    """Comprehensive market analysis - all indicators integrated"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.patterns = PatternRecognition()
        self.sentiment = SentimentAnalysis()
    
    def analyze_comprehensive(self, ohlcv: List) -> Dict:
        """Run all analysis methods"""
        if len(ohlcv) < 50:
            return {'error': 'Insufficient data'}
        
        return {
            'technical': self.indicators.calculate_all(ohlcv),
            'patterns': self.patterns.detect_all(ohlcv),
            'sentiment': self.sentiment.aggregate_sentiment(),
            'timestamp': datetime.now().isoformat()
        }

class TechnicalIndicators:
    """All technical indicators in one place"""
    
    def calculate_all(self, ohlcv: List) -> Dict:
        """Calculate all indicators at once"""
        closes = np.array([c[4] for c in ohlcv])
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        volumes = np.array([c[5] for c in ohlcv])
        
        return {
            'trend': self._trend_indicators(closes, highs, lows),
            'momentum': self._momentum_indicators(closes),
            'volatility': self._volatility_indicators(closes, highs, lows),
            'volume': self._volume_indicators(volumes, closes)
        }
    
    def _trend_indicators(self, closes, highs, lows) -> Dict:
        """All trend indicators"""
        sma_20 = closes[-20:].mean()
        sma_50 = closes[-50:].mean() if len(closes) >= 50 else sma_20
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'trend': 'UP' if sma_20 > sma_50 else 'DOWN',
            'price_vs_sma': (closes[-1] - sma_20) / sma_20
        }
    
    def _momentum_indicators(self, closes) -> Dict:
        """All momentum indicators"""
        if len(closes) < 14:
            return {}
        
        # RSI
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = gains[-14:].mean()
        avg_loss = losses[-14:].mean()
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = closes[-12:].mean()
        ema_26 = closes[-26:].mean() if len(closes) >= 26 else ema_12
        macd = ema_12 - ema_26
        
        return {
            'rsi': rsi,
            'macd': macd,
            'momentum': (closes[-1] - closes[-10]) / closes[-10] if len(closes) > 10 else 0
        }
    
    def _volatility_indicators(self, closes, highs, lows) -> Dict:
        """All volatility indicators"""
        # ATR
        tr = np.maximum(highs[1:] - lows[1:], 
                       np.maximum(abs(highs[1:] - closes[:-1]), 
                                 abs(lows[1:] - closes[:-1])))
        atr = tr[-14:].mean() if len(tr) >= 14 else tr.mean()
        
        # Bollinger Bands
        sma = closes[-20:].mean()
        std = closes[-20:].std()
        bb_upper = sma + 2 * std
        bb_lower = sma - 2 * std
        
        return {
            'atr': atr,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'volatility': std / sma
        }
    
    def _volume_indicators(self, volumes, closes) -> Dict:
        """All volume indicators"""
        avg_vol = volumes[-20:].mean()
        current_vol = volumes[-1]
        
        return {
            'volume_ratio': current_vol / avg_vol if avg_vol > 0 else 1,
            'volume_trend': 'INCREASING' if volumes[-5:].mean() > volumes[-20:-5].mean() else 'DECREASING'
        }

class PatternRecognition:
    """Pattern detection integrated"""
    
    def detect_all(self, ohlcv: List) -> Dict:
        """Detect all patterns"""
        return {
            'support_resistance': self._find_sr_levels(ohlcv),
            'candlestick': self._detect_candlestick_patterns(ohlcv[-3:]),
            'chart_patterns': self._detect_chart_patterns(ohlcv)
        }
    
    def _find_sr_levels(self, ohlcv: List) -> Dict:
        """Find support/resistance"""
        highs = [c[2] for c in ohlcv]
        lows = [c[3] for c in ohlcv]
        current = ohlcv[-1][4]
        
        resistance = max(highs[-20:]) if len(highs) >= 20 else max(highs)
        support = min(lows[-20:]) if len(lows) >= 20 else min(lows)
        
        return {'resistance': resistance, 'support': support, 'current': current}
    
    def _detect_candlestick_patterns(self, recent_candles: List) -> List:
        """Detect candlestick patterns"""
        patterns = []
        if not recent_candles:
            return patterns
        
        last = recent_candles[-1]
        body = abs(last[4] - last[1])
        range_total = last[2] - last[3]
        
        if body < range_total * 0.1:
            patterns.append('DOJI')
        
        return patterns
    
    def _detect_chart_patterns(self, ohlcv: List) -> List:
        """Detect chart patterns"""
        # Simplified - could expand
        return []

class SentimentAnalysis:
    """Sentiment aggregation"""
    
    def aggregate_sentiment(self) -> Dict:
        """Aggregate all sentiment sources"""
        # Placeholder - integrate sentiment bots here
        return {
            'overall': 'NEUTRAL',
            'score': 0,
            'sources': 0
        }

class SignalGenerationLayer:
    """Generate unified trading signals"""
    
    def generate_unified_signal(self, analysis: Dict) -> Dict:
        """Combine all analysis into single signal"""
        tech = analysis.get('technical', {})
        patterns = analysis.get('patterns', {})
        
        signals = []
        weights = []
        
        # Technical indicators
        trend = tech.get('trend', {})
        momentum = tech.get('momentum', {})
        
        if trend.get('trend') == 'UP':
            signals.append('BUY')
            weights.append(0.3)
        elif trend.get('trend') == 'DOWN':
            signals.append('SELL')
            weights.append(0.3)
        
        rsi = momentum.get('rsi', 50)
        if rsi < 30:
            signals.append('BUY')
            weights.append(0.4)
        elif rsi > 70:
            signals.append('SELL')
            weights.append(0.4)
        
        # Aggregate
        buy_weight = sum(w for s, w in zip(signals, weights) if s == 'BUY')
        sell_weight = sum(w for s, w in zip(signals, weights) if s == 'SELL')
        
        if buy_weight > sell_weight and buy_weight > 0.5:
            return {'signal': 'BUY', 'confidence': buy_weight}
        elif sell_weight > buy_weight and sell_weight > 0.5:
            return {'signal': 'SELL', 'confidence': sell_weight}
        else:
            return {'signal': 'HOLD', 'confidence': 0.5}

class RiskManagementLayer:
    """Integrated risk management"""
    
    def __init__(self):
        self.max_position_pct = 0.10
        self.max_risk_per_trade = 0.02
    
    def validate_trade(self, signals: Dict, analysis: Dict) -> Dict:
        """Validate trade against risk rules"""
        
        # Check confidence
        if signals.get('confidence', 0) < 0.65:
            return {'approved': False, 'reason': 'Low confidence'}
        
        # Check volatility
        vol = analysis.get('technical', {}).get('volatility', {}).get('volatility', 0)
        if vol > 0.05:
            return {'approved': False, 'reason': 'High volatility'}
        
        return {
            'approved': True,
            'position_size': self.max_position_pct,
            'stop_loss': self.max_risk_per_trade
        }

class ExecutionLayer:
    """Trade execution"""
    
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
    
    def plan_execution(self, symbol: str, signals: Dict, risk: Dict) -> Dict:
        """Plan trade execution"""
        return {
            'symbol': symbol,
            'signal': signals.get('signal'),
            'confidence': signals.get('confidence'),
            'position_size': risk.get('position_size'),
            'execution_method': 'MARKET',  # Could use VWAP, TWAP, etc.
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    print("✅ Unified Trading Engine v3.0 - Integrated Layers")
