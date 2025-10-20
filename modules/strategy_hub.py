#!/usr/bin/env python3
"""Strategy Hub - selection and coordination of multiple strategies."""

from __future__ import annotations

from typing import Dict, List


class StrategyHub:
    def __init__(self) -> None:
        self.enabled_strategies: List[str] = ['scalping', 'trend_following', 'mean_reversion']
        self.weights: Dict[str, float] = {k: 1.0 for k in self.enabled_strategies}

    def select(self, candidates: List[Dict]) -> Dict:
        """Select the best signal among candidates.
        Each candidate: {'strategy': str, 'pair': str, 'signal': 'BUY|SELL|HOLD', 'confidence': float}
        """
        if not candidates:
            return {}
        # Weighted max by confidence; unknown strategy weight = 1.0
        best = max(
            candidates,
            key=lambda c: (float(c.get('confidence', 0.0)) * float(self.weights.get(c.get('strategy', ''), 1.0)))
        )
        return best

    def set_weights(self, weights: Dict[str, float]) -> None:
        for k, v in weights.items():
            try:
                self.weights[k] = float(v)
            except Exception:
                continue
