# ContextDev - JeecgBoot AI 增强开发

## 📋 核心功能

JeecgBoot项目AI赋能开发工具集，实现从需求到代码的全自动化流程：

- **双PRP工作流**: `/jeecg-generate-prp` + `/jeecg-execute-prp` 完整开发流程
- **CodeGen深度集成**: 与JeecgBoot CodeGen系统无缝对接
- **智能环境管理**: 自动化部署和配置管理
- **企业级质量保证**: ≥95%执行成功率标准

## 🏗️ 技术架构

### 双命令协作机制
```mermaid
graph LR
    A[业务需求] --> B[/jeecg-generate-prp]
    B --> C[需求文档.md]
    C --> D[/jeecg-execute-prp]
    D --> E[完整代码实现]
    
    B --> F[智能需求分类]
    B --> G[CodeGen配置生成]
    B --> H[官方文档研究]
    
    D --> I[文档解析验证]
    D --> J[环境验证修复]
    D --> K[CodeGen自动执行]
    D --> L[质量验证报告]
```

### 四大核心增强特性
1. **智能需求分类决策引擎** (Generate)
   - 自动识别：简单CRUD vs 复杂业务需求
   - 智能选择：CodeGen路径 vs 官方文档研究路径
   - 分层策略：混合需求的优化实现方案

2. **CodeGen系统深度集成** (Generate)
   - 零容忍检查：强制使用CodeGen，禁止手动编码
   - 智能配置：自动提取MODULE_NAME、ENTITY_NAME、TABLE_NAME
   - 规范遵循：us_{module}_{entity}表命名、org.jeecg.modules包结构

3. **智能执行引擎** (Execute)
   - 四阶段流程：文档分析→环境验证→代码生成→质量验证
   - 完美继承：所有Generate命令的配置和上下文
   - 实时监控：代码生成过程和错误自动处理

4. **端到端质量保证**
   - Generate: ≥8/10置信度标准，完整验证门槛脚本
   - Execute: ≥9/10置信度标准，编译+功能+集成测试
   - 自动修复：断点续传、状态恢复、智能错误诊断

## 🚀 快速开始

### 1. 安装部署

```bash
# 完整安装（推荐）
bash ContextDev/jeecg-ai-setup.sh

# 仅部署命令
bash ContextDev/jeecg-ai-setup.sh --deploy-commands-only

# 验证安装
bash ContextDev/jeecg-ai-setup.sh --verify
```

### 2. 双PRP工作流使用

**完整开发流程**：
```bash
# 步骤1: 生成需求文档（8+/10质量标准）
/jeecg-generate-prp 客户关系管理系统，包含客户信息管理、销售跟踪、合同管理功能

# 输出: projectDocs/REQUIREMENTS_customer-relationship.md

# 步骤2: 执行需求实现（9+/10质量标准）
/jeecg-execute-prp projectDocs/REQUIREMENTS_customer-relationship.md

# 输出: 完整的前后端代码 + 执行日志
```

**业务场景示例**：
```bash
# 简单CRUD需求（自动选择CodeGen路径）
/jeecg-generate-prp 员工基本信息管理，包含增删改查功能
/jeecg-execute-prp projectDocs/REQUIREMENTS_employee-basic.md

# 复杂业务需求（自动启用官方文档研究）
/jeecg-generate-prp 财务报表系统，支持多维分析、权限分级、第三方ERP集成
/jeecg-execute-prp projectDocs/REQUIREMENTS_financial-reporting.md

# 混合需求（分层实现策略）
/jeecg-generate-prp 库存管理模块，包含商品入库出库、批次管理、预警系统
/jeecg-execute-prp projectDocs/REQUIREMENTS_inventory-management.md
```

## ⚡ 核心命令

### `/jeecg-generate-prp` - 智能需求文档生成命令
专为JeecgBoot设计的需求文档生成命令，集成智能需求分类、CodeGen配置生成、官方文档研究。

**核心特性**:
- **智能需求分类决策引擎**：自动识别简单CRUD vs 复杂业务需求
- **CodeGen系统深度集成**：零容忍违规检查，自动生成配置参数
- **官方文档智能研究**：集成context7.com最佳实践和deepwiki.com技术原理
- **质量保证机制**：8+/10置信度标准，完整验证门槛脚本

