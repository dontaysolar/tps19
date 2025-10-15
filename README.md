# TPS19 Unified Crypto Trading System

A comprehensive, AI-powered cryptocurrency trading system with multiple exchange integrations, automated trading strategies, and real-time monitoring capabilities.

## 🚀 Features

- **Multi-Exchange Support**: 
  - Crypto.com API integration for real-time crypto data
  - Alpha Vantage API for traditional markets and technical indicators
  - NO CoinGecko dependencies (removed for compliance)

- **Advanced Trading Engine**:
  - SIUL (Smart Intelligent Unified Logic) decision engine
  - Real-time market data aggregation
  - Technical indicator analysis (RSI, MACD, ADX)
  - Risk management system

- **Communication & Monitoring**:
  - Telegram bot for alerts and control
  - Google Sheets integration for portfolio tracking
  - N8N workflow automation support

- **Data Management**:
  - Unified market data aggregator
  - Local database storage
  - Performance metrics tracking

## 📋 System Requirements

- Python 3.7 or higher
- Linux/Unix environment (tested on Ubuntu)
- Internet connection for API access

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tps19.git
cd tps19
```

2. Install required dependencies:
```bash
pip3 install requests
# Optional dependencies:
pip3 install python-telegram-bot  # For Telegram integration
pip3 install google-api-python-client google-auth  # For Google Sheets
pip3 install psutil  # For system monitoring
```

3. Set up configuration (optional):
```bash
# For Telegram Bot
export TELEGRAM_BOT_TOKEN="your_bot_token"

# For Google Sheets
export GOOGLE_SHEETS_CREDS="/path/to/credentials.json"
export GOOGLE_SHEETS_ID="your_spreadsheet_id"

# For Alpha Vantage (enhanced features)
export ALPHA_VANTAGE_API_KEY="your_api_key"
```

## 🚀 Quick Start

1. Run system tests:
```bash
python3 tps19_main.py test
```

2. Start the trading system:
```bash
python3 tps19_main.py
```

3. Run validation checks:
```bash
python3 run_validation.py
```

## 📁 Project Structure

```
tps19/
├── tps19_main.py              # Main application entry point
├── run_validation.py          # System validation script
├── modules/
│   ├── exchanges/            # Exchange API integrations
│   │   ├── crypto_com.py    # Crypto.com API client
│   │   └── alpha_vantage.py # Alpha Vantage API client
│   ├── market/              # Market data modules
│   │   └── unified_market_data.py
│   ├── integrations/        # External service integrations
│   │   └── google_sheets.py
│   ├── telegram_bot.py      # Telegram bot module
│   ├── market_data.py       # Market data handler
│   ├── realtime_data.py     # Real-time data feed
│   └── testing/             # Test suites
│       └── comprehensive_test_suite.py
├── config/                   # Configuration files
├── data/                     # Data storage
│   └── databases/           # SQLite databases
└── logs/                     # System logs
```

## 🔧 Configuration

### Exchange Configuration

The system uses crypto.com as the primary exchange. No additional configuration needed for basic functionality.

### Telegram Bot Setup

1. Create a bot via @BotFather on Telegram
2. Get your bot token
3. Set the environment variable:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token_here"
   ```

### Google Sheets Integration

1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create service account credentials
4. Set environment variables:
   ```bash
   export GOOGLE_SHEETS_CREDS="/path/to/credentials.json"
   export GOOGLE_SHEETS_ID="your_spreadsheet_id"
   ```

## 📊 Trading Pairs

Default monitored pairs:
- BTC_USDT
- ETH_USDT
- DOGE_USDT
- CRO_USDT
- ADA_USDT

## 🧪 Testing

Run comprehensive tests:
```bash
python3 modules/testing/comprehensive_test_suite.py
```

Run system validation:
```bash
python3 run_validation.py
```

## 📈 API Integrations

### Crypto.com
- Real-time price data
- Order book depth
- Trade history
- Candlestick/OHLC data

### Alpha Vantage
- Technical indicators (RSI, MACD, etc.)
- Traditional market data
- Crypto exchange rates

### Telegram Bot Commands
- `/start` - Initialize bot
- `/price [symbol]` - Get current price
- `/market` - Market overview
- `/alerts` - Manage price alerts
- `/signals` - Trading signal subscription
- `/portfolio` - View portfolio
- `/performance` - Performance metrics

## ⚠️ Important Notes

1. **No CoinGecko**: This system does not use CoinGecko API as per requirements
2. **API Limits**: Be aware of rate limits for free API tiers
3. **Risk**: This is a trading system - use at your own risk
4. **Testing**: Always test in simulation mode first

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests and validation
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions:
- Open an issue on GitHub
- Contact via Telegram: @tps19support

## 🔐 Security

- Never commit API keys or credentials
- Use environment variables for sensitive data
- Regular security audits recommended

## 📝 Compliance

This system complies with the following requirements:
- ✅ No CoinGecko API usage
- ✅ Crypto.com integration
- ✅ Alpha Vantage integration  
- ✅ Telegram bot support
- ✅ Google Sheets integration
- ✅ Unified repository structure
- ✅ Comprehensive testing suite
- ✅ Quality assurance protocols

---

**Disclaimer**: This software is for educational and research purposes. Trading cryptocurrencies involves substantial risk. Always do your own research and trade responsibly.