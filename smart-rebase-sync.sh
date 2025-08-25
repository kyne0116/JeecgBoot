#!/bin/bash

# ========================================
# 智能Git同步工具 - 基于Rebase的单向同步脚本
# 功能：支持仓库级和文件级的智能Git同步，具备完善的冲突处理机制
# 作者：智能生成
# 版本：v1.0
# ========================================

set -e

# ========================================
# 配置变量 - 可自定义修改
# ========================================

# 默认同步配置 (继承自sync-upstream.sh)
SOURCE_REMOTE="upstream"
SOURCE_BRANCH="master"
TARGET_REMOTE="origin"
TARGET_BRANCH="my-custom"

# 仓库URL配置 (可选，脚本会自动检测)
UPSTREAM_REPO_URL="https://github.com/jeecgboot/JeecgBoot.git"
ORIGIN_REPO_URL="https://github.com/kyne0116/JeecgBoot.git"

# 脚本运行时变量
SCRIPT_NAME=$(basename "$0")
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
BACKUP_BRANCH=""
REPORT_FILE=""
CONFLICT_FILES=()
RESOLVED_FILES=()

# 进度跟踪变量
REBASE_CURRENT_COMMIT=0
REBASE_TOTAL_COMMITS=0
CURRENT_COMMIT_SHA=""
CURRENT_COMMIT_MSG=""
TOTAL_CONFLICT_FILES=0
PROCESSED_CONFLICT_FILES=0

# 智能状态检测全局变量
CURRENT_GIT_STATE=""
CURRENT_GIT_DETAILS=""
CURRENT_CONFLICTS=()
CURRENT_SUGGESTIONS=()

# ========================================
# 颜色和日志定义
# ========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# 日志前缀
INFO_PREFIX="[INFO]"
SUCCESS_PREFIX="[SUCCESS]"
WARNING_PREFIX="[WARNING]"
ERROR_PREFIX="[ERROR]"

# ========================================
# 日志函数
# ========================================

log_info() {
    echo -e "${BLUE}${INFO_PREFIX}${NC} $1"
}

log_success() {
    echo -e "${GREEN}${SUCCESS_PREFIX}${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}${WARNING_PREFIX}${NC} $1"
}

log_error() {
    echo -e "${RED}${ERROR_PREFIX}${NC} $1"
}

log_section() {
    echo
    echo "========================================"
    echo "  $1"
    echo "========================================"
    echo
}

# ========================================
# 进度显示函数
# ========================================

# 更新rebase进度信息
update_rebase_progress() {
    if [ -f ".git/rebase-merge/msgnum" ] && [ -f ".git/rebase-merge/end" ]; then
        REBASE_CURRENT_COMMIT=$(cat .git/rebase-merge/msgnum)
        REBASE_TOTAL_COMMITS=$(cat .git/rebase-merge/end)
    else
        REBASE_CURRENT_COMMIT=0
        REBASE_TOTAL_COMMITS=0
    fi
    
    # 获取当前commit信息
    if [ -f ".git/rebase-merge/stopped-sha" ]; then
        CURRENT_COMMIT_SHA=$(cat .git/rebase-merge/stopped-sha | cut -c1-8)
        CURRENT_COMMIT_MSG=$(git log --format="%s" -n 1 "$CURRENT_COMMIT_SHA" 2>/dev/null || echo "无法获取提交信息")
    else
        CURRENT_COMMIT_SHA=""
        CURRENT_COMMIT_MSG=""
    fi
}

# 显示当前rebase总体进度
show_rebase_progress() {
    update_rebase_progress
    
    if [ "$REBASE_TOTAL_COMMITS" -gt 0 ]; then
        local progress_percent=$((REBASE_CURRENT_COMMIT * 100 / REBASE_TOTAL_COMMITS))
        echo -e "${CYAN}📊 Rebase进度: ${REBASE_CURRENT_COMMIT}/${REBASE_TOTAL_COMMITS} (${progress_percent}%)${NC}"
        
        if [ -n "$CURRENT_COMMIT_SHA" ]; then
            echo -e "${PURPLE}🔄 当前提交: ${CURRENT_COMMIT_SHA} \"${CURRENT_COMMIT_MSG}\"${NC}"
        fi
    fi
}

# 显示文件处理进度
show_file_processing_progress() {
    local current="$1"
    local total="$2"
    local filename="$3"
    
    if [ "$total" -gt 0 ]; then
        local progress_percent=$((current * 100 / total))
        echo -e "${YELLOW}📁 文件进度: ${current}/${total} (${progress_percent}%)${NC}"
        echo -e "${BLUE}🔧 当前处理: ${filename}${NC}"
    fi
}

# 显示冲突解决进度
show_conflict_resolution_progress() {
    local resolved="$1"
    local total="$2"
    
    if [ "$total" -gt 0 ]; then
        local progress_percent=$((resolved * 100 / total))
        echo -e "${GREEN}✅ 冲突解决: ${resolved}/${total} (${progress_percent}%)${NC}"
    fi
}

# ========================================
# 增强批量处理功能
# ========================================

# 解析文件选择语法：支持范围(1-5)、逗号分隔(1,3,5)、组合(1-3,5,7-9)、全部(all)
parse_file_selection() {
    local input="$1"
    local total_files="$2"
    local selected_indices=()
    
    # 处理 "all" 或 "*" 等全选语法
    if [[ "$input" =~ ^(all|\*|全部)$ ]]; then
        for i in $(seq 1 "$total_files"); do
            selected_indices+=("$i")
        done
        printf '%s\n' "${selected_indices[@]}"
        return 0
    fi
    
    # 分割输入，支持逗号和空格分隔
    IFS=',' read -ra parts <<< "$input"
    
    for part in "${parts[@]}"; do
        # 去除空格
        part=$(echo "$part" | tr -d ' ')
        
        # 检查是否是范围格式 (1-5, 10-20)
        if [[ "$part" =~ ^([0-9]+)-([0-9]+)$ ]]; then
            local start="${BASH_REMATCH[1]}"
            local end="${BASH_REMATCH[2]}"
            
            # 验证范围有效性
            if [ "$start" -le "$end" ] && [ "$start" -ge 1 ] && [ "$end" -le "$total_files" ]; then
                for i in $(seq "$start" "$end"); do
                    selected_indices+=("$i")
                done
            else
                log_warning "无效范围: $part (范围应为 1-$total_files)"
                return 1
            fi
        # 检查是否是单个数字
        elif [[ "$part" =~ ^[0-9]+$ ]]; then
            if [ "$part" -ge 1 ] && [ "$part" -le "$total_files" ]; then
                selected_indices+=("$part")
            else
                log_warning "无效文件索引: $part (应为 1-$total_files)"
                return 1
            fi
        else
            log_warning "无效选择格式: $part"
            return 1
        fi
    done
    
    # 去重并排序
    if [ ${#selected_indices[@]} -gt 0 ]; then
        printf '%s\n' "${selected_indices[@]}" | sort -nu
    fi
    return 0
}

# 智能批量处理函数
process_conflicts_smart_batch() {
    local conflict_files="$1"
    local total=$(echo "$conflict_files" | wc -l | tr -d ' ')
    
    # 创建文件数组用于索引访问
    IFS=$'\n' read -d '' -r -a file_array <<< "$conflict_files" || true
    
    echo
    echo "========================================"
    echo -e "${BLUE}📋 智能批量冲突处理${NC}"
    echo "========================================"
    echo -e "${CYAN}总共 $total 个冲突文件：${NC}"
    echo
    
    # 显示所有冲突文件，带索引
    local count=1
    for file in "${file_array[@]}"; do
        if [ -n "$file" ]; then
            # 获取文件基本信息
            local file_info=""
            if [ -f "$file" ]; then
                local file_size=$(ls -lh "$file" | awk '{print $5}' 2>/dev/null || echo "?")
                local conflict_count=$(grep -c "<<<<<<< HEAD" "$file" 2>/dev/null || echo "0")
                # 确保冲突数正确显示
                file_info=" (${file_size}, ${conflict_count}个冲突)"
            fi
            echo -e "  ${count}) ${YELLOW}📄 $file${NC}${file_info}"
            count=$((count + 1))
        fi
    done
    
    echo
    echo -e "${GREEN}💡 批量选择语法示例：${NC}"
    echo -e "  ${BLUE}all${NC} 或 ${BLUE}*${NC}     - 处理所有文件"
    echo -e "  ${BLUE}1-5${NC}         - 处理文件 1 到 5"
    echo -e "  ${BLUE}1,3,5${NC}       - 处理文件 1、3、5"
    echo -e "  ${BLUE}1-3,5,7-9${NC}   - 处理文件 1-3、5、7-9"
    echo
    
    # 获取用户选择
    while true; do
        read -p "请输入要处理的文件选择 (或输入 'help' 查看帮助): " file_selection
        
        case "$file_selection" in
            "help"|"h"|"?")
                show_batch_processing_help
                continue
                ;;
            "")
                echo -e "${YELLOW}⚠️  请输入文件选择，不能为空${NC}"
                continue
                ;;
            *)
                # 解析文件选择
                local selected_indices
                if selected_indices=$(parse_file_selection "$file_selection" "$total"); then
                    local selected_count=$(echo "$selected_indices" | wc -l | tr -d ' ')
                    if [ "$selected_count" -eq 0 ]; then
                        echo -e "${YELLOW}⚠️  未选择任何文件，请重新输入${NC}"
                        continue
                    fi
                    
                    echo -e "${GREEN}✅ 已选择 $selected_count 个文件${NC}"
                    
                    # 显示选择的文件
                    echo -e "${CYAN}即将处理的文件：${NC}"
                    echo "$selected_indices" | while IFS= read -r index; do
                        if [ -n "$index" ] && [ "$index" -le "${#file_array[@]}" ]; then
                            local array_index=$((index - 1))  # 转换为数组索引(从0开始)
                            echo -e "  ${index}) ${file_array[$array_index]}"
                        fi
                    done
                    echo
                    
                    # 确认处理方式
                    apply_batch_strategy "$selected_indices" "file_array"
                    return 0
                else
                    echo -e "${RED}❌ 输入格式错误，请重新输入${NC}"
                    continue
                fi
                ;;
        esac
    done
}

# 显示批量处理帮助信息
show_batch_processing_help() {
    echo
    echo "========================================"
    echo -e "${BLUE}📖 批量处理帮助${NC}"
    echo "========================================"
    echo -e "${GREEN}支持的选择语法：${NC}"
    echo
    echo -e "${YELLOW}1. 全部文件：${NC}"
    echo -e "   ${BLUE}all${NC}, ${BLUE}*${NC}, ${BLUE}全部${NC}"
    echo
    echo -e "${YELLOW}2. 单个文件：${NC}"
    echo -e "   ${BLUE}5${NC}           - 选择第5个文件"
    echo
    echo -e "${YELLOW}3. 连续范围：${NC}"
    echo -e "   ${BLUE}1-5${NC}         - 选择第1到5个文件"
    echo -e "   ${BLUE}10-20${NC}       - 选择第10到20个文件"
    echo
    echo -e "${YELLOW}4. 离散选择：${NC}"
    echo -e "   ${BLUE}1,3,5${NC}       - 选择第1、3、5个文件"
    echo -e "   ${BLUE}2,7,15${NC}      - 选择第2、7、15个文件"
    echo
    echo -e "${YELLOW}5. 组合选择：${NC}"
    echo -e "   ${BLUE}1-3,5,7-9${NC}   - 选择第1-3、5、7-9个文件"
    echo -e "   ${BLUE}1,5-10,15${NC}   - 选择第1、5-10、15个文件"
    echo
    echo -e "${GREEN}💡 提示：${NC}"
    echo -e "  - 索引从 1 开始计数"
    echo -e "  - 支持空格分隔，如 '1, 3, 5'"
    echo -e "  - 输入 'help' 可随时查看此帮助"
    echo "========================================"
    echo
}

