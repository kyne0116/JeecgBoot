# JeecgBoot AI 赋能快速开始指南

## 🚀 5 分钟快速上手

### 前提条件

- ✅ JeecgBoot 项目已运行
- ✅ Python 3.7+ 已安装 (CodeGen 系统要求)
- ✅ Node.js 16+ 已安装
- ✅ Claude Code 已安装
- ✅ CodeGen 系统可用 (CodeGen/目录存在)

### 一键安装

```bash
# 1. 下载并执行安装脚本
curl -O https://raw.githubusercontent.com/kyne0116/JeecgBoot/my-custom/ContextDev/jeecg-ai-setup.sh
chmod +x jeecg-ai-setup.sh
./jeecg-ai-setup.sh

# 2. 等待安装完成（约5-10分钟）
# 预期输出: ✨ JeecgBoot AI赋能环境搭建完成！
```

### 立即测试

在 Claude Code 中执行：

```bash
# 测试基础功能
/sc:analyze "测试JeecgBoot AI集成"

# 测试JeecgBoot特定功能
/sc:implement "创建一个简单的用户实体类"

# 测试CodeGen AI代理
/sc:jeecg-analyze "设计一个客户管理模块"

# 测试人格切换
/sc:architect "设计一个简单的模块架构"
```

## 🎯 核心功能演示

### 1. PRP 工作流（推荐方式）

**PRP (Product Requirements Prompt)** 是最高效的开发方式，一键完成从需求到代码的全流程：

```bash
# 步骤1: 创建需求文件（使用模板）
cp ContextDev/templates/jeecg-prp-template.md my-customer-management.md
# 编辑文件，填入具体需求

# 步骤2: 生成 PRP（AI 研究代码库，生成实现蓝图）
/generate-prp my-customer-management.md

# 步骤3: 执行 PRP（AI 自动调用 CodeGen，完成代码生成）
/execute-prp PRPs/customer-management.md
```

**PRP 工作流优势**：

- ✅ **90%+ 成功率** - 包含完整上下文和验证机制
- ✅ **自动化验证** - 内置多层质量检查
- ✅ **错误自愈** - 自动重试和问题修复
- ✅ **标准化输出** - 确保符合项目规范

### 2. 传统命令流程（备选方式）

```bash
# 分步执行（适合学习和调试）
/sc:jeecg-analyze "开发商品管理模块，包含商品基本信息、分类、库存管理"
/sc:design "设计商品管理的数据模型和API"
/sc:jeecg-config "生成商品管理模块的JSON配置文件"
/sc:codegen "执行完整的代码生成工作流"
/sc:test "生成测试用例"
/sc:document "生成API文档"
```

### 3. CodeGen 增强的代码生成器

```bash
# AI生成配置文件
/sc:jeecg-config "为订单管理生成JeecgBoot配置JSON，包含订单基本信息、商品明细、支付状态等字段"

# 执行代码生成
python3 CodeGen/Code_Gen_Guide.py --module-name ecommerce --form-config ai_generated_config.json

# AI优化生成结果
/sc:improve "优化生成的代码质量"
```

### 4. 智能问题诊断

```bash
# 性能问题分析
/sc:troubleshoot "数据库查询慢的问题"

# 安全漏洞检查
/sc:security "检查权限配置是否安全"

# 代码质量评估
/sc:analyze "评估当前代码质量"
```

## 📋 常用命令速查

| 场景           | 命令                           | 说明                             |
| -------------- | ------------------------------ | -------------------------------- |
| **PRP 工作流** | `/generate-prp 需求文件.md`    | 生成产品需求提示（推荐）         |
| **PRP 执行**   | `/execute-prp PRPs/功能.md`    | 执行 PRP 进行代码生成（推荐）    |
| 需求分析       | `/sc:jeecg-analyze "需求描述"` | 基于 CodeGen AI 代理分析业务需求 |
| 配置生成       | `/sc:jeecg-config "配置需求"`  | 生成 JeecgBoot JSON 配置文件     |
| 代码生成       | `/sc:codegen "生成目标"`       | 执行完整 CodeGen 工作流          |
| 架构设计       | `/sc:design "设计目标"`        | 设计系统架构                     |
| 代码实现       | `/sc:implement "功能描述"`     | 实现具体功能                     |
| 代码优化       | `/sc:improve "优化目标"`       | 优化代码质量                     |
| 测试生成       | `/sc:test "测试范围"`          | 生成测试用例                     |
| 问题诊断       | `/sc:troubleshoot "问题描述"`  | 诊断和解决问题                   |
| 安全检查       | `/sc:security "检查范围"`      | 安全漏洞扫描                     |
| 文档生成       | `/sc:document "文档类型"`      | 生成技术文档                     |

## 🔧 专家人格应用

### 架构师模式

```bash
/sc:architect "设计微服务架构"
# 适用: 系统设计、技术选型、架构优化
```

