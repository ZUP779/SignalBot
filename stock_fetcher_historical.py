import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class HistoricalDataFetcher:
    """历史数据获取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_historical_data(self, code: str, days: int = 60) -> Optional[List[Dict]]:
        """
        获取股票历史数据
        Args:
            code: 股票代码
            days: 获取天数，默认60天
        Returns:
            包含历史数据的列表，每个元素是字典: {date, open, high, low, close, volume}
        """
        try:
            if self._is_hk_stock(code):
                return self._fetch_hk_historical_data(code, days)
            else:
                return self._fetch_a_historical_data(code, days)
        except Exception as e:
            self.logger.error(f"获取股票 {code} 历史数据失败: {e}")
            return None
    
    def _is_hk_stock(self, code: str) -> bool:
        """判断是否为港股"""
        return len(code) == 5 and code.isdigit()
    
    def _fetch_a_historical_data(self, code: str, days: int) -> Optional[List[Dict]]:
        """获取A股历史数据"""
        try:
            # 使用网易财经API获取A股历史数据
            market_code = f"0{code}" if code.startswith("6") else f"1{code}"
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 30)  # 多获取一些数据以防节假日
            
            start_str = start_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d")
            
            url = f"http://quotes.money.163.com/service/chddata.html"
            params = {
                'code': market_code,
                'start': start_str,
                'end': end_str,
                'fields': 'TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.encoding = 'gbk'
            
            if response.status_code == 200 and response.text:
                return self._parse_netease_historical_data(response.text)
                
        except Exception as e:
            self.logger.error(f"获取A股 {code} 历史数据失败: {e}")
            
        # 备用方案：使用腾讯财经API
        try:
            return self._fetch_tencent_historical_data(code, days, is_hk=False)
        except Exception as e:
            self.logger.error(f"腾讯API获取A股 {code} 历史数据失败: {e}")
            
        return None
    
    def _fetch_hk_historical_data(self, code: str, days: int) -> Optional[List[Dict]]:
        """获取港股历史数据"""
        try:
            # 使用腾讯财经API获取港股历史数据
            return self._fetch_tencent_historical_data(code, days, is_hk=True)
        except Exception as e:
            self.logger.error(f"获取港股 {code} 历史数据失败: {e}")
            return None
    
    def _fetch_tencent_historical_data(self, code: str, days: int, is_hk: bool) -> Optional[List[Dict]]:
        """使用腾讯API获取历史数据"""
        try:
            if is_hk:
                symbol = f"hk{code}"
            else:
                market_prefix = "sh" if code.startswith("6") else "sz"
                symbol = f"{market_prefix}{code}"
            
            # 腾讯历史数据API
            url = f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
            params = {
                'param': f"{symbol},day,,,{days},qfq",
                '_var': 'kline_dayqfq',
                '_callback': 'kline_dayqfq'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://gu.qq.com'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return self._parse_tencent_historical_data(response.text)
                
        except Exception as e:
            self.logger.error(f"腾讯API获取历史数据失败: {e}")
            
        return None
    
    def _parse_netease_historical_data(self, text: str) -> Optional[List[Dict]]:
        """解析网易历史数据"""
        try:
            lines = text.strip().split('\n')
            if len(lines) < 2:
                return None
            
            # 跳过标题行
            data_lines = lines[1:]
            data = []
            
            for line in data_lines:
                parts = line.split(',')
                if len(parts) >= 10:
                    try:
                        date_str = parts[0].strip()
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        
                        data.append({
                            'date': date,
                            'open': float(parts[6]),    # TOPEN
                            'high': float(parts[2]),    # HIGH
                            'low': float(parts[3]),     # LOW
                            'close': float(parts[1]),   # TCLOSE
                            'volume': int(float(parts[8])) if parts[8] else 0  # VOTURNOVER
                        })
                    except (ValueError, IndexError):
                        continue
            
            if not data:
                return None
                
            # 按日期排序
            data.sort(key=lambda x: x['date'])
            return data
            
        except Exception as e:
            self.logger.error(f"解析网易历史数据失败: {e}")
            return None
    
    def _parse_tencent_historical_data(self, text: str) -> Optional[List[Dict]]:
        """解析腾讯历史数据"""
        try:
            # 提取JSON数据
            start_pos = text.find('{')
            end_pos = text.rfind('}') + 1
            
            if start_pos == -1 or end_pos == 0:
                return None
                
            json_str = text[start_pos:end_pos]
            data_dict = json.loads(json_str)
            
            if 'data' not in data_dict:
                return None
            
            symbol_data = data_dict['data']
            if not symbol_data or len(symbol_data) == 0:
                return None
                
            # 获取第一个股票的数据
            stock_data = list(symbol_data.values())[0]
            if 'day' not in stock_data:
                return None
                
            kline_data = stock_data['day']
            if not kline_data:
                return None
                
            data = []
            for item in kline_data:
                try:
                    # 腾讯数据格式: [date, open, close, high, low, volume, ...]
                    date_str = item[0]
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    data.append({
                        'date': date,
                        'open': float(item[1]),
                        'high': float(item[3]),
                        'low': float(item[4]),
                        'close': float(item[2]),
                        'volume': int(float(item[5])) if len(item) > 5 else 0
                    })
                except (ValueError, IndexError):
                    continue
            
            if not data:
                return None
                
            # 按日期排序
            data.sort(key=lambda x: x['date'])
            return data
            
        except Exception as e:
            self.logger.error(f"解析腾讯历史数据失败: {e}")
            return None
    
    def get_fundamental_data(self, code: str) -> Optional[Dict]:
        """
        获取基本面数据
        Args:
            code: 股票代码
        Returns:
            基本面数据字典
        """
        try:
            # 这里可以集成更多基本面数据源
            # 目前返回基础框架，后续可以扩展
            fundamental_data = {
                'pe_ratio': None,       # 市盈率
                'pb_ratio': None,       # 市净率
                'market_cap': None,     # 市值
                'revenue_growth': None, # 营收增长率
                'profit_growth': None,  # 利润增长率
                'roe': None,           # 净资产收益率
                'debt_ratio': None,    # 负债率
            }
            
            # TODO: 实现具体的基本面数据获取逻辑
            # 可以使用同花顺、东方财富等API
            
            return fundamental_data
            
        except Exception as e:
            self.logger.error(f"获取股票 {code} 基本面数据失败: {e}")
            return None