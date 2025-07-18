"""
Configuration centralisée pour NIKKOTRADER V11
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Configuration principale du système"""
    
    # Informations générales
    app_name: str = "NIKKOTRADER V11"
    app_version: str = "11.0.0"
    description: str = "Système de trading algorithmique multi-agents"
    
    # Environnement
    environment: str = "development"
    debug: bool = True
    
    # Base de données
    database_url: str = "postgresql+asyncpg://nikkotrader:nikkotrader123@localhost:5432/nikkotrader_v11"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl: int = 3600  # 1 heure
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Sécurité
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Trading Configuration
    mt5_login: int = 51862230
    mt5_password: str = "AiMwI&gG$26Z8i"
    mt5_server: str = "ICMarkets-Demo"
    mt5_path: str = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    
    # Telegram
    telegram_bot_token: str = "8069695013:AAFs7M8knILYIS_NacS2QlIGUVEiZWLmlj0"
    telegram_chat_id: str = "-1002272137953"
    
    # Trading Pairs
    trading_pairs: List[str] = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
        "EURGBP", "EURJPY", "EURCHF", "EURAUD", "EURCAD", "EURNZD",
        "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD",
        "AUDJPY", "CADJPY", "CHFJPY", "NZDJPY",
        "AUDCAD", "AUDCHF", "AUDNZD",
        "CADCHF", "NZDCAD", "NZDCHF"
    ]
    
    # Agents Configuration
    agents_config: dict = {
        "master": {
            "name": "MasterAgent",
            "description": "Orchestrateur principal",
            "max_concurrent_tasks": 10,
            "heartbeat_interval": 30
        },
        "market_data": {
            "name": "MarketDataAgent",
            "description": "Collecte des données de marché",
            "scan_interval": 5,
            "max_retries": 3
        },
        "strategy": {
            "name": "StrategyAgent",
            "description": "Agents de stratégies - Options Binaires Optimisées",
            "strategies": ["Breakout", "Pullback", "Range", "Scalping", "MeanReversion", "Consolidation", "Divergence", "NewsImpact", "SessionBreakout"],
            "total_strategies": 9,
            "timeframe_distribution": {
                "short_term_3_5min": 6,  # 67% (Scalping, Consolidation, Breakout, Pullback, MeanReversion, Range)
                "medium_term_10_15min": 2, # 22% (Divergence, NewsImpact)
                "long_term_30min": 1      # 11% (SessionBreakout)
            },
            "distribution_optimal": "67% / 22% / 11%"
        },
        "risk": {
            "name": "RiskManagementAgent",
            "description": "Gestion des risques - Mode Forward Testing",
            "max_drawdown": 0.50,  # 50% pour forward testing
            "max_daily_loss": 0.25,  # 25% pour forward testing
            "forward_testing_mode": True,
            "permissive_risk": True
        },
        "notification": {
            "name": "NotificationAgent",
            "description": "Gestion des notifications",
            "min_interval": 60
        }
    }
    
    # Performance Configuration
    performance_config: dict = {
        "tracking": {
            "enabled": True,
            "detailed_logging": True,
            "metrics_interval": 60
        },
        "analytics": {
            "min_trades_for_analysis": 10,
            "confidence_threshold": 0.65,
            "max_correlation_threshold": 0.8
        }
    }
    
    # Monitoring Configuration
    monitoring_config: dict = {
        "prometheus": {
            "enabled": True,
            "port": 9090
        },
        "grafana": {
            "enabled": True,
            "port": 3001
        },
        "alerts": {
            "enabled": True,
            "email_notifications": False,
            "telegram_alerts": True
        }
    }
    
    # Logging Configuration
    logging_config: dict = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_rotation": "1 day",
        "max_file_size": "10 MB",
        "backup_count": 7
    }
    
    # Strategy Versioning
    strategy_versioning: dict = {
        "enabled": True,
        "auto_backup": True,
        "max_versions": 10,
        "version_format": "v{major}.{minor}.{patch}"
    }
    
    # Forward Testing Configuration
    forward_testing: dict = {
        "enabled": True,
        "demo_account_only": True,
        "max_daily_trades": 500,  # Plus de trades pour collecter données
        "max_concurrent_positions": 20,  # Plus de positions simultanées
        "stop_loss_percentage": 0.10,  # Stop loss plus large
        "take_profit_percentage": 0.05,
        "permissive_risk_mode": True,
        "data_collection_priority": True
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Instance globale des paramètres
settings = Settings()

# Validation des paramètres critiques
def validate_settings():
    """Valide les paramètres critiques au démarrage"""
    errors = []
    
    if not settings.database_url:
        errors.append("DATABASE_URL is required")
    
    if not settings.redis_url:
        errors.append("REDIS_URL is required")
    
    if not settings.secret_key or settings.secret_key == "your-secret-key-here-change-in-production":
        errors.append("SECRET_KEY must be set to a secure value")
    
    if not settings.telegram_bot_token:
        errors.append("TELEGRAM_BOT_TOKEN is required")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True 