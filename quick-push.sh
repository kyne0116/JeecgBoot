#!/bin/bash

# 快速推送脚本 - 适合网络不稳定环境
BRANCH=${1:-$(git branch --show-current)}

echo "🚀 快速推送分支: $BRANCH"

# 优化配置
git config http.version HTTP/1.1
git config http.postBuffer 10485760  # 10MB
git config http.lowSpeedLimit 1000
git config http.lowSpeedTime 300

# 尝试快速推送
git push origin "$BRANCH" || {
    echo "⚡ 尝试强制推送..."
    git push -f origin "$BRANCH" || {
        echo "❌ 推送失败，请稍后重试"
        exit 1
    }
}

echo "✅ 推送完成!"