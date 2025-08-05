# ContextDev: AI Programming Methodology System

**Context Engineering + Chain of Thought (CoT) 驱动的 AI 原生开发方法论**

专为 JeecgBoot 3.8.1+框架设计的 AI 编程系统，基于 Context Engineering 理论和 CoT 推理链，通过 MCP (Model Context Protocol) 工具集成，实现从需求理解到测试验证的完整 AI 驱动开发生命周期。

## 🧠 核心方法论

### 🔗 Context Engineering + CoT 推理链

**AI 原生开发流程**: `需求理解 → 分析推理 → 设计思考 → 架构决策 → 任务分解 → 实施生成 → 测试验证`

- **agent-1 (Context 基线师)**: Context 基线建立 + 领域知识构建 + 上下文管理
- **agent-2 (需求推理师)**: EARS 需求分析 + BDD 场景设计 + CoT 业务推理
- **agent-3 (设计思考师)**: 需求可视化 + 交互设计推理 + 原型生成
- **agent-4 (架构推理师)**: 技术架构 CoT 推理 + 设计决策链 + 组件设计
- **agent-5 (实施推理师)**: 任务分解 CoT + 代码生成策略 + 实施推理
- **agent-6 (验证推理师)**: 测试策略推理 + 质量保证 CoT + 验证设计

### 🛠️ AI 编程技术栈

- **Context Engineering**: 上下文工程和领域知识管理
- **CoT Reasoning**: 思维链推理和决策追溯
- **MCP Integration**: Model Context Protocol 工具集成
- **EARS Compliance**: 结构化需求表达标准
- **BDD Specification**: 行为驱动开发规范

### 🗂️ AI 编程方法论架构

```
ContextDev/
├── agents/                         # AI推理Agent定义
│   ├── baseline-manager.md         # Context基线师
│   ├── requirements-analyst.md     # 需求推理师
│   ├── prototype-designer.md       # 设计思考师
│   ├── system-architect.md         # 架构推理师
│   ├── code-developer.md           # 实施推理师
│   └── quality-tester.md           # 验证推理师
├── templates/                      # Context Engineering模板
│   ├── 01-baseline/               # Context基线
│   ├── 02-requirements/           # EARS需求推理
│   ├── 03-prototype/              # 设计思考
│   ├── 04-architecture/           # 架构推理
│   ├── 05-development/            # 实施推理
│   └── 06-testing/                # 验证推理
└── README.md                      # AI编程方法论说明
```

### 🔗 AI 推理协作链

**Context Engineering + 推理流程**:

```
Context基线 → 需求推理 → 设计思考 → 架构推理 → 实施推理 → 验证推理
   ↓           ↓          ↓          ↓          ↓          ↓
领域知识构建 → EARS+BDD → 交互设计 → 技术决策 → 代码生成 → 质量保证
```

**文件命名格式**: `[SYSTEM]-[MODULE]-[TIMESTAMP]-[AGENT]-[TITLE].yaml`

**示例**:

- `HAIR-CUSTOMER-20250804143000-REQ-客户信息管理.yaml`
- `HAIR-CUSTOMER-20250804143000-PROTO-客户信息管理.yaml`
- `HAIR-CUSTOMER-20250804143000-ARCH-客户信息管理.yaml`
- `HAIR-CUSTOMER-20250804143000-DEV-客户信息管理.yaml`
- `HAIR-CUSTOMER-20250804143000-TEST-客户信息管理.yaml`

### 🎯 Context Engineering 存储结构

```
AIGC/
├── context_base_[SYSTEM].yaml                    # Context基线和领域知识
├── reasoning_baseline_[SYSTEM]_[MODULE].yaml     # 推理基线和上下文
└── [SYSTEM]_[MODULE]/
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-REQ-[TITLE].yaml    # EARS需求推理
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-PROTO-[TITLE].yaml  # 设计思考
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-ARCH-[TITLE].yaml   # 架构推理
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-DEV-[TITLE].yaml    # 实施推理
    └── [SYSTEM]-[MODULE]-[TIMESTAMP]-TEST-[TITLE].yaml   # 验证推理
└── CONTEXT-KNOWLEDGE/
    ├── domain-knowledge.yaml                     # 领域知识库
    └── reasoning-patterns.yaml                   # 推理模式库
```

## 🚀 AI 编程方法论快速开始

### 1. Context Engineering 初始化

```bash
# 建立Context基线和领域知识
cp templates/01-baseline/context_base_template.yaml AIGC/context_base_[SYSTEM].yaml

# 建立推理基线和上下文
cp templates/01-baseline/reasoning_baseline_template.yaml AIGC/reasoning_baseline_[SYSTEM]_[MODULE].yaml
```

### 2. AI 推理协作链执行

```bash
# Step 1: Context基线师 - 领域知识构建
使用 templates/01-baseline/context_base_template.yaml

# Step 2: 需求推理师 - EARS需求分析 + 推理链
使用 templates/02-requirements/requirement_template.yaml

# Step 3: 设计思考师 - 交互设计推理
使用 templates/03-prototype/prototype_template.yaml

# Step 4: 架构推理师 - 技术架构推理
使用 templates/04-architecture/architecture_template.yaml

# Step 5: 实施推理师 - 任务分解推理 + 代码生成
使用 templates/05-development/development_template.yaml

# Step 6: 验证推理师 - 测试策略推理
使用 templates/06-testing/testing_design_template.yaml
```

### 3. MCP 工具集成和 JeecgBoot 适配

- **MCP Protocol**: Model Context Protocol 工具链集成
- **Context Retrieval**: 智能上下文检索和知识管理
- **CoT Reasoning**: 思维链推理和决策追溯
- **EARS Compliance**: 结构化需求表达自动化
- **BDD Generation**: 行为驱动场景自动生成
- **JeecgBoot CodeGen**: 基于推理结果的代码自动生成

## 🧠 AI 编程方法论特性

### 🔗 Context Engineering 核心

- **领域知识管理**: 构建和维护领域特定的知识图谱
- **上下文工程**: 智能上下文构建和推理链管理
- **推理模式库**: 可复用的推理模式和决策模板
- **知识追溯**: 完整的推理链追溯和决策依据记录

### 🧩 推理增强

- **多层推理**: 业务理解 → 技术分析 → 实施决策的递进推理
- **决策透明**: 每个技术决策都有明确的推理过程和依据
- **质量保证**: 推理质量评分和一致性验证机制
- **协作传递**: Agent 间推理结论的无缝传递和继承

### 🛠️ AI 原生工具链

- **MCP 集成**: 原生支持 Model Context Protocol 工具生态
- **EARS 自动化**: 自动化需求结构化表达和分类
- **BDD 生成**: 基于推理的行为驱动场景自动生成
- **代码推理**: 从架构推理到代码生成的完整链路

## 🎯 AI 编程适用场景

- **AI 驱动开发**: 基于 AI 推理和 Context Engineering 的原生开发方法论
- **复杂业务分析**: 需要深度推理和决策追溯的复杂业务系统
- **知识密集型应用**: 依赖领域知识和专家推理的应用开发
- **标准化 AI 协作**: 需要标准化 AI 协作流程的团队和项目

## 📚 方法论架构

- **agents/**: AI 推理 Agent 定义和推理规范
- **templates/**: Context Engineering 模板和推理链模板
- **README.md**: AI 编程方法论说明和实施指南

---

**方法论版本**: v6.0
**Context Engineering**: 基于上下文工程理论
**Reasoning Integration**: 完整思维链推理集成
**MCP Compatible**: Model Context Protocol 兼容
**更新**: 2025-08-05
