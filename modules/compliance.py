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

    def can_trade(self, state: Dict, signal_confidence: float) -> Dict:
        """Return a gating result with allow boolean and reason.

        Args:
            state: system/trader state with at least 'cycle' and optional 'trade_count_today'
            signal_confidence: confidence (0..1)
        """
        trade_count = int(state.get('trade_count_today', 0))
        if trade_count >= self.max_daily_trades:
            return {'allow': False, 'reason': 'max_daily_trades_exceeded'}
        min_conf = float(os.environ.get('COMPLIANCE_MIN_CONFIDENCE', '0.55') or 0.55)
        if signal_confidence < min_conf:
            return {'allow': False, 'reason': 'low_confidence'}
        return {'allow': True, 'reason': 'ok'}