# 批量策略应用函数
apply_batch_strategy() {
    local selected_indices="$1"
    # 通过eval方式获取数组引用，兼容老版本bash
    local array_name="${2%\[@\]}"
    local processed_count=0
    
    echo -e "${BLUE}🎯 选择批量处理策略：${NC}"
    echo "  [1] 🟢 全部保留你的版本 (HEAD/ours)"
    echo "  [2] 🔵 全部使用上游版本 (upstream/theirs)"
    echo "  [3] ✏️  逐个决策处理"
    echo "  [4] 🛑 取消批量处理"
    echo
    
    while true; do
        echo -n "请选择策略 (1-4): "
        read -r choice
        REPLY="${choice:0:1}"
        
        case $REPLY in
            1)
                echo -e "${GREEN}🟢 批量应用：保留你的版本${NC}"
                # 使用数组避免子Shell问题
                IFS=$'\n' read -d '' -r -a index_array <<< "$selected_indices" || true
                for index in "${index_array[@]}"; do
                    if [ -n "$index" ] && [ "$index" -ge 1 ]; then
                        local array_index=$((index - 1))
                        eval "local file=\${${array_name}[$array_index]}"
                        if [ -n "$file" ]; then
                            git checkout --ours "$file"
                            git add "$file"
                            log_success "✅ 已处理: $file (保留你的版本)"
                            processed_count=$((processed_count + 1))
                        fi
                    fi
                done
                break
                ;;
            2)
                echo -e "${BLUE}🔵 批量应用：使用上游版本${NC}"
                # 使用数组避免子Shell问题
                IFS=$'\n' read -d '' -r -a index_array <<< "$selected_indices" || true
                for index in "${index_array[@]}"; do
                    if [ -n "$index" ] && [ "$index" -ge 1 ]; then
                        local array_index=$((index - 1))
                        eval "local file=\${${array_name}[$array_index]}"
                        if [ -n "$file" ]; then
                            git checkout --theirs "$file"
                            git add "$file"
                            log_success "✅ 已处理: $file (使用上游版本)"
                            processed_count=$((processed_count + 1))
                        fi
                    fi
                done
                break
                ;;
            3)
                echo -e "${YELLOW}✏️  逐个决策处理${NC}"
                process_selected_files_individually "$selected_indices" "$array_name"
                break
                ;;
            4)
                echo -e "${YELLOW}🛑 取消批量处理${NC}"
                return 0
                ;;
            "")
                echo -e "${YELLOW}⚠️  请输入有效选择 (1-4)，不能为空${NC}"
                echo
                ;;
            *)
                echo -e "${YELLOW}⚠️  无效选择 '$REPLY'，请输入 1、2、3 或 4${NC}"
                echo
                ;;
        esac
    done
    
    # 统计处理结果
    local total_selected=$(echo "$selected_indices" | wc -l | tr -d ' ')
    log_success "✅ 批量处理完成：已处理 $processed_count 个文件"
    
    # 更新全局进度变量
    PROCESSED_CONFLICT_FILES=$((PROCESSED_CONFLICT_FILES + processed_count))
}

# 逐个决策处理选中的文件
process_selected_files_individually() {
    local selected_indices="$1"
    local array_name="$2"
    local count=1
    local total=$(echo "$selected_indices" | wc -l | tr -d ' ')
    
    echo -e "${BLUE}🔧 逐个处理选中文件 (共 $total 个)${NC}"
    echo
    
    # 使用数组避免子Shell问题
    IFS=$'\n' read -d '' -r -a index_array <<< "$selected_indices" || true
    
    for index in "${index_array[@]}"; do
        if [ -n "$index" ] && [ "$index" -ge 1 ]; then
            local array_index=$((index - 1))
            eval "local file=\${${array_name}[$array_index]}"
            
            if [ -n "$file" ]; then
                echo "========================================"
                echo -e "${YELLOW}📁 文件处理进度: [$count/$total]${NC}"
                echo -e "${BLUE}🔧 当前处理: $file (原索引: $index)${NC}"
                echo "========================================"
                
                # 显示文件基本信息
                if [ -f "$file" ]; then
                    local file_size=$(ls -lh "$file" | awk '{print $5}' 2>/dev/null || echo "?")
                    local file_lines=$(wc -l < "$file" 2>/dev/null || echo "0")
                    local conflict_count=$(grep -c "<<<<<<< HEAD" "$file" 2>/dev/null || echo "0")
                    
                    echo -e "${CYAN}📏 文件信息:${NC}"
                    echo -e "  📄 大小: $file_size"
                    echo -e "  📝 行数: $file_lines"
                    echo -e "  ⚠️  冲突标记数: $conflict_count"
                    echo
                fi
                
                # 显示冲突详情预览
                show_conflict_details "$file"
                
                echo
                echo -e "${GREEN}🎯 选择处理方式:${NC}"
                echo "  [1] 🟢 保留你的版本 (HEAD/ours)"
                echo "  [2] 🔵 使用上游版本 (upstream/theirs)"
                echo "  [3] ✏️  手动编辑文件"
                echo "  [4] ⏭️  跳过此文件"
                echo
                
                while true; do
                    echo -n "请选择 (1-4): "
                    read -r choice
                    REPLY="${choice:0:1}"
                    
                    case $REPLY in
                        1)
                            git checkout --ours "$file"
                            git add "$file"
                            log_success "✅ 已保留你的版本: $file"
                            break
                            ;;
                        2)
                            git checkout --theirs "$file"
                            git add "$file"
                            log_success "✅ 已使用上游版本: $file"
                            break
                            ;;
                        3)
                            edit_file_manually "$file"
                            break
                            ;;
                        4)
                            log_info "⏭️  跳过文件: $file"
                            break
                            ;;
                        "")
                            echo -e "${YELLOW}⚠️  请输入有效选择 (1-4)，不能为空${NC}"
                            ;;
                        *)
                            echo -e "${YELLOW}⚠️  无效选择 '$REPLY'，请输入 1、2、3 或 4${NC}"
                            ;;
                    esac
                done
                
                # 显示当前进度
                echo
                echo -e "${CYAN}📊 处理进度: $count/$total${NC}"
                
                if [ $count -lt $total ]; then
                    echo
                    echo "----------------------------------------"
                    echo -e "${BLUE}⏳ 准备处理下一个文件...${NC}"
                    echo
                fi
                
                count=$((count + 1))
            fi
        fi
    done
}

# 显示综合进度信息
show_comprehensive_progress() {
    echo
    echo "========================================"
    echo "📋 当前进度信息"
    echo "========================================"
    
    # Rebase总体进度
    show_rebase_progress
    
    # 冲突文件进度
    if [ "$TOTAL_CONFLICT_FILES" -gt 0 ]; then
        echo
        show_conflict_resolution_progress "$PROCESSED_CONFLICT_FILES" "$TOTAL_CONFLICT_FILES"
    fi
    
    echo "========================================"
    echo
}

# ========================================
# 增强的环境检查和自动修复系统
# ========================================

# 精简的核心环境检查
perform_health_check() {
    local critical_issues=()
    
    # 仅检查关键问题
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        critical_issues+=("当前目录不是Git仓库")
    fi
    
    if [[ ! -w .git ]] && [[ -d .git ]]; then
        critical_issues+=("没有.git目录写权限")
    fi
    
    # 只有关键问题才退出
    if [[ ${#critical_issues[@]} -gt 0 ]]; then
        log_error "环境检查失败："
        for issue in "${critical_issues[@]}"; do
            echo -e "  ❌ $issue"
        done
        exit 1
    fi
}

# 快速自动修复
quick_auto_fix() {
    # 静默修复常见问题
    [[ -f .git/index.lock ]] && rm -f .git/index.lock 2>/dev/null
    
    # 启用rerere（如果未启用）
    if [[ $(git config --get rerere.enabled) != "true" ]]; then
        git config rerere.enabled true 2>/dev/null
    fi
    
    # 修复常见的Git配置问题
    if [[ $(git config --get core.autocrlf) == "true" ]]; then
        git config core.autocrlf input 2>/dev/null
    fi
}


check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "当前目录不是Git仓库"
        exit 1
    fi
}

check_git_safe_directory() {
    # 静默处理Git安全目录
    current_dir=$(pwd)
    if ! git config --global --get-all safe.directory | grep -q "^${current_dir}$" 2>/dev/null; then
        git config --global --add safe.directory "$current_dir" 2>/dev/null || true
    fi
}

setup_git_rerere() {
    # 静默启用rerere
    git config rerere.enabled true 2>/dev/null || true
}

check_upstream_remote() {
    if ! git remote get-url "$SOURCE_REMOTE" > /dev/null 2>&1; then
        log_warning "未找到upstream远程仓库，自动添加..."
        git remote add "$SOURCE_REMOTE" "$UPSTREAM_REPO_URL" 2>/dev/null || {
            log_error "无法添加upstream远程仓库"
            exit 1
        }
        log_success "已添加upstream远程仓库"
    fi
}

# ========================================
# 智能建议和引导系统
# ========================================

# 智能操作建议系统
provide_intelligent_suggestions() {
    local git_state="$1"
    local suggestions=()
    local quick_actions=()
    
    case "$git_state" in
        "CLEAN")
            if [ ${#CURRENT_CONFLICTS[@]} -eq 0 ]; then
                suggestions+=("状态正常，可以开始同步")
                quick_actions+=("开始同步")
            else
                suggestions+=("需要处理检测到的问题")
                quick_actions+=("自动处理问题" "手动检查")
            fi
            ;;
        "REBASE_STOPPED")
            suggestions+=("Rebase因冲突停止，需要解决冲突")
            quick_actions+=("继续处理冲突" "查看冲突详情" "中止rebase")
            ;;
        "REBASE_ACTIVE")
            suggestions+=("Rebase正在进行中")
            quick_actions+=("查看状态" "等待完成")
            ;;
        *)
            suggestions+=("检测到Git操作进行中")
            quick_actions+=("查看详细状态")
            ;;
    esac
    
    # 添加基于历史的智能建议
    add_historical_suggestions "suggestions" "quick_actions"
    
    display_intelligent_suggestions "suggestions" "quick_actions"
}

# 基于历史操作的智能建议
add_historical_suggestions() {
    local suggestions_array_name="$1"
    local actions_array_name="$2"
    
    # 检查最近的Git操作历史
    local recent_operations=$(git reflog --oneline -10 2>/dev/null || true)
    
    if echo "$recent_operations" | grep -q "rebase" 2>/dev/null; then
        eval "${suggestions_array_name}+=(\"📚 检测到最近有rebase操作，可能需要继续之前的工作\")"
    fi
    
    if echo "$recent_operations" | grep -q "merge" 2>/dev/null; then
        eval "${suggestions_array_name}+=(\"🔀 检测到最近有merge操作，注意检查合并结果\")"
    fi
    
    # 检查分支状态
    local branch_status=$(git status --porcelain=v1 2>/dev/null | wc -l)
    if [ "$branch_status" -gt 10 ]; then
        eval "${suggestions_array_name}+=(\"📁 工作区文件较多，建议分批处理或使用批量操作\")"
        eval "${actions_array_name}+=(\"智能批量处理\")"
    fi
}

# 显示智能建议
display_intelligent_suggestions() {
    local suggestions_array_name="$1"
    local actions_array_name="$2"
    
    eval "local suggestions_count=\${#${suggestions_array_name}[@]}"
    if [ $suggestions_count -gt 0 ]; then
        echo
        echo "========================================"
        echo -e "${BLUE}🤖 智能助手建议${NC}"
        echo "========================================"
        
        eval "for suggestion in \"\${${suggestions_array_name}[@]}\"; do
            echo -e \"  \$suggestion\"
        done"
        
        eval "local actions_count=\${#${actions_array_name}[@]}"
        if [ $actions_count -gt 0 ]; then
            echo
            echo -e "${GREEN}🚀 快捷操作:${NC}"
            local count=1
            eval "for action in \"\${${actions_array_name}[@]}\"; do
                echo -e \"  [\$count] \$action\"
                ((count++))
            done"
            
            echo
            echo -n "选择快捷操作 (直接回车或3秒后自动继续): "
            
            local choice
            read -t 3 choice || choice=""  # 3秒超时，更快响应
            
            if [[ -n "$choice" ]] && [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le $actions_count ]; then
                execute_quick_action "$choice" "$actions_array_name"
            fi
        fi
        
        echo "========================================"
        echo
    fi
}

# 执行快捷操作
execute_quick_action() {
    local action_index="$1"
    local actions_array_name="$2"
    eval "local action=\"\${${actions_array_name}[$((action_index-1))]}\""
    
    log_info "🚀 执行快捷操作: $action"
    
    case "$action" in
        "开始完整仓库同步")
            log_info "跳转到完整同步流程..."
            ;;
        "继续处理冲突")
            log_info "继续处理rebase冲突..."
            # 直接进入冲突处理流程
            ;;
        "查看详细冲突信息"|"查看rebase状态"|"查看详细状态")
            show_intelligent_rebase_status
            echo -n "按Enter键继续..."
            read -r
            ;;
        "中止当前rebase")
            confirm_and_abort_rebase
            ;;
        "自动处理检测到的问题")
            auto_fix_detected_issues
            ;;
        *)
            log_info "执行自定义操作: $action"
            ;;
    esac
}

