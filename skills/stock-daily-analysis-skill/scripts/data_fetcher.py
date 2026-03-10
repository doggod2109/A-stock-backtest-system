# -*- coding: utf-8 -*-
"""
数据获取模块 - 基于腾讯财经的A股数据获取（前复权）
支持 A股、港股、美股行情获取
"""

import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# 配置requests重试机制
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)

session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)
requests.Session = lambda: session


@dataclass
class StockQuote:
    """统一实时行情数据结构"""
    code: str
    name: str = ""
    price: float = 0.0
    change_pct: float = 0.0
    change_amount: float = 0.0
    volume: int = 0
    amount: float = 0.0
    open_price: float = 0.0
    high: float = 0.0
    low: float = 0.0
    pre_close: float = 0.0
    volume_ratio: Optional[float] = None
    turnover_rate: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    total_mv: Optional[float] = None
    circ_mv: Optional[float] = None


@dataclass
class ChipDistribution:
    """筹码分布数据"""
    profit_ratio: float = 0.0
    avg_cost: float = 0.0
    concentration_90: float = 0.0
    concentration_70: float = 0.0


def _is_us_code(stock_code: str) -> bool:
    """判断是否为美股代码（1-5个大写字母）"""
    code = stock_code.strip().upper()
    return bool(re.match(r'^[A-Z]{1,5}(\.[A-Z])?$', code))


def _is_hk_code(stock_code: str) -> bool:
    """判断是否为港股代码（5位数字）"""
    code = stock_code.lower()
    if code.startswith('hk'):
        numeric_part = code[2:]
        return numeric_part.isdigit() and 1 <= len(numeric_part) <= 5
    return code.isdigit() and len(code) == 5


def _is_etf_code(stock_code: str) -> bool:
    """判断是否为 ETF 代码"""
    etf_prefixes = ('51', '52', '56', '58', '15', '16', '18')
    return stock_code.startswith(etf_prefixes) and len(stock_code) == 6


def normalize_code(stock_code: str) -> tuple:
    """标准化股票代码"""
    code = stock_code.strip()
    if _is_us_code(code):
        return 'us', code.upper()
    if _is_hk_code(code):
        if code.lower().startswith('hk'):
            code = code[2:]
        return 'hk', code.zfill(5)
    return 'a', code


def get_daily_data(stock_code: str, days: int = 60) -> Optional[pd.DataFrame]:
    """获取股票日线数据（带重试）"""
    market, code = normalize_code(stock_code)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days * 2)

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            if market == 'us':
                return _fetch_us_data(code, start_date, end_date)
            elif market == 'hk':
                return _fetch_hk_data(code, start_date, end_date)
            else:
                return _fetch_a_stock_data(code, start_date, end_date, days)
        except Exception as e:
            logger.warning(f"获取 {stock_code} 数据失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"获取 {stock_code} 数据最终失败: {e}")
                return None


def _fetch_a_stock_data(stock_code: str, start_date: datetime, end_date: datetime, days: int) -> pd.DataFrame:
    """获取 A 股/ETF 数据 - 支持腾讯财经和新浪财经双数据源"""

    # 计算需要的数据量
    need_days = (end_date - start_date).days
    # 交易日大约是日历日的70%
    needed_data_points = int(need_days * 0.7) + 50

    # 优先使用新浪财经（数据量更大，最多2000条）
    if needed_data_points > 200:
        logger.info(f"需要 {needed_data_points} 条数据，优先使用新浪财经API: {stock_code}")
        df = _fetch_from_sina(stock_code, days=max(needed_data_points * 2, 2000))

        # 如果新浪财经失败，才尝试腾讯财经
        if df.empty:
            logger.info(f"新浪财经无数据，尝试腾讯财经API: {stock_code}")
            df = _fetch_from_tencent(stock_code)
    else:
        # 数据需求较少时，优先腾讯财经（速度更快）
        df = _fetch_from_tencent(stock_code)

        # 如果腾讯财经数据不足，尝试新浪财经
        if df.empty or len(df) < needed_data_points:
            logger.info(f"腾讯财经数据不足，尝试新浪财经API: {stock_code}")
            df = _fetch_from_sina(stock_code, days=max(needed_data_points * 2, 2000))

    if df.empty:
        logger.error(f"所有数据源均无数据: {stock_code}")
        return pd.DataFrame()

    # 过滤日期范围
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    return df


def _fetch_from_tencent(stock_code: str) -> pd.DataFrame:
    """从腾讯财经获取数据（前复权）"""
    # 腾讯财经API - 深圳股票需要sz前缀，上海股票需要sh前缀
    if stock_code.startswith('00') or stock_code.startswith('30') or stock_code.startswith('399'):
        tencent_code = f'sz{stock_code}'
    else:
        tencent_code = f'sh{stock_code}'
    
    # 腾讯财经K线接口（前复权）
    url = 'https://web.ifzq.gtimg.cn/appstock/app/newfqkline/get'
    params = {
        'param': f'{tencent_code},day,,,200,qfq'  # qfq 表示前复权
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = session.get(url, params=params, headers=headers, timeout=15)
        if response.status_code != 200:
            logger.warning(f"腾讯财经请求失败: HTTP {response.status_code}")
            return pd.DataFrame()

        data = response.json()
        if data.get('code') != 0 or not data.get('data'):
            return pd.DataFrame()

        # 提取K线数据
        stock_data = data['data'].get(tencent_code, {})
        klines = stock_data.get('qfqday', [])

        if not klines:
            return pd.DataFrame()

        # 腾讯数据格式: [日期, 开盘, 收盘, 最高, 最低, 成交量, {}, ...]
        # 注意：除权除息日会多返回列，需要过滤
        filtered_klines = []
        for kline in klines:
            if len(kline) >= 6:
                filtered_klines.append(kline[:6])

        df = pd.DataFrame(filtered_klines, columns=['date', 'open', 'close', 'high', 'low', 'volume'])

        if df.empty:
            return pd.DataFrame()

        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date'])

        # 数值转换
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 计算涨跌幅
        df['pct_chg'] = df['close'].pct_change() * 100
        df['pct_chg'] = df['pct_chg'].fillna(0)

        # 计算成交额
        df['amount'] = df['volume'] * df['close']

        # 去除空值行
        df = df.dropna(subset=['close', 'volume'])

        # 按日期排序
        df = df.sort_values('date', ascending=True).reset_index(drop=True)

        # 尝试从返回数据中获取股票名称
        qt_data = stock_data.get('qt', {})
        if qt_data and tencent_code in qt_data:
            qt_info = qt_data[tencent_code]
            if len(qt_info) > 1:
                df.attrs['stock_name'] = qt_info[1]  # 股票名称在第二列

        return df
        
    except Exception as e:
        logger.warning(f"腾讯财经获取数据异常: {e}")
        return pd.DataFrame()


def _fetch_from_sina(stock_code: str, days: int) -> pd.DataFrame:
    """从新浪财经获取数据（支持ETF和科创板）"""
    # 新浪财经API需要完整前缀
    # 沪市（6开头、5/51/52/56/58开头的ETF）用sh前缀
    # 深市（0开头）、创业板（3开头）、深市ETF（15/16/18开头）用sz前缀
    if stock_code.startswith('6') or stock_code.startswith(('5', '51', '52', '56', '58')):
        sina_code = f'sh{stock_code}'
    elif stock_code.startswith('0') or stock_code.startswith('3') or stock_code.startswith(('15', '16', '18')):
        sina_code = f'sz{stock_code}'
    else:
        sina_code = stock_code
    
    url = 'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData'
    params = {
        'symbol': sina_code,
        'scale': '240',  # 日线
        'ma': 'no',
        'datalen': str(days)
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finance.sina.com.cn'
    }
    
    try:
        response = session.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.warning(f"新浪财经请求失败: HTTP {response.status_code}")
            return pd.DataFrame()
        
        data_str = response.text.strip()
        if not data_str or data_str == 'null':
            logger.warning(f"新浪财经返回空数据: {stock_code}")
            return pd.DataFrame()
        
        # 新浪财经返回JSON数组，但格式特殊，需要eval
        data = eval(data_str)
        
        if not data:
            return pd.DataFrame()
        
        # 新浪数据格式: [{"day":"2025-05-14","open":"2.691","high":"2.752","low":"2.689","close":"2.737","volume":"12546489.00","amount":"34286605.93"}]
        df = pd.DataFrame(data)
        
        # 重命名列
        if 'day' in df.columns:
            df = df.rename(columns={'day': 'date'})
        
        # 确保必要的列存在
        required_cols = ['date', 'open', 'close', 'high', 'low', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"新浪财经数据缺少列: {missing_cols}")
            return pd.DataFrame()
        
        # 日期格式转换
        df['date'] = pd.to_datetime(df['date'])
        
        # 数值转换
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 计算成交额（如果没有返回）
        if 'amount' not in df.columns:
            df['amount'] = df['volume'] * df['close']
        else:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # 计算涨跌幅
        df['pct_chg'] = df['close'].pct_change() * 100
        df['pct_chg'] = df['pct_chg'].fillna(0)
        
        # 去除空值行
        df = df.dropna(subset=['close', 'volume'])
        
        # 按日期排序
        df = df.sort_values('date', ascending=True).reset_index(drop=True)
        
        logger.info(f"新浪财经成功获取 {stock_code} 数据: {len(df)} 条")
        
        return df
        
    except Exception as e:
        logger.warning(f"新浪财经获取数据异常: {e}")
        return pd.DataFrame()


def _fetch_hk_data(stock_code: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """获取港股数据"""
    logger.warning(f"暂不支持港股数据获取: {stock_code}")
    return pd.DataFrame()


def _fetch_us_data(stock_code: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """获取美股数据"""
    logger.warning(f"暂不支持美股数据获取: {stock_code}")
    return pd.DataFrame()


def get_stock_name(stock_code: str) -> str:
    """从历史数据中获取股票名称"""
    df = get_daily_data(stock_code, days=1)
    if df is not None and hasattr(df, 'attrs') and 'stock_name' in df.attrs:
        return df.attrs['stock_name']
    return stock_code


def get_realtime_quote(stock_code: str) -> Optional[StockQuote]:
    """获取实时行情（带重试）- 已废弃，仅保留兼容性"""
    logger.warning(f"get_realtime_quote 已废弃，请使用 get_daily_data 获取数据")
    return None


def get_chip_distribution(stock_code: str) -> Optional[ChipDistribution]:
    """获取筹码分布数据（暂不支持）"""
    logger.warning(f"暂不支持筹码分布数据获取: {stock_code}")
    return None
