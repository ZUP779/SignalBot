import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime, timedelta

class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_all_indicators(self, price_data: List[Dict]) -> Dict:
        """
        计算所有技术指标
        Args:
            price_data: 价格数据列表，每个元素包含 {date, open, high, low, close, volume}
        Returns:
            技术指标字典
        """
        if not price_data or len(price_data) < 5:
            return {}
        
        # 转换为DataFrame便于计算
        df = pd.DataFrame(price_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        indicators = {}
        
        try:
            # 移动平均线
            indicators.update(self._calculate_moving_averages(df))
            
            # RSI相对强弱指标
            indicators['rsi'] = self._calculate_rsi(df['close'])
            
            # MACD指标
            macd_data = self._calculate_macd(df['close'])
            indicators.update(macd_data)
            
            # 布林带
            bollinger_data = self._calculate_bollinger_bands(df['close'])
            indicators.update(bollinger_data)
            
            # KDJ指标
            kdj_data = self._calculate_kdj(df['high'], df['low'], df['close'])
            indicators.update(kdj_data)
            
            # 成交量指标
            volume_data = self._calculate_volume_indicators(df['close'], df['volume'])
            indicators.update(volume_data)
            
            # 波动率指标
            indicators['volatility_20'] = self._calculate_volatility(df['close'], 20)
            
            # 价格形态指标
            pattern_data = self._calculate_price_patterns(df)
            indicators.update(pattern_data)
            
            # 趋势强度指标
            trend_data = self._calculate_trend_strength(df)
            indicators.update(trend_data)
            
        except Exception as e:
            self.logger.error(f"计算技术指标失败: {e}")
        
        return indicators
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> Dict:
        """计算移动平均线"""
        close = df['close']
        return {
            'ma5': close.rolling(window=5).mean().iloc[-1] if len(close) >= 5 else 0,
            'ma10': close.rolling(window=10).mean().iloc[-1] if len(close) >= 10 else 0,
            'ma20': close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else 0,
            'ma60': close.rolling(window=60).mean().iloc[-1] if len(close) >= 60 else 0,
            'ema12': close.ewm(span=12).mean().iloc[-1] if len(close) >= 12 else 0,
            'ema26': close.ewm(span=26).mean().iloc[-1] if len(close) >= 26 else 0,
        }
    
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> float:
        """计算RSI相对强弱指标"""
        if len(close) < period + 1:
            return 50.0
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _calculate_macd(self, close: pd.Series) -> Dict:
        """计算MACD指标"""
        if len(close) < 26:
            return {'macd': 0, 'macd_signal': 0, 'macd_histogram': 0}
        
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1] if not pd.isna(macd_line.iloc[-1]) else 0,
            'macd_signal': 1 if histogram.iloc[-1] > 0 else -1,
            'macd_histogram': histogram.iloc[-1] if not pd.isna(histogram.iloc[-1]) else 0
        }
    
    def _calculate_bollinger_bands(self, close: pd.Series, period: int = 20, std_dev: int = 2) -> Dict:
        """计算布林带"""
        if len(close) < period:
            return {'bb_upper': 0, 'bb_middle': 0, 'bb_lower': 0, 'bb_width': 0}
        
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        width = (upper - lower) / sma * 100
        
        return {
            'bb_upper': upper.iloc[-1] if not pd.isna(upper.iloc[-1]) else 0,
            'bb_middle': sma.iloc[-1] if not pd.isna(sma.iloc[-1]) else 0,
            'bb_lower': lower.iloc[-1] if not pd.isna(lower.iloc[-1]) else 0,
            'bb_width': width.iloc[-1] if not pd.isna(width.iloc[-1]) else 0
        }
    
    def _calculate_kdj(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 9) -> Dict:
        """计算KDJ指标"""
        if len(close) < period:
            return {'k_value': 50, 'd_value': 50, 'j_value': 50}
        
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        k_value = rsv.ewm(alpha=1/3).mean()
        d_value = k_value.ewm(alpha=1/3).mean()
        j_value = 3 * k_value - 2 * d_value
        
        return {
            'k_value': k_value.iloc[-1] if not pd.isna(k_value.iloc[-1]) else 50,
            'd_value': d_value.iloc[-1] if not pd.isna(d_value.iloc[-1]) else 50,
            'j_value': j_value.iloc[-1] if not pd.isna(j_value.iloc[-1]) else 50
        }
    
    def _calculate_volume_indicators(self, close: pd.Series, volume: pd.Series) -> Dict:
        """计算成交量指标"""
        if len(volume) < 20:
            return {'avg_volume_5': 0, 'avg_volume_20': 0, 'volume_ratio': 1.0, 'obv': 0}
        
        avg_volume_5 = volume.rolling(window=5).mean().iloc[-1]
        avg_volume_20 = volume.rolling(window=20).mean().iloc[-1]
        volume_ratio = volume.iloc[-1] / avg_volume_20 if avg_volume_20 > 0 else 1.0
        
        # OBV能量潮指标
        price_change = close.diff()
        obv = (volume * np.sign(price_change)).cumsum().iloc[-1]
        
        return {
            'avg_volume_5': avg_volume_5,
            'avg_volume_20': avg_volume_20,
            'volume_ratio': volume_ratio,
            'obv': obv
        }
    
    def _calculate_volatility(self, close: pd.Series, period: int = 20) -> float:
        """计算波动率"""
        if len(close) < period:
            return 0.0
        
        returns = close.pct_change().dropna()
        volatility = returns.rolling(window=period).std().iloc[-1] * np.sqrt(252) * 100
        
        return volatility if not pd.isna(volatility) else 0.0
    
    def _calculate_price_patterns(self, df: pd.DataFrame) -> Dict:
        """计算价格形态指标"""
        close = df['close']
        high = df['high']
        low = df['low']
        
        if len(close) < 20:
            return {'consecutive_up_days': 0, 'consecutive_down_days': 0, 'max_drawdown_20': 0}
        
        # 连续上涨/下跌天数
        price_change = close.diff()
        consecutive_up = 0
        consecutive_down = 0
        
        for i in range(len(price_change) - 1, -1, -1):
            if pd.isna(price_change.iloc[i]):
                break
            if price_change.iloc[i] > 0:
                consecutive_up += 1
            elif price_change.iloc[i] < 0:
                consecutive_down += 1
            else:
                break
        
        # 最大回撤
        rolling_max = close.rolling(window=20).max()
        drawdown = (close - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        
        return {
            'consecutive_up_days': consecutive_up,
            'consecutive_down_days': consecutive_down,
            'max_drawdown_20': max_drawdown if not pd.isna(max_drawdown) else 0
        }
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> Dict:
        """计算趋势强度指标"""
        close = df['close']
        
        if len(close) < 20:
            return {'trend_strength': 0, 'trend_direction': 0, 'adx': 0}
        
        # 简化的趋势强度计算
        ma5 = close.rolling(window=5).mean()
        ma20 = close.rolling(window=20).mean()
        
        # 趋势方向
        trend_direction = 1 if ma5.iloc[-1] > ma20.iloc[-1] else -1
        
        # 趋势强度（基于价格与均线的偏离度）
        trend_strength = abs(close.iloc[-1] - ma20.iloc[-1]) / ma20.iloc[-1] * 100
        
        # 简化的ADX计算
        high = df['high']
        low = df['low']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / tr.rolling(window=14).mean())
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / tr.rolling(window=14).mean())
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=14).mean().iloc[-1]
        
        return {
            'trend_strength': trend_strength if not pd.isna(trend_strength) else 0,
            'trend_direction': trend_direction,
            'adx': adx if not pd.isna(adx) else 0
        }
    
    def get_signal_summary(self, indicators: Dict) -> Dict:
        """获取技术指标信号汇总"""
        signals = {
            'bullish_signals': [],
            'bearish_signals': [],
            'neutral_signals': [],
            'overall_signal': 'neutral'
        }
        
        # RSI信号
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            signals['bullish_signals'].append('RSI超卖')
        elif rsi > 70:
            signals['bearish_signals'].append('RSI超买')
        else:
            signals['neutral_signals'].append('RSI中性')
        
        # MACD信号
        macd_signal = indicators.get('macd_signal', 0)
        if macd_signal > 0:
            signals['bullish_signals'].append('MACD金叉')
        elif macd_signal < 0:
            signals['bearish_signals'].append('MACD死叉')
        
        # 均线信号
        ma5 = indicators.get('ma5', 0)
        ma20 = indicators.get('ma20', 0)
        if ma5 > ma20 > 0:
            signals['bullish_signals'].append('短期均线向上')
        elif ma20 > ma5 > 0:
            signals['bearish_signals'].append('短期均线向下')
        
        # KDJ信号
        k_value = indicators.get('k_value', 50)
        d_value = indicators.get('d_value', 50)
        if k_value > d_value and k_value < 80:
            signals['bullish_signals'].append('KDJ金叉')
        elif k_value < d_value and k_value > 20:
            signals['bearish_signals'].append('KDJ死叉')
        
        # 成交量信号
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if volume_ratio > 2.0:
            signals['bullish_signals'].append('成交量放大')
        elif volume_ratio < 0.5:
            signals['bearish_signals'].append('成交量萎缩')
        
        # 综合信号判断
        bullish_count = len(signals['bullish_signals'])
        bearish_count = len(signals['bearish_signals'])
        
        if bullish_count > bearish_count + 1:
            signals['overall_signal'] = 'bullish'
        elif bearish_count > bullish_count + 1:
            signals['overall_signal'] = 'bearish'
        else:
            signals['overall_signal'] = 'neutral'
        
        return signals
    
    def format_indicators_report(self, indicators: Dict) -> str:
        """格式化技术指标报告"""
        if not indicators:
            return "技术指标数据不足"
        
        lines = ["📊 技术指标分析报告\n"]
        
        # 移动平均线
        lines.append("📈 移动平均线:")
        lines.append(f"   MA5: {indicators.get('ma5', 0):.2f}")
        lines.append(f"   MA20: {indicators.get('ma20', 0):.2f}")
        lines.append(f"   MA60: {indicators.get('ma60', 0):.2f}")
        
        # 技术指标
        lines.append("\n🎯 关键指标:")
        lines.append(f"   RSI: {indicators.get('rsi', 0):.1f}")
        lines.append(f"   MACD信号: {'看涨' if indicators.get('macd_signal', 0) > 0 else '看跌'}")
        lines.append(f"   KDJ: K={indicators.get('k_value', 0):.1f}, D={indicators.get('d_value', 0):.1f}")
        
        # 成交量分析
        lines.append("\n📊 成交量分析:")
        lines.append(f"   量比: {indicators.get('volume_ratio', 0):.1f}")
        lines.append(f"   20日均量: {indicators.get('avg_volume_20', 0):,.0f}")
        
        # 风险指标
        lines.append("\n⚠️ 风险指标:")
        lines.append(f"   波动率: {indicators.get('volatility_20', 0):.1f}%")
        lines.append(f"   最大回撤: {indicators.get('max_drawdown_20', 0):.1f}%")
        
        # 信号汇总
        signals = self.get_signal_summary(indicators)
        lines.append(f"\n🎯 综合信号: {signals['overall_signal'].upper()}")
        
        if signals['bullish_signals']:
            lines.append(f"✅ 看涨信号: {', '.join(signals['bullish_signals'])}")
        
        if signals['bearish_signals']:
            lines.append(f"❌ 看跌信号: {', '.join(signals['bearish_signals'])}")
        
        return "\n".join(lines)