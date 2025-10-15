"""
TPS19 Configuration Management
Centralized configuration using pydantic for validation
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    url: str = Field(default="sqlite:///data/tps19.db", env="DATABASE_URL")
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=200)
    pool_timeout: int = Field(default=30, ge=10, le=300)
    echo: bool = Field(default=False)
    
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_ttl: int = Field(default=3600)  # 1 hour default TTL


class CryptoComSettings(BaseSettings):
    """Crypto.com API configuration"""
    api_key: str = Field(env="CRYPTO_COM_API_KEY")
    api_secret: str = Field(env="CRYPTO_COM_API_SECRET")
    api_url: str = Field(
        default="https://api.crypto.com/v2",
        env="CRYPTO_COM_API_URL"
    )
    timeout: int = Field(default=30)
    rate_limit_per_second: int = Field(default=10)
    
    @validator("api_key", "api_secret")
    def validate_api_credentials(cls, v):
        if not v or v == "your_api_key_here" or v == "your_api_secret_here":
            raise ValueError("Valid API credentials must be provided")
        return v


class TradingSettings(BaseSettings):
    """Trading configuration"""
    default_quote_currency: str = Field(default="USDT", env="DEFAULT_QUOTE_CURRENCY")
    max_position_size_percent: float = Field(default=10.0, ge=0.1, le=100.0)
    default_stop_loss_percent: float = Field(default=2.0, ge=0.1, le=50.0)
    default_take_profit_percent: float = Field(default=5.0, ge=0.1, le=100.0)
    
    # Risk management
    max_daily_loss_percent: float = Field(default=5.0, ge=0.1, le=100.0)
    max_open_positions: int = Field(default=5, ge=1, le=50)
    min_trade_amount_usdt: float = Field(default=10.0, ge=1.0)
    
    # Execution
    enable_live_trading: bool = Field(default=False)
    use_market_orders: bool = Field(default=False)
    slippage_tolerance_percent: float = Field(default=0.1, ge=0.01, le=5.0)


class AISettings(BaseSettings):
    """AI/ML configuration"""
    model_update_interval_hours: int = Field(default=24, ge=1)
    min_data_points_for_prediction: int = Field(default=100, ge=10)
    confidence_threshold: float = Field(default=0.7, ge=0.1, le=1.0)
    
    # SIUL weights
    market_analyzer_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    risk_assessor_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    pattern_detector_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    sentiment_analyzer_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    trend_predictor_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    
    @validator(
        "market_analyzer_weight",
        "risk_assessor_weight",
        "pattern_detector_weight",
        "sentiment_analyzer_weight",
        "trend_predictor_weight"
    )
    def validate_weights_sum(cls, v, values):
        weights = [
            values.get("market_analyzer_weight", 0.25),
            values.get("risk_assessor_weight", 0.20),
            values.get("pattern_detector_weight", 0.20),
            values.get("sentiment_analyzer_weight", 0.15),
            v  # Current value being validated
        ]
        if sum(weights) > 1.01:  # Allow small floating point errors
            raise ValueError("Sum of weights must equal 1.0")
        return v


class N8NSettings(BaseSettings):
    """N8N automation configuration"""
    url: str = Field(default="http://localhost:5678", env="N8N_URL")
    api_key: Optional[str] = Field(default=None, env="N8N_API_KEY")
    webhook_timeout: int = Field(default=10)
    enable_webhooks: bool = Field(default=True)


class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration"""
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json")  # json or text
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=8000)


class SecuritySettings(BaseSettings):
    """Security configuration"""
    secret_key: str = Field(env="SECRET_KEY")
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    encryption_key: str = Field(env="ENCRYPTION_KEY")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24)
    
    @validator("secret_key", "jwt_secret_key", "encryption_key")
    def validate_keys(cls, v):
        if len(v) < 32:
            raise ValueError("Security keys must be at least 32 characters long")
        return v


class NotificationSettings(BaseSettings):
    """Notification configuration"""
    # Telegram
    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, env="TELEGRAM_CHAT_ID")
    
    # Email
    smtp_server: Optional[str] = Field(default=None, env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    notification_email: Optional[str] = Field(default=None, env="NOTIFICATION_EMAIL")
    
    # Notification preferences
    notify_on_trade: bool = Field(default=True)
    notify_on_error: bool = Field(default=True)
    notify_on_opportunity: bool = Field(default=True)


class Settings(BaseSettings):
    """Main settings aggregator"""
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    crypto_com: CryptoComSettings = CryptoComSettings()
    trading: TradingSettings = TradingSettings()
    ai: AISettings = AISettings()
    n8n: N8NSettings = N8NSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    security: SecuritySettings = SecuritySettings()
    notifications: NotificationSettings = NotificationSettings()
    
    # Paths
    root_dir: Path = Path(__file__).parent.parent
    data_dir: Path = root_dir / "data"
    logs_dir: Path = root_dir / "logs"
    models_dir: Path = root_dir / "models"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        for dir_path in [self.data_dir, self.logs_dir, self.models_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    def get_siul_weights(self) -> Dict[str, float]:
        """Get SIUL module weights as dictionary"""
        return {
            "market_analyzer": self.ai.market_analyzer_weight,
            "risk_assessor": self.ai.risk_assessor_weight,
            "pattern_detector": self.ai.pattern_detector_weight,
            "sentiment_analyzer": self.ai.sentiment_analyzer_weight,
            "trend_predictor": self.ai.trend_predictor_weight
        }


# Global settings instance
settings = Settings()

# Export commonly used settings
DEBUG = settings.debug
ENVIRONMENT = settings.environment
DATABASE_URL = settings.database.url
REDIS_URL = settings.database.redis_url