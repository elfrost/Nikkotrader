# 🚀 NIKKOTRADER V11 - Système de Trading Algorithmique

![Version](https://img.shields.io/badge/version-11.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-Ready%20for%20Forward%20Testing-green.svg)
![Trading](https://img.shields.io/badge/trading-Binary%20Options-orange.svg)

## 🎯 **Vue d'Ensemble**

NIKKOTRADER V11 est un **système de trading algorithmique avancé** spécialisé dans les **options binaires** avec architecture multi-agents intelligente.

### ⚡ **Démarrage Rapide (2 minutes)**

```bash
# 1. Cloner et naviguer
cd NIKKOTRADER_V11

# 2. Lancer le système complet
./scripts/start.bat    # Windows
./scripts/start.sh     # Linux/Mac

# 3. Ouvrir UNE SEULE interface
🎯 Interface Principale: http://localhost:3001 (admin/admin123)
```

**🔗 Guide détaillé :** [QUICKSTART.md](./QUICKSTART.md)

---

## 🎛️ **Interface Principale Unique - Grafana**

### **📱 Navigation Simplifiée**

**🎯 UNE SEULE URL à retenir :** `http://localhost:3001`

```
📊 Menu Grafana (côté gauche):
├── 🏠 Dashboards
    ├── 📁 "NIKKOTRADER V11"
        ├── 🎯 "Overview" (PAGE PRINCIPALE)
        └── 📈 "Strategy Performance" (Détails)
```

### **🔥 Page "Overview" - Tout ce dont tu as besoin**
- ✅ **Statut système** (agents verts = OK)
- 📈 **Signaux temps réel** 
- 💰 **P&L live**
- 📊 **Win Rate global**
- ⚡ **Trades actifs**
- 🔄 **Refresh automatique** (5 secondes)

### **📊 Les Autres Interfaces (Optionnelles)**
```
🔍 Debug avancé:     http://localhost:9090 (Prometheus)
🐰 Messages agents:  http://localhost:15672 (RabbitMQ)
🔧 API technique:    http://localhost:8000 (Backend)
```

**💡 99% du temps, tu n'as besoin QUE de Grafana !**

---

## 🏗️ **Architecture du Système**

### 🤖 **9 Stratégies Optimisées**
- **Court terme (3-5min)** : Scalping, Consolidation, Breakout, Pullback, Mean Reversion
- **Moyen terme (10-15min)** : Range, Divergence, **NewsImpact** 📰
- **Long terme (30min)** : SessionBreakout

### 🛡️ **Agents Spécialisés**
- **MasterAgent** : Orchestrateur principal avec IA
- **MarketDataAgent** : Collecte données MT5 temps réel
- **StrategyAgents** : 9 agents spécialisés par stratégie
- **RiskAgent** : Gestion risques (mode permissif forward testing)
- **NewsImpactAgent** : Trading sur nouvelles économiques
- **PerformanceAgent** : Analyse et optimisation continue
- **NotificationAgent** : Alertes Telegram intelligentes

### 💾 **Infrastructure**
- **Backend** : FastAPI + PostgreSQL + Redis
- **Monitoring** : Prometheus + Grafana + RabbitMQ
- **Containerisation** : Docker + Docker Compose
- **Trading** : MT5 ICMarkets Demo (51862230)

---

## 📊 **Configuration Forward Testing**

### 🧪 **Mode Actuel : Collecte de Données**
```json
{
  "max_daily_trades": 500,
  "max_concurrent_positions": 20,
  "max_drawdown": 50%,
  "risk_mode": "permissive",
  "data_collection_priority": true
}
```

### 🎯 **Objectifs Forward Testing**
- ✅ **Win Rate Cible** : 70%+ global
- ✅ **Données Minimales** : 10,000 trades
- ✅ **Stratégies Validées** : 6/9 rentables
- ✅ **Compte DÉMO uniquement** : Aucun risque financier

---

## 📚 **Documentation Spécialisée**

### 🚀 **Démarrage et Usage**
- **[QUICKSTART.md](./QUICKSTART.md)** - Guide de démarrage complet (5 min)
- **[GUIDE_DOCKER.md](./GUIDE_DOCKER.md)** - Configuration Docker avancée

### 📈 **Stratégies et Trading**
- **[BINARY_OPTIONS_STRATEGY_CONFIG.md](./BINARY_OPTIONS_STRATEGY_CONFIG.md)** - Configuration optimale des 9 stratégies
- **[NEWS_INTEGRATION_GUIDE.md](./NEWS_INTEGRATION_GUIDE.md)** - Système NewsImpact complet
- **[STRATEGY_ROADMAP.md](./STRATEGY_ROADMAP.md)** - Vision et évolution stratégique

---

## 🔧 **Configuration Système**

### 🐳 **Services Docker (11 containers)**
```yaml
Core Trading:       6 agents NIKKOTRADER
Database:          PostgreSQL + Redis  
Monitoring:        Prometheus + Grafana + RabbitMQ
```

### 📊 **Monitoring en Temps Réel**
- **Grafana Dashboards** : Performance stratégies, métriques agents
- **Prometheus Metrics** : 15+ métriques spécialisées options binaires
- **Alertes Intelligentes** : Telegram + seuils adaptatifs

### 🎛️ **Configuration MT5**
```
Courtier: ICMarkets Demo
Login:    51862230
Serveur:  ICMarkets-Demo
Paires:   28 paires majeures/mineures
```

---

## 📈 **Performances Attendues**

### 🏆 **Win Rates Théoriques par Stratégie**
```
🥇 NewsImpact:     78% (nouvelles économiques)
🥈 Divergence:     75% (signaux techniques forts)
🥉 SessionBreakout: 73% (ouvertures sessions)
📊 Pullback:       72% (retracements Fibonacci)
📊 Consolidation:  70% (patterns consolidation)
```

### 📊 **Allocation Ressources**
- **40%** signaux haute fréquence (3-5min)
- **35%** signaux fréquence moyenne (10-15min)
- **25%** signaux basse fréquence (30min+)

---

## 🛠️ **Commandes Essentielles**

### 🔄 **Gestion Système**
```bash
# Démarrer tout le système
docker-compose up -d

# Voir les logs en temps réel
docker-compose logs -f

# Redémarrer un agent spécifique
docker-compose restart strategy-agents

# Arrêter tout le système
docker-compose down
```

### 📊 **Monitoring et Debug**
```bash
# Vérifier l'état des agents
curl http://localhost:8000/api/v1/agents/status

# Métriques de performance
curl http://localhost:8000/api/v1/performance/current

# Stats par stratégie
curl http://localhost:8000/api/v1/strategies/performance
```

---

## 🚨 **Sécurité et Risques**

### ⚠️ **Mode Forward Testing Sécurisé**
- ✅ **Compte DÉMO uniquement** - Aucun capital réel
- ✅ **Risk Agent permissif** - Collecte maximale de données
- ✅ **Monitoring 24/7** - Alertes en temps réel
- ✅ **Logs détaillés** - Traçabilité complète

### 🔒 **Protection Capital**
- **Kill Switch** : Arrêt d'urgence 1-click
- **Limites quotidiennes** : Drawdown 50% max
- **Validation double** : Risk Agent + Master Agent
- **Environnement isolé** : Docker containerisé

---

## 🎊 **Vision Future**

### 📊 **Phase Actuelle (3-6 mois)**
Forward testing complet avec collecte massive de données

### 🤖 **Phase 2 (6-12 mois)**  
Filtre IA intelligent sélectionnant signaux premium (>75% win rate)

### 🚀 **Phase 3 (12+ mois)**
Système production avec capital réel et risk agent strict

**🔗 Détails complets :** [STRATEGY_ROADMAP.md](./STRATEGY_ROADMAP.md)

---

## 🤝 **Support et Contact**

### 📞 **Ressources**
- **Documentation** : Guides spécialisés ci-dessus
- **Monitoring** : Grafana + Prometheus
- **Notifications** : Telegram (@nikkotrader_alerts)
- **Health Check** : `http://localhost:8000/health`

### 🐛 **Troubleshooting**
1. **Services ne démarrent pas** → Vérifier Docker Desktop
2. **Pas de signaux** → Vérifier connexion MT5
3. **Erreurs agents** → Consulter `docker-compose logs`
4. **Performance dégradée** → Redémarrer avec `docker-compose restart`

---

**⚡ NIKKOTRADER V11 - Prêt pour le Forward Testing Immédiat ! 🚀** 