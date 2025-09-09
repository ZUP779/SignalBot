import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from config import PRICE_CHANGE_THRESHOLD, VOLUME_SPIKE_THRESHOLD

class SignalDetector:
    """智能信号检测器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.price_threshold = PRICE_CHANGE_THRESHOLD
        self.volume_threshold = VOLUME_SPIKE_THRESHOLD
    
    def detect_signals(self, current_data: Dict[str, Dict], historical_data: Dict[str, List] = None) -> Dict[str, List]:
        """
        检测股票信号
        Args:
            current_data: 当前股票数据
            historical_data: 历史数据（可选）
        Returns:
            检测到的信号字典
        """
        signals = {}
        
        for code, data in current_data.items():
            stock_signals = []
            
            # 价格异动信号
            price_signals = self._detect_price_signals(data)
            stock_signals.extend(price_signals)
            
            # 成交量异常信号
            volume_signals = self._detect_volume_signals(data, historical_data.get(code, []) if historical_data else [])
            stock_signals.extend(volume_signals)
            
            # 技术指标信号
            technical_signals = self._detect_technical_signals(data)
            stock_signals.extend(technical_signals)
            
            if stock_signals:
                signals[code] = stock_signals
                
        return signals
    
    def _detect_price_signals(self, data: Dict) -> List[Dict]:
        """检测价格异动信号"""
        signals = []
        change_percent = abs(data.get('change_percent', 0))
        
        if change_percent >= self.price_threshold:
            signal_type = "涨停预警" if data.get('change_percent', 0) > 0 else "跌停预警"
            signals.append({
                'type': 'price_movement',
                'level': 'high' if change_percent >= 8 else 'medium',
                'message': f"{signal_type}: 涨跌幅{data.get('change_percent', 0):+.2f}%",
                'value': change_percent,
                'timestamp': datetime.now()
            })
        
        return signals
    
    def _detect_volume_signals(self, data: Dict, historical_volumes: List) -> List[Dict]:
        """检测成交量异常信号"""
        signals = []
        current_volume = data.get('volume', 0)
        
        if not historical_volumes or current_volume == 0:
            return signals
        
        # 计算平均成交量
        avg_volume = sum(historical_volumes[-5:]) / min(len(historical_volumes), 5)
        
        if avg_volume > 0 and current_volume > avg_volume * self.volume_threshold:
            ratio = current_volume / avg_volume
            signals.append({
                'type': 'volume_spike',
                'level': 'high' if ratio >= 3 else 'medium',
                'message': f"成交量异常: 是平均值的{ratio:.1f}倍",
                'value': ratio,
                'timestamp': datetime.now()
            })
        
        return signals
    
    def _detect_technical_signals(self, data: Dict) -> List[Dict]:
        """检测技术指标信号"""
        signals = []
        
        current_price = data.get('current_price', 0)
        high_price = data.get('high_price', 0)
        low_price = data.get('low_price', 0)
        
        if current_price > 0 and high_price > 0 and low_price > 0:
            # 接近涨停
            if abs(current_price - high_price) / current_price < 0.01:
                signals.append({
                    'type': 'technical',
                    'level': 'high',
                    'message': "接近今日最高价",
                    'value': (current_price - high_price) / current_price * 100,
                    'timestamp': datetime.now()
                })
            
            # 接近跌停
            elif abs(current_price - low_price) / current_price < 0.01:
                signals.append({
                    'type': 'technical',
                    'level': 'high',
                    'message': "接近今日最低价",
                    'value': (current_price - low_price) / current_price * 100,
                    'timestamp': datetime.now()
                })
        
        return signals
    
    def should_notify(self, signals: Dict[str, List]) -> bool:
        """判断是否需要发送通知"""
        if not signals:
            return False
        
        # 有高级别信号就通知
        for code, stock_signals in signals.items():
            for signal in stock_signals:
                if signal.get('level') == 'high':
                    return True
        
        # 或者有多个中级别信号
        medium_count = 0
        for code, stock_signals in signals.items():
            for signal in stock_signals:
                if signal.get('level') == 'medium':
                    medium_count += 1
        
        return medium_count >= 2
    
    def format_signals_for_notification(self, signals: Dict[str, List], stock_data: Dict[str, Dict]) -> str:
        """格式化信号为通知消息"""
        if not signals:
            return ""
        
        lines = ["🤖 SignalBot 检测到重要信号!\n"]
        
        for code, stock_signals in signals.items():
            stock_info = stock_data.get(code, {})
            name = stock_info.get('name', code)
            
            lines.append(f"📊 {name}({code})")
            
            for signal in stock_signals:
                level_icon = "🔴" if signal['level'] == 'high' else "🟡"
                lines.append(f"{level_icon} {signal['message']}")
            
            # 添加当前价格信息
            if stock_info:
                current = stock_info.get('current_price', 0)
                change = stock_info.get('change_percent', 0)
                currency = stock_info.get('currency', '¥')
                lines.append(f"💰 当前价格: {currency}{current:.2f} ({change:+.2f}%)")
            
            lines.append("")
        
        return "\n".join(lines)