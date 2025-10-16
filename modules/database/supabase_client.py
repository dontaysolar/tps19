#!/usr/bin/env python3
"""
Supabase Database Client - Cloud-native data persistence
Optimized for Vercel deployment
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    Client = None

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseClient:
    """
    Supabase client for cloud database operations
    Replaces local SQLite for Vercel deployment
    """
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.connected = False
        
        # Get credentials from environment
        self.url = os.getenv('SUPABASE_URL', '')
        self.key = os.getenv('SUPABASE_KEY', '')
        
        if HAS_SUPABASE and self.url and self.key:
            self._connect()
        else:
            logger.warning("Supabase not configured - using local fallback")
    
    def _connect(self):
        """Connect to Supabase"""
        try:
            self.client = create_client(self.url, self.key)
            self.connected = True
            logger.info("✅ Connected to Supabase")
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}")
            self.connected = False
    
    # ========== TRADES TABLE ==========
    
    def save_trade(self, trade: Dict) -> Optional[str]:
        """Save trade to database"""
        if not self.connected:
            return self._fallback_save('trades', trade)
        
        try:
            result = self.client.table('trades').insert({
                'trade_id': trade.get('id', f"trade_{datetime.now().timestamp()}"),
                'symbol': trade['symbol'],
                'side': trade['side'],
                'entry_price': trade['entry_price'],
                'exit_price': trade.get('exit_price'),
                'size': trade['size'],
                'pnl': trade.get('pnl', 0),
                'pnl_pct': trade.get('pnl_pct', 0),
                'strategy': trade.get('strategy', ''),
                'entry_time': trade['entry_time'],
                'exit_time': trade.get('exit_time'),
                'status': trade.get('status', 'open'),
                'metadata': json.dumps(trade.get('metadata', {}))
            }).execute()
            
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            logger.error(f"Trade save error: {e}")
            return None
    
    def get_trades(self, filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
        """Get trades with optional filters"""
        if not self.connected:
            return []
        
        try:
            query = self.client.table('trades').select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.limit(limit).order('entry_time', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Get trades error: {e}")
            return []
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        return self.get_trades({'status': 'open'})
    
    # ========== PERFORMANCE TABLE ==========
    
    def save_performance_snapshot(self, snapshot: Dict) -> bool:
        """Save daily/hourly performance snapshot"""
        if not self.connected:
            return False
        
        try:
            self.client.table('performance_snapshots').insert({
                'timestamp': snapshot.get('timestamp', datetime.now().isoformat()),
                'total_pnl': snapshot['total_pnl'],
                'daily_pnl': snapshot.get('daily_pnl', 0),
                'total_trades': snapshot['total_trades'],
                'win_rate': snapshot['win_rate'],
                'sharpe_ratio': snapshot.get('sharpe_ratio', 0),
                'max_drawdown': snapshot.get('max_drawdown', 0),
                'health_score': snapshot.get('health_score', 100),
                'active_positions': snapshot.get('active_positions', 0),
                'metadata': json.dumps(snapshot.get('metadata', {}))
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Performance save error: {e}")
            return False
    
    def get_performance_history(self, days: int = 30) -> List[Dict]:
        """Get performance history"""
        if not self.connected:
            return []
        
        try:
            cutoff = datetime.now() - timedelta(days=days)
            result = self.client.table('performance_snapshots')\
                .select('*')\
                .gte('timestamp', cutoff.isoformat())\
                .order('timestamp', desc=False)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Get performance error: {e}")
            return []
    
    # ========== SIGNALS TABLE ==========
    
    def save_signal(self, signal: Dict) -> bool:
        """Save trading signal"""
        if not self.connected:
            return False
        
        try:
            self.client.table('signals').insert({
                'timestamp': signal.get('timestamp', datetime.now().isoformat()),
                'symbol': signal['symbol'],
                'signal_type': signal['signal'],
                'strategy': signal.get('strategy', ''),
                'confidence': signal.get('confidence', 0),
                'price': signal.get('price', 0),
                'indicators': json.dumps(signal.get('indicators', {})),
                'action_taken': signal.get('action_taken', False),
                'metadata': json.dumps(signal.get('metadata', {}))
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Signal save error: {e}")
            return False
    
    # ========== ALERTS TABLE ==========
    
    def save_alert(self, alert: Dict) -> bool:
        """Save alert to history"""
        if not self.connected:
            return False
        
        try:
            self.client.table('alerts').insert({
                'timestamp': alert.get('timestamp', datetime.now().isoformat()),
                'alert_type': alert['type'],
                'priority': alert['priority'],
                'message': alert['message'],
                'channels': json.dumps(alert.get('channels', [])),
                'acknowledged': False
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Alert save error: {e}")
            return False
    
    # ========== ML MODELS TABLE ==========
    
    def save_model_performance(self, model_name: str, metrics: Dict) -> bool:
        """Save ML model performance metrics"""
        if not self.connected:
            return False
        
        try:
            self.client.table('ml_model_performance').insert({
                'model_name': model_name,
                'timestamp': datetime.now().isoformat(),
                'accuracy': metrics.get('accuracy', 0),
                'precision': metrics.get('precision', 0),
                'recall': metrics.get('recall', 0),
                'f1_score': metrics.get('f1_score', 0),
                'predictions': metrics.get('total_predictions', 0),
                'correct': metrics.get('correct_predictions', 0),
                'metadata': json.dumps(metrics.get('metadata', {}))
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Model performance save error: {e}")
            return False
    
    # ========== ANALYTICS ==========
    
    def get_analytics(self, metric: str, timeframe: str = '24h') -> Any:
        """Get aggregated analytics"""
        if not self.connected:
            return None
        
        try:
            # Example: Get win rate over time
            if metric == 'win_rate_trend':
                result = self.client.table('performance_snapshots')\
                    .select('timestamp, win_rate')\
                    .order('timestamp', desc=False)\
                    .execute()
                return result.data
            
            # Add more analytics queries as needed
            
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return None
    
    # ========== FALLBACK (Local Storage) ==========
    
    def _fallback_save(self, table: str, data: Dict) -> Optional[str]:
        """Fallback to local JSON storage"""
        import uuid
        try:
            os.makedirs('data/fallback', exist_ok=True)
            filename = f"data/fallback/{table}_{uuid.uuid4()}.json"
            with open(filename, 'w') as f:
                json.dump(data, f)
            return filename
        except Exception as e:
            logger.error(f"Fallback save error: {e}")
            return None


# Global instance
supabase_client = SupabaseClient()


# Database schema for Supabase (SQL)
SUPABASE_SCHEMA = """
-- TPS19 APEX Organism - Supabase Schema

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    trade_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price DECIMAL(20, 8) NOT NULL,
    exit_price DECIMAL(20, 8),
    size DECIMAL(20, 8) NOT NULL,
    pnl DECIMAL(20, 8) DEFAULT 0,
    pnl_pct DECIMAL(10, 6) DEFAULT 0,
    strategy TEXT,
    entry_time TIMESTAMPTZ NOT NULL,
    exit_time TIMESTAMPTZ,
    status TEXT DEFAULT 'open',
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_entry_time ON trades(entry_time DESC);

