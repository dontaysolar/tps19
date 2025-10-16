#!/usr/bin/env python3
"""
Correlation Analyzer - Portfolio risk correlation analysis
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class CorrelationAnalyzer:
    """
    Analyze correlation between assets and strategies for risk management
    """
    
    def __init__(self):
        self.correlation_matrix = {}
        self.price_history = {}  # Store recent price history
        self.max_history = 288  # 24 hours of 5-min candles
        
    def update_price(self, symbol: str, price: float, timestamp: datetime):
        """Update price history for symbol"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'price': price,
            'timestamp': timestamp
        })
        
        # Keep only recent history
        if len(self.price_history[symbol]) > self.max_history:
            self.price_history[symbol] = self.price_history[symbol][-self.max_history:]
    
    def calculate_correlation(self, symbol1: str, symbol2: str, 
                             periods: int = 100) -> float:
        """
        Calculate correlation between two assets
        
        Args:
            symbol1: First asset symbol
            symbol2: Second asset symbol
            periods: Number of periods to analyze
            
        Returns:
            Correlation coefficient (-1 to 1)
        """
        if symbol1 not in self.price_history or symbol2 not in self.price_history:
            return 0.0
        
        prices1 = [p['price'] for p in self.price_history[symbol1][-periods:]]
        prices2 = [p['price'] for p in self.price_history[symbol2][-periods:]]
        
        if len(prices1) < 10 or len(prices2) < 10:
            return 0.0
        
        # Ensure same length
        min_len = min(len(prices1), len(prices2))
        prices1 = prices1[-min_len:]
        prices2 = prices2[-min_len:]
        
        # Calculate returns
        returns1 = [(prices1[i] - prices1[i-1]) / prices1[i-1] 
                    for i in range(1, len(prices1))]
        returns2 = [(prices2[i] - prices2[i-1]) / prices2[i-1] 
                    for i in range(1, len(prices2))]
        
        if not returns1 or not returns2:
            return 0.0
        
        # Calculate correlation
        correlation = np.corrcoef(returns1, returns2)[0, 1]
        
        return float(correlation) if not np.isnan(correlation) else 0.0
    
    def get_portfolio_correlation_matrix(self, symbols: List[str]) -> Dict:
        """
        Get full correlation matrix for portfolio
        
        Args:
            symbols: List of symbols in portfolio
            
        Returns:
            Correlation matrix dict
        """
        matrix = {}
        
        for i, sym1 in enumerate(symbols):
            matrix[sym1] = {}
            for sym2 in symbols:
                if sym1 == sym2:
                    matrix[sym1][sym2] = 1.0
                else:
                    corr = self.calculate_correlation(sym1, sym2)
                    matrix[sym1][sym2] = corr
        
        return matrix
    
    def calculate_portfolio_risk(self, positions: List[Dict]) -> Dict:
        """
        Calculate portfolio-level risk considering correlations
        
        Args:
            positions: List of position dicts with symbol, size, volatility
            
        Returns:
            Risk metrics dict
        """
        if not positions:
            return {'total_risk': 0, 'diversification_benefit': 0}
        
        symbols = [p['symbol'] for p in positions]
        weights = np.array([p.get('weight', 1.0) for p in positions])
        volatilities = np.array([p.get('volatility', 0.02) for p in positions])
        
        # Normalize weights
        weights = weights / weights.sum()
        
        # Get correlation matrix
        n = len(positions)
        corr_matrix = np.eye(n)
        
        for i in range(n):
            for j in range(i+1, n):
                corr = self.calculate_correlation(symbols[i], symbols[j])
                corr_matrix[i, j] = corr
                corr_matrix[j, i] = corr
        
        # Calculate portfolio variance
        # σ_p^2 = w^T * Σ * w, where Σ = diag(σ) * C * diag(σ)
        vol_matrix = np.diag(volatilities)
        covariance_matrix = vol_matrix @ corr_matrix @ vol_matrix
        
        portfolio_variance = weights @ covariance_matrix @ weights
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Individual risk (if uncorrelated)
        individual_risk = np.sqrt(np.sum((weights * volatilities) ** 2))
        
        # Diversification benefit
        diversification_benefit = 1 - (portfolio_volatility / individual_risk)
        
        return {
            'portfolio_volatility': float(portfolio_volatility),
            'individual_risk': float(individual_risk),
            'diversification_benefit': float(diversification_benefit),
            'correlation_matrix': corr_matrix.tolist(),
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_high_correlation_risk(self, positions: List[Dict], 
                                    threshold: float = 0.8) -> List[Dict]:
        """
        Detect positions with dangerously high correlation
        
        Args:
            positions: List of positions
            threshold: Correlation threshold (default 0.8)
            
        Returns:
            List of high-correlation pairs
        """
        high_corr_pairs = []
        
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:
                corr = self.calculate_correlation(pos1['symbol'], pos2['symbol'])
                
                if abs(corr) > threshold:
                    high_corr_pairs.append({
                        'symbol1': pos1['symbol'],
                        'symbol2': pos2['symbol'],
                        'correlation': corr,
                        'risk_level': 'HIGH' if abs(corr) > 0.9 else 'MEDIUM',
                        'recommendation': self._generate_correlation_recommendation(corr, pos1, pos2)
                    })
        
        return high_corr_pairs
    
    def _generate_correlation_recommendation(self, corr: float, 
                                            pos1: Dict, pos2: Dict) -> str:
        """Generate recommendation based on correlation"""
        if abs(corr) > 0.9:
            return f"VERY HIGH correlation ({corr:.2f}) - Consider closing one position to reduce risk"
        elif abs(corr) > 0.8:
            return f"HIGH correlation ({corr:.2f}) - Reduce position sizes or hedge"
        else:
            return "Moderate correlation - Monitor closely"
    
    def get_diversification_score(self, positions: List[Dict]) -> float:
        """
        Calculate portfolio diversification score (0-100)
        
        Higher score = better diversification
        """
        if len(positions) < 2:
            return 0  # Can't diversify with 1 position
        
        symbols = [p['symbol'] for p in positions]
        
        # Calculate average correlation
        correlations = []
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                corr = self.calculate_correlation(sym1, sym2)
                correlations.append(abs(corr))
        
        if not correlations:
            return 50  # Default
        
        avg_correlation = np.mean(correlations)
        
        # Convert to score (lower correlation = higher score)
        # 0 correlation = 100 score, 1 correlation = 0 score
        score = (1 - avg_correlation) * 100
        
        return float(score)


# Global instance
correlation_analyzer = CorrelationAnalyzer()