**技术实现**:
- **自动参数提取**: MODULE_NAME、ENTITY_NAME、TABLE_NAME
- **规范强制遵循**: us_{module}_{entity}表命名、org.jeecg.modules包结构
- **智能路径选择**: CodeGen路径 vs 官方文档研究路径 vs 混合策略
- **配置完整性验证**: JeecgBoot环境、CodeGen系统、项目结构验证

### `/jeecg-execute-prp` - 智能需求文档执行命令
基于需求文档的端到端代码实现命令，深度集成CodeGen系统。

**核心能力**:
- **四阶段智能执行流程**: 文档分析→环境验证→代码生成→质量验证
- **完美配置继承**: 自动继承Generate命令的所有配置和上下文
- **CodeGen系统自动化调用**: 智能执行Code_Gen_Guide.py完整工作流
- **端到端质量保证**: 9+/10置信度，编译+功能+集成测试验证

**智能特性**:
- **实时监控**: 代码生成过程监控和错误自动处理
- **自动修复**: 断点续传、状态恢复、智能错误诊断
- **完整性验证**: 后端（Entity、Controller、Service、Mapper）+ 前端（Vue组件、API、路由）
- **质量报告**: 详细执行日志和后续优化建议

## 📁 文件结构

```
ContextDev/
├── jeecg-ai-setup.sh             # 整合版主安装脚本（包含所有enhanced功能）
├── jeecg-ai-config.json          # 主配置文件（双命令详细配置）  
├── jeecg-generate-prp-command.md # 生成命令模板（242行，三大增强特性）
├── jeecg-execute-prp-command.md  # 执行命令模板（331行，四阶段流程）
├── jeecg-ai-update.sh           # 更新维护脚本
└── templates/                    # 完整PRP模板体系
    ├── REQUIREMENTS_JEECGBOOT.md # 需求文档模板
    ├── CLAUDE_JEECGBOOT.md       # AI编程规范
    ├── DESIGN_JEECGBOOT.md       # 系统设计模板
    ├── PLANNING_JEECGBOOT.md     # 项目规划模板
    ├── TASK_JEECGBOOT.md         # 任务管理模板
    └── TESTING_JEECGBOOT.md      # 测试计划模板
```

## 🎯 技术特点

**智能化**: 需求自动分析、路径智能选择、配置自动生成  
**规范化**: 严格遵循JeecgBoot架构约束和命名规范  
**自动化**: 从文档生成到代码实现的完整自动化链路  
**企业级**: 高质量标准、完整错误处理、详细执行报告

## 📊 质量标准

**Generate命令**: ≥8/10置信度，完整验证门槛脚本  
**Execute命令**: ≥9/10置信度，编译+功能+集成测试  
**整体成功率**: ≥95%端到端执行成功率  
**代码规范**: 100%JeecgBoot架构规范遵循

## 💡 最佳实践

### 需求描述优化技巧
- **简单CRUD**: 描述核心实体和基础操作，AI会自动选择CodeGen路径
- **复杂业务**: 详细描述业务流程、集成需求，AI会启用官方文档研究
- **混合需求**: 分层描述基础功能和高级特性，AI会制定分层实现策略

### 执行效率提升建议
- **预执行检查**: 确保JeecgBoot服务运行和CodeGen系统可用
- **分阶段执行**: 大型项目可拆分为多个模块分别执行
- **日志分析**: 定期查看执行日志，及时发现和解决问题

### 质量保证最佳实践
- **遵循置信度标准**: Generate≥8/10, Execute≥9/10
- **完整验证流程**: 文档→环境→代码→功能，逐步验证
- **规范严格遵循**: 表命名、包结构、权限配置必须符合JeecgBoot规范

## 🔧 故障排除

**常见问题**:
- **命令未找到**: 运行 `bash ContextDev/jeecg-ai-setup.sh --verify` 检查部署状态
- **CodeGen连接失败**: 确保 `python3 CodeGen/Code_Gen_Guide.py --test-connection` 通过
- **环境验证失败**: 检查Maven、Java、Node.js版本是否符合要求
- **生成文档不完整**: 重新运行generate命令，提供更详细的需求描述

**获取支持**:
- 查看执行日志：`projectDocs/EXECUTION_LOG_*.md`
- 检查配置文件：`jeecg-ai-config.json`
- 验证模板文件：`templates/REQUIREMENTS_JEECGBOOT.md`

---

**JeecgBoot AI 增强开发 - 让企业级开发更智能！** 🚀
