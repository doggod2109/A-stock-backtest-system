#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股回测交互式配置选择器
"""

import sys
from pathlib import Path

# 添加父目录到路径
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from backtesting.config import (
    BACKTEST_CONFIG,
    DEFAULT_WEIGHTS,
    SIGNAL_CONFIG,
    OPTIMIZATION_CONFIG,
)
from backtesting.engine import AStockBacktestEngine
from backtesting.optimizer import WeightOptimizer


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_menu(options):
    """打印菜单选项"""
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print()


def get_choice(prompt, max_choice):
    """获取用户选择"""
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= max_choice:
                return choice
            print(f"⚠️ 请输入 1-{max_choice} 之间的数字")
        except ValueError:
            print("⚠️ 请输入有效数字")


def get_number(prompt, default=None, min_val=None, max_val=None):
    """获取数字输入"""
    while True:
        try:
            input_str = input(prompt)
            if input_str == "" and default is not None:
                return default

            value = float(input_str)

            if min_val is not None and value < min_val:
                print(f"⚠️ 值不能小于 {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"⚠️ 值不能大于 {max_val}")
                continue

            return value
        except ValueError:
            print("⚠️ 请输入有效数字")


def get_date(prompt, default=None):
    """获取日期输入"""
    while True:
        try:
            input_str = input(prompt)
            if input_str == "" and default is not None:
                return default

            # 简单验证日期格式
            parts = input_str.split("-")
            if len(parts) != 3:
                print("⚠️ 请使用 YYYY-MM-DD 格式")
                continue

            return input_str
        except:
            print("⚠️ 日期格式错误")


def interactive_config():
    """交互式配置"""
    print_header("🎛️ A股回测 - 交互式配置选择器")

    config = {}
    weights = {}

    # 1. 选择股票
    print("📌 步骤1：选择股票代码")
    print("  输入股票代码，多个代码用逗号分隔")
    print("  示例：002353,000592,600519")
    print()

    codes_input = input("股票代码 [默认: 002353,000592,600519]: ").strip()
    if codes_input:
        codes = [c.strip() for c in codes_input.split(",")]
    else:
        codes = ['002353', '000592', '600519']

    config['codes'] = codes
    print(f"✅ 已选择: {', '.join(codes)}\n")

    # 2. 选择时间范围
    print("📌 步骤2：选择回测时间范围")
    start_date = get_date("开始日期 [默认: 2023-01-01]: ", "2023-01-01")
    end_date = get_date("结束日期 [默认: 2026-03-10]: ", "2026-03-10")

    config['start_date'] = start_date
    config['end_date'] = end_date
    print(f"✅ 时间范围: {start_date} ~ {end_date}\n")

    # 3. 选择初始资金
    print("📌 步骤3：选择初始资金")
    init_cash = int(get_number("初始资金（元）[默认: 1000000]: ", 1000000, min_val=1000))
    config['init_cash'] = init_cash
    print(f"✅ 初始资金: ¥{init_cash:,}\n")

    # 4. 选择仓位管理
    print("📌 步骤4：选择仓位管理")
    position_size = get_number("单只股票最大仓位（0.1-1.0）[默认: 0.3]: ", 0.3, min_val=0.01, max_val=1.0)
    max_positions = int(get_number("最多同时持仓数量（1-10）[默认: 3]: ", 3, min_val=1, max_val=10))

    config['position_size'] = position_size
    config['max_positions'] = max_positions
    print(f"✅ 单只仓位: {position_size*100:.0f}%, 最大持仓: {max_positions}只\n")

    # 5. 选择评分权重
    print("📌 步骤5：调整评分权重（总和需为100）")
    print("  输入0使用默认值")

    print("\n当前默认权重:")
    for key, value in DEFAULT_WEIGHTS.items():
        print(f"  {key}: {value}")

    print("\n是否调整权重？")
    print("  1. 使用默认权重")
    print("  2. 手动调整权重")

    choice = get_choice("请选择 [默认: 1]: ", 2)

    if choice == 2:
        print("\n请输入各维度权重（总和必须为100）：")
        total = 0
        for key, default_value in DEFAULT_WEIGHTS.items():
            value = int(get_number(f"  {key} [默认: {default_value}]: ", default_value, min_val=0, max_val=100))
            weights[key] = value
            total += value

        if total != 100:
            print(f"\n⚠️ 权重总和为 {total}，自动调整到100")
            for key in weights:
                weights[key] = int(weights[key] * 100 / total)
    else:
        weights = DEFAULT_WEIGHTS.copy()

    print(f"✅ 权重配置: {weights}\n")

    # 6. 选择买卖阈值
    print("📌 步骤6：调整买卖信号阈值")

    print("\n当前默认阈值:")
    print(f"  买入阈值: {SIGNAL_CONFIG['buy_thresholds']['buy']}")
    print(f"  卖出阈值: {SIGNAL_CONFIG['sell_thresholds']['sell']}")

    print("\n是否调整阈值？")
    print("  1. 使用默认阈值")
    print("  2. 手动调整阈值")

    choice = get_choice("请选择 [默认: 1]: ", 2)

    if choice == 2:
        buy_threshold = get_number("  买入阈值（0-100）[默认: 60]: ", 60, min_val=0, max_val=100)
        sell_threshold = get_number("  卖出阈值（0-100）[默认: 30]: ", 30, min_val=0, max_val=100)
        config['buy_threshold'] = buy_threshold
        config['sell_threshold'] = sell_threshold
        print(f"✅ 买入阈值: {buy_threshold}, 卖出阈值: {sell_threshold}\n")
    else:
        config['buy_threshold'] = SIGNAL_CONFIG['buy_thresholds']['buy']
        config['sell_threshold'] = SIGNAL_CONFIG['sell_thresholds']['sell']
        print(f"✅ 使用默认阈值\n")

    # 7. 选择止损止盈
    print("📌 步骤7：调整止损止盈参数")

    print("\n当前默认参数:")
    print(f"  止损: {SIGNAL_CONFIG['risk_management']['stop_loss']*100:.0f}%")
    print(f"  止盈: {SIGNAL_CONFIG['risk_management']['take_profit']*100:.0f}%")

    print("\n是否调整？")
    print("  1. 使用默认参数")
    print("  2. 手动调整")

    choice = get_choice("请选择 [默认: 1]: ", 2)

    if choice == 2:
        stop_loss = get_number("  止损百分比（负数，如-8表示-8%）[默认: -8]: ", -8, min_val=-50, max_val=0)
        take_profit = get_number("  止盈百分比（正数，如15表示+15%）[默认: 15]: ", 15, min_val=1, max_val=200)
        config['stop_loss'] = stop_loss / 100
        config['take_profit'] = take_profit / 100
        print(f"✅ 止损: {stop_loss}%, 止盈: {take_profit}%\n")
    else:
        config['stop_loss'] = SIGNAL_CONFIG['risk_management']['stop_loss']
        config['take_profit'] = SIGNAL_CONFIG['risk_management']['take_profit']
        print(f"✅ 使用默认参数\n")

    # 8. 配置汇总
    print_header("📋 配置汇总")
    print(f"股票代码: {', '.join(codes)}")
    print(f"时间范围: {start_date} ~ {end_date}")
    print(f"初始资金: ¥{init_cash:,}")
    print(f"单只仓位: {position_size*100:.0f}%")
    print(f"最大持仓: {max_positions}只")
    print(f"评分权重: {weights}")
    print(f"买入阈值: {config.get('buy_threshold', 60)}")
    print(f"卖出阈值: {config.get('sell_threshold', 30)}")
    print(f"止损: {config.get('stop_loss', -0.08)*100:.0f}%")
    print(f"止盈: {config.get('take_profit', 0.15)*100:.0f}%")

    # 9. 确认运行
    print("\n是否开始回测？")
    print("  1. 开始回测")
    print("  2. 重新配置")
    print("  3. 退出")

    choice = get_choice("请选择 [默认: 1]: ", 3)

    if choice == 1:
        return config, weights
    elif choice == 2:
        return interactive_config()
    else:
        print("\n👋 已取消")
        return None, None


def run_interactive_backtest():
    """运行交互式回测"""
    config, weights = interactive_config()

    if config is None:
        return

    print_header("🚀 开始回测")

    # 创建回测引擎
    engine = AStockBacktestEngine(config)

    # 运行回测
    result = engine.run_backtest(
        codes=config['codes'],
        start_date=config['start_date'],
        end_date=config['end_date'],
        weights=weights
    )

    # 显示结果
    if 'error' in result:
        print(f"\n❌ 回测失败: {result['error']}")
        return

    print_header("📊 回测结果")
    print(f"总收益率: {result['total_return']:.2%}")
    print(f"年化收益率: {result['annual_return']:.2%}")
    print(f"夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"最大回撤: {result['max_drawdown']:.2%}")
    print(f"胜率: {result['win_rate']:.2%}")
    print(f"平均盈亏: {result['avg_profit']:.2%}")
    print(f"交易次数: {result['total_trades']}")
    print(f"最终权益: ¥{result['final_equity']:,.2f}")

    # 保存交易记录
    if 'trades' in result and not result['trades'].empty:
        print("\n💾 交易记录已保存到 trades.csv")
        result['trades'].to_csv('trades.csv', index=False)


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  🎯 A股回测 - 交互式配置选择器")
    print("=" * 70)

    while True:
        print("\n主菜单:")
        print("  1. 交互式配置回测")
        print("  2. 快速回测（使用默认配置）")
        print("  3. 权重优化")
        print("  4. 退出")

        choice = get_choice("请选择 [默认: 1]: ", 4)

        if choice == 1:
            run_interactive_backtest()
        elif choice == 2:
            print("\n运行快速回测...")
            codes = ['002353', '000592', '600519']
            result = AStockBacktestEngine(BACKTEST_CONFIG).run_backtest(
                codes, "2023-01-01", "2026-03-10", DEFAULT_WEIGHTS
            )
            if 'error' not in result:
                print(f"总收益率: {result['total_return']:.2%}")
                print(f"夏普比率: {result['sharpe_ratio']:.2f}")
        elif choice == 3:
            print("\n运行权重优化...")
            print("⚠️ 权重优化耗时较长，请耐心等待")
            optimizer = WeightOptimizer(OPTIMIZATION_CONFIG)
            best = optimizer.optimize(['002353', '000592'], "2023-01-01", "2026-03-10", step=10)
            if 'error' not in best:
                print(f"最优权重: {best['weights']}")
                print(f"最优夏普比率: {best['result']['sharpe_ratio']:.2f}")
        else:
            print("\n👋 再见!")
            break


if __name__ == "__main__":
    main()