# -*- coding: utf-8 -*-
"""
A股回测框架配置文件
"""

# === 回测参数配置 ===
BACKTEST_CONFIG = {
    # 时间范围
    "start_date": "2023-01-01",
    "end_date": "2026-03-10",

    # 初始资金
    "init_cash": 1_000_000,

    # 手续费配置（A股）
    "fees": {
        "commission": 0.0003,      # 万三佣金
        "stamp_duty": 0.001,       # 千一印花税（仅卖出）
        "transfer_fee": 0.00002,   # 万二过户费（仅沪市）
    },

    # 滑点
    "slippage": 0.0001,

    # 仓位管理
    "position_size": 0.3,          # 单只股票最大仓位30%
    "max_positions": 3,            # 最多同时持有3只股票
}

# === 评分系统权重配置 ===
# 当前使用的权重（待优化）
DEFAULT_WEIGHTS = {
    "trend": 30,        # 趋势评分
    "bias": 20,         # 乖离率
    "volume": 15,       # 量能
    "support": 10,      # 支撑压力
    "macd": 15,         # MACD
    "rsi": 10,          # RSI
}

# === 动态权重配置 ===
DYNAMIC_WEIGHT_CONFIG = {
    # 市场环境因子
    "market_factors": {
        "vix_threshold": 25,           # VIX恐慌阈值
        "up_ratio_threshold": 0.7,     # 上涨家数占比阈值
        "bull_market_up_ratio": 0.75,  # 牛市定义
        "bear_market_up_ratio": 0.25,  # 熊市定义
    },

    # 权重调整范围
    "weight_adjustment": {
        "min_weight": 5,               # 最小权重
        "max_weight": 50,              # 最大权重
        "adjust_step": 5,              # 调整步长
    },
}

# === 买卖信号配置 ===
SIGNAL_CONFIG = {
    # 买入信号阈值
    "buy_thresholds": {
        "strong_buy": 75,      # 强烈买入
        "buy": 60,             # 买入
        "hold": 45,            # 持有
    },

    # 卖出信号阈值
    "sell_thresholds": {
        "strong_sell": 20,     # 强烈卖出
        "sell": 30,            # 卖出
        "wait": 40,            # 观望
    },

    # 止损止盈
    "risk_management": {
        "stop_loss": -0.08,        # -8%止损
        "take_profit": 0.15,       # +15%止盈
        "trailing_stop": 0.05,     # +5%回撤止盈
    },
}

# === 优化配置 ===
OPTIMIZATION_CONFIG = {
    # 权重搜索空间
    "weight_ranges": {
        "trend": (10, 50),
        "bias": (5, 35),
        "volume": (5, 25),
        "support": (5, 20),
        "macd": (5, 25),
        "rsi": (5, 20),
    },

    # 优化方法
    "method": "grid_search",  # grid_search, random_search, bayesian

    # 优化目标
    "objective": "sharpe_ratio",  # sharpe_ratio, total_return, sortino_ratio, profit_factor

    # 交叉验证
    "cv": {
        "method": "time_series",  # time_series, k_fold
        "n_splits": 5,
    },

    # Walk-Forward配置
    "walk_forward": {
        "train_size": 0.7,      # 训练集占比70%
        "test_size": 0.3,       # 测试集占比30%
        "step": 0.2,            # 滚动步长20%
    },
}

# === 基准配置 ===
BENCHMARK_CONFIG = {
    "symbol": "000300",           # 沪深300
    "name": "沪深300",
}

# === 回测报告配置 ===
REPORT_CONFIG = {
    # 评估指标
    "metrics": [
        "total_return",
        "annual_return",
        "sharpe_ratio",
        "sortino_ratio",
        "max_drawdown",
        "calmar_ratio",
        "win_rate",
        "profit_factor",
        "avg_win",
        "avg_loss",
        "total_trades",
    ],

    # 可视化
    "plots": [
        "equity_curve",
        "drawdown",
        "monthly_returns",
        "trade_distribution",
    ],
}