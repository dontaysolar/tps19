"""
Enhanced Trading Engine with Simulation Support
Supports both live trading and realistic simulation
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum

from core.logging_config import get_logger
from database.connection import db_manager
from database.models import Order, Trade, TradingSignal, Portfolio, OrderStatus, OrderType, OrderSide
from exchanges.crypto_com_client import CryptoComClient
from simulation.market_simulator import MarketSimulator
from simulation.backtesting_engine import BacktestingEngine


logger = get_logger(__name__)


class TradingMode(Enum):
    """Trading mode enumeration"""
    LIVE = "live"
    PAPER = "paper"
    SIMULATION = "simulation"
    BACKTEST = "backtest"


class EnhancedTradingEngine:
    """
    Enhanced trading engine with multiple modes:
    - Live trading with real exchange
    - Paper trading with real data but no execution
    - Simulation with realistic fake data
    - Backtesting with historical patterns
    """
    
    def __init__(
        self,
        mode: TradingMode = TradingMode.SIMULATION,
        exchange_client: Optional[CryptoComClient] = None,
        market_simulator: Optional[MarketSimulator] = None
    ):
        self.mode = mode
        self.exchange_client = exchange_client
        self.market_simulator = market_simulator or MarketSimulator()
        self.backtesting_engine = None
        
        # Trading state
        self.active_orders: Dict[str, Order] = {}
        self.positions: Dict[str, Any] = {}
        self.is_running = False
        
        # Risk parameters
        self.max_position_size = 0.1  # 10% of capital
        self.max_open_orders = 10
        self.min_order_size = 10.0  # $10 minimum
        
        # Performance tracking
        self.trade_count = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        
        logger.info(f"Trading engine initialized in {mode.value} mode")
    
    async def start(self):
        """Start the trading engine"""
        logger.info(f"Starting trading engine in {self.mode.value} mode")
        self.is_running = True
        
        if self.mode == TradingMode.SIMULATION:
            # Start market simulation
            self.market_simulator.set_market_condition(
                self.market_simulator.market_condition
            )
            self.market_simulator.generate_random_events(num_events=10)
        
        # Main trading loop
        asyncio.create_task(self._trading_loop())
    
    async def stop(self):
        """Stop the trading engine"""
        logger.info("Stopping trading engine")
        self.is_running = False
        
        # Cancel all open orders
        await self._cancel_all_orders()
    
    async def _trading_loop(self):
        """Main trading loop"""
        while self.is_running:
            try:
                # Update market data
                await self._update_market_data()
                
                # Check open orders
                await self._check_open_orders()
                
                # Update positions
                await self._update_positions()
                
                # Log status
                if self.trade_count % 10 == 0:
                    await self._log_performance()
                
                # Sleep based on mode
                if self.mode == TradingMode.LIVE:
                    await asyncio.sleep(1)  # 1 second for live
                else:
                    await asyncio.sleep(0.1)  # 100ms for simulation
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(5)
    
    async def _update_market_data(self):
        """Update market data based on mode"""
        if self.mode == TradingMode.SIMULATION:
            # Update simulated prices
            self.market_simulator.update_prices()
        elif self.mode in [TradingMode.LIVE, TradingMode.PAPER]:
            # Fetch real market data
            if self.exchange_client:
                for symbol in self.get_traded_symbols():
                    try:
                        ticker = self.exchange_client.get_ticker(symbol)
                        # Process ticker data
                    except Exception as e:
                        logger.error(f"Failed to get ticker for {symbol}: {e}")
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        if self.mode == TradingMode.SIMULATION:
            return self.market_simulator.current_prices.get(symbol, 0.0)
        elif self.exchange_client:
            try:
                ticker = self.exchange_client.get_ticker(symbol)
                return float(ticker.get("last", 0))
            except:
                return 0.0
        return 0.0
    
    def get_order_book(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Get order book for a symbol"""
        if self.mode == TradingMode.SIMULATION:
            return self.market_simulator.get_order_book(symbol, depth)
        elif self.exchange_client:
            try:
                return self.exchange_client.get_orderbook(symbol, depth)
            except:
                return {"bids": [], "asks": []}
        return {"bids": [], "asks": []}
    
    def get_market_stats(self, symbol: str) -> Dict[str, Any]:
        """Get market statistics"""
        if self.mode == TradingMode.SIMULATION:
            return self.market_simulator.get_market_stats(symbol)
        else:
            # Calculate from real data
            current_price = self.get_current_price(symbol)
            return {
                "symbol": symbol,
                "price": current_price,
                "change_24h": 0.0,  # Would need historical data
                "volume_24h": 0.0,
                "volatility": 0.0
            }
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        price: Optional[float] = None
    ) -> Optional[str]:
        """
        Place an order
        
        Args:
            symbol: Trading symbol
            side: "buy" or "sell"
            quantity: Order quantity
            order_type: "market" or "limit"
            price: Limit price (required for limit orders)
            
        Returns:
            Order ID if successful, None otherwise
        """
        # Validate order
        if not await self._validate_order(symbol, side, quantity, order_type, price):
            return None
        
        # Create order based on mode
        if self.mode == TradingMode.LIVE:
            return await self._place_live_order(symbol, side, quantity, order_type, price)
        elif self.mode == TradingMode.PAPER:
            return await self._place_paper_order(symbol, side, quantity, order_type, price)
        elif self.mode == TradingMode.SIMULATION:
            return await self._place_simulated_order(symbol, side, quantity, order_type, price)
        
        return None
    
    async def _validate_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        price: Optional[float]
    ) -> bool:
        """Validate order parameters"""
        # Check minimum size
        current_price = self.get_current_price(symbol)
        order_value = quantity * (price or current_price)
        
        if order_value < self.min_order_size:
            logger.warning(f"Order value {order_value} below minimum {self.min_order_size}")
            return False
        
        # Check maximum open orders
        if len(self.active_orders) >= self.max_open_orders:
            logger.warning(f"Maximum open orders ({self.max_open_orders}) reached")
            return False
        
        # Check if limit order has price
        if order_type == "limit" and not price:
            logger.error("Limit order requires price")
            return False
        
        return True
    
    async def _place_live_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        price: Optional[float]
    ) -> Optional[str]:
        """Place a live order on the exchange"""
        if not self.exchange_client:
            logger.error("No exchange client available for live trading")
            return None
        
        try:
            # Convert to exchange format
            exchange_side = side.upper()
            exchange_type = "LIMIT" if order_type == "limit" else "MARKET"
            
            # Place order
            response = self.exchange_client.create_order(
                symbol=symbol,
                side=exchange_side,
                order_type=exchange_type,
                quantity=Decimal(str(quantity)),
                price=Decimal(str(price)) if price else None
            )
            
            order_id = response.get("order_id")
            
            if order_id:
                # Store order in database
                with db_manager.get_session() as session:
                    order = Order(
                        order_id=order_id,
                        symbol=symbol,
                        side=OrderSide(side),
                        type=OrderType(order_type),
                        status=OrderStatus.OPEN,
                        quantity=Decimal(str(quantity)),
                        price=Decimal(str(price)) if price else None
                    )
                    session.add(order)
                    session.commit()
                
                self.active_orders[order_id] = order
                logger.info(f"Live order placed: {order_id}")
                return order_id
            
        except Exception as e:
            logger.error(f"Failed to place live order: {e}")
        
        return None
    
    async def _place_paper_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        price: Optional[float]
    ) -> Optional[str]:
        """Place a paper trading order"""
        # Generate order ID
        order_id = f"PAPER_{int(datetime.now().timestamp())}_{symbol}"
        
        # Get current price for market orders
        if order_type == "market":
            price = self.get_current_price(symbol)
        
        # Create order
        with db_manager.get_session() as session:
            order = Order(
                order_id=order_id,
                symbol=symbol,
                side=OrderSide(side),
                type=OrderType(order_type),
                status=OrderStatus.OPEN if order_type == "limit" else OrderStatus.FILLED,
                quantity=Decimal(str(quantity)),
                price=Decimal(str(price)) if price else None,
                filled_quantity=Decimal(str(quantity)) if order_type == "market" else Decimal("0"),
                average_price=Decimal(str(price)) if order_type == "market" else None,
                filled_at=datetime.now() if order_type == "market" else None
            )
            session.add(order)
            session.commit()
        
        self.active_orders[order_id] = order
        
        # Update trade statistics for market orders
        if order_type == "market":
            self.trade_count += 1
        
        logger.info(f"Paper order placed: {order_id}")
        return order_id
    
    async def _place_simulated_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        price: Optional[float]
    ) -> Optional[str]:
        """Place a simulated order"""
        # Similar to paper trading but with simulated fills
        order_id = f"SIM_{int(datetime.now().timestamp())}_{symbol}"
        
        # Get simulated price
        current_price = self.market_simulator.current_prices.get(symbol, 0)
        
        if current_price == 0:
            logger.error(f"No price available for {symbol}")
            return None
        
        # Apply slippage for market orders
        if order_type == "market":
            slippage = 0.001  # 0.1% slippage
            if side == "buy":
                price = current_price * (1 + slippage)
            else:
                price = current_price * (1 - slippage)
        
        # Simulate order execution
        fill_probability = 0.95 if order_type == "market" else 0.7
        is_filled = asyncio.get_event_loop().time() % 1 < fill_probability
        
        # Create order record
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=OrderSide(side),
            type=OrderType(order_type),
            status=OrderStatus.FILLED if is_filled and order_type == "market" else OrderStatus.OPEN,
            quantity=Decimal(str(quantity)),
            price=Decimal(str(price)) if price else None,
            filled_quantity=Decimal(str(quantity)) if is_filled and order_type == "market" else Decimal("0"),
            average_price=Decimal(str(price)) if is_filled and order_type == "market" else None,
            filled_at=datetime.now() if is_filled and order_type == "market" else None
        )
        
        # Save to database
        with db_manager.get_session() as session:
            session.add(order)
            session.commit()
        
        self.active_orders[order_id] = order
        
        # Update statistics
        if is_filled and order_type == "market":
            self.trade_count += 1
            
            # Simulate P&L (random for now)
            if side == "sell" and symbol in self.positions:
                pnl = (float(price) - self.positions[symbol]["entry_price"]) * quantity
                self.total_pnl += pnl
                if pnl > 0:
                    self.winning_trades += 1
        
        logger.info(f"Simulated order placed: {order_id} (filled: {is_filled})")
        return order_id
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        if order_id not in self.active_orders:
            logger.warning(f"Order {order_id} not found")
            return False
        
        order = self.active_orders[order_id]
        
        if self.mode == TradingMode.LIVE:
            # Cancel on exchange
            if self.exchange_client:
                try:
                    self.exchange_client.cancel_order(order_id, order.symbol)
                except Exception as e:
                    logger.error(f"Failed to cancel order {order_id}: {e}")
                    return False
        
        # Update order status
        with db_manager.get_session() as session:
            db_order = session.query(Order).filter_by(order_id=order_id).first()
            if db_order:
                db_order.status = OrderStatus.CANCELLED
                db_order.cancelled_at = datetime.now()
                session.commit()
        
        # Remove from active orders
        del self.active_orders[order_id]
        
        logger.info(f"Order cancelled: {order_id}")
        return True
    
    async def _cancel_all_orders(self):
        """Cancel all open orders"""
        order_ids = list(self.active_orders.keys())
        for order_id in order_ids:
            await self.cancel_order(order_id)
    
    async def _check_open_orders(self):
        """Check and update open orders"""
        for order_id, order in list(self.active_orders.items()):
            if order.status != OrderStatus.OPEN:
                continue
            
            # Check if order should be filled (for simulation/paper)
            if self.mode in [TradingMode.SIMULATION, TradingMode.PAPER]:
                current_price = self.get_current_price(order.symbol)
                
                should_fill = False
                if order.type == OrderType.LIMIT:
                    if order.side == OrderSide.BUY and current_price <= float(order.price):
                        should_fill = True
                    elif order.side == OrderSide.SELL and current_price >= float(order.price):
                        should_fill = True
                
                if should_fill:
                    # Fill the order
                    with db_manager.get_session() as session:
                        db_order = session.query(Order).filter_by(order_id=order_id).first()
                        if db_order:
                            db_order.status = OrderStatus.FILLED
                            db_order.filled_quantity = db_order.quantity
                            db_order.average_price = db_order.price
                            db_order.filled_at = datetime.now()
                            session.commit()
                    
                    order.status = OrderStatus.FILLED
                    self.trade_count += 1
                    
                    logger.info(f"Order filled: {order_id} @ {order.price}")
    
    async def _update_positions(self):
        """Update position tracking"""
        # This would track open positions and calculate unrealized P&L
        pass
    
    async def _log_performance(self):
        """Log trading performance"""
        win_rate = self.winning_trades / self.trade_count if self.trade_count > 0 else 0
        
        logger.info(
            "Trading performance",
            extra={
                "mode": self.mode.value,
                "trades": self.trade_count,
                "win_rate": f"{win_rate:.2%}",
                "total_pnl": f"${self.total_pnl:.2f}",
                "active_orders": len(self.active_orders),
                "positions": len(self.positions)
            }
        )
    
    def get_traded_symbols(self) -> List[str]:
        """Get list of symbols being traded"""
        # This would come from configuration
        return ["BTC_USDT", "ETH_USDT", "BNB_USDT"]
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        if self.mode == TradingMode.LIVE and self.exchange_client:
            try:
                return self.exchange_client.get_account_balance()
            except Exception as e:
                logger.error(f"Failed to get account balance: {e}")
                return {}
        else:
            # Return simulated balance
            return {
                "USDT": {"available": 10000.0, "total": 10000.0},
                "BTC": {"available": 0.0, "total": 0.0},
                "ETH": {"available": 0.0, "total": 0.0}
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check trading engine health"""
        return {
            "healthy": self.is_running,
            "mode": self.mode.value,
            "active_orders": len(self.active_orders),
            "positions": len(self.positions),
            "trade_count": self.trade_count
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get trading statistics"""
        win_rate = self.winning_trades / self.trade_count if self.trade_count > 0 else 0
        
        return {
            "mode": self.mode.value,
            "is_running": self.is_running,
            "total_trades": self.trade_count,
            "winning_trades": self.winning_trades,
            "win_rate": win_rate,
            "total_pnl": self.total_pnl,
            "active_orders": len(self.active_orders),
            "open_positions": len(self.positions)
        }