#!/bin/bash

# Git上游同步脚本
# 用途：将my-custom分支与upstream/master保持同步
# 作者：自动生成

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Git仓库状态
check_git_status() {
    log_info "检查Git仓库状态..."
    
    if [ ! -d ".git" ]; then
        log_error "当前目录不是Git仓库"
        exit 1
    fi
    
    # 检查工作区是否干净
    if [ -n "$(git status --porcelain)" ]; then
        log_error "工作区有未提交的更改，请先提交或储藏"
        exit 1
    fi
    
    # 检查当前分支
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "my-custom" ]; then
        log_error "当前不在my-custom分支，请切换到my-custom分支"
        exit 1
    fi
    
    log_success "Git仓库状态检查通过"
}

# 获取上游更新
fetch_upstream() {
    log_info "获取上游仓库最新信息..."
    
    if ! git remote | grep -q "upstream"; then
        log_error "未找到upstream远程仓库"
        exit 1
    fi
    
    if ! git fetch upstream; then
        log_error "获取上游信息失败"
        exit 1
    fi
    
    log_success "上游信息获取完成"
}

# 检查差异
check_differences() {
    log_info "分析分支差异..."
    
    # 统计上游领先的提交
    upstream_commits=$(git rev-list --count my-custom..upstream/master)
    local_commits=$(git rev-list --count upstream/master..my-custom)
    
    log_info "上游master领先 $upstream_commits 个提交"
    log_info "本地my-custom领先 $local_commits 个提交"
    
    if [ "$upstream_commits" -eq 0 ]; then
        log_success "当前分支已经是最新的，无需同步"
        exit 0
    fi
}

# 尝试合并并检测冲突
attempt_merge() {
    log_info "尝试合并上游master分支..."
    
    # 创建备份分支
    backup_branch="my-custom-backup-$(date +%Y%m%d-%H%M%S)"
    git branch "$backup_branch"
    log_info "已创建备份分支：$backup_branch"
    
    # 尝试合并
    if git merge upstream/master --no-edit; then
        log_success "合并成功，无冲突"
        generate_success_report
    else
        log_warning "合并出现冲突，正在生成冲突解决指南..."
        generate_conflict_guide
        
        # 取消合并
        git merge --abort
        log_info "已取消合并操作"
        
        log_warning "请手动解决冲突后再次运行此脚本"
        exit 1
    fi
}

