"""
Modèles de base de données pour NIKKOTRADER V11
Système de stats détaillées avec versioning des stratégies
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class Strategy(Base):
    """Modèle pour les stratégies de trading avec versioning"""
    __tablename__ = "strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    description = Column(Text)
    
    # Configuration de la stratégie
    config = Column(JSON, nullable=False)
    
    # Métadonnées de version
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    created_by = Column(String(100), default="system")
    is_active = Column(Boolean, default=True)
    
    # Relation avec les trades
    trades = relationship("Trade", back_populates="strategy")
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        Index('idx_strategy_name_version', 'name', 'version'),
        Index('idx_strategy_active', 'is_active'),
    )

class Trade(Base):
    """Modèle pour les trades avec stats détaillées"""
    __tablename__ = "trades"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Référence à la stratégie
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    
    # Informations de base du trade
    symbol = Column(String(10), nullable=False)
    direction = Column(String(4), nullable=False)  # CALL ou PUT
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    
    # Timing
    entry_time = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    exit_time = Column(DateTime(timezone=True))
    expiry_minutes = Column(Integer, nullable=False)
    
    # Résultat
    result = Column(String(10))  # WIN, LOSS, PENDING
    pnl = Column(Float)  # Profit/Loss
    pnl_percentage = Column(Float)
    
    # Métriques de confiance et risque
    confidence = Column(Float, nullable=False)
    risk_score = Column(Float)
    
    # Conditions de marché au moment du trade
    market_state = Column(String(20))  # STRONG_TREND, MODERATE_TREND, WEAK_TREND, RANGING
    adx_value = Column(Float)
    rsi_value = Column(Float)
    volatility = Column(Float)
    volume_ratio = Column(Float)
    
    # Spread et slippage
    spread = Column(Float)
    slippage = Column(Float)
    
    # Métadonnées additionnelles
    metadata = Column(JSON)
    
    # Relations
    strategy = relationship("Strategy", back_populates="trades")
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        Index('idx_trade_symbol_time', 'symbol', 'entry_time'),
        Index('idx_trade_strategy_result', 'strategy_id', 'result'),
        Index('idx_trade_entry_time', 'entry_time'),
    )

class Agent(Base):
    """Modèle pour tracker les agents"""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # master, market_data, strategy, risk, notification
    
    # État de l'agent
    status = Column(String(20), default="stopped")  # running, stopped, error
    last_heartbeat = Column(DateTime(timezone=True))
    
    # Métriques de performance
    total_tasks = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    
    # Configuration
    config = Column(JSON)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relations
    logs = relationship("AgentLog", back_populates="agent")

class AgentLog(Base):
    """Logs détaillés des agents"""
    __tablename__ = "agent_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    
    # Informations du log
    level = Column(String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    
    # Contexte additionnel
    context = Column(JSON)
    
    # Timing
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Relations
    agent = relationship("Agent", back_populates="logs")
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        Index('idx_agent_log_time', 'agent_id', 'created_at'),
        Index('idx_agent_log_level', 'level'),
    )

class MarketData(Base):
    """Données de marché historiques"""
    __tablename__ = "market_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    
    # Prix OHLC
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    
    # Volume et spread
    volume = Column(Float)
    spread = Column(Float)
    
    # Indicateurs techniques
    adx = Column(Float)
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    bb_upper = Column(Float)
    bb_lower = Column(Float)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        Index('idx_market_data_symbol_time', 'symbol', 'timestamp'),
    )

class PerformanceMetrics(Base):
    """Métriques de performance agrégées"""
    __tablename__ = "performance_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Période de calcul
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Dimension d'analyse
    dimension = Column(String(50), nullable=False)  # strategy, symbol, hour, day
    dimension_value = Column(String(100), nullable=False)
    
    # Métriques de base
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # Métriques financières
    total_pnl = Column(Float, default=0.0)
    average_pnl = Column(Float, default=0.0)
    max_win = Column(Float, default=0.0)
    max_loss = Column(Float, default=0.0)
    
    # Métriques de risque
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    profit_factor = Column(Float)
    
    # Métriques de confiance
    average_confidence = Column(Float)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        Index('idx_performance_dimension', 'dimension', 'dimension_value'),
        Index('idx_performance_period', 'period_start', 'period_end'),
    )

class SystemEvent(Base):
    """Événements système pour audit"""
    __tablename__ = "system_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Type d'événement
    event_type = Column(String(50), nullable=False)
    
    # Description
    description = Column(Text, nullable=False)
    
    # Données additionnelles
    data = Column(JSON)
    
    # Sévérité
    severity = Column(String(20), default="info")  # debug, info, warning, error, critical
    
    # Timing
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        Index('idx_system_event_type_time', 'event_type', 'created_at'),
        Index('idx_system_event_severity', 'severity'),
    )

class Configuration(Base):
    """Configuration système avec versioning"""
    __tablename__ = "configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Clé de configuration
    key = Column(String(200), nullable=False)
    
    # Valeur
    value = Column(JSON, nullable=False)
    
    # Versioning
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Métadonnées
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    created_by = Column(String(100), default="system")
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        Index('idx_config_key_active', 'key', 'is_active'),
        Index('idx_config_version', 'version'),
    ) 