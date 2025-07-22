# ContextDev - JeecgBoot AI 赋能开发

## 📋 概述

ContextDev 为 JeecgBoot 提供 AI 赋能开发能力，集成了两个成熟的开源项目：

- **[Context Engineering Intro](https://github.com/coleam00/context-engineering-intro)** (6.7k⭐): PRP 工作流，90%+成功率
- **[SuperClaude Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework)** (9.9k⭐): 16 专业命令+9AI 人格
- **JeecgBoot CodeGen**: 官方 API 驱动的代码生成引擎

### 🎯 核心价值

- 🤖 **AI 驱动**: 从需求分析到代码生成的全流程 AI 辅助
- 📋 **PRP 工作流**: 产品需求提示，包含完整上下文和验证
- 🛠️ **专业工具**: 16 个专业命令覆盖开发全流程
- 🔗 **深度集成**: 与 JeecgBoot CodeGen 系统无缝集成

## 🎯 核心特性

### 🤖 AI 代理驱动的代码生成

- **CodeGen AI 代理**: 基于`Code_Gen_Agent.md`规范的智能代码生成
- **业务需求理解**: AI 自动分析业务需求，生成标准化字段设计
- **配置文件智能生成**: 自动生成符合 JeecgBoot 规范的 JSON 配置
- **完整工作流自动化**: 从需求分析到代码部署的全流程自动化

### 🔧 深度集成 JeecgBoot CodeGen 系统

- **AI 增强的 Code_Gen_Guide.py**: 智能参数生成和执行优化
- **标准化表名解析**: AI 辅助的模块和包名生成
- **自动化编译验证**: Maven 编译和前端代码迁移
- **权限系统集成**: 自动权限授权和角色管理

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
# PRP 工作流（推荐）
/generate-prp customer-management-requirements.md
/execute-prp PRPs/customer-management.md

# SuperClaude 命令
/sc:analyze "分析业务需求"
/sc:implement "实现客户管理模块"
/sc:architect "设计系统架构"
```

## 📁 文件说明

| 文件                                | 说明               |
| ----------------------------------- | ------------------ |
| `jeecg-ai-setup.sh`                 | 一键安装脚本       |
| `jeecg-ai-config.json`              | 主配置文件         |
| `jeecg-claude-extension.md`         | Claude AI 扩展配置 |
| `JeecgBoot_AI_Integration_Guide.md` | 详细集成指南       |
| `templates/jeecg-prp-template.md`   | PRP 模板           |

## 📞 相关链接

- 📖 详细文档: [JeecgBoot_AI_Integration_Guide.md](JeecgBoot_AI_Integration_Guide.md)
- 🤖 CodeGen 系统: [../CodeGen/Code_Gen_Agent.md](../CodeGen/Code_Gen_Agent.md)
- 🌐 上游项目:
  - [Context Engineering Intro](https://github.com/coleam00/context-engineering-intro)
  - [SuperClaude Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework)

---

**让 JeecgBoot 开发更智能、更高效！** 🚀
