# -*- coding: utf-8 -*-
"""
A股回测引擎
基于评分系统的策略回测
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AStockBacktestEngine:
    """A股回测引擎"""

    def __init__(self, config: Optional[Dict] = None, data_fetcher=None, analyzer=None):
        """初始化回测引擎

        Args:
            config: 回测配置
            data_fetcher: 数据获取函数（可选）
            analyzer: 技术分析器（可选）
        """
        self.config = config or {}
        self.init_cash = self.config.get("init_cash", 1_000_000)
        self.fees = self.config.get("fees", {})
        self.slippage = self.config.get("slippage", 0.0001)

        # 交易记录
        self.trades = []
        self.positions = {}  # {code: {'quantity': 0, 'avg_price': 0, 'entry_date': None}}
        self.cash = self.init_cash
        self.equity_curve = []

        # 分析器和数据获取器（外部传入）
        self.data_fetcher = data_fetcher
        self.analyzer = analyzer

    def fetch_data(self, code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            股票数据DataFrame
        """
        if self.data_fetcher is None:
            logger.warning("未提供数据获取器，请从外部传入")
            return None

        # 计算需要的数据天数
        from datetime import datetime
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_dt - start_dt).days + 30  # 多取30天确保数据充足

        return self.data_fetcher(code, days=days)
        """
        获取股票历史数据

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame
        """
        try:
            # 计算需要的天数，确保能获取到足够的历史数据
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            days_needed = (end_dt - start_dt).days * 2  # 乘以2确保覆盖

            # 至少获取1000天数据
            days = max(days_needed, 1000)

            df = get_daily_data(code, days=days)
            if df.empty:
                return None

            # 过滤日期范围
            df['date'] = pd.to_datetime(df['date'])
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            if df.empty:
                return None

            return df.set_index('date').sort_index()
        except Exception as e:
            logger.error(f"获取 {code} 数据失败: {e}")
            return None

    def calculate_signals(self, df: pd.DataFrame, code: str, weights: Dict[str, int]) -> pd.DataFrame:
        """
        计算买卖信号（基于评分系统）

        Args:
            df: K线数据
            code: 股票代码
            weights: 评分权重

        Returns:
            添加信号列的DataFrame
        """
        df = df.copy()

        # 逐日计算评分和信号
        signals = []
        for i in range(len(df)):
            # 历史数据
            hist_df = df.iloc[:i+1]
            if len(hist_df) < 20:  # 至少20天数据才能计算
                signals.append(0)
                continue

            # 使用分析器计算
            try:
                result = self.analyzer.analyze(hist_df, code)

                # 计算加权评分
                score = self._calculate_weighted_score(result, weights)

                # 判断信号
                signal = self._score_to_signal(score)
                signals.append(signal)
            except Exception as e:
                logger.warning(f"计算 {code} 第 {i} 天信号失败: {e}")
                signals.append(0)

        df['signal'] = signals
        df['score'] = 0  # TODO: 添加评分
        return df

    def _calculate_weighted_score(self, result, weights: Dict[str, int]) -> float:
        """
        计算加权评分

        Args:
            result: 分析结果
            weights: 权重配置

        Returns:
            加权评分
        """
        score = 0

        # 趋势评分
        trend_map = {
            "强势多头": 30,
            "多头排列": 26,
            "弱势多头": 18,
            "盘整": 12,
            "弱势空头": 8,
            "空头排列": 4,
            "强势空头": 0,
        }
        score += trend_map.get(result.trend_status.value, 12) * (weights.get('trend', 30) / 30)

        # MACD评分
        macd_map = {
            "零轴上金叉": 15,
            "金叉": 12,
            "上穿零轴": 10,
            "多头": 8,
            "空头": 2,
            "下穿零轴": 0,
            "死叉": 0,
        }
        score += macd_map.get(result.macd_status.value, 5) * (weights.get('macd', 15) / 15)

        # RSI评分
        rsi_map = {
            "超卖": 10,
            "强势买入": 8,
            "中性": 5,
            "弱势": 3,
            "超买": 0,
        }
        score += rsi_map.get(result.rsi_status.value, 5) * (weights.get('rsi', 10) / 10)

        # 乖离率评分
        bias = result.bias_ma5
        if bias < 0:
            bias_score = 20 if bias > -3 else (16 if bias > -5 else 8)
        elif bias < 2:
            bias_score = 18
        elif bias < 5:
            bias_score = 14
        else:
            bias_score = 4
        score += bias_score * (weights.get('bias', 20) / 20)

        # 量能评分
        vol_map = {
            "缩量回调": 15,
            "放量上涨": 12,
            "量能正常": 10,
            "缩量上涨": 6,
            "放量下跌": 0,
        }
        score += vol_map.get(result.volume_status.value, 8) * (weights.get('volume', 15) / 15)

        # 支撑评分
        support_score = 0
        if result.support_ma5:
            support_score += 5
        if result.support_ma10:
            support_score += 5
        score += support_score * (weights.get('support', 10) / 10)

        return min(score, 100)

    def _score_to_signal(self, score: float) -> int:
        """
        评分转信号

        Returns:
            1=买入, 0=持有, -1=卖出
        """
        if score >= 75:
            return 1  # 强烈买入
        elif score >= 60:
            return 1  # 买入
        elif score >= 45:
            return 0  # 持有
        elif score >= 30:
            return 0  # 观望
        else:
            return -1  # 卖出

    def run_backtest(
        self,
        codes: List[str],
        start_date: str,
        end_date: str,
        weights: Optional[Dict[str, int]] = None
    ) -> Dict:
        """
        运行回测

        Args:
            codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            weights: 评分权重

        Returns:
            回测结果
        """
        logger.info(f"开始回测: {codes}, {start_date} ~ {end_date}")

        weights = weights or {}

        # 获取所有股票数据
        stock_data = {}
        for code in codes:
            df = self.fetch_data(code, start_date, end_date)
            if df is not None:
                stock_data[code] = df

        if not stock_data:
            logger.error("没有获取到任何股票数据")
            return {"error": "无数据"}

        # 找出共同的交易日
        all_dates = set()
        for df in stock_data.values():
            all_dates.update(df.index)
        trading_dates = sorted(all_dates)

        # 逐日回测
        for date in trading_dates:
            self._process_trading_day(date, stock_data, weights)

            # 记录权益
            total_equity = self._calculate_equity(stock_data, date)
            self.equity_curve.append({
                'date': date,
                'equity': total_equity,
                'cash': self.cash,
            })

        # 生成回测报告
        report = self._generate_report(trading_dates)

        logger.info(f"回测完成: 总收益率 {report['total_return']:.2%}")
        return report

    def _process_trading_day(
        self,
        date: pd.Timestamp,
        stock_data: Dict[str, pd.DataFrame],
        weights: Dict[str, int]
    ):
        """处理单个交易日"""
        for code, df in stock_data.items():
            # 计算信号（如果还没有）
            if 'signal' not in df.columns:
                df_with_signals = self.calculate_signals(df, code, weights)
                stock_data[code] = df_with_signals
                df = df_with_signals

            if date not in df.index:
                continue

            row = df.loc[date]

            # 获取前一日的信号（用前一日的信号，当日开盘价执行）
            # 找到上一个有数据的日期
            all_dates = df.index.tolist()
            date_idx = all_dates.index(date)

            if date_idx == 0:
                # 第一天没有前一日的信号，跳过
                continue

            prev_date = all_dates[date_idx - 1]
            if prev_date not in df.index:
                continue

            signal = df.loc[prev_date, 'signal']
            price = row['open']  # 使用当日开盘价执行交易

            # 执行交易
            if signal == 1:  # 买入信号
                self._execute_buy(code, price, date)
            elif signal == -1:  # 卖出信号
                self._execute_sell(code, price, date)

            # 止损止盈检查（用当日收盘价检查）
            self._check_risk_management(code, row['close'], date)

    def _execute_buy(self, code: str, price: float, date: pd.Timestamp):
        """执行买入"""
        if code in self.positions and self.positions[code]['quantity'] > 0:
            return  # 已持仓

        # 计算可买数量（考虑手续费）
        commission_rate = self.fees.get('commission', 0.0003)
        max_invest = self.cash * self.config.get('position_size', 0.3)

        # 实际可用于买股票的金额（扣除佣金）
        invest_amount = max_invest / (1 + commission_rate)
        quantity = int(invest_amount / price)

        if quantity <= 0:
            return

        # 计算实际成本（含佣金）
        amount = quantity * price
        commission = amount * commission_rate
        total_cost = amount + commission

        if total_cost > self.cash:
            return

        # 执行买入
        self.cash -= total_cost
        self.positions[code] = {
            'quantity': quantity,
            'avg_price': price,
            'entry_date': date,
        }

        self.trades.append({
            'date': date,
            'code': code,
            'action': 'buy',
            'price': price,
            'quantity': quantity,
            'amount': total_cost,
        })

    def _execute_sell(self, code: str, price: float, date: pd.Timestamp):
        """执行卖出"""
        if code not in self.positions or self.positions[code]['quantity'] <= 0:
            return  # 未持仓

        position = self.positions[code]
        quantity = position['quantity']
        avg_price = position['avg_price']

        # 计算手续费
        amount = quantity * price
        commission = amount * self.fees.get('commission', 0.0003)
        stamp_duty = amount * self.fees.get('stamp_duty', 0.001)
        transfer_fee = amount * self.fees.get('transfer_fee', 0.00002)
        total_fee = commission + stamp_duty + transfer_fee

        # 执行卖出
        net_amount = amount - total_fee
        self.cash += net_amount

        # 记录盈亏
        profit = (price - avg_price) * quantity
        self.trades.append({
            'date': date,
            'code': code,
            'action': 'sell',
            'price': price,
            'quantity': quantity,
            'amount': amount,
            'profit': profit,
            'profit_pct': (price - avg_price) / avg_price,
        })

        # 清空持仓
        del self.positions[code]

    def _check_risk_management(self, code: str, price: float, date: pd.Timestamp):
        """止损止盈检查"""
        if code not in self.positions:
            return

        position = self.positions[code]
        avg_price = position['avg_price']
        profit_pct = (price - avg_price) / avg_price

        stop_loss = self.config.get('stop_loss', -0.08)
        take_profit = self.config.get('take_profit', 0.15)

        if profit_pct <= stop_loss or profit_pct >= take_profit:
            self._execute_sell(code, price, date)

    def _calculate_equity(self, stock_data: Dict[str, pd.DataFrame], date: pd.Timestamp) -> float:
        """计算总权益"""
        equity = self.cash

        for code, position in self.positions.items():
            if code in stock_data and date in stock_data[code].index:
                price = stock_data[code].loc[date, 'close']
                equity += position['quantity'] * price

        return equity

    def _generate_report(self, trading_dates: List[pd.Timestamp]) -> Dict:
        """生成回测报告"""
        if not self.equity_curve:
            return {"error": "无回测数据"}

        equity_df = pd.DataFrame(self.equity_curve)
        equity_df = equity_df.set_index('date')

        # 基本指标
        final_equity = equity_df['equity'].iloc[-1]
        total_return = (final_equity - self.init_cash) / self.init_cash

        # 年化收益率
        years = len(trading_dates) / 252  # 假设每年252个交易日
        annual_return = (final_equity / self.init_cash) ** (1 / years) - 1

        # 每日收益率
        daily_returns = equity_df['equity'].pct_change().dropna()

        # 夏普比率
        sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0

        # 最大回撤
        cum_returns = (1 + daily_returns).cumprod()
        running_max = cum_returns.expanding().max()
        drawdown = (cum_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        # 交易统计
        trade_df = pd.DataFrame(self.trades)
        if not trade_df.empty:
            sell_trades = trade_df[trade_df['action'] == 'sell']
            if not sell_trades.empty:
                win_rate = (sell_trades['profit'] > 0).sum() / len(sell_trades)
                avg_profit = sell_trades['profit_pct'].mean()
                total_trades = len(sell_trades)
            else:
                win_rate = 0
                avg_profit = 0
                total_trades = 0
        else:
            win_rate = 0
            avg_profit = 0
            total_trades = 0

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'total_trades': total_trades,
            'final_equity': final_equity,
            'equity_curve': equity_df,
            'trades': trade_df,
        }


def run_simple_backtest(codes: List[str], weights: Optional[Dict] = None) -> Dict:
    """便捷函数：运行简单回测"""
    engine = AStockBacktestEngine()
    return engine.run_backtest(codes, "2023-01-01", "2026-03-10", weights)