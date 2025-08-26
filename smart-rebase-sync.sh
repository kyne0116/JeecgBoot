#!/bin/bash

# ========================================
# 智能Git同步工具 - 简化版本
# 功能：基于Rebase的单向Git同步，upstream -> origin
# ========================================

set -e

# ========================================
# 配置变量
# ========================================

# 默认同步配置
SOURCE_REMOTE="upstream"
SOURCE_BRANCH="master"
TARGET_REMOTE="origin"
TARGET_BRANCH="my-custom"

# 仓库URL配置
UPSTREAM_REPO_URL="https://github.com/jeecgboot/JeecgBoot.git"

# 脚本运行时变量
SCRIPT_NAME=$(basename "$0")
BACKUP_BRANCH=""

# ========================================
# 日志函数
# ========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

log_section() {
    echo
    echo "========================================"
    echo "  $1"
    echo "========================================"
    echo
}

# ========================================
# 环境检查
# ========================================

check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "当前目录不是Git仓库"
        exit 1
    fi
}

check_upstream_remote() {
    if ! git remote get-url "$SOURCE_REMOTE" > /dev/null 2>&1; then
        log_info "添加upstream远程仓库..."
        git remote add "$SOURCE_REMOTE" "$UPSTREAM_REPO_URL" || {
            log_error "无法添加upstream远程仓库"
            exit 1
        }
        log_success "已添加upstream远程仓库"
    fi
}

check_working_tree() {
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        log_warning "工作区有未提交的更改"
        echo
        echo "未提交的更改："
        git status --porcelain | head -10
        echo
        
        echo "选择处理方式："
        echo "  [1] 创建提交保存更改"
        echo "  [2] 储藏当前修改"
        echo "  [3] 退出脚本"
        echo
        
        while true; do
            read -p "请选择 (1-3): " choice
            case "$choice" in
                1)
                    git add .
                    git commit -m "临时提交：保存工作区更改以进行同步操作"
                    log_success "已暂存并提交所有更改"
                    break
                    ;;
                2)
                    git stash push -m "临时储藏：为同步操作储藏工作区更改"
                    log_success "已储藏所有更改"
                    break
                    ;;
                3)
                    log_info "用户选择退出"
                    exit 0
                    ;;
                *)
                    echo "请输入 1、2 或 3"
                    ;;
            esac
        done
    fi
}

check_rebase_status() {
    if [ -d ".git/rebase-merge" ] || [ -d ".git/rebase-apply" ]; then
        log_warning "检测到未完成的rebase操作"
        echo "选择操作："
        echo "  [1] 继续处理冲突"
        echo "  [2] 中止rebase"
        echo "  [3] 退出脚本"
        echo
        
        while true; do
            read -p "请选择 (1-3): " choice
            case "$choice" in
                1)
                    log_info "继续处理rebase冲突..."
                    handle_rebase_conflicts
                    return 1
                    ;;
                2)
                    git rebase --abort
                    log_success "Rebase已中止"
                    return 0
                    ;;
                3)
                    exit 0
                    ;;
                *)
                    echo "请输入 1、2 或 3"
                    ;;
            esac
        done
    fi
}

# ========================================
# 核心同步功能
# ========================================

create_backup_branch() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    BACKUP_BRANCH="${TARGET_BRANCH}-backup-${timestamp}"
    
    log_info "创建备份分支: $BACKUP_BRANCH"
    
    if git checkout -b "$BACKUP_BRANCH" > /dev/null 2>&1; then
        git checkout "$TARGET_BRANCH" > /dev/null 2>&1
        log_success "备份分支创建成功: $BACKUP_BRANCH"
    else
        log_error "创建备份分支失败"
        exit 1
    fi
}

fetch_upstream() {
    log_info "获取upstream最新更新..."
    
    if git fetch "$SOURCE_REMOTE"; then
        log_success "Upstream更新获取成功"
    else
        log_error "获取upstream更新失败"
        exit 1
    fi
}

