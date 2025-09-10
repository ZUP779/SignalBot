import logging
import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
from stock_fetcher_historical import HistoricalDataFetcher

class ScreenerCriteria(Enum):
    """筛选标准枚举"""
    TECHNICAL_BREAKOUT = "技术突破"
    VOLUME_SURGE = "放量突破"
    MOMENTUM_STRONG = "强势动量"
    VALUE_OPPORTUNITY = "价值机会"
    GROWTH_POTENTIAL = "成长潜力"
    OVERSOLD_BOUNCE = "超跌反弹"
    TREND_FOLLOWING = "趋势跟随"

@dataclass
class ScreenerResult:
    """筛选结果数据类"""
    code: str
    name: str
    score: float
    criteria_met: List[str]
    technical_signals: Dict
    fundamental_data: Dict
    risk_level: str
    recommendation: str
    reason: str

class StockScreener:
    """智能股票筛选器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.historical_fetcher = HistoricalDataFetcher()
        
        # 筛选参数配置
        self.config = {
            'min_market_cap': 50,  # 最小市值(亿元)
            'min_daily_volume': 10000000,  # 最小日成交额(元)
            'max_pe_ratio': 50,  # 最大PE比率
            'min_roe': 8,  # 最小ROE(%)
            'max_debt_ratio': 70,  # 最大负债率(%)
            'min_revenue_growth': 10,  # 最小营收增长率(%)
            'rsi_oversold': 30,  # RSI超卖线
            'rsi_overbought': 70,  # RSI超买线
            'volume_surge_ratio': 2.0,  # 成交量放大倍数
            'price_change_threshold': 3.0,  # 价格变动阈值(%)
        }
    
    def screen_stocks(self, stock_pool: List[str], criteria: List[ScreenerCriteria] = None) -> List[ScreenerResult]:
        """
        筛选股票
        Args:
            stock_pool: 股票池代码列表
            criteria: 筛选标准列表，默认使用所有标准
        Returns:
            筛选结果列表，按评分排序
        """
        if criteria is None:
            criteria = list(ScreenerCriteria)
        
        results = []
        
        for code in stock_pool:
            try:
                result = self._evaluate_stock(code, criteria)
                if result and result.score > 0:
                    results.append(result)
            except Exception as e:
                self.logger.error(f"评估股票 {code} 失败: {e}")
        
        # 按评分排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def _evaluate_stock(self, code: str, criteria: List[ScreenerCriteria]) -> Optional[ScreenerResult]:
        """评估单只股票"""
        # 获取股票基础数据
        basic_data = self._get_basic_data(code)
        if not basic_data:
            return None
        
        # 获取技术指标数据
        technical_data = self._get_technical_data(code)
        
        # 获取基本面数据
        fundamental_data = self._get_fundamental_data(code)
        
        # 计算各维度评分
        scores = {}
        criteria_met = []
        
        for criterion in criteria:
            score, met = self._evaluate_criterion(criterion, basic_data, technical_data, fundamental_data)
            scores[criterion.value] = score
            if met:
                criteria_met.append(criterion.value)
        
        # 计算综合评分
        total_score = sum(scores.values()) / len(scores) if scores else 0
        
        # 风险评估
        risk_level = self._assess_risk(basic_data, technical_data, fundamental_data)
        
        # 生成投资建议
        recommendation, reason = self._generate_recommendation(total_score, criteria_met, risk_level)
        
        return ScreenerResult(
            code=code,
            name=basic_data.get('name', code),
            score=total_score,
            criteria_met=criteria_met,
            technical_signals=technical_data or {},
            fundamental_data=fundamental_data or {},
            risk_level=risk_level,
            recommendation=recommendation,
            reason=reason
        )
    
    def _evaluate_criterion(self, criterion: ScreenerCriteria, basic_data: Dict, 
                          technical_data: Dict, fundamental_data: Dict) -> Tuple[float, bool]:
        """评估单个筛选标准"""
        
        if criterion == ScreenerCriteria.TECHNICAL_BREAKOUT:
            return self._evaluate_technical_breakout(basic_data, technical_data)
        
        elif criterion == ScreenerCriteria.VOLUME_SURGE:
            return self._evaluate_volume_surge(basic_data, technical_data)
        
        elif criterion == ScreenerCriteria.MOMENTUM_STRONG:
            return self._evaluate_momentum(basic_data, technical_data)
        
        elif criterion == ScreenerCriteria.VALUE_OPPORTUNITY:
            return self._evaluate_value_opportunity(fundamental_data)
        
        elif criterion == ScreenerCriteria.GROWTH_POTENTIAL:
            return self._evaluate_growth_potential(fundamental_data)
        
        elif criterion == ScreenerCriteria.OVERSOLD_BOUNCE:
            return self._evaluate_oversold_bounce(basic_data, technical_data)
        
        elif criterion == ScreenerCriteria.TREND_FOLLOWING:
            return self._evaluate_trend_following(basic_data, technical_data)
        
        return 0.0, False
    
    def _evaluate_technical_breakout(self, basic_data: Dict, technical_data: Dict) -> Tuple[float, bool]:
        """评估技术突破"""
        score = 0.0
        met = False
        
        current_price = basic_data.get('current_price', 0)
        high_price = basic_data.get('high_price', 0)
        volume = basic_data.get('volume', 0)
        
        if current_price > 0 and high_price > 0:
            # 接近或突破今日最高价
            price_ratio = current_price / high_price
            if price_ratio >= 0.98:
                score += 30
                if price_ratio >= 1.0:
                    score += 20
                    met = True
            
            # 成交量配合
            if volume > self.config['min_daily_volume']:
                score += 20
        
        # RSI突破
        rsi = technical_data.get('rsi', 50) if technical_data else 50
        if 50 < rsi < self.config['rsi_overbought']:
            score += 30
            met = True
        
        return min(score, 100), met
    
    def _evaluate_volume_surge(self, basic_data: Dict, technical_data: Dict) -> Tuple[float, bool]:
        """评估放量突破"""
        score = 0.0
        met = False
        
        volume = basic_data.get('volume', 0)
        avg_volume = technical_data.get('avg_volume_20', 0) if technical_data else 0
        
        if volume > 0 and avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio >= self.config['volume_surge_ratio']:
                score = min(volume_ratio * 20, 80)
                met = True
            
            # 价格配合上涨
            change_percent = basic_data.get('change_percent', 0)
            if change_percent > 0:
                score += 20
        
        return min(score, 100), met
    
    def _evaluate_momentum(self, basic_data: Dict, technical_data: Dict) -> Tuple[float, bool]:
        """评估动量强度"""
        score = 0.0
        met = False
        
        change_percent = abs(basic_data.get('change_percent', 0))
        
        # 价格动量
        if change_percent >= self.config['price_change_threshold']:
            score += 40
            met = True
        
        # MACD金叉
        macd_signal = technical_data.get('macd_signal', 0) if technical_data else 0
        if macd_signal > 0:
            score += 30
        
        # 连续上涨天数
        consecutive_up = technical_data.get('consecutive_up_days', 0) if technical_data else 0
        if consecutive_up >= 3:
            score += 30
            met = True
        
        return min(score, 100), met
    
    def _evaluate_value_opportunity(self, fundamental_data: Dict) -> Tuple[float, bool]:
        """评估价值机会"""
        score = 0.0
        met = False
        
        if not fundamental_data:
            return score, met
        
        pe_ratio = fundamental_data.get('pe_ratio') or 999
        pb_ratio = fundamental_data.get('pb_ratio') or 999  
        roe = fundamental_data.get('roe') or 0
        
        # PE估值
        if 0 < pe_ratio < 15:
            score += 40
            met = True
        elif 15 <= pe_ratio < 25:
            score += 20
        
        # PB估值
        if 0 < pb_ratio < 2:
            score += 30
        
        # ROE质量
        if roe >= self.config['min_roe']:
            score += 30
        
        return min(score, 100), met
    
    def _evaluate_growth_potential(self, fundamental_data: Dict) -> Tuple[float, bool]:
        """评估成长潜力"""
        score = 0.0
        met = False
        
        if not fundamental_data:
            return score, met
        
        revenue_growth = fundamental_data.get('revenue_growth') or 0
        profit_growth = fundamental_data.get('profit_growth') or 0
        roe = fundamental_data.get('roe') or 0
        
        # 营收增长
        if revenue_growth >= self.config['min_revenue_growth']:
            score += 40
            met = True
        
        # 利润增长
        if profit_growth >= 15:
            score += 40
            met = True
        
        # ROE趋势
        if roe >= 15:
            score += 20
        
        return min(score, 100), met
    
    def _evaluate_oversold_bounce(self, basic_data: Dict, technical_data: Dict) -> Tuple[float, bool]:
        """评估超跌反弹"""
        score = 0.0
        met = False
        
        rsi = technical_data.get('rsi', 50) if technical_data else 50
        change_percent = basic_data.get('change_percent', 0)
        
        # RSI超卖后反弹
        if rsi <= self.config['rsi_oversold'] and change_percent > 0:
            score += 60
            met = True
        
        # 跌幅较大后反弹
        max_drawdown = technical_data.get('max_drawdown_20', 0) if technical_data else 0
        if max_drawdown <= -10 and change_percent > 2:
            score += 40
            met = True
        
        return min(score, 100), met
    
    def _evaluate_trend_following(self, basic_data: Dict, technical_data: Dict) -> Tuple[float, bool]:
        """评估趋势跟随"""
        score = 0.0
        met = False
        
        if not technical_data:
            return score, met
        
        ma5 = technical_data.get('ma5', 0)
        ma20 = technical_data.get('ma20', 0)
        ma60 = technical_data.get('ma60', 0)
        current_price = basic_data.get('current_price', 0)
        
        # 多头排列
        if current_price > ma5 > ma20 > ma60 > 0:
            score += 60
            met = True
        
        # 均线支撑
        if ma5 > 0 and abs(current_price - ma5) / ma5 < 0.02:
            score += 40
        
        return min(score, 100), met
    
    def _assess_risk(self, basic_data: Dict, technical_data: Dict, fundamental_data: Dict) -> str:
        """评估风险等级"""
        risk_score = 0
        
        # 波动率风险
        volatility = technical_data.get('volatility_20', 0) if technical_data else 0
        if volatility > 30:
            risk_score += 30
        elif volatility > 20:
            risk_score += 15
        
        # 流动性风险
        volume = basic_data.get('volume', 0)
        if volume < self.config['min_daily_volume']:
            risk_score += 25
        
        # 基本面风险
        if fundamental_data:
            debt_ratio = fundamental_data.get('debt_ratio') or 0
            if debt_ratio > self.config['max_debt_ratio']:
                risk_score += 20
            
            pe_ratio = fundamental_data.get('pe_ratio') or 0
            if pe_ratio > self.config['max_pe_ratio']:
                risk_score += 15
        
        # 技术面风险
        rsi = technical_data.get('rsi', 50) if technical_data else 50
        if rsi > self.config['rsi_overbought']:
            risk_score += 20
        
        if risk_score >= 50:
            return "高风险"
        elif risk_score >= 25:
            return "中风险"
        else:
            return "低风险"
    
    def _generate_recommendation(self, score: float, criteria_met: List[str], risk_level: str) -> Tuple[str, str]:
        """生成投资建议"""
        if score >= 80 and risk_level != "高风险":
            return "强烈推荐", f"综合评分{score:.1f}，满足{len(criteria_met)}个筛选条件，风险等级{risk_level}"
        elif score >= 60 and risk_level == "低风险":
            return "推荐", f"综合评分{score:.1f}，满足{len(criteria_met)}个筛选条件，风险可控"
        elif score >= 40:
            return "关注", f"综合评分{score:.1f}，有一定投资价值，需谨慎评估风险"
        else:
            return "不推荐", f"综合评分{score:.1f}，投资价值有限"
    
    def _get_basic_data(self, code: str) -> Optional[Dict]:
        """获取股票基础数据"""
        try:
            # 这里可以集成现有的StockFetcher
            from stock_fetcher import StockFetcher
            fetcher = StockFetcher()
            data = fetcher.get_stock_data([code])
            return data.get(code)
        except Exception as e:
            self.logger.error(f"获取股票 {code} 基础数据失败: {e}")
            return None
    
    def _get_technical_data(self, code: str) -> Optional[Dict]:
        """获取技术指标数据"""
        try:
            # 获取历史数据
            historical_data = self.historical_fetcher.get_historical_data(code, days=60)
            if historical_data is None or len(historical_data) == 0:
                self.logger.warning(f"无法获取股票 {code} 的历史数据，使用模拟数据")
                return self._get_mock_technical_data()
            
            # 使用简化版技术指标计算器
            from simple_technical_indicators import SimpleTechnicalIndicators
            tech_indicators = SimpleTechnicalIndicators(historical_data)
            
            # 计算各项技术指标
            rsi = tech_indicators.calculate_rsi()
            macd_data = tech_indicators.calculate_macd()
            ma_data = tech_indicators.calculate_moving_averages()
            volume_data = tech_indicators.calculate_volume_indicators()
            volatility = tech_indicators.calculate_volatility()
            
            # 获取最新值
            latest_rsi = rsi
            latest_macd_signal = 1 if macd_data['macd'] > macd_data['signal'] else -1
            latest_ma5 = ma_data['MA5']
            latest_ma20 = ma_data['MA20']
            latest_ma60 = ma_data['MA60']
            avg_volume_20 = volume_data['avg_volume_20']
            
            # 计算连续上涨天数
            consecutive_up_days = self._calculate_consecutive_up_days(historical_data)
            
            # 计算最大回撤
            max_drawdown_20 = self._calculate_max_drawdown(historical_data, 20)
            
            return {
                'rsi': float(latest_rsi),
                'macd_signal': latest_macd_signal,
                'ma5': float(latest_ma5),
                'ma20': float(latest_ma20),
                'ma60': float(latest_ma60),
                'avg_volume_20': int(avg_volume_20),
                'volatility_20': float(volatility),
                'consecutive_up_days': consecutive_up_days,
                'max_drawdown_20': max_drawdown_20
            }
            
        except Exception as e:
            self.logger.error(f"计算股票 {code} 技术指标失败: {e}")
            return self._get_mock_technical_data()
    
    def _get_mock_technical_data(self) -> Dict:
        """获取模拟技术指标数据"""
        return {
            'rsi': 55.0,
            'macd_signal': 1,
            'ma5': 10.5,
            'ma20': 10.2,
            'ma60': 9.8,
            'avg_volume_20': 50000000,
            'volatility_20': 15.0,
            'consecutive_up_days': 2,
            'max_drawdown_20': -5.2
        }
    
    def _calculate_consecutive_up_days(self, data) -> int:
        """计算连续上涨天数"""
        try:
            consecutive_days = 0
            for i in range(len(data) - 1, 0, -1):
                if data[i]['close'] > data[i-1]['close']:
                    consecutive_days += 1
                else:
                    break
            return consecutive_days
        except:
            return 0
    
    def _calculate_max_drawdown(self, data, period: int) -> float:
        """计算最大回撤"""
        try:
            if len(data) < period:
                period = len(data)
            
            recent_data = data[-period:]
            closes = [item['close'] for item in recent_data]
            
            if not closes:
                return 0.0
                
            peak = max(closes)
            trough = min(closes)
            
            if peak > 0:
                drawdown = (trough - peak) / peak * 100
                return drawdown
            return 0.0
        except:
            return 0.0
    
    def _get_fundamental_data(self, code: str) -> Optional[Dict]:
        """获取基本面数据"""
        try:
            # 尝试获取真实基本面数据
            fundamental_data = self.historical_fetcher.get_fundamental_data(code)
            if fundamental_data:
                return {
                    'pe_ratio': fundamental_data.get('pe_ratio') or 18.5,
                    'pb_ratio': fundamental_data.get('pb_ratio') or 1.8,
                    'roe': fundamental_data.get('roe') or 12.5,
                    'debt_ratio': fundamental_data.get('debt_ratio') or 45.0,
                    'revenue_growth': fundamental_data.get('revenue_growth') or 15.2,
                    'profit_growth': fundamental_data.get('profit_growth') or 18.7,
                    'market_cap': fundamental_data.get('market_cap') or 150.0
                }
        except Exception as e:
            self.logger.error(f"获取股票 {code} 基本面数据失败: {e}")
        
        # 返回模拟数据作为备用
        return {
            'pe_ratio': 18.5,
            'pb_ratio': 1.8,
            'roe': 12.5,
            'debt_ratio': 45.0,
            'revenue_growth': 15.2,
            'profit_growth': 18.7,
            'market_cap': 150.0
        }
    
    def get_recommended_stocks(self, market: str = "A股", top_n: int = 20) -> List[ScreenerResult]:
        """获取推荐股票列表"""
        # 这里应该从股票池中筛选
        # 暂时使用示例股票池
        if market == "A股":
            stock_pool = ["000001", "000002", "600036", "600519", "000858"]
        else:
            stock_pool = ["00700", "09988", "01810", "02318"]
        
        criteria = [
            ScreenerCriteria.TECHNICAL_BREAKOUT,
            ScreenerCriteria.VOLUME_SURGE,
            ScreenerCriteria.MOMENTUM_STRONG,
            ScreenerCriteria.VALUE_OPPORTUNITY
        ]
        
        results = self.screen_stocks(stock_pool, criteria)
        return results[:top_n]
    
    def format_screening_report(self, results: List[ScreenerResult]) -> str:
        """格式化筛选报告"""
        if not results:
            return "📊 智能筛选结果：暂无符合条件的股票"
        
        lines = ["🎯 智能股票筛选报告\n"]
        lines.append(f"📈 共筛选出 {len(results)} 只优质股票\n")
        
        for i, result in enumerate(results[:10], 1):
            lines.append(f"{i}. {result.name}({result.code})")
            lines.append(f"   📊 综合评分: {result.score:.1f}/100")
            lines.append(f"   🎯 投资建议: {result.recommendation}")
            lines.append(f"   ⚠️  风险等级: {result.risk_level}")
            lines.append(f"   ✅ 符合条件: {', '.join(result.criteria_met[:3])}")
            lines.append(f"   💡 推荐理由: {result.reason}")
            lines.append("")
        
        lines.append("⚠️ 以上分析仅供参考，投资有风险，决策需谨慎！")
        return "\n".join(lines)