# 确认并中止rebase
confirm_and_abort_rebase() {
    echo
    echo -e "${YELLOW}⚠️  确认要中止当前的rebase操作吗？${NC}"
    echo -e "${RED}注意: 这将丢失所有rebase过程中的更改${NC}"
    echo -n "确认中止 (y/N): "
    read -r response
    
    if [[ $response =~ ^[Yy]$ ]]; then
        git rebase --abort
        log_success "Rebase已中止"
        exit 0
    else
        log_info "已取消中止操作"
    fi
}

# 自动修复检测到的问题
auto_fix_detected_issues() {
    log_info "🔧 开始自动修复检测到的问题..."
    
    local fixed_count=0
    
    for conflict in "${CURRENT_CONFLICTS[@]}"; do
        local type="${conflict%%:*}"
        local file="${conflict#*:}"
        
        case "$type" in
            "UNSTAGED")
                log_info "自动暂存文件: $file"
                git add "$file"
                ((fixed_count++))
                ;;
            "UNTRACKED_BLOCKING")
                echo -n "删除阻塞文件 $file？ (y/N): "
                read -r response
                if [[ $response =~ ^[Yy]$ ]]; then
                    rm -f "$file"
                    log_success "已删除: $file"
                    ((fixed_count++))
                fi
                ;;
        esac
    done
    
    if [ $fixed_count -gt 0 ]; then
        log_success "自动修复了 $fixed_count 个问题"
        # 重新检测状态
        detect_git_state > /dev/null
    else
        log_info "没有可以自动修复的问题"
    fi
}

check_working_tree() {
    log_info "检查工作区状态..."
    
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        log_warning "工作区有未提交的更改"
        echo
        echo -e "${YELLOW}未提交的更改：${NC}"
        git status --porcelain | head -10
        local total_changes=$(git status --porcelain | wc -l)
        if [ "$total_changes" -gt 10 ]; then
            echo -e "${CYAN}... 还有 $((total_changes - 10)) 个文件${NC}"
        fi
        echo
        
        echo -e "${BLUE}════════════════════════════════════════${NC}"
        echo -e "${GREEN}💡 工作区更改处理选项${NC}"
        echo -e "${BLUE}════════════════════════════════════════${NC}"
        echo
        echo -e "${YELLOW}[1] 🗂️  创建提交保存所有更改${NC}"
        echo -e "    ${CYAN}命令:${NC} git add . && git commit -m '临时提交'"
        echo -e "    ${GREEN}✅ 包含:${NC} 所有修改文件 + 新增文件 (M + ??)"
        echo -e "    ${GREEN}✅ 结果:${NC} 创建永久Git提交，工作区完全干净"
        echo -e "    ${BLUE}📝 恢复:${NC} git reset HEAD~1 (撤销最后一个提交)"
        echo -e "    ${PURPLE}💡 适用:${NC} 想要保留这些更改作为正式提交"
        echo
        echo -e "${YELLOW}[2] 📦 储藏当前修改${NC}"
        echo -e "    ${CYAN}命令:${NC} git stash push -m '临时储藏'"
        echo -e "    ${GREEN}✅ 包含:${NC} 已跟踪文件的修改 (仅M标记文件)"
        echo -e "    ${RED}⚠️  排除:${NC} 新增文件会保留在工作区 (?? 文件)"
        echo -e "    ${GREEN}✅ 结果:${NC} 修改被临时保存，工作区相对干净"
        echo -e "    ${BLUE}📝 恢复:${NC} git stash pop (稍后恢复储藏的修改)"
        echo -e "    ${PURPLE}💡 适用:${NC} 临时保存修改，稍后决定如何处理"
        echo
        echo -e "${YELLOW}[3] 📋 查看详细变更${NC}"
        echo -e "    ${CYAN}命令:${NC} git diff --stat"
        echo -e "    ${GREEN}✅ 效果:${NC} 显示每个文件的具体变更统计"
        echo -e "    ${PURPLE}💡 适用:${NC} 了解具体改动内容后再决定"
        echo
        echo -e "${YELLOW}[4] 🚫 退出脚本${NC}"
        echo -e "    ${RED}⚠️  效果:${NC} 保持当前状态不变，需手动处理"
        echo -e "    ${PURPLE}💡 适用:${NC} 想要手动处理这些更改"
        echo
        echo -e "${BLUE}════════════════════════════════════════${NC}"
        echo
        
        while true; do
            echo -n "请选择处理方式 (1-4): "
            read -r choice
            
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
                    echo
                    git diff --stat
                    echo
                    ;;
                4)
                    log_info "用户选择退出"
                    exit 0
                    ;;
                *)
                    echo -e "${YELLOW}⚠️  请输入有效选择 (1-4)${NC}"
                    ;;
            esac
        done
    fi
    
    log_success "工作区状态检查通过"
}

# ========================================
# 配置管理和交互确认函数
# ========================================

show_current_config() {
    log_section "智能Git同步工具"
    
    echo "当前同步配置："
    echo "  源端: ${SOURCE_REMOTE}/${SOURCE_BRANCH}"
    echo "  目标: ${TARGET_REMOTE}/${TARGET_BRANCH}"
    echo
    
    # 显示远程仓库信息
    local source_url=$(git remote get-url "$SOURCE_REMOTE" 2>/dev/null || echo "未配置")
    local target_url=$(git remote get-url "$TARGET_REMOTE" 2>/dev/null || echo "未配置")
    
    echo "远程仓库信息："
    echo "  源端URL: $source_url"
    echo "  目标URL: $target_url"
    echo
    
    # 显示分支差异信息
    if git show-ref --verify --quiet "refs/remotes/$SOURCE_REMOTE/$SOURCE_BRANCH"; then
        local commits_behind=$(git rev-list --count "$TARGET_BRANCH..$SOURCE_REMOTE/$SOURCE_BRANCH" 2>/dev/null || echo "0")
        local commits_ahead=$(git rev-list --count "$SOURCE_REMOTE/$SOURCE_BRANCH..$TARGET_BRANCH" 2>/dev/null || echo "0")
        
        echo "分支差异信息："
        echo "  上游领先: $commits_behind 个提交"
        echo "  本地领先: $commits_ahead 个提交"
    else
        echo "分支差异信息：需要先fetch获取最新信息"
    fi
}

interactive_config() {
    while true; do
        show_current_config
        echo
        echo "选择操作："
        echo "  [1] 确认配置并开始同步"
        echo "  [2] 修改源端配置 (${SOURCE_REMOTE}/${SOURCE_BRANCH})"
        echo "  [3] 修改目标配置 (${TARGET_REMOTE}/${TARGET_BRANCH})"
        echo "  [4] 退出脚本"
        echo
        read -p "请选择 (1-4): " -n 1 -r
        echo
        
        case $REPLY in
            1)
                log_info "用户确认配置，开始同步..."
                return 0
                ;;
            2)
                modify_source_config
                ;;
            3)
                modify_target_config
                ;;
            4)
                log_info "用户退出脚本"
                exit 0
                ;;
            *)
                log_warning "无效选择，请重新选择"
                ;;
        esac
        echo
    done
}

modify_source_config() {
    echo
    echo "=== 修改源端配置 ==="
    echo "当前源端: ${SOURCE_REMOTE}/${SOURCE_BRANCH}"
    echo
    
    read -p "输入源端remote名称 (当前: $SOURCE_REMOTE): " new_remote
    if [ -n "$new_remote" ]; then
        SOURCE_REMOTE="$new_remote"
    fi
    
    read -p "输入源端branch名称 (当前: $SOURCE_BRANCH): " new_branch
    if [ -n "$new_branch" ]; then
        SOURCE_BRANCH="$new_branch"
    fi
    
    log_success "源端配置已更新: ${SOURCE_REMOTE}/${SOURCE_BRANCH}"
}

modify_target_config() {
    echo
    echo "=== 修改目标配置 ==="
    echo "当前目标: ${TARGET_REMOTE}/${TARGET_BRANCH}"
    echo
    
    read -p "输入目标remote名称 (当前: $TARGET_REMOTE): " new_remote
    if [ -n "$new_remote" ]; then
        TARGET_REMOTE="$new_remote"
    fi
    
    read -p "输入目标branch名称 (当前: $TARGET_BRANCH): " new_branch
    if [ -n "$new_branch" ]; then
        TARGET_BRANCH="$new_branch"
    fi
    
    log_success "目标配置已更新: ${TARGET_REMOTE}/${TARGET_BRANCH}"
}

# ========================================
# 智能Git状态检测和管理系统
# ========================================

# Git状态类型定义（兼容老版本bash）
get_git_state_description() {
    local state="$1"
    case "$state" in
        "CLEAN") echo "工作区干净，无进行中的操作" ;;
        "REBASE_ACTIVE") echo "正在进行rebase操作" ;;
        "REBASE_STOPPED") echo "rebase因冲突而停止" ;;
        "REBASE_COMPLETED") echo "rebase已完成" ;;
        "MERGE_ACTIVE") echo "正在进行merge操作" ;;
        "CHERRY_PICK_ACTIVE") echo "正在进行cherry-pick操作" ;;
        "UNKNOWN") echo "未知状态" ;;
        *) echo "未定义状态" ;;
    esac
}

# 全面的Git状态检测函数
detect_git_state() {
    local git_dir=".git"
    local state="CLEAN"
    local details=""
    local conflicts=()
    local suggestions=()
    
    log_info "🔍 开始全面Git状态检测..." >&2
    
    # 检测各种Git操作状态
    if [ -d "${git_dir}/rebase-merge" ]; then
        if [ -f "${git_dir}/rebase-merge/interactive" ]; then
            state="REBASE_ACTIVE"
            details="交互式rebase进行中"
        else
            state="REBASE_ACTIVE" 
            details="普通rebase进行中"
        fi
        
        # 检查是否因冲突停止
        if [ -f "${git_dir}/rebase-merge/stopped-sha" ]; then
            state="REBASE_STOPPED"
            local current_sha=$(cat "${git_dir}/rebase-merge/stopped-sha" 2>/dev/null | cut -c1-8)
            local current_msg=$(git log --format="%s" -n 1 "$current_sha" 2>/dev/null || echo "无法获取提交信息")
            details="rebase因冲突停止在提交: $current_sha \"$current_msg\""
        fi
        
    elif [ -d "${git_dir}/rebase-apply" ]; then
        state="REBASE_ACTIVE"
        details="rebase-apply进行中"
        if [ -f "${git_dir}/rebase-apply/applying" ]; then
            state="REBASE_STOPPED"
            details="rebase-apply因冲突停止"
        fi
        
    elif [ -f "${git_dir}/MERGE_HEAD" ]; then
        state="MERGE_ACTIVE"
        details="merge操作进行中"
        
    elif [ -f "${git_dir}/CHERRY_PICK_HEAD" ]; then
        state="CHERRY_PICK_ACTIVE"
        details="cherry-pick操作进行中"
        
    else
        # 检查是否有未提交的更改
        local git_status=$(git status --porcelain 2>/dev/null)
        if [ -z "$git_status" ]; then
            state="CLEAN"
            details="工作区干净，无进行中的操作"
        else
            # 检查是否只是未跟踪文件
            local untracked_only=$(echo "$git_status" | grep -v "^??" || true)
            if [ -z "$untracked_only" ]; then
                state="CLEAN"
                details="工作区只有未跟踪文件，无Git操作进行中"
            else
                state="CLEAN"
                details="工作区有未提交更改，但无进行中的Git操作"
            fi
        fi
    fi
    
    # 深度冲突检测
    detect_real_conflicts "conflicts" "suggestions"
    
    # 输出检测结果到全局变量
    CURRENT_GIT_STATE="$state"
    CURRENT_GIT_DETAILS="$details"
    CURRENT_CONFLICTS=("${conflicts[@]}")
    CURRENT_SUGGESTIONS=("${suggestions[@]}")
    
    echo "$state"
}

# 智能冲突检测函数
detect_real_conflicts() {
    local conflicts_array_name="$1"
    local suggestions_array_name="$2"
    
    # 清空数组
    eval "${conflicts_array_name}=()"
    eval "${suggestions_array_name}=()"
    
    # 1. 检测真实的合并冲突
    local merge_conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null | grep -v "^$" || true)
    if [ -n "$merge_conflicts" ]; then
        while IFS= read -r file; do
            [ -n "$file" ] && eval "${conflicts_array_name}+=(\"MERGE:\$file\")"
        done <<< "$merge_conflicts"
        eval "${suggestions_array_name}+=(\"处理合并冲突标记\")"
    fi
    
    # 2. 检测未暂存的修改
    local unstaged_files=$(git diff --name-only 2>/dev/null | grep -v "^$" || true)
    if [ -n "$unstaged_files" ]; then
        while IFS= read -r file; do
            [ -n "$file" ] && eval "${conflicts_array_name}+=(\"UNSTAGED:\$file\")"
        done <<< "$unstaged_files"
        eval "${suggestions_array_name}+=(\"暂存修改的文件\")"
    fi
    
    # 3. 检测未跟踪文件是否会阻塞操作
    local untracked_blocking=$(check_untracked_blocking_files)
    if [ -n "$untracked_blocking" ]; then
        while IFS= read -r file; do
            [ -n "$file" ] && eval "${conflicts_array_name}+=(\"UNTRACKED_BLOCKING:\$file\")"
        done <<< "$untracked_blocking"
        eval "${suggestions_array_name}+=(\"处理阻塞的未跟踪文件\")"
    fi
    
    # 4. 验证冲突的真实性
    validate_conflict_reality "$conflicts_array_name"
}

