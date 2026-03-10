# Stock Backtesting Skill

A股量化回测系统 - 基于技术分析评分的完整回测框架

## 功能

- 📊 真实交易模拟（T+1开盘价执行）
- 🎯 完整的回测引擎（止损、止盈、仓位管理）
- 📈 权重优化器（网格搜索、Walk-Forward）
- 📝 多格式报告（JSON、Excel、HTML）

## 快速使用

### 1. 基础回测

```python
from backtesting.config import BACKTEST_CONFIG
from backtesting.engine import AStockBacktestEngine

config = BACKTEST_CONFIG.copy()
engine = AStockBacktestEngine(config)
result = engine.run_backtest(
    codes=['000592'],
    start_date='2023-01-01',
    end_date='2026-03-10',
    weights={'trend': 30, 'bias': 20, 'volume': 15, 'support': 10, 'macd': 15, 'rsi': 10}
)
```

### 2. 使用配置模板

```python
# 编辑 backtesting/config_template.py
python3 backtesting/quick_backtest.py
```

### 3. 权重优化

```python
from backtesting.optimizer import run_weight_optimization
best = run_weight_optimization(['000592'], step=10)
print(f"最优权重: {best['weights']}")
```

## 配置说明

见 `backtesting/config.py`

## 依赖

需要配合 `stock-daily-analysis-skill` 使用，提供数据获取和技术分析功能。

## 报告

回测完成后自动生成：
- JSON报告
- Excel交易明细
- HTML可视化报告