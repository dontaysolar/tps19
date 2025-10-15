#!/usr/bin/env python3
import os, json, sqlite3, time, random
from datetime import datetime, timedelta
from modules.utils.paths import db_path
class TPS19SimulationEngine:
    def __init__(self, initial_balance=10000.0):
        self.db_path = db_path('simulation.db')
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.portfolio = {}
        self.trade_history = []
        self.simulation_active = False
        self.simulation_id = None
        self.start_time = None
        self._init_database()
    def _init_database(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS simulation_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT UNIQUE NOT NULL, initial_balance REAL NOT NULL, current_balance REAL NOT NULL, start_time DATETIME NOT NULL, end_time DATETIME, status TEXT DEFAULT 'active', total_trades INTEGER DEFAULT 0, total_pnl REAL DEFAULT 0.0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS simulation_trades (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, trade_id TEXT UNIQUE NOT NULL, pair TEXT NOT NULL, side TEXT NOT NULL, amount REAL NOT NULL, price REAL NOT NULL, pnl REAL DEFAULT 0.0, fee REAL DEFAULT 0.0, timestamp DATETIME NOT NULL, status TEXT DEFAULT 'filled')""")
        conn.commit()
        conn.close()
        print("✅ Simulation database initialized")
    def start_simulation(self, session_name=None):
        if not session_name:
            session_name = f"sim_{int(time.time())}"
        self.simulation_id = session_name
        self.simulation_active = True
        self.start_time = datetime.now()
        self.current_balance = self.initial_balance
        self.portfolio = {}
        self.trade_history = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO simulation_sessions (session_id, initial_balance, current_balance, start_time, status) VALUES (?, ?, ?, ?, 'active')""", (self.simulation_id, self.initial_balance, self.current_balance, self.start_time))
        conn.commit()
        conn.close()
        print(f"🎮 Simulation '{session_name}' started with ${self.initial_balance:,.2f}")
        return self.simulation_id
    def simulate_trade(self, pair, side, amount, strategy="manual"):
        if not self.simulation_active:
            return {"error": "No active simulation"}
        current_price = self._get_simulated_price(pair)
        if not current_price:
            return {"error": f"No price data for {pair}"}
        fee_rate = 0.001
        trade_id = f"sim_{int(time.time())}_{len(self.trade_history)}"
        if side.lower() == 'buy':
            cost = amount * current_price
            fee = cost * fee_rate
            total_cost = cost + fee
            if total_cost > self.current_balance:
                return {"error": "Insufficient balance"}
            self.current_balance -= total_cost
            asset = pair.split('_')[0]
            if asset in self.portfolio:
                old_qty = self.portfolio[asset]['quantity']
                old_price = self.portfolio[asset]['avg_price']
                new_qty = old_qty + amount
                new_avg_price = ((old_qty * old_price) + (amount * current_price)) / new_qty
                self.portfolio[asset] = {'quantity': new_qty, 'avg_price': new_avg_price}
            else:
                self.portfolio[asset] = {'quantity': amount, 'avg_price': current_price}
            trade_result = {"trade_id": trade_id, "pair": pair, "side": side, "amount": amount, "price": current_price, "cost": cost, "fee": fee, "total_cost": total_cost, "status": "filled", "timestamp": datetime.now().isoformat()}
        else:
            asset = pair.split('_')[0]
            if asset not in self.portfolio or self.portfolio[asset]['quantity'] < amount:
                return {"error": "Insufficient asset balance"}
            revenue = amount * current_price
            fee = revenue * fee_rate
            net_revenue = revenue - fee
            avg_price = self.portfolio[asset]['avg_price']
            pnl = (current_price - avg_price) * amount - fee
            self.current_balance += net_revenue
            self.portfolio[asset]['quantity'] -= amount
            if self.portfolio[asset]['quantity'] <= 0:
                del self.portfolio[asset]
            trade_result = {"trade_id": trade_id, "pair": pair, "side": side, "amount": amount, "price": current_price, "revenue": revenue, "fee": fee, "net_revenue": net_revenue, "pnl": pnl, "status": "filled", "timestamp": datetime.now().isoformat()}
        self.trade_history.append(trade_result)
        self._store_trade(trade_result)
        print(f"🎮 Simulated {side} {amount} {pair} @ ${current_price:.2f}")
        return trade_result
    def _get_simulated_price(self, pair):
        base_prices = {'BTC_USDT': 45000.0, 'ETH_USDT': 2800.0, 'ADA_USDT': 0.45, 'DOT_USDT': 6.50, 'MATIC_USDT': 0.85, 'SOL_USDT': 95.0, 'AVAX_USDT': 35.0, 'ATOM_USDT': 12.0, 'LINK_USDT': 14.5, 'UNI_USDT': 6.2}
        if pair not in base_prices:
            return None
        base_price = base_prices[pair]
        fluctuation = random.uniform(-0.02, 0.02)
        return round(base_price * (1 + fluctuation), 8)
    def _store_trade(self, trade):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO simulation_trades (session_id, trade_id, pair, side, amount, price, fee, timestamp, status, pnl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.simulation_id, trade['trade_id'], trade['pair'], trade['side'], trade['amount'], trade['price'], trade.get('fee', 0), datetime.now(), 'filled', trade.get('pnl', 0)))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Failed to store trade: {e}")
    def get_portfolio_value(self):
        total_value = self.current_balance
        portfolio_details = {}
        for asset, details in self.portfolio.items():
            current_price = self._get_simulated_price(f"{asset}_USDT")
            if current_price:
                asset_value = details['quantity'] * current_price
                unrealized_pnl = (current_price - details['avg_price']) * details['quantity']
                total_value += asset_value
                portfolio_details[asset] = {'quantity': details['quantity'], 'avg_price': details['avg_price'], 'current_price': current_price, 'value': asset_value, 'unrealized_pnl': unrealized_pnl}
        return {'cash_balance': self.current_balance, 'portfolio_value': total_value - self.current_balance, 'total_value': total_value, 'total_pnl': total_value - self.initial_balance, 'pnl_percentage': ((total_value - self.initial_balance) / self.initial_balance * 100), 'assets': portfolio_details}
    def stop_simulation(self):
        if not self.simulation_active:
            return {"error": "No active simulation"}
        end_time = datetime.now()
        duration = end_time - self.start_time
        total_pnl = self.current_balance - self.initial_balance
        total_trades = len(self.trade_history)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""UPDATE simulation_sessions SET end_time = ?, status = 'completed', current_balance = ?, total_trades = ?, total_pnl = ? WHERE session_id = ?""", (end_time, self.current_balance, total_trades, total_pnl, self.simulation_id))
        conn.commit()
        conn.close()
        results = {"session_id": self.simulation_id, "duration": str(duration), "initial_balance": self.initial_balance, "final_balance": self.current_balance, "total_pnl": total_pnl, "pnl_percentage": (total_pnl / self.initial_balance * 100), "total_trades": total_trades, "portfolio": self.portfolio}
        self.simulation_active = False
        print(f"🏁 Simulation completed: {total_pnl:+.2f} ({total_pnl/self.initial_balance*100:+.1f}%)")
        return results
simulation_engine = TPS19SimulationEngine()
