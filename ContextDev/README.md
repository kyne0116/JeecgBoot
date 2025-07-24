# ContextDev - JeecgBoot AI 增强开发 v3.0 (精简优化版)

## 📋 核心理念

**小而全，少而精，实用** - 专为 6 个模板文件的双 PRP 工作流程设计，实现工程级软件开发最佳实践。

## 🏗️ 核心功能

- **6 个核心模板**：完整开发生命周期管理体系
- **双 PRP 工作流**：`/jeecg-generate-prp` + `/jeecg-execute-prp` 完整开发流程
- **CodeGen 深度集成**：与 JeecgBoot CodeGen 系统无缝对接
- **示例代码集成**：自动复制 JeecgBoot 示例代码到 `PRPs/examples/`
- **符号链接机制**：项目根目录 `CLAUDE.md` 自动链接到 `PRPs/CLAUDE.md`
- **项目级别配置**：不影响全局设置的独立 AI 环境

## 🚀 快速开始

### 1. 安装部署

```bash
# 完整安装（推荐）
bash ContextDev/jeecg-ai-setup.sh

# 验证安装
bash ContextDev/jeecg-ai-setup.sh --verify
```

### 2. 双 PRP 工作流使用

```bash
# 步骤1: 生成需求文档
/jeecg-generate-prp 客户关系管理系统，包含客户信息管理、销售跟踪功能

# 步骤2: 执行需求实现
/jeecg-execute-prp projectDocs/REQUIREMENTS_customer-relationship.md
```

## 📁 完整文件结构

```
ContextDev/
├── jeecg-ai-setup.sh             # 主安装脚本 v2.0 (增强版)
├── jeecg-ai-update.sh            # 更新维护脚本
├── jeecg-ai-config.json          # 核心配置文件
├── jeecg-generate-prp-command.md # 生成命令模板
├── jeecg-execute-prp-command.md  # 执行命令模板
├── examples/                     # JeecgBoot示例代码源
│   └── jeecgboot/               # JeecgBoot完整示例代码
│       ├── backend/             # 后端Java代码示例
│       └── frontend/            # 前端Vue3代码示例
└── templates/                   # 6个核心模板
    ├── REQUIREMENTS_JEECGBOOT.md # 需求文档模板
    ├── DESIGN_JEECGBOOT.md       # 系统设计模板
    ├── PLANNING_JEECGBOOT.md     # 项目规划模板
    ├── TASK_JEECGBOOT.md         # 任务管理模板
    ├── CLAUDE_JEECGBOOT.md       # AI编程规范
    └── TESTING_JEECGBOOT.md      # 测试计划模板
```

## 🏗️ 技术架构与实现原理

### 📋 PRPs 目录结构

安装脚本会在项目根目录创建完整的 AI 工作环境：

```
PRPs/                              # AI工作目录
├── CLAUDE.md                      # 项目级别AI配置（实际文件）
├── examples/                      # 示例代码集合
│   └── jeecgboot/                # JeecgBoot示例代码
│       ├── backend/              # 后端示例（Entity、Controller、Service、Mapper）
│       └── frontend/             # 前端示例（Vue3组件、API、路由）
├── templates/                     # AI编程模板集合
│   ├── CLAUDE_JEECGBOOT.md       # AI编程规范
│   ├── REQUIREMENTS_JEECGBOOT.md # 需求分析模板
│   ├── TASK_JEECGBOOT.md         # 任务管理模板
│   └── ...                       # 其他模板文件
├── codegen_commands.json          # CodeGen命令配置
├── active/                        # 活跃任务目录
└── completed/                     # 已完成任务目录
```

### 🔗 符号链接机制

为了让 Claude Code 能够自动检测项目级别的 AI 配置，安装脚本会创建符号链接：

```bash
# 项目根目录
CLAUDE.md -> PRPs/CLAUDE.md        # 符号链接，Claude Code检测点

# 实际配置文件位置
PRPs/CLAUDE.md                     # 包含完整的JeecgBoot AI编程规范
```

**优势**：

- ✅ Claude Code 在项目根目录即可自动检测配置
- ✅ 实际配置文件集中在 PRPs/ 目录便于管理
- ✅ 符号链接已添加到 .gitignore，不影响版本控制

### 📚 示例代码集成逻辑

#### 复制流程

1. **源码检测**: 脚本检查 `ContextDev/examples/` 是否存在
2. **目录创建**: 在 `PRPs/examples/` 创建目标目录结构
3. **完整复制**: 复制所有示例代码文件，保持目录结构
4. **权限设置**: 自动设置正确的文件权限（644/755）
5. **索引生成**: 创建 `INDEX.json` 文件，描述示例代码结构

#### AI 集成机制

**模板引用**: 所有 AI 编程模板都包含示例代码引用指导

```yaml
# 在模板文件中的引用
- examples: PRPs/examples/jeecgboot/ # JeecgBoot示例代码集合
```

**开发指导**: AI 在进行代码开发前会自动参考示例代码

- 实体设计参考: `backend/entity/SysUser.java`
- 控制器参考: `backend/controller/SysUserController.java`
- 前端组件参考: `frontend/views/system/user/`

