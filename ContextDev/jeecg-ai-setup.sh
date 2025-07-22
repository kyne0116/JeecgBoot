#!/bin/bash

# JeecgBoot AI 赋能快速安装脚本 v2.0 (CodeGen + PRP 集成版)
# 基于上游项目，最小化定制，深度集成 CodeGen 系统和 PRP 工作流

set -e

echo "🚀 JeecgBoot AI 赋能环境快速搭建 v2.0 (CodeGen + PRP 集成版)"
echo "======================================================="

# 检查依赖
check_dependencies() {
    echo "📋 检查依赖环境..."
    
    # 检查Python (CodeGen系统要求)
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 未安装，请先安装Python 3.7+ (CodeGen系统要求)"
        exit 1
    fi

    # 检查Python版本
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "ℹ️  Python版本: $python_version"

    # 检查CodeGen系统
    if [ ! -d "CodeGen" ]; then
        echo "❌ CodeGen目录不存在，请确保在JeecgBoot项目根目录执行此脚本"
        exit 1
    fi

    if [ ! -f "CodeGen/Code_Gen_Guide.py" ]; then
        echo "❌ CodeGen/Code_Gen_Guide.py 不存在"
        exit 1
    fi

    if [ ! -f "CodeGen/Code_Gen_Agent.md" ]; then
        echo "❌ CodeGen/Code_Gen_Agent.md 不存在"
        exit 1
    fi

    echo "✅ CodeGen系统检查通过"

    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装，请先安装Node.js 16+"
        exit 1
    fi

    # 检查Maven (CodeGen编译要求)
    if ! command -v mvn &> /dev/null; then
        echo "⚠️  Maven 未安装，CodeGen编译功能将受限"
    else
        echo "✅ Maven检查通过"
    fi

    # 检查JeecgBoot服务
    if curl -s --connect-timeout 5 http://localhost:8080/jeecg-boot/sys/common/403 > /dev/null; then
        echo "✅ JeecgBoot服务运行正常"
    else
        echo "⚠️  JeecgBoot服务未运行或无法访问，某些功能可能受限"
    fi

    # 检查uv
    if ! command -v uv &> /dev/null; then
        echo "📦 安装uv包管理器..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.bashrc
    fi

    echo "✅ 依赖检查完成"
}

# 安装Context Engineering
setup_context_engineering() {
    echo "📚 设置Context Engineering..."
    
    if [ ! -d "context-engineering-intro" ]; then
        git clone https://github.com/coleam00/context-engineering-intro.git
    fi
    
    cd context-engineering-intro
    
    # 追加JeecgBoot配置到CLAUDE.md
    if [ -f "../ContextDev/jeecg-claude-extension.md" ]; then
        echo "" >> CLAUDE.md
        echo "# ===== JeecgBoot项目扩展配置 =====" >> CLAUDE.md
        cat ../ContextDev/jeecg-claude-extension.md >> CLAUDE.md
        echo "✅ JeecgBoot配置已追加到CLAUDE.md"
    fi

    # 追加CodeGen AI代理规范集成
    echo "" >> CLAUDE.md
    echo "# ===== CodeGen AI代理规范集成 =====" >> CLAUDE.md
    echo "## 🤖 CodeGen AI代理核心规范" >> CLAUDE.md
    echo "- 严格遵循CodeGen/Code_Gen_Agent.md中定义的AI行为边界" >> CLAUDE.md
    echo "- 使用LangGPT结构化提示进行业务需求分析" >> CLAUDE.md
    echo "- 自动生成符合JeecgBoot规范的JSON配置文件" >> CLAUDE.md
    echo "- 调用Code_Gen_Guide.py执行完整代码生成工作流" >> CLAUDE.md
    echo "✅ CodeGen AI代理规范集成完成"

    # 创建JeecgBoot示例目录（包含PRP模板）
    mkdir -p examples/jeecg-boot/{backend,frontend,database,tests,codegen}
    mkdir -p PRPs/templates

    # 复制CodeGen示例到examples
    if [ -f "../CodeGen/Code_Gen_Guide.json" ]; then
        cp ../CodeGen/Code_Gen_Guide.json examples/jeecg-boot/codegen/
    fi
    if [ -f "../CodeGen/Code_Gen_field_templates.json" ]; then
        cp ../CodeGen/Code_Gen_field_templates.json examples/jeecg-boot/codegen/
    fi
    echo "✅ CodeGen示例文件复制完成"

    # 复制JeecgBoot专用PRP模板
    if [ -f "../ContextDev/templates/jeecg-prp-template.md" ]; then
        cp ../ContextDev/templates/jeecg-prp-template.md PRPs/templates/
        echo "✅ JeecgBoot PRP模板复制完成"
    fi
    
    # 复制JeecgBoot示例到examples目录
    if [ ! -d "examples/jeecg-boot" ]; then
        mkdir -p examples/jeecg-boot
        echo "📁 创建JeecgBoot示例目录"
        # 这里可以复制示例文件
    fi
    
    cd ..
    echo "✅ Context Engineering设置完成"
}

