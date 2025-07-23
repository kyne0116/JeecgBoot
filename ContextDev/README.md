# ContextDev - JeecgBoot AI 赋能开发

## 📋 概述

为 JeecgBoot 项目提供 AI 赋能开发能力，整合先进的 AI 工作流和专业开发工具：

- **AI 代码生成**: 基于 JeecgBoot CodeGen 的智能代码生成
- **PRP 工作流**: 产品需求提示工作流，90%+ 成功率  
- **专业命令**: 16 个专业命令覆盖开发全流程
- **项目级配置**: 独立的项目级 AI 配置，不污染全局设置

## 🎯 核心功能

- **智能需求分析**: AI 自动分析业务需求，生成标准化设计
- **自动化代码生成**: 与 JeecgBoot CodeGen 系统深度集成
- **完整开发工作流**: 从需求到部署的全流程 AI 辅助
- **项目隔离配置**: 每个项目独立的 AI 配置环境

## 🚀 快速开始

### 1. 一键安装

```bash
# 在 JeecgBoot 项目根目录执行
chmod +x ContextDev/jeecg-ai-setup.sh
./ContextDev/jeecg-ai-setup.sh
```

### 2. 测试功能

安装完成后，在 Claude Code 中测试：

```bash
# JeecgBoot 专用 PRP 工作流（推荐）
/jeecg-generate-prp 客户管理系统需求

# 通用 PRP 工作流
/generate-prp customer-management-requirements.md
/execute-prp PRPs/customer-management.md

# SuperClaude 命令
/sc:jeecg-analyze "分析业务需求"
/sc:jeecg-config "生成配置文件"
/sc:codegen "执行代码生成"
```

## ⚡ 核心命令

### `/jeecg-generate-prp` - JeecgBoot 专用需求文档生成

**专为 JeecgBoot 设计的智能需求文档生成命令，基于 Context Engineering 最佳实践。**

**命令语法：**
```bash
/jeecg-generate-prp [需求描述]
```

**使用示例：**
```bash
# 生成客户管理系统需求文档
/jeecg-generate-prp 客户管理系统需求

# 生成库存管理模块需求文档  
/jeecg-generate-prp 库存管理模块，包含商品入库、出库、盘点功能

# 生成财务报表系统需求文档
/jeecg-generate-prp 财务报表系统，支持月度和年度报表生成
```

**核心特性：**
- 🎯 **JeecgBoot 专用优化**: 针对 JeecgBoot 平台特点进行深度定制
- 📝 **自动模板应用**: 使用 `PRPs/templates/REQUIREMENTS_JEECGBOOT.md` 作为基础模板
- 💾 **智能文件命名**: 自动保存到 `projectDocs/REQUIREMENTS_{project-name}.md`
- 🔧 **CodeGen 深度集成**: 生成的需求文档直接兼容 CodeGen 系统
- ✅ **环境验证门槛**: 包含完整的 JeecgBoot 环境验证脚本

**与 CodeGen 系统的关系：**
1. **需求输入阶段**: 使用 `/jeecg-generate-prp` 生成标准化需求文档
2. **配置转换阶段**: 需求文档为 CodeGen 配置生成提供完整上下文
3. **代码生成阶段**: CodeGen 系统基于需求文档执行代码生成
4. **质量保证阶段**: 验证生成的代码是否符合需求文档的规格

## 📁 文件说明

| 文件                                | 说明               |
| ----------------------------------- | ------------------ |
| `jeecg-ai-setup.sh`                 | 一键安装脚本       |
| `jeecg-ai-config.json`              | 主配置文件         |
| `jeecg-claude-extension.md`         | Claude AI 扩展配置 |
| `JeecgBoot_AI_Integration_Guide.md` | 详细集成指南       |

## 📞 相关链接

- 📖 **详细文档**: [JeecgBoot_AI_Integration_Guide.md](JeecgBoot_AI_Integration_Guide.md)
- 🤖 **CodeGen 系统**: [../CodeGen/Code_Gen_Agent.md](../CodeGen/Code_Gen_Agent.md)
- 📋 **AI 配置**: [../PRPs/CLAUDE.md](../PRPs/CLAUDE.md)

---

**让 JeecgBoot 开发更智能、更高效！** 🚀
