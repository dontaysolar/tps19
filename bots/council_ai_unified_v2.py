#!/usr/bin/env python3
"""
Council AI Unified v2.0 - AEGIS Consolidated Bot
Consolidates Council AI 1-5 into single flexible bot

AEGIS v2.3 Enhancement: Bot Consolidation (NEW-1 Phase 3)
Replaces 5 separate Council AI bots with 1 configurable bot

SPECIALTIES:
- ROI_ANALYZER: Risk-reward ratio analysis
- VOLATILITY_RISK: Market volatility assessment
- DRAWDOWN_PROTECTION: Portfolio drawdown monitoring
- PERFORMANCE_AUDIT: Historical performance review
- LIQUIDITY_QUALITY: Market liquidity scoring

PURPOSE:
Multi-expert trading approval system. Each specialty provides independent
analysis and recommendations that feed into collective decision-making.

USAGE:
    # Create council member with specific specialty
    roi_analyzer = CouncilAIUnified(specialty='ROI_ANALYZER')
    
    # Analyze trade proposal
    analysis = roi_analyzer.analyze_trade(trade_data)
    
    # Or create full council
    council = [CouncilAIUnified(specialty=s) for s in CouncilAIUnified.VALID_SPECIALTIES]
    votes = [member.analyze_trade(trade_data) for member in council]
"""

import os
import sys
from typing import Dict, Optional
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase


