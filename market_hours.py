"""
股票市场开市时间判断模块
支持A股和港股的开市时间检查
"""
import logging
from datetime import datetime, time
from typing import Dict, List, Tuple
import pytz

class MarketHours:
    """股票市场开市时间管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 定义时区
        self.china_tz = pytz.timezone('Asia/Shanghai')
        self.hk_tz = pytz.timezone('Asia/Hong_Kong')
        
        # A股开市时间 (北京时间)
        self.a_stock_sessions = [
            (time(9, 30), time(11, 30)),   # 上午交易时段
            (time(13, 0), time(15, 0))     # 下午交易时段
        ]
        
        # 港股开市时间 (香港时间)
        self.hk_stock_sessions = [
            (time(9, 30), time(12, 0)),    # 上午交易时段
            (time(13, 0), time(16, 0))     # 下午交易时段
        ]
        
        # A股交易日 (周一到周五)
        self.a_stock_weekdays = [0, 1, 2, 3, 4]  # Monday=0, Sunday=6
        
        # 港股交易日 (周一到周五)
        self.hk_stock_weekdays = [0, 1, 2, 3, 4]
        
        # 节假日配置 (可以后续扩展为从API获取)
        # 格式: 'YYYY-MM-DD'
        self.a_stock_holidays = {
            # 2024年节假日 (示例)
            '2024-01-01',  # 元旦
            '2024-02-10', '2024-02-11', '2024-02-12', '2024-02-13', '2024-02-14', '2024-02-15', '2024-02-16', '2024-02-17',  # 春节
            '2024-04-04', '2024-04-05', '2024-04-06',  # 清明节
            '2024-05-01', '2024-05-02', '2024-05-03',  # 劳动节
            '2024-06-10',  # 端午节
            '2024-09-15', '2024-09-16', '2024-09-17',  # 中秋节
            '2024-10-01', '2024-10-02', '2024-10-03', '2024-10-04', '2024-10-05', '2024-10-06', '2024-10-07',  # 国庆节
            
            # 2025年节假日 (示例)
            '2025-01-01',  # 元旦
            '2025-01-28', '2025-01-29', '2025-01-30', '2025-01-31', '2025-02-01', '2025-02-02', '2025-02-03', '2025-02-04',  # 春节
            '2025-04-05', '2025-04-06', '2025-04-07',  # 清明节
            '2025-05-01', '2025-05-02', '2025-05-03',  # 劳动节
            '2025-05-31',  # 端午节
            '2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04', '2025-10-05', '2025-10-06', '2025-10-07',  # 国庆节
        }
        
        self.hk_stock_holidays = {
            # 港股节假日 (示例)
            '2024-01-01',  # 新年
            '2024-02-10', '2024-02-12', '2024-02-13',  # 农历新年
            '2024-03-29',  # 耶稣受难节
            '2024-04-01',  # 复活节星期一
            '2024-05-01',  # 劳动节
            '2024-05-15',  # 佛诞节
            '2024-06-10',  # 端午节
            '2024-07-01',  # 香港特别行政区成立纪念日
            '2024-09-18',  # 中秋节翌日
            '2024-10-01',  # 国庆日
            '2024-10-11',  # 重阳节
            '2024-12-25', '2024-12-26',  # 圣诞节
            
            # 2025年港股节假日 (示例)
            '2025-01-01',  # 新年
            '2025-01-29', '2025-01-30', '2025-01-31',  # 农历新年
            '2025-04-18',  # 耶稣受难节
            '2025-04-21',  # 复活节星期一
            '2025-05-01',  # 劳动节
            '2025-05-05',  # 佛诞节
            '2025-05-31',  # 端午节
            '2025-07-01',  # 香港特别行政区成立纪念日
            '2025-10-01',  # 国庆日
            '2025-10-07',  # 重阳节
            '2025-12-25', '2025-12-26',  # 圣诞节
        }
    
    def is_market_open(self, market: str = 'A股', check_time: datetime = None) -> bool:
        """
        检查指定市场是否开市
        
        Args:
            market: 市场类型 ('A股' 或 '港股')
            check_time: 检查时间，默认为当前时间
            
        Returns:
            bool: 是否开市
        """
        if check_time is None:
            check_time = datetime.now()
        
        if market == 'A股':
            return self._is_a_stock_open(check_time)
        elif market == '港股':
            return self._is_hk_stock_open(check_time)
        else:
            self.logger.warning(f"不支持的市场类型: {market}")
            return False
    
    def _is_a_stock_open(self, check_time: datetime) -> bool:
        """检查A股是否开市"""
        # 转换为北京时间
        if check_time.tzinfo is None:
            beijing_time = self.china_tz.localize(check_time)
        else:
            beijing_time = check_time.astimezone(self.china_tz)
        
        # 检查是否为交易日
        if not self._is_trading_day(beijing_time, 'A股'):
            return False
        
        # 检查是否在交易时段内
        current_time = beijing_time.time()
        for start_time, end_time in self.a_stock_sessions:
            if start_time <= current_time <= end_time:
                return True
        
        return False
    
    def _is_hk_stock_open(self, check_time: datetime) -> bool:
        """检查港股是否开市"""
        # 转换为香港时间
        if check_time.tzinfo is None:
            hk_time = self.hk_tz.localize(check_time)
        else:
            hk_time = check_time.astimezone(self.hk_tz)
        
        # 检查是否为交易日
        if not self._is_trading_day(hk_time, '港股'):
            return False
        
        # 检查是否在交易时段内
        current_time = hk_time.time()
        for start_time, end_time in self.hk_stock_sessions:
            if start_time <= current_time <= end_time:
                return True
        
        return False
    
    def _is_trading_day(self, check_time: datetime, market: str) -> bool:
        """检查是否为交易日"""
        # 检查是否为周末
        weekday = check_time.weekday()
        
        if market == 'A股':
            if weekday not in self.a_stock_weekdays:
                return False
            # 检查是否为节假日
            date_str = check_time.strftime('%Y-%m-%d')
            return date_str not in self.a_stock_holidays
        
        elif market == '港股':
            if weekday not in self.hk_stock_weekdays:
                return False
            # 检查是否为节假日
            date_str = check_time.strftime('%Y-%m-%d')
            return date_str not in self.hk_stock_holidays
        
        return False
    
    def get_next_trading_session(self, market: str = 'A股', check_time: datetime = None) -> Tuple[datetime, datetime]:
        """
        获取下一个交易时段
        
        Args:
            market: 市场类型
            check_time: 检查时间
            
        Returns:
            Tuple[datetime, datetime]: (开始时间, 结束时间)
        """
        if check_time is None:
            check_time = datetime.now()
        
        if market == 'A股':
            return self._get_next_a_stock_session(check_time)
        elif market == '港股':
            return self._get_next_hk_stock_session(check_time)
        else:
            raise ValueError(f"不支持的市场类型: {market}")
    
    def _get_next_a_stock_session(self, check_time: datetime) -> Tuple[datetime, datetime]:
        """获取下一个A股交易时段"""
        # 转换为北京时间
        if check_time.tzinfo is None:
            beijing_time = self.china_tz.localize(check_time)
        else:
            beijing_time = check_time.astimezone(self.china_tz)
        
        current_date = beijing_time.date()
        current_time = beijing_time.time()
        
        # 检查今天的交易时段
        if self._is_trading_day(beijing_time, 'A股'):
            for start_time, end_time in self.a_stock_sessions:
                if current_time < start_time:
                    # 今天还有交易时段
                    start_dt = self.china_tz.localize(datetime.combine(current_date, start_time))
                    end_dt = self.china_tz.localize(datetime.combine(current_date, end_time))
                    return start_dt, end_dt
        
        # 寻找下一个交易日
        next_date = current_date
        for _ in range(10):  # 最多查找10天
            next_date = datetime.combine(next_date, time()).date()
            next_date = next_date.replace(day=next_date.day + 1)
            next_datetime = self.china_tz.localize(datetime.combine(next_date, time()))
            
            if self._is_trading_day(next_datetime, 'A股'):
                start_time, end_time = self.a_stock_sessions[0]  # 第一个交易时段
                start_dt = self.china_tz.localize(datetime.combine(next_date, start_time))
                end_dt = self.china_tz.localize(datetime.combine(next_date, end_time))
                return start_dt, end_dt
        
        raise RuntimeError("无法找到下一个A股交易时段")
    
    def _get_next_hk_stock_session(self, check_time: datetime) -> Tuple[datetime, datetime]:
        """获取下一个港股交易时段"""
        # 转换为香港时间
        if check_time.tzinfo is None:
            hk_time = self.hk_tz.localize(check_time)
        else:
            hk_time = check_time.astimezone(self.hk_tz)
        
        current_date = hk_time.date()
        current_time = hk_time.time()
        
        # 检查今天的交易时段
        if self._is_trading_day(hk_time, '港股'):
            for start_time, end_time in self.hk_stock_sessions:
                if current_time < start_time:
                    # 今天还有交易时段
                    start_dt = self.hk_tz.localize(datetime.combine(current_date, start_time))
                    end_dt = self.hk_tz.localize(datetime.combine(current_date, end_time))
                    return start_dt, end_dt
        
        # 寻找下一个交易日
        next_date = current_date
        for _ in range(10):  # 最多查找10天
            next_date = datetime.combine(next_date, time()).date()
            next_date = next_date.replace(day=next_date.day + 1)
            next_datetime = self.hk_tz.localize(datetime.combine(next_date, time()))
            
            if self._is_trading_day(next_datetime, '港股'):
                start_time, end_time = self.hk_stock_sessions[0]  # 第一个交易时段
                start_dt = self.hk_tz.localize(datetime.combine(next_date, start_time))
                end_dt = self.hk_tz.localize(datetime.combine(next_date, end_time))
                return start_dt, end_dt
        
        raise RuntimeError("无法找到下一个港股交易时段")
    
    def get_market_status_message(self, market: str = 'A股') -> str:
        """
        获取市场状态消息
        
        Args:
            market: 市场类型
            
        Returns:
            str: 状态消息
        """
        now = datetime.now()
        is_open = self.is_market_open(market, now)
        
        if is_open:
            return f"🟢 {market}市场当前开市中"
        else:
            try:
                next_start, next_end = self.get_next_trading_session(market, now)
                return f"🔴 {market}市场当前休市，下次开市时间: {next_start.strftime('%Y-%m-%d %H:%M')}"
            except Exception as e:
                return f"🔴 {market}市场当前休市"
    
    def should_send_notification(self, stock_codes: List[str], check_time: datetime = None) -> bool:
        """
        根据股票代码判断是否应该发送通知
        
        Args:
            stock_codes: 股票代码列表
            check_time: 检查时间，默认为当前时间
            
        Returns:
            bool: 是否应该发送通知
        """
        if not stock_codes:
            return False
        
        # 检查是否有任何相关市场开市
        has_a_stock = any(self._is_a_stock_code(code) for code in stock_codes)
        has_hk_stock = any(self._is_hk_stock_code(code) for code in stock_codes)
        
        if has_a_stock and self.is_market_open('A股', check_time):
            return True
        
        if has_hk_stock and self.is_market_open('港股', check_time):
            return True
        
        return False
    
    def _is_a_stock_code(self, code: str) -> bool:
        """判断是否为A股代码"""
        # A股代码通常以 sh 或 sz 开头，或者是6位数字
        if code.startswith(('sh', 'sz')):
            return True
        if len(code) == 6 and code.isdigit():
            return True
        return False
    
    def _is_hk_stock_code(self, code: str) -> bool:
        """判断是否为港股代码"""
        # 港股代码通常以 hk 开头，或者是5位数字
        if code.startswith('hk'):
            return True
        if len(code) == 5 and code.isdigit():
            return True
        return False
    
    def get_filtered_stock_codes(self, stock_codes: List[str], check_time: datetime = None) -> Dict[str, List[str]]:
        """
        根据开市状态过滤股票代码
        
        Args:
            stock_codes: 股票代码列表
            check_time: 检查时间，默认为当前时间
            
        Returns:
            Dict[str, List[str]]: 按市场分类的开市股票代码
        """
        result = {
            'A股': [],
            '港股': []
        }
        
        for code in stock_codes:
            if self._is_a_stock_code(code) and self.is_market_open('A股', check_time):
                result['A股'].append(code)
            elif self._is_hk_stock_code(code) and self.is_market_open('港股', check_time):
                result['港股'].append(code)
        
        return result