# JeecgBoot AI 赋能集成指南

## 📋 概述

本指南将帮助您在现有 JeecgBoot 项目中集成 Context Engineering Intro 和 SuperClaude Framework，并深度整合 JeecgBoot CodeGen 系统，实现 AI 辅助开发能力。整个集成过程采用"最大化上游复用，最小化自定义"的原则，确保与上游项目保持同步。

## 🎯 核心特性

### 🤖 AI 代理驱动的代码生成

- **CodeGen AI 代理**: 基于 Code_Gen_Agent.md 规范的智能代码生成
- **业务需求理解**: AI 自动分析业务需求，生成标准化字段设计
- **配置文件智能生成**: 自动生成符合 JeecgBoot 规范的 JSON 配置
- **完整工作流自动化**: 从需求分析到代码部署的全流程自动化

### 📋 PRP 工作流集成

- **产品需求提示 (PRP)**: Context Engineering 的核心工作流，90%+ 成功率
- **完整上下文**: 包含项目文档、代码模式、最佳实践的综合实现蓝图
- **自动化验证**: 多层次质量检查和验证门槛
- **错误自愈**: 内置错误处理和自动重试机制

### 🔧 深度集成 JeecgBoot CodeGen 系统

- **AI 增强的 Code_Gen_Guide.py**: 智能参数生成和执行优化
- **标准化表名解析**: AI 辅助的模块和包名生成
- **自动化编译验证**: Maven 编译和前端代码迁移
- **权限系统集成**: 自动权限授权和角色管理

## 🔍 1. 环境准备与依赖检查

### 1.1 系统要求

**基础环境**：

- Python 3.7+ (CodeGen 系统要求)
- Node.js 16+
- Git 2.20+
- JeecgBoot 项目（Spring Boot + Vue3）
- Maven 3.6+ (代码编译要求)

**JeecgBoot CodeGen 系统要求**：

- JeecgBoot 后端服务运行在 http://localhost:8080
- 管理员账户权限 (admin/123456)
- MySQL 数据库连接正常
- 在线表单功能可用

**兼容性矩阵**：
| 组件 | 最低版本 | 推荐版本 | JeecgBoot 兼容性 | CodeGen 集成 |
|------|----------|----------|----------------|-------------|
| Context Engineering Intro | 1.0.0 | latest | ✅ 完全兼容 | ✅ AI 代理集成 |
| SuperClaude Framework | 3.0.0 | latest | ✅ 完全兼容 | ✅ 命令映射 |
| JeecgBoot CodeGen | 3.0+ | latest | ✅ 原生支持 | ✅ 核心系统 |
| Claude Code | 1.0.0 | latest | ✅ 完全兼容 | ✅ AI 执行引擎 |
| Node.js | 16 | 18+ | ✅ 完全兼容 |

### 1.2 环境检查脚本

在 JeecgBoot 项目根目录执行：

```bash
# 检查Python版本和CodeGen系统
python3 --version
# 预期输出: Python 3.7.x 或更高

# 检查CodeGen系统
ls -la CodeGen/
# 预期输出: 应包含Code_Gen_Agent.md, Code_Gen_Guide.py等文件

# 检查JeecgBoot服务状态
curl -s http://localhost:8080/jeecg-boot/sys/common/403 | head -1
# 预期输出: 应返回JeecgBoot响应

# 验证CodeGen配置
python3 CodeGen/Code_Gen_Guide.py --help
# 预期输出: CodeGen工具帮助信息

# 检查Maven环境
mvn --version
# 预期输出: Apache Maven 3.6.x 或更高

# 检查Node.js版本
node --version
# 预期输出: v16.x.x 或更高

# 检查Git版本
git --version
# 预期输出: git version 2.20.x 或更高

# 检查当前Git状态
git status
# 预期输出: 工作目录干净，无未提交的更改
```

### 1.3 CodeGen 系统验证

**验证 CodeGen 核心功能**：

```bash
# 1. 验证配置文件
python3 CodeGen/Code_Gen_Guide.py --validate-config

# 2. 测试JeecgBoot连接
python3 CodeGen/Code_Gen_Guide.py --test-connection

# 3. 获取数据字典
python3 CodeGen/Code_Gen_Guide.py --dict

# 4. 验证表名格式
python3 CodeGen/Code_Gen_Guide.py --validate-table-name us_test_demo
# 预期输出: 表名格式验证通过
```

### 1.4 依赖工具安装

