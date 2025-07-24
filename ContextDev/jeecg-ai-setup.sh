#!/bin/bash

# JeecgBoot AI 环境安装脚本 v2.0 (ContextDev + CodeGen 集成版)
# 为 JeecgBoot 项目提供完整的 AI 赋能开发环境

set -e

echo "🚀 JeecgBoot AI 环境安装 v2.0 (ContextDev + CodeGen 集成版)"
echo "============================================================="

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONTEXT_DEV_DIR="$PROJECT_ROOT/ContextDev"
PRP_WORK_DIR="$PROJECT_ROOT/PRPs"
PROJECT_CLAUDE_CONFIG="$PRP_WORK_DIR/CLAUDE.md"

# 检查系统要求
check_prerequisites() {
    echo "🔍 检查系统要求..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    echo "✅ Python 3: $(python3 --version)"
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装，请先安装 Node.js 18+"
        exit 1
    fi
    echo "✅ Node.js: $(node --version)"
    
    # 检查是否在JeecgBoot项目目录
    if [[ ! -f "$PROJECT_ROOT/jeecg-boot/pom.xml" ]] || [[ ! -f "$PROJECT_ROOT/jeecgboot-vue3/package.json" ]]; then
        echo "❌ 请在 JeecgBoot 项目根目录运行此脚本"
        exit 1
    fi
    echo "✅ JeecgBoot 项目目录验证通过"
}

# 安装Context Engineering
install_context_engineering() {
    echo "📚 安装 Context Engineering..."
    
    if [[ ! -d "$PROJECT_ROOT/context-engineering-intro" ]]; then
        echo "📥 克隆 Context Engineering 项目..."
        cd "$PROJECT_ROOT"
        git clone https://github.com/coleam00/context-engineering-intro.git
        cd "$CONTEXT_DEV_DIR"
    else
        echo "📦 更新现有的 Context Engineering..."
        cd "$PROJECT_ROOT/context-engineering-intro"
        if ! git pull origin main; then
            echo "⚠️  网络更新失败，但现有版本可以继续使用"
        fi
        cd "$CONTEXT_DEV_DIR"
    fi
    
    echo "✅ Context Engineering 安装完成"
}

# 安装SuperClaude Framework
install_superclaude() {
    echo "🤖 安装 SuperClaude Framework..."
    
    # 检查是否已安装uv
    if ! command -v uv &> /dev/null; then
        echo "📦 安装 uv 包管理器..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # 添加到当前会话的PATH
        export PATH="/Users/admin/.local/bin:$PATH"
    fi
    
    # 安装SuperClaude (使用pip作为备选方案)
    echo "📦 安装 SuperClaude 包..."
    if command -v uv &> /dev/null && [[ -f "pyproject.toml" ]]; then
        uv add SuperClaude
    else
        pip3 install SuperClaude
    fi
    
    # 配置SuperClaude
    echo "🔧 配置 SuperClaude..."
    python3 -c "try:
    import SuperClaude
    print('✅ SuperClaude 可用')
except ImportError:
    print('⚠️  SuperClaude 安装需要手动配置')
except Exception as e:
    print(f'⚠️  SuperClaude 配置: {e}')"
    
    echo "✅ SuperClaude Framework 安装完成"
}

# 创建AI配置目录
setup_ai_config() {
    echo "📁 设置 AI 配置目录..."
    
    mkdir -p "$PROJECT_ROOT/.ai-config"
    
    # 复制配置文件
    if [[ -f "$CONTEXT_DEV_DIR/jeecg-ai-config.json" ]]; then
        cp "$CONTEXT_DEV_DIR/jeecg-ai-config.json" "$PROJECT_ROOT/.ai-config/"
        echo "✅ AI 配置文件已复制"
    fi
    
    # 创建项目级别的PRP工作目录和Claude配置
    mkdir -p "$PRP_WORK_DIR"
    echo "📁 创建PRP工作目录: $PRP_WORK_DIR"
    
    echo "✅ AI 配置目录设置完成"
}

