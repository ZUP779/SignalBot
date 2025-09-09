import requests
import json
import logging
from datetime import datetime
from typing import Dict, List
from config import WECHAT_WEBHOOK_URL

class WeChatNotifier:
    """企业微信通知器"""
    
    def __init__(self):
        self.webhook_url = WECHAT_WEBHOOK_URL
        self.logger = logging.getLogger(__name__)
    
    def send_stock_report(self, stock_data: Dict[str, Dict]) -> bool:
        """
        发送股票监控报告
        Args:
            stock_data: 股票数据字典
        Returns:
            发送是否成功
        """
        if not self.webhook_url:
            self.logger.error("企业微信Webhook URL未配置")
            return False
        
        if not stock_data:
            self.logger.warning("没有股票数据需要发送")
            return False
        
        try:
            message = self._format_stock_message(stock_data)
            return self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"发送股票报告失败: {e}")
            return False
    
    def _format_stock_message(self, stock_data: Dict[str, Dict]) -> str:
        """格式化股票消息"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        message_lines = [f"📈 股票监控 - {now}\n"]
        
        for code, data in stock_data.items():
            try:
                name = data['name']
                current = data['current_price']
                change = data['change']
                change_percent = data['change_percent']
                open_price = data['open_price']
                high_price = data['high_price']
                low_price = data['low_price']
                currency = data['currency']
                market = data['market']
                
                # 涨跌状态图标
                if change > 0:
                    status_icon = "🔴"
                    change_icon = "↑"
                elif change < 0:
                    status_icon = "🟢"
                    change_icon = "↓"
                else:
                    status_icon = "⚪"
                    change_icon = "→"
                
                # 格式化消息
                stock_line = (
                    f"{status_icon} {name}({code}) [{market}]\n"
                    f"当前: {currency}{current:.2f} {change_icon}{change:+.2f}({change_percent:+.2f}%)\n"
                    f"今日: 开盘{currency}{open_price:.2f} 最高{currency}{high_price:.2f} 最低{currency}{low_price:.2f}\n"
                )
                
                message_lines.append(stock_line)
                
            except Exception as e:
                self.logger.error(f"格式化股票 {code} 消息失败: {e}")
                continue
        
        return "\n".join(message_lines)
    
    def _send_message(self, message: str) -> bool:
        """发送消息到企业微信"""
        try:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    self.logger.info("企业微信消息发送成功")
                    return True
                else:
                    self.logger.error(f"企业微信消息发送失败: {result}")
                    return False
            else:
                self.logger.error(f"企业微信API请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送企业微信消息异常: {e}")
            return False
    
    def send_signal_alert(self, signal_message: str) -> bool:
        """发送信号预警消息"""
        return self._send_message(signal_message)
    
    def send_test_message(self) -> bool:
        """发送测试消息"""
        test_message = f"🤖 SignalBot 测试消息\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self._send_message(test_message)