# 检测会阻塞操作的未跟踪文件
check_untracked_blocking_files() {
    local untracked_files=$(git ls-files --others --exclude-standard 2>/dev/null || true)
    local blocking_files=""
    
    if [ -n "$untracked_files" ] && [ "$CURRENT_GIT_STATE" = "REBASE_STOPPED" ]; then
        # 测试这些未跟踪文件是否会阻止rebase continue
        local test_output=$(git rebase --continue --dry-run 2>&1 || true)
        if echo "$test_output" | grep -q "would be overwritten\|will be overwritten" 2>/dev/null; then
            # 从错误信息中提取具体的阻塞文件
            blocking_files=$(echo "$test_output" | grep -A 10 "would be overwritten\|will be overwritten" | \
                            grep "^[[:space:]]*[^[:space:]]" | sed 's/^[[:space:]]*//' | grep -v "^$" || true)
        fi
    fi
    
    echo "$blocking_files"
}

# 验证冲突真实性（去除误报）
validate_conflict_reality() {
    local conflicts_array_name="$1"
    local validated_conflicts=()
    
    eval "for conflict in \"\${${conflicts_array_name}[@]}\"; do
        local type=\"\${conflict%%:*}\"
        local file=\"\${conflict#*:}\"
        
        case \"\$type\" in
            \"MERGE\")
                # 验证文件确实包含冲突标记
                if [ -f \"\$file\" ] && grep -q \"<<<<<<< HEAD\" \"\$file\" 2>/dev/null; then
                    validated_conflicts+=(\"\$conflict\")
                fi
                ;;
            \"UNSTAGED\")
                # 验证文件确实有未暂存的更改
                if ! git diff --quiet \"\$file\" 2>/dev/null; then
                    validated_conflicts+=(\"\$conflict\")
                fi
                ;;
            \"UNTRACKED_BLOCKING\")
                # 验证文件确实会阻塞操作
                if [ -f \"\$file\" ]; then
                    validated_conflicts+=(\"\$conflict\")
                fi
                ;;
        esac
    done"
    
    eval "${conflicts_array_name}=(\"\${validated_conflicts[@]}\")"
}

# 增强的rebase状态检查
check_rebase_status() {
    local git_state=$(detect_git_state)
    
    case "$git_state" in
        "REBASE_STOPPED")
            log_warning "🔄 检测到rebase操作因冲突而停止"
            show_intelligent_rebase_status
            provide_intelligent_suggestions "$git_state"
            handle_existing_rebase
            return 1
            ;;
        "REBASE_ACTIVE")
            log_warning "🔄 检测到正在进行的rebase操作"
            show_intelligent_rebase_status
            provide_intelligent_suggestions "$git_state"
            handle_existing_rebase
            return 1
            ;;
        "REBASE_COMPLETED"|"CLEAN")
            if [ ${#CURRENT_CONFLICTS[@]} -gt 0 ]; then
                log_warning "⚠️  虽然没有活跃的rebase，但检测到需要处理的文件"
                show_remaining_issues
                provide_intelligent_suggestions "$git_state"
                return 1
            else
                log_info "✅ 当前无进行中的rebase操作，状态正常"
                provide_intelligent_suggestions "$git_state"
                return 0
            fi
            ;;
        "MERGE_ACTIVE")
            log_warning "🔄 检测到正在进行的merge操作"
            log_info "建议完成或中止merge操作后再运行此脚本"
            provide_intelligent_suggestions "$git_state"
            exit 1
            ;;
        *)
            log_warning "⚠️  检测到其他Git操作进行中: $CURRENT_GIT_DETAILS"
            log_info "建议完成当前操作后再运行此脚本"
            provide_intelligent_suggestions "$git_state"
            exit 1
            ;;
    esac
}

# 显示智能的rebase状态信息
show_intelligent_rebase_status() {
    echo
    echo "========================================"
    echo -e "${BLUE}🔍 智能Git状态分析${NC}"
    echo "========================================"
    echo -e "${YELLOW}当前状态:${NC} $CURRENT_GIT_STATE"
    echo -e "${CYAN}详细信息:${NC} $CURRENT_GIT_DETAILS"
    
    if [ ${#CURRENT_CONFLICTS[@]} -gt 0 ]; then
        echo
        echo -e "${RED}检测到的问题:${NC}"
        for conflict in "${CURRENT_CONFLICTS[@]}"; do
            local type="${conflict%%:*}"
            local file="${conflict#*:}"
            local icon="📄"
            local desc=""
            
            case "$type" in
                "MERGE") icon="⚔️"; desc="合并冲突" ;;
                "UNSTAGED") icon="📝"; desc="未暂存修改" ;;
                "UNTRACKED_BLOCKING") icon="🚫"; desc="阻塞性未跟踪文件" ;;
            esac
            
            echo -e "  ${icon} ${desc}: $file"
        done
    fi
    
    if [ ${#CURRENT_SUGGESTIONS[@]} -gt 0 ]; then
        echo
        echo -e "${GREEN}建议操作:${NC}"
        for suggestion in "${CURRENT_SUGGESTIONS[@]}"; do
            echo -e "  💡 $suggestion"
        done
    fi
    
    echo "========================================"
    echo
}

# 显示剩余问题
show_remaining_issues() {
    echo
    echo "========================================"
    echo -e "${YELLOW}⚠️  检测到需要处理的问题${NC}"
    echo "========================================"
    echo -e "${CYAN}当前状态:${NC} $CURRENT_GIT_DETAILS"
    
    if [ ${#CURRENT_CONFLICTS[@]} -gt 0 ]; then
        echo
        echo -e "${YELLOW}需要处理的文件:${NC}"
        for conflict in "${CURRENT_CONFLICTS[@]}"; do
            local type="${conflict%%:*}"
            local file="${conflict#*:}"
            local icon="📄"
            local action=""
            
            case "$type" in
                "UNSTAGED") 
                    icon="📝"; action="需要暂存或撤销修改" ;;
                "UNTRACKED_BLOCKING") 
                    icon="🚫"; action="需要删除或移动" ;;
                *)
                    icon="❓"; action="需要手动检查" ;;
            esac
            
            echo -e "  ${icon} $file - $action"
        done
        
        echo
        echo -e "${GREEN}建议操作:${NC}"
        echo -e "  1. 检查上述文件的具体情况"
        echo -e "  2. 根据需要进行暂存、删除或移动"
        echo -e "  3. 重新运行脚本进行同步"
    fi
    
    echo "========================================"
    echo
}

handle_existing_rebase() {
    echo
    echo "发现未完成的rebase操作"
    echo "选择操作："
    echo "  [1] 继续处理冲突"
    echo "  [2] 查看当前rebase状态"
    echo "  [3] 中止rebase"
    echo "  [4] 退出脚本"
    echo
    read -p "请选择 (1-4): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            log_info "继续处理rebase冲突..."
            handle_rebase_conflicts
            ;;
        2)
            show_rebase_status
            handle_existing_rebase
            ;;
        3)
            abort_rebase
            ;;
        4)
            log_info "用户退出脚本"
            exit 0
            ;;
        *)
            log_warning "无效选择，请重新选择"
            handle_existing_rebase
            ;;
    esac
}

show_rebase_status() {
    echo
    echo "=== 📊 详细Rebase状态信息 ==="
    
    # 显示当前分支
    local current_branch=$(git branch --show-current 2>/dev/null || echo "detached")
    echo -e "${BLUE}🌿 当前分支: $current_branch${NC}"
    
    # 显示详细的rebase进度
    update_rebase_progress
    if [ "$REBASE_TOTAL_COMMITS" -gt 0 ]; then
        local progress_percent=$((REBASE_CURRENT_COMMIT * 100 / REBASE_TOTAL_COMMITS))
        echo -e "${CYAN}📊 Rebase进度: ${REBASE_CURRENT_COMMIT}/${REBASE_TOTAL_COMMITS} (${progress_percent}%)${NC}"
        
        if [ -n "$CURRENT_COMMIT_SHA" ]; then
            echo -e "${PURPLE}🔄 当前处理commit: ${CURRENT_COMMIT_SHA}${NC}"
            echo -e "${PURPLE}📝 提交信息: \"${CURRENT_COMMIT_MSG}\"${NC}"
        fi
        
        # 显示剩余提交数
        local remaining=$((REBASE_TOTAL_COMMITS - REBASE_CURRENT_COMMIT))
        echo -e "${YELLOW}⏳ 剩余提交: ${remaining}${NC}"
    else
        echo -e "${YELLOW}⚠️  无法获取rebase进度信息${NC}"
    fi
    
    # 显示冲突文件详情
    local conflict_files=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
    local untracked_blocking_files=$(check_untracked_file_conflicts)
    
    if [ -n "$conflict_files" ]; then
        local conflict_count=$(echo "$conflict_files" | wc -l)
        echo -e "${RED}⚠️  合并冲突文件 ($conflict_count 个):${NC}"
        echo "$conflict_files" | sed 's/^/  📄 /'
    fi
    
    if [ -n "$untracked_blocking_files" ]; then
        local untracked_count=$(echo "$untracked_blocking_files" | wc -l)
        echo -e "${YELLOW}🚫 未跟踪文件冲突 ($untracked_count 个):${NC}"
        echo "$untracked_blocking_files" | sed 's/^/  📄 /'
    fi
    
    if [ -z "$conflict_files" ] && [ -z "$untracked_blocking_files" ]; then
        echo -e "${GREEN}✅ 当前无冲突文件${NC}"
    fi
    
    echo
}

abort_rebase() {
    log_warning "中止当前rebase操作..."
    
    if git rebase --abort; then
        log_success "Rebase已中止"
    else
        log_error "中止rebase失败"
    fi
    
    exit 0
}

# ========================================
# 同步执行和冲突处理核心逻辑
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
    if ! git checkout "$TARGET_BRANCH" 2>/dev/null; then
        log_error "切换到目标分支失败: $TARGET_BRANCH"
        exit 1
    fi
    
    # 开始rebase
    if git rebase "$SOURCE_REMOTE/$SOURCE_BRANCH"; then
        log_success "Rebase成功完成，无冲突！"
        return 0
    else
        log_warning "Rebase遇到冲突，开始处理..."
        handle_rebase_conflicts
        return 1
    fi
}

# 检测未跟踪文件冲突
check_untracked_file_conflicts() {
    local untracked_files=""
    local blocking_files=""
    
    # 获取所有未跟踪文件
    untracked_files=$(git status --porcelain=v1 2>/dev/null | grep "^??" | cut -c4- || echo "")
    
    if [ -n "$untracked_files" ]; then
        # 测试这些未跟踪文件是否会阻止rebase continue
        local rebase_test_output
        rebase_test_output=$(git rebase --continue --dry-run 2>&1 || echo "")
        
        # 检查是否有"工作区中下列未跟踪的文件将会因为合并操作而被覆盖"错误
        if echo "$rebase_test_output" | grep -q "工作区中下列未跟踪的文件将会因为合并操作而被覆盖\|would be overwritten by merge" 2>/dev/null; then
            # 提取具体的阻塞文件
            blocking_files=$(echo "$rebase_test_output" | grep -A 20 "工作区中下列未跟踪的文件将会因为合并操作而被覆盖\|would be overwritten by merge" | grep "^[[:space:]]" | sed 's/^[[:space:]]*//' | grep -v "^$" || echo "")
            
            # 如果无法精确提取，使用所有未跟踪文件作为候选
            if [ -z "$blocking_files" ]; then
                blocking_files="$untracked_files"
            fi
        fi
    fi
    
    echo "$blocking_files"
}

