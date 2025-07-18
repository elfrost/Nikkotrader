"""
Master Agent - Orchestrateur principal du système NIKKOTRADER V11
Utilise CrewAI pour coordonner tous les agents spécialisés
"""

import asyncio
import json
import logging
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
        """Boucle de heartbeat pour indiquer que l'agent est vivant"""
        while self.status == "running":
            try:
                # Mettre à jour Redis
                await self.redis_manager.set_agent_status(self.agent_name, {
                    "status": "running",
                    "last_heartbeat": datetime.now(timezone.utc).isoformat(),
                    "total_tasks": self.total_decisions,
                    "successful_tasks": self.successful_decisions,
                    "failed_tasks": self.failed_decisions
                })
                
                # Mettre à jour les métriques Prometheus
                self.metrics.update_heartbeat()
                self.metrics.update_performance(
                    daily_pnl=0,  # À calculer selon vos données
                    win_rate=self.successful_decisions / max(self.total_decisions, 1),
                    active_trades=len(self.active_tasks),
                    drawdown=0  # À calculer selon vos données
                )
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"❌ Erreur dans heartbeat: {str(e)}")
                self.metrics.record_task("failed")
                await asyncio.sleep(5)
    
    async def signal_processing_loop(self):
        """Boucle de traitement des signaux entrants"""
        while self.status == "running":
            try:
                # Écouter les signaux des agents spécialisés
                signals = await self.redis_manager.get_pending_signals()
                
                for signal in signals:
                    await self.process_signal(signal)
                
                await asyncio.sleep(1)  # Vérification toutes les secondes
                
            except Exception as e:
                logger.error(f"❌ Erreur dans signal processing: {str(e)}")
                await asyncio.sleep(5)
    
    async def agent_monitoring_loop(self):
        """Surveillance des agents spécialisés"""
        while self.status == "running":
            try:
                # Vérifier l'état de tous les agents
                agents_status = await self.redis_manager.get_all_agents_status()
                
                for agent_name, status in agents_status.items():
                    if agent_name != self.agent_name:
                        await self.check_agent_health(agent_name, status)
                
                await asyncio.sleep(30)  # Vérification toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"❌ Erreur dans agent monitoring: {str(e)}")
                await asyncio.sleep(10)
    
    async def decision_making_loop(self):
        """Boucle de prise de décision principale"""
        while self.status == "running":
            try:
                # Traiter la queue des signaux
                if self.signal_queue:
                    signals_batch = self.signal_queue[:10]  # Traiter par batch de 10
                    self.signal_queue = self.signal_queue[10:]
                    
                    decision = await self.make_trading_decision(signals_batch)
                    
                    if decision:
                        await self.execute_decision(decision)
                
                await asyncio.sleep(5)  # Décisions toutes les 5 secondes
                
            except Exception as e:
                logger.error(f"❌ Erreur dans decision making: {str(e)}")
                await asyncio.sleep(10)
    
    async def process_signal(self, signal: Dict[str, Any]):
        """Traiter un signal entrant"""
        try:
            logger.info(f"📊 Traitement du signal: {signal['symbol']} - {signal['strategy']}")
            
            # Ajouter le signal à la queue pour traitement
            self.signal_queue.append(signal)
            
            # Mettre à jour les métriques
            self.total_decisions += 1
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement du signal: {str(e)}")
            self.failed_decisions += 1
    
    async def make_trading_decision(self, signals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Prendre une décision de trading basée sur les signaux"""
        try:
            if not signals:
                return None
            
            # Créer une tâche pour l'équipe CrewAI
            decision_task = Task(
                description=f"""
                Analyser les signaux de trading suivants et prendre une décision:
                {json.dumps(signals, indent=2)}
                
                Critères à évaluer:
                1. Qualité des signaux (confiance, cohérence)
                2. Risque/rendement
                3. Corrélations entre paires
                4. Conditions de marché actuelles
                5. Limites de risque
                
                Retourner une décision structurée avec:
                - Action recommandée (EXECUTE, REJECT, WAIT)
                - Signaux sélectionnés
                - Justification
                - Score de confiance
                """,
                agent=self.crew.agents[0]
            )
            
            # Exécuter la tâche
            result = self.crew.kickoff([decision_task])
            
            # Parser le résultat
            decision = await self.parse_crew_decision(result)
            
            if decision and decision.get("action") == "EXECUTE":
                self.successful_decisions += 1
                return decision
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la prise de décision: {str(e)}")
            self.failed_decisions += 1
            return None
    
    async def parse_crew_decision(self, crew_result: Any) -> Optional[Dict[str, Any]]:
        """Parser le résultat de l'équipe CrewAI"""
        try:
            # Extraire la décision du résultat CrewAI
            # (Implémentation spécifique selon le format de retour)
            
            return {
                "action": "EXECUTE",
                "signals": [],
                "justification": "Test decision",
                "confidence": 0.75,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du parsing de la décision: {str(e)}")
            return None
    
    async def execute_decision(self, decision: Dict[str, Any]):
        """Exécuter une décision de trading"""
        try:
            logger.info(f"🎯 Exécution de la décision: {decision['action']}")
            
            # Publier la décision pour les autres agents
            await self.redis_manager.publish_decision(decision)
            
            # Enregistrer l'événement
            await self.redis_manager.log_system_event({
                "event_type": "trading.decision_executed",
                "agent": self.agent_name,
                "decision": decision,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution de la décision: {str(e)}")
    
    async def check_agent_health(self, agent_name: str, status: Dict[str, Any]):
        """Vérifier la santé d'un agent spécialisé"""
        try:
            last_heartbeat = datetime.fromisoformat(status.get("last_heartbeat", "1970-01-01T00:00:00+00:00"))
            time_since_heartbeat = (datetime.now(timezone.utc) - last_heartbeat).total_seconds()
            
            if time_since_heartbeat > 60:  # Plus de 1 minute sans heartbeat
                logger.warning(f"⚠️ Agent {agent_name} n'a pas donné signe de vie depuis {time_since_heartbeat}s")
                
                # Essayer de redémarrer l'agent
                await self.restart_agent(agent_name)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification de l'agent {agent_name}: {str(e)}")
    
    async def restart_agent(self, agent_name: str):
        """Redémarrer un agent défaillant"""
        try:
            logger.info(f"🔄 Redémarrage de l'agent {agent_name}")
            
            # Envoyer un signal de redémarrage
            await self.redis_manager.send_agent_command(agent_name, {
                "command": "restart",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du redémarrage de l'agent {agent_name}: {str(e)}")

# Point d'entrée principal
async def main():
    """Point d'entrée principal du Master Agent"""
    
    # Configuration
    config = AgentConfig(
        name="MasterAgent",
        type="master",
        redis_url="redis://localhost:6379",
        max_concurrent_tasks=10,
        heartbeat_interval=30
    )
    
    # Créer et démarrer le Master Agent
    master = MasterAgent(config)
    
    try:
        await master.start()
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur critique: {str(e)}")
    finally:
        await master.stop()

if __name__ == "__main__":
    asyncio.run(main()) 