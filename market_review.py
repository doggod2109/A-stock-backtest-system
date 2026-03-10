#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股大盘复盘报告生成器
分析上证指数、深证成指、创业板指等主要指数的涨跌幅、成交量、板块表现、热点分析等内容
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# 添加skill目录到Python路径
skill_dir = Path.home() / '.openclaw' / 'skills' / 'stock-daily-analysis-skill'
sys.path.insert(0, str(skill_dir))

from scripts.data_fetcher import get_daily_data, get_realtime_quote, get_stock_name
from scripts.trend_analyzer import StockTrendAnalyzer
from scripts.ai_analyzer import AIAnalyzer
import json


def load_config():
    """加载配置"""
    config_path = Path.home() / '.openclaw' / 'skills' / 'stock-daily-analysis-skill' / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"警告: 加载配置失败: {e}，使用默认配置")
        return {
            "data": {"days": 60, "realtime_enabled": True},
            "analysis": {"bias_threshold": 5.0}
        }


def format_market_report(index_name, code, result):
    """格式化单个指数报告"""
    technical = result.get('technical_indicators', {})
    ai_result = result.get('ai_analysis', {})

    lines = [
        f"\n{'='*60}",
        f"📊 {index_name} ({code})",
        f"{'='*60}",
        "",
        "【基本信息】",
    ]

    # 获取实时行情
    # 先尝试直接用code获取，如果失败则尝试其他格式
    quote = get_realtime_quote(code)

    if quote:
        lines.extend([
            f"  收盘价: {quote.price:.2f}",
            f"  涨跌幅: {quote.change_pct:+.2f}%",
            f"  涨跌额: {quote.change_amount:+.2f}",
            f"  成交量: {quote.volume/100000000:.2f}亿股" if quote.volume else "",
            f"  成交额: {quote.amount/100000000:.2f}亿元" if quote.amount else "",
            "",
        ])

    lines.extend([
        "【技术面分析】",
    ])

    if 'trend_status' in technical:
        lines.append(f"  趋势状态: {technical['trend_status']}")

    if 'ma5' in technical:
        lines.append(f"  MA5: {technical['ma5']:.2f}")
        lines.append(f"  MA10: {technical['ma10']:.2f}")
        lines.append(f"  MA20: {technical['ma20']:.2f}")

    if 'bias_ma5' in technical:
        lines.append(f"  乖离率(MA5): {technical['bias_ma5']:+.2f}%")

    if 'macd_status' in technical:
        lines.append(f"  MACD: {technical['macd_status']}")

    if 'rsi_status' in technical:
        lines.append(f"  RSI: {technical['rsi_status']}")

    if 'volume_status' in technical:
        lines.append(f"  量能状态: {technical['volume_status']}")

    if 'buy_signal' in technical:
        lines.append(f"  信号评分: {technical['signal_score']}/100")

    lines.append("")

    # AI分析
    if ai_result.get('analysis_summary'):
        lines.extend([
            "【AI深度分析】",
            f"  {ai_result['analysis_summary']}",
            "",
        ])

    if ai_result.get('risk_warning'):
        lines.extend([
            "【风险提示】",
            f"  {ai_result['risk_warning']}",
            "",
        ])

    return "\n".join(filter(None, lines))


def analyze_index(index_code, display_code, config):
    """分析单个指数"""
    print(f"正在分析 {display_code}...")

    # 获取指数名称
    name = get_stock_name(index_code)
    if not name:
        name = display_code

    # 获取历史数据（使用display_code格式）
    days = config.get('data', {}).get('days', 60)
    df = get_daily_data(display_code, days=days)

    if df is None or df.empty:
        return {
            'code': display_code,
            'name': name,
            'error': '数据获取失败'
        }

    # 技术分析
    analyzer = StockTrendAnalyzer()
    trend_result = analyzer.analyze(df, display_code)

    # AI分析
    ai_config = config.get('ai', {})
    ai_analyzer = AIAnalyzer(ai_config)
    ai_result = ai_analyzer.analyze(display_code, name, trend_result.to_dict())

    # 整合结果
    result = {
        'code': display_code,
        'name': name,
        'technical_indicators': trend_result.to_dict(),
        'ai_analysis': ai_result
    }

    return result


