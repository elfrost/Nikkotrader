# 🚀 Guide de Démarrage Rapide - NIKKOTRADER V11

## 📋 Prérequis

### 🐳 Docker Desktop
- **Windows/Mac** : Télécharger et installer [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux** : Installer Docker et Docker Compose via votre gestionnaire de packages

### ⚙️ Vérifications
```bash
# Vérifier Docker
docker --version

# Vérifier Docker Compose
docker-compose --version

# Vérifier que Docker est démarré
docker info
```

## 🚀 Démarrage Ultra-Rapide

### 🖥️ Windows
```cmd
cd NIKKOTRADER_V11
scripts\start.bat
```

### 🐧 Linux/Mac
```bash
cd NIKKOTRADER_V11
./scripts/start.sh
```

## 🎯 Accès aux Services

Une fois le système démarré, vous pouvez accéder à :

| Service | URL | Identifiants |
|---------|-----|-------------|
| 🎛️ **Dashboard Frontend** | http://localhost:3000 | - |
| 🔧 **API Backend** | http://localhost:8000 | - |
| 📚 **API Documentation** | http://localhost:8000/docs | - |
| 📊 **Grafana Monitoring** | http://localhost:3001 | admin/admin123 |
| 🔍 **Prometheus** | http://localhost:9090 | - |
| 🐰 **RabbitMQ** | http://localhost:15672 | nikkotrader/nikkotrader123 |

## 📊 Système de Stats Détaillées

### 🎯 Métriques Trackées
- **Performance par stratégie** avec versioning automatique
- **Analyse des patterns de marché** (ADX, RSI, volatilité)
- **Corrélations entre paires** forex
- **Analyse temporelle** (performance par heure/jour/mois)
- **Metrics de risque** (drawdown, Sharpe ratio, profit factor)
- **Optimisation continue** des paramètres

### 📈 Versioning des Stratégies
```
Exemple de versioning automatique :
- Breakout v1.0.0 -> v1.0.1 (ajustement paramètres)
- Breakout v1.0.1 -> v1.1.0 (nouvelle fonctionnalité)
- Breakout v1.1.0 -> v2.0.0 (refonte majeure)
```

## 🤖 Architecture Multi-Agents

### 🎯 Agents Principaux
- **MasterAgent** : Orchestrateur principal
- **MarketDataAgent** : Collecte données MT5
- **StrategyAgents** : 7 stratégies spécialisées
- **RiskManagementAgent** : Gestion des risques
- **NotificationAgent** : Notifications Telegram

### 📊 Communication Inter-Agents
- **Redis** : Cache et communication temps réel
- **RabbitMQ** : Queue de messages
- **PostgreSQL** : Données persistantes
- **WebSocket** : Mises à jour temps réel

## 🔧 Commandes Utiles

### 📜 Monitoring
```bash
# Voir tous les logs
docker-compose logs -f

# Logs spécifiques
docker-compose logs -f master-agent
docker-compose logs -f api
docker-compose logs -f frontend

# État des services
docker-compose ps
```

### 🔄 Gestion des Services
```bash
# Redémarrer un service
docker-compose restart master-agent

# Arrêter tout le système
docker-compose down

# Redémarrer tout le système
docker-compose up -d

# Rebuild et redémarrer
docker-compose build --no-cache
docker-compose up -d
```

## 🎯 Forward Testing

### ⚠️ Sécurité
- **COMPTE DEMO UNIQUEMENT** - Système configuré pour MT5 demo
- **Pas de trading réel** - Protection intégrée
- **Données historiques** - Toutes les décisions sont loggées

### 📊 Suivi des Performances
```bash
# Accéder aux stats en temps réel
curl http://localhost:8000/api/v1/performance/current

# Voir les métriques par stratégie
curl http://localhost:8000/api/v1/strategies/performance

# Analyser les patterns
curl http://localhost:8000/api/v1/performance/patterns
```

## 🛠️ Développement

### 🔧 **Système de Versioning Automatique**

**🎯 NIKKOTRADER V11 utilise un versioning automatique complet :**

```json
{
  "program_version": "NIKKOTRADER V11.0.0",
  "strategy_versioning": {
    "enabled": true,
    "auto_backup": true,
    "max_versions": 10,
    "format": "v{major}.{minor}.{patch}"
  }
}
```

### 📈 **Modifier une Stratégie (Versioning Automatique)**

**Processus automatique :**

1. **Modifier le fichier** dans `agents/strategies/`
2. **Système détecte** automatiquement les changements
3. **Nouvelle version créée** automatiquement (ex: v1.0.0 → v1.0.1)
4. **Backup automatique** de l'ancienne version
5. **Comparaison performance** vs version précédente
6. **Tests A/B** nouvelle vs ancienne version

### 🔄 **Exemples de Versioning**

```
Breakout v1.0.0 → v1.0.1 (ajustement paramètres ADX)
Breakout v1.0.1 → v1.1.0 (ajout filtre volatilité)
Breakout v1.1.0 → v2.0.0 (refonte algorithme complet)

NewsImpact v1.0.0 → v1.0.1 (optimisation fenêtres)
NewsImpact v1.0.1 → v1.1.0 (nouvelles sources API)
```

### 📊 **Versioning du Programme Principal**

```
NIKKOTRADER V11.0.0 (Actuel - Forward Testing)
    ↓
NIKKOTRADER V11.1.0 (+ Filtre IA + Optimisations)
    ↓  
NIKKOTRADER V11.2.0 (+ Production Ready + ML)
    ↓
NIKKOTRADER V12.0.0 (+ Architecture v2 + Multi-Assets)
```

### 🗄️ **Base de Données - Versioning**

**Toutes les versions sont conservées :**

```sql
-- Voir l'historique d'une stratégie
SELECT name, version, created_at, is_active 
FROM strategies 
WHERE name = 'Breakout' 
ORDER BY created_at DESC;

-- Résultat exemple :
-- Breakout | v1.0.2 | 2024-01-15 | true
-- Breakout | v1.0.1 | 2024-01-10 | false  
-- Breakout | v1.0.0 | 2024-01-01 | false
```

### ⚡ **Rollback Automatique**

**Si nouvelle version performe mal :**

```python
# Rollback automatique si win rate < version précédente
if new_version.win_rate < previous_version.win_rate - 5%:
    auto_rollback_to_previous_version()
    send_alert("Rollback automatique - Performance dégradée")
```

### 📊 Ajouter de Nouvelles Métriques
1. Modifier le schéma dans `backend/models/database.py`
2. Ajouter la logique dans `backend/api/v1/performance.py`
3. Mettre à jour le dashboard frontend

## 🐛 Dépannage

### ❌ Problèmes Courants

**Docker n'est pas démarré**
```bash
# Windows : Démarrer Docker Desktop
# Linux : sudo systemctl start docker
```

**Port déjà utilisé**
```bash
# Vérifier quels ports sont utilisés
netstat -an | findstr :8000
netstat -an | findstr :3000

# Arrêter les services conflictuels
docker-compose down
```

**Base de données corrompue**
```bash
# Réinitialiser la base de données
docker-compose down
docker volume rm nikkotrader_v11_postgres_data
docker-compose up -d
```

## 📞 Support

### 🔍 Logs et Debugging
```bash
# Logs détaillés avec timestamps
docker-compose logs -f --timestamps

# Logs d'un agent spécifique
docker-compose exec master-agent cat /app/logs/master_agent.log

# Vérifier la santé du système
curl http://localhost:8000/health
```

### 🛠️ Outils de Développement
- **Swagger UI** : http://localhost:8000/docs
- **Grafana** : Dashboards personnalisés
- **Prometheus** : Métriques système
- **RabbitMQ** : Queue de messages

## 🎯 Prochaines Étapes

1. **Lancer le système** avec le script de démarrage
2. **Accéder au dashboard** pour voir les stats
3. **Configurer les alertes** Telegram
4. **Analyser les performances** des stratégies
5. **Optimiser les paramètres** selon les résultats

---

**🚨 Rappel Important** : Ce système est conçu pour le forward testing sur compte démo uniquement. Toute utilisation en production nécessite des tests approfondis et une validation complète. 