#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速回测脚本
修改 config_template.py 后运行此脚本

注意：此脚本需要配合 stock-daily-analysis-skill 使用
"""

import sys
from pathlib import Path

# 添加 stock-daily-analysis-skill 到路径（用于数据获取和分析）
stock_analysis_path = Path(__file__).parent.parent.parent / "stock-daily-analysis-skill"
if stock_analysis_path.exists():
    sys.path.insert(0, str(stock_analysis_path))
    from scripts.data_fetcher import get_daily_data
    from scripts.trend_analyzer import StockTrendAnalyzer

from config_template import (
    STOCK_CODES,
    START_DATE,
    END_DATE,
    INIT_CASH,
    POSITION_SIZE,
    MAX_POSITIONS,
    WEIGHTS,
    BUY_THRESHOLD,
    SELL_THRESHOLD,
    STOP_LOSS,
    TAKE_PROFIT,
)
from backtesting.config import BACKTEST_CONFIG, SIGNAL_CONFIG
from backtesting.engine import AStockBacktestEngine
from backtesting.report_generator import ReportGenerator


def run_backtest():
    """运行回测"""
    print("=" * 70)
    print("🎯 A股快速回测")
    print("=" * 70)

    # 配置汇总
    config = BACKTEST_CONFIG.copy()
    config['init_cash'] = INIT_CASH
    config['position_size'] = POSITION_SIZE
    config['max_positions'] = MAX_POSITIONS
    config['stop_loss'] = STOP_LOSS / 100
    config['take_profit'] = TAKE_PROFIT / 100
    config['buy_threshold'] = BUY_THRESHOLD
    config['sell_threshold'] = SELL_THRESHOLD

    print(f"\n📋 配置汇总:")
    print(f"  股票代码: {', '.join(STOCK_CODES)}")
    print(f"  时间范围: {START_DATE} ~ {END_DATE}")
    print(f"  初始资金: ¥{INIT_CASH:,}")
    print(f"  单只仓位: {POSITION_SIZE*100:.0f}%")
    print(f"  最大持仓: {MAX_POSITIONS}只")
    print(f"  评分权重: {WEIGHTS}")
    print(f"  买入阈值: {BUY_THRESHOLD}")
    print(f"  卖出阈值: {SELL_THRESHOLD}")
    print(f"  止损: {STOP_LOSS}%")
    print(f"  止盈: {TAKE_PROFIT}%")

    print("\n" + "=" * 70)
    print("🚀 开始回测")
    print("=" * 70 + "\n")

    # 检查是否可以访问数据获取和分析模块
    try:
        from scripts.data_fetcher import get_daily_data
        from scripts.trend_analyzer import StockTrendAnalyzer
        has_stock_analysis = True
    except ImportError:
        print("⚠️  未找到 stock-daily-analysis-skill，无法运行回测")
        print("   请确保 stock-daily-analysis-skill 位于 ../stock-daily-analysis-skill")
        return

    # 创建回测引擎，传入数据获取和分析器
    engine = AStockBacktestEngine(config, data_fetcher=get_daily_data, analyzer=StockTrendAnalyzer())

    # 运行回测
    result = engine.run_backtest(STOCK_CODES, START_DATE, END_DATE, WEIGHTS)

    # 显示结果
    if 'error' in result:
        print(f"\n❌ 回测失败: {result['error']}")
        return

    print("\n" + "=" * 70)
    print("📊 回测结果")
    print("=" * 70)
    print(f"总收益率: {result['total_return']:.2%}")
    print(f"年化收益率: {result['annual_return']:.2%}")
    print(f"夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"最大回撤: {result['max_drawdown']:.2%}")
    print(f"胜率: {result['win_rate']:.2%}")
    print(f"平均盈亏: {result['avg_profit']:.2%}")
    print(f"交易次数: {result['total_trades']}")
    print(f"最终权益: ¥{result['final_equity']:,.2f}")

    # 显示交易明细
    if result['total_trades'] > 0 and not result['trades'].empty:
        print(f"\n💰 交易明细:")
        print(result['trades'].to_string(index=False))

    print("\n" + "=" * 70)
    print("✅ 回测完成！")
    print("=" * 70)

    # 保存交易记录
    if result['total_trades'] > 0 and not result['trades'].empty:
        trades_file = Path(__file__).parent / "trades.csv"
        result['trades'].to_csv(trades_file, index=False)
        print(f"\n💾 交易记录已保存到: {trades_file}")

    # 生成完整报告（JSON + Excel + HTML）
    print(f"\n📝 正在生成完整回测报告...")
    report_config = {
        'codes': STOCK_CODES,
        'start_date': START_DATE,
        'end_date': END_DATE,
        'init_cash': INIT_CASH,
        'position_size': POSITION_SIZE,
        'max_positions': MAX_POSITIONS,
        'weights': WEIGHTS,
        'buy_threshold': BUY_THRESHOLD,
        'sell_threshold': SELL_THRESHOLD,
        'stop_loss': STOP_LOSS / 100,
        'take_profit': TAKE_PROFIT / 100,
    }

    report_gen = ReportGenerator()
    trades_df = result['trades'] if result['total_trades'] > 0 else None
    report_gen.generate(result, report_config, trades_df)


if __name__ == "__main__":
    run_backtest()