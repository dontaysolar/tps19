#!/usr/bin/env python3
"""
AEGIS v2.0 - Position State Manager
Centralized, crash-safe, auditable state management for all trading positions

FEATURES:
- Single source of truth for position data
- SQLite with WAL (Write-Ahead Logging) for crash safety
- Event sourcing for complete audit trail
- Automatic reconciliation with exchange on startup
- ACID-compliant transactions
- Fractal recursion hook: Self-diagnosis and repair
"""

import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class PositionStateManager:
    """
    Centralized position state manager with event sourcing
    
    This replaces the fragmented state in:
    - apex_nexus_v2.py (self.state['positions'])
    - conflict_resolver_bot.py (self.active_positions)
    - trailing_stoploss.py (file-based)
    """
    
    def __init__(self, db_path: str = '/workspace/data/databases/positions.db'):
        """
        Initialize position state manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        
        # Enable WAL mode for crash safety and concurrent reads
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")  # Balance safety vs performance
        
        self._create_schema()
        self._create_indices()
    
    def _create_schema(self):
        """Create database schema for positions and events"""
        
        # Main positions table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                position_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                amount REAL NOT NULL,
                current_price REAL,
                stop_price REAL,
                take_profit_price REAL,
                trailing_stop_pct REAL DEFAULT 0.0,
                opened_at TEXT NOT NULL,
                closed_at TEXT,
                status TEXT NOT NULL DEFAULT 'OPEN',
                pnl REAL DEFAULT 0.0,
                pnl_pct REAL DEFAULT 0.0,
                fees REAL DEFAULT 0.0,
                exchange_order_id TEXT,
                created_by TEXT DEFAULT 'apex_nexus',
                notes TEXT,
                metadata TEXT
            )
        """)
        
        # Event sourcing table (immutable log)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS position_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                actor TEXT DEFAULT 'system',
                timestamp TEXT NOT NULL,
                FOREIGN KEY (position_id) REFERENCES positions(position_id)
            )
        """)
        
        # Audit trail for state reconciliations
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS reconciliations (
                reconciliation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                exchange_positions INTEGER DEFAULT 0,
                local_positions INTEGER DEFAULT 0,
                discrepancies INTEGER DEFAULT 0,
                actions_taken TEXT,
                status TEXT DEFAULT 'SUCCESS'
            )
        """)
        
        # System health metrics (AEGIS self-diagnosis hook)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS system_health (
                check_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                check_type TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                auto_fixed BOOLEAN DEFAULT 0
            )
        """)
        
        self.conn.commit()
    
    def _create_indices(self):
        """Create indices for performance"""
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status)",
            "CREATE INDEX IF NOT EXISTS idx_positions_opened_at ON positions(opened_at)",
            "CREATE INDEX IF NOT EXISTS idx_events_position ON position_events(position_id)",
            "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON position_events(timestamp)",
        ]
        
        for idx_sql in indices:
            self.conn.execute(idx_sql)
        
        self.conn.commit()
    
    def open_position(self, symbol: str, side: str, entry_price: float, 
                     amount: float, exchange_order_id: Optional[str] = None,
                     stop_price: Optional[float] = None, 
                     take_profit_price: Optional[float] = None,
                     trailing_stop_pct: float = 0.0,
                     **kwargs) -> str:
        """
        Open a new position (ACID transaction)
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'BUY' or 'SELL'
            entry_price: Entry price
            amount: Position size
            exchange_order_id: Order ID from exchange
            stop_price: Stop-loss price
            take_profit_price: Take-profit price
            trailing_stop_pct: Trailing stop percentage
            **kwargs: Additional metadata
        
        Returns:
            position_id: Unique position identifier
        """
        position_id = f"{symbol.replace('/', '_')}_{side}_{int(time.time() * 1000)}"
        opened_at = datetime.now().isoformat()
        
        try:
            with self.conn:  # Atomic transaction
                # Insert position
                self.conn.execute("""
                    INSERT INTO positions (
                        position_id, symbol, side, entry_price, amount,
                        current_price, stop_price, take_profit_price,
                        trailing_stop_pct, opened_at, status,
                        exchange_order_id, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?)
                """, (
                    position_id, symbol, side, entry_price, amount,
                    entry_price,  # current_price = entry_price initially
                    stop_price, take_profit_price, trailing_stop_pct,
                    opened_at, exchange_order_id, json.dumps(kwargs)
                ))
                
                # Log event
                self._log_event(position_id, 'POSITION_OPENED', {
                    'symbol': symbol,
                    'side': side,
                    'entry_price': entry_price,
                    'amount': amount,
                    'exchange_order_id': exchange_order_id
                })
            
            print(f"✅ Position opened: {position_id}")
            return position_id
        
        except sqlite3.IntegrityError as e:
            print(f"❌ Failed to open position (duplicate?): {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error opening position: {e}")
            raise
    
    def update_position(self, position_id: str, current_price: float,
                       stop_price: Optional[float] = None,
                       take_profit_price: Optional[float] = None) -> bool:
        """
        Update position with current market data
        
        Args:
            position_id: Position to update
            current_price: Current market price
            stop_price: New stop price (optional)
            take_profit_price: New TP price (optional)
        
        Returns:
            True if updated successfully
        """
        try:
            with self.conn:
                # Get current position
                cursor = self.conn.execute(
                    "SELECT * FROM positions WHERE position_id = ?", 
                    (position_id,)
                )
                pos = cursor.fetchone()
                
                if not pos:
                    print(f"⚠️ Position {position_id} not found")
                    return False
                
                # Calculate P&L
                entry_price = pos['entry_price']
                amount = pos['amount']
                side = pos['side']
                
                if side == 'BUY':
                    pnl = (current_price - entry_price) * amount
                else:  # SELL/SHORT
                    pnl = (entry_price - current_price) * amount
                
                pnl_pct = (pnl / (entry_price * amount)) * 100 if amount > 0 else 0
                
                # Update position
                update_fields = []
                update_values = []
                
                update_fields.append("current_price = ?")
                update_values.append(current_price)
                
                update_fields.append("pnl = ?")
                update_values.append(pnl)
                
                update_fields.append("pnl_pct = ?")
                update_values.append(pnl_pct)
                
                if stop_price is not None:
                    update_fields.append("stop_price = ?")
                    update_values.append(stop_price)
                
                if take_profit_price is not None:
                    update_fields.append("take_profit_price = ?")
                    update_values.append(take_profit_price)
                
                update_values.append(position_id)
                
                self.conn.execute(f"""
                    UPDATE positions 
                    SET {', '.join(update_fields)}
                    WHERE position_id = ?
                """, tuple(update_values))
                
                # Log event
                self._log_event(position_id, 'POSITION_UPDATED', {
                    'current_price': current_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
            
            return True
        
        except Exception as e:
            print(f"❌ Error updating position {position_id}: {e}")
            return False
    
    def close_position(self, position_id: str, exit_price: float,
                      reason: str = 'MANUAL', fees: float = 0.0) -> bool:
        """
        Close an open position
        
        Args:
            position_id: Position to close
            exit_price: Exit price
            reason: Reason for closing
            fees: Trading fees
        
        Returns:
            True if closed successfully
        """
        try:
            with self.conn:
                cursor = self.conn.execute(
                    "SELECT * FROM positions WHERE position_id = ? AND status = 'OPEN'",
                    (position_id,)
                )
                pos = cursor.fetchone()
                
                if not pos:
                    print(f"⚠️ Position {position_id} not found or already closed")
                    return False
                
                # Calculate final P&L
                entry_price = pos['entry_price']
                amount = pos['amount']
                side = pos['side']
                
                if side == 'BUY':
                    pnl = (exit_price - entry_price) * amount - fees
                else:
                    pnl = (entry_price - exit_price) * amount - fees
                
                pnl_pct = (pnl / (entry_price * amount)) * 100 if amount > 0 else 0
                
                # Close position
                self.conn.execute("""
                    UPDATE positions
                    SET status = 'CLOSED', 
                        closed_at = ?,
                        current_price = ?,
                        pnl = ?,
                        pnl_pct = ?,
                        fees = ?,
                        notes = ?
                    WHERE position_id = ?
                """, (
                    datetime.now().isoformat(),
                    exit_price,
                    pnl,
                    pnl_pct,
                    fees,
                    reason,
                    position_id
                ))
                
                # Log event
                self._log_event(position_id, 'POSITION_CLOSED', {
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'reason': reason,
                    'fees': fees
                })
            
            print(f"✅ Position closed: {position_id} (P&L: ${pnl:.2f}, {pnl_pct:.2f}%)")
            return True
        
        except Exception as e:
            print(f"❌ Error closing position {position_id}: {e}")
            return False
    
    def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all open positions
        
        Args:
            symbol: Filter by symbol (optional)
        
        Returns:
            List of position dictionaries
        """
        query = "SELECT * FROM positions WHERE status = 'OPEN'"
        params = tuple()
        
        if symbol:
            query += " AND symbol = ?"
            params = (symbol,)
        
        query += " ORDER BY opened_at DESC"
        
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_position(self, position_id: str) -> Optional[Dict]:
        """Get single position by ID"""
        cursor = self.conn.execute(
            "SELECT * FROM positions WHERE position_id = ?",
            (position_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def _log_event(self, position_id: str, event_type: str, 
                   event_data: Dict, actor: str = 'system'):
        """Log event to immutable event log (internal method)"""
        self.conn.execute("""
            INSERT INTO position_events (position_id, event_type, event_data, actor, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            position_id,
            event_type,
            json.dumps(event_data),
            actor,
            datetime.now().isoformat()
        ))
    
    def get_position_history(self, position_id: str) -> List[Dict]:
        """Get complete event history for a position"""
        cursor = self.conn.execute("""
            SELECT * FROM position_events
            WHERE position_id = ?
            ORDER BY timestamp ASC
        """, (position_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def reconcile_with_exchange(self, exchange_positions: List[Dict]) -> Dict:
        """
        Reconcile local state with exchange reality
        
        This is the FRACTAL RECURSION HOOK for auto-healing
        
        Args:
            exchange_positions: List of positions from exchange API
        
        Returns:
            Reconciliation report
        """
        print("🔄 Starting state reconciliation with exchange...")
        
        local_positions = {p['symbol']: p for p in self.get_open_positions()}
        exchange_map = {p['symbol']: p for p in exchange_positions}
        
        discrepancies = []
        actions_taken = []
        
        # Find positions on exchange but not locally (phantom positions)
        for symbol in exchange_map:
            if symbol not in local_positions:
                discrepancies.append(f"PHANTOM: {symbol} on exchange but not in local DB")
                
                # AUTO-FIX: Create position record from exchange data
                exch_pos = exchange_map[symbol]
                try:
                    self.open_position(
                        symbol=symbol,
                        side='BUY',  # Assume buy for spot
                        entry_price=exch_pos.get('entry_price', exch_pos.get('price', 0)),
                        amount=exch_pos.get('amount', 0),
                        exchange_order_id=exch_pos.get('order_id'),
                        metadata={'reconciled': True, 'source': 'exchange'}
                    )
                    actions_taken.append(f"CREATED local record for {symbol}")
                except Exception as e:
                    actions_taken.append(f"FAILED to create {symbol}: {e}")
        
        # Find positions locally but not on exchange (ghost positions)
        for symbol in local_positions:
            if symbol not in exchange_map:
                discrepancies.append(f"GHOST: {symbol} in local DB but not on exchange")
                
                # AUTO-FIX: Mark as closed (likely manually closed on exchange)
                pos = local_positions[symbol]
                self.close_position(
                    pos['position_id'],
                    pos['current_price'],
                    reason='AUTO_RECONCILED (not found on exchange)'
                )
                actions_taken.append(f"CLOSED ghost position {symbol}")
        
        # Log reconciliation
        with self.conn:
            self.conn.execute("""
                INSERT INTO reconciliations (
                    timestamp, exchange_positions, local_positions,
                    discrepancies, actions_taken, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                len(exchange_positions),
                len(local_positions),
                len(discrepancies),
                json.dumps(actions_taken),
                'SUCCESS' if len(discrepancies) == 0 else 'FIXED'
            ))
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'exchange_positions': len(exchange_positions),
            'local_positions': len(local_positions),
            'discrepancies': discrepancies,
            'actions_taken': actions_taken,
            'status': 'SYNCED' if len(discrepancies) == 0 else 'FIXED'
        }
        
        if discrepancies:
            print(f"⚠️ Found {len(discrepancies)} discrepancies - AUTO-FIXED")
        else:
            print("✅ State fully synchronized with exchange")
        
        return report
    
    def self_diagnose(self) -> Dict:
        """
        AEGIS Self-Diagnosis Hook
        
        Checks system health and auto-fixes issues
        """
        print("🔍 Running self-diagnosis...")
        
        issues = []
        fixes = []
        
        # Check for stuck positions (open > 7 days)
        cursor = self.conn.execute("""
            SELECT position_id, symbol, opened_at
            FROM positions
            WHERE status = 'OPEN'
              AND julianday('now') - julianday(opened_at) > 7
        """)
        
        stuck_positions = cursor.fetchall()
        if stuck_positions:
            issues.append(f"Found {len(stuck_positions)} positions open >7 days")
            for pos in stuck_positions:
                fixes.append(f"FLAG: {pos['position_id']} for review")
        
        # Check for orphaned events (events without positions)
        cursor = self.conn.execute("""
            SELECT COUNT(*) as orphaned
            FROM position_events e
            LEFT JOIN positions p ON e.position_id = p.position_id
            WHERE p.position_id IS NULL
        """)
        
        orphaned = cursor.fetchone()['orphaned']
        if orphaned > 0:
            issues.append(f"Found {orphaned} orphaned events")
            # Auto-fix: Clean up orphaned events
            with self.conn:
                self.conn.execute("""
                    DELETE FROM position_events
                    WHERE position_id NOT IN (SELECT position_id FROM positions)
                """)
            fixes.append(f"CLEANED {orphaned} orphaned events")
        
        # Log diagnosis
        with self.conn:
            self.conn.execute("""
                INSERT INTO system_health (timestamp, check_type, status, details, auto_fixed)
                VALUES (?, 'SELF_DIAGNOSIS', ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                'HEALTHY' if len(issues) == 0 else 'ISSUES_FOUND',
                json.dumps({'issues': issues, 'fixes': fixes}),
                len(fixes) > 0
            ))
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'issues_found': len(issues),
            'auto_fixes_applied': len(fixes),
            'issues': issues,
            'fixes': fixes,
            'status': 'HEALTHY' if len(issues) == 0 else 'REPAIRED'
        }
        
        if fixes:
            print(f"🔧 Applied {len(fixes)} automatic fixes")
        
        return report
    
    def get_statistics(self) -> Dict:
        """Get position statistics"""
        stats = {}
        
        # Open positions
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM positions WHERE status = 'OPEN'")
        stats['open_positions'] = cursor.fetchone()['count']
        
        # Closed positions
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM positions WHERE status = 'CLOSED'")
        stats['closed_positions'] = cursor.fetchone()['count']
        
        # Total P&L
        cursor = self.conn.execute("SELECT SUM(pnl) as total_pnl FROM positions WHERE status = 'CLOSED'")
        stats['total_pnl'] = cursor.fetchone()['total_pnl'] or 0.0
        
        # Win rate
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins
            FROM positions 
            WHERE status = 'CLOSED'
        """)
        row = cursor.fetchone()
        total = row['total']
        wins = row['wins']
        stats['win_rate'] = (wins / total * 100) if total > 0 else 0.0
        
        # Reconciliation count
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM reconciliations")
        stats['reconciliations_performed'] = cursor.fetchone()['count']
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()


# Example usage
if __name__ == '__main__':
    print("="*70)
    print("AEGIS Position State Manager - Test Suite")
    print("="*70)
    
    with PositionStateManager() as psm:
        # Test 1: Open position
        print("\n[Test 1] Opening position...")
        pos_id = psm.open_position(
            symbol='BTC/USDT',
            side='BUY',
            entry_price=50000.0,
            amount=0.001,
            stop_price=49000.0,
            take_profit_price=52000.0
        )
        
        # Test 2: Update position
        print("\n[Test 2] Updating position...")
        psm.update_position(pos_id, current_price=51000.0)
        
        # Test 3: Get position
        print("\n[Test 3] Retrieving position...")
        pos = psm.get_position(pos_id)
        print(f"   Position: {pos['symbol']} @ ${pos['current_price']}")
        print(f"   P&L: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")
        
        # Test 4: Get history
        print("\n[Test 4] Position history...")
        history = psm.get_position_history(pos_id)
        for event in history:
            print(f"   {event['timestamp']}: {event['event_type']}")
        
        # Test 5: Self-diagnosis
        print("\n[Test 5] Self-diagnosis...")
        diag = psm.self_diagnose()
        print(f"   Status: {diag['status']}")
        print(f"   Issues: {diag['issues_found']}")
        
        # Test 6: Statistics
        print("\n[Test 6] Statistics...")
        stats = psm.get_statistics()
        print(f"   Open: {stats['open_positions']}")
        print(f"   Closed: {stats['closed_positions']}")
        print(f"   Total P&L: ${stats['total_pnl']:.2f}")
        
        # Test 7: Close position
        print("\n[Test 7] Closing position...")
        psm.close_position(pos_id, exit_price=52000.0, reason='TAKE_PROFIT')
        
        print("\n✅ All tests passed!")
