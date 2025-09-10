#!/usr/bin/env python3
"""
测试混合市场开市时间场景
"""
from datetime import datetime, time
import pytz
from market_hours import MarketHours

def test_mixed_market_scenarios():
    """测试混合市场开市场景"""
    print("🧪 测试混合市场开市场景\n")
    
    market_hours = MarketHours()
    china_tz = pytz.timezone('Asia/Shanghai')
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    
    # 测试股票代码
    mixed_stocks = ['000001', '600036', '00700', '09988']  # A股 + 港股
    a_stocks_only = ['000001', '600036']  # 只有A股
    hk_stocks_only = ['00700', '09988']   # 只有港股
    
    # 测试场景1: A股休市，港股开市（港股12:30-13:00午休时段）
    print("📊 场景1: A股休市，港股开市")
    test_time = china_tz.localize(datetime.now().replace(hour=12, minute=30, second=0, microsecond=0))
    
    a_open = market_hours.is_market_open('A股', test_time)
    hk_open = market_hours.is_market_open('港股', test_time)
    
    print(f"时间: {test_time.strftime('%H:%M')} (北京时间)")
    print(f"A股状态: {'🟢 开市' if a_open else '🔴 休市'}")
    print(f"港股状态: {'🟢 开市' if hk_open else '🔴 休市'}")
    
    # 测试不同股票组合的通知判断
    should_notify_mixed = market_hours.should_send_notification(mixed_stocks)
    should_notify_a = market_hours.should_send_notification(a_stocks_only)
    should_notify_hk = market_hours.should_send_notification(hk_stocks_only)
    
    print(f"混合股票是否推送: {'✅ 是' if should_notify_mixed else '❌ 否'}")
    print(f"只有A股是否推送: {'✅ 是' if should_notify_a else '❌ 否'}")
    print(f"只有港股是否推送: {'✅ 是' if should_notify_hk else '❌ 否'}")
    
    # 过滤股票代码
    filtered = market_hours.get_filtered_stock_codes(mixed_stocks)
    print(f"过滤后的股票: {filtered}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试场景2: A股开市，港股休市（A股14:00，港股已收市）
    print("📊 场景2: A股开市，港股休市")
    test_time2 = china_tz.localize(datetime.now().replace(hour=14, minute=0, second=0, microsecond=0))
    
    a_open2 = market_hours.is_market_open('A股', test_time2)
    hk_open2 = market_hours.is_market_open('港股', test_time2)
    
    print(f"时间: {test_time2.strftime('%H:%M')} (北京时间)")
    print(f"A股状态: {'🟢 开市' if a_open2 else '🔴 休市'}")
    print(f"港股状态: {'🟢 开市' if hk_open2 else '🔴 休市'}")
    
    should_notify_mixed2 = market_hours.should_send_notification(mixed_stocks)
    should_notify_a2 = market_hours.should_send_notification(a_stocks_only)
    should_notify_hk2 = market_hours.should_send_notification(hk_stocks_only)
    
    print(f"混合股票是否推送: {'✅ 是' if should_notify_mixed2 else '❌ 否'}")
    print(f"只有A股是否推送: {'✅ 是' if should_notify_a2 else '❌ 否'}")
    print(f"只有港股是否推送: {'✅ 是' if should_notify_hk2 else '❌ 否'}")
    
    filtered2 = market_hours.get_filtered_stock_codes(mixed_stocks)
    print(f"过滤后的股票: {filtered2}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试场景3: 都开市（上午10:00）
    print("📊 场景3: A股和港股都开市")
    test_time3 = china_tz.localize(datetime.now().replace(hour=10, minute=0, second=0, microsecond=0))
    
    a_open3 = market_hours.is_market_open('A股', test_time3)
    hk_open3 = market_hours.is_market_open('港股', test_time3)
    
    print(f"时间: {test_time3.strftime('%H:%M')} (北京时间)")
    print(f"A股状态: {'🟢 开市' if a_open3 else '🔴 休市'}")
    print(f"港股状态: {'🟢 开市' if hk_open3 else '🔴 休市'}")
    
    should_notify_mixed3 = market_hours.should_send_notification(mixed_stocks)
    should_notify_a3 = market_hours.should_send_notification(a_stocks_only)
    should_notify_hk3 = market_hours.should_send_notification(hk_stocks_only)
    
    print(f"混合股票是否推送: {'✅ 是' if should_notify_mixed3 else '❌ 否'}")
    print(f"只有A股是否推送: {'✅ 是' if should_notify_a3 else '❌ 否'}")
    print(f"只有港股是否推送: {'✅ 是' if should_notify_hk3 else '❌ 否'}")
    
    filtered3 = market_hours.get_filtered_stock_codes(mixed_stocks)
    print(f"过滤后的股票: {filtered3}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试场景4: 都休市（晚上20:00）
    print("📊 场景4: A股和港股都休市")
    test_time4 = china_tz.localize(datetime.now().replace(hour=20, minute=0, second=0, microsecond=0))
    
    a_open4 = market_hours.is_market_open('A股', test_time4)
    hk_open4 = market_hours.is_market_open('港股', test_time4)
    
    print(f"时间: {test_time4.strftime('%H:%M')} (北京时间)")
    print(f"A股状态: {'🟢 开市' if a_open4 else '🔴 休市'}")
    print(f"港股状态: {'🟢 开市' if hk_open4 else '🔴 休市'}")
    
    should_notify_mixed4 = market_hours.should_send_notification(mixed_stocks)
    should_notify_a4 = market_hours.should_send_notification(a_stocks_only)
    should_notify_hk4 = market_hours.should_send_notification(hk_stocks_only)
    
    print(f"混合股票是否推送: {'✅ 是' if should_notify_mixed4 else '❌ 否'}")
    print(f"只有A股是否推送: {'✅ 是' if should_notify_a4 else '❌ 否'}")
    print(f"只有港股是否推送: {'✅ 是' if should_notify_hk4 else '❌ 否'}")
    
    filtered4 = market_hours.get_filtered_stock_codes(mixed_stocks)
    print(f"过滤后的股票: {filtered4}")

if __name__ == '__main__':
    test_mixed_market_scenarios()
    print("\n✅ 混合市场测试完成")