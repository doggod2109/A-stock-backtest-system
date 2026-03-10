#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股01810（小米集团-W）技术面分析脚本 - 使用腾讯数据源
"""
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

# 配置
requests.packages.urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://gu.qq.com/',
}

session = requests.Session()
session.headers.update(headers)
session.verify = False


def get_hk_realtime_data(stock_code='01810'):
    """获取港股实时行情数据"""
    try:
        url = f"https://qt.gtimg.cn/q=hk{stock_code}"
        response = session.get(url, timeout=10)
        response.encoding = 'gbk'

        if response.status_code != 200:
            print(f"请求失败: HTTP {response.status_code}")
            return None

        # 解析腾讯财经数据格式
        data_str = response.text
        if 'v_hk' not in data_str:
            print("数据格式错误")
            return None

        # 提取数据部分
        start = data_str.find('"') + 1
        end = data_str.rfind('"')
        data_str = data_str[start:end]

        parts = data_str.split('~')
        if len(parts) < 40:
            print(f"数据字段不足: {len(parts)}")
            return None

        # 腾讯数据字段映射（根据实际返回数据验证）
        # 字段0=变量名, 字段1=名称, 字段2=代码, 字段3=当前价, 字段4=昨收, 字段5=开盘, 字段6=成交量
        # 字段30=时间, 字段31=涨跌额, 字段32=涨跌幅
        # 字段33=最高, 字段34=最低, 字段37=成交额
        real_data = {
            'name': parts[1],
            'code': parts[2],
            'price': float(parts[3]) if parts[3] else 0,
            'pre_close': float(parts[4]) if parts[4] else 0,
            'open': float(parts[5]) if parts[5] else 0,
            'volume': float(parts[6]) if parts[6] else 0,
            'high': float(parts[33]) if len(parts) > 33 and parts[33] else 0,
            'low': float(parts[34]) if len(parts) > 34 and parts[34] else 0,
            'turnover': float(parts[37]) if len(parts) > 37 and parts[37] else 0,
            'timestamp': parts[30] if len(parts) > 30 else '',
            'change': float(parts[31]) if len(parts) > 31 and parts[31] else 0,
            'pct_chg': float(parts[32]) if len(parts) > 32 and parts[32] else 0,
            'pe': 0,
        }

        # 计算涨跌额和涨跌幅（如果API未提供）
        if real_data['change'] == 0 and real_data['pre_close'] > 0:
            real_data['change'] = real_data['price'] - real_data['pre_close']
        if real_data['pct_chg'] == 0 and real_data['pre_close'] > 0:
            real_data['pct_chg'] = (real_data['change'] / real_data['pre_close']) * 100

        # 如果成交额为空，使用量价估算
        if real_data['turnover'] == 0 and real_data['volume'] > 0 and real_data['price'] > 0:
            real_data['turnover'] = real_data['volume'] * real_data['price']

        # 如果成交额为空，使用量价估算
        if real_data['turnover'] == 0 and real_data['volume'] > 0 and real_data['price'] > 0:
            real_data['turnover'] = real_data['volume'] * real_data['price']

        return real_data

    except Exception as e:
        print(f"获取实时数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_hk_historical_data(stock_code='01810', num_days=250):
    """获取港股历史K线数据 - 使用腾讯证券API"""
    try:
        # 腾讯证券API
        # 格式: https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get
        # 参数: param=hk01810,day,,,250,qfq (前复权)
        sina_code = f'hk{stock_code.zfill(5)}'

        url = "https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get"
        params = {
            'param': f'{sina_code},day,,,{num_days},qfq',  # qfq=前复权
        }

        response = session.get(url, params=params, timeout=15)

        if response.status_code != 200:
            print(f"历史数据请求失败: HTTP {response.status_code}")
            return None

        data = response.json()
        if data.get('code') != 0:
            print(f"历史数据返回错误: {data.get('msg')}")
            return None

        stock_data = data['data'].get(sina_code, {})
        klines = stock_data.get('day', [])

        if not klines:
            print("无K线数据")
            return None

        # 解析K线数据
        # 格式: [日期, 开盘, 收盘, 最高, 最低, 成交量, {}, 涨跌幅, 成交额, ...]
        records = []
        for kline in klines:
            if len(kline) >= 9:
                records.append({
                    'date': kline[0],
                    'open': float(kline[1]),
                    'close': float(kline[2]),
                    'high': float(kline[3]),
                    'low': float(kline[4]),
                    'volume': float(kline[5]),
                    'pct_chg': float(kline[7]),
                    'amount': float(kline[8]),
                })

        if not records:
            return None

        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # 过滤掉未来的日期（可能是数据问题）
        today = datetime.now()
        df = df[df['date'] <= today]

        return df

    except Exception as e:
        print(f"获取历史数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_technical_indicators(df):
    """计算技术指标"""
    df = df.copy()

    # 均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA60'] = df['close'].rolling(window=min(60, len(df))).mean()

    # MACD
    df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = df['EMA12'] - df['EMA26']
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 乖离率
    df['BIAS_MA5'] = ((df['close'] - df['MA5']) / df['MA5']) * 100
    df['BIAS_MA10'] = ((df['close'] - df['MA10']) / df['MA10']) * 100
    df['BIAS_MA20'] = ((df['close'] - df['MA20']) / df['MA20']) * 100

    # KDJ
    low_list = df['low'].rolling(9, min_periods=1).min()
    high_list = df['high'].rolling(9, min_periods=1).max()
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    df['K'] = rsv.ewm(com=2).mean()
    df['D'] = df['K'].ewm(com=2).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']

    # 成交量均线
    df['VOL5'] = df['volume'].rolling(window=5).mean()
    df['VOL10'] = df['volume'].rolling(window=10).mean()

    return df


def analyze_trend(df):
    """趋势分析"""
    if len(df) < 20:
        return {'status': '数据不足', 'score': 0}

    latest = df.iloc[-1]

    # 趋势判断
    if latest['close'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
        status = '强势多头'
        score = 35
    elif latest['close'] > latest['MA20'] and latest['MA5'] > latest['MA20']:
        status = '多头排列'
        score = 30
    elif latest['close'] > latest['MA20']:
        status = '上升通道'
        score = 20
    elif latest['close'] < latest['MA5'] < latest['MA10'] < latest['MA20']:
        status = '弱势空头'
        score = 5
    elif latest['close'] < latest['MA20']:
        status = '下降通道'
        score = 10
    else:
        status = '盘整震荡'
        score = 15

    return {'status': status, 'score': score}


def calculate_signal_score(df, real_data):
    """计算买入信号评分"""
    latest = df.iloc[-1]
    score = 0
    details = []

    # 1. 趋势评分（35分）
    trend = analyze_trend(df)
    score += trend['score']
    details.append(f"趋势: {trend['score']}/35 ({trend['status']})")

    # 2. MACD评分（15分）
    if not pd.isna(latest['DIF']) and not pd.isna(latest['DEA']):
        if latest['DIF'] > latest['DEA'] and latest['DIF'] > 0:
            macd_score = 15
            macd_status = '金叉（多头）'
        elif latest['DIF'] > latest['DEA'] and latest['DIF'] < 0:
            macd_score = 10
            macd_status = '金叉（零轴下）'
        elif latest['DIF'] < latest['DEA']:
            macd_score = 0
            macd_status = '死叉（空头）'
        else:
            macd_score = 8
            macd_status = '中性'
    else:
        macd_score = 0
        macd_status = '数据不足'

    score += macd_score
    details.append(f"MACD: {macd_score}/15 ({macd_status})")

    # 3. RSI评分（10分）
    if not pd.isna(latest['RSI']):
        if latest['RSI'] < 30:
            rsi_score = 10
            rsi_status = '超卖'
        elif latest['RSI'] < 50:
            rsi_score = 6
            rsi_status = '偏弱'
        elif latest['RSI'] < 70:
            rsi_score = 8
            rsi_status = '偏强'
        else:
            rsi_score = 0
            rsi_status = '超买'
    else:
        rsi_score = 0
        rsi_status = '数据不足'

    score += rsi_score
    details.append(f"RSI: {rsi_score}/10 ({rsi_status})")

    # 4. 乖离率评分（15分）
    if not pd.isna(latest['BIAS_MA5']):
        bias_abs = abs(latest['BIAS_MA5'])
        if bias_abs < 3:
            bias_score = 15
        elif bias_abs < 5:
            bias_score = 10
        elif bias_abs < 8:
            bias_score = 5
        else:
            bias_score = 0
    else:
        bias_score = 0

    score += bias_score
    details.append(f"乖离率: {bias_score}/15")

    # 5. 支撑压力评分（15分）
    support_score = 0
    if not pd.isna(latest['MA5']):
        if latest['close'] >= latest['MA5']:
            support_score += 5
    if not pd.isna(latest['MA10']):
        if latest['close'] >= latest['MA10']:
            support_score += 5
    if not pd.isna(latest['MA20']):
        if latest['close'] >= latest['MA20']:
            support_score += 5

    score += support_score
    details.append(f"均线支撑: {support_score}/15")

    # 6. 量能评分（10分）
    if not pd.isna(latest['VOL5']) and not pd.isna(latest['volume']):
        vol_ratio = latest['volume'] / latest['VOL5'] if latest['VOL5'] > 0 else 1
        if real_data['pct_chg'] > 0:  # 上涨时
            if vol_ratio >= 1.5:
                vol_score = 8  # 放量上涨
            elif vol_ratio >= 1.0:
                vol_score = 5  # 正常量
            else:
                vol_score = 2  # 缩量上涨
        else:  # 下跌时
            if vol_ratio <= 0.7:
                vol_score = 8  # 缩量下跌
            elif vol_ratio <= 1.2:
                vol_score = 5  # 正常量
            else:
                vol_score = 0  # 放量下跌
    else:
        vol_score = 0

    score += vol_score
    details.append(f"量能: {vol_score}/10")

    return score, details


def get_support_resistance(df):
    """计算支撑阻力位"""
    recent = df.tail(30)  # 最近30个交易日

    # 计算近期高点作为阻力位
    resistance_levels = recent.nlargest(3, 'high')['high'].tolist()

    # 计算近期低点作为支撑位
    support_levels = recent.nsmallest(3, 'low')['low'].tolist()

    # 均线支撑
    latest = df.iloc[-1]
    ma_support = []
    if not pd.isna(latest['MA20']):
        ma_support.append(latest['MA20'])
    if not pd.isna(latest['MA60']):
        ma_support.append(latest['MA60'])

    return {
        'resistance': sorted(set(resistance_levels), reverse=True),
        'support': sorted(set(support_levels)),
        'ma_support': sorted([x for x in ma_support if not pd.isna(x)])
    }


def generate_ai_analysis(df, real_data, signal_score):
    """生成AI分析建议"""
    latest = df.iloc[-1]

    # 基础信息
    analysis = {
        'current_price': real_data['price'],
        'change_pct': real_data['pct_chg'],
        'signal_score': signal_score,
    }

    # 综合判断
    if signal_score >= 75:
        analysis['operation_advice'] = '买入'
        analysis['confidence_level'] = '高'
        analysis['target_price'] = round(latest['high'] * 1.1, 2)
        analysis['stop_loss'] = round(latest['low'] * 0.95, 2)
        analysis['sentiment'] = '技术面强势，建议关注'
    elif signal_score >= 60:
        analysis['operation_advice'] = '逢低买入'
        analysis['confidence_level'] = '中高'
        analysis['target_price'] = round(latest['high'] * 1.08, 2)
        analysis['stop_loss'] = round(latest['low'] * 0.92, 2)
        analysis['sentiment'] = '趋势向好，可分批介入'
    elif signal_score >= 45:
        analysis['operation_advice'] = '持有'
        analysis['confidence_level'] = '中'
        analysis['target_price'] = round(latest['high'] * 1.05, 2)
        analysis['stop_loss'] = round(latest['low'] * 0.90, 2)
        analysis['sentiment'] = '观望为主，谨慎操作'
    elif signal_score >= 30:
        analysis['operation_advice'] = '观望'
        analysis['confidence_level'] = '低'
        analysis['target_price'] = '-'
        analysis['stop_loss'] = '-'
        analysis['sentiment'] = '信号不明，等待方向'
    else:
        analysis['operation_advice'] = '规避'
        analysis['confidence_level'] = '低'
        analysis['target_price'] = '-'
        analysis['stop_loss'] = '-'
        analysis['sentiment'] = '风险较高，建议回避'

    return analysis


def generate_report(real_data, df, signal_score, score_details, ai_analysis, support_resistance):
    """生成完整分析报告"""
    latest = df.iloc[-1]

    report = f"""{'='*70}
