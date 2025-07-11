#!/bin/bash

# GitHub镜像源切换脚本
# 在GitHub直连不稳定时使用

echo "配置GitHub镜像源..."

# 添加GitHub镜像源
git remote add github-mirror https://gitee.com/kyne0116/JeecgBoot.git 2>/dev/null || true

# 显示当前配置
echo "当前远程仓库配置:"
git remote -v

echo ""
echo "使用方法:"
echo "1. 推送到GitHub原始仓库: git push origin [branch]"
echo "2. 推送到GitHub镜像: git push github-mirror [branch]"
echo "3. 使用增强脚本推送: ./push-github.sh [branch]"