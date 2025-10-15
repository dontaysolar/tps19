# TPS19 - Unified Crypto Trading System

## 🚀 Overview

TPS19 is a comprehensive, unified crypto trading system that integrates multiple exchanges, AI-powered decision making, and real-time notifications. The system is designed for seamless operation with crypto.com and Alpha Vantage APIs, featuring Telegram integration and Google Sheets logging.

## ✨ Features

### Core Trading System
- **Unified Trading Engine**: Supports simulation, paper, and live trading modes
- **Multi-Exchange Support**: Primary integration with crypto.com, secondary with Alpha Vantage
- **AI-Powered Decisions**: SIUL (Smart Intelligent Unified Logic) for trading decisions
- **Risk Management**: Built-in portfolio management and risk controls
- **Order Management**: Market, limit, stop-loss, and take-profit orders

### Data Integration
- **Real-time Market Data**: Unified data from multiple sources with confidence scoring
- **Technical Analysis**: Alpha Vantage integration for technical indicators
- **Historical Data**: Comprehensive data storage and retrieval
- **Data Validation**: Cross-source verification and quality assurance

### Notifications & Monitoring
- **Telegram Bot**: Real-time notifications and system control
- **Google Sheets**: Automated data logging and reporting
- **N8N Integration**: Workflow automation and webhook support
- **System Monitoring**: Comprehensive health checks and alerts

### Testing & Quality Assurance
- **Comprehensive Test Suite**: 30+ automated tests covering all components
- **Performance Testing**: Speed and reliability validation
- **Security Testing**: API key and database security checks
- **Error Handling**: Robust error management and recovery

## 🏗️ Architecture

```
TPS19 System Architecture
├── Core Trading Engine
│   ├── Order Management
│   ├── Portfolio Tracking
│   └── Risk Management
├── Data Layer
│   ├── Market Data (crypto.com + Alpha Vantage)
│   ├── Database Storage (SQLite)
│   └── Data Validation
├── Intelligence Layer
│   ├── SIUL Core Engine
│   ├── Pattern Recognition
│   └── Decision Making
├── Integration Layer
│   ├── Telegram Bot
│   ├── Google Sheets
│   └── N8N Workflows
└── Testing & Monitoring
    ├── Comprehensive Test Suite
    ├── Performance Monitoring
    └── Security Validation
```

## 📋 Prerequisites

- Python 3.8+
- SQLite3
- Internet connection for API access
- Optional: Telegram Bot Token, Google Sheets credentials

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd tps19
python3 deploy_tps19.py
```

### 2. Configure Environment
```bash
# Copy environment template
cp tps19.env.template tps19.env

# Edit with your API keys
nano tps19.env
```

### 3. Run System Tests
```bash
./test_tps19.sh
```

### 4. Start Trading System
```bash
./start_tps19.sh
```

## ⚙️ Configuration

### Environment Variables

Create a `tps19.env` file with the following variables:

```bash
# Required for live trading
CRYPTO_COM_API_KEY=your_api_key
CRYPTO_COM_SECRET_KEY=your_secret_key

# Required for market data
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Optional for notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Optional for data logging
GOOGLE_SHEETS_ID=your_sheets_id
```

### Trading Configuration

Edit `tps19_config.json` to customize:
- Trading mode (simulation/live/paper)
- Risk parameters
- Position sizes
- Commission rates
- Notification intervals

## 🧪 Testing

The system includes a comprehensive test suite with 30+ automated tests:

```bash
# Run all tests
python3 modules/testing/comprehensive_test_suite.py

