#!/usr/bin/env python3
"""
Scalping Bot - High-frequency short-term trading
New implementation based on enhancement roadmap
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class ScalpingBot:
    """
    High-frequency scalping bot
    
    Features:
    - 1-5 minute timeframe
    - Small profit targets (0.3-1%)
    - High win rate focus (70%+)
    - Quick exits (minutes, not hours)
    - Volume and spread sensitive
    """
    
    def __init__(self):
        self.name = "Scalping Bot"
        
        # Scalping parameters
        self.timeframe = "1m"  # 1 minute candles
        self.profit_target = 0.005  # 0.5% profit target
        self.stop_loss = 0.003  # 0.3% stop loss
        self.max_hold_time = timedelta(minutes=15)
        
        # Entry requirements
        self.min_volume_ratio = 1.5  # 1.5x average volume
        self.max_spread_pct = 0.001  # 0.1% max spread
        self.min_momentum = 0.002  # 0.2% momentum
        
        # Position tracking
        self.active_scalps = []
        self.completed_scalps = []
        
        # Performance
        self.total_scalps = 0
        self.winning_scalps = 0
        self.total_profit = 0
        self.today_scalps = 0
        
        logger.info("⚡ Scalping Bot initialized")
    
    def scan_scalping_opportunity(self, market_data: Dict) -> Optional[Dict]:
        """
        Scan for scalping opportunity
        
        Args:
            market_data: Real-time market data
            
        Returns:
            Scalping opportunity or None
        """
        try:
            symbol = market_data.get('symbol')
            price = market_data.get('price', 0)
            volume = market_data.get('volume', 0)
            avg_volume = market_data.get('avg_volume', volume)
            bid = market_data.get('bid', price * 0.999)
            ask = market_data.get('ask', price * 1.001)
            
            # Check volume requirement
            volume_ratio = volume / avg_volume if avg_volume > 0 else 0
            if volume_ratio < self.min_volume_ratio:
                return None
            
            # Check spread
            spread_pct = (ask - bid) / bid if bid > 0 else 1
            if spread_pct > self.max_spread_pct:
                return None
            
            # Check momentum
            momentum = self._calculate_momentum(market_data)
            if abs(momentum) < self.min_momentum:
                return None
            
            # Determine direction
            if momentum > 0:
                direction = "LONG"
                entry_price = ask
                target_price = entry_price * (1 + self.profit_target)
                stop_price = entry_price * (1 - self.stop_loss)
            else:
                direction = "SHORT"
                entry_price = bid
                target_price = entry_price * (1 - self.profit_target)
                stop_price = entry_price * (1 + self.stop_loss)
            
            opportunity = {
                'symbol': symbol,
                'direction': direction,
                'entry_price': entry_price,
                'target_price': target_price,
                'stop_price': stop_price,
                'volume_ratio': volume_ratio,
                'spread_pct': spread_pct,
                'momentum': momentum,
                'confidence': self._calculate_confidence(volume_ratio, spread_pct, momentum),
                'detected_at': datetime.now()
            }
            
            logger.info(f"⚡ Scalp opportunity: {symbol} {direction} @ {entry_price:.2f} "
                       f"(Target: {target_price:.2f}, Stop: {stop_price:.2f})")
            
            return opportunity
            
        except Exception as e:
            logger.error(f"Scalping scan error: {e}")
            return None
    
    def _calculate_momentum(self, market_data: Dict) -> float:
        """Calculate short-term momentum"""
        # Get recent price changes
        recent_prices = market_data.get('recent_prices', [])
        if len(recent_prices) < 5:
            return 0
        
        # Calculate momentum as rate of change
        latest = recent_prices[-1]
        five_ago = recent_prices[-5]
        
        momentum = (latest - five_ago) / five_ago if five_ago > 0 else 0
        return momentum
    
    def _calculate_confidence(self, volume_ratio: float, 
                             spread_pct: float, momentum: float) -> float:
        """Calculate confidence score for scalp"""
        # Volume component (0-0.4)
        volume_score = min(0.4, volume_ratio / 3)
        
        # Spread component (0-0.3)
        spread_score = 0.3 * (1 - min(1, spread_pct / self.max_spread_pct))
        
        # Momentum component (0-0.3)
        momentum_score = min(0.3, abs(momentum) / 0.01)
        
        confidence = volume_score + spread_score + momentum_score
        return min(0.95, confidence)
    
    def enter_scalp(self, opportunity: Dict) -> Dict:
        """
        Enter scalp position
        
        Args:
            opportunity: Scalping opportunity
            
        Returns:
            Position details
        """
        scalp = {
            'id': f"scalp_{int(datetime.now().timestamp())}",
            'symbol': opportunity['symbol'],
            'direction': opportunity['direction'],
            'entry_price': opportunity['entry_price'],
            'target_price': opportunity['target_price'],
            'stop_price': opportunity['stop_price'],
            'entry_time': datetime.now(),
            'max_hold_until': datetime.now() + self.max_hold_time,
            'status': 'OPEN',
            'confidence': opportunity['confidence']
        }
        
        self.active_scalps.append(scalp)
        self.total_scalps += 1
        self.today_scalps += 1
        
        logger.info(f"⚡ Scalp entered: {scalp['symbol']} {scalp['direction']} "
                   f"@ {scalp['entry_price']:.2f}")
        
        return scalp
    
    def monitor_scalp(self, scalp: Dict, current_price: float) -> Optional[str]:
        """
        Monitor active scalp position
        
        Args:
            scalp: Active scalp position
            current_price: Current market price
            
        Returns:
            Action to take (None, 'EXIT_TARGET', 'EXIT_STOP', 'EXIT_TIME')
        """
        if scalp['status'] != 'OPEN':
            return None
        
        direction = scalp['direction']
        target = scalp['target_price']
        stop = scalp['stop_price']
        max_hold = scalp['max_hold_until']
        
        # Check profit target
        if direction == "LONG" and current_price >= target:
            return 'EXIT_TARGET'
        elif direction == "SHORT" and current_price <= target:
            return 'EXIT_TARGET'
        
        # Check stop loss
        if direction == "LONG" and current_price <= stop:
            return 'EXIT_STOP'
        elif direction == "SHORT" and current_price >= stop:
            return 'EXIT_STOP'
        
        # Check time stop
        if datetime.now() >= max_hold:
            return 'EXIT_TIME'
        
        return None
    
    def exit_scalp(self, scalp: Dict, exit_price: float, reason: str):
        """
        Exit scalp position
        
        Args:
            scalp: Scalp position
            exit_price: Exit price
            reason: Exit reason
        """
        entry_price = scalp['entry_price']
        direction = scalp['direction']
        
        # Calculate P&L
        if direction == "LONG":
            pnl_pct = (exit_price - entry_price) / entry_price
        else:  # SHORT
            pnl_pct = (entry_price - exit_price) / entry_price
        
        # Update scalp
        scalp['status'] = 'CLOSED'
        scalp['exit_price'] = exit_price
        scalp['exit_time'] = datetime.now()
        scalp['exit_reason'] = reason
        scalp['pnl_pct'] = pnl_pct
        scalp['hold_time'] = (datetime.now() - scalp['entry_time']).total_seconds()
        
        # Update stats
        if pnl_pct > 0:
            self.winning_scalps += 1
        
        self.total_profit += pnl_pct
        
        # Move to completed
        if scalp in self.active_scalps:
            self.active_scalps.remove(scalp)
        self.completed_scalps.append(scalp)
        
        # Keep only last 100
        if len(self.completed_scalps) > 100:
            self.completed_scalps = self.completed_scalps[-100:]
        
        logger.info(f"⚡ Scalp exited: {scalp['symbol']} {direction} "
                   f"@ {exit_price:.2f} - P&L: {pnl_pct:+.2%} ({reason})")
    
    def get_stats(self) -> Dict:
        """Get scalping bot statistics"""
        win_rate = self.winning_scalps / max(1, self.total_scalps)
        
        # Calculate average hold time
        if self.completed_scalps:
            avg_hold_time = statistics.mean([
                s['hold_time'] for s in self.completed_scalps
                if 'hold_time' in s
            ]) / 60  # Convert to minutes
        else:
            avg_hold_time = 0
        
        return {
            'active_scalps': len(self.active_scalps),
            'total_scalps': self.total_scalps,
            'today_scalps': self.today_scalps,
            'winning_scalps': self.winning_scalps,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'avg_profit_per_scalp': self.total_profit / max(1, self.total_scalps),
            'avg_hold_time_minutes': avg_hold_time,
            'profit_target': self.profit_target,
            'stop_loss': self.stop_loss
        }


# Global instance
scalping_bot = ScalpingBot()
