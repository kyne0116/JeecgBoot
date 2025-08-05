# ContextDev: AI Programming Methodology System

**Context Engineering + Chain of Thought (CoT) 驱动的 AI 原生开发方法论**

专为 JeecgBoot 3.8.1+框架设计的 AI 编程系统，基于 Context Engineering 理论和 CoT 推理链，通过 A2A (Agent-to-Agent) 协议集成，实现从需求理解到代码生成的完整 AI 驱动开发生命周期。

## 📚 文档导航

- **[使用指南](ContextDev_Usage_Guide.md)** - 详细的使用方法和示例
- **[A2A 协议指南](A2A_Protocol_Guide.md)** - A2A 协议规范、集成实施和使用说明
- **[命名规范](naming_convention.md)** - 代码和文档命名规范

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

## 📖 上手指南

ContextDev 系统支持两种主要使用场景，根据用户需求的明确程度选择合适的工作流程：

### 🔍 场景 1：探索式需求分析场景

**适用情况**：

- 用户提出宽泛的系统建设目标（如"我想做一个电商系统"、"需要一个客户管理系统"）
- 业务需求不够明确，需要进一步澄清和细化
- 商业目标和功能范围需要确认和界定

**工作流程**：

```
需求探索 → 商业目标确认 → 系统功能范围界定 → 需求基线建立 → 6-Agent协作链执行
```

**操作步骤**：

1. **启动需求探索** (agent-1 主导)

   ```
   用户输入: "我想做一个电商系统"
   agent-1 响应:
   - 引导用户明确商业目标
   - 询问目标用户群体
   - 了解核心业务流程
   - 确认技术约束条件
   ```

2. **商业目标确认** (agent-1 + agent-2 协作)

   ```
   确认内容:
   - 业务价值和盈利模式
   - 核心功能优先级
   - 用户体验期望
   - 系统规模和性能要求
   ```

3. **功能范围界定** (agent-2 主导)

   ```
   输出内容:
   - 核心功能清单
   - 功能边界定义
   - 实施优先级排序
   - 技术可行性评估
   ```

4. **需求基线建立** (agent-1 完成)

   ```
   生成文档:
   - context_base_[SYSTEM].yaml
   - reasoning_baseline_[SYSTEM]_[MODULE].yaml
   ```

5. **6-Agent 协作链执行**
   ```
   按标准流程执行: agent-2 → agent-3 → agent-4 → agent-5 → agent-6
   ```

**示例交互流程**：

```
用户: "我想做一个电商系统"

agent-1:
"我来帮您明确电商系统的具体需求。请告诉我：
1. 您的目标客户群体是什么？(B2B/B2C/C2C)
2. 主要销售什么类型的商品？
3. 预期的用户规模和交易量？
4. 是否需要移动端支持？
5. 有哪些特殊的业务流程要求？"

用户: "主要做B2C，销售数码产品，预期1000+用户，需要手机APP"

agent-1:
"基于您的描述，我为您规划一个数码产品B2C电商系统。
核心功能包括：商品管理、订单处理、用户管理、支付集成、移动端支持。
接下来我将建立系统基线，然后启动详细的需求分析..."
```

**预期输出**：

- 明确的商业目标和功能范围
- 完整的系统基线文档
- 详细的需求分析文档
- 后续的架构设计和实施方案

### ✅ 场景 2：明确需求实施场景

**适用情况**：

- 用户提供详细的系统建设目标和具体功能需求
- 业务需求清晰明确，功能范围已确定
- 可以直接进行技术实施规划

**工作流程**：

```
需求理解 → 文档架构预览 → 内容摘要确认 → 6-Agent协作链执行
```

**操作步骤**：

1. **需求理解** (agent-2 主导)

   ```
   处理内容:
   - 解析用户提供的详细需求
   - 识别核心业务实体和流程
   - 确认技术约束和集成要求
   ```

2. **文档架构预览** (agent-1 支持)

   ```
   生成预览:
   - 系统模块划分
   - 文档结构规划
   - 协作链执行计划
   ```

3. **内容摘要确认** (用户确认)

   ```
   确认内容:
   - 需求理解的准确性
   - 系统架构的合理性
   - 实施计划的可行性
   ```

4. **6-Agent 协作链执行**
   ```
   完整执行: agent-1 → agent-2 → agent-3 → agent-4 → agent-5 → agent-6
   ```

**示例交互流程**：

```
用户: "我需要开发一个培训管理系统，包含课程管理、学员管理、考试系统、证书颁发等功能，基于JeecgBoot框架，支持多租户"

agent-2:
"我理解您需要开发一个培训管理系统，核心功能包括：
- 课程管理：课程创建、分类、排课
- 学员管理：注册、学习进度跟踪
- 考试系统：试题管理、在线考试、成绩统计
- 证书颁发：证书模板、自动颁发
- 多租户支持：数据隔离、权限管理

技术栈：JeecgBoot + Vue3 + MySQL
是否确认开始详细的需求分析和架构设计？"

用户: "确认，请开始"

agent-2: "开始执行6-Agent协作链，为您生成完整的技术实施方案..."
```

**预期输出**：

- 标准化的需求分析文档
- 完整的系统架构设计
- 详细的开发实施计划
- 全面的测试验证方案

### 🎯 场景选择指南

**选择场景 1 的情况**：

- 需求描述少于 50 字
- 缺少具体功能描述
- 没有明确的技术要求
- 需要商业模式咨询

**选择场景 2 的情况**：

- 需求描述超过 100 字
- 包含具体功能清单
- 明确技术栈和约束
- 有清晰的业务流程

### 🚀 快速开始建议

1. **准备阶段**：明确您的需求类型（探索式 vs 明确式）
2. **选择场景**：根据需求明确程度选择合适的工作流程
3. **启动协作**：按照对应场景的操作步骤开始
4. **跟踪进度**：关注每个 Agent 的输出和质量标准
5. **验证结果**：确保最终输出符合预期目标

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