### 后端专家模式

```bash
/sc:backend "实现分布式事务"
# 适用: Spring Boot开发、数据库设计、API实现
```

### 前端专家模式

```bash
/sc:frontend "优化页面性能"
# 适用: Vue3开发、组件设计、用户体验
```

### 安全专家模式

```bash
/sc:security "审查安全配置"
# 适用: 安全审计、权限设计、漏洞修复
```

## 🛠️ 实际应用示例

### 示例 1: PRP 驱动的完整模块开发（推荐）

```bash
# 1. 创建需求文件
cat > jeecg-customer-management.md << 'EOF'
## FEATURE:
开发 CRM 客户管理模块，包含客户基本信息、联系方式、订单历史、业务状态管理

## EXAMPLES:
- CodeGen/Code_Gen_Guide.json - 标准配置模板
- examples/jeecg-boot/backend/ - 后端代码模式

## DOCUMENTATION:
- JeecgBoot API: http://localhost:8080/jeecg-boot/doc.html
- CodeGen 指南: CodeGen/Code_Gen_Guide.md

## OTHER CONSIDERATIONS:
- 表名格式: us_crm_customer_management
- 包含 7 个 JeecgBoot 系统字段
- 需要数据权限控制
- 集成消息通知功能
EOF

# 2. 一键生成和执行（90%+ 成功率）
/generate-prp jeecg-customer-management.md
/execute-prp PRPs/customer-management.md

# 预期结果: 完整的客户管理模块，包含前后端代码、数据库表、权限配置
```

### 示例 2: 传统命令方式（备选）

```bash
# 分步执行（适合学习和调试）
/sc:jeecg-analyze "创建客户管理模块，包含客户基本信息、联系方式、订单历史"
/sc:jeecg-config "生成客户管理模块的 JSON 配置"
/sc:codegen "执行完整的代码生成工作流"
/sc:improve "优化客户管理模块的代码结构和性能"
```

### 示例 3: PRP 驱动的在线表单开发

```bash
# 1. 创建表单需求文件
cat > jeecg-employee-onboarding-form.md << 'EOF'
## FEATURE:
开发员工入职申请在线表单，包含个人信息、教育背景、工作经历、紧急联系人等

## EXAMPLES:
- CodeGen/Code_Gen_Guide.json - 在线表单配置模板
- examples/jeecg-boot/forms/ - 表单设计模式

## OTHER CONSIDERATIONS:
- 表名格式: us_hr_employee_onboarding_form
- 支持文件上传（简历、证件照）
- 集成审批流程
- 移动端适配
EOF

# 2. PRP 工作流（自动创建表单和管理页面）
/generate-prp jeecg-employee-onboarding-form.md
/execute-prp PRPs/employee-onboarding-form.md
```

## 🔄 日常维护

### 更新上游项目

```bash
# 执行更新脚本
./jeecg-ai-update.sh

# 验证更新结果
/sc:analyze "测试更新后的功能"
```

### 备份和恢复

```bash
# 查看备份
ls jeecg-backup-*/

# 恢复配置
cp jeecg-backup-latest/* .ai-config/
```

## ❓ 常见问题

**Q: AI 命令没有响应？**

```bash
# 检查SuperClaude状态
python3 -c "import SuperClaude; print('OK')"

# 重新安装
uv add SuperClaude --reinstall
```

**Q: MCP 服务器连接失败？**

```bash
# 检查服务器状态
npm list -g | grep mcp-server

# 重新安装
npm install -g @context7/mcp-server
```

**Q: 配置文件丢失？**

```bash
# 重新生成配置
cp context-engineering-intro/CLAUDE.md ~/.claude/CLAUDE.md
```

## 📚 进阶学习

- 📖 [完整集成指南](JeecgBoot_AI_Integration_Guide.md)
- 🔧 [配置文件详解](jeecg-ai-config.json)
- 📝 [示例代码库](jeecg-examples-structure.md)
- 🔄 [更新同步脚本](jeecg-ai-update.sh)

## 🎉 开始您的 AI 辅助开发之旅！

现在您已经完成了 JeecgBoot AI 赋能环境的搭建，可以开始享受 AI 辅助开发带来的效率提升了！

**下一步建议**:

1. 尝试用 PRP 工作流开发一个完整的模块
2. 体验 CodeGen AI 代理的智能配置生成
3. 使用不同的 AI 人格和命令
4. 将 AI 工具集成到您的日常开发流程中
5. 与团队分享 AI 开发的最佳实践

**技术支持**:

- 遇到问题请查看[完整集成指南](JeecgBoot_AI_Integration_Guide.md)
- 加入 JeecgBoot 社区获取更多帮助
- 关注上游项目获取最新功能更新

---

**版本**: v2.0.0 (CodeGen + PRP 集成版)
**最后更新**: 2024 年 1 月 22 日
**维护者**: JeecgBoot AI 集成团队