# 生成成功报告
generate_success_report() {
    local report_file="sync-success-report.md"
    
    cat > "$report_file" << EOF
# Git同步成功报告

**同步时间：** $(date '+%Y-%m-%d %H:%M:%S')
**当前分支：** my-custom
**上游分支：** upstream/master

## 同步结果

✅ **同步成功** - 未发现冲突

## 合并的提交

\`\`\`
$(git log --oneline HEAD~10..HEAD)
\`\`\`

## 下一步操作

1. 测试应用功能确保无问题
2. 推送到远程仓库：\`git push origin my-custom\`

---
*此报告由同步脚本自动生成*
EOF
    
    log_success "同步成功报告已生成：$report_file"
}

# 生成冲突解决指南
generate_conflict_guide() {
    local guide_file="conflict-resolution-guide.md"
    
    # 获取冲突文件列表
    local conflict_files=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "无法获取冲突文件")
    
    cat > "$guide_file" << EOF
# Git冲突解决指南

**生成时间：** $(date '+%Y-%m-%d %H:%M:%S')
**当前分支：** my-custom
**目标分支：** upstream/master

## 冲突概述

在尝试将 \`my-custom\` 分支与 \`upstream/master\` 合并时发现冲突。

### 冲突文件列表

\`\`\`
$conflict_files
\`\`\`

## 上游新增提交

\`\`\`
$(git log --oneline my-custom..upstream/master | head -10)
\`\`\`

## 本地特有提交

\`\`\`
$(git log --oneline upstream/master..my-custom | head -10)
\`\`\`

## 手动解决步骤

### 1. 开始合并

\`\`\`bash
git merge upstream/master
\`\`\`

### 2. 查看冲突状态

\`\`\`bash
git status
\`\`\`

### 3. 解决每个冲突文件

对于每个冲突文件：

1. 打开文件，找到冲突标记：
   - \`<<<<<<< HEAD\` - 当前分支的代码
   - \`=======\` - 分割线
   - \`>>>>>>> upstream/master\` - 上游分支的代码

2. 手动编辑文件，选择保留的代码
3. 删除冲突标记
4. 添加解决后的文件：\`git add <文件名>\`

### 4. 完成合并

\`\`\`bash
git commit -m "合并upstream/master，解决冲突"
\`\`\`

### 5. 验证合并结果

\`\`\`bash
# 运行测试
npm test # 或其他测试命令

# 检查应用启动
npm start # 或其他启动命令
\`\`\`

### 6. 推送更新

\`\`\`bash
git push origin my-custom
\`\`\`

## 冲突解决技巧

1. **优先保留功能性代码**：如果不确定，优先保留实现核心功能的代码
2. **保持代码风格一致**：合并后确保代码风格与项目规范一致
3. **测试验证**：解决冲突后必须进行充分测试
4. **渐进式合并**：如果冲突太多，考虑分批次合并部分提交

## 紧急回退方案

如果合并出现严重问题，可以回退到备份分支：

\`\`\`bash
# 切换到备份分支
git checkout my-custom-backup-$(date +%Y%m%d-%H%M%S)

# 删除问题分支
git branch -D my-custom

# 重新创建my-custom分支
git checkout -b my-custom
\`\`\`

---
*此指南由同步脚本自动生成，请根据实际情况调整*
EOF
    
    log_success "冲突解决指南已生成：$guide_file"
}

# 显示同步配置信息
show_sync_info() {
    echo "========================================"
    echo "        Git上游同步配置信息"
    echo "========================================"
    echo
    
    # 获取当前分支
    local current_branch=$(git branch --show-current)
    
    # 获取远程仓库URL
    local upstream_url=$(git remote get-url upstream 2>/dev/null || echo "未配置")
    local origin_url=$(git remote get-url origin 2>/dev/null || echo "未配置")
    
    # 获取分支差异信息
    local upstream_commits=$(git rev-list --count ${current_branch}..upstream/master 2>/dev/null || echo "0")
    local local_commits=$(git rev-list --count upstream/master..${current_branch} 2>/dev/null || echo "0")
    
    echo "📋 同步配置:"
    echo "  🎯 目标分支: ${current_branch} (当前分支)"
    echo "  🔄 源分支: upstream/master"
    echo
    echo "📡 远程仓库信息:"
    echo "  🏠 Origin (Fork): ${origin_url}"
    echo "  ⬆️  Upstream (官方): ${upstream_url}"
    echo
    echo "📊 分支状态:"
    echo "  📈 上游领先: ${upstream_commits} 个提交"
    echo "  📉 本地领先: ${local_commits} 个提交"
    echo
    echo "🔄 同步操作:"
    echo "  将 upstream/master 的更新合并到 ${current_branch} 分支"
    
    if [ "$upstream_commits" -gt 0 ]; then
        echo "  📦 预计同步: ${upstream_commits} 个新提交"
    else
        echo "  ✅ 状态: 已是最新，无需同步"
    fi
    
    echo
    echo "========================================"
}

# 用户确认函数
confirm_sync() {
    echo
    log_warning "⚠️  同步操作将会："
    echo "   1. 创建备份分支 (my-custom-backup-时间戳)"
    echo "   2. 将上游更新合并到当前分支"
    echo "   3. 如有冲突会生成解决指南并中止操作"
    echo
    
    read -p "🤔 确认执行同步操作吗？(y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "用户取消同步操作"
        exit 0
    fi
    
    log_info "用户确认，开始执行同步..."
    echo
}

# 主函数
main() {
    log_info "开始Git上游同步流程..."
    
    check_git_status
    fetch_upstream
    
    # 显示同步信息
    show_sync_info
    
    # 用户确认
    confirm_sync
    
    check_differences
    attempt_merge
    
    log_success "同步流程执行完成"
}

# 错误处理
trap 'log_error "脚本执行中断"; exit 1' ERR

# 执行主函数
main "$@"