# 全面检测所有类型的冲突
check_all_conflicts() {
    local merge_conflicts=""
    local untracked_conflicts=""
    local staging_conflicts=""
    local all_conflicts=""
    
    # 1. 检测传统的合并冲突文件
    merge_conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
    
    # 2. 检测未跟踪文件冲突
    untracked_conflicts=$(check_untracked_file_conflicts)
    
    # 3. 检测未暂存的修改（可能是冲突解决后忘记add的文件）
    staging_conflicts=$(git diff --name-only 2>/dev/null || echo "")
    
    # 4. 使用git status检查rebase状态
    local git_status_output=$(git status --porcelain 2>/dev/null || echo "")
    local status_conflicts=$(echo "$git_status_output" | grep "^UU\|^AA\|^DD\|^AU\|^UA\|^DU\|^UD" | cut -c4- || echo "")
    
    # 合并所有冲突文件（去重）
    {
        [ -n "$merge_conflicts" ] && echo "$merge_conflicts"
        [ -n "$untracked_conflicts" ] && echo "$untracked_conflicts"
        [ -n "$staging_conflicts" ] && echo "$staging_conflicts"
        [ -n "$status_conflicts" ] && echo "$status_conflicts"
    } | sort -u | grep -v "^$" || echo ""
}

# 诊断rebase continue失败的具体原因
diagnose_rebase_failure() {
    echo
    echo "========================================"
    echo -e "${RED}🔍 诊断Rebase Continue失败原因${NC}"
    echo "========================================"
    
    # 获取详细的git状态
    local git_status=$(git status --porcelain 2>/dev/null || echo "")
    local git_status_full=$(git status 2>/dev/null || echo "")
    
    echo -e "${YELLOW}📋 Git状态详情:${NC}"
    echo "$git_status_full"
    echo
    
    # 检查各种类型的冲突文件
    local merge_conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
    local unstaged_files=$(git diff --name-only 2>/dev/null || echo "")
    local staged_files=$(git diff --cached --name-only 2>/dev/null || echo "")
    local untracked_files=$(git ls-files --others --exclude-standard 2>/dev/null || echo "")
    
    echo -e "${RED}🚫 合并冲突文件:${NC}"
    if [ -n "$merge_conflicts" ]; then
        echo "$merge_conflicts" | sed 's/^/  - /'
    else
        echo "  无"
    fi
    echo
    
    echo -e "${YELLOW}📝 未暂存的修改:${NC}"
    if [ -n "$unstaged_files" ]; then
        echo "$unstaged_files" | sed 's/^/  - /'
    else
        echo "  无"
    fi
    echo
    
    echo -e "${GREEN}✅ 已暂存的文件:${NC}"
    if [ -n "$staged_files" ]; then
        echo "$staged_files" | sed 's/^/  - /'
    else
        echo "  无"
    fi
    echo
    
    echo -e "${BLUE}❓ 未跟踪的文件:${NC}"
    if [ -n "$untracked_files" ]; then
        echo "$untracked_files" | head -10 | sed 's/^/  - /'
        local untracked_count=$(echo "$untracked_files" | wc -l)
        if [ "$untracked_count" -gt 10 ]; then
            echo "  ... (还有 $((untracked_count - 10)) 个文件)"
        fi
    else
        echo "  无"
    fi
    echo
    
    # 尝试获取rebase continue的具体错误
    echo -e "${PURPLE}🔬 Rebase Continue错误详情:${NC}"
    local rebase_error=$(git rebase --continue 2>&1 || echo "")
    echo "$rebase_error" | head -10
    echo
    
    echo "========================================"
}

# 处理未暂存的文件
handle_unstaged_files() {
    local unstaged_files="$1"
    
    echo
    echo "========================================"
    echo -e "${BLUE}📝 处理未暂存的修改${NC}"
    echo "========================================"
    echo "发现以下未暂存的修改文件："
    echo "$unstaged_files" | sed 's/^/  - /'
    echo
    
    echo "这些文件可能是："
    echo "  1. 已解决冲突但忘记使用 git add 暂存"
    echo "  2. 需要进一步处理的冲突文件"
    echo "  3. 其他意外的修改"
    echo
    
    echo "选择处理方式："
    echo "  [1] 自动暂存所有修改文件"
    echo "  [2] 逐个检查并选择性暂存"
    echo "  [3] 显示文件差异详情"
    echo "  [4] 跳过，保持现状"
    echo
    while true; do
        read -p "请选择 (1-4): " -n 1 -r
        echo
        
        case $REPLY in
            1)
                echo -e "${GREEN}自动暂存所有修改...${NC}"
                echo "$unstaged_files" | while IFS= read -r file; do
                    if [ -n "$file" ]; then
                        git add "$file"
                        log_success "已暂存: $file"
                    fi
                done
                break
                ;;
            2)
                echo -e "${BLUE}逐个检查文件...${NC}"
                echo "$unstaged_files" | while IFS= read -r file; do
                    if [ -n "$file" ]; then
                        echo
                        echo "文件: $file"
                        echo "选择操作："
                        echo "  [y] 暂存此文件"
                        echo "  [n] 跳过此文件"
                        echo "  [d] 查看差异"
                        while true; do
                            read -p "选择 (y/n/d): " -n 1 -r
                            echo
                            
                            case $REPLY in
                                y|Y)
                                    git add "$file"
                                    log_success "已暂存: $file"
                                    break
                                    ;;
                                d|D)
                                    echo "文件差异："
                                    git diff "$file" | head -20
                                    echo
                                    read -p "是否暂存此文件? (y/N): " -n 1 -r
                                    echo
                                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                                        git add "$file"
                                        log_success "已暂存: $file"
                                    fi
                                    break
                                    ;;
                                n|N)
                                    log_info "跳过文件: $file"
                                    break
                                    ;;
                                "")
                                    echo -e "${YELLOW}⚠️  请选择 y/n/d，不能为空${NC}"
                                    ;;
                                *)
                                    echo -e "${YELLOW}⚠️  无效选择 '$REPLY'，请输入 y、n 或 d${NC}"
                                    ;;
                            esac
                        done
                    fi
                done
                break
                ;;
            3)
                echo -e "${CYAN}显示文件差异详情：${NC}"
                echo "$unstaged_files" | while IFS= read -r file; do
                    if [ -n "$file" ]; then
                        echo
                        echo "======== $file ========"
                        git diff "$file" | head -10
                        echo
                    fi
                done
                break
                ;;
            4)
                log_info "保持现状，跳过处理"
                break
                ;;
            "")
                echo -e "${YELLOW}⚠️  请输入有效选择 (1-4)，不能为空${NC}"
                echo
                ;;
            *)
                echo -e "${YELLOW}⚠️  无效选择 '$REPLY'，请输入 1、2、3 或 4${NC}"
                echo
                ;;
        esac
    done
}

# 强制解决卡住的状态
force_resolve_stuck_state() {
    echo
    echo "========================================"
    echo -e "${YELLOW}🔧 强制诊断并尝试修复${NC}"
    echo "========================================"
    
    # 1. 检查并清理可能的临时文件
    log_info "检查rebase临时文件..."
    if [ -d ".git/rebase-merge" ]; then
        echo "发现rebase-merge目录"
        ls -la .git/rebase-merge/
    fi
    
    # 2. 强制暂存所有修改的文件
    local modified_files=$(git diff --name-only 2>/dev/null || echo "")
    if [ -n "$modified_files" ]; then
        echo -e "${YELLOW}发现修改的文件，尝试自动暂存：${NC}"
        echo "$modified_files" | sed 's/^/  - /'
        
        read -p "是否自动暂存这些文件? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            log_success "已暂存所有修改"
        fi
    fi
    
    # 3. 检查是否有冲突标记未解决
    log_info "扫描剩余的冲突标记..."
    local files_with_conflicts=$(grep -r "<<<<<<< HEAD" . --exclude-dir=.git 2>/dev/null | cut -d: -f1 | sort -u || echo "")
    if [ -n "$files_with_conflicts" ]; then
        echo -e "${RED}发现包含冲突标记的文件：${NC}"
        echo "$files_with_conflicts" | sed 's/^/  - /'
        
        read -p "是否打开这些文件进行编辑? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "$files_with_conflicts" | while IFS= read -r file; do
                if [ -n "$file" ]; then
                    echo "编辑文件: $file"
                    echo "请手动解决冲突标记，然后保存文件"
                    read -p "按Enter键继续到下一个文件..."
                fi
            done
        fi
    fi
    
    # 4. 尝试强制继续
    echo -e "${GREEN}强制修复完成，将在下一轮尝试继续rebase${NC}"
}

# 处理未跟踪文件冲突
handle_untracked_file_conflicts() {
    local blocking_files="$1"
    
    echo
    echo "========================================"
    echo "🚫 检测到未跟踪文件冲突"
    echo "========================================"
    echo "以下未跟踪文件阻止rebase继续："
    echo "$blocking_files" | sed 's/^/  - /'
    echo
    
    echo "选择处理方式："
    echo "  [1] 删除阻塞文件 (⚠️  文件将丢失)"
    echo "  [2] 备份后删除文件"
    echo "  [3] 添加到.gitignore后删除"
    echo "  [4] 提交这些文件到当前分支"
    echo "  [5] 手动处理 (暂停脚本)"
    echo "  [6] 中止rebase"
    echo
    read -p "请选择 (1-6): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            remove_untracked_files "$blocking_files"
            ;;
        2)
            backup_and_remove_untracked_files "$blocking_files"
            ;;
        3)
            gitignore_and_remove_untracked_files "$blocking_files"
            ;;
        4)
            commit_untracked_files "$blocking_files"
            ;;
        5)
            pause_for_manual_handling "$blocking_files"
            ;;
        6)
            abort_rebase
            return 1
            ;;
        *)
            log_warning "无效选择，请重新选择"
            handle_untracked_file_conflicts "$blocking_files"
            ;;
    esac
}

# 删除未跟踪文件
remove_untracked_files() {
    local files="$1"
    
    log_warning "正在删除阻塞文件..."
    echo "$files" | while IFS= read -r file; do
        if [ -n "$file" ] && [ -f "$file" ]; then
            log_info "删除文件: $file"
            rm -f "$file"
        elif [ -n "$file" ] && [ -d "$file" ]; then
            log_info "删除目录: $file"
            rm -rf "$file"
        fi
    done
    log_success "阻塞文件已删除"
}

# 备份后删除未跟踪文件
backup_and_remove_untracked_files() {
    local files="$1"
    local backup_dir=".untracked-backup-$(date +%Y%m%d-%H%M%S)"
    
    log_info "创建备份目录: $backup_dir"
    mkdir -p "$backup_dir"
    
    echo "$files" | while IFS= read -r file; do
        if [ -n "$file" ] && [ -e "$file" ]; then
            local backup_path="$backup_dir/$file"
            local backup_parent_dir=$(dirname "$backup_path")
            
            log_info "备份文件: $file -> $backup_path"
            mkdir -p "$backup_parent_dir"
            cp -r "$file" "$backup_path"
            rm -rf "$file"
        fi
    done
    
    log_success "文件已备份到 $backup_dir 并删除"
}

# 添加到.gitignore后删除
gitignore_and_remove_untracked_files() {
    local files="$1"
    
    log_info "添加文件到.gitignore..."
    
    echo "$files" | while IFS= read -r file; do
        if [ -n "$file" ]; then
            # 检查是否已在.gitignore中
            if ! grep -q "^${file}$" .gitignore 2>/dev/null; then
                echo "$file" >> .gitignore
                log_info "已添加到.gitignore: $file"
            fi
            
            # 删除文件
            if [ -e "$file" ]; then
                rm -rf "$file"
                log_info "已删除: $file"
            fi
        fi
    done
    
    # 提交.gitignore更改
    if git add .gitignore && git diff --cached --quiet .gitignore; then
        log_info ".gitignore无需更新"
    else
        git commit -m "Add untracked files to .gitignore to resolve rebase conflict"
        log_success ".gitignore已更新并提交"
    fi
}

# 提交未跟踪文件
commit_untracked_files() {
    local files="$1"
    
    log_info "提交未跟踪文件..."
    
    echo "$files" | while IFS= read -r file; do
        if [ -n "$file" ] && [ -e "$file" ]; then
            git add "$file"
            log_info "已暂存: $file"
        fi
    done
    
    if git diff --cached --quiet; then
        log_warning "没有文件需要提交"
    else
        git commit -m "Add untracked files to resolve rebase conflict"
        log_success "未跟踪文件已提交"
    fi
}

# 暂停处理，让用户手动解决
pause_for_manual_handling() {
    local files="$1"
    
    echo
    log_warning "脚本暂停，请手动处理以下文件："
    echo "$files" | sed 's/^/  - /'
    echo
    echo "处理建议："
    echo "  1. 删除文件: rm <文件名>"
    echo "  2. 移动文件: mv <文件名> <新位置>"
    echo "  3. 添加到.gitignore: echo '<文件名>' >> .gitignore"
    echo "  4. 提交文件: git add <文件名> && git commit -m 'Add untracked file'"
    echo
    echo "处理完成后，可以："
    echo "  - 继续rebase: git rebase --continue"
    echo "  - 重新运行此脚本"
    echo
    read -p "按Enter键退出脚本..."
    exit 0
}

