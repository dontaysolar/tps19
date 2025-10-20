#!/usr/bin/env python3
"""NEXUS Coordinator - Central lightweight decision orchestrator for TPS19.

Combines signals from SIUL, TransformerAnalyzer, and other components
into a consolidated decision with an aggregated confidence and rationale.

This is intentionally lightweight and dependency-free. It can be upgraded
later to a full-blown orchestrator without changing the public API.
"""

from __future__ import annotations

from typing import Dict, Optional


class NexusCoordinator:
    """Lightweight coordinator to combine multiple subsystem decisions."""

    def __init__(self) -> None:
        pass

    def combine_decisions(
        self,
        siul_decision: Optional[Dict],
        transformer_prediction: Optional[Dict],
        recommended_position_value: Optional[float] = None,
    ) -> Dict:
        """Combine SIUL decision and Transformer prediction.

        Args:
            siul_decision: Dict with fields like {'decision': 'buy|sell|hold', 'confidence': float}
            transformer_prediction: Dict with fields like {'direction': 'UP|DOWN|HOLD', 'confidence': float}
            recommended_position_value: Optional position sizing recommendation (absolute $ value)
        Returns:
            Unified decision dict.
        """
        final_signal = 'hold'
        final_confidence = 0.0
        rationale = []

        if siul_decision and isinstance(siul_decision, dict):
            siul_sig = siul_decision.get('decision', 'hold')
            siul_conf = float(siul_decision.get('confidence', 0.0) or 0.0)
            rationale.append(f"SIUL={siul_sig}({siul_conf:.2f})")
        else:
            siul_sig, siul_conf = 'hold', 0.0
            rationale.append("SIUL=hold(0.00)")

        if transformer_prediction and isinstance(transformer_prediction, dict):
            t_dir = transformer_prediction.get('direction', 'HOLD')
            t_conf = float(transformer_prediction.get('confidence', 0.0) or 0.0)
            rationale.append(f"TX={t_dir}({t_conf:.2f})")
        else:
            t_dir, t_conf = 'HOLD', 0.0
            rationale.append("TX=HOLD(0.00)")

        # Map Transformer direction into buy/sell/hold
        t_sig = 'buy' if t_dir == 'UP' else 'sell' if t_dir == 'DOWN' else 'hold'

        # Simple combination logic: require alignment or high confidence from one side
        if siul_sig == 'buy' and t_sig in ('buy', 'hold'):
            final_signal = 'buy'
        elif siul_sig == 'sell' and t_sig in ('sell', 'hold'):
            final_signal = 'sell'
        elif t_sig == 'buy' and siul_sig in ('buy', 'hold'):
            final_signal = 'buy'
        elif t_sig == 'sell' and siul_sig in ('sell', 'hold'):
            final_signal = 'sell'
        else:
            final_signal = 'hold'

        # Aggregate confidence: weighted average
        weights_total = 0.0
        if siul_conf > 0:
            final_confidence += siul_conf * 0.6
            weights_total += 0.6
        if t_conf > 0:
            final_confidence += t_conf * 0.4
            weights_total += 0.4
        if weights_total > 0:
            final_confidence /= weights_total

        unified = {
            'signal': final_signal,
            'confidence': round(final_confidence, 4),
            'recommended_position_value': float(recommended_position_value) if recommended_position_value is not None else None,
            'rationale': rationale,
        }
        return unified
