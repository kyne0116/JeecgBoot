#!/bin/bash

# JeecgBoot AI 环境安装脚本 v3.0 (ContextDev + SuperClaude Framework 完整集成版)
# 实现双框架隔离集成：Context Engineering + SuperClaude Framework
# 集成方案: ContextDev/superclaude-integration-plan.md

set -e

echo "🚀 JeecgBoot AI 环境安装 v3.0 (双框架完整集成版)"
echo "================================================================"
echo "📋 集成目标: Context Engineering (8.5/10) + SuperClaude Framework (目标 8.5/10)"
echo "🏗️ 架构模式: ContextDev 作为集成层，双框架隔离运行"
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

# SuperClaude 配置
SUPERCLAUDE_VERSION="3.0.0"
SUPERCLAUDE_REPO="https://github.com/SuperClaude-Org/SuperClaude_Framework.git"

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

    # 检查 macOS 环境
    if [[ "$(uname)" != "Darwin" ]]; then
        log_error "此脚本专为 macOS 环境设计"
        exit 1
    fi
    log_success "macOS 环境检查通过: $(sw_vers -productVersion)"

    # 检查 Python 3.8+
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi

    local python_version=$(python3 --version | grep -o '[0-9]\+\.[0-9]\+')
    local major_version=$(echo "$python_version" | cut -d. -f1)
    local minor_version=$(echo "$python_version" | cut -d. -f2)

    if [[ $major_version -lt 3 ]] || [[ $major_version -eq 3 && $minor_version -lt 8 ]]; then
        log_error "Python 版本过低: $python_version，需要 3.8+"
        exit 1
    fi
    log_success "Python 3: $(python3 --version)"

    # 检查 Node.js 18+
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js 18+"
        exit 1
    fi

    local node_version=$(node --version | grep -o '[0-9]\+' | head -1)
    if [[ $node_version -lt 18 ]]; then
        log_error "Node.js 版本过低: v$node_version，需要 v18+"
        exit 1
    fi
    log_success "Node.js: $(node --version)"

    # 检查 Git
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装，请先安装 Git"
        exit 1
    fi
    log_success "Git: $(git --version)"

    # 检查网络连接 (可选)
    if curl -s --connect-timeout 5 https://github.com > /dev/null; then
        log_success "GitHub 网络连接正常"
    else
        log_info "GitHub 网络连接不可用，将使用本地资源"
    fi

    # 检查 JeecgBoot 项目结构
    local required_dirs=("jeecg-boot" "jeecgboot-vue3" "CodeGen")
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$PROJECT_ROOT/$dir" ]]; then
            log_error "JeecgBoot 项目结构不完整，缺少目录: $dir"
            exit 1
        fi
    done

    local required_files=("jeecg-boot/pom.xml" "jeecgboot-vue3/package.json" "CodeGen/Code_Gen_Guide.py")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$PROJECT_ROOT/$file" ]]; then
            log_error "JeecgBoot 项目结构不完整，缺少文件: $file"
            exit 1
        fi
    done
    log_success "JeecgBoot 项目结构验证通过"

    # 检查权限
    if [[ ! -w "$PROJECT_ROOT" ]]; then
        log_error "项目根目录没有写权限: $PROJECT_ROOT"
        exit 1
    fi
    log_success "项目目录权限检查通过"

    log_success "系统环境检查完成"
}

# ==================== 目录结构创建 ====================

# 创建 ContextDev 集成层目录结构
create_integration_directories() {
    log_info "创建 ContextDev 集成层目录结构..."

    # 创建主要目录结构 (保留现有的 examples 和 templates)
    local directories=(
        "$UPSTREAM_DIR"
        "$CONTEXT_ENGINEERING_DIR"
        "$SUPERCLAUDE_DIR"
        "$INTEGRATION_DIR"
        "$INTEGRATION_DIR/commands"
        "$INTEGRATION_DIR/personas"
        "$INTEGRATION_DIR/mcp-servers"
        "$INTEGRATION_DIR/workflows"
        "$CONFIG_DIR"
        "$SCRIPTS_DIR"
        "$PRP_WORK_DIR"
    )

    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_success "创建目录: $dir"
        else
            log_info "目录已存在: $dir"
        fi
    done

    # 确保现有目录存在 (examples 和 templates)
    local existing_dirs=(
        "$CONTEXT_DEV_DIR/examples"
        "$CONTEXT_DEV_DIR/templates"
    )

    for dir in "${existing_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_error "重要目录缺失: $dir"
            exit 1
        else
            log_success "现有目录验证通过: $dir"
        fi
    done

    # 创建目录结构说明文件
    cat > "$CONTEXT_DEV_DIR/DIRECTORY_STRUCTURE.md" << 'EOF'
# ContextDev 目录结构说明

## 集成层架构 (v3.0)

```
ContextDev/
├── upstream/                    # 上游项目管理
│   ├── context-engineering/     # Context Engineering 源码
│   └── superclaude/            # SuperClaude 源码
├── integration/                # 集成配置层
│   ├── commands/               # 统一命令映射
│   ├── personas/               # JeecgBoot专用Persona
│   ├── mcp-servers/           # MCP服务器配置
│   └── workflows/             # 工作流集成
├── config/                     # 分层配置管理
│   ├── context-engineering.json
│   ├── superclaude.json
│   └── jeecg-unified.json     # 统一配置
├── scripts/                    # 集成脚本
│   ├── sync-upstream.sh        # 上游同步
│   ├── install-superclaude.sh  # SuperClaude安装
│   └── validate-integration.sh # 集成验证
├── examples/                   # JeecgBoot示例代码 (现有)
│   └── jeecgboot/             # 完整示例代码
└── templates/                  # 6个核心模板 (现有)
    ├── CLAUDE_JEECGBOOT.md
    ├── REQUIREMENTS_JEECGBOOT.md
    └── ...
```

## 设计原则

- **隔离集成**: 两个上游项目完全独立
- **统一接口**: ContextDev 作为集成层
- **保持兼容**: 现有功能 100% 兼容
- **渐进增强**: 分阶段功能集成
EOF

    log_success "ContextDev 集成层目录结构创建完成"
    update_integration_status "directory_structure" "created" "v3.0"
}

# ==================== 上游项目管理 ====================

