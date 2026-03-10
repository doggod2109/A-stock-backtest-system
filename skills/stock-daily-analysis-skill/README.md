# A股智能分析系统

基于技术分析评分系统的A股量化分析框架

## 特性

- 📊 完整的技术分析评分系统（6维度）
- 🤖 AI深度分析（DeepSeek/Gemini）
- 📈 实时行情和历史数据获取
- 🎯 买卖信号生成和风险评估
- 🔄 多数据源支持（腾讯财经、新浪财经、东方财富）

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置API Key

编辑 `config.json`，配置DeepSeek API Key：

```json
{
  "ai": {
    "api_key": "sk-your-deepseek-api-key"
  }
}
```

### 分析股票

```python
from scripts.analyzer import analyze_stock

result = analyze_stock('000592')
print(result)
```

## 技术分析功能

### 数据获取

- **数据源：** 新浪财经API（稳定可靠，支持2000天历史数据）
- **支持市场：** A股（个股、ETF）
- **历史数据：** 支持任意时间段K线数据
- **实时行情：** 当前价格、涨跌幅、成交量等

### 技术面分析

- **均线系统：** MA5/MA10/MA20/MA60 多头/空头排列判断
- **MACD指标：** DIF、DEA、MACD柱状图 + 金叉死叉信号
- **RSI指标：** RSI(6/12/24) + 超买超卖判断
- **乖离率：** BIAS_MA5/MA10/MA20（判断是否追高风险）
- **量能分析：** 缩量/放量判断 + 量价配合分析
- **支撑压力：** 均线支撑位、近期高点压力位

### AI 深度分析

- **AI模型：** DeepSeek/Gemini
- **智能判断：** 综合技术指标给出操作建议
- **风险提示：** 识别潜在风险因素
- **目标价位：** 预测目标价和止损位

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
stock-daily-analysis-skill/
├── scripts/
│   ├── data_fetcher.py       # 数据获取
│   ├── trend_analyzer.py     # 技术分析
│   ├── ai_analyzer.py        # AI分析
│   └── analyzer.py           # 主入口
├── config.json               # 配置文件
├── config.example.json       # 配置示例
├── README.md                 # 项目说明
└── requirements.txt          # 依赖列表
```

## 回测功能

回测功能已独立为 **stock-backtesting-skill**，详见：
https://github.com/doggod2109/A-stock-backtest-system/tree/main/skills/stock-backtesting-skill

## ⚠️ 风险提示

- 本系统仅供学习和研究使用
- 分析结果不构成投资建议
- 股市有风险，投资需谨慎

## 许可证

MIT License

---

*最后更新：2026-03-10*