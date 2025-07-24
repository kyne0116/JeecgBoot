#!/bin/bash
# 上游项目同步脚本
# 用于同步 Context Engineering 和 SuperClaude Framework

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_DEV_DIR="$(dirname "$SCRIPT_DIR")"
UPSTREAM_DIR="$CONTEXT_DEV_DIR/upstream"

echo "🔄 开始上游项目同步..."

# 同步 Context Engineering
if [[ -d "$UPSTREAM_DIR/context-engineering" ]]; then
    echo "📚 同步 Context Engineering..."
    cd "$UPSTREAM_DIR/context-engineering"
    git pull origin main
    echo "✅ Context Engineering 同步完成"
else
    echo "❌ Context Engineering 目录不存在"
fi

# 同步 SuperClaude Framework
if [[ -d "$UPSTREAM_DIR/superclaude" ]]; then
    echo "🤖 同步 SuperClaude Framework..."
    cd "$UPSTREAM_DIR/superclaude"
    git pull origin master
    echo "✅ SuperClaude Framework 同步完成"
else
    echo "❌ SuperClaude Framework 目录不存在"
fi

echo "✅ 上游项目同步完成"
