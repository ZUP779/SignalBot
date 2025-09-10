#!/usr/bin/env python3
"""
测试特定的混合市场场景
"""
from datetime import datetime, time
import pytz
from market_hours import MarketHours

def test_specific_mixed_scenarios():
    """测试特定的混合市场场景"""
    print("🧪 测试特定混合市场场景\n")
    
    market_hours = MarketHours()
    china_tz = pytz.timezone('Asia/Shanghai')
    
    # 测试股票代码
    mixed_stocks = ['000001', '600036', '00700', '09988']  # A股 + 港股
    a_stocks_only = ['000001', '600036']  # 只有A股
    hk_stocks_only = ['00700', '09988']   # 只有港股
    
    # 场景1: A股午休时间，港股开市 (12:00)
    print("📊 场景1: A股午休，港股开市 (12:00)")
    test_time1 = china_tz.localize(datetime(2025, 9, 10, 12, 0, 0))
    
    a_open1 = market_hours.is_market_open('A股', test_time1)
    hk_open1 = market_hours.is_market_open('港股', test_time1)
    
    print(f"时间: {test_time1.strftime('%H:%M')} (北京时间)")
    print(f"A股状态: {'🟢 开市' if a_open1 else '🔴 休市'}")
    print(f"港股状态: {'🟢 开市' if hk_open1 else '🔴 休市'}")
    
    should_notify_mixed1 = market_hours.should_send_notification(mixed_stocks, test_time1)
    should_notify_a1 = market_hours.should_send_notification(a_stocks_only, test_time1)
    should_notify_hk1 = market_hours.should_send_notification(hk_stocks_only, test_time1)
    
    print(f"混合股票是否推送: {'✅ 是' if should_notify_mixed1 else '❌ 否'}")
    print(f"只有A股是否推送: {'✅ 是' if should_notify_a1 else '❌ 否'}")
    print(f"只有港股是否推送: {'✅ 是' if should_notify_hk1 else '❌ 否'}")
    
    filtered1 = market_hours.get_filtered_stock_codes(mixed_stocks, test_time1)
    print(f"过滤后的股票: {filtered1}")
    
    print("\n" + "="*60 + "\n")
    
    # 场景2: A股开市，港股休市 (15:30，A股已收市，港股也已收市)
    # 让我们用A股下午开市但港股午休的时间
    print("📊 场景2: A股开市，港股午休 (13:30)")
    test_time2 = china_tz.localize(datetime(2025, 9, 10, 13, 30, 0))
    
    a_open2 = market_hours.is_market_open('A股', test_time2)
    hk_open2 = market_hours.is_market_open('港股', test_time2)
    
    print(f"时间: {test_time2.strftime('%H:%M')} (北京时间)")
    print(f"A股状态: {'🟢 开市' if a_open2 else '🔴 休市'}")
    print(f"港股状态: {'🟢 开市' if hk_open2 else '🔴 休市'}")
    
    should_notify_mixed2 = market_hours.should_send_notification(mixed_stocks, test_time2)
    should_notify_a2 = market_hours.should_send_notification(a_stocks_only, test_time2)
    should_notify_hk2 = market_hours.should_send_notification(hk_stocks_only, test_time2)
    
    print(f"混合股票是否推送: {'✅ 是' if should_notify_mixed2 else '❌ 否'}")
    print(f"只有A股是否推送: {'✅ 是' if should_notify_a2 else '❌ 否'}")
    print(f"只有港股是否推送: {'✅ 是' if should_notify_hk2 else '❌ 否'}")
    
    filtered2 = market_hours.get_filtered_stock_codes(mixed_stocks, test_time2)
    print(f"过滤后的股票: {filtered2}")
    
    print("\n" + "="*60 + "\n")
    
    # 场景3: A股收市，港股开市 (15:30)
    print("📊 场景3: A股收市，港股开市 (15:30)")
    test_time3 = china_tz.localize(datetime(2025, 9, 10, 15, 30, 0))
    
    a_open3 = market_hours.is_market_open('A股', test_time3)
    hk_open3 = market_hours.is_market_open('港股', test_time3)
    
    print(f"时间: {test_time3.strftime('%H:%M')} (北京时间)")
    print(f"A股状态: {'🟢 开市' if a_open3 else '🔴 休市'}")
    print(f"港股状态: {'🟢 开市' if hk_open3 else '🔴 休市'}")
    
    should_notify_mixed3 = market_hours.should_send_notification(mixed_stocks, test_time3)
    should_notify_a3 = market_hours.should_send_notification(a_stocks_only, test_time3)
    should_notify_hk3 = market_hours.should_send_notification(hk_stocks_only, test_time3)
    
    print(f"混合股票是否推送: {'✅ 是' if should_notify_mixed3 else '❌ 否'}")
    print(f"只有A股是否推送: {'✅ 是' if should_notify_a3 else '❌ 否'}")
    print(f"只有港股是否推送: {'✅ 是' if should_notify_hk3 else '❌ 否'}")
    
    filtered3 = market_hours.get_filtered_stock_codes(mixed_stocks, test_time3)
    print(f"过滤后的股票: {filtered3}")
    
    print("\n" + "="*60 + "\n")
    
    # 场景4: 都开市 (10:00)
    print("📊 场景4: A股和港股都开市 (10:00)")
    test_time4 = china_tz.localize(datetime(2025, 9, 10, 10, 0, 0))
    
    a_open4 = market_hours.is_market_open('A股', test_time4)
    hk_open4 = market_hours.is_market_open('港股', test_time4)
    
    print(f"时间: {test_time4.strftime('%H:%M')} (北京时间)")
    print(f"A股状态: {'🟢 开市' if a_open4 else '🔴 休市'}")
    print(f"港股状态: {'🟢 开市' if hk_open4 else '🔴 休市'}")
    
    should_notify_mixed4 = market_hours.should_send_notification(mixed_stocks, test_time4)
    should_notify_a4 = market_hours.should_send_notification(a_stocks_only, test_time4)
    should_notify_hk4 = market_hours.should_send_notification(hk_stocks_only, test_time4)
    
    print(f"混合股票是否推送: {'✅ 是' if should_notify_mixed4 else '❌ 否'}")
    print(f"只有A股是否推送: {'✅ 是' if should_notify_a4 else '❌ 否'}")
    print(f"只有港股是否推送: {'✅ 是' if should_notify_hk4 else '❌ 否'}")
    
    filtered4 = market_hours.get_filtered_stock_codes(mixed_stocks, test_time4)
    print(f"过滤后的股票: {filtered4}")

if __name__ == '__main__':
    test_specific_mixed_scenarios()
    print("\n✅ 特定场景测试完成")