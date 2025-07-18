"""
Configuration des APIs de Nouvelles Économiques - NIKKOTRADER V11
Configuration centralisée pour toutes les sources de données économiques
"""

import os
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class NewsAPIConfig:
    """Configuration pour une API de nouvelles"""
    name: str
    base_url: str
    api_key: str = ""
    rate_limit: int = 100  # Requêtes par heure
    reliability: float = 0.8  # Score de fiabilité (0-1)
    cost: str = "free"  # free, paid, premium
    requires_auth: bool = False

class NewsSourcesConfig:
    """Configuration complète des sources de nouvelles"""
    
    def __init__(self):
        # Sources principales (APIs payantes recommandées pour production)
        self.premium_sources = [
            NewsAPIConfig(
                name="ForexFactory",
                base_url="https://nfs.faireconomy.media/ff_calendar_thisweek.json",
                api_key="",  # Gratuit mais limité
                rate_limit=50,
                reliability=0.9,
                cost="free",
                requires_auth=False
            ),
            NewsAPIConfig(
                name="TradingEconomics",
                base_url="https://api.tradingeconomics.com/calendar",
                api_key=os.getenv("TRADING_ECONOMICS_API_KEY", ""),
                rate_limit=1000,
                reliability=0.95,
                cost="premium",
                requires_auth=True
            ),
            NewsAPIConfig(
                name="AlphaVantage",
                base_url="https://www.alphavantage.co/query",
                api_key=os.getenv("ALPHAVANTAGE_API_KEY", ""),
                rate_limit=500,
                reliability=0.85,
                cost="paid",
                requires_auth=True
            )
        ]
        
        # Sources de fallback (gratuites mais moins fiables)
        self.fallback_sources = [
            NewsAPIConfig(
                name="FRED",  # Federal Reserve Economic Data
                base_url="https://api.stlouisfed.org/fred",
                api_key=os.getenv("FRED_API_KEY", ""),
                rate_limit=1000,
                reliability=0.9,
                cost="free",
                requires_auth=True
            ),
            NewsAPIConfig(
                name="MarketStack",
                base_url="https://api.marketstack.com/v1",
                api_key=os.getenv("MARKETSTACK_API_KEY", ""),
                rate_limit=1000,
                reliability=0.75,
                cost="free",
                requires_auth=True
            ),
            NewsAPIConfig(
                name="DailyFX",
                base_url="https://www.dailyfx.com/economic-calendar",
                api_key="",
                rate_limit=20,
                reliability=0.7,
                cost="free",
                requires_auth=False
            )
        ]
        
        # Sources simulées pour développement/test
        self.simulation_sources = [
            NewsAPIConfig(
                name="SimulatedNews",
                base_url="internal://simulation",
                api_key="",
                rate_limit=999999,
                reliability=0.85,
                cost="free",
                requires_auth=False
            )
        ]
    
    def get_available_sources(self) -> List[NewsAPIConfig]:
        """Obtenir les sources disponibles (avec clés API valides)"""
        available = []
        
        # Vérifier les sources premium
        for source in self.premium_sources:
            if not source.requires_auth or source.api_key:
                available.append(source)
        
        # Ajouter les fallbacks si nécessaire
        if len(available) < 2:  # Au moins 2 sources
            for source in self.fallback_sources:
                if not source.requires_auth or source.api_key:
                    available.append(source)
        
        # En dernier recours, utiliser la simulation
        if not available:
            available.extend(self.simulation_sources)
        
        # Trier par fiabilité
        available.sort(key=lambda x: x.reliability, reverse=True)
        
        return available
    
    def get_economic_indicators_mapping(self) -> Dict:
        """Mapping des indicateurs économiques par importance"""
        return {
            "critical": {
                "indicators": [
                    "Non-Farm Payrolls",
                    "Unemployment Rate", 
                    "Federal Reserve Rate Decision",
                    "ECB Rate Decision",
                    "BOE Rate Decision",
                    "BOJ Rate Decision",
                    "GDP Growth Rate",
                    "Inflation Rate (CPI)",
                    "Core PCE"
                ],
                "keywords": [
                    "nfp", "unemployment", "fed", "ecb", "boe", "boj", 
                    "interest rate", "gdp", "inflation", "cpi", "pce"
                ]
            },
            "high": {
                "indicators": [
                    "Retail Sales",
                    "Manufacturing PMI",
                    "Services PMI",
                    "Consumer Confidence",
                    "Producer Price Index",
                    "Trade Balance",
                    "Current Account",
                    "Industrial Production"
                ],
                "keywords": [
                    "retail sales", "pmi", "consumer confidence",
                    "ppi", "trade balance", "current account", "industrial"
                ]
            },
            "medium": {
                "indicators": [
                    "Housing Starts",
                    "Building Permits",
                    "Factory Orders",
                    "Durable Goods",
                    "Initial Jobless Claims",
                    "Business Confidence",
                    "Consumer Spending"
                ],
                "keywords": [
                    "housing", "building permits", "factory orders",
                    "durable goods", "jobless claims", "business confidence"
                ]
            }
        }
    
    def get_currency_news_sources(self) -> Dict:
        """Sources spécialisées par devise"""
        return {
            "USD": [
                "https://www.federalreserve.gov/releases/",
                "https://www.bls.gov/news.release/",
                "https://www.census.gov/economic-indicators/"
            ],
            "EUR": [
                "https://www.ecb.europa.eu/press/calendars/",
                "https://ec.europa.eu/eurostat/",
                "https://www.bundesbank.de/en/"
            ],
            "GBP": [
                "https://www.bankofengland.co.uk/news/",
                "https://www.ons.gov.uk/releases",
                "https://www.gov.uk/government/statistics"
            ],
            "JPY": [
                "https://www.boj.or.jp/en/",
                "https://www.esri.cao.go.jp/en/",
                "https://www.stat.go.jp/english/"
            ],
            "CHF": [
                "https://www.snb.ch/en/",
                "https://www.seco.admin.ch/seco/en/"
            ],
            "AUD": [
                "https://www.rba.gov.au/",
                "https://www.abs.gov.au/"
            ],
            "CAD": [
                "https://www.bankofcanada.ca/",
                "https://www.statcan.gc.ca/"
            ]
        }
    
    def get_news_impact_rules(self) -> Dict:
        """Règles d'évaluation de l'impact des nouvelles"""
        return {
            "deviation_thresholds": {
                "critical": 5.0,    # 5%+ d'écart = critique
                "high": 2.0,        # 2-5% d'écart = important  
                "medium": 1.0,      # 1-2% d'écart = moyen
                "low": 0.5          # <1% d'écart = faible
            },
            "time_impact_decay": {
                "immediate": 1.0,        # 0-5 minutes
                "short_term": 0.8,       # 5-30 minutes  
                "medium_term": 0.5,      # 30-120 minutes
                "long_term": 0.2         # 2h+
            },
            "currency_correlation": {
                "major_pairs": ["USD", "EUR", "GBP", "JPY"],
                "minor_pairs": ["CHF", "AUD", "CAD", "NZD"],
                "correlation_matrix": {
                    # Corrélation entre devises (simplifié)
                    "USD": {"EUR": -0.7, "GBP": -0.6, "JPY": -0.5},
                    "EUR": {"GBP": 0.6, "CHF": 0.8, "JPY": -0.3},
                    "GBP": {"CHF": 0.4, "AUD": 0.3, "CAD": 0.2}
                }
            },
            "market_session_multipliers": {
                "london": 1.2,      # 08:00-16:00 UTC
                "new_york": 1.3,    # 13:00-21:00 UTC
                "overlap": 1.5,     # 13:00-16:00 UTC (overlap)
                "asian": 0.8,       # 22:00-08:00 UTC
                "weekend": 0.3      # Samedi/Dimanche
            }
        }
    
    def get_default_trading_windows(self) -> Dict:
        """Fenêtres de trading par défaut pour les nouvelles"""
        return {
            "critical_news": {
                "avoid_before_minutes": 30,
                "avoid_after_minutes": 60,
                "opportunity_window_minutes": 15,
                "max_trades_per_news": 3
            },
            "high_impact_news": {
                "avoid_before_minutes": 15,
                "avoid_after_minutes": 30,
                "opportunity_window_minutes": 10,
                "max_trades_per_news": 2
            },
            "medium_impact_news": {
                "avoid_before_minutes": 5,
                "avoid_after_minutes": 15,
                "opportunity_window_minutes": 5,
                "max_trades_per_news": 1
            }
        }
    
    def get_api_fallback_strategy(self) -> Dict:
        """Stratégie de fallback en cas d'échec des APIs"""
        return {
            "max_retries": 3,
            "retry_delay_seconds": 5,
            "circuit_breaker_failures": 5,  # Désactiver après 5 échecs
            "circuit_breaker_timeout": 300,  # Réessayer après 5 minutes
            "fallback_to_simulation": True,
            "cache_duration_minutes": 60,
            "stale_data_threshold_minutes": 120
        }

