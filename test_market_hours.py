#!/usr/bin/env python3
"""
测试市场开市时间功能
"""
import sys
from datetime import datetime, time
import pytz
from market_hours import MarketHours

def test_market_hours():
    """测试市场开市时间功能"""
    print("🧪 测试市场开市时间功能\n")
    
    market_hours = MarketHours()
    
    # 测试当前时间
    print("📅 当前时间测试:")
    now = datetime.now()
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试A股
    a_stock_open = market_hours.is_market_open('A股')
    print(f"A股开市状态: {'🟢 开市' if a_stock_open else '🔴 休市'}")
    
    # 测试港股
    hk_stock_open = market_hours.is_market_open('港股')
    print(f"港股开市状态: {'🟢 开市' if hk_stock_open else '🔴 休市'}")
    
    print()
    
    # 测试状态消息
    print("📊 市场状态消息:")
    print(market_hours.get_market_status_message('A股'))
    print(market_hours.get_market_status_message('港股'))
    
    print()
    
    # 测试股票代码分类
    print("🏷️ 股票代码分类测试:")
    test_codes = ['000001', 'sh600000', 'sz000002', 'hk00700', '00700', 'us_aapl']
    
    for code in test_codes:
        is_a_stock = market_hours._is_a_stock_code(code)
        is_hk_stock = market_hours._is_hk_stock_code(code)
        print(f"{code}: A股={is_a_stock}, 港股={is_hk_stock}")
    
    print()
    
    # 测试通知判断
    print("🔔 通知判断测试:")
    should_notify = market_hours.should_send_notification(test_codes)
    print(f"是否应该发送通知: {'✅ 是' if should_notify else '❌ 否'}")
    
    # 测试过滤股票代码
    filtered = market_hours.get_filtered_stock_codes(test_codes)
    print(f"过滤后的股票代码: {filtered}")
    
    print()
    
    # 测试特定时间点
    print("⏰ 特定时间点测试:")
    
    # 测试A股开市时间
    china_tz = pytz.timezone('Asia/Shanghai')
    
    test_times = [
        # A股开市时间
        china_tz.localize(datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)),  # 上午开市
        china_tz.localize(datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)),  # 下午开市
        china_tz.localize(datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)),  # 午休
        china_tz.localize(datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)),  # 收市后
    ]
    
    for test_time in test_times:
        a_open = market_hours.is_market_open('A股', test_time)
        hk_open = market_hours.is_market_open('港股', test_time)
        print(f"{test_time.strftime('%H:%M')}: A股={'🟢' if a_open else '🔴'}, 港股={'🟢' if hk_open else '🔴'}")

def test_next_trading_session():
    """测试下一个交易时段"""
    print("\n🔮 下一个交易时段测试:")
    
    market_hours = MarketHours()
    
    try:
        # 测试A股
        next_start, next_end = market_hours.get_next_trading_session('A股')
        print(f"A股下一个交易时段: {next_start.strftime('%Y-%m-%d %H:%M')} - {next_end.strftime('%H:%M')}")
    except Exception as e:
        print(f"A股下一个交易时段获取失败: {e}")
    
    try:
        # 测试港股
        next_start, next_end = market_hours.get_next_trading_session('港股')
        print(f"港股下一个交易时段: {next_start.strftime('%Y-%m-%d %H:%M')} - {next_end.strftime('%H:%M')}")
    except Exception as e:
        print(f"港股下一个交易时段获取失败: {e}")

if __name__ == '__main__':
    try:
        test_market_hours()
        test_next_trading_session()
        print("\n✅ 测试完成")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)