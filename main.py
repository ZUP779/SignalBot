#!/usr/bin/env python3
import logging
import schedule
import time
import argparse
from datetime import datetime
from stock_fetcher import StockFetcher
from wechat_notifier import WeChatNotifier
from stock_manager import StockManager
from signal_detector import SignalDetector
from stock_screener import StockScreener, ScreenerCriteria
from market_hours import MarketHours
from config import LOG_LEVEL, LOG_FILE, UPDATE_INTERVAL_HOURS, ALWAYS_SEND_REPORT, SEND_SIGNAL_ALERTS, CHECK_MARKET_HOURS

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def monitor_stocks():
    """SignalBot 智能监控股票并发送信号通知"""
    logger = logging.getLogger(__name__)
    logger.info("🤖 SignalBot 开始智能监控任务")
    
    try:
        # 初始化组件
        stock_manager = StockManager()
        stock_fetcher = StockFetcher()
        notifier = WeChatNotifier()
        signal_detector = SignalDetector()
        market_hours = MarketHours()
        
        # 获取需要监控的股票代码
        all_stock_codes = stock_manager.get_active_stocks()
        
        if not all_stock_codes:
            logger.warning("没有需要监控的股票代码")
            return
        
        # 根据配置决定是否检查开市时间
        if CHECK_MARKET_HOURS:
            # 检查是否有任何市场开市
            if not market_hours.should_send_notification(all_stock_codes):
                # 获取市场状态信息
                a_stock_status = market_hours.get_market_status_message('A股')
                hk_stock_status = market_hours.get_market_status_message('港股')
                logger.info(f"📊 市场状态检查: {a_stock_status}, {hk_stock_status}")
                logger.info("🔕 所有相关市场均已休市，跳过本次监控")
                return
            
            # 过滤出开市的股票代码
            filtered_codes = market_hours.get_filtered_stock_codes(all_stock_codes)
            stock_codes = []
            for market, codes in filtered_codes.items():
                if codes:
                    logger.info(f"🟢 {market}开市中，监控 {len(codes)} 只股票: {codes}")
                    stock_codes.extend(codes)
            
            if not stock_codes:
                logger.info("📊 虽有股票代码，但相关市场均已休市，跳过本次监控")
                return
            
            logger.info(f"🎯 开始监控 {len(stock_codes)} 只开市股票: {stock_codes}")
        else:
            # 不检查开市时间，监控所有股票
            stock_codes = all_stock_codes
            logger.info(f"🎯 开始监控 {len(stock_codes)} 只股票 (未启用开市时间检查): {stock_codes}")
        
        # 获取股票数据
        stock_data = stock_fetcher.get_stock_data(stock_codes)
        
        if not stock_data:
            logger.warning("未获取到任何股票数据")
            return
        
        # 获取历史数据用于信号检测
        historical_data = stock_manager.get_historical_volumes(stock_codes)
        
        # 检测信号
        signals = signal_detector.detect_signals(stock_data, historical_data)
        
        # 保存历史数据
        for code, data in stock_data.items():
            stock_manager.save_stock_history(
                code, 
                data['current_price'], 
                data['change_percent'], 
                data['volume']
            )
            
            # 更新股票名称（如果数据库中没有）
            if data.get('name'):
                stock_manager.update_stock_info(code, data['name'])
        
        # 根据配置决定推送策略
        report_sent = False
        
        # 发送常规股票数据报告（保持原有格式）
        if ALWAYS_SEND_REPORT:
            success = notifier.send_stock_report(stock_data)
            report_sent = success
            if success:
                logger.info(f"📊 发送常规监控报告: {len(stock_data)} 只股票")
        
        # 如果检测到重要信号，发送信号预警
        if SEND_SIGNAL_ALERTS and signal_detector.should_notify(signals):
            signal_message = signal_detector.format_signals_for_notification(signals, stock_data)
            signal_sent = notifier.send_signal_alert(signal_message)
            if signal_sent:
                logger.info(f"🚨 发送信号预警: {len(signals)} 只股票有重要信号")
        
        # 如果既不发送常规报告，也没有信号，则记录日志
        if not ALWAYS_SEND_REPORT and not signal_detector.should_notify(signals):
            logger.info(f"📊 监控完成，未检测到重要信号，未发送通知 ({len(stock_data)} 只股票)")
        elif report_sent or signal_detector.should_notify(signals):
            logger.info(f"✅ SignalBot 任务完成")
        else:
            logger.error("❌ 通知发送失败")
            
    except Exception as e:
        logger.error(f"SignalBot 监控任务执行失败: {e}")

