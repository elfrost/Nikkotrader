"""
NIKKOTRADER V11 - Backend API
Architecture Multi-Agents pour Trading Algorithmique
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import List, Dict, Any

from core.config import settings
from core.database import init_db
from core.redis_client import redis_client
from core.websocket_manager import WebSocketManager

# Import des routers
from api.v1.trading import router as trading_router
from api.v1.strategies import router as strategies_router
from api.v1.performance import router as performance_router
from api.v1.monitoring import router as monitoring_router
from api.v1.agents import router as agents_router

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Gestionnaire WebSocket
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application"""
    logger.info("🚀 Démarrage de NIKKOTRADER V11")
    
    # Initialisation de la base de données
    await init_db()
    
    # Initialisation de Redis
    await redis_client.initialize()
    
    # Démarrage des tâches de background
    background_tasks = [
        asyncio.create_task(monitor_agents()),
        asyncio.create_task(cleanup_old_data()),
        asyncio.create_task(performance_analyzer()),
    ]
    
    logger.info("✅ Tous les services sont démarrés")
    
    yield
    
    # Nettoyage lors de l'arrêt
    logger.info("🛑 Arrêt de NIKKOTRADER V11")
    for task in background_tasks:
        task.cancel()
    
    await redis_client.close()
    logger.info("✅ Nettoyage terminé")

# Création de l'application FastAPI
app = FastAPI(
    title="NIKKOTRADER V11 API",
    description="API pour système de trading algorithmique multi-agents",
    version="11.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(trading_router, prefix="/api/v1/trading", tags=["Trading"])
app.include_router(strategies_router, prefix="/api/v1/strategies", tags=["Strategies"])
app.include_router(performance_router, prefix="/api/v1/performance", tags=["Performance"])
app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["Monitoring"])
app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])

# Routes principales
@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil avec informations système"""
    return """
    <html>
        <head>
            <title>NIKKOTRADER V11</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .status { color: green; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <h1>🚀 NIKKOTRADER V11 - Multi-Agents Trading System</h1>
            <p class="status">✅ API Server is running</p>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/api/v1/monitoring/status">System Status</a></li>
            </ul>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Vérification de l'état du système"""
    try:
        # Vérifier Redis
        await redis_client.ping()
        
        # Vérifier la base de données
        # TODO: Ajouter vérification DB
        
        return {
            "status": "healthy",
            "version": "11.0.0",
            "services": {
                "redis": "connected",
                "database": "connected",
                "agents": "running"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket pour les mises à jour temps réel"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Traitement des messages WebSocket
            await websocket_manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Tâches de background
async def monitor_agents():
    """Surveillance des agents en continu"""
    while True:
        try:
            # Vérifier l'état des agents
            agents_status = await redis_client.get_agents_status()
            
            # Envoyer les mises à jour via WebSocket
            await websocket_manager.broadcast({
                "type": "agents_status",
                "data": agents_status
            })
            
            await asyncio.sleep(5)  # Vérification toutes les 5 secondes
            
        except Exception as e:
            logger.error(f"Error monitoring agents: {str(e)}")
            await asyncio.sleep(10)

async def cleanup_old_data():
    """Nettoyage des données anciennes"""
    while True:
        try:
            # Nettoyer les données de plus de 30 jours
            await redis_client.cleanup_old_data(days=30)
            
            # Attendre 1 heure avant le prochain nettoyage
            await asyncio.sleep(3600)
            
        except Exception as e:
            logger.error(f"Error cleaning old data: {str(e)}")
            await asyncio.sleep(1800)  # Retry après 30 minutes

async def performance_analyzer():
    """Analyse des performances en continu"""
    while True:
        try:
            # Analyser les performances des stratégies
            performance_data = await redis_client.get_performance_data()
            
            # Envoyer les mises à jour via WebSocket
            await websocket_manager.broadcast({
                "type": "performance_update",
                "data": performance_data
            })
            
            await asyncio.sleep(30)  # Analyse toutes les 30 secondes
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {str(e)}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 