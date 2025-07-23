#!/bin/bash
cd /opt/tps19
python3 -c "
import sys
sys.path.append('/opt/tps19')
from modules.simulation.simulation_engine import simulation_engine

def show_simulation_menu():
    print('🎮 TPS19 SIMULATION MODE')
    print('═══════════════════════════')
    print()
    if simulation_engine.simulation_active:
        portfolio = simulation_engine.get_portfolio_value()
        print(f'📊 Active Simulation: {simulation_engine.simulation_id}')
        print(f'💰 Total Value: \${portfolio[\"total_value\"]:,.2f}')
        print(f'📈 P&L: \${portfolio[\"total_pnl\"]:+,.2f} ({portfolio[\"pnl_percentage\"]:+.1f}%)')
        print(f'🔄 Trades: {len(simulation_engine.trade_history)}')
        print()
        print('1. 📈 Simulate Buy Trade')
        print('2. 📉 Simulate Sell Trade')
        print('3. 📊 View Portfolio')
        print('4. 🏁 Stop Simulation')
        print('0. 🔙 Back')
    else:
        print('No active simulation')
        print()
        print('1. 🎮 Start New Simulation')
        print('0. 🔙 Back')
    
    choice = input('🎯 Select option: ').strip()
    return choice

def handle_choice(choice):
    if not simulation_engine.simulation_active and choice == '1':
        balance = input('💰 Initial balance (default \$10,000): ').strip()
        try:
            balance = float(balance) if balance else 10000.0
        except:
            balance = 10000.0
        simulation_engine.initial_balance = balance
        session_id = simulation_engine.start_simulation()
        print(f'✅ Simulation started: {session_id}')
    elif simulation_engine.simulation_active:
        if choice == '1':
            pair = input('Trading pair (e.g., BTC_USDT): ').strip().upper()
            amount = input('Amount to buy: ').strip()
            try:
                amount = float(amount)
                result = simulation_engine.simulate_trade(pair, 'buy', amount)
                if 'error' in result:
                    print(f'❌ {result[\"error\"]}')
                else:
                    print(f'✅ Buy executed: {amount} {pair} @ \${result[\"price\"]:.2f}')
            except:
                print('❌ Invalid amount')
        elif choice == '2':
            pair = input('Trading pair (e.g., BTC_USDT): ').strip().upper()
            amount = input('Amount to sell: ').strip()
            try:
                amount = float(amount)
                result = simulation_engine.simulate_trade(pair, 'sell', amount)
                if 'error' in result:
                    print(f'❌ {result[\"error\"]}')
                else:
                    print(f'✅ Sell executed: {amount} {pair} @ \${result[\"price\"]:.2f}')
            except:
                print('❌ Invalid amount')
        elif choice == '3':
            portfolio = simulation_engine.get_portfolio_value()
            print('📊 Current Portfolio:')
            print(f'💰 Cash: \${portfolio[\"cash_balance\"]:,.2f}')
            print(f'📈 Assets Value: \${portfolio[\"portfolio_value\"]:,.2f}')
            print(f'💎 Total Value: \${portfolio[\"total_value\"]:,.2f}')
            print(f'📊 P&L: \${portfolio[\"total_pnl\"]:+,.2f} ({portfolio[\"pnl_percentage\"]:+.1f}%)')
            print()
            for asset, details in portfolio['assets'].items():
                print(f'{asset}: {details[\"quantity\"]:.4f} @ \${details[\"current_price\"]:.2f} (P&L: \${details[\"unrealized_pnl\"]:+.2f})')
        elif choice == '4':
            results = simulation_engine.stop_simulation()
            print('📊 Final Results:')
            print(f'💰 Final Balance: \${results[\"final_balance\"]:,.2f}')
            print(f'📈 Total P&L: \${results[\"total_pnl\"]:+,.2f} ({results[\"pnl_percentage\"]:+.1f}%)')
            print(f'🔄 Total Trades: {results[\"total_trades\"]}')
    
    if choice != '0':
        input('Press Enter to continue...')

while True:
    choice = show_simulation_menu()
    if choice == '0':
        break
    handle_choice(choice)
"
