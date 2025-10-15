"""
Enhanced Market Simulator
Provides realistic market data simulation with various market conditions
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
import random
from dataclasses import dataclass

from core.logging_config import get_logger


logger = get_logger(__name__)


class MarketCondition(Enum):
    """Market condition types"""
    BULL_RUN = "bull_run"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    FLASH_CRASH = "flash_crash"
    RECOVERY = "recovery"


class EventType(Enum):
    """Market event types"""
    NEWS_POSITIVE = "news_positive"
    NEWS_NEGATIVE = "news_negative"
    WHALE_BUY = "whale_buy"
    WHALE_SELL = "whale_sell"
    EXCHANGE_HACK = "exchange_hack"
    REGULATION_FUD = "regulation_fud"
    ADOPTION_NEWS = "adoption_news"
    TECHNICAL_BREAKOUT = "technical_breakout"
    TECHNICAL_BREAKDOWN = "technical_breakdown"


@dataclass
class MarketEvent:
    """Market event that affects price"""
    timestamp: datetime
    event_type: EventType
    impact: float  # -1.0 to 1.0
    duration_minutes: int
    description: str


class MarketSimulator:
    """
    Realistic market data simulator with multiple features:
    - Various market conditions (bull, bear, sideways)
    - Realistic price movements with volatility
    - Order book simulation
    - Market events and news impact
    - Multiple timeframes
    - Correlation between assets
    """
    
    def __init__(self, base_prices: Dict[str, float] = None):
        """
        Initialize market simulator
        
        Args:
            base_prices: Starting prices for assets
        """
        self.base_prices = base_prices or {
            "BTC_USDT": 45000.0,
            "ETH_USDT": 3000.0,
            "BNB_USDT": 400.0,
            "SOL_USDT": 100.0,
            "ADA_USDT": 0.50,
            "DOT_USDT": 20.0,
            "MATIC_USDT": 1.50,
            "LINK_USDT": 15.0,
            "UNI_USDT": 10.0,
            "AVAX_USDT": 35.0
        }
        
        self.current_prices = self.base_prices.copy()
        self.price_history = {symbol: [] for symbol in self.base_prices}
        self.market_condition = MarketCondition.SIDEWAYS
        self.volatility = 0.02  # 2% base volatility
        self.trend_strength = 0.0  # -1 to 1
        self.events = []
        self.last_update = datetime.now()
        
        # Market microstructure parameters
        self.spread_basis_points = 10  # 0.1% spread
        self.market_depth = 100  # Orders on each side
        
        # Correlation matrix (simplified)
        self.correlations = {
            "BTC_USDT": {"ETH_USDT": 0.8, "BNB_USDT": 0.7, "SOL_USDT": 0.6},
            "ETH_USDT": {"BTC_USDT": 0.8, "UNI_USDT": 0.7, "LINK_USDT": 0.6},
            # Add more correlations as needed
        }
        
        # Technical indicators state
        self.sma_20 = {symbol: price for symbol, price in self.base_prices.items()}
        self.sma_50 = {symbol: price for symbol, price in self.base_prices.items()}
        self.rsi = {symbol: 50.0 for symbol in self.base_prices}  # Neutral RSI
        
        logger.info("Market simulator initialized", extra={"symbols": list(self.base_prices.keys())})
    
    def set_market_condition(self, condition: MarketCondition, duration_hours: int = 24):
        """
        Set the current market condition
        
        Args:
            condition: Market condition to simulate
            duration_hours: How long this condition should last
        """
        self.market_condition = condition
        
        # Adjust parameters based on condition
        if condition == MarketCondition.BULL_RUN:
            self.trend_strength = random.uniform(0.3, 0.7)
            self.volatility = random.uniform(0.02, 0.04)
        elif condition == MarketCondition.BEAR_MARKET:
            self.trend_strength = random.uniform(-0.7, -0.3)
            self.volatility = random.uniform(0.03, 0.05)
        elif condition == MarketCondition.HIGH_VOLATILITY:
            self.trend_strength = 0.0
            self.volatility = random.uniform(0.05, 0.10)
        elif condition == MarketCondition.LOW_VOLATILITY:
            self.trend_strength = 0.0
            self.volatility = random.uniform(0.005, 0.01)
        elif condition == MarketCondition.FLASH_CRASH:
            self.trend_strength = -0.9
            self.volatility = 0.15
        else:  # SIDEWAYS
            self.trend_strength = 0.0
            self.volatility = random.uniform(0.01, 0.02)
        
        logger.info(f"Market condition set to {condition.value}", extra={
            "trend_strength": self.trend_strength,
            "volatility": self.volatility,
            "duration_hours": duration_hours
        })
    
    def add_market_event(self, event: MarketEvent):
        """Add a market event that will impact prices"""
        self.events.append(event)
        logger.info(f"Market event added: {event.description}")
    
    def generate_random_events(self, num_events: int = 5, time_range_hours: int = 24):
        """Generate random market events"""
        for _ in range(num_events):
            event_type = random.choice(list(EventType))
            
            # Set impact based on event type
            impact_ranges = {
                EventType.NEWS_POSITIVE: (0.02, 0.05),
                EventType.NEWS_NEGATIVE: (-0.05, -0.02),
                EventType.WHALE_BUY: (0.01, 0.03),
                EventType.WHALE_SELL: (-0.03, -0.01),
                EventType.EXCHANGE_HACK: (-0.10, -0.05),
                EventType.REGULATION_FUD: (-0.08, -0.03),
                EventType.ADOPTION_NEWS: (0.03, 0.08),
                EventType.TECHNICAL_BREAKOUT: (0.02, 0.04),
                EventType.TECHNICAL_BREAKDOWN: (-0.04, -0.02)
            }
            
            impact = random.uniform(*impact_ranges.get(event_type, (-0.02, 0.02)))
            
            event = MarketEvent(
                timestamp=datetime.now() + timedelta(hours=random.uniform(0, time_range_hours)),
                event_type=event_type,
                impact=impact,
                duration_minutes=random.randint(30, 240),
                description=f"{event_type.value} event"
            )
            
            self.add_market_event(event)
    
    def _apply_price_movement(self, symbol: str, base_return: float) -> float:
        """
        Apply realistic price movement with various factors
        
        Args:
            symbol: Asset symbol
            base_return: Base return before adjustments
            
        Returns:
            New price after movement
        """
        current_price = self.current_prices[symbol]
        
        # 1. Add trend component
        trend_return = self.trend_strength * 0.001  # 0.1% max trend per update
        
        # 2. Add random walk component
        random_return = np.random.normal(0, self.volatility / np.sqrt(24 * 60))  # Adjust for minute updates
        
        # 3. Add correlation effects (simplified)
        correlation_return = 0.0
        if symbol in self.correlations:
            for corr_symbol, correlation in self.correlations[symbol].items():
                if corr_symbol in self.current_prices:
                    corr_price_change = (self.current_prices[corr_symbol] - self.base_prices[corr_symbol]) / self.base_prices[corr_symbol]
                    correlation_return += correlation * corr_price_change * 0.0001
        
        # 4. Apply event impacts
        event_return = 0.0
        current_time = datetime.now()
        for event in self.events:
            if event.timestamp <= current_time <= event.timestamp + timedelta(minutes=event.duration_minutes):
                # Events affect BTC most, others proportionally
                if symbol == "BTC_USDT":
                    event_return += event.impact
                else:
                    event_return += event.impact * 0.5
        
        # 5. Add mean reversion component
        price_deviation = (current_price - self.base_prices[symbol]) / self.base_prices[symbol]
        mean_reversion = -price_deviation * 0.0001  # Weak mean reversion
        
        # 6. Technical indicator influence
        # Simulate support/resistance at round numbers
        round_number_distance = current_price % 1000
        if round_number_distance < 50:  # Near support
            technical_influence = 0.0001
        elif round_number_distance > 950:  # Near resistance
            technical_influence = -0.0001
        else:
            technical_influence = 0.0
        
        # Combine all factors
        total_return = (
            base_return + 
            trend_return + 
            random_return + 
            correlation_return + 
            event_return + 
            mean_reversion + 
            technical_influence
        )
        
        # Apply limits to prevent unrealistic moves
        total_return = np.clip(total_return, -0.10, 0.10)  # Max 10% move per update
        
        # Calculate new price
        new_price = current_price * (1 + total_return)
        
        # Ensure price doesn't go negative
        new_price = max(new_price, current_price * 0.5)  # Max 50% drop in one update
        
        return new_price
    
    def update_prices(self) -> Dict[str, float]:
        """
        Update all asset prices based on market conditions
        
        Returns:
            Dictionary of updated prices
        """
        for symbol in self.current_prices:
            # Base return can be influenced by asset-specific factors
            base_return = 0.0
            
            # Apply price movement
            new_price = self._apply_price_movement(symbol, base_return)
            
            # Round price based on asset value
            if new_price > 1000:
                new_price = round(new_price, 2)
            elif new_price > 10:
                new_price = round(new_price, 4)
            else:
                new_price = round(new_price, 6)
            
            # Update price
            self.current_prices[symbol] = new_price
            
            # Update technical indicators
            self._update_technical_indicators(symbol, new_price)
            
            # Store in history
            self.price_history[symbol].append({
                "timestamp": datetime.now(),
                "price": new_price,
                "volume": self._generate_volume(symbol),
                "market_condition": self.market_condition.value
            })
        
        self.last_update = datetime.now()
        return self.current_prices.copy()
    
    def _update_technical_indicators(self, symbol: str, new_price: float):
        """Update technical indicators for the symbol"""
        # Simple moving averages (exponential smoothing)
        alpha_20 = 2 / (20 + 1)
        alpha_50 = 2 / (50 + 1)
        
        self.sma_20[symbol] = alpha_20 * new_price + (1 - alpha_20) * self.sma_20[symbol]
        self.sma_50[symbol] = alpha_50 * new_price + (1 - alpha_50) * self.sma_50[symbol]
        
        # RSI calculation (simplified)
        price_change = new_price - self.current_prices[symbol]
        if price_change > 0:
            self.rsi[symbol] = min(100, self.rsi[symbol] + price_change / new_price * 100)
        else:
            self.rsi[symbol] = max(0, self.rsi[symbol] + price_change / new_price * 100)
    
    def _generate_volume(self, symbol: str) -> float:
        """Generate realistic volume based on market conditions"""
        base_volumes = {
            "BTC_USDT": 50000,
            "ETH_USDT": 30000,
            "BNB_USDT": 10000,
            "SOL_USDT": 8000,
            "ADA_USDT": 5000,
            "DOT_USDT": 3000,
            "MATIC_USDT": 4000,
            "LINK_USDT": 2000,
            "UNI_USDT": 2500,
            "AVAX_USDT": 3500
        }
        
        base_volume = base_volumes.get(symbol, 1000)
        
        # Volume increases with volatility
        volume_multiplier = 1 + self.volatility * 10
        
        # Add randomness
        random_factor = random.uniform(0.5, 1.5)
        
        # Events increase volume
        event_multiplier = 1.0
        current_time = datetime.now()
        for event in self.events:
            if event.timestamp <= current_time <= event.timestamp + timedelta(minutes=event.duration_minutes):
                event_multiplier = 2.0
                break
        
        return base_volume * volume_multiplier * random_factor * event_multiplier
    
    def get_order_book(self, symbol: str, depth: int = 20) -> Dict[str, List[Tuple[float, float]]]:
        """
        Generate realistic order book
        
        Args:
            symbol: Asset symbol
            depth: Number of levels on each side
            
        Returns:
            Dictionary with 'bids' and 'asks' lists
        """
        current_price = self.current_prices[symbol]
        spread = current_price * self.spread_basis_points / 10000
        
        # Generate bids
        bids = []
        bid_price = current_price - spread / 2
        for i in range(depth):
            # Price decreases as we go down the book
            price = bid_price * (1 - 0.0001 * i)
            # Size increases with distance from mid (more liquidity deeper)
            size = random.uniform(0.1, 1.0) * (1 + i * 0.1)
            bids.append((round(price, 8), round(size, 8)))
        
        # Generate asks
        asks = []
        ask_price = current_price + spread / 2
        for i in range(depth):
            # Price increases as we go up the book
            price = ask_price * (1 + 0.0001 * i)
            # Size increases with distance from mid
            size = random.uniform(0.1, 1.0) * (1 + i * 0.1)
            asks.append((round(price, 8), round(size, 8)))
        
        return {
            "bids": bids,
            "asks": asks,
            "spread": round(spread, 8),
            "mid_price": round(current_price, 8)
        }
    
    def get_candles(
        self, 
        symbol: str, 
        timeframe: str = "1m", 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Generate candlestick data
        
        Args:
            symbol: Asset symbol
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, etc.)
            limit: Number of candles to return
            
        Returns:
            List of OHLCV candles
        """
        if symbol not in self.price_history or not self.price_history[symbol]:
            return []
        
        # For simulation, we'll generate based on current data
        candles = []
        current_price = self.current_prices[symbol]
        
        for i in range(limit):
            # Generate OHLCV data
            open_price = current_price * (1 + random.uniform(-self.volatility, self.volatility))
            high_price = open_price * (1 + random.uniform(0, self.volatility))
            low_price = open_price * (1 - random.uniform(0, self.volatility))
            close_price = random.uniform(low_price, high_price)
            volume = self._generate_volume(symbol)
            
            candle = {
                "timestamp": datetime.now() - timedelta(minutes=i),
                "open": round(open_price, 8),
                "high": round(high_price, 8),
                "low": round(low_price, 8),
                "close": round(close_price, 8),
                "volume": round(volume, 2)
            }
            
            candles.append(candle)
            
            # Update current price for next candle
            current_price = close_price
        
        return list(reversed(candles))  # Return in chronological order
    
    def get_market_stats(self, symbol: str) -> Dict[str, Any]:
        """Get market statistics for a symbol"""
        current_price = self.current_prices[symbol]
        base_price = self.base_prices[symbol]
        
        # Calculate 24h change (simulated)
        change_24h = ((current_price - base_price) / base_price) * 100
        
        # Get recent history
        recent_prices = [h["price"] for h in self.price_history.get(symbol, [])[-100:]]
        if not recent_prices:
            recent_prices = [current_price]
        
        return {
            "symbol": symbol,
            "price": current_price,
            "change_24h": round(change_24h, 2),
            "high_24h": round(max(recent_prices + [current_price]) * 1.02, 8),
            "low_24h": round(min(recent_prices + [current_price]) * 0.98, 8),
            "volume_24h": sum(h.get("volume", 0) for h in self.price_history.get(symbol, [])[-1440:]),
            "market_condition": self.market_condition.value,
            "volatility": round(self.volatility * 100, 2),
            "rsi": round(self.rsi.get(symbol, 50), 2),
            "sma_20": round(self.sma_20.get(symbol, current_price), 8),
            "sma_50": round(self.sma_50.get(symbol, current_price), 8)
        }
    
    def simulate_market_cycle(self, duration_hours: int = 24):
        """
        Simulate a complete market cycle with various conditions
        
        Args:
            duration_hours: Duration of the simulation
        """
        logger.info(f"Starting market cycle simulation for {duration_hours} hours")
        
        # Define a market cycle
        cycle_phases = [
            (MarketCondition.LOW_VOLATILITY, 0.1),
            (MarketCondition.BULL_RUN, 0.2),
            (MarketCondition.HIGH_VOLATILITY, 0.1),
            (MarketCondition.SIDEWAYS, 0.2),
            (MarketCondition.BEAR_MARKET, 0.2),
            (MarketCondition.RECOVERY, 0.2)
        ]
        
        # Generate random events throughout the cycle
        self.generate_random_events(
            num_events=int(duration_hours / 4),
            time_range_hours=duration_hours
        )
        
        # Simulate the cycle
        for condition, phase_duration_ratio in cycle_phases:
            phase_duration = int(duration_hours * phase_duration_ratio * 60)  # Convert to minutes
            self.set_market_condition(condition)
            
            for minute in range(phase_duration):
                self.update_prices()
                
                # Log progress every hour
                if minute % 60 == 0:
                    btc_stats = self.get_market_stats("BTC_USDT")
                    logger.info(f"Simulation progress - {condition.value}", extra=btc_stats)


# Example usage
if __name__ == "__main__":
    # Create simulator
    simulator = MarketSimulator()
    
    # Set market condition
    simulator.set_market_condition(MarketCondition.HIGH_VOLATILITY)
    
    # Generate some random events
    simulator.generate_random_events(num_events=3)
    
    # Run simulation for a few updates
    for i in range(10):
        prices = simulator.update_prices()
        print(f"\nUpdate {i+1}:")
        print(f"BTC: ${prices['BTC_USDT']:,.2f}")
        print(f"ETH: ${prices['ETH_USDT']:,.2f}")
        
        # Get order book
        order_book = simulator.get_order_book("BTC_USDT", depth=5)
        print(f"Spread: ${order_book['spread']:.2f}")
        
        # Get market stats
        stats = simulator.get_market_stats("BTC_USDT")
        print(f"24h Change: {stats['change_24h']:.2f}%")
        print(f"RSI: {stats['rsi']:.2f}")