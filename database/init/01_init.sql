-- Script d'initialisation pour NIKKOTRADER V11
-- Création des extensions et données de base

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Insertion des stratégies de base
INSERT INTO strategies (id, name, version, description, config, created_at, created_by, is_active) VALUES
(
    uuid_generate_v4(),
    'Breakout',
    'v1.0.0',
    'Stratégie de breakout sur niveaux de support/résistance',
    '{
        "min_adx": 25,
        "lookback_periods": 20,
        "volume_filter": true,
        "confidence_base": 65,
        "expiry_minutes": 5,
        "market_hours_filter": true,
        "volatility_min": 0.0005,
        "spread_max": 3,
        "time_windows": ["08:00-12:00", "13:00-17:00"],
        "avoid_news_minutes": 30
    }',
    NOW(),
    'system',
    true
),
(
    uuid_generate_v4(),
    'Pullback',
    'v1.0.0',
    'Stratégie de pullback sur niveaux de Fibonacci',
    '{
        "fibonacci_levels": [0.382, 0.5, 0.618],
        "min_adx": 20,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "confidence_base": 70,
        "expiry_minutes": 5
    }',
    NOW(),
    'system',
    true
),
(
    uuid_generate_v4(),
    'Range',
    'v1.0.0',
    'Stratégie de trading en range',
    '{
        "max_adx": 20,
        "range_periods": 20,
        "bounce_confirmation": true,
        "confidence_base": 65,
        "expiry_minutes": 10
    }',
    NOW(),
    'system',
    true
),
(
    uuid_generate_v4(),
    'Scalping',
    'v1.0.0',
    'Stratégie de scalping rapide',
    '{
        "rsi_extreme_buy": 25,
        "rsi_extreme_sell": 75,
        "max_adx": 20,
        "confidence_base": 60,
        "expiry_minutes": 3
    }',
    NOW(),
    'system',
    true
),
(
    uuid_generate_v4(),
    'MeanReversion',
    'v1.0.0',
    'Stratégie de retour à la moyenne',
    '{
        "bb_periods": 20,
        "bb_std_dev": 2.0,
        "rsi_threshold": 30,
        "confidence_base": 65,
        "expiry_minutes": 5
    }',
    NOW(),
    'system',
    true
),
(
    uuid_generate_v4(),
    'Consolidation',
    'v1.0.0',
    'Stratégie de consolidation',
    '{
        "consolidation_periods": 15,
        "volatility_threshold": 0.001,
        "breakout_confirmation": true,
        "confidence_base": 70,
        "expiry_minutes": 3
    }',
    NOW(),
    'system',
    true
),
    (
        uuid_generate_v4(),
        'Divergence',
        'v1.0.0',
        'Stratégie basée sur les divergences',
        '{
            "rsi_periods": 14,
            "macd_fast": 12,
            "macd_slow": 26,
            "divergence_lookback": 20,
            "confidence_base": 75,
            "expiry_minutes": 10
        }',
        NOW(),
        'system',
        true
    ),
    (
        uuid_generate_v4(),
        'NewsImpact',
        'v1.0.0',
        'Stratégie basée sur l\'impact des nouvelles économiques',
        '{
            "news_calendar_enabled": true,
            "high_impact_only": true,
            "pre_news_minutes": 15,
            "post_news_minutes": 60,
            "volatility_spike_threshold": 0.002,
            "confidence_base": 80,
            "expiry_minutes": 15,
            "major_pairs_only": true,
            "avoid_overlapping_news": true
        }',
        NOW(),
        'system',
        true
    ),
    (
        uuid_generate_v4(),
        'SessionBreakout',
        'v1.0.0',
        'Stratégie de breakout aux ouvertures de sessions',
        '{
            "sessions": {
                "london": "08:00-09:00",
                "new_york": "13:00-14:00",
                "tokyo": "00:00-01:00"
            },
            "pre_session_range_minutes": 60,
            "breakout_threshold": 0.0008,
            "volume_confirmation": true,
            "confidence_base": 70,
            "expiry_minutes": 30,
            "max_trades_per_session": 2
        }',
        NOW(),
        'system',
        true
    );