def add_stock_command(code: str, name: str = ""):
    """添加股票命令"""
    print(f"🔍 正在添加股票: {code}")
    if not name:
        print("📡 正在自动获取股票名称...")
    
    manager = StockManager()
    success = manager.add_stock(code, name)
    
    if success:
        # 获取添加后的股票信息以显示完整信息
        stocks = manager.list_stocks()
        added_stock = next((s for s in stocks if s['code'] == code), None)
        if added_stock:
            display_name = added_stock['name'] if added_stock['name'] != '未知' else '(未获取到名称)'
            print(f"✅ 成功添加股票: {code} {display_name} [{added_stock['market']}]")
        else:
            print(f"✅ 成功添加股票: {code}")
    else:
        print(f"❌ 添加股票失败: {code}")

def remove_stock_command(code: str):
    """移除股票命令"""
    manager = StockManager()
    success = manager.remove_stock(code)
    if success:
        print(f"✅ 成功移除股票: {code}")
    else:
        print(f"❌ 移除股票失败: {code}")

def list_stocks_command():
    """列出股票命令"""
    manager = StockManager()
    stocks = manager.list_stocks()
    
    if not stocks:
        print("📋 暂无股票代码")
        return
    
    print(f"📋 股票列表 (共 {len(stocks)} 只):")
    print("-" * 60)
    
    for stock in stocks:
        status = "✅" if stock['is_active'] else "❌"
        print(f"{status} {stock['code']} | {stock['name']} | {stock['market']} | {stock['added_time']}")

def update_stock_names_command():
    """更新所有股票名称"""
    print("🔄 正在更新所有股票名称...")
    manager = StockManager()
    stocks = manager.list_stocks()
    
    updated_count = 0
    for stock in stocks:
        if stock['is_active'] and (not stock['name'] or stock['name'] == '未知'):
            print(f"📡 正在获取 {stock['code']} 的名称...")
            fetcher = StockFetcher()
            name = fetcher.get_stock_name(stock['code'])
            if name:
                success = manager.update_stock_info(stock['code'], name)
                if success:
                    print(f"✅ 更新成功: {stock['code']} -> {name}")
                    updated_count += 1
                else:
                    print(f"❌ 更新失败: {stock['code']}")
            else:
                print(f"⚠️  无法获取 {stock['code']} 的名称")
    
    print(f"🎉 更新完成，共更新了 {updated_count} 只股票的名称")

def test_notification():
    """测试通知"""
    notifier = WeChatNotifier()
    success = notifier.send_test_message()
    if success:
        print("✅ 测试通知发送成功")
    else:
        print("❌ 测试通知发送失败")

def run_once():
    """立即执行一次监控"""
    print("🚀 立即执行股票监控...")
    monitor_stocks()

