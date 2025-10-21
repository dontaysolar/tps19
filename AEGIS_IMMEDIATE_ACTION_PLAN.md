# 🔴 AEGIS v2.0 - IMMEDIATE ACTION PLAN
## CRITICAL SECURITY REMEDIATION PROTOCOL

**Generated**: 2025-10-20  
**Priority**: 🔴 CODE RED - STOP ALL TRADING OPERATIONS  
**Estimated Time**: 2-4 hours for critical items  

---

## ⚠️ BEFORE YOU BEGIN

**READ THIS FIRST**:

Your TPS19/APEX trading system has **CRITICAL SECURITY VULNERABILITIES** that expose live trading credentials. Anyone with access to your git repository can:
- Execute trades on your behalf
- Withdraw your funds
- Impersonate your Telegram bot
- Monitor your trading strategies

**Status**: The system is NOT currently running (verified), but credentials are exposed.

---

## 🔴 PHASE 1: IMMEDIATE CREDENTIAL ROTATION (DO THIS NOW)

### Step 1.1: Rotate Crypto.com API Keys
**Time**: 5 minutes  
**Instructions**:
1. Log into Crypto.com exchange
2. Navigate to API Management
3. **DELETE** the current API key (starts with A8Ymbn...)
4. Generate NEW API key with minimal permissions:
   - ✅ Read account balance
   - ✅ Read order history
   - ✅ Place spot orders
   - ❌ Withdrawals (DISABLED)
   - ❌ Futures trading (DISABLED unless needed)
5. Save the new credentials securely (password manager)

**Why This Matters**: The old credentials are in git history and potentially compromised.

---

### Step 1.2: Rotate Telegram Bot Token
**Time**: 5 minutes  
**Instructions**:
1. Open Telegram and message @BotFather
2. Send `/mybots`
3. Select your trading bot
4. Select "API Token"
5. Select "Revoke current token"
6. Copy the NEW token
7. Update your secure storage

**Why This Matters**: The old token (7289126201:AAH...) is hardcoded in source files.

---

### Step 1.3: Update .env File (DO NOT COMMIT)
**Time**: 2 minutes  
**Instructions**:
```bash
# Navigate to workspace
cd /workspace

# Backup old .env (for reference only)
cp .env .env.OLD_INSECURE

# Edit .env with your NEW credentials
nano .env
# OR
vim .env

# Replace these lines with your NEW values:
EXCHANGE_API_KEY=<your_new_key>
EXCHANGE_API_SECRET=<your_new_secret>
TELEGRAM_BOT_TOKEN=<your_new_token>

# Save and exit
```

**CRITICAL**: Do NOT commit this file to git!

---

## 🔴 PHASE 2: GIT HISTORY CLEANUP (PURGE OLD CREDENTIALS)

### Step 2.1: Remove .env from Git History
**Time**: 10 minutes  
**Danger Level**: HIGH (requires force push)  
**Instructions**:

```bash
cd /workspace

# Create backup branch (safety net)
git branch backup-before-cleanup

# Remove .env from entire git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Verify .env is gone from history
git log --all --full-history -- .env
# Should show: "not found"

# Clean up refs
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (THIS WILL REWRITE HISTORY)
# WARNING: Coordinate with team first!
git push origin --force --all
git push origin --force --tags
```

**⚠️ WARNING**: This rewrites git history. If others have cloned the repo, they'll need to re-clone.

**Alternative (if force-push is not possible)**:
- Treat the repository as compromised
- Create a NEW repository
- Copy code (without .env) to new repo
- Update all remotes to point to new repo

---

### Step 2.2: Add .gitignore
**Time**: 1 minute  
**Status**: ✅ Already created by AEGIS  
**Instructions**:
```bash
# Verify .gitignore exists
cat /workspace/.gitignore

# Add to git
git add .gitignore
git commit -m "security: Add comprehensive .gitignore"
```

---

### Step 2.3: Verify .env is Ignored
**Time**: 1 minute  
**Instructions**:
```bash
# This command should show NOTHING
git status | grep ".env"

# Try to add .env (should fail)
git add .env
# Expected: "The following paths are ignored by one of your .gitignore files"
```