📊 小米集团-W (01810.HK) 技术面分析报告
{'='*70}

📌 【基本信息】
股票名称: {real_data['name']}
股票代码: {real_data['code']}
当前价格: HK${real_data['price']:.3f}
昨收价格: HK${real_data['pre_close']:.3f}
涨跌价格: HK${real_data['change']:+.3f}
涨跌幅: {real_data['pct_chg']:+.2f}%
开盘价格: HK${real_data['open']:.3f}
最高价格: HK${real_data['high']:.3f}
最低价格: HK${real_data['low']:.3f}
成交量: {real_data['volume']:,.0f} 股
成交额: HK${real_data['turnover']:,.0f}
更新时间: {real_data['timestamp']}

📈 【技术指标分析】

【均线系统】
趋势状态: {analyze_trend(df)['status']}
MA5:  HK${latest['MA5']:.3f}
MA10: HK${latest['MA10']:.3f}
MA20: HK${latest['MA20']:.3f}
MA60: HK${latest['MA60']:.3f}

均线排列: {'MA5 > MA10 > MA20 (多头排列)' if latest['MA5'] > latest['MA10'] > latest['MA20'] else '均线交叉'}

【MACD指标】
DIF: {latest['DIF']:.6f}
DEA: {latest['DEA']:.6f}
MACD: {latest['MACD']:.6f}
信号: {'金叉（多头）' if latest['DIF'] > latest['DEA'] and latest['DIF'] > 0 else '金叉（零轴下）' if latest['DIF'] > latest['DEA'] else '死叉（空头）'}

