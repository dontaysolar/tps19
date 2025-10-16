#!/usr/bin/env python3
"""
Multi-Engine Master - Coordinates ALL trading engines for maximum profit
RAPID parallel execution - all engines analyze simultaneously
"""

from typing import Dict, List, Optional
from datetime import datetime
import concurrent.futures
import time

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class MultiEngineMaster:
    """
    Master coordinator for ALL trading engines
    
    Executes in PARALLEL for sub-second decisions
    
    Engines:
    1. Fibonacci Engine
    2. Harmonic Pattern Engine
    3. Volume Profile Engine
    4. Elliott Wave Engine
    5. Grid Trading Engine
    6. Arbitrage Engine
    7. Scalping Engine
    8. Market Making Engine
    9. Trend Following Engine
    10. Mean Reversion Engine
    11. Breakout Engine
    12. Momentum Engine
    
    Target: <500ms total decision time for ALL engines
    """
    
    def __init__(self):
        self.name = "Multi-Engine Master"
        
        # All available engines
        self.engines = {}
        self.engine_status = {}
        
        # Performance
        self.total_decisions = 0
        self.avg_total_time_ms = 0
        self.engines_per_decision = []
        
        # Rapid execution settings
        self.parallel_execution = True
        self.max_threads = 12  # All engines in parallel
        self.timeout_per_engine_ms = 150  # 150ms max per engine
        
        self._initialize_all_engines()
        
    def _initialize_all_engines(self):
        """Initialize ALL trading engines"""
        engines_to_load = [
            ('fibonacci', 'modules.engines.fibonacci_engine', 'fibonacci_engine'),
            ('harmonic', 'modules.engines.harmonic_engine', 'harmonic_engine'),
            ('volume_profile', 'modules.engines.volume_profile_engine', 'volume_profile_engine'),
            ('elliott_wave', 'modules.engines.elliott_wave_engine', 'elliott_wave_engine'),
            ('grid', 'modules.bots.grid_bot', 'grid_trading_bot'),
            ('arbitrage', 'modules.bots.arbitrage_bot', 'arbitrage_bot'),
            ('scalping', 'modules.bots.scalping_bot', 'scalping_bot'),
            ('market_making', 'modules.bots.market_making_bot', 'market_making_bot'),
        ]
        
        for engine_name, module_path, instance_name in engines_to_load:
            try:
                module = __import__(module_path, fromlist=[instance_name])
                instance = getattr(module, instance_name)
                self.engines[engine_name] = instance
                self.engine_status[engine_name] = 'ACTIVE'
            except Exception as e:
                logger.warning(f"Engine {engine_name} not available: {e}")
                self.engine_status[engine_name] = 'UNAVAILABLE'
        
        active_count = sum(1 for status in self.engine_status.values() if status == 'ACTIVE')
        logger.info(f"⚡ Multi-Engine Master: {active_count}/12 engines active")
    
    def execute_all_engines(self, market_data: Dict, df=None) -> Dict:
        """
        Execute ALL engines in PARALLEL
        
        Target: <500ms for complete analysis across all engines
        
        Args:
            market_data: Current market data
            df: Price dataframe
            
        Returns:
            Aggregated results from all engines
        """
        start_time = time.time()
        
        results = {
            'signals': [],
            'opportunities': [],
            'execution_time_ms': 0,
            'engines_executed': 0,
            'consensus': None
        }
        
        if self.parallel_execution:
            # PARALLEL execution (FAST)
            engine_results = self._execute_parallel(market_data, df)
        else:
            # Sequential execution (slower)
            engine_results = self._execute_sequential(market_data, df)
        
        # Process results
        for engine_name, result in engine_results.items():
            if result:
                results['signals'].append({
                    'engine': engine_name,
                    'signal': result.get('signal', 'HOLD'),
                    'confidence': result.get('confidence', 0.5),
                    'rapid': result.get('rapid', False)
                })
                results['engines_executed'] += 1
        
        # Calculate consensus
        results['consensus'] = self._calculate_rapid_consensus(engine_results)
        
        # Total execution time
        total_time_ms = (time.time() - start_time) * 1000
        results['execution_time_ms'] = total_time_ms
        
        # Track performance
        self._track_performance(total_time_ms, results['engines_executed'])
        
        logger.info(f"⚡ All engines executed in {total_time_ms:.1f}ms "
                   f"({results['engines_executed']} engines)")
        
        return results
    
    def _execute_parallel(self, market_data: Dict, df) -> Dict:
        """Execute all engines in PARALLEL using thread pool"""
        results = {}
        timeout_sec = self.timeout_per_engine_ms / 1000
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {}
            
            # Submit all engine tasks
            for engine_name, engine in self.engines.items():
                if self.engine_status[engine_name] != 'ACTIVE':
                    continue
                
                # Try rapid_analyze first, fallback to analyze
                if hasattr(engine, 'rapid_analyze'):
                    future = executor.submit(engine.rapid_analyze, df if df is not None else market_data)
                elif hasattr(engine, 'analyze'):
                    future = executor.submit(engine.analyze, df if df is not None else market_data)
                elif hasattr(engine, 'scan_scalping_opportunity'):
                    future = executor.submit(engine.scan_scalping_opportunity, market_data)
                else:
                    continue
                
                futures[engine_name] = future
            
            # Collect results with timeout
            for engine_name, future in futures.items():
                try:
                    result = future.result(timeout=timeout_sec)
                    results[engine_name] = result
                except concurrent.futures.TimeoutError:
                    logger.warning(f"Engine {engine_name} timeout (>{self.timeout_per_engine_ms}ms)")
                    results[engine_name] = None
                except Exception as e:
                    logger.error(f"Engine {engine_name} error: {e}")
                    results[engine_name] = None
        
        return results
    
    def _execute_sequential(self, market_data: Dict, df) -> Dict:
        """Execute engines sequentially (slower, for debugging)"""
        results = {}
        
        for engine_name, engine in self.engines.items():
            if self.engine_status[engine_name] != 'ACTIVE':
                continue
            
            try:
                if hasattr(engine, 'rapid_analyze'):
                    results[engine_name] = engine.rapid_analyze(df if df is not None else market_data)
                elif hasattr(engine, 'analyze'):
                    results[engine_name] = engine.analyze(df if df is not None else market_data)
            except Exception as e:
                logger.error(f"Engine {engine_name} error: {e}")
                results[engine_name] = None
        
        return results
    
    def _calculate_rapid_consensus(self, engine_results: Dict) -> Optional[Dict]:
        """
        Calculate RAPID consensus across all engines
        
        Simple majority voting for speed
        """
        votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        confidences = []
        engines_voted = []
        
        for engine_name, result in engine_results.items():
            if not result:
                continue
            
            signal = result.get('signal', result.get('action', 'HOLD'))
            confidence = result.get('confidence', 0.5)
            
            if signal in ['BUY', 'UP']:
                votes['BUY'] += 1
                confidences.append(confidence)
                engines_voted.append(engine_name)
            elif signal in ['SELL', 'DOWN']:
                votes['SELL'] += 1
                confidences.append(confidence)
                engines_voted.append(engine_name)
            else:
                votes['HOLD'] += 1
        
        # Determine consensus
        total_votes = sum(votes.values())
        if total_votes == 0:
            return None
        
        max_votes = max(votes.values())
        consensus_action = [k for k, v in votes.items() if v == max_votes][0]
        
        # Require at least 3 engines and 50% majority
        if len(engines_voted) < 3 or max_votes / total_votes < 0.50:
            return None
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        return {
            'action': consensus_action,
            'signal': consensus_action,
            'confidence': avg_confidence,
            'engines_agreed': max_votes,
            'total_engines': total_votes,
            'agreement_pct': max_votes / total_votes,
            'engines': engines_voted,
            'strategy': 'Multi_Engine_Consensus',
            'rapid': True
        }
    
    def _track_performance(self, total_time_ms: float, engines_executed: int):
        """Track multi-engine performance"""
        self.total_decisions += 1
        
        self.avg_total_time_ms = (
            (self.avg_total_time_ms * (self.total_decisions - 1) + total_time_ms)
            / self.total_decisions
        )
        
        self.engines_per_decision.append(engines_executed)
    
    def get_master_stats(self) -> Dict:
        """Get comprehensive master statistics"""
        active_engines = sum(1 for status in self.engine_status.values() if status == 'ACTIVE')
        
        # Get individual engine stats
        engine_stats = {}
        for engine_name, engine in self.engines.items():
            if hasattr(engine, 'get_stats'):
                try:
                    engine_stats[engine_name] = engine.get_stats()
                except:
                    engine_stats[engine_name] = {'status': 'error'}
        
        avg_engines = sum(self.engines_per_decision) / len(self.engines_per_decision) if self.engines_per_decision else 0
        
        return {
            'master': 'Multi_Engine_Master',
            'total_engines': len(self.engines),
            'active_engines': active_engines,
            'engine_status': self.engine_status,
            'total_decisions': self.total_decisions,
            'avg_total_time_ms': self.avg_total_time_ms,
            'avg_engines_per_decision': avg_engines,
            'parallel_execution': self.parallel_execution,
            'max_threads': self.max_threads,
            'target_time_ms': 500,
            'meeting_target': self.avg_total_time_ms < 500,
            'individual_engine_stats': engine_stats
        }


# Global instance
multi_engine_master = MultiEngineMaster()
