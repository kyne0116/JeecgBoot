#!/bin/bash
# 上游项目同步脚本
# 用于同步 Context Engineering 项目

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_DEV_DIR="$(dirname "$SCRIPT_DIR")"
UPSTREAM_DIR="$CONTEXT_DEV_DIR/upstream"

echo "🔄 开始上游项目同步..."

# 同步 Context Engineering
if [[ -d "$UPSTREAM_DIR/context-engineering" ]]; then
    echo "📚 同步 Context Engineering..."
    cd "$UPSTREAM_DIR/context-engineering"
    if git pull origin main; then
        echo "✅ Context Engineering 同步完成"
    else
        echo "⚠️ Context Engineering 同步失败，可能是网络问题"
    fi
else
    echo "❌ Context Engineering 目录不存在"
    echo "💡 运行 'bash ContextDev/jeecg-ai-setup.sh' 来初始化环境"
fi

echo "✅ 上游项目同步完成"