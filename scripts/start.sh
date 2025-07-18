#!/bin/bash

# Script de démarrage pour NIKKOTRADER V11
# Système de trading algorithmique multi-agents

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    NIKKOTRADER V11                           ║"
echo "║              Système Multi-Agents de Trading                 ║"
echo "║                                                              ║"
echo "║  🚀 Démarrage de l'environnement de développement           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Vérifications préalables
echo -e "${YELLOW}📋 Vérifications préalables...${NC}"

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    exit 1
fi

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
    exit 1
fi

# Vérifier que Docker est démarré
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas démarré${NC}"
    echo -e "${YELLOW}💡 Veuillez démarrer Docker Desktop${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker est disponible et fonctionnel${NC}"

# Créer les dossiers nécessaires
echo -e "${YELLOW}📁 Création des dossiers...${NC}"
mkdir -p logs
mkdir -p data
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

echo -e "${GREEN}✅ Dossiers créés${NC}"

# Créer le fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚙️ Création du fichier .env...${NC}"
    cat > .env << EOF
# NIKKOTRADER V11 Configuration

# Environnement
ENVIRONMENT=development
DEBUG=true

# Base de données
DATABASE_URL=postgresql://nikkotrader:nikkotrader123@postgres:5432/nikkotrader_v11

# Redis
REDIS_URL=redis://redis:6379

# Trading (COMPTE DEMO UNIQUEMENT)
MT5_LOGIN=51862230
MT5_PASSWORD=AiMwI&gG$26Z8i
MT5_SERVER=ICMarkets-Demo

# Telegram
TELEGRAM_BOT_TOKEN=8069695013:AAFs7M8knILYIS_NacS2QlIGUVEiZWLmlj0
TELEGRAM_CHAT_ID=-1002272137953

# Sécurité
SECRET_KEY=change-this-secret-key-in-production

# Forward Testing
FORWARD_TESTING_MODE=true
DEMO_ACCOUNT_ONLY=true
EOF
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
fi

# Fonction pour arrêter tous les services
cleanup() {
    echo -e "\n${YELLOW}🛑 Arrêt des services...${NC}"
    docker-compose down
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Démarrer les services
echo -e "${YELLOW}🚀 Démarrage des services...${NC}"

# Construire et démarrer les services
echo -e "${BLUE}📦 Construction des images Docker...${NC}"
docker-compose build --no-cache

echo -e "${BLUE}🔄 Démarrage des services...${NC}"
docker-compose up -d

# Attendre que les services soient prêts
echo -e "${YELLOW}⏳ Attente du démarrage des services...${NC}"
sleep 10

# Vérifier l'état des services
echo -e "${BLUE}🔍 Vérification de l'état des services...${NC}"

# Vérifier PostgreSQL
if docker-compose exec postgres pg_isready -U nikkotrader &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL est prêt${NC}"
else
    echo -e "${RED}❌ PostgreSQL n'est pas prêt${NC}"
fi

# Vérifier Redis
if docker-compose exec redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✅ Redis est prêt${NC}"
else
    echo -e "${RED}❌ Redis n'est pas prêt${NC}"
fi

# Vérifier l'API
sleep 5
if curl -s http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✅ API Backend est prête${NC}"
else
    echo -e "${YELLOW}⚠️ API Backend en cours de démarrage...${NC}"
fi

# Afficher les informations de connexion
echo -e "\n${GREEN}🎉 NIKKOTRADER V11 est démarré !${NC}"
echo -e "\n${BLUE}📊 Accès aux services :${NC}"
echo -e "• Dashboard Frontend : ${GREEN}http://localhost:3000${NC}"
echo -e "• API Backend        : ${GREEN}http://localhost:8000${NC}"
echo -e "• API Documentation  : ${GREEN}http://localhost:8000/docs${NC}"
echo -e "• Grafana Monitoring : ${GREEN}http://localhost:3001${NC} (admin/admin123)"
echo -e "• Prometheus         : ${GREEN}http://localhost:9090${NC}"
echo -e "• RabbitMQ           : ${GREEN}http://localhost:15672${NC} (nikkotrader/nikkotrader123)"

echo -e "\n${YELLOW}📋 Commandes utiles :${NC}"
echo -e "• Voir les logs      : ${BLUE}docker-compose logs -f${NC}"
echo -e "• Arrêter le système : ${BLUE}docker-compose down${NC}"
echo -e "• Redémarrer         : ${BLUE}docker-compose restart${NC}"
echo -e "• État des services  : ${BLUE}docker-compose ps${NC}"

echo -e "\n${YELLOW}🔍 Monitoring :${NC}"
echo -e "• Logs des agents    : ${BLUE}docker-compose logs -f master-agent${NC}"
echo -e "• Logs de l'API      : ${BLUE}docker-compose logs -f api${NC}"
echo -e "• Logs du frontend   : ${BLUE}docker-compose logs -f frontend${NC}"

echo -e "\n${GREEN}⚡ Le système est maintenant prêt pour les forward tests !${NC}"
echo -e "${YELLOW}⚠️ Rappel : Ce système fonctionne uniquement avec un compte DEMO${NC}"

# Afficher les logs en temps réel
echo -e "\n${BLUE}📜 Logs en temps réel (Ctrl+C pour arrêter) :${NC}"
docker-compose logs -f 