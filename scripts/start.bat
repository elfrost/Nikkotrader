@echo off
setlocal enabledelayedexpansion

REM Script de démarrage pour NIKKOTRADER V11 - Windows
REM Système de trading algorithmique multi-agents

title NIKKOTRADER V11 - Démarrage

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    NIKKOTRADER V11                           ║
echo ║              Système Multi-Agents de Trading                 ║
echo ║                                                              ║
echo ║  🚀 Démarrage de l'environnement de développement           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Vérifications préalables
echo 📋 Vérifications préalables...

REM Vérifier Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas installé
    pause
    exit /b 1
)

REM Vérifier Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose n'est pas installé
    pause
    exit /b 1
)

REM Vérifier que Docker est démarré
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas démarré
    echo 💡 Veuillez démarrer Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker est disponible et fonctionnel

REM Créer les dossiers nécessaires
echo 📁 Création des dossiers...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist monitoring mkdir monitoring
if not exist monitoring\prometheus mkdir monitoring\prometheus
if not exist monitoring\grafana mkdir monitoring\grafana
if not exist monitoring\grafana\dashboards mkdir monitoring\grafana\dashboards
if not exist monitoring\grafana\datasources mkdir monitoring\grafana\datasources

echo ✅ Dossiers créés

REM Créer le fichier .env s'il n'existe pas
if not exist .env (
    echo ⚙️ Création du fichier .env...
    (
        echo # NIKKOTRADER V11 Configuration
        echo.
        echo # Environnement
        echo ENVIRONMENT=development
        echo DEBUG=true
        echo.
        echo # Base de données
        echo DATABASE_URL=postgresql://nikkotrader:nikkotrader123@postgres:5432/nikkotrader_v11
        echo.
        echo # Redis
        echo REDIS_URL=redis://redis:6379
        echo.
        echo # Trading ^(COMPTE DEMO UNIQUEMENT^)
        echo MT5_LOGIN=51862230
        echo MT5_PASSWORD=AiMwI^&gG$26Z8i
        echo MT5_SERVER=ICMarkets-Demo
        echo.
        echo # Telegram
        echo TELEGRAM_BOT_TOKEN=8069695013:AAFs7M8knILYIS_NacS2QlIGUVEiZWLmlj0
        echo TELEGRAM_CHAT_ID=-1002272137953
        echo.
        echo # Sécurité
        echo SECRET_KEY=change-this-secret-key-in-production
        echo.
        echo # Forward Testing
        echo FORWARD_TESTING_MODE=true
        echo DEMO_ACCOUNT_ONLY=true
    ) > .env
    echo ✅ Fichier .env créé
)

REM Démarrer les services
echo 🚀 Démarrage des services...

REM Construire et démarrer les services
echo 📦 Construction des images Docker...
docker-compose build --no-cache

echo 🔄 Démarrage des services...
docker-compose up -d

REM Attendre que les services soient prêts
echo ⏳ Attente du démarrage des services...
timeout /t 10 /nobreak >nul

REM Vérifier l'état des services
echo 🔍 Vérification de l'état des services...

REM Vérifier PostgreSQL
docker-compose exec postgres pg_isready -U nikkotrader >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL est prêt
) else (
    echo ❌ PostgreSQL n'est pas prêt
)

REM Vérifier Redis
docker-compose exec redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis est prêt
) else (
    echo ❌ Redis n'est pas prêt
)

REM Vérifier l'API
timeout /t 5 /nobreak >nul
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API Backend est prête
) else (
    echo ⚠️ API Backend en cours de démarrage...
)

REM Afficher les informations de connexion
echo.
echo 🎉 NIKKOTRADER V11 est démarré !
echo.
echo 📊 Accès aux services :
echo • Dashboard Frontend : http://localhost:3000
echo • API Backend        : http://localhost:8000
echo • API Documentation  : http://localhost:8000/docs
echo • Grafana Monitoring : http://localhost:3001 (admin/admin123)
echo • Prometheus         : http://localhost:9090
echo • RabbitMQ           : http://localhost:15672 (nikkotrader/nikkotrader123)

echo.
echo 📋 Commandes utiles :
echo • Voir les logs      : docker-compose logs -f
echo • Arrêter le système : docker-compose down
echo • Redémarrer         : docker-compose restart
echo • État des services  : docker-compose ps

echo.
echo 🔍 Monitoring :
echo • Logs des agents    : docker-compose logs -f master-agent
echo • Logs de l'API      : docker-compose logs -f api
echo • Logs du frontend   : docker-compose logs -f frontend

echo.
echo ⚡ Le système est maintenant prêt pour les forward tests !
echo ⚠️ Rappel : Ce système fonctionne uniquement avec un compte DEMO
echo.

echo 📜 Logs en temps réel (Ctrl+C pour arrêter) :
docker-compose logs -f 