#!/bin/bash

################################################################################
# JeecgBoot Upstream 同步脚本 v2.1
#
# 用途：智能同步 upstream 最新代码，保留本地定制
# 作者：SIMBEST
# 日期：2025-11-20
# 更新：v2.1 - 新增智能检测逻辑，避免重复同步
#
# 使用方法：
#   ./sync-upstream.sh                    # 交互模式（默认）
#   ./sync-upstream.sh --mode analyze     # 分析模式（只分析不合并）
#   ./sync-upstream.sh --mode auto        # 自动模式（完全自动）
#   ./sync-upstream.sh --help             # 显示帮助
#
# 新特性（v2.1）：
#   ✅ 智能检测：自动判断是否需要同步，避免重复执行
#   ✅ 提交分析：精确显示 upstream 新增的提交数量
#   ✅ 状态提示：清晰展示本地与 upstream 的关系
################################################################################

set -e  # 遇到错误立即退出

# ============================================================================
# 配置区域
# ============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 上游仓库配置
UPSTREAM_REMOTE="upstream"
UPSTREAM_BRANCH="master"

# 本地分支
LOCAL_BRANCH=$(git branch --show-current)

# 工作目录
WORK_DIR=$(pwd)
TEMP_DIR="/tmp/jeecg-sync-$$"

# 报告文件
REPORT_FILE="${WORK_DIR}/sync-analysis-report.md"
STRATEGY_FILE="${WORK_DIR}/handling-strategy.md"

# 模式：analyze, interactive, auto
MODE="interactive"

# ============================================================================
# 工具函数
# ============================================================================

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_step() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════${NC}\n"
}

# 询问用户确认
ask_confirmation() {
    local prompt="$1"
    local default="${2:-n}"

    if [ "$MODE" = "auto" ]; then
        print_info "自动模式：自动确认 - $prompt"
        return 0
    fi

    while true; do
        if [ "$default" = "y" ]; then
            read -p "$(echo -e ${CYAN}$prompt [Y/n]: ${NC})" answer
            answer=${answer:-y}
        else
            read -p "$(echo -e ${CYAN}$prompt [y/N]: ${NC})" answer
            answer=${answer:-n}
        fi

        case $answer in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "请输入 y 或 n";;
        esac
    done
}

# 显示帮助信息
show_help() {
    cat << EOF
JeecgBoot Upstream 同步脚本 v2.1

用法: $0 [选项]

选项:
    --mode <mode>       运行模式
                        analyze     - 只分析，不合并（安全）
                        interactive - 交互模式，关键点需确认（默认）
                        auto        - 自动模式，完全自动执行（危险）

    --upstream <name>   指定 upstream 远程仓库名（默认: upstream）
    --branch <name>     指定 upstream 分支名（默认: master）
    --help              显示此帮助信息

示例:
    # 分析模式：只看看差异，不做任何修改
    $0 --mode analyze

    # 交互模式：在关键点询问用户（推荐）
    $0 --mode interactive

    # 自动模式：完全自动化（需谨慎使用）
    $0 --mode auto

工作流程（8步）:
    1. 创建备份分支和标签
    2. 识别核心修改（生成详细报告）⭐ 最关键
       ✨ 新增：智能检测是否需要同步，避免重复执行
    3. 启动合并（触发冲突）
    4. 批量保留配置文件
    5. 批量保留自定义类
    6. 批量保留新增文件
    7. 处理剩余冲突
    8. 提交并推送（可选）

新特性（v2.1）:
    ✅ 智能检测逻辑
       - 自动判断本地是否已包含 upstream 所有提交
       - 精确显示需要同步的新提交数量
       - 避免重复同步，节省时间

    ✅ 增强的状态提示
       - 清晰展示本地与 upstream 的提交关系
       - 显示共同祖先点
       - 预览 upstream 新提交内容

    ✅ 防重复检测
       - 检测 24 小时内是否已同步
       - 交互模式下二次确认

EOF
    exit 0
}

# ============================================================================
# 步骤 1：创建备份
# ============================================================================

