# 股票名称自动获取功能

## 功能说明

现在添加股票代码时，系统会自动从API获取股票名称，无需手动输入。

## 使用方法

### 1. 添加股票（自动获取名称）
```bash
python main.py add 000001
# 输出: ✅ 成功添加股票: 000001 平安银行 [A股]

python main.py add 00700
# 输出: ✅ 成功添加股票: 00700 腾讯控股 [港股]
```

### 2. 添加股票（手动指定名称）
```bash
python main.py add 600036 --name "招商银行"
# 输出: ✅ 成功添加股票: 600036 招商银行 [A股]
```

### 3. 更新现有股票名称
```bash
python main.py update-names
# 会自动更新所有没有名称或名称为"未知"的股票
```

## 支持的市场

- **A股**: 使用腾讯财经API (qt.gtimg.cn)
- **港股**: 使用腾讯财经API (qt.gtimg.cn)

## 技术实现

1. **StockFetcher类新增方法**:
   - `get_stock_name(code)`: 专门获取股票名称

2. **StockManager类增强**:
   - `add_stock()` 方法支持自动获取名称
   - 如果未提供名称，自动调用API获取

3. **命令行界面改进**:
   - 添加 `update-names` 命令
   - 优化添加股票时的用户体验

## API说明

- A股使用腾讯财经API: `https://qt.gtimg.cn/q=sh{code}` 或 `https://qt.gtimg.cn/q=sz{code}`
- 港股使用腾讯财经API: `https://qt.gtimg.cn/q=hk{code}`
- 自动判断市场类型（6开头为沪市，其他为深市；5位数字为港股）