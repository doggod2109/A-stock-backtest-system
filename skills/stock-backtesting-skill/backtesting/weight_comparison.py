#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多权重对比工具
对比不同权重组合的回测效果
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

stock_analysis_path = current_dir.parent.parent / "stock-daily-analysis-skill"
if stock_analysis_path.exists():
    sys.path.insert(0, str(stock_analysis_path))

from config import BACKTEST_CONFIG
from engine import AStockBacktestEngine

# ============================================================
# 待测试的权重组合
# ============================================================
WEIGHT_SETS = [
    {
        'name': '当前默认',
        'weights': {'trend': 35, 'bias': 25, 'volume': 10, 'support': 10, 'macd': 10, 'rsi': 10}
    },
    {
        'name': '趋势优先',
        'weights': {'trend': 45, 'bias': 20, 'volume': 10, 'support': 5, 'macd': 10, 'rsi': 10}
    },
    {
        'name': '乖离优先',
        'weights': {'trend': 25, 'bias': 40, 'volume': 10, 'support': 10, 'macd': 10, 'rsi': 5}
    },
    {
        'name': '平衡配置',
        'weights': {'trend': 30, 'bias': 20, 'volume': 15, 'support': 10, 'macd': 15, 'rsi': 10}
    },
    {
        'name': '量能优先',
        'weights': {'trend': 30, 'bias': 20, 'volume': 25, 'support': 10, 'macd': 10, 'rsi': 5}
    },
    {
        'name': 'MACD优先',
        'weights': {'trend': 30, 'bias': 20, 'volume': 5, 'support': 10, 'macd': 25, 'rsi': 10}
    },
]

# ============================================================
# 配置
# ============================================================
STOCK_CODE = "000592"
START_DATE = "2025-06-01"
END_DATE = "2026-03-10"

# ============================================================
# 运行对比
# ============================================================
print("=" * 90)
print("🎯 多权重组合对比")
print("=" * 90)
print(f"\n📋 配置:")
print(f"  股票代码: {STOCK_CODE}")
print(f"  时间范围: {START_DATE} ~ {END_DATE}")
print(f"  待测组合: {len(WEIGHT_SETS)}组")

print("\n" + "=" * 90)
print("🚀 开始对比测试...")
print("=" * 90)

# 初始化引擎
config = BACKTEST_CONFIG.copy()
config['init_cash'] = 10_000

stock_analysis_path = current_dir.parent.parent / "stock-daily-analysis-skill"
sys.path.insert(0, str(stock_analysis_path))
from scripts.data_fetcher import get_daily_data
from scripts.trend_analyzer import StockTrendAnalyzer

engine = AStockBacktestEngine(config, data_fetcher=get_daily_data, analyzer=StockTrendAnalyzer())

# 回测所有组合
results = []
for i, weight_set in enumerate(WEIGHT_SETS):
    print(f"\n[{i+1}/{len(WEIGHT_SETS)}] 测试: {weight_set['name']}")
    print(f"    权重: {weight_set['weights']}")

    try:
        result = engine.run_backtest(
            codes=[STOCK_CODE],
            start_date=START_DATE,
            end_date=END_DATE,
            weights=weight_set['weights']
        )

        results.append({
            'name': weight_set['name'],
            'weights': weight_set['weights'],
            **result
        })

        print(f"    ✓ 完成 - 收益率: {result['total_return']:.2%}")

    except Exception as e:
        print(f"    ✗ 失败: {e}")

# ============================================================
# 转换为DataFrame
# ============================================================
df = pd.DataFrame(results)

# 选择关键指标
columns = ['name', 'total_return', 'annual_return', 'sharpe_ratio',
           'max_drawdown', 'win_rate', 'avg_profit', 'total_trades', 'final_equity']

df_display = df[columns].copy()

# 格式化
df_display['total_return'] = df_display['total_return'].apply(lambda x: f"{x:.2%}")
df_display['annual_return'] = df_display['annual_return'].apply(lambda x: f"{x:.2%}")
df_display['sharpe_ratio'] = df_display['sharpe_ratio'].apply(lambda x: f"{x:.2f}")
df_display['max_drawdown'] = df_display['max_drawdown'].apply(lambda x: f"{x:.2%}")
df_display['win_rate'] = df_display['win_rate'].apply(lambda x: f"{x:.2%}")
df_display['avg_profit'] = df_display['avg_profit'].apply(lambda x: f"{x:.2%}")
df_display['final_equity'] = df_display['final_equity'].apply(lambda x: f"¥{x:.2f}")

df_display.columns = ['组合名称', '总收益率', '年化收益率', '夏普比率',
                      '最大回撤', '胜率', '平均盈亏', '交易次数', '最终权益']

# 按夏普比率排序
df_sorted = df.sort_values('sharpe_ratio', ascending=False)

