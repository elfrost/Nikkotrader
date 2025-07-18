"""
Optimiseur de Stratégies NIKKOTRADER V11
Analyse et optimisation automatique des paramètres de stratégies
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from loguru import logger

@dataclass
class StrategyPerformance:
    """Données de performance d'une stratégie"""
    name: str
    win_rate: float
    avg_confidence: float
    total_trades: int
    profitable_trades: int
    avg_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    best_timeframes: List[str]
    best_pairs: List[str]
    optimal_params: Dict

class StrategyOptimizer:
    """Optimiseur de stratégies utilisant les données historiques"""
    
    def __init__(self):
        self.strategies_data = {}
        self.optimization_results = {}
        self.market_conditions = {}
        
    async def analyze_strategy_performance(self, strategy_name: str, days: int = 30) -> StrategyPerformance:
        """Analyser la performance d'une stratégie sur N jours"""
        logger.info(f"📊 Analyse performance {strategy_name} sur {days} jours")
        
        # Simulation de données (à remplacer par vraies données DB)
        performance_data = await self._get_strategy_data(strategy_name, days)
        
        # Calculs de performance
        win_rate = self._calculate_win_rate(performance_data)
        avg_confidence = self._calculate_avg_confidence(performance_data)
        sharpe_ratio = self._calculate_sharpe_ratio(performance_data)
        max_drawdown = self._calculate_max_drawdown(performance_data)
        
        # Analyse des meilleures conditions
        best_timeframes = self._find_best_timeframes(performance_data)
        best_pairs = self._find_best_pairs(performance_data)
        optimal_params = self._optimize_parameters(performance_data)
        
        return StrategyPerformance(
            name=strategy_name,
            win_rate=win_rate,
            avg_confidence=avg_confidence,
            total_trades=len(performance_data),
            profitable_trades=len([t for t in performance_data if t['pnl'] > 0]),
            avg_pnl=np.mean([t['pnl'] for t in performance_data]),
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            best_timeframes=best_timeframes,
            best_pairs=best_pairs,
            optimal_params=optimal_params
        )
    
    async def optimize_all_strategies(self) -> Dict[str, StrategyPerformance]:
        """Optimiser toutes les stratégies"""
        strategies = [
            "Breakout", "Pullback", "Range", "Scalping", 
            "MeanReversion", "Consolidation", "Divergence",
            "NewsImpact", "SessionBreakout"
        ]
        
        results = {}
        for strategy in strategies:
            try:
                performance = await self.analyze_strategy_performance(strategy)
                results[strategy] = performance
                logger.info(f"✅ {strategy}: Win Rate {performance.win_rate:.1f}%")
            except Exception as e:
                logger.error(f"❌ Erreur analyse {strategy}: {e}")
        
        return results
    
    def generate_optimization_recommendations(self, performance_data: Dict[str, StrategyPerformance]) -> Dict:
        """Générer des recommandations d'optimisation"""
        recommendations = {
            "top_performers": [],
            "needs_improvement": [],
            "parameter_adjustments": {},
            "timeframe_optimizations": {},
            "pair_recommendations": {}
        }
        
        # Classer les stratégies par performance
        sorted_strategies = sorted(
            performance_data.items(),
            key=lambda x: x[1].win_rate * x[1].sharpe_ratio,
            reverse=True
        )
        
        # Top 3 performers
        recommendations["top_performers"] = [
            {
                "name": name,
                "win_rate": perf.win_rate,
                "sharpe_ratio": perf.sharpe_ratio,
                "recommendation": "Maintenir configuration actuelle"
            }
            for name, perf in sorted_strategies[:3]
        ]
        
        # Stratégies à améliorer
        recommendations["needs_improvement"] = [
            {
                "name": name,
                "win_rate": perf.win_rate,
                "issues": self._identify_issues(perf),
                "suggested_fixes": self._suggest_fixes(perf)
            }
            for name, perf in sorted_strategies[-3:]
        ]
        
        # Optimisations de paramètres
        for name, perf in performance_data.items():
            if perf.win_rate < 65:  # Seuil d'amélioration
                recommendations["parameter_adjustments"][name] = {
                    "current_params": self._get_current_params(name),
                    "suggested_params": perf.optimal_params,
                    "expected_improvement": f"+{5-10}% win rate"
                }
        
        return recommendations
    
    def create_strategy_dashboard_data(self, performance_data: Dict[str, StrategyPerformance]) -> Dict:
        """Créer les données pour le dashboard de stratégies"""
        dashboard_data = {
            "summary": {
                "total_strategies": len(performance_data),
                "avg_win_rate": np.mean([p.win_rate for p in performance_data.values()]),
                "total_trades": sum([p.total_trades for p in performance_data.values()]),
                "best_strategy": max(performance_data.items(), key=lambda x: x[1].win_rate)[0]
            },
            "strategy_comparison": [
                {
                    "name": name,
                    "win_rate": perf.win_rate,
                    "trades_count": perf.total_trades,
                    "avg_confidence": perf.avg_confidence,
                    "sharpe_ratio": perf.sharpe_ratio,
                    "status": "excellent" if perf.win_rate > 75 else "good" if perf.win_rate > 65 else "needs_improvement"
                }
                for name, perf in performance_data.items()
            ],
            "timeframe_analysis": self._analyze_timeframe_performance(performance_data),
            "pair_analysis": self._analyze_pair_performance(performance_data)
        }
        
        return dashboard_data
    
    # Méthodes utilitaires
    async def _get_strategy_data(self, strategy_name: str, days: int) -> List[Dict]:
        """Récupérer les données de trading d'une stratégie"""
        # Simulation de données réelles
        np.random.seed(hash(strategy_name) % 2**32)
        
        num_trades = np.random.randint(50, 200)  # 50-200 trades sur la période
        trades = []
        
        for i in range(num_trades):
            # Générer des données réalistes basées sur le type de stratégie
            base_win_rate = self._get_strategy_base_win_rate(strategy_name)
            is_win = np.random.random() < base_win_rate
            
            trade = {
                'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, days*24*60)),
                'symbol': np.random.choice(['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD']),
                'direction': np.random.choice(['CALL', 'PUT']),
                'confidence': np.random.uniform(0.55, 0.95),
                'pnl': np.random.uniform(0.8, 1.0) if is_win else np.random.uniform(-1.0, -0.8),
                'expiry_minutes': self._get_strategy_expiry(strategy_name),
                'result': 'WIN' if is_win else 'LOSS'
            }
            trades.append(trade)
        
        return trades
    
    def _get_strategy_base_win_rate(self, strategy_name: str) -> float:
        """Obtenir le win rate de base théorique d'une stratégie"""
        base_rates = {
            'Breakout': 0.68,
            'Pullback': 0.72,
            'Range': 0.65,
            'Scalping': 0.62,
            'MeanReversion': 0.66,
            'Consolidation': 0.70,
            'Divergence': 0.75,
            'NewsImpact': 0.78,
            'SessionBreakout': 0.73
        }
        return base_rates.get(strategy_name, 0.65)
    
    def _get_strategy_expiry(self, strategy_name: str) -> int:
        """Obtenir l'expiry typique d'une stratégie"""
        expiries = {
            'Breakout': 5,
            'Pullback': 5,
            'Range': 10,
            'Scalping': 3,
            'MeanReversion': 5,
            'Consolidation': 3,
            'Divergence': 10,
            'NewsImpact': 15,
            'SessionBreakout': 30
        }
        return expiries.get(strategy_name, 5)
    
    def _calculate_win_rate(self, trades: List[Dict]) -> float:
        """Calculer le win rate"""
        if not trades:
            return 0.0
        wins = len([t for t in trades if t['result'] == 'WIN'])
        return (wins / len(trades)) * 100
    
    def _calculate_avg_confidence(self, trades: List[Dict]) -> float:
        """Calculer la confiance moyenne"""
        if not trades:
            return 0.0
        return np.mean([t['confidence'] for t in trades]) * 100
    
    def _calculate_sharpe_ratio(self, trades: List[Dict]) -> float:
        """Calculer le ratio de Sharpe"""
        if not trades:
            return 0.0
        returns = [t['pnl'] for t in trades]
        return np.mean(returns) / (np.std(returns) + 1e-6)
    
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Calculer le drawdown maximum"""
        if not trades:
            return 0.0
        
        # Simuler une courbe de capital
        cumulative_pnl = np.cumsum([t['pnl'] for t in trades])
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdown = (cumulative_pnl - running_max) / (running_max + 1)
        
        return abs(np.min(drawdown)) * 100
    
    def _find_best_timeframes(self, trades: List[Dict]) -> List[str]:
        """Identifier les meilleurs créneaux horaires"""
        # Analyser la performance par heure
        hourly_performance = {}
        for trade in trades:
            hour = trade['timestamp'].hour
            if hour not in hourly_performance:
                hourly_performance[hour] = []
            hourly_performance[hour].append(trade['pnl'])
        
        # Calculer le win rate par heure
        best_hours = []
        for hour, pnls in hourly_performance.items():
            win_rate = len([p for p in pnls if p > 0]) / len(pnls)
            if win_rate > 0.7:  # Seuil de 70%
                best_hours.append(f"{hour:02d}:00-{hour+1:02d}:00")
        
        return best_hours[:3]  # Top 3
    
    def _find_best_pairs(self, trades: List[Dict]) -> List[str]:
        """Identifier les meilleures paires de devises"""
        pair_performance = {}
        for trade in trades:
            pair = trade['symbol']
            if pair not in pair_performance:
                pair_performance[pair] = []
            pair_performance[pair].append(trade['pnl'])
        
        # Classer par performance
        pair_scores = {}
        for pair, pnls in pair_performance.items():
            win_rate = len([p for p in pnls if p > 0]) / len(pnls)
            avg_pnl = np.mean(pnls)
            pair_scores[pair] = win_rate * avg_pnl
        
        sorted_pairs = sorted(pair_scores.items(), key=lambda x: x[1], reverse=True)
        return [pair for pair, score in sorted_pairs[:3]]
    
    def _optimize_parameters(self, trades: List[Dict]) -> Dict:
        """Optimiser les paramètres basés sur la performance"""
        # Analyser les corrélations entre confidence et résultats
        confidences = [t['confidence'] for t in trades]
        results = [1 if t['result'] == 'WIN' else 0 for t in trades]
        
        # Trouver le seuil de confiance optimal
        optimal_confidence = 0.6
        best_performance = 0
        
        for threshold in np.arange(0.55, 0.85, 0.05):
            filtered_trades = [t for t in trades if t['confidence'] >= threshold]
            if len(filtered_trades) > 10:  # Minimum de trades
                win_rate = len([t for t in filtered_trades if t['result'] == 'WIN']) / len(filtered_trades)
                performance_score = win_rate * len(filtered_trades) / len(trades)  # Win rate pondéré par volume
                
                if performance_score > best_performance:
                    best_performance = performance_score
                    optimal_confidence = threshold
        
        return {
            "min_confidence_threshold": optimal_confidence,
            "suggested_max_signals_per_hour": len(trades) // 24 // 30,  # Moyenne par heure
            "optimal_trade_frequency": "medium" if len(trades) < 100 else "high"
        }
    
    def _identify_issues(self, performance: StrategyPerformance) -> List[str]:
        """Identifier les problèmes d'une stratégie"""
        issues = []
        
        if performance.win_rate < 60:
            issues.append("Win rate trop faible")
        if performance.sharpe_ratio < 0.5:
            issues.append("Ratio risque/rendement insuffisant")
        if performance.max_drawdown > 20:
            issues.append("Drawdown excessif")
        if performance.total_trades < 50:
            issues.append("Volume de trades insuffisant")
        
        return issues
    
    def _suggest_fixes(self, performance: StrategyPerformance) -> List[str]:
        """Suggérer des corrections"""
        fixes = []
        
        if performance.win_rate < 60:
            fixes.append("Augmenter le seuil de confiance minimum")
            fixes.append("Restreindre aux meilleures heures de marché")
        if performance.sharpe_ratio < 0.5:
            fixes.append("Optimiser les points d'entrée")
            fixes.append("Améliorer la gestion des stops")
        if performance.max_drawdown > 20:
            fixes.append("Réduire la taille des positions")
            fixes.append("Implémenter un filtre de corrélation")
        
        return fixes
    
    def _get_current_params(self, strategy_name: str) -> Dict:
        """Obtenir les paramètres actuels d'une stratégie"""
        # Retourner les paramètres par défaut (à remplacer par DB)
        default_params = {
            "confidence_base": 65,
            "max_signals_per_hour": 5,
            "expiry_minutes": 5
        }
        return default_params
    
    def _analyze_timeframe_performance(self, performance_data: Dict[str, StrategyPerformance]) -> Dict:
        """Analyser la performance par timeframe"""
        timeframe_groups = {
            "3min": ["Scalping", "Consolidation"],
            "5min": ["Breakout", "Pullback", "MeanReversion"],
            "10min": ["Range", "Divergence"],
            "15min": ["NewsImpact"],
            "30min": ["SessionBreakout"]
        }
        
        timeframe_analysis = {}
        for timeframe, strategies in timeframe_groups.items():
            strategy_performances = [performance_data[s] for s in strategies if s in performance_data]
            if strategy_performances:
                timeframe_analysis[timeframe] = {
                    "avg_win_rate": np.mean([p.win_rate for p in strategy_performances]),
                    "total_trades": sum([p.total_trades for p in strategy_performances]),
                    "best_strategy": max(strategy_performances, key=lambda x: x.win_rate).name
                }
        
        return timeframe_analysis
    
    def _analyze_pair_performance(self, performance_data: Dict[str, StrategyPerformance]) -> Dict:
        """Analyser la performance par paire de devises"""
        # Simulation d'analyse de paires
        pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD"]
        pair_analysis = {}
        
        for pair in pairs:
            # Simuler la performance de la paire
            win_rates = [np.random.uniform(0.6, 0.8) for _ in performance_data]
            pair_analysis[pair] = {
                "avg_win_rate": np.mean(win_rates) * 100,
                "best_strategies": list(performance_data.keys())[:3],
                "recommendation": "optimal" if np.mean(win_rates) > 0.7 else "moderate"
            }
        
        return pair_analysis

# Test et exemple d'utilisation
async def main():
    """Test de l'optimiseur de stratégies"""
    optimizer = StrategyOptimizer()
    
    # Analyser toutes les stratégies
    logger.info("🚀 Démarrage de l'analyse des stratégies...")
    performance_results = await optimizer.optimize_all_strategies()
    
    # Générer les recommandations
    recommendations = optimizer.generate_optimization_recommendations(performance_results)
    
    # Créer les données dashboard
    dashboard_data = optimizer.create_strategy_dashboard_data(performance_results)
    
    # Afficher les résultats
    logger.info("📊 RÉSULTATS D'OPTIMISATION:")
    for name, perf in performance_results.items():
        logger.info(f"📈 {name}: {perf.win_rate:.1f}% win rate, {perf.total_trades} trades")
    
    logger.info(f"🏆 Top Performers: {[r['name'] for r in recommendations['top_performers']]}")
    logger.info(f"⚠️  Need Improvement: {[r['name'] for r in recommendations['needs_improvement']]}")

if __name__ == "__main__":
    asyncio.run(main()) 