class CouncilAIUnified(TradingBotBase):
    """
    Unified Council AI with configurable specialties
    
    Consolidates functionality of Council AI 1-5 into single flexible implementation.
    Uses specialty parameter to switch between different analytical focuses.
    
    ATLAS Compliance:
    - Assertion 1: Specialty is valid
    - Assertion 2: Analysis returns dict with required fields
    """
    
    VALID_SPECIALTIES = [
        'ROI_ANALYZER',
        'VOLATILITY_RISK',
        'DRAWDOWN_PROTECTION',
        'PERFORMANCE_AUDIT',
        'LIQUIDITY_QUALITY'
    ]
    
    def __init__(self, specialty: str = 'ROI_ANALYZER', council_id: Optional[int] = None):
        """
        Initialize Council AI with specific analytical specialty
        
        Args:
            specialty: Analytical focus area
            council_id: Optional legacy council ID for backward compatibility (1-5)
        
        ATLAS Compliance:
        - Assertion 1: Specialty is valid
        - Assertion 2: Council ID if provided is 1-5
        """
        assert specialty in self.VALID_SPECIALTIES, f"Specialty must be one of {self.VALID_SPECIALTIES}"
        assert council_id is None or (1 <= council_id <= 5), "Council ID must be 1-5 if provided"
        
        # Determine bot name
        if council_id:
            bot_name = f"COUNCIL_AI_{council_id}_{specialty.split('_')[0]}"
        else:
            bot_name = f"COUNCIL_AI_UNIFIED_{specialty}"
        
        super().__init__(
            bot_name=bot_name,
            bot_version="2.0.0",
            exchange_name='mock',
            enable_psm=False,
            enable_logging=False
        )
        
        # Configuration
        self.specialty = specialty
        self.council_id = council_id
        
        # Metrics
        self.metrics.update({
            'analyses': 0,
            'recommendations': 0,
            'approvals': 0,
            'rejections': 0,
            'cautions': 0
        })
        
        print(f"✅ {bot_name} initialized (specialty: {specialty})")
    
    def analyze_trade(self, trade_data: Dict) -> Dict:
        """
        Analyze trade proposal based on specialty
        
        Args:
            trade_data: Trade proposal with relevant metrics
        
        Returns:
            Analysis dict with recommendation and confidence
        
        ATLAS Compliance:
        - Assertion 1: Trade data is dict
        - Assertion 2: Result is dict with required fields
        """
        assert isinstance(trade_data, dict), "Trade data must be dict"
        
        self.metrics['analyses'] += 1
        
        # Route to specialty-specific analysis
        if self.specialty == 'ROI_ANALYZER':
            result = self._analyze_roi(trade_data)
        elif self.specialty == 'VOLATILITY_RISK':
            result = self._analyze_volatility(trade_data)
        elif self.specialty == 'DRAWDOWN_PROTECTION':
            result = self._analyze_drawdown(trade_data)
        elif self.specialty == 'PERFORMANCE_AUDIT':
            result = self._analyze_performance(trade_data)
        elif self.specialty == 'LIQUIDITY_QUALITY':
            result = self._analyze_liquidity(trade_data)
        else:
            raise ValueError(f"Unknown specialty: {self.specialty}")
        
        # Update metrics
        recommendation = result['recommendation']
        if recommendation == 'APPROVE':
            self.metrics['approvals'] += 1
        elif recommendation == 'REJECT':
            self.metrics['rejections'] += 1
        elif recommendation == 'CAUTION':
            self.metrics['cautions'] += 1
        
        if recommendation != 'REJECT':
            self.metrics['recommendations'] += 1
        
        assert isinstance(result, dict), "Result must be dict"
        assert 'recommendation' in result, "Result must have recommendation"
        return result
    
    def _analyze_roi(self, trade_data: Dict) -> Dict:
        """Analyze risk-reward ratio"""
        expected_profit = trade_data.get('target_profit', 0)
        risk = trade_data.get('stop_loss_amount', 1)
        roi_ratio = expected_profit / risk if risk > 0 else 0
        
        recommendation = (
            'APPROVE' if roi_ratio >= 2.0 else 
            'REJECT' if roi_ratio < 1.0 else 
            'CAUTION'
        )
        
        return {
            'council_member': self.council_id or 1,
            'specialty': 'ROI',
            'roi_ratio': roi_ratio,
            'recommendation': recommendation,
            'confidence': min(roi_ratio / 3, 1.0)
        }
    
    def _analyze_volatility(self, trade_data: Dict) -> Dict:
        """Analyze market volatility risk"""
        volatility = trade_data.get('volatility', 0)
        
        recommendation = (
            'REJECT' if volatility > 5.0 else 
            'CAUTION' if volatility > 2.0 else 
            'APPROVE'
        )
        
        confidence = 1.0 - min(volatility / 10, 0.9)
        
        return {
            'council_member': self.council_id or 2,
            'specialty': 'VOLATILITY',
            'volatility': volatility,
            'recommendation': recommendation,
            'confidence': confidence
        }
    
    def _analyze_drawdown(self, trade_data: Dict) -> Dict:
        """Analyze portfolio drawdown protection"""
        current_drawdown = trade_data.get('current_drawdown', 0)
        max_acceptable = trade_data.get('max_drawdown', 20.0)
        
        recommendation = (
            'REJECT' if current_drawdown >= max_acceptable else 
            'CAUTION' if current_drawdown > max_acceptable * 0.7 else 
            'APPROVE'
        )
        
        confidence = 1.0 - (current_drawdown / max_acceptable)
        
        return {
            'council_member': self.council_id or 3,
            'specialty': 'DRAWDOWN',
            'drawdown_pct': current_drawdown,
            'recommendation': recommendation,
            'confidence': max(confidence, 0.0)
        }
    
    def _analyze_performance(self, trade_data: Dict) -> Dict:
        """Analyze historical performance"""
        win_rate = trade_data.get('win_rate', 0.5)
        total_trades = trade_data.get('total_trades', 0)
        
        # Need minimum sample size
        if total_trades < 10:
            recommendation = 'CAUTION'
            confidence = 0.5
        else:
            recommendation = (
                'APPROVE' if win_rate >= 0.55 else 
                'REJECT' if win_rate < 0.40 else 
                'CAUTION'
            )
            confidence = win_rate
        
        return {
            'council_member': self.council_id or 4,
            'specialty': 'PERFORMANCE',
            'win_rate': win_rate,
            'total_trades': total_trades,
            'recommendation': recommendation,
            'confidence': confidence
        }
    
    def _analyze_liquidity(self, trade_data: Dict) -> Dict:
        """Analyze market liquidity quality"""
        volume = trade_data.get('volume_24h', 0)
        spread = trade_data.get('spread_pct', 0)
        
        # Calculate liquidity score (0-10)
        volume_score = min(volume / 1000000, 10)  # $1M = 10 points
        spread_score = max(10 - (spread * 100), 0)  # < 0.1% = 10 points
        liquidity_score = (volume_score + spread_score) / 2
        
        recommendation = (
            'APPROVE' if liquidity_score >= 7.0 else 
            'REJECT' if liquidity_score < 3.0 else 
            'CAUTION'
        )
        
        return {
            'council_member': self.council_id or 5,
            'specialty': 'LIQUIDITY',
            'liquidity_score': liquidity_score,
            'volume': volume,
            'spread': spread,
            'recommendation': recommendation,
            'confidence': liquidity_score / 10
        }
    
    def get_metrics(self) -> Dict:
        """Get analysis metrics"""
        total = self.metrics['analyses']
        return {
            'specialty': self.specialty,
            'total_analyses': total,
            'approvals': self.metrics['approvals'],
            'rejections': self.metrics['rejections'],
            'cautions': self.metrics['cautions'],
            'approval_rate': self.metrics['approvals'] / total if total > 0 else 0
        }


# Backward compatibility: Create instances for legacy Council AI 1-5
def create_council_ai_1():
    """Legacy Council AI 1 (ROI)"""
    return CouncilAIUnified(specialty='ROI_ANALYZER', council_id=1)


def create_council_ai_2():
    """Legacy Council AI 2 (Volatility)"""
    return CouncilAIUnified(specialty='VOLATILITY_RISK', council_id=2)


def create_council_ai_3():
    """Legacy Council AI 3 (Drawdown)"""
    return CouncilAIUnified(specialty='DRAWDOWN_PROTECTION', council_id=3)


def create_council_ai_4():
    """Legacy Council AI 4 (Performance)"""
    return CouncilAIUnified(specialty='PERFORMANCE_AUDIT', council_id=4)


