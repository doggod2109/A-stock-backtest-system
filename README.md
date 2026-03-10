# 🎯 A股智能回测系统

> 基于技术分析评分系统的A股量化回测框架

## ✨ 特性

- 📊 **完整的技术分析评分系统**：6个维度综合评分（趋势、乖离率、量能、支撑压力、MACD、RSI）
- 🔬 **智能回测引擎**：支持止损止盈、仓位管理、滑点模拟
- 📈 **权重优化器**：网格搜索、Walk-Forward验证、动态权重调整
- 📝 **自动化报告**：JSON、Excel、HTML多格式报告生成
- 🔄 **多数据源**：腾讯财经、新浪财经、东方财富API自动切换
- 🎯 **真实交易模拟**：T日计算信号 → T+1日开盘价执行交易

## 🚀 快速开始

### 安装依赖

```bash
pip install pandas numpy requests openpyxl
```

### 运行回测

```python
from backtesting.config import BACKTEST_CONFIG
from backtesting.engine import AStockBacktestEngine

# 配置参数
config = BACKTEST_CONFIG.copy()
config['init_cash'] = 1_000_000
config['buy_threshold'] = 60
config['sell_threshold'] = 30

# 创建回测引擎
engine = AStockBacktestEngine(config)

# 运行回测
result = engine.run_backtest(
    codes=['000592'],
    start_date='2023-01-01',
    end_date='2026-03-10',
    weights={
        'trend': 30,
        'bias': 20,
        'volume': 15,
        'support': 10,
        'macd': 15,
        'rsi': 10
    }
)

# 查看结果
print(f"总收益率: {result['total_return']:.2%}")
print(f"年化收益率: {result['annual_return']:.2%}")
print(f"夏普比率: {result['sharpe_ratio']:.2f}")
```

### 使用配置模板

修改 `config_template.py` 后运行：

```bash
python3 backtesting/quick_backtest.py
```

## 📊 评分系统

### 评分维度（100分）

| 维度 | 权重 | 评分规则 |
|------|------|----------|
| 趋势 | 30 | 强势多头=30, 多头排列=26, 盘整=12, 空头=4 |
| 乖离率 | 20 | 负乖离（回调）高分, 正乖离>5%低分 |
| 量能 | 15 | 缩量回调=15, 放量上涨=12, 放量下跌=0 |
| 支撑压力 | 10 | MA5支撑=5, MA10支撑=5 |
| MACD | 15 | 零轴金叉=15, 金叉=12, 死叉=0 |
| RSI | 10 | 超卖=10, 强势买入=8, 超买=0 |

### 信号阈值

- **买入信号**：评分 >= 60分
- **持有信号**：30分 <= 评分 < 60分
- **卖出信号**：评分 < 30分

## 🔧 配置说明

### 交易费用

```python
commission_rate = 0.0003  # 万三佣金
stamp_duty_rate = 0.001   # 千一印花税（仅卖出）
transfer_fee_rate = 0.00002  # 万二过户费
slippage = 0.0001         # 万一滑点
```

### 风险管理

```python
stop_loss = -0.08     # -8% 止损
take_profit = 0.15    # +15% 止盈
position_size = 1.0   # 单只仓位100%
max_positions = 1     # 最多持仓1只
```

## 📁 项目结构

```
stock-agent/
├── skills/
│   └── stock-daily-analysis-skill/
│       ├── scripts/
│       │   ├── data_fetcher.py       # 数据获取
│       │   ├── trend_analyzer.py     # 技术分析
│       │   └── ai_analyzer.py        # AI分析
│       └── backtesting/
│           ├── config.py             # 配置文件
│           ├── engine.py             # 回测引擎
│           ├── optimizer.py          # 优化器
│           ├── report_generator.py   # 报告生成
│           ├── interactive.py        # 交互配置
│           ├── quick_backtest.py     # 快速回测
│           └── config_template.py    # 配置模板
├── OPTIMIZATION_GUIDE.md             # 优化指南
├── AGENTS.md                         # Agent配置
├── SOUL.md                           # Agent人格
└── README.md                         # 项目说明
```

## 📈 回测示例

### 示例：000592 平潭发展（2023-2026）

**配置：**
- 初始资金：¥1,000,000
- 时间范围：2023-01-01 ~ 2026-03-10
- 仓位：100%单只
- 止损：-8%，止盈：+15%

**结果：**
- 总收益率：365.61%
- 年化收益率：65.98%
- 夏普比率：1.39
- 最大回撤：-35.84%
- 胜率：58.62%
- 交易次数：29次

## 🎯 优化方向

详细优化指南请查看 [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md)

### 高优先级
- ✅ 权重优化
- ✅ Walk-Forward验证
- 🚧 买卖阈值优化
- 🚧 止损止盈优化

### 中优先级
- 🚧 仓位管理优化
- 🚧 评分维度优化
- 🚧 多市场环境优化

## ⚠️ 风险提示

- 本系统仅供学习和研究使用
- 回测结果不代表未来表现
- 实际投资请谨慎决策
- 股市有风险，投资需谨慎

## 📝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👤 作者

**总舵主徐祥** - 专业股票分析师

---

*最后更新：2026-03-10*