**安装 uv 包管理器**（推荐）：

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 验证安装
uv --version
# 预期输出: uv x.x.x
```

## 🚀 2. 分步安装指南

### 2.1 快速安装（推荐）

**使用一键安装脚本**：

```bash
# 1. 下载安装脚本
curl -O https://raw.githubusercontent.com/kyne0116/JeecgBoot/my-custom/ContextDev/jeecg-ai-setup.sh
chmod +x jeecg-ai-setup.sh

# 2. 执行安装
./jeecg-ai-setup.sh

# 预期输出:
# 🚀 JeecgBoot AI赋能环境快速搭建
# ==================================
# 📋 检查依赖环境...
# ✅ 依赖检查完成
# 📚 设置Context Engineering...
# ✅ Context Engineering设置完成
# 🤖 安装SuperClaude Framework...
# ✅ SuperClaude Framework安装完成
# 🔗 安装MCP服务器...
# ✅ MCP服务器安装完成
# ⚙️ 配置Claude Code...
# ✅ Claude Code配置完成
# 🏗️ 配置JeecgBoot项目...
# ✅ JeecgBoot项目AI配置完成
# 🎉 安装完成！
```

### 2.2 手动安装步骤

#### 2.2.1 Context Engineering Intro 安装

```bash
# 1. 克隆Context Engineering项目
git clone https://github.com/coleam00/context-engineering-intro.git
cd context-engineering-intro

# 2. 验证项目结构
ls -la
# 预期输出: 应包含CLAUDE.md, PRPs/, examples/, .claude/等目录

# 3. 追加JeecgBoot配置到CLAUDE.md
echo "" >> CLAUDE.md
echo "# ===== JeecgBoot项目扩展配置 =====" >> CLAUDE.md
cat ../jeecg-claude-extension.md >> CLAUDE.md

# 4. 创建JeecgBoot示例目录（包含PRP模板）
mkdir -p examples/jeecg-boot/{backend,frontend,database,tests,codegen}

# 5. 复制CodeGen示例到examples
cp ../CodeGen/Code_Gen_Guide.json examples/jeecg-boot/codegen/
[ -f ../CodeGen/Code_Gen_field_templates.json ] && cp ../CodeGen/Code_Gen_field_templates.json examples/jeecg-boot/codegen/

