# 🚀 QUICK START GUIDE

**Get APEX V3 running in 5 minutes**

---

## ⚠️ PREREQUISITES

Before you start, you MUST have rotated your API credentials.

**If you haven't done this yet:**
👉 **READ:** `USER_ACTION_REQUIRED.md` **FIRST**

---

## 🏃 QUICK START

### **Option 1: Automated Quick Start**

```bash
cd /workspace
./quick_start.sh
```

This will:
1. ✅ Check credentials
2. ✅ Install dependencies
3. ✅ Run tests
4. ✅ Start system

---

### **Option 2: Manual Step-by-Step**

#### **Step 1: Verify System**
```bash
python3 verify_system.py
```

Should show:
```
✅ SYSTEM READY
```

#### **Step 2: Run Tests**
```bash
python3 test_suite.py
```

Should show:
```
✅ Passed: 47
❌ Failed: 0
```

#### **Step 3: Start System**
```bash
./start_system.sh
```

Or manually:
```bash
python3 apex_v3_integrated.py
```

---

## 🎯 WHAT TO EXPECT

When you start the system:

```
================================================================================
🚀 APEX V3 - FULLY INTEGRATED SYSTEM
================================================================================

📦 Initializing Infrastructure...
🔗 Connecting to exchange...
🔍 Initializing Market Analysis Layer...
🎯 Initializing Signal Generation Layer...
🤖 Initializing AI/ML Layer...
🛡️ Initializing Risk Management Layer...
⚡ Initializing Execution Layer...
💭 Initializing Sentiment Analysis Layer...
⛓️ Initializing On-Chain Analysis Layer...
💼 Initializing Portfolio Management Layer...
📊 Initializing Backtesting Layer...

================================================================================
✅ APEX V3 INITIALIZED - ALL 10 LAYERS ACTIVE
   Trading: MONITORING ONLY
   Pairs: 3
   AI/ML: ENABLED
   Layers: 10
================================================================================

🔄 Starting main loop...

================================================================================
CYCLE #1 - 19:30:45
================================================================================

📊 BTC/USDT:
   Price: $50000.00
   Signal: HOLD (50%)
   Trend: UPTREND
   RSI: 55.5
   Vol: MEDIUM

📊 ETH/USDT:
   Price: $3000.00
   Signal: BUY (72%)
   Trend: UPTREND
   RSI: 45.2
   Vol: MEDIUM

✅ Cycle complete
```

---

## 🛡️ SAFETY FEATURES

### **Trading is DISABLED by default**
- System runs in monitoring mode
- Generates signals but doesn't trade
- Safe to run and observe

### **To Enable Trading:**
1. Monitor for 24-48 hours first
2. Edit `apex_v3_integrated.py`
3. Find: `'trading_enabled': False`
4. Change to: `'trading_enabled': True`
5. **Start with small amounts** ($50-100 max)

---

## 📊 MONITORING

### **View Logs:**
```bash
# System logs to console
# Watch for errors or warnings
```

### **Check Trades:**
```bash
# View trade journal
cat data/trades.jsonl

# View positions
sqlite3 data/positions.db "SELECT * FROM positions;"
```

### **Check Performance:**
```bash
python3 -c "
from trade_persistence import PersistenceManager
pm = PersistenceManager()
print(pm.get_trade_summary())
"
```

---

## 🔧 TROUBLESHOOTING

### **"Module not found" errors:**
```bash
pip3 install -r requirements.txt
```

### **"API authentication failed":**
- Check your `.env` file
- Verify API keys are correct
- Make sure you rotated old credentials

### **"No data" or "Insufficient data":**
- Normal on first run
- System needs ~60 candles (1 hour of data)
- Wait a few minutes and it will start working

### **System crashes:**
```bash
# Check logs for errors
# Verify credentials in .env
# Run verification again
python3 verify_system.py
```

---

## 📈 NEXT STEPS

### **After System is Running:**

1. **Monitor for 24-48 hours**
   - Watch signals
   - Check if analysis makes sense
   - Verify no errors

2. **Review Performance**
   - Check logs
   - Review generated signals
   - Validate risk checks

3. **Enable Trading (Optional)**
   - Only if monitoring looks good
   - Start with $50-100 max
   - Monitor closely

4. **Scale Up (Carefully)**
   - After 1-2 weeks of successful small trades
   - Gradually increase position sizes
   - Never risk more than you can afford to lose

---

## 🆘 NEED HELP?

### **Check These First:**
1. `USER_ACTION_REQUIRED.md` - Credential setup
2. `THREAT_REMEDIATION_COMPLETE.md` - What was fixed
3. `CREDENTIAL_EXPOSURE_NOTICE.md` - Security info
4. `REMEDIATION_SUMMARY.txt` - Quick overview

### **Common Commands:**
```bash
# Verify system
python3 verify_system.py

# Run tests
python3 test_suite.py

# Start system
./start_system.sh

# Stop system
Ctrl+C

# Check persistence
python3 trade_persistence.py
```

---

## ✅ CHECKLIST

Before you start:
- [ ] API credentials rotated
- [ ] `.env` file updated
- [ ] Dependencies installed
- [ ] Tests passing (47/47)
- [ ] Verification passed

Ready to run:
- [ ] Start with `./quick_start.sh` or `./start_system.sh`
- [ ] Monitor output for errors
- [ ] Trading is disabled (safe mode)
- [ ] Let it run for 24-48 hours
- [ ] Review signals and performance

---

**That's it! System is ready to run.**

**Start with:** `./quick_start.sh`
