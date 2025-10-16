#!/usr/bin/env python3
"""
Organism Nervous System - Multi-Strategy Coordination

The nervous system coordinates multiple strategies simultaneously,
routing signals to execution pathways like neurons firing.

Instead of 400 competing bots, we have coordinated pathways.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class StrategyPathway:
    """
    A neural pathway for one strategy
    Each pathway can fire (generate signals) independently
    """
    
    def __init__(self, name: str, allocation: float, parameters: Dict):
        self.name = name
        self.allocation = allocation  # % of capital
        self.parameters = parameters
        self.active = True
        self.performance = {
            'trades': 0,
            'wins': 0,
            'total_pnl': 0.0,
            'sharpe': 0.0
        }
    
    def can_fire(self, market_conditions: Dict) -> bool:
        """Check if this pathway should activate"""
        # Each strategy has optimal conditions
        return self.active and self._check_conditions(market_conditions)
    
    def _check_conditions(self, market_conditions: Dict) -> bool:
        """Override in subclasses"""
        return True
    
    def generate_signal(self, market_data: Dict) -> Optional[Dict]:
        """Generate trading signal"""
        # Override in subclasses
        return None
    
    def update_performance(self, trade_result: Dict):
        """Update pathway performance"""
        self.performance['trades'] += 1
        if trade_result.get('pnl', 0) > 0:
            self.performance['wins'] += 1
        self.performance['total_pnl'] += trade_result.get('pnl', 0)


class NervousSystem:
    """
    Coordinates multiple strategy pathways
    
    Like a nervous system routing signals through neurons
    Instead of 400 bots competing, we have coordinated pathways
    """
    
    def __init__(self):
        # Initialize strategy pathways (our "neurons")
        self.pathways = {
            'trend_following': self._init_trend_pathway(),
            'mean_reversion': self._init_reversion_pathway(),
            'breakout': self._init_breakout_pathway(),
            'momentum': self._init_momentum_pathway(),
            'arbitrage': self._init_arbitrage_pathway(),
        }
        
        # Pathway coordination state
        self.signal_queue = []
        self.active_pathways = set()
        self.pathway_cooldowns = {}
        
        logger.info(f"⚡ Nervous System initialized - {len(self.pathways)} pathways active")
    
    def _init_trend_pathway(self) -> StrategyPathway:
        """Trend following pathway"""
        return StrategyPathway(
            name='trend_following',
            allocation=0.40,  # 40% of capital
            parameters={
                'ma_fast': 20,
                'ma_slow': 50,
                'ma_trend': 200,
                'min_trend_strength': 0.6,
                'rsi_threshold': 50,
            }
        )
    
    def _init_reversion_pathway(self) -> StrategyPathway:
        """Mean reversion pathway"""
        return StrategyPathway(
            name='mean_reversion',
            allocation=0.30,  # 30% of capital
            parameters={
                'bb_period': 20,
                'bb_std': 2.0,
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'z_score_threshold': 2.0,
            }
        )
    
    def _init_breakout_pathway(self) -> StrategyPathway:
        """Breakout pathway"""
        return StrategyPathway(
            name='breakout',
            allocation=0.15,  # 15% of capital
            parameters={
                'consolidation_days': 5,
                'volume_spike_threshold': 1.5,
                'breakout_confirmation': True,
            }
        )
    
    def _init_momentum_pathway(self) -> StrategyPathway:
        """Momentum pathway"""
        return StrategyPathway(
            name='momentum',
            allocation=0.10,  # 10% of capital
            parameters={
                'consecutive_gains': 3,
                'volume_trend': 'increasing',
                'rsi_momentum': 60,
            }
        )
    
    def _init_arbitrage_pathway(self) -> StrategyPathway:
        """Arbitrage pathway (low risk)"""
        return StrategyPathway(
            name='arbitrage',
            allocation=0.05,  # 5% of capital
            parameters={
                'min_spread': 0.003,  # 0.3% minimum
                'max_execution_time': 5,  # seconds
            }
        )
    
    def process_market_data(self, market_data: Dict) -> List[Dict]:
        """
        Process market data through all pathways
        
        Like sensory input traveling through neurons
        Multiple pathways can fire simultaneously
        
        Args:
            market_data: Current market state
            
        Returns:
            List of signals from active pathways
        """
        signals = []
        market_conditions = self._assess_conditions(market_data)
        
        for pathway_name, pathway in self.pathways.items():
            # Check if pathway can fire
            if not pathway.can_fire(market_conditions):
                continue
            
            # Check cooldown
            if self._is_on_cooldown(pathway_name):
                continue
            
            # Generate signal
            signal = pathway.generate_signal(market_data)
            
            if signal:
                signal['pathway'] = pathway_name
                signal['allocation'] = pathway.allocation
                signals.append(signal)
                logger.info(f"⚡ Pathway {pathway_name} fired signal")
        
        return signals
    
    def _assess_conditions(self, market_data: Dict) -> Dict:
        """Assess current market conditions"""
        return {
            'volatility': market_data.get('volatility', 0.05),
            'trend_strength': market_data.get('trend_strength', 0.5),
            'volume': market_data.get('volume', 1000),
            'regime': market_data.get('regime', 'uncertain'),
        }
    
    def _is_on_cooldown(self, pathway_name: str) -> bool:
        """Check if pathway is on cooldown"""
        if pathway_name not in self.pathway_cooldowns:
            return False
        
        cooldown_until = self.pathway_cooldowns[pathway_name]
        return datetime.now() < cooldown_until
    
    def set_cooldown(self, pathway_name: str, seconds: int = 60):
        """Set cooldown for a pathway"""
        self.pathway_cooldowns[pathway_name] = datetime.now() + timedelta(seconds=seconds)
    
    def integrate_signals(self, signals: List[Dict]) -> Optional[Dict]:
        """
        Integrate multiple signals into one decision
        
        Like neural integration in the brain
        Multiple pathways firing → one coordinated action
        
        Args:
            signals: List of signals from different pathways
            
        Returns:
            Integrated signal or None
        """
        if not signals:
            return None
        
        # If only one signal, return it
        if len(signals) == 1:
            return signals[0]
        
        # Multiple signals - need to integrate
        # Check if they agree on direction
        buy_signals = [s for s in signals if s.get('action') == 'BUY']
        sell_signals = [s for s in signals if s.get('action') == 'SELL']
        
        # If conflicting, use highest confidence
        if buy_signals and sell_signals:
            all_signals = buy_signals + sell_signals
            return max(all_signals, key=lambda s: s.get('confidence', 0))
        
        # If all agree, combine confidences
        if buy_signals:
            combined = self._combine_signals(buy_signals)
            combined['action'] = 'BUY'
            return combined
        elif sell_signals:
            combined = self._combine_signals(sell_signals)
            combined['action'] = 'SELL'
            return combined
        
        return None
    
    def _combine_signals(self, signals: List[Dict]) -> Dict:
        """Combine multiple agreeing signals"""
        # Weight by allocation
        total_weight = sum(s['allocation'] for s in signals)
        
        combined_confidence = sum(
            s['confidence'] * s['allocation'] 
            for s in signals
        ) / total_weight
        
        # Use highest individual size recommendation
        combined_size = max(s.get('size_pct', 0.05) for s in signals)
        
        return {
            'confidence': combined_confidence,
            'size_pct': combined_size,
            'pathways': [s['pathway'] for s in signals],
            'signal_count': len(signals),
            'integrated': True
        }
    
    def adapt_allocations(self, performance_data: Dict):
        """
        Adapt pathway allocations based on performance
        
        This is how the organism LEARNS which strategies work best
        """
        try:
            for pathway_name, pathway in self.pathways.items():
                perf = performance_data.get(pathway_name, {})
                
                # Increase allocation for winners
                if perf.get('sharpe', 0) > 1.5 and perf.get('win_rate', 0) > 0.55:
                    pathway.allocation = min(pathway.allocation * 1.05, 0.50)
                    logger.info(f"⚡ Increased {pathway_name} allocation to {pathway.allocation:.2%}")
                
                # Decrease allocation for losers
                elif perf.get('sharpe', 0) < 0.8 or perf.get('win_rate', 0) < 0.40:
                    pathway.allocation = max(pathway.allocation * 0.95, 0.05)
                    logger.warning(f"⚡ Decreased {pathway_name} allocation to {pathway.allocation:.2%}")
            
            # Renormalize allocations to sum to 1.0
            total_allocation = sum(p.allocation for p in self.pathways.values())
            for pathway in self.pathways.values():
                pathway.allocation /= total_allocation
            
        except Exception as e:
            logger.error(f"Allocation adaptation error: {e}")


# Global nervous system instance
nervous_system = NervousSystem()
