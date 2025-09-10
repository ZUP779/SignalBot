import os
from dotenv import load_dotenv

load_dotenv()

# 企业微信配置
WECHAT_WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL', '')

# 数据库配置
DATABASE_PATH = 'stocks.db'

# 股票数据源配置
SINA_API_BASE = 'https://hq.sinajs.cn/list='
TENCENT_API_BASE = 'https://qt.gtimg.cn/q='

# SignalBot 配置
UPDATE_INTERVAL_HOURS = 1

# 推送策略配置
ALWAYS_SEND_REPORT = os.getenv('ALWAYS_SEND_REPORT', 'true').lower() == 'true'
SEND_SIGNAL_ALERTS = os.getenv('SEND_SIGNAL_ALERTS', 'true').lower() == 'true'

# 开市时间检查配置
CHECK_MARKET_HOURS = os.getenv('CHECK_MARKET_HOURS', 'true').lower() == 'true'

# 信号检测配置
PRICE_CHANGE_THRESHOLD = float(os.getenv('PRICE_CHANGE_THRESHOLD', '5.0'))
VOLUME_SPIKE_THRESHOLD = float(os.getenv('VOLUME_SPIKE_THRESHOLD', '2.0'))

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'signalbot.log'