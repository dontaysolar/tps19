#!/usr/bin/env python3
"""Compliance and pre-trade checks for TPS19.

This module provides a simple gating mechanism to block trades under
certain conditions and log the reason.
"""

from __future__ import annotations

import os
from typing import Dict


class ComplianceGate:
    def __init__(self) -> None:
        self.jurisdiction = os.environ.get('COMPLIANCE_JURISDICTION', 'GLOBAL')
        self.max_daily_trades = int(os.environ.get('COMPLIANCE_MAX_DAILY_TRADES', '200') or 200)
        self.block_leverage = os.environ.get('COMPLIANCE_BLOCK_LEVERAGE', 'true').lower() in ('1', 'true', 'yes')
        self.min_notional = float(os.environ.get('COMPLIANCE_MIN_NOTIONAL', '1') or 1)
        self.cooldown_seconds = int(os.environ.get('COMPLIANCE_COOLDOWN_SECONDS', '15') or 15)

    def can_trade(self, state: Dict, signal_confidence: float, notional_value: float = 0.0) -> Dict:
        """Return a gating result with allow boolean and reason.

        Args:
            state: system/trader state with at least 'cycle' and optional 'trade_count_today'
            signal_confidence: confidence (0..1)
        """
        trade_count = int(state.get('trade_count_today', 0))
        last_trade_ts = int(state.get('last_trade_ts', 0))
        now_ts = int(os.environ.get('EPOCH_NOW', '0') or 0)  # caller may inject for testing
        if trade_count >= self.max_daily_trades:
            return {'allow': False, 'reason': 'max_daily_trades_exceeded'}
        min_conf = float(os.environ.get('COMPLIANCE_MIN_CONFIDENCE', '0.55') or 0.55)
        if signal_confidence < min_conf:
            return {'allow': False, 'reason': 'low_confidence'}
        if notional_value < self.min_notional:
            return {'allow': False, 'reason': 'below_min_notional'}
        if now_ts and last_trade_ts and (now_ts - last_trade_ts) < self.cooldown_seconds:
            return {'allow': False, 'reason': 'cooldown_active'}
        return {'allow': True, 'reason': 'ok'}
