#!/usr/bin/env python3
"""Transformer Analyzer - Lightweight market structure analysis for TPS19

This module provides a lightweight, dependency-friendly approximation of a
transformer-style analyzer suitable for quick signal generation and
market regime analysis without requiring heavyweight deep learning stacks.

Design goals:
- Zero heavy dependencies (uses numpy if available, otherwise pure Python)
- Deterministic, fast computations suitable for live trading loops
- Clear, inspectable outputs with confidences and auxiliary metrics

If you later decide to plug in a real transformer (PyTorch/TF), keep this
class' public interface stable so callers do not need to change.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

try:
    import numpy as np  # type: ignore
    _NUMPY_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    np = None  # type: ignore
    _NUMPY_AVAILABLE = False


@dataclass
class AnalyzerConfig:
    short_ema_window: int = 12
    long_ema_window: int = 26
    volatility_window: int = 20
    momentum_window: int = 14
    min_series_length: int = 30


class TransformerAnalyzer:
    """Lightweight market analyzer exposing transformer-like signals.

    Public API (stable):
    - analyze_market_structure(prices) -> Dict[str, float|str]
    - predict_direction(prices, horizon_steps=30) -> Dict[str, float|str]
    - get_status() -> Dict[str, Any]
    """

    def __init__(self, config: Optional[AnalyzerConfig] = None) -> None:
        self.config: AnalyzerConfig = config or AnalyzerConfig()

    # ---------- public API ----------
    def analyze_market_structure(self, price_series: List[float]) -> Dict[str, object]:
        prices = self._sanitize_series(price_series)
        if len(prices) < self.config.min_series_length:
            return {
                'regime': 'UNKNOWN',
                'trend_strength': 0.0,
                'volatility': 0.0,
                'momentum': 0.0,
                'support': None,
                'resistance': None,
                'confidence': 0.0,
                'notes': 'insufficient_data'
            }

        short_ema = self._ema(prices, self.config.short_ema_window)
        long_ema = self._ema(prices, self.config.long_ema_window)

        trend_strength = self._normalize(self._last(short_ema) - self._last(long_ema), denom=self._last(long_ema))
        volatility = self._volatility(prices, self.config.volatility_window)
        momentum = self._momentum(prices, self.config.momentum_window)
        regime = self._regime(trend_strength, volatility)
        support, resistance = self._support_resistance(prices)
        confidence = self._confidence(trend_strength, momentum, volatility)

        return {
            'regime': regime,
            'trend_strength': trend_strength,
            'volatility': volatility,
            'momentum': momentum,
            'support': support,
            'resistance': resistance,
            'confidence': confidence
        }

    def predict_direction(self, price_series: List[float], horizon_steps: int = 30) -> Dict[str, object]:
        prices = self._sanitize_series(price_series)
        if len(prices) < self.config.min_series_length:
            return {'direction': 'HOLD', 'confidence': 0.0, 'horizon': horizon_steps}

        short_ema = self._ema(prices, self.config.short_ema_window)
        long_ema = self._ema(prices, self.config.long_ema_window)
        ema_delta = self._last(short_ema) - self._last(long_ema)
        momentum = self._momentum(prices, self.config.momentum_window)
        volatility = self._volatility(prices, self.config.volatility_window)

        # Simple decision logic combining EMA crossover and momentum
        if ema_delta > 0 and momentum > 0:
            direction = 'UP'
        elif ema_delta < 0 and momentum < 0:
            direction = 'DOWN'
        else:
            direction = 'HOLD'

        confidence = self._confidence(
            self._normalize(ema_delta, denom=self._last(long_ema)),
            momentum,
            volatility
        )

        return {
            'direction': direction,
            'confidence': confidence,
            'horizon': horizon_steps,
            'volatility': volatility,
            'momentum': momentum
        }

    def get_status(self) -> Dict[str, object]:
        return {
            'short_ema_window': self.config.short_ema_window,
            'long_ema_window': self.config.long_ema_window,
            'volatility_window': self.config.volatility_window,
            'momentum_window': self.config.momentum_window,
            'numpy_available': _NUMPY_AVAILABLE
        }

    # ---------- helper computations ----------
    def _sanitize_series(self, series: List[float]) -> List[float]:
        return [float(x) for x in series if self._is_finite(x)]

    def _is_finite(self, x: float) -> bool:
        try:
            return math.isfinite(float(x))
        except Exception:
            return False

    def _ema(self, series: List[float], window: int) -> List[float]:
        if not series or window <= 1:
            return list(series)
        if _NUMPY_AVAILABLE:
            arr = np.array(series, dtype=float)
            alpha = 2.0 / (window + 1)
            ema = np.empty_like(arr)
            ema[0] = arr[0]
            for i in range(1, len(arr)):
                ema[i] = alpha * arr[i] + (1 - alpha) * ema[i - 1]
            return ema.tolist()
        # Pure Python fallback
        alpha = 2.0 / (window + 1)
        ema: List[float] = [series[0]]
        for i in range(1, len(series)):
            ema.append(alpha * series[i] + (1 - alpha) * ema[i - 1])
        return ema

    def _volatility(self, series: List[float], window: int) -> float:
        if len(series) < window + 1:
            return 0.0
        returns: List[float] = []
        for i in range(-window, 0):
            prev = series[i - 1]
            curr = series[i]
            if prev != 0:
                returns.append((curr - prev) / prev)
        if not returns:
            return 0.0
        try:
            return float(statistics.pstdev(returns))
        except statistics.StatisticsError:
            return 0.0

    def _momentum(self, series: List[float], window: int) -> float:
        if len(series) < window + 1:
            return 0.0
        start = series[-window - 1]
        end = series[-1]
        return self._normalize(end - start, denom=start)

    def _support_resistance(self, series: List[float]) -> Tuple[Optional[float], Optional[float]]:
        if len(series) < 10:
            return None, None
        recent = series[-50:] if len(series) >= 50 else series
        support = min(recent)
        resistance = max(recent)
        return float(support), float(resistance)

    def _regime(self, trend_strength: float, volatility: float) -> str:
        if abs(trend_strength) < 0.001:
            return 'RANGING'
        if trend_strength > 0:
            return 'BULLISH' if volatility < 0.02 else 'BULLISH_VOLATILE'
        return 'BEARISH' if volatility < 0.02 else 'BEARISH_VOLATILE'

    def _confidence(self, trend_strength: float, momentum: float, volatility: float) -> float:
        # Heuristic: stronger trend and momentum increase confidence; higher volatility reduces it
        base = 0.5 + 0.3 * self._clip(trend_strength, -0.2, 0.2) + 0.3 * self._clip(momentum, -0.2, 0.2)
        penalty = 0.4 * self._clip(volatility, 0.0, 0.05)  # cap vol effect
        confidence = max(0.0, min(1.0, base - penalty))
        return float(confidence)

    def _normalize(self, value: float, denom: float, eps: float = 1e-9) -> float:
        if abs(denom) < eps:
            return 0.0
        return float(value / denom)

    def _clip(self, x: float, lo: float, hi: float) -> float:
        return float(max(lo, min(hi, x)))

    def _last(self, seq: List[float]) -> float:
        return float(seq[-1]) if seq else 0.0


# ---------- simple self-test ----------
if __name__ == '__main__':
    import random

    analyzer = TransformerAnalyzer()
    prices = []
    price = 100.0
    for _ in range(200):
        price *= (1.0 + random.uniform(-0.01, 0.01))
        prices.append(price)

    structure = analyzer.analyze_market_structure(prices)
    pred = analyzer.predict_direction(prices, horizon_steps=30)

    print('Structure:', structure)
    print('Prediction:', pred)
