#!/usr/bin/env python3
"""
AI-PPT System 状态检查脚本
System status checker for AI-PPT System
"""

import requests
import json
import sys
import time
from datetime import datetime

def check_service(url, name, timeout=5):
    """检查服务状态"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, response.json() if 'application/json' in response.headers.get('content-type', '') else response.text[:100]
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "连接被拒绝"
    except requests.exceptions.Timeout:
        return False, "连接超时"
    except Exception as e:
        return False, str(e)

def format_status(is_ok, message):
    """格式化状态信息"""
    status_icon = "✅" if is_ok else "❌"
    return f"{status_icon} {message}"

def main():
    print("🔍 AI-PPT System 状态检查")
    print("=" * 40)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查后端健康状态
    print("🔧 后端服务检查:")
    backend_ok, backend_data = check_service("http://localhost:8000/health", "Backend Health")
    print(f"  {format_status(backend_ok, '健康检查')}")
    
    if backend_ok and isinstance(backend_data, dict):
        print(f"    版本: {backend_data.get('version', 'N/A')}")
        print(f"    状态: {backend_data.get('status', 'N/A')}")
        print(f"    AI就绪: {backend_data.get('ai_ready', False)}")
        print(f"    已处理操作: {backend_data.get('operations_processed', 0)}")
    
    # 检查前端服务
    print("\n🌐 前端服务检查:")
    frontend_ok, frontend_data = check_service("http://localhost:3000", "Frontend")
    print(f"  {format_status(frontend_ok, '前端可访问性')}")
    
    # 检查API端点
    print("\n📡 API端点检查:")
    api_endpoints = [
        ("/api/operations/stats", "操作统计"),
        ("/api/ai/metrics", "AI指标"),
        ("/docs", "API文档")
    ]
    
    for endpoint, name in api_endpoints:
        api_ok, api_data = check_service(f"http://localhost:8000{endpoint}", name)
        print(f"  {format_status(api_ok, name)}")
    
    # 检查WebSocket连接
    print("\n🔌 WebSocket检查:")
    try:
        import websocket
        ws = websocket.create_connection("ws://localhost:8000/ws", timeout=3)
        ws.close()
        print("  ✅ WebSocket连接")
    except ImportError:
        print("  ⚠️  websocket-client未安装，跳过WebSocket检查")
    except Exception as e:
        print(f"  ❌ WebSocket连接失败: {e}")
    
    # 系统资源检查
    print("\n💻 系统资源:")
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"  CPU使用率: {cpu_percent:.1f}%")
        print(f"  内存使用: {memory.percent:.1f}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)")
        print(f"  磁盘使用: {disk.percent:.1f}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)")
    except ImportError:
        print("  ⚠️  psutil未安装，跳过系统资源检查")
    
    # 数据库检查
    print("\n🗄️  数据库检查:")
    import os
    db_path = "backend/ai_ppt_system.db"
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path)
        print(f"  ✅ 数据库文件存在 ({db_size // 1024}KB)")
    else:
        print("  ❌ 数据库文件不存在")
    
    # 总体状态
    print("\n📊 总体状态:")
    overall_ok = backend_ok and frontend_ok
    print(f"  {format_status(overall_ok, '系统整体状态')}")
    
    if overall_ok:
        print("\n🎉 系统运行正常！")
        print("🌐 前端地址: http://localhost:3000")
        print("🔧 后端地址: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
    else:
        print("\n⚠️  系统存在问题，请检查服务状态")
        sys.exit(1)

if __name__ == "__main__":
    main()