### ⚙️ CodeGen 系统集成

#### 配置文件生成

安装脚本自动生成 `PRPs/codegen_commands.json`，包含：

```json
{
  "commands": {
    "/sc:jeecg-analyze": "基于CodeGen AI代理的业务需求分析",
    "/sc:jeecg-config": "智能生成JeecgBoot JSON配置文件",
    "/sc:codegen": "执行完整CodeGen工作流"
  }
}
```

#### 工作流集成

1. **需求分析**: 使用 Code_Gen_Agent.md 解析业务需求
2. **配置生成**: 基于示例代码生成标准化配置
3. **代码生成**: 调用 Code_Gen_Guide.py 执行生成流程
4. **质量验证**: 对比示例代码验证生成质量
   └── TESTING_JEECGBOOT.md # 测试计划模板

````

## ⚡ 核心命令

### `/jeecg-generate-prp` - 智能需求文档生成

- **智能需求分类**：自动识别简单 CRUD vs 复杂业务需求
- **CodeGen 配置生成**：自动提取 MODULE_NAME、ENTITY_NAME、TABLE_NAME
- **质量保证**：8+/10 置信度标准

### `/jeecg-execute-prp` - 智能需求文档执行

- **四阶段流程**：文档分析 → 环境验证 → 代码生成 → 质量验证
- **CodeGen 自动化**：智能执行 Code_Gen_Guide.py 完整工作流
- **质量保证**：9+/10 置信度标准

## 🎯 技术特点

**精简化**：v3.0 去除复杂依赖，专注核心功能
**规范化**：严格遵循 JeecgBoot 架构约束和命名规范
**自动化**：从文档生成到代码实现的完整自动化链路
**工程级**：高质量标准、完整错误处理、详细执行报告

## 🏗️ 核心架构与底层机制

### 📝 CLAUDE.md 文件生成机制

#### **生成流程**

```mermaid
graph TD
    A[jeecg-ai-setup.sh脚本] --> B[setup_project_claude_config函数]
    B --> C{检查模板文件}
    C -->|存在| D[ContextDev/templates/CLAUDE_JEECGBOOT.md]
    C -->|不存在| E[创建基础配置]
    D --> F[复制到PRPs/CLAUDE.md]
    E --> F
    F --> G[验证配置完整性]
    G --> H[Claude Code自动识别]
````

#### **核心机制**

- **模板复制机制**：从 `ContextDev/templates/CLAUDE_JEECGBOOT.md` 复制到 PRPs/CLAUDE.md
- **项目级隔离**：仅在项目根目录生效，不影响用户全局配置
- **内容验证**：通过 grep 检查是否包含"JeecgBoot"关键字确保配置正确
- **自动识别**：Claude Code 启动时自动读取项目根目录的 CLAUDE.md

### 🔗 6 个模板文件引用关系与作用

#### **核心引用链**

```markdown
CLAUDE.md (项目主配置)
↓ 第 340-344 行定义工作流
├── REQUIREMENTS_JEECGBOOT.md → 阶段 2: 需求文件生成
├── PLANNING_JEECGBOOT.md → 阶段 3: 架构设计  
 ├── DESIGN_JEECGBOOT.md → 阶段 4: 设计文档生成
├── TASK_JEECGBOOT.md → 阶段 6: 任务清单生成
└── TESTING_JEECGBOOT.md → 质量保证阶段
```

#### **模板依赖矩阵**

| 模板文件                      | 引用关系                 | 应用时机 | 核心作用                      |
| ----------------------------- | ------------------------ | -------- | ----------------------------- |
| **CLAUDE_JEECGBOOT.md**       | 被所有模板引用           | 全流程   | AI 行为规范、CodeGen 强制约束 |
| **REQUIREMENTS_JEECGBOOT.md** | 工作流入口               | 阶段 2   | 需求分析、CodeGen 配置生成    |
| **DESIGN_JEECGBOOT.md**       | 依赖 REQUIREMENTS        | 阶段 4   | 系统架构、技术方案设计        |
| **TASK_JEECGBOOT.md**         | 依赖 DESIGN+REQUIREMENTS | 阶段 6   | 任务分解、进度跟踪管理        |
| **PLANNING_JEECGBOOT.md**     | 关联所有模板             | 阶段 3   | 项目规划、里程碑制定          |
| **TESTING_JEECGBOOT.md**      | 贯穿全流程               | 质量保证 | 测试策略、验证门槛            |

#### **双 PRP 命令的模板调用机制**

```bash
# 生成阶段 (/jeecg-generate-prp)
用户需求 → REQUIREMENTS_JEECGBOOT.md模板 → projectDocs/REQUIREMENTS_*.md

# 执行阶段 (/jeecg-execute-prp)
需求文档 → CLAUDE.md规范决策 → 其他模板协同应用
    ├── 简单CRUD → CodeGen系统
    └── 复杂业务 → DESIGN+TASK+TESTING模板
