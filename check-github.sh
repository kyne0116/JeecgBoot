#!/bin/bash

echo "🔍 GitHub连接状态检查"
echo "===================="

# 检查网络连接
echo -n "网络连通性: "
if ping -c 2 github.com >/dev/null 2>&1; then
    echo "✅ 正常"
    ping -c 1 github.com | grep "time=" | awk '{print "延迟:", $7}'
else
    echo "❌ 网络不通"
    exit 1
fi

# 检查Git配置
echo -n "Git配置: "
echo "HTTP版本: $(git config http.version)"
echo "缓冲区: $(git config http.postBuffer) bytes"

# 检查本地状态
echo -n "本地仓库: "
if git status >/dev/null 2>&1; then
    echo "✅ 正常"
    echo "当前分支: $(git branch --show-current)"
    echo "待推送提交: $(git log --oneline origin/$(git branch --show-current)..HEAD 2>/dev/null | wc -l | tr -d ' ')"
else
    echo "❌ Git仓库异常"
fi

echo "===================="
echo "建议操作:"
echo "1. 网络稳定时: ./quick-push.sh"
echo "2. 网络不稳定: 等待网络改善"
echo "3. 紧急推送: 考虑使用VPN或移动热点"