【RSI指标】
RSI(14): {latest['RSI']:.2f}
状态: {'超买' if latest['RSI'] > 70 else '超卖' if latest['RSI'] < 30 else '强势' if latest['RSI'] > 50 else '弱势'}

【KDJ指标】
K: {latest['K']:.2f}
D: {latest['D']:.2f}
J: {latest['J']:.2f}

【乖离率】
BIAS_MA5: {latest['BIAS_MA5']:+.2f}%
BIAS_MA10: {latest['BIAS_MA10']:+.2f}%
BIAS_MA20: {latest['BIAS_MA20']:+.2f}%

📊 【趋势判断】
当前趋势: {analyze_trend(df)['status']}
方向: {'向上' if latest['close'] > latest['MA20'] else '向下'}

📉 【量能分析】
当前成交量: {latest['volume']:,.0f}
5日均量: {latest['VOL5']:,.0f}
10日均量: {latest['VOL10']:,.0f}
量比: {latest['volume']/latest['VOL5']:.2f} (相对于5日均量)
量价关系: {'放量上涨' if real_data['pct_chg'] > 0 and latest['volume']/latest['VOL5'] > 1.2 else '缩量上涨' if real_data['pct_chg'] > 0 else '放量下跌' if latest['volume']/latest['VOL5'] > 1.2 else '缩量下跌'}