def generate_market_summary():
    """生成市场综述"""
    lines = [
        f"\n{'='*60}",
        "📈 A股大盘复盘报告",
        f"{'='*60}",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "【主要指数表现】",
    ]
    return "\n".join(lines)


def main():
    """主函数"""
    # 加载配置
    config = load_config()

    # 主要指数列表（使用新浪财经格式）
    indices = [
        ('sh000001', '上证指数', '000001'),
        ('sz399001', '深证成指', '399001'),
        ('sz399006', '创业板指', '399006'),
    ]

    # 生成报告
    report_lines = []
    report_lines.append(generate_market_summary())

    index_results = {}

    for sina_code, name, display_code in indices:
        result = analyze_index(sina_code, display_code, config)
        index_results[display_code] = result

        # 格式化报告 - 传入sina_code用于获取实时行情
        index_report = format_market_report(name, display_code, result, sina_code)
        report_lines.append(index_report)

    # 生成大盘综合分析
    summary_lines = [
        f"\n{'='*60}",
        "📋 市场综合分析",
        f"{'='*60}",
        "",
    ]

    # 统计指数表现
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0

    for code, result in index_results.items():
        if 'error' in result:
            continue

        technical = result.get('technical_indicators', {})
        trend = technical.get('trend_status', '')

        if '多头' in trend:
            bullish_count += 1
        elif '空头' in trend:
            bearish_count += 1
        else:
            neutral_count += 1

    summary_lines.extend([
        "【市场整体走势】",
        f"  多头指数: {bullish_count} 个",
        f"  空头指数: {bearish_count} 个",
        f"  震荡指数: {neutral_count} 个",
        "",
    ])

    # 市场情绪分析
    if bullish_count >= 2:
        sentiment = "🟢 强势"
        sentiment_desc = "市场整体走强，多头占优，可积极参与"
    elif bearish_count >= 2:
        sentiment = "🔴 弱势"
        sentiment_desc = "市场整体偏弱，空头主导，建议谨慎观望"
    else:
        sentiment = "🟡 震荡"
        sentiment_desc = "市场方向不明，多空分歧较大，建议控制仓位"

    summary_lines.extend([
        f"【市场情绪】",
        f"  情绪等级: {sentiment}",
        f"  情绪描述: {sentiment_desc}",
        "",
    ])

    # 操作建议
    summary_lines.extend([
        "【操作建议】",
        "",
    ])

    if bullish_count >= 2:
        summary_lines.extend([
            "  市场整体向好，可适当增加仓位",
            "  重点关注：强势板块的龙头股",
            "  仓位建议：6-8成",
        ])
    elif bearish_count >= 2:
        summary_lines.extend([
            "  市场整体偏弱，建议降低仓位",
            "  重点关注：抗跌品种和防御性板块",
            "  仓位建议：2-4成",
        ])
    else:
        summary_lines.extend([
            "  市场方向不明，建议观望为主",
            "  重点关注：震荡市中的结构性机会",
            "  仓位建议：3-5成",
        ])

    summary_lines.append("")

    # 风险提示
    summary_lines.extend([
        "【风险提示】",
        "  ⚠️ 技术分析基于历史数据，无法预测突发事件",
        "  ⚠️ 指数走势不代表个股表现，需具体分析",
        "  ⚠️ 股市有风险，投资需谨慎",
        "",
        f"{'='*60}",
    ])

    report_lines.append("\n".join(summary_lines))

    # 打印完整报告
    print("\n".join(report_lines))


if __name__ == "__main__":
    main()