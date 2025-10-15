#!/usr/bin/env python3
"""
TPS19 - Production-Ready Crypto Trading System
Main application entry point
"""

import asyncio
import signal
import sys
from typing import Optional
import click
from datetime import datetime

from config.settings import settings
from core.logging_config import setup_logging, get_logger
from database.connection import db_manager
from exchanges.crypto_com_client import CryptoComClient
from modules.trading_engine import TradingEngine
from modules.market_feed import MarketFeedManager
from modules.ai_council import AICouncilV2
from modules.risk_manager import RiskManager
from modules.n8n_integration import N8NIntegration


# Setup logging
setup_logging(
    log_level=settings.monitoring.log_level,
    log_format=settings.monitoring.log_format,
    log_file=settings.logs_dir / "tps19.log"
)

logger = get_logger(__name__)


class TPS19System:
    """Main TPS19 Trading System"""
    
    def __init__(self):
        self.running = False
        self.components = {}
        self.tasks = []
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            logger.info("Initializing TPS19 system components...")
            
            # Database
            db_manager.initialize()
            db_manager.create_tables()
            
            # Exchange client
            self.exchange_client = CryptoComClient()
            
            # Core components
            self.components = {
                "market_feed": MarketFeedManager(self.exchange_client),
                "ai_council": AICouncilV2(db_manager),
                "risk_manager": RiskManager(db_manager),
                "trading_engine": TradingEngine(
                    exchange_client=self.exchange_client,
                    db_manager=db_manager,
                    ai_council=None,  # Set after initialization
                    risk_manager=None  # Set after initialization
                ),
                "n8n_integration": N8NIntegration() if settings.n8n.enable_webhooks else None
            }
            
            # Set cross-references
            self.components["trading_engine"].ai_council = self.components["ai_council"]
            self.components["trading_engine"].risk_manager = self.components["risk_manager"]
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def start(self):
        """Start the trading system"""
        try:
            logger.info("Starting TPS19 Trading System...")
            self.running = True
            
            # Start market feed
            await self.components["market_feed"].start()
            
            # Start trading engine
            if settings.trading.enable_live_trading:
                await self.components["trading_engine"].start()
                logger.warning("LIVE TRADING ENABLED - Real money at risk!")
            else:
                logger.info("Running in simulation mode - no real trades will be executed")
            
            # Start N8N integration if enabled
            if self.components.get("n8n_integration"):
                await self.components["n8n_integration"].start()
            
            # Main loop
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"System error: {e}")
            await self.stop()
            raise
    
    async def _main_loop(self):
        """Main system loop"""
        logger.info("Entering main loop...")
        
        while self.running:
            try:
                # System health check
                health = await self._check_system_health()
                if not health["healthy"]:
                    logger.warning(f"System health check failed: {health}")
                
                # Log system status
                if int(datetime.now().timestamp()) % 300 == 0:  # Every 5 minutes
                    await self._log_system_status()
                
                # Sleep for a short interval
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _check_system_health(self) -> dict:
        """Check system health"""
        health = {
            "healthy": True,
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check each component
        for name, component in self.components.items():
            if component and hasattr(component, "health_check"):
                try:
                    component_health = await component.health_check()
                    health["components"][name] = component_health
                    if not component_health.get("healthy", True):
                        health["healthy"] = False
                except Exception as e:
                    health["components"][name] = {"healthy": False, "error": str(e)}
                    health["healthy"] = False
        
        return health
    
    async def _log_system_status(self):
        """Log system status"""
        try:
            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": "running",  # Calculate actual uptime
                "components": {}
            }
            
            # Get stats from each component
            for name, component in self.components.items():
                if component and hasattr(component, "get_stats"):
                    stats["components"][name] = await component.get_stats()
            
            # Get database stats
            stats["database"] = db_manager.get_table_stats()
            
            logger.info("System status", extra=stats)
            
        except Exception as e:
            logger.error(f"Failed to log system status: {e}")
    
    async def stop(self):
        """Stop the trading system"""
        logger.info("Stopping TPS19 Trading System...")
        self.running = False
        
        # Stop all components
        for name, component in self.components.items():
            if component and hasattr(component, "stop"):
                try:
                    await component.stop()
                    logger.info(f"Stopped component: {name}")
                except Exception as e:
                    logger.error(f"Error stopping {name}: {e}")
        
        # Close database connections
        db_manager.close()
        
        logger.info("TPS19 Trading System stopped")
    
    def handle_signal(self, signum, frame):
        """Handle system signals"""
        logger.info(f"Received signal {signum}")
        asyncio.create_task(self.stop())


@click.group()
def cli():
    """TPS19 Crypto Trading System CLI"""
    pass


@cli.command()
@click.option('--live', is_flag=True, help='Enable live trading (use with caution!)')
def start(live: bool):
    """Start the trading system"""
    if live:
        # Double confirmation for live trading
        click.echo("⚠️  WARNING: Live trading mode requested!")
        click.echo("This will execute real trades with real money.")
        confirmation = click.prompt("Type 'I UNDERSTAND' to continue", type=str)
        
        if confirmation != "I UNDERSTAND":
            click.echo("Live trading cancelled.")
            return
        
        settings.trading.enable_live_trading = True
    
    # Create system instance
    system = TPS19System()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, system.handle_signal)
    signal.signal(signal.SIGTERM, system.handle_signal)
    
    # Run the system
    try:
        asyncio.run(system.start())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"System crashed: {e}")
        sys.exit(1)


@cli.command()
def test():
    """Run system tests"""
    click.echo("Running system tests...")
    
    # Initialize components
    system = TPS19System()
    
    # Run component tests
    test_results = {}
    
    for name, component in system.components.items():
        if component and hasattr(component, "test"):
            try:
                result = component.test()
                test_results[name] = "✅ PASS" if result else "❌ FAIL"
            except Exception as e:
                test_results[name] = f"❌ ERROR: {e}"
        else:
            test_results[name] = "⏭️  SKIP (no test method)"
    
    # Display results
    click.echo("\nTest Results:")
    click.echo("=" * 50)
    
    for component, result in test_results.items():
        click.echo(f"{component}: {result}")
    
    # Summary
    passed = sum(1 for r in test_results.values() if "✅ PASS" in r)
    total = len(test_results)
    
    click.echo("=" * 50)
    click.echo(f"Summary: {passed}/{total} tests passed")
    
    if passed == total:
        click.echo("🎉 All tests passed!")
        sys.exit(0)
    else:
        click.echo("❌ Some tests failed")
        sys.exit(1)


@cli.command()
def status():
    """Check system status"""
    click.echo("Checking system status...")
    
    # Check if system is running
    # This would typically check for a PID file or process
    click.echo("System status: Not implemented yet")


@cli.command()
@click.option('--symbol', default='BTC_USDT', help='Symbol to backtest')
@click.option('--strategy', default='trend_following', help='Strategy to test')
@click.option('--days', default=30, help='Number of days to backtest')
def backtest(symbol: str, strategy: str, days: int):
    """Run backtesting"""
    click.echo(f"Running backtest for {symbol} using {strategy} strategy over {days} days...")
    click.echo("Backtesting not implemented yet")


@cli.command()
def migrate():
    """Run database migrations"""
    from database.connection import run_migrations
    
    click.echo("Running database migrations...")
    try:
        run_migrations()
        click.echo("✅ Migrations completed successfully")
    except Exception as e:
        click.echo(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()