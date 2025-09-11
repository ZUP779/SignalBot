"""
SignalBot 进程管理器
自动管理监控进程的启动、停止和重启
"""
import os
import sys
import time
import signal
import psutil
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class ProcessManager:
    """SignalBot 进程管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pid_file = Path("signalbot.pid")
        self.log_file = Path("signalbot_daemon.log")
        self.script_path = Path(__file__).parent / "main.py"
        
    def get_running_process(self) -> Optional[psutil.Process]:
        """获取正在运行的SignalBot进程"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # 检查进程是否还在运行
                if psutil.pid_exists(pid):
                    proc = psutil.Process(pid)
                    # 验证是否是SignalBot进程
                    if 'python' in proc.name().lower() and 'main.py' in ' '.join(proc.cmdline()):
                        return proc
                
                # PID文件存在但进程不存在，清理PID文件
                self.pid_file.unlink()
                
        except (FileNotFoundError, ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return None
    
    def is_running(self) -> bool:
        """检查SignalBot是否正在运行"""
        return self.get_running_process() is not None
    
    def start_daemon(self) -> bool:
        """启动SignalBot守护进程"""
        if self.is_running():
            print("⚠️  SignalBot 已在运行中")
            return False
        
        try:
            # 启动守护进程
            cmd = [sys.executable, str(self.script_path), "start"]
            
            # 使用subprocess.Popen启动后台进程
            with open(self.log_file, 'a') as log_f:
                process = subprocess.Popen(
                    cmd,
                    stdout=log_f,
                    stderr=log_f,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True  # 创建新的进程组
                )
            
            # 保存PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # 等待一下确保进程启动
            time.sleep(2)
            
            if self.is_running():
                print(f"✅ SignalBot 守护进程已启动 (PID: {process.pid})")
                print(f"📋 日志文件: {self.log_file}")
                return True
            else:
                print("❌ SignalBot 启动失败")
                return False
                
        except Exception as e:
            self.logger.error(f"启动守护进程失败: {e}")
            print(f"❌ 启动失败: {e}")
            return False
    
    def stop_daemon(self) -> bool:
        """停止SignalBot守护进程"""
        process = self.get_running_process()
        if not process:
            print("ℹ️  SignalBot 未在运行")
            return True
        
        try:
            pid = process.pid
            print(f"🛑 正在停止 SignalBot (PID: {pid})...")
            
            # 优雅停止
            process.terminate()
            
            # 等待进程结束
            try:
                process.wait(timeout=10)
                print("✅ SignalBot 已停止")
            except psutil.TimeoutExpired:
                # 强制杀死
                print("⚠️  进程未响应，强制停止...")
                process.kill()
                process.wait(timeout=5)
                print("✅ SignalBot 已强制停止")
            
            # 清理PID文件
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            return True
            
        except Exception as e:
            self.logger.error(f"停止进程失败: {e}")
            print(f"❌ 停止失败: {e}")
            return False
    
    def restart_daemon(self) -> bool:
        """重启SignalBot守护进程"""
        print("🔄 正在重启 SignalBot...")
        
        # 停止现有进程
        if not self.stop_daemon():
            return False
        
        # 等待一下
        time.sleep(1)
        
        # 启动新进程
        return self.start_daemon()
    
    def get_status(self) -> Dict[str, Any]:
        """获取SignalBot状态信息"""
        process = self.get_running_process()
        
        if not process:
            return {
                'running': False,
                'pid': None,
                'start_time': None,
                'cpu_percent': None,
                'memory_mb': None,
                'status': 'stopped'
            }
        
        try:
            return {
                'running': True,
                'pid': process.pid,
                'start_time': datetime.fromtimestamp(process.create_time()),
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'status': process.status()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {
                'running': False,
                'pid': None,
                'start_time': None,
                'cpu_percent': None,
                'memory_mb': None,
                'status': 'error'
            }
    
    def show_status(self):
        """显示SignalBot状态"""
        status = self.get_status()
        
        print("📊 SignalBot 状态:")
        print("-" * 40)
        
        if status['running']:
            print(f"🟢 状态: 运行中")
            print(f"🆔 进程ID: {status['pid']}")
            print(f"⏰ 启动时间: {status['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 计算运行时长
            runtime = datetime.now() - status['start_time']
            hours = int(runtime.total_seconds() // 3600)
            minutes = int((runtime.total_seconds() % 3600) // 60)
            print(f"⏱️  运行时长: {hours}小时{minutes}分钟")
            
            print(f"💾 内存使用: {status['memory_mb']:.1f} MB")
            print(f"🔄 CPU使用: {status['cpu_percent']:.1f}%")
        else:
            print(f"🔴 状态: 未运行")
        
        # 显示日志文件信息
        if self.log_file.exists():
            log_size = self.log_file.stat().st_size / 1024
            print(f"📋 日志文件: {self.log_file} ({log_size:.1f} KB)")
    
    def show_logs(self, lines: int = 20):
        """显示最近的日志"""
        if not self.log_file.exists():
            print("📋 暂无日志文件")
            return
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
            
            print(f"📋 最近 {min(lines, len(log_lines))} 行日志:")
            print("-" * 60)
            
            for line in log_lines[-lines:]:
                print(line.rstrip())
                
        except Exception as e:
            print(f"❌ 读取日志失败: {e}")
    
    def auto_restart_on_change(self):
        """监控股票列表变化并自动重启"""
        from stock_manager import StockManager
        
        print("👁️  启动自动重启监控...")
        print("📝 监控股票列表变化，自动重启SignalBot")
        print("按 Ctrl+C 停止监控")
        
        stock_manager = StockManager()
        last_stock_list = set(stock_manager.get_active_stocks())
        last_check_time = datetime.now()
        
        try:
            while True:
                time.sleep(5)  # 每5秒检查一次
                
                try:
                    current_stock_list = set(stock_manager.get_active_stocks())
                    
                    # 检查股票列表是否有变化
                    if current_stock_list != last_stock_list:
                        added = current_stock_list - last_stock_list
                        removed = last_stock_list - current_stock_list
                        
                        print(f"\n🔄 检测到股票列表变化:")
                        if added:
                            print(f"  ➕ 新增: {', '.join(added)}")
                        if removed:
                            print(f"  ➖ 移除: {', '.join(removed)}")
                        
                        print("🔄 自动重启SignalBot...")
                        
                        if self.restart_daemon():
                            print("✅ SignalBot 已自动重启")
                        else:
                            print("❌ 自动重启失败")
                        
                        last_stock_list = current_stock_list
                        last_check_time = datetime.now()
                    
                    # 每分钟显示一次状态
                    if (datetime.now() - last_check_time).total_seconds() > 60:
                        print(f"💓 监控中... ({datetime.now().strftime('%H:%M:%S')})")
                        last_check_time = datetime.now()
                        
                except Exception as e:
                    self.logger.error(f"监控过程中出错: {e}")
                    time.sleep(10)  # 出错时等待更长时间
                    
        except KeyboardInterrupt:
            print("\n👋 停止自动重启监控")
    
    def cleanup(self):
        """清理残留文件"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                print("🧹 已清理PID文件")
            
            # 可选：清理日志文件
            # if self.log_file.exists():
            #     self.log_file.unlink()
            #     print("🧹 已清理日志文件")
                
        except Exception as e:
            print(f"❌ 清理失败: {e}")

def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n收到信号 {signum}，正在优雅退出...")
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)