-- Insertion des agents de base
INSERT INTO agents (id, name, type, status, config, created_at) VALUES
(
    uuid_generate_v4(),
    'MasterAgent',
    'master',
    'stopped',
    '{
        "max_concurrent_tasks": 10,
        "heartbeat_interval": 30,
        "decision_timeout": 10
    }',
    NOW()
),
(
    uuid_generate_v4(),
    'MarketDataAgent',
    'market_data',
    'stopped',
    '{
        "scan_interval": 5,
        "max_retries": 3,
        "symbols": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD"]
    }',
    NOW()
),
(
    uuid_generate_v4(),
    'BreakoutAgent',
    'strategy',
    'stopped',
    '{
        "strategy_name": "Breakout",
        "min_confidence": 65,
        "max_signals_per_hour": 5
    }',
    NOW()
),
(
    uuid_generate_v4(),
    'PullbackAgent',
    'strategy',
    'stopped',
    '{
        "strategy_name": "Pullback",
        "min_confidence": 70,
        "max_signals_per_hour": 3
    }',
    NOW()
),
(
    uuid_generate_v4(),
    'RangeAgent',
    'strategy',
    'stopped',
    '{
        "strategy_name": "Range",
        "min_confidence": 65,
        "max_signals_per_hour": 4
    }',
    NOW()
),
(
    uuid_generate_v4(),
    'ScalpingAgent',
    'strategy',
    'stopped',
    '{
        "strategy_name": "Scalping",
        "min_confidence": 60,
        "max_signals_per_hour": 10
    }',
    NOW()
),
(
    uuid_generate_v4(),
    'MeanReversionAgent',
    'strategy',
    'stopped',
    '{
        "strategy_name": "MeanReversion",
        "min_confidence": 65,
        "max_signals_per_hour": 5
    }',
    NOW()
),
(
    uuid_generate_v4(),
    'ConsolidationAgent',
    'strategy',
    'stopped',
    '{
        "strategy_name": "Consolidation",
        "min_confidence": 70,
        "max_signals_per_hour": 3
    }',
    NOW()
),
    (
        uuid_generate_v4(),
        'DivergenceAgent',
        'strategy',
        'stopped',
        '{
            "strategy_name": "Divergence",
            "min_confidence": 75,
            "max_signals_per_hour": 2
        }',
        NOW()
    ),
    (
        uuid_generate_v4(),
        'NewsImpactAgent',
        'strategy',
        'stopped',
        '{
            "strategy_name": "NewsImpact",
            "min_confidence": 80,
            "max_signals_per_hour": 4,
            "news_calendar_api": true,
            "major_currencies_only": true
        }',
        NOW()
    ),
    (
        uuid_generate_v4(),
        'SessionBreakoutAgent',
        'strategy',
        'stopped',
        '{
            "strategy_name": "SessionBreakout",
            "min_confidence": 70,
            "max_signals_per_hour": 6,
            "session_monitoring": true,
            "timezone_aware": true
        }',
        NOW()
    ),
    (
        uuid_generate_v4(),
        'RiskManagementAgent',
        'risk',
        'stopped',
        '{
            "max_drawdown": 0.50,
            "max_daily_loss": 0.25,
            "max_concurrent_positions": 20,
            "position_sizing": "fixed",
            "forward_testing_mode": true,
            "permissive_risk": true,
            "data_collection_priority": true
        }',
        NOW()
    ),
(
    uuid_generate_v4(),
    'NotificationAgent',
    'notification',
    'stopped',
    '{
        "telegram_enabled": true,
        "min_interval": 60,
        "alert_levels": ["info", "warning", "error"]
    }',
    NOW()
);

-- Insertion des configurations de base
INSERT INTO configurations (id, key, value, version, is_active, description, created_at, created_by) VALUES
(
    uuid_generate_v4(),
    'trading.demo_account_only',
    'true',
    1,
    true,
    'Force l''utilisation du compte démo uniquement',
    NOW(),
    'system'
),
    (
        uuid_generate_v4(),
        'trading.max_daily_trades',
        '500',
        1,
        true,
        'Nombre maximum de trades par jour (Forward Testing)',
        NOW(),
        'system'
    ),
    (
        uuid_generate_v4(),
        'trading.max_concurrent_positions',
        '20',
        1,
        true,
        'Nombre maximum de positions concurrentes (Forward Testing)',
        NOW(),
        'system'
    ),
    (
        uuid_generate_v4(),
        'risk.max_drawdown',
        '0.50',
        1,
        true,
        'Drawdown maximum autorisé (50% - Forward Testing)',
        NOW(),
        'system'
    ),
