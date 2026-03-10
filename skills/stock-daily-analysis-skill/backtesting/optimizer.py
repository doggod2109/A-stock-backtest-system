# -*- coding: utf-8 -*-
"""
权重优化器
动态权重优化和参数搜索
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from itertools import product
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtesting.engine import AStockBacktestEngine, run_simple_backtest

logger = logging.getLogger(__name__)


class WeightOptimizer:
    """权重优化器"""

    def __init__(self, config: Optional[Dict] = None):
        """初始化优化器"""
        self.config = config or {}
        self.weight_ranges = self.config.get('weight_ranges', {})
        self.objective = self.config.get('objective', 'sharpe_ratio')
        self.method = self.config.get('method', 'grid_search')

    def optimize(
        self,
        codes: List[str],
        start_date: str,
        end_date: str,
        step: int = 5
    ) -> Dict:
        """
        优化权重

        Args:
            codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            step: 权重步长

        Returns:
            优化结果
        """
        logger.info(f"开始权重优化: {len(codes)} 只股票, 步长={step}")

        # 生成权重组合
        weight_combinations = self._generate_weight_combinations(step)
        logger.info(f"生成 {len(weight_combinations)} 组权重组合")

        # 回测所有组合
        results = []
        for i, weights in enumerate(weight_combinations):
            logger.info(f"回测组合 {i+1}/{len(weight_combinations)}: {weights}")

            try:
                result = run_simple_backtest(codes, weights)

                if 'error' not in result:
                    results.append({
                        'weights': weights,
                        'result': result,
                    })
            except Exception as e:
                logger.warning(f"回测失败: {e}")

        logger.info(f"完成 {len(results)} 组有效回测")

        # 选择最优组合
        best_result = self._select_best_result(results)

        logger.info(f"最优组合: {best_result['weights']}")
        logger.info(f"最优 {self.objective}: {best_result['result'][self.objective]:.4f}")

        return best_result

    def _generate_weight_combinations(self, step: int) -> List[Dict[str, int]]:
        """
        生成权重组合

        Args:
            step: 权重步长

        Returns:
            权重组合列表
        """
        # 权重范围
        ranges = {
            'trend': range(10, 51, step),
            'bias': range(5, 36, step),
            'volume': range(5, 26, step),
            'support': range(5, 21, step),
            'macd': range(5, 26, step),
            'rsi': range(5, 21, step),
        }

        # 生成所有组合
        all_combinations = product(
            ranges['trend'],
            ranges['bias'],
            ranges['volume'],
            ranges['support'],
            ranges['macd'],
            ranges['rsi'],
        )

        # 过滤总和为100的组合
        valid_combinations = []
        for combo in all_combinations:
            if sum(combo) == 100:
                valid_combinations.append({
                    'trend': combo[0],
                    'bias': combo[1],
                    'volume': combo[2],
                    'support': combo[3],
                    'macd': combo[4],
                    'rsi': combo[5],
                })

        logger.info(f"总组合数: {len(product(*ranges.values()))}, 有效组合数: {len(valid_combinations)}")

        return valid_combinations

    def _select_best_result(self, results: List[Dict]) -> Dict:
        """
        选择最优结果

        Args:
            results: 回测结果列表

        Returns:
            最优结果
        """
        if not results:
            return {'error': '无有效结果'}

        # 按目标函数排序
        results_sorted = sorted(
            results,
            key=lambda x: x['result'].get(self.objective, 0),
            reverse=True
        )

        return results_sorted[0]

    def compare_weights(
        self,
        codes: List[str],
        weight_sets: List[Dict[str, int]],
        names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        对比不同权重组合

        Args:
            codes: 股票代码列表
            weight_sets: 权重组合列表
            names: 组合名称列表

        Returns:
            对比结果DataFrame
        """
        names = names or [f"组合{i+1}" for i in range(len(weight_sets))]

        results = []
        for i, weights in enumerate(weight_sets):
            logger.info(f"回测 {names[i]}: {weights}")

            try:
                result = run_simple_backtest(codes, weights)

                if 'error' not in result:
                    results.append({
                        'name': names[i],
                        'weights': weights,
                        **result
                    })
            except Exception as e:
                logger.warning(f"回测失败: {e}")

        # 转为DataFrame
        df = pd.DataFrame(results)

        # 选择关键指标
        metrics = ['name', 'total_return', 'annual_return', 'sharpe_ratio',
                   'max_drawdown', 'win_rate', 'total_trades']

        return df[metrics] if not df.empty else df


