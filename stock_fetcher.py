import requests
import re
import logging
from typing import Dict, List, Optional

class StockFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_stock_data(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """
        获取股票数据
        Args:
            stock_codes: 股票代码列表，如 ['000001', '00700']
        Returns:
            股票数据字典
        """
        results = {}
        
        for code in stock_codes:
            try:
                if self._is_hk_stock(code):
                    data = self._fetch_hk_stock(code)
                else:
                    data = self._fetch_a_stock(code)
                
                if data:
                    results[code] = data
                    
            except Exception as e:
                self.logger.error(f"获取股票 {code} 数据失败: {e}")
                
        return results
    
    def get_stock_name(self, code: str) -> Optional[str]:
        """
        获取股票名称
        Args:
            code: 股票代码
        Returns:
            股票名称，获取失败返回None
        """
        try:
            if self._is_hk_stock(code):
                data = self._fetch_hk_stock(code)
            else:
                data = self._fetch_a_stock(code)
            
            if data and data.get('name'):
                self.logger.info(f"成功获取股票名称: {code} -> {data['name']}")
                return data['name']
            else:
                self.logger.warning(f"未能获取到股票 {code} 的名称")
                return None
                
        except Exception as e:
            self.logger.error(f"获取股票 {code} 名称失败: {e}")
            return None
    
    def _is_hk_stock(self, code: str) -> bool:
        """判断是否为港股"""
        return len(code) == 5 and code.isdigit()
    
    def _fetch_a_stock(self, code: str) -> Optional[Dict]:
        """获取A股数据"""
        try:
            # 尝试腾讯财经API
            market_prefix = "sh" if code.startswith("6") else "sz"
            tencent_code = f"{market_prefix}{code}"
            url = f"https://qt.gtimg.cn/q={tencent_code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            
            if response.status_code == 200 and response.text:
                return self._parse_tencent_a_stock(response.text, code)
                
        except Exception as e:
            self.logger.error(f"获取A股 {code} 数据失败: {e}")
            
        return None
    
    def _fetch_hk_stock(self, code: str) -> Optional[Dict]:
        """获取港股数据"""
        try:
            # 腾讯财经API
            hk_code = f"hk{code}"
            url = f"https://qt.gtimg.cn/q={hk_code}"
            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'
            
            if response.status_code == 200:
                return self._parse_tencent_hk_stock(response.text, code)
                
        except Exception as e:
            self.logger.error(f"获取港股 {code} 数据失败: {e}")
            
        return None
    
    def _parse_sina_a_stock(self, text: str, code: str) -> Optional[Dict]:
        """解析新浪A股数据"""
        try:
            # 提取数据部分
            match = re.search(r'"([^"]*)"', text)
            if not match:
                return None
                
            data_str = match.group(1)
            parts = data_str.split(',')
            
            if len(parts) < 32:
                return None
            
            name = parts[0]
            current_price = float(parts[3]) if parts[3] else 0
            prev_close = float(parts[2]) if parts[2] else 0
            open_price = float(parts[1]) if parts[1] else 0
            high_price = float(parts[4]) if parts[4] else 0
            low_price = float(parts[5]) if parts[5] else 0
            volume = int(float(parts[8])) if parts[8] else 0
            
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            return {
                'code': code,
                'name': name,
                'current_price': current_price,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'prev_close': prev_close,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'market': 'A股',
                'currency': '¥'
            }
            
        except Exception as e:
            self.logger.error(f"解析A股 {code} 数据失败: {e}")
            return None
    
    def _parse_tencent_hk_stock(self, text: str, code: str) -> Optional[Dict]:
        """解析腾讯港股数据"""
        try:
            # 提取数据部分
            match = re.search(r'"([^"]*)"', text)
            if not match:
                return None
                
            data_str = match.group(1)
            parts = data_str.split('~')
            
            if len(parts) < 50:
                return None
            
            name = parts[1]
            current_price = float(parts[3]) if parts[3] else 0
            prev_close = float(parts[4]) if parts[4] else 0
            open_price = float(parts[5]) if parts[5] else 0
            high_price = float(parts[33]) if parts[33] else 0
            low_price = float(parts[34]) if parts[34] else 0
            volume = int(float(parts[6])) if parts[6] else 0
            
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            return {
                'code': code,
                'name': name,
                'current_price': current_price,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'prev_close': prev_close,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'market': '港股',
                'currency': 'HK$'
            }
            
        except Exception as e:
            self.logger.error(f"解析港股 {code} 数据失败: {e}")
            return None
    
    def _parse_tencent_a_stock(self, text: str, code: str) -> Optional[Dict]:
        """解析腾讯A股数据"""
        try:
            # 提取数据部分
            match = re.search(r'"([^"]*)"', text)
            if not match:
                return None
                
            data_str = match.group(1)
            parts = data_str.split('~')
            
            if len(parts) < 50:
                return None
            
            name = parts[1]
            current_price = float(parts[3]) if parts[3] else 0
            prev_close = float(parts[4]) if parts[4] else 0
            open_price = float(parts[5]) if parts[5] else 0
            high_price = float(parts[33]) if parts[33] else 0
            low_price = float(parts[34]) if parts[34] else 0
            volume = int(float(parts[6]) * 100) if parts[6] else 0  # 腾讯API返回的是手数，需要乘以100
            
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            return {
                'code': code,
                'name': name,
                'current_price': current_price,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'prev_close': prev_close,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'market': 'A股',
                'currency': '¥'
            }
            
        except Exception as e:
            self.logger.error(f"解析A股 {code} 数据失败: {e}")
            return None