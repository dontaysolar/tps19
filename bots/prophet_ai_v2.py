#!/usr/bin/env python3
"""
Prophet AI v2.0 - Long-Term Trend Forecaster
MIGRATED TO AEGIS ARCHITECTURE

Features: 1-30 day trend forecasting with SMA analysis
Part of APEX AI Trading System - Strategy Layer
"""

import os, sys
from datetime import datetime, timedelta
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

try:
    import numpy as np
except ImportError:
    np = None

from trading_bot_base import TradingBotBase

class ProphetAI(TradingBotBase):
    """Long-term trend forecasting (1-30 days)"""
    
    def __init__(self, exchange_config=None):
        super().__init__(
            bot_name="PROPHET_AI",
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        assert hasattr(self, 'exchange_adapter'), "Base init failed"
        
        self.forecasts = {}
        self.metrics.update({'forecasts_made': 0, 'accuracy': 0.0})
    
    def forecast_trend(self, symbol: str, days_ahead: int = 7) -> Dict:
        """Forecast price trend for next N days"""
        assert len(symbol) > 0, "Symbol required"
        assert days_ahead > 0, "Days must be positive"
        
        try:
            ohlcv = self.exchange_adapter.get_ohlcv(symbol, '1d', limit=90)
            if not ohlcv or len(ohlcv) < 30:
                return {'symbol': symbol, 'error': 'Insufficient data'}
            
            closes = [c[4] for c in ohlcv[:90]]  # Fixed bound
            
            # Calculate SMAs
            sma_30 = sum(closes[-30:]) / 30 if np is None else float(np.mean(closes[-30:]))
            sma_60 = sum(closes[-60:]) / 60 if len(closes) >= 60 else sma_30
            if np and len(closes) >= 60:
                sma_60 = float(np.mean(closes[-60:]))
            
            # Momentum
            momentum_30d = (closes[-1] - closes[-30]) / closes[-30] if closes[-30] > 0 else 0
            trend_strength = abs((sma_30 - sma_60) / sma_60) if sma_60 > 0 else 0
            
            # Forecast
            if sma_30 > sma_60 * 1.05 and momentum_30d > 0:
                forecast, confidence = 'STRONG_BULL', min(0.7 + trend_strength * 2, 0.95)
            elif sma_30 > sma_60:
                forecast, confidence = 'BULL', 0.65 + trend_strength
            elif sma_30 < sma_60 * 0.95 and momentum_30d < 0:
                forecast, confidence = 'STRONG_BEAR', min(0.7 + trend_strength * 2, 0.95)
            elif sma_30 < sma_60:
                forecast, confidence = 'BEAR', 0.65 + trend_strength
            else:
                forecast, confidence = 'SIDEWAYS', 0.6
            
            result = {
                'symbol': symbol, 'forecast': forecast, 'confidence': confidence,
                'days_ahead': days_ahead, 'current_price': closes[-1],
                'momentum_30d': momentum_30d, 'trend_strength': trend_strength,
                'timestamp': datetime.now().isoformat(),
                'valid_until': (datetime.now() + timedelta(days=days_ahead)).isoformat()
            }
            
            self.forecasts[symbol] = result
            self.metrics['forecasts_made'] += 1
            assert isinstance(result, dict), "Result must be dict"
            return result
        except Exception as e:
            self.metrics['errors'] += 1
            return {'symbol': symbol, 'error': str(e)}
    
    def get_status(self) -> Dict:
        base_status = super().get_status()
        assert isinstance(base_status, dict), "Base status invalid"
        base_status.update({'active_forecasts': len(self.forecasts)})
        return base_status

if __name__ == '__main__':
    print("🔮 Prophet AI v2.0 - Test")
    bot = ProphetAI()
    forecast = bot.forecast_trend('BTC/USDT', 7)
    print(f"Forecast: {forecast.get('forecast', 'N/A')} ({forecast.get('confidence', 0)*100:.0f}%)")
    bot.close()
    print("✅ Prophet AI v2.0 migration complete!")
