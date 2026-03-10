#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETF数据获取模块 - 基于天天基金网/新浪财经
"""
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_etf_realtime_info(fund_code):
    """获取ETF实时估值"""
    try:
        url = f"http://fundgz.1234567.com.cn/js/{fund_code}.js"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text.strip()
            # 格式: jsonpgz({...});
            if content.startswith('jsonpgz(') and content.endswith(');'):
                import json
                json_str = content[8:-2]  # 去掉 jsonpgz( 和 );
                data = json.loads(json_str)
                return {
                    'name': data.get('name', ''),
                    'price': float(data.get('gsz', 0)),  # 估算净值
                    'change_pct': float(data.get('gszzl', 0)),
                    'date': data.get('jzrq', ''),
                    'net_value': float(data.get('dwjz', 0))  # 单位净值
                }
    except Exception as e:
        logger.warning(f"获取ETF实时数据失败: {e}")
    return None

def get_etf_historical_data(fund_code, days=60):
    """获取ETF历史净值数据"""
    try:
        # 尝试使用天天基金历史净值接口
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y-%m-%d')

        url = f"https://fund.eastmoney.com/f10/F10DataApi.aspx"
        params = {
            'type': 'lsjz',
            'code': fund_code,
            'page': 1,
            'per': 100,
            'sdate': start_date,
            'edate': end_date,
            'rt': int(datetime.now().timestamp() * 1000)
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f'https://fund.eastmoney.com/{fund_code}.html'
        }

        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            # 解析返回的数据
            import re
            data = response.text
            # 提取JSON数据
            match = re.search(r'var apidata=\{content:"([^"]+)",records:(\d+),pages:(\d+)\}', data)
            if match:
                content = match.group(1)
                # content中的HTML表格解析
                import html
                content = html.unescape(content)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')

                # 解析表格数据
                rows = []
                for tr in soup.find_all('tr'):
                    tds = tr.find_all('td')
                    if len(tds) >= 6:
                        rows.append(tds)

                if rows:
                    data_list = []
                    for row in rows:
                        try:
                            date_str = row[0].get_text().strip()
                            net_value = float(row[1].get_text().strip())
                            accum_value = float(row[2].get_text().strip())
                            daily_growth = row[3].get_text().strip()

                            # 处理增长率
                            if daily_growth.endswith('%'):
                                pct_chg = float(daily_growth.rstrip('%'))
                            else:
                                pct_chg = float(daily_growth) if daily_growth else 0

                            data_list.append({
                                'date': pd.to_datetime(date_str),
                                'close': net_value,
                                'open': net_value,  # 每日净值只有收盘价
                                'high': net_value,
                                'low': net_value,
                                'volume': 0,
                                'pct_chg': pct_chg,
                                'amount': 0
                            })
                        except Exception as e:
                            continue

                    if data_list:
                        df = pd.DataFrame(data_list)
                        df = df.sort_values('date', ascending=True).reset_index(drop=True)
                        return df

    except Exception as e:
        logger.warning(f"获取ETF历史数据失败: {e}")
    return pd.DataFrame()

if __name__ == "__main__":
    # 测试获取159326数据
    code = "159326"
    print(f"=== 获取 {code} 实时数据 ===")
    realtime = get_etf_realtime_info(code)
    if realtime:
        print(f"名称: {realtime['name']}")
        print(f"当前净值: {realtime['price']}")
        print(f"涨跌幅: {realtime['change_pct']}%")
        print(f"日期: {realtime['date']}")

    print(f"\n=== 获取 {code} 历史数据 ===")
    hist = get_etf_historical_data(code, days=30)
    if not hist.empty:
        print(hist.head(10))
    else:
        print("未获取到历史数据")