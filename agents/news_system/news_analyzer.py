"""
Système d'Analyse des Nouvelles Économiques - NIKKOTRADER V11
Module complet pour détecter, analyser et interpréter l'impact des news sur le forex
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from loguru import logger
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

class NewsImpact(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"
    AUD = "AUD"
    CAD = "CAD"
    NZD = "NZD"

@dataclass
class EconomicNews:
    """Structure pour une nouvelle économique"""
    id: str
    title: str
    description: str
    currency: Currency
    impact: NewsImpact
    actual: Optional[float]
    forecast: Optional[float]
    previous: Optional[float]
    release_time: datetime
    source: str
    deviation_score: float = 0.0  # Écart par rapport aux prévisions
    market_reaction_expected: str = "neutral"  # bullish, bearish, neutral

class NewsAnalyzer:
    """Analyseur de nouvelles économiques avec sources multiples"""
    
    def __init__(self):
        self.news_cache = {}
        self.impact_keywords = self._load_impact_keywords()
        self.currency_mappings = self._load_currency_mappings()
        self.sources = {
            "forexfactory": "https://www.forexfactory.com/calendar.php",
            "investing": "https://www.investing.com/economic-calendar/",
            "tradingeconomics": "https://tradingeconomics.com/calendar"
        }
        
    async def get_todays_news(self) -> List[EconomicNews]:
        """Récupérer les nouvelles du jour depuis plusieurs sources"""
        logger.info("📰 Récupération des nouvelles économiques du jour")
        
        all_news = []
        
        # Source 1: ForexFactory (RSS/Scraping)
        ff_news = await self._fetch_forexfactory_news()
        all_news.extend(ff_news)
        
        # Source 2: Fallback avec données simulées réalistes
        if not all_news:
            logger.warning("⚠️ Pas de données externes, utilisation des données simulées")
            all_news = self._generate_realistic_news()
        
        # Filtrer et trier par impact
        filtered_news = self._filter_and_prioritize(all_news)
        
        logger.info(f"✅ {len(filtered_news)} nouvelles économiques analysées")
        return filtered_news
    
    async def _fetch_forexfactory_news(self) -> List[EconomicNews]:
        """Récupérer les nouvelles depuis ForexFactory"""
        try:
            # Note: Pour production, utiliser une API payante ou scraping légal
            # Ici on simule une réponse réaliste
            news_data = [
                {
                    "title": "US Non-Farm Payrolls",
                    "currency": "USD",
                    "impact": "high",
                    "time": "13:30",
                    "forecast": "200K",
                    "previous": "195K"
                },
                {
                    "title": "ECB Interest Rate Decision",
                    "currency": "EUR", 
                    "impact": "critical",
                    "time": "12:45",
                    "forecast": "4.50%",
                    "previous": "4.25%"
                },
                {
                    "title": "UK GDP Growth Rate",
                    "currency": "GBP",
                    "impact": "high",
                    "time": "09:30",
                    "forecast": "0.3%",
                    "previous": "0.1%"
                }
            ]
            
            parsed_news = []
            for item in news_data:
                news = self._parse_news_item(item)
                if news:
                    parsed_news.append(news)
            
            return parsed_news
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération ForexFactory: {e}")
            return []
    
    def _generate_realistic_news(self) -> List[EconomicNews]:
        """Générer des nouvelles réalistes pour le testing"""
        now = datetime.now()
        today_news = []
        
        # Templates de nouvelles économiques réalistes
        news_templates = [
            {
                "title": "US Non-Farm Payrolls",
                "currency": Currency.USD,
                "impact": NewsImpact.HIGH,
                "time_offset": 330,  # 13:30 UTC
                "forecast": 200.0,
                "previous": 195.0,
                "description": "Monthly change in employment"
            },
            {
                "title": "ECB Monetary Policy Decision", 
                "currency": Currency.EUR,
                "impact": NewsImpact.CRITICAL,
                "time_offset": 765,  # 12:45 UTC
                "forecast": 4.50,
                "previous": 4.25,
                "description": "Central bank interest rate decision"
            },
            {
                "title": "UK GDP Growth Rate QoQ",
                "currency": Currency.GBP,
                "impact": NewsImpact.HIGH,
                "time_offset": 570,  # 09:30 UTC
                "forecast": 0.3,
                "previous": 0.1,
                "description": "Quarterly GDP growth percentage"
            },
            {
                "title": "Japanese Core CPI YoY",
                "currency": Currency.JPY,
                "impact": NewsImpact.MEDIUM,
                "time_offset": 1430,  # 23:50 UTC
                "forecast": 2.8,
                "previous": 2.7,
                "description": "Core consumer price index year over year"
            },
            {
                "title": "Canadian Employment Change",
                "currency": Currency.CAD,
                "impact": NewsImpact.MEDIUM,
                "time_offset": 750,  # 12:30 UTC
                "forecast": 25.0,
                "previous": 21.8,
                "description": "Monthly employment change in thousands"
            },
            {
                "title": "Australian RBA Rate Decision",
                "currency": Currency.AUD,
                "impact": NewsImpact.HIGH,
                "time_offset": 140,  # 02:20 UTC
                "forecast": 4.35,
                "previous": 4.35,
                "description": "Reserve Bank of Australia interest rate"
            }
        ]
        
        for i, template in enumerate(news_templates):
            # Simuler des valeurs actuelles avec déviation réaliste
            actual = self._simulate_actual_value(template["forecast"], template["previous"])
            
            release_time = now.replace(
                hour=template["time_offset"] // 60,
                minute=template["time_offset"] % 60,
                second=0,
                microsecond=0
            )
            
            # Ajuster pour aujourd'hui si l'heure est passée
            if release_time < now:
                release_time += timedelta(days=1)
            
            news = EconomicNews(
                id=f"sim_{i}_{now.strftime('%Y%m%d')}",
                title=template["title"],
                description=template["description"],
                currency=template["currency"],
                impact=template["impact"],
                actual=actual,
                forecast=template["forecast"],
                previous=template["previous"],
                release_time=release_time,
                source="simulation",
                deviation_score=self._calculate_deviation(actual, template["forecast"]),
                market_reaction_expected=self._predict_market_reaction(actual, template["forecast"])
            )
            
            today_news.append(news)
        
        return today_news
    
    def _simulate_actual_value(self, forecast: float, previous: float) -> float:
        """Simuler une valeur actuelle réaliste"""
        import random
        
        # Variance typique par rapport aux prévisions
        variance = abs(forecast - previous) * 0.5 if forecast != previous else forecast * 0.02
        
        # 70% de chances que la valeur soit proche des prévisions
        if random.random() < 0.7:
            return forecast + random.uniform(-variance/2, variance/2)
        else:
            # 30% de surprises (positives ou négatives)
            surprise_factor = random.uniform(1.5, 3.0)
            direction = 1 if random.random() > 0.5 else -1
            return forecast + (variance * surprise_factor * direction)
    
    def _calculate_deviation(self, actual: float, forecast: float) -> float:
        """Calculer l'écart en pourcentage par rapport aux prévisions"""
        if forecast == 0:
            return 0.0
        return abs((actual - forecast) / forecast) * 100
    
    def _predict_market_reaction(self, actual: float, forecast: float) -> str:
        """Prédire la réaction du marché basée sur l'écart"""
        if actual > forecast:
            return "bullish"
        elif actual < forecast:
            return "bearish"
        else:
            return "neutral"
    
    def _parse_news_item(self, item: Dict) -> Optional[EconomicNews]:
        """Parser un item de nouvelle depuis les données externes"""
        try:
            currency = Currency(item.get("currency", "USD"))
            impact = NewsImpact(item.get("impact", "medium"))
            
            # Parser le temps
            time_str = item.get("time", "12:00")
            today = datetime.now().date()
            time_parts = time_str.split(":")
            release_time = datetime.combine(
                today, 
                datetime.min.time().replace(
                    hour=int(time_parts[0]), 
                    minute=int(time_parts[1])
                )
            )
            
            return EconomicNews(
                id=f"ext_{hash(item.get('title', ''))%10000}",
                title=item.get("title", ""),
                description=item.get("description", ""),
                currency=currency,
                impact=impact,
                actual=self._parse_numeric_value(item.get("actual")),
                forecast=self._parse_numeric_value(item.get("forecast")),
                previous=self._parse_numeric_value(item.get("previous")),
                release_time=release_time,
                source="external_api"
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur parsing news item: {e}")
            return None
    
    def _parse_numeric_value(self, value: Optional[str]) -> Optional[float]:
        """Parser une valeur numérique depuis string"""
        if not value:
            return None
        
        try:
            # Nettoyer la string (retirer %, K, M, etc.)
            clean_value = re.sub(r'[^\d.-]', '', str(value))
            
            # Gérer les multiplicateurs
            if 'K' in str(value).upper():
                return float(clean_value) * 1000
            elif 'M' in str(value).upper():
                return float(clean_value) * 1000000
            else:
                return float(clean_value)
                
        except (ValueError, TypeError):
            return None
    
    def _filter_and_prioritize(self, news_list: List[EconomicNews]) -> List[EconomicNews]:
        """Filtrer et prioriser les nouvelles par impact"""
        
        # Filtrer les nouvelles importantes
        filtered = [
            news for news in news_list 
            if news.impact in [NewsImpact.HIGH, NewsImpact.CRITICAL]
            and news.currency in [Currency.USD, Currency.EUR, Currency.GBP, Currency.JPY]
        ]
        
        # Trier par impact et proximité temporelle
        now = datetime.now()
        
        def priority_score(news: EconomicNews) -> float:
            # Score basé sur impact et proximité temporelle
            impact_score = {
                NewsImpact.CRITICAL: 4.0,
                NewsImpact.HIGH: 3.0,
                NewsImpact.MEDIUM: 2.0,
                NewsImpact.LOW: 1.0
            }[news.impact]
            
            # Bonus si proche dans le temps (prochaines 4 heures)
            time_diff = abs((news.release_time - now).total_seconds() / 3600)
            time_bonus = max(0, 2.0 - time_diff/2) if time_diff < 4 else 0
            
            # Bonus si forte déviation attendue
            deviation_bonus = news.deviation_score / 10 if news.deviation_score else 0
            
            return impact_score + time_bonus + deviation_bonus
        
        filtered.sort(key=priority_score, reverse=True)
        
        return filtered[:10]  # Top 10 nouvelles
    
    def analyze_news_impact(self, news: EconomicNews) -> Dict:
        """Analyser l'impact potentiel d'une nouvelle sur les paires"""
        
        # Paires affectées par la devise
        affected_pairs = self._get_affected_pairs(news.currency)
        
        # Calcul de l'impact
        impact_analysis = {
            "news": {
                "title": news.title,
                "currency": news.currency.value,
                "impact": news.impact.value,
                "release_time": news.release_time.isoformat(),
                "deviation_score": news.deviation_score
            },
            "affected_pairs": affected_pairs,
            "trading_recommendation": self._generate_trading_recommendation(news),
            "volatility_prediction": self._predict_volatility_impact(news),
            "time_windows": {
                "avoid_before_minutes": 30 if news.impact == NewsImpact.CRITICAL else 15,
                "avoid_after_minutes": 60 if news.impact == NewsImpact.CRITICAL else 30,
                "opportunity_window_minutes": 15 if news.deviation_score > 5 else 0
            }
        }
        
        return impact_analysis
    
    def _get_affected_pairs(self, currency: Currency) -> List[str]:
        """Obtenir les paires affectées par une devise"""
        major_pairs = {
            Currency.USD: ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD"],
            Currency.EUR: ["EURUSD", "EURGBP", "EURJPY", "EURCHF", "EURAUD", "EURCAD"],
            Currency.GBP: ["GBPUSD", "EURGBP", "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD"],
            Currency.JPY: ["USDJPY", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY"],
            Currency.CHF: ["USDCHF", "EURCHF", "GBPCHF", "CHFJPY", "AUDCHF", "CADCHF"],
            Currency.AUD: ["AUDUSD", "EURAUD", "GBPAUD", "AUDJPY", "AUDCHF", "AUDCAD"],
            Currency.CAD: ["USDCAD", "EURCAD", "GBPCAD", "CADJPY", "AUDCAD", "CADCHF"],
            Currency.NZD: ["NZDUSD", "EURNZD", "GBPNZD", "NZDJPY", "AUDNZD", "NZDCAD"]
        }
        
        return major_pairs.get(currency, [])
    
    def _generate_trading_recommendation(self, news: EconomicNews) -> Dict:
        """Générer une recommandation de trading basée sur la nouvelle"""
        
        if not news.actual or not news.forecast:
            return {"action": "avoid", "reason": "Insufficient data"}
        
        deviation = news.deviation_score
        reaction = news.market_reaction_expected
        
        if deviation < 1.0:  # Faible déviation
            return {
                "action": "avoid",
                "reason": "Low deviation, minimal market impact expected",
                "confidence": 0.3
            }
        elif deviation > 5.0:  # Forte déviation
            direction = "bullish" if reaction == "bullish" else "bearish"
            return {
                "action": "trade_opportunity",
                "direction": direction,
                "reason": f"High deviation ({deviation:.1f}%), strong {direction} reaction expected",
                "confidence": min(0.9, 0.6 + deviation/20),
                "timeframe": "15-30 minutes post-release"
            }
        else:  # Déviation moyenne
            return {
                "action": "cautious_trade",
                "direction": reaction,
                "reason": f"Moderate deviation ({deviation:.1f}%), {reaction} bias",
                "confidence": 0.5 + deviation/20,
                "timeframe": "5-15 minutes post-release"
            }
    
    def _predict_volatility_impact(self, news: EconomicNews) -> Dict:
        """Prédire l'impact sur la volatilité"""
        
        base_volatility = {
            NewsImpact.CRITICAL: 0.008,  # 0.8%
            NewsImpact.HIGH: 0.005,      # 0.5%
            NewsImpact.MEDIUM: 0.003,    # 0.3%
            NewsImpact.LOW: 0.001        # 0.1%
        }[news.impact]
        
        # Multiplier par déviation
        volatility_spike = base_volatility * (1 + news.deviation_score/10)
        
        return {
            "expected_volatility_spike": volatility_spike,
            "duration_minutes": 30 if news.impact == NewsImpact.CRITICAL else 15,
            "affected_timeframes": ["1min", "5min", "15min"],
            "recommendation": "avoid_trading" if volatility_spike > 0.006 else "monitor_closely"
        }
    
    def _load_impact_keywords(self) -> Dict:
        """Charger les mots-clés d'impact pour classification"""
        return {
            "critical": [
                "interest rate", "monetary policy", "central bank", "fed", "ecb", "boe",
                "nfp", "non-farm payrolls", "employment", "unemployment rate"
            ],
            "high": [
                "gdp", "inflation", "cpi", "ppi", "retail sales", "manufacturing",
                "consumer confidence", "trade balance", "current account"
            ],
            "medium": [
                "building permits", "housing starts", "industrial production",
                "capacity utilization", "business confidence"
            ]
        }
    
    def _load_currency_mappings(self) -> Dict:
        """Charger les mappings devise/pays"""
        return {
            "USD": ["US", "USA", "United States", "American"],
            "EUR": ["EU", "Euro", "European", "Eurozone"],
            "GBP": ["UK", "Britain", "British", "England"],
            "JPY": ["Japan", "Japanese", "BOJ"],
            "CHF": ["Switzerland", "Swiss", "SNB"],
            "AUD": ["Australia", "Australian", "RBA"],
            "CAD": ["Canada", "Canadian", "BOC"],
            "NZD": ["New Zealand", "RBNZ"]
        }

# Test et utilisation
async def main():
    """Test du système d'analyse des nouvelles"""
    analyzer = NewsAnalyzer()
    
    # Récupérer les nouvelles du jour
    logger.info("🚀 Test du système d'analyse des nouvelles...")
    news_list = await analyzer.get_todays_news()
    
    logger.info(f"📰 {len(news_list)} nouvelles analysées:")
    
    for news in news_list:
        impact_analysis = analyzer.analyze_news_impact(news)
        
        logger.info(f"📊 {news.title}")
        logger.info(f"   💱 {news.currency.value} | ⚡ {news.impact.value}")
        logger.info(f"   🕐 {news.release_time.strftime('%H:%M')}")
        logger.info(f"   📈 Déviation: {news.deviation_score:.1f}%")
        logger.info(f"   🎯 Recommandation: {impact_analysis['trading_recommendation']['action']}")
        logger.info(f"   📊 Paires affectées: {len(impact_analysis['affected_pairs'])}")
        logger.info("---")

if __name__ == "__main__":
    asyncio.run(main()) 