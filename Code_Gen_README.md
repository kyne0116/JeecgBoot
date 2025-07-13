# JeecgBoot 表单工作流自动化工具 v2.0

## 📋 概述

本工具提供完整的 JeecgBoot 表单代码生成解决方案，支持智能模块管理和自动化代码生成。

## 🚀 核心功能

### 1. 智能模块管理

- 自动检测 `jeecg-module-{系统名}` 是否存在
- 如不存在，自动使用 Maven archetype 创建新模块
- 自动更新主项目和启动项目的 pom.xml 配置

### 2. 完整工作流执行

- 系统登录获取 Token
- 在线表单创建
- 数据库结构同步
- 完整 CRUD 代码生成

### 3. AI 智能助手支持

- 基于 LangGPT 的智能需求分析
- 自动识别业务系统类型
- 智能表结构设计

## 📁 文件结构

```
├── Code_Gen_Guide.py              # 🚀 主执行脚本
├── Code_Gen_Agent.md              # 🤖 AI智能助手提示词
├── Code_Gen_Guide.md              # 📚 详细使用文档
├── Code_Gen_Config.json           # ⚙️ 主配置文件
├── Code_Gen_Guide.json           # 📋 基础模板文件
├── Code_Gen_field_templates.json # 🔧 字段类型模板库
└── example_training_config.json  # 📝 示例配置文件
```

## 🚀 快速开始

### 方式 1: AI 智能助手（推荐）

1. 将 `Code_Gen_Agent.md` 作为系统提示词输入到 AI 助手
2. 用自然语言描述业务需求
3. AI 助手自动完成整个流程

**示例对话**：

```
用户: "我需要创建员工培训记录表，包含培训名称、时间、参与人员、效果评估等字段"

AI助手将：
1. 识别为人力资源系统(hrms)
2. 检查jeecg-module-hrms模块是否存在
3. 如不存在，自动创建Maven模块
4. 生成配置文件并执行代码生成
```

### 方式 2: 直接使用脚本

```bash
# 系统诊断
python Code_Gen_Guide.py --test

# 指定系统名称执行
python Code_Gen_Guide.py --system-name hrms --form-config example_training_config.json

# 验证配置
python Code_Gen_Guide.py --validate
```

## 📋 命令行参数

### 主要参数

- `--system-name` / `-s`：指定业务系统名称（hrms、crm、scm、oa、finance）
- `--form-config` / `-f`：指定表单配置文件路径
- `--test`：运行系统诊断测试
- `--validate`：仅验证配置，不执行工作流
- `--skip-module-management`：跳过模块管理（使用现有配置）

### 使用示例

```bash
# 创建人力资源系统的员工表
python Code_Gen_Guide.py --system-name hrms --form-config employee_config.json

# 创建客户管理系统的客户表
python Code_Gen_Guide.py --system-name crm --form-config customer_config.json

# 跳过模块管理，直接使用现有配置
python Code_Gen_Guide.py --skip-module-management --form-config config.json
```

## 🎯 支持的业务系统

1. **hrms** - 人力资源管理系统

   - 关键词：员工、人事、薪资、考勤、招聘、培训、绩效

2. **crm** - 客户关系管理系统

   - 关键词：客户、销售、合同、商机、服务、支持

3. **scm** - 供应链管理系统

   - 关键词：供应商、采购、库存、物流、仓储

4. **oa** - 办公自动化系统

   - 关键词：审批、流程、公告、会议、文档

5. **finance** - 财务管理系统
   - 关键词：财务、会计、成本、预算、报表

## ⚠️ 注意事项

### 环境要求

- 确保 Maven 已正确安装并配置环境变量
- 确保 JeecgBoot 服务正常运行
- 在 jeecg-boot 项目根目录下执行命令

### 重要规则

- `Code_Gen_Guide.json` 是永久模板文件，请勿修改
- 业务配置文件必须保持 7 个系统字段不变
- 表名必须使用 `us_` 前缀
- 业务字段的 orderNum 从 7 开始

### 自动化功能

- **智能系统识别**：基于关键词匹配自动识别业务系统类型
- **模块存在性检查**：自动检查 `jeecg-boot/jeecg-module-{系统名}` 是否存在
- **Maven 模块创建**：使用非交互模式自动创建新模块
- **项目配置更新**：自动更新主项目和启动项目的 pom.xml 文件
- **跨平台兼容**：支持 Windows/Linux/Mac 平台
- **错误处理**：完整的异常捕获和超时控制机制

## 📚 详细文档

- [Code_Gen_Guide.md](Code_Gen_Guide.md) - 完整使用文档
- [Code_Gen_Agent.md](Code_Gen_Agent.md) - AI 智能助手提示词

## 🎉 版本更新

### v2.0 重构亮点

- **文档专注说明**：md 文档专注于使用说明和指导
- **脚本专注执行**：py 脚本专注于自动化执行
- **智能模块管理**：自动检查和创建业务模块
- **简化参数**：优化命令行参数，更易使用
- **清理机制**：自动清理临时文件，保持环境整洁

### 技术实现亮点

- **智能识别算法**：基于关键词匹配的业务系统识别
- **非交互模式**：Maven archetype 使用 `-DinteractiveMode=false`
- **XML 安全处理**：使用 ElementTree 解析和修改 pom.xml
- **超时控制**：Maven 命令执行 5 分钟超时保护
- **跨平台兼容**：自动检测操作系统，适配不同平台
- **完整错误处理**：异常捕获、错误报告、流程终止机制

---

**开始使用**: 现在就可以通过 AI 助手或直接使用脚本来创建 JeecgBoot 表单代码！
