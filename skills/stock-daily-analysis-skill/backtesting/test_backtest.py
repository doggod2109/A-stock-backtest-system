#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股回测框架测试脚本
"""

import sys
from pathlib import Path

# 添加父目录到路径
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from backtesting.config import DEFAULT_WEIGHTS, OPTIMIZATION_CONFIG
from backtesting.engine import run_simple_backtest
from backtesting.optimizer import run_weight_optimization, WeightOptimizer, WalkForwardAnalyzer

def test_simple_backtest():
    """测试简单回测"""
    print("=" * 70)
    print("测试1: 简单回测")
    print("=" * 70)

    codes = ['002353', '000592', '600519']  # 杰瑞股份、平潭发展、贵州茅台

    print(f"\n股票代码: {codes}")
    print(f"默认权重: {DEFAULT_WEIGHTS}")

    result = run_simple_backtest(codes)

    if 'error' in result:
        print(f"\n❌ 回测失败: {result['error']}")
        return

    print(f"\n✅ 回测成功!")
    print(f"总收益率: {result['total_return']:.2%}")
    print(f"年化收益率: {result['annual_return']:.2%}")
    print(f"夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"最大回撤: {result['max_drawdown']:.2%}")
    print(f"胜率: {result['win_rate']:.2%}")
    print(f"交易次数: {result['total_trades']}")
    print(f"最终权益: ¥{result['final_equity']:,.2f}")


def test_weight_optimization():
    """测试权重优化"""
    print("\n" + "=" * 70)
    print("测试2: 权重优化")
    print("=" * 70)

    codes = ['002353', '000592']  # 用2只股票加快测试

    print(f"\n股票代码: {codes}")
    print(f"优化目标: {OPTIMIZATION_CONFIG['objective']}")
    print(f"步长: 10")

    result = run_weight_optimization(codes, step=10)

    if 'error' in result:
        print(f"\n❌ 优化失败: {result['error']}")
        return

    print(f"\n✅ 优化成功!")
    print(f"最优权重: {result['weights']}")

    opt_result = result['result']
    print(f"\n最优策略表现:")
    print(f"总收益率: {opt_result['total_return']:.2%}")
    print(f"年化收益率: {opt_result['annual_return']:.2%}")
    print(f"夏普比率: {opt_result['sharpe_ratio']:.2f}")
    print(f"最大回撤: {opt_result['max_drawdown']:.2%}")
    print(f"胜率: {opt_result['win_rate']:.2%}")


def test_weight_comparison():
    """测试权重对比"""
    print("\n" + "=" * 70)
    print("测试3: 权重对比")
    print("=" * 70)

    codes = ['002353', '000592']

    # 定义几组权重进行对比
    weight_sets = [
        DEFAULT_WEIGHTS,
        {
            'trend': 35, 'bias': 15, 'volume': 20,
            'support': 10, 'macd': 10, 'rsi': 10
        },
        {
            'trend': 25, 'bias': 25, 'volume': 10,
            'support': 15, 'macd': 15, 'rsi': 10
        },
    ]

    names = ['默认权重', '趋势增强', '乖离增强']

    print(f"\n股票代码: {codes}")
    print(f"\n对比组数: {len(weight_sets)}")

    optimizer = WeightOptimizer()
    comparison = optimizer.compare_weights(codes, weight_sets, names)

    if comparison.empty:
        print(f"\n❌ 对比失败")
        return

    print(f"\n✅ 对比完成!")
    print(f"\n{comparison.to_string(index=False)}")


def test_walk_forward():
    """测试Walk-Forward分析"""
    print("\n" + "=" * 70)
    print("测试4: Walk-Forward分析")
    print("=" * 70)

    codes = ['002353']

    print(f"\n股票代码: {codes}")
    print(f"分析周期: 2023-01-01 ~ 2026-03-10")

    analyzer = WalkForwardAnalyzer()
    result = analyzer.analyze(codes, "2023-01-01", "2026-03-10")

    if 'error' in result:
        print(f"\n❌ 分析失败: {result['error']}")
        return

    print(f"\n✅ 分析完成!")
    print(f"窗口数量: {len(result['windows'])}")

    summary = result['summary']
    print(f"\n测试集平均表现:")
    print(f"平均总收益率: {summary.get('avg_total_return', 0):.2%}")
    print(f"平均年化收益率: {summary.get('avg_annual_return', 0):.2%}")
    print(f"平均夏普比率: {summary.get('avg_sharpe_ratio', 0):.2f}")
    print(f"平均最大回撤: {summary.get('avg_max_drawdown', 0):.2%}")
    print(f"夏普比率标准差: {summary.get('std_sharpe_ratio', 0):.2f}")
    print(f"WFE比率: {summary.get('wfe_ratio', 0):.2f}")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("A股回测框架测试")
    print("=" * 70)

    # 运行测试
    test_simple_backtest()
    # test_weight_optimization()  # 暂时注释，耗时较长
    # test_weight_comparison()      # 暂时注释，耗时较长
    # test_walk_forward()          # 暂时注释，耗时较长

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()