handle_rebase_conflicts() {
    log_section "🔄 开始处理Rebase冲突"
    
    # 显示初始进度信息
    show_comprehensive_progress
    
    local conflict_resolution_round=1
    local max_rounds=100  # 防止无限循环
    local last_commit_position=0
    local stuck_rounds=0
    
    while true; do
        # 防止无限循环检查
        if [ $conflict_resolution_round -gt $max_rounds ]; then
            echo -e "${RED}❌ 达到最大处理轮数 ($max_rounds)，可能存在死循环${NC}"
            echo -e "${YELLOW}建议手动检查rebase状态或中止rebase${NC}"
            return 1
        fi
        
        # 更新进度信息
        update_rebase_progress
        local current_position=$REBASE_CURRENT_COMMIT
        
        # 检测是否卡住（连续多轮没有进度）
        if [ $current_position -eq $last_commit_position ]; then
            stuck_rounds=$((stuck_rounds + 1))
        else
            stuck_rounds=0
        fi
        last_commit_position=$current_position
        
        if [ $stuck_rounds -ge 5 ]; then
            echo -e "${RED}⚠️  检测到可能的死循环：连续 $stuck_rounds 轮无进度${NC}"
            diagnose_rebase_failure
            
            echo -e "${YELLOW}选择处理方式:${NC}"
            echo "  [1] 强制诊断并尝试修复"
            echo "  [2] 跳过当前提交"
            echo "  [3] 中止rebase"
            echo "  [4] 继续尝试（不推荐）"
            echo
            read -p "请选择 (1-4): " -n 1 -r
            echo
            
            case $REPLY in
                1)
                    force_resolve_stuck_state
                    stuck_rounds=0
                    ;;
                2)
                    skip_current_commit
                    stuck_rounds=0
                    ;;
                3)
                    abort_rebase
                    return 1
                    ;;
                4)
                    echo -e "${YELLOW}继续尝试...${NC}"
                    stuck_rounds=0
                    ;;
                *)
                    echo -e "${YELLOW}无效选择，继续尝试...${NC}"
                    stuck_rounds=0
                    ;;
            esac
        fi
        
        echo -e "${BLUE}🔄 第 $conflict_resolution_round 轮冲突检测和处理${NC}"
        echo
        
        # 使用更强的冲突检测逻辑
        local all_conflicts
        all_conflicts=$(check_all_conflicts)
        
        # 分类检测
        local conflict_files=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
        local untracked_blocking_files
        untracked_blocking_files=$(check_untracked_file_conflicts)
        local unstaged_files=$(git diff --name-only 2>/dev/null || echo "")
        
        # 显示当前检测到的冲突类型
        if [ -n "$conflict_files" ]; then
            local conflict_count=$(echo "$conflict_files" | wc -l | tr -d ' ')
            echo -e "${RED}🚫 发现 $conflict_count 个合并冲突文件${NC}"
        fi
        
        if [ -n "$untracked_blocking_files" ]; then
            local untracked_count=$(echo "$untracked_blocking_files" | wc -l | tr -d ' ')
            echo -e "${YELLOW}🚫 发现 $untracked_count 个未跟踪文件冲突${NC}"
        fi
        
        if [ -n "$unstaged_files" ]; then
            local unstaged_count=$(echo "$unstaged_files" | wc -l | tr -d ' ')
            echo -e "${BLUE}📝 发现 $unstaged_count 个未暂存的修改${NC}"
        fi
        
        echo
        
        # 判断冲突类型和处理方式
        if [ -z "$all_conflicts" ]; then
            # 使用全面检测后仍然无冲突，尝试继续rebase
            echo -e "${GREEN}✅ 全面检测：所有冲突已解决，尝试继续rebase...${NC}"
            
            # 显示当前进度
            if [ "$REBASE_TOTAL_COMMITS" -gt 0 ]; then
                local remaining=$((REBASE_TOTAL_COMMITS - REBASE_CURRENT_COMMIT))
                echo -e "${CYAN}📊 剩余提交数: $remaining${NC}"
            fi
            
            if git rebase --continue; then
                log_success "🎉 Rebase成功完成！"
                
                # 显示最终统计
                echo
                echo "========================================"
                echo -e "${GREEN}📊 Rebase完成统计${NC}"
                echo "========================================"
                echo -e "${GREEN}✅ 总冲突处理轮数: $conflict_resolution_round${NC}"
                if [ "$TOTAL_CONFLICT_FILES" -gt 0 ]; then
                    echo -e "${GREEN}✅ 处理的冲突文件数: $PROCESSED_CONFLICT_FILES/$TOTAL_CONFLICT_FILES${NC}"
                fi
                echo "========================================"
                
                return 0
            else
                # rebase继续失败，进行详细诊断
                echo -e "${RED}❌ Rebase继续失败，进行详细诊断...${NC}"
                diagnose_rebase_failure
                conflict_resolution_round=$((conflict_resolution_round + 1))
                echo
                continue
            fi
        elif [ -n "$untracked_blocking_files" ]; then
            # 处理未跟踪文件冲突
            echo -e "${YELLOW}🚫 优先处理未跟踪文件冲突...${NC}"
            if ! handle_untracked_file_conflicts "$untracked_blocking_files"; then
                return 1
            fi
            echo -e "${GREEN}✅ 未跟踪文件冲突处理完成${NC}"
            conflict_resolution_round=$((conflict_resolution_round + 1))
            echo
            continue
        elif [ -n "$unstaged_files" ] && [ -z "$conflict_files" ]; then
            # 处理未暂存的文件（可能是解决冲突后忘记add）
            echo -e "${BLUE}📝 发现未暂存的修改，可能是已解决的冲突文件${NC}"
            handle_unstaged_files "$unstaged_files"
            conflict_resolution_round=$((conflict_resolution_round + 1))
            echo
            continue
        elif [ -n "$conflict_files" ]; then
            # 处理传统的合并冲突
            echo -e "${RED}🚫 处理合并冲突文件...${NC}"
            show_conflict_info "$conflict_files"
            
            if ! process_conflicts "$conflict_files"; then
                return 1
            fi
            
            echo -e "${GREEN}✅ 本轮合并冲突处理完成${NC}"
            if [ "$TOTAL_CONFLICT_FILES" -gt 0 ] && [ "$PROCESSED_CONFLICT_FILES" -gt 0 ]; then
                show_conflict_resolution_progress "$PROCESSED_CONFLICT_FILES" "$TOTAL_CONFLICT_FILES"
            fi
            conflict_resolution_round=$((conflict_resolution_round + 1))
            echo
            continue
        fi
    done
}

show_conflict_info() {
    local conflict_files="$1"
    
    echo
    echo "========================================"
    echo "⚠️  检测到Rebase合并冲突"
    echo "========================================"
    
    # 显示总体进度信息
    update_rebase_progress
    if [ "$REBASE_TOTAL_COMMITS" -gt 0 ]; then
        local progress_percent=$((REBASE_CURRENT_COMMIT * 100 / REBASE_TOTAL_COMMITS))
        echo -e "${CYAN}📊 Rebase总进度: ${REBASE_CURRENT_COMMIT}/${REBASE_TOTAL_COMMITS} (${progress_percent}%)${NC}"
        
        local remaining=$((REBASE_TOTAL_COMMITS - REBASE_CURRENT_COMMIT))
        echo -e "${YELLOW}⏳ 剩余提交数: ${remaining}${NC}"
    fi
    
    echo
    
    # 显示当前处理的commit详情
    if [ -n "$CURRENT_COMMIT_SHA" ]; then
        echo -e "${PURPLE}🔄 当前冲突提交: ${CURRENT_COMMIT_SHA}${NC}"
        echo -e "${PURPLE}📝 提交信息: \"${CURRENT_COMMIT_MSG}\"${NC}"
        
        # 显示提交作者和时间
        local commit_author=$(git log --format="%an" -n 1 "$CURRENT_COMMIT_SHA" 2>/dev/null || echo "未知")
        local commit_date=$(git log --format="%ad" --date=short -n 1 "$CURRENT_COMMIT_SHA" 2>/dev/null || echo "未知")
        echo -e "${PURPLE}👤 提交作者: ${commit_author} (${commit_date})${NC}"
    else
        echo -e "${YELLOW}⚠️  无法获取当前提交信息${NC}"
    fi
    
    echo
    
    # 显示冲突文件列表和详情
    local conflict_count=$(echo "$conflict_files" | wc -l | tr -d ' ')
    TOTAL_CONFLICT_FILES=$conflict_count
    
    echo -e "${RED}🚫 冲突文件列表 (${conflict_count} 个文件):${NC}"
    local count=1
    echo "$conflict_files" | while IFS= read -r file; do
        if [ -n "$file" ]; then
            # 获取文件大小和类型信息
            local file_size=""
            local file_type=""
            if [ -f "$file" ]; then
                file_size=$(ls -lh "$file" | awk '{print $5}')
                file_type=$(file -b "$file" 2>/dev/null | cut -d',' -f1 || echo "unknown")
            fi
            
            echo -e "  ${count}) ${YELLOW}📄 $file${NC}"
            if [ -n "$file_size" ]; then
                echo -e "      ${BLUE}📏 大小: $file_size | 类型: $file_type${NC}"
            fi
            count=$((count + 1))
        fi
    done
    
    echo
    echo -e "${GREEN}💡 提示: 选择处理方式时，建议优先查看文件内容和冲突复杂度${NC}"
    echo
}

process_conflicts() {
    local conflict_files="$1"
    local file_count=$(echo "$conflict_files" | wc -l | tr -d ' ')
    
    echo "选择处理方式："
    echo "  [1] 逐个文件处理 (推荐)"
    
    # 根据文件数量智能显示批量处理选项
    if [ "$file_count" -gt 1 ]; then
        echo "  [2] 🚀 智能批量处理 (支持灵活文件选择)"
        echo "  [3] 📦 简单批量策略 (全部ours/theirs)"
        echo "  [4] ✏️  手动编辑所有文件"
        echo "  [5] ⏭️  跳过此commit"
        echo "  [6] 🛑 中止rebase"
        local max_option=6
    else
        echo "  [2] ✏️  手动编辑文件"
        echo "  [3] ⏭️  跳过此commit"  
        echo "  [4] 🛑 中止rebase"
        local max_option=4
    fi
    
    echo
    echo -e "${CYAN}💡 提示: 共 $file_count 个冲突文件${NC}"
    if [ "$file_count" -gt 1 ]; then
        echo -e "${GREEN}推荐使用智能批量处理，支持范围选择和组合选择${NC}"
    fi
    echo
    
    while true; do
        echo -n "请选择 (1-$max_option): "
        read -r choice
        # 取输入的第一个字符
        REPLY="${choice:0:1}"
        
        if [ "$file_count" -gt 1 ]; then
            # 多文件菜单
            case $REPLY in
                1)
                    process_conflicts_individually "$conflict_files"
                    return
                    ;;
                2)
                    process_conflicts_smart_batch "$conflict_files"
                    return
                    ;;
                3)
                    process_conflicts_batch "$conflict_files"
                    return
                    ;;
                4)
                    process_conflicts_manually "$conflict_files"
                    return
                    ;;
                5)
                    skip_current_commit
                    return
                    ;;
                6)
                    abort_rebase
                    return
                    ;;
                "")
                    echo -e "${YELLOW}⚠️  请输入有效选择 (1-$max_option)，不能为空${NC}"
                    echo
                    ;;
                *)
                    echo -e "${YELLOW}⚠️  无效选择 '$REPLY'，请输入 1 到 $max_option${NC}"
                    echo
                    ;;
            esac
        else
            # 单文件菜单
            case $REPLY in
                1)
                    process_conflicts_individually "$conflict_files"
                    return
                    ;;
                2)
                    process_conflicts_manually "$conflict_files"
                    return
                    ;;
                3)
                    skip_current_commit
                    return
                    ;;
                4)
                    abort_rebase
                    return
                    ;;
                "")
                    echo -e "${YELLOW}⚠️  请输入有效选择 (1-$max_option)，不能为空${NC}"
                    echo
                    ;;
                *)
                    echo -e "${YELLOW}⚠️  无效选择 '$REPLY'，请输入 1 到 $max_option${NC}"
                    echo
                    ;;
            esac
        fi
    done
}

