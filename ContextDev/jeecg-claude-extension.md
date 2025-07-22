# JeecgBoot 项目扩展配置

# 此文件追加到 Context Engineering 的 CLAUDE.md 中

## 🤖 CodeGen AI 代理核心规范

- **严格遵循**: CodeGen/Code_Gen_Agent.md 中定义的 AI 行为边界
- **推理策略**: 使用 LangGPT 结构化提示进行业务需求分析
- **决策逻辑**: 基于业务场景自动选择合适的字段类型和验证规则
- **执行协议**: 配置生成 → 调用 Code_Gen_Guide.py → 结果验证
- **AI 命令映射**:
  - `/sc:jeecg-analyze` - 基于 CodeGen AI 代理的需求分析
  - `/sc:jeecg-config` - 智能生成 JSON 配置文件
  - `/sc:codegen` - 执行完整 CodeGen 工作流
- **PRP 工作流集成**:
  - `/generate-prp` - 生成 JeecgBoot 专用的产品需求提示
  - `/execute-prp` - 执行 PRP 并调用 CodeGen 系统
  - 自动集成 CodeGen AI 代理规范和验证门槛
  - 使用 JeecgBoot PRP 模板: `ContextDev/templates/jeecg-prp-template.md`
  - 90%+ 成功率，包含完整上下文和自动化验证

## 🏗️ JeecgBoot 架构约定

- **模块命名**: jeecg-module-{业务域} (如 jeecg-module-hrms)
- **包结构**: org.jeecg.modules.{业务域}
- **数据表**: {业务域}\_{表名} (如 hrms_employee)
- **API 路径**: /api/{业务域}/{功能} (如/api/hrms/employee)

## 📋 强制系统字段 (每个实体必含)

```java
@TableId(type = IdType.ASSIGN_ID)
private String id;

@CreatedBy
private String createBy;

@CreatedDate
private Date createTime;

@LastModifiedBy
private String updateBy;

@LastModifiedDate
private Date updateTime;

private String sysOrgCode;

@TableLogic
private Integer delFlag;
```

## 🔧 CodeGen 系统深度集成

- **核心脚本**: CodeGen/Code_Gen_Guide.py (完整自动化工作流)
- **AI 代理规范**: CodeGen/Code_Gen_Agent.md (AI 行为边界定义)
- **配置模板**: CodeGen/Code_Gen_Guide.json (表单模板)
- **系统配置**: CodeGen/Code_Gen_Config.json (系统级配置)
- **AI 增强流程**: AI 需求分析 → 智能配置生成 → CodeGen 执行 → 结果优化
- **自动化能力**: 表单创建、代码生成、编译验证、前端迁移、权限授权
- **严禁**: 绕过 CodeGen 系统重新实现代码生成逻辑

## 📋 PRP 工作流最佳实践

### 推荐的开发流程

1. **使用 PRP 模板**: 基于 `ContextDev/templates/jeecg-prp-template.md` 创建需求文件
2. **完善需求描述**: 在 FEATURE 部分提供详细的业务需求
3. **指定参考资源**: 在 EXAMPLES 和 DOCUMENTATION 部分提供相关资源
4. **执行 PRP 工作流**: 使用 `/generate-prp` 和 `/execute-prp` 命令
5. **验证生成结果**: PRP 会自动执行验证门槛

### PRP vs 传统命令对比

- **上下文完整性**: PRP 包含完整项目上下文，传统命令依赖单次对话
- **成功率**: PRP 90%+，传统命令 60-70%
- **验证机制**: PRP 自动化验证，传统命令需要手工验证
- **错误处理**: PRP 内置错误处理和重试，传统命令需要手工调试

### 典型使用场景

- **复杂模块开发**: 多表关联、工作流集成、权限控制
- **在线表单创建**: 动态表单、文件上传、审批流程
- **系统集成**: 第三方 API 集成、消息队列、分布式事务

## 🛡️ 权限系统约定

- **菜单权限**: {业务域}:{功能}:list
- **按钮权限**: {业务域}:{功能}:add/edit/delete
- **数据权限**: 使用@DataScope 注解
- **前端权限**: v-auth 指令

## 🎨 前端开发约定

- **框架**: Vue3 Composition API + TypeScript
- **UI 库**: Ant Design Vue
- **表格**: 优先使用 JVxeTable
- **表单**: 优先使用 JFormContainer
- **路由**: 包含权限控制配置

## 📊 在线表单 API 流程

1. POST /sys/mLogin (获取 token)
2. POST /online/cgform/api/addAll (创建表单)
3. GET /online/cgform/head/list (获取表单 ID)
4. POST /online/cgform/api/doDbSynch/{id}/normal (同步数据库)
5. POST /online/cgform/api/codeGenerate (生成代码)

## ⚠️ 重要提醒

- 永不修改 Code_Gen_Config.json 模板文件
- 始终创建临时配置文件
- 新模块需先检查是否存在，不存在则用 Maven archetype 创建
- 所有 API 返回必须使用 Result 统一格式
