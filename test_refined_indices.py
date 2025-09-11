#!/usr/bin/env python3
"""
测试精简后的指数功能
"""
from stock_fetcher import StockFetcher
from market_hours import MarketHours
from wechat_notifier import WeChatNotifier

def test_refined_indices():
    """测试精简后的指数功能"""
    print("🧪 测试精简后的指数功能\n")
    
    # 精简后的指数列表
    refined_indices = ['sh000300', 'sh000905', 'sh000016', 'HSI']
    
    fetcher = StockFetcher()
    
    print("📊 测试精简指数数据获取:")
    for code in refined_indices:
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

def test_separated_push():
    """测试分离推送功能"""
    print("📱 测试分离推送功能\n")
    
    # 模拟混合数据
    mixed_data = {
        '000001': {
            'name': '平安银行',
            'current_price': 11.83,
            'change': 0.06,
            'change_percent': 0.51,
            'open_price': 11.77,
            'high_price': 11.85,
            'low_price': 11.75,
            'market': 'A股',
            'currency': '¥'
        },
        'sh000300': {
            'name': '沪深300',
            'current_price': 4539.28,
            'change': 95.12,
            'change_percent': 2.14,
            'open_price': 4450.16,
            'high_price': 4545.89,
            'low_price': 4445.23,
            'market': 'A股指数',
            'currency': '点'
        },
        '00700': {
            'name': '腾讯控股',
            'current_price': 629.50,
            'change': -4.00,
            'change_percent': -0.63,
            'open_price': 633.50,
            'high_price': 635.00,
            'low_price': 628.00,
            'market': '港股',
            'currency': 'HK$'
        },
        'HSI': {
            'name': '恒生指数',
            'current_price': 26137.39,
            'change': -62.26,
            'change_percent': -0.24,
            'open_price': 26200.15,
            'high_price': 26250.88,
            'low_price': 26120.45,
            'market': '港股指数',
            'currency': '点'
        }
    }
    
    print("📊 混合数据内容:")
    stocks_count = sum(1 for data in mixed_data.values() if '指数' not in data.get('market', ''))
    indices_count = sum(1 for data in mixed_data.values() if '指数' in data.get('market', ''))
    
    print(f"  股票: {stocks_count} 只")
    print(f"  指数: {indices_count} 个")
    
    for code, data in mixed_data.items():
        print(f"  {data['name']} ({code}) - {data['market']}")
    
    print(f"\n💡 推送逻辑:")
    print(f"  • 股票和指数将分别推送两条消息")
    print(f"  • 股票消息标题: '📈 股票监控'")
    print(f"  • 指数消息标题: '📊 指数监控'")

def test_market_classification():
    """测试市场分类功能"""
    print("\n🏷️ 测试市场分类功能\n")
    
    market_hours = MarketHours()
    
    test_codes = [
        '000001',    # A股股票
        'sh000300',  # A股指数
        'sh000905',  # A股指数
        'sh000016',  # A股指数
        '00700',     # 港股股票
        'HSI',       # 港股指数
    ]
    
    print("📋 代码分类测试:")
    for code in test_codes:
        is_a_stock = market_hours._is_a_stock_code(code)
        is_hk_stock = market_hours._is_hk_stock_code(code)
        is_index = market_hours._is_index_code(code)
        
        if is_index:
            if is_a_stock:
                category = "A股指数"
            elif is_hk_stock:
                category = "港股指数"
            else:
                category = "未知指数"
        else:
            if is_a_stock:
                category = "A股股票"
            elif is_hk_stock:
                category = "港股股票"
            else:
                category = "未知类型"
        
        print(f"  {code:<10}: {category}")
    
    # 测试过滤功能
    filtered = market_hours.get_filtered_stock_codes(test_codes)
    print(f"\n🔍 过滤结果:")
    for market, codes in filtered.items():
        if codes:
            print(f"  {market}: {codes}")

if __name__ == '__main__':
    try:
        test_refined_indices()
        test_separated_push()
        test_market_classification()
        print("\n✅ 所有测试完成")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()