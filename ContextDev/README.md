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

## 📞 相关链接

- 📖 **详细文档**: [JeecgBoot_AI_Integration_Guide.md](JeecgBoot_AI_Integration_Guide.md)
- 🤖 **CodeGen 系统**: [../CodeGen/Code_Gen_Agent.md](../CodeGen/Code_Gen_Agent.md)
- 📋 **AI 配置**: [../PRPs/CLAUDE.md](../PRPs/CLAUDE.md)

---

**让 JeecgBoot 开发更智能、更高效！** 🚀