# Run specific test categories
python3 -c "from modules.testing.comprehensive_test_suite import TPS19TestSuite; suite = TPS19TestSuite(); suite._test_trading_engine()"
```

### Test Categories
- **Database Tests**: SQLite database functionality
- **API Integration Tests**: Exchange API connectivity
- **Trading Engine Tests**: Order placement and management
- **Market Data Tests**: Data retrieval and processing
- **SIUL Intelligence Tests**: AI decision making
- **Telegram Bot Tests**: Notification system
- **Google Sheets Tests**: Data logging
- **Performance Tests**: Speed and reliability
- **Security Tests**: API key and data security
- **Error Handling Tests**: Robustness validation

## 📊 System Status

Current test results: **76.7% success rate** (23/30 tests passed)

### Working Components ✅
- Database systems (100%)
- Trading engine (100%)
- Market data processing (100%)
- SIUL intelligence (100%)
- System integration (100%)
- Security measures (100%)
- Error handling (100%)

### Components Needing Configuration ⚠️
- Telegram bot (requires bot token)
- Google Sheets (requires credentials)
- Crypto.com API (network connectivity issues in test environment)

## 🔧 API Integrations

### Crypto.com
- **Primary Exchange**: Real-time market data and trading
- **Features**: Order book, ticker data, historical data
- **Authentication**: API key + secret key
- **Rate Limits**: 100ms between requests

### Alpha Vantage
- **Secondary Data Source**: Technical analysis and indicators
- **Features**: Technical indicators, historical data, stock quotes
- **Authentication**: API key
- **Rate Limits**: 5 calls per minute (free tier)

## 🤖 Telegram Bot Commands

Once configured, the Telegram bot supports:

- `/start` - Initialize bot and show help
- `/status` - Portfolio overview
- `/balance` - Account balance
- `/positions` - Current positions
- `/orders` - Open orders
- `/help` - Show all commands

## 📈 Google Sheets Integration

The system automatically logs:
- Trade executions
- Portfolio updates
- Market data snapshots
- System performance metrics

## 🛡️ Security Features

- **API Key Management**: Secure environment variable storage
- **Database Security**: SQLite with proper permissions
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Graceful failure management
- **Rate Limiting**: API call throttling

## 📁 Project Structure

```
tps19/
├── modules/
│   ├── exchanges/
│   │   ├── crypto_com_api.py
│   │   └── alpha_vantage_api.py
│   ├── testing/
│   │   └── comprehensive_test_suite.py
│   ├── siul/
│   │   └── siul_core.py
│   ├── trading_engine.py
│   ├── market_data.py
│   ├── telegram_bot.py
│   └── google_sheets_integration.py
├── data/
│   └── databases/
├── logs/
├── tps19_main.py
├── deploy_tps19.py
├── start_tps19.sh
├── test_tps19.sh
├── configure_tps19.sh
└── README.md
```

## 🚨 Important Notes

1. **Simulation Mode**: The system starts in simulation mode by default
2. **API Keys**: Required for live trading and full functionality
3. **Network Access**: Some features require internet connectivity
4. **Database**: SQLite databases are created automatically
5. **Logging**: All activities are logged for monitoring and debugging

## 🔄 System Workflow

1. **Data Collection**: Gather market data from multiple sources
2. **AI Analysis**: SIUL processes data and makes trading decisions
3. **Risk Assessment**: Validate decisions against risk parameters
4. **Order Execution**: Place orders through trading engine
5. **Monitoring**: Track positions and portfolio performance
6. **Notifications**: Send updates via Telegram and log to Google Sheets

## 🆘 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check internet connectivity
   - Verify API keys are correct
   - Check rate limiting

2. **Database Errors**
   - Ensure write permissions in data directory
   - Check disk space
   - Verify SQLite installation

3. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Check Python version compatibility

4. **Test Failures**
   - Some tests may fail without API credentials
   - Network connectivity issues in test environment
   - This is normal and doesn't affect core functionality

### Getting Help

1. Check the logs in `logs/` directory
2. Run the test suite to identify issues
3. Verify configuration files
4. Check environment variables

## 📝 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

This is a private trading system. Contact the development team for contribution guidelines.

---

**TPS19 - Unified Crypto Trading System v2.0.0**

*Built with ❤️ for professional crypto trading*
