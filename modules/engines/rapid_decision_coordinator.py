#!/usr/bin/env python3
"""
Rapid Decision Coordinator - Parallel engine execution for millisecond decisions
Coordinates multiple trading engines for instant analysis
"""

from typing import Dict, List, Optional
from datetime import datetime
import concurrent.futures
import time

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class RapidDecisionCoordinator:
    """
    Coordinates multiple trading engines in PARALLEL for rapid decisions
    
    Target: <200ms total decision time
    
    Engines:
    - Fibonacci Engine
    - Harmonic Engine  
    - Volume Profile Engine
    - Grid Engine (existing grid_bot)
    - Technical Engine (Market Cipher inspired)
    - ML Engine (existing ml_predictor)
    """
    
    def __init__(self):
        self.name = "Rapid Decision Coordinator"
        
        # Register engines
        self.engines = {}
        self.engine_weights = {}
        
        # Performance tracking
        self.total_decisions = 0
        self.avg_decision_time_ms = 0
        self.fastest_decision_ms = float('inf')
        self.slowest_decision_ms = 0
        
        self._initialize_engines()
        
    def _initialize_engines(self):
        """Initialize all rapid trading engines"""
        # Fibonacci Engine
        try:
            from modules.engines.fibonacci_engine import fibonacci_engine
            self.engines['fibonacci'] = fibonacci_engine
            self.engine_weights['fibonacci'] = 0.25
        except Exception as e:
            logger.warning(f"Fibonacci engine not available: {e}")
        
        # Harmonic Engine
        try:
            from modules.engines.harmonic_engine import harmonic_engine
            self.engines['harmonic'] = harmonic_engine
            self.engine_weights['harmonic'] = 0.20
        except Exception as e:
            logger.warning(f"Harmonic engine not available: {e}")
        
        # Volume Profile Engine
        try:
            from modules.engines.volume_profile_engine import volume_profile_engine
            self.engines['volume_profile'] = volume_profile_engine
            self.engine_weights['volume_profile'] = 0.25
        except Exception as e:
            logger.warning(f"Volume profile engine not available: {e}")
        
        # Grid Engine
        try:
            from modules.bots.grid_bot import grid_trading_bot
            self.engines['grid'] = grid_trading_bot
            self.engine_weights['grid'] = 0.15
        except Exception as e:
            logger.warning(f"Grid engine not available: {e}")
        
        # Technical Engine (existing strategies)
        try:
            from modules.strategies.trend_following import trend_following
            self.engines['technical'] = trend_following
            self.engine_weights['technical'] = 0.15
        except Exception as e:
            logger.warning(f"Technical engine not available: {e}")
        
        logger.info(f"⚡ Rapid Decision Coordinator: {len(self.engines)} engines ready")
    
    def make_rapid_decision(self, market_data: Dict, df=None) -> Optional[Dict]:
        """
        Make RAPID decision by running all engines in PARALLEL
        
        Target: <200ms total execution time
        
        Args:
            market_data: Current market data
            df: Price dataframe (optional)
            
        Returns:
            Rapid trading decision (if consensus found)
        """
        start_time = time.time()
        
        try:
            # Execute all engines in PARALLEL
            engine_results = self._execute_engines_parallel(market_data, df)
            
            # Rapid consensus (no complex logic, just voting)
            decision = self._rapid_consensus(engine_results)
            
            # Track performance
            execution_time_ms = (time.time() - start_time) * 1000
            self._track_performance(execution_time_ms)
            
            if decision:
                decision['total_execution_time_ms'] = execution_time_ms
                decision['engines_consulted'] = len(engine_results)
                decision['rapid_decision'] = True
                
                logger.info(f"⚡ RAPID DECISION: {decision['action']} "
                           f"in {execution_time_ms:.1f}ms "
                           f"({decision['confirmations']} confirmations)")
            
            return decision
            
        except Exception as e:
            logger.error(f"Rapid decision error: {e}")
            return None
    
    def _execute_engines_parallel(self, market_data: Dict, df) -> Dict:
        """Execute all engines in parallel using thread pool"""
        results = {}
        
        # Use ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            # Submit all engine tasks
            futures = {}
            
            for engine_name, engine in self.engines.items():
                if hasattr(engine, 'rapid_analyze'):
                    future = executor.submit(engine.rapid_analyze, df)
                    futures[engine_name] = future
                elif hasattr(engine, 'analyze') and df is not None:
                    future = executor.submit(engine.analyze, df)
                    futures[engine_name] = future
            
            # Collect results (wait max 150ms for all)
            for engine_name, future in futures.items():
                try:
                    result = future.result(timeout=0.15)  # 150ms timeout
                    if result:
                        results[engine_name] = result
                except concurrent.futures.TimeoutError:
                    logger.warning(f"Engine {engine_name} timeout (>150ms)")
                except Exception as e:
                    logger.error(f"Engine {engine_name} error: {e}")
        
        return results
    
    def _rapid_consensus(self, engine_results: Dict) -> Optional[Dict]:
        """
        RAPID consensus from engine results
        
        Simple voting - no complex logic (speed critical)
        """
        if not engine_results:
            return None
        
        # Count votes
        buy_score = 0
        sell_score = 0
        confirmations = 0
        reasons = []
        
        for engine_name, result in engine_results.items():
            signal = result.get('signal', result.get('action', 'HOLD'))
            confidence = result.get('confidence', 0.5)
            weight = self.engine_weights.get(engine_name, 0.1)
            
            weighted_confidence = confidence * weight
            
            if signal in ['BUY', 'UP']:
                buy_score += weighted_confidence
                confirmations += 1
                reasons.append(f"{engine_name}: BUY")
            elif signal in ['SELL', 'DOWN']:
                sell_score += weighted_confidence
                confirmations += 1
                reasons.append(f"{engine_name}: SELL")
        
        # Require at least 2 engine confirmations for speed
        if confirmations < 2:
            return None
        
        # Require 60%+ confidence for rapid execution
        min_confidence = 0.60
        
        current_price = list(engine_results.values())[0].get('entry_price', 0)
        
        if buy_score > sell_score and buy_score > min_confidence:
            return {
                'action': 'BUY',
                'signal': 'BUY',
                'confidence': buy_score,
                'confirmations': confirmations,
                'reason': f"Rapid consensus: {', '.join(reasons[:2])}",
                'entry_price': current_price,
                'strategy': 'Rapid_Multi_Engine',
                'engines': list(engine_results.keys()),
                'rapid': True
            }
        
        elif sell_score > buy_score and sell_score > min_confidence:
            return {
                'action': 'SELL',
                'signal': 'SELL',
                'confidence': sell_score,
                'confirmations': confirmations,
                'reason': f"Rapid consensus: {', '.join(reasons[:2])}",
                'entry_price': current_price,
                'strategy': 'Rapid_Multi_Engine',
                'engines': list(engine_results.keys()),
                'rapid': True
            }
        
        return None
    
    def _track_performance(self, execution_time_ms: float):
        """Track decision speed performance"""
        self.total_decisions += 1
        
        # Update average
        self.avg_decision_time_ms = (
            (self.avg_decision_time_ms * (self.total_decisions - 1) + execution_time_ms)
            / self.total_decisions
        )
        
        # Update fastest/slowest
        if execution_time_ms < self.fastest_decision_ms:
            self.fastest_decision_ms = execution_time_ms
        
        if execution_time_ms > self.slowest_decision_ms:
            self.slowest_decision_ms = execution_time_ms
    
    def get_performance_stats(self) -> Dict:
        """Get rapid decision performance statistics"""
        return {
            'coordinator': 'Rapid_Decision',
            'total_decisions': self.total_decisions,
            'avg_decision_time_ms': self.avg_decision_time_ms,
            'fastest_decision_ms': self.fastest_decision_ms,
            'slowest_decision_ms': self.slowest_decision_ms,
            'target_time_ms': 200,
            'meeting_target': self.avg_decision_time_ms < 200,
            'active_engines': len(self.engines),
            'parallel_execution': True
        }
    
    def benchmark_speed(self, df, iterations: int = 10) -> Dict:
        """Benchmark decision speed"""
        times = []
        
        for i in range(iterations):
            start = time.time()
            self.make_rapid_decision({'price': 45000}, df)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
        
        return {
            'avg_time_ms': statistics.mean(times),
            'min_time_ms': min(times),
            'max_time_ms': max(times),
            'std_dev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations,
            'target_met': statistics.mean(times) < 200
        }


# Global instance
rapid_decision_coordinator = RapidDecisionCoordinator()
