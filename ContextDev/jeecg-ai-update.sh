#!/bin/bash

# JeecgBoot AI 环境更新维护脚本 v3.0 (SuperClaude Framework 完整集成版)
# 实现双框架同步更新：Context Engineering + SuperClaude Framework
# 支持上游同步、配置更新、版本管理和集成验证

set -e

echo "🔄 JeecgBoot AI 环境更新维护 v3.0 (双框架完整集成版)"
echo "=================================================================="
echo "📋 维护目标: Context Engineering (8.5/10) + SuperClaude Framework (目标 8.5/10)"
echo "🏗️ 架构模式: ContextDev 集成层，双框架隔离更新"
echo ""

# ==================== 全局变量定义 ====================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONTEXT_DEV_DIR="$PROJECT_ROOT/ContextDev"

# ContextDev 集成层目录结构
UPSTREAM_DIR="$CONTEXT_DEV_DIR/upstream"
INTEGRATION_DIR="$CONTEXT_DEV_DIR/integration"
CONFIG_DIR="$CONTEXT_DEV_DIR/config"
SCRIPTS_DIR="$CONTEXT_DEV_DIR/scripts"

# 上游项目目录
CONTEXT_ENGINEERING_DIR="$UPSTREAM_DIR/context-engineering"
SUPERCLAUDE_DIR="$UPSTREAM_DIR/superclaude"

# 工作目录
PRP_WORK_DIR="$PROJECT_ROOT/PRPs"
PROJECT_CLAUDE_CONFIG="$PRP_WORK_DIR/CLAUDE.md"

# 更新配置
CONTEXT_ENGINEERING_REPO="https://github.com/coleam00/context-engineering-intro.git"
SUPERCLAUDE_REPO="https://github.com/SuperClaude-Org/SuperClaude_Framework.git"

# 日志和备份
UPDATE_LOG="$CONTEXT_DEV_DIR/update.log"
BACKUP_DIR="$CONTEXT_DEV_DIR/backup-$(date +%Y%m%d-%H%M%S)"
INTEGRATION_STATUS="$CONTEXT_DEV_DIR/integration-status.json"

# ==================== 工具函数 ====================

# 日志记录函数
log_info() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" | tee -a "$UPDATE_LOG"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" | tee -a "$UPDATE_LOG"
}

log_success() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" | tee -a "$UPDATE_LOG"
}

# 更新集成状态
update_integration_status() {
    local component="$1"
    local status="$2"
    local version="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # 创建或更新状态文件
    if [[ ! -f "$INTEGRATION_STATUS" ]]; then
        echo '{"integration_status": {}, "last_updated": ""}' > "$INTEGRATION_STATUS"
    fi

    # 使用 python 更新 JSON (兼容 macOS)
    python3 -c "
import json
import sys

try:
    with open('$INTEGRATION_STATUS', 'r') as f:
        data = json.load(f)

    data['integration_status']['$component'] = {
        'status': '$status',
        'version': '$version',
        'timestamp': '$timestamp'
    }
    data['last_updated'] = '$timestamp'

    with open('$INTEGRATION_STATUS', 'w') as f:
        json.dump(data, f, indent=2)

    print(f'✅ 状态更新: {\"$component\"} -> {\"$status\"}')
except Exception as e:
    print(f'⚠️ 状态更新失败: {e}', file=sys.stderr)
"
}

# ==================== 备份功能 ====================

# 备份 ContextDev 集成配置
backup_integration_config() {
    log_info "备份 ContextDev 集成配置..."

    mkdir -p "$BACKUP_DIR"

    # 备份集成状态
    if [[ -f "$INTEGRATION_STATUS" ]]; then
        cp "$INTEGRATION_STATUS" "$BACKUP_DIR/"
        log_success "集成状态已备份"
    fi

    # 备份配置文件
    if [[ -d "$CONFIG_DIR" ]]; then
        cp -r "$CONFIG_DIR" "$BACKUP_DIR/"
        log_success "配置文件已备份"
    fi

    # 备份集成脚本
    if [[ -d "$SCRIPTS_DIR" ]]; then
        cp -r "$SCRIPTS_DIR" "$BACKUP_DIR/"
        log_success "集成脚本已备份"
    fi

    # 备份 integration 目录
    if [[ -d "$INTEGRATION_DIR" ]]; then
        cp -r "$INTEGRATION_DIR" "$BACKUP_DIR/"
        log_success "集成配置已备份"
    fi

    # 备份 PRP 工作目录
    if [[ -d "$PRP_WORK_DIR" ]]; then
        cp -r "$PRP_WORK_DIR" "$BACKUP_DIR/PRPs_backup"
        log_success "PRP 工作目录已备份"
    fi

    # 备份项目级别 CLAUDE.md
    if [[ -f "$PROJECT_CLAUDE_CONFIG" ]]; then
        cp "$PROJECT_CLAUDE_CONFIG" "$BACKUP_DIR/PROJECT_CLAUDE.md"
        log_success "项目级别 CLAUDE.md 已备份"
    fi

    # 备份现有的 jeecg-ai-config.json
    if [[ -f "$CONTEXT_DEV_DIR/jeecg-ai-config.json" ]]; then
        cp "$CONTEXT_DEV_DIR/jeecg-ai-config.json" "$BACKUP_DIR/"
        log_success "JeecgBoot AI 配置已备份"
    fi

    log_success "ContextDev 集成配置备份完成: $BACKUP_DIR"
}