# 创建CLAUDE.md符号链接到项目根目录
create_claude_symlink() {
    echo "🔗 创建 CLAUDE.md 符号链接到项目根目录..."

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

# 复制JeecgBoot示例代码到Context Engineering
copy_example_codes() {
    echo "📋 复制 JeecgBoot 示例代码到 Context Engineering..."
    
    EXAMPLES_DIR="$PROJECT_ROOT/context-engineering-intro/examples"
    
    # 创建示例代码目录结构
    mkdir -p "$EXAMPLES_DIR/jeecgboot"
    mkdir -p "$EXAMPLES_DIR/jeecgboot/backend"
    mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend"
    
    # 后端示例代码复制
    echo "📂 复制后端示例代码..."
    
    # 实体类示例
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/entity"
        
        # 复制核心实体类
        declare -a entities=("SysUser.java" "SysDepart.java" "SysRole.java" "SysPermission.java")
        for entity in "${entities[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/$entity" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/$entity" "$EXAMPLES_DIR/jeecgboot/backend/entity/"
                echo "  ✓ 复制实体类: $entity"
            fi
        done
        
        # 复制关联实体
        declare -a relations=("SysUserRole.java" "SysUserDepart.java" "SysRolePermission.java")
        for relation in "${relations[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/$relation" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/$relation" "$EXAMPLES_DIR/jeecgboot/backend/entity/"
                echo "  ✓ 复制关联实体: $relation"
            fi
        done
    fi
    
    # 控制器示例
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/controller"
        
        declare -a controllers=("SysUserController.java" "SysDepartController.java" "SysRoleController.java")
        for controller in "${controllers[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/$controller" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/$controller" "$EXAMPLES_DIR/jeecgboot/backend/controller/"
                echo "  ✓ 复制控制器: $controller"
            fi
        done
    fi
    
    # 服务层示例
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/service"
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/service/impl"
        
        # 服务接口
        declare -a services=("ISysUserService.java" "ISysDepartService.java" "ISysRoleService.java")
        for service in "${services[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/$service" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/$service" "$EXAMPLES_DIR/jeecgboot/backend/service/"
                echo "  ✓ 复制服务接口: $service"
            fi
        done
        
        # 服务实现
        declare -a impls=("SysUserServiceImpl.java" "SysDepartServiceImpl.java" "SysRoleServiceImpl.java")
        for impl in "${impls[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/impl/$impl" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/impl/$impl" "$EXAMPLES_DIR/jeecgboot/backend/service/impl/"
                echo "  ✓ 复制服务实现: $impl"
            fi
        done
    fi
    
    # Mapper层示例
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/mapper" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/mapper"
        
        declare -a mappers=("SysUserMapper.java" "SysDepartMapper.java" "SysRoleMapper.java")
        for mapper in "${mappers[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/mapper/$mapper" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/mapper/$mapper" "$EXAMPLES_DIR/jeecgboot/backend/mapper/"
                echo "  ✓ 复制Mapper: $mapper"
            fi
        done
    fi
    
    # Demo模块示例（如果存在）
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/demo"
        
        # 复制Demo实体
        if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test/entity/JeecgDemo.java" ]]; then
            cp "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test/entity/JeecgDemo.java" "$EXAMPLES_DIR/jeecgboot/backend/demo/"
            echo "  ✓ 复制Demo实体: JeecgDemo.java"
        fi
        
        # 复制Demo控制器
        if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test/controller/JeecgDemoController.java" ]]; then
            cp "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test/controller/JeecgDemoController.java" "$EXAMPLES_DIR/jeecgboot/backend/demo/"
            echo "  ✓ 复制Demo控制器: JeecgDemoController.java"
        fi
    fi
    
    # 前端示例代码复制
    echo "📂 复制前端示例代码..."
    
    # 用户管理页面
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/user" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/views/system/user"
        cp -r "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/user/"* "$EXAMPLES_DIR/jeecgboot/frontend/views/system/user/"
        echo "  ✓ 复制用户管理页面"
    fi
    
    # 部门管理页面
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/depart" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/views/system/depart"
        cp -r "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/depart/"* "$EXAMPLES_DIR/jeecgboot/frontend/views/system/depart/"
        echo "  ✓ 复制部门管理页面"
    fi
    
    # 角色管理页面
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/role" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/views/system/role"
        cp -r "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/role/"* "$EXAMPLES_DIR/jeecgboot/frontend/views/system/role/"
        echo "  ✓ 复制角色管理页面"
    fi
    
    # 菜单权限页面
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/menu" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/views/system/menu"
        cp -r "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/menu/"* "$EXAMPLES_DIR/jeecgboot/frontend/views/system/menu/"
        echo "  ✓ 复制菜单权限页面"
    fi
    
    # API服务层
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/api/sys" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/api/sys"
        
        declare -a apis=("user.ts" "menu.ts" "role.ts" "depart.ts")
        for api in "${apis[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecgboot-vue3/src/api/sys/$api" ]]; then
                cp "$PROJECT_ROOT/jeecgboot-vue3/src/api/sys/$api" "$EXAMPLES_DIR/jeecgboot/frontend/api/sys/"
                echo "  ✓ 复制API服务: $api"
            fi
        done
    fi
    
    # 状态管理
    if [[ -f "$PROJECT_ROOT/jeecgboot-vue3/src/store/modules/user.ts" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/store/modules"
        cp "$PROJECT_ROOT/jeecgboot-vue3/src/store/modules/user.ts" "$EXAMPLES_DIR/jeecgboot/frontend/store/modules/"
        echo "  ✓ 复制用户状态管理"
    fi
    
    # 路由配置
    if [[ -f "$PROJECT_ROOT/jeecgboot-vue3/src/router/routes/modules/demo/system.ts" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/router/routes/modules/demo"
        cp "$PROJECT_ROOT/jeecgboot-vue3/src/router/routes/modules/demo/system.ts" "$EXAMPLES_DIR/jeecgboot/frontend/router/routes/modules/demo/"
        echo "  ✓ 复制系统路由配置"
    fi
    
    # AI模块示例（如果存在）
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/airag"
        
        # AI实体类
        if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/entity/AiragModel.java" ]]; then
            cp "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/entity/AiragModel.java" "$EXAMPLES_DIR/jeecgboot/backend/airag/"
            echo "  ✓ 复制AI模型实体"
        fi
        
        # AI控制器
        if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/app/controller/AiragChatController.java" ]]; then
            cp "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/app/controller/AiragChatController.java" "$EXAMPLES_DIR/jeecgboot/backend/airag/"
            echo "  ✓ 复制AI聊天控制器"
        fi
    fi
    
    # 创建示例代码说明文档
    cat > "$EXAMPLES_DIR/jeecgboot/README.md" << 'EOF'
# JeecgBoot 示例代码集合

本目录包含了JeecgBoot项目的典型前后端示例代码，用于Context Engineering和AI开发参考。

## 后端示例代码 (backend/)

### 1. 实体类 (entity/)
- **SysUser.java** - 系统用户实体，展示完整的JPA注解、系统字段、Excel导出等
- **SysDepart.java** - 部门实体，展示树形结构设计
- **SysRole.java** - 角色实体，展示权限管理相关设计
- **SysPermission.java** - 权限实体，展示菜单权限控制
- **SysUserRole.java** - 用户角色关联，展示多对多关系设计

### 2. 控制器 (controller/)
- **SysUserController.java** - 用户管理控制器，展示完整的CRUD操作、权限控制、Excel导入导出
- **SysDepartController.java** - 部门管理控制器，展示树形结构操作
- **SysRoleController.java** - 角色管理控制器，展示权限分配逻辑

### 3. 服务层 (service/ & service/impl/)
- 服务接口和实现类，展示业务逻辑封装和事务处理

### 4. 数据访问层 (mapper/)
- MyBatis-Plus Mapper接口，展示数据访问层设计

### 5. 业务示例 (demo/)
- **JeecgDemo.java** - 典型业务实体示例
- **JeecgDemoController.java** - 典型业务控制器示例

### 6. AI模块 (airag/)
- AI相关的实体类和控制器示例

## 前端示例代码 (frontend/)

### 1. 页面组件 (views/system/)
- **user/** - 用户管理页面，展示列表页面、表单编辑、权限控制
- **depart/** - 部门管理页面，展示树形组件使用
- **role/** - 角色管理页面，展示权限分配界面
- **menu/** - 菜单权限页面，展示菜单树管理

### 2. API服务 (api/sys/)
- **user.ts** - 用户相关API接口定义
- **menu.ts** - 菜单相关API接口定义
- **role.ts** - 角色相关API接口定义
- **depart.ts** - 部门相关API接口定义

### 3. 状态管理 (store/modules/)
- **user.ts** - 用户状态管理模块，展示Pinia使用

### 4. 路由配置 (router/routes/modules/demo/)
- **system.ts** - 系统管理模块路由配置

## 使用说明

1. **开发参考**: 这些示例代码展示了JeecgBoot的标准开发模式
2. **AI训练**: 可用于训练AI理解JeecgBoot的代码结构和最佳实践
3. **Context Engineering**: 为PRP和其他AI工作流提供上下文参考
4. **Code Generation**: CodeGen系统可以基于这些示例生成类似的代码结构

## 核心特点

- **统一的实体基类**: 所有实体都继承基础系统字段
- **权限注解**: 使用@RequiresPermissions等注解进行权限控制
- **Excel支持**: 实体类支持Excel导入导出
- **树形结构**: 部门和菜单展示了树形数据处理
- **组件化**: 前端使用可复用的JEECG组件
- **TypeScript**: 前端全面使用TypeScript提供类型安全

这些示例代码是JeecgBoot开发的最佳实践参考。
EOF
    
    echo "✅ JeecgBoot 示例代码复制完成"
    echo "📍 示例代码位置: $EXAMPLES_DIR/jeecgboot/"
}

# 部署JeecgBoot模板集合到Context Engineering
deploy_template_system() {
    echo "📋 部署 JeecgBoot 模板体系到 Context Engineering..."
    
    TEMPLATES_DEPLOY_DIR="$PROJECT_ROOT/context-engineering-intro/templates"
    
    # 创建模板部署目录
    mkdir -p "$TEMPLATES_DEPLOY_DIR/jeecgboot"
    
    # 部署完整的JeecgBoot模板体系
    echo "📂 部署JeecgBoot完整模板体系..."
    
    # 复制所有模板文件到Context Engineering
    declare -a template_files=(
        "CLAUDE_JEECGBOOT.md"
        "REQUIREMENTS_JEECGBOOT.md" 
        "PLANNING_JEECGBOOT.md"
        "DESIGN_JEECGBOOT.md"
        "TASK_JEECGBOOT.md"
        "TESTING_JEECGBOOT.md"
    )
    
    for template_file in "${template_files[@]}"; do
        if [[ -f "$CONTEXT_DEV_DIR/templates/$template_file" ]]; then
            cp "$CONTEXT_DEV_DIR/templates/$template_file" "$TEMPLATES_DEPLOY_DIR/jeecgboot/"
            echo "  ✓ 部署模板: $template_file"
        else
            echo "  ⚠️  模板文件不存在: $template_file"
        fi
    done
    
    # 创建模板使用指南
    cat > "$TEMPLATES_DEPLOY_DIR/jeecgboot/USAGE_GUIDE.md" << 'EOF'
# JeecgBoot 模板体系使用指南

## 📚 模板文件说明

### 核心模板文件
- **CLAUDE_JEECGBOOT.md** - AI编程规范和行为约束
- **REQUIREMENTS_JEECGBOOT.md** - 需求分析和规格说明模板
- **PLANNING_JEECGBOOT.md** - 项目规划和架构设计模板
- **DESIGN_JEECGBOOT.md** - 系统设计和技术方案模板
- **TASK_JEECGBOOT.md** - 任务管理和进度跟踪模板
- **TESTING_JEECGBOOT.md** - 测试计划和用例管理模板
- **CLAUDE_JEECGBOOT.md** - 主要的AI编程规范文档 (现已移至PRPs/CLAUDE.md)

## 🚀 快速开始

### 方式一：使用完整文档体系
1. 复制所有模板文件到项目根目录
2. 根据项目需求填写各模板文件
3. 按照文档间的引用关系维护一致性

### 方式二：选择性使用
1. 根据项目需求选择必要的模板文件
2. 确保保持模板间的交叉引用完整性
3. 参考各模板文件内的使用说明

## 🔄 与CodeGen系统集成

模板体系已完全集成CodeGen系统的实现蓝图：
- **环境准备**: 数据字典获取和需求分析
- **配置生成**: JSON配置文件生成和验证
- **代码生成**: Maven模块创建和代码生成
- **前端迁移**: Vue3代码集成和路由配置
- **权限测试**: 权限配置和功能验证

## 📋 验证门槛

使用模板开发的项目必须通过以下验证：
1. CodeGen配置验证通过
2. JeecgBoot服务连接正常
3. 表名格式符合规范
4. 代码生成成功执行
5. 后端编译无错误
6. 前端构建成功
7. 单元测试通过

## 📞 获取支持

- **技术问题**: 参考各模板文件中的故障排除章节
- **使用指导**: 查看PRPs/CLAUDE.md中的完整规范文档
- **最佳实践**: 参考templates/目录下的示例代码
EOF
    
    # 创建模板索引文件
    cat > "$TEMPLATES_DEPLOY_DIR/jeecgboot/INDEX.json" << 'EOF'
{
  "template_system": "JeecgBoot完整模板体系",
  "version": "2.0.0",
  "updated": "2025-07-23",
  "templates": {
    "ai_programming": {
      "file": "CLAUDE_JEECGBOOT.md",
      "type": "AI规范",
      "description": "AI编程规范和行为约束指南"
    },
    "requirements": {
      "file": "REQUIREMENTS_JEECGBOOT.md", 
      "type": "需求分析",
      "description": "需求分析和规格说明模板"
    },
    "planning": {
      "file": "PLANNING_JEECGBOOT.md",
      "type": "项目规划", 
      "description": "项目规划和架构设计模板"
    },
    "design": {
      "file": "DESIGN_JEECGBOOT.md",
      "type": "系统设计",
      "description": "系统设计和技术方案模板，包含故障排除"
    },
    "task_management": {
      "file": "TASK_JEECGBOOT.md",
      "type": "任务管理",
      "description": "任务管理和进度跟踪模板，含CodeGen实现蓝图"
    },
    "testing": {
      "file": "TESTING_JEECGBOOT.md", 
      "type": "测试计划",
      "description": "测试计划和验证门槛模板"
    },
    "ai_programming": {
      "file": "PRPs/CLAUDE.md",
      "type": "主文档",
      "description": "完整的AI编程规范和使用指南"
    }
  },
  "integration": {
    "codegen_system": true,
    "prp_workflow": true,
    "context_engineering": true
  }
}
EOF
    
    echo "✅ JeecgBoot 模板体系部署完成"
    echo "📍 模板部署位置: $TEMPLATES_DEPLOY_DIR/jeecgboot/"
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
    
    # 检查示例代码
    if [[ -d "$PROJECT_ROOT/context-engineering-intro/examples/jeecgboot" ]]; then
        echo "✅ JeecgBoot 示例代码已复制"
    else
        echo "❌ JeecgBoot 示例代码复制失败"
    fi
    
    # 检查模板体系部署
    if [[ -d "$PROJECT_ROOT/context-engineering-intro/templates/jeecgboot" ]] && [[ -f "$PROJECT_ROOT/context-engineering-intro/templates/jeecgboot/INDEX.json" ]]; then
        echo "✅ JeecgBoot 模板体系已部署"
    else
        echo "❌ JeecgBoot 模板体系部署失败"
    fi
    
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

# 主安装流程
main() {
    echo "开始安装 JeecgBoot AI 环境..."
    
    check_prerequisites
    install_context_engineering
    install_superclaude
    setup_ai_config
    setup_claude_config
    setup_prp_templates
    setup_codegen_integration
    setup_claude_commands
    copy_example_codes
    deploy_template_system
    verify_installation
    show_usage_guide
    
    echo ""
    echo "✨ 安装完成！现在可以使用 AI 赋能开发功能了！"
}

# 检查参数
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "JeecgBoot AI环境安装脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h                显示此帮助信息"
    echo "  --verify                  仅验证环境，不执行安装"
    echo "  --examples-only           仅复制JeecgBoot示例代码到Context Engineering"
    echo "  --templates-only          仅部署JeecgBoot模板体系到Context Engineering"
    echo "  --generate-codegen        仅生成CodeGen命令配置文件"
    echo "  --update-claude-config    仅从JeecgBoot模板更新CLAUDE配置文件"
    echo "  --setup-claude-commands   仅安装Claude命令系统"
    echo "  --create-claude-symlink   仅创建CLAUDE.md符号链接到项目根目录"
    echo ""
    echo "此脚本将安装："
    echo "1. Context Engineering (PRP工作流)"
    echo "2. SuperClaude Framework (专业命令)"
    echo "3. CodeGen AI代理集成"
    echo "4. Claude Code配置"
    echo "5. JeecgBoot完整模板体系"
    echo "6. JeecgBoot前后端示例代码"
    exit 0
fi

if [[ "$1" == "--verify" ]]; then
    echo "🔍 验证模式 - 仅检查安装状态"
    verify_installation
    exit 0
fi

if [[ "$1" == "--examples-only" ]]; then
    echo "📋 仅复制示例代码模式"
    copy_example_codes
    echo "✅ 示例代码复制完成"
    exit 0
fi

if [[ "$1" == "--templates-only" ]]; then
    echo "📋 仅部署模板体系模式"
    deploy_template_system
    echo "✅ 模板体系部署完成"
    exit 0
fi

if [[ "$1" == "--generate-codegen" ]]; then
    echo "🔧 仅生成CodeGen命令配置文件模式"
    generate_codegen_commands
    echo "✅ CodeGen命令配置文件生成完成"
    exit 0
fi

if [[ "$1" == "--update-claude-config" ]]; then
    echo "🔄 仅更新CLAUDE配置文件模式"
    update_claude_config_from_template
    echo "✅ CLAUDE配置文件更新完成"
    exit 0
fi

if [[ "$1" == "--setup-claude-commands" ]]; then
    echo "⚡ 仅安装Claude命令系统模式"
    setup_claude_commands
    echo "✅ Claude命令系统安装完成"
    exit 0
fi

if [[ "$1" == "--create-claude-symlink" ]]; then
    echo "🔗 仅创建CLAUDE.md符号链接模式"
    create_claude_symlink
    echo "✅ CLAUDE.md符号链接创建完成"
    exit 0
fi

# 运行主安装流程
main "$@"