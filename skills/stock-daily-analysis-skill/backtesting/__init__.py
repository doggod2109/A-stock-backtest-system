# -*- coding: utf-8 -*-
"""
A股回测框架
基于评分系统的策略回测和优化
"""

from .config import (
    BACKTEST_CONFIG,
    DEFAULT_WEIGHTS,
    DYNAMIC_WEIGHT_CONFIG,
    SIGNAL_CONFIG,
    OPTIMIZATION_CONFIG,
    BENCHMARK_CONFIG,
    REPORT_CONFIG,
)

from .engine import AStockBacktestEngine, run_simple_backtest
from .optimizer import (
    WeightOptimizer,
    WalkForwardAnalyzer,
    DynamicWeightManager,
    run_weight_optimization,
)

__version__ = "1.0.0"
__all__ = [
    # Config
    'BACKTEST_CONFIG',
    'DEFAULT_WEIGHTS',
    'DYNAMIC_WEIGHT_CONFIG',
    'SIGNAL_CONFIG',
    'OPTIMIZATION_CONFIG',
    'BENCHMARK_CONFIG',
    'REPORT_CONFIG',

    # Engine
    'AStockBacktestEngine',
    'run_simple_backtest',

    # Optimizer
    'WeightOptimizer',
    'WalkForwardAnalyzer',
    'DynamicWeightManager',
    'run_weight_optimization',
]