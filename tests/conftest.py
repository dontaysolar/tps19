"""
Pytest Configuration & Fixtures for AEGIS Test Suite

AEGIS v2.3 Enhancement: Test database isolation and cleanup
Implements TD-4 from technical debt register

Features:
- Isolated test database per test
- Automatic cleanup after tests
- Fresh state for each test
- Prevents test data pollution
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope='function')
def test_db_path():
    """
    Provide isolated test database path
    
    Creates temporary database for each test
    Auto-cleans up after test completes
    
    FRACTAL HOOK: Enables parallel test execution
    """
    # Create temp directory for test
    test_dir = tempfile.mkdtemp(prefix='aegis_test_')
    db_path = os.path.join(test_dir, 'test_positions.db')
    
    yield db_path
    
    # Cleanup after test
    try:
        shutil.rmtree(test_dir)
    except:
        pass  # Best effort cleanup


@pytest.fixture(scope='function')
def isolated_psm(test_db_path):
    """
    Provide isolated PSM instance for testing
    
    Each test gets fresh PSM with clean database
    Auto-closes connection after test
    
    Usage:
        def test_something(isolated_psm):
            pos_id = isolated_psm.open_position(...)
            assert pos_id is not None
    """
    from core.position_state_manager import PositionStateManager
    
    psm = PositionStateManager(db_path=test_db_path)
    
    yield psm
    
    # Cleanup
    try:
        psm.close()
    except:
        pass


@pytest.fixture(scope='function')
def mock_exchange_adapter():
    """
    Provide mock ExchangeAdapter for testing
    
    Returns pre-configured adapter in mock mode
    No real API calls, suitable for CI/CD
    """
    from core.exchange_adapter import ExchangeAdapter
    
    adapter = ExchangeAdapter(exchange_name='mock', enable_logging=False)
    
    yield adapter
    
    # Cleanup
    try:
        adapter.close()
    except:
        pass


@pytest.fixture(scope='function')
def test_trading_bot(mock_exchange_adapter, isolated_psm):
    """
    Provide test TradingBot instance
    
    Pre-configured with mock adapter and isolated PSM
    Ready for testing bot functionality
    """
    from core.trading_bot_base import TradingBotBase
    
    class TestBot(TradingBotBase):
        def __init__(self):
            super().__init__(
                bot_name="TEST_BOT",
                bot_version="1.0.0",
                exchange_name='mock',
                enable_psm=True,
                enable_logging=False
            )
    
    bot = TestBot()
    # Override PSM with isolated instance
    bot.psm = isolated_psm
    
    yield bot
    
    # Cleanup
    try:
        bot.close()
    except:
        pass


# Pytest configuration
def pytest_configure(config):
    """
    Configure pytest for AEGIS test suite
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# FRACTAL HOOK: Test database cleanup
# Usage: pytest --tb=short -v
# All tests now use isolated databases, preventing pollution
