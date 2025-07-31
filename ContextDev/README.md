# JeecgBoot AI Agent协作开发模板

基于JeecgBoot 3.5.0+框架的AI Agent协作开发模板系统，支持需求驱动的软件开发流程。

## 📋 核心功能

### 🤖 四Agent协作体系
- **Agent-A (需求分析师)**: EARS结构化需求分析 + BDD场景设计
- **Agent-B (架构设计师)**: 技术架构设计 + CodeGen配置
- **Agent-C (开发工程师)**: TBDWBS任务分解 + 工作量估算
- **Agent-D (测试工程师)**: BTDTP测试设计 + 质量保证

### 📐 四大协议标准
- **EARS协议**: 五种需求类型的结构化表达
- **BDD协议**: 四种场景类型的行为驱动描述
- **TBDWBS协议**: Given-When-Then-But任务分解
- **BTDTP协议**: 四维测试空间映射

### 🗂️ 模板结构

```
templates/
├── 01-baseline/                    # 基线管理
│   ├── requirement_baseline_template.yaml
│   └── system_base_info_template.yaml
├── 02-requirements/                # 需求分析
│   └── requirement_template.yaml
├── 03-architecture/                # 架构设计
│   └── architecture_design_template.yaml
├── 04-development/                 # 开发任务
│   └── development_task_template.yaml
├── 05-testing/                     # 测试设计
│   └── testing_design_template.yaml
└── 文件命名规范指导v3.0.md           # 命名规范
```

### 📁 文件命名规范

**格式**: `系统功能模块-子功能模块-年月日时分秒-环节代码-需求标题`

**示例**:
- `ECOM-PROD-20250731143000-REQ-产品管理功能.yaml`
- `ECOM-PROD-20250731143000-ARCH-产品管理功能.yaml`
- `ECOM-PROD-20250731143000-DEV-产品管理功能.yaml`
- `ECOM-PROD-20250731143000-TEST-产品管理功能.yaml`

### 🎯 目录组织

每个需求形成独立目录，包含完整的四环节文档：
```
example/
├── L0-system-base/
│   └── system_base_info.yaml
├── ECOM-PROD-20250731143000-产品管理功能/
│   ├── ECOM-PROD-20250731143000-REQ-产品管理功能.yaml
│   ├── ECOM-PROD-20250731143000-ARCH-产品管理功能.yaml
│   ├── ECOM-PROD-20250731143000-DEV-产品管理功能.yaml
│   └── ECOM-PROD-20250731143000-TEST-产品管理功能.yaml
└── SHARED-COMPONENTS/
    ├── common-entities.yaml
    └── shared-services.yaml
```

## 🚀 使用流程

### 1. 系统基础信息设置
使用 `system_base_info_template.yaml` 配置系统基础信息和技术栈。

### 2. 需求基线管理
使用 `requirement_baseline_template.yaml` 建立需求基线和套件管理。

### 3. Agent协作流程
1. **Agent-A**: 使用需求模板进行EARS需求分析和BDD场景设计
2. **Agent-B**: 基于需求输出进行架构设计和CodeGen配置
3. **Agent-C**: 基于需求和设计进行任务分解和工作量估算
4. **Agent-D**: 基于前三环节输出进行测试设计和质量规划

### 4. 代码生成集成
- 支持JeecgBoot标准CodeGen功能
- 自动生成CRUD操作和页面
- 集成数据字典和权限控制
- 支持自定义业务逻辑扩展

## 📖 技术特性

### JeecgBoot集成
- **前端**: Vue 3 + Ant Design Vue + TypeScript
- **后端**: Spring Boot + MyBatis Plus + Java 17
- **代码生成**: 基于模板的自动化代码生成
- **权限管理**: Spring Security + JWT + Apache Shiro

### 质量保证
- 100%需求追溯性
- 完整的四层测试覆盖
- 自动化测试支持
- 持续集成友好

### 协作特性
- 需求驱动的文件组织
- 支持并行开发
- 版本化管理
- 跨需求依赖管理

## 📋 快速开始

1. 根据项目需求修改系统基础信息模板
2. 建立需求基线和套件结构
3. 使用Agent协作流程开发具体需求
4. 集成JeecgBoot CodeGen生成基础代码
5. 基于测试设计进行质量验证

## 📚 相关文档

详细的文件命名规范和使用指导请参考 `文件命名规范指导v3.0.md`。

---

**版本**: v3.0  
**更新日期**: 2025-07-31  
**兼容框架**: JeecgBoot 3.5.0+