📍 【支撑阻力位】
近期阻力位:
{chr(10).join([f"  • HK${r:.3f}" for r in support_resistance['resistance'][:3]])}

近期支撑位:
{chr(10).join([f"  • HK${s:.3f}" for s in support_resistance['support'][:3]])}

均线支撑:
{chr(10).join([f"  • HK${m:.3f}" for m in support_resistance['ma_support'][:2]])}

🎯 【买入信号评分】
总分: {signal_score}/100
详细评分:
{chr(10).join([f"  • {d}" for d in score_details])}

💡 【AI分析建议】
操作建议: {ai_analysis['operation_advice']}
信心度: {ai_analysis['confidence_level']}
目标价位: HK${ai_analysis['target_price']}
止损价位: HK${ai_analysis['stop_loss']}
市场情绪: {ai_analysis['sentiment']}

⚠️ 【风险提示】
"""

    # 风险提示
    warnings = []
    if latest['RSI'] > 70:
        warnings.append(f"⚠️ RSI({latest['RSI']:.1f})接近超买区间，短期可能面临回调压力")
    if latest['RSI'] < 30:
        warnings.append(f"⚠️ RSI({latest['RSI']:.1f})进入超卖区间，可能存在反弹机会")
    if abs(latest['BIAS_MA5']) > 5:
        warnings.append(f"⚠️ 股价偏离MA5乖离率较大({latest['BIAS_MA5']:+.2f}%)，短期波动风险增加")
    if real_data['pct_chg'] < -5:
        warnings.append(f"⚠️ 今日跌幅较大({real_data['pct_chg']:.2f}%)，关注下方支撑位")
    if real_data['pct_chg'] > 5:
        warnings.append(f"⚠️ 今日涨幅较大({real_data['pct_chg']:.2f}%)，注意追高风险")
    if latest['volume'] / latest['VOL5'] > 2:
        warnings.append(f"⚠️ 今日成交量异常放大，需关注资金流向")

    if warnings:
        report += '\n'.join(warnings)
    else:
        report += "✓ 当前技术指标相对健康，无明显风险信号"

    # 操作策略
    report += f"""

