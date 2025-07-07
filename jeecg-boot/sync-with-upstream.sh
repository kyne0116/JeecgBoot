#!/bin/bash

# JeecgBoot 官方仓库同步脚本
# 用途：保持fork与官方仓库同步，并更新个人分支

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 初始化总结变量
master_sync_status="未开始"
master_changes_count=0
master_files_changed=""
commits_behind=0
personal_branch_status="未开始"
backup_branch_name=""
rebase_method=""
conflicts_occurred="否"
commits_before=0
commits_after=0

# 日志函数
log_info() {
    echo -e "${BLUE}[信息]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

log_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 检查是否在git仓库中
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "当前目录不是Git仓库！"
        exit 1
    fi
}

# 检查是否有未提交的变更
check_uncommitted_changes() {
    if ! git diff-index --quiet HEAD --; then
        log_warning "检测到未提交的变更！"
        echo "请先提交或暂存您的变更："
        git status --porcelain
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            exit 0
        fi
    fi
}

# 检查并添加上游仓库
setup_upstream() {
    log_info "检查上游仓库配置..."

    if ! git remote get-url upstream > /dev/null 2>&1; then
        log_info "添加上游仓库..."
        git remote add upstream https://github.com/jeecgboot/JeecgBoot.git
        log_success "上游仓库已添加"
    else
        log_info "上游仓库已存在"
    fi

    # 显示远程仓库配置
    echo "当前远程仓库配置："
    git remote -v
}

# 同步master分支
sync_master() {
    log_info "开始同步master分支..."

    # 切换到master分支
    log_info "切换到master分支..."
    if ! git checkout master; then
        log_error "切换到master分支失败！"
        master_sync_status="失败"
        exit 1
    fi

    # 获取落后的提交数量
    commits_behind=$(git rev-list --count HEAD..upstream/master 2>/dev/null || echo "0")

    # 获取上游更新
    log_info "获取上游仓库更新..."
    if ! git fetch upstream; then
        log_error "获取上游更新失败！"
        master_sync_status="失败"
        exit 1
    fi

    # 重新计算落后的提交数量
    commits_behind=$(git rev-list --count HEAD..upstream/master 2>/dev/null || echo "0")

    # 合并上游更新
    log_info "合并上游更新到本地master..."
    merge_output=$(git merge upstream/master --stat 2>&1)
    if [ $? -ne 0 ]; then
        log_error "合并上游更新失败！可能存在冲突需要手动解决"
        master_sync_status="失败"
        conflicts_occurred="是"
        exit 1
    else
        # 解析合并统计信息
        master_files_changed=$(echo "$merge_output" | grep "files changed" | tail -1 || echo "无文件变更")
        master_sync_status="成功"
    fi

    # 推送到fork
    log_info "推送更新到您的fork..."
    if ! git push origin master; then
        log_warning "推送到fork失败，可能需要手动推送"
        master_sync_status="部分成功"
    fi

    log_success "master分支同步完成！"
}

# 更新个人分支
update_custom_branch() {
    local branch_name="my-custom"

    log_info "开始更新个人分支 ${branch_name}..."

    # 检查分支是否存在
    if ! git show-ref --verify --quiet refs/heads/${branch_name}; then
        log_warning "分支 ${branch_name} 不存在，跳过个人分支更新"
        personal_branch_status="跳过（分支不存在）"
        return 0
    fi

    # 切换到个人分支
    log_info "切换到个人分支 ${branch_name}..."
    if ! git checkout ${branch_name}; then
        log_error "切换到个人分支失败！"
        personal_branch_status="失败"
        exit 1
    fi

    # 获取更新前的提交数量
    commits_before=$(git rev-list --count HEAD)

    # 创建备份分支
    backup_branch_name="${branch_name}-backup-$(date +%Y%m%d-%H%M%S)"
    log_info "创建备份分支 ${backup_branch_name}..."
    git checkout -b ${backup_branch_name} > /dev/null 2>&1
    git checkout ${branch_name} > /dev/null 2>&1

    # 选择更新方式
    echo "选择更新方式："
    echo "1) Rebase (推荐，保持历史清洁)"
    echo "2) Merge (安全，保留完整历史)"
    read -p "请选择 (1/2): " -n 1 -r
    echo

    case $REPLY in
        1)
            log_info "使用rebase方式更新..."
            rebase_method="Rebase"
            if git rebase master; then
                log_success "Rebase完成！"
                personal_branch_status="成功"
            else
                log_error "Rebase遇到冲突，请手动解决后运行："
                echo "  git add <冲突文件>"
                echo "  git rebase --continue"
                echo "或者放弃rebase："
                echo "  git rebase --abort"
                personal_branch_status="失败（冲突）"
                conflicts_occurred="是"
                exit 1
            fi
            ;;
        2)
            log_info "使用merge方式更新..."
            rebase_method="Merge"
            if git merge master; then
                log_success "Merge完成！"
                personal_branch_status="成功"
            else
                log_error "Merge遇到冲突，请手动解决后运行："
                echo "  git add <冲突文件>"
                echo "  git commit"
                personal_branch_status="失败（冲突）"
                conflicts_occurred="是"
                exit 1
            fi
            ;;
        *)
            log_warning "无效选择，跳过个人分支更新"
            personal_branch_status="跳过（用户取消）"
            return 0
            ;;
    esac

    # 获取更新后的提交数量
    commits_after=$(git rev-list --count HEAD)

    log_success "个人分支 ${branch_name} 更新完成！"
    log_info "备份分支已创建：${backup_branch_name}"
}

# 显示总结报告
show_summary() {
    echo
    echo "========================================"
    echo -e "${CYAN}           同步操作总结报告${NC}"
    echo "========================================"
    echo
    echo -e "${BLUE}📊 Master分支同步结果：${NC}"
    echo "   状态: ${master_sync_status}"
    if [ "$commits_behind" -gt 0 ]; then
        echo "   更新: 同步了 ${commits_behind} 个提交"
    else
        echo "   更新: 已是最新版本"
    fi
    if [ -n "$master_files_changed" ]; then
        echo "   变更: ${master_files_changed}"
    fi
    echo
    echo -e "${PURPLE}🔧 个人分支处理结果：${NC}"
    echo "   分支名称: my-custom"
    echo "   处理状态: ${personal_branch_status}"
    if [ -n "$rebase_method" ]; then
        echo "   更新方式: ${rebase_method}"
    fi
    if [ -n "$backup_branch_name" ]; then
        echo "   备份分支: ${backup_branch_name}"
    fi
    if [ "$commits_before" -gt 0 ] && [ "$commits_after" -gt 0 ]; then
        echo "   提交数量: ${commits_before} → ${commits_after}"
    fi
    echo
    echo -e "${YELLOW}🚨 冲突情况：${NC}"
    echo "   是否有冲突: ${conflicts_occurred}"
    echo
    echo "========================================"
    echo
    if [ "$master_sync_status" = "成功" ] && [ "$personal_branch_status" = "成功" ]; then
        echo -e "${GREEN}✅ 同步操作全部完成！您的代码已更新到最新版本。${NC}"
    else
        echo -e "${YELLOW}⚠️  同步操作部分完成，请检查上述状态信息。${NC}"
    fi
    echo
}

# 主函数
main() {
    echo "========================================"
    echo "    JeecgBoot 官方仓库同步脚本"
    echo "========================================"

    check_git_repo
    check_uncommitted_changes
    setup_upstream

    echo
    sync_master

    echo
    update_custom_branch

    show_summary
}

# 执行主函数
main "$@"
