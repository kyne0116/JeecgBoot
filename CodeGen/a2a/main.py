#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeGen Expert A2A Service Main Entry Point
基于虚拟环境的 Python 服务，运行在端口 8888
"""

import sys
import signal
import logging
import threading
import time
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入Flask应用
try:
    from a2a_flask_app import app
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量用于优雅关闭
shutdown_event = threading.Event()
server_thread = None

def signal_handler(signum, frame):
    """信号处理器 - 处理 Ctrl+C (SIGINT) 和 SIGTERM"""
    signal_names = {
        signal.SIGINT: "SIGINT (Ctrl+C)",
        signal.SIGTERM: "SIGTERM"
    }
    signal_name = signal_names.get(signum, f"Signal {signum}")

    logger.info(f"\n🛑 接收到 {signal_name} 信号，正在优雅关闭服务...")
    shutdown_event.set()

    # 给服务一些时间来处理正在进行的请求
    logger.info("⏳ 等待当前请求完成...")
    time.sleep(1)

    logger.info("✅ 服务已安全停止")
    sys.exit(0)

def check_port_available(host, port):
    """检查端口是否可用"""
    import socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # 不设置 SO_REUSEADDR，这样可以更准确地检测端口占用
            sock.bind((host, port))
            return True
    except OSError as e:
        # 端口被占用的错误码
        if e.errno in [98, 10048]:  # Linux: EADDRINUSE, Windows: WSAEADDRINUSE
            logger.error(f"❌ 端口 {port} 已被占用")
            return False
        else:
            logger.error(f"端口检查异常: {e} (errno: {e.errno})")
            return False

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='CodeGen Expert A2A Service')
    parser.add_argument('--port', type=int, default=8888, help='服务端口')
    parser.add_argument('--host', default='0.0.0.0', help='服务主机')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')

    args = parser.parse_args()

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)  # 终止信号

    # 检查端口是否可用
    if not check_port_available(args.host, args.port):
        logger.error(f"❌ 端口 {args.port} 已被占用，请检查是否有其他服务在运行")
        logger.info(f"💡 提示: 使用 'netstat -ano | findstr :{args.port}' 查看占用进程")
        sys.exit(1)

    # 构建服务 URL
    if args.host == '0.0.0.0':
        display_host = '127.0.0.1'  # 使用 localhost 显示更友好
    else:
        display_host = args.host

    base_url = f"http://{display_host}:{args.port}"

    logger.info("=" * 70)
    logger.info("🚀 CodeGen Expert A2A Service 启动中...")
    logger.info("=" * 70)
    logger.info(f"📡 监听地址: {base_url}")
    logger.info("")
    logger.info("🔍 核心端点:")
    logger.info(f"   📋 Agent Card (服务发现): {base_url}/.well-known/agent.json")
    logger.info(f"   💚 健康检查: {base_url}/health")
    logger.info(f"   📊 服务状态: {base_url}/codegen/status")
    logger.info(f"   🤖 A2A 协议: {base_url}/codegen/a2a")
    logger.info("")
    logger.info("🧪 测试端点:")
    logger.info(f"   🔧 变量提取: {base_url}/codegen/variables/extract")
    logger.info(f"   ⚙️  配置生成: {base_url}/codegen/config/generate")
    logger.info("")
    logger.info("💡 快速验证:")
    logger.info(f"   curl {base_url}/.well-known/agent.json")
    logger.info("=" * 70)

    # 验证路由注册
    logger.info("🔍 验证路由注册...")
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    if '/.well-known/agent.json' in routes:
        logger.info("✅ AgentCard 路由已注册")
    else:
        logger.error("❌ AgentCard 路由未找到")
        logger.info(f"已注册的路由: {routes}")

    try:
        logger.info("🌟 服务启动成功，等待请求...")
        logger.info("💡 按 Ctrl+C 优雅停止服务")
        logger.info("")

        # 启动 Flask 应用
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True,
            use_reloader=False  # 禁用重载器避免多进程问题
        )

    except KeyboardInterrupt:
        # 这个异常会被信号处理器处理，但保留作为备用
        logger.info("\n👋 服务已通过 KeyboardInterrupt 停止")
    except OSError as e:
        if "Address already in use" in str(e) or "地址已在使用" in str(e):
            logger.error(f"❌ 端口 {args.port} 被占用: {e}")
            logger.info(f"💡 提示: 使用 'netstat -ano | findstr :{args.port}' 查看占用进程")
        else:
            logger.error(f"❌ 网络错误: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 服务运行异常: {e}")
        sys.exit(1)
    finally:
        logger.info("🔄 清理资源...")
        shutdown_event.set()



if __name__ == '__main__':
    main()
