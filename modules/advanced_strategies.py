#!/usr/bin/env python3
"""
TPS19 Advanced Trading Strategies
Implements: Fox Mode, Gorilla Mode, Scholar Mode, Guardian Mode, Conqueror Mode
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedStrategies:
    """
    Collection of advanced trading strategies and modes
    """
    
    def __init__(self, trading_engine, market_data, risk_manager, ai_council):
        """
        Initialize Advanced Strategies
        
        Args:
            trading_engine: Trading engine instance
            market_data: Market data handler instance
            risk_manager: Risk manager instance
            ai_council: AI council instance
        """
        self.trading_engine = trading_engine
        self.market_data = market_data
        self.risk_manager = risk_manager
        self.ai_council = ai_council
        
        self.active_mode = "balanced"
        self.strategy_stats = {}
        
        logger.info("Advanced Strategies initialized")
        
    def fox_mode(self, market_data: Dict, portfolio_value: float) -> Dict:
        """
        Fox Mode - Stealth trading for flash crashes and flash pumps
        
        Strategy:
        - Wait for extreme price movements (flash crashes/pumps)
        - Execute quickly with tight stops
        - Scale out quickly on recovery
        
        Args:
            market_data: Current market data
            portfolio_value: Current portfolio value
            
        Returns:
            Trade signal or None
        """
        price = market_data.get('price', 0)
        change_24h = market_data.get('change_24h', 0)
        volume_24h = market_data.get('volume_24h', 0)
        
        # Flash crash detection (sudden drop > 5% with high volume)
        if change_24h < -5 and volume_24h > 1500000000:
            # Buy the dip
            position_size = self.risk_manager.calculate_position_size(
                portfolio_value, 
                risk_per_trade=0.03,  # 3% risk for flash opportunities
                stop_loss_pct=0.01,   # Tight 1% stop
                method="dynamic"
            )
            
            return {
                "mode": "fox_mode",
                "action": "buy",
                "reason": "flash_crash_detected",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "position_size": position_size,
                "stop_loss_pct": 1.0,
                "take_profit_pct": 3.0,  # Quick 3% profit target
                "urgency": "high",
                "confidence": 0.80
            }
            
        # Flash pump detection (sudden rise > 5%)
        elif change_24h > 5 and volume_24h > 1500000000:
            # Ride the momentum with quick exit
            position_size = self.risk_manager.calculate_position_size(
                portfolio_value,
                risk_per_trade=0.02,
                stop_loss_pct=0.015,
                method="volatility"
            )
            
            return {
                "mode": "fox_mode",
                "action": "buy",
                "reason": "flash_pump_momentum",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "position_size": position_size,
                "stop_loss_pct": 1.5,
                "take_profit_pct": 4.0,
                "urgency": "high",
                "confidence": 0.75
            }
            
        return None
        
    def gorilla_mode(self, market_data: Dict, portfolio_value: float) -> Dict:
        """
        Gorilla Mode - High confidence, large position aggressive trading
        
        Strategy:
        - Only trade when AI confidence > 85%
        - Use larger position sizes
        - Hold for bigger gains
        - Strong conviction trades only
        
        Args:
            market_data: Current market data
            portfolio_value: Current portfolio value
            
        Returns:
            Trade signal or None
        """
        # Get AI decision
        portfolio_data = {
            "balance": portfolio_value,
            "exposure": 0.3,  # Would get from trading engine
            "positions": len(self.trading_engine.active_positions)
        }
        
        ai_decision = self.ai_council.make_trading_decision(market_data, portfolio_data)
        
        # Only proceed if high confidence
        if ai_decision['confidence'] < 0.85:
            return None
            
        if ai_decision['decision'] in ['strong_buy', 'buy']:
            # Aggressive position sizing
            position_size = self.risk_manager.calculate_position_size(
                portfolio_value,
                risk_per_trade=0.05,  # 5% risk
                stop_loss_pct=0.03,
                method="kelly"
            )
            
            return {
                "mode": "gorilla_mode",
                "action": "buy",
                "reason": "high_confidence_signal",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "position_size": position_size,
                "stop_loss_pct": 3.0,
                "take_profit_pct": 10.0,  # Aim for 10% gain
                "urgency": "medium",
                "confidence": ai_decision['confidence'],
                "ai_reasoning": ai_decision['reasoning']
            }
            
        elif ai_decision['decision'] in ['strong_sell', 'sell']:
            return {
                "mode": "gorilla_mode",
                "action": "close_all",
                "reason": "high_confidence_exit",
                "confidence": ai_decision['confidence']
            }
            
        return None
        
    def scholar_mode(self, market_data: Dict, portfolio_value: float) -> Dict:
        """
        Scholar Mode - Learning and training mode with small positions
        
        Strategy:
        - Use minimal position sizes
        - Test multiple strategies
        - Collect data for AI training
        - Focus on learning rather than profit
        
        Args:
            market_data: Current market data
            portfolio_value: Current portfolio value
            
        Returns:
            Trade signal for learning
        """
        # Small position for learning
        position_size = min(portfolio_value * 0.01, 50)  # Max $50 per trade
        
        # Rotate through different entry signals
        change_24h = market_data.get('change_24h', 0)
        
        if abs(change_24h) > 1:  # Any 1% movement is a learning opportunity
            action = "buy" if change_24h > 0 else "sell"
            
            return {
                "mode": "scholar_mode",
                "action": action,
                "reason": "learning_opportunity",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "position_size": position_size,
                "stop_loss_pct": 2.0,
                "take_profit_pct": 4.0,
                "urgency": "low",
                "confidence": 0.50,
                "learning": True
            }
            
        return None
        
    def guardian_mode(self, market_data: Dict, portfolio_value: float) -> Dict:
        """
        Guardian Mode - Defensive trading for bear markets
        
        Strategy:
        - Capital preservation is priority
        - Very tight stop losses
        - Only high probability trades
        - Reduce exposure significantly
        
        Args:
            market_data: Current market data
            portfolio_value: Current portfolio value
            
        Returns:
            Defensive trade signal or risk reduction
        """
        change_24h = market_data.get('change_24h', 0)
        
        # Check if in bear market
        if change_24h < -3:
            # Close positions or tighten stops
            return {
                "mode": "guardian_mode",
                "action": "reduce_exposure",
                "reason": "bear_market_protection",
                "target_exposure": 0.2,  # Reduce to 20% exposure
                "urgency": "high",
                "confidence": 0.90
            }
            
        # Only take very safe trades
        if change_24h > 2 and market_data.get('volume_24h', 0) > 2000000000:
            position_size = portfolio_value * 0.02  # Only 2% risk
            
            return {
                "mode": "guardian_mode",
                "action": "buy",
                "reason": "safe_entry_opportunity",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "position_size": position_size,
                "stop_loss_pct": 1.0,  # Very tight stop
                "take_profit_pct": 3.0,
                "urgency": "medium",
                "confidence": 0.75
            }
            
        return None
        
    def conqueror_mode(self, market_data: Dict, portfolio_value: float) -> Dict:
        """
        Conqueror Mode - High-frequency scalping
        
        Strategy:
        - Multiple small trades
        - Quick entries and exits
        - Target 0.5-1% gains
        - High win rate focus
        
        Args:
            market_data: Current market data
            portfolio_value: Current portfolio value
            
        Returns:
            Scalping signal
        """
        # Check for small movements
        ticker = self.market_data.get_ticker(market_data.get('symbol', 'BTC/USDT'))
        
        spread = ticker.get('spread', 0)
        
        # Only scalp when spreads are tight
        if spread < ticker.get('last', 50000) * 0.001:  # Spread < 0.1%
            # Quick scalp trade
            position_size = portfolio_value * 0.03
            
            return {
                "mode": "conqueror_mode",
                "action": "scalp",
                "reason": "tight_spread_opportunity",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "position_size": position_size,
                "stop_loss_pct": 0.3,   # Very tight
                "take_profit_pct": 0.8,  # Quick small gain
                "urgency": "immediate",
                "confidence": 0.70,
                "hold_time": "1-5min"
            }
            
        return None
        
    def momentum_rider_mode(self, market_data: Dict, portfolio_value: float) -> Dict:
        """
        Momentum Rider Mode - Trend following strategy
        
        Strategy:
        - Identify strong trends
        - Enter on pullbacks
        - Ride the trend with trailing stops
        
        Args:
            market_data: Current market data
            portfolio_value: Current portfolio value
            
        Returns:
            Trend following signal
        """
        change_24h = market_data.get('change_24h', 0)
        
        # Strong uptrend
        if change_24h > 3:
            position_size = self.risk_manager.calculate_position_size(
                portfolio_value,
                risk_per_trade=0.03,
                stop_loss_pct=0.02,
                method="fixed"
            )
            
            return {
                "mode": "momentum_rider",
                "action": "buy",
                "reason": "strong_uptrend",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "position_size": position_size,
                "stop_loss_pct": 2.0,
                "take_profit_pct": 8.0,
                "trailing_stop": True,
                "trailing_stop_pct": 2.0,
                "urgency": "medium",
                "confidence": 0.75
            }
            
        return None
        
    def whale_monitor_mode(self, market_data: Dict, portfolio_value: float) -> Dict:
        """
        Whale Monitor Mode - Detect and follow large orders
        
        Strategy:
        - Monitor order book for large orders
        - Follow whale movements
        - Alert on unusual activity
        
        Args:
            market_data: Current market data
            portfolio_value: Current portfolio value
            
        Returns:
            Whale following signal
        """
        # Get order book
        order_book = self.market_data.get_order_book(
            market_data.get('symbol', 'BTC/USDT'), 
            depth=20
        )
        
        # Analyze for whale activity (simplified)
        large_bids = sum(1 for bid in order_book['bids'] if bid[1] > 10)  # > 10 BTC
        large_asks = sum(1 for ask in order_book['asks'] if ask[1] > 10)
        
        if large_bids > large_asks * 1.5:
            # Whale accumulation detected
            position_size = portfolio_value * 0.04
            
            return {
                "mode": "whale_monitor",
                "action": "buy",
                "reason": "whale_accumulation",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "position_size": position_size,
                "stop_loss_pct": 2.0,
                "take_profit_pct": 6.0,
                "urgency": "medium",
                "confidence": 0.70,
                "whale_signal": True
            }
            
        return None
        
    def grid_trading_mode(self, market_data: Dict, portfolio_value: float,
                         grid_levels: int = 5, grid_range: float = 0.05) -> List[Dict]:
        """
        Grid Trading Mode - Place multiple orders at different price levels
        
        Strategy:
        - Create buy orders below current price
        - Create sell orders above current price
        - Profit from range-bound markets
        
        Args:
            market_data: Current market data
            portfolio_value: Current portfolio value
            grid_levels: Number of grid levels
            grid_range: Range for grid (e.g., 0.05 = 5%)
            
        Returns:
            List of grid orders
        """
        price = market_data.get('price', 50000)
        total_capital = portfolio_value * 0.20  # Use 20% for grid
        per_level = total_capital / grid_levels
        
        orders = []
        
        # Create buy grid
        for i in range(1, grid_levels + 1):
            level_pct = (grid_range / grid_levels) * i
            buy_price = price * (1 - level_pct)
            
            orders.append({
                "mode": "grid_trading",
                "action": "buy_limit",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "price": buy_price,
                "size": per_level / buy_price,
                "type": "grid_buy",
                "level": i
            })
            
        # Create sell grid
        for i in range(1, grid_levels + 1):
            level_pct = (grid_range / grid_levels) * i
            sell_price = price * (1 + level_pct)
            
            orders.append({
                "mode": "grid_trading",
                "action": "sell_limit",
                "pair": market_data.get('symbol', 'BTC/USDT'),
                "price": sell_price,
                "size": per_level / sell_price,
                "type": "grid_sell",
                "level": i
            })
            
        return orders
        
    def dca_mode(self, symbol: str, portfolio_value: float, 
                interval_hours: int = 24, amount_per_buy: float = 100) -> Dict:
        """
        DCA Mode - Dollar Cost Averaging strategy
        
        Strategy:
        - Buy fixed amount at regular intervals
        - Ignore price movements
        - Long-term accumulation
        
        Args:
            symbol: Trading pair
            portfolio_value: Current portfolio value
            interval_hours: Hours between buys
            amount_per_buy: Fixed amount per purchase
            
        Returns:
            DCA buy signal
        """
        return {
            "mode": "dca",
            "action": "buy",
            "reason": "scheduled_dca_purchase",
            "pair": symbol,
            "position_size": amount_per_buy,
            "order_type": "market",
            "urgency": "low",
            "confidence": 1.0,
            "scheduled": True
        }
        
    def execute_strategy(self, mode: str, market_data: Dict, 
                        portfolio_value: float) -> Optional[Dict]:
        """
        Execute the specified strategy mode
        
        Args:
            mode: Strategy mode name
            market_data: Current market data
            portfolio_value: Current portfolio value
            
        Returns:
            Trade signal from selected mode
        """
        mode_map = {
            "fox": self.fox_mode,
            "gorilla": self.gorilla_mode,
            "scholar": self.scholar_mode,
            "guardian": self.guardian_mode,
            "conqueror": self.conqueror_mode,
            "momentum": self.momentum_rider_mode,
            "whale": self.whale_monitor_mode,
        }
        
        if mode in mode_map:
            self.active_mode = mode
            logger.info(f"Executing {mode} mode strategy")
            return mode_map[mode](market_data, portfolio_value)
        else:
            logger.warning(f"Unknown strategy mode: {mode}")
            return None
            
    def get_best_strategy(self, market_data: Dict, portfolio_value: float) -> Dict:
        """
        Automatically select the best strategy based on market conditions
        
        Args:
            market_data: Current market data
            portfolio_value: Current portfolio value
            
        Returns:
            Best strategy signal
        """
        change_24h = market_data.get('change_24h', 0)
        volume_24h = market_data.get('volume_24h', 0)
        
        # Extreme movements -> Fox Mode
        if abs(change_24h) > 5 and volume_24h > 1500000000:
            return self.fox_mode(market_data, portfolio_value)
            
        # Strong trends -> Momentum Rider
        elif abs(change_24h) > 3:
            return self.momentum_rider_mode(market_data, portfolio_value)
            
        # Bear market -> Guardian Mode
        elif change_24h < -2:
            return self.guardian_mode(market_data, portfolio_value)
            
        # Normal conditions -> Check AI confidence for Gorilla
        else:
            portfolio_data = {
                "balance": portfolio_value,
                "exposure": 0.3,
                "positions": len(self.trading_engine.active_positions)
            }
            ai_decision = self.ai_council.make_trading_decision(market_data, portfolio_data)
            
            if ai_decision['confidence'] > 0.85:
                return self.gorilla_mode(market_data, portfolio_value)
            else:
                return self.conqueror_mode(market_data, portfolio_value)
                
    def get_strategy_performance(self) -> Dict:
        """Get performance statistics for each strategy mode"""
        return self.strategy_stats


if __name__ == "__main__":
    print("✅ Advanced Strategies module loaded")
    print("\nAvailable Strategy Modes:")
    print("  - Fox Mode: Stealth flash crash/pump trading")
    print("  - Gorilla Mode: High-confidence aggressive trades")
    print("  - Scholar Mode: Learning mode with small positions")
    print("  - Guardian Mode: Defensive bear market protection")
    print("  - Conqueror Mode: High-frequency scalping")
    print("  - Momentum Rider: Trend following")
    print("  - Whale Monitor: Follow large orders")
    print("  - Grid Trading: Range-bound profit taking")
    print("  - DCA Mode: Dollar cost averaging")