step1_create_backup() {
    print_step "步骤 1/8: 创建备份"

    local backup_date=$(date +%Y%m%d-%H%M%S)
    local backup_branch="backup-sync-${backup_date}"
    local backup_tag="backup-tag-${backup_date}"

    print_info "创建备份分支: $backup_branch"
    git branch "$backup_branch"

    print_info "创建备份标签: $backup_tag"
    git tag "$backup_tag"

    print_success "备份创建完成"
    echo "  - 备份分支: $backup_branch"
    echo "  - 备份标签: $backup_tag"
    echo "  - 回滚命令: git reset --hard $backup_tag"

    # 保存备份信息供后续使用
    BACKUP_BRANCH="$backup_branch"
    BACKUP_TAG="$backup_tag"
}

# ============================================================================
# 步骤 2：识别核心修改（最关键！）
# ============================================================================

step2_identify_changes() {
    print_step "步骤 2/8: 识别核心修改（最关键！）"

    print_info "获取 upstream 最新代码..."
    git fetch "$UPSTREAM_REMOTE"

    # ========================================
    # 智能检测：判断是否真的需要同步
    # ========================================

    print_info "检测同步状态..."

    # 获取关键提交点
    LOCAL_HEAD=$(git rev-parse HEAD)
    UPSTREAM_HEAD=$(git rev-parse ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH})
    MERGE_BASE=$(git merge-base HEAD ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH})

    echo ""
    echo "📍 提交状态："
    echo "  ├─ 本地 HEAD:    $(git rev-parse --short HEAD) ($(git log -1 --format='%s' HEAD | head -c 50)...)"
    echo "  ├─ Upstream:     $(git rev-parse --short ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH}) ($(git log -1 --format='%s' ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH} | head -c 50)...)"
    echo "  └─ 共同祖先:     $(git rev-parse --short $MERGE_BASE)"
    echo ""

    # 情况1：本地已经包含 upstream 所有提交（本地是 upstream 的超集）
    if [ "$MERGE_BASE" = "$UPSTREAM_HEAD" ]; then
        print_success "✅ 本地分支已包含 upstream 所有提交"
        echo ""
        echo "📊 状态说明："
        echo "  本地分支是基于 upstream 开发的，包含了所有 upstream 的提交"
        echo "  本地还有额外的提交（本地定制）"
        echo ""

        # 计算本地领先的提交数
        LOCAL_AHEAD=$(git rev-list --count ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH}..HEAD)
        echo "  本地领先 upstream: $LOCAL_AHEAD 个提交"

        print_success "✨ 无需同步！本地已是最新状态"
        echo ""
        echo "💡 提示："
        echo "  如果 upstream 有新的提交，请稍后再次运行此脚本"
        echo "  查看 upstream 最新状态: git log ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH} -5"

        cleanup_and_exit 0
    fi

    # 情况2：本地与 upstream 完全一致
    if [ "$LOCAL_HEAD" = "$UPSTREAM_HEAD" ]; then
        print_success "✅ 本地分支与 upstream 完全一致"
        print_success "✨ 无需同步！"
        cleanup_and_exit 0
    fi

    # 情况3：有新的 upstream 提交需要合并
    NEW_COMMITS=$(git rev-list --count ${MERGE_BASE}..${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH})
    LOCAL_COMMITS=$(git rev-list --count ${MERGE_BASE}..HEAD)

    print_warning "检测到需要同步"
    echo ""
    echo "📊 提交对比："
    echo "  ├─ Upstream 新增提交: $NEW_COMMITS 个"
    echo "  └─ 本地新增提交:      $LOCAL_COMMITS 个"
    echo ""

    if [ "$NEW_COMMITS" -gt 0 ]; then
        echo "🔍 Upstream 新提交预览（最新 5 个）："
        git log --oneline --graph --decorate ${MERGE_BASE}..${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH} | head -10
        echo ""
    fi

    # 检查最近是否刚同步过（24小时内）
    LAST_MERGE=$(git log --all --grep="合并 upstream" --since="24 hours ago" --oneline 2>/dev/null | head -1)
    if [ -n "$LAST_MERGE" ]; then
        print_warning "检测到最近 24 小时内已同步过："
        echo "  $LAST_MERGE"
        echo ""

        if [ "$MODE" = "interactive" ]; then
            if ! ask_confirmation "确认要再次同步吗？" "n"; then
                print_info "取消同步"
                cleanup_and_exit 0
            fi
        elif [ "$MODE" = "analyze" ]; then
            print_info "分析模式：继续分析..."
        fi
    fi

    # ========================================
    # 继续文件差异分析
    # ========================================

    print_info "分析文件差异..."
    echo ""

    # 创建临时目录
    mkdir -p "$TEMP_DIR"

    # 统计差异文件
    git diff --name-only ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH} > ${TEMP_DIR}/all-changes.txt
    git diff --name-status ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH} > ${TEMP_DIR}/all-changes-status.txt

    # 识别不同类型的文件
    grep -E "\.(yml|yaml|properties|xml)$" ${TEMP_DIR}/all-changes.txt > ${TEMP_DIR}/config-files.txt 2>/dev/null || true
    grep -i "custom" ${TEMP_DIR}/all-changes.txt > ${TEMP_DIR}/custom-files.txt 2>/dev/null || true
    grep "^A" ${TEMP_DIR}/all-changes-status.txt | awk '{print $2}' > ${TEMP_DIR}/new-files.txt 2>/dev/null || true
    grep "\.java$" ${TEMP_DIR}/all-changes.txt > ${TEMP_DIR}/java-files.txt 2>/dev/null || true
    grep -E "\.(vue|ts|js)$" ${TEMP_DIR}/all-changes.txt > ${TEMP_DIR}/frontend-files.txt 2>/dev/null || true

    # 统计数量
    TOTAL_CHANGES=$(cat ${TEMP_DIR}/all-changes.txt | wc -l | tr -d ' ')
    CONFIG_COUNT=$(cat ${TEMP_DIR}/config-files.txt | wc -l | tr -d ' ')
    CUSTOM_COUNT=$(cat ${TEMP_DIR}/custom-files.txt | wc -l | tr -d ' ')
    NEW_COUNT=$(cat ${TEMP_DIR}/new-files.txt | wc -l | tr -d ' ')
    JAVA_COUNT=$(cat ${TEMP_DIR}/java-files.txt | wc -l | tr -d ' ')
    FRONTEND_COUNT=$(cat ${TEMP_DIR}/frontend-files.txt | wc -l | tr -d ' ')

    # 生成详细报告
    generate_analysis_report

    # 显示摘要
    print_success "分析完成！"
    echo ""
    echo "📊 修改统计:"
    echo "  ├─ 总修改文件数: $TOTAL_CHANGES"
    echo "  ├─ 配置文件: $CONFIG_COUNT"
    echo "  ├─ 自定义类: $CUSTOM_COUNT"
    echo "  ├─ 新增文件: $NEW_COUNT"
    echo "  ├─ Java 文件: $JAVA_COUNT"
    echo "  └─ 前端文件: $FRONTEND_COUNT"
    echo ""
    echo "📄 详细报告已生成: $REPORT_FILE"

    # 如果是分析模式，到此结束
    if [ "$MODE" = "analyze" ]; then
        print_success "分析模式完成，未执行合并操作"
        echo ""
        echo "下一步："
        echo "  1. 查看报告: cat $REPORT_FILE"
        echo "  2. 确认无误后执行: $0 --mode interactive"
        cleanup_and_exit 0
    fi

    # 交互模式：询问是否继续
    if [ "$MODE" = "interactive" ]; then
        echo ""
        if ! ask_confirmation "是否继续执行合并？" "n"; then
            print_warning "用户取消操作"
            cleanup_and_exit 0
        fi
    fi
}

