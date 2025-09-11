#!/usr/bin/env python3
"""
测试指数监控功能
"""
from stock_fetcher import StockFetcher
from market_hours import MarketHours

def test_index_data_fetching():
    """测试指数数据获取"""
    print("🧪 测试指数数据获取功能\n")
    
    fetcher = StockFetcher()
    
    # 测试A股指数
    print("📊 测试A股指数:")
    a_indices = ['sh000001', 'sz399001', 'sz399006', 'sh000300']
    
    for code in a_indices:
        print(f"🔍 获取 {code} 数据...")
        data = fetcher.get_stock_data([code])
        
        if data and code in data:
            info = data[code]
            print(f"✅ {info['name']} ({code})")
            print(f"   当前: {info['current_price']:.2f}{info['currency']} ({info['change_percent']:+.2f}%)")
            print(f"   市场: {info['market']}")
        else:
            print(f"❌ 获取失败: {code}")
        print()
    
    # 测试港股指数
    print("📊 测试港股指数:")
    hk_indices = ['HSI', 'HSCEI', 'HSTECH']
    
    for code in hk_indices:
        print(f"🔍 获取 {code} 数据...")
        data = fetcher.get_stock_data([code])
        
        if data and code in data:
            info = data[code]
            print(f"✅ {info['name']} ({code})")
            print(f"   当前: {info['current_price']:.2f}{info['currency']} ({info['change_percent']:+.2f}%)")
            print(f"   市场: {info['market']}")
        else:
            print(f"❌ 获取失败: {code}")
        print()

def test_index_market_hours():
    """测试指数的市场开市时间判断"""
    print("🕐 测试指数市场开市时间判断\n")
    
    market_hours = MarketHours()
    
    # 测试指数代码识别
    test_codes = [
        'sh000001',  # A股指数
        'sz399001',  # A股指数
        'HSI',       # 港股指数
        'HSCEI',     # 港股指数
        '000001',    # A股股票
        '00700',     # 港股股票
    ]
    
    print("📋 代码识别测试:")
    for code in test_codes:
        is_a_stock = market_hours._is_a_stock_code(code)
        is_hk_stock = market_hours._is_hk_stock_code(code)
        is_index = market_hours._is_index_code(code)
        
        print(f"{code:<10}: A股={is_a_stock}, 港股={is_hk_stock}, 指数={is_index}")
    
    print("\n🔔 通知判断测试:")
    should_notify = market_hours.should_send_notification(test_codes)
    print(f"是否应该发送通知: {'✅ 是' if should_notify else '❌ 否'}")
    
    # 测试过滤
    filtered = market_hours.get_filtered_stock_codes(test_codes)
    print(f"过滤后的代码: {filtered}")

def test_mixed_monitoring():
    """测试混合监控（股票+指数）"""
    print("\n🔄 测试混合监控功能\n")
    
    fetcher = StockFetcher()
    
    # 混合代码列表
    mixed_codes = [
        '000001',    # A股股票
        'sh000001',  # A股指数
        '00700',     # 港股股票
        'HSI',       # 港股指数
    ]
    
    print("📊 获取混合数据:")
    data = fetcher.get_stock_data(mixed_codes)
    
    for code, info in data.items():
        print(f"📈 {info['name']} ({code})")
        print(f"   类型: {info['market']}")
        print(f"   当前: {info['current_price']:.2f}{info['currency']} ({info['change_percent']:+.2f}%)")
        print()

if __name__ == '__main__':
    try:
        test_index_data_fetching()
        test_index_market_hours()
        test_mixed_monitoring()
        print("✅ 所有测试完成")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()