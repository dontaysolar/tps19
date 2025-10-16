#!/usr/bin/env python3
"""
Trading Primarch - Supreme Trading Intelligence Authority
Coordinates all trading systems with absolute authority
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class PrimarchMode(Enum):
    """Trading Primarch operational modes"""
    AGGRESSIVE_EXPANSION = "aggressive_expansion"
    BALANCED_GROWTH = "balanced_growth"
    DEFENSIVE_PRESERVATION = "defensive_preservation"
    HIBERNATION = "hibernation"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


class TradingPrimarch:
    """
    Supreme Trading Intelligence Authority
    
    The Primarch coordinates and overrides all trading decisions,
    combining SIUL intelligence with organism biology and external systems
    """
    
    def __init__(self):
        self.mode = PrimarchMode.BALANCED_GROWTH
        self.authority_level = 100  # Maximum authority
        
        # Primarch state
        self.command_history = []
        self.veto_count = 0
        self.override_count = 0
        self.strategic_directives = []
        
        # System coordination
        self.systems = {
            'siul': None,  # SIUL intelligence
            'organism': None,  # TPS19 organism
            'multidisciplinary': None,  # Fusion system
            'risk': None,  # Risk management
            'profit': None,  # Profit engine
        }
        
        # Performance tracking
        self.primarch_decisions = []
        self.success_rate = 0.0
        
        logger.info("🎖️ Trading Primarch initialized - Supreme authority established")
    
    def register_system(self, system_name: str, system_instance):
        """Register a system under Primarch authority"""
        if system_name in self.systems:
            self.systems[system_name] = system_instance
            logger.info(f"✅ System registered: {system_name}")
        else:
            logger.warning(f"Unknown system: {system_name}")
    
    def supreme_decision(self, market_data: Dict, signals: Dict,
                        portfolio: Dict) -> Dict:
        """
        Supreme decision-making authority
        
        Coordinates all systems and makes final binding decision
        
        Args:
            market_data: Current market state
            signals: Signals from all systems
            portfolio: Current portfolio state
            
        Returns:
            Supreme command with absolute authority
        """
        logger.info("⚔️ Trading Primarch analyzing situation...")
        
        # Phase 1: Strategic assessment
        strategic_state = self._assess_strategic_state(market_data, portfolio)
        
        # Phase 2: System consensus
        system_consensus = self._gather_system_consensus(signals)
        
        # Phase 3: SIUL intelligence integration
        siul_intelligence = self._integrate_siul_intelligence(market_data)
        
        # Phase 4: Primarch judgment
        primarch_judgment = self._render_supreme_judgment(
            strategic_state,
            system_consensus,
            siul_intelligence,
            market_data,
            portfolio
        )
        
        # Phase 5: Authority enforcement
        supreme_command = self._enforce_authority(primarch_judgment)
        
        # Record decision
        self._record_primarch_decision(supreme_command)
        
        return supreme_command
    
    def _assess_strategic_state(self, market_data: Dict, portfolio: Dict) -> Dict:
        """Assess current strategic state"""
        # Evaluate global conditions
        drawdown = portfolio.get('current_drawdown', 0)
        win_rate = portfolio.get('win_rate', 0.5)
        total_pnl = portfolio.get('total_pnl', 0)
        
        # Determine strategic context
        if drawdown > 0.15:
            context = 'CRISIS'
        elif drawdown > 0.10:
            context = 'UNDER_PRESSURE'
        elif win_rate > 0.70 and total_pnl > 0:
            context = 'DOMINANT'
        elif win_rate > 0.60:
            context = 'STRONG'
        else:
            context = 'NEUTRAL'
        
        # Mode assessment
        recommended_mode = self._recommend_mode(context, portfolio)
        
        return {
            'context': context,
            'recommended_mode': recommended_mode,
            'current_mode': self.mode.value,
            'drawdown': drawdown,
            'win_rate': win_rate,
            'total_pnl': total_pnl
        }
    
    def _recommend_mode(self, context: str, portfolio: Dict) -> PrimarchMode:
        """Recommend operational mode based on context"""
        if context == 'CRISIS':
            return PrimarchMode.EMERGENCY_SHUTDOWN
        elif context == 'UNDER_PRESSURE':
            return PrimarchMode.DEFENSIVE_PRESERVATION
        elif context == 'DOMINANT':
            return PrimarchMode.AGGRESSIVE_EXPANSION
        elif context == 'STRONG':
            return PrimarchMode.BALANCED_GROWTH
        else:
            return PrimarchMode.BALANCED_GROWTH
    
    def _gather_system_consensus(self, signals: Dict) -> Dict:
        """Gather consensus from all registered systems"""
        consensus_votes = {
            'BUY': 0,
            'SELL': 0,
            'HOLD': 0
        }
        
        confidence_sum = 0
        vote_count = 0
        
        for system_name, signal in signals.items():
            if signal and isinstance(signal, dict):
                action = signal.get('signal', signal.get('action', 'HOLD'))
                confidence = signal.get('confidence', 0.5)
                
                if action in ['BUY', 'UP']:
                    consensus_votes['BUY'] += confidence
                elif action in ['SELL', 'DOWN']:
                    consensus_votes['SELL'] += confidence
                else:
                    consensus_votes['HOLD'] += confidence
                
                confidence_sum += confidence
                vote_count += 1
        
        # Determine consensus
        if vote_count > 0:
            max_vote = max(consensus_votes.values())
            consensus_action = [k for k, v in consensus_votes.items() if v == max_vote][0]
            avg_confidence = confidence_sum / vote_count
        else:
            consensus_action = 'HOLD'
            avg_confidence = 0.5
        
        return {
            'action': consensus_action,
            'confidence': avg_confidence,
            'votes': consensus_votes,
            'vote_count': vote_count,
            'unanimous': max_vote == confidence_sum if vote_count > 0 else False
        }
    
    def _integrate_siul_intelligence(self, market_data: Dict) -> Dict:
        """Integrate SIUL intelligence layer"""
        if self.systems['siul']:
            try:
                siul_result = self.systems['siul'].process_unified_logic(market_data)
                return {
                    'available': True,
                    'decision': siul_result.get('final_decision', {}).get('decision', 'hold'),
                    'confidence': siul_result.get('confidence', 0.5),
                    'reasoning': siul_result.get('final_decision', {}).get('reasoning', '')
                }
            except Exception as e:
                logger.error(f"SIUL integration error: {e}")
                return {'available': False}
        
        return {'available': False}
    
    def _render_supreme_judgment(self, strategic_state: Dict,
                                 system_consensus: Dict,
                                 siul_intelligence: Dict,
                                 market_data: Dict,
                                 portfolio: Dict) -> Dict:
        """
        Render supreme judgment combining all intelligence
        
        The Primarch's decision supersedes all others
        """
        context = strategic_state['context']
        consensus = system_consensus['action']
        
        # Context-based decision modifiers
        if context == 'CRISIS':
            # In crisis: SELL everything or HOLD
            if portfolio.get('active_positions', 0) > 0:
                judgment = 'SELL'
                reason = "CRISIS PROTOCOL: Liquidating all positions"
                confidence = 1.0
            else:
                judgment = 'HOLD'
                reason = "CRISIS PROTOCOL: No trading until recovery"
                confidence = 1.0
        
        elif context == 'UNDER_PRESSURE':
            # Under pressure: Only take high-confidence trades
            if system_consensus['confidence'] > 0.80:
                judgment = consensus
                reason = "High-confidence signal approved despite pressure"
                confidence = system_consensus['confidence']
            else:
                judgment = 'HOLD'
                reason = "Insufficient confidence during pressure period"
                confidence = 0.7
        
        elif context == 'DOMINANT':
            # Dominant: Be aggressive
            if consensus == 'BUY' and system_consensus['confidence'] > 0.65:
                judgment = 'BUY'
                reason = "AGGRESSIVE EXPANSION: Capitalizing on dominance"
                confidence = min(0.95, system_consensus['confidence'] + 0.15)
            elif consensus == 'SELL':
                judgment = 'SELL'
                reason = "Taking profits during dominant phase"
                confidence = system_consensus['confidence']
            else:
                judgment = 'HOLD'
                reason = "Awaiting high-quality setup"
                confidence = 0.6
        
        else:  # STRONG or NEUTRAL
            # Normal mode: Trust consensus if high confidence
            if system_consensus['confidence'] > 0.75 and system_consensus['vote_count'] >= 3:
                judgment = consensus
                reason = f"System consensus ({system_consensus['vote_count']} systems agree)"
                confidence = system_consensus['confidence']
            elif siul_intelligence['available'] and siul_intelligence['confidence'] > 0.75:
                judgment = siul_intelligence['decision'].upper()
                reason = "SIUL intelligence override"
                confidence = siul_intelligence['confidence']
            else:
                judgment = 'HOLD'
                reason = "Insufficient consensus or confidence"
                confidence = 0.5
        
        return {
            'judgment': judgment,
            'confidence': confidence,
            'reason': reason,
            'context': context,
            'consensus': consensus,
            'siul_available': siul_intelligence['available'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _enforce_authority(self, judgment: Dict) -> Dict:
        """Enforce Primarch authority and generate supreme command"""
        command = {
            'authority': 'PRIMARCH',
            'command': judgment['judgment'],
            'confidence': judgment['confidence'],
            'binding': True,  # This decision is final and binding
            'reason': judgment['reason'],
            'context': judgment['context'],
            'mode': self.mode.value,
            'timestamp': judgment['timestamp'],
            'override_count': self.override_count,
            'veto_count': self.veto_count
        }
        
        logger.info(f"⚔️ PRIMARCH COMMAND: {command['command']} "
                   f"(Confidence: {command['confidence']:.0%})")
        logger.info(f"   Reason: {command['reason']}")
        
        return command
    
    def _record_primarch_decision(self, command: Dict):
        """Record Primarch decision for analysis"""
        self.primarch_decisions.append(command)
        self.command_history.append({
            'timestamp': command['timestamp'],
            'command': command['command'],
            'confidence': command['confidence'],
            'context': command['context']
        })
        
        # Keep only last 100 decisions
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
    
    def veto_decision(self, decision: Dict, reason: str) -> Dict:
        """
        Veto a system decision
        
        The Primarch has absolute veto power
        """
        self.veto_count += 1
        
        logger.warning(f"⚔️ PRIMARCH VETO: {reason}")
        
        return {
            'veto': True,
            'original_decision': decision,
            'reason': reason,
            'authority': 'PRIMARCH',
            'timestamp': datetime.now().isoformat()
        }
    
    def override_system(self, system_name: str, new_decision: Dict, 
                       reason: str) -> Dict:
        """
        Override a specific system's decision
        
        Used when Primarch disagrees with a system
        """
        self.override_count += 1
        
        logger.warning(f"⚔️ PRIMARCH OVERRIDE: {system_name} - {reason}")
        
        return {
            'override': True,
            'system': system_name,
            'new_decision': new_decision,
            'reason': reason,
            'authority': 'PRIMARCH',
            'timestamp': datetime.now().isoformat()
        }
    
    def set_mode(self, mode: PrimarchMode):
        """Set operational mode"""
        old_mode = self.mode
        self.mode = mode
        
        logger.info(f"⚔️ PRIMARCH MODE CHANGE: {old_mode.value} → {mode.value}")
        
        # Add to strategic directives
        self.strategic_directives.append({
            'timestamp': datetime.now().isoformat(),
            'directive': f'MODE_CHANGE: {mode.value}',
            'from_mode': old_mode.value,
            'to_mode': mode.value
        })
    
    def issue_strategic_directive(self, directive: str, parameters: Dict = None):
        """
        Issue a strategic directive to all systems
        
        Strategic directives alter system behavior globally
        """
        directive_obj = {
            'timestamp': datetime.now().isoformat(),
            'directive': directive,
            'parameters': parameters or {},
            'authority': 'PRIMARCH'
        }
        
        self.strategic_directives.append(directive_obj)
        
        logger.info(f"⚔️ STRATEGIC DIRECTIVE: {directive}")
        
        return directive_obj
    
    def get_primarch_status(self) -> Dict:
        """Get Primarch status and statistics"""
        total_decisions = len(self.primarch_decisions)
        
        if total_decisions > 0:
            # Calculate success rate (would need outcome tracking)
            buy_commands = sum(1 for d in self.primarch_decisions if d['command'] == 'BUY')
            sell_commands = sum(1 for d in self.primarch_decisions if d['command'] == 'SELL')
            hold_commands = sum(1 for d in self.primarch_decisions if d['command'] == 'HOLD')
        else:
            buy_commands = sell_commands = hold_commands = 0
        
        return {
            'mode': self.mode.value,
            'authority_level': self.authority_level,
            'total_decisions': total_decisions,
            'veto_count': self.veto_count,
            'override_count': self.override_count,
            'command_distribution': {
                'BUY': buy_commands,
                'SELL': sell_commands,
                'HOLD': hold_commands
            },
            'recent_commands': self.command_history[-10:],
            'active_directives': len(self.strategic_directives),
            'systems_registered': sum(1 for s in self.systems.values() if s is not None)
        }


# Global instance
trading_primarch = TradingPrimarch()
