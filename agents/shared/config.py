"""
Configuration temporaire pour les agents
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class AgentConfig:
    """Configuration pour un agent"""
    name: str = "Agent"
    type: str = "market"
    agent_type: str = "market"
    redis_url: str = "redis://redis:6379"
    api_url: str = "http://api:8000"
    debug: bool = True
    max_concurrent_tasks: int = 10
    retry_attempts: int = 3
    heartbeat_interval: int = 30
    
    def __post_init__(self):
        """Post-initialization"""
        # Synchroniser agent_type et type
        if self.type and not self.agent_type:
            self.agent_type = self.type
        elif self.agent_type and not self.type:
            self.type = self.agent_type
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Créer la configuration depuis les variables d'environnement"""
        import os
        return cls(
            name=os.getenv("AGENT_NAME", "Agent"),
            type=os.getenv("AGENT_TYPE", "market"),
            agent_type=os.getenv("AGENT_TYPE", "market"),
            redis_url=os.getenv("REDIS_URL", "redis://redis:6379"),
            api_url=os.getenv("API_URL", "http://api:8000"),
            debug=os.getenv("DEBUG", "true").lower() == "true",
            max_concurrent_tasks=int(os.getenv("MAX_CONCURRENT_TASKS", "10")),
            retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
            heartbeat_interval=int(os.getenv("HEARTBEAT_INTERVAL", "30"))
        ) 