start_rebase() {
    log_info "开始rebase同步: $TARGET_BRANCH -> $SOURCE_REMOTE/$SOURCE_BRANCH"
    
    # 确保在目标分支上
    git checkout "$TARGET_BRANCH" 2>/dev/null || {
        log_error "切换到目标分支失败: $TARGET_BRANCH"
        exit 1
    }
    
    # 开始rebase
    if git rebase "$SOURCE_REMOTE/$SOURCE_BRANCH"; then
        log_success "Rebase成功完成，无冲突！"
        return 0
    else
        log_warning "Rebase遇到冲突，开始处理..."
        handle_rebase_conflicts
        return $?
    fi
}

# ========================================
# 冲突处理
# ========================================

handle_rebase_conflicts() {
    log_section "处理Rebase冲突"
    
    while true; do
        local conflict_files=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
        
        if [ -z "$conflict_files" ]; then
            # 无冲突，尝试继续rebase
            if git rebase --continue; then
                log_success "Rebase成功完成！"
                return 0
            else
                log_error "Rebase继续失败"
                return 1
            fi
        fi
        
        echo "发现冲突文件："
        echo "$conflict_files" | sed 's/^/  - /'
        echo
        
        echo "选择处理方式："
        echo "  [1] 逐个文件处理"
        echo "  [2] 全部使用你的版本"
        echo "  [3] 全部使用上游版本"
        echo "  [4] 中止rebase"
        echo
        
        while true; do
            read -p "请选择 (1-4): " choice
            case "$choice" in
                1)
                    process_conflicts_individually "$conflict_files"
                    break
                    ;;
                2)
                    echo "$conflict_files" | while IFS= read -r file; do
                        [ -n "$file" ] && git checkout --ours "$file" && git add "$file"
                    done
                    log_success "已保留你的版本"
                    break
                    ;;
                3)
                    echo "$conflict_files" | while IFS= read -r file; do
                        [ -n "$file" ] && git checkout --theirs "$file" && git add "$file"
                    done
                    log_success "已使用上游版本"
                    break
                    ;;
                4)
                    git rebase --abort
                    log_success "Rebase已中止"
                    return 1
                    ;;
                *)
                    echo "请输入 1、2、3 或 4"
                    ;;
            esac
        done
    done
}

process_conflicts_individually() {
    local conflict_files="$1"
    local count=1
    local total=$(echo "$conflict_files" | wc -l | tr -d ' ')
    
    echo "$conflict_files" | while IFS= read -r file; do
        if [ -n "$file" ]; then
            echo
            echo "========================================="
            echo "处理文件 [$count/$total]: $file"
            echo "========================================="
            
            # 显示冲突内容预览
            if grep -q "<<<<<<< HEAD" "$file" 2>/dev/null; then
                echo "冲突内容预览："
                grep -A 5 -B 2 "<<<<<<< HEAD" "$file" | head -15
                echo "..."
            fi
            
            echo
            echo "选择处理方式："
            echo "  [1] 保留你的版本"
            echo "  [2] 使用上游版本"
            echo "  [3] 手动编辑文件"
            echo "  [4] 跳过此文件"
            echo
            
            while true; do
                read -p "请选择 (1-4): " choice
                case "$choice" in
                    1)
                        git checkout --ours "$file"
                        git add "$file"
                        log_success "已保留你的版本: $file"
                        break
                        ;;
                    2)
                        git checkout --theirs "$file"
                        git add "$file"
                        log_success "已使用上游版本: $file"
                        break
                        ;;
                    3)
                        edit_file_manually "$file"
                        break
                        ;;
                    4)
                        log_info "跳过文件: $file"
                        break
                        ;;
                    *)
                        echo "请输入 1、2、3 或 4"
                        ;;
                esac
            done
            
            count=$((count + 1))
        fi
    done
}

