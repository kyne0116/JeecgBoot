#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeGen Expert A2A Service Main Entry Point
基于虚拟环境的 Python 服务，运行在端口 8888
"""

import sys
import logging
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

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='CodeGen Expert A2A Service')
    parser.add_argument('--port', type=int, default=8888, help='服务端口')
    parser.add_argument('--host', default='0.0.0.0', help='服务主机')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')

    args = parser.parse_args()

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
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("\n👋 服务已停止")
    except Exception as e:
        logger.error(f"❌ 服务运行异常: {e}")
        sys.exit(1)



if __name__ == '__main__':
    main()
