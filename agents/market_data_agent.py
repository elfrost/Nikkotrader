"""
Market Data Agent - Collecteur de données MT5 temps réel
Agent spécialisé dans la collecte de données de marché depuis MetaTrader 5
"""

import asyncio
import os
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Configuration simple sans dépendances externes
from dataclasses import dataclass

@dataclass
class SimpleConfig:
    """Configuration simplifiée pour l'agent"""
    redis_url: str = "redis://redis:6379"
    agent_type: str = "market"
    
    @classmethod
    def from_env(cls):
        return cls(
            redis_url=os.getenv("REDIS_URL", "redis://redis:6379"),
            agent_type=os.getenv("AGENT_TYPE", "market")
        )

# Simulation simple de Redis Manager
class SimpleRedisManager:
    """Manager Redis simplifié"""
    
    def __init__(self):
        self.connected = False
    
    async def set_agent_status(self, agent_name: str, status: Dict):
        """Simuler mise à jour statut Redis"""
        print(f"📊 Status {agent_name}: {status['status']}")
    
    async def set_market_data(self, symbol: str, data: Dict):
        """Simuler stockage données marché"""
        print(f"💹 {symbol}: {data['bid']}/{data['ask']} (spread: {data.get('spread_pips', 'N/A')} pips)")
    
    async def publish_market_data(self, symbol: str, data: Dict):
        """Simuler publication données"""
        pass

# Simulation simple de métriques
class SimpleMetrics:
    """Métriques simplifiées"""
    
    def __init__(self, agent_name: str, agent_type: str, port: int):
        self.agent_name = agent_name
        print(f"📊 Métriques {agent_name} sur port {port}")
    
    def start_server(self):
        """Simuler démarrage serveur métriques"""
        print(f"🔍 Serveur métriques démarré")