edit_file_manually() {
    local file="$1"
    
    log_info "打开编辑器处理文件: $file"
    
    # 尝试使用编辑器
    if [ -n "$EDITOR" ] && command -v "$EDITOR" >/dev/null 2>&1; then
        "$EDITOR" "$file"
    elif command -v vim >/dev/null 2>&1; then
        vim "$file"
    elif command -v nano >/dev/null 2>&1; then
        nano "$file"
    else
        log_error "未找到可用的编辑器"
        read -p "请手动编辑文件后按Enter继续..."
    fi
    
    echo
    read -p "冲突是否已解决? (y/N): " response
    if [[ $response =~ ^[Yy]$ ]]; then
        git add "$file"
        log_success "文件已标记为已解决: $file"
    else
        log_warning "文件未标记为已解决: $file"
    fi
}

# ========================================
# 后续工作流
# ========================================

post_sync_workflow() {
    log_section "后续工作流"
    
    echo "同步完成！选择后续操作："
    echo "  [1] 推送到远程仓库"
    echo "  [2] 清理工作区"
    echo "  [3] 执行全部后续任务"
    echo "  [4] 跳过后续操作"
    echo
    
    while true; do
        read -p "请选择 (1-4): " choice
        case "$choice" in
            1)
                push_workflow
                break
                ;;
            2)
                cleanup_workflow
                break
                ;;
            3)
                push_workflow
                cleanup_workflow
                final_status_report
                break
                ;;
            4)
                log_info "跳过后续操作"
                break
                ;;
            *)
                echo "请输入 1、2、3 或 4"
                ;;
        esac
    done
}

push_workflow() {
    log_section "推送到远程仓库"
    
    # 检查远程分支差异
    local commits_ahead=$(git rev-list --count "$TARGET_REMOTE/$TARGET_BRANCH"..HEAD 2>/dev/null || echo "0")
    
    if [ "$commits_ahead" -eq 0 ]; then
        log_info "本地与远程已同步，无需推送"
        return 0
    fi
    
    log_info "本地领先远程 $commits_ahead 个提交"
    
    echo
    read -p "确认推送到 $TARGET_REMOTE/$TARGET_BRANCH? (y/N): " response
    if [[ $response =~ ^[Yy]$ ]]; then
        if git push "$TARGET_REMOTE" "$TARGET_BRANCH"; then
            log_success "推送成功"
        else
            log_warning "推送失败，可能需要强制推送"
            read -p "是否强制推送? (y/N): " force_response
            if [[ $force_response =~ ^[Yy]$ ]]; then
                git push "$TARGET_REMOTE" "$TARGET_BRANCH" --force-with-lease
                log_success "强制推送完成"
            fi
        fi
    else
        log_info "用户取消推送"
    fi
}

cleanup_workflow() {
    log_section "清理工作区"
    
    # 清理临时文件
    if [ -f ".git/index.lock" ]; then
        rm -f ".git/index.lock"
        log_success "清理index.lock文件"
    fi
    
    # 清理过期的备份分支
    local backup_branches=$(git branch | grep "backup-" | head -5)
    if [ -n "$backup_branches" ]; then
        echo "发现备份分支："
        echo "$backup_branches"
        echo
        read -p "是否删除旧的备份分支? (y/N): " response
        if [[ $response =~ ^[Yy]$ ]]; then
            echo "$backup_branches" | while IFS= read -r branch; do
                branch=$(echo "$branch" | tr -d ' *')
                if [ -n "$branch" ] && [ "$branch" != "$BACKUP_BRANCH" ]; then
                    git branch -D "$branch" 2>/dev/null && log_success "删除备份分支: $branch"
                fi
            done
        fi
    fi
    
    log_success "工作区清理完成"
}

