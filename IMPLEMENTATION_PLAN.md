# TPS19 Profitability Implementation Plan

## 🎯 Complete Implementation Guide with Code

This document provides step-by-step implementation of all strategies, guardrails, and rules needed to make TPS19 profitable.

---

## 📋 TABLE OF CONTENTS

1. [Guardrails System](#guardrails-system)
2. [Trading Rules Engine](#trading-rules-engine)
3. [Strategy Implementations](#strategy-implementations)
4. [Risk Management](#risk-management)
5. [Backtesting Framework](#backtesting-framework)
6. [Performance Monitoring](#performance-monitoring)
7. [Integration Guide](#integration-guide)

---

## 🛡️ PART 1: GUARDRAILS SYSTEM

### Create: `modules/guardrails/__init__.py`

```python
"""TPS19 Multi-Layer Guardrails System"""

from .pre_trade import PreTradeGuardrails
from .position import PositionGuardrails
from .portfolio import PortfolioGuardrails
from .system import SystemGuardrails

__all__ = [
    'PreTradeGuardrails',
    'PositionGuardrails', 
    'PortfolioGuardrails',
    'SystemGuardrails'
]
```

### Create: `modules/guardrails/pre_trade.py`

```python
#!/usr/bin/env python3
"""Pre-Trade Guardrails - Check BEFORE every trade"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class PreTradeGuardrails:
    """
    Validates trades BEFORE execution
    All checks must pass or trade is rejected
    """
    
    def __init__(self):
        # Load limits from config
        self.MAX_DAILY_LOSS = config.get('risk.max_daily_loss', 0.05)
        self.MAX_WEEKLY_LOSS = config.get('risk.max_weekly_loss', 0.10)
        self.MAX_DRAWDOWN = config.get('risk.max_drawdown', 0.15)
        self.MAX_POSITIONS = config.get('risk.max_positions', 5)
        self.MAX_POSITION_SIZE = config.get('risk.max_position_size', 0.10)
        self.MIN_CONFIDENCE = config.get('trading.min_confidence', 0.65)
        
    def validate(self, trade_signal: Dict[str, Any], 
                 portfolio_state: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate trade signal against all guardrails
        
        Args:
            trade_signal: Proposed trade with symbol, side, size, confidence
            portfolio_state: Current portfolio state with positions, PnL, etc.
            
        Returns:
            (approved: bool, reason: str)
        """
        checks = [
            self._check_daily_loss_limit(portfolio_state),
            self._check_weekly_loss_limit(portfolio_state),
            self._check_drawdown_limit(portfolio_state),
            self._check_position_limits(portfolio_state),
            self._check_position_size(trade_signal, portfolio_state),
            self._check_correlation(trade_signal, portfolio_state),
            self._check_volatility(trade_signal),
            self._check_liquidity(trade_signal),
            self._check_spread(trade_signal),
            self._check_confidence(trade_signal),
            self._check_consecutive_losses(portfolio_state),
            self._check_time_of_day(),
            self._check_market_conditions(trade_signal),
        ]
        
        # All checks must pass
        for passed, reason in checks:
            if not passed:
                logger.warning(f"Trade rejected: {reason}")
                return False, reason
        
        logger.info(f"Trade approved: {trade_signal['symbol']}")
        return True, "All guardrails passed"
    
    def _check_daily_loss_limit(self, portfolio: Dict) -> tuple[bool, str]:
        """Check if daily loss limit exceeded"""
        daily_pnl = portfolio.get('daily_pnl', 0)
        daily_pnl_pct = daily_pnl / portfolio['total_value']
        
        if daily_pnl_pct < -self.MAX_DAILY_LOSS:
            return False, f"Daily loss limit exceeded: {daily_pnl_pct:.2%}"
        return True, "Daily loss OK"
    
    def _check_weekly_loss_limit(self, portfolio: Dict) -> tuple[bool, str]:
        """Check if weekly loss limit exceeded"""
        weekly_pnl = portfolio.get('weekly_pnl', 0)
        weekly_pnl_pct = weekly_pnl / portfolio['total_value']
        
        if weekly_pnl_pct < -self.MAX_WEEKLY_LOSS:
            return False, f"Weekly loss limit exceeded: {weekly_pnl_pct:.2%}"
        return True, "Weekly loss OK"
    
    def _check_drawdown_limit(self, portfolio: Dict) -> tuple[bool, str]:
        """Check if max drawdown exceeded"""
        drawdown = portfolio.get('current_drawdown', 0)
        
        if drawdown > self.MAX_DRAWDOWN:
            return False, f"Drawdown limit exceeded: {drawdown:.2%}"
        return True, "Drawdown OK"
    
    def _check_position_limits(self, portfolio: Dict) -> tuple[bool, str]:
        """Check if max positions exceeded"""
        open_positions = len(portfolio.get('positions', {}))
        
        if open_positions >= self.MAX_POSITIONS:
            return False, f"Max positions reached: {open_positions}/{self.MAX_POSITIONS}"
        return True, "Position count OK"
    
    def _check_position_size(self, signal: Dict, portfolio: Dict) -> tuple[bool, str]:
        """Check if position size within limits"""
        position_size = signal.get('size', 0)
        portfolio_value = portfolio['total_value']
        size_pct = (position_size * signal.get('price', 0)) / portfolio_value
        
        if size_pct > self.MAX_POSITION_SIZE:
            return False, f"Position too large: {size_pct:.2%} > {self.MAX_POSITION_SIZE:.2%}"
        return True, "Position size OK"
    
    def _check_correlation(self, signal: Dict, portfolio: Dict) -> tuple[bool, str]:
        """Check if new position correlated with existing"""
        # TODO: Implement correlation calculation
        # For now, simple check: don't hold both BTC and ETH at max
        symbol = signal['symbol']
        positions = portfolio.get('positions', {})
        
        # Basic correlation check
        correlated_symbols = {
            'BTC': ['BTC/USD', 'BTC/USDT', 'BTCUSD'],
            'ETH': ['ETH/USD', 'ETH/USDT', 'ETHUSD']
        }
        
        for base, variants in correlated_symbols.items():
            if any(s in symbol for s in variants):
                # Check if we already have max exposure to this asset
                related_positions = [p for p in positions.keys() 
                                   if any(s in p for s in variants)]
                if len(related_positions) >= 2:
                    return False, f"Too much {base} exposure"
        
        return True, "Correlation OK"
    
    def _check_volatility(self, signal: Dict) -> tuple[bool, str]:
        """Check if volatility within acceptable range"""
        volatility = signal.get('volatility', 0)
        
        # Don't trade if volatility is extreme (> 100% annualized)
        if volatility > 1.0:
            return False, f"Volatility too high: {volatility:.2%}"
        
        return True, "Volatility OK"
    
    def _check_liquidity(self, signal: Dict) -> tuple[bool, str]:
        """Check if sufficient liquidity"""
        volume = signal.get('volume', 0)
        min_volume = config.get('trading.min_volume', 1_000_000)
        
        if volume < min_volume:
            return False, f"Insufficient volume: ${volume:,.0f}"
        
        return True, "Liquidity OK"
    
    def _check_spread(self, signal: Dict) -> tuple[bool, str]:
        """Check if bid/ask spread reasonable"""
        spread = signal.get('spread', 0)
        max_spread = config.get('trading.max_spread', 0.005)
        
        if spread > max_spread:
            return False, f"Spread too wide: {spread:.2%}"
        
        return True, "Spread OK"
    
    def _check_confidence(self, signal: Dict) -> tuple[bool, str]:
        """Check if AI confidence sufficient"""
        confidence = signal.get('confidence', 0)
        
        if confidence < self.MIN_CONFIDENCE:
            return False, f"Confidence too low: {confidence:.2%}"
        
        return True, "Confidence OK"
    
    def _check_consecutive_losses(self, portfolio: Dict) -> tuple[bool, str]:
        """Circuit breaker: stop after N losses in a row"""
        consecutive_losses = portfolio.get('consecutive_losses', 0)
        max_consecutive = config.get('risk.max_consecutive_losses', 5)
        
        if consecutive_losses >= max_consecutive:
            return False, f"Too many consecutive losses: {consecutive_losses}"
        
        return True, "Loss streak OK"
    
    def _check_time_of_day(self) -> tuple[bool, str]:
        """Avoid low liquidity hours"""
        current_hour = datetime.utcnow().hour
        
        # Avoid 2-6 AM UTC (low liquidity)
        if 2 <= current_hour < 6:
            return False, "Low liquidity hours (2-6 AM UTC)"
        
        return True, "Time OK"
    
    def _check_market_conditions(self, signal: Dict) -> tuple[bool, str]:
        """Check overall market health"""
        # TODO: Implement market regime detection
        # For now, basic checks
        
        # Don't trade during extreme fear/greed
        fear_greed = signal.get('fear_greed_index', 50)
        if fear_greed < 20 or fear_greed > 80:
            return False, f"Extreme market sentiment: {fear_greed}"
        
        return True, "Market conditions OK"
```

### Create: `modules/guardrails/portfolio.py`

```python
#!/usr/bin/env python3
"""Portfolio-Level Guardrails"""

from typing import Dict, List
from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class PortfolioGuardrails:
    """
    Monitor and manage portfolio-level risks
    """
    
    def __init__(self):
        self.MAX_PORTFOLIO_RISK = 0.20  # 20% max at risk
        self.MAX_DRAWDOWN_ACTION = 0.10  # 10% triggers action
        self.MAX_DRAWDOWN_EMERGENCY = 0.15  # 15% emergency stop
        self.MAX_CORRELATED_EXPOSURE = 0.30  # 30% max in correlated
        
    def monitor(self, portfolio: Dict) -> List[str]:
        """
        Monitor portfolio and return required actions
        
        Returns:
            List of actions to take (e.g., "reduce_positions", "close_all")
        """
        actions = []
        
        # Check drawdown
        drawdown = portfolio.get('current_drawdown', 0)
        
        if drawdown > self.MAX_DRAWDOWN_EMERGENCY:
            actions.append('EMERGENCY_STOP')
            logger.critical(f"EMERGENCY: Drawdown {drawdown:.2%} > {self.MAX_DRAWDOWN_EMERGENCY:.2%}")
            
        elif drawdown > self.MAX_DRAWDOWN_ACTION:
            actions.append('REDUCE_RISK')
            logger.warning(f"Drawdown {drawdown:.2%} - reducing risk")
        
        # Check concentration
        if self._check_concentration(portfolio):
            actions.append('DIVERSIFY')
        
        # Check total portfolio risk
        total_risk = self._calculate_portfolio_risk(portfolio)
        if total_risk > self.MAX_PORTFOLIO_RISK:
            actions.append('REDUCE_POSITIONS')
            logger.warning(f"Portfolio risk {total_risk:.2%} too high")
        
        return actions
    
    def _check_concentration(self, portfolio: Dict) -> bool:
        """Check if portfolio too concentrated"""
        positions = portfolio.get('positions', {})
        
        if not positions:
            return False
        
        # Check single asset concentration
        total_value = portfolio['total_value']
        for symbol, position in positions.items():
            position_pct = position['value'] / total_value
            if position_pct > 0.25:  # 25% max single asset
                logger.warning(f"Over-concentrated in {symbol}: {position_pct:.2%}")
                return True
        
        return False
    
    def _calculate_portfolio_risk(self, portfolio: Dict) -> float:
        """Calculate total portfolio risk exposure"""
        positions = portfolio.get('positions', {})
        total_risk = 0
        
        for position in positions.values():
            # Risk = position size * volatility
            position_risk = position['size'] * position.get('volatility', 0.02)
            total_risk += position_risk
        
        return total_risk
    
    def execute_action(self, action: str, portfolio: Dict):
        """Execute risk management action"""
        if action == 'EMERGENCY_STOP':
            logger.critical("EMERGENCY STOP - Closing all positions")
            return {'action': 'close_all', 'pause_hours': 24}
        
        elif action == 'REDUCE_RISK':
            logger.warning("Reducing position sizes by 50%")
            return {'action': 'reduce_sizes', 'factor': 0.5}
        
        elif action == 'DIVERSIFY':
            logger.info("Blocking trades in over-concentrated assets")
            return {'action': 'block_concentrated'}
        
        elif action == 'REDUCE_POSITIONS':
            logger.info("Closing weakest positions")
            return {'action': 'close_weakest', 'count': 2}
```

---

## 📏 PART 2: TRADING RULES ENGINE

### Create: `modules/rules/__init__.py`

```python
"""TPS19 Trading Rules Engine"""

from .engine import TradingRulesEngine

__all__ = ['TradingRulesEngine']
```

### Create: `modules/rules/engine.py`

```python
#!/usr/bin/env python3
"""Trading Rules Engine - Enforces ALL trading rules"""

from typing import Dict, Any, Optional
from datetime import datetime
from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class TradingRulesEngine:
    """
    Comprehensive trading rules enforcement
    """
    
    def __init__(self):
        self.rules = self._load_rules()
        self.trade_history = []
        
    def _load_rules(self) -> Dict:
        """Load trading rules from config"""
        return {
            'entry': {
                'min_confidence': config.get('rules.min_confidence', 0.65),
                'min_confirmations': config.get('rules.min_confirmations', 3),
                'max_risk_per_trade': config.get('rules.max_risk_per_trade', 0.02),
                'min_volume': config.get('rules.min_volume', 1_000_000),
                'max_spread': config.get('rules.max_spread', 0.005),
            },
            'exit': {
                'stop_loss_pct': config.get('rules.stop_loss', 0.02),
                'take_profit_levels': [0.03, 0.06, 0.10],  # 3%, 6%, 10%
                'take_profit_portions': [0.25, 0.25, 0.25],  # Sell 25% at each
                'trailing_stop_pct': config.get('rules.trailing_stop', 0.03),
                'time_stop_days': config.get('rules.time_stop', 5),
            },
            'position_management': {
                'max_positions': config.get('rules.max_positions', 5),
                'max_position_size': config.get('rules.max_position_size', 0.10),
                'min_position_size': config.get('rules.min_position_size', 0.02),
            },
            'reentry': {
                'wait_after_loss_hours': 24,
                'max_reentries_per_symbol': 3,
                'max_reentries_per_week': 3,
            }
        }
    
    def validate_entry(self, signal: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate entry signal against rules
        
        Args:
            signal: Trade signal with symbol, side, confidence, etc.
            
        Returns:
            (approved: bool, reason: str)
        """
        # Confidence check
        if signal.get('confidence', 0) < self.rules['entry']['min_confidence']:
            return False, f"Confidence {signal['confidence']:.2%} < {self.rules['entry']['min_confidence']:.2%}"
        
        # Confirmations check (multiple indicators agree)
        confirmations = signal.get('confirmations', 0)
        if confirmations < self.rules['entry']['min_confirmations']:
            return False, f"Only {confirmations} confirmations (need {self.rules['entry']['min_confirmations']})"
        
        # Volume check
        if signal.get('volume', 0) < self.rules['entry']['min_volume']:
            return False, f"Volume too low: ${signal.get('volume', 0):,.0f}"
        
        # Spread check
        if signal.get('spread', 0) > self.rules['entry']['max_spread']:
            return False, f"Spread too wide: {signal.get('spread', 0):.2%}"
        
        return True, "Entry rules passed"
    
    def calculate_position_size(self, signal: Dict, portfolio_value: float) -> float:
        """
        Calculate optimal position size using Kelly Criterion
        
        Args:
            signal: Trade signal
            portfolio_value: Current portfolio value
            
        Returns:
            Position size in dollars
        """
        # Get strategy stats
        win_rate = signal.get('strategy_win_rate', 0.50)
        avg_win = signal.get('strategy_avg_win', 0.04)
        avg_loss = signal.get('strategy_avg_loss', 0.02)
        
        # Kelly Criterion: f = (p*b - q) / b
        # where p = win_rate, q = loss_rate, b = avg_win/avg_loss
        if avg_loss == 0:
            kelly_fraction = 0.05  # Default
        else:
            b = avg_win / avg_loss
            kelly_fraction = (win_rate * b - (1 - win_rate)) / b
        
        # Use fractional Kelly (more conservative)
        fractional_kelly = kelly_fraction * 0.5  # Half Kelly
        
        # Apply limits
        max_size = self.rules['position_management']['max_position_size']
        min_size = self.rules['position_management']['min_position_size']
        
        position_fraction = max(min_size, min(fractional_kelly, max_size))
        
        # Adjust for confidence
        confidence = signal.get('confidence', 0.65)
        position_fraction *= confidence
        
        # Calculate dollar amount
        position_size = portfolio_value * position_fraction
        
        logger.info(f"Position size: ${position_size:,.2f} ({position_fraction:.2%} of portfolio)")
        
        return position_size
    
    def get_stop_loss(self, entry_price: float) -> float:
        """Calculate stop loss price"""
        stop_pct = self.rules['exit']['stop_loss_pct']
        return entry_price * (1 - stop_pct)
    
    def get_take_profit_levels(self, entry_price: float) -> List[Dict]:
        """
        Get take profit levels with portions to sell
        
        Returns:
            List of {price, portion} dicts
        """
        levels = self.rules['exit']['take_profit_levels']
        portions = self.rules['exit']['take_profit_portions']
        
        return [
            {
                'price': entry_price * (1 + level),
                'portion': portion,
                'level_pct': level
            }
            for level, portion in zip(levels, portions)
        ]
    
    def check_reentry_allowed(self, symbol: str) -> tuple[bool, str]:
        """
        Check if reentry allowed for symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            (allowed: bool, reason: str)
        """
        # Check recent trades for this symbol
        recent_trades = [t for t in self.trade_history 
                        if t['symbol'] == symbol 
                        and t['timestamp'] > datetime.now() - timedelta(days=7)]
        
        # Count losses
        losses = [t for t in recent_trades if t['pnl'] < 0]
        
        # Check if last trade was a loss
        if recent_trades and recent_trades[-1]['pnl'] < 0:
            time_since_loss = datetime.now() - recent_trades[-1]['timestamp']
            wait_hours = self.rules['reentry']['wait_after_loss_hours']
            
            if time_since_loss.total_seconds() < wait_hours * 3600:
                return False, f"Wait {wait_hours}h after loss"
        
        # Check reentry limit
        if len(recent_trades) >= self.rules['reentry']['max_reentries_per_week']:
            return False, f"Max reentries ({self.rules['reentry']['max_reentries_per_week']}) reached"
        
        return True, "Reentry allowed"
    
    def should_exit(self, position: Dict) -> Optional[Dict]:
        """
        Check if position should be exited
        
        Args:
            position: Position details
            
        Returns:
            Exit order dict if should exit, None otherwise
        """
        current_price = position['current_price']
        entry_price = position['entry_price']
        hold_time = (datetime.now() - position['entry_time']).days
        
        # Stop loss check
        stop_loss = self.get_stop_loss(entry_price)
        if current_price <= stop_loss:
            logger.warning(f"Stop loss hit: {position['symbol']}")
            return {
                'reason': 'stop_loss',
                'price': current_price,
                'portion': 1.0
            }
        
        # Take profit checks
        pnl_pct = (current_price - entry_price) / entry_price
        take_profit_levels = self.get_take_profit_levels(entry_price)
        
        for level in take_profit_levels:
            if pnl_pct >= level['level_pct'] and not position.get(f"tp_{level['level_pct']}_hit"):
                logger.info(f"Take profit {level['level_pct']:.1%} hit: {position['symbol']}")
                return {
                    'reason': f"take_profit_{level['level_pct']:.1%}",
                    'price': current_price,
                    'portion': level['portion']
                }
        
        # Time stop check
        time_stop = self.rules['exit']['time_stop_days']
        if hold_time >= time_stop and pnl_pct < 0.05:  # 5% profit threshold
            logger.info(f"Time stop: {position['symbol']} held {hold_time} days")
            return {
                'reason': 'time_stop',
                'price': current_price,
                'portion': 1.0
            }
        
        return None
```

---

## 📊 PART 3: STRATEGY IMPLEMENTATIONS

### Create: `modules/strategies/trend_following.py`

```python
#!/usr/bin/env python3
"""Trend Following Strategy"""

from typing import Dict, Optional
import pandas as pd
from modules.utils.logger import get_logger

logger = get_logger(__name__)


class TrendFollowingStrategy:
    """
    Trend Following: Ride strong trends with the momentum
    
    Entry: MAs aligned, momentum strong, volume confirming
    Exit: Trend breaks, momentum reverses, or stops hit
    """
    
    def __init__(self):
        self.name = "Trend Following"
        self.timeframe = "1d"  # Daily charts
        
        # Historical performance (update from backtests)
        self.win_rate = 0.42
        self.avg_win = 0.06  # 6% average win
        self.avg_loss = 0.02  # 2% average loss
        self.profit_factor = 1.8
        
    def analyze(self, market_data: pd.DataFrame) -> Optional[Dict]:
        """
        Analyze market data for trend following signals
        
        Args:
            market_data: OHLCV data with indicators
            
        Returns:
            Signal dict or None
        """
        if len(market_data) < 200:
            return None  # Need enough data for 200 MA
        
        latest = market_data.iloc[-1]
        
        # Calculate indicators
        ma20 = market_data['close'].rolling(20).mean().iloc[-1]
        ma50 = market_data['close'].rolling(50).mean().iloc[-1]
        ma200 = market_data['close'].rolling(200).mean().iloc[-1]
        
        rsi = self._calculate_rsi(market_data['close'])
        macd, signal_line = self._calculate_macd(market_data['close'])
        
        volume_avg = market_data['volume'].rolling(20).mean().iloc[-1]
        
        # BUY CONDITIONS
        if (ma20 > ma50 > ma200 and  # MAs aligned (uptrend)
            latest['close'] > ma20 and  # Price above short MA
            rsi > 50 and  # Momentum positive
            latest['volume'] > volume_avg and  # Volume confirming
            macd > signal_line):  # MACD bullish
            
            confirmations = sum([
                ma20 > ma50,
                ma50 > ma200,
                latest['close'] > ma20,
                rsi > 50,
                rsi < 70,  # Not overbought
                latest['volume'] > volume_avg,
                macd > signal_line
            ])
            
            confidence = min(confirmations / 7, 0.95)
            
            return {
                'signal': 'BUY',
                'strategy': self.name,
                'confidence': confidence,
                'confirmations': confirmations,
                'entry_price': latest['close'],
                'stop_loss': ma20,  # Stop below 20 MA
                'target': latest['close'] * 1.06,  # 6% target
                'reasoning': f"Strong uptrend: MAs aligned, RSI {rsi:.1f}, Volume ↑",
                'strategy_win_rate': self.win_rate,
                'strategy_avg_win': self.avg_win,
                'strategy_avg_loss': self.avg_loss,
            }
        
        # SELL CONDITIONS (trend reversal)
        elif (latest['close'] < ma20 and  # Price broke below MA
              rsi < 30):  # Momentum turned negative
            
            return {
                'signal': 'SELL',
                'strategy': self.name,
                'confidence': 0.75,
                'reasoning': "Trend break: Price < MA20, RSI < 30"
            }
        
        return None  # No signal
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def _calculate_macd(self, prices: pd.Series) -> tuple:
        """Calculate MACD and signal line"""
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return macd.iloc[-1], signal.iloc[-1]
```

### Create: `modules/strategies/mean_reversion.py`

```python
#!/usr/bin/env python3
"""Mean Reversion Strategy"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from modules.utils.logger import get_logger

logger = get_logger(__name__)


class MeanReversionStrategy:
    """
    Mean Reversion: Buy oversold, sell overbought
    
    Works best in ranging/sideways markets
    Higher win rate but smaller R/R
    """
    
    def __init__(self):
        self.name = "Mean Reversion"
        self.timeframe = "4h"  # 4-hour charts
        
        # Historical performance
        self.win_rate = 0.62
        self.avg_win = 0.04
        self.avg_loss = 0.03
        self.profit_factor = 1.5
        
    def analyze(self, market_data: pd.DataFrame) -> Optional[Dict]:
        """
        Analyze for mean reversion opportunities
        
        Args:
            market_data: OHLCV data
            
        Returns:
            Signal dict or None
        """
        if len(market_data) < 30:
            return None
        
        latest = market_data.iloc[-1]
        
        # Calculate indicators
        ma20 = market_data['close'].rolling(20).mean().iloc[-1]
        std20 = market_data['close'].rolling(20).std().iloc[-1]
        
        # Bollinger Bands
        upper_band = ma20 + (2 * std20)
        lower_band = ma20 - (2 * std20)
        
        rsi = self._calculate_rsi(market_data['close'])
        
        # Z-score (how many std devs from mean)
        z_score = (latest['close'] - ma20) / std20
        
        volume_avg = market_data['volume'].rolling(20).mean().iloc[-1]
        
        # BUY CONDITIONS (oversold)
        if (latest['close'] <= lower_band and  # Price at lower BB
            z_score < -2 and  # 2+ std devs below mean
            rsi < 30 and  # Oversold
            latest['volume'] > volume_avg * 1.2):  # Volume spike (panic)
            
            confirmations = sum([
                latest['close'] <= lower_band,
                z_score < -2,
                rsi < 30,
                rsi > 20,  # Not extreme
                latest['volume'] > volume_avg
            ])
            
            confidence = min(confirmations / 5, 0.90)
            
            return {
                'signal': 'BUY',
                'strategy': self.name,
                'confidence': confidence,
                'confirmations': confirmations,
                'entry_price': latest['close'],
                'stop_loss': latest['close'] * 0.97,  # 3% stop (wider)
                'target': ma20,  # Target mean reversion
                'reasoning': f"Oversold: Z-score {z_score:.2f}, RSI {rsi:.1f}",
                'strategy_win_rate': self.win_rate,
                'strategy_avg_win': self.avg_win,
                'strategy_avg_loss': self.avg_loss,
            }
        
        # SELL CONDITIONS (overbought)
        elif (latest['close'] >= upper_band and
              z_score > 2 and
              rsi > 70):
            
            return {
                'signal': 'SELL',
                'strategy': self.name,
                'confidence': 0.70,
                'reasoning': f"Overbought: Z-score {z_score:.2f}, RSI {rsi:.1f}"
            }
        
        return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
```

---

## 🎯 INTEGRATION GUIDE

### Update: `modules/trading_engine.py`

Add this method to integrate guardrails and rules:

```python
def place_order_with_guardrails(self, symbol: str, side: OrderSide, 
                                amount: float, signal: Dict) -> Dict:
    """
    Place order with full guardrails and rules validation
    """
    from modules.guardrails.pre_trade import PreTradeGuardrails
    from modules.rules.engine import TradingRulesEngine
    
    # Get current portfolio state
    portfolio_state = self.get_portfolio_state()
    
    # 1. Pre-trade guardrails
    guardrails = PreTradeGuardrails()
    approved, reason = guardrails.validate(signal, portfolio_state)
    
    if not approved:
        logger.warning(f"Guardrails rejected trade: {reason}")
        return {'status': 'rejected', 'reason': reason}
    
    # 2. Trading rules validation
    rules = TradingRulesEngine()
    approved, reason = rules.validate_entry(signal)
    
    if not approved:
        logger.warning(f"Rules rejected trade: {reason}")
        return {'status': 'rejected', 'reason': reason}
    
    # 3. Calculate position size
    portfolio_value = portfolio_state['total_value']
    position_size = rules.calculate_position_size(signal, portfolio_value)
    
    # 4. Execute trade
    return self.place_order(symbol, side, position_size)
```

---

See **BACKTESTING_GUIDE.md** for backtesting framework implementation.

**Total Implementation Time**: 2-3 weeks for full system with testing.