-- Performance snapshots
CREATE TABLE IF NOT EXISTS performance_snapshots (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    total_pnl DECIMAL(20, 8) NOT NULL,
    daily_pnl DECIMAL(20, 8) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 4) DEFAULT 0,
    sharpe_ratio DECIMAL(10, 4) DEFAULT 0,
    max_drawdown DECIMAL(5, 4) DEFAULT 0,
    health_score DECIMAL(5, 2) DEFAULT 100,
    active_positions INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_snapshots_timestamp ON performance_snapshots(timestamp DESC);

-- Signals table
CREATE TABLE IF NOT EXISTS signals (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    strategy TEXT,
    confidence DECIMAL(5, 4) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    indicators JSONB,
    action_taken BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signals_symbol ON signals(symbol);
CREATE INDEX idx_signals_timestamp ON signals(timestamp DESC);
CREATE INDEX idx_signals_action ON signals(action_taken);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    alert_type TEXT NOT NULL,
    priority TEXT NOT NULL,
    message TEXT NOT NULL,
    channels JSONB,
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged);

-- ML Model Performance
CREATE TABLE IF NOT EXISTS ml_model_performance (
    id BIGSERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    accuracy DECIMAL(5, 4) DEFAULT 0,
    precision DECIMAL(5, 4) DEFAULT 0,
    recall DECIMAL(5, 4) DEFAULT 0,
    f1_score DECIMAL(5, 4) DEFAULT 0,
    predictions INTEGER DEFAULT 0,
    correct INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ml_model ON ml_model_performance(model_name);
CREATE INDEX idx_ml_timestamp ON ml_model_performance(timestamp DESC);

-- Market Research Cache
CREATE TABLE IF NOT EXISTS market_research (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    research_type TEXT NOT NULL,
    data JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_research_symbol ON market_research(symbol);
CREATE INDEX idx_research_type ON market_research(research_type);
CREATE INDEX idx_research_expires ON market_research(expires_at);
"""
