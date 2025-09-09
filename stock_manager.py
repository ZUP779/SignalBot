import sqlite3
import logging
from typing import List, Optional
from config import DATABASE_PATH
from stock_fetcher import StockFetcher

class StockManager:
    """股票代码管理器"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.logger = logging.getLogger(__name__)
        self.stock_fetcher = StockFetcher()
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stocks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT UNIQUE NOT NULL,
                        name TEXT,
                        market TEXT,
                        added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL,
                        price REAL,
                        change_percent REAL,
                        volume INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                self.logger.info("数据库初始化完成")
                
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise
    
    def add_stock(self, code: str, name: str = "", market: str = "") -> bool:
        """
        添加股票代码
        Args:
            code: 股票代码
            name: 股票名称（可选，如果为空则自动获取）
            market: 市场类型（可选）
        Returns:
            添加是否成功
        """
        try:
            # 自动判断市场类型
            if not market:
                market = "港股" if len(code) == 5 and code.isdigit() else "A股"
            
            # 如果没有提供股票名称，尝试自动获取
            if not name:
                self.logger.info(f"正在自动获取股票 {code} 的名称...")
                fetched_name = self.stock_fetcher.get_stock_name(code)
                if fetched_name:
                    name = fetched_name
                    self.logger.info(f"成功获取股票名称: {code} -> {name}")
                else:
                    self.logger.warning(f"无法获取股票 {code} 的名称，将使用空名称")
                    name = ""
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO stocks (code, name, market, is_active)
                    VALUES (?, ?, ?, 1)
                ''', (code, name, market))
                conn.commit()
                
            self.logger.info(f"添加股票成功: {code} ({name}) [{market}]")
            return True
            
        except Exception as e:
            self.logger.error(f"添加股票 {code} 失败: {e}")
            return False
    
    def remove_stock(self, code: str) -> bool:
        """
        移除股票代码
        Args:
            code: 股票代码
        Returns:
            移除是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE stocks SET is_active = 0 WHERE code = ?', (code,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"移除股票成功: {code}")
                    return True
                else:
                    self.logger.warning(f"股票代码不存在: {code}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"移除股票 {code} 失败: {e}")
            return False
    
    def get_active_stocks(self) -> List[str]:
        """
        获取所有活跃的股票代码
        Returns:
            股票代码列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT code FROM stocks WHERE is_active = 1 ORDER BY added_time')
                results = cursor.fetchall()
                
            codes = [row[0] for row in results]
            self.logger.info(f"获取到 {len(codes)} 个活跃股票代码")
            return codes
            
        except Exception as e:
            self.logger.error(f"获取股票代码失败: {e}")
            return []
    
    def list_stocks(self) -> List[dict]:
        """
        列出所有股票信息
        Returns:
            股票信息列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT code, name, market, added_time, is_active 
                    FROM stocks 
                    ORDER BY added_time DESC
                ''')
                results = cursor.fetchall()
            
            stocks = []
            for row in results:
                stocks.append({
                    'code': row[0],
                    'name': row[1] or '未知',
                    'market': row[2] or '未知',
                    'added_time': row[3],
                    'is_active': bool(row[4])
                })
            
            return stocks
            
        except Exception as e:
            self.logger.error(f"列出股票信息失败: {e}")
            return []
    
    def update_stock_info(self, code: str, name: str) -> bool:
        """
        更新股票信息
        Args:
            code: 股票代码
            name: 股票名称
        Returns:
            更新是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE stocks SET name = ? WHERE code = ?', (name, code))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"更新股票信息成功: {code} -> {name}")
                    return True
                else:
                    return False
                    
        except Exception as e:
            self.logger.error(f"更新股票信息失败: {e}")
            return False
    
    def save_stock_history(self, code: str, price: float, change_percent: float, volume: int):
        """保存股票历史数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO stock_history (code, price, change_percent, volume)
                    VALUES (?, ?, ?, ?)
                ''', (code, price, change_percent, volume))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"保存股票历史数据失败: {e}")
    
    def get_historical_volumes(self, codes: List[str], days: int = 7) -> dict:
        """获取历史成交量数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                historical_data = {}
                for code in codes:
                    cursor.execute('''
                        SELECT volume FROM stock_history 
                        WHERE code = ? AND volume > 0
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (code, days * 24))  # 假设每小时一条记录
                    
                    results = cursor.fetchall()
                    volumes = [row[0] for row in results]
                    historical_data[code] = volumes
                
                return historical_data
                
        except Exception as e:
            self.logger.error(f"获取历史成交量失败: {e}")
            return {}