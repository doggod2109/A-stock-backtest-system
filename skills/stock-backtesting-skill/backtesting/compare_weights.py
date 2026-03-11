#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权重优化对比脚本
运行权重优化并生成对比报告
"""

import sys
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
stock_analysis_path = current_dir.parent.parent / "stock-daily-analysis-skill"
if stock_analysis_path.exists():
    sys.path.insert(0, str(stock_analysis_path))

import pandas as pd
from optimizer import WeightOptimizer, run_weight_optimization

# ============================================================
# 配置
# ============================================================
STOCK_CODE = "000592"
START_DATE = "2025-06-01"
END_DATE = "2026-03-10"

# 步长：5=精细（慢），10=快速（推荐），20=粗略（快）
STEP = 10

# 目标函数：sharpe_ratio, total_return, annual_return, win_rate
OBJECTIVE = "sharpe_ratio"

# ============================================================
# 运行权重优化
# ============================================================
print("=" * 80)
print("🎯 权重优化对比")
print("=" * 80)
print(f"\n📋 配置:")
print(f"  股票代码: {STOCK_CODE}")
print(f"  时间范围: {START_DATE} ~ {END_DATE}")
print(f"  步长: {STEP}")
print(f"  目标函数: {OBJECTIVE}")

print("\n" + "=" * 80)
print("🚀 开始优化...")
print("=" * 80)

# 运行优化
best_result = run_weight_optimization([STOCK_CODE], step=STEP)

if 'error' in best_result:
    print(f"\n❌ 优化失败: {best_result['error']}")
    sys.exit(1)

# ============================================================
# 展示结果
# ============================================================
print("\n" + "=" * 80)
print("📊 最优权重组合")
print("=" * 80)

best_weights = best_result['weights']
best_metrics = best_result['result']

print("\n🎨 权重配置:")
print("-" * 80)
for key, value in sorted(best_weights.items(), key=lambda x: x[1], reverse=True):
    bar = "█" * (value // 2)
    print(f"  {key:10s}: {value:2d} {bar}")

print("\n" + "=" * 80)
print("📈 回测结果")
print("=" * 80)

metrics = [
    ("总收益率", "total_return", "{:.2%}"),
    ("年化收益率", "annual_return", "{:.2%}"),
    ("夏普比率", "sharpe_ratio", "{:.2f}"),
    ("最大回撤", "max_drawdown", "{:.2%}"),
    ("胜率", "win_rate", "{:.2%}"),
    ("平均盈亏", "avg_profit", "{:.2%}"),
    ("交易次数", "total_trades", "{}"),
    ("最终权益", "final_equity", "¥{:.2f}"),
]

for name, key, fmt in metrics:
    value = best_metrics.get(key, 0)
    print(f"  {name:12s}: {fmt.format(value)}")

# ============================================================
# 保存结果
# ============================================================
print("\n" + "=" * 80)
print("💾 保存结果")
print("=" * 80)

output_dir = Path(f"optimization_{STOCK_CODE}")
output_dir.mkdir(exist_ok=True)

# 保存最优权重
import json
weights_file = output_dir / "best_weights.json"
with open(weights_file, 'w', encoding='utf-8') as f:
    json.dump({
        'best_weights': best_weights,
        'metrics': best_metrics,
        'config': {
            'stock': STOCK_CODE,
            'date_range': f"{START_DATE} ~ {END_DATE}",
            'step': STEP,
            'objective': OBJECTIVE
        }
    }, f, indent=2, ensure_ascii=False)

print(f"\n✅ 结果已保存到: {output_dir.absolute()}")
print(f"   - best_weights.json  (最优权重)")

print("\n" + "=" * 80)
print("🎉 优化完成！")
print("=" * 80)

print("\n💡 使用建议:")
print(f"   在 config_template.py 中设置:")
print(f"   WEIGHTS = {best_weights}")