---

## 🔴 PHASE 3: REMOVE HARDCODED CREDENTIALS FROM SOURCE

### Step 3.1: Fix telegram_controller.py
**Time**: 2 minutes  
**Instructions**:

```bash
# Open file
nano /workspace/telegram_controller.py

# Find line 19-20 (currently):
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7289126201:AAH...')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '7517400013')

# Replace with:
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Add validation after line 20:
if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

# Save and exit
```

**Or use AEGIS automated fix** (see Phase 4 below).

---

### Step 3.2: Fix enhanced_notifications.py
**Time**: 2 minutes  
**Instructions**:

```bash
# Open file
nano /workspace/enhanced_notifications.py

# Find line 16-17 (currently):
self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '7289126201:AAH...')
self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '7517400013')

# Replace with:
self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

# Add validation in __init__:
if not self.bot_token or not self.chat_id:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

# Save and exit
```

---

### Step 3.3: Commit Security Fixes
**Time**: 1 minute  
**Instructions**:
```bash
git add telegram_controller.py enhanced_notifications.py
git commit -m "security: Remove hardcoded credentials from source files"
git push origin cursor/initiate-aegis-v2-0-singularity-drive-e07b
```

---

## 🟠 PHASE 4: IMPLEMENT SECURE ENVIRONMENT LOADING

### Step 4.1: Fix apex_nexus_v2.py Custom Parser
**Time**: 5 minutes  
**Current Risk**: Custom .env parser is vulnerable  
**Instructions**:

```bash
nano /workspace/apex_nexus_v2.py

# Find lines 11-15 (custom parser):
with open('.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k,v = line.strip().split('=',1)
            os.environ[k] = v

# Replace with:
from dotenv import load_dotenv
load_dotenv()  # Secure, standard library

# Remove lines 11-15
# Add: import dotenv at top of file (line 7)

# Save and exit
```

---

### Step 4.2: Validate Environment Variables
**Time**: 10 minutes  
**Instructions**:

Create `/workspace/utils/env_validator.py`:

```python
#!/usr/bin/env python3
"""Environment Variable Validator - AEGIS Security Protocol"""

import os
import sys
from typing import List, Dict

class EnvValidator:
    """Validates required environment variables are set and secure"""
    
    REQUIRED_VARS = [
        'EXCHANGE_API_KEY',
        'EXCHANGE_API_SECRET',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'LIVE_MODE',
        'INITIAL_BALANCE',
        'MAX_POSITION_SIZE'
    ]
    
    OPTIONAL_VARS = [
        'REDIS_HOST',
        'REDIS_PORT',
        'GOOGLE_SHEETS_ID'
    ]
    
    @staticmethod
    def validate() -> Dict[str, any]:
        """Validate all environment variables"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required variables
        for var in EnvValidator.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                results['valid'] = False
                results['errors'].append(f"Missing required variable: {var}")
            elif value in ['your_key_here', 'placeholder', 'CHANGE_ME']:
                results['valid'] = False
                results['errors'].append(f"{var} is set to placeholder value")
        
        # Validate LIVE_MODE
        live_mode = os.getenv('LIVE_MODE', 'False').lower()
        if live_mode not in ['true', 'false']:
            results['valid'] = False
            results['errors'].append("LIVE_MODE must be 'True' or 'False'")
        
        # Security checks
        api_key = os.getenv('EXCHANGE_API_KEY', '')
        if len(api_key) < 10:
            results['warnings'].append("EXCHANGE_API_KEY seems too short")
        
        return results

def main():
    print("🔍 AEGIS Environment Validation")
    print("=" * 60)
    
    results = EnvValidator.validate()
    
    if results['errors']:
        print("\n❌ ERRORS:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if results['warnings']:
        print("\n⚠️  WARNINGS:")
        for warning in results['warnings']:
            print(f"  - {warning}")
    
    if results['valid'] and not results['warnings']:
        print("\n✅ All environment variables are valid!")
        return 0
    elif results['valid']:
        print("\n⚠️  Environment is valid but has warnings")
        return 0
    else:
        print("\n❌ Environment validation FAILED")
        print("   Fix errors before running the trading system")
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

**Run validation**:
```bash
python3 /workspace/utils/env_validator.py
```

---

## 🟠 PHASE 5: IMPLEMENT EMERGENCY STOP MECHANISM

### Step 5.1: Add Emergency Stop Command
**Time**: 10 minutes  
**Purpose**: Ability to instantly halt all trading  
**Instructions**:

Add to `/workspace/telegram_controller.py`:

```python
def handle_emergency_stop(self, message):
    """EMERGENCY: Stop all trading immediately"""
    print("🚨 EMERGENCY STOP INITIATED")
    
    # Close all positions
    try:
        import apex_nexus_v2
        nexus = apex_nexus_v2.APEXNexusV2()
        
        for pair, position in nexus.state.get('positions', {}).items():
            try:
                # Market sell to close
                order = nexus.exchange.create_market_sell_order(
                    pair, 
                    position['amount']
                )
                print(f"✅ Closed {pair}: {order}")
            except Exception as e:
                print(f"❌ Failed to close {pair}: {e}")
        
        # Halt system
        nexus.state['trading_enabled'] = False
        
        self.send_message("🚨 EMERGENCY STOP COMPLETE\n\nAll positions closed\nTrading HALTED")
        
    except Exception as e:
        self.send_message(f"❌ EMERGENCY STOP FAILED: {str(e)}")
