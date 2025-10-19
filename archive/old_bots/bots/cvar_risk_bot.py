#!/usr/bin/env python3
"""
CVaR (Conditional Value at Risk) Bot
Expected Shortfall - average loss in worst scenarios
More conservative than VaR
"""

import numpy as np
from datetime import datetime
from typing import Dict

class CVaRRiskBot:
    def __init__(self):
        self.name = "CVaR_Risk"
        self.version = "1.0.0"
        self.enabled = True
        self.confidence_level = 0.95
        self.metrics = {'calculations': 0, 'alerts': 0}
    
    def calculate_cvar(self, returns: np.ndarray, confidence: float = 0.95) -> Dict:
        """Calculate CVaR (Expected Shortfall)"""
        var_threshold = np.percentile(returns, (1 - confidence) * 100)
        tail_losses = returns[returns <= var_threshold]
        cvar = tail_losses.mean() if len(tail_losses) > 0 else var_threshold
        
        self.metrics['calculations'] += 1
        
        return {
            'cvar': cvar,
            'cvar_pct': cvar * 100,
            'var': var_threshold,
            'tail_observations': len(tail_losses),
            'worst_case': returns.min(),
            'confidence': confidence,
            'interpretation': f"Average loss in worst {(1-confidence)*100:.0f}% scenarios: {cvar*100:.2f}%",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = CVaRRiskBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
