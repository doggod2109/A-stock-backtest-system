# 🎯 A股智能回测系统

> 基于技术分析评分系统的A股量化回测框架

一个完整的A股量化分析和回测系统，支持技术分析评分、智能回测、权重优化和多格式报告生成。

---

## ✨ 主要功能

### 📊 技术分析（stock-daily-analysis-skill）
- **6维度评分系统**：趋势、乖离率、量能、支撑压力、MACD、RSI
- **多数据源**：腾讯财经、新浪财经、东方财富API自动切换
- **AI深度分析**：支持DeepSeek/Gemini AI增强分析
- **智能信号**：自动生成买入/卖出/持有信号

### 🎯 量化回测（stock-backtesting-skill）
- **真实交易模拟**：T日计算信号 → T+1日开盘价执行
- **完整风控**：止损止盈、仓位管理、滑点模拟
- **权重优化**：网格搜索、Walk-Forward验证、动态权重
- **多格式报告**：JSON、Excel、HTML可视化报告

---

## 🚀 快速开始

### 1️⃣ 克隆项目

```bash
git clone https://github.com/doggod2109/A-stock-backtest-system.git
cd A-stock-backtest-system
```

### 2️⃣ 安装依赖

```bash
cd skills/stock-daily-analysis-skill
pip install -r requirements.txt
```

### 3️⃣ 配置回测参数

编辑 `skills/stock-backtesting-skill/backtesting/config_template.py`：

```python
# 股票代码
STOCK_CODES = ["000592"]

# 时间范围
START_DATE = "2025-06-01"
END_DATE = "2026-03-10"

# 初始资金
INIT_CASH = 10_000  # 1万元

# 评分权重（总和100）
WEIGHTS = {
    "trend": 35,    # 趋势
    "bias": 25,     # 乖离率
    "volume": 10,   # 量能
    "support": 10,  # 支撑
    "macd": 10,     # MACD
    "rsi": 10,      # RSI
}

# 买卖阈值
BUY_THRESHOLD = 60   # 买入阈值
SELL_THRESHOLD = 30  # 卖出阈值

# 止损止盈
STOP_LOSS = -8   # -8% 止损
TAKE_PROFIT = 15  # +15% 止盈
```

### 4️⃣ 运行回测

```bash
cd skills/stock-backtesting-skill
python3 backtesting/quick_backtest.py
```

### 5️⃣ 查看结果

回测完成后会生成报告：

```
backtest_YYYYMMDD_HHMMSS/
├── report.json      # 完整数据（JSON格式）
├── trades.xlsx      # 交易明细（Excel格式）
└── report.html      # 可视化报告（HTML格式）
```

---

## 📊 项目结构

```
stock-agent/
├── skills/
│   ├── stock-daily-analysis-skill/    # 技术分析模块
│   │   ├── scripts/
│   │   │   ├── data_fetcher.py       # 数据获取
│   │   │   ├── trend_analyzer.py     # 技术分析
│   │   │   └── ai_analyzer.py        # AI分析
│   │   ├── config.json               # 配置文件
│   │   ├── config.example.json       # 配置示例
│   │   └── README.md
│   └── stock-backtesting-skill/       # 回测模块
│       ├── backtesting/
│       │   ├── config.py             # 配置
│       │   ├── engine.py             # 回测引擎
│       │   ├── optimizer.py          # 优化器
│       │   ├── report_generator.py   # 报告生成
│       │   ├── quick_backtest.py     # 快速回测
│       │   └── config_template.py    # 配置模板
│       ├── README.md
│       ├── SKILL.md
│       └── requirements.txt
├── OPTIMIZATION_GUIDE.md              # 优化指南
└── README.md                         # 本文件
```

---

## 📖 评分系统

### 评分维度（100分）

| 维度 | 权重 | 评分规则 |
|------|------|----------|
| 趋势 | 35 | 强势多头=35, 多头排列=30, 盘整=15, 空头=5 |
| 乖离率 | 25 | 负乖离（回调）高分, 正乖离>5%低分 |
| 量能 | 10 | 缩量回调=10, 放量上涨=8, 放量下跌=0 |
| 支撑 | 10 | MA5支撑=5, MA10支撑=5 |
| MACD | 10 | 零轴金叉=10, 金叉=8, 死叉=0 |
| RSI | 10 | 超卖=10, 强势买入=8, 超买=0 |

### 信号阈值

- **买入信号**：评分 >= 60分
- **持有信号**：30分 <= 评分 < 60分
- **卖出信号**：评分 < 30分

---

## 📈 回测示例

### 示例：000592 平潭发展

**配置：**
- 时间：2025-06-01 ~ 2026-03-10
- 初始资金：¥10,000
- 仓位：100%单只
- 止损：-8%，止盈：+15%

**结果：**
```
总收益率：575.22%
年化收益率：223.45%
夏普比率：2.56
最大回撤：-25.34%
胜率：72.73%
交易次数：11次
最终权益：¥33,590.47
```

---

## 🔧 高级功能

### 权重优化

```python
from backtesting.optimizer import run_weight_optimization

# 网格搜索最优权重
best = run_weight_optimization(['000592'], step=10)
print(f"最优权重: {best['weights']}")
```

### Walk-Forward验证

```python
from backtesting.optimizer import WalkForwardAnalyzer

analyzer = WalkForwardAnalyzer()
result = analyzer.analyze(['000592'], '2023-01-01', '2026-03-10')
print(f"平均夏普比率: {result['avg_sharpe']}")
```

详细优化指南请查看 [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md)

---

## ⚙️ 配置说明

### 交易费用（默认）

```python
commission_rate = 0.0003   # 万三佣金
stamp_duty_rate = 0.001    # 千一印花税（仅卖出）
transfer_fee_rate = 0.00002 # 万二过户费
slippage = 0.0001          # 万一滑点
```

### AI分析配置（可选）

编辑 `skills/stock-daily-analysis-skill/config.json`：

```json
{
  "ai": {
    "api_key": "sk-your-deepseek-api-key",
    "model": "deepseek-chat",
    "temperature": 0.3
  }
}
```

---

## ❓ 常见问题

### Q1: 回测需要什么数据？

A: 系统自动从新浪财经API获取历史数据，无需手动下载。

### Q2: 支持哪些股票？

A: 支持A股（主板、创业板、科创板）、港股、美股、ETF。

### Q3: 可以模拟实盘交易吗？

A: 可以！回测引擎模拟了真实的T+1交易、费用和滑点。

### Q4: 如何调整策略参数？

A: 修改 `config_template.py` 中的权重、阈值、止损止盈等参数。

### Q5: 报告在哪里查看？

A: 回测完成后自动生成在 `backtest_YYYYMMDD_HHMMSS/` 目录下。

---

## 📝 依赖项

```
pandas >= 1.3.0
numpy >= 1.21.0
requests >= 2.26.0
openpyxl >= 3.0.0
```

---

## ⚠️ 风险提示

- 本系统仅供学习和研究使用
- 回测结果不代表未来表现
- 实际投资请谨慎决策
- 股市有风险，投资需谨慎

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👤 作者

**总舵主徐祥** - 专业股票分析师

---

*最后更新：2026-03-11*

---

**觉得有用？给个 ⭐️ Star 支持一下吧！**