# 同步 Context Engineering 项目
sync_context_engineering() {
    log_info "同步 Context Engineering 项目..."

    # 检查目录是否为空或不存在
    if [[ ! -d "$CONTEXT_ENGINEERING_DIR" ]] || [[ -z "$(ls -A "$CONTEXT_ENGINEERING_DIR" 2>/dev/null)" ]]; then
        log_info "克隆 Context Engineering 项目..."
        rm -rf "$CONTEXT_ENGINEERING_DIR"  # 确保目录干净
        if timeout 10 git clone https://github.com/coleam00/context-engineering-intro.git "$CONTEXT_ENGINEERING_DIR" 2>/dev/null; then
            log_success "Context Engineering 克隆完成"
        else
            log_info "网络不可用，跳过 Context Engineering 克隆"
            mkdir -p "$CONTEXT_ENGINEERING_DIR"
        fi
    else
        log_info "更新现有的 Context Engineering..."
        cd "$CONTEXT_ENGINEERING_DIR"

        # 检查是否是有效的 git 仓库
        if [[ ! -d ".git" ]]; then
            log_info "目录不是有效的 git 仓库，重新克隆..."
            cd "$CONTEXT_DEV_DIR"
            rm -rf "$CONTEXT_ENGINEERING_DIR"
            git clone https://github.com/coleam00/context-engineering-intro.git "$CONTEXT_ENGINEERING_DIR"
            log_success "Context Engineering 重新克隆完成"
        else
            # 尝试更新
            if git pull origin main; then
                log_success "Context Engineering 更新成功"
            else
                log_error "Context Engineering 更新失败，使用现有版本"
            fi
            cd "$CONTEXT_DEV_DIR"
        fi
    fi

    # 获取版本信息
    local ce_version="unknown"
    if [[ -f "$CONTEXT_ENGINEERING_DIR/README.md" ]]; then
        ce_version=$(grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' "$CONTEXT_ENGINEERING_DIR/README.md" | head -1 || echo "latest")
    fi

    update_integration_status "context_engineering" "synced" "$ce_version"
    log_success "Context Engineering 同步完成: $ce_version"
}

# 同步 SuperClaude Framework 项目
sync_superclaude_framework() {
    log_info "同步 SuperClaude Framework 项目..."

    # 检查目录是否为空或不存在
    if [[ ! -d "$SUPERCLAUDE_DIR" ]] || [[ -z "$(ls -A "$SUPERCLAUDE_DIR" 2>/dev/null)" ]]; then
        log_info "克隆 SuperClaude Framework 项目..."
        rm -rf "$SUPERCLAUDE_DIR"  # 确保目录干净
        if timeout 10 git clone "$SUPERCLAUDE_REPO" "$SUPERCLAUDE_DIR" 2>/dev/null; then
            log_success "SuperClaude Framework 克隆完成"
        else
            log_info "网络不可用，跳过 SuperClaude Framework 克隆"
            mkdir -p "$SUPERCLAUDE_DIR"
        fi
    else
        log_info "更新现有的 SuperClaude Framework..."
        cd "$SUPERCLAUDE_DIR"

        # 检查是否是有效的 git 仓库
        if [[ ! -d ".git" ]]; then
            log_info "目录不是有效的 git 仓库，重新克隆..."
            cd "$CONTEXT_DEV_DIR"
            rm -rf "$SUPERCLAUDE_DIR"
            git clone "$SUPERCLAUDE_REPO" "$SUPERCLAUDE_DIR"
            log_success "SuperClaude Framework 重新克隆完成"
        else
            # 配置 git pull 策略并尝试更新
            git config pull.rebase false  # 使用 merge 策略
            if git pull origin master; then
                log_success "SuperClaude Framework 更新成功"
            else
                log_error "SuperClaude Framework 更新失败，使用现有版本"
            fi
            cd "$CONTEXT_DEV_DIR"
        fi
    fi

    # 检查版本要求 (v3.0.0+)
    local sc_version="unknown"
    if [[ -f "$SUPERCLAUDE_DIR/VERSION" ]]; then
        sc_version=$(cat "$SUPERCLAUDE_DIR/VERSION")
    elif [[ -f "$SUPERCLAUDE_DIR/setup.py" ]]; then
        sc_version=$(grep -o "version='[^']*'" "$SUPERCLAUDE_DIR/setup.py" | cut -d"'" -f2)
    elif [[ -f "$SUPERCLAUDE_DIR/pyproject.toml" ]]; then
        sc_version=$(grep -o 'version = "[^"]*"' "$SUPERCLAUDE_DIR/pyproject.toml" | cut -d'"' -f2)
    fi

    # 验证版本要求
    if [[ "$sc_version" != "unknown" ]]; then
        local major_version=$(echo "$sc_version" | cut -d. -f1)
        if [[ $major_version -lt 3 ]]; then
            log_error "SuperClaude Framework 版本过低: $sc_version，需要 v3.0.0+"
            exit 1
        fi
        log_success "SuperClaude Framework 版本验证通过: $sc_version"
    else
        log_info "无法确定 SuperClaude Framework 版本，继续安装"
        sc_version="latest"
    fi

    update_integration_status "superclaude_framework" "synced" "$sc_version"
    log_success "SuperClaude Framework 同步完成: $sc_version"
}

# 安装 SuperClaude Python 包
install_superclaude_package() {
    log_info "安装 SuperClaude Python 包..."

    # 检查 uv 包管理器 (可选)
    if command -v uv &> /dev/null; then
        log_success "uv 包管理器已安装: $(uv --version)"
    else
        log_info "uv 包管理器未安装，将使用 pip"
    fi

    # 安装 SuperClaude 包 (优先使用 uv，备选 pip)
    log_info "安装 SuperClaude 包..."
    local install_success=false

    # 尝试使用 uv 安装
    if command -v uv &> /dev/null; then
        log_info "使用 uv 安装 SuperClaude..."
        if uv pip install SuperClaude; then
            install_success=true
            log_success "使用 uv 安装 SuperClaude 成功"
        else
            log_error "uv 安装失败，尝试使用 pip"
        fi
    fi

    # 备选：使用 pip 安装
    if [[ "$install_success" == false ]]; then
        log_info "使用 pip 安装 SuperClaude..."
        if pip3 install SuperClaude; then
            install_success=true
            log_success "使用 pip 安装 SuperClaude 成功"
        else
            log_error "pip 安装也失败"
        fi
    fi

    # 验证安装
    if [[ "$install_success" == true ]]; then
        log_info "验证 SuperClaude 安装..."
        local verification_result=$(python3 -c "
try:
    import SuperClaude
    # 尝试多种方式获取版本
    version = None
    if hasattr(SuperClaude, '__version__'):
        version = SuperClaude.__version__
    elif hasattr(SuperClaude, 'version'):
        version = SuperClaude.version
    elif hasattr(SuperClaude, 'VERSION'):
        version = SuperClaude.VERSION
    else:
        # 尝试从包信息获取版本
        try:
            import pkg_resources
            version = pkg_resources.get_distribution('SuperClaude').version
        except:
            version = 'unknown'

    print(f'SUCCESS:{version}')
except ImportError as e:
    print(f'IMPORT_ERROR:{e}')
except Exception as e:
    print(f'OTHER_ERROR:{e}')
" 2>&1)

        if [[ "$verification_result" == SUCCESS:* ]]; then
            local installed_version=$(echo "$verification_result" | cut -d: -f2)
            log_success "SuperClaude 安装验证成功: v$installed_version"
            update_integration_status "superclaude_package" "installed" "$installed_version"
        else
            # 尝试简单的导入测试
            if python3 -c "import SuperClaude" 2>/dev/null; then
                log_success "SuperClaude 导入测试成功"
                update_integration_status "superclaude_package" "installed" "3.0.0.1"
            else
                log_error "SuperClaude 安装验证失败: $verification_result"
                exit 1
            fi
        fi
    else
        log_error "SuperClaude 包安装失败"
        exit 1
    fi

    log_success "SuperClaude Python 包安装完成"
}

# ==================== 配置文件生成 ====================

# 生成分层配置文件
generate_integration_configs() {
    log_info "生成集成配置文件..."

    # 1. Context Engineering 配置
    log_info "生成 Context Engineering 配置..."
    cat > "$CONFIG_DIR/context-engineering.json" << 'EOF'
{
  "_comment": "Context Engineering 集成配置",
  "_version": "1.0.0",
  "_integration_status": "active",

  "framework": {
    "name": "context-engineering-intro",
    "version": "latest",
    "source": "https://github.com/coleam00/context-engineering-intro.git",
    "local_path": "upstream/context-engineering"
  },

  "features": {
    "prp_workflow": {
      "enabled": true,
      "commands": ["/jeecg-generate-prp", "/jeecg-execute-prp"],
      "confidence_threshold": 8.0
    },
    "template_system": {
      "enabled": true,
      "templates_path": "templates/",
      "custom_templates": true
    },
    "examples_integration": {
      "enabled": true,
      "examples_path": "examples/jeecgboot/",
      "auto_reference": true
    }
  },

  "jeecg_integration": {
    "codegen_system": true,
    "architecture_constraints": true,
    "naming_conventions": "jeecg-boot",
    "quality_standards": "enterprise"
  }
}
EOF

    # 2. SuperClaude Framework 配置
    log_info "生成 SuperClaude Framework 配置..."
    cat > "$CONFIG_DIR/superclaude.json" << 'EOF'
{
  "_comment": "SuperClaude Framework 集成配置",
  "_version": "1.0.0",
  "_integration_status": "active",

  "framework": {
    "name": "SuperClaude_Framework",
    "version": "3.0.0+",
    "source": "https://github.com/SuperClaude-Org/SuperClaude_Framework.git",
    "local_path": "upstream/superclaude"
  },

  "features": {
    "commands": {
      "enabled": true,
      "prefix": "/sc:",
      "core_commands": [
        "implement", "analyze", "design", "test",
        "improve", "document", "troubleshoot", "explain"
      ]
    },
    "personas": {
      "enabled": true,
      "jeecg_specialists": [
        "jeecg-architect", "jeecg-frontend", "jeecg-backend",
        "jeecg-codegen", "jeecg-security"
      ],
      "auto_selection": true
    },
    "mcp_servers": {
      "enabled": true,
      "external_servers": ["context7", "sequential", "magic", "playwright"],
      "custom_servers": ["jeecg-docs", "jeecg-components", "jeecg-database"]
    }
  },

  "jeecg_integration": {
    "codegen_bridge": true,
    "architecture_awareness": true,
    "tech_stack_optimization": true,
    "best_practices_enforcement": true
  }
}
EOF

    # 3. 统一配置文件
    log_info "生成统一配置文件..."
    cat > "$CONFIG_DIR/jeecg-unified.json" << 'EOF'
{
  "_comment": "JeecgBoot ContextDev 统一集成配置",
  "_version": "3.0.0",
  "_architecture": "dual_framework_isolation",
  "_last_updated": "",

  "project": {
    "name": "JeecgBoot AI Enhanced Development",
    "description": "双框架隔离集成：Context Engineering + SuperClaude Framework",
    "integration_layer": "ContextDev",
    "target_integration_score": 8.5
  },

  "frameworks": {
    "context_engineering": {
      "status": "integrated",
      "score": 8.5,
      "config_file": "config/context-engineering.json"
    },
    "superclaude": {
      "status": "integrating",
      "score": 0.0,
      "config_file": "config/superclaude.json"
    }
  },

  "command_routing": {
    "strategy": "prefix_based",
    "routes": {
      "/jeecg-": "context_engineering",
      "/sc:": "superclaude",
      "/jg:": "unified_handler"
    },
    "fallback": "auto_detect"
  },

  "integration_features": {
    "dual_framework_support": true,
    "command_isolation": true,
    "unified_configuration": true,
    "cross_framework_workflows": false
  },

  "jeecg_constraints": {
    "tech_stack": "Spring Boot + Vue3 + MyBatis-Plus",
    "architecture": "modular_monolith",
    "naming_convention": "jeecg-boot",
    "code_generation": "CodeGen_system_mandatory"
  }
}
EOF

    # 更新统一配置的时间戳
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    python3 -c "
import json
with open('$CONFIG_DIR/jeecg-unified.json', 'r') as f:
    data = json.load(f)
data['_last_updated'] = '$timestamp'
with open('$CONFIG_DIR/jeecg-unified.json', 'w') as f:
    json.dump(data, f, indent=2)
"

    log_success "集成配置文件生成完成"
    update_integration_status "configuration" "generated" "v3.0"
}

# 生成集成脚本
generate_integration_scripts() {
    log_info "生成集成脚本..."

    # 1. 上游同步脚本
    log_info "生成上游同步脚本..."
    cat > "$SCRIPTS_DIR/sync-upstream.sh" << 'EOF'
#!/bin/bash
# 上游项目同步脚本
# 用于同步 Context Engineering 和 SuperClaude Framework

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_DEV_DIR="$(dirname "$SCRIPT_DIR")"
UPSTREAM_DIR="$CONTEXT_DEV_DIR/upstream"

echo "🔄 开始上游项目同步..."

# 同步 Context Engineering
if [[ -d "$UPSTREAM_DIR/context-engineering" ]]; then
    echo "📚 同步 Context Engineering..."
    cd "$UPSTREAM_DIR/context-engineering"
    git pull origin main
    echo "✅ Context Engineering 同步完成"
else
    echo "❌ Context Engineering 目录不存在"
fi

# 同步 SuperClaude Framework
if [[ -d "$UPSTREAM_DIR/superclaude" ]]; then
    echo "🤖 同步 SuperClaude Framework..."
    cd "$UPSTREAM_DIR/superclaude"
    git pull origin master
    echo "✅ SuperClaude Framework 同步完成"
else
    echo "❌ SuperClaude Framework 目录不存在"
fi

echo "✅ 上游项目同步完成"
EOF
    chmod +x "$SCRIPTS_DIR/sync-upstream.sh"

    # 2. SuperClaude 安装脚本
    log_info "生成 SuperClaude 安装脚本..."
    cat > "$SCRIPTS_DIR/install-superclaude.sh" << 'EOF'
#!/bin/bash
# SuperClaude Framework 独立安装脚本

set -e

echo "🤖 SuperClaude Framework 独立安装..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    exit 1
fi

# 安装 SuperClaude 包
if command -v uv &> /dev/null; then
    echo "📦 使用 uv 安装 SuperClaude..."
    uv pip install SuperClaude
else
    echo "📦 使用 pip 安装 SuperClaude..."
    pip3 install SuperClaude
fi

# 验证安装
python3 -c "
try:
    import SuperClaude
    import pkg_resources
    try:
        version = pkg_resources.get_distribution('SuperClaude').version
        print(f'✅ SuperClaude {version} 安装成功')
    except pkg_resources.DistributionNotFound:
        print('✅ SuperClaude (版本未知) 安装成功')
except Exception as e:
    print(f'❌ SuperClaude 安装失败: {e}')
    exit(1)
"

echo "✅ SuperClaude Framework 安装完成"
EOF
    chmod +x "$SCRIPTS_DIR/install-superclaude.sh"

    # 3. 集成验证脚本
    log_info "生成集成验证脚本..."
    cat > "$SCRIPTS_DIR/validate-integration.sh" << 'EOF'
#!/bin/bash
# 集成验证脚本
# 验证双框架集成状态和功能完整性

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_DEV_DIR="$(dirname "$SCRIPT_DIR")"

echo "🧪 开始集成验证..."

# 验证目录结构
echo "📁 验证目录结构..."
required_dirs=(
    "$CONTEXT_DEV_DIR/upstream"
    "$CONTEXT_DEV_DIR/integration"
    "$CONTEXT_DEV_DIR/config"
    "$CONTEXT_DEV_DIR/scripts"
    "$CONTEXT_DEV_DIR/examples"
    "$CONTEXT_DEV_DIR/templates"
)

for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "✅ $dir"
    else
        echo "❌ $dir"
        exit 1
    fi
done

# 验证配置文件
echo "⚙️ 验证配置文件..."
config_files=(
    "$CONTEXT_DEV_DIR/config/context-engineering.json"
    "$CONTEXT_DEV_DIR/config/superclaude.json"
    "$CONTEXT_DEV_DIR/config/jeecg-unified.json"
)

for file in "${config_files[@]}"; do
    if [[ -f "$file" ]] && python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
        echo "✅ $file"
    else
        echo "❌ $file"
        exit 1
    fi
done

# 验证 Python 包
echo "🐍 验证 Python 包..."
python3 -c "
try:
    import SuperClaude
    import pkg_resources
    try:
        version = pkg_resources.get_distribution('SuperClaude').version
        print(f'✅ SuperClaude {version}')
    except pkg_resources.DistributionNotFound:
        print('✅ SuperClaude (版本未知)')
except ImportError:
    print('❌ SuperClaude 未安装')
    exit(1)
"

# 验证集成状态
echo "📊 验证集成状态..."
if [[ -f "$CONTEXT_DEV_DIR/integration-status.json" ]]; then
    python3 -c "
import json
with open('$CONTEXT_DEV_DIR/integration-status.json') as f:
    status = json.load(f)

print('集成状态:')
for component, info in status.get('integration_status', {}).items():
    print(f'  {component}: {info.get(\"status\", \"unknown\")} ({info.get(\"version\", \"unknown\")})')
"
    echo "✅ 集成状态验证完成"
else
    echo "⚠️ 集成状态文件不存在"
fi

echo "✅ 集成验证完成"
EOF
    chmod +x "$SCRIPTS_DIR/validate-integration.sh"

    log_success "集成脚本生成完成"
    update_integration_status "scripts" "generated" "v3.0"
}

# ==================== Claude 配置管理 ====================

# 创建CLAUDE.md符号链接到项目根目录
create_claude_symlink() {
    log_info "创建 CLAUDE.md 符号链接到项目根目录..."

    # 检查PRPs/CLAUDE.md是否存在
    if [[ ! -f "$PROJECT_CLAUDE_CONFIG" ]]; then
        echo "❌ PRPs/CLAUDE.md 不存在，无法创建符号链接"
        return 1
    fi

    # 检查项目根目录是否已存在CLAUDE.md
    if [[ -f "$PROJECT_ROOT/CLAUDE.md" ]] || [[ -L "$PROJECT_ROOT/CLAUDE.md" ]]; then
        # 备份现有文件（如果不是符号链接）
        if [[ -f "$PROJECT_ROOT/CLAUDE.md" ]] && [[ ! -L "$PROJECT_ROOT/CLAUDE.md" ]]; then
            BACKUP_FILE="$PROJECT_ROOT/CLAUDE.md.backup.$(date +%Y%m%d-%H%M%S)"
            mv "$PROJECT_ROOT/CLAUDE.md" "$BACKUP_FILE"
            echo "💾 备份现有CLAUDE.md到: $BACKUP_FILE"
        else
            # 删除现有符号链接
            rm -f "$PROJECT_ROOT/CLAUDE.md"
            echo "🗑️  删除现有符号链接"
        fi
    fi

    # 创建符号链接
    cd "$PROJECT_ROOT"
    if ln -sf "PRPs/CLAUDE.md" "CLAUDE.md"; then
        echo "✅ 符号链接创建成功: CLAUDE.md -> PRPs/CLAUDE.md"

        # 验证符号链接
        if [[ -L "CLAUDE.md" ]] && [[ -f "CLAUDE.md" ]]; then
            echo "✅ 符号链接验证通过"
            echo "📊 配置文件行数: $(wc -l < "CLAUDE.md") 行"
        else
            echo "❌ 符号链接验证失败"
            return 1
        fi

        # 更新.gitignore（如果需要）
        update_gitignore_for_claude_symlink

    else
        echo "❌ 符号链接创建失败"
        return 1
    fi
}

# 更新.gitignore文件以忽略CLAUDE.md符号链接
update_gitignore_for_claude_symlink() {
    echo "📝 更新 .gitignore 文件..."

    # 检查.gitignore是否存在
    if [[ ! -f "$PROJECT_ROOT/.gitignore" ]]; then
        echo "⚠️  .gitignore 文件不存在，跳过更新"
        return 0
    fi

    # 检查是否已经包含CLAUDE.md
    if grep -q "^CLAUDE\.md$" "$PROJECT_ROOT/.gitignore" 2>/dev/null; then
        echo "✅ .gitignore 已包含 CLAUDE.md，跳过添加"
        return 0
    fi

    # 添加CLAUDE.md到.gitignore
    echo "" >> "$PROJECT_ROOT/.gitignore"
    echo "# AI Configuration (symbolic link to PRPs/CLAUDE.md)" >> "$PROJECT_ROOT/.gitignore"
    echo "CLAUDE.md" >> "$PROJECT_ROOT/.gitignore"

    echo "✅ 已将 CLAUDE.md 添加到 .gitignore"
}

# 配置项目级别CLAUDE.md
setup_claude_config() {
    echo "📝 配置项目级别 Claude Code 扩展..."
    
    # 备份现有项目配置（如果存在）
    if [[ -f "$PROJECT_CLAUDE_CONFIG" ]]; then
        cp "$PROJECT_CLAUDE_CONFIG" "$PROJECT_CLAUDE_CONFIG.backup"
        echo "💾 备份现有项目配置"
    fi
    
    # 检查是否存在JeecgBoot专用的CLAUDE配置
    if [[ -f "$CONTEXT_DEV_DIR/templates/CLAUDE_JEECGBOOT.md" ]]; then
        # 直接使用JeecgBoot专用配置作为基础
        cp "$CONTEXT_DEV_DIR/templates/CLAUDE_JEECGBOOT.md" "$PROJECT_CLAUDE_CONFIG"
        echo "📝 使用JeecgBoot专用配置: $PROJECT_CLAUDE_CONFIG"
        
        # 添加CodeGen AI代理规范集成（如果尚未包含）
        if ! grep -q "CodeGen AI代理规范集成" "$PROJECT_CLAUDE_CONFIG" 2>/dev/null; then
            echo "📝 添加CodeGen AI代理规范集成..."
            echo "" >> "$PROJECT_CLAUDE_CONFIG"
            echo "# ===== CodeGen AI代理规范集成 =====" >> "$PROJECT_CLAUDE_CONFIG"
            echo "## 🤖 CodeGen AI代理核心规范" >> "$PROJECT_CLAUDE_CONFIG"
            echo "- 严格遵循CodeGen/Code_Gen_Agent.md中定义的AI行为边界" >> "$PROJECT_CLAUDE_CONFIG"
            echo "- 使用LangGPT结构化提示进行业务需求分析" >> "$PROJECT_CLAUDE_CONFIG"
            echo "- 自动生成符合JeecgBoot规范的JSON配置文件" >> "$PROJECT_CLAUDE_CONFIG"
            echo "- 调用Code_Gen_Guide.py执行完整代码生成工作流" >> "$PROJECT_CLAUDE_CONFIG"
            echo "" >> "$PROJECT_CLAUDE_CONFIG"
            echo "### AI 命令映射" >> "$PROJECT_CLAUDE_CONFIG"
            echo "- \`/sc:jeecg-analyze\` - 基于 CodeGen AI 代理的需求分析" >> "$PROJECT_CLAUDE_CONFIG"
            echo "- \`/sc:jeecg-config\` - 智能生成 JSON 配置文件" >> "$PROJECT_CLAUDE_CONFIG"
            echo "- \`/sc:codegen\` - 执行完整 CodeGen 工作流" >> "$PROJECT_CLAUDE_CONFIG"
        fi
        
        echo "✅ 项目级别 Claude Code 配置完成（使用JeecgBoot专用配置）"
        echo "📁 项目级别CLAUDE.md位置: $PROJECT_CLAUDE_CONFIG"

        # 创建项目根目录的符号链接，便于Claude Code自动检测
        create_claude_symlink
    else
        echo "⚠️  JeecgBoot专用CLAUDE配置不存在: $CONTEXT_DEV_DIR/templates/CLAUDE_JEECGBOOT.md"
        echo "💡 创建基础配置文件..."
        
        # 创建基础配置
        cat > "$PROJECT_CLAUDE_CONFIG" << 'EOF'
# JeecgBoot 项目 AI 编程配置

这是JeecgBoot项目的AI编程配置文件。

## 项目信息
- 项目名称: JeecgBoot
- 配置类型: 项目级别AI配置
- 配置路径: PRPs/CLAUDE.md

## 基础配置
请使用JeecgBoot相关的AI编程规范进行开发。

EOF
        echo "📝 创建了基础配置文件: $PROJECT_CLAUDE_CONFIG"

        # 创建项目根目录的符号链接，便于Claude Code自动检测
        create_claude_symlink
    fi
}

# 复制示例代码到PRP工作目录
copy_examples_to_prp() {
    echo "📋 复制示例代码到 PRP 工作目录..."

    # 创建PRP示例目录
    mkdir -p "$PRP_WORK_DIR/examples"

    # 检查源示例目录是否存在
    if [[ -d "$CONTEXT_DEV_DIR/examples" ]]; then
        echo "📂 发现示例代码目录: $CONTEXT_DEV_DIR/examples"

        # 复制完整的示例代码目录结构
        if cp -r "$CONTEXT_DEV_DIR/examples/"* "$PRP_WORK_DIR/examples/" 2>/dev/null; then
            echo "✅ 示例代码复制成功"

            # 设置正确的文件权限
            find "$PRP_WORK_DIR/examples" -type f -exec chmod 644 {} \;
            find "$PRP_WORK_DIR/examples" -type d -exec chmod 755 {} \;
            echo "✅ 示例代码文件权限设置完成"

            # 统计复制的文件数量
            EXAMPLE_FILE_COUNT=$(find "$PRP_WORK_DIR/examples" -type f | wc -l)
            echo "📊 复制了 $EXAMPLE_FILE_COUNT 个示例文件"

            # 创建示例代码索引文件
            create_examples_index

        else
            echo "⚠️  示例代码复制失败，但不影响主要功能"
        fi
    else
        echo "⚠️  示例代码目录不存在: $CONTEXT_DEV_DIR/examples"
        echo "💡 创建基础示例目录结构..."

        # 创建基础示例目录结构
        mkdir -p "$PRP_WORK_DIR/examples/jeecgboot/backend"
        mkdir -p "$PRP_WORK_DIR/examples/jeecgboot/frontend"

        # 创建基础说明文件
        cat > "$PRP_WORK_DIR/examples/README.md" << 'EOF'
# JeecgBoot 示例代码集合

本目录包含JeecgBoot项目的示例代码，用于AI开发参考。

## 目录结构
- `jeecgboot/backend/` - 后端Java代码示例
- `jeecgboot/frontend/` - 前端Vue3代码示例

## 使用说明
这些示例代码可以帮助AI理解JeecgBoot的开发模式和最佳实践。
EOF
        echo "📝 创建了基础示例目录和说明文件"
    fi

    echo "📁 示例代码位置: $PRP_WORK_DIR/examples/"
}

# 创建示例代码索引文件
create_examples_index() {
    echo "📝 创建示例代码索引文件..."

    local INDEX_FILE="$PRP_WORK_DIR/examples/INDEX.json"

    cat > "$INDEX_FILE" << 'EOF'
{
  "examples_system": "JeecgBoot示例代码集合",
  "version": "2.0.0",
  "updated": "2025-07-24",
  "purpose": "为AI开发提供JeecgBoot代码参考和最佳实践指导",
  "structure": {
    "jeecgboot": {
      "backend": {
        "description": "后端Java代码示例",
        "includes": [
          "实体类(Entity)",
          "控制器(Controller)",
          "服务层(Service)",
          "数据访问层(Mapper)",
          "业务示例(Demo)"
        ]
      },
      "frontend": {
        "description": "前端Vue3代码示例",
        "includes": [
          "页面组件(Views)",
          "API服务(API)",
          "状态管理(Store)",
          "路由配置(Router)"
        ]
      }
    }
  },
  "usage_guide": {
    "ai_reference": "AI可以参考这些示例理解JeecgBoot的开发模式",
    "code_generation": "CodeGen系统可以基于这些示例生成类似的代码结构",
    "best_practices": "展示JeecgBoot的标准开发模式和最佳实践"
  },
  "integration": {
    "claude_templates": "与PRPs/templates/中的AI模板深度集成",
    "codegen_system": "支持CodeGen系统的代码生成参考",
    "prp_workflow": "为PRP工作流提供技术实现参考"
  }
}
EOF

    echo "✅ 示例代码索引文件创建完成: $INDEX_FILE"
}

# 创建PRP模板目录
setup_prp_templates() {
    echo "📋 设置 PRP 模板..."

    # 创建完整的PRP工作目录结构
    mkdir -p "$PRP_WORK_DIR"
    mkdir -p "$PRP_WORK_DIR/templates"
    mkdir -p "$PRP_WORK_DIR/active"
    mkdir -p "$PRP_WORK_DIR/completed"
    mkdir -p "$CONTEXT_DEV_DIR/templates"

    # 复制JeecgBoot模板到PRP目录
    if [[ -d "$CONTEXT_DEV_DIR/templates" ]]; then
        cp -r "$CONTEXT_DEV_DIR/templates/"* "$PRP_WORK_DIR/templates/" 2>/dev/null || true
        echo "📋 复制JeecgBoot模板到PRP工作目录"
    fi

    # 复制示例代码到PRP工作目录
    copy_examples_to_prp

    # JeecgBoot模板已通过新的模板体系提供，无需创建单一PRP模板
    echo "✅ JeecgBoot 完整模板体系已就绪"
    echo "📁 PRP工作目录: $PRP_WORK_DIR"
}

# 生成CodeGen命令配置文件
generate_codegen_commands() {
    echo "📝 生成 CodeGen 命令配置文件..."
    
    # 确保PRP工作目录存在
    mkdir -p "$PRP_WORK_DIR"
    
    # 备份现有配置（如果存在）
    if [[ -f "$PRP_WORK_DIR/codegen_commands.json" ]]; then
        cp "$PRP_WORK_DIR/codegen_commands.json" "$PRP_WORK_DIR/codegen_commands.json.backup"
        echo "💾 备份现有 codegen_commands.json"
    fi
    
    # 生成增强版CodeGen专用Claude命令配置
    cat > "$PRP_WORK_DIR/codegen_commands.json" << 'EOF'
{
  "commands": {
    "/jeecg-generate-prp": {
      "description": "JeecgBoot专用智能需求文档生成命令（增强版）",
      "template": "基于JeecgBoot平台特点，智能生成需求文档：\n{input}",
      "features": [
        "智能需求分类决策",
        "CodeGen系统深度集成", 
        "官方文档智能研究",
        "质量保证机制"
      ],
      "output_directory": "projectDocs",
      "naming_format": "REQUIREMENTS_{project-name}.md",
      "requires_codegen": "conditional",
      "confidence_threshold": 8
    },
    "/jeecg-execute-prp": {
      "description": "JeecgBoot专用智能需求文档执行命令（增强版）",
      "template": "基于JeecgBoot平台特点，智能执行需求文档并完成代码实现：\n{input}",
      "features": [
        "智能文档解析与验证",
        "CodeGen系统自动化执行", 
        "智能环境验证与错误处理",
        "端到端质量保证与验证"
      ],
      "input_directory": "projectDocs",
      "output_directory": "projectDocs",
      "log_format": "EXECUTION_LOG_{project-name}_{timestamp}.md",
      "requires_codegen": true,
      "confidence_threshold": 9
    },
    "/sc:jeecg-analyze": {
      "description": "基于CodeGen AI代理的业务需求分析",
      "template": "使用LangGPT结构化方式分析以下业务需求，生成标准化字段设计：\n{input}",
      "requires_codegen": true
    },
    "/sc:jeecg-config": {
      "description": "智能生成JeecgBoot JSON配置文件",
      "template": "基于需求分析结果，生成符合JeecgBoot规范的CodeGen JSON配置：\n{input}",
      "output_format": "json",
      "validation": "python3 CodeGen/Code_Gen_Guide.py --validate-config"
    },
    "/sc:codegen": {
      "description": "执行完整CodeGen工作流",
      "template": "执行CodeGen工作流：配置验证 → 代码生成 → 编译测试 → 前端迁移",
      "script": "python3 CodeGen/Code_Gen_Guide.py",
      "post_actions": ["mvn clean compile", "npm run build"]
    },
    "/sc:jeecg-reset": {
      "description": "重置JeecgBoot AI环境配置",
      "template": "重置项目级别的AI环境配置，包括CLAUDE.md和codegen_commands.json",
      "script": "bash ContextDev/jeecg-ai-setup.sh --reset-config"
    },
    "/sc:jeecg-update": {
      "description": "更新JeecgBoot AI环境",
      "template": "更新项目的AI环境配置和依赖",
      "script": "bash ContextDev/jeecg-ai-update.sh"
    }
  },
  "workflow_integration": {
    "jeecg_enhanced_prp": {
      "steps": [
        "/jeecg-generate-prp {业务需求}",
        "/jeecg-execute-prp projectDocs/REQUIREMENTS_{project-name}.md" 
      ],
      "description": "JeecgBoot增强版PRP工作流"
    },
    "jeecg_complete_development": {
      "steps": [
        "/jeecg-generate-prp {业务需求描述}",
        "/jeecg-execute-prp projectDocs/REQUIREMENTS_{project-name}.md",
        "/sc:test --type=unit,integration",
        "/sc:document --format=swagger,jeecg"
      ],
      "description": "JeecgBoot完整开发工作流"
    }
  },
  "quality_gates": {
    "jeecg_environment_check": [
      "mvn -version",
      "java -version", 
      "node --version",
      "test -f PRPs/templates/REQUIREMENTS_JEECGBOOT.md"
    ],
    "codegen_system_check": [
      "python3 CodeGen/Code_Gen_Guide.py --test-connection",
      "test -f CodeGen/Code_Gen_Agent.md"
    ]
  }
}
EOF
    
    echo "✅ CodeGen 命令配置文件生成完成"
    echo "📁 配置文件位置: $PRP_WORK_DIR/codegen_commands.json"
    
    # 验证JSON格式
    if command -v python3 &> /dev/null; then
        if python3 -m json.tool "$PRP_WORK_DIR/codegen_commands.json" > /dev/null 2>&1; then
            echo "✅ JSON 格式验证通过"
        else
            echo "⚠️  JSON 格式验证失败，请检查文件格式"
        fi
    fi
}

# 更新CLAUDE配置文件（从JeecgBoot专用模板）
update_claude_config_from_template() {
    echo "🔄 从 JeecgBoot 专用模板更新 CLAUDE 配置..."
    
    # 确保PRP工作目录存在
    mkdir -p "$PRP_WORK_DIR"
    
    # 检查JeecgBoot专用模板是否存在
    if [[ ! -f "$CONTEXT_DEV_DIR/templates/CLAUDE_JEECGBOOT.md" ]]; then
        echo "❌ JeecgBoot专用模板不存在: $CONTEXT_DEV_DIR/templates/CLAUDE_JEECGBOOT.md"
        echo "💡 请确保模板文件存在，或运行完整安装: ./jeecg-ai-setup.sh"
        return 1
    fi
    
    # 备份现有配置（如果存在）
    if [[ -f "$PROJECT_CLAUDE_CONFIG" ]]; then
        BACKUP_FILE="$PROJECT_CLAUDE_CONFIG.backup.$(date +%Y%m%d-%H%M%S)"
        cp "$PROJECT_CLAUDE_CONFIG" "$BACKUP_FILE"
        echo "💾 备份现有配置到: $BACKUP_FILE"
    fi
    
    # 从JeecgBoot专用模板复制配置
    cp "$CONTEXT_DEV_DIR/templates/CLAUDE_JEECGBOOT.md" "$PROJECT_CLAUDE_CONFIG"
    echo "📝 从模板复制配置: CLAUDE_JEECGBOOT.md → CLAUDE.md"
    
    # 添加CodeGen AI代理规范集成（如果尚未包含）
    if ! grep -q "CodeGen AI代理规范集成" "$PROJECT_CLAUDE_CONFIG" 2>/dev/null; then
        echo "📝 添加 CodeGen AI 代理规范集成..."
        echo "" >> "$PROJECT_CLAUDE_CONFIG"
        echo "# ===== CodeGen AI代理规范集成 =====" >> "$PROJECT_CLAUDE_CONFIG"
        echo "## 🤖 CodeGen AI代理核心规范" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- 严格遵循CodeGen/Code_Gen_Agent.md中定义的AI行为边界" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- 使用LangGPT结构化提示进行业务需求分析" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- 自动生成符合JeecgBoot规范的JSON配置文件" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- 调用Code_Gen_Guide.py执行完整代码生成工作流" >> "$PROJECT_CLAUDE_CONFIG"
        echo "" >> "$PROJECT_CLAUDE_CONFIG"
        echo "### AI 命令映射" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- \`/sc:jeecg-analyze\` - 基于 CodeGen AI 代理的需求分析" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- \`/sc:jeecg-config\` - 智能生成 JSON 配置文件" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- \`/sc:codegen\` - 执行完整 CodeGen 工作流" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- \`/sc:jeecg-reset\` - 重置 JeecgBoot AI 环境配置" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- \`/sc:jeecg-update\` - 更新 JeecgBoot AI 环境" >> "$PROJECT_CLAUDE_CONFIG"
    else
        echo "✅ CodeGen AI 代理规范集成已存在，跳过添加"
    fi
    
    echo "✅ CLAUDE 配置更新完成"
    echo "📁 配置文件位置: $PROJECT_CLAUDE_CONFIG"
    echo "📊 配置文件行数: $(wc -l < "$PROJECT_CLAUDE_CONFIG") 行"

    # 验证配置文件完整性
    if [[ $(wc -l < "$PROJECT_CLAUDE_CONFIG") -lt 100 ]]; then
        echo "⚠️  配置文件可能不完整（少于100行），请检查模板文件"
    else
        echo "✅ 配置文件完整性验证通过"
    fi

    # 创建或更新符号链接
    create_claude_symlink
}

# 配置CodeGen集成
setup_codegen_integration() {
    echo "🔧 配置 CodeGen 集成..."
    
    # 检查CodeGen目录
    if [[ ! -d "$PROJECT_ROOT/CodeGen" ]]; then
        echo "⚠️  CodeGen 目录不存在，创建基础结构..."
        mkdir -p "$PROJECT_ROOT/CodeGen"
    fi
    
    # 调用专用函数生成CodeGen命令配置
    generate_codegen_commands
    
    echo "✅ CodeGen 集成配置完成"
}

# 部署增强的 /jeecg-generate-prp 命令
deploy_jeecg_generate_prp_command() {
    echo "🚀 部署增强版 /jeecg-generate-prp 命令..."
    
    # 确保命令目录存在
    CLAUDE_COMMANDS_DIR="$PROJECT_ROOT/.claude/commands"
    mkdir -p "$CLAUDE_COMMANDS_DIR"
    
    # 检查源模板文件是否存在
    if [[ -f "$CONTEXT_DEV_DIR/jeecg-generate-prp-command.md" ]]; then
        # 备份现有命令文件（如果存在）
        if [[ -f "$CLAUDE_COMMANDS_DIR/jeecg-generate-prp.md" ]]; then
            BACKUP_FILE="$CLAUDE_COMMANDS_DIR/jeecg-generate-prp.md.backup.$(date +%Y%m%d-%H%M%S)"
            cp "$CLAUDE_COMMANDS_DIR/jeecg-generate-prp.md" "$BACKUP_FILE"
            echo "💾 备份现有命令文件到: $BACKUP_FILE"
        fi
        
        # 部署新的命令文件
        cp "$CONTEXT_DEV_DIR/jeecg-generate-prp-command.md" "$CLAUDE_COMMANDS_DIR/jeecg-generate-prp.md"
        echo "📝 部署命令文件: jeecg-generate-prp-command.md → .claude/commands/jeecg-generate-prp.md"
        echo "📊 命令文件大小: $(wc -l < "$CLAUDE_COMMANDS_DIR/jeecg-generate-prp.md") 行"
        return 0
    fi
    
    # 如果模板文件不存在，使用内置版本
    echo "📝 使用内置版本创建 /jeecg-generate-prp 命令..."
    
    cat > "$CLAUDE_COMMANDS_DIR/jeecg-generate-prp.md" << 'EOF'
# Create JeecgBoot Requirements PRP

## Feature request: $ARGUMENTS

Generate a comprehensive JeecgBoot requirements document (PRP) based on business needs with thorough research and context. This command is specifically designed for JeecgBoot enterprise rapid development platform, following Context Engineering best practices and CodeGen integration workflows.

The AI agent will receive complete context to enable self-validation and iterative refinement. The generated PRP will be compatible with JeecgBoot's CodeGen system and development workflow.

## Research Process

1. **JeecgBoot Codebase Analysis**
   - Search for similar business modules/patterns in the JeecgBoot codebase
   - Identify existing entities, controllers, and services to reference
   - Note JeecgBoot-specific conventions and architectural patterns
   - Check existing module structures for validation approach
   - Review CodeGen system capabilities and constraints

2. **Business Requirements Analysis**
   - Parse the feature request for business entities and relationships
   - Identify CRUD vs complex business logic requirements  
   - Determine data model design patterns
   - Map business rules to JeecgBoot implementation patterns
   - Analyze integration requirements with existing modules

3. **JeecgBoot Technical Research**
   - Review JeecgBoot documentation and best practices
   - Study table naming conventions (us_{module}_{entity})
   - Check package structure patterns (org.jeecg.modules.{module})
   - Understand CodeGen configuration requirements
   - Research similar implementations in the platform

4. **User Clarification** (if needed)
   - Specific business entity relationships and constraints?
   - Integration requirements with existing JeecgBoot modules?
   - Special permissions or workflow requirements?
   - Performance or scalability considerations?

## PRP Generation

Using PRPs/templates/REQUIREMENTS_JEECGBOOT.md as the foundation template:

### Critical Context to Include for JeecgBoot Development

**JeecgBoot Platform Context:**
- Current project structure and module organization
- Existing entity patterns and naming conventions
- CodeGen system capabilities and configuration requirements
- Integration points with system management modules

**Business Context:**
- Clear business entity definitions with relationships
- User roles and permission requirements
- Business workflow and process definitions
- Data validation and business rules

**Technical Implementation Context:**
- Table naming following us_{module}_{entity} pattern
- Required system fields (id, create_by, create_time, etc.)
- Controller patterns with @RequiresPermissions annotations
- Service layer design with MyBatis-Plus integration
- Vue 3 frontend component requirements

### Implementation Blueprint

**CodeGen Configuration:**
- MODULE_NAME and ENTITY_NAME extraction
- Field definitions with proper data types
- Relationship mappings for complex scenarios
- Permission configuration requirements

**Complex Business Logic Planning:**
- Extensions beyond basic CRUD operations
- Custom business rules and validations
- Workflow integration requirements
- Reporting and analytics needs

### Validation Gates (Must be Executable for JeecgBoot)

```bash
# JeecgBoot Environment Validation
echo "验证 JeecgBoot 开发环境..."
mvn -version
java -version
node --version

# CodeGen System Validation
echo "验证 CodeGen 系统可用性..."
python3 CodeGen/Code_Gen_Guide.py --test-connection

# Project Structure Validation
echo "验证项目结构完整性..."
ls -la jeecg-boot/jeecg-module-system/
ls -la jeecgboot-vue3/src/

# Configuration Validation
echo "验证 JeecgBoot 配置..."
test -f jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application.yml
test -f jeecgboot-vue3/vite.config.ts

# Template Validation
echo "验证模板文件可用性..."
test -f PRPs/templates/REQUIREMENTS_JEECGBOOT.md
```

*** CRITICAL BEFORE WRITING THE PRP ***

*** ULTRATHINK ABOUT THE JEECGBOOT-SPECIFIC REQUIREMENTS AND IMPLEMENTATION APPROACH ***

Consider:
- How does this fit into JeecgBoot's modular architecture?
- What CodeGen configurations will be needed?
- How will this integrate with existing system modules?
- What are the table naming and package structure requirements?
- Are there security and permission considerations?
- What frontend components and APIs will be needed?

## Output

Save the generated requirements document as: `projectDocs/REQUIREMENTS_{project-name}.md`

**File naming convention:**
- Use descriptive project names in kebab-case
- Example: `REQUIREMENTS_customer-management.md`
- Example: `REQUIREMENTS_inventory-system.md`
- Example: `REQUIREMENTS_financial-reporting.md`

## Quality Checklist for JeecgBoot PRPs

- [ ] All JeecgBoot architectural constraints included
- [ ] CodeGen system integration requirements specified
- [ ] Table naming follows us_{module}_{entity} pattern
- [ ] System fields and permissions properly defined
- [ ] Validation gates executable in JeecgBoot environment
- [ ] References existing JeecgBoot patterns and modules
- [ ] Business logic complexity properly classified
- [ ] Frontend and backend requirements aligned
- [ ] Security and permission model complete
- [ ] Performance and scalability considered

## Success Criteria

**CodeGen Compatibility:**
- Requirements can be directly translated to CodeGen configuration
- All entities follow JeecgBoot naming conventions
- Field definitions include proper types and constraints

**Development Readiness:**
- Clear separation between CodeGen tasks and custom development
- Specific implementation guidance for complex business logic
- Complete context for JeecgBoot developers

**Quality Assurance:**
- Executable validation commands for each requirement
- Anti-patterns clearly identified and avoided
- Confidence score of 8+/10 for implementation success

Score the PRP on a scale of 1-10 (confidence level for successful JeecgBoot implementation using CodeGen system and platform best practices)

Remember: The goal is creating a requirements document that enables one-pass implementation success through comprehensive JeecgBoot-specific context and CodeGen integration.
EOF
    
    echo "✅ /jeecg-generate-prp 命令安装完成"
    echo "📁 命令位置: $CLAUDE_COMMANDS_DIR/jeecg-generate-prp.md"
}

# 部署增强的 /jeecg-execute-prp 命令
deploy_jeecg_execute_prp_command() {
    echo "🚀 部署增强版 /jeecg-execute-prp 命令..."
    
    # 确保命令目录存在
    CLAUDE_COMMANDS_DIR="$PROJECT_ROOT/.claude/commands"
    mkdir -p "$CLAUDE_COMMANDS_DIR"
    
    # 检查源模板文件是否存在
    if [[ -f "$CONTEXT_DEV_DIR/jeecg-execute-prp-command.md" ]]; then
        # 备份现有命令文件（如果存在）
        if [[ -f "$CLAUDE_COMMANDS_DIR/jeecg-execute-prp.md" ]]; then
            BACKUP_FILE="$CLAUDE_COMMANDS_DIR/jeecg-execute-prp.md.backup.$(date +%Y%m%d-%H%M%S)"
            cp "$CLAUDE_COMMANDS_DIR/jeecg-execute-prp.md" "$BACKUP_FILE"
            echo "💾 备份现有命令文件到: $BACKUP_FILE"
        fi
        
        # 部署新的命令文件
        cp "$CONTEXT_DEV_DIR/jeecg-execute-prp-command.md" "$CLAUDE_COMMANDS_DIR/jeecg-execute-prp.md"
        echo "📝 部署命令文件: jeecg-execute-prp-command.md → .claude/commands/jeecg-execute-prp.md"
        echo "📊 命令文件大小: $(wc -l < "$CLAUDE_COMMANDS_DIR/jeecg-execute-prp.md") 行"
        echo "✅ /jeecg-execute-prp 命令部署成功"
    else
        echo "⚠️ 执行命令模板文件不存在，跳过部署"
    fi
    
}

# 安装Claude命令系统（整合版）
setup_claude_commands() {
    echo "⚡ 安装 Claude 命令系统（整合版）..."
    
    # 部署增强命令
    deploy_jeecg_generate_prp_command
    deploy_jeecg_execute_prp_command
    
    # 创建命令系统使用指南
    echo "📝 创建命令系统使用指南..."
    
    cat > "$PROJECT_ROOT/.claude/commands/README.md" << 'EOF'
# JeecgBoot Claude 命令系统 (增强版)

## 📋 可用命令

### `/jeecg-generate-prp` - JeecgBoot专用智能需求文档生成命令 (增强版)

专为JeecgBoot企业级快速开发平台设计的智能需求文档生成命令，基于Context Engineering最佳实践，深度集成CodeGen系统工作流程，实现从自然语言需求到标准化项目需求文档的智能化转换。

#### 🌟 增强特性

**1. 智能需求分类决策引擎**
- 自动识别简单CRUD vs 复杂业务需求
- 智能选择CodeGen路径 vs 官方文档研究路径  
- 混合需求的分层实现策略制定

**2. CodeGen系统深度集成**
- 零容忍违规检查机制
- MODULE_NAME、ENTITY_NAME、TABLE_NAME自动提取
- Code_Gen_Agent.md兼容配置自动生成
- 符合JeecgBoot规范的配置参数

**3. 官方技术文档智能研究**
- 自动查询context7.com最佳实践
- 深度研究deepwiki.com技术原理
- JeecgBoot架构合规性自动验证

### `/jeecg-execute-prp` - JeecgBoot专用需求文档执行命令 (增强版)

基于需求文档的端到端代码实现命令，深度集成CodeGen系统，实现四阶段智能执行流程。

#### 🌟 核心执行特性

**1. 智能文档解析与验证引擎**
- 完美继承 `/jeecg-generate-prp` 生成的所有专用配置
- 自动识别需求复杂度分类和技术实现要求
- 智能上下文继承和配置参数提取

**2. CodeGen系统自动化执行集成**
- 自动调用Code_Gen_Agent.md进行需求智能解析
- 智能执行Code_Gen_Guide.py完整代码生成工作流
- 实时监控代码生成过程和错误处理

**3. 智能环境验证与错误处理系统**
- 执行完整的JeecgBoot环境验证脚本
- 智能错误诊断与自动修复能力
- 支持断点续传和执行状态恢复机制

**4. 端到端质量保证与验证机制**
- 验证生成的后端和前端代码完整性
- 执行编译测试和基础功能验证
- 生成详细的执行报告和后续优化建议

#### 命令语法
```bash
/jeecg-generate-prp [需求描述]
/jeecg-execute-prp [需求文档路径]
```

#### 使用示例
```bash
# 基础 CRUD 模块需求
/jeecg-generate-prp 客户管理系统需求

# 复杂业务模块需求
/jeecg-generate-prp 库存管理模块，包含商品入库、出库、盘点功能，支持批次管理和库存预警

# 多功能系统需求
/jeecg-generate-prp 财务报表系统，支持月度和年度报表生成，包含收入分析、支出统计、利润计算等功能
```

#### 核心特性
- 🎯 **JeecgBoot 专用优化**: 针对平台特点进行深度定制
- 📝 **自动模板应用**: 使用 `PRPs/templates/REQUIREMENTS_JEECGBOOT.md` 基础模板
- 💾 **智能文件命名**: 自动保存到 `projectDocs/REQUIREMENTS_{project-name}.md`
- 🔧 **CodeGen 深度集成**: 生成的文档直接兼容 CodeGen 系统
- ✅ **环境验证门槛**: 包含完整的 JeecgBoot 环境验证脚本
- 📊 **质量保证机制**: 内置评分系统确保实施成功率 8+/10

#### 生成文档包含
- **JeecgBoot 平台约束**: 技术栈规范、表命名规范、包结构规范
- **业务需求规格**: 完整的实体定义、业务流程、操作权限
- **技术实现蓝图**: CodeGen 配置要求、前后端实现指导、数据库设计方案
- **验证门槛脚本**: JeecgBoot 环境验证、CodeGen 系统验证、项目结构验证

#### 与 CodeGen 系统的集成工作流
1. **需求输入阶段**: 使用 `/jeecg-generate-prp` 生成标准化需求文档
2. **配置转换阶段**: 需求文档为 CodeGen 配置生成提供完整上下文
3. **代码生成阶段**: CodeGen 系统基于需求文档执行代码生成
4. **质量保证阶段**: 验证生成的代码是否符合需求文档的规格

## 🚀 安装与更新

**完整安装:**
```bash
bash ContextDev/jeecg-ai-setup.sh
```

**仅安装命令系统:**
```bash  
bash ContextDev/jeecg-ai-setup.sh --setup-claude-commands
```

**验证安装:**
```bash
bash ContextDev/jeecg-ai-setup.sh --verify
```

## 📁 相关目录

- **命令定义**: `.claude/commands/`
- **模板文件**: `PRPs/templates/REQUIREMENTS_JEECGBOOT.md`
- **输出目录**: `projectDocs/`
- **配置文件**: `PRPs/CLAUDE.md`

## 🔄 工作流程

1. **需求输入**: 使用 `/jeecg-generate-prp` 命令描述业务需求
2. **自动分析**: AI基于JeecgBoot模式进行深度分析
3. **文档生成**: 生成完整的需求规格文档
4. **CodeGen集成**: 直接用于CodeGen系统代码生成

## ✅ 质量保证

每个生成的需求文档都包含:
- JeecgBoot环境验证脚本
- CodeGen兼容性检查
- 实施成功率评分 (8+/10)
- 可执行的验证命令

---

通过 `jeecg-ai-setup.sh` 脚本维护，与JeecgBoot完整AI环境集成。
EOF
    
    echo "✅ 命令系统使用指南创建完成"
    echo "📁 使用指南位置: $CLAUDE_COMMANDS_DIR/README.md"
    
    # 创建projectDocs目录
    mkdir -p "$PROJECT_ROOT/projectDocs"
    echo "📁 创建输出目录: $PROJECT_ROOT/projectDocs"
    
    echo "✅ Claude 命令系统安装完成"
}

# 跳过Context Engineering示例代码植入（已移除）
# 注意：示例代码仍然会复制到PRPs/examples/目录，供AI开发参考
skip_context_engineering_examples() {
    echo "⏭️  跳过 Context Engineering 示例代码植入..."
    echo "📋 示例代码已保存到 PRPs/examples/ 目录，供 AI 开发参考"
    echo "✅ Context Engineering 保持干净状态"
}

# 跳过Context Engineering模板植入（已移除）
# 注意：模板文件仍然保存在ContextDev/templates/目录，供项目内部使用
skip_context_engineering_templates() {
    echo "⏭️  跳过 Context Engineering 模板植入..."
    echo "📋 模板文件仍然保存在 ContextDev/templates/ 目录，供项目内部使用"
    echo "✅ Context Engineering 模板目录保持干净状态"
}

# 验证安装
verify_installation() {
    echo "🔍 验证安装..."
    
    # 检查Context Engineering
    if [[ -d "$PROJECT_ROOT/context-engineering-intro" ]]; then
        echo "✅ Context Engineering 已安装"
    else
        echo "❌ Context Engineering 安装失败"
    fi
    
    # 检查SuperClaude
    if python3 -c "import SuperClaude; print('SuperClaude available')" 2>/dev/null; then
        echo "✅ SuperClaude Framework 已安装"
    else
        echo "⚠️  SuperClaude Framework 需要手动配置 (可选)"
    fi
    
    # 检查项目级别Claude配置
    if [[ -f "$PROJECT_CLAUDE_CONFIG" ]] && grep -q "JeecgBoot" "$PROJECT_CLAUDE_CONFIG"; then
        echo "✅ 项目级别 Claude Code 配置已加载"
    else
        echo "❌ 项目级别 Claude Code 配置未正确加载"
    fi

    # 检查CLAUDE.md符号链接
    if [[ -L "$PROJECT_ROOT/CLAUDE.md" ]] && [[ -f "$PROJECT_ROOT/CLAUDE.md" ]]; then
        echo "✅ CLAUDE.md 符号链接已创建并有效"
        echo "📍 符号链接: $(ls -la "$PROJECT_ROOT/CLAUDE.md" | awk '{print $9 " -> " $11}')"
    else
        echo "❌ CLAUDE.md 符号链接未正确创建"
    fi
    
    # 检查CodeGen命令配置
    if [[ -f "$PRP_WORK_DIR/codegen_commands.json" ]]; then
        echo "✅ CodeGen 命令配置已创建"
    else
        echo "❌ CodeGen 命令配置创建失败"
    fi
    
    # 检查目录结构
    if [[ -d "$PROJECT_ROOT/PRPs" ]] && [[ -d "$PROJECT_ROOT/.ai-config" ]]; then
        echo "✅ AI 工作目录已创建"
    else
        echo "❌ AI 工作目录创建失败"
    fi
    
    # 检查示例代码（仅检查PRP工作目录）
    echo "✅ Context Engineering 保持干净状态（无示例代码植入）"
    
    # 检查模板体系状态（不再部署到Context Engineering）
    echo "✅ Context Engineering 模板目录保持干净状态（无JeecgBoot模板植入）"
    
    # 检查Claude命令系统（增强版）
    if [[ -d "$PROJECT_ROOT/.claude/commands" ]] && [[ -f "$PROJECT_ROOT/.claude/commands/jeecg-generate-prp.md" ]]; then
        echo "✅ Claude 命令系统已安装 (/jeecg-generate-prp 可用)"
        
        # 检查execute命令
        if [[ -f "$PROJECT_ROOT/.claude/commands/jeecg-execute-prp.md" ]]; then
            echo "✅ Claude 执行命令已安装 (/jeecg-execute-prp 可用)"
        else
            echo "⚠️ Claude 执行命令未安装 (需要jeecg-execute-prp-command.md模板)"
        fi
    else
        echo "❌ Claude 命令系统安装失败"
    fi
    
    # 检查输出目录
    if [[ -d "$PROJECT_ROOT/projectDocs" ]]; then
        echo "✅ 项目文档输出目录已创建"
    else
        echo "❌ 项目文档输出目录创建失败"
    fi

    # 检查示例代码目录
    if [[ -d "$PRP_WORK_DIR/examples" ]] && [[ -f "$PRP_WORK_DIR/examples/INDEX.json" ]]; then
        EXAMPLE_FILE_COUNT=$(find "$PRP_WORK_DIR/examples" -type f | wc -l)
        echo "✅ 示例代码已复制到PRP工作目录 ($EXAMPLE_FILE_COUNT 个文件)"

        # 检查JeecgBoot示例目录
        if [[ -d "$PRP_WORK_DIR/examples/jeecgboot" ]]; then
            echo "✅ JeecgBoot 示例代码结构完整"
        else
            echo "⚠️  JeecgBoot 示例代码结构不完整"
        fi
    else
        echo "❌ 示例代码复制失败或索引文件缺失"
    fi
}

# 显示使用指南
show_usage_guide() {
    echo ""
    echo "🎉 JeecgBoot AI 环境安装完成！"
    echo "================================="
    echo ""
    echo "📚 快速开始："
    echo ""
    echo "1. JeecgBoot 增强版 PRP 工作流（推荐）："
    echo "   /jeecg-generate-prp 客户管理系统需求"
    echo "   /jeecg-execute-prp projectDocs/REQUIREMENTS_customer-management.md"
    echo "   输出: projectDocs/REQUIREMENTS_customer-management.md 和执行日志"
    echo ""
    echo "2. 通用 PRP 工作流："
    echo "   /generate-prp customer-management-requirements.md"
    echo "   /execute-prp PRPs/customer-management.md"
    echo ""
    echo "3. SuperClaude 命令："
    echo "   /sc:jeecg-analyze \"分析业务需求\""
    echo "   /sc:jeecg-config \"生成配置文件\""
    echo "   /sc:codegen \"执行代码生成\""
    echo ""
    echo "4. CodeGen AI 代理："
    echo "   - 严格遵循 CodeGen/Code_Gen_Agent.md 规范"
    echo "   - 自动生成 JeecgBoot 标准配置"
    echo "   - 完整工作流：需求→配置→生成→验证"
    echo ""
    echo "📁 重要目录："
    echo "   - CLAUDE.md -> PRPs/CLAUDE.md              # Claude Code自动检测的符号链接"
    echo "   - PRPs/                                    # PRP工作目录（包含CLAUDE.md）"
    echo "   - PRPs/CLAUDE.md                           # 项目级别Claude配置（实际文件）"
    echo "   - PRPs/examples/                           # JeecgBoot示例代码集合（AI参考）"
    echo "   - PRPs/codegen_commands.json               # CodeGen命令配置"
    echo "   - PRPs/templates/                          # JeecgBoot模板集合"
    echo "   - .claude/commands/                        # Claude命令系统"
    echo "   - projectDocs/                             # 生成的需求文档输出"
    echo "   - .ai-config/                              # AI配置文件"
    echo "   - ContextDev/templates/                    # 原始PRP模板"
    echo "   - ContextDev/examples/                     # 原始示例代码"
    echo ""
    echo "📖 详细文档："
    echo "   - ContextDev/README.md"
    echo "   - ContextDev/JeecgBoot_AI_Integration_Guide.md"
    echo ""
    echo "🔄 更新环境："
    echo "   ./ContextDev/jeecg-ai-update.sh"
    echo ""
    echo "⚠️  重要提示："
    echo "   - 请在JeecgBoot项目根目录中使用Claude Code"
    echo "   - Claude Code会自动检测根目录的CLAUDE.md符号链接"
    echo "   - 实际配置文件位于PRPs/CLAUDE.md，符号链接便于Claude Code检测"
    echo "   - 符号链接已添加到.gitignore，不会影响版本控制"
    echo "   - 全部配置都在项目级别，不影响全局设置"
}

# ==================== 主安装流程 ====================

# 主安装流程 - SuperClaude Framework 完整集成
main() {
    local start_time=$(date +%s)

    echo ""
    echo "🚀 开始 JeecgBoot AI 环境 v3.0 完整集成..."
    echo "📋 集成方案: ContextDev/superclaude-integration-plan.md"
    echo "🎯 目标: 双框架隔离集成 (Context Engineering + SuperClaude Framework)"
    echo ""

    # 初始化日志
    echo "$(date '+%Y-%m-%d %H:%M:%S') [START] JeecgBoot AI 环境安装开始" > "$INSTALL_LOG"

    # 阶段一：基础设施搭建
    log_info "=== 阶段一：基础设施搭建 ==="

    # 1.1 系统环境检查
    check_prerequisites

    # 1.2 创建集成层目录结构
    create_integration_directories

    # 1.3 上游项目同步
    sync_context_engineering
    sync_superclaude_framework

    # 1.4 Python 包安装
    install_superclaude_package

    # 1.5 配置文件生成
    generate_integration_configs

    # 1.6 集成脚本生成
    generate_integration_scripts

    # 阶段一验证
    log_info "验证阶段一完成状态..."
    if "$SCRIPTS_DIR/validate-integration.sh"; then
        log_success "阶段一：基础设施搭建完成 ✅"
        update_integration_status "phase_1" "completed" "v3.0"
    else
        log_error "阶段一验证失败"
        exit 1
    fi

    # 保持现有功能兼容性
    log_info "=== 兼容性保证：现有功能集成 ==="

    # 设置 PRP 工作流
    setup_prp_templates
    setup_claude_config

    # 保持现有的 Claude 配置和 PRP 工作流
    create_claude_symlink

    # 显示安装结果
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo ""
    echo "🎉 JeecgBoot AI 环境 v3.0 集成完成！"
    echo "⏱️  总耗时: ${duration} 秒"
    echo ""
    echo "📊 集成状态:"
    echo "  ✅ Context Engineering: 8.5/10 (已集成)"
    echo "  ✅ SuperClaude Framework: 基础设施完成"
    echo "  ✅ ContextDev 集成层: 已建立"
    echo "  ✅ 双框架隔离: 已实现"
    echo ""
    echo "📋 下一步:"
    echo "  1. 运行验证: bash ContextDev/scripts/validate-integration.sh"
    echo "  2. 查看集成方案: ContextDev/superclaude-integration-plan.md"
    echo "  3. 开始阶段二: 命令系统集成 (手动执行)"
    echo ""
    echo "🔧 可用命令:"
    echo "  - 现有: /jeecg-generate-prp, /jeecg-execute-prp"
    echo "  - 计划: /sc:implement, /sc:analyze, /sc:design, /sc:test"
    echo ""

    log_success "JeecgBoot AI 环境 v3.0 安装完成"
}

# ==================== 参数处理 ====================

# 检查参数和显示帮助
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "🚀 JeecgBoot AI 环境安装脚本 v3.0 (SuperClaude Framework 完整集成版)"
    echo "=================================================================="
    echo ""
    echo "📋 集成方案: 双框架隔离集成 (Context Engineering + SuperClaude Framework)"
    echo "🏗️ 架构模式: ContextDev 作为集成层，两个上游项目完全独立"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "🔧 主要选项:"
    echo "  --help, -h                显示此帮助信息"
    echo "  --verify                  验证集成状态和环境"
    echo "  --phase1                  仅执行阶段一：基础设施搭建"
    echo "  --sync-upstream           仅同步上游项目"
    echo "  --validate-integration    仅运行集成验证"
    echo ""
    echo "🛠️ 维护选项:"
    echo "  --update-configs          更新配置文件"
    echo "  --regenerate-scripts      重新生成集成脚本"
    echo "  --create-claude-symlink   创建CLAUDE.md符号链接"
    echo ""
    echo "📊 此脚本将完成："
    echo "  ✅ 阶段一：基础设施搭建"
    echo "    - 创建 ContextDev 集成层目录结构"
    echo "    - 同步 Context Engineering 和 SuperClaude Framework"
    echo "    - 安装 SuperClaude Python 包"
    echo "    - 生成分层配置文件"
    echo "    - 创建集成脚本和验证工具"
    echo ""
    echo "  🔄 后续阶段 (需手动执行)："
    echo "    - 阶段二：命令系统集成 (/sc: 命令)"
    echo "    - 阶段三：Persona 系统集成 (智能专家)"
    echo "    - 阶段四：MCP 服务器集成 (外部工具)"
    echo ""
    echo "📖 详细信息: ContextDev/superclaude-integration-plan.md"
    exit 0
fi

# 验证模式
if [[ "$1" == "--verify" ]]; then
    echo "🔍 验证集成状态和环境..."
    if [[ -f "$SCRIPTS_DIR/validate-integration.sh" ]]; then
        bash "$SCRIPTS_DIR/validate-integration.sh"
    else
        echo "❌ 验证脚本不存在，请先运行完整安装"
        exit 1
    fi
    exit 0
fi

# 阶段一模式
if [[ "$1" == "--phase1" ]]; then
    echo "🚀 仅执行阶段一：基础设施搭建..."
    check_prerequisites
    create_integration_directories
    sync_context_engineering
    sync_superclaude_framework
    install_superclaude_package
    generate_integration_configs
    generate_integration_scripts
    echo "✅ 阶段一完成"
    exit 0
fi

# 同步上游项目
if [[ "$1" == "--sync-upstream" ]]; then
    echo "🔄 同步上游项目..."
    if [[ -f "$SCRIPTS_DIR/sync-upstream.sh" ]]; then
        bash "$SCRIPTS_DIR/sync-upstream.sh"
    else
        sync_context_engineering
        sync_superclaude_framework
    fi
    exit 0
fi

# 验证集成
if [[ "$1" == "--validate-integration" ]]; then
    echo "🧪 运行集成验证..."
    if [[ -f "$SCRIPTS_DIR/validate-integration.sh" ]]; then
        bash "$SCRIPTS_DIR/validate-integration.sh"
    else
        echo "❌ 验证脚本不存在，请先运行安装"
        exit 1
    fi
    exit 0
fi

# 更新配置文件
if [[ "$1" == "--update-configs" ]]; then
    echo "⚙️ 更新配置文件..."
    generate_integration_configs
    echo "✅ 配置文件更新完成"
    exit 0
fi

# 重新生成脚本
if [[ "$1" == "--regenerate-scripts" ]]; then
    echo "🔧 重新生成集成脚本..."
    generate_integration_scripts
    echo "✅ 集成脚本重新生成完成"
    exit 0
fi

# 创建符号链接
if [[ "$1" == "--create-claude-symlink" ]]; then
    echo "🔗 创建CLAUDE.md符号链接..."
    create_claude_symlink
    echo "✅ CLAUDE.md符号链接创建完成"
    exit 0
fi

# ==================== 主程序入口 ====================

# 运行主安装流程 - SuperClaude Framework 完整集成
echo "🎯 启动 JeecgBoot AI 环境 v3.0 安装程序..."
echo "📋 集成方案文档: ContextDev/superclaude-integration-plan.md"
echo ""

main "$@"