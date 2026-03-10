#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理配置模块
为akshare等需要访问外网的库提供代理支持
"""
import os

def get_proxies():
    """获取代理配置"""
    proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy') or os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    if proxy:
        return {
            'http': proxy,
            'https': proxy
        }
    return None

def setup_akshare_proxy():
    """为akshare设置代理"""
    proxies = get_proxies()
    if proxies:
        import akshare as ak
        try:
            # akshare使用requests，可以通过环境变量设置
            os.environ['HTTP_PROXY'] = proxies['http']
            os.environ['HTTPS_PROXY'] = proxies['https']
            return True
        except:
            return False
    return False

if __name__ == '__main__':
    proxies = get_proxies()
    if proxies:
        print(f"代理已配置: {proxies['http']}")
    else:
        print("未找到代理配置")
