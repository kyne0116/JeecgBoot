#!/bin/bash
# SuperClaude Framework 独立安装脚本

set -e

echo "🤖 SuperClaude Framework 独立安装..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    exit 1
fi

# 安装 SuperClaude 包
if command -v uv &> /dev/null; then
    echo "📦 使用 uv 安装 SuperClaude..."
    uv pip install SuperClaude
else
    echo "📦 使用 pip 安装 SuperClaude..."
    pip3 install SuperClaude
fi

# 验证安装
python3 -c "
try:
    import SuperClaude
    import pkg_resources
    try:
        version = pkg_resources.get_distribution('SuperClaude').version
        print(f'✅ SuperClaude {version} 安装成功')
    except pkg_resources.DistributionNotFound:
        print('✅ SuperClaude (版本未知) 安装成功')
except Exception as e:
    print(f'❌ SuperClaude 安装失败: {e}')
    exit(1)
"

echo "✅ SuperClaude Framework 安装完成"
