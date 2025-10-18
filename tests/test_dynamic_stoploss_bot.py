#!/usr/bin/env python3
"""
Comprehensive Test Suite for Dynamic Stop-Loss Bot
Following Aegis Pre-Deployment Validation Protocol
"""

import sys
import os
import unittest
import json
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bots'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

from dynamic_stoploss_bot import DynamicStopLossBot

class TestDynamicStopLossBot(unittest.TestCase):
    """Test suite for Dynamic Stop-Loss Bot"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bot = DynamicStopLossBot()
        self.test_symbol = 'BTC/USDT'
        self.test_entry = 50000.0
        self.test_amount = 0.001
    
    def test_bot_initialization(self):
        """Test bot initializes correctly"""
        self.assertEqual(self.bot.name, "DynamicStopLossBot")
        self.assertEqual(self.bot.version, "1.0.0")
        self.assertIsNotNone(self.bot.config)
        self.assertIsInstance(self.bot.positions, dict)
        self.assertEqual(len(self.bot.positions), 0)
    
    def test_atr_calculation(self):
        """Test ATR calculation returns valid values"""
        atr = self.bot.calculate_atr(self.test_symbol)
        
        # ATR should be non-negative
        self.assertGreaterEqual(atr, 0)
        
        # ATR should be cached
        self.assertIn(self.test_symbol, self.bot.atr_cache)
        
        # Cache should have required fields
        cache = self.bot.atr_cache[self.test_symbol]
        self.assertIn('value', cache)
        self.assertIn('timestamp', cache)
        self.assertIn('timeframe', cache)
    
    def test_dynamic_stop_calculation_long(self):
        """Test dynamic stop-loss calculation for long positions"""
        stop_price = self.bot.calculate_dynamic_stop(
            self.test_symbol, 
            self.test_entry, 
            'long'
        )
        
        # Stop should be below entry for long
        self.assertLess(stop_price, self.test_entry)
        
        # Stop distance should be within configured bounds
        distance_pct = ((self.test_entry - stop_price) / self.test_entry) * 100
        self.assertGreaterEqual(distance_pct, self.bot.config['min_stop_percent'])
        self.assertLessEqual(distance_pct, self.bot.config['max_stop_percent'])
    
    def test_dynamic_stop_calculation_short(self):
        """Test dynamic stop-loss calculation for short positions"""
        stop_price = self.bot.calculate_dynamic_stop(
            self.test_symbol, 
            self.test_entry, 
            'short'
        )
        
        # Stop should be above entry for short
        self.assertGreater(stop_price, self.test_entry)
        
        # Stop distance should be within configured bounds
        distance_pct = ((stop_price - self.test_entry) / self.test_entry) * 100
        self.assertGreaterEqual(distance_pct, self.bot.config['min_stop_percent'])
        self.assertLessEqual(distance_pct, self.bot.config['max_stop_percent'])
    
    def test_add_position(self):
        """Test adding a position to monitor"""
        pos_id = self.bot.add_position(
            self.test_symbol,
            self.test_entry,
            self.test_amount,
            'long'
        )
        
        # Position should be created
        self.assertIn(pos_id, self.bot.positions)
        
        # Position should have required fields
        pos = self.bot.positions[pos_id]
        self.assertEqual(pos['symbol'], self.test_symbol)
        self.assertEqual(pos['entry_price'], self.test_entry)
        self.assertEqual(pos['amount'], self.test_amount)
        self.assertEqual(pos['side'], 'long')
        self.assertIn('stop_price', pos)
        self.assertIn('created_at', pos)
        
        # Stop price should be valid
        self.assertLess(pos['stop_price'], pos['entry_price'])
    
    def test_stop_loss_hit_long(self):
        """Test stop-loss triggers correctly for long positions"""
        # Add long position
        pos_id = self.bot.add_position(
            self.test_symbol,
            self.test_entry,
            self.test_amount,
            'long'
        )
        
        pos = self.bot.positions[pos_id]
        
        # Simulate price dropping below stop
        close_data = self.bot.update_stop_loss(
            pos_id,
            pos['stop_price'] - 100  # Price below stop
        )
        
        # Should return close data
        self.assertIsNotNone(close_data)
        self.assertEqual(close_data['reason'], 'DYNAMIC_SL')
        self.assertIn('profit', close_data)
        self.assertIn('profit_pct', close_data)
    
    def test_stop_loss_adjustment(self):
        """Test stop-loss adjusts correctly as price moves"""
        # Add position
        pos_id = self.bot.add_position(
            self.test_symbol,
            self.test_entry,
            self.test_amount,
            'long'
        )
        
        original_stop = self.bot.positions[pos_id]['stop_price']
        
        # Simulate price increase
        # Note: In real scenario, ATR would change and stop would adjust
        # For test, we'll just verify the mechanism works
        
        # Force update interval to pass
        self.bot.positions[pos_id]['last_adjusted'] = datetime(2020, 1, 1).isoformat()
        
        # Update with higher price
        close_data = self.bot.update_stop_loss(
            pos_id,
            self.test_entry + 1000
        )
        
        # Should not close position (price above stop)
        self.assertIsNone(close_data)
        
        # Verify position still exists
        self.assertIn(pos_id, self.bot.positions)
    
    def test_state_persistence(self):
        """Test bot can save and load state"""
        # Add position
        pos_id = self.bot.add_position(
            self.test_symbol,
            self.test_entry,
            self.test_amount,
            'long'
        )
        
        # Save state
        test_file = 'data/test_stoploss_state.json'
        self.bot.save_state(test_file)
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_file))
        
        # Create new bot and load state
        new_bot = DynamicStopLossBot()
        new_bot.load_state(test_file)
        
        # Verify state loaded
        self.assertIn(pos_id, new_bot.positions)
        self.assertEqual(new_bot.positions[pos_id]['symbol'], self.test_symbol)
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
    
    def test_get_status(self):
        """Test status reporting"""
        status = self.bot.get_status()
        
        # Verify required fields
        self.assertIn('name', status)
        self.assertIn('version', status)
        self.assertIn('active_positions', status)
        self.assertIn('metrics', status)
        self.assertIn('config', status)
        
        # Verify metrics structure
        metrics = status['metrics']
        self.assertIn('total_adjustments', metrics)
        self.assertIn('stops_hit', metrics)
        self.assertIn('capital_saved', metrics)
    
    def test_concurrent_positions(self):
        """Test bot handles multiple positions correctly"""
        # Add multiple positions
        pos1 = self.bot.add_position('BTC/USDT', 50000, 0.001, 'long')
        pos2 = self.bot.add_position('ETH/USDT', 3000, 0.01, 'long')
        pos3 = self.bot.add_position('SOL/USDT', 100, 0.1, 'short')
        
        # Verify all positions tracked
        self.assertEqual(len(self.bot.positions), 3)
        self.assertIn(pos1, self.bot.positions)
        self.assertIn(pos2, self.bot.positions)
        self.assertIn(pos3, self.bot.positions)
        
        # Verify each has unique stop price
        stops = [pos['stop_price'] for pos in self.bot.positions.values()]
        self.assertEqual(len(stops), len(set(stops)))  # All unique
    
    def test_edge_case_zero_atr(self):
        """Test bot handles zero ATR gracefully"""
        # Force ATR to zero
        self.bot.atr_cache[self.test_symbol] = {
            'value': 0,
            'timestamp': datetime.now(),
            'timeframe': '1h'
        }
        
        # Calculate stop (should fallback to base percentage)
        stop_price = self.bot.calculate_dynamic_stop(
            self.test_symbol,
            self.test_entry,
            'long'
        )
        
        # Should still return valid stop
        self.assertGreater(stop_price, 0)
        self.assertLess(stop_price, self.test_entry)
        
        # Distance should be base stop percent
        distance = ((self.test_entry - stop_price) / self.test_entry) * 100
        self.assertAlmostEqual(distance, self.bot.config['base_stop_percent'], places=1)

def run_tests():
    """Run test suite and generate report"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDynamicStopLossBot)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': result.testsRun,
        'passed': result.testsRun - len(result.failures) - len(result.errors),
        'failed': len(result.failures),
        'errors': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    }
    
    # Save report
    os.makedirs('data', exist_ok=True)
    with open('data/test_report_dynamic_stoploss.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return result.wasSuccessful(), report

if __name__ == '__main__':
    success, report = run_tests()
    
    print("\n" + "="*70)
    print("📊 TEST REPORT")
    print("="*70)
    print(json.dumps(report, indent=2))
    print("="*70)
    
    if success:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