# Instance globale de configuration
news_config = NewsSourcesConfig()

# Variables d'environnement recommandées
RECOMMENDED_ENV_VARS = {
    "TRADING_ECONOMICS_API_KEY": "Clé API Trading Economics (premium)",
    "ALPHAVANTAGE_API_KEY": "Clé API Alpha Vantage (gratuite avec limites)",
    "FRED_API_KEY": "Clé API Federal Reserve (gratuite)",
    "MARKETSTACK_API_KEY": "Clé API MarketStack (gratuite avec limites)",
    "NEWS_CACHE_REDIS_URL": "URL Redis pour cache des nouvelles",
    "NEWS_NOTIFICATION_WEBHOOK": "Webhook pour notifications nouvelles importantes"
}

def validate_news_configuration() -> Dict:
    """Valider la configuration des sources de nouvelles"""
    validation_result = {
        "status": "ok",
        "available_sources": 0,
        "premium_sources": 0,
        "issues": [],
        "recommendations": []
    }
    
    available_sources = news_config.get_available_sources()
    validation_result["available_sources"] = len(available_sources)
    
    # Compter les sources premium
    premium_count = len([s for s in available_sources if s.cost == "premium"])
    validation_result["premium_sources"] = premium_count
    
    # Vérifications
    if len(available_sources) == 0:
        validation_result["status"] = "error"
        validation_result["issues"].append("Aucune source de nouvelles disponible")
    elif len(available_sources) == 1 and available_sources[0].name == "SimulatedNews":
        validation_result["status"] = "warning"
        validation_result["issues"].append("Utilisation uniquement de données simulées")
        validation_result["recommendations"].append("Configurer au moins une API externe")
    elif premium_count == 0:
        validation_result["status"] = "warning"
        validation_result["recommendations"].append("Considérer une source premium pour meilleure fiabilité")
    
    # Vérifier les variables d'environnement manquantes
    missing_vars = []
    for var, description in RECOMMENDED_ENV_VARS.items():
        if not os.getenv(var):
            missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        validation_result["recommendations"].extend([
            "Variables d'environnement recommandées manquantes:",
            *missing_vars
        ])
    
    return validation_result

if __name__ == "__main__":
    # Test de la configuration
    print("🔧 Configuration des sources de nouvelles:")
    print(f"Sources disponibles: {len(news_config.get_available_sources())}")
    
    for source in news_config.get_available_sources():
        print(f"  📰 {source.name}: {source.cost} (fiabilité: {source.reliability})")
    
    print("\n🔍 Validation de la configuration:")
    validation = validate_news_configuration()
    print(f"Statut: {validation['status']}")
    
    if validation["issues"]:
        print("❌ Problèmes détectés:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    
    if validation["recommendations"]:
        print("💡 Recommandations:")
        for rec in validation["recommendations"]:
            print(f"  - {rec}") 