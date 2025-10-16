#!/usr/bin/env python3
"""
Organism Orchestrator - The Complete Living System

This brings together all organism systems:
- Brain (intelligence)
- Immune System (protection)
- Nervous System (execution)
- Evolution (learning)
- Metabolism (capital management)

Into ONE coordinated, evolving financial organism.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from modules.utils.logger import get_logger
from modules.utils.config import config

from .brain import organism_brain, MarketRegime
from .immune_system import immune_system
from .nervous_system import nervous_system
from .evolution import evolution_engine
from .metabolism import metabolism

logger = get_logger(__name__)


class TradingOrganism:
    """
    The complete trading organism
    
    This replaces 400 bots with ONE unified, evolving system
    """
    
    def __init__(self):
        # Core systems
        self.brain = organism_brain
        self.immune_system = immune_system
        self.nervous_system = nervous_system
        self.evolution = evolution_engine
        self.metabolism = metabolism
        
        # Organism state
        self.state = {
            'alive': True,
            'birth_time': datetime.now(),
            'age_hours': 0,
            'total_decisions': 0,
            'successful_trades': 0,
            'health_score': 100.0,
            'evolution_generation': 1,
        }
        
        # Performance tracking
        self.performance = {
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
        }
        
        logger.info("🧬 Trading Organism initialized - LIFE BEGINS")
    
    def process_market_cycle(self, market_data: Dict, portfolio: Dict) -> Optional[Dict]:
        """
        Complete organism cycle - one "heartbeat"
        
        This is the organism's main loop:
        1. SENSE environment (brain)
        2. CHECK immune system (protection)
        3. DECIDE action (nervous system)
        4. EXECUTE trade (metabolism)
        5. LEARN from result (evolution)
        
        Args:
            market_data: Current market state
            portfolio: Current portfolio state
            
        Returns:
            Trade decision or None
        """
        try:
            # Update organism age
            self.state['age_hours'] = (
                datetime.now() - self.state['birth_time']
            ).total_seconds() / 3600
            
            # 1. BRAIN: Process information and make decision
            decision = self.brain.process_information(market_data)
            self.state['total_decisions'] += 1
            
            logger.info(f"🧠 Brain decision: {decision['strategy']} "
                       f"(confidence: {decision['confidence']:.2%})")
            
            # 2. Generate trading signals through nervous system
            signals = self.nervous_system.process_market_data(market_data)
            
            if not signals:
                logger.info("⚡ No signals from nervous system")
                return None
            
            # Integrate multiple signals
            integrated_signal = self.nervous_system.integrate_signals(signals)
            
            if not integrated_signal:
                logger.info("⚡ Signals did not integrate")
                return None
            
            # 3. Calculate position size (metabolism)
            position_size_pct = self.metabolism.calculate_position_size(
                integrated_signal, 
                portfolio
            )
            
            integrated_signal['size_pct'] = position_size_pct
            integrated_signal['size_usdt'] = portfolio['total_value'] * position_size_pct
            
            # 4. IMMUNE SYSTEM: Check all protection layers
            
            # Layer 1: Pre-trade antibodies
            approved, reason = self.immune_system.layer1_pretrade_antibodies(
                integrated_signal, 
                portfolio
            )
            
            if not approved:
                logger.warning(f"🛡️ Trade rejected by immune system: {reason}")
                return None
            
            # Layer 2: Position-level check
            # (happens after trade execution in monitor loop)
            
            # Layer 3: Portfolio-level check
            portfolio_actions = self.immune_system.layer3_portfolio_immunity(portfolio)
            if portfolio_actions:
                logger.warning(f"🛡️ Portfolio immune actions: {portfolio_actions}")
                self._execute_portfolio_actions(portfolio_actions)
            
            # Layer 4: Emergency check
            emergency, emergency_reason = self.immune_system.layer4_emergency_response(
                portfolio, 
                market_data
            )
            
            if emergency:
                logger.critical(f"🚨 EMERGENCY SHUTDOWN: {emergency_reason}")
                self.enter_hibernation(emergency_reason)
                return None
            
            # 5. Final trade decision
            trade_decision = {
                'symbol': integrated_signal.get('symbol'),
                'action': integrated_signal.get('action'),
                'size_pct': position_size_pct,
                'size_usdt': integrated_signal['size_usdt'],
                'confidence': integrated_signal['confidence'],
                'strategy': decision['strategy'],
                'pathways': integrated_signal.get('pathways', []),
                'timestamp': datetime.now(),
                'organism_age': self.state['age_hours'],
                'health_score': self.state['health_score'],
            }
            
            logger.info(f"✅ ORGANISM DECISION: {trade_decision['action']} "
                       f"{trade_decision['symbol']} - "
                       f"Size: {trade_decision['size_pct']:.2%}, "
                       f"Confidence: {trade_decision['confidence']:.2%}")
            
            return trade_decision
            
        except Exception as e:
            logger.error(f"Organism cycle error: {e}")
            return None
    
    def learn_from_trade(self, trade_result: Dict):
        """
        Learn from trade result
        
        This is how the organism EVOLVES
        
        Args:
            trade_result: Result of executed trade
        """
        try:
            # Update performance
            if trade_result.get('pnl', 0) > 0:
                self.state['successful_trades'] += 1
            
            # Update win rate
            self.performance['win_rate'] = (
                self.state['successful_trades'] / 
                max(self.state['total_decisions'], 1)
            )
            
            # Adapt brain based on performance
            self.brain.adapt_to_performance(self.performance)
            
            # Adapt metabolism
            self.metabolism.adjust_metabolic_rate(self.performance)
            
            # Adapt nervous system allocations
            self.nervous_system.adapt_allocations(self.performance)
            
            # Update health score
            self._update_health_score()
            
            logger.info(f"🧬 Organism learned from trade - "
                       f"Health: {self.state['health_score']:.1f}, "
                       f"Win rate: {self.performance['win_rate']:.2%}")
            
        except Exception as e:
            logger.error(f"Learning error: {e}")
    
    def weekly_evolution(self):
        """
        Weekly evolution cycle
        
        This is when the organism EVOLVES its strategies
        Happens every 7 days
        """
        try:
            logger.info("🧬 Starting weekly evolution cycle...")
            
            # Get current strategy performance
            performance_data = self._gather_strategy_performance()
            
            # Evolve strategies
            next_generation = self.evolution.evolve_generation(performance_data)
            
            logger.info(f"🧬 Evolution complete - Generation {self.evolution.generation}")
            
            # Update state
            self.state['evolution_generation'] = self.evolution.generation
            
        except Exception as e:
            logger.error(f"Weekly evolution error: {e}")
    
    def _gather_strategy_performance(self) -> Dict:
        """Gather performance data for all strategies"""
        # Placeholder - integrate with actual performance tracking
        return {
            'trend_following': {
                'sharpe_ratio': 1.5,
                'win_rate': 0.55,
                'profit_factor': 1.8,
                'max_drawdown': 0.10,
            },
            'mean_reversion': {
                'sharpe_ratio': 1.3,
                'win_rate': 0.62,
                'profit_factor': 1.5,
                'max_drawdown': 0.08,
            },
        }
    
    def _update_health_score(self):
        """
        Update organism health score (0-100)
        
        Health reflects overall system wellness
        """
        health_factors = {
            'win_rate': self.performance['win_rate'],
            'sharpe': min(self.performance.get('sharpe_ratio', 0) / 2.0, 1.0),
            'drawdown': 1 - self.performance.get('current_drawdown', 0),
        }
        
        # Weighted health score
        self.state['health_score'] = (
            health_factors['win_rate'] * 40 +
            health_factors['sharpe'] * 30 +
            health_factors['drawdown'] * 30
        ) * 100
        
        # Log health status
        if self.state['health_score'] > 80:
            logger.info(f"💚 Organism health: EXCELLENT ({self.state['health_score']:.1f})")
        elif self.state['health_score'] > 60:
            logger.info(f"💛 Organism health: GOOD ({self.state['health_score']:.1f})")
        else:
            logger.warning(f"❤️ Organism health: POOR ({self.state['health_score']:.1f})")
    
    def _execute_portfolio_actions(self, actions: List[str]):
        """Execute portfolio-level immune responses"""
        for action in actions:
            response = self.immune_system.execute_immune_response(action, {})
            logger.info(f"🛡️ Executed immune response: {action}")
    
    def enter_hibernation(self, reason: str):
        """
        Enter hibernation mode
        
        Like an organism sleeping to recover from stress
        """
        logger.critical(f"😴 Organism entering HIBERNATION: {reason}")
        
        self.state['alive'] = False
        self.state['hibernation_start'] = datetime.now()
        self.state['hibernation_reason'] = reason
        
        # Reduce all activity
        self.metabolism.metabolic_rate = 0.1
        self.brain.state['consciousness_level'] = 0.3
    
    def wake_from_hibernation(self):
        """Wake from hibernation if conditions are safe"""
        if not self.state.get('hibernation_start'):
            return
        
        # Check if enough time has passed (24 hours minimum)
        time_asleep = (datetime.now() - self.state['hibernation_start']).total_seconds() / 3600
        
        if time_asleep > 24:
            logger.info(f"🌅 Organism waking from hibernation after {time_asleep:.1f} hours")
            
            self.state['alive'] = True
            self.metabolism.metabolic_rate = 0.5  # Start slow
            self.brain.state['consciousness_level'] = 0.6
            
            del self.state['hibernation_start']
            del self.state['hibernation_reason']
    
    def get_vital_signs(self) -> Dict:
        """
        Get organism vital signs
        
        Like checking pulse, blood pressure, etc.
        """
        return {
            'status': 'alive' if self.state['alive'] else 'hibernating',
            'age_hours': self.state['age_hours'],
            'health_score': self.state['health_score'],
            'consciousness': self.brain.state['consciousness_level'],
            'metabolic_rate': self.metabolism.metabolic_rate,
            'generation': self.state['evolution_generation'],
            'total_decisions': self.state['total_decisions'],
            'win_rate': self.performance['win_rate'],
            'sharpe_ratio': self.performance.get('sharpe_ratio', 0),
            'current_drawdown': self.performance.get('current_drawdown', 0),
            'timestamp': datetime.now().isoformat()
        }


# Global organism instance - THE trading organism
trading_organism = TradingOrganism()
