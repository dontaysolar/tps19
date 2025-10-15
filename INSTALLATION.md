# TPS19 Installation Guide

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP library for API calls
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework
- `black`, `flake8`, `mypy` - Code quality tools

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
nano .env  # or vim, code, etc.
```

**Minimum configuration** (.env):
```bash
TPS19_HOME=/opt/tps19          # Or use current directory
TPS19_ENV=simulation           # Start with simulation mode!
TPS19_DEBUG=true               # Enable debug logging
```

**For production** (when ready):
```bash
# Add these only when moving to live trading
CRYPTO_COM_API_KEY=your_api_key
CRYPTO_COM_API_SECRET=your_secret
CRYPTO_COM_API_PASSPHRASE=your_passphrase
```

### 3. Verify Installation

```bash
# Test the system
python3 tps19_main.py test
```

Expected output:
```
🧪 Running Comprehensive System Tests...
============================================================
🔍 Testing SIUL...
✅ PASSED SIUL
🔍 Testing Patch + Rollback System...
✅ PASSED PATCH_MANAGER
🔍 Testing N8N Integration...
✅ PASSED N8N

============================================================
📊 COMPREHENSIVE TEST RESULTS
============================================================
✅ PASSED siul
✅ PASSED patch_manager
✅ PASSED n8n

🎯 OVERALL: 3/3 tests passed
🎉 ALL TESTS PASSED! SYSTEM FULLY OPERATIONAL!
```

### 4. Start Trading (Simulation)

```bash
# Start in simulation mode
python3 tps19_main.py
```

You should see:
```
✅ All unified modules imported successfully
🚀 Starting TPS19 Definitive Unified System...
💓 TPS19 Unified System - 2025-10-15 ...
🧠 SIUL Decision: hold
📊 Confidence: 62.50%
```

## Directory Setup

### Option A: Use /opt/tps19 (Recommended for Production)

```bash
# Create directory structure
sudo mkdir -p /opt/tps19
sudo chown $USER:$USER /opt/tps19

# Copy or symlink your code
cp -r . /opt/tps19/
# OR
ln -s $(pwd) /opt/tps19

# Set environment
export TPS19_HOME=/opt/tps19
```

### Option B: Use Current Directory (Development)

The system will automatically use the workspace directory if /opt/tps19 is not accessible.

```bash
# Just set the environment variable
export TPS19_HOME=$(pwd)

# Or add to .env
echo "TPS19_HOME=$(pwd)" >> .env
```

## Database Initialization

Databases are created automatically on first run. They will be stored in:
- `{TPS19_HOME}/data/databases/` (default)
- Or as specified in `config/system.json`

Expected databases:
```
data/databases/
├── ai_council.db
├── ai_decisions.db
├── market_data.db
├── risk.db
├── risk_management.db
├── simulation.db
└── trading.db
```

## Configuration Files

### config/mode.json
```json
{
  "mode": "simulation",
  "timestamp": "20250630_001026"
}
```

Modes:
- `simulation` - Paper trading (safe, no real money)
- `predeployment` - Final testing before live
- `production` - Live trading with real money

### config/trading.json
```json
{
  "trading": {
    "mode": "simulation",
    "default_pair": "BTC/USD",
    "max_position_size": 0.1,
    "risk_per_trade": 0.02
  },
  "risk_management": {
    "max_daily_loss": 0.05,
    "stop_loss": 0.02,
    "take_profit": 0.04
  }
}
```

### config/system.json
```json
{
  "system": {
    "name": "TPS19",
    "version": "1.0.0",
    "environment": "production",
    "debug": false
  },
  "database": {
    "path": "/opt/tps19/data/databases/",
    "backup_interval": 3600
  },
  "logging": {
    "level": "INFO",
    "file": "/opt/tps19/logs/system.log",
    "max_size": "10MB",
    "backup_count": 5
  }
}
```

## Troubleshooting

### Permission Denied Errors

```bash
# If you see: PermissionError: [Errno 13] Permission denied: '/opt/tps19'

# Solution 1: Use workspace
export TPS19_HOME=$(pwd)

# Solution 2: Fix permissions
sudo mkdir -p /opt/tps19
sudo chown $USER:$USER /opt/tps19
```

### Module Not Found Errors

```bash
# If you see: ModuleNotFoundError: No module named 'xxx'

# Install dependencies
pip install -r requirements.txt

# Or specific module
pip install requests python-dotenv
```

### Database Errors

```bash
# If databases are corrupted or causing issues

# Backup current databases
mv data/databases data/databases.backup

# System will recreate on next run
python3 tps19_main.py test
```

### API Errors

```bash
# If market data fails to load

# Check internet connection
ping api.coingecko.com

# Check API rate limits (CoinGecko: 10-50 calls/min free tier)
# System respects rate limits automatically
```

## Verification Checklist

After installation, verify:

- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Dependencies installed (`pip list | grep requests`)
- [ ] Configuration files exist (`ls config/*.json`)
- [ ] Databases created (`ls data/databases/*.db`)
- [ ] Logs directory exists (`ls logs/`)
- [ ] Tests pass (`python3 tps19_main.py test`)
- [ ] System starts (`python3 tps19_main.py`)

## Development Setup

For development work:

```bash
# Install development dependencies
pip install -r requirements.txt

# Install code quality tools
pip install black flake8 mypy

# Format code
black modules/

# Lint code
flake8 modules/

# Type check
mypy modules/
```

## Production Deployment

### Prerequisites
- [ ] Extensive testing in simulation mode (weeks/months)
- [ ] Security audit completed
- [ ] API keys securely stored
- [ ] Monitoring set up
- [ ] Backup strategy in place

### Deployment Steps

1. **Set up production server**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade
   
   # Install Python 3.8+
   sudo apt install python3 python3-pip
   ```

2. **Deploy code**
   ```bash
   sudo mkdir -p /opt/tps19
   sudo chown $USER:$USER /opt/tps19
   cd /opt/tps19
   git clone <your-repo>
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Add production API keys
   ```

4. **Set production mode**
   ```bash
   # Edit config/mode.json
   {
     "mode": "production",
     "timestamp": "$(date +%Y%m%d_%H%M%S)"
   }
   ```

5. **Set up systemd service**
   ```bash
   sudo cp services/tps19_main.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable tps19_main
   sudo systemctl start tps19_main
   ```

6. **Monitor**
   ```bash
   # Check status
   sudo systemctl status tps19_main
   
   # View logs
   tail -f /opt/tps19/logs/system.log
   ```

## Security Considerations

Before going live:

1. **Never commit .env to git**
   - Already in .gitignore
   - Double check: `git status`

2. **Secure API keys**
   - Use environment variables
   - Consider key encryption
   - Rotate regularly

3. **Database security**
   - Implement encryption (future)
   - Restrict file permissions
   - Regular backups

4. **Network security**
   - Use HTTPS only
   - Firewall configuration
   - VPN for admin access

5. **Monitoring**
   - Set up alerts
   - Monitor API usage
   - Track system health

## Support

If you encounter issues:

1. Check logs: `tail -f logs/system.log`
2. Read documentation: `README.md`, `ANALYSIS.md`
3. Review error messages carefully
4. Test in simulation mode first

## Next Steps

After successful installation:

1. **Read** `README.md` - User guide
2. **Review** `ANALYSIS.md` - System architecture
3. **Check** `NEXT_STEPS.md` - Development roadmap
4. **Test** extensively in simulation mode
5. **Monitor** system performance
6. **Start** with small amounts when going live

---

**⚠️ IMPORTANT**: Always test in simulation mode first. Cryptocurrency trading involves substantial risk. Use at your own risk.