process_conflicts_individually() {
    local conflict_files="$1"
    local count=1
    local total=$(echo "$conflict_files" | wc -l | tr -d ' ')
    local processed=0
    
    echo -e "${BLUE}🔧 开始逐个处理冲突文件 (共 $total 个文件)${NC}"
    echo
    
    # 使用数组避免子Shell问题
    IFS=$'\n' read -d '' -r -a file_array <<< "$conflict_files" || true
    
    for file in "${file_array[@]}"; do
        if [ -n "$file" ]; then
            echo "========================================"
            echo -e "${YELLOW}📁 文件处理进度: [$count/$total]${NC}"
            echo -e "${BLUE}🔧 当前处理文件: $file${NC}"
            echo "========================================"
            
            # 显示文件基本信息
            if [ -f "$file" ]; then
                local file_size=$(ls -lh "$file" | awk '{print $5}')
                local file_lines=$(wc -l < "$file" 2>/dev/null || echo "0")
                local conflict_count=$(grep -c "<<<<<<< HEAD" "$file" 2>/dev/null || echo "0")
                
                echo -e "${CYAN}📏 文件信息:${NC}"
                echo -e "  📄 大小: $file_size"
                echo -e "  📝 行数: $file_lines"
                echo -e "  ⚠️  冲突标记数: $conflict_count"
                echo
            fi
            
            # 显示冲突详情
            show_conflict_details "$file"
            
            echo
            echo -e "${GREEN}🎯 选择处理方式:${NC}"
            echo "  [1] 🟢 保留你的版本 (HEAD/ours)"
            echo "  [2] 🔵 使用上游版本 (upstream/theirs)"
            echo "  [3] ✏️  手动编辑文件"
            echo "  [4] ⏭️  跳过此文件"
            echo
            
            # 显示处理建议
            local file_ext="${file##*.}"
            case "$file_ext" in
                "java"|"js"|"ts"|"py"|"cpp"|"c"|"h")
                    echo -e "${YELLOW}💡 代码文件建议: 仔细检查逻辑冲突，建议手动编辑${NC}"
                    ;;
                "xml"|"json"|"yml"|"yaml")
                    echo -e "${YELLOW}💡 配置文件建议: 注意格式完整性，可考虑使用上游版本${NC}"
                    ;;
                "md"|"txt"|"rst")
                    echo -e "${YELLOW}💡 文档文件建议: 通常可以安全合并或保留自己的版本${NC}"
                    ;;
                "sh"|"bash")
                    echo -e "${YELLOW}💡 脚本文件建议: 仔细检查逻辑完整性，建议手动编辑${NC}"
                    ;;
            esac
            echo
            
            # 输入验证循环，确保用户必须做出有效选择
            while true; do
                echo -n "请选择 (1-4): "
                read -r choice
                REPLY="${choice:0:1}"
                
                case $REPLY in
                    1)
                        git checkout --ours "$file"
                        git add "$file"
                        log_success "✅ 已保留你的版本: $file"
                        processed=$((processed + 1))
                        break
                        ;;
                    2)
                        git checkout --theirs "$file"
                        git add "$file"
                        log_success "✅ 已使用上游版本: $file"
                        processed=$((processed + 1))
                        break
                        ;;
                    3)
                        edit_file_manually "$file"
                        if git diff --cached --name-only | grep -q "^${file}$"; then
                            processed=$((processed + 1))
                            log_success "✅ 文件已手动解决并暂存"
                        fi
                        break
                        ;;
                    4)
                        log_info "⏭️  跳过文件: $file"
                        break
                        ;;
                    "")
                        echo -e "${YELLOW}⚠️  请输入有效选择 (1-4)，不能为空${NC}"
                        ;;
                    *)
                        echo -e "${YELLOW}⚠️  无效选择 '$REPLY'，请输入 1、2、3 或 4${NC}"
                        ;;
                esac
            done
            
            # 显示当前进度总结
            echo
            echo -e "${CYAN}📊 当前处理进度: 已处理 $processed/$total 个文件${NC}"
            
            # 如果不是最后一个文件，显示分割线
            if [ $count -lt $total ]; then
                echo
                echo "----------------------------------------"
                echo -e "${BLUE}⏳ 准备处理下一个文件...${NC}"
                echo
            fi
            
            count=$((count + 1))
        fi
    done
    
    # 更新全局进度变量
    PROCESSED_CONFLICT_FILES=$processed
}

show_conflict_details() {
    local file="$1"
    
    echo "冲突内容预览："
    echo "=============="
    
    # 显示冲突标记的前后几行内容
    if grep -q "<<<<<<< HEAD" "$file" 2>/dev/null; then
        grep -A 10 -B 2 "<<<<<<< HEAD" "$file" | head -20
        echo "... (更多内容请手动查看文件)"
    else
        echo "无法显示冲突内容，请手动查看文件"
    fi
}

edit_file_manually() {
    local file="$1"
    
    log_info "打开编辑器处理文件: $file"
    
    # 尝试使用不同的编辑器
    local editors=("$EDITOR" "vim" "nano" "vi")
    local editor_found=false
    
    for editor in "${editors[@]}"; do
        if [ -n "$editor" ] && command -v "$editor" >/dev/null 2>&1; then
            $editor "$file"
            editor_found=true
            break
        fi
    done
    
    if [ "$editor_found" = false ]; then
        log_error "未找到可用的编辑器，请手动编辑文件: $file"
        read -p "编辑完成后按Enter键继续..."
    fi
    
    # 询问是否解决了冲突
    echo
    read -p "冲突是否已解决? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add "$file"
        log_success "文件已标记为已解决: $file"
    else
        log_warning "文件未标记为已解决: $file"
    fi
}

process_conflicts_batch() {
    local conflict_files="$1"
    
    echo "批量处理策略："
    echo "  [1] 全部保留你的版本 (HEAD/ours)"
    echo "  [2] 全部使用上游版本 (upstream/theirs)"
    echo "  [3] 取消批量处理"
    echo
    while true; do
        read -p "请选择 (1-3): " -n 1 -r
        echo
        
        case $REPLY in
            1)
                log_info "批量选择：保留你的版本"
                echo "$conflict_files" | while IFS= read -r file; do
                    git checkout --ours "$file"
                    git add "$file"
                    log_success "已处理: $file (保留你的版本)"
                done
                break
                ;;
            2)
                log_info "批量选择：使用上游版本"
                echo "$conflict_files" | while IFS= read -r file; do
                    git checkout --theirs "$file"
                    git add "$file"
                    log_success "已处理: $file (使用上游版本)"
                done
                break
                ;;
            3)
                log_info "取消批量处理"
                process_conflicts "$conflict_files"
                return
                ;;
            "")
                echo -e "${YELLOW}⚠️  请输入有效选择 (1-3)，不能为空${NC}"
                echo
                ;;
            *)
                echo -e "${YELLOW}⚠️  无效选择 '$REPLY'，请输入 1、2 或 3${NC}"
                echo
                ;;
        esac
    done
}

process_conflicts_manually() {
    local conflict_files="$1"
    
    log_info "请手动编辑以下冲突文件："
    echo "$conflict_files" | sed 's/^/  /'
    echo
    echo "冲突标记说明："
    echo "  <<<<<<< HEAD - 你的更改"
    echo "  ======= - 分割线"
    echo "  >>>>>>> commit_hash - 上游更改"
    echo
    read -p "编辑完成后按Enter键继续..."
    
    # 让用户确认哪些文件已解决
    echo "$conflict_files" | while IFS= read -r file; do
        read -p "文件 $file 是否已解决? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add "$file"
            log_success "文件已标记为已解决: $file"
        else
            log_warning "文件未标记为已解决: $file"
        fi
    done
}

skip_current_commit() {
    log_warning "跳过当前commit..."
    
    if git rebase --skip; then
        log_info "已跳过当前commit，继续rebase"
    else
        log_error "跳过commit失败"
        return 1
    fi
}

# ========================================
# 文件级处理功能
# ========================================

process_file_level_sync() {
    local files=("$@")
    
    log_info "开始文件级同步处理..."
    log_info "目标文件: ${files[*]}"
    
    # 检查是否在rebase状态
    if [ -d ".git/rebase-merge" ] || [ -d ".git/rebase-apply" ]; then
        log_info "检测到rebase状态，处理指定文件的冲突"
        process_specific_files_in_rebase "${files[@]}"
    else
        log_info "非rebase状态，执行文件级targeted同步"
        perform_file_targeted_sync "${files[@]}"
    fi
}

process_specific_files_in_rebase() {
    local files=("$@")
    local processed_files=()
    
    # 获取当前冲突文件
    local current_conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
    
    if [ -z "$current_conflicts" ]; then
        log_warning "当前无冲突文件需要处理"
        return 0
    fi
    
    echo "当前冲突文件："
    echo "$current_conflicts" | sed 's/^/  /'
    echo
    
    # 处理指定的文件
    for file in "${files[@]}"; do
        if echo "$current_conflicts" | grep -q "^${file}$"; then
            log_info "处理冲突文件: $file"
            process_single_file_conflict "$file"
            processed_files+=("$file")
        else
            log_warning "文件不在冲突列表中: $file"
        fi
    done
    
    # 检查是否还有冲突
    local remaining_conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
    if [ -z "$remaining_conflicts" ]; then
        log_success "所有冲突已解决，尝试继续rebase..."
        if git rebase --continue; then
            log_success "Rebase继续成功！"
        else
            log_warning "继续rebase时遇到新的冲突"
        fi
    else
        log_info "剩余冲突文件:"
        echo "$remaining_conflicts" | sed 's/^/  /'
    fi
    
    # 更新报告
    update_report_after_file_processing "${processed_files[@]}"
}

process_single_file_conflict() {
    local file="$1"
    
    echo
    echo "========================================"
    echo "处理文件: $file"
    echo "========================================"
    
    # 显示冲突详情
    show_conflict_details "$file"
    
    echo
    echo "选择处理方式："
    echo "  [1] 保留你的版本 (HEAD/ours)"
    echo "  [2] 使用上游版本 (upstream/theirs)"
    echo "  [3] 手动编辑文件"
    echo "  [4] 跳过此文件"
    echo
    read -p "请选择 (1-4): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            git checkout --ours "$file"
            git add "$file"
            log_success "已选择保留你的版本: $file"
            RESOLVED_FILES+=("$file")
            ;;
        2)
            git checkout --theirs "$file"
            git add "$file"
            log_success "已选择使用上游版本: $file"
            RESOLVED_FILES+=("$file")
            ;;
        3)
            edit_file_manually "$file"
            if git diff --cached --name-only | grep -q "^${file}$"; then
                RESOLVED_FILES+=("$file")
            fi
            ;;
        4)
            log_info "跳过文件: $file"
            ;;
        *)
            log_warning "无效选择，跳过文件: $file"
            ;;
    esac
}

perform_file_targeted_sync() {
    local files=("$@")
    
    log_warning "文件级targeted同步功能需要特殊实现"
    log_info "当前建议：先执行完整仓库同步，再处理具体文件冲突"
    
    # 这里可以实现更复杂的文件级同步逻辑
    # 比如：cherry-pick特定文件的更改等
}

# ========================================
# 报告生成功能
# ========================================

generate_report_filename() {
    # 格式: {SOURCE_REMOTE}/{SOURCE_BRANCH}-{TARGET_REMOTE}/{TARGET_BRANCH}.md
    # 需要处理路径分隔符，避免文件名包含/
    local source_part="${SOURCE_REMOTE}-${SOURCE_BRANCH}"
    local target_part="${TARGET_REMOTE}-${TARGET_BRANCH}"
    REPORT_FILE="${source_part}-${target_part}.md"
}

