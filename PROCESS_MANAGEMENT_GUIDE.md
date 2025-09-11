# SignalBot 进程管理指南

## 🤖 自动化进程管理

SignalBot 现在支持完全自动化的进程管理，无需手动杀掉和重启监控进程。

## 🚀 快速开始

### 1. 启动后台监控
```bash
# 启动守护进程
python main.py daemon

# 查看运行状态
python main.py ps
```

### 2. 管理股票列表
```bash
# 添加股票（自动重启监控）
python main.py add 000001 --name "平安银行"

# 移除股票（自动重启监控）
python main.py remove 000001

# 批量添加指数（自动重启监控）
python main.py add-indices
```

### 3. 监控进程状态
```bash
# 查看详细状态
python main.py ps

# 查看最近日志
python main.py logs --lines 50

# 重启进程
python main.py restart

# 停止进程
python main.py stop
```

## 📋 命令详解

### 守护进程管理

| 命令 | 功能 | 说明 |
|------|------|------|
| `daemon` | 启动后台守护进程 | 在后台运行，不占用终端 |
| `stop` | 停止守护进程 | 优雅停止，保存状态 |
| `restart` | 重启守护进程 | 停止后重新启动 |
| `ps` | 查看进程状态 | 显示PID、内存、CPU等信息 |

### 日志管理

| 命令 | 功能 | 说明 |
|------|------|------|
| `logs` | 查看日志 | 默认显示最近20行 |
| `logs --lines 50` | 查看更多日志 | 显示最近50行 |

### 高级功能

| 命令 | 功能 | 说明 |
|------|------|------|
| `monitor` | 自动重启监控 | 监控股票列表变化，自动重启 |
| `cleanup` | 清理残留文件 | 清理PID文件等 |

## 🔄 自动重启机制

### 触发条件
以下操作会自动重启监控进程（如果正在运行）：

1. **添加股票**: `python main.py add <code>`
2. **移除股票**: `python main.py remove <code>`
3. **批量添加指数**: `python main.py add-indices`

### 工作流程
```
用户执行操作 → 检测进程状态 → 自动重启 → 应用新配置
```

### 示例输出
```bash
$ python main.py add 000001 --name "平安银行"
🔍 正在添加股票: 000001
✅ 成功添加股票: 000001 平安银行 [A股]

🔄 检测到监控进程正在运行，自动重启以应用更改...
🔄 正在重启 SignalBot...
🛑 正在停止 SignalBot (PID: 12345)...
✅ SignalBot 已停止
✅ SignalBot 守护进程已启动 (PID: 12346)
📋 日志文件: signalbot_daemon.log
✅ 监控进程已自动重启
```

## 📊 进程状态监控

### 状态信息
```bash
$ python main.py ps
📊 SignalBot 状态:
----------------------------------------
🟢 状态: 运行中
🆔 进程ID: 12346
⏰ 启动时间: 2025-09-11 15:58:59
⏱️  运行时长: 2小时15分钟
💾 内存使用: 25.3 MB
🔄 CPU使用: 0.1%
📋 日志文件: signalbot_daemon.log (2.5 KB)
```

### 日志查看
```bash
$ python main.py logs --lines 10
📋 最近 10 行日志:
------------------------------------------------------------
2025-09-11 15:58:59,792 - __main__ - INFO - 启动股票监控定时任务，每 1 小时执行一次
2025-09-11 16:58:59,845 - __main__ - INFO - 🤖 SignalBot 开始智能监控任务
2025-09-11 16:59:05,123 - __main__ - INFO - 📊 发送监控报告: 6 只股票, 4 个指数
2025-09-11 16:59:05,124 - __main__ - INFO - ✅ SignalBot 任务完成
```

## 🛠️ 高级用法

### 自动重启监控
如果你经常修改股票列表，可以启动自动重启监控：

```bash
# 启动自动重启监控
python main.py monitor
```

这会监控股票列表的变化，自动重启SignalBot，无需手动干预。

### 故障排除

#### 进程无法启动
```bash
# 清理残留文件
python main.py cleanup

# 重新启动
python main.py daemon
```

#### 进程状态异常
```bash
# 强制停止
python main.py stop

# 查看日志
python main.py logs --lines 50

# 重新启动
python main.py daemon
```

## 💡 最佳实践

### 1. 推荐工作流程
```bash
# 1. 启动后台监控
python main.py daemon

# 2. 配置股票列表（自动重启）
python main.py add-indices
python main.py add 000001 --name "平安银行"

# 3. 定期检查状态
python main.py ps
python main.py logs
```

### 2. 生产环境部署
```bash
# 启动守护进程
python main.py daemon

# 设置定时检查（可选）
# 在crontab中添加：
# */30 * * * * cd /path/to/SignalBot && python main.py ps > /dev/null
```

### 3. 开发调试
```bash
# 使用前台模式便于调试
python main.py run

# 或者查看实时日志
python main.py daemon
tail -f signalbot_daemon.log
```

## 🔧 技术细节

### 进程管理
- 使用 `psutil` 库进行进程管理
- PID文件存储在 `signalbot.pid`
- 日志文件存储在 `signalbot_daemon.log`

### 自动重启逻辑
- 检测进程是否运行
- 优雅停止现有进程
- 启动新进程
- 验证启动成功

### 安全性
- 进程隔离，避免冲突
- 优雅停止，保护数据
- 错误处理，避免僵尸进程

## 🎯 总结

通过自动化进程管理，SignalBot 现在可以：

✅ **无缝更新** - 修改股票列表后自动应用  
✅ **后台运行** - 守护进程模式，不占用终端  
✅ **状态监控** - 实时查看运行状态和资源使用  
✅ **日志管理** - 完整的运行日志记录  
✅ **故障恢复** - 自动处理异常情况  

这大大提升了使用体验，让股票监控变得更加便捷和可靠！