```

### ⚙️ .claude/commands/目录生成规则

#### **目录结构生成**

```bash
# setup_claude_commands()函数执行流程
.claude/commands/
├── jeecg-generate-prp.md    # 从ContextDev/jeecg-generate-prp-command.md复制
├── jeecg-execute-prp.md     # 从ContextDev/jeecg-execute-prp-command.md复制
└── README.md                # 脚本自动生成(第623-756行)
```

#### **文件生成规则**

```markdown
**jeecg-generate-prp.md**:

- 源文件: ContextDev/jeecg-generate-prp-command.md
- 生成方式: 直接复制或内置模板生成(第 418-578 行)
- 核心功能: 智能需求分类、CodeGen 配置提取、质量验证

**jeecg-execute-prp.md**:

- 源文件: ContextDev/jeecg-execute-prp-command.md
- 生成方式: 直接复制(第 602-603 行)
- 核心功能: 四阶段执行、环境验证、代码生成

**README.md**:

- 生成方式: cat << 'EOF' 完全自动生成
- 内容来源: 脚本内置标准化说明
- 自动同步: 与实际命令功能保持一致
```

### 🔧 jeecg-ai-setup.sh 核心底层逻辑

#### **安装执行序列**

```bash
main() {
    check_prerequisites         # 环境检查(Python/Node.js/项目结构)
    setup_project_structure    # 创建目录结构
    deploy_prp_commands        # 部署双PRP命令系统
    setup_project_claude_config # 配置项目级CLAUDE.md
    verify_installation        # 验证安装结果
}
```

#### **关键变量体系**

```bash
# 核心路径变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONTEXT_DEV_DIR="$PROJECT_ROOT/ContextDev"
PROJECT_DOCS_DIR="$PROJECT_ROOT/projectDocs"
CLAUDE_COMMANDS_DIR="$PROJECT_ROOT/.claude/commands"
```

#### **核心配置逻辑**

```markdown
**setup_project_claude_config()核心逻辑**:

1. 定义项目级 CLAUDE.md 路径: $PRP_WORK_DIR/CLAUDE.md
2. 检查 JeecgBoot 专用模板存在性
3. 模板复制: CLAUDE_JEECGBOOT.md → PRPs/CLAUDE.md
4. 验证配置: grep -q "JeecgBoot" CLAUDE.md
5. 错误处理: 模板不存在时退出安装

**deploy_prp_commands()核心逻辑**:

1. 创建.claude/commands 目录结构
2. 复制双 PRP 命令定义文件
3. 验证命令文件完整性
4. 记录部署状态和文件大小
```

#### **质量保证机制**

```markdown
**verify_installation()验证检查**:

- [ ] 双 PRP 命令文件存在性检查
- [ ] 项目 CLAUDE.md 配置完整性验证
- [ ] 目录结构正确性确认
- [ ] 命令系统功能可用性测试

**错误处理策略**:

- 文件不存在 → 使用内置模板创建
- 配置验证失败 → 脚本退出并报错
- 权限问题 → 提供解决方案提示
- 环境不兼容 → 详细错误信息输出
```

#### **v3.0 精简优化原理**

```markdown
**优化策略**:

- 去除 Context Engineering 和 SuperClaude 依赖
- 专注 6 个核心模板和双 PRP 工作流
- 内置所有必要模板，避免外部依赖
- 统一错误处理和验证机制

**核心保留**:

- 完整的模板文件系统(6 个核心模板)
- 双 PRP 命令系统(.claude/commands/)
- 项目级 CLAUDE.md 配置机制
- 质量保证和验证门槛脚本
```

## 📊 质量标准

- **Generate 命令**: ≥8/10 置信度，完整验证门槛脚本
- **Execute 命令**: ≥9/10 置信度，编译+功能+集成测试
- **整体成功率**: ≥95%端到端执行成功率
- **代码规范**: 100%JeecgBoot 架构规范遵循

## 🔧 维护管理

```bash
# 系统更新
bash ContextDev/jeecg-ai-update.sh

# 验证系统状态
bash ContextDev/jeecg-ai-update.sh --verify

# 重新安装（如有问题）
bash ContextDev/jeecg-ai-setup.sh
```

## 💡 设计原则

**v3.0 核心原则**：

1. **小而全**：功能完整但体积精简
2. **少而精**：文件数量少但质量高
3. **实用**：专注实际开发需求，去除冗余功能

**优化成果**：

- 安装脚本：1377 行 → 195 行 (减少 86%)
- 配置文件：266 行 → 71 行 (减少 73%)
- 更新脚本：401 行 → 206 行 (减少 49%)
- 保持 6 个核心模板的完整性和质量

## 🔍 故障排除

**常见问题**：

- **命令未找到**：运行 `bash ContextDev/jeecg-ai-setup.sh --verify`
- **CodeGen 连接失败**：确保 `python3 CodeGen/Code_Gen_Guide.py --test-connection` 通过
- **环境验证失败**：检查 Maven、Java、Node.js 版本

**获取支持**：

- 查看执行日志：`projectDocs/EXECUTION_LOG_*.md`
- 检查配置文件：`jeecg-ai-config.json`
- 验证系统状态：`bash ContextDev/jeecg-ai-update.sh --verify`

---

**JeecgBoot AI 增强开发 v3.0 - 精简而强大！** 🚀