(
    uuid_generate_v4(),
    'risk.stop_loss_percentage',
    '0.02',
    1,
    true,
    'Stop loss en pourcentage (2%)',
    NOW(),
    'system'
),
(
    uuid_generate_v4(),
    'monitoring.performance_tracking',
    'true',
    1,
    true,
    'Activer le suivi des performances détaillé',
    NOW(),
    'system'
),
(
    uuid_generate_v4(),
    'notifications.telegram_enabled',
    'true',
    1,
    true,
    'Activer les notifications Telegram',
    NOW(),
    'system'
),
    (
        uuid_generate_v4(),
        'system.forward_testing_mode',
        'true',
        1,
        true,
        'Mode forward testing activé',
        NOW(),
        'system'
    ),
    (
        uuid_generate_v4(),
        'risk.permissive_mode',
        'true',
        1,
        true,
        'Mode risque permissif pour collecte de données (Forward Testing)',
        NOW(),
        'system'
    ),
    (
        uuid_generate_v4(),
        'system.data_collection_priority',
        'true',
        1,
        true,
        'Priorité à la collecte de données sur la protection (Forward Testing)',
        NOW(),
        'system'
    );

-- Insertion d'un événement système de démarrage
INSERT INTO system_events (id, event_type, description, data, severity, created_at) VALUES
(
    uuid_generate_v4(),
    'system.initialization',
    'Initialisation de la base de données NIKKOTRADER V11 - Options Binaires Optimisées',
    '{
        "version": "11.0.0",
        "strategies_count": 9,
        "agents_count": 13,
        "configurations_count": 10,
        "binary_options_optimized": true,
        "timeframes": ["3min", "5min", "10min", "15min", "30min"],
        "new_strategies": ["NewsImpact", "SessionBreakout"]
    }',
    'info',
    NOW()
);

-- Vues pour faciliter les requêtes
CREATE OR REPLACE VIEW v_active_strategies AS
SELECT 
    s.id,
    s.name,
    s.version,
    s.description,
    s.config,
    s.created_at,
    COUNT(t.id) as total_trades,
    COUNT(CASE WHEN t.result = 'WIN' THEN 1 END) as winning_trades,
    ROUND(
        COUNT(CASE WHEN t.result = 'WIN' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN t.result IN ('WIN', 'LOSS') THEN 1 END), 0), 
        2
    ) as win_rate
FROM strategies s
LEFT JOIN trades t ON s.id = t.strategy_id
WHERE s.is_active = true
GROUP BY s.id, s.name, s.version, s.description, s.config, s.created_at;

CREATE OR REPLACE VIEW v_agent_status AS
SELECT 
    a.id,
    a.name,
    a.type,
    a.status,
    a.last_heartbeat,
    a.total_tasks,
    a.successful_tasks,
    a.failed_tasks,
    ROUND(
        a.successful_tasks * 100.0 / NULLIF(a.total_tasks, 0), 
        2
    ) as success_rate
FROM agents a;

CREATE OR REPLACE VIEW v_daily_performance AS
SELECT 
    DATE(t.entry_time) as trading_date,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN t.result = 'WIN' THEN 1 END) as winning_trades,
    COUNT(CASE WHEN t.result = 'LOSS' THEN 1 END) as losing_trades,
    ROUND(
        COUNT(CASE WHEN t.result = 'WIN' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN t.result IN ('WIN', 'LOSS') THEN 1 END), 0), 
        2
    ) as win_rate,
    ROUND(SUM(COALESCE(t.pnl, 0)), 2) as daily_pnl
FROM trades t
WHERE t.entry_time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(t.entry_time)
ORDER BY trading_date DESC; 