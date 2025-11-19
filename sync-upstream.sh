#!/bin/bash

# Git同步脚本 - 基于rebase策略同步upstream
# 功能：以upstream最新版本为主，保留本地个性化定制

set -e  # 遇到错误立即退出

# ==========================================
# 配置变量区域 - 请根据实际情况修改
# ==========================================

# Upstream 远程仓库配置
UPSTREAM_URL="https://github.com/jeecgboot/JeecgBoot.git"
UPSTREAM_BRANCH="springboot3"
UPSTREAM_REMOTE_NAME="upstream"

# 本地仓库配置
LOCAL_BRANCH=$(git branch --show-current)

# Origin 远程仓库配置（用于推送）
ORIGIN_URL=$(git remote get-url origin 2>/dev/null || echo "")
ORIGIN_BRANCH="${LOCAL_BRANCH}"

# 备份配置
BACKUP_BRANCH_PREFIX="backup"

# ==========================================
# 颜色输出配置
# ==========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[信息]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 读取用户输入，支持默认值
read_with_default() {
    local prompt="$1"
    local default="$2"
    local value

    # 提示信息输出到stderr，避免干扰返回值
    echo -e -n "${prompt} [${GREEN}${default}${NC}]: " >&2
    read value

    # 如果用户直接按回车，使用默认值
    if [ -z "$value" ]; then
        echo "$default"
    else
        echo "$value"
    fi
}

# 显示当前配置
show_config() {
    local title="$1"
    echo ""
    echo "=========================================="
    echo -e "   ${BOLD}${title}${NC}"
    echo "=========================================="
    echo ""

    # 源端信息
    echo -e "${BOLD}${BLUE}┌─ 源端（Source）- Upstream 远程仓库 ─────────────${NC}"
    echo -e "${CYAN}│${NC}"
    echo -e "${CYAN}│${NC}  同步来源: 从这里拉取最新代码"
    echo -e "${CYAN}│${NC}"
    echo -e "${CYAN}│${NC}  1. Remote名称: ${GREEN}${UPSTREAM_REMOTE_NAME}${NC}"
    echo -e "${CYAN}│${NC}  2. 仓库地址:   ${GREEN}${UPSTREAM_URL}${NC}"
    echo -e "${CYAN}│${NC}  3. 源端分支:   ${GREEN}${UPSTREAM_REMOTE_NAME}/${UPSTREAM_BRANCH}${NC}"
    echo -e "${BOLD}${BLUE}└────────────────────────────────────────────────${NC}"
    echo ""

    # 目标端信息
    echo -e "${BOLD}${YELLOW}┌─ 目标端（Target）- 本地仓库 ──────────────────${NC}"
    echo -e "${CYAN}│${NC}"
    echo -e "${CYAN}│${NC}  同步目标: 将源端代码合并到这里"
    echo -e "${CYAN}│${NC}"
    echo -e "${CYAN}│${NC}  4. 本地分支:   ${GREEN}${LOCAL_BRANCH}${NC}"
    echo -e "${CYAN}│${NC}  5. 工作目录:   ${GREEN}$(pwd)${NC}"
    echo -e "${BOLD}${YELLOW}└────────────────────────────────────────────────${NC}"
    echo ""

    # 推送目标信息
    if [ -n "$ORIGIN_URL" ]; then
        echo -e "${BOLD}${YELLOW}┌─ 推送目标（Push Target）- Origin 远程仓库 ───${NC}"
        echo -e "${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}  同步完成后可推送到这里（可选）"
        echo -e "${CYAN}│${NC}"
        echo -e "${CYAN}│${NC}  6. 仓库地址:   ${GREEN}${ORIGIN_URL}${NC}"
        echo -e "${CYAN}│${NC}  7. 目标分支:   ${GREEN}origin/${ORIGIN_BRANCH}${NC}"
        echo -e "${BOLD}${YELLOW}└────────────────────────────────────────────────${NC}"
        echo ""
    fi

    # 备份信息
    BACKUP_BRANCH="${BACKUP_BRANCH_PREFIX}-${LOCAL_BRANCH}-$(date +%Y%m%d-%H%M%S)"
    echo -e "${BOLD}${GREEN}┌─ 安全备份（Backup）────────────────────────${NC}"
    echo -e "${CYAN}│${NC}"
    echo -e "${CYAN}│${NC}  同步前自动创建备份，可随时回滚"
    echo -e "${CYAN}│${NC}"
    echo -e "${CYAN}│${NC}  8. 备份分支:   ${GREEN}${BACKUP_BRANCH}${NC} ${YELLOW}(自动)${NC}"
    echo -e "${BOLD}${GREEN}└────────────────────────────────────────────────${NC}"
    echo ""

    # 同步流程说明
    echo -e "${BOLD}同步流程：${NC}"
    echo -e "  ${GREEN}${UPSTREAM_REMOTE_NAME}/${UPSTREAM_BRANCH}${NC} ${BLUE}→${NC} ${GREEN}${LOCAL_BRANCH}${NC}"
    if [ -n "$ORIGIN_URL" ]; then
        echo -e "  ${GREEN}${LOCAL_BRANCH}${NC} ${YELLOW}→${NC} ${GREEN}origin/${ORIGIN_BRANCH}${NC} ${YELLOW}(推送，可选)${NC}"
    fi
    echo ""
}

