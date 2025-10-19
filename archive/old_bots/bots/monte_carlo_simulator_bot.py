#!/usr/bin/env python3
"""
Monte Carlo Simulation Bot
Risk analysis through probabilistic modeling
Tests strategies under thousands of scenarios
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class MonteCarloSimulatorBot:
    def __init__(self):
        self.name = "Monte_Carlo_Simulator"
        self.version = "1.0.0"
        self.enabled = True
        
        self.n_simulations = 1000
        self.confidence_levels = [0.95, 0.99]
        
        self.metrics = {
            'simulations_run': 0,
            'scenarios_tested': 0,
            'var_calculations': 0
        }
    
    def simulate_price_paths(self, current_price: float, volatility: float, 
                            drift: float, n_steps: int) -> np.ndarray:
        """
        Simulate future price paths using geometric Brownian motion
        
        Args:
            current_price: Starting price
            volatility: Annual volatility (e.g., 0.3 for 30%)
            drift: Expected annual return
            n_steps: Number of time steps
        """
        dt = 1/252  # Daily steps
        
        # Generate random shocks
        shocks = np.random.standard_normal((self.n_simulations, n_steps))
        
        # Calculate price paths
        price_paths = np.zeros((self.n_simulations, n_steps + 1))
        price_paths[:, 0] = current_price
        
        for t in range(1, n_steps + 1):
            # Geometric Brownian Motion
            price_paths[:, t] = price_paths[:, t-1] * np.exp(
                (drift - 0.5 * volatility**2) * dt + 
                volatility * np.sqrt(dt) * shocks[:, t-1]
            )
        
        self.metrics['simulations_run'] += 1
        self.metrics['scenarios_tested'] += self.n_simulations
        
        return price_paths
    
    def calculate_var(self, returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: Array of returns from simulations
            confidence_level: Confidence level (e.g., 0.95 for 95%)
        """
        var = np.percentile(returns, (1 - confidence_level) * 100)
        self.metrics['var_calculations'] += 1
        return var
    
    def calculate_cvar(self, returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR / Expected Shortfall)
        Average loss in worst (1-confidence_level)% of cases
        """
        var = self.calculate_var(returns, confidence_level)
        cvar = returns[returns <= var].mean()
        return cvar
    
    def stress_test_strategy(self, strategy_returns: List[float], 
                            scenarios: Dict[str, Dict]) -> Dict:
        """
        Stress test strategy under various scenarios
        
        Args:
            strategy_returns: Historical strategy returns
            scenarios: {scenario_name: {volatility_mult: float, drift_adj: float}}
        """
        results = {}
        base_volatility = np.std(strategy_returns)
        base_drift = np.mean(strategy_returns)
        
        for scenario_name, params in scenarios.items():
            vol_mult = params.get('volatility_mult', 1.0)
            drift_adj = params.get('drift_adj', 0.0)
            
            # Adjust parameters for scenario
            scenario_vol = base_volatility * vol_mult
            scenario_drift = base_drift + drift_adj
            
            # Simulate
            simulated_returns = np.random.normal(
                scenario_drift, 
                scenario_vol, 
                self.n_simulations
            )
            
            # Calculate risk metrics
            var_95 = self.calculate_var(simulated_returns, 0.95)
            var_99 = self.calculate_var(simulated_returns, 0.99)
            cvar_95 = self.calculate_cvar(simulated_returns, 0.95)
            
            # Probability of loss
            prob_loss = (simulated_returns < 0).sum() / len(simulated_returns)
            
            # Expected return
            expected_return = simulated_returns.mean()
            
            results[scenario_name] = {
                'expected_return': expected_return,
                'var_95': var_95,
                'var_99': var_99,
                'cvar_95': cvar_95,
                'probability_of_loss': prob_loss,
                'worst_case': simulated_returns.min(),
                'best_case': simulated_returns.max()
            }
        
        return {
            'scenarios': results,
            'n_simulations': self.n_simulations,
            'base_volatility': base_volatility,
            'base_drift': base_drift,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_portfolio_risk(self, positions: Dict[str, Dict], 
                                correlation_matrix: np.ndarray = None) -> Dict:
        """
        Simulate portfolio risk with multiple positions
        
        Args:
            positions: {asset: {price: float, quantity: float, volatility: float}}
            correlation_matrix: Correlation between assets
        """
        n_assets = len(positions)
        
        if correlation_matrix is None:
            # Assume moderate correlation
            correlation_matrix = np.eye(n_assets) * 0.7 + 0.3
        
        # Simulate correlated returns
        cholesky = np.linalg.cholesky(correlation_matrix)
        uncorrelated_returns = np.random.standard_normal((self.n_simulations, n_assets))
        correlated_returns = uncorrelated_returns @ cholesky.T
        
        # Calculate portfolio values
        portfolio_values = []
        assets = list(positions.keys())
        
        for sim in range(self.n_simulations):
            portfolio_value = 0
            for i, asset in enumerate(assets):
                pos = positions[asset]
                price = pos['price']
                quantity = pos['quantity']
                volatility = pos.get('volatility', 0.3)
                
                # Simulate price change
                return_pct = correlated_returns[sim, i] * volatility
                new_price = price * (1 + return_pct)
                portfolio_value += new_price * quantity
            
            portfolio_values.append(portfolio_value)
        
        portfolio_values = np.array(portfolio_values)
        initial_value = sum([p['price'] * p['quantity'] for p in positions.values()])
        portfolio_returns = (portfolio_values - initial_value) / initial_value
        
        # Risk metrics
        var_95 = self.calculate_var(portfolio_returns, 0.95)
        var_99 = self.calculate_var(portfolio_returns, 0.99)
        cvar_95 = self.calculate_cvar(portfolio_returns, 0.95)
        
        return {
            'initial_value': initial_value,
            'mean_final_value': portfolio_values.mean(),
            'var_95_pct': var_95 * 100,
            'var_99_pct': var_99 * 100,
            'cvar_95_pct': cvar_95 * 100,
            'max_loss_pct': portfolio_returns.min() * 100,
            'max_gain_pct': portfolio_returns.max() * 100,
            'probability_of_loss': (portfolio_returns < 0).sum() / len(portfolio_returns),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'n_simulations': self.n_simulations,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = MonteCarloSimulatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