# 6. 创建JeecgBoot专用PRP模板目录
mkdir -p PRPs/templates
cp ../ContextDev/templates/*.md PRPs/templates/

# 7. 复制配置到Claude Code目录
cp CLAUDE.md ~/.claude/CLAUDE.md

cd ..
```

#### 2.2.2 SuperClaude Framework 安装

```bash
# 1. 安装SuperClaude包
uv add SuperClaude

# 2. 运行安装器（交互式）
python3 -m SuperClaude install --interactive

# 安装选项选择:
# ✅ Core Framework
# ✅ All 16 Commands
# ✅ 9 AI Personas
# ✅ MCP Servers (Context7, Sequential, Magic, Playwright)

# 3. 验证安装
python3 -c "import SuperClaude; print(f'SuperClaude {SuperClaude.__version__} installed')"
# 预期输出: SuperClaude 3.x.x installed

# 4. 测试命令可用性
SuperClaude --help
# 预期输出: SuperClaude命令帮助信息
```

#### 2.2.3 MCP 服务器安装

```bash
# 1. 安装Context7 MCP服务器
npm install -g @context7/mcp-server

# 2. 安装Sequential MCP服务器
npm install -g @sequential/mcp-server

# 3. 安装Magic MCP服务器
npm install -g @magic/mcp-server

# 4. 安装Playwright MCP服务器
npm install -g @playwright/mcp-server

# 5. 验证安装
npm list -g | grep mcp-server
# 预期输出: 应显示所有已安装的MCP服务器
```

#### 2.2.4 Claude Code 配置

```bash
# 1. 创建MCP服务器配置
mkdir -p ~/.claude
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
    }
  }
}
EOF

# 2. 验证配置文件
cat ~/.claude/mcp_servers.json | python3 -m json.tool
# 预期输出: 格式化的JSON配置
```

#### 2.2.5 JeecgBoot 特定配置

```bash
# 1. 在JeecgBoot项目根目录创建AI配置
mkdir -p .ai-config

# 2. 复制项目配置文件
cp jeecg-ai-config.json .ai-config/

# 3. 创建环境变量文件
cat > .ai-config/.env << EOF
JEECG_PROJECT_ROOT=$(pwd)
JEECG_MODULE_PREFIX=jeecg-module
JEECG_API_BASE=http://localhost:8080/jeecg-boot
JEECG_CODE_GEN_SCRIPT=Code_Gen_Guide.py
EOF

# 4. 验证配置
ls -la .ai-config/
# 预期输出: 应包含jeecg-ai-config.json和.env文件
```

## ✅ 3. 集成验证测试

### 3.1 基础功能验证

**验证 Context Engineering**：

```bash
# 1. 检查CLAUDE.md配置
grep -A 5 "JeecgBoot项目扩展配置" ~/.claude/CLAUDE.md
# 预期输出: 应显示JeecgBoot扩展配置内容

# 2. 检查PRP模板
ls context-engineering-intro/PRPs/templates/
# 预期输出: 应包含prp_base.md等模板文件
```

**验证 SuperClaude Framework**：

```bash
# 1. 测试SuperClaude命令
python3 -c "
from SuperClaude import commands
print('Available commands:', len(commands.get_all_commands()))
"
# 预期输出: Available commands: 16

# 2. 测试AI人格
python3 -c "
from SuperClaude import personas
print('Available personas:', len(personas.get_all_personas()))
"
# 预期输出: Available personas: 9
```

**验证 MCP 服务器**：

```bash
# 1. 测试Context7连接
npx @context7/mcp-server --test
# 预期输出: Context7 MCP server test passed

# 2. 测试其他MCP服务器
for server in sequential magic playwright; do
    echo "Testing $server..."
    npx @$server/mcp-server --version
done
# 预期输出: 每个服务器的版本信息
```

### 3.2 Claude Code 集成测试

**在 Claude Code 中测试以下命令**：

```bash
# 1. 测试基础分析命令
/sc:analyze "测试JeecgBoot AI集成是否正常工作"
# 预期输出: AI应该识别这是一个测试请求并提供分析

# 2. 测试设计命令
/sc:design "设计一个简单的JeecgBoot用户管理模块"
# 预期输出: AI应该提供JeecgBoot风格的模块设计方案

# 3. 测试实现命令
/sc:implement "创建一个简单的JeecgBoot实体类示例"
# 预期输出: AI应该生成包含7个系统字段的JeecgBoot实体类

# 4. 测试人格切换
/sc:architect "从架构师角度分析JeecgBoot模块设计"
# 预期输出: AI应该以架构师身份提供专业建议

# 5. 测试CodeGen专用命令
/sc:jeecg-analyze "设计一个产品管理模块"
# 预期输出: AI应该基于CodeGen AI代理规范提供字段设计方案

/sc:jeecg-config "生成产品管理模块的JSON配置"
# 预期输出: AI应该生成包含7个系统字段的完整JSON配置

/sc:codegen "执行产品管理模块的代码生成"
# 预期输出: AI应该调用Code_Gen_Guide.py执行代码生成

# 6. 测试PRP工作流（推荐）
/generate-prp test-requirements.md
# 预期输出: AI应该生成包含完整上下文的PRP文件

/execute-prp PRPs/test-module.md
# 预期输出: AI应该执行PRP并调用CodeGen系统

# 7. 测试MCP服务器
/sc:load context7 "JeecgBoot开发最佳实践"
# 预期输出: 应该从Context7获取相关文档信息
```

### 3.3 JeecgBoot 代码生成器集成测试

```bash
# 1. 验证Code_Gen_Guide.py可用性
python3 Code_Gen_Guide.py --help
# 预期输出: 代码生成器帮助信息

# 2. 测试AI增强的配置生成
# 在Claude Code中执行:
/sc:implement "为员工管理模块生成JSON配置文件"
# 预期输出: AI应该生成符合JeecgBoot规范的JSON配置

# 3. 验证生成的配置格式
python3 -m json.tool generated_config.json
# 预期输出: 格式正确的JSON配置文件
```

### 3.4 常见问题排查

**问题 1: SuperClaude 命令不可用**

```bash
# 诊断步骤
python3 -c "import SuperClaude"
# 如果报错，重新安装:
uv add SuperClaude --reinstall
python3 -m SuperClaude install --force
```

**问题 2: MCP 服务器连接失败**

```bash
# 检查服务器状态
npm list -g | grep mcp-server
# 重新安装问题服务器:
npm uninstall -g @context7/mcp-server
npm install -g @context7/mcp-server
```

**问题 3: Claude Code 配置未生效**

```bash
# 检查配置文件
ls -la ~/.claude/
cat ~/.claude/CLAUDE.md | grep "JeecgBoot"
# 重新复制配置:
cp context-engineering-intro/CLAUDE.md ~/.claude/CLAUDE.md
```

## 📖 4. 日常使用教程

### 4.1 JeecgBoot 模块开发 AI 工作流

**完整开发流程示例**：

```bash
# 步骤1: 需求分析
/sc:analyze "开发HRMS人力资源管理系统的员工信息管理模块，包含员工基本信息CRUD、部门关联、职位管理等功能"

# 步骤2: 架构设计
/sc:design "基于JeecgBoot框架设计员工管理模块，包含数据模型、API接口、权限控制等"

# 步骤3: 模块实现
/sc:implement "实现员工管理模块，包含后端Entity、Service、Controller和前端Vue组件"

# 步骤4: 代码优化
/sc:improve "优化员工管理模块的代码质量、性能和安全性"

# 步骤5: 测试生成
/sc:test "为员工管理模块生成完整的单元测试和集成测试"

# 步骤6: 文档生成
/sc:document "生成员工管理模块的API文档和用户手册"
```

### 4.2 常用 AI 命令应用场景

**开发类命令**：

```bash
# 分析业务需求
/sc:analyze "分析电商订单管理系统的核心功能需求"

# 设计系统架构
/sc:design "设计基于JeecgBoot的订单管理模块架构"

# 实现具体功能
/sc:implement "实现订单状态流转的业务逻辑"

# 构建项目
/sc:build "构建JeecgBoot项目的前后端代码"
```

**质量类命令**：

```bash
# 代码改进
/sc:improve "优化订单查询的数据库性能"

# 测试生成
/sc:test "为订单服务生成单元测试用例"

# 代码清理
/sc:cleanup "清理订单模块中的冗余代码和依赖"
```

**问题排查命令**：

```bash
# 故障诊断
/sc:troubleshoot "订单创建时出现数据库连接超时错误"

# 代码解释
/sc:explain "解释JeecgBoot权限拦截器的工作原理"
```

### 4.3 专业人格应用示例

**架构师人格**：

```bash
/sc:architect "设计一个支持多租户的JeecgBoot SaaS架构"
# 应用场景: 系统架构设计、技术选型、性能优化方案
```

**后端专家人格**：

```bash
/sc:backend "实现JeecgBoot中的分布式事务处理机制"
# 应用场景: Spring Boot开发、数据库设计、API实现
```

**前端专家人格**：

```bash
/sc:frontend "优化JeecgBoot前端的页面加载性能"
# 应用场景: Vue3开发、组件设计、用户体验优化
```

**安全专家人格**：

```bash
/sc:security "审查JeecgBoot项目的安全漏洞和防护措施"
# 应用场景: 安全审计、权限设计、漏洞修复
```

### 4.4 上游项目更新同步

**定期更新流程**：

```bash
# 1. 执行更新脚本
./jeecg-ai-update.sh

# 预期输出:
# 🔄 JeecgBoot AI环境上游同步
# ==========================
# 💾 备份JeecgBoot定制配置...
# 📁 备份保存在: jeecg-backup-20240122-143022
# 📚 更新Context Engineering...
# ✅ Context Engineering更新完成
# 🤖 更新SuperClaude Framework...
# ✅ SuperClaude Framework更新完成
# 🔗 更新MCP服务器...
# ✅ MCP服务器更新完成
# 🔧 恢复JeecgBoot定制配置...
# ✅ JeecgBoot配置已恢复
# ✨ 上游同步完成！

# 2. 验证更新结果
./jeecg-ai-update.sh --dry-run

# 3. 测试更新后的功能
/sc:analyze "测试更新后的AI功能是否正常"
```

**手动更新步骤**：

```bash
# 1. 更新Context Engineering
cd context-engineering-intro
git pull origin main
cd ..

# 2. 更新SuperClaude Framework
uv add SuperClaude --upgrade

# 3. 更新MCP服务器
npm update -g @context7/mcp-server @sequential/mcp-server @magic/mcp-server @playwright/mcp-server

# 4. 重新配置Claude Code
cp context-engineering-intro/CLAUDE.md ~/.claude/CLAUDE.md
```

## 🔧 维护和故障排除

### 常见问题解决方案

**问题: AI 命令响应缓慢**

```bash
# 解决方案: 检查MCP服务器状态
npx @context7/mcp-server --status
# 重启Claude Code应用
```

**问题: 代码生成器集成失败**

```bash
# 解决方案: 检查Python环境和依赖
python3 -c "import sys; print(sys.path)"
pip install -r requirements.txt
```

**问题: 配置文件丢失**

```bash
# 解决方案: 从备份恢复
ls jeecg-backup-*/
cp jeecg-backup-latest/jeecg-ai-config.json .ai-config/
```

## 🎯 实际应用案例

### 案例 1: 员工管理模块开发

**需求**: 开发 HRMS 系统的员工管理模块

**AI 辅助开发流程**:

```bash
# 1. 需求分析
/sc:analyze "开发员工管理模块，包含员工基本信息、部门关联、入职离职流程"

