# A股回测框架

基于评分系统的A股策略回测和优化框架

## 功能特性

- ✅ **回测引擎** - 完整的A股交易回测，支持手续费、滑点、止损止盈
- ✅ **权重优化** - 网格搜索最优评分权重组合
- ✅ **Walk-Forward分析** - 前向验证，避免过拟合
- ✅ **动态权重** - 根据市场环境自动调整权重
- ✅ **权重对比** - 对比不同权重组合的表现
- ✅ **完整报告** - 收益率、夏普比率、最大回撤等指标

## 快速开始

### 1. 简单回测

```python
from backtesting import run_simple_backtest

# 定义股票池
codes = ['002353', '000592', '600519']

# 运行回测（使用默认权重）
result = run_simple_backtest(codes)

# 查看结果
print(f"总收益率: {result['total_return']:.2%}")
print(f"夏普比率: {result['sharpe_ratio']:.2f}")
print(f"最大回撤: {result['max_drawdown']:.2%}")
```

### 2. 权重优化

```python
from backtesting import run_weight_optimization

# 优化权重（网格搜索）
best = run_weight_optimization(codes, step=10)

# 查看最优权重
print(f"最优权重: {best['weights']}")

# 使用最优权重重新回测
result = run_simple_backtest(codes, best['weights'])
```

### 3. 权重对比

```python
from backtesting import WeightOptimizer

# 定义多组权重
weight_sets = [
    {'trend': 30, 'bias': 20, 'volume': 15, 'support': 10, 'macd': 15, 'rsi': 10},
    {'trend': 35, 'bias': 15, 'volume': 20, 'support': 10, 'macd': 10, 'rsi': 10},
    {'trend': 25, 'bias': 25, 'volume': 10, 'support': 15, 'macd': 15, 'rsi': 10},
]

names = ['默认权重', '趋势增强', '乖离增强']

# 对比回测
optimizer = WeightOptimizer()
comparison = optimizer.compare_weights(codes, weight_sets, names)

print(comparison)
```

### 4. Walk-Forward分析

```python
from backtesting import WalkForwardAnalyzer

# Walk-Forward前向验证
analyzer = WalkForwardAnalyzer()
result = analyzer.analyze(codes, "2023-01-01", "2026-03-10")

# 查看汇总统计
summary = result['summary']
print(f"平均夏普比率: {summary['avg_sharpe_ratio']:.2f}")
print(f"WFE比率: {summary['wfe_ratio']:.2f}")
```

## 运行测试

```bash
cd /home/admin/openclaw/stock-agent/skills/stock-daily-analysis-skill/backtesting
python test_backtest.py
```

## 配置说明

### 评分权重配置

```python
DEFAULT_WEIGHTS = {
    "trend": 30,        # 趋势评分 (10-50)
    "bias": 20,         # 乖离率 (5-35)
    "volume": 15,       # 量能 (5-25)
    "support": 10,      # 支撑压力 (5-20)
    "macd": 15,         # MACD (5-25)
    "rsi": 10,          # RSI (5-20)
}
```

### 优化配置

```python
OPTIMIZATION_CONFIG = {
    "weight_ranges": {
        "trend": (10, 50),
        "bias": (5, 35),
        "volume": (5, 25),
        "support": (5, 20),
        "macd": (5, 25),
        "rsi": (5, 20),
    },
    "objective": "sharpe_ratio",  # 优化目标
    "method": "grid_search",
}
```

### 风险管理配置

```python
SIGNAL_CONFIG = {
    "risk_management": {
        "stop_loss": -0.08,        # -8%止损
        "take_profit": 0.15,       # +15%止盈
        "trailing_stop": 0.05,     # +5%回撤止盈
    },
}
```

## 回测指标

- **总收益率**: 整个回测期间的总收益
- **年化收益率**: 折算成年化收益
- **夏普比率**: 风险调整后收益
- **最大回撤**: 最大的资金回撤
- **胜率**: 盈利交易占比
- **平均盈亏比**: 平均盈利/平均亏损
- **总交易次数**: 完成的交易数

## 文件结构

```
backtesting/
├── __init__.py           # 模块入口
├── config.py             # 配置文件
├── engine.py             # 回测引擎
├── optimizer.py          # 权重优化器
├── test_backtest.py      # 测试脚本
└── README.md             # 说明文档
```

## 下一步

- [ ] 添加更多数据源支持
- [ ] 实现动态权重管理（基于VIX、涨跌停数等市场因子）
- [ ] 添加可视化图表（权益曲线、回撤图等）
- [ ] 实现多因子回测
- [ ] 添加实盘交易接口

## 注意事项

⚠️ **风险提示**：
- 本框架仅供学习研究使用
- 回测结果不代表未来表现
- 实盘交易有风险，请谨慎操作
- 建议在充分测试后再考虑实盘