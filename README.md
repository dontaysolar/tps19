# TPS19 - Crypto Trading System

## Overview

TPS19 is a Python-based cryptocurrency trading system designed for automated trading on Crypto.com exchange. The system features AI-driven decision making, risk management, and automated trade execution.

**⚠️ WARNING**: This system can execute real trades with real money. Use with extreme caution and only trade with funds you can afford to lose.

## Current Status

**Development Stage**: The system is currently in early development/prototype stage. While the architecture is sound, several critical components need to be implemented before production use:

- ❌ Real market data integration (currently using simulated data)
- ❌ Actual AI/ML models (currently using basic if-else logic)
- ❌ Comprehensive backtesting
- ❌ Production-grade error handling
- ✅ Modular architecture
- ✅ Database schema
- ✅ Configuration management
- ✅ Logging infrastructure

## Features

### Implemented
- Modular architecture with clear separation of concerns
- SQLAlchemy-based database models
- Configuration management with environment variables
- Structured logging with JSON output
- Basic AI decision framework (SIUL - Smart Intelligent Unified Logic)
- N8N webhook integration for automation
- Risk management framework
- Order and trade tracking
- **Enhanced Market Simulation** with:
  - Realistic price movements and volatility
  - Multiple market conditions (bull, bear, sideways, flash crash)
  - Market events and news impact
  - Order book simulation
  - Technical indicators (SMA, RSI)
  - Correlation between assets
- **Comprehensive Backtesting Engine** with:
  - Multiple order types (market, limit, stop)
  - Realistic commission and slippage
  - Performance metrics (Sharpe, Sortino, Calmar ratios)
  - Equity curve tracking
  - Trade analytics
- **Web-based Simulation Dashboard** with:
  - Real-time price updates
  - Market condition control
  - Live backtesting
  - Performance visualization

### Planned
- Real Crypto.com API integration
- WebSocket support for real-time data
- Machine learning models for prediction
- Performance analytics dashboard
- Multi-exchange support
- Advanced trading strategies

## Architecture

```
TPS19/
├── config/           # Configuration files
├── core/            # Core utilities (logging, etc.)
├── database/        # Database models and connection
├── exchanges/       # Exchange API clients
├── modules/         # Trading modules
│   ├── ai_council.py      # AI decision making
│   ├── market_feed.py     # Market data handling
│   ├── risk_manager.py    # Risk management
│   ├── trading_engine.py  # Trade execution
│   └── siul/              # SIUL AI system
├── scripts/         # Utility scripts
├── tests/          # Test suite
└── main.py         # Main application entry
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite used by default)
- Redis (optional, for caching)
- N8N (optional, for automation)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd tps19
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
python main.py migrate
```

## Configuration

Key configuration options in `.env`:

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# Crypto.com API
CRYPTO_COM_API_KEY=your_api_key
CRYPTO_COM_API_SECRET=your_api_secret

# Trading
ENABLE_LIVE_TRADING=false
MAX_POSITION_SIZE_PERCENT=10
DEFAULT_STOP_LOSS_PERCENT=2

# Risk Management
MAX_DAILY_LOSS_PERCENT=5
MAX_OPEN_POSITIONS=5
```

## Usage

### Running Tests
```bash
python main.py test
```

### Starting in Simulation Mode
```bash
python main.py start
```

### Starting with Live Trading (DANGEROUS!)
```bash
python main.py start --live
# You will be asked to confirm multiple times
```

### Checking Status
```bash
python main.py status
```

### Running Backtest
```bash
python main.py backtest --symbol BTC_USDT --strategy trend_following --days 30
```

### Running Enhanced Simulation Demo
```bash
# Run the comprehensive simulation demo
python run_enhanced_simulation.py

# Start the web dashboard
python simulation/simulation_dashboard.py
# Then open http://localhost:8000 in your browser
```

## System Components

### SIUL (Smart Intelligent Unified Logic)
The core AI decision engine that combines multiple intelligence modules:
- Market Analyzer: Analyzes market conditions
- Risk Assessor: Evaluates risk levels
- Pattern Detector: Identifies trading patterns
- Sentiment Analyzer: Gauges market sentiment
- Trend Predictor: Predicts future trends

### Trading Engine
Handles order execution and trade management:
- Order placement and cancellation
- Position management
- Trade execution monitoring
- Slippage control

### Risk Manager
Protects capital through:
- Position sizing
- Stop-loss management
- Maximum drawdown limits
- Exposure controls

### Market Feed Manager
Handles market data:
- Real-time price feeds
- Order book data
- Trade history
- Technical indicators

## Safety Features

1. **Simulation Mode by Default**: System runs in simulation mode unless explicitly enabled for live trading
2. **Risk Limits**: Configurable maximum position sizes and daily loss limits
3. **Double Confirmation**: Live trading requires explicit confirmation
4. **Comprehensive Logging**: All actions are logged for audit
5. **Error Recovery**: Automatic error handling and recovery mechanisms

## Development

### Adding a New Strategy
1. Create new strategy file in `modules/strategies/`
2. Implement the `BaseStrategy` interface
3. Register in the trading engine
4. Add configuration options

### Running Development Server
```bash
python main.py start --debug
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Monitoring

The system provides several monitoring endpoints:
- System health checks
- Performance metrics
- Trade history
- Error logs

Logs are stored in JSON format for easy parsing and analysis.

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Encryption**: Sensitive data should be encrypted at rest
3. **Access Control**: Implement proper authentication for any web interfaces
4. **Network Security**: Use VPN/firewall for production deployment
5. **Audit Trail**: All trades and decisions are logged

## Troubleshooting

### Common Issues

1. **"API credentials must be provided"**
   - Ensure valid API keys are set in `.env`

2. **"Database connection failed"**
   - Check database URL in configuration
   - Ensure database service is running

3. **"Rate limit exceeded"**
   - System automatically handles rate limits
   - Adjust `RATE_LIMIT_PER_SECOND` if needed

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Disclaimer

**USE AT YOUR OWN RISK**

This software is provided "as is", without warranty of any kind. The authors are not responsible for any financial losses incurred through the use of this software. Cryptocurrency trading carries significant risk, and you should never trade with money you cannot afford to lose.

## License

[Specify license here]

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review the logs for error details

## Roadmap

### Phase 1 (Current)
- ✅ Basic architecture
- ✅ Configuration management
- ✅ Database schema
- ⏳ Real API integration
- ⏳ Basic strategies

### Phase 2
- [ ] Machine learning models
- [ ] Backtesting engine
- [ ] Performance dashboard
- [ ] Mobile notifications

### Phase 3
- [ ] Multi-exchange support
- [ ] Advanced strategies
- [ ] Social trading features
- [ ] API for external tools