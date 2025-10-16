#!/usr/bin/env python3
"""
Unified Coordinator - Integrates SIUL + Primarch + TPS19 APEX
Supreme coordination layer for all trading systems
"""

from typing import Dict, List, Optional
from datetime import datetime

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class UnifiedCoordinator:
    """
    Master coordinator that integrates:
    - Enhanced SIUL (intelligence layer)
    - Trading Primarch (supreme authority)
    - TPS19 APEX Organism (biological trading)
    - Multidisciplinary Fusion (AI consensus)
    """
    
    def __init__(self):
        self.systems = {
            'siul': None,
            'primarch': None,
            'organism': None,
            'multidisciplinary': None,
            'market_cipher': None,
            'profit_engine': None,
            'risk_manager': None
        }
        
        self.coordination_mode = 'FULL_INTEGRATION'
        self.decision_log = []
        
        logger.info("🎯 Unified Coordinator initialized")
    
    def register_system(self, name: str, system):
        """Register a system"""
        if name in self.systems:
            self.systems[name] = system
            logger.info(f"✅ Registered: {name}")
            
            # Auto-register with Primarch if available
            if name != 'primarch' and self.systems['primarch']:
                self.systems['primarch'].register_system(name, system)
    
    def coordinate_decision(self, market_data: Dict, portfolio: Dict) -> Dict:
        """
        Coordinate a unified trading decision across all systems
        
        Flow:
        1. Gather signals from all systems
        2. SIUL processes unified intelligence
        3. Primarch renders supreme judgment
        4. Execute with full coordination
        
        Args:
            market_data: Current market state
            portfolio: Current portfolio
            
        Returns:
            Unified coordinated decision
        """
        logger.info("🎯 Unified Coordinator: Coordinating decision...")
        
        # Phase 1: Gather signals from all systems
        signals = self._gather_all_signals(market_data, portfolio)
        
        # Phase 2: SIUL unified intelligence
        siul_intelligence = self._process_siul_intelligence(market_data, signals)
        
        # Phase 3: Primarch supreme decision
        primarch_command = self._invoke_primarch_authority(
            market_data,
            signals,
            siul_intelligence,
            portfolio
        )
        
        # Phase 4: Generate coordinated action
        coordinated_decision = self._generate_coordinated_action(
            primarch_command,
            siul_intelligence,
            signals
        )
        
        # Record decision
        self._record_coordinated_decision(coordinated_decision)
        
        return coordinated_decision
    
    def _gather_all_signals(self, market_data: Dict, portfolio: Dict) -> Dict:
        """Gather signals from all registered systems"""
        signals = {}
        
        # Organism signal
        if self.systems['organism']:
            try:
                organism_signal = self.systems['organism'].brain.process_cognition(
                    market_data, portfolio
                )
                signals['organism'] = organism_signal
            except Exception as e:
                logger.error(f"Organism signal error: {e}")
        
        # Multidisciplinary fusion
        if self.systems['multidisciplinary']:
            try:
                # This would call multidisciplinary_fusion.analyze_all_disciplines
                # Placeholder for now
                signals['multidisciplinary'] = {
                    'signal': 'HOLD',
                    'confidence': 0.7
                }
            except Exception as e:
                logger.error(f"Multidisciplinary signal error: {e}")
        
        # Market Cipher
        if self.systems['market_cipher']:
            try:
                # This would call market_cipher_indicators.analyze
                signals['market_cipher'] = {
                    'signal': 'HOLD',
                    'confidence': 0.6
                }
            except Exception as e:
                logger.error(f"Market Cipher signal error: {e}")
        
        return signals
    
    def _process_siul_intelligence(self, market_data: Dict, 
                                   signals: Dict) -> Dict:
        """Process through SIUL intelligence layer"""
        if self.systems['siul']:
            try:
                # Extract TPS19 signals for SIUL integration
                tps19_signals = {}
                if 'multidisciplinary' in signals:
                    tps19_signals = signals['multidisciplinary']
                
                siul_result = self.systems['siul'].analyze(market_data, tps19_signals)
                return siul_result
            except Exception as e:
                logger.error(f"SIUL intelligence error: {e}")
        
        return {
            'decision': 'HOLD',
            'confidence': 0.5,
            'reasoning': 'SIUL unavailable'
        }
    
    def _invoke_primarch_authority(self, market_data: Dict, signals: Dict,
                                   siul_intelligence: Dict, 
                                   portfolio: Dict) -> Dict:
        """Invoke Primarch supreme authority"""
        if self.systems['primarch']:
            try:
                # Add SIUL to signals
                signals['siul'] = siul_intelligence
                
                primarch_command = self.systems['primarch'].supreme_decision(
                    market_data,
                    signals,
                    portfolio
                )
                return primarch_command
            except Exception as e:
                logger.error(f"Primarch invocation error: {e}")
        
        # Fallback: Use SIUL decision
        return {
            'authority': 'SIUL_FALLBACK',
            'command': siul_intelligence.get('decision', 'HOLD'),
            'confidence': siul_intelligence.get('confidence', 0.5),
            'binding': True
        }
    
    def _generate_coordinated_action(self, primarch_command: Dict,
                                    siul_intelligence: Dict,
                                    signals: Dict) -> Dict:
        """Generate final coordinated action"""
        return {
            'action': primarch_command['command'],
            'signal': primarch_command['command'],
            'confidence': primarch_command['confidence'],
            'authority': primarch_command['authority'],
            'binding': primarch_command.get('binding', True),
            'reason': primarch_command.get('reason', ''),
            'siul_intelligence': {
                'decision': siul_intelligence.get('decision', 'HOLD'),
                'confidence': siul_intelligence.get('confidence', 0.5),
                'score': siul_intelligence.get('score', 0.5)
            },
            'system_consensus': self._calculate_consensus(signals),
            'coordination_mode': self.coordination_mode,
            'timestamp': datetime.now().isoformat(),
            'system': 'Unified_Coordinator'
        }
    
    def _calculate_consensus(self, signals: Dict) -> Dict:
        """Calculate consensus across all signals"""
        votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        
        for system_name, signal in signals.items():
            if signal and isinstance(signal, dict):
                action = signal.get('signal', signal.get('action', 'HOLD'))
                if action in ['BUY', 'UP']:
                    votes['BUY'] += 1
                elif action in ['SELL', 'DOWN']:
                    votes['SELL'] += 1
                else:
                    votes['HOLD'] += 1
        
        total = sum(votes.values())
        consensus = max(votes, key=votes.get) if total > 0 else 'HOLD'
        agreement = votes[consensus] / total if total > 0 else 0
        
        return {
            'consensus': consensus,
            'agreement': agreement,
            'votes': votes
        }
    
    def _record_coordinated_decision(self, decision: Dict):
        """Record coordinated decision"""
        self.decision_log.append(decision)
        
        # Keep only last 100
        if len(self.decision_log) > 100:
            self.decision_log = self.decision_log[-100:]
    
    def get_coordination_status(self) -> Dict:
        """Get coordination status"""
        active_systems = sum(1 for s in self.systems.values() if s is not None)
        
        return {
            'coordination_mode': self.coordination_mode,
            'active_systems': active_systems,
            'total_systems': len(self.systems),
            'systems': {
                name: 'ACTIVE' if system is not None else 'INACTIVE'
                for name, system in self.systems.items()
            },
            'total_decisions': len(self.decision_log),
            'recent_decisions': self.decision_log[-5:] if self.decision_log else []
        }


# Global instance
unified_coordinator = UnifiedCoordinator()