# 2. 数据库设计
/sc:data "设计员工信息表结构，包含JeecgBoot必需的7个系统字段"

# 3. 后端实现
/sc:backend "实现员工管理的Entity、Service、Controller"

# 4. 前端开发
/sc:frontend "创建员工管理的Vue3页面，使用Ant Design Vue组件"

# 5. 权限配置
/sc:security "配置员工管理的菜单权限和数据权限"

# 6. 测试验证
/sc:test "生成员工管理模块的完整测试用例"
```

**预期成果**:

- 完整的员工管理 CRUD 功能
- 符合 JeecgBoot 规范的代码结构
- 包含权限控制的前后端实现
- 完整的测试覆盖

### 案例 2: 在线表单快速创建

**需求**: 创建产品信息录入表单

**AI 辅助流程**:

```bash
# 1. 表单设计
/sc:design "设计产品信息在线表单，包含基本信息、分类、价格等字段"

# 2. 配置生成
/sc:implement "生成产品信息表单的JSON配置文件"

# 3. 表单创建
# 使用生成的配置调用JeecgBoot在线表单API
python Code_Gen_Guide.py --config product_form_config.json

# 4. 界面优化
/sc:frontend "优化产品信息表单的用户界面和交互体验"
```

## 🔄 持续集成和自动化

### CI/CD 集成

**GitHub Actions 配置示例**:

```yaml
# .github/workflows/ai-quality-check.yml
name: AI Quality Check