# 安装SuperClaude Framework
setup_superclaude() {
    echo "🤖 安装SuperClaude Framework..."
    
    # 安装SuperClaude
    uv add SuperClaude
    
    # 运行安装器 - 使用developer profile包含所有功能
    echo "🔧 配置SuperClaude Framework..."
    python3 -m SuperClaude install --profile developer --non-interactive
    
    echo "✅ SuperClaude Framework安装完成"
}

# 安装MCP服务器
setup_mcp_servers() {
    echo "🔗 安装MCP服务器..."
    
    # 安装常用MCP服务器
    npm install -g @context7/mcp-server || echo "⚠️  Context7 MCP服务器安装失败，可稍后手动安装"
    npm install -g @sequential/mcp-server || echo "⚠️  Sequential MCP服务器安装失败，可稍后手动安装"
    npm install -g @magic/mcp-server || echo "⚠️  Magic MCP服务器安装失败，可稍后手动安装"
    npm install -g @playwright/mcp-server || echo "⚠️  Playwright MCP服务器安装失败，可稍后手动安装"
    
    echo "✅ MCP服务器安装完成"
}

# 配置Claude Code
setup_claude_code() {
    echo "⚙️  配置Claude Code..."
    
    # 确保.claude目录存在
    mkdir -p ~/.claude
    
    # 复制CLAUDE.md到Claude Code配置目录
    if [ -f "context-engineering-intro/CLAUDE.md" ]; then
        cp context-engineering-intro/CLAUDE.md ~/.claude/CLAUDE.md
        echo "✅ CLAUDE.md已复制到Claude Code配置目录"
    fi
    
    # 创建CodeGen专用MCP服务器
    mkdir -p ~/.claude/mcp-codegen
    cat > ~/.claude/mcp-codegen/server.js << 'EOF'
// CodeGen MCP服务器 - JeecgBoot代码生成专用
const { spawn } = require('child_process');
const path = require('path');

class CodeGenMCPServer {
  constructor() {
    this.codegenPath = process.env.CODEGEN_PATH || './CodeGen';
  }

  async generateCode(config) {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(this.codegenPath, 'Code_Gen_Guide.py');
      const process = spawn('python3', [scriptPath, '--config', config]);

      let output = '';
      process.stdout.on('data', (data) => {
        output += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve(output);
        } else {
          reject(new Error(`CodeGen process failed with code ${code}`));
        }
      });
    });
  }

  async validateTableName(tableName) {
    const pattern = /^us_[a-z]+_[a-z_]+$/;
    return pattern.test(tableName);
  }
}

module.exports = CodeGenMCPServer;
EOF
    echo "✅ CodeGen MCP服务器创建完成"

    # 创建CodeGen专用命令配置
    cat > ~/.claude/codegen_commands.json << 'EOF'
{
  "codegen_commands": {
    "/sc:codegen": {
      "description": "JeecgBoot代码生成",
      "workflow": [
        "分析业务需求",
        "设计字段结构",
        "生成JSON配置",
        "执行Code_Gen_Guide.py",
        "验证生成结果"
      ]
    },
    "/sc:jeecg-analyze": {
      "description": "JeecgBoot业务需求分析",
      "ai_agent": "Code_Gen_Agent",
      "output": "字段设计方案"
    },
    "/sc:jeecg-config": {
      "description": "生成JeecgBoot配置文件",
      "template": "Code_Gen_Guide.json",
      "validation": "7个系统字段检查"
    }
  }
}
EOF
    echo "✅ CodeGen专用命令配置完成"

    # 创建MCP服务器配置（包含CodeGen服务器）
    if [ ! -f "~/.claude/mcp_servers.json" ]; then
        cat > ~/.claude/mcp_servers.json << 'EOF'
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["@context7/mcp-server"],
      "env": {
        "CONTEXT7_API_KEY": "your-api-key-here"
      }
    },
    "sequential": {
      "command": "npx",
      "args": ["@sequential/mcp-server"]
    },
    "magic": {
      "command": "npx",
      "args": ["@magic/mcp-server"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp-server"]
    },
    "codegen": {
      "command": "node",
      "args": ["~/.claude/mcp-codegen/server.js"],
      "env": {
        "CODEGEN_PATH": "./CodeGen"
      },
      "description": "JeecgBoot CodeGen专用MCP服务器"
    }
  }
}
EOF
        echo "✅ MCP服务器配置已创建（包含CodeGen服务器）"
    fi
}