def create_council_ai_5():
    """Legacy Council AI 5 (Liquidity)"""
    return CouncilAIUnified(specialty='LIQUIDITY_QUALITY', council_id=5)


# Helper: Create full council
def create_full_council():
    """Create complete 5-member council"""
    return [CouncilAIUnified(specialty=s, council_id=i+1) 
            for i, s in enumerate(CouncilAIUnified.VALID_SPECIALTIES)]


# Self-test
if __name__ == '__main__':
    print("=" * 70)
    print("COUNCIL AI UNIFIED - SELF-TEST")
    print("=" * 70)
    print("")
    
    # Test 1: Create with each specialty
    print("Test 1: Specialty initialization")
    for specialty in CouncilAIUnified.VALID_SPECIALTIES:
        bot = CouncilAIUnified(specialty=specialty)
        assert bot.specialty == specialty, f"Specialty mismatch"
        bot.close()
        print(f"✅ {specialty} initialized")
    print("")
    
    # Test 2: ROI analysis
    print("Test 2: ROI Analysis")
    bot = CouncilAIUnified(specialty='ROI_ANALYZER')
    
    # Good ROI
    result = bot.analyze_trade({'target_profit': 200, 'stop_loss_amount': 50})
    assert result['recommendation'] == 'APPROVE', "Should approve good ROI"
    assert result['roi_ratio'] == 4.0, "ROI calc wrong"
    print(f"✅ Good ROI (4.0): {result['recommendation']}")
    
    # Poor ROI
    result = bot.analyze_trade({'target_profit': 50, 'stop_loss_amount': 100})
    assert result['recommendation'] == 'REJECT', "Should reject poor ROI"
    print(f"✅ Poor ROI (0.5): {result['recommendation']}")
    
    bot.close()
    print("")
    
    # Test 3: Volatility analysis
    print("Test 3: Volatility Analysis")
    bot = CouncilAIUnified(specialty='VOLATILITY_RISK')
    
    result = bot.analyze_trade({'volatility': 1.5})
    assert result['recommendation'] == 'APPROVE', "Low volatility should approve"
    print(f"✅ Low volatility (1.5): {result['recommendation']}")
    
    result = bot.analyze_trade({'volatility': 6.0})
    assert result['recommendation'] == 'REJECT', "High volatility should reject"
    print(f"✅ High volatility (6.0): {result['recommendation']}")
    
    bot.close()
    print("")
    
    # Test 4: Full council vote
    print("Test 4: Full Council Vote")
    council = create_full_council()
    
    trade_proposal = {
        'target_profit': 300,
        'stop_loss_amount': 100,
        'volatility': 2.5,
        'current_drawdown': 5.0,
        'max_drawdown': 20.0,
        'win_rate': 0.60,
        'total_trades': 50,
        'volume_24h': 5000000,
        'spread_pct': 0.001
    }
    
    votes = [member.analyze_trade(trade_proposal) for member in council]
    approvals = sum(1 for v in votes if v['recommendation'] == 'APPROVE')
    
    print(f"  Council size: {len(council)}")
    print(f"  Votes cast: {len(votes)}")
    print(f"  Approvals: {approvals}")
    print(f"  Rejections: {sum(1 for v in votes if v['recommendation'] == 'REJECT')}")
    print(f"  Cautions: {sum(1 for v in votes if v['recommendation'] == 'CAUTION')}")
    
    assert len(votes) == 5, "Should have 5 votes"
    assert approvals >= 3, "Good trade should get majority approval"
    
    for member in council:
        member.close()
    
    print(f"✅ Council voting works (majority: {approvals}/5)")
    print("")
    
    # Test 5: Legacy compatibility
    print("Test 5: Legacy bot creation")
    legacy_bots = [
        ('Council AI 1', create_council_ai_1, 'ROI_ANALYZER'),
        ('Council AI 2', create_council_ai_2, 'VOLATILITY_RISK'),
        ('Council AI 3', create_council_ai_3, 'DRAWDOWN_PROTECTION'),
        ('Council AI 4', create_council_ai_4, 'PERFORMANCE_AUDIT'),
        ('Council AI 5', create_council_ai_5, 'LIQUIDITY_QUALITY')
    ]
    
    for name, creator, expected_specialty in legacy_bots:
        bot = creator()
        assert bot.specialty == expected_specialty, f"{name} specialty mismatch"
        assert bot.council_id is not None, f"{name} missing council_id"
        bot.close()
        print(f"✅ {name} legacy compatibility confirmed")
    print("")
    
    print("=" * 70)
    print("✅ ALL SELF-TESTS PASSED")
    print("=" * 70)
    print("")
    print("CONSOLIDATION COMPLETE:")
    print("  Before: 5 separate Council AI files")
    print("  After:  1 unified file with 5 specialties")
    print("  Reduction: 80% fewer files")
    print("  Backward Compatible: ✅ YES")
    print("  Full Council Support: ✅ YES")
