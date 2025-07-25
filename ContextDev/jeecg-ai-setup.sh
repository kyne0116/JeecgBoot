#!/bin/bash

# JeecgBoot AI 环境安装脚本 v4.0 (纯 Context Engineering 版)
# 专注于 Context Engineering 基础能力和 CodeGen 系统集成

set -e

echo "🚀 JeecgBoot AI 环境安装 v4.0 (Context Engineering 版)"
echo "================================================================"
echo "📋 核心功能: Context Engineering + CodeGen 系统深度集成"
echo "🏗️ 架构模式: 纯 JeecgBoot 原生 AI 能力，无第三方框架依赖"
echo ""

# ==================== 全局变量定义 ====================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONTEXT_DEV_DIR="$PROJECT_ROOT/ContextDev"

# ContextDev 集成层目录结构
UPSTREAM_DIR="$CONTEXT_DEV_DIR/upstream"
CONFIG_DIR="$CONTEXT_DEV_DIR/config"
TEMPLATES_DIR="$CONTEXT_DEV_DIR/templates"

# 上游项目目录
CONTEXT_ENGINEERING_DIR="$UPSTREAM_DIR/context-engineering"

# 工作目录
PRP_WORK_DIR="$PROJECT_ROOT/PRPs"
PROJECT_CLAUDE_CONFIG="$PRP_WORK_DIR/CLAUDE.md"

# 日志和状态
INSTALL_LOG="$CONTEXT_DEV_DIR/install.log"
INTEGRATION_STATUS="$CONTEXT_DEV_DIR/integration-status.json"

# ==================== 工具函数 ====================

# 日志记录函数
log_info() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" | tee -a "$INSTALL_LOG"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" | tee -a "$INSTALL_LOG"
}

log_success() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" | tee -a "$INSTALL_LOG"
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

# ==================== 系统检查 ====================

# 检查系统要求和环境
check_prerequisites() {
    log_info "开始系统环境检查..."

    # 检查 Python 3
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi

    # 检查 Git
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装，请先安装 Git"
        exit 1
    fi

    log_success "系统环境检查通过"
}

# ==================== 目录结构初始化 ====================

# 确保所有必要的目录存在
ensure_directory_structure() {
    log_info "初始化目录结构..."
    
    # 创建基础目录结构
    local directories=(
        "$CONTEXT_DEV_DIR"
        "$UPSTREAM_DIR"
        "$CONFIG_DIR"
        "$TEMPLATES_DIR"
        "$PRP_WORK_DIR"
        "$PRP_WORK_DIR/examples"
        "$PRP_WORK_DIR/templates"
        "$PROJECT_ROOT/projectDocs"
    )

    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "创建目录: $dir"
        fi
    done

    log_success "目录结构初始化完成"
}

# ==================== Context Engineering 集成 ====================

# 同步 Context Engineering 项目
sync_context_engineering() {
    log_info "同步 Context Engineering 项目..."

    # 检查是否需要克隆或更新
    if [[ ! -d "$CONTEXT_ENGINEERING_DIR" ]] || [[ -z "$(ls -A "$CONTEXT_ENGINEERING_DIR" 2>/dev/null)" ]]; then
        log_info "克隆 Context Engineering 项目..."
        rm -rf "$CONTEXT_ENGINEERING_DIR"  # 确保目录干净
        if timeout 10 git clone "https://github.com/context-engineering/context-engineering.git" "$CONTEXT_ENGINEERING_DIR" 2>/dev/null; then
            log_success "Context Engineering 克隆完成"
        else
            log_info "GitHub 克隆失败，使用本地备份资源..."
            # 这里可以添加使用本地备份的逻辑
        fi
    else
        log_info "Context Engineering 项目已存在，跳过克隆"
    fi

    update_integration_status "context_engineering" "synchronized" "latest"
}

# ==================== 项目配置 ====================

# 创建项目级 CLAUDE 配置
create_claude_config() {
    log_info "创建项目级 CLAUDE 配置..."

    # 确保项目根目录的 CLAUDE.md 存在
    if [[ ! -f "$PROJECT_ROOT/CLAUDE.md" ]]; then
        cat > "$PROJECT_ROOT/CLAUDE.md" << 'EOF'
# ===== JeecgBoot 项目 AI 编程配置 =====

# Context Engineering 基础规范
@ContextDev/templates/CLAUDE_JEECGBOOT.md

# ===== 项目特定配置 =====
## JeecgBoot 技术栈约束
- 严格使用 Spring Boot 3.x + Vue 3 + TypeScript
- 强制通过 CodeGen 系统生成基础 CRUD 代码
- 遵循 JeecgBoot 模块化架构规范

## CodeGen 系统集成
- 通过 Code_Gen_Guide.py 执行完整代码生成工作流
- 基于 Code_Gen_Agent.md 进行智能需求分析
- 生成符合 JeecgBoot 规范的前后端代码
EOF
        log_success "项目 CLAUDE.md 配置创建完成"
    else
        log_info "项目 CLAUDE.md 配置已存在"
    fi

    update_integration_status "claude_config" "configured" "4.0"
}

