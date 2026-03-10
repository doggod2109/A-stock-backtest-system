# -*- coding: utf-8 -*-
"""
回测报告生成器
保存回测结果到文件（JSON、Excel、HTML）
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class ReportGenerator:
    """报告生成器"""

    def __init__(self, output_dir: str = None):
        """
        初始化报告生成器

        Args:
            output_dir: 输出目录，如果为None则自动生成带时间戳的目录
        """
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"backtest_{timestamp}"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, result: Dict, config: Dict, trades_df: pd.DataFrame = None):
        """
        生成完整回测报告

        Args:
            result: 回测结果
            config: 回测配置
            trades_df: 交易明细DataFrame
        """
        print(f"💾 正在生成回测报告...")

        # 1. 保存JSON报告
        self._save_json_report(result, config)

        # 2. 保存Excel交易明细
        if trades_df is not None and not trades_df.empty:
            self._save_excel_trades(trades_df, config)

        # 3. 生成HTML可视化报告
        self._generate_html_report(result, config, trades_df)

        print(f"✅ 报告已保存到: {self.output_dir.absolute()}")

    def _save_json_report(self, result: Dict, config: Dict):
        """保存JSON格式报告"""
        report_data = {
            "backtest_time": datetime.now().isoformat(),
            "config": {
                "stocks": config.get('codes', []),
                "start_date": config.get('start_date', ''),
                "end_date": config.get('end_date', ''),
                "init_cash": config.get('init_cash', 0),
                "position_size": config.get('position_size', 0),
                "max_positions": config.get('max_positions', 0),
                "weights": config.get('weights', {}),
                "buy_threshold": config.get('buy_threshold', 0),
                "sell_threshold": config.get('sell_threshold', 0),
                "stop_loss": config.get('stop_loss', 0),
                "take_profit": config.get('take_profit', 0),
            },
            "results": {
                "total_return": result.get('total_return', 0),
                "annual_return": result.get('annual_return', 0),
                "sharpe_ratio": result.get('sharpe_ratio', 0),
                "max_drawdown": result.get('max_drawdown', 0),
                "win_rate": result.get('win_rate', 0),
                "avg_profit": result.get('avg_profit', 0),
                "total_trades": result.get('total_trades', 0),
                "final_equity": result.get('final_equity', 0),
            }
        }

        json_file = self.output_dir / "report.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def _save_excel_trades(self, trades_df: pd.DataFrame, config: Dict):
        """保存Excel格式交易明细"""
        excel_file = self.output_dir / "trades.xlsx"

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 交易明细
            trades_df.to_excel(writer, sheet_name='交易明细', index=False)

            # 配置信息
            config_data = {
                "配置项": ["股票代码", "时间范围", "初始资金", "单只仓位", "最大持仓",
                          "买入阈值", "卖出阈值", "止损", "止盈"],
                "值": [
                    ', '.join(config.get('codes', [])),
                    f"{config.get('start_date', '')} ~ {config.get('end_date', '')}",
                    f"¥{config.get('init_cash', 0):,}",
                    f"{config.get('position_size', 0) * 100:.0f}%",
                    config.get('max_positions', 0),
                    config.get('buy_threshold', 0),
                    config.get('sell_threshold', 0),
                    f"{config.get('stop_loss', 0) * 100:.0f}%",
                    f"{config.get('take_profit', 0) * 100:.0f}%"
                ]
            }
            pd.DataFrame(config_data).to_excel(writer, sheet_name='配置', index=False)

    def _generate_html_report(self, result: Dict, config: Dict, trades_df: pd.DataFrame = None):
        """生成HTML可视化报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>回测报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-card.good {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .metric-card.bad {{
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }}
        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .config-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .config-label {{
            font-weight: bold;
            color: #555;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            margin: 2px;
        }}
        .badge-buy {{
            background-color: #4CAF50;
            color: white;
        }}
        .badge-sell {{
            background-color: #f44336;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 A股回测报告</h1>
        <p style="color: #666;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>📋 回测配置</h2>
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
            <div class="config-item">
                <span class="config-label">股票代码</span>
                <span>{', '.join(config.get('codes', []))}</span>
            </div>
            <div class="config-item">
                <span class="config-label">时间范围</span>
                <span>{config.get('start_date', '')} ~ {config.get('end_date', '')}</span>
            </div>
            <div class="config-item">
                <span class="config-label">初始资金</span>
                <span>¥{config.get('init_cash', 0):,}</span>
            </div>
            <div class="config-item">
                <span class="config-label">单只仓位</span>
                <span>{config.get('position_size', 0) * 100:.0f}%</span>
            </div>
            <div class="config-item">
                <span class="config-label">最大持仓</span>
                <span>{config.get('max_positions', 0)} 只</span>
            </div>
        </div>

        <h2>📈 回测结果</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">总收益率</div>
                <div class="metric-value">{result.get('total_return', 0):.2%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">年化收益率</div>
                <div class="metric-value">{result.get('annual_return', 0):.2%}</div>
            </div>
            <div class="metric-card {'good' if result.get('sharpe_ratio', 0) > 2 else ''}">
                <div class="metric-label">夏普比率</div>
                <div class="metric-value">{result.get('sharpe_ratio', 0):.2f}</div>
            </div>
            <div class="metric-card {'bad' if result.get('max_drawdown', 0) < -0.2 else ''}">
                <div class="metric-label">最大回撤</div>
                <div class="metric-value">{result.get('max_drawdown', 0):.2%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">胜率</div>
                <div class="metric-value">{result.get('win_rate', 0):.2%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">交易次数</div>
                <div class="metric-value">{result.get('total_trades', 0)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">平均盈亏</div>
                <div class="metric-value">{result.get('avg_profit', 0):.2%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">最终权益</div>
                <div class="metric-value">¥{result.get('final_equity', 0):,.2f}</div>
            </div>
        </div>
"""

        # 添加交易明细表格
        if trades_df is not None and not trades_df.empty:
            html += """
        <h2>💰 交易明细</h2>
        <table>
            <thead>
                <tr>
                    <th>日期</th>
                    <th>代码</th>
                    <th>操作</th>
                    <th>价格</th>
                    <th>数量</th>
                    <th>金额</th>
"""

            # 添加盈利列（如果有）
            if 'profit' in trades_df.columns:
                html += "                    <th>盈利</th>\n"

            html += """                </tr>
            </thead>
            <tbody>
"""

            for _, row in trades_df.iterrows():
                action_badge = f'<span class="badge badge-buy">买入</span>' if row['action'] == 'buy' else f'<span class="badge badge-sell">卖出</span>'
                html += f"""                <tr>
                    <td>{row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else row['date']}</td>
                    <td>{row['code']}</td>
                    <td>{action_badge}</td>
                    <td>¥{row['price']:.3f}</td>
                    <td>{int(row['quantity']):,}</td>
                    <td>¥{row['amount']:,.2f}</td>
"""

                if 'profit' in trades_df.columns and pd.notna(row['profit']):
                    profit_color = 'green' if row['profit'] > 0 else 'red'
                    html += f"""                    <td style="color: {profit_color};">¥{row['profit']:,.2f} ({row.get('profit_pct', 0):.2%})</td>
"""

                html += """                </tr>
"""

            html += """            </tbody>
        </table>
"""

        html += """
    </div>
</body>
</html>
"""

        html_file = self.output_dir / "report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)