def screen_stocks_command(market: str = "A股", top_n: int = 10):
    """智能筛选股票命令"""
    print(f"🎯 开始智能筛选{market}优质股票...")
    
    try:
        screener = StockScreener()
        results = screener.get_recommended_stocks(market, top_n)
        
        if not results:
            print("❌ 未找到符合条件的股票")
            return
        
        print(f"\n📊 智能筛选结果 (共{len(results)}只股票):")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.name}({result.code})")
            print(f"   📊 综合评分: {result.score:.1f}/100")
            print(f"   🎯 投资建议: {result.recommendation}")
            print(f"   ⚠️  风险等级: {result.risk_level}")
            print(f"   ✅ 符合条件: {', '.join(result.criteria_met[:3])}")
            print(f"   💡 推荐理由: {result.reason}")
        
        print("\n" + "=" * 80)
        print("⚠️ 以上分析仅供参考，投资有风险，决策需谨慎！")
        
        # 询问是否添加到监控列表
        if results:
            print(f"\n💡 发现 {len(results)} 只优质股票，是否添加到监控列表？")
            choice = input("输入要添加的股票序号(用逗号分隔，如1,3,5)，或按回车跳过: ").strip()
            
            if choice:
                try:
                    indices = [int(x.strip()) - 1 for x in choice.split(',')]
                    manager = StockManager()
                    added_count = 0
                    
                    for idx in indices:
                        if 0 <= idx < len(results):
                            result = results[idx]
                            success = manager.add_stock(result.code, result.name)
                            if success:
                                print(f"✅ 已添加: {result.name}({result.code})")
                                added_count += 1
                            else:
                                print(f"❌ 添加失败: {result.name}({result.code})")
                    
                    print(f"\n🎉 成功添加 {added_count} 只股票到监控列表")
                except ValueError:
                    print("❌ 输入格式错误")
        
    except Exception as e:
        print(f"❌ 股票筛选失败: {e}")

def analyze_stock_command(code: str):
    """分析单只股票命令"""
    print(f"🔍 正在分析股票: {code}")
    
    try:
        screener = StockScreener()
        
        # 获取股票基础数据
        basic_data = screener._get_basic_data(code)
        if not basic_data:
            print(f"❌ 无法获取股票 {code} 的数据")
            return
        
        # 获取技术指标数据
        technical_data = screener._get_technical_data(code)
        
        # 评估股票
        criteria = list(ScreenerCriteria)
        result = screener._evaluate_stock(code, criteria)
        
        if not result:
            print(f"❌ 无法分析股票 {code}")
            return
        
        print(f"\n📊 {result.name}({result.code}) 详细分析报告")
        print("=" * 60)
        
        # 基本信息
        print(f"💰 当前价格: {basic_data.get('currency', '¥')}{basic_data.get('current_price', 0):.2f}")
        print(f"📈 涨跌幅: {basic_data.get('change_percent', 0):+.2f}%")
        print(f"📊 成交量: {basic_data.get('volume', 0):,}")
        print(f"🏢 市场: {basic_data.get('market', '未知')}")
        
        # 评估结果
        print(f"\n🎯 综合评分: {result.score:.1f}/100")
        print(f"📋 投资建议: {result.recommendation}")
        print(f"⚠️ 风险等级: {result.risk_level}")
        print(f"💡 推荐理由: {result.reason}")
        
        # 符合的筛选条件
        if result.criteria_met:
            print(f"\n✅ 符合筛选条件:")
            for criterion in result.criteria_met:
                print(f"   • {criterion}")
        
        # 技术指标
        if technical_data:
            print(f"\n📊 技术指标:")
            print(f"   RSI: {technical_data.get('rsi', 0):.1f}")
            print(f"   MACD: {'看涨' if technical_data.get('macd_signal', 0) > 0 else '看跌'}")
            print(f"   MA5: {technical_data.get('ma5', 0):.2f}")
            print(f"   MA20: {technical_data.get('ma20', 0):.2f}")
            print(f"   量比: {technical_data.get('volume_ratio', 0):.1f}")
        
        print("\n" + "=" * 60)
        print("⚠️ 以上分析仅供参考，投资有风险，决策需谨慎！")
        
    except Exception as e:
        print(f"❌ 分析股票失败: {e}")

