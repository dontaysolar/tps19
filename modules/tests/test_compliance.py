#!/usr/bin/env python3
import os
import unittest

from modules.compliance import ComplianceGate


class TestCompliance(unittest.TestCase):
    def test_low_confidence_blocks(self):
        os.environ['COMPLIANCE_MIN_CONFIDENCE'] = '0.8'
        gate = ComplianceGate()
        res = gate.can_trade({'trade_count_today': 0}, signal_confidence=0.5, notional_value=10)
        self.assertFalse(res['allow'])

    def test_min_notional_blocks(self):
        os.environ['COMPLIANCE_MIN_NOTIONAL'] = '5'
        gate = ComplianceGate()
        res = gate.can_trade({'trade_count_today': 0}, signal_confidence=0.9, notional_value=1)
        self.assertFalse(res['allow'])

    def test_cooldown_blocks(self):
        os.environ['COMPLIANCE_COOLDOWN_SECONDS'] = '30'
        os.environ['EPOCH_NOW'] = '100'
        gate = ComplianceGate()
        res = gate.can_trade({'trade_count_today': 0, 'last_trade_ts': 90}, signal_confidence=0.9, notional_value=100)
        self.assertFalse(res['allow'])


if __name__ == '__main__':
    unittest.main()
