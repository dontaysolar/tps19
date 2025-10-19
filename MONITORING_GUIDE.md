# 📊 MONITORING & MAINTENANCE GUIDE

**For use after system is running**

---

## 🎯 DAILY MONITORING

### **What to Check Every Day:**

#### **1. System Status**
```bash
# Check if system is running
ps aux | grep apex_v3_integrated.py

# Check logs for errors
tail -f /var/log/apex_v3.log  # If you set up logging
# OR just watch console output
```

#### **2. Trade Performance**
```python
# Run this daily to check performance
python3 -c "
from trade_persistence import PersistenceManager

pm = PersistenceManager()
summary = pm.get_trade_summary()

print('📊 DAILY PERFORMANCE SUMMARY')
print('='*50)
print(f'Total Trades: {summary[\"total_trades\"]}')
print(f'Realized P&L: ${summary[\"realized_pnl\"]:.2f}')
print(f'Win Rate: {summary[\"win_rate\"]:.1f}%')
print(f'Avg P&L: ${summary[\"avg_pnl\"]:.2f}')
print('='*50)
"
```

#### **3. Open Positions**
```python
# Check current positions
python3 -c "
from trade_persistence import PersistenceManager

pm = PersistenceManager()
positions = pm.get_all_positions()

print('📍 OPEN POSITIONS')
print('='*50)
for pos in positions:
    print(f\"{pos['symbol']}: {pos['amount']:.6f} @ ${pos['entry_price']:.2f}\")
    print(f\"  Unrealized P&L: ${pos.get('unrealized_pnl', 0):.2f}\")
print('='*50)
"
```

#### **4. System Health**
```bash
# Run verification
python3 verify_system.py

# Check resource usage
top -p $(pgrep -f apex_v3_integrated.py)
```

---

## 📈 WEEKLY REVIEW

### **Every Week, Review:**

#### **1. Overall Performance**
- Total P&L (profit/loss)
- Win rate percentage
- Average trade size
- Best/worst trades
- Risk metrics

#### **2. Strategy Effectiveness**
```python
# Analyze which strategies are working
python3 -c "
from trade_persistence import PersistenceManager

pm = PersistenceManager()
trades = pm.get_trades()

# Group by strategy if you log that
for trade in trades[-20:]:  # Last 20 trades
    print(f\"{trade.get('timestamp', 'N/A')}: {trade.get('symbol', 'N/A')} - ${trade.get('pnl', 0):.2f}\")
"
```

#### **3. Risk Compliance**
- Are position sizes within limits?
- Are stop losses being hit too often?
- Is daily loss limit being respected?
- Any drawdown concerns?

---

## 🔧 MAINTENANCE TASKS

### **Weekly Tasks:**

#### **1. Backup Data**
```bash
# Backup trade journal and database
mkdir -p backups/$(date +%Y%m%d)
cp data/trades.jsonl backups/$(date +%Y%m%d)/
cp data/positions.db backups/$(date +%Y%m%d)/
```

#### **2. Clean Logs**
```bash
# If logs are getting large
find . -name "*.log" -mtime +7 -delete
```

#### **3. Update Dependencies**
```bash
# Check for updates (carefully!)
pip3 list --outdated

# Update if needed (test first!)
# pip3 install -U ccxt
```

---

### **Monthly Tasks:**

#### **1. Performance Review**
- Calculate monthly return
- Compare to benchmarks (BTC hold, etc.)
- Review worst trades
- Adjust strategy if needed

#### **2. Security Check**
```bash
# Verify credentials still secure
cat .env | grep "YOUR_API_KEY_HERE"
# Should return nothing

# Check .env not in git
git status | grep .env
# Should be untracked
```

#### **3. System Update**
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Python version check
python3 --version
```

---

## 🚨 ALERTS TO WATCH FOR

### **Critical Alerts:**

1. **API Authentication Failed**
   - Action: Check API keys in .env
   - May need to regenerate

2. **Daily Loss Limit Hit**
   - Action: System stops trading (good!)
   - Review what went wrong
   - Don't override limits!

3. **Exchange API Down**
   - Action: Wait for exchange to recover
   - Check exchange status page
   - System will retry automatically

4. **Database Error**
   - Action: Check disk space
   - Backup immediately
   - May need to restore from backup

### **Warning Alerts:**

1. **High Memory Usage**
   - Normal: <500MB
   - Restart if >1GB

2. **Slow Response Times**
   - Check internet connection
   - Check exchange API status
   - May be rate limited

3. **Unusual Signal Patterns**
   - All BUY or all SELL signals
   - May indicate market anomaly
   - Review manually

---

## 📊 KEY METRICS TO TRACK

### **Performance Metrics:**
- **Total P&L** - Overall profit/loss
- **Win Rate** - % of profitable trades
- **Sharpe Ratio** - Risk-adjusted return
- **Max Drawdown** - Largest peak-to-trough decline
- **Average Trade** - Mean profit per trade

### **Risk Metrics:**
- **Position Sizes** - Should be <10% each
- **Daily Loss** - Should be <5%
- **Correlation** - Between positions
- **Volatility** - Market regime

### **System Metrics:**
- **Uptime** - % time system running
- **Errors** - Number of errors per day
- **API Calls** - Should be <100/min
- **Cycle Time** - Should be 5-10s

---

## 🔍 TROUBLESHOOTING COMMON ISSUES

### **Issue: System Stops Responding**
```bash
# Check if process is running
ps aux | grep apex_v3_integrated.py