class MarketDataAgent:
    """
    Agent de collecte de données de marché depuis MT5
    Version simplifiée pour le trading sur compte démo
    """
    
    def __init__(self, config: SimpleConfig):
        self.config = config
        self.redis_manager = SimpleRedisManager()
        self.agent_name = "MarketDataAgent"
        self.status = "stopped"
        
        # Configuration MT5 (simulation uniquement en Docker)
        self.mt5_login = int(os.getenv("MT5_LOGIN", "51862230"))
        self.mt5_password = os.getenv("MT5_PASSWORD", "AiMwI&gG$26Z8i")
        self.mt5_server = os.getenv("MT5_SERVER", "ICMarkets-Demo")
        self.mt5_connected = False  # Toujours False en Docker
        
        # Paires à surveiller
        self.trading_pairs = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
            "EURGBP", "EURJPY", "EURCHF", "EURAUD", "EURCAD", "EURNZD",
            "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD"
        ]
        
        # État interne
        self.last_prices = {}
        self.scan_interval = 5  # Secondes
        self.error_count = 0
        self.max_errors = 10
        
        # Métriques
        self.total_scans = 0
        self.successful_scans = 0
        self.failed_scans = 0
        
        # Initialisation des métriques
        self.metrics = SimpleMetrics(self.agent_name, "market_data", 8080)
        
        print(f"🎯 {self.agent_name} initialisé")
    
    async def start(self):
        """Démarrage du Market Data Agent"""
        print(f"🚀 Démarrage du {self.agent_name}")
        
        self.status = "running"
        
        # Démarrer le serveur de métriques
        self.metrics.start_server()
        
        print("⚠️ Mode simulation activé (MT5 non disponible en Docker)")
        
        # Mettre à jour le statut dans Redis
        await self.redis_manager.set_agent_status(self.agent_name, {
            "status": "running",
            "last_heartbeat": datetime.now(timezone.utc).isoformat(),
            "mt5_connected": False,
            "simulation_mode": True,
            "total_scans": self.total_scans,
            "successful_scans": self.successful_scans,
            "failed_scans": self.failed_scans
        })
        
        # Démarrer les tâches principales
        await asyncio.gather(
            self.heartbeat_loop(),
            self.market_data_loop()
        )
    
    async def stop(self):
        """Arrêt du Market Data Agent"""
        print(f"🛑 Arrêt du {self.agent_name}")
        
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
                    "mt5_connected": False,
                    "simulation_mode": True,
                    "total_scans": self.total_scans,
                    "successful_scans": self.successful_scans,
                    "error_count": self.error_count
                })
                
                await asyncio.sleep(30)  # Heartbeat toutes les 30 secondes
                
            except Exception as e:
                print(f"❌ Erreur heartbeat: {e}")
                await asyncio.sleep(10)
    
    async def market_data_loop(self):
        """Boucle principale de collecte des données de marché"""
        while self.status == "running":
            try:
                await self.scan_market_data()
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                print(f"❌ Erreur scan marché: {e}")
                self.error_count += 1
                
                if self.error_count >= self.max_errors:
                    print("🚨 Trop d'erreurs - arrêt de l'agent")
                    self.status = "error"
                    break
                
                await asyncio.sleep(10)
    
    async def scan_market_data(self):
        """Scanner les données de marché - Mode simulation"""
        self.total_scans += 1
        
        try:
            await self.simulate_market_data()
            
        except Exception as e:
            self.failed_scans += 1
            print(f"❌ Erreur scan marché: {e}")
            raise
    
    async def simulate_market_data(self):
        """Simuler des données de marché réalistes"""
        import random
        
        try:
            # Prix de base simulés (mise à jour 18 juillet 2025)
            base_prices = {
                "EURUSD": 1.0920, "GBPUSD": 1.2680, "USDJPY": 151.20,
                "USDCHF": 0.9180, "AUDUSD": 0.6580, "USDCAD": 1.3620,
                "NZDUSD": 0.6080, "EURGBP": 0.8610, "EURJPY": 165.10,
                "EURCHF": 0.9750, "EURAUD": 1.6580, "EURCAD": 1.4880,
                "EURNZD": 1.7960, "GBPJPY": 191.80, "GBPCHF": 1.1640
            }
            
            for symbol in self.trading_pairs[:9]:  # Simuler 9 paires principales
                if symbol in base_prices:
                    base_price = base_prices[symbol]
                    
                    # Générer variation aléatoire (-0.05% à +0.05%)
                    variation = random.uniform(-0.0005, 0.0005)
                    bid = base_price * (1 + variation)
                    
                    # Spread typique selon la paire
                    if "JPY" in symbol:
                        spread_pips = random.uniform(0.8, 2.0)
                        point = 0.01
                        digits = 3
                    else:
                        spread_pips = random.uniform(0.5, 1.8)
                        point = 0.0001
                        digits = 5
                    
                    spread = spread_pips * point * 10
                    ask = bid + spread
                    
                    market_data = {
                        "symbol": symbol,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "bid": round(bid, digits),
                        "ask": round(ask, digits),
                        "last": round(bid, digits),
                        "volume": random.randint(50, 200),
                        "spread": round(spread, digits),
                        "spread_pips": round(spread_pips, 1),
                        "digits": digits,
                        "point": point,
                        "simulated": True,
                        "trade_allowed": True,
                        "market_hours": self.get_market_status()
                    }
                    
                    # Stocker et publier
                    await self.redis_manager.set_market_data(symbol, market_data)
                    await self.redis_manager.publish_market_data(symbol, market_data)
            
            self.successful_scans += 1
            print(f"📊 Scan simulation réussi: 9 paires (scan #{self.total_scans})")
            
        except Exception as e:
            self.failed_scans += 1
            print(f"❌ Erreur simulation: {e}")
    
    def get_market_status(self) -> str:
        """Obtenir le statut du marché selon l'heure"""
        current_hour = datetime.now(timezone.utc).hour
        
        if 22 <= current_hour or current_hour < 2:  # Session Asie
            return "ASIA_SESSION"
        elif 8 <= current_hour < 16:  # Session London
            return "LONDON_SESSION"
        elif 13 <= current_hour < 22:  # Session NYC (overlap)
            return "NYC_SESSION"
        else:
            return "LOW_LIQUIDITY"

# Point d'entrée principal
async def main():
    """Point d'entrée principal pour le Market Data Agent"""
    config = SimpleConfig.from_env()
    agent = MarketDataAgent(config)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("🛑 Interruption clavier détectée")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
    finally:
        await agent.stop()

if __name__ == "__main__":
    print("🚀 NIKKOTRADER V11.1.0 - Market Data Agent")
    print("📊 Collecteur de données de marché (mode simulation)")
    print("="*50)
    asyncio.run(main()) 