# 创建JeecgBoot项目配置
setup_jeecg_project() {
    echo "🏗️  配置JeecgBoot项目..."
    
    # 如果在JeecgBoot项目目录中运行
    if [ -f "pom.xml" ] && grep -q "jeecg-boot" pom.xml; then
        echo "📍 检测到JeecgBoot项目，创建AI配置..."
        
        # 创建.ai-config目录
        mkdir -p .ai-config
        
        # 复制配置文件
        if [ -f "ContextDev/jeecg-ai-config.json" ]; then
            cp ContextDev/jeecg-ai-config.json .ai-config/
        fi

        # 创建CodeGen集成环境变量文件
        cat > .ai-config/.env << EOF
JEECG_PROJECT_ROOT=$(pwd)
JEECG_MODULE_PREFIX=jeecg-module
JEECG_API_BASE=http://localhost:8080/jeecg-boot
JEECG_CODE_GEN_SCRIPT=CodeGen/Code_Gen_Guide.py
JEECG_CODE_GEN_CONFIG=CodeGen/Code_Gen_Config.json
JEECG_CODE_GEN_TEMPLATE=CodeGen/Code_Gen_Guide.json
JEECG_AI_AGENT_SPEC=CodeGen/Code_Gen_Agent.md
EOF

        # 创建CodeGen AI代理配置
        cat > .ai-config/codegen-ai-config.json << 'EOF'
{
  "ai_agent": {
    "name": "JeecgBoot CodeGen AI Agent",
    "version": "3.0",
    "specification_file": "CodeGen/Code_Gen_Agent.md",
    "capabilities": [
      "业务需求分析",
      "字段结构设计",
      "JSON配置生成",
      "代码生成执行",
      "结果验证"
    ]
  },
  "integration": {
    "context_engineering": {
      "prp_template": "jeecg-codegen-prp.md",
      "examples_path": "examples/jeecg-boot/codegen"
    },
    "superclaude": {
      "custom_commands": [
        "/sc:codegen",
        "/sc:jeecg-analyze",
        "/sc:jeecg-config"
      ]
    },
    "mcp_servers": {
      "codegen_server": "~/.claude/mcp-codegen/server.js"
    }
  },
  "workflow": {
    "steps": [
      "AI需求分析",
      "字段设计",
      "配置生成",
      "代码生成",
      "编译验证",
      "前端迁移",
      "权限授权"
    ],
    "automation_level": "full"
  }
}
EOF

        echo "✅ JeecgBoot项目AI配置完成（包含CodeGen集成）"
    else
        echo "ℹ️  未检测到JeecgBoot项目，跳过项目配置"
    fi
}