```

**Register command**:
```python
# In TelegramController.__init__, add:
self.commands = {
    '/start': self.handle_start,
    '/status': self.handle_status,
    '/emergency_stop': self.handle_emergency_stop,  # NEW
    # ... other commands
}
```

---

## 🟡 PHASE 6: IMMEDIATE MONITORING & ALERTING

### Step 6.1: Set Up Daily Security Checks
**Time**: 5 minutes  
**Instructions**:

Create `/workspace/scripts/daily_security_check.sh`:

```bash
#!/bin/bash
# AEGIS Daily Security Check
# Run this every day (set up cron job)

echo "🔍 AEGIS Daily Security Check"
echo "=============================="

# Check if .env is in git
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "❌ CRITICAL: .env is tracked in git!"
    exit 1
else
    echo "✅ .env is not tracked"
fi

# Check for hardcoded secrets
if grep -r "TELEGRAM_BOT_TOKEN.*=" --include="*.py" . | grep -v "os.getenv" | grep -v ".example"; then
    echo "❌ WARNING: Found hardcoded tokens!"
    exit 1
else
    echo "✅ No hardcoded tokens found"
fi

# Validate environment
python3 /workspace/utils/env_validator.py
if [ $? -ne 0 ]; then
    echo "❌ Environment validation failed"
    exit 1
fi

echo ""
echo "✅ All security checks passed!"
```

**Make executable**:
```bash
chmod +x /workspace/scripts/daily_security_check.sh
```

**Set up cron (optional)**:
```bash
crontab -e
# Add: 0 9 * * * /workspace/scripts/daily_security_check.sh
```

---

## 📊 PHASE 7: VERIFICATION & TESTING

### Step 7.1: Run Security Checklist
**Time**: 5 minutes  
**Instructions**:

```bash
cd /workspace

echo "Running AEGIS Security Verification..."
echo ""

# 1. Check .gitignore exists
if [ -f ".gitignore" ]; then
    echo "✅ .gitignore exists"
else
    echo "❌ .gitignore missing"
fi

# 2. Verify .env is not in git
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "❌ .env is tracked in git (BAD!)"
else
    echo "✅ .env is not tracked"
fi

# 3. Check for hardcoded credentials
echo "Checking for hardcoded credentials..."
grep -r "7289126201" --include="*.py" . 2>/dev/null
if [ $? -eq 0 ]; then
    echo "❌ Found hardcoded Telegram token!"
else
    echo "✅ No hardcoded tokens found"
fi

# 4. Validate environment
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
required = ['EXCHANGE_API_KEY', 'TELEGRAM_BOT_TOKEN', 'LIVE_MODE']
missing = [v for v in required if not os.getenv(v)]
if missing:
    print(f'❌ Missing: {missing}')
    exit(1)
else:
    print('✅ All required env vars present')
"

