# 通用仓库同步脚本使用指南

## 概述

这些脚本可以帮助您保持 fork 仓库与官方仓库的同步，同时保留您的个人变更。脚本已经通用化，可以适用于任何 GitHub 项目。

## 文件说明

- `sync-with-upstream.bat` - Windows 批处理脚本
- `sync-with-upstream.sh` - Linux/Mac Bash 脚本
- `SYNC_SCRIPTS_README.md` - 本说明文件

## 快速开始

### 1. 配置脚本

在使用脚本前，需要修改脚本顶部的配置变量：

```bash
# 配置变量示例
UPSTREAM_REPO_URL="https://github.com/original-owner/project.git"
ORIGIN_REPO_URL="https://github.com/your-username/project.git"
MAIN_BRANCH="master"
PERSONAL_BRANCH="my-custom"
UPSTREAM_REMOTE_NAME="upstream"
ORIGIN_REMOTE_NAME="origin"
```

### 2. 运行脚本

**Windows 系统：**

```cmd
sync-with-upstream.bat
```

**Linux/Mac 系统：**

```bash
chmod +x sync-with-upstream.sh
./sync-with-upstream.sh
```

## 详细配置说明

### 配置变量含义

| 变量名                 | 说明               | 示例                                         |
| ---------------------- | ------------------ | -------------------------------------------- |
| `UPSTREAM_REPO_URL`    | 官方原始仓库 URL   | `https://github.com/jeecgboot/JeecgBoot.git` |
| `ORIGIN_REPO_URL`      | 您的 fork 仓库 URL | `https://github.com/kyne0116/JeecgBoot.git`  |
| `MAIN_BRANCH`          | 主分支名称         | `master`, `main`, `dev`                      |
| `PERSONAL_BRANCH`      | 个人开发分支       | `my-custom`, `feature/my-work`               |
| `UPSTREAM_REMOTE_NAME` | 上游远程名称       | `upstream`                                   |
| `ORIGIN_REMOTE_NAME`   | 源远程名称         | `origin`                                     |

### 常见项目配置示例

#### JeecgBoot 项目（默认配置）

```bash
UPSTREAM_REPO_URL="https://github.com/jeecgboot/JeecgBoot.git"
ORIGIN_REPO_URL="https://github.com/your-username/JeecgBoot.git"
MAIN_BRANCH="master"
PERSONAL_BRANCH="my-custom"
```

#### Spring Boot 项目

```bash
UPSTREAM_REPO_URL="https://github.com/spring-projects/spring-boot.git"
ORIGIN_REPO_URL="https://github.com/your-username/spring-boot.git"
MAIN_BRANCH="main"
PERSONAL_BRANCH="my-features"
```

#### Vue.js 项目

```bash
UPSTREAM_REPO_URL="https://github.com/vuejs/vue.git"
ORIGIN_REPO_URL="https://github.com/your-username/vue.git"
MAIN_BRANCH="dev"
PERSONAL_BRANCH="my-dev"
```

## 脚本功能

### 主要功能

1. **自动检查配置** - 验证 Git 仓库和远程配置
2. **同步主分支** - 从上游获取最新更新并合并
3. **更新个人分支** - 将个人分支更新到最新主分支
4. **创建备份** - 自动创建备份分支防止数据丢失
5. **冲突处理** - 提供详细的冲突解决指导
6. **操作总结** - 显示详细的同步结果报告

### 同步流程

1. 检查 Git 仓库状态
2. 配置上游仓库（如果不存在）
3. 切换到主分支并获取上游更新
4. 合并上游更新到本地主分支
5. 推送更新到您的 fork 仓库
6. 切换到个人分支并创建备份
7. 选择更新方式（Rebase 或 Merge）
8. 更新个人分支到最新主分支
9. 显示详细的操作总结

## 操作总结报告

脚本执行完成后会显示详细的中文总结报告：

```
========================================
           同步操作总结报告
========================================

📊 master分支同步结果：
   状态: 成功
   更新: 同步了 15 个提交
   变更: 3 files changed, 45 insertions(+), 12 deletions(-)

🔧 个人分支处理结果：
   分支名称: my-custom
   处理状态: 成功
   更新方式: Rebase
   备份分支: my-custom-backup-20250705-1841
   提交数量: 25 → 40

🚨 冲突情况：
   是否有冲突: 否

========================================

✅ 同步操作全部完成！您的代码已更新到最新版本。
```

## 注意事项

### 使用前准备

- 确保已安装 Git 并配置好 SSH 密钥或访问令牌
- 确保对配置的仓库有相应的访问权限
- 建议在重要操作前手动备份代码

### 冲突处理

如果遇到合并冲突，脚本会提供详细指导：

**Rebase 冲突：**

```bash
git add <冲突文件>
git rebase --continue
# 或放弃操作
git rebase --abort
```

**Merge 冲突：**

```bash
git add <冲突文件>
git commit
```

### 最佳实践

1. **定期同步** - 建议每周执行一次同步
2. **小而频繁的提交** - 减少冲突复杂度
3. **描述性提交信息** - 便于冲突解决时理解
4. **测试验证** - 同步后进行完整测试

## 故障排除

### 常见问题

**问题 1：网络连接失败**

```
fatal: unable to access 'https://github.com/...': Connection timed out
```

解决方案：检查网络连接，或使用 VPN

**问题 2：权限不足**

```
Permission denied (publickey)
```

解决方案：检查 SSH 密钥配置或使用 HTTPS 认证

**问题 3：分支不存在**

```
error: pathspec 'my-custom' did not match any file(s) known to git
```

解决方案：检查个人分支名称配置是否正确

## 自定义扩展

您可以根据需要修改脚本：

1. **添加新的检查** - 在相应函数中添加验证逻辑
2. **修改输出格式** - 调整日志函数的输出样式
3. **增加自动化** - 添加自动推送、标签等功能
4. **集成 CI/CD** - 将脚本集成到自动化流程中

## 支持的项目类型

这些脚本适用于所有基于 Git 的项目：

- Java 项目（Spring Boot、Maven、Gradle）
- JavaScript 项目（Node.js、Vue.js、React）
- Python 项目（Django、Flask）
- Go 项目
- .NET 项目
- 任何其他 Git 仓库

## 版本历史

- v1.0 - 基础同步功能
- v1.1 - 添加中文总结报告
- v1.2 - 通用化配置，支持任意项目

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这些脚本！
