# -*- coding: utf-8 -*-
"""
测试回测功能（配合 stock-daily-analysis-skill）
"""

import sys
from pathlib import Path

# 添加 stock-daily-analysis-skill 到路径
stock_analysis_path = Path(__file__).parent.parent / "stock-daily-analysis-skill"
if stock_analysis_path.exists():
    sys.path.insert(0, str(stock_analysis_path))
    print("✅ 找到 stock-daily-analysis-skill")
else:
    print("❌ 未找到 stock-daily-analysis-skill")
    sys.exit(1)

from scripts.data_fetcher import get_daily_data
from scripts.trend_analyzer import StockTrendAnalyzer

from backtesting.config import BACKTEST_CONFIG
from backtesting.engine import AStockBacktestEngine
from backtesting.report_generator import ReportGenerator

print("\n" + "=" * 70)
print("测试 stock-backtesting-skill")
print("=" * 70)

# 配置
config = BACKTEST_CONFIG.copy()
config['init_cash'] = 1_000_000
config['position_size'] = 1.0
config['max_positions'] = 1

codes = ['000592']
start_date = "2025-01-01"
end_date = "2026-03-10"
weights = {'trend': 30, 'bias': 20, 'volume': 15, 'support': 10, 'macd': 15, 'rsi': 10}

print(f"\n📋 配置:")
print(f"  股票: {codes}")
print(f"  时间: {start_date} ~ {end_date}")
print(f"  初始资金: ¥{config['init_cash']:,}")

print("\n" + "=" * 70)
print("🚀 开始回测")
print("=" * 70)

# 创建回测引擎
engine = AStockBacktestEngine(config, data_fetcher=get_daily_data, analyzer=StockTrendAnalyzer())

# 运行回测
result = engine.run_backtest(codes, start_date, end_date, weights)

# 显示结果
if 'error' in result:
    print(f"\n❌ 回测失败: {result['error']}")
else:
    print("\n" + "=" * 70)
    print("📊 回测结果")
    print("=" * 70)
    print(f"总收益率: {result['total_return']:.2%}")
    print(f"年化收益率: {result['annual_return']:.2%}")
    print(f"夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"交易次数: {result['total_trades']}")

print("\n" + "=" * 70)
print("✅ 测试完成")
print("=" * 70)