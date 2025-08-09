# SubAgent 自动化安装指南

本项目提供了完整的 SubAgent 自动化安装脚本，支持 Windows、macOS、Linux 三个平台，实现一键安装和管理。

## 脚本文件

- **subagent-installer.py** - 完整的 SubAgent 自动安装和管理脚本

## 🚀 快速开始

### 一键安装（推荐）

```bash
# 自动清理 + 安装所有 SubAgent
python subagent-installer.py
```

这是最简单的使用方式，脚本会自动：

1. 清理已安装的 SubAgent 文件
2. 清理 Claude Code 缓存
3. 安装所有 7 个 SubAgent 到官方目录
4. 提供重启 Claude Code 的建议

## 📋 命令参数

### 基本用法

```bash
# 显示平台信息
python subagent-installer.py --platform

# 显示发现的 subagent 报告
python subagent-installer.py --report

# 仅安装（不清理）
python subagent-installer.py --install

# 仅清理已安装的 SubAgent
python subagent-installer.py --clean

# 生成创建命令（适用于手动安装）
python subagent-installer.py --commands
```

### 高级功能

```bash
# 生成命令并复制到剪贴板
python subagent-installer.py --copy

# 生成批处理脚本文件
python subagent-installer.py --batch
```

## 🔧 安装原理

### 官方安装位置

SubAgent 文件被安装到 Claude Code 官方目录：

- **Windows**: `C:\Users\用户名\.claude\agents\`
- **macOS**: `~/.claude/agents/`
- **Linux**: `~/.claude/agents/`

### 安装过程

1. **发现阶段**: 扫描项目中的 SubAgent 定义文件
2. **清理阶段**: 删除已存在的 SubAgent 文件和缓存
3. **安装阶段**: 复制文件到 Claude Code 官方目录
4. **验证阶段**: 确认文件正确安装

## 📁 发现的 SubAgent

项目中包含以下 7 个 SubAgent：

### ContextDev 协作链（6 个）

1. **baseline-manager** - Context 基线师，专注 Context 基线建立和领域知识管理
2. **requirements-analyst** - 需求分析专家，负责业务需求分析和功能设计
3. **prototype-designer** - 原型设计师，创建交互原型和用户体验设计
4. **system-architect** - 系统架构师，设计技术架构和系统方案
5. **code-developer** - 开发工程师，实现具体功能和代码开发
6. **quality-tester** - 质量测试师，负责测试设计和质量保证

### CodeGen 模块（1 个）

7. **codegen-expert** - 代码生成专家，基于 JeecgBoot 的智能代码生成

## ⚠️ 重要说明：Claude Code 缓存问题

### 问题现象

如果在 Claude Code 中使用 `/agents` 命令看到 SubAgent 重复显示（如每个 agent 显示两次），这是由于 Claude Code 的会话级缓存机制导致的。

### 解决方案

1. **完全退出 Claude Code**（包括后台进程）
2. **运行安装脚本**：
   ```bash
   python subagent-installer.py
   ```
3. **重新启动 Claude Code**
4. **验证结果**：使用 `/agents` 命令检查

### 根本原因

Claude Code 在 `~/.claude/projects/` 目录为每个工作目录维护会话缓存，可能导致 SubAgent 信息被重复加载。脚本已内置缓存清理功能。

## 🖥️ 平台兼容性

### Windows

- 支持 Windows 7/8/10/11
- 兼容 CMD、PowerShell、Windows Terminal
- 自动处理编码问题和路径格式

### macOS

- 支持 macOS 10.12+
- 兼容 Terminal.app、iTerm2
- 支持 Intel 和 Apple Silicon

### Linux

- 支持主流 Linux 发行版
- 兼容各种 Shell 环境
- 自动检测系统架构

## ✨ 功能特性

- **🔍 智能发现**: 自动扫描并识别有效的 SubAgent 定义文件
- **🧹 智能清理**: 强力清理已安装文件和缓存目录
- **🔄 覆盖安装**: 支持安全的覆盖更新，无重复安装
- **🌐 跨平台**: 完全兼容 Windows、macOS、Linux
- **📝 详细日志**: 提供完整的安装过程和结果反馈
- **⚡ 一键操作**: 默认执行完整的清理+安装流程

## 🔍 使用示例

### 标准安装流程

```bash
# 1. 进入项目目录
cd /path/to/JeecgBoot

# 2. 执行一键安装
python subagent-installer.py

# 预期输出：
# 🚀 开始 SubAgent 自动化安装流程...
# 📋 步骤1: 清理已安装的 SubAgent...
# ✅ 清理完成
# 📋 步骤2: 安装 SubAgent 到Claude Code目录...
# [1/7] 正在安装: baseline-manager
# ✅ baseline-manager 安装成功
# ...
# 🎉 所有 7 个 SubAgent 安装成功！
# 🔄 请重启Claude Code以清除缓存并加载新的SubAgent
```

### 仅查看信息

```bash
# 查看平台信息
python subagent-installer.py --platform

# 查看发现的 SubAgent
python subagent-installer.py --report
```

### 手动安装模式

```bash
# 生成命令并复制到剪贴板
python subagent-installer.py --copy

# 然后在 Claude Code 中手动执行显示的命令
```

## 🚨 故障排除

### 1. 编码问题（Windows）

```cmd
# 设置控制台为 UTF-8
chcp 65001
python subagent-installer.py
```

### 2. 权限问题

```bash
# Linux/macOS - 确保有读取权限
chmod +r ContextDev/agents/*.md CodeGen/*.md

# Windows - 以管理员身份运行
python subagent-installer.py
```

### 3. Claude Code 仍显示重复

完全退出 Claude Code 后重新安装：

```bash
# 1. 完全退出 Claude Code
# 2. 运行安装
python subagent-installer.py
# 3. 重启 Claude Code
```

### 4. 文件读取失败

脚本会自动尝试多种编码：UTF-8、UTF-8 BOM、GBK、CP1252

## 🛠️ 技术实现

- **语言**: Python 3.7+
- **依赖**: yaml, pathlib, psutil（标准库 + psutil）
- **架构**: 模块化设计，易于扩展和维护
- **平台检测**: 基于 `platform` 模块自动识别操作系统

## 📊 安装统计

每次安装完成后，脚本会显示详细统计：

- 发现的 SubAgent 数量
- 成功安装的数量
- 失败安装的数量（如有）
- 安装位置和文件大小信息

## 🔄 更新和维护

### 更新 SubAgent

当项目中的 SubAgent 定义更新时，只需重新运行：

```bash
python subagent-installer.py
```

### 卸载所有 SubAgent

```bash
python subagent-installer.py --clean
```

## 👥 开发团队

- JeecgBoot ContextDev Team
- Subagent 集成支持
- 跨平台兼容性优化
- Claude Code 集成专家

## 📝 版本历史

- **v3.0**: 完整的自动化安装流程，支持缓存清理
- **v2.0**: 添加覆盖安装和重复检测
- **v1.2**: 优化编码处理和错误提示
- **v1.1**: 添加跨平台支持
- **v1.0**: 基础功能实现

---

**💡 提示**: 推荐使用默认的一键安装命令 `python subagent-installer.py`，这是最简单且最可靠的安装方式。
