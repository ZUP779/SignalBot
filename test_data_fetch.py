#!/usr/bin/env python3
"""测试数据获取功能"""

import sys
import logging
from stock_fetcher_historical import HistoricalDataFetcher

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_historical_data():
    """测试历史数据获取"""
    fetcher = HistoricalDataFetcher()
    
    # 测试A股数据
    print("🔍 测试获取A股历史数据...")
    test_codes = ["000001", "600519"]
    
    for code in test_codes:
        print(f"\n📊 获取 {code} 的历史数据...")
        data = fetcher.get_historical_data(code, days=10)
        
        if data and len(data) > 0:
            print(f"✅ 成功获取 {len(data)} 条数据")
            print(f"   最新数据: {data[-1]}")
        else:
            print("❌ 获取失败")
    
    # 测试港股数据
    print("\n🔍 测试获取港股历史数据...")
    hk_codes = ["00700"]
    
    for code in hk_codes:
        print(f"\n📊 获取 {code} 的历史数据...")
        data = fetcher.get_historical_data(code, days=10)
        
        if data and len(data) > 0:
            print(f"✅ 成功获取 {len(data)} 条数据")
            print(f"   最新数据: {data[-1]}")
        else:
            print("❌ 获取失败")

if __name__ == "__main__":
    test_historical_data()