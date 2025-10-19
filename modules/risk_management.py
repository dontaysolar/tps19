#!/usr/bin/env python3
"""
TPS19 Risk Management - Advanced position sizing and risk controls
Implements: Kelly Criterion, VaR, CVaR, Maximum Drawdown Protection, Dynamic Position Sizing
"""

import json
import sqlite3
import os
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskManager:
    """
    Advanced risk management system with multiple position sizing algorithms
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        """
        Initialize Risk Manager
        
        Args:
            initial_capital: Starting capital for risk calculations
        """
        workspace = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(workspace, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "risk.db")
        
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Risk limits
        self.max_position_size = 0.1  # 10% max per position
        self.max_daily_loss = 0.05    # 5% max daily loss
        self.max_total_exposure = 0.5  # 50% max total exposure
        self.max_correlation_exposure = 0.3  # 30% for correlated assets
        
        # Kelly Criterion settings
        self.kelly_fraction = 0.25  # Use 25% of Kelly (fractional Kelly)
        self.min_kelly_edge = 0.55  # Min win rate to use Kelly
        
        self.init_database()
        logger.info("Risk Manager initialized")
        
    def init_database(self):
        """Initialize risk management database with enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Risk metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_value REAL NOT NULL,
                daily_pnl REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                current_drawdown REAL DEFAULT 0.0,
                var_95 REAL DEFAULT 0.0,
                cvar_95 REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                sortino_ratio REAL DEFAULT 0.0,
                total_exposure REAL DEFAULT 0.0,
                leverage REAL DEFAULT 1.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Risk limits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                limit_type TEXT NOT NULL,
                limit_value REAL NOT NULL,
                current_value REAL DEFAULT 0.0,
                status TEXT DEFAULT 'ok',
                breached_at DATETIME,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Position risk table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_risk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                position_size REAL NOT NULL,
                var_95 REAL,
                expected_loss REAL,
                max_loss REAL,
                risk_score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Correlation matrix table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset_correlation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_1 TEXT NOT NULL,
                symbol_2 TEXT NOT NULL,
                correlation REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trade outcomes (for Kelly Criterion)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT,
                win BOOLEAN NOT NULL,
                pnl REAL NOT NULL,
                risk_amount REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Risk database initialized")
        
    def calculate_kelly_position_size(self, win_rate: float, avg_win: float, 
                                     avg_loss: float, portfolio_value: float) -> float:
        """
        Calculate optimal position size using Kelly Criterion
        
        Kelly % = W - [(1 - W) / R]
        Where:
            W = Win rate (probability of winning)
            R = Win/Loss ratio (average win / average loss)
            
        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average winning trade amount
            avg_loss: Average losing trade amount (positive number)
            portfolio_value: Current portfolio value
            
        Returns:
            Recommended position size in dollars
        """
        if win_rate < self.min_kelly_edge or avg_loss == 0:
            # If edge is too small or no data, use fixed percentage
            return portfolio_value * 0.02  # 2% fixed
            
        # Calculate win/loss ratio
        win_loss_ratio = abs(avg_win / avg_loss)
        
        # Kelly formula
        kelly_pct = win_rate - ((1 - win_rate) / win_loss_ratio)
        
        # Apply Kelly fraction (fractional Kelly for safety)
        kelly_pct *= self.kelly_fraction
        
        # Ensure Kelly is positive and capped
        kelly_pct = max(0, min(kelly_pct, self.max_position_size))
        
        position_size = portfolio_value * kelly_pct
        
        logger.info(f"Kelly position size: ${position_size:.2f} ({kelly_pct*100:.2f}% of portfolio)")
        
        return position_size
        
    def calculate_position_size(self, portfolio_value: float, risk_per_trade: float = 0.02,
                               stop_loss_pct: float = 0.02, method: str = "fixed") -> float:
        """
        Calculate position size using various methods
        
        Args:
            portfolio_value: Current portfolio value
            risk_per_trade: Risk percentage per trade (0-1)
            stop_loss_pct: Stop loss percentage (0-1)
            method: Sizing method (fixed, kelly, volatility, dynamic)
            
        Returns:
            Position size in dollars
        """
        if method == "fixed":
            # Fixed percentage risk
            max_risk_amount = portfolio_value * risk_per_trade
            position_size = max_risk_amount / stop_loss_pct
            
        elif method == "kelly":
            # Use Kelly Criterion
            stats = self._get_historical_stats()
            position_size = self.calculate_kelly_position_size(
                stats['win_rate'],
                stats['avg_win'],
                stats['avg_loss'],
                portfolio_value
            )
            
        elif method == "volatility":
            # Volatility-based sizing (inverse relationship)
            # Higher volatility = smaller position
            volatility = self._estimate_volatility()
            base_size = portfolio_value * risk_per_trade
            position_size = base_size / max(volatility, 0.01)
            
        elif method == "dynamic":
            # Dynamic sizing based on recent performance
            performance_factor = self._get_performance_factor()
            base_size = portfolio_value * risk_per_trade
            position_size = base_size * performance_factor
            
        else:
            # Default to fixed
            max_risk_amount = portfolio_value * risk_per_trade
            position_size = max_risk_amount / stop_loss_pct
            
        # Apply maximum position size limit
        max_position_value = portfolio_value * self.max_position_size
        position_size = min(position_size, max_position_value)
        
        return position_size
        
    def check_risk_limits(self, portfolio_value: float, daily_pnl: float,
                         total_exposure: float) -> List[Dict]:
        """
        Check if any risk limits are exceeded
        
        Returns:
            List of risk violations
        """
        risks = []
        
        # Check daily loss limit
        daily_loss_pct = abs(daily_pnl) / portfolio_value if portfolio_value > 0 else 0
        if daily_pnl < 0 and daily_loss_pct > self.max_daily_loss:
            risks.append({
                "type": "daily_loss_limit",
                "current": round(daily_loss_pct * 100, 2),
                "limit": round(self.max_daily_loss * 100, 2),
                "severity": "high",
                "action": "halt_trading"
            })
            self._log_risk_breach("daily_loss_limit", daily_loss_pct)
            
        # Check total exposure limit
        exposure_pct = total_exposure / portfolio_value if portfolio_value > 0 else 0
        if exposure_pct > self.max_total_exposure:
            risks.append({
                "type": "total_exposure_limit",
                "current": round(exposure_pct * 100, 2),
                "limit": round(self.max_total_exposure * 100, 2),
                "severity": "medium",
                "action": "reduce_positions"
            })
            self._log_risk_breach("total_exposure", exposure_pct)
            
        # Check drawdown
        drawdown = self._calculate_current_drawdown(portfolio_value)
        if drawdown > 0.15:  # 15% drawdown threshold
            risks.append({
                "type": "maximum_drawdown",
                "current": round(drawdown * 100, 2),
                "limit": 15,
                "severity": "critical",
                "action": "reduce_risk"
            })
            
        return risks
        
    def calculate_var(self, returns: List[float], confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: List of historical returns
            confidence: Confidence level (e.g., 0.95 for 95% VaR)
            
        Returns:
            VaR value (positive number representing potential loss)
        """
        if not returns or len(returns) < 2:
            return 0.0
            
        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        
        var = abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0
        
        return var
        
    def calculate_cvar(self, returns: List[float], confidence: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR / Expected Shortfall)
        Average of losses beyond VaR
        
        Args:
            returns: List of historical returns
            confidence: Confidence level
            
        Returns:
            CVaR value
        """
        if not returns or len(returns) < 2:
            return 0.0
            
        var = self.calculate_var(returns, confidence)
        
        # Calculate average of returns worse than VaR
        tail_losses = [abs(r) for r in returns if r < -var]
        
        if tail_losses:
            cvar = sum(tail_losses) / len(tail_losses)
        else:
            cvar = var
            
        return cvar
        
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            returns: List of returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sharpe ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
            
        avg_return = sum(returns) / len(returns)
        
        # Calculate standard deviation
        variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return 0.0
            
        # Annualize (assuming daily returns)
        annual_return = avg_return * 252
        annual_std = std_dev * math.sqrt(252)
        
        sharpe = (annual_return - risk_free_rate) / annual_std
        
        return sharpe
        
    def calculate_sortino_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sortino Ratio (only considers downside deviation)
        
        Args:
            returns: List of returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sortino ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
            
        avg_return = sum(returns) / len(returns)
        
        # Calculate downside deviation (only negative returns)
        negative_returns = [r for r in returns if r < 0]
        
        if not negative_returns:
            return float('inf')  # No downside risk
            
        downside_variance = sum(r ** 2 for r in negative_returns) / len(negative_returns)
        downside_dev = math.sqrt(downside_variance)
        
        if downside_dev == 0:
            return 0.0
            
        # Annualize
        annual_return = avg_return * 252
        annual_downside = downside_dev * math.sqrt(252)
        
        sortino = (annual_return - risk_free_rate) / annual_downside
        
        return sortino
        
    def calculate_max_drawdown(self, equity_curve: List[float]) -> Tuple[float, int, int]:
        """
        Calculate maximum drawdown from equity curve
        
        Args:
            equity_curve: List of portfolio values over time
            
        Returns:
            Tuple of (max_drawdown_pct, start_index, end_index)
        """
        if not equity_curve or len(equity_curve) < 2:
            return 0.0, 0, 0
            
        peak = equity_curve[0]
        max_dd = 0.0
        max_dd_start = 0
        max_dd_end = 0
        current_peak_idx = 0
        
        for i, value in enumerate(equity_curve):
            if value > peak:
                peak = value
                current_peak_idx = i
            else:
                dd = (peak - value) / peak
                if dd > max_dd:
                    max_dd = dd
                    max_dd_start = current_peak_idx
                    max_dd_end = i
                    
        return max_dd, max_dd_start, max_dd_end
        
    def _calculate_current_drawdown(self, current_value: float) -> float:
        """Calculate current drawdown from peak"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT MAX(portfolio_value) FROM risk_metrics
            WHERE timestamp >= datetime('now', '-30 days')
        ''')
        
        peak = cursor.fetchone()[0]
        conn.close()
        
        if peak and peak > 0:
            drawdown = (peak - current_value) / peak
            return max(0, drawdown)
        return 0.0
        
    def _get_historical_stats(self) -> Dict:
        """Get historical trading statistics for Kelly Criterion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as win_rate,
                AVG(CASE WHEN win = 1 THEN pnl ELSE 0 END) as avg_win,
                AVG(CASE WHEN win = 0 THEN ABS(pnl) ELSE 0 END) as avg_loss
            FROM trade_outcomes
            WHERE timestamp >= datetime('now', '-90 days')
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] is not None:
            return {
                "win_rate": result[0],
                "avg_win": result[1] or 0,
                "avg_loss": result[2] or 1
            }
        else:
            # Default values if no history
            return {
                "win_rate": 0.5,
                "avg_win": 100,
                "avg_loss": 100
            }
            
    def _estimate_volatility(self) -> float:
        """Estimate market volatility from recent data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT daily_pnl FROM risk_metrics
            WHERE timestamp >= datetime('now', '-30 days')
            ORDER BY timestamp DESC
        ''')
        
        pnls = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if len(pnls) < 2:
            return 0.02  # Default 2% volatility
            
        # Calculate standard deviation
        mean_pnl = sum(pnls) / len(pnls)
        variance = sum((p - mean_pnl) ** 2 for p in pnls) / (len(pnls) - 1)
        std_dev = math.sqrt(variance)
        
        # Normalize to percentage
        avg_portfolio = self.current_capital
        volatility = std_dev / avg_portfolio if avg_portfolio > 0 else 0.02
        
        return min(volatility, 0.10)  # Cap at 10%
        
    def _get_performance_factor(self) -> float:
        """Get performance factor for dynamic position sizing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT daily_pnl FROM risk_metrics
            WHERE timestamp >= datetime('now', '-7 days')
            ORDER BY timestamp DESC
        ''')
        
        recent_pnls = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not recent_pnls:
            return 1.0
            
        # If winning, increase size slightly; if losing, decrease
        total_pnl = sum(recent_pnls)
        
        if total_pnl > 0:
            factor = min(1.5, 1.0 + (total_pnl / self.current_capital))
        else:
            factor = max(0.5, 1.0 + (total_pnl / self.current_capital))
            
        return factor
        
    def _log_risk_breach(self, limit_type: str, current_value: float):
        """Log a risk limit breach"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO risk_limits (limit_type, current_value, status, breached_at)
            VALUES (?, ?, 'breached', CURRENT_TIMESTAMP)
        ''', (limit_type, current_value))
        
        conn.commit()
        conn.close()
        
    def update_risk_metrics(self, portfolio_value: float, daily_pnl: float,
                           total_exposure: float = 0.0):
        """Update risk metrics in database"""
        # Calculate current drawdown
        drawdown = self._calculate_current_drawdown(portfolio_value)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO risk_metrics (portfolio_value, daily_pnl, current_drawdown, total_exposure)
            VALUES (?, ?, ?, ?)
        ''', (portfolio_value, daily_pnl, drawdown, total_exposure))
        
        conn.commit()
        conn.close()
        
        self.current_capital = portfolio_value
        
    def log_trade_outcome(self, strategy: str, win: bool, pnl: float, risk_amount: float):
        """Log trade outcome for Kelly Criterion calculations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trade_outcomes (strategy, win, pnl, risk_amount)
            VALUES (?, ?, ?, ?)
        ''', (strategy, win, pnl, risk_amount))
        
        conn.commit()
        conn.close()
        
    def get_risk_report(self) -> Dict:
        """Generate comprehensive risk report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get latest metrics
        cursor.execute('''
            SELECT portfolio_value, daily_pnl, max_drawdown, current_drawdown,
                   var_95, sharpe_ratio, total_exposure
            FROM risk_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        
        latest = cursor.fetchone()
        
        # Get recent performance
        cursor.execute('''
            SELECT AVG(daily_pnl), MIN(daily_pnl), MAX(daily_pnl)
            FROM risk_metrics
            WHERE timestamp >= datetime('now', '-7 days')
        ''')
        
        performance = cursor.fetchone()
        
        # Get active risk breaches
        cursor.execute('''
            SELECT limit_type, current_value
            FROM risk_limits
            WHERE status = 'breached' AND timestamp >= datetime('now', '-1 day')
        ''')
        
        breaches = cursor.fetchall()
        conn.close()
        
        return {
            "portfolio_value": latest[0] if latest else 0,
            "daily_pnl": latest[1] if latest else 0,
            "max_drawdown": round((latest[2] if latest else 0) * 100, 2),
            "current_drawdown": round((latest[3] if latest else 0) * 100, 2),
            "var_95": latest[4] if latest else 0,
            "sharpe_ratio": round(latest[5] if latest else 0, 2),
            "total_exposure": round((latest[6] if latest else 0) / (latest[0] if latest and latest[0] > 0 else 1) * 100, 2),
            "avg_daily_pnl_7d": performance[0] if performance else 0,
            "min_daily_pnl_7d": performance[1] if performance else 0,
            "max_daily_pnl_7d": performance[2] if performance else 0,
            "active_breaches": len(breaches),
            "risk_status": "critical" if breaches else "normal"
        }


if __name__ == "__main__":
    # Test the risk manager
    risk = RiskManager(initial_capital=10000)
    print("✅ Risk Manager initialized successfully")
    
    # Test Kelly position sizing
    kelly_size = risk.calculate_kelly_position_size(0.6, 150, 100, 10000)
    print(f"Kelly position size: ${kelly_size:.2f}")
    
    # Test position sizing methods
    fixed_size = risk.calculate_position_size(10000, method="fixed")
    print(f"Fixed position size: ${fixed_size:.2f}")
    
    # Test risk limits
    risks = risk.check_risk_limits(10000, -300, 4000)
    print(f"Risk violations: {len(risks)}")
    
    # Test VaR calculation
    returns = [-0.02, 0.01, -0.01, 0.03, -0.04, 0.02, -0.01]
    var = risk.calculate_var(returns)
    print(f"95% VaR: {var*100:.2f}%")
    
    # Get risk report
    report = risk.get_risk_report()
    print(f"Risk report: {report}")