# 验证安装
verify_installation() {
    echo "🔍 验证安装..."

    # 检查SuperClaude
    if python3 -c "import SuperClaude; print(f'SuperClaude {SuperClaude.__version__} installed')" 2>/dev/null; then
        echo "✅ SuperClaude Framework 可用"
    else
        echo "❌ SuperClaude Framework 安装失败"
    fi

    # 检查Context Engineering
    if [ -f "context-engineering-intro/CLAUDE.md" ]; then
        echo "✅ Context Engineering 可用"
    else
        echo "❌ Context Engineering 设置失败"
    fi

    # 检查Claude Code配置
    if [ -f ~/.claude/CLAUDE.md ]; then
        echo "✅ Claude Code 配置完成"
    else
        echo "❌ Claude Code 配置失败"
    fi

    # 检查CodeGen系统
    if python3 CodeGen/Code_Gen_Guide.py --help > /dev/null 2>&1; then
        echo "✅ CodeGen系统可用"
    else
        echo "❌ CodeGen系统验证失败"
    fi

    # 检查MCP服务器
    if npm list -g | grep -q mcp-server; then
        echo "✅ MCP服务器安装完成"
    else
        echo "❌ MCP服务器安装失败"
    fi

    # 检查CodeGen MCP服务器
    if [ -f ~/.claude/mcp-codegen/server.js ]; then
        echo "✅ CodeGen MCP服务器创建完成"
    else
        echo "❌ CodeGen MCP服务器创建失败"
    fi

    # 检查项目配置
    if [ -f .ai-config/jeecg-ai-config.json ] && [ -f .ai-config/codegen-ai-config.json ]; then
        echo "✅ JeecgBoot项目配置完成"
    else
        echo "❌ JeecgBoot项目配置失败"
    fi

    # 检查PRP模板
    if [ -f ContextDev/templates/jeecg-prp-template.md ]; then
        echo "✅ JeecgBoot PRP模板验证通过"
    else
        echo "❌ JeecgBoot PRP模板验证失败"
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    echo "🎉 安装完成！"
    echo "=============="
    echo ""
    echo "📖 快速开始："
    echo "1. 打开Claude Code"
    echo "2. 在JeecgBoot项目中使用以下命令测试功能："
    echo ""
    echo "   # 测试基础功能"
    echo "   /sc:analyze \"测试JeecgBoot AI集成\""
    echo ""
    echo "   # 测试CodeGen AI代理"
    echo "   /sc:jeecg-analyze \"设计一个客户管理模块\""
    echo ""
    echo "   # 测试配置生成"
    echo "   /sc:jeecg-config \"生成客户管理模块的JSON配置\""
    echo ""
    echo "   # 测试完整代码生成"
    echo "   /sc:codegen \"执行完整的代码生成工作流\""
    echo ""
    echo "   # 测试PRP工作流（推荐）"
    echo "   /generate-prp customer-management-requirements.md"
    echo "   /execute-prp PRPs/customer-management.md"
    echo ""
    echo "   # 测试架构设计"
    echo "   /sc:architect \"设计一个简单的模块架构\""
    echo ""
    echo "🔧 CodeGen系统测试："
    echo "   python3 CodeGen/Code_Gen_Guide.py --help"
    echo "   python3 CodeGen/Code_Gen_Guide.py --validate-config"
    echo "   python3 CodeGen/Code_Gen_Guide.py --test-connection"
    echo ""
    echo "📚 更多信息："
    echo "- 快速开始指南: ContextDev/Quick_Start_Guide.md"
    echo "- 完整集成指南: ContextDev/JeecgBoot_AI_Integration_Guide.md"
    echo "- CodeGen系统文档: CodeGen/Code_Gen_Guide.md"
    echo "- CodeGen AI代理规范: CodeGen/Code_Gen_Agent.md"
    echo "- Context Engineering: ./context-engineering-intro/README.md"
    echo "- SuperClaude Framework: https://github.com/SuperClaude-Org/SuperClaude_Framework"
    echo "- JeecgBoot配置: ./ContextDev/jeecg-ai-config.json"
    echo ""
    echo "🔧 配置文件位置："
    echo "- Claude配置: ~/.claude/"
    echo "- 项目配置: .ai-config/"
    echo "- CodeGen MCP服务器: ~/.claude/mcp-codegen/"
    echo ""
    echo "🔄 如需更新上游项目："
    echo "   ./ContextDev/jeecg-ai-update.sh"
}

# 主函数
main() {
    echo "🚀 开始安装JeecgBoot AI赋能环境（CodeGen集成版）..."
    echo ""

    check_dependencies
    echo ""

    setup_context_engineering
    echo ""

    setup_superclaude
    echo ""

    setup_mcp_servers
    echo ""

    setup_claude_code
    echo ""

    setup_jeecg_project
    echo ""

    verify_installation
    echo ""

    show_usage
    
    echo ""
    echo "✨ JeecgBoot AI赋能环境搭建完成！"
}

# 运行主函数
main "$@"
