#!/usr/bin/env python3
"""
Integration Tests for Unified Bots
Tests Queen, Continuity, and Council AI unified implementations

AEGIS v2.3 Enhancement: TEST-1
Comprehensive testing of consolidated bot architecture
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bots.queen_bot_unified_v2 import QueenBotUnified, create_queen_bot_1
from bots.continuity_bot_unified_v2 import ContinuityBotUnified, create_continuity_bot_1
from bots.council_ai_unified_v2 import CouncilAIUnified, create_council_ai_1, create_full_council
from datetime import datetime, timedelta


class TestQueenBotUnified:
    """Integration tests for Queen Bot Unified"""
    
    def test_all_modes_initialize(self):
        """Test all 5 trading modes initialize correctly"""
        modes = ['SCALPING', 'TREND_FOLLOWING', 'MEAN_REVERSION', 'BREAKOUT', 'HYBRID']
        
        for mode in modes:
            bot = QueenBotUnified(mode=mode)
            assert bot.get_mode() == mode, f"Mode mismatch for {mode}"
            assert bot.metrics['initialized_at'] is not None
            bot.close()
    
    def test_mode_switching_workflow(self):
        """Test complete mode switching workflow"""
        bot = QueenBotUnified(mode='SCALPING')
        
        # Switch through all modes
        modes = ['TREND_FOLLOWING', 'MEAN_REVERSION', 'BREAKOUT', 'HYBRID']
        for mode in modes:
            result = bot.switch_mode(mode)
            assert result['success'], f"Failed to switch to {mode}"
            assert result['new_mode'] == mode
            assert bot.get_mode() == mode
        
        # Verify metrics updated
        assert bot.metrics['mode_switches'] == 4
        
        bot.close()
    
    def test_invalid_mode_handling(self):
        """Test error handling for invalid modes"""
        bot = QueenBotUnified(mode='SCALPING')
        
        result = bot.switch_mode('INVALID')
        assert not result['success']
        assert 'error' in result
        assert bot.get_mode() == 'SCALPING'  # Should not change
        
        bot.close()
    
    def test_trade_execution_per_mode(self):
        """Test trade execution in different modes"""
        modes = ['SCALPING', 'TREND_FOLLOWING', 'HYBRID']
        
        for mode in modes:
            bot = QueenBotUnified(mode=mode)
            
            result = bot.execute_trade('BTC/USDT', 'BUY')
            assert result['success']
            assert result['mode'] == mode
            assert bot.metrics['trades_executed'] == 1
            
            bot.close()
    
    def test_legacy_compatibility(self):
        """Test legacy bot creation functions"""
        creators = [
            (create_queen_bot_1, 'SCALPING', 1),
            # Add more if needed
        ]
        
        for creator, expected_mode, expected_id in creators:
            bot = creator()
            assert bot.get_mode() == expected_mode
            assert bot.queen_id == expected_id
            bot.close()
    
    def test_metrics_tracking(self):
        """Test metrics are properly tracked"""
        bot = QueenBotUnified(mode='SCALPING')
        
        # Execute trades
        for _ in range(3):
            bot.execute_trade('BTC/USDT', 'BUY')
        
        assert bot.metrics['trades_executed'] == 3
        
        # Switch modes
        bot.switch_mode('HYBRID')
        assert bot.metrics['mode_switches'] == 1
        
        bot.close()


class TestContinuityBotUnified:
    """Integration tests for Continuity Bot Unified"""
    
    def test_all_presets_initialize(self):
        """Test all preset hold periods initialize correctly"""
        presets = ['SHORT', 'MEDIUM', 'LONG']
        expected_hours = [24, 48, 72]
        
        for preset, hours in zip(presets, expected_hours):
            bot = ContinuityBotUnified(hold_period=preset)
            config = bot.get_config()
            assert config['min_hold_hours'] == hours
            bot.close()
    
    def test_custom_configuration(self):
        """Test custom hold period configuration"""
        bot = ContinuityBotUnified(
            hold_period='CUSTOM',
            min_hold_hours=36,
            profit_target=18.0,
            max_loss=8.0
        )
        
        config = bot.get_config()
        assert config['min_hold_hours'] == 36
        assert config['profit_target_pct'] == 18.0
        assert config['max_loss_pct'] == 8.0
        
        bot.close()
    
    def test_position_close_logic_recent(self):
        """Test position close decision for recent position"""
        bot = ContinuityBotUnified(hold_period='SHORT')  # 24h, 15% target
        
        # Position opened 12 hours ago
        recent_time = (datetime.now() - timedelta(hours=12)).isoformat()
        position = {
            'entry_price': 50000.0,
            'created_at': recent_time
        }
        
        # Current price +5% profit
        result = bot.should_close_position(position, 52500.0)
        
        assert not result['should_close'], "Should not close yet"
        assert result['hours_held'] < 24
        assert not result['hold_time_met']
        
        bot.close()
    
    def test_position_close_logic_profit_target(self):
        """Test position close decision when profit target met"""
        bot = ContinuityBotUnified(hold_period='SHORT')  # 24h, 15% target
        
        # Position opened 30 hours ago
        old_time = (datetime.now() - timedelta(hours=30)).isoformat()
        position = {
            'entry_price': 50000.0,
            'created_at': old_time
        }
        
        # Current price +16% profit
        result = bot.should_close_position(position, 58000.0)
        
        assert result['should_close'], "Should close"
        assert result['hold_time_met']
        assert result['profit_target_met']
        assert result['profit_pct'] == 16.0
        
        bot.close()
    
    def test_position_close_logic_stop_loss(self):
        """Test position close decision when stop-loss hit"""
        bot = ContinuityBotUnified(hold_period='SHORT')  # 24h, -10% stop
        
        # Position opened 26 hours ago
        old_time = (datetime.now() - timedelta(hours=26)).isoformat()
        position = {
            'entry_price': 50000.0,
            'created_at': old_time
        }
        
        # Current price -12% loss
        result = bot.should_close_position(position, 44000.0)
        
        assert result['should_close'], "Should close on stop-loss"
        assert result['hold_time_met']
        assert result['stop_loss_hit']
        assert result['profit_pct'] == -12.0
        
        bot.close()
    
    def test_dynamic_config_update(self):
        """Test configuration can be updated dynamically"""
        bot = ContinuityBotUnified(hold_period='MEDIUM')
        
        original = bot.get_config()
        assert original['min_hold_hours'] == 48
        
        updated = bot.update_config(min_hold_hours=60, profit_target=22.0)
        assert updated['min_hold_hours'] == 60
        assert updated['profit_target_pct'] == 22.0
        assert updated['hold_period'] == 'CUSTOM'
        
        bot.close()
    
    def test_legacy_compatibility(self):
        """Test legacy bot creation"""
        bot = create_continuity_bot_1()
        assert bot.continuity_id == 1
        config = bot.get_config()
        assert config['min_hold_hours'] == 24
        bot.close()


class TestCouncilAIUnified:
    """Integration tests for Council AI Unified"""
    
    def test_all_specialties_initialize(self):
        """Test all 5 specialties initialize correctly"""
        specialties = [
            'ROI_ANALYZER',
            'VOLATILITY_RISK',
            'DRAWDOWN_PROTECTION',
            'PERFORMANCE_AUDIT',
            'LIQUIDITY_QUALITY'
        ]
        
        for specialty in specialties:
            bot = CouncilAIUnified(specialty=specialty)
            assert bot.specialty == specialty
            bot.close()
    
    def test_roi_analysis_approve(self):
        """Test ROI analyzer approves good ratio"""
        bot = CouncilAIUnified(specialty='ROI_ANALYZER')
        
        # Good ROI: 4.0
        result = bot.analyze_trade({
            'target_profit': 200,
            'stop_loss_amount': 50
        })
        
        assert result['recommendation'] == 'APPROVE'
        assert result['roi_ratio'] == 4.0
        assert bot.metrics['approvals'] == 1
        
        bot.close()
    
    def test_roi_analysis_reject(self):
        """Test ROI analyzer rejects poor ratio"""
        bot = CouncilAIUnified(specialty='ROI_ANALYZER')
        
        # Poor ROI: 0.5
        result = bot.analyze_trade({
            'target_profit': 50,
            'stop_loss_amount': 100
        })
        
        assert result['recommendation'] == 'REJECT'
        assert result['roi_ratio'] == 0.5
        assert bot.metrics['rejections'] == 1
        
        bot.close()
    
    def test_volatility_analysis(self):
        """Test volatility analyzer"""
        bot = CouncilAIUnified(specialty='VOLATILITY_RISK')
        
        # Low volatility
        result_low = bot.analyze_trade({'volatility': 1.5})
        assert result_low['recommendation'] == 'APPROVE'
        
        # High volatility
        result_high = bot.analyze_trade({'volatility': 6.0})
        assert result_high['recommendation'] == 'REJECT'
        
        bot.close()
    
    def test_drawdown_analysis(self):
        """Test drawdown protection analyzer"""
        bot = CouncilAIUnified(specialty='DRAWDOWN_PROTECTION')
        
        # Safe drawdown
        result_safe = bot.analyze_trade({
            'current_drawdown': 5.0,
            'max_drawdown': 20.0
        })
        assert result_safe['recommendation'] == 'APPROVE'
        
        # Excessive drawdown
        result_high = bot.analyze_trade({
            'current_drawdown': 22.0,
            'max_drawdown': 20.0
        })
        assert result_high['recommendation'] == 'REJECT'
        
        bot.close()
    
    def test_performance_analysis(self):
        """Test performance audit analyzer"""
        bot = CouncilAIUnified(specialty='PERFORMANCE_AUDIT')
        
        # Good performance
        result_good = bot.analyze_trade({
            'win_rate': 0.60,
            'total_trades': 50
        })
        assert result_good['recommendation'] == 'APPROVE'
        
        # Poor performance
        result_poor = bot.analyze_trade({
            'win_rate': 0.35,
            'total_trades': 50
        })
        assert result_poor['recommendation'] == 'REJECT'
        
        bot.close()
    
    def test_liquidity_analysis(self):
        """Test liquidity quality analyzer"""
        bot = CouncilAIUnified(specialty='LIQUIDITY_QUALITY')
        
        # Good liquidity
        result_good = bot.analyze_trade({
            'volume_24h': 10000000,
            'spread_pct': 0.0005
        })
        assert result_good['recommendation'] == 'APPROVE'
        
        # Poor liquidity
        result_poor = bot.analyze_trade({
            'volume_24h': 100000,
            'spread_pct': 0.05
        })
        assert result_poor['recommendation'] == 'REJECT'
        
        bot.close()
    
    def test_full_council_voting(self):
        """Test full 5-member council vote"""
        council = create_full_council()
        assert len(council) == 5
        
        # Good trade proposal
        proposal = {
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
        
        votes = [member.analyze_trade(proposal) for member in council]
        
        assert len(votes) == 5
        approvals = sum(1 for v in votes if v['recommendation'] == 'APPROVE')
        assert approvals >= 3, "Good trade should get majority approval"
        
        for member in council:
            member.close()
    
    def test_metrics_tracking(self):
        """Test metrics are properly tracked"""
        bot = CouncilAIUnified(specialty='ROI_ANALYZER')
        
        # Approve
        bot.analyze_trade({'target_profit': 200, 'stop_loss_amount': 50})
        
        # Reject
        bot.analyze_trade({'target_profit': 50, 'stop_loss_amount': 100})
        
        # Caution
        bot.analyze_trade({'target_profit': 150, 'stop_loss_amount': 100})
        
        metrics = bot.get_metrics()
        assert metrics['total_analyses'] == 3
        assert metrics['approvals'] == 1
        assert metrics['rejections'] == 1
        assert metrics['cautions'] == 1
        
        bot.close()
    
    def test_legacy_compatibility(self):
        """Test legacy bot creation"""
        bot = create_council_ai_1()
        assert bot.council_id == 1
        assert bot.specialty == 'ROI_ANALYZER'
        bot.close()


class TestCrossBot

Integration:
    """Integration tests across multiple unified bots"""
    
    def test_queen_continuity_workflow(self):
        """Test Queen bot with Continuity bot workflow"""
        queen = QueenBotUnified(mode='SCALPING')
        continuity = ContinuityBotUnified(hold_period='SHORT')
        
        # Queen executes trade
        trade_result = queen.execute_trade('BTC/USDT', 'BUY')
        assert trade_result['success']
        
        # Simulate position (would come from PSM in real scenario)
        position = {
            'entry_price': 50000.0,
            'created_at': datetime.now().isoformat()
        }
        
        # Continuity evaluates when to close
        close_result = continuity.should_close_position(position, 50500.0)
        assert not close_result['should_close']  # Too recent
        
        queen.close()
        continuity.close()
    
    def test_council_approval_workflow(self):
        """Test council approval before trade execution"""
        council = create_full_council()
        queen = QueenBotUnified(mode='SCALPING')
        
        # Proposal
        proposal = {
            'target_profit': 200,
            'stop_loss_amount': 100,
            'volatility': 2.0,
            'current_drawdown': 5.0,
            'max_drawdown': 20.0,
            'win_rate': 0.55,
            'total_trades': 30,
            'volume_24h': 3000000,
            'spread_pct': 0.002
        }
        
        # Get council votes
        votes = [member.analyze_trade(proposal) for member in council]
        approvals = sum(1 for v in votes if v['recommendation'] == 'APPROVE')
        
        # Execute if majority approves
        if approvals >= 3:
            result = queen.execute_trade('BTC/USDT', 'BUY')
            assert result['success']
        
        for member in council:
            member.close()
        queen.close()
    
    def test_all_bots_coexist(self):
        """Test all unified bots can coexist"""
        queen = QueenBotUnified(mode='HYBRID')
        continuity = ContinuityBotUnified(hold_period='MEDIUM')
        council = create_full_council()
        
        # All should initialize
        assert queen.get_mode() == 'HYBRID'
        assert continuity.get_config()['hold_period'] == 'MEDIUM'
        assert len(council) == 5
        
        # All should operate independently
        queen.execute_trade('BTC/USDT', 'BUY')
        council[0].analyze_trade({'target_profit': 100, 'stop_loss_amount': 50})
        
        # Cleanup
        queen.close()
        continuity.close()
        for member in council:
            member.close()


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