# 编辑配置
edit_config() {
    echo ""
    echo -e "${YELLOW}╔════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║         请选择要编辑的配置项               ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  可编辑的配置项："
    echo -e "  ${BLUE}[源端]${NC}  1-3: Upstream配置 (Remote名称/仓库地址/分支)"
    echo -e "  ${YELLOW}[目标]${NC}  4-5: 本地配置 (分支名称/工作目录-不可改)"
    echo -e "  ${YELLOW}[推送]${NC}  6-7: Origin配置 (仓库地址/分支)"
    echo ""
    echo -e "${YELLOW}输入编号（可多选，用空格分隔，如：2 3），或按回车跳过：${NC}"
    echo -n "> "
    read edit_choices

    if [ -z "$edit_choices" ]; then
        return 0
    fi

    for choice in $edit_choices; do
        case $choice in
            1)
                UPSTREAM_REMOTE_NAME=$(read_with_default "源端Remote名称" "$UPSTREAM_REMOTE_NAME")
                ;;
            2)
                UPSTREAM_URL=$(read_with_default "源端仓库地址" "$UPSTREAM_URL")
                ;;
            3)
                UPSTREAM_BRANCH=$(read_with_default "源端分支名称" "$UPSTREAM_BRANCH")
                ;;
            4)
                LOCAL_BRANCH=$(read_with_default "目标本地分支" "$LOCAL_BRANCH")
                ;;
            5)
                print_warning "工作目录不可编辑，跳过"
                ;;
            6)
                ORIGIN_URL=$(read_with_default "推送目标仓库地址" "$ORIGIN_URL")
                ;;
            7)
                ORIGIN_BRANCH=$(read_with_default "推送目标分支" "$ORIGIN_BRANCH")
                ;;
            8)
                print_warning "备份分支自动生成，不可编辑"
                ;;
            *)
                print_warning "无效的选项: $choice"
                ;;
        esac
    done
}

# 检查是否在git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "当前目录不是一个Git仓库"
    exit 1
fi

# 显示脚本说明
echo ""
echo "=========================================="
echo "   Git Upstream 同步脚本 (Rebase策略)"
echo "=========================================="
echo ""
print_info "此脚本将："
echo "  1. 创建当前分支的备份"
echo "  2. 从upstream拉取最新代码"
echo "  3. 使用rebase策略合并（优先upstream版本）"
echo "  4. 保留本地独有的提交和文件"
echo ""

# 显示当前配置（在检查工作区之前）
show_config "当前配置"

# 检查工作区是否干净
if ! git diff-index --quiet HEAD --; then
    print_warning "检测到未提交的更改"
    git status --short
    echo ""
    echo -n "是否继续？这些更改会被暂存 (y/N): " >&2
    read continue_with_changes
    if [[ ! "$continue_with_changes" =~ ^[Yy]$ ]]; then
        print_info "操作已取消"
        exit 0
    fi
    STASH_NEEDED=true
else
    STASH_NEEDED=false
fi