def market_status_command():
    """查看市场状态命令"""
    print("📊 正在检查市场状态...")
    
    try:
        market_hours = MarketHours()
        
        # 检查A股状态
        a_stock_status = market_hours.get_market_status_message('A股')
        print(f"\n{a_stock_status}")
        
        # 检查港股状态
        hk_stock_status = market_hours.get_market_status_message('港股')
        print(f"{hk_stock_status}")
        
        # 检查监控的股票
        stock_manager = StockManager()
        stock_codes = stock_manager.get_active_stocks()
        
        if stock_codes:
            print(f"\n📋 当前监控的股票 ({len(stock_codes)} 只):")
            
            # 按市场分类显示
            filtered_codes = market_hours.get_filtered_stock_codes(stock_codes)
            
            for market, codes in filtered_codes.items():
                if codes:
                    market_open = market_hours.is_market_open(market)
                    status_icon = "🟢" if market_open else "🔴"
                    print(f"  {status_icon} {market}: {len(codes)} 只股票 - {', '.join(codes)}")
            
            # 显示休市的股票
            all_filtered = []
            for codes in filtered_codes.values():
                all_filtered.extend(codes)
            
            closed_stocks = [code for code in stock_codes if code not in all_filtered]
            if closed_stocks:
                print(f"  🔴 休市股票: {len(closed_stocks)} 只 - {', '.join(closed_stocks)}")
            
            # 总结
            active_count = len(all_filtered)
            if active_count > 0:
                print(f"\n✅ 当前有 {active_count} 只股票的市场正在开市")
            else:
                print(f"\n🔕 当前所有监控股票的市场均已休市")
        else:
            print("\n📋 暂无监控的股票")
        
    except Exception as e:
        print(f"❌ 检查市场状态失败: {e}")

def start_scheduler():
    """启动定时任务"""
    logger = logging.getLogger(__name__)
    logger.info(f"启动股票监控定时任务，每 {UPDATE_INTERVAL_HOURS} 小时执行一次")
    
    # 设置定时任务
    schedule.every(UPDATE_INTERVAL_HOURS).hours.do(monitor_stocks)
    
    print(f"📅 股票监控已启动，每 {UPDATE_INTERVAL_HOURS} 小时执行一次")
    print("按 Ctrl+C 停止监控")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("用户停止了股票监控")
        print("\n👋 股票监控已停止")

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description='股票监控系统')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加股票
    add_parser = subparsers.add_parser('add', help='添加股票代码')
    add_parser.add_argument('code', help='股票代码')
    add_parser.add_argument('--name', default='', help='股票名称')
    
    # 移除股票
    remove_parser = subparsers.add_parser('remove', help='移除股票代码')
    remove_parser.add_argument('code', help='股票代码')
    
    # 列出股票
    subparsers.add_parser('list', help='列出所有股票')
    
    # 更新股票名称
    subparsers.add_parser('update-names', help='更新所有股票名称')
    
    # 测试通知
    subparsers.add_parser('test', help='测试企业微信通知')
    
    # 立即执行
    subparsers.add_parser('run', help='立即执行一次监控')
    
    # 启动定时任务
    subparsers.add_parser('start', help='启动定时监控')
    
    # 智能筛选股票
    screen_parser = subparsers.add_parser('screen', help='智能筛选优质股票')
    screen_parser.add_argument('--market', default='A股', choices=['A股', '港股'], help='市场类型')
    screen_parser.add_argument('--top', type=int, default=10, help='显示前N只股票')
    
    # 分析单只股票
    analyze_parser = subparsers.add_parser('analyze', help='分析单只股票')
    analyze_parser.add_argument('code', help='股票代码')
    
    # 查看市场状态
    subparsers.add_parser('status', help='查看市场开市状态')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        add_stock_command(args.code, args.name)
    elif args.command == 'remove':
        remove_stock_command(args.code)
    elif args.command == 'list':
        list_stocks_command()
    elif args.command == 'update-names':
        update_stock_names_command()
    elif args.command == 'test':
        test_notification()
    elif args.command == 'run':
        run_once()
    elif args.command == 'start':
        start_scheduler()
    elif args.command == 'screen':
        screen_stocks_command(args.market, args.top)
    elif args.command == 'analyze':
        analyze_stock_command(args.code)
    elif args.command == 'status':
        market_status_command()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()