echo ""
echo "Security verification complete!"
```

---

### Step 7.2: Test System Startup (DRY RUN)
**Time**: 5 minutes  
**Instructions**:

```bash
# Set to simulation mode first
sed -i 's/LIVE_MODE=True/LIVE_MODE=False/' /workspace/.env

# Test startup
python3 /workspace/apex_nexus_v2.py &
APEX_PID=$!

# Wait 10 seconds
sleep 10

# Check if running
if ps -p $APEX_PID > /dev/null; then
    echo "✅ System started successfully"
    kill $APEX_PID
else
    echo "❌ System failed to start"
fi
```

---

## 📋 COMPLETION CHECKLIST

Before resuming trading, verify ALL items are complete:

### Critical Items (Must Complete)
- [ ] Rotated Crypto.com API keys
- [ ] Rotated Telegram bot token
- [ ] Updated .env with new credentials
- [ ] Removed .env from git history (or created new repo)
- [ ] Added .gitignore
- [ ] Verified .env is not tracked in git
- [ ] Removed hardcoded credentials from telegram_controller.py
- [ ] Removed hardcoded credentials from enhanced_notifications.py
- [ ] Fixed apex_nexus_v2.py .env parser
- [ ] Committed all security fixes

### Important Items (Should Complete)
- [ ] Created env_validator.py
- [ ] Created emergency stop command
- [ ] Created daily security check script
- [ ] Tested system startup in simulation mode
- [ ] Verified no old credentials work

### Verification Commands
```bash
# Run all checks
/workspace/scripts/daily_security_check.sh

# Verify git history
git log --all --oneline -- .env
# Should show: fatal: ambiguous argument '.env': unknown revision or path

# Test environment
python3 /workspace/utils/env_validator.py
```

---

## 🚀 RESUMING TRADING OPERATIONS

**ONLY after ALL critical items are complete:**

1. **Double-check LIVE_MODE**:
   ```bash
   grep "LIVE_MODE" /workspace/.env
   ```

2. **Start in simulation first**:
   ```bash
   # Set to simulation
   sed -i 's/LIVE_MODE=True/LIVE_MODE=False/' /workspace/.env
   
   # Run for 24 hours
   python3 /workspace/apex_nexus_v2.py
   ```

3. **Review simulation results**:
   - Check logs in `/workspace/logs/`
   - Verify Telegram notifications working
   - Confirm no errors

4. **Enable live trading** (if satisfied):
   ```bash
   sed -i 's/LIVE_MODE=False/LIVE_MODE=True/' /workspace/.env
   python3 /workspace/apex_nexus_v2.py
   ```

---

## 📞 NEED HELP?

If you encounter issues:

1. **DO NOT** skip security steps
2. **DO NOT** commit .env to git
3. **DO NOT** enable LIVE_MODE until all checks pass

AEGIS v2.0 is standing by to assist with:
- Phase 1: Deep security audit
- Phase 2: Architecture redesign
- Phase 3: Automated implementation
- Phase 4: Comprehensive testing

---

## 📊 ESTIMATED TIME SUMMARY

| Phase | Time | Priority |
|-------|------|----------|
| Phase 1: Credential Rotation | 15 min | 🔴 CRITICAL |
| Phase 2: Git History Cleanup | 15 min | 🔴 CRITICAL |
| Phase 3: Remove Hardcoded Creds | 10 min | 🔴 CRITICAL |
| Phase 4: Secure Env Loading | 15 min | 🟠 HIGH |
| Phase 5: Emergency Stop | 10 min | 🟠 HIGH |
| Phase 6: Monitoring | 10 min | 🟡 MEDIUM |
| Phase 7: Verification | 10 min | 🟠 HIGH |
| **TOTAL** | **~1.5 hours** | |

---

## AEGIS v2.0 - IMMEDIATE ACTION PLAN COMPLETE

This plan addresses the MOST CRITICAL vulnerabilities. For comprehensive remediation, proceed to **AEGIS Phase 1: Quantum Dissection**.

**Status**: ✅ ACTION PLAN READY FOR EXECUTION

---

*Generated by AEGIS v2.0 under PROMETHEUS (autonomous action) protocol with VERITAS evidence linkage.*