on:
  pull_request:
    branches: [main, develop]

jobs:
  ai-quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install AI Tools
        run: |
          pip install SuperClaude
          npm install -g @context7/mcp-server

      - name: Run AI Code Review
        run: |
          /sc:analyze "代码质量检查"
          /sc:security "安全漏洞扫描"
          /sc:improve "代码优化建议"
```

### 自动化脚本

**每日 AI 辅助开发脚本**:

```bash
#!/bin/bash
# daily-ai-dev.sh

echo "🌅 开始每日AI辅助开发流程"

# 1. 检查待办任务
/sc:task "检查今日开发任务列表"

# 2. 代码质量检查
/sc:analyze "分析昨日提交的代码变更"

# 3. 安全扫描
/sc:security "扫描新增代码的安全问题"

# 4. 性能优化建议
/sc:improve "提供性能优化建议"

echo "✅ 每日AI检查完成"
```

## 📊 效果评估和指标

### 开发效率指标

**量化指标**:

- 模块开发时间: 传统方式 vs AI 辅助
- 代码质量评分: SonarQube 分析结果
- 测试覆盖率: 单元测试和集成测试覆盖率
- 文档完整性: API 文档和用户手册完成度

**评估脚本**:

```bash
#!/bin/bash
# metrics-collection.sh

echo "📊 收集开发效率指标"

# 1. 代码质量指标
sonar-scanner -Dsonar.projectKey=jeecg-ai-enhanced

# 2. 测试覆盖率
mvn clean test jacoco:report

# 3. AI使用统计
/sc:analyze "统计本周AI命令使用情况"

# 4. 生成报告
/sc:document "生成开发效率评估报告"
```

## 🚨 安全和最佳实践

### 安全配置

**API 密钥管理**:

```bash
# 1. 创建环境变量文件
cat > .ai-config/.env.local << EOF
CONTEXT7_API_KEY=your-secure-api-key
OPENAI_API_KEY=your-openai-key
CLAUDE_API_KEY=your-claude-key
EOF

# 2. 添加到.gitignore
echo ".ai-config/.env.local" >> .gitignore

