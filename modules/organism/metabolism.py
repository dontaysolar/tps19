#!/usr/bin/env python3
"""
Organism Metabolism - Capital Management & Energy Flow

Like biological metabolism converting food to energy,
this converts capital into profits and manages the flow of resources.

Handles:
- Position sizing (energy allocation)
- Profit taking (nutrient extraction)
- Reinvestment (growth)
- Withdrawals (waste removal)
- Capital efficiency (metabolic rate)
"""

from typing import Dict, Any, Optional
from datetime import datetime
from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class Metabolism:
    """
    Manages capital flow through the organism
    
    Functions:
    - Allocate capital to strategies (energy distribution)
    - Size positions (portion control)
    - Extract profits (harvest energy)
    - Reinvest (fuel growth)
    - Withdraw (eliminate waste)
    """
    
    def __init__(self):
        # Metabolic configuration
        self.metabolic_rate = 1.0  # How aggressively organism uses capital
        
        # Capital management parameters
        self.reinvestment_rate = config.get('metabolism.reinvestment_rate', 0.50)
        self.withdrawal_btc_pct = config.get('metabolism.withdrawal_btc', 0.30)
        self.withdrawal_usdt_pct = config.get('metabolism.withdrawal_usdt', 0.20)
        self.profit_threshold = config.get('metabolism.profit_threshold', 100)
        
        # Position sizing parameters
        self.base_position_size = config.get('metabolism.base_position', 0.05)
        self.max_position_size = config.get('metabolism.max_position', 0.10)
        self.min_position_size = config.get('metabolism.min_position', 0.02)
        
        # Efficiency tracking
        self.capital_utilization = 0.0
        self.metabolic_efficiency = 1.0
        
        logger.info("💰 Metabolism system initialized")
    
    def calculate_position_size(self, signal: Dict, portfolio: Dict) -> float:
        """
        Calculate optimal position size using Kelly Criterion + AI
        
        This is like the organism deciding how much energy to invest
        in a particular action
        
        Args:
            signal: Trade signal with strategy info
            portfolio: Current portfolio state
            
        Returns:
            Position size as % of portfolio
        """
        try:
            # Get strategy performance
            win_rate = signal.get('strategy_win_rate', 0.50)
            avg_win = signal.get('strategy_avg_win', 0.04)
            avg_loss = signal.get('strategy_avg_loss', 0.02)
            confidence = signal.get('confidence', 0.65)
            
            # Kelly Criterion: f = (p*b - q) / b
            # where p = win_rate, q = loss_rate, b = avg_win/avg_loss
            if avg_loss == 0:
                kelly_fraction = self.base_position_size
            else:
                b = avg_win / avg_loss
                kelly_fraction = (win_rate * b - (1 - win_rate)) / b
            
            # Use fractional Kelly (safer)
            fractional_kelly = kelly_fraction * 0.5  # Half Kelly
            
            # Apply bounds
            position_size = max(
                self.min_position_size,
                min(fractional_kelly, self.max_position_size)
            )
            
            # Adjust for confidence
            position_size *= confidence
            
            # Adjust for metabolic rate (organism's energy level)
            position_size *= self.metabolic_rate
            
            # Adjust for current drawdown
            drawdown = portfolio.get('current_drawdown', 0)
            if drawdown > 0.05:  # 5% drawdown
                position_size *= (1 - drawdown)  # Reduce size proportionally
            
            logger.info(f"💰 Position size calculated: {position_size:.2%} "
                       f"(Kelly: {fractional_kelly:.2%}, Confidence: {confidence:.2%})")
            
            return position_size
            
        except Exception as e:
            logger.error(f"Position sizing error: {e}")
            return self.min_position_size
    
    def extract_profits(self, portfolio: Dict) -> Dict[str, float]:
        """
        Extract profits like organism extracting nutrients
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Dict with amounts to withdraw
        """
        try:
            total_value = portfolio.get('total_value', 0)
            starting_capital = portfolio.get('starting_capital', 0)
            profit = total_value - starting_capital
            
            # Only extract if above threshold
            if profit < self.profit_threshold:
                logger.info(f"💰 Profit ${profit:.2f} below threshold ${self.profit_threshold:.2f}")
                return {'btc': 0, 'usdt': 0, 'reinvest': 0}
            
            # Calculate extraction amounts
            btc_amount = profit * self.withdrawal_btc_pct
            usdt_amount = profit * self.withdrawal_usdt_pct
            reinvest_amount = profit * self.reinvestment_rate
            
            logger.info(f"💰 Extracting profits: BTC ${btc_amount:.2f}, "
                       f"USDT ${usdt_amount:.2f}, Reinvest ${reinvest_amount:.2f}")
            
            return {
                'btc': btc_amount,
                'usdt': usdt_amount,
                'reinvest': reinvest_amount,
                'total_profit': profit
            }
            
        except Exception as e:
            logger.error(f"Profit extraction error: {e}")
            return {'btc': 0, 'usdt': 0, 'reinvest': 0}
    
    def adjust_metabolic_rate(self, performance: Dict):
        """
        Adjust how aggressively organism uses capital
        
        Good performance → Increase metabolism (more aggressive)
        Poor performance → Decrease metabolism (more conservative)
        
        Args:
            performance: Recent performance metrics
        """
        try:
            win_rate = performance.get('win_rate', 0.50)
            sharpe = performance.get('sharpe_ratio', 1.0)
            drawdown = performance.get('current_drawdown', 0)
            
            # Increase metabolic rate if performing well
            if win_rate > 0.60 and sharpe > 1.5 and drawdown < 0.08:
                self.metabolic_rate = min(self.metabolic_rate * 1.05, 1.5)
                logger.info(f"💰 Metabolic rate increased to {self.metabolic_rate:.2f}")
            
            # Decrease if performing poorly
            elif win_rate < 0.45 or drawdown > 0.12:
                self.metabolic_rate = max(self.metabolic_rate * 0.90, 0.5)
                logger.warning(f"💰 Metabolic rate decreased to {self.metabolic_rate:.2f}")
            
            # Update efficiency
            self._calculate_efficiency(performance)
            
        except Exception as e:
            logger.error(f"Metabolic rate adjustment error: {e}")
    
    def _calculate_efficiency(self, performance: Dict):
        """
        Calculate metabolic efficiency
        
        Efficiency = Returns / Risk Taken
        """
        try:
            returns = performance.get('total_return', 0)
            risk_taken = performance.get('total_risk_taken', 1)
            
            self.metabolic_efficiency = returns / max(risk_taken, 0.01)
            
            logger.info(f"💰 Metabolic efficiency: {self.metabolic_efficiency:.2f}")
            
        except Exception as e:
            logger.error(f"Efficiency calculation error: {e}")
    
    def allocate_capital(self, portfolio_value: float, pathway_allocations: Dict) -> Dict[str, float]:
        """
        Allocate capital across strategy pathways
        
        Args:
            portfolio_value: Total portfolio value
            pathway_allocations: Target allocation for each pathway
            
        Returns:
            Capital allocated to each pathway
        """
        allocations = {}
        
        for pathway, allocation_pct in pathway_allocations.items():
            allocated_capital = portfolio_value * allocation_pct * self.metabolic_rate
            allocations[pathway] = allocated_capital
            
        logger.info(f"💰 Capital allocated across {len(allocations)} pathways")
        
        return allocations
    
    def ensure_minimum_order_sizes(self, signal: Dict, pair_info: Dict) -> bool:
        """
        Ensure trade meets minimum order size
        
        Critical for avoiding exchange rejection
        
        Args:
            signal: Trade signal
            pair_info: Trading pair information
            
        Returns:
            True if meets minimum, False otherwise
        """
        min_order_usdt = pair_info.get('min_order_size_usdt', 10)
        signal_size_usdt = signal.get('size_usdt', 0)
        
        if signal_size_usdt < min_order_usdt:
            logger.warning(f"💰 Order size ${signal_size_usdt:.2f} below minimum ${min_order_usdt:.2f}")
            
            # Try to adjust to minimum
            if signal_size_usdt * 1.5 >= min_order_usdt:
                signal['size_usdt'] = min_order_usdt
                signal['adjusted'] = True
                logger.info(f"💰 Adjusted order size to ${min_order_usdt:.2f}")
                return True
            else:
                return False
        
        return True
    
    def manage_liquidity(self, portfolio: Dict, required_capital: float) -> bool:
        """
        Ensure sufficient liquidity for trades
        
        Args:
            portfolio: Current portfolio
            required_capital: Capital needed for trade
            
        Returns:
            True if sufficient liquidity available
        """
        available_capital = portfolio.get('available_capital', 0)
        reserved_capital = portfolio.get('reserved_capital', 0)
        
        free_capital = available_capital - reserved_capital
        
        if free_capital >= required_capital:
            return True
        
        # Check if we can free up capital from low-performing positions
        if self._can_free_capital(portfolio, required_capital - free_capital):
            logger.info(f"💰 Can free up ${required_capital - free_capital:.2f} from positions")
            return True
        
        logger.warning(f"💰 Insufficient liquidity: need ${required_capital:.2f}, have ${free_capital:.2f}")
        return False
    
    def _can_free_capital(self, portfolio: Dict, amount_needed: float) -> bool:
        """Check if we can liquidate positions to free capital"""
        positions = portfolio.get('positions', {})
        
        # Sort positions by performance (liquidate worst first)
        sorted_positions = sorted(
            positions.items(),
            key=lambda x: x[1].get('pnl_pct', 0)
        )
        
        available = 0
        for symbol, position in sorted_positions:
            if position.get('pnl_pct', 0) < 0.02:  # <2% profit
                available += position.get('value', 0)
                if available >= amount_needed:
                    return True
        
        return False


# Global metabolism instance
metabolism = Metabolism()