# 生成详细分析报告
generate_analysis_report() {
    cat > "$REPORT_FILE" << EOF
# JeecgBoot Upstream 同步分析报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**当前分支**: $LOCAL_BRANCH
**对比目标**: ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH}
**备份分支**: $BACKUP_BRANCH
**备份标签**: $BACKUP_TAG

---

## 🔍 同步状态检测

### 提交状态
- **本地 HEAD**: \`$(git rev-parse --short HEAD)\` - $(git log -1 --format='%s' HEAD)
- **Upstream**: \`$(git rev-parse --short ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH})\` - $(git log -1 --format='%s' ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH})
- **共同祖先**: \`$(git rev-parse --short $MERGE_BASE)\`

### 提交对比
- **Upstream 新增提交**: $NEW_COMMITS 个
- **本地新增提交**: $LOCAL_COMMITS 个

### Upstream 新提交列表
\`\`\`
$(git log --oneline ${MERGE_BASE}..${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH} | head -20)
$([ $NEW_COMMITS -gt 20 ] && echo "... 还有 $(( NEW_COMMITS - 20 )) 个提交" || true)
\`\`\`

---

## 📊 文件差异统计

| 类型 | 数量 | 占比 |
|------|------|------|
| 总修改文件 | $TOTAL_CHANGES | 100% |
| 配置文件 | $CONFIG_COUNT | $(( TOTAL_CHANGES > 0 ? CONFIG_COUNT * 100 / TOTAL_CHANGES : 0 ))% |
| 自定义类 | $CUSTOM_COUNT | $(( TOTAL_CHANGES > 0 ? CUSTOM_COUNT * 100 / TOTAL_CHANGES : 0 ))% |
| 新增文件 | $NEW_COUNT | $(( TOTAL_CHANGES > 0 ? NEW_COUNT * 100 / TOTAL_CHANGES : 0 ))% |
| Java 文件 | $JAVA_COUNT | $(( TOTAL_CHANGES > 0 ? JAVA_COUNT * 100 / TOTAL_CHANGES : 0 ))% |
| 前端文件 | $FRONTEND_COUNT | $(( TOTAL_CHANGES > 0 ? FRONTEND_COUNT * 100 / TOTAL_CHANGES : 0 ))% |

---

## 🔴 必须保留的文件（核心定制）

### 配置文件 ($CONFIG_COUNT 个)
\`\`\`
$(cat ${TEMP_DIR}/config-files.txt)
\`\`\`

### 自定义类 ($CUSTOM_COUNT 个)
\`\`\`
$(cat ${TEMP_DIR}/custom-files.txt)
\`\`\`

### 新增文件 ($NEW_COUNT 个)
\`\`\`
$(cat ${TEMP_DIR}/new-files.txt)
\`\`\`

---

## 🟢 可以使用 upstream 版本的文件

建议对以下类型的文件使用 upstream 版本：
- 框架核心代码（jeecg-boot-base/**）
- 未定制的系统模块
- 依赖配置（pom.xml, package.json）

---

## 📋 推荐处理策略

### 策略 1: 自动保留（git checkout --ours）
- ✅ 所有配置文件
- ✅ 所有自定义类
- ✅ 所有新增文件

### 策略 2: 自动使用 upstream（git checkout --theirs）
- ✅ 框架核心文件
- ✅ 依赖配置文件

### 策略 3: 手动检查
- ⚠️ 既有框架更新又有本地修改的业务模块
- ⚠️ 不确定的文件

---

## 🔍 详细文件清单

### Java 文件
\`\`\`
$(cat ${TEMP_DIR}/java-files.txt | head -50)
$([ $(cat ${TEMP_DIR}/java-files.txt | wc -l) -gt 50 ] && echo "... 还有 $(( $(cat ${TEMP_DIR}/java-files.txt | wc -l) - 50 )) 个文件" || true)
\`\`\`

### 前端文件
\`\`\`
$(cat ${TEMP_DIR}/frontend-files.txt | head -50)
$([ $(cat ${TEMP_DIR}/frontend-files.txt | wc -l) -gt 50 ] && echo "... 还有 $(( $(cat ${TEMP_DIR}/frontend-files.txt | wc -l) - 50 )) 个文件" || true)
\`\`\`

---

## ⚠️ 注意事项

1. **配置文件**: 虽然保留本地版本，但需检查 upstream 是否新增配置项
2. **自定义类**: 注意框架升级后 API 是否有变化
3. **依赖文件**: 使用 upstream 版本后需测试兼容性
4. **充分测试**: 合并后务必测试核心功能

---

## 🚀 下一步操作

1. 仔细阅读本报告，理解修改分布
2. 决定使用哪种模式继续：
   - 交互模式（推荐）: \`$0 --mode interactive\`
   - 自动模式（快速）: \`$0 --mode auto\`
3. 执行合并
4. 充分测试

EOF

    print_success "报告已生成: $REPORT_FILE"
}

# ============================================================================
# 步骤 3：启动合并
# ============================================================================

step3_start_merge() {
    print_step "步骤 3/8: 启动合并"

    print_info "开始合并 ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH}..."

    if git merge ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH} --no-commit --no-ff 2>&1 | tee ${TEMP_DIR}/merge-output.txt; then
        print_success "合并完成，无冲突"
        HAS_CONFLICTS=false
    else
        if grep -q "CONFLICT" ${TEMP_DIR}/merge-output.txt; then
            print_warning "检测到冲突，将进行批量处理"
            HAS_CONFLICTS=true

            # 统计冲突
            INITIAL_CONFLICTS=$(git diff --name-only --diff-filter=U | wc -l | tr -d ' ')
            print_info "冲突文件数: $INITIAL_CONFLICTS"
        else
            print_error "合并失败，请检查错误信息"
            cat ${TEMP_DIR}/merge-output.txt
            cleanup_and_exit 1
        fi
    fi
}

# ============================================================================
# 步骤 4：批量保留配置文件
# ============================================================================

step4_keep_configs() {
    print_step "步骤 4/8: 批量保留配置文件"

    if [ ! -s ${TEMP_DIR}/config-files.txt ]; then
        print_info "没有配置文件需要处理"
        return
    fi

    print_info "保留 $CONFIG_COUNT 个配置文件的本地版本..."

    local count=0
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            git checkout --ours -- "$file" 2>/dev/null || true
            git add "$file" 2>/dev/null || true
            count=$((count + 1))
            echo "  [$count/$CONFIG_COUNT] $file"
        fi
    done < ${TEMP_DIR}/config-files.txt

    print_success "配置文件处理完成: $count 个"
}

# ============================================================================
# 步骤 5：批量保留自定义类
# ============================================================================

step5_keep_custom_classes() {
    print_step "步骤 5/8: 批量保留自定义类"

    if [ ! -s ${TEMP_DIR}/custom-files.txt ]; then
        print_info "没有自定义类需要处理"
        return
    fi

    print_info "保留 $CUSTOM_COUNT 个自定义类的本地版本..."

    local count=0
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            git checkout --ours -- "$file" 2>/dev/null || true
            git add "$file" 2>/dev/null || true
            count=$((count + 1))
            echo "  [$count/$CUSTOM_COUNT] $file"
        fi
    done < ${TEMP_DIR}/custom-files.txt

    print_success "自定义类处理完成: $count 个"
}

# ============================================================================
# 步骤 6：批量保留新增文件
# ============================================================================

step6_keep_new_files() {
    print_step "步骤 6/8: 批量保留新增文件"

    if [ ! -s ${TEMP_DIR}/new-files.txt ]; then
        print_info "没有新增文件需要处理"
        return
    fi

    print_info "保留 $NEW_COUNT 个新增文件..."

    local count=0
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            git checkout --ours -- "$file" 2>/dev/null || true
            git add "$file" 2>/dev/null || true
            count=$((count + 1))
            echo "  [$count/$NEW_COUNT] $file"
        fi
    done < ${TEMP_DIR}/new-files.txt

    print_success "新增文件处理完成: $count 个"
}

# ============================================================================
# 步骤 7：处理剩余冲突
# ============================================================================

step7_handle_remaining_conflicts() {
    print_step "步骤 7/8: 处理剩余冲突"

    # 检查剩余冲突
    REMAINING_CONFLICTS=$(git diff --name-only --diff-filter=U 2>/dev/null | wc -l | tr -d ' ')

    if [ "$REMAINING_CONFLICTS" -eq 0 ]; then
        print_success "没有剩余冲突！"
        return
    fi

    print_info "剩余冲突文件: $REMAINING_CONFLICTS 个"

    if [ "$HAS_CONFLICTS" = true ] && [ -n "$INITIAL_CONFLICTS" ]; then
        local resolved=$((INITIAL_CONFLICTS - REMAINING_CONFLICTS))
        print_success "已自动解决: $resolved 个 ($(( resolved * 100 / INITIAL_CONFLICTS ))%)"
    fi

    # 显示剩余冲突文件
    echo ""
    echo "剩余冲突文件列表:"
    git diff --name-only --diff-filter=U | head -20
    if [ "$REMAINING_CONFLICTS" -gt 20 ]; then
        echo "... 还有 $(( REMAINING_CONFLICTS - 20 )) 个文件"
    fi
    echo ""

    # 分析剩余冲突类型
    git diff --name-only --diff-filter=U > ${TEMP_DIR}/remaining-conflicts.txt

    # 提供批量处理选项
    if [ "$MODE" = "interactive" ]; then
        echo "批量处理选项:"
        echo "  1. 保留所有本地版本 (git checkout --ours)"
        echo "  2. 使用所有 upstream 版本 (git checkout --theirs)"
        echo "  3. 对框架文件使用 upstream，其他手动处理"
        echo "  4. 跳过，稍后使用 IDE 手动处理"
        echo ""
        read -p "$(echo -e ${CYAN}请选择 [1-4]: ${NC})" choice

        case $choice in
            1)
                print_info "保留所有本地版本..."
                git diff --name-only --diff-filter=U | xargs -I {} git checkout --ours -- {}
                git add .
                print_success "已保留所有本地版本"
                ;;
            2)
                print_warning "使用所有 upstream 版本..."
                if ask_confirmation "确认要覆盖所有本地修改吗？" "n"; then
                    git diff --name-only --diff-filter=U | xargs -I {} git checkout --theirs -- {}
                    git add .
                    print_success "已使用所有 upstream 版本"
                fi
                ;;
            3)
                print_info "对框架文件使用 upstream 版本..."
                git diff --name-only --diff-filter=U | grep -E "jeecg-boot-base|jeecg-module-system" | xargs -I {} git checkout --theirs -- {} 2>/dev/null || true
                git add . 2>/dev/null || true

                REMAINING=$(git diff --name-only --diff-filter=U | wc -l | tr -d ' ')
                print_success "框架文件已处理，剩余 $REMAINING 个需手动处理"
                ;;
            4)
                print_info "跳过批量处理"
                ;;
            *)
                print_warning "无效选择，跳过"
                ;;
        esac
    elif [ "$MODE" = "auto" ]; then
        print_info "自动模式：对框架文件使用 upstream 版本..."
        git diff --name-only --diff-filter=U | grep -E "jeecg-boot-base|pom\.xml|package\.json" | xargs -I {} git checkout --theirs -- {} 2>/dev/null || true
        git add . 2>/dev/null || true
    fi

    # 最终检查
    FINAL_CONFLICTS=$(git diff --name-only --diff-filter=U 2>/dev/null | wc -l | tr -d ' ')

    if [ "$FINAL_CONFLICTS" -gt 0 ]; then
        print_warning "仍有 $FINAL_CONFLICTS 个冲突需要手动处理"
        echo ""
        echo "建议："
        echo "  1. 使用 IDE 的冲突解决工具（推荐）"
        echo "  2. 或手动编辑文件解决冲突标记（<<<<<<<, =======, >>>>>>>）"
        echo "  3. 解决后执行: git add . && git commit"
        echo ""

        if [ "$MODE" = "interactive" ]; then
            if ! ask_confirmation "现在暂停，让您手动处理剩余冲突。处理完成后继续？" "n"; then
                print_info "请手动处理冲突后，执行以下命令完成合并："
                echo ""
                echo "  git add ."
                echo "  git commit -m \"合并 upstream/${UPSTREAM_BRANCH}，保留本地定制\""
                echo "  git push origin $LOCAL_BRANCH --force-with-lease"
                echo ""
                cleanup_and_exit 0
            fi
        fi
    else
        print_success "所有冲突已解决！"
    fi
}

# ============================================================================
# 步骤 8：提交并推送
# ============================================================================

step8_commit_and_push() {
    print_step "步骤 8/8: 提交并推送"

    # 检查是否还有未解决的冲突
    if [ $(git diff --name-only --diff-filter=U 2>/dev/null | wc -l) -gt 0 ]; then
        print_error "仍有未解决的冲突，无法提交"
        git diff --name-only --diff-filter=U
        cleanup_and_exit 1
    fi

    # 显示变更摘要
    print_info "变更摘要:"
    echo ""
    git diff --cached --stat | head -20
    echo ""

    # 交互模式：询问是否提交
    if [ "$MODE" = "interactive" ]; then
        if ! ask_confirmation "是否提交合并？" "y"; then
            print_warning "用户取消提交"
            echo ""
            echo "未提交的更改已暂存，您可以稍后提交："
            echo "  git commit -m \"合并 upstream/${UPSTREAM_BRANCH}\""
            cleanup_and_exit 0
        fi
    fi

    # 生成提交信息
    local commit_msg=$(cat <<EOF
合并 upstream/${UPSTREAM_BRANCH} 最新代码，保留 SIMBEST 定制

📊 统计:
- 总修改文件: $TOTAL_CHANGES
- 配置文件: $CONFIG_COUNT (已保留本地版本)
- 自定义类: $CUSTOM_COUNT (已保留本地版本)
- 新增文件: $NEW_COUNT (已保留)

✅ 自动处理:
- 批量保留配置文件
- 批量保留自定义类
- 批量保留新增文件

🔄 框架更新:
- 更新到 upstream 最新版本
- 保留 SIMBEST 核心定制

⚠️ 测试状态: 待测试

备份: $BACKUP_TAG
EOF
)

    print_info "提交合并..."
    git commit -m "$commit_msg"

    print_success "提交完成"

    # 询问是否推送
    if [ "$MODE" = "interactive" ]; then
        echo ""
        if ! ask_confirmation "是否推送到远程仓库 origin/$LOCAL_BRANCH？" "n"; then
            print_info "未推送，您可以稍后手动推送："
            echo "  git push origin $LOCAL_BRANCH --force-with-lease"
            cleanup_and_exit 0
        fi
    fi

    print_info "推送到 origin/$LOCAL_BRANCH..."
    if git push origin "$LOCAL_BRANCH" --force-with-lease; then
        print_success "推送成功！"
    else
        print_error "推送失败，可能需要先拉取远程更改"
        echo ""
        echo "建议操作："
        echo "  git pull --rebase origin $LOCAL_BRANCH"
        echo "  git push origin $LOCAL_BRANCH --force-with-lease"
        cleanup_and_exit 1
    fi
}

# ============================================================================
# 清理和退出
# ============================================================================

cleanup_and_exit() {
    local exit_code=$1

    # 清理临时文件
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi

    if [ $exit_code -eq 0 ]; then
        print_success "同步流程完成！"
        echo ""
        echo "📋 重要提醒:"
        echo "  1. 测试应用是否正常启动"
        echo "  2. 测试核心功能是否正常"
        echo "  3. 检查日志是否有异常"
        echo "  4. 如有问题，回滚到备份: git reset --hard $BACKUP_TAG"
    fi

    exit $exit_code
}

# 捕获中断信号
trap 'print_error "用户中断操作"; cleanup_and_exit 1' INT TERM

# ============================================================================
# 主流程
# ============================================================================

main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --mode)
                MODE="$2"
                shift 2
                ;;
            --upstream)
                UPSTREAM_REMOTE="$2"
                shift 2
                ;;
            --branch)
                UPSTREAM_BRANCH="$2"
                shift 2
                ;;
            --help)
                show_help
                ;;
            *)
                print_error "未知参数: $1"
                echo "使用 --help 查看帮助"
                exit 1
                ;;
        esac
    done

    # 验证模式
    if [[ ! "$MODE" =~ ^(analyze|interactive|auto)$ ]]; then
        print_error "无效的模式: $MODE"
        echo "有效模式: analyze, interactive, auto"
        exit 1
    fi

    # 显示欢迎信息
    echo ""
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║   JeecgBoot Upstream 同步脚本 v2.1                ║"
    echo "║   ✨ 新增：智能检测，避免重复同步                 ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo ""
    print_info "运行模式: $MODE"
    print_info "当前分支: $LOCAL_BRANCH"
    print_info "同步目标: ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH}"
    echo ""

    # 安全检查
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "工作区有未提交的修改"
        git status --short
        echo ""
        if ! ask_confirmation "是否继续？未提交的修改可能丢失！" "n"; then
            print_info "请先提交或暂存您的修改"
            exit 0
        fi
    fi

    # 检查 upstream 是否存在
    if ! git remote | grep -q "^${UPSTREAM_REMOTE}$"; then
        print_error "未找到远程仓库: $UPSTREAM_REMOTE"
        echo ""
        echo "请先添加 upstream:"
        echo "  git remote add $UPSTREAM_REMOTE <upstream-url>"
        exit 1
    fi

    # 执行八步流程
    step1_create_backup
    step2_identify_changes

    # 如果是分析模式，在 step2 中已经退出
    # 以下步骤只在 interactive 和 auto 模式执行

    step3_start_merge
    step4_keep_configs
    step5_keep_custom_classes
    step6_keep_new_files
    step7_handle_remaining_conflicts
    step8_commit_and_push

    cleanup_and_exit 0
}

# 执行主流程
main "$@"
