# TPS19 Crypto Trading System

**TPS19** is an advanced cryptocurrency trading system with AI-powered decision making, real-time market data, and comprehensive risk management.

## 🚀 Features

- **AI-Powered Trading**: Multi-module AI council with SIUL (Smart Intelligent Unified Logic)
- **Risk Management**: Automated position sizing, stop-loss, and daily loss limits
- **Real-time Data**: Live market data feeds from CoinGecko API
- **Simulation Mode**: Paper trading for strategy testing
- **N8N Integration**: Workflow automation for trade signals and arbitrage
- **Patch Management**: System versioning with rollback capability
- **Multi-Database**: Separate databases for trading, AI, risk, and market data

## 🏗️ Architecture

### Core Components

- **SIUL Core**: Central intelligence with 5 AI modules
  - Market Analyzer
  - Risk Assessor
  - Pattern Detector
  - Sentiment Analyzer
  - Trend Predictor

- **Trading Engine**: Trade execution and order management
- **AI Council**: Learning-based decision system
- **Risk Manager**: Position sizing and exposure limits
- **Simulation Engine**: Paper trading environment
- **N8N Integration**: Webhook-based automation

### Technology Stack

- **Language**: Python 3.8+
- **Database**: SQLite
- **APIs**: CoinGecko (market data)
- **Automation**: N8N (Node.js workflow automation)
- **Exchange**: Crypto.com (primary target)

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- N8N (optional, for automation features)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tps19
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the system**
   
   Edit configuration files in `config/`:
   - `system.json` - System-wide settings
   - `trading.json` - Trading parameters
   - `n8n_config.json` - N8N integration settings

4. **Set deployment mode**
   
   Edit `config/mode.json`:
   ```json
   {"mode": "simulation", "timestamp": "..."}
   ```
   
   Modes: `simulation`, `predeployment`, `production`

5. **Initialize databases**
   ```bash
   python3 -c "from modules.siul.siul_core import siul_core; from modules.ai_council import AICouncil; AICouncil()"
   ```

## 🎯 Usage

### Running the System

**Start in simulation mode:**
```bash
python3 tps19_main.py
```

**Run tests:**
```bash
python3 tps19_main.py test
```

**Alternative startup:**
```bash
./start_system.sh
```

### Configuration

#### Trading Parameters (`config/trading.json`)

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

#### System Settings (`config/system.json`)

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
  }
}
```

## 🧪 Testing

Run comprehensive system tests:

```bash
python3 tps19_main.py test
```

This tests:
- SIUL intelligence system
- Patch & rollback functionality
- N8N integration
- Database connectivity

## 🔒 Security

⚠️ **Important Security Notes:**

1. **API Keys**: Store exchange API keys in environment variables, not config files
2. **Database Encryption**: Enable encryption for production deployments
3. **N8N Webhooks**: Secure webhook endpoints with authentication
4. **Backup Strategy**: Keep backups outside of version control

## 📊 Database Schema

TPS19 uses multiple SQLite databases:

- `trading.db` - Trade execution logs and positions
- `ai_decisions.db` - AI council decisions and learning
- `market_data.db` - Real-time price data
- `risk.db` - Risk metrics and limits
- `simulation.db` - Paper trading records
- `siul_core.db` - SIUL intelligence chains
- `patch_manager.db` - System versioning

## 🔧 Development

### Project Structure

```
tps19/
├── config/           # Configuration files
├── core/             # Core system components
├── data/             # Databases (gitignored)
├── logs/             # Log files (gitignored)
├── modules/          # Main modules
│   ├── ai_council.py
│   ├── brain/
│   ├── market/
│   ├── n8n/
│   ├── patching/
│   ├── risk_management.py
│   ├── simulation/
│   ├── siul/
│   └── trading_engine.py
├── scripts/          # Utility scripts
└── tps19_main.py     # Main entry point
```

### Code Quality

We use:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing

## 📝 Operational Modes

1. **Simulation Mode** (Default)
   - Paper trading with mock execution
   - Safe for strategy testing
   - Uses `simulation.db`

2. **Pre-deployment Mode**
   - Final testing before production
   - Limited live trading
   - Enhanced monitoring

3. **Production Mode**
   - Full live trading
   - Real money at risk
   - Comprehensive logging

## 🤖 AI Decision System

### SIUL (Smart Intelligent Unified Logic)

SIUL combines 5 intelligence modules using weighted scoring:

- **Market Analyzer** (25%): Price and volume analysis
- **Risk Assessor** (20%): Risk level evaluation
- **Pattern Detector** (20%): Technical pattern recognition
- **Sentiment Analyzer** (15%): Market sentiment
- **Trend Predictor** (20%): Trend forecasting

Decision thresholds:
- **Buy**: Combined score > 0.7
- **Sell**: Combined score < 0.3
- **Hold**: 0.3 ≤ score ≤ 0.7

## 📈 Performance

Current implementation handles:
- Real-time data: 5 symbols per minute (CoinGecko rate limit)
- Decision cycle: ~30 seconds
- Database operations: <100ms average

## 🚧 Known Limitations

1. **Exchange Support**: Currently hardcoded for Crypto.com
2. **Trading Engine**: Implementation in progress
3. **Path Configuration**: Uses hardcoded `/opt/tps19/` paths
4. **API Integration**: Limited to CoinGecko free tier

## 🗺️ Roadmap

- [ ] Complete trading engine implementation
- [ ] Multi-exchange support
- [ ] Advanced technical indicators
- [ ] Machine learning model integration
- [ ] Web-based dashboard
- [ ] Mobile alerts via Telegram
- [ ] Portfolio optimization

## 🤝 Contributing

This is a private trading system. For authorized contributors:

1. Test all changes in simulation mode
2. Follow existing code structure
3. Add tests for new features
4. Update documentation

## ⚠️ Disclaimer

**This software is for educational and research purposes. Cryptocurrency trading involves substantial risk of loss. Use at your own risk. The authors are not responsible for any financial losses incurred.**

## 📄 License

Proprietary - All rights reserved

## 📧 Support

For issues or questions, contact the system administrator.

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-15  
**Status**: Active Development
