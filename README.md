# TPS19 Crypto Trading System

## Overview

TPS19 is a comprehensive cryptocurrency trading system built with AI-driven decision making, designed for the Crypto.com exchange. The system features modular architecture, intelligent trading signals, risk management, and comprehensive testing capabilities.

## System Architecture

### Core Components

1. **SIUL (Smart Intelligent Unified Logic)** - AI decision-making engine
2. **Trading Engine** - Order execution and portfolio management
3. **Market Data** - Real-time price feeds and analysis
4. **Risk Management** - Position sizing and risk controls
5. **AI Council** - Multi-factor decision making system
6. **Simulation Engine** - Paper trading capabilities
7. **N8N Integration** - Workflow automation
8. **Patch Manager** - System updates and rollback capabilities

### Key Features

- ✅ **AI-Driven Trading Decisions** - Multi-module intelligence system
- ✅ **Risk Management** - Automated position sizing and loss limits
- ✅ **Simulation Mode** - Safe paper trading environment
- ✅ **Real-time Market Data** - Live price feeds and analysis
- ✅ **Modular Architecture** - Easy to extend and maintain
- ✅ **Database Persistence** - SQLite for reliable data storage
- ✅ **Comprehensive Testing** - Automated test suites
- ✅ **Patch/Rollback System** - Safe system updates

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tps19
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the system**
   ```bash
   python3 test_system.py
   ```

## Usage

### Start the System
```bash
./start_system.sh
# or
python3 tps19_main.py
```

### Run Tests
```bash
python3 test_system.py
```

### Menu System
```bash
./start_menu.sh
```

## Configuration

### System Configuration (`config/system.json`)
- System name, version, environment settings
- Database paths and connection limits
- Logging configuration
- Security settings

### Trading Configuration (`config/trading.json`)
- Trading mode (simulation/live)
- Default trading pairs
- Risk parameters
- Strategy settings

### Mode Configuration (`config/mode.json`)
- Current system mode
- Deployment status

## Database Structure

The system uses SQLite databases for persistence:

- `ai_decisions.db` - AI Council decisions and learning
- `market_data.db` - Price data and market statistics
- `trading.db` - Trade history and portfolio
- `simulation.db` - Paper trading records
- `risk.db` - Risk metrics and limits
- `siul_core.db` - SIUL intelligence data

## Security Features

- Simulation mode by default
- Encrypted configuration options
- Multi-factor authentication support
- Session timeout controls
- Comprehensive audit trails

## Development

### Adding New Modules

1. Create module in `/modules/` directory
2. Follow the existing pattern for database initialization
3. Add tests to the test suite
4. Update configuration as needed

### Testing

The system includes comprehensive testing:
- Unit tests for individual modules
- Integration tests for system components
- Performance benchmarks
- Rollback system verification

## API Integration

### Supported Exchanges
- Crypto.com (primary)
- Extensible for other exchanges

### Data Sources
- CoinGecko API (free tier)
- Real-time WebSocket feeds (configurable)
- Custom data providers

## Monitoring & Alerts

- Telegram bot integration (configurable)
- System health monitoring
- Performance metrics
- Risk alerts
- Trade notifications

## Backup & Recovery

- Automated system backups
- Patch rollback capabilities
- Database integrity checks
- Configuration versioning

## License

This project is proprietary software. All rights reserved.

## Support

For technical support and questions, please refer to the system documentation or contact the development team.

---

**⚠️ IMPORTANT DISCLAIMER**: This software is for educational and simulation purposes. Always test thoroughly before using with real funds. Cryptocurrency trading involves significant risk.