# Check logs for errors
tail -100 /var/log/apex_v3.log

# Restart system
./start_system.sh
```

### **Issue: No Trades Being Executed**
Check:
1. Is `trading_enabled: True`?
2. Are signals being generated?
3. Are risk checks passing?
4. Is there sufficient balance?

### **Issue: Too Many Trades**
Adjust risk parameters in `risk_management_layer.py`:
- Increase `min_confidence` threshold
- Decrease `max_position_size`
- Add cooldown period between trades

### **Issue: Poor Performance**
Review:
1. Market conditions (are markets trending or choppy?)
2. Strategy settings (may need tuning)
3. Position sizing (too aggressive?)
4. Stop losses (too tight?)

---

## 🎯 OPTIMIZATION TIPS

### **After 1 Month of Data:**

#### **1. Backtest Parameter Changes**
```python
# Use backtesting layer to test changes
from backtesting_layer import BacktestingLayer

bt = BacktestingLayer()
# Run backtest with different parameters
# Compare results before deploying
```

#### **2. Review Strategy Mix**
- Which strategies are most profitable?
- Which strategies have highest win rate?
- Should you adjust weights?

#### **3. Position Sizing Optimization**
- Are positions too small? (leaving money on table)
- Are positions too large? (too much risk)
- Use Kelly Criterion for optimal sizing

---

## 📱 NOTIFICATIONS SETUP

### **Configure Telegram Alerts:**
Edit `apex_v3_integrated.py` to enable notifications for:
- Trade executions
- Daily P&L summary
- Risk limit hits
- System errors

### **Alert Levels:**
- **HIGH** - Critical errors, risk limits
- **NORMAL** - Trade executions, daily summary
- **LOW** - General info, system status

---

## 🔄 CONTINUOUS IMPROVEMENT

### **Monthly Improvement Cycle:**

1. **Analyze** - Review performance data
2. **Identify** - Find areas for improvement
3. **Test** - Backtest proposed changes
4. **Deploy** - Implement if beneficial
5. **Monitor** - Track impact of changes

### **What to Optimize:**
- Strategy parameters (RSI thresholds, etc.)
- Position sizing rules
- Stop loss placement
- Take profit targets
- Trading hours (if relevant)

---

## 📚 USEFUL COMMANDS

```bash
# System Status
python3 verify_system.py

# Run Tests
python3 test_suite.py

# Check Performance
python3 -c "from trade_persistence import PersistenceManager; pm = PersistenceManager(); print(pm.get_trade_summary())"

# View Recent Trades
tail -20 data/trades.jsonl

# Check Positions
python3 -c "from trade_persistence import PersistenceManager; pm = PersistenceManager(); print(pm.get_all_positions())"

# Backup Data
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Restart System
./start_system.sh
```

---

## 🎯 SUCCESS METRICS

### **You're doing well if:**
- ✅ Win rate > 50%
- ✅ Positive P&L over time
- ✅ Drawdown < 20%
- ✅ No daily loss limits hit
- ✅ System uptime > 95%
- ✅ All tests still passing

### **Warning signs:**
- ❌ Win rate < 40%
- ❌ Consistent losses
- ❌ Frequent stop losses
- ❌ System crashes
- ❌ API errors

---

## 🆘 EMERGENCY PROCEDURES

### **If System Goes Wrong:**

1. **STOP TRADING IMMEDIATELY**
   ```bash
   # Kill system
   pkill -f apex_v3_integrated.py
   ```

2. **Close All Positions Manually**
   - Go to exchange website
   - Close positions manually
   - Don't rely on system if it's broken

3. **Review Logs**
   - Find out what went wrong
   - Check trade history
   - Calculate actual P&L

4. **Fix Issues**
   - Run diagnostics
   - Fix bugs if found
   - Test thoroughly before restarting

5. **Restart Carefully**
   - Start in monitoring mode first
   - Watch for 24 hours
   - Enable trading only if stable

---

**Monitor regularly. Adjust carefully. Trade responsibly.**

*Monitoring guide for APEX V3*