📝 【操作策略】
"""

    if ai_analysis['operation_advice'] in ['买入', '逢低买入']:
        report += f"""当前技术面{analyze_trend(df)['status']}，各项指标配合较好。
建议操作:
  • 激进型: 可在回调至MA5附近时分批建仓
  • 稳健型: 等待回踩MA20确认支撑后再介入
  • 仓位建议: 初始仓位不超过20%
  • 止损策略: 跌破{ai_analysis['stop_loss']}果断止损
"""
    elif ai_analysis['operation_advice'] == '持有':
        report += f"""当前趋势不明确，建议以观望为主。
建议操作:
  • 已持有: 继续持有，关注均线支撑
  • 未持有: 等待更明确的入场信号
  • 止损位: {ai_analysis['stop_loss']}
"""
    else:
        report += f"""当前技术面偏弱，建议谨慎操作。
建议操作:
  • 已持有: 可考虑减仓或清仓
  • 未持有: 暂时观望，等待企稳信号
  • 关注点: 下方支撑位突破情况
"""

    # 近期走势
    report += f"""
📅 【近期表现】
"""
    recent_5 = df.tail(5)[::-1]  # 最近5天，倒序
    for _, row in recent_5.iterrows():
        arrow = "🔴" if row['pct_chg'] < 0 else "🟢"
        report += f"{arrow} {row['date'].strftime('%Y-%m-%d')} | 收盘: HK${row['close']:.3f} | 涨跌: {row['pct_chg']:+.2f}% | 成交量: {row['volume']:,.0f}\n"

    report += f"""
{'='*70}
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
免责声明: 本报告基于技术指标分析，仅供参考，不构成投资建议。
{'='*70}
"""

    return report


def main():
    """主函数"""
    print("🔍 开始分析港股01810（小米集团-W）...\n")

    # 1. 获取实时行情
    print("📡 获取实时行情...")
    real_data = get_hk_realtime_data('01810')
    if not real_data:
        print("❌ 获取实时行情失败")
        return

    print(f"✅ 实时行情: {real_data['name']} ({real_data['code']}) 价格: HK${real_data['price']:.3f} {real_data['pct_chg']:+.2f}%\n")

    # 2. 获取历史数据
    print("📊 获取历史K线数据...")
    df = get_hk_historical_data('01810', 250)
    if df is None or len(df) < 60:
        print("❌ 历史数据不足")
        return

    print(f"✅ 历史数据: 获取到 {len(df)} 个交易日数据\n")

    # 3. 计算技术指标
    print("🔢 计算技术指标...")
    df = calculate_technical_indicators(df)
    print("✅ 技术指标计算完成\n")

    # 4. 计算信号评分
    print("🎯 计算买入信号评分...")
    signal_score, score_details = calculate_signal_score(df, real_data)
    print(f"✅ 信号评分: {signal_score}/100\n")

    # 5. 生成AI分析
    print("🤖 生成AI分析...")
    ai_analysis = generate_ai_analysis(df, real_data, signal_score)
    print("✅ AI分析完成\n")

    # 6. 计算支撑阻力位
    print("📏 计算支撑阻力位...")
    support_resistance = get_support_resistance(df)
    print("✅ 支撑阻力位计算完成\n")

    # 7. 生成完整报告
    print("📝 生成分析报告...")
    report = generate_report(real_data, df, signal_score, score_details, ai_analysis, support_resistance)

    # 输出报告
    print("\n" + "="*70)
    print(report)

    # 保存报告
    report_file = '/tmp/xiaomi_01810_analysis_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ 报告已保存至: {report_file}")

    return report_file


if __name__ == '__main__':
    main()