# ============================================================
# 展示结果（表格形式）
# ============================================================
print("\n" + "=" * 90)
print("📊 对比结果（按夏普比率排序）")
print("=" * 90)
print(df_sorted.to_string(index=False))

# ============================================================
# 展示结果（可视化条形图）
# ============================================================
print("\n" + "=" * 90)
print("📊 收益率对比")
print("=" * 90)

df_by_return = df.sort_values('total_return', ascending=False)
for _, row in df_by_return.iterrows():
    name = row['name']
    return_pct = row['total_return']
    bar_length = int(return_pct * 5)  # 500% = 250字符
    bar = "█" * bar_length
    print(f"{name:12s} {return_pct:6.2%} {bar}")

print("\n" + "=" * 90)
print("📊 夏普比率对比")
print("=" * 90)

df_by_sharpe = df.sort_values('sharpe_ratio', ascending=False)
for _, row in df_by_sharpe.iterrows():
    name = row['name']
    sharpe = row['sharpe_ratio']
    bar_length = int(sharpe * 20)  # 4.0 = 80字符
    bar = "█" * bar_length
    print(f"{name:12s} {sharpe:5.2f} {bar}")

# ============================================================
# 推荐最优组合
# ============================================================
print("\n" + "=" * 90)
print("🏆 最优组合推荐")
print("=" * 90)

best = df_sorted.iloc[0]
print(f"\n🎯 推荐组合: {best['name']}")
print(f"\n📊 性能指标:")
print(f"  总收益率:    {best['total_return']:.2%}")
print(f"  年化收益率:  {best['annual_return']:.2%}")
print(f"  夏普比率:    {best['sharpe_ratio']:.2f}")
print(f"  最大回撤:    {best['max_drawdown']:.2%}")
print(f"  胜率:        {best['win_rate']:.2%}")

print(f"\n🎨 权重配置:")
for key, value in sorted(best['weights'].items(), key=lambda x: x[1], reverse=True):
    print(f"  {key:10s}: {value:2d}")

# ============================================================
# 保存结果
# ============================================================
print("\n" + "=" * 90)
print("💾 保存结果")
print("=" * 90)

output_dir = Path(f"weight_comparison_{STOCK_CODE}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
output_dir.mkdir(exist_ok=True)

# 保存Excel
excel_file = output_dir / "weight_comparison.xlsx"
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='详细数据', index=False)
    df_display.to_excel(writer, sheet_name='对比表格', index=False)

# 清理results中的不可序列化对象
results_clean = []
for r in results:
    results_clean.append({
        'name': r['name'],
        'weights': r['weights'],
        'total_return': float(r['total_return']),
        'annual_return': float(r['annual_return']),
        'sharpe_ratio': float(r['sharpe_ratio']),
        'max_drawdown': float(r['max_drawdown']),
        'win_rate': float(r['win_rate']),
        'avg_profit': float(r['avg_profit']),
        'total_trades': int(r['total_trades']),
        'final_equity': float(r['final_equity']),
    })

# 保存JSON
json_file = output_dir / "weight_comparison.json"
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump({
        'config': {
            'stock': STOCK_CODE,
            'date_range': f"{START_DATE} ~ {END_DATE}",
            'timestamp': datetime.now().isoformat()
        },
        'results': results_clean,
        'best': {
            'name': best['name'],
            'weights': best['weights'],
            'total_return': float(best['total_return']),
            'annual_return': float(best['annual_return']),
            'sharpe_ratio': float(best['sharpe_ratio']),
            'max_drawdown': float(best['max_drawdown']),
            'win_rate': float(best['win_rate']),
            'avg_profit': float(best['avg_profit']),
            'total_trades': int(best['total_trades']),
            'final_equity': float(best['final_equity']),
        }
    }, f, indent=2, ensure_ascii=False)

# 保存推荐配置
recommend_file = output_dir / "recommended_weights.txt"
with open(recommend_file, 'w', encoding='utf-8') as f:
    f.write(f"# 推荐权重配置\n")
    f.write(f"# 组合: {best['name']}\n")
    f.write(f"# 时间: {START_DATE} ~ {END_DATE}\n\n")
    f.write(f"WEIGHTS = {{\n")
    for key, value in best['weights'].items():
        f.write(f"    '{key}': {value},  # {value}%\n")
    f.write(f"}}\n")

print(f"\n✅ 结果已保存到: {output_dir.absolute()}")
print(f"   - weight_comparison.xlsx  (Excel对比表)")
print(f"   - weight_comparison.json  (详细JSON)")
print(f"   - recommended_weights.txt (推荐配置)")

print("\n" + "=" * 90)
print("🎉 对比完成！")
print("=" * 90)

print("\n💡 使用建议:")
print(f"   复制 recommended_weights.txt 中的配置到 config_template.py")
print(f"   然后运行: python3 backtesting/quick_backtest.py")