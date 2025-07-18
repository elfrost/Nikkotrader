"""
Modèles de données temporaires
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class SignalType(Enum):
    """Types de signaux de trading"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class AgentStatusType(Enum):
    """États des agents"""
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"

@dataclass
class TradingSignal:
    """Signal de trading"""
    symbol: str
    signal_type: SignalType
    price: float
    timestamp: datetime
    confidence: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AgentStatus:
    """Statut d'un agent"""
    agent_id: str
    status: AgentStatusType
    timestamp: datetime
    message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SystemEvent:
    """Événement système"""
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    
    def __post_init__(self):
        if self.data is None:
            self.data = {} 