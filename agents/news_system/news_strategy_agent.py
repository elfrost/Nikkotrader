"""
Agent Stratégie NewsImpact - NIKKOTRADER V11
Agent spécialisé pour le trading basé sur l'impact des nouvelles économiques
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from .news_analyzer import NewsAnalyzer, EconomicNews, NewsImpact, Currency
from ..shared.base_agent import BaseAgent
from ..shared.models import TradingSignal, MarketCondition

class NewsImpactAgent(BaseAgent):
    """Agent de trading basé sur l'impact des nouvelles économiques"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.news_analyzer = NewsAnalyzer()
        self.active_news = []
        self.blocked_pairs = {}  # Paires temporairement bloquées
        self.opportunity_windows = {}  # Fenêtres d'opportunité
        
        # Configuration spécifique NewsImpact
        self.high_impact_only = config.get("high_impact_only", True)
        self.pre_news_minutes = config.get("pre_news_minutes", 15)
        self.post_news_minutes = config.get("post_news_minutes", 60)
        self.major_pairs_only = config.get("major_pairs_only", True)
        self.min_deviation_threshold = config.get("min_deviation_threshold", 2.0)
        
    async def initialize(self):
        """Initialiser l'agent NewsImpact"""
        await super().initialize()
        logger.info("📰 Initialisation NewsImpact Agent")
        
        # Charger les nouvelles du jour
        await self._load_daily_news()
        
        # Programmer les tâches de surveillance
        asyncio.create_task(self._news_monitoring_loop())
        asyncio.create_task(self._opportunity_scanner())
        
    async def _load_daily_news(self):
        """Charger et analyser les nouvelles du jour"""
        try:
            self.active_news = await self.news_analyzer.get_todays_news()
            logger.info(f"📊 {len(self.active_news)} nouvelles économiques chargées")
            
            # Programmer les blocages préventifs
            await self._schedule_preventive_blocks()
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement nouvelles: {e}")
            self.active_news = []
    
    async def _schedule_preventive_blocks(self):
        """Programmer les blocages préventifs avant les nouvelles importantes"""
        now = datetime.now()
        
        for news in self.active_news:
            if news.impact in [NewsImpact.HIGH, NewsImpact.CRITICAL]:
                affected_pairs = self.news_analyzer._get_affected_pairs(news.currency)
                
                # Bloquer avant la nouvelle
                block_start = news.release_time - timedelta(minutes=self.pre_news_minutes)
                block_end = news.release_time + timedelta(minutes=self.post_news_minutes)
                
                if block_start > now:  # Seulement si futur
                    for pair in affected_pairs:
                        if pair not in self.blocked_pairs:
                            self.blocked_pairs[pair] = []
                        
                        self.blocked_pairs[pair].append({
                            "start": block_start,
                            "end": block_end,
                            "reason": f"News: {news.title}",
                            "impact": news.impact.value
                        })
                
                logger.info(f"🚫 Blocage programmé pour {len(affected_pairs)} paires - {news.title}")
    
    async def _news_monitoring_loop(self):
        """Boucle de monitoring des nouvelles en temps réel"""
        while True:
            try:
                now = datetime.now()
                
                # Vérifier les nouvelles qui viennent de sortir (dernières 5 minutes)
                recent_news = [
                    news for news in self.active_news
                    if abs((now - news.release_time).total_seconds()) <= 300  # 5 minutes
                    and news.actual is not None
                ]
                
                for news in recent_news:
                    await self._process_released_news(news)
                
                # Nettoyer les blocages expirés
                await self._cleanup_expired_blocks()
                
                await asyncio.sleep(60)  # Vérifier chaque minute
                
            except Exception as e:
                logger.error(f"❌ Erreur monitoring news: {e}")
                await asyncio.sleep(300)
    
    async def _process_released_news(self, news: EconomicNews):
        """Traiter une nouvelle qui vient d'être publiée"""
        impact_analysis = self.news_analyzer.analyze_news_impact(news)
        
        logger.info(f"📰 Nouvelle publiée: {news.title}")
        logger.info(f"   🎯 Déviation: {news.deviation_score:.1f}%")
        logger.info(f"   📈 Réaction attendue: {news.market_reaction_expected}")
        
        # Vérifier si c'est une opportunité de trading
        recommendation = impact_analysis["trading_recommendation"]
        
        if recommendation["action"] == "trade_opportunity":
            await self._create_news_opportunity(news, impact_analysis)
        elif recommendation["action"] == "cautious_trade":
            await self._create_cautious_opportunity(news, impact_analysis)
        
        # Mettre à jour les blocages si nécessaire
        volatility_pred = impact_analysis["volatility_prediction"]
        if volatility_pred["recommendation"] == "avoid_trading":
            await self._extend_trading_blocks(news, volatility_pred["duration_minutes"])
    
    async def _create_news_opportunity(self, news: EconomicNews, analysis: Dict):
        """Créer une fenêtre d'opportunité de trading basée sur une nouvelle"""
        affected_pairs = analysis["affected_pairs"]
        recommendation = analysis["trading_recommendation"]
        
        logger.info(f"🚀 Opportunité de trading détectée: {news.title}")
        
        for pair in affected_pairs:
            if self._is_pair_tradeable(pair):
                
                # Déterminer la direction basée sur l'impact
                direction = self._determine_trade_direction(pair, news, recommendation)
                
                if direction:
                    signal = await self._generate_news_signal(
                        pair, direction, news, analysis
                    )
                    
                    if signal:
                        await self._send_signal(signal)
                        
                        # Programmer la fenêtre d'opportunité
                        opportunity_duration = recommendation.get("timeframe", "15 minutes")
                        duration_minutes = self._parse_duration(opportunity_duration)
                        
                        self.opportunity_windows[f"{pair}_{news.id}"] = {
                            "pair": pair,
                            "start": datetime.now(),
                            "end": datetime.now() + timedelta(minutes=duration_minutes),
                            "direction": direction,
                            "news_title": news.title,
                            "confidence": recommendation["confidence"]
                        }
    
    def _determine_trade_direction(self, pair: str, news: EconomicNews, recommendation: Dict) -> Optional[str]:
        """Déterminer la direction du trade basée sur la nouvelle et la paire"""
        
        # Logique de corrélation devise/paire
        base_currency = pair[:3]
        quote_currency = pair[3:]
        
        reaction = recommendation["direction"]
        news_currency = news.currency.value
        
        if base_currency == news_currency:
            # La devise de base est affectée
            if reaction == "bullish":
                return "CALL"  # Devise forte -> paire monte
            elif reaction == "bearish":
                return "PUT"   # Devise faible -> paire baisse
        
        elif quote_currency == news_currency:
            # La devise de cotation est affectée
            if reaction == "bullish":
                return "PUT"   # Devise de cotation forte -> paire baisse
            elif reaction == "bearish":
                return "CALL"  # Devise de cotation faible -> paire monte
        
        return None
    
    async def _generate_news_signal(self, pair: str, direction: str, news: EconomicNews, analysis: Dict) -> Optional[TradingSignal]:
        """Générer un signal de trading basé sur une nouvelle"""
        
        try:
            # Obtenir les données de marché actuelles
            market_data = await self._get_current_market_data(pair)
            if not market_data:
                return None
            
            # Calculer la confiance basée sur la déviation et l'impact
            base_confidence = analysis["trading_recommendation"]["confidence"]
            impact_bonus = {
                NewsImpact.CRITICAL: 0.15,
                NewsImpact.HIGH: 0.10,
                NewsImpact.MEDIUM: 0.05,
                NewsImpact.LOW: 0.0
            }[news.impact]
            
            final_confidence = min(0.95, base_confidence + impact_bonus)
            
            # Ajuster l'expiry basé sur l'impact
            expiry_minutes = 15  # Par défaut
            if news.impact == NewsImpact.CRITICAL:
                expiry_minutes = 30
            elif news.deviation_score > 10:
                expiry_minutes = 20
            
            signal = TradingSignal(
                id=f"news_{news.id}_{pair}_{datetime.now().strftime('%H%M%S')}",
                strategy="NewsImpact",
                symbol=pair,
                direction=direction,
                confidence=final_confidence,
                entry_price=market_data["current_price"],
                expiry_minutes=expiry_minutes,
                market_condition=MarketCondition.NEWS_DRIVEN,
                metadata={
                    "news_title": news.title,
                    "news_currency": news.currency.value,
                    "news_impact": news.impact.value,
                    "deviation_score": news.deviation_score,
                    "market_reaction": news.market_reaction_expected,
                    "release_time": news.release_time.isoformat(),
                    "analysis_confidence": analysis["trading_recommendation"]["confidence"],
                    "volatility_spike_expected": analysis["volatility_prediction"]["expected_volatility_spike"]
                }
            )
            
            logger.info(f"📊 Signal NewsImpact généré: {pair} {direction} @ {final_confidence:.2f}")
            return signal
            
        except Exception as e:
            logger.error(f"❌ Erreur génération signal news: {e}")
            return None
    
    def _is_pair_tradeable(self, pair: str) -> bool:
        """Vérifier si une paire est tradeable (pas bloquée)"""
        now = datetime.now()
        
        if pair in self.blocked_pairs:
            active_blocks = [
                block for block in self.blocked_pairs[pair]
                if block["start"] <= now <= block["end"]
            ]
            
            if active_blocks:
                logger.debug(f"🚫 Paire {pair} bloquée: {active_blocks[0]['reason']}")
                return False
        
        return True
    
    async def _opportunity_scanner(self):
        """Scanner les opportunités de trading liées aux nouvelles"""
        while True:
            try:
                now = datetime.now()
                
                # Vérifier les fenêtres d'opportunité actives
                active_opportunities = {
                    key: opp for key, opp in self.opportunity_windows.items()
                    if opp["start"] <= now <= opp["end"]
                }
                
                if active_opportunities:
                    logger.info(f"🎯 {len(active_opportunities)} opportunités news actives")
                
                # Nettoyer les opportunités expirées
                expired_keys = [
                    key for key, opp in self.opportunity_windows.items()
                    if now > opp["end"]
                ]
                
                for key in expired_keys:
                    del self.opportunity_windows[key]
                
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Erreur scanner opportunités: {e}")
                await asyncio.sleep(600)
    
    async def _cleanup_expired_blocks(self):
        """Nettoyer les blocages expirés"""
        now = datetime.now()
        
        for pair in list(self.blocked_pairs.keys()):
            self.blocked_pairs[pair] = [
                block for block in self.blocked_pairs[pair]
                if now < block["end"]
            ]
            
            if not self.blocked_pairs[pair]:
                del self.blocked_pairs[pair]
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parser une durée en string vers minutes"""
        # Ex: "15-30 minutes" -> 22 (moyenne)
        import re
        
        numbers = re.findall(r'\d+', duration_str)
        if len(numbers) == 2:
            return (int(numbers[0]) + int(numbers[1])) // 2
        elif len(numbers) == 1:
            return int(numbers[0])
        else:
            return 15  # Défaut
    
    async def get_strategy_status(self) -> Dict:
        """Obtenir le statut de la stratégie NewsImpact"""
        now = datetime.now()
        
        # Nouvelles à venir dans les prochaines 4 heures
        upcoming_news = [
            news for news in self.active_news
            if news.release_time > now 
            and (news.release_time - now).total_seconds() < 14400  # 4h
        ]
        
        # Paires actuellement bloquées
        blocked_pairs_count = len([
            pair for pair, blocks in self.blocked_pairs.items()
            if any(block["start"] <= now <= block["end"] for block in blocks)
        ])
        
        # Opportunités actives
        active_opportunities = len([
            opp for opp in self.opportunity_windows.values()
            if opp["start"] <= now <= opp["end"]
        ])
        
        return {
            "agent_type": "NewsImpact",
            "status": "active",
            "upcoming_news_4h": len(upcoming_news),
            "blocked_pairs": blocked_pairs_count,
            "active_opportunities": active_opportunities,
            "total_news_today": len(self.active_news),
            "high_impact_news": len([n for n in self.active_news if n.impact == NewsImpact.HIGH]),
            "critical_news": len([n for n in self.active_news if n.impact == NewsImpact.CRITICAL]),
            "next_major_news": upcoming_news[0].title if upcoming_news else None,
            "next_news_time": upcoming_news[0].release_time.isoformat() if upcoming_news else None
        }
    
    async def analyze_market_conditions(self) -> Dict:
        """Analyser les conditions de marché liées aux nouvelles"""
        
        news_outlook = {
            "short_term_2h": [],
            "medium_term_4h": [],
            "daily_impact": "low"
        }
        
        now = datetime.now()
        
        # Nouvelles dans les 2 prochaines heures
        for news in self.active_news:
            time_diff = (news.release_time - now).total_seconds() / 3600
            
            if 0 <= time_diff <= 2:
                news_outlook["short_term_2h"].append({
                    "title": news.title,
                    "currency": news.currency.value,
                    "impact": news.impact.value,
                    "time": news.release_time.strftime("%H:%M")
                })
            elif 0 <= time_diff <= 4:
                news_outlook["medium_term_4h"].append({
                    "title": news.title,
                    "currency": news.currency.value,
                    "impact": news.impact.value,
                    "time": news.release_time.strftime("%H:%M")
                })
        
        # Évaluer l'impact quotidien global
        critical_count = len([n for n in self.active_news if n.impact == NewsImpact.CRITICAL])
        high_count = len([n for n in self.active_news if n.impact == NewsImpact.HIGH])
        
        if critical_count >= 2:
            news_outlook["daily_impact"] = "very_high"
        elif critical_count >= 1 or high_count >= 3:
            news_outlook["daily_impact"] = "high" 
        elif high_count >= 2:
            news_outlook["daily_impact"] = "medium"
        
        return news_outlook

# Test de l'agent NewsImpact
async def test_news_impact_agent():
    """Test de l'agent NewsImpact"""
    
    config = {
        "strategy_name": "NewsImpact",
        "min_confidence": 0.80,
        "high_impact_only": True,
        "pre_news_minutes": 15,
        "post_news_minutes": 60,
        "major_pairs_only": True,
        "min_deviation_threshold": 2.0
    }
    
    agent = NewsImpactAgent(config)
    await agent.initialize()
    
    # Afficher le statut
    status = await agent.get_strategy_status()
    logger.info(f"📊 Statut NewsImpact Agent: {status}")
    
    # Analyser les conditions de marché
    market_conditions = await agent.analyze_market_conditions()
    logger.info(f"📈 Conditions marché news: {market_conditions}")

if __name__ == "__main__":
    asyncio.run(test_news_impact_agent()) 