final_status_report() {
    log_section "同步完成报告"
    
    echo -e "${GREEN}✅ Git同步成功完成${NC}"
    echo
    echo "同步信息："
    echo "  源端: $SOURCE_REMOTE/$SOURCE_BRANCH"
    echo "  目标: $TARGET_REMOTE/$TARGET_BRANCH"
    echo "  备份: $BACKUP_BRANCH"
    echo
    
    # 显示最新的几个提交
    echo "最新提交："
    git log --oneline -5
    echo
    
    echo "恢复命令（如需回滚）："
    echo "  git checkout $TARGET_BRANCH"
    echo "  git reset --hard $BACKUP_BRANCH"
    echo "  git push $TARGET_REMOTE $TARGET_BRANCH --force"
}

# ========================================
# 主函数
# ========================================

show_usage() {
    echo "智能Git同步工具 - 简化版本"
    echo
    echo "用法："
    echo "  $SCRIPT_NAME                    # 完整仓库同步"
    echo "  $SCRIPT_NAME -h, --help         # 显示帮助"
    echo
    echo "功能："
    echo "  - 基于rebase的Git同步 (upstream -> origin)"
    echo "  - 智能冲突处理"
    echo "  - 自动推送到远程仓库"
    echo "  - 安全的备份机制"
}

show_config() {
    log_section "当前配置"
    
    echo "同步配置："
    echo "  源端: $SOURCE_REMOTE/$SOURCE_BRANCH"
    echo "  目标: $TARGET_REMOTE/$TARGET_BRANCH"
    echo
    
    # 显示远程仓库信息
    local source_url=$(git remote get-url "$SOURCE_REMOTE" 2>/dev/null || echo "未配置")
    local target_url=$(git remote get-url "$TARGET_REMOTE" 2>/dev/null || echo "未配置")
    
    echo "远程仓库："
    echo "  源端URL: $source_url"
    echo "  目标URL: $target_url"
    echo
}

perform_full_sync() {
    log_section "开始Git同步"
    
    # 显示当前配置
    show_config
    
    # 确认开始同步
    read -p "确认开始同步? (Y/n): " response
    if [[ $response =~ ^[Nn]$ ]]; then
        log_info "用户取消同步"
        exit 0
    fi
    
    # 检查并处理现有rebase状态
    if ! check_rebase_status; then
        return 0
    fi
    
    # 环境检查
    check_upstream_remote
    check_working_tree
    
    # 创建备份
    create_backup_branch
    
    # 获取更新并开始同步
    fetch_upstream
    
    # 检查是否需要同步
    local commits_behind=$(git rev-list --count "$TARGET_BRANCH..$SOURCE_REMOTE/$SOURCE_BRANCH" 2>/dev/null || echo "0")
    
    if [ "$commits_behind" -eq 0 ]; then
        log_success "目标分支已是最新，无需同步"
        return 0
    fi
    
    log_info "发现 $commits_behind 个新提交，开始同步..."
    
    # 开始rebase同步
    if start_rebase; then
        # 同步成功，启动后续工作流
        post_sync_workflow
        final_status_report
    else
        log_error "同步过程中遇到问题"
        return 1
    fi
}

main() {
    # 参数解析
    case "${1:-}" in
        -h|--help)
            show_usage
            exit 0
            ;;
        "")
            # 无参数：完整仓库同步
            perform_full_sync
            ;;
        *)
            log_error "未知参数: $1"
            show_usage
            exit 1
            ;;
    esac
}

# ========================================
# 脚本入口点
# ========================================

# 错误处理
trap 'log_error "脚本执行中断"; exit 1' ERR

# 环境初始化
log_info "智能Git同步工具启动 - $(date '+%Y-%m-%d %H:%M:%S')"

# 基础检查
check_git_repo

# 启用rerere自动冲突重用
git config rerere.enabled true 2>/dev/null || true

# 执行主函数
main "$@"

log_success "脚本执行完成 - $(date '+%Y-%m-%d %H:%M:%S')"