generate_sync_report() {
    local status="$1"
    local additional_info="$2"
    
    generate_report_filename
    
    log_info "生成同步报告: $REPORT_FILE"
    
    # 生成报告内容
    cat > "$REPORT_FILE" << EOF
# Git同步报告

**同步时间**: $(date '+%Y-%m-%d %H:%M:%S')
**源端**: ${SOURCE_REMOTE}/${SOURCE_BRANCH}
**目标**: ${TARGET_REMOTE}/${TARGET_BRANCH}
**脚本版本**: v1.0

## 同步结果

**状态**: $status

$additional_info

## 备份信息

**备份分支**: $BACKUP_BRANCH
**恢复命令**: 
\`\`\`bash
git checkout $TARGET_BRANCH
git reset --hard $BACKUP_BRANCH
git push $TARGET_REMOTE $TARGET_BRANCH --force
\`\`\`

## 后续操作建议

### 如果同步成功
1. 测试应用功能确保无问题
2. 推送更新到远程仓库：\`git push $TARGET_REMOTE $TARGET_BRANCH\`

### 如果有未解决冲突
使用文件级处理功能：
\`\`\`bash
# 针对特定文件处理
./$SCRIPT_NAME <文件路径1> <文件路径2>

# 示例
./$SCRIPT_NAME src/main/java/UserController.java
\`\`\`

---
*此报告由智能Git同步脚本自动生成*
EOF

    log_success "同步报告已生成: $REPORT_FILE"
}

generate_conflict_report() {
    local conflict_files="$1"
    local resolved_count=${#RESOLVED_FILES[@]}
    local total_conflicts=$(echo "$conflict_files" | wc -l)
    
    generate_report_filename
    
    log_info "生成冲突报告: $REPORT_FILE"
    
    # 获取成功同步的提交信息
    local success_commits=""
    if [ -n "$BACKUP_BRANCH" ]; then
        success_commits=$(git log --oneline "$BACKUP_BRANCH..HEAD" 2>/dev/null || echo "无法获取同步信息")
    fi
    
    cat > "$REPORT_FILE" << EOF
# Git同步报告 - 存在冲突

**同步时间**: $(date '+%Y-%m-%d %H:%M:%S')
**源端**: ${SOURCE_REMOTE}/${SOURCE_BRANCH}
**目标**: ${TARGET_REMOTE}/${TARGET_BRANCH}
**脚本版本**: v1.0

## 同步结果

❌ **同步状态**: 存在冲突
📊 **冲突处理进度**: 已解决 $resolved_count/$total_conflicts 个冲突文件

## 成功同步部分

\`\`\`
$success_commits
\`\`\`

## 冲突文件清单

EOF

    # 添加冲突文件详情
    local count=1
    echo "$conflict_files" | while IFS= read -r file; do
        local status="❌ 未解决"
        if printf '%s\n' "${RESOLVED_FILES[@]}" | grep -q "^${file}$" 2>/dev/null; then
            status="✅ 已解决"
        fi
        
        echo "### $count. $file" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo "- **状态**: $status" >> "$REPORT_FILE"
        echo "- **建议**: 手动编辑解决冲突或使用文件级同步" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        count=$((count + 1))
    done
    
    cat >> "$REPORT_FILE" << EOF

## 处理建议

### 手动处理冲突
1. 编辑冲突文件，查找并解决冲突标记：
   - \`<<<<<<< HEAD\` - 你的更改
   - \`=======\` - 分割线  
   - \`>>>>>>> commit_hash\` - 上游更改
2. 删除冲突标记，保留最终代码
3. \`git add <解决的文件>\`
4. \`git rebase --continue\`

### 智能文件级处理
\`\`\`bash
# 处理特定冲突文件
./$SCRIPT_NAME <文件路径>

# 处理多个文件
./$SCRIPT_NAME file1.java file2.yml file3.xml
\`\`\`

### 中止并回滚
如需回滚到同步前状态：
\`\`\`bash
git rebase --abort
git checkout $TARGET_BRANCH
git reset --hard $BACKUP_BRANCH
\`\`\`

---
*多轮执行此脚本可观察冲突文件的减少过程*
EOF

    log_success "冲突报告已生成: $REPORT_FILE"
}

# ========================================
# 后续工作流管理
# ========================================

# 主后续工作流控制器
post_sync_workflow() {
    log_section "🚀 开始后续工作流处理"
    
    echo -e "${GREEN}✅ Git同步已成功完成！${NC}"
    echo -e "${CYAN}为确保完整的同步流程，建议执行以下后续任务：${NC}"
    echo
    
    show_post_sync_overview
    
    while true; do
        echo
        echo -e "${BLUE}════════════════════════════════════════${NC}"
        echo -e "${GREEN}🛠️ 后续工作流选择${NC}"
        echo -e "${BLUE}════════════════════════════════════════${NC}"
        echo
        echo -e "${YELLOW}[1] 🧹 工作区清理${NC}"
        echo -e "    ${GREEN}✅ 清理临时文件和提交历史${NC}"
        echo -e "    ${PURPLE}💡 建议: 保持仓库整洁${NC}"
        echo
        echo -e "${YELLOW}[2] 📤 推送到远程仓库${NC}"
        echo -e "    ${GREEN}✅ 将同步结果推送到origin远程${NC}"
        echo -e "    ${PURPLE}💡 建议: 备份同步成果${NC}"
        echo
        echo -e "${YELLOW}[3] 🔨 构建验证${NC}"
        echo -e "    ${GREEN}✅ 验证项目编译和运行状态${NC}"
        echo -e "    ${PURPLE}💡 建议: 确保同步后项目正常${NC}"
        echo
        echo -e "${YELLOW}[4] 📊 完整状态报告${NC}"
        echo -e "    ${GREEN}✅ 生成详细的最终同步报告${NC}"
        echo -e "    ${PURPLE}💡 建议: 记录同步详情${NC}"
        echo
        echo -e "${YELLOW}[5] 🎯 执行全部任务${NC}"
        echo -e "    ${GREEN}✅ 按顺序执行所有推荐任务${NC}"
        echo -e "    ${PURPLE}💡 推荐: 完整的端到端处理${NC}"
        echo
        echo -e "${YELLOW}[6] ✅ 跳过后续工作流${NC}"
        echo -e "    ${RED}⚠️  直接结束，手动处理剩余任务${NC}"
        echo
        echo -e "${BLUE}════════════════════════════════════════${NC}"
        
        echo -n "请选择操作 (1-6): "
        read -r choice
        
        case "$choice" in
            1)
                cleanup_workflow
                ;;
            2)
                push_workflow  
                ;;
            3)
                build_verification_workflow
                ;;
            4)
                final_status_report
                ;;
            5)
                execute_full_workflow
                return 0
                ;;
            6)
                log_info "跳过后续工作流，同步流程结束"
                return 0
                ;;
            "")
                echo -e "${YELLOW}⚠️  请输入有效选择 (1-6)，不能为空${NC}"
                ;;
            *)
                echo -e "${YELLOW}⚠️  无效选择 '$choice'，请输入 1-6${NC}"
                ;;
        esac
    done
}

# 显示后续工作流概览
show_post_sync_overview() {
    echo -e "${BLUE}📋 当前状态概览：${NC}"
    
    # 检查工作区状态
    local git_status=$(git status --porcelain 2>/dev/null || echo "")
    local unclean_files=$(echo "$git_status" | wc -l | tr -d ' ')
    
    if [ "$unclean_files" -gt 0 ]; then
        echo -e "${YELLOW}  ⚠️  工作区: $unclean_files 个未处理文件${NC}"
    else
        echo -e "${GREEN}  ✅ 工作区: 干净${NC}"
    fi
    
    # 检查临时提交
    local temp_commits=$(git log --oneline --grep="临时提交" -n 5 | wc -l | tr -d ' ')
    if [ "$temp_commits" -gt 0 ]; then
        echo -e "${YELLOW}  ⚠️  临时提交: 发现 $temp_commits 个需要整理${NC}"
    else
        echo -e "${GREEN}  ✅ 提交历史: 整洁${NC}"
    fi
    
    # 检查与远程的差异
    local commits_ahead=$(git rev-list --count origin/$TARGET_BRANCH..HEAD 2>/dev/null || echo "0")
    if [ "$commits_ahead" -gt 0 ]; then
        echo -e "${BLUE}  📤 远程同步: 本地领先 $commits_ahead 个提交${NC}"
    else
        echo -e "${GREEN}  ✅ 远程同步: 已同步${NC}"
    fi
    
    # Maven构建状态（如果存在pom.xml）
    if [ -f "jeecg-boot/pom.xml" ]; then
        echo -e "${BLUE}  🔨 构建验证: 需要验证Maven项目状态${NC}"
    fi
}

# 执行完整工作流
execute_full_workflow() {
    echo
    log_section "🚀 执行完整后续工作流"
    echo -e "${GREEN}将按以下顺序执行所有推荐任务：${NC}"
    echo -e "${CYAN}1. 工作区清理${NC}"
    echo -e "${CYAN}2. 推送到远程仓库${NC}"
    echo -e "${CYAN}3. 构建验证${NC}" 
    echo -e "${CYAN}4. 生成最终报告${NC}"
    echo
    
    if ! confirm_action "确认执行完整工作流"; then
        log_info "用户取消完整工作流执行"
        return 1
    fi
    
    echo
    log_info "🚀 开始执行完整后续工作流..."
    
    # 1. 工作区清理
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log_info "📍 步骤 1/4: 工作区清理"
    cleanup_workflow
    
    # 2. 推送到远程
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log_info "📍 步骤 2/4: 推送到远程仓库"
    push_workflow
    
    # 3. 构建验证
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log_info "📍 步骤 3/4: 构建验证"
    build_verification_workflow
    
    # 4. 最终报告
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log_info "📍 步骤 4/4: 生成最终报告"
    final_status_report
    
    echo
    log_success "🎉 完整后续工作流执行完毕！"
}

# 用户确认函数
confirm_action() {
    local action_description="$1"
    local default_yes="${2:-false}"
    
    if [ "$default_yes" = "true" ]; then
        local prompt="$action_description (Y/n): "
    else
        local prompt="$action_description (y/N): "
    fi
    
    while true; do
        echo -n "$prompt"
        read -r response
        
        case "$response" in
            [Yy]|[Yy][Ee][Ss])
                return 0
                ;;
            [Nn]|[Nn][Oo])
                return 1
                ;;
            "")
                if [ "$default_yes" = "true" ]; then
                    return 0
                else
                    return 1
                fi
                ;;
            *)
                echo -e "${YELLOW}请输入 y/yes 或 n/no${NC}"
                ;;
        esac
    done
}

update_report_after_file_processing() {
    local processed_files=("$@")
    
    if [ ${#processed_files[@]} -eq 0 ]; then
        return 0
    fi
    
    log_info "更新报告，标记已处理文件..."
    
    # 简单的更新方式：重新生成报告
    local remaining_conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
    if [ -n "$remaining_conflicts" ]; then
        generate_conflict_report "$remaining_conflicts"
    else
        generate_sync_report "✅ 同步成功" "所有冲突已解决，rebase完成"
    fi
}

# ========================================
# 主函数和参数解析
# ========================================

show_usage() {
    echo "智能Git同步工具 - 用法说明"
    echo
    echo "用法："
    echo "  $SCRIPT_NAME                    # 完整仓库同步"
    echo "  $SCRIPT_NAME <文件1> [文件2...]  # 文件级冲突处理"
    echo
    echo "示例："
    echo "  $SCRIPT_NAME                                    # 交互式仓库同步"
    echo "  $SCRIPT_NAME src/main/java/UserController.java  # 处理特定文件冲突"
    echo "  $SCRIPT_NAME file1.java file2.yml file3.xml     # 处理多个文件冲突"
    echo
    echo "功能特性："
    echo "  - 支持rebase方式的单向Git同步"
    echo "  - 智能冲突处理 (逐个/批量/手动)"
    echo "  - 断点续传和状态恢复"
    echo "  - 结构化同步报告生成"
    echo "  - Git rerere自动冲突重用"
    echo "  - 多轮执行冲突跟踪"
    echo
}

perform_full_sync() {
    log_section "开始完整仓库同步"
    
    # 检查并处理现有rebase状态
    if ! check_rebase_status; then
        # 如果有现有rebase且已处理，直接返回
        return 0
    fi
    
    # 交互式配置确认
    interactive_config
    
    # 初始化环境
    setup_git_rerere
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
        generate_sync_report "✅ 已是最新" "无需同步，分支已是最新状态"
        return 0
    fi
    
    log_info "发现 $commits_behind 个新提交，开始同步..."
    
    # 开始rebase同步
    if start_rebase; then
        # 同步成功
        generate_sync_report "✅ 同步成功" "成功同步 $commits_behind 个提交，无冲突"
        # 启动后续工作流
        post_sync_workflow
    else
        # 同步过程中有冲突，由handle_rebase_conflicts处理
        local remaining_conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
        if [ -n "$remaining_conflicts" ]; then
            generate_conflict_report "$remaining_conflicts"
        else
            generate_sync_report "✅ 同步成功" "冲突已解决，同步完成"
            # 启动后续工作流
            post_sync_workflow
        fi
    fi
}

main() {
    # 参数解析
    if [ $# -eq 0 ]; then
        # 无参数：完整仓库同步
        perform_full_sync
    elif [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        # 显示帮助
        show_usage
        exit 0
    else
        # 有参数：文件级处理
        process_file_level_sync "$@"
    fi
}

# ========================================
# 脚本入口点
# ========================================

# 错误处理
trap 'log_error "脚本执行中断"; exit 1' ERR

# 环境初始化
log_info "智能Git同步工具启动 - $(date '+%Y-%m-%d %H:%M:%S')"

# 快速环境检查和修复
perform_health_check
check_git_repo
check_git_safe_directory
quick_auto_fix

# 执行主函数
main "$@"

log_success "脚本执行完成 - $(date '+%Y-%m-%d %H:%M:%S')"测试修改
