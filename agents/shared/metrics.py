"""
Module de métriques Prometheus pour les agents NIKKOTRADER V11
Système d'options binaires avec expiration
"""

import time
import asyncio
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, start_http_server, generate_latest
from prometheus_client.core import CollectorRegistry
from loguru import logger
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

class MetricsExporter:
    """Exportateur de métriques Prometheus pour les agents"""
    
    def __init__(self, agent_name: str, agent_type: str, port: int = 8080):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.port = port
        self.registry = CollectorRegistry()
        self.server = None
        self.server_thread = None
        
        # Métriques spécifiques aux options binaires
        self.setup_metrics()
        
    def setup_metrics(self):
        """Configuration des métriques Prometheus"""
        
        # Agent Health Metrics
        self.agent_heartbeat = Gauge(
            'nikkotrader_agent_heartbeat_timestamp',
            'Timestamp du dernier heartbeat de l\'agent',
            ['agent_name', 'agent_type'],
            registry=self.registry
        )
        
        self.agent_tasks_total = Counter(
            'nikkotrader_agent_tasks_total',
            'Nombre total de tâches exécutées par l\'agent',
            ['agent_name', 'agent_type', 'status'],
            registry=self.registry
        )
        
        # Trading Metrics (Options Binaires)
        self.signals_total = Counter(
            'nikkotrader_signals_total',
            'Nombre total de signaux générés',
            ['agent_name', 'strategy', 'symbol', 'direction'],
            registry=self.registry
        )
        
        self.signal_confidence = Histogram(
            'nikkotrader_signal_confidence',
            'Distribution de la confiance des signaux',
            ['agent_name', 'strategy'],
            buckets=[0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
            registry=self.registry
        )
        
        self.trades_total = Counter(
            'nikkotrader_trades_total',
            'Nombre total de trades exécutés',
            ['agent_name', 'strategy', 'symbol', 'direction', 'result'],
            registry=self.registry
        )
        
        self.trade_expiry_minutes = Histogram(
            'nikkotrader_trade_expiry_minutes',
            'Distribution des temps d\'expiration des trades',
            ['strategy'],
            buckets=[1, 3, 5, 10, 15, 30, 60],
            registry=self.registry
        )
        
        # Performance Metrics
        self.daily_pnl = Gauge(
            'nikkotrader_daily_pnl',
            'P&L quotidien en cours',
            ['agent_name'],
            registry=self.registry
        )
        
        self.win_rate = Gauge(
            'nikkotrader_win_rate',
            'Taux de réussite actuel (0-1)',
            ['agent_name', 'strategy'],
            registry=self.registry
        )
        
        self.active_trades = Gauge(
            'nikkotrader_active_trades',
            'Nombre de trades actifs en cours',
            ['agent_name'],
            registry=self.registry
        )
        
        self.drawdown_percentage = Gauge(
            'nikkotrader_drawdown_percentage',
            'Pourcentage de drawdown actuel',
            ['agent_name'],
            registry=self.registry
        )
        
        # Risk Metrics
        self.risk_score = Histogram(
            'nikkotrader_risk_score',
            'Distribution des scores de risque',
            ['agent_name', 'strategy'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        # System Metrics
        self.processing_duration = Histogram(
            'nikkotrader_processing_duration_seconds',
            'Durée de traitement des tâches',
            ['agent_name', 'task_type'],
            registry=self.registry
        )
        
        # Market Data Metrics
        self.market_data_updates = Counter(
            'nikkotrader_market_data_updates_total',
            'Nombre de mises à jour des données de marché',
            ['agent_name', 'symbol'],
            registry=self.registry
        )
        
        # Notifications Metrics
        self.notifications_sent = Counter(
            'nikkotrader_notifications_sent_total',
            'Nombre de notifications envoyées',
            ['agent_name', 'channel', 'type'],
            registry=self.registry
        )

    def start_server(self):
        """Démarrer le serveur HTTP pour exposer les métriques"""
        try:
            # Vérifier si le port est libre
            if self.is_port_in_use(self.port):
                logger.warning(f"Port {self.port} déjà utilisé, tentative port suivant")
                self.port += 1
            
            # Créer la classe handler pour Prometheus
            class MetricsHandler(BaseHTTPRequestHandler):
                def __init__(self, request, client_address, server, registry=None):
                    self.registry = registry or self.registry
                    super().__init__(request, client_address, server)
                
                def do_GET(self):
                    """Handler pour les requêtes GET /metrics"""
                    if self.path == '/metrics':
                        try:
                            output = generate_latest(self.registry)
                            self.send_response(200)
                            self.send_header('Content-Type', 'text/plain; charset=utf-8') # Changed from CONTENT_TYPE_LATEST to 'text/plain; charset=utf-8'
                            self.send_header('Content-Length', str(len(output)))
                            self.end_headers()
                            self.wfile.write(output)
                        except Exception as e:
                            self.send_error(500, f"Error generating metrics: {e}")
                    else:
                        self.send_error(404, "Not Found")
                
                def log_message(self, format, *args):
                    # Supprimer les logs HTTP pour éviter le spam
                    pass
            
            # Factory pour passer le registry
            def handler_factory(registry):
                def handler(request, client_address, server):
                    return MetricsHandler(request, client_address, server, registry)
                return handler
            
            self.server = HTTPServer(('0.0.0.0', self.port), handler_factory(self.registry))
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            logger.info(f"🔍 Serveur métriques Prometheus démarré sur port {self.port} pour {self.agent_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage serveur métriques: {str(e)}")
    
    def stop_server(self):
        """Arrêter le serveur HTTP"""
        if self.server:
            self.server.shutdown()
            logger.info(f"🛑 Serveur métriques arrêté pour {self.agent_name}")
    
    def is_port_in_use(self, port: int) -> bool:
        """Vérifier si un port est déjà utilisé"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    # Méthodes pour mettre à jour les métriques
    
    def update_heartbeat(self):
        """Mettre à jour le heartbeat"""
        self.agent_heartbeat.labels(
            agent_name=self.agent_name,
            agent_type=self.agent_type
        ).set_to_current_time()
    
    def record_task(self, status: str):
        """Enregistrer une tâche exécutée"""
        self.agent_tasks_total.labels(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            status=status
        ).inc()
    
    def record_signal(self, strategy: str, symbol: str, direction: str, confidence: float):
        """Enregistrer un signal généré"""
        self.signals_total.labels(
            agent_name=self.agent_name,
            strategy=strategy,
            symbol=symbol,
            direction=direction
        ).inc()
        
        self.signal_confidence.labels(
            agent_name=self.agent_name,
            strategy=strategy
        ).observe(confidence)
    
    def record_trade(self, strategy: str, symbol: str, direction: str, result: str, 
                    expiry_minutes: int, pnl: float = None):
        """Enregistrer un trade exécuté"""
        self.trades_total.labels(
            agent_name=self.agent_name,
            strategy=strategy,
            symbol=symbol,
            direction=direction,
            result=result
        ).inc()
        
        self.trade_expiry_minutes.labels(
            strategy=strategy
        ).observe(expiry_minutes)
    
    def update_performance(self, daily_pnl: float, win_rate: float, active_trades: int, 
                          drawdown: float, strategy: str = None):
        """Mettre à jour les métriques de performance"""
        self.daily_pnl.labels(agent_name=self.agent_name).set(daily_pnl)
        self.active_trades.labels(agent_name=self.agent_name).set(active_trades)
        self.drawdown_percentage.labels(agent_name=self.agent_name).set(drawdown * 100)
        
        if strategy:
            self.win_rate.labels(agent_name=self.agent_name, strategy=strategy).set(win_rate)
    
    def record_processing_time(self, task_type: str, duration: float):
        """Enregistrer le temps de traitement"""
        self.processing_duration.labels(
            agent_name=self.agent_name,
            task_type=task_type
        ).observe(duration)
    
    def record_notification(self, channel: str, notification_type: str):
        """Enregistrer une notification envoyée"""
        self.notifications_sent.labels(
            agent_name=self.agent_name,
            channel=channel,
            type=notification_type
        ).inc()
    
    def record_market_data_update(self, symbol: str):
        """Enregistrer une mise à jour de données de marché"""
        self.market_data_updates.labels(
            agent_name=self.agent_name,
            symbol=symbol
        ).inc() 