# 配置编辑-确认循环
while true; do
    # 询问是否需要编辑（配置已经在上面显示过了）
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 询问是否需要编辑
    echo -e "${BOLD}是否需要编辑配置？${NC}"
    echo "  [e] 编辑配置"
    echo "  [c] 确认并继续执行"
    echo "  [q] 退出"
    echo -n "> " >&2
    read action

    case $action in
        e|E)
            edit_config
            # 编辑后重新显示配置
            echo ""
            show_config "更新后的配置"
            ;;
        c|C)
            # 最终确认
            echo ""
            echo -e "${BOLD}${YELLOW}╔════════════════════════════════════════════════════╗${NC}"
            echo -e "${BOLD}${YELLOW}║                   最终确认                         ║${NC}"
            echo -e "${BOLD}${YELLOW}╚════════════════════════════════════════════════════╝${NC}"
            echo ""
            echo -e "${RED}${BOLD}⚠️  请仔细核对以下配置，确认无误后将开始同步操作${NC}"
            echo ""

            # 源端信息
            echo -e "${BOLD}${BLUE}【源端 Source】${NC} ${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "  ${BLUE}▸${NC} Remote名称: ${GREEN}${UPSTREAM_REMOTE_NAME}${NC}"
            echo -e "  ${BLUE}▸${NC} 仓库地址:   ${GREEN}${UPSTREAM_URL}${NC}"
            echo -e "  ${BLUE}▸${NC} 源端分支:   ${GREEN}${UPSTREAM_REMOTE_NAME}/${UPSTREAM_BRANCH}${NC}"
            echo ""

            # 目标端信息
            echo -e "${BOLD}${YELLOW}【目标端 Target】${NC} ${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "  ${YELLOW}▸${NC} 本地分支:   ${GREEN}${LOCAL_BRANCH}${NC}"
            echo -e "  ${YELLOW}▸${NC} 工作目录:   ${GREEN}$(pwd)${NC}"
            echo ""

            # 推送目标
            if [ -n "$ORIGIN_URL" ]; then
                echo -e "${BOLD}${YELLOW}【推送目标 Push】${NC} ${YELLOW}━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo -e "  ${YELLOW}▸${NC} 仓库地址:   ${GREEN}${ORIGIN_URL}${NC}"
                echo -e "  ${YELLOW}▸${NC} 目标分支:   ${GREEN}origin/${ORIGIN_BRANCH}${NC}"
                echo ""
            fi

            # 备份信息
            BACKUP_BRANCH="${BACKUP_BRANCH_PREFIX}-${LOCAL_BRANCH}-$(date +%Y%m%d-%H%M%S)"
            echo -e "${BOLD}${GREEN}【安全备份 Backup】${NC} ${GREEN}━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "  ${GREEN}▸${NC} 备份分支:   ${GREEN}${BACKUP_BRANCH}${NC}"
            echo ""

            # 同步流程
            echo -e "${BOLD}【同步流程】${NC}"
            echo -e "  ${GREEN}${UPSTREAM_REMOTE_NAME}/${UPSTREAM_BRANCH}${NC} ${BLUE}━━▶${NC} ${GREEN}${LOCAL_BRANCH}${NC}"
            if [ -n "$ORIGIN_URL" ]; then
                echo -e "  ${GREEN}${LOCAL_BRANCH}${NC} ${YELLOW}━━▶${NC} ${GREEN}origin/${ORIGIN_BRANCH}${NC} ${YELLOW}(可选推送)${NC}"
            fi
            echo ""
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -n -e "${BOLD}${RED}确认开始同步？(输入 yes 确认 / 其他取消): ${NC}" >&2
            read final_confirm

            if [[ "$final_confirm" == "yes" ]]; then
                print_success "配置确认完成，开始执行同步..."
                break
            else
                print_warning "已取消，返回配置界面"
            fi
            ;;
        q|Q)
            print_info "操作已取消"
            exit 0
            ;;
        *)
            print_warning "无效的选项，请重新选择"
            ;;
    esac
done

echo ""
print_info "开始执行同步流程..."

# 暂存当前更改（如果需要）
if [ "$STASH_NEEDED" = true ]; then
    print_info "暂存当前未提交的更改..."
    git stash push -m "Auto stash before upstream sync $(date +%Y%m%d-%H%M%S)"
    print_success "更改已暂存"
fi

# 确保在正确的本地分支上
if [ "$(git branch --show-current)" != "$LOCAL_BRANCH" ]; then
    print_info "切换到分支: $LOCAL_BRANCH"
    git checkout "$LOCAL_BRANCH"
