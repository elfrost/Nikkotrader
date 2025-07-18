"""
Gestionnaire Redis temporaire
"""

import asyncio
import redis.asyncio as aioredis
from typing import Optional, Any, Dict, List
from loguru import logger
import json
from datetime import datetime

class RedisManager:
    """Gestionnaire de connexion Redis"""
    
    def __init__(self, redis_url: str = "redis://redis:6379"):
        self.redis_url = redis_url
        self.redis = None
    
    async def connect(self) -> None:
        """Se connecter à Redis"""
        try:
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info(f"Connecté à Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"Erreur de connexion à Redis: {e}")
            self.redis = None
    
    async def disconnect(self) -> None:
        """Se déconnecter de Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Déconnecté de Redis")
    
    async def publish(self, channel: str, message: str) -> None:
        """Publier un message"""
        if self.redis:
            await self.redis.publish(channel, message)
    
    async def subscribe(self, channel: str):
        """S'abonner à un canal"""
        if self.redis:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel)
            return pubsub
        return None
    
    async def set_agent_status(self, agent_name: str, status: Dict[str, Any]) -> None:
        """Définir le statut d'un agent"""
        if self.redis:
            try:
                key = f"agent_status:{agent_name}"
                status["timestamp"] = datetime.now().isoformat()
                await self.redis.set(key, json.dumps(status))
                logger.info(f"Statut mis à jour pour {agent_name}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du statut: {e}")
    
    async def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Récupérer le statut d'un agent"""
        if self.redis:
            try:
                key = f"agent_status:{agent_name}"
                status = await self.redis.get(key)
                if status:
                    return json.loads(status)
            except Exception as e:
                logger.error(f"Erreur lors de la récupération du statut: {e}")
        return None
    
    async def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Récupérer le statut de tous les agents"""
        if self.redis:
            try:
                pattern = "agent_status:*"
                keys = await self.redis.keys(pattern)
                agents_status = {}
                
                for key in keys:
                    agent_name = key.decode().replace("agent_status:", "")
                    status_data = await self.redis.get(key)
                    if status_data:
                        agents_status[agent_name] = json.loads(status_data)
                
                return agents_status
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de tous les statuts: {e}")
        return {}
    
    async def add_pending_signal(self, signal: Dict[str, Any]) -> None:
        """Ajouter un signal en attente"""
        if self.redis:
            try:
                signal["timestamp"] = datetime.now().isoformat()
                signal["id"] = f"signal_{datetime.now().timestamp()}"
                await self.redis.lpush("pending_signals", json.dumps(signal))
                logger.info(f"Signal ajouté: {signal.get('id')}")
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout du signal: {e}")
    
    async def get_pending_signals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupérer les signaux en attente"""
        if self.redis:
            try:
                signals_data = await self.redis.lrange("pending_signals", 0, limit - 1)
                signals = []
                for signal_data in signals_data:
                    try:
                        signal = json.loads(signal_data)
                        signals.append(signal)
                    except json.JSONDecodeError as e:
                        logger.error(f"Erreur de décodage du signal: {e}")
                
                # Supprimer les signaux récupérés
                if signals:
                    await self.redis.ltrim("pending_signals", len(signals), -1)
                
                return signals
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des signaux: {e}")
        return []
    
    async def set_key(self, key: str, value: Any, expire: int = None) -> None:
        """Définir une clé avec une valeur optionnellement avec expiration"""
        if self.redis:
            try:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                await self.redis.set(key, value, ex=expire)
            except Exception as e:
                logger.error(f"Erreur lors de la définition de la clé {key}: {e}")
    
    async def get_key(self, key: str) -> Optional[Any]:
        """Récupérer une valeur par clé"""
        if self.redis:
            try:
                value = await self.redis.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value.decode()
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de la clé {key}: {e}")
        return None
    
    async def delete_key(self, key: str) -> bool:
        """Supprimer une clé"""
        if self.redis:
            try:
                result = await self.redis.delete(key)
                return result > 0
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de la clé {key}: {e}")
        return False 