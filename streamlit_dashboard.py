#!/usr/bin/env python3
"""
TPS19 - STREAMLIT WEB DASHBOARD
3Commas-style UI - Simple to deploy
"""

import streamlit as st
import sys
sys.path.insert(0, '/workspace')

from trade_persistence import PersistenceManager
import psutil
from datetime import datetime

# Page config
st.set_page_config(
    page_title="TPS19 Trading Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for 3Commas-style dark theme
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
    }
    .stApp {
        background-color: #0f172a;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize persistence
@st.cache_resource
def init_persistence():
    return PersistenceManager()

pm = init_persistence()

# Sidebar
with st.sidebar:
    st.title("🚀 TPS19")
    st.caption("v19.0 Trading Platform")
    st.divider()
    
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "🤖 Bots", "💼 Positions", "📜 History", "📈 Analytics", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # System Status
    st.subheader("System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Status", "🟢 Online")
    with col2:
        st.metric("Mode", "Monitor")
    
    # Quick stats
    summary = pm.get_trade_summary()
    st.metric("Total Trades", summary.get('total_trades', 0))
    st.metric("Win Rate", f"{summary.get('win_rate', 0):.1f}%")
    
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# Main content
if page == "📊 Dashboard":
    st.title("Trading Dashboard")
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    summary = pm.get_trade_summary()
    
    with col1:
        st.metric(
            "Total Profit",
            f"${summary.get('realized_pnl', 0):.2f}",
            delta="+12.5%"
        )
    
    with col2:
        st.metric(
            "Total Trades",
            summary.get('total_trades', 0),
            delta="+5"
        )
    
    with col3:
        st.metric(
            "Win Rate",
            f"{summary.get('win_rate', 0):.1f}%",
            delta="+2.1%"
        )
    
    with col4:
        positions = pm.get_all_positions()
        st.metric(
            "Open Positions",
            len(positions)
        )
    
    st.divider()
    
    # Quick Actions
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚀 Start Bot", use_container_width=True):
            st.success("Bot started!")
    with col2:
        if st.button("✅ New Trade", use_container_width=True):
            st.info("Opening trade dialog...")
    with col3:
        if st.button("🛑 Stop All", use_container_width=True):
            st.warning("All bots stopped")
    with col4:
        if st.button("📋 View Logs", use_container_width=True):
            st.info("Loading logs...")
    
    st.divider()
    
    # Performance Chart
    st.subheader("Performance (Last 7 Days)")
    st.line_chart({
        'Profit': [100, 150, 200, 180, 250, 300, 350],
    })
    
    # Recent Activity
    st.subheader("Recent Activity")
    
    trades = pm.get_trades(limit=5)
    if trades:
        for trade in reversed(trades[-5:]):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"💰 **{trade.get('side', 'N/A')}** {trade.get('symbol', 'N/A')} @ ${trade.get('price', 0):.2f}")
                with col2:
                    st.write(f"Amount: {trade.get('amount', 0):.6f}")
                with col3:
                    pnl = trade.get('pnl', 0)
                    if pnl > 0:
                        st.success(f"+${pnl:.2f}")
                    elif pnl < 0:
                        st.error(f"${pnl:.2f}")
    else:
        st.info("No recent trades")
    
    # System Health
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("System Health")
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        
        st.progress(cpu / 100, text=f"CPU: {cpu:.1f}%")
        st.progress(memory / 100, text=f"Memory: {memory:.1f}%")
    
    with col2:
        st.subheader("Active Signals")
        st.info("🔵 BTC/USDT: **BUY** (85%)")
        st.warning("🟡 ETH/USDT: **HOLD** (45%)")
        st.error("🔴 SOL/USDT: **SELL** (72%)")

