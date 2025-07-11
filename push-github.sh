#!/bin/bash

# GitHub推送增强脚本
# 使用方法: ./push-github.sh [branch_name]

BRANCH=${1:-$(git branch --show-current)}
MAX_RETRIES=5
RETRY_DELAY=10

echo "正在推送分支: $BRANCH"

for i in $(seq 1 $MAX_RETRIES); do
    echo "尝试推送 ($i/$MAX_RETRIES)..."
    
    # 方案1: 尝试标准推送
    if git push origin "$BRANCH"; then
        echo "✅ 推送成功!"
        exit 0
    fi
    
    echo "❌ 推送失败，尝试备用方案..."
    
    # 方案2: 使用HTTP/1.1
    git config http.version HTTP/1.1
    if git push origin "$BRANCH"; then
        echo "✅ 使用HTTP/1.1推送成功!"
        exit 0
    fi
    
    # 方案3: 禁用SSL验证
    git config http.sslVerify false
    if git push origin "$BRANCH"; then
        echo "✅ 禁用SSL验证推送成功!"
        git config http.sslVerify true
        exit 0
    fi
    git config http.sslVerify true
    
    # 方案4: 分块推送
    if git push --set-upstream origin "$BRANCH"; then
        echo "✅ 分块推送成功!"
        exit 0
    fi
    
    # 恢复HTTP/2
    git config http.version HTTP/2
    
    if [ $i -lt $MAX_RETRIES ]; then
        echo "⏳ 等待${RETRY_DELAY}秒后重试..."
        sleep $RETRY_DELAY
    fi
done

echo "❌ 所有推送尝试均失败，请检查网络连接或联系管理员"
exit 1