# ==================== 上游项目同步 ====================

# 同步 Context Engineering 项目
sync_context_engineering() {
    log_info "同步 Context Engineering 项目..."

    if [[ ! -d "$CONTEXT_ENGINEERING_DIR" ]]; then
        log_info "Context Engineering 目录不存在，重新克隆..."
        git clone "$CONTEXT_ENGINEERING_REPO" "$CONTEXT_ENGINEERING_DIR"
        log_success "Context Engineering 重新克隆完成"
    else
        log_info "更新现有的 Context Engineering..."
        cd "$CONTEXT_ENGINEERING_DIR"

        # 检查是否有本地修改
        if ! git diff --quiet; then
            log_info "检测到本地修改，暂存更改..."
            git stash push -m "Auto-stash before update $(date)"
        fi

        # 拉取最新更改
        if git pull origin main; then
            log_success "Context Engineering 更新成功"
        else
            log_error "Context Engineering 更新失败"
            return 1
        fi

        cd "$CONTEXT_DEV_DIR"
    fi

    # 获取版本信息
    local ce_version="unknown"
    if [[ -f "$CONTEXT_ENGINEERING_DIR/README.md" ]]; then
        ce_version=$(grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' "$CONTEXT_ENGINEERING_DIR/README.md" | head -1 || echo "latest")
    fi

    update_integration_status "context_engineering" "updated" "$ce_version"
    log_success "Context Engineering 同步完成: $ce_version"
}

# 同步 SuperClaude Framework 项目
sync_superclaude_framework() {
    log_info "同步 SuperClaude Framework 项目..."

    if [[ ! -d "$SUPERCLAUDE_DIR" ]]; then
        log_info "SuperClaude Framework 目录不存在，重新克隆..."
        git clone "$SUPERCLAUDE_REPO" "$SUPERCLAUDE_DIR"
        log_success "SuperClaude Framework 重新克隆完成"
    else
        log_info "更新现有的 SuperClaude Framework..."
        cd "$SUPERCLAUDE_DIR"

        # 检查是否有本地修改
        if ! git diff --quiet; then
            log_info "检测到本地修改，暂存更改..."
            git stash push -m "Auto-stash before update $(date)"
        fi

        # 拉取最新更改
        if git pull origin master; then
            log_success "SuperClaude Framework 更新成功"
        else
            log_error "SuperClaude Framework 更新失败"
            return 1
        fi

        cd "$CONTEXT_DEV_DIR"
    fi

    # 检查版本要求 (v3.0.0+)
    local sc_version="unknown"
    if [[ -f "$SUPERCLAUDE_DIR/VERSION" ]]; then
        sc_version=$(cat "$SUPERCLAUDE_DIR/VERSION")
    elif [[ -f "$SUPERCLAUDE_DIR/setup.py" ]]; then
        sc_version=$(grep -o "version='[^']*'" "$SUPERCLAUDE_DIR/setup.py" | cut -d"'" -f2)
    fi

    # 验证版本要求
    if [[ "$sc_version" != "unknown" ]]; then
        local major_version=$(echo "$sc_version" | cut -d. -f1)
        if [[ $major_version -lt 3 ]]; then
            log_error "SuperClaude Framework 版本过低: $sc_version，需要 v3.0.0+"
            return 1
        fi
        log_success "SuperClaude Framework 版本验证通过: $sc_version"
    else
        log_info "无法确定 SuperClaude Framework 版本，继续更新"
        sc_version="latest"
    fi

    update_integration_status "superclaude_framework" "updated" "$sc_version"
    log_success "SuperClaude Framework 同步完成: $sc_version"
}

# 更新 SuperClaude Python 包
update_superclaude_package() {
    log_info "更新 SuperClaude Python 包..."

    # 检查当前安装的版本
    local current_version=$(python3 -c "
try:
    import SuperClaude
    print(SuperClaude.__version__)
except ImportError:
    print('not_installed')
except Exception:
    print('unknown')
" 2>/dev/null)

    log_info "当前 SuperClaude 版本: $current_version"

    # 更新包
    local update_success=false

    # 尝试使用 uv 更新
    if command -v uv &> /dev/null; then
        log_info "使用 uv 更新 SuperClaude..."
        if uv pip install --upgrade SuperClaude; then
            update_success=true
            log_success "使用 uv 更新 SuperClaude 成功"
        else
            log_error "uv 更新失败，尝试使用 pip"
        fi
    fi

    # 备选：使用 pip 更新
    if [[ "$update_success" == false ]]; then
        log_info "使用 pip 更新 SuperClaude..."
        if pip3 install --upgrade SuperClaude; then
            update_success=true
            log_success "使用 pip 更新 SuperClaude 成功"
        else
            log_error "pip 更新也失败"
            return 1
        fi
    fi

    # 验证更新后的版本
    local new_version=$(python3 -c "
try:
    import SuperClaude
    print(SuperClaude.__version__)
except Exception as e:
    print(f'error:{e}')
" 2>/dev/null)

    if [[ "$new_version" != error:* ]] && [[ "$new_version" != "not_installed" ]]; then
        log_success "SuperClaude 更新验证成功: v$new_version"
        update_integration_status "superclaude_package" "updated" "$new_version"

        if [[ "$new_version" != "$current_version" ]]; then
            log_success "SuperClaude 版本升级: $current_version → $new_version"
        else
            log_info "SuperClaude 已是最新版本: $new_version"
        fi
    else
        log_error "SuperClaude 更新验证失败: $new_version"
        return 1
    fi

    log_success "SuperClaude Python 包更新完成"
}

# ==================== 配置更新 ====================

# 更新集成配置文件
update_integration_configs() {
    log_info "更新集成配置文件..."

    # 备份现有配置
    if [[ -d "$CONFIG_DIR" ]]; then
        cp -r "$CONFIG_DIR" "$BACKUP_DIR/config_backup"
        log_success "现有配置已备份"
    fi

    # 重新生成配置文件 (调用安装脚本中的函数)
    if [[ -f "$CONTEXT_DEV_DIR/jeecg-ai-setup.sh" ]]; then
        log_info "调用安装脚本重新生成配置..."
        source "$CONTEXT_DEV_DIR/jeecg-ai-setup.sh"
        generate_integration_configs
        log_success "集成配置文件更新完成"
    else
        log_error "安装脚本不存在，无法更新配置"
        return 1
    fi

    update_integration_status "configuration" "updated" "v3.0"
}

# 更新集成脚本
update_integration_scripts() {
    log_info "更新集成脚本..."

    # 备份现有脚本
    if [[ -d "$SCRIPTS_DIR" ]]; then
        cp -r "$SCRIPTS_DIR" "$BACKUP_DIR/scripts_backup"
        log_success "现有脚本已备份"
    fi

    # 重新生成脚本 (调用安装脚本中的函数)
    if [[ -f "$CONTEXT_DEV_DIR/jeecg-ai-setup.sh" ]]; then
        log_info "调用安装脚本重新生成脚本..."
        source "$CONTEXT_DEV_DIR/jeecg-ai-setup.sh"
        generate_integration_scripts
        log_success "集成脚本更新完成"
    else
        log_error "安装脚本不存在，无法更新脚本"
        return 1
    fi

    update_integration_status "scripts" "updated" "v3.0"
}

# ==================== 验证和恢复 ====================

# 验证集成状态
validate_integration() {
    log_info "验证集成状态..."

    if [[ -f "$SCRIPTS_DIR/validate-integration.sh" ]]; then
        if bash "$SCRIPTS_DIR/validate-integration.sh"; then
            log_success "集成验证通过"
            return 0
        else
            log_error "集成验证失败"
            return 1
        fi
    else
        log_error "验证脚本不存在"
        return 1
    fi
}

# 恢复配置 (如果更新失败)
restore_from_backup() {
    log_info "从备份恢复配置..."

    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_error "备份目录不存在: $BACKUP_DIR"
        return 1
    fi

    # 恢复配置文件
    if [[ -d "$BACKUP_DIR/config" ]]; then
        rm -rf "$CONFIG_DIR"
        cp -r "$BACKUP_DIR/config" "$CONFIG_DIR"
        log_success "配置文件已恢复"
    fi

    # 恢复集成脚本
    if [[ -d "$BACKUP_DIR/scripts" ]]; then
        rm -rf "$SCRIPTS_DIR"
        cp -r "$BACKUP_DIR/scripts" "$SCRIPTS_DIR"
        log_success "集成脚本已恢复"
    fi

    # 恢复集成状态
    if [[ -f "$BACKUP_DIR/integration-status.json" ]]; then
        cp "$BACKUP_DIR/integration-status.json" "$INTEGRATION_STATUS"
        log_success "集成状态已恢复"
    fi

    log_success "配置恢复完成"
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理旧备份..."

    # 保留最近5个备份
    local backup_count=$(find "$CONTEXT_DEV_DIR" -maxdepth 1 -name "backup-*" -type d | wc -l)
    if [[ $backup_count -gt 5 ]]; then
        find "$CONTEXT_DEV_DIR" -maxdepth 1 -name "backup-*" -type d | sort | head -n $((backup_count - 5)) | xargs rm -rf
        log_success "清理了 $((backup_count - 5)) 个旧备份"
    else
        log_info "备份数量合理，无需清理"
    fi
}

# ==================== 主更新流程 ====================

# 主更新流程 - SuperClaude Framework 完整更新
main() {
    local start_time=$(date +%s)

    echo ""
    echo "🔄 开始 JeecgBoot AI 环境 v3.0 更新维护..."
    echo "📋 更新方案: 双框架隔离更新 (Context Engineering + SuperClaude Framework)"
    echo "🎯 目标: 保持集成完整性，同步上游最新版本"
    echo ""

    # 初始化日志
    echo "$(date '+%Y-%m-%d %H:%M:%S') [START] JeecgBoot AI 环境更新开始" > "$UPDATE_LOG"

    # 检查环境
    log_info "检查更新环境..."
    if [[ ! -d "$CONTEXT_DEV_DIR" ]]; then
        log_error "ContextDev 目录不存在，请先运行 jeecg-ai-setup.sh 安装"
        exit 1
    fi

    if [[ ! -f "$INTEGRATION_STATUS" ]]; then
        log_error "集成状态文件不存在，请先运行 jeecg-ai-setup.sh 安装"
        exit 1
    fi

    # 备份现有配置
    log_info "=== 第一步：备份现有配置 ==="
    backup_integration_config

    # 同步上游项目
    log_info "=== 第二步：同步上游项目 ==="

    if sync_context_engineering; then
        log_success "Context Engineering 同步成功"
    else
        log_error "Context Engineering 同步失败"
        restore_from_backup
        exit 1
    fi

    if sync_superclaude_framework; then
        log_success "SuperClaude Framework 同步成功"
    else
        log_error "SuperClaude Framework 同步失败"
        restore_from_backup
        exit 1
    fi

    # 更新 Python 包
    log_info "=== 第三步：更新 Python 包 ==="
    if update_superclaude_package; then
        log_success "SuperClaude Python 包更新成功"
    else
        log_error "SuperClaude Python 包更新失败"
        restore_from_backup
        exit 1
    fi

    # 更新配置文件
    log_info "=== 第四步：更新配置文件 ==="
    if update_integration_configs; then
        log_success "集成配置更新成功"
    else
        log_error "集成配置更新失败"
        restore_from_backup
        exit 1
    fi

    # 更新集成脚本
    log_info "=== 第五步：更新集成脚本 ==="
    if update_integration_scripts; then
        log_success "集成脚本更新成功"
    else
        log_error "集成脚本更新失败"
        restore_from_backup
        exit 1
    fi

    # 验证更新结果
    log_info "=== 第六步：验证更新结果 ==="
    if validate_integration; then
        log_success "更新验证通过"
    else
        log_error "更新验证失败"
        restore_from_backup
        exit 1
    fi

    # 清理旧备份
    cleanup_old_backups

    # 显示更新结果
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo ""
    echo "🎉 JeecgBoot AI 环境 v3.0 更新完成！"
    echo "⏱️  总耗时: ${duration} 秒"
    echo ""
    echo "📊 更新状态:"
    if [[ -f "$INTEGRATION_STATUS" ]]; then
        python3 -c "
import json
with open('$INTEGRATION_STATUS') as f:
    status = json.load(f)

print('集成状态:')
for component, info in status.get('integration_status', {}).items():
    print(f'  ✅ {component}: {info.get(\"status\", \"unknown\")} ({info.get(\"version\", \"unknown\")})')
"
    fi
    echo ""
    echo "📋 更新内容:"
    echo "  ✅ Context Engineering: 已同步到最新版本"
    echo "  ✅ SuperClaude Framework: 已同步到最新版本"
    echo "  ✅ SuperClaude Python 包: 已更新到最新版本"
    echo "  ✅ 集成配置文件: 已更新"
    echo "  ✅ 集成脚本: 已更新"
    echo ""
    echo "🔧 验证命令:"
    echo "  bash ContextDev/scripts/validate-integration.sh"
    echo ""
    echo "📖 更新日志: $UPDATE_LOG"
    echo "💾 备份位置: $BACKUP_DIR"
    echo ""

    log_success "JeecgBoot AI 环境 v3.0 更新完成"
}

# ==================== 参数处理 ====================

# 检查参数和显示帮助
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "🔄 JeecgBoot AI 环境更新维护脚本 v3.0 (SuperClaude Framework 完整集成版)"
    echo "=============================================================================="
    echo ""
    echo "📋 更新方案: 双框架隔离更新 (Context Engineering + SuperClaude Framework)"
    echo "🏗️ 架构模式: ContextDev 集成层，保持上游项目独立"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "🔧 主要选项:"
    echo "  --help, -h                显示此帮助信息"
    echo "  --dry-run                 仅检查更新，不执行实际更新"
    echo "  --backup-only             仅备份现有配置"
    echo "  --sync-upstream           仅同步上游项目"
    echo "  --update-packages         仅更新 Python 包"
    echo "  --validate                仅验证集成状态"
    echo ""
    echo "🛠️ 维护选项:"
    echo "  --restore-backup          从最新备份恢复配置"
    echo "  --cleanup-backups         清理旧备份文件"
    echo "  --force-update            强制更新（忽略版本检查）"
    echo ""
    echo "📊 此脚本将执行："
    echo "  ✅ 备份现有 ContextDev 集成配置"
    echo "  ✅ 同步 Context Engineering 到最新版本"
    echo "  ✅ 同步 SuperClaude Framework 到最新版本"
    echo "  ✅ 更新 SuperClaude Python 包"
    echo "  ✅ 更新集成配置文件和脚本"
    echo "  ✅ 验证更新结果和集成完整性"
    echo ""
    echo "📖 详细信息: ContextDev/superclaude-integration-plan.md"
    exit 0
fi

# 仅检查模式
if [[ "$1" == "--dry-run" ]]; then
    echo "🔍 检查模式 - 仅检查更新状态，不执行实际更新"
    if [[ -f "$SCRIPTS_DIR/validate-integration.sh" ]]; then
        bash "$SCRIPTS_DIR/validate-integration.sh"
    else
        echo "❌ 验证脚本不存在，请先运行完整安装"
        exit 1
    fi
    exit 0
fi

# 仅备份模式
if [[ "$1" == "--backup-only" ]]; then
    echo "💾 仅备份现有配置..."
    backup_integration_config
    echo "✅ 备份完成: $BACKUP_DIR"
    exit 0
fi

# 仅同步上游项目
if [[ "$1" == "--sync-upstream" ]]; then
    echo "🔄 仅同步上游项目..."
    sync_context_engineering
    sync_superclaude_framework
    echo "✅ 上游项目同步完成"
    exit 0
fi

# 仅更新包
if [[ "$1" == "--update-packages" ]]; then
    echo "📦 仅更新 Python 包..."
    update_superclaude_package
    echo "✅ Python 包更新完成"
    exit 0
fi

# 仅验证
if [[ "$1" == "--validate" ]]; then
    echo "🧪 仅验证集成状态..."
    if [[ -f "$SCRIPTS_DIR/validate-integration.sh" ]]; then
        bash "$SCRIPTS_DIR/validate-integration.sh"
    else
        echo "❌ 验证脚本不存在"
        exit 1
    fi
    exit 0
fi

# 恢复备份
if [[ "$1" == "--restore-backup" ]]; then
    echo "🔄 从最新备份恢复配置..."
    # 查找最新备份
    local latest_backup=$(find "$CONTEXT_DEV_DIR" -maxdepth 1 -name "backup-*" -type d | sort | tail -1)
    if [[ -n "$latest_backup" ]]; then
        BACKUP_DIR="$latest_backup"
        restore_from_backup
        echo "✅ 配置恢复完成"
    else
        echo "❌ 未找到备份文件"
        exit 1
    fi
    exit 0
fi

# 清理备份
if [[ "$1" == "--cleanup-backups" ]]; then
    echo "🧹 清理旧备份文件..."
    cleanup_old_backups
    echo "✅ 备份清理完成"
    exit 0
fi

# ==================== 主程序入口 ====================

# 运行主更新流程 - SuperClaude Framework 完整更新
echo "🎯 启动 JeecgBoot AI 环境 v3.0 更新程序..."
echo "📋 更新方案文档: ContextDev/superclaude-integration-plan.md"
echo ""

main "$@"

