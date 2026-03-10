#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/home/admin/.openclaw/skills/stock-daily-analysis-skill')

from scripts.analyzer import analyze_stock
from scripts.notifier import create_report_from_result, format_analysis_report, format_dashboard_report

# 分析159326
print("=== 正在分析 159326 ===\n")
result = analyze_stock('159326')

# 格式化输出
if 'error' not in result:
    report = create_report_from_result(result)
    print(format_dashboard_report([report]))
    print("\n" + format_analysis_report(report))
else:
    print(f"分析失败: {result.get('error', '未知错误')}")