# 3. 使用环境变量
export $(cat .ai-config/.env.local | xargs)
```

**代码审查清单**:

```bash
# AI生成代码审查清单
/sc:security "审查AI生成的代码是否存在安全漏洞"
/sc:analyze "检查代码是否符合JeecgBoot开发规范"
/sc:test "验证AI生成的测试用例是否充分"
```

### 最佳实践建议

1. **渐进式采用**: 从简单模块开始，逐步扩展到复杂业务
2. **人工审查**: AI 生成的代码必须经过人工审查
3. **版本控制**: 定期备份 AI 配置和自定义内容
4. **团队培训**: 确保团队成员了解 AI 工具的正确使用方法
5. **持续优化**: 根据使用反馈不断优化 AI 配置和工作流程

## 📞 技术支持

### 社区资源

- **JeecgBoot 社区**: [http://jeecg.com](http://jeecg.com)
- **Context Engineering 讨论**: GitHub Issues
- **SuperClaude Framework 支持**: 官方文档和社区论坛

### 故障报告

**问题反馈模板**:

```markdown
## 问题描述

[详细描述遇到的问题]

## 环境信息

- JeecgBoot 版本:
- Context Engineering 版本:
- SuperClaude Framework 版本:
- 操作系统:
- Python 版本:
- Node.js 版本:

## 重现步骤

1. [步骤 1]
2. [步骤 2]
3. [步骤 3]

## 预期结果

[描述预期的正确结果]

## 实际结果

[描述实际发生的结果]

## 错误日志
```

[粘贴相关的错误日志]

````

## 📚 参考资源

- [Context Engineering Intro官方文档](https://github.com/coleam00/context-engineering-intro)
- [SuperClaude Framework官方文档](https://github.com/SuperClaude-Org/SuperClaude_Framework)
- [JeecgBoot官方文档](http://doc.jeecg.com)
- [Claude Code使用指南](https://docs.anthropic.com/en/docs/claude-code)
- [MCP服务器开发指南](https://modelcontextprotocol.io)

## 📋 附录

### A. 配置文件模板

**jeecg-ai-config.json完整示例**:
```json
{
  "project": {
    "name": "JeecgBoot AI Enhanced Development",
    "version": "1.0.0",
    "description": "JeecgBoot项目AI赋能配置"
  },
  "ai_enhancements": {
    "context_engineering": {
      "use_upstream_prp": true,
      "custom_sections": ["jeecg_architecture", "code_generation_workflow"]
    },
    "superclaude": {
      "use_all_commands": true,
      "use_all_personas": true
    }
  }
}
````

### B. 常用命令速查表

| 命令                | 用途               | 示例                               | 集成特性              |
| ------------------- | ------------------ | ---------------------------------- | --------------------- |
| `/generate-prp`     | PRP 生成           | `/generate-prp requirements.md`    | ✅ 推荐方式           |
| `/execute-prp`      | PRP 执行           | `/execute-prp PRPs/module.md`      | ✅ 90%+ 成功率        |
| `/sc:jeecg-analyze` | JeecgBoot 需求分析 | `/sc:jeecg-analyze "用户管理需求"` | ✅ CodeGen AI 代理    |
| `/sc:jeecg-config`  | 配置文件生成       | `/sc:jeecg-config "生成JSON配置"`  | ✅ 智能生成           |
| `/sc:codegen`       | 代码生成           | `/sc:codegen "执行代码生成"`       | ✅ CodeGen 集成       |
| `/sc:design`        | 架构设计           | `/sc:design "模块架构"`            | ✅ JeecgBoot 最佳实践 |
| `/sc:implement`     | 功能实现           | `/sc:implement "CRUD功能"`         | ✅ 生成代码优化       |
| `/sc:test`          | 测试生成           | `/sc:test "单元测试"`              | ✅ 生成代码测试       |
| `/sc:improve`       | 代码优化           | `/sc:improve "性能优化"`           | ✅ 生成代码改进       |
| `/sc:security`      | 安全检查           | `/sc:security "漏洞扫描"`          | ✅ 生成代码审计       |
| `/sc:document`      | 文档生成           | `/sc:document "API文档"`           | ✅ 生成代码文档       |

---

**注意**: 本指南基于最新版本的上游项目和 CodeGen + PRP 集成版编写，如遇到版本兼容性问题，请参考上游项目的官方文档或使用更新脚本同步到最新版本。

**版本**: v2.0.0 (CodeGen + PRP 集成版)
**最后更新**: 2024 年 1 月 22 日
**维护者**: JeecgBoot AI 集成团队