fi

# 创建备份分支
print_info "创建备份分支: $BACKUP_BRANCH"
git branch "$BACKUP_BRANCH"
print_success "备份分支创建成功"

# 添加或更新upstream remote
print_info "配置 ${UPSTREAM_REMOTE_NAME} 远程仓库..."
if git remote | grep -q "^${UPSTREAM_REMOTE_NAME}$"; then
    print_info "更新已存在的 ${UPSTREAM_REMOTE_NAME} 地址"
    git remote set-url "${UPSTREAM_REMOTE_NAME}" "$UPSTREAM_URL"
else
    print_info "添加 ${UPSTREAM_REMOTE_NAME} 远程仓库"
    git remote add "${UPSTREAM_REMOTE_NAME}" "$UPSTREAM_URL"
fi
print_success "远程仓库配置完成"

# 拉取upstream最新代码
print_info "拉取 ${UPSTREAM_REMOTE_NAME}/${UPSTREAM_BRANCH} 最新代码..."
git fetch "${UPSTREAM_REMOTE_NAME}"
print_success "代码拉取完成"

# 执行rebase操作
print_info "开始rebase操作 (将本地提交应用到 ${UPSTREAM_REMOTE_NAME}/${UPSTREAM_BRANCH} 上)..."
echo ""
print_warning "注意: 如果出现冲突，脚本会提示您手动解决"
echo ""

# 尝试执行rebase
if git rebase "${UPSTREAM_REMOTE_NAME}/$UPSTREAM_BRANCH"; then
    print_success "Rebase成功完成！"

    # 恢复之前暂存的更改
    if [ "$STASH_NEEDED" = true ]; then
        print_info "恢复之前暂存的更改..."
        if git stash pop; then
            print_success "暂存的更改已恢复"
        else
            print_warning "恢复暂存更改时出现冲突，请手动解决"
        fi
    fi

    echo ""
    print_success "=========================================="
    print_success "  同步完成！"
    print_success "=========================================="
    echo ""
    print_info "备份分支: ${GREEN}$BACKUP_BRANCH${NC}"
    print_info "当前分支: ${GREEN}$LOCAL_BRANCH${NC}"
    echo ""
    if [ -n "$ORIGIN_URL" ]; then
        print_info "如果需要推送到远程仓库 origin/${ORIGIN_BRANCH}，请执行："
        echo "  ${YELLOW}git push origin ${ORIGIN_BRANCH} --force-with-lease${NC}"
        echo ""
    fi
    print_info "如果需要回滚到同步前的状态，请执行："
    echo "  ${YELLOW}git reset --hard $BACKUP_BRANCH${NC}"
    echo ""
    print_info "如果需要删除备份分支，请执行："
    echo "  ${YELLOW}git branch -D $BACKUP_BRANCH${NC}"
    echo ""

else
    # Rebase失败，可能有冲突
    print_error "Rebase过程中出现冲突"
    echo ""
    print_info "请按以下步骤解决："
    echo ""
    echo "1. 查看冲突文件："
    echo "   ${YELLOW}git status${NC}"
    echo ""
    echo "2. 编辑冲突文件，解决冲突标记"
    echo ""
    echo "3. 对于每个文件，选择解决方式："
    echo "   - 使用upstream版本: ${YELLOW}git checkout --theirs <文件>${NC}"
    echo "   - 使用本地版本: ${YELLOW}git checkout --ours <文件>${NC}"
    echo "   - 手动编辑合并: 直接编辑文件"
    echo ""
    echo "4. 标记冲突已解决："
    echo "   ${YELLOW}git add <已解决的文件>${NC}"
    echo ""
    echo "5. 继续rebase："
    echo "   ${YELLOW}git rebase --continue${NC}"
    echo ""
    echo "或者放弃rebase，恢复到同步前状态："
    echo "   ${YELLOW}git rebase --abort${NC}"
    echo "   ${YELLOW}git reset --hard $BACKUP_BRANCH${NC}"
    echo ""

    # 恢复暂存的更改
    if [ "$STASH_NEEDED" = true ]; then
        print_warning "您有暂存的更改，解决冲突后请执行: ${YELLOW}git stash pop${NC}"
    fi

    exit 1
fi
