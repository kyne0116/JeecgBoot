#!/bin/bash

echo "=== 手动推送脚本 ==="
echo "当前分支: $(git branch --show-current)"
echo "待推送提交:"
git log --oneline origin/my-custom..HEAD

echo ""
echo "执行推送..."
git push origin my-custom

echo ""
echo "推送完成后，请访问 GitHub Actions 页面查看 CI 执行情况:"
echo "https://github.com/kyne0116/JeecgBoot/actions"