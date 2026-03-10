# 交易策略优化指南

## 📊 当前已实现的优化方向

### 1. 权重优化（已实现 ✅）
**位置：** `backtesting/optimizer.py - WeightOptimizer`

**优化目标：** 找出6个评分维度的最优权重组合

**方法：**
- 网格搜索（grid_search）：遍历所有可能的权重组合
- 随机搜索（random_search）：随机采样权重组合
- 贝叶斯优化（bayesian）：智能搜索最优权重

**优化范围：**
```python
weight_ranges = {
    "trend": (10, 50),      # 趋势权重
    "bias": (5, 35),       # 乖离率权重
    "volume": (5, 25),     # 量能权重
    "support": (5, 20),    # 支撑压力权重
    "macd": (5, 25),       # MACD权重
    "rsi": (5, 20),        # RSI权重
}
```

**使用方法：**
```python
from backtesting.optimizer import run_weight_optimization
best = run_weight_optimization(['000592'], step=10)
```

---

### 2. Walk-Forward 前向验证（已实现 ✅）
**位置：** `backtesting/optimizer.py - WalkForwardAnalyzer`

**优化目标：** 验证策略的稳健性，避免过拟合

**方法：**
- 训练集优化权重
- 测试集验证效果
- 滚动窗口逐步验证

**参数：**
```python
walk_forward = {
    "train_size": 0.7,    # 训练集占比70%
    "test_size": 0.3,     # 测试集占比30%
    "step": 0.2,          # 滚动步长20%
}
```

**评估指标：**
- 平均夏普比率
- 夏普比率标准差
- WFE比率（Walk-Forward Efficiency）

---

### 3. 权重对比分析（已实现 ✅）
**位置：** `backtesting/optimizer.py - WeightOptimizer.compare_weights`

**优化目标：** 对比不同权重组合的表现

**方法：** 同时回测多组权重，横向对比

**输出：** DataFrame格式的对比结果

---

## 🚀 待实现的优化方向

### 4. 买卖阈值优化

**位置：** 可在 `backtesting/config.py` 中添加

**优化目标：** 找出最优买入/卖出阈值

**优化范围：**
```python
# 买入阈值：40-80（当前60）
# 卖出阈值：10-40（当前30）
```

**方法：**
- 网格搜索遍历阈值组合
- 回测每组阈值的表现
- 选择最优阈值组合

**预期效果：**
- 提高胜率
- 减少无效交易
- 优化风险收益比

---

### 5. 止损止盈优化

**位置：** 可在 `backtesting/config.py` 中添加

**优化目标：** 找出最优止损止盈参数

**优化范围：**
```python
stop_loss_range = (-0.15, -0.03)    # -15% 到 -3%
take_profit_range = (0.05, 0.30)   # +5% 到 +30%
```

**方法：**
- 网格搜索止损止盈组合
- 回测每组参数
- 选择收益率最优组合

**预期效果：**
- 控制最大回撤
- 提高夏普比率
- 保护盈利

---

### 6. 仓位管理优化

**位置：** 可在 `backtesting/config.py` 中添加

**优化目标：** 优化仓位配置策略

**优化方向：**

**a) 固定仓位优化**
```python
# 测试不同单只仓位
position_sizes = [0.2, 0.3, 0.5, 0.7, 1.0]
max_positions = [1, 2, 3, 5, 10]
```

**b) 动态仓位（Kelly公式）**
根据胜率和盈亏比动态调整仓位
```python
kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
position_size = min(kelly_fraction, max_position_size)
```

**c) 金字塔仓位**
趋势越强，仓位越大
```python
if score >= 80:
    position_size = 1.0
elif score >= 70:
    position_size = 0.7
elif score >= 60:
    position_size = 0.5
```

---

### 7. 评分维度优化

**位置：** `scripts/trend_analyzer.py`

**优化目标：** 优化评分维度的计算方法

**优化方向：**

**a) 调整评分映射**
```python
# 当前：强势多头=30分
# 优化：根据实际表现调整
trend_map = {
    "强势多头": 30,  # 可调整
    "多头排列": 26,  # 可调整
    ...
}
```

**b) 增加新的评分维度**
```python
# 新增维度示例
ATR_volatility_score = ...    # ATR波动率
momentum_score = ...          # 动量指标
fundamental_score = ...       # 基本面评分
```

**c) 移除无效维度**
通过回测验证哪些维度贡献度低

---

### 8. 数据源优化

**位置：** `scripts/data_fetcher.py`

**优化目标：** 测试不同数据源的表现

**方法：**
- 分别用腾讯财经、新浪财经、东方财富回测
- 对比数据质量差异
- 选择最优数据源

---

### 9. 交易时间优化

**位置：** `backtesting/engine.py`

**优化目标：** 测试不同交易时间的表现

**优化选项：**
```python
# 已测试：
price = row['close']      # 当日收盘价（不现实）
price = row['open']       # 次日开盘价（当前）✅

# 待测试：
price = (row['open'] + row['close']) / 2  # 平均价
price = row['high']       # 最高价（激进）
price = row['low']        # 最低价（保守）
price = row['vwap']       # 成交量加权平均价
```

---

### 10. 多市场环境优化

**位置：** `backtesting/optimizer.py - DynamicWeightManager`

**优化目标：** 根据市场环境调整策略

**实现方法：**

**a) 牛市/熊市识别**
```python
# 识别市场环境
if up_ratio > 0.75:
    market_sentiment = 'bullish'
elif up_ratio < 0.25:
    market_sentiment = 'bearish'
else:
    market_sentiment = 'neutral'
```

**b) 动态调整权重**
```python
if market_sentiment == 'bullish':
    # 牛市：增加趋势和量能权重
    weights['trend'] += 10
    weights['volume'] += 5
elif market_sentiment == 'bearish':
    # 熊市：增加支撑和RSI权重
    weights['support'] += 10
    weights['rsi'] += 5
```

---

### 11. 多因子组合优化

**位置：** 新建 `backtesting/factor_optimizer.py`

**优化目标：** 优化多个因子的组合效果

**方法：**
- 因子分析（IC、IR）
- 因子正交化
- 因子权重分配

---

### 12. 风险管理优化

**位置：** 可在 `backtesting/engine.py` 中添加

**优化目标：** 优化风险控制策略

**优化方向：**

**a) 动态止损**
```python
# 根据ATR动态调整止损
atr = calculate_atr(df, period=14)
dynamic_stop_loss = price - 2 * atr
```

**b) 波动率止损**
```python
# 高波动时降低止损，低波动时提高止损
volatility = df['close'].pct_change().std()
if volatility > threshold:
    stop_loss = -0.05  # 降低止损
else:
    stop_loss = -0.10  # 提高止损
```

**c) 回撤控制**
```python
# 动态平仓，控制回撤
if current_drawdown < max_drawdown * 0.5:
    reduce_position()  # 减仓
```

---

## 📋 优化优先级建议

### 高优先级（近期）
1. ✅ 权重优化（已实现）
2. ✅ Walk-Forward验证（已实现）
3. 🚧 买卖阈值优化
4. 🚧 止损止盈优化

### 中优先级（中期）
5. 🚧 仓位管理优化
6. 🚧 评分维度优化
7. 🚧 多市场环境优化

### 低优先级（长期）
8. 🚧 多因子组合优化
9. 🚧 风险管理优化
10. 🚧 机器学习优化（用ML预测最佳策略）

---

## 🎯 优化工作流

```
1. 基础回测 → 确认策略基本可用
   ↓
2. 权重优化 → 找出最优权重组合
   ↓
3. Walk-Forward验证 → 验证稳健性
   ↓
4. 阈值优化 → 优化买卖阈值
   ↓
5. 止损止盈优化 → 优化风险控制
   ↓
6. 仓位优化 → 优化资金管理
   ↓
7. 动态权重 → 根据市场环境调整
   ↓
8. 实盘测试 → 小资金验证
```

---

## 📝 记录建议

每次优化后记录：

1. **优化内容**
   - 优化了什么参数
   - 使用了什么方法

2. **优化结果**
   - 优化前的指标
   - 优化后的指标
   - 提升幅度

3. **最佳参数**
   - 最优参数组合
   - 适用场景

4. **下一步计划**
   - 还需要优化什么
   - 优先级排序

---

## 💡 快速开始

### 1. 权重优化
```bash
cd /home/admin/openclaw/stock-agent/skills/stock-daily-analysis-skill
python3 -c "
from backtesting.optimizer import run_weight_optimization
best = run_weight_optimization(['000592'], step=10)
print(f'最优权重: {best[\"weights\"]}')
"
```

### 2. Walk-Forward验证
```python
from backtesting.optimizer import WalkForwardAnalyzer
analyzer = WalkForwardAnalyzer()
result = analyzer.analyze(['000592'], '2023-01-01', '2026-03-10')
```

### 3. 查看历史回测报告
```bash
ls -la /home/admin/openclaw/stock-agent/skills/stock-daily-analysis-skill/backtest_*/
```

---

*最后更新：2026-03-10*
*版本：1.0*