# A股回测系统

基于技术分析评分系统的A股量化回测框架

## 特性

- 📊 真实交易模拟：T日计算信号 → T+1日开盘价执行
- 📈 完整的回测引擎：支持止损止盈、仓位管理、滑点模拟
- 🎯 权重优化器：网格搜索、Walk-Forward验证、动态权重调整
- 📝 自动化报告：JSON、Excel、HTML多格式报告生成
- 🔄 多数据源支持：腾讯财经、新浪财经、东方财富API

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置参数

编辑 `backtesting/config_template.py`，设置回测参数。

### 运行回测

```python
from backtesting.config import BACKTEST_CONFIG
from backtesting.engine import AStockBacktestEngine

config = BACKTEST_CONFIG.copy()
config['init_cash'] = 1_000_000
config['buy_threshold'] = 60
config['sell_threshold'] = 30

engine = AStockBacktestEngine(config)
result = engine.run_backtest(
    codes=['000592'],
    start_date='2023-01-01',
    end_date='2026-03-10',
    weights={'trend': 30, 'bias': 20, 'volume': 15, 'support': 10, 'macd': 15, 'rsi': 10}
)
```

### 使用配置模板

修改 `backtesting/config_template.py` 后运行：

```bash
cd skills/stock-backtesting-skill
python3 backtesting/quick_backtest.py
```

## 配置说明

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

## 评分系统

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

## 项目结构

```
stock-backtesting-skill/
├── backtesting/
│   ├── config.py             # 配置文件
│   ├── engine.py             # 回测引擎
│   ├── optimizer.py          # 优化器
│   ├── report_generator.py   # 报告生成
│   ├── interactive.py        # 交互配置
│   ├── quick_backtest.py     # 快速回测
│   └── config_template.py    # 配置模板
├── README.md                 # 项目说明
├── LICENSE                   # 许可证
└── requirements.txt          # 依赖列表
```

## 回测示例

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

## 优化方向

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

## 许可证

MIT License

---

*最后更新：2026-03-10*