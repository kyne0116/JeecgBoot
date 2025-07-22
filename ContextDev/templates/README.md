# ContextDev Templates - JeecgBoot AI 赋能模板目录

## 📁 目录说明

本目录包含 JeecgBoot AI 赋能开发的各种模板文件，用于标准化和自动化开发流程。

## 📋 模板文件清单

### 🎯 PRP (Product Requirements Prompt) 模板

- **[jeecg-prp-template.md](jeecg-prp-template.md)** - JeecgBoot 专用的产品需求提示模板
  - 集成 CodeGen 系统工作流
  - 包含完整的验证门槛
  - 支持 JeecgBoot 开发规范

## 🚀 使用方法

### 1. 使用 PRP 模板进行模块开发

```bash
# 1. 基于模板创建具体的需求文件
cp ContextDev/templates/jeecg-prp-template.md my-customer-management.md

# 2. 编辑需求文件，填入具体的业务需求
cat > my-customer-management.md << 'EOF'
# JeecgBoot 客户管理模块 - 产品需求提示 (PRP)

## 🎯 功能需求

### 业务功能描述
开发 CRM 客户管理模块，包含客户基本信息管理、联系方式管理、业务状态跟踪、订单历史查询等功能

### 技术要求
- **表名格式**: us_crm_customer_management
- **系统字段**: 必须包含 7 个 JeecgBoot 标准系统字段
- **权限控制**: 菜单权限 + 按钮权限 + 数据权限
- **前端规范**: Vue3 Composition API + TypeScript

## 📚 参考资源

### 代码示例
- **后端模式**: examples/jeecg-boot/backend/
- **前端模式**: examples/jeecg-boot/frontend/
- **配置模式**: CodeGen/Code_Gen_Guide.json

### 文档链接
- **JeecgBoot 官方文档**: http://doc.jeecg.com
- **在线表单 API**: http://localhost:8080/jeecg-boot/doc.html
- **CodeGen 使用指南**: CodeGen/Code_Gen_Guide.md

## 🔧 其他考虑因素
- 需要支持客户分级管理
- 集成消息通知功能
- 支持数据导入导出
- 需要移动端适配
EOF

# 3. 在 Claude Code 中生成 PRP（AI 会研究代码库并生成综合实现蓝图）
/generate-prp my-customer-management.md

# 4. 执行 PRP 进行代码生成（AI 会自动调用 CodeGen 系统）
/execute-prp PRPs/customer-management.md

# 预期结果: 完整的客户管理模块，包含前后端代码、数据库表、权限配置
```

### PRP 工作流优势

相比传统的分步命令，PRP 工作流具有以下优势：

| 特性         | 传统命令         | PRP 工作流         |
| ------------ | ---------------- | ------------------ |
| 成功率       | 60-70%           | 90%+               |
| 上下文完整性 | 依赖单次对话     | 包含完整项目上下文 |
| 验证机制     | 手工验证         | 自动化验证门槛     |
| 错误处理     | 需要手工调试     | 内置错误处理和重试 |
| 代码质量     | 依赖 AI 临时判断 | 基于项目最佳实践   |

### 2. 模板定制指南

#### 修改 PRP 模板

1. **业务需求部分**: 根据项目特点调整业务功能描述模板
2. **技术要求部分**: 根据技术栈调整技术规范
3. **验证门槛部分**: 根据项目质量要求调整验证命令
4. **成功标准部分**: 根据项目标准调整成功标准

#### 添加新模板

1. 在 templates 目录下创建新的模板文件
2. 遵循现有的命名规范：`jeecg-{用途}-template.{扩展名}`
3. 在本 README.md 中添加模板说明
4. 在相关配置文件中引用新模板

## 🎯 模板特性

### JeecgBoot PRP 模板特性

- **CodeGen 系统集成**: 深度集成 CodeGen AI 代理规范
- **完整工作流**: 从需求分析到代码部署的全流程覆盖
- **验证门槛**: 多层次的质量验证机制
- **标准化**: 符合 JeecgBoot 开发规范和最佳实践
- **可扩展**: 支持不同业务场景的定制化

### 模板设计原则

1. **标准化**: 统一的格式和结构
2. **可复用**: 适用于不同的业务场景
3. **可扩展**: 支持项目特定的定制
4. **质量导向**: 内置质量检查和验证机制
5. **文档完整**: 包含详细的使用说明和示例

## 📚 相关文档

- **[ContextDev 主目录](../README.md)** - AI 赋能开发总览
- **[快速开始指南](../Quick_Start_Guide.md)** - 5 分钟快速上手
- **[完整集成指南](../JeecgBoot_AI_Integration_Guide.md)** - 详细集成文档
- **[CodeGen 系统文档](../../CodeGen/Code_Gen_Guide.md)** - 代码生成系统
- **[CodeGen AI 代理规范](../../CodeGen/Code_Gen_Agent.md)** - AI 代理行为规范

## 🔄 模板维护

### 版本管理

- 模板文件包含版本信息和更新日期
- 重大变更时更新版本号
- 保持与 CodeGen 系统的兼容性

### 质量保证

- 定期验证模板的有效性
- 收集用户反馈进行改进
- 与上游项目保持同步

### 贡献指南

1. 提交模板改进建议
2. 报告模板使用中的问题
3. 分享最佳实践和使用经验

---

**目录版本**: v2.0.0 (CodeGen + PRP 集成版)
**最后更新**: 2024 年 1 月 22 日
**维护者**: JeecgBoot AI 集成团队