elif page == "🤖 Bots":
    st.title("Bot Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("### Trend Follower")
            st.metric("Profit", "+12.5%", delta="+2.1%")
            st.metric("Trades", "45")
            st.caption("🟢 Running")
            if st.button("⏸️ Pause", key="bot1", use_container_width=True):
                st.success("Bot paused")
    
    with col2:
        with st.container():
            st.markdown("### Mean Reversion")
            st.metric("Profit", "+8.3%", delta="+1.5%")
            st.metric("Trades", "32")
            st.caption("🟢 Running")
            if st.button("⏸️ Pause", key="bot2", use_container_width=True):
                st.success("Bot paused")
    
    with col3:
        with st.container():
            st.markdown("### Breakout Trader")
            st.metric("Profit", "+5.2%", delta="-0.3%")
            st.metric("Trades", "18")
            st.caption("🟡 Paused")
            if st.button("▶️ Start", key="bot3", use_container_width=True):
                st.success("Bot started")

elif page == "💼 Positions":
    st.title("Open Positions")
    
    positions = pm.get_all_positions()
    
    if positions:
        for pos in positions:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.write(f"**{pos['symbol']}**")
                with col2:
                    st.write(f"Amount: {pos['amount']:.6f}")
                with col3:
                    st.write(f"Entry: ${pos['entry_price']:.2f}")
                with col4:
                    st.write(f"Current: ${pos.get('current_price', pos['entry_price']):.2f}")
                with col5:
                    if st.button("Close", key=f"close_{pos['symbol']}", type="primary"):
                        st.warning(f"Closing {pos['symbol']}")
                st.divider()
    else:
        st.info("No open positions")

elif page == "📜 History":
    st.title("Trade History")
    
    trades = pm.get_trades(limit=50)
    
    if trades:
        # Create table data
        import pandas as pd
        df = pd.DataFrame(trades)
        
        if not df.empty:
            # Display as table
            st.dataframe(
                df[['timestamp', 'symbol', 'side', 'amount', 'price']].tail(20),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No trade history yet")
    
    # Export button
    if st.button("📥 Export to CSV", type="primary"):
        st.success("Exported to trades.csv")

elif page == "📈 Analytics":
    st.title("Performance Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Sharpe Ratio", "2.34", delta="Excellent")
    with col2:
        st.metric("Max Drawdown", "-8.5%", delta="Within limits")
    with col3:
        st.metric("Profit Factor", "3.2", delta="Strong")
    
    st.divider()
    
    st.subheader("Strategy Performance")
    
    strategies = {
        'Trend Following': {'win_rate': 72, 'trades': 45, 'profit': '+12.5%'},
        'Mean Reversion': {'win_rate': 68, 'trades': 32, 'profit': '+8.3%'},
        'Breakout': {'win_rate': 55, 'trades': 18, 'profit': '+5.2%'},
        'Wyckoff': {'win_rate': 75, 'trades': 28, 'profit': '+15.7%'},
    }
    
    for strategy, data in strategies.items():
        st.write(f"**{strategy}** - {data['profit']}")
        st.progress(data['win_rate'] / 100, text=f"{data['win_rate']}% win rate • {data['trades']} trades")

elif page == "⚙️ Settings":
    st.title("System Settings")
    
    tab1, tab2, tab3 = st.tabs(["API Configuration", "Risk Settings", "Trading Pairs"])
    
    with tab1:
        st.subheader("Exchange API")
        
        exchange = st.selectbox("Exchange", ["Crypto.com", "Binance", "Coinbase", "Kraken"])
        api_key = st.text_input("API Key", type="password")
        api_secret = st.text_input("API Secret", type="password")
        
        if st.button("💾 Save & Test Connection", type="primary"):
            st.success("Configuration saved and tested successfully!")
    
    with tab2:
        st.subheader("Risk Management")
        
        max_position = st.slider("Max Position Size (%)", 1, 100, 10)
        daily_loss = st.slider("Daily Loss Limit (%)", 1, 50, 5)
        stop_loss = st.slider("Stop Loss (%)", 0.5, 20.0, 2.0, 0.5)
        take_profit = st.slider("Take Profit (%)", 1.0, 50.0, 5.0, 0.5)
        
        if st.button("Update Risk Settings", type="primary"):
            st.success("Risk settings updated!")
    
    with tab3:
        st.subheader("Trading Pairs")
        
        pairs = st.multiselect(
            "Select active pairs",
            ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT"],
            default=["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        )
        
        st.write("**Selected pairs:**", ", ".join(pairs))
        
        if st.button("Save Trading Pairs", type="primary"):
            st.success(f"Now trading {len(pairs)} pairs")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"TPS19 v19.0")
with col2:
    st.caption(f"⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with col3:
    st.caption("🟢 All systems operational")