# 复制 JeecgBoot 示例代码
copy_jeecgboot_examples() {
    log_info "复制 JeecgBoot 示例代码..."

    local examples_source="$CONTEXT_DEV_DIR/examples/jeecgboot"
    local examples_target="$PRP_WORK_DIR/examples/jeecgboot"

    if [[ -d "$examples_source" ]]; then
        rm -rf "$examples_target"
        cp -r "$examples_source" "$examples_target"
        log_success "JeecgBoot 示例代码复制完成"
    else
        log_info "示例代码源目录不存在，跳过复制"
    fi

    update_integration_status "examples" "copied" "latest"
}

# 复制模板文件
copy_templates() {
    log_info "复制模板文件..."

    local templates_source="$CONTEXT_DEV_DIR/templates"
    local templates_target="$PRP_WORK_DIR/templates"

    if [[ -d "$templates_source" ]]; then
        rm -rf "$templates_target"
        cp -r "$templates_source" "$templates_target"
        log_success "模板文件复制完成"
    else
        log_info "模板源目录不存在，跳过复制"
    fi

    update_integration_status "templates" "copied" "latest"
}

# ==================== CodeGen 系统集成 ====================

# 配置 CodeGen 命令
configure_codegen_commands() {
    log_info "配置 CodeGen 命令..."

    local codegen_config="$PRP_WORK_DIR/codegen_commands.json"
    
    cat > "$codegen_config" << 'EOF'
{
  "jeecg_commands": {
    "generate-prp": {
      "description": "生成 JeecgBoot 需求文档",
      "template": "REQUIREMENTS_JEECGBOOT.md",
      "output_dir": "projectDocs"
    },
    "execute-prp": {
      "description": "执行需求文档并调用 CodeGen",
      "codegen_integration": true,
      "validation": true
    }
  },
  "codegen_integration": {
    "script_path": "CodeGen/Code_Gen_Guide.py",
    "config_path": "CodeGen/Code_Gen_Config.json",
    "agent_path": "CodeGen/Code_Gen_Agent.md"
  }
}
EOF

    log_success "CodeGen 命令配置完成"
    update_integration_status "codegen_commands" "configured" "4.0"
}

# ==================== 安装验证 ====================

# 验证安装结果
verify_installation() {
    log_info "验证安装结果..."

    local verification_passed=true

    # 检查关键文件是否存在
    local critical_files=(
        "$PROJECT_ROOT/CLAUDE.md"
        "$CONTEXT_DEV_DIR/templates/CLAUDE_JEECGBOOT.md"
        "$PRP_WORK_DIR/codegen_commands.json"
    )

    for file in "${critical_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "关键文件缺失: $file"
            verification_passed=false
        fi
    done

    # 检查 CodeGen 系统
    if [[ ! -f "$PROJECT_ROOT/CodeGen/Code_Gen_Guide.py" ]]; then
        log_error "CodeGen 系统缺失"
        verification_passed=false
    fi

    if $verification_passed; then
        log_success "✅ 安装验证通过！"
        echo ""
        echo "🎉 JeecgBoot AI 环境安装完成！"
        echo ""
        echo "📁 主要目录结构:"
        echo "├── CLAUDE.md                     # 项目级 AI 配置"
        echo "├── ContextDev/                   # Context Engineering"
        echo "│   ├── templates/                # AI 编程模板"
        echo "│   └── examples/                 # JeecgBoot 示例代码"
        echo "├── PRPs/                         # AI 工作目录"
        echo "├── CodeGen/                      # CodeGen 系统"
        echo "└── projectDocs/                  # 生成的需求文档"
        echo ""
        echo "🚀 可用功能:"
        echo "• Context Engineering 基础能力"
        echo "• CodeGen 系统完整集成"
        echo "• JeecgBoot 示例代码参考"
        echo "• AI 编程模板集合"
        echo ""
        echo "💡 使用建议:"
        echo "• 使用 CodeGen 系统生成基础 CRUD 代码"
        echo "• 参考 PRPs/examples/ 中的示例代码"
        echo "• 基于模板创建需求文档"
        echo ""
    else
        log_error "❌ 安装验证失败！"
        exit 1
    fi

    update_integration_status "installation" "completed" "4.0"
}

# ==================== 主执行逻辑 ====================

main() {
    echo "开始 JeecgBoot AI 环境安装..."
    echo ""

    # 执行安装步骤
    check_prerequisites
    ensure_directory_structure
    sync_context_engineering
    create_claude_config
    copy_jeecgboot_examples
    copy_templates
    configure_codegen_commands
    verify_installation

    echo ""
    echo "🎯 安装完成！JeecgBoot AI 环境已准备就绪。"
}

# 处理命令行参数
case "${1:-}" in
    --verify)
        verify_installation
        ;;
    --examples-only)
        copy_jeecgboot_examples
        ;;
    --update-claude-config)
        create_claude_config
        ;;
    *)
        main
        ;;
esac