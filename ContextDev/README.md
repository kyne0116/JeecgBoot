# JeecgBoot AI Agent 协作开发系统

高效的 AI Agent 协作开发系统，专为 JeecgBoot 3.8.1+框架优化，实现标准化的 4-Agent 协作流程。

## 🎯 系统特性

### 🤖 4-Agent 协作链

- **Agent-A (需求分析师)**: EARS 需求分析 + BDD 场景设计
- **Agent-B (架构设计师)**: 技术架构设计 + 数据模型设计
- **Agent-C (开发工程师)**: 任务分解 + 代码生成配置
- **Agent-D (测试工程师)**: 测试设计 + 质量验证

### 📐 标准化协议

- **EARS 协议**: 结构化需求表达
- **BDD 协议**: 行为驱动场景设计
- **架构协议**: 技术架构标准化
- **测试协议**: 全栈测试覆盖

### 🗂️ 系统架构

```
ContextDev/
├── agents/                         # AI Agent定义
│   ├── requirements_analyst.md     # Agent-A
│   ├── system_architect.md         # Agent-B
│   ├── code_developer.md           # Agent-C
│   └── quality_tester.md           # Agent-D
├── templates/                      # 标准化模板
│   ├── 01-baseline/               # 系统基线
│   ├── 02-requirements/           # 需求分析
│   ├── 03-architecture/           # 架构设计
│   ├── 04-development/            # 开发任务
│   └── 05-testing/                # 测试设计
└── README.md                      # 系统说明
```

### 📁 协作流程

**4-Agent 标准协作链**:

```
Agent-A → Agent-B → Agent-C → Agent-D
需求分析 → 架构设计 → 开发任务 → 测试设计
```

**文件命名格式**: `[SYSTEM]-[MODULE]-[TIMESTAMP]-[AGENT]-[TITLE].yaml`

**示例**:

- `HAIR-CUSTOMER-20250804143000-REQ-客户信息管理.yaml`
- `HAIR-CUSTOMER-20250804143000-ARCH-客户信息管理.yaml`
- `HAIR-CUSTOMER-20250804143000-DEV-客户信息管理.yaml`
- `HAIR-CUSTOMER-20250804143000-TEST-客户信息管理.yaml`

### 🎯 存储结构

```
AIGC/
├── system_base_info_[SYSTEM].yaml
├── requirement_baseline_[SYSTEM]_[MODULE].yaml
└── [SYSTEM]_[MODULE]/
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-REQ-[TITLE].yaml
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-ARCH-[TITLE].yaml
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-DEV-[TITLE].yaml
    └── [SYSTEM]-[MODULE]-[TIMESTAMP]-TEST-[TITLE].yaml
└── SHARED-COMPONENTS/
    ├── common-entities.yaml
    └── shared-services.yaml
```

## 🚀 快速开始

### 1. 系统初始化

```bash
# 配置系统基础信息
cp templates/01-baseline/system_base_info_template.yaml AIGC/system_base_info_[SYSTEM].yaml

# 建立模块基线
cp templates/01-baseline/requirement_baseline_template.yaml AIGC/requirement_baseline_[SYSTEM]_[MODULE].yaml
```

### 2. 4-Agent 协作流程

```bash
# Step 1: Agent-A 需求分析
使用 templates/02-requirements/requirement_template.yaml

# Step 2: Agent-B 架构设计
使用 templates/03-architecture/architecture_template.yaml

# Step 3: Agent-C 开发任务
使用 templates/04-development/development_template.yaml

# Step 4: Agent-D 测试设计
使用 templates/05-testing/testing_template.yaml
```

### 3. JeecgBoot 集成

- **CodeGen 支持**: 自动生成 CRUD 操作和页面
- **数据字典**: 集成标准数据字典管理
- **权限控制**: 支持细粒度权限配置
- **业务扩展**: 支持自定义业务逻辑

## 📖 技术规范

### 🏗️ 架构标准

- **前端**: Vue 3 + Ant Design Vue + TypeScript
- **后端**: Spring Boot + MyBatis Plus + Java 17
- **数据库**: MySQL 8.0+ / PostgreSQL 12+
- **缓存**: Redis 6.0+

### 📐 协议规范

- **EARS 协议**: 结构化需求表达标准
- **BDD 协议**: Given-When-Then 场景设计
- **API 规范**: RESTful API 设计标准
- **测试规范**: 单元测试 + 集成测试 + E2E 测试

### 🎯 质量标准

- **需求覆盖率**: ≥95%
- **代码覆盖率**: ≥80%
- **API 响应时间**: ≤2 秒
- **系统可用性**: ≥99.9%

---

**版本**: v5.0
**更新日期**: 2025-08-04
**兼容框架**: JeecgBoot 3.8.1+
**维护团队**: JeecgBoot ContextDev Team
