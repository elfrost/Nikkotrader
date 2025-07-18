"""
Master Agent - Orchestrateur principal du système NIKKOTRADER V11
Utilise CrewAI pour coordonner tous les agents spécialisés
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI
from langchain.tools import BaseTool
import redis.asyncio as redis
from loguru import logger

from shared.config import AgentConfig
from shared.redis_manager import RedisManager
from shared.models import TradingSignal, AgentStatus, SystemEvent
from shared.metrics import MetricsExporter

# Import conditionnel des agents spécialisés
try:
    from market_data_agent import MarketDataAgent
except ImportError:
    MarketDataAgent = None

@dataclass
class AgentTask:
    """Représente une tâche assignée à un agent"""
    id: str
    agent_name: str
    task_type: str
    priority: int
    data: Dict[str, Any]
    created_at: datetime
    status: str = "pending"

class MasterAgent:
    """
    Agent Master - Orchestrateur principal du système
    Coordonne tous les agents spécialisés et prend les décisions finales
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.redis_manager = RedisManager()
        self.agent_name = "MasterAgent"
        self.status = "stopped"
        self.heartbeat_interval = 30
        
        # Agents spécialisés
        self.specialized_agents = {}
        self.active_tasks = {}
        self.signal_queue = []
        
        # Métriques
        self.total_decisions = 0
        self.successful_decisions = 0
        self.failed_decisions = 0
        
        # Configuration CrewAI
        self.crew = None
        self.setup_crew()
        
        # Initialisation des métriques Prometheus
        self.metrics = MetricsExporter(self.agent_name, "master", 8080)
        
        logger.info(f"🎯 {self.agent_name} initialisé")
    
    def setup_crew(self):
        """Configuration de l'équipe CrewAI"""
        
        # Agent principal de décision
        decision_agent = Agent(
            role="Trading Decision Coordinator",
            goal="Coordonner les décisions de trading en analysant les signaux de tous les agents spécialisés",
            backstory="""
            Je suis l'orchestrateur principal d'un système de trading algorithmique multi-agents.
            Ma mission est de collecter les signaux de tous les agents spécialisés,
            d'analyser leur qualité et leur cohérence, puis de prendre les décisions finales
            pour maximiser les performances tout en minimisant les risques.
            """,
            verbose=True,
            allow_delegation=False
        )
        
        # Agent de gestion des risques
        risk_agent = Agent(
            role="Risk Management Specialist",
            goal="Évaluer et filtrer les signaux selon les critères de risque définis",
            backstory="""
            Je suis spécialisé dans l'analyse des risques. J'évalue chaque signal
            selon les critères de drawdown, corrélation, et exposition.
            Je peux rejeter des signaux qui ne respectent pas les limites de risque.
            """,
            verbose=True,
            allow_delegation=False
        )
        
        # Agent de performance
        performance_agent = Agent(
            role="Performance Analyst",
            goal="Analyser les performances historiques pour optimiser les décisions futures",
            backstory="""
            J'analyse en continu les performances des stratégies et des agents.
            J'identifie les patterns de succès et d'échec pour améliorer
            les critères de décision et l'allocation des ressources.
            """,
            verbose=True,
            allow_delegation=False
        )
        
        # Créer l'équipe
        self.crew = Crew(
            agents=[decision_agent, risk_agent, performance_agent],
            tasks=[],  # Les tâches seront ajoutées dynamiquement
            verbose=True,
            process=Process.sequential
        )
    
    async def start(self):
        """Démarrage du Master Agent"""
        logger.info(f"🚀 Démarrage du {self.agent_name}")
        
        self.status = "running"
        
        # Démarrer le serveur de métriques Prometheus
        self.metrics.start_server()
        
        # Mettre à jour le statut dans Redis
        await self.redis_manager.set_agent_status(self.agent_name, {
            "status": "running",
            "last_heartbeat": datetime.now(timezone.utc).isoformat(),
            "total_tasks": self.total_decisions,
            "successful_tasks": self.successful_decisions,
            "failed_tasks": self.failed_decisions
        })
        
        # Démarrer les tâches principales
        await asyncio.gather(
            self.heartbeat_loop(),
            self.signal_processing_loop(),
            self.agent_monitoring_loop(),
            self.decision_making_loop()
        )
    
    async def stop(self):
        """Arrêt du Master Agent"""
        logger.info(f"🛑 Arrêt du {self.agent_name}")
        
        self.status = "stopped"
        
        # Mettre à jour le statut dans Redis
        await self.redis_manager.set_agent_status(self.agent_name, {
            "status": "stopped",
            "last_heartbeat": datetime.now(timezone.utc).isoformat()
        })
    
    async def heartbeat_loop(self):
        """Boucle de heartbeat pour maintenir le statut de l'agent"""
        while self.status == "running":
            try:
                await self.redis_manager.set_agent_status(self.agent_name, {
                    "status": "running",
                    "last_heartbeat": datetime.now(timezone.utc).isoformat(),
                    "total_decisions": self.total_decisions,
                    "successful_decisions": self.successful_decisions,
                    "failed_decisions": self.failed_decisions
                })
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"❌ Erreur heartbeat: {e}")
                await asyncio.sleep(10)
    
    async def signal_processing_loop(self):
        """Boucle de traitement des signaux de trading"""
        while self.status == "running":
            try:
                # Traiter les signaux en attente
                await self.process_pending_signals()
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Erreur traitement signaux: {e}")
                await asyncio.sleep(5)
    
    async def agent_monitoring_loop(self):
        """Boucle de surveillance des autres agents"""
        while self.status == "running":
            try:
                await self.monitor_agents_health()
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Erreur surveillance agents: {e}")
                await asyncio.sleep(10)
    
    async def decision_making_loop(self):
        """Boucle de prise de décision principale"""
        while self.status == "running":
            try:
                await self.make_trading_decisions()
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Erreur prise de décision: {e}")
                await asyncio.sleep(10)
    
    async def process_pending_signals(self):
        """Traiter les signaux de trading en attente"""
        try:
            # Récupérer les signaux depuis Redis
            signals = await self.redis_manager.get_pending_signals()
            
            for signal in signals:
                await self.analyze_signal(signal)
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement signaux: {e}")
    
    async def analyze_signal(self, signal: Dict):
        """Analyser un signal de trading"""
        try:
            self.total_decisions += 1
            
            # Logique d'analyse du signal
            # Ici on peut ajouter des critères de validation
            
            logger.info(f"📊 Signal analysé: {signal.get('symbol', 'Unknown')}")
            self.successful_decisions += 1
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse signal: {e}")
            self.failed_decisions += 1
    
    async def monitor_agents_health(self):
        """Surveiller la santé des autres agents"""
        try:
            # Vérifier le statut des agents
            agents_status = await self.redis_manager.get_all_agents_status()
            
            for agent_name, status in agents_status.items():
                if status.get("status") != "running":
                    logger.warning(f"⚠️ Agent {agent_name} non actif: {status.get('status')}")
                    
        except Exception as e:
            logger.error(f"❌ Erreur surveillance agents: {e}")
    
    async def make_trading_decisions(self):
        """Prendre des décisions de trading basées sur les signaux analysés"""
        try:
            # Logique de décision de trading
            # Ici on peut implémenter la logique CrewAI pour les décisions complexes
            pass
            
        except Exception as e:
            logger.error(f"❌ Erreur prise de décision trading: {e}")

# Point d'entrée principal avec détection du type d'agent
async def main():
    """Point d'entrée principal - détecte et lance le bon type d'agent"""
    agent_type = os.getenv("AGENT_TYPE", "master").lower()
    config = AgentConfig.from_env()
    
    logger.info(f"🎯 Lancement de l'agent type: {agent_type}")
    
    try:
        if agent_type == "market" and MarketDataAgent:
            # Lancer l'agent de données de marché
            agent = MarketDataAgent(config)
            await agent.start()
            
        elif agent_type in ["master", "strategy", "risk", "performance", "notification"]:
            # Lancer l'agent master (pour l'instant tous utilisent le même code)
            agent = MasterAgent(config)
            await agent.start()
            
        else:
            logger.error(f"❌ Type d'agent inconnu: {agent_type}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Interruption clavier détectée")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
    finally:
        if 'agent' in locals():
            await agent.stop()

if __name__ == "__main__":
    asyncio.run(main()) 