#!/usr/bin/env python3
"""
Organism Brain - Central Intelligence System

The brain processes all market data, makes decisions, and coordinates
all other systems. It's the consciousness of the trading organism.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class MarketRegime(Enum):
    """Market regime states"""
    STRONG_TREND = "strong_trend"
    WEAK_TREND = "weak_trend"
    RANGING = "ranging"
    BREAKOUT_SETUP = "breakout_setup"
    HIGH_VOLATILITY = "high_volatility"
    UNCERTAIN = "uncertain"


class OrganismBrain:
    """
    Central intelligence coordinating all systems
    
    Unlike 400 separate bots, this is ONE unified brain
    with 12 specialized cognitive modules working together
    """
    
    def __init__(self):
        self.logger = logger
        self.state = {
            'consciousness_level': 1.0,  # How active/confident
            'current_regime': MarketRegime.UNCERTAIN,
            'market_memory': [],  # Recent market states
            'decision_history': [],  # Past decisions
            'learning_rate': 0.1,
        }
        
        # Cognitive modules (12 specialized processors)
        self.modules = {
            # PERCEPTION
            'market_sensor': self._init_market_sensor(),
            'sentiment_processor': self._init_sentiment_processor(),
            'pattern_recognizer': self._init_pattern_recognizer(),
            
            # COGNITION
            'strategy_selector': self._init_strategy_selector(),
            'risk_assessor': self._init_risk_assessor(),
            'confidence_calculator': self._init_confidence_calculator(),
            
            # EXECUTION
            'position_sizer': self._init_position_sizer(),
            'order_executor': self._init_order_executor(),
            'portfolio_manager': self._init_portfolio_manager(),
            
            # LEARNING
            'performance_analyzer': self._init_performance_analyzer(),
            'strategy_evolver': self._init_strategy_evolver(),
            'meta_learner': self._init_meta_learner(),
        }
        
        logger.info("🧠 Organism Brain initialized - Consciousness online")
    
    def _init_market_sensor(self) -> Dict:
        """Module 1: Perceives market conditions"""
        return {
            'name': 'Market Sensor',
            'function': 'detect_regime',
            'state': 'active'
        }
    
    def _init_sentiment_processor(self) -> Dict:
        """Module 2: Processes sentiment data"""
        return {
            'name': 'Sentiment Processor',
            'function': 'analyze_sentiment',
            'state': 'active'
        }
    
    def _init_pattern_recognizer(self) -> Dict:
        """Module 3: Recognizes price patterns"""
        return {
            'name': 'Pattern Recognizer',
            'function': 'identify_patterns',
            'state': 'active'
        }
    
    def _init_strategy_selector(self) -> Dict:
        """Module 4: Selects best strategy for conditions"""
        return {
            'name': 'Strategy Selector',
            'function': 'select_strategy',
            'state': 'active'
        }
    
    def _init_risk_assessor(self) -> Dict:
        """Module 5: Assesses trade risk"""
        return {
            'name': 'Risk Assessor',
            'function': 'assess_risk',
            'state': 'active'
        }
    
    def _init_confidence_calculator(self) -> Dict:
        """Module 6: Calculates confidence scores"""
        return {
            'name': 'Confidence Calculator',
            'function': 'calculate_confidence',
            'state': 'active'
        }
    
    def _init_position_sizer(self) -> Dict:
        """Module 7: Determines position sizes"""
        return {
            'name': 'Position Sizer',
            'function': 'size_position',
            'state': 'active'
        }
    
    def _init_order_executor(self) -> Dict:
        """Module 8: Executes orders"""
        return {
            'name': 'Order Executor',
            'function': 'execute_order',
            'state': 'active'
        }
    
    def _init_portfolio_manager(self) -> Dict:
        """Module 9: Manages portfolio"""
        return {
            'name': 'Portfolio Manager',
            'function': 'manage_portfolio',
            'state': 'active'
        }
    
    def _init_performance_analyzer(self) -> Dict:
        """Module 10: Analyzes performance"""
        return {
            'name': 'Performance Analyzer',
            'function': 'analyze_performance',
            'state': 'active'
        }
    
    def _init_strategy_evolver(self) -> Dict:
        """Module 11: Evolves strategies"""
        return {
            'name': 'Strategy Evolver',
            'function': 'evolve_strategies',
            'state': 'active'
        }
    
    def _init_meta_learner(self) -> Dict:
        """Module 12: Learns how to learn better"""
        return {
            'name': 'Meta Learner',
            'function': 'meta_learn',
            'state': 'active'
        }
    
    def detect_market_regime(self, market_data: Dict) -> MarketRegime:
        """
        Detect current market regime
        
        This is like the organism sensing its environment
        
        Args:
            market_data: Current market state
            
        Returns:
            Detected market regime
        """
        try:
            # Calculate key metrics
            volatility = self._calculate_volatility(market_data)
            trend_strength = self._calculate_trend_strength(market_data)
            volume_profile = self._analyze_volume(market_data)
            
            # Regime detection logic
            if trend_strength > 0.7 and volatility < 0.05:
                regime = MarketRegime.STRONG_TREND
            elif trend_strength > 0.4 and volatility < 0.08:
                regime = MarketRegime.WEAK_TREND
            elif volatility > 0.10:
                regime = MarketRegime.HIGH_VOLATILITY
            elif self._detect_consolidation(market_data):
                regime = MarketRegime.BREAKOUT_SETUP
            elif volatility < 0.05 and trend_strength < 0.3:
                regime = MarketRegime.RANGING
            else:
                regime = MarketRegime.UNCERTAIN
            
            # Update organism state
            self.state['current_regime'] = regime
            logger.info(f"Market regime detected: {regime.value}")
            
            return regime
            
        except Exception as e:
            logger.error(f"Regime detection error: {e}")
            return MarketRegime.UNCERTAIN
    
    def _calculate_volatility(self, market_data: Dict) -> float:
        """Calculate market volatility"""
        # Placeholder - implement with real market data
        return 0.05
    
    def _calculate_trend_strength(self, market_data: Dict) -> float:
        """Calculate trend strength (0-1)"""
        # Placeholder - implement ADX or similar
        return 0.5
    
    def _analyze_volume(self, market_data: Dict) -> Dict:
        """Analyze volume profile"""
        # Placeholder
        return {'average': 1000, 'current': 1200}
    
    def _detect_consolidation(self, market_data: Dict) -> bool:
        """Detect consolidation/squeeze pattern"""
        # Placeholder - implement Bollinger Band squeeze
        return False
    
    def process_information(self, market_data: Dict) -> Dict[str, Any]:
        """
        Process all information like a brain processes sensory input
        
        Args:
            market_data: Raw market information
            
        Returns:
            Processed decision data
        """
        # Perception phase
        regime = self.detect_market_regime(market_data)
        sentiment = self._process_sentiment(market_data)
        patterns = self._recognize_patterns(market_data)
        
        # Cognition phase
        strategy = self._select_strategy(regime, sentiment, patterns)
        risk_level = self._assess_risk(market_data, strategy)
        confidence = self._calculate_confidence(strategy, risk_level, sentiment)
        
        # Decision synthesis
        decision = {
            'regime': regime,
            'strategy': strategy,
            'confidence': confidence,
            'risk_level': risk_level,
            'sentiment': sentiment,
            'patterns': patterns,
            'timestamp': datetime.now(),
            'consciousness_level': self.state['consciousness_level']
        }
        
        # Store in memory
        self.state['decision_history'].append(decision)
        
        return decision
    
    def _process_sentiment(self, market_data: Dict) -> float:
        """Process market sentiment (-1 to 1)"""
        # Integrate with SIUL sentiment module
        return 0.0
    
    def _recognize_patterns(self, market_data: Dict) -> List[str]:
        """Recognize chart patterns"""
        # Integrate with SIUL pattern detector
        return []
    
    def _select_strategy(self, regime: MarketRegime, sentiment: float, 
                        patterns: List[str]) -> str:
        """
        Select optimal strategy for current conditions
        
        This is the organism deciding HOW to act
        """
        if regime == MarketRegime.STRONG_TREND:
            return 'trend_following'
        elif regime == MarketRegime.RANGING:
            return 'mean_reversion'
        elif regime == MarketRegime.BREAKOUT_SETUP:
            return 'breakout'
        elif regime == MarketRegime.HIGH_VOLATILITY:
            return 'arbitrage' if sentiment > 0 else 'cash'
        elif regime == MarketRegime.WEAK_TREND and sentiment > 0.5:
            return 'momentum'
        else:
            return 'conservative'
    
    def _assess_risk(self, market_data: Dict, strategy: str) -> float:
        """Assess risk level (0-1)"""
        base_risk = {
            'trend_following': 0.3,
            'mean_reversion': 0.4,
            'breakout': 0.5,
            'momentum': 0.6,
            'arbitrage': 0.2,
            'conservative': 0.1,
            'cash': 0.0
        }.get(strategy, 0.5)
        
        # Adjust for market conditions
        volatility = self._calculate_volatility(market_data)
        adjusted_risk = base_risk * (1 + volatility)
        
        return min(adjusted_risk, 1.0)
    
    def _calculate_confidence(self, strategy: str, risk_level: float, 
                            sentiment: float) -> float:
        """
        Calculate confidence in decision (0-1)
        
        This is the organism's certainty level
        """
        # Base confidence from strategy
        base_confidence = {
            'trend_following': 0.70,
            'mean_reversion': 0.75,
            'breakout': 0.60,
            'momentum': 0.65,
            'arbitrage': 0.85,
            'conservative': 0.50,
            'cash': 1.00
        }.get(strategy, 0.50)
        
        # Adjust for risk (lower risk = higher confidence)
        risk_adjustment = (1 - risk_level) * 0.2
        
        # Adjust for sentiment alignment
        sentiment_adjustment = abs(sentiment) * 0.1
        
        confidence = base_confidence + risk_adjustment + sentiment_adjustment
        
        return min(confidence, 0.95)  # Cap at 95%
    
    def adapt_to_performance(self, performance_data: Dict):
        """
        Adapt organism behavior based on performance
        
        This is how the organism LEARNS and EVOLVES
        """
        try:
            # Extract key metrics
            win_rate = performance_data.get('win_rate', 0.5)
            sharpe = performance_data.get('sharpe_ratio', 1.0)
            drawdown = performance_data.get('max_drawdown', 0.0)
            
            # Adapt consciousness level
            if win_rate > 0.60 and sharpe > 1.5:
                # Performing well - increase aggression slightly
                self.state['consciousness_level'] = min(
                    self.state['consciousness_level'] * 1.05, 
                    1.2
                )
                logger.info(f"🧠 Organism confidence increased to {self.state['consciousness_level']:.2f}")
                
            elif win_rate < 0.45 or drawdown > 0.12:
                # Performing poorly - reduce aggression
                self.state['consciousness_level'] = max(
                    self.state['consciousness_level'] * 0.90,
                    0.5
                )
                logger.warning(f"🧠 Organism reducing activity to {self.state['consciousness_level']:.2f}")
            
            # Adapt learning rate
            if sharpe > 2.0:
                # Great performance - learn slower (don't mess with success)
                self.state['learning_rate'] = 0.05
            elif sharpe < 1.0:
                # Poor performance - learn faster (need to adapt)
                self.state['learning_rate'] = 0.20
            
            logger.info(f"🧠 Organism adapted - Consciousness: {self.state['consciousness_level']:.2f}, "
                       f"Learning rate: {self.state['learning_rate']:.2f}")
            
        except Exception as e:
            logger.error(f"Adaptation error: {e}")
    
    def get_consciousness_state(self) -> Dict:
        """
        Return current consciousness state
        
        This shows the organism's current "awareness" and activity level
        """
        return {
            'consciousness_level': self.state['consciousness_level'],
            'current_regime': self.state['current_regime'].value,
            'decisions_made': len(self.state['decision_history']),
            'learning_rate': self.state['learning_rate'],
            'active_modules': len([m for m in self.modules.values() if m['state'] == 'active']),
            'status': 'fully_conscious' if self.state['consciousness_level'] > 0.8 else 'adaptive_mode'
        }


# Global brain instance - the organism's consciousness
organism_brain = OrganismBrain()
