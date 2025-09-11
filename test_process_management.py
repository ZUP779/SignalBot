#!/usr/bin/env python3
"""
测试进程管理功能
"""
import time
import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时"

def test_process_management():
    """测试进程管理功能"""
    print("🧪 测试进程管理功能\n")
    
    base_cmd = "python main.py"
    
    # 1. 测试状态查看（应该显示未运行）
    print("📊 1. 测试初始状态")
    success, stdout, stderr = run_command(f"{base_cmd} ps")
    if success and "未运行" in stdout:
        print("✅ 初始状态正确：未运行")
    else:
        print("❌ 初始状态异常")
        print(f"输出: {stdout}")
    
    # 2. 测试启动守护进程
    print("\n🚀 2. 测试启动守护进程")
    success, stdout, stderr = run_command(f"{base_cmd} daemon")
    if success and "守护进程已启动" in stdout:
        print("✅ 守护进程启动成功")
        time.sleep(2)  # 等待进程完全启动
    else:
        print("❌ 守护进程启动失败")
        print(f"输出: {stdout}")
        print(f"错误: {stderr}")
        return
    
    # 3. 测试状态查看（应该显示运行中）
    print("\n📊 3. 测试运行状态")
    success, stdout, stderr = run_command(f"{base_cmd} ps")
    if success and "运行中" in stdout:
        print("✅ 运行状态正确：运行中")
    else:
        print("❌ 运行状态异常")
        print(f"输出: {stdout}")
    
    # 4. 测试添加股票（应该自动重启）
    print("\n➕ 4. 测试添加股票自动重启")
    success, stdout, stderr = run_command(f"{base_cmd} add 002415 --name '海康威视'")
    if success and "自动重启" in stdout:
        print("✅ 添加股票自动重启成功")
        time.sleep(2)  # 等待重启完成
    else:
        print("❌ 添加股票自动重启失败")
        print(f"输出: {stdout}")
    
    # 5. 测试移除股票（应该自动重启）
    print("\n➖ 5. 测试移除股票自动重启")
    success, stdout, stderr = run_command(f"{base_cmd} remove 002415")
    if success and "自动重启" in stdout:
        print("✅ 移除股票自动重启成功")
        time.sleep(2)  # 等待重启完成
    else:
        print("❌ 移除股票自动重启失败")
        print(f"输出: {stdout}")
    
    # 6. 测试日志查看
    print("\n📋 6. 测试日志查看")
    success, stdout, stderr = run_command(f"{base_cmd} logs --lines 5")
    if success and "日志" in stdout:
        print("✅ 日志查看成功")
    else:
        print("❌ 日志查看失败")
        print(f"输出: {stdout}")
    
    # 7. 测试重启
    print("\n🔄 7. 测试手动重启")
    success, stdout, stderr = run_command(f"{base_cmd} restart")
    if success and "重启" in stdout:
        print("✅ 手动重启成功")
        time.sleep(2)  # 等待重启完成
    else:
        print("❌ 手动重启失败")
        print(f"输出: {stdout}")
    
    # 8. 测试停止
    print("\n🛑 8. 测试停止守护进程")
    success, stdout, stderr = run_command(f"{base_cmd} stop")
    if success and "已停止" in stdout:
        print("✅ 停止守护进程成功")
    else:
        print("❌ 停止守护进程失败")
        print(f"输出: {stdout}")
    
    # 9. 测试清理
    print("\n🧹 9. 测试清理残留文件")
    success, stdout, stderr = run_command(f"{base_cmd} cleanup")
    if success:
        print("✅ 清理成功")
    else:
        print("❌ 清理失败")
        print(f"输出: {stdout}")
    
    # 10. 最终状态检查
    print("\n📊 10. 最终状态检查")
    success, stdout, stderr = run_command(f"{base_cmd} ps")
    if success and "未运行" in stdout:
        print("✅ 最终状态正确：未运行")
    else:
        print("❌ 最终状态异常")
        print(f"输出: {stdout}")

def test_file_management():
    """测试文件管理"""
    print("\n📁 测试文件管理")
    
    pid_file = Path("signalbot.pid")
    log_file = Path("signalbot_daemon.log")
    
    # 检查文件是否被正确清理
    if not pid_file.exists():
        print("✅ PID文件已清理")
    else:
        print("❌ PID文件未清理")
    
    if log_file.exists():
        log_size = log_file.stat().st_size
        print(f"📋 日志文件大小: {log_size} 字节")
    else:
        print("📋 无日志文件")

def main():
    """主函数"""
    print("🤖 SignalBot 进程管理功能测试")
    print("=" * 50)
    
    try:
        test_process_management()
        test_file_management()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成")
        
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        # 确保清理
        run_command("python main.py stop")
        run_command("python main.py cleanup")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        # 确保清理
        run_command("python main.py stop")
        run_command("python main.py cleanup")

if __name__ == '__main__':
    main()