class WalkForwardAnalyzer:
    """Walk-Forward前向验证"""

    def __init__(self, config: Optional[Dict] = None):
        """初始化"""
        self.config = config or {}
        self.train_size = self.config.get('train_size', 0.7)
        self.test_size = self.config.get('test_size', 0.3)
        self.step = self.config.get('step', 0.2)

    def analyze(
        self,
        codes: List[str],
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Walk-Forward分析

        Args:
            codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            分析结果
        """
        logger.info(f"开始Walk-Forward分析: {start_date} ~ {end_date}")

        # 生成时间窗口
        windows = self._generate_windows(start_date, end_date)

        results = []
        for i, (train_start, train_end, test_start, test_end) in enumerate(windows):
            logger.info(f"窗口 {i+1}/{len(windows)}:")
            logger.info(f"  训练: {train_start} ~ {train_end}")
            logger.info(f"  测试: {test_start} ~ {test_end}")

            # 训练集优化权重
            optimizer = WeightOptimizer(self.config)
            best = optimizer.optimize(codes, train_start, train_end)

            if 'error' not in best:
                # 测试集验证
                test_result = run_simple_backtest(codes, best['weights'])

                if 'error' not in test_result:
                    results.append({
                        'window': i + 1,
                        'train_period': f"{train_start}~{train_end}",
                        'test_period': f"{test_start}~{test_end}",
                        'weights': best['weights'],
                        'train_result': best['result'],
                        'test_result': test_result,
                    })

        # 汇总结果
        summary = self._summarize_walk_forward(results)

        return {
            'windows': results,
            'summary': summary,
        }

    def _generate_windows(
        self,
        start_date: str,
        end_date: str
    ) -> List[Tuple[str, str, str, str]]:
        """
        生成时间窗口

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            时间窗口列表
        """
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        total_days = (end - start).days

        train_days = int(total_days * self.train_size)
        test_days = int(total_days * self.test_size)
        step_days = int(total_days * self.step)

        windows = []
        current_start = start

        while current_start + pd.Timedelta(days=train_days + test_days) <= end:
            train_end = current_start + pd.Timedelta(days=train_days)
            test_start = train_end + pd.Timedelta(days=1)
            test_end = test_start + pd.Timedelta(days=test_days)

            windows.append((
                current_start.strftime('%Y-%m-%d'),
                train_end.strftime('%Y-%m-%d'),
                test_start.strftime('%Y-%m-%d'),
                test_end.strftime('%Y-%m-%d'),
            ))

            current_start += pd.Timedelta(days=step_days)

        return windows

    def _summarize_walk_forward(self, results: List[Dict]) -> Dict:
        """
        汇总Walk-Forward结果

        Args:
            results: 窗口结果列表

        Returns:
            汇总统计
        """
        if not results:
            return {'error': '无结果'}

        # 提取测试集指标
        test_metrics = ['total_return', 'annual_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']

        summary = {}
        for metric in test_metrics:
            values = [r['test_result'].get(metric, 0) for r in results]
            summary[f'avg_{metric}'] = np.mean(values)
            summary[f'std_{metric}'] = np.std(values)
            summary[f'min_{metric}'] = np.min(values)
            summary[f'max_{metric}'] = np.max(values)

        # 计算WFE比率
        avg_sharpe = summary.get('avg_sharpe_ratio', 0)
        wfe = avg_sharpe / np.std([r['test_result'].get('sharpe_ratio', 0) for r in results]) if summary.get('std_sharpe_ratio', 0) > 0 else 0
        summary['wfe_ratio'] = wfe

        return summary


class DynamicWeightManager:
    """动态权重管理器"""

    def __init__(self, config: Optional[Dict] = None):
        """初始化"""
        self.config = config or {}
        self.market_factors = self.config.get('market_factors', {})

    def calculate_market_sentiment(self, market_data: pd.DataFrame) -> str:
        """
        计算市场情绪

        Args:
            market_data: 市场数据

        Returns:
            情绪: bullish, bearish, neutral
        """
        # 这里可以接入市场数据计算
        # 暂时返回中性
        return 'neutral'

    def adjust_weights(
        self,
        base_weights: Dict[str, int],
        market_sentiment: str
    ) -> Dict[str, int]:
        """
        根据市场情绪调整权重

        Args:
            base_weights: 基础权重
            market_sentiment: 市场情绪

        Returns:
            调整后的权重
        """
        weights = base_weights.copy()

        if market_sentiment == 'bullish':
            # 牛市：增加趋势和量能权重
            weights['trend'] = min(weights['trend'] + 10, 50)
            weights['volume'] = min(weights['volume'] + 5, 25)
            weights['bias'] = max(weights['bias'] - 5, 5)
        elif market_sentiment == 'bearish':
            # 熊市：增加支撑和RSI权重
            weights['support'] = min(weights['support'] + 10, 20)
            weights['rsi'] = min(weights['rsi'] + 5, 20)
            weights['trend'] = max(weights['trend'] - 5, 10)

        # 重新归一化
        total = sum(weights.values())
        for key in weights:
            weights[key] = int(weights[key] * 100 / total)

        return weights


def run_weight_optimization(codes: List[str], step: int = 10) -> Dict:
    """便捷函数：运行权重优化"""
    optimizer = WeightOptimizer()
    return optimizer.optimize(codes, "2023-01-01", "2026-03-10", step)