#!/usr/bin/env python3
"""
调试市场开市时间
"""
from datetime import datetime, time
import pytz
from market_hours import MarketHours

def debug_market_hours():
    """调试市场开市时间"""
    print("🔍 调试市场开市时间\n")
    
    market_hours = MarketHours()
    china_tz = pytz.timezone('Asia/Shanghai')
    
    # 检查今天是否为交易日
    now = datetime.now()
    beijing_now = china_tz.localize(now)
    
    print(f"当前时间: {now}")
    print(f"北京时间: {beijing_now}")
    print(f"星期几: {beijing_now.weekday()} (0=周一, 6=周日)")
    print(f"日期字符串: {beijing_now.strftime('%Y-%m-%d')}")
    
    # 检查是否为交易日
    is_a_trading_day = market_hours._is_trading_day(beijing_now, 'A股')
    is_hk_trading_day = market_hours._is_trading_day(beijing_now, '港股')
    
    print(f"A股是否为交易日: {is_a_trading_day}")
    print(f"港股是否为交易日: {is_hk_trading_day}")
    
    # 检查节假日
    date_str = beijing_now.strftime('%Y-%m-%d')
    print(f"是否在A股节假日列表: {date_str in market_hours.a_stock_holidays}")
    print(f"是否在港股节假日列表: {date_str in market_hours.hk_stock_holidays}")
    
    # 测试特定时间的开市状态
    test_times = [
        beijing_now.replace(hour=10, minute=0, second=0, microsecond=0),
        beijing_now.replace(hour=14, minute=0, second=0, microsecond=0),
        beijing_now.replace(hour=12, minute=0, second=0, microsecond=0),
        beijing_now.replace(hour=16, minute=0, second=0, microsecond=0),
    ]
    
    print("\n时间点测试:")
    for test_time in test_times:
        a_open = market_hours.is_market_open('A股', test_time)
        hk_open = market_hours.is_market_open('港股', test_time)
        print(f"{test_time.strftime('%H:%M')}: A股={a_open}, 港股={hk_open}")
    
    # 测试股票代码识别
    print("\n股票代码识别测试:")
    test_codes = ['000001', '600036', '00700', '09988']
    for code in test_codes:
        is_a = market_hours._is_a_stock_code(code)
        is_hk = market_hours._is_hk_stock_code(code)
        print(f"{code}: A股={is_a}, 港股={is_hk}")
    
    # 测试过滤功能
    print("\n过滤功能测试:")
    filtered = market_hours.get_filtered_stock_codes(test_codes)
    print(f"过滤结果: {filtered}")
    
    # 测试通知判断
    should_notify = market_hours.should_send_notification(test_codes)
    print(f"是否应该通知: {should_notify}")

if __name__ == '__main__':
    debug_market_hours()