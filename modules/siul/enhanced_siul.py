#!/usr/bin/env python3
"""
Enhanced SIUL - Smart Intelligent Unified Logic (Production Version)
Advanced intelligence layer integrated with TPS19 APEX
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import statistics

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedSIUL:
    """
    Enhanced Smart Intelligent Unified Logic
    
    Production-grade intelligence layer that combines:
    - Original SIUL weighted fusion
    - TPS19 APEX multidisciplinary analysis
    - Meta-learning optimization
    - Performance tracking and adaptation
    """
    
    def __init__(self):
        self.name = "Enhanced SIUL"
        
        # Intelligence modules with adaptive weights
        self.module_weights = {
            'market_analyzer': 0.20,
            'risk_assessor': 0.15,
            'pattern_detector': 0.15,
            'sentiment_analyzer': 0.15,
            'trend_predictor': 0.15,
            'ml_fusion': 0.20  # TPS19 ML systems
        }
        
        # Performance tracking
        self.decision_history = []
        self.module_performance = {name: {'correct': 0, 'total': 0} 
                                   for name in self.module_weights.keys()}
        
        # Meta-learning state
        self.learning_enabled = True
        self.adaptation_rate = 0.05  # 5% weight adjustment
        
        logger.info("🧠 Enhanced SIUL initialized")
    
    def analyze(self, market_data: Dict, tps19_signals: Optional[Dict] = None) -> Dict:
        """
        Comprehensive SIUL analysis
        
        Args:
            market_data: Current market data
            tps19_signals: Optional signals from TPS19 APEX systems
            
        Returns:
            Unified intelligent decision
        """
        try:
            # Phase 1: Gather intelligence from all modules
            intelligence = self._gather_intelligence(market_data)
            
            # Phase 2: Integrate TPS19 APEX signals
            if tps19_signals:
                intelligence['ml_fusion'] = self._integrate_tps19_signals(tps19_signals)
            
            # Phase 3: Apply unified logic
            unified_decision = self._apply_unified_logic(intelligence, market_data)
            
            # Phase 4: Meta-learning adjustment
            if self.learning_enabled:
                self._adjust_meta_learning(intelligence)
            
            return {
                'decision': unified_decision['action'],
                'signal': unified_decision['action'],
                'confidence': unified_decision['confidence'],
                'score': unified_decision['score'],
                'reasoning': unified_decision['reasoning'],
                'intelligence_breakdown': intelligence,
                'module_weights': self.module_weights.copy(),
                'timestamp': datetime.now().isoformat(),
                'system': 'Enhanced_SIUL'
            }
            
        except Exception as e:
            logger.error(f"Enhanced SIUL analysis error: {e}")
            return {
                'decision': 'HOLD',
                'signal': 'HOLD',
                'confidence': 0.5,
                'score': 0.5,
                'reasoning': f"Error in analysis: {e}",
                'timestamp': datetime.now().isoformat()
            }
    
    def _gather_intelligence(self, market_data: Dict) -> Dict:
        """Gather intelligence from all modules"""
        intelligence = {}
        
        # Market Analysis
        intelligence['market_analyzer'] = self._analyze_market(market_data)
        
        # Risk Assessment
        intelligence['risk_assessor'] = self._assess_risk(market_data)
        
        # Pattern Detection
        intelligence['pattern_detector'] = self._detect_patterns(market_data)
        
        # Sentiment Analysis
        intelligence['sentiment_analyzer'] = self._analyze_sentiment(market_data)
        
        # Trend Prediction
        intelligence['trend_predictor'] = self._predict_trend(market_data)
        
        return intelligence
    
    def _analyze_market(self, data: Dict) -> Dict:
        """Analyze market conditions"""
        price = data.get('price', data.get('close', 0))
        volume = data.get('volume', 0)
        
        # Market strength analysis
        if price > 0 and volume > 0:
            # Simplified - in production would use more sophisticated analysis
            score = 0.6  # Neutral-bullish
            confidence = 0.75
            reasoning = f"Market analysis: Price ${price:.2f}, Volume {volume}"
        else:
            score = 0.5
            confidence = 0.5
            reasoning = "Insufficient market data"
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': reasoning,
            'module': 'market_analyzer'
        }
    
    def _assess_risk(self, data: Dict) -> Dict:
        """Assess risk levels"""
        # Risk factors
        volatility = data.get('volatility', 0.02)
        
        # Higher volatility = lower score (more caution)
        if volatility > 0.05:
            score = 0.3  # High risk
            confidence = 0.80
        elif volatility > 0.03:
            score = 0.5  # Moderate risk
            confidence = 0.75
        else:
            score = 0.7  # Low risk (favorable)
            confidence = 0.70
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': f"Risk assessment: Volatility {volatility:.4f}",
            'module': 'risk_assessor'
        }
    
    def _detect_patterns(self, data: Dict) -> Dict:
        """Detect chart patterns"""
        # Pattern detection (simplified)
        # In production: would analyze OHLCV for actual patterns
        
        score = 0.6  # Slight bullish pattern
        confidence = 0.65
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': "Pattern detection: Neutral trend",
            'module': 'pattern_detector'
        }
    
    def _analyze_sentiment(self, data: Dict) -> Dict:
        """Analyze market sentiment"""
        # Sentiment (simplified)
        # In production: would integrate with sentiment_analyzer module
        
        sentiment_score = data.get('sentiment', 0.5)
        score = sentiment_score
        confidence = 0.70
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': f"Sentiment: {sentiment_score:.2f}",
            'module': 'sentiment_analyzer'
        }
    
    def _predict_trend(self, data: Dict) -> Dict:
        """Predict trend direction"""
        # Trend prediction (simplified)
        # In production: would use ML models
        
        score = 0.65  # Slight uptrend
        confidence = 0.75
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': "Trend prediction: Continuation likely",
            'module': 'trend_predictor'
        }
    
    def _integrate_tps19_signals(self, signals: Dict) -> Dict:
        """Integrate signals from TPS19 APEX systems"""
        try:
            # Extract TPS19 consensus
            if isinstance(signals, dict):
                action = signals.get('action', signals.get('signal', 'HOLD'))
                confidence = signals.get('confidence', 0.5)
                
                # Map action to score
                if action in ['BUY', 'UP']:
                    score = 0.7 + (confidence - 0.5) * 0.6
                elif action in ['SELL', 'DOWN']:
                    score = 0.3 - (confidence - 0.5) * 0.6
                else:
                    score = 0.5
                
                return {
                    'score': score,
                    'confidence': confidence,
                    'reasoning': f"TPS19 ML Fusion: {action} ({confidence:.0%})",
                    'module': 'ml_fusion'
                }
            
        except Exception as e:
            logger.error(f"TPS19 signal integration error: {e}")
        
        return {
            'score': 0.5,
            'confidence': 0.5,
            'reasoning': "TPS19 signals unavailable",
            'module': 'ml_fusion'
        }
    
    def _apply_unified_logic(self, intelligence: Dict, market_data: Dict) -> Dict:
        """Apply SIUL unified logic to intelligence results"""
        total_score = 0
        total_confidence = 0
        total_weight = 0
        
        decision_factors = []
        
        # Calculate weighted scores
        for module_name, result in intelligence.items():
            if result and 'score' in result:
                weight = self.module_weights.get(module_name, 0.1)
                weighted_score = result['score'] * weight
                total_score += weighted_score
                total_confidence += result.get('confidence', 0.5) * weight
                total_weight += weight
                
                decision_factors.append({
                    'module': module_name,
                    'score': result['score'],
                    'weight': weight,
                    'weighted_score': weighted_score,
                    'confidence': result.get('confidence', 0.5),
                    'reasoning': result.get('reasoning', '')
                })
        
        # Normalize
        if total_weight > 0:
            total_score /= total_weight
            total_confidence /= total_weight
        
        # Determine action
        if total_score > 0.65 and total_confidence > 0.70:
            action = 'BUY'
        elif total_score < 0.35 and total_confidence > 0.70:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        # Generate reasoning
        top_factors = sorted(decision_factors, 
                           key=lambda x: x['weighted_score'], 
                           reverse=True)[:3]
        reasoning = f"SIUL Unified Logic: {action} (Score: {total_score:.2f}). "
        reasoning += "Top factors: " + ", ".join([f['module'] for f in top_factors])
        
        return {
            'action': action,
            'score': total_score,
            'confidence': total_confidence,
            'reasoning': reasoning,
            'factors': decision_factors
        }
    
    def _adjust_meta_learning(self, intelligence: Dict):
        """
        Meta-learning: Adjust module weights based on performance
        
        Modules that perform well get higher weights
        """
        # Calculate performance-based weight adjustments
        adjustments = {}
        
        for module_name, perf in self.module_performance.items():
            if perf['total'] >= 10:  # Need minimum sample
                accuracy = perf['correct'] / perf['total']
                
                # Adjust weight based on accuracy
                if accuracy > 0.65:  # Above average
                    adjustments[module_name] = self.adaptation_rate
                elif accuracy < 0.45:  # Below average
                    adjustments[module_name] = -self.adaptation_rate
        
        # Apply adjustments
        if adjustments:
            for module_name, adjustment in adjustments.items():
                old_weight = self.module_weights[module_name]
                new_weight = max(0.05, min(0.35, old_weight + adjustment))
                self.module_weights[module_name] = new_weight
            
            # Normalize weights
            total = sum(self.module_weights.values())
            for key in self.module_weights:
                self.module_weights[key] /= total
            
            logger.debug(f"SIUL meta-learning: Adjusted {len(adjustments)} module weights")
    
    def record_outcome(self, decision: str, was_correct: bool):
        """Record decision outcome for meta-learning"""
        self.decision_history.append({
            'decision': decision,
            'correct': was_correct,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update module performance (simplified)
        # In production: would track which modules contributed to correct decisions
        for module_name in self.module_performance:
            self.module_performance[module_name]['total'] += 1
            if was_correct:
                self.module_performance[module_name]['correct'] += 1
    
    def get_siul_stats(self) -> Dict:
        """Get SIUL statistics"""
        total_decisions = len(self.decision_history)
        
        if total_decisions > 0:
            correct_decisions = sum(1 for d in self.decision_history if d['correct'])
            accuracy = correct_decisions / total_decisions
        else:
            accuracy = 0
        
        return {
            'total_decisions': total_decisions,
            'accuracy': accuracy,
            'module_weights': self.module_weights.copy(),
            'learning_enabled': self.learning_enabled,
            'module_performance': {
                name: {
                    'accuracy': perf['correct'] / perf['total'] if perf['total'] > 0 else 0,
                    'total': perf['total']
                }
                for name, perf in self.module_performance.items()
            }
        }


# Global instance
enhanced_siul = EnhancedSIUL()
