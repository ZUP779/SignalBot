import logging
from typing import Dict, List, Optional
from datetime import datetime
import statistics

class SimpleTechnicalIndicators:
    """简化版技术指标计算器 - 不依赖pandas"""
    
    def __init__(self, historical_data: List[Dict]):
        """
        Args:
            historical_data: 历史数据列表，每个元素包含date, open, high, low, close, volume
        """
        self.data = historical_data
        self.logger = logging.getLogger(__name__)
        
        if not self.data:
            raise ValueError("历史数据不能为空")
    
    def calculate_rsi(self, period: int = 14) -> float:
        """计算RSI指标"""
        try:
            if len(self.data) < period + 1:
                return 50.0  # 默认中性值
            
            gains = []
            losses = []
            
            for i in range(1, len(self.data)):
                change = self.data[i]['close'] - self.data[i-1]['close']
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if len(gains) < period:
                return 50.0
            
            # 计算平均收益和平均损失
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            self.logger.error(f"计算RSI失败: {e}")
            return 50.0
    
    def calculate_macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict:
        """计算MACD指标"""
        try:
            if len(self.data) < slow_period:
                return {'macd': 0, 'signal': 0, 'histogram': 0}
            
            closes = [item['close'] for item in self.data]
            
            # 计算EMA
            def calculate_ema(data, period):
                if len(data) < period:
                    return data[-1] if data else 0
                
                multiplier = 2 / (period + 1)
                ema = data[0]  # 初始值
                
                for price in data[1:]:
                    ema = (price * multiplier) + (ema * (1 - multiplier))
                
                return ema
            
            fast_ema = calculate_ema(closes, fast_period)
            slow_ema = calculate_ema(closes, slow_period)
            
            macd = fast_ema - slow_ema
            
            # 简化的signal计算
            signal = macd * 0.8  # 简化处理
            histogram = macd - signal
            
            return {
                'macd': macd,
                'signal': signal,
                'histogram': histogram
            }
            
        except Exception as e:
            self.logger.error(f"计算MACD失败: {e}")
            return {'macd': 0, 'signal': 0, 'histogram': 0}
    
    def calculate_moving_averages(self) -> Dict:
        """计算移动平均线"""
        try:
            closes = [item['close'] for item in self.data]
            
            def calculate_ma(data, period):
                if len(data) < period:
                    return sum(data) / len(data) if data else 0
                return sum(data[-period:]) / period
            
            ma5 = calculate_ma(closes, 5)
            ma10 = calculate_ma(closes, 10)
            ma20 = calculate_ma(closes, 20)
            ma60 = calculate_ma(closes, 60)
            
            return {
                'MA5': ma5,
                'MA10': ma10,
                'MA20': ma20,
                'MA60': ma60
            }
            
        except Exception as e:
            self.logger.error(f"计算移动平均线失败: {e}")
            return {'MA5': 0, 'MA10': 0, 'MA20': 0, 'MA60': 0}
    
    def calculate_volume_indicators(self) -> Dict:
        """计算成交量指标"""
        try:
            volumes = [item['volume'] for item in self.data]
            
            # 20日平均成交量
            avg_volume_20 = sum(volumes[-20:]) / min(20, len(volumes)) if volumes else 0
            
            # 当日成交量与平均值比较
            current_volume = volumes[-1] if volumes else 0
            volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
            
            return {
                'avg_volume_20': avg_volume_20,
                'current_volume': current_volume,
                'volume_ratio': volume_ratio
            }
            
        except Exception as e:
            self.logger.error(f"计算成交量指标失败: {e}")
            return {'avg_volume_20': 0, 'current_volume': 0, 'volume_ratio': 1}
    
    def calculate_volatility(self, period: int = 20) -> float:
        """计算波动率"""
        try:
            if len(self.data) < 2:
                return 0.0
            
            # 计算日收益率
            returns = []
            for i in range(1, len(self.data)):
                if self.data[i-1]['close'] > 0:
                    daily_return = (self.data[i]['close'] - self.data[i-1]['close']) / self.data[i-1]['close']
                    returns.append(daily_return)
            
            if len(returns) < 2:
                return 0.0
            
            # 使用最近period天的数据计算波动率
            recent_returns = returns[-period:] if len(returns) >= period else returns
            
            # 计算标准差
            mean_return = sum(recent_returns) / len(recent_returns)
            variance = sum((r - mean_return) ** 2 for r in recent_returns) / len(recent_returns)
            volatility = (variance ** 0.5) * (252 ** 0.5) * 100  # 年化波动率(%)
            
            return volatility
            
        except Exception as e:
            self.logger.error(f"计算波动率失败: {e}")
            return 15.0
    
    def get_signals_summary(self) -> Dict:
        """获取技术指标信号汇总"""
        try:
            rsi = self.calculate_rsi()
            macd_data = self.calculate_macd()
            ma_data = self.calculate_moving_averages()
            volume_data = self.calculate_volume_indicators()
            volatility = self.calculate_volatility()
            
            current_price = self.data[-1]['close'] if self.data else 0
            
            # 生成信号
            signals = {
                'rsi_signal': 'neutral',
                'macd_signal': 'neutral', 
                'ma_signal': 'neutral',
                'volume_signal': 'neutral'
            }
            
            # RSI信号
            if rsi < 30:
                signals['rsi_signal'] = 'oversold'
            elif rsi > 70:
                signals['rsi_signal'] = 'overbought'
            
            # MACD信号
            if macd_data['macd'] > macd_data['signal']:
                signals['macd_signal'] = 'bullish'
            elif macd_data['macd'] < macd_data['signal']:
                signals['macd_signal'] = 'bearish'
            
            # 移动平均线信号
            if current_price > ma_data['MA20']:
                signals['ma_signal'] = 'bullish'
            elif current_price < ma_data['MA20']:
                signals['ma_signal'] = 'bearish'
            
            # 成交量信号
            if volume_data['volume_ratio'] > 2:
                signals['volume_signal'] = 'high'
            elif volume_data['volume_ratio'] < 0.5:
                signals['volume_signal'] = 'low'
            
            return {
                'signals': signals,
                'rsi': rsi,
                'macd': macd_data,
                'moving_averages': ma_data,
                'volume': volume_data,
                'volatility': volatility,
                'current_price': current_price
            }
            
        except Exception as e:
            self.logger.error(f"生成信号汇总失败: {e}")
            return {}