# JeecgBoot 模块开发 - 产品需求提示 (PRP) 模板

## 📋 项目上下文

### JeecgBoot 框架信息

- **框架版本**: JeecgBoot 3.x
- **技术栈**: Spring Boot + Vue3 + Ant Design Vue
- **数据库**: MySQL 8.0+
- **构建工具**: Maven 3.6+

### CodeGen 系统集成

- **AI 代理规范**: CodeGen/Code_Gen_Agent.md
- **执行脚本**: CodeGen/Code_Gen_Guide.py
- **配置模板**: CodeGen/Code_Gen_Guide.json
- **字段模板**: CodeGen/Code_Gen_field_templates.json

## 🎯 功能需求

### 业务功能描述

[详细描述要实现的业务功能，包括核心功能点和业务流程]

### 技术要求

- **表名格式**: us*{模块名}*{子模块名}\_{业务场景}
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

## 🔄 实现蓝图

### 阶段 1: 环境准备和需求分析

1. **数据字典获取**

   ```bash
   python3 CodeGen/Code_Gen_Guide.py --dict
   ```

2. **需求分析** (基于 Code_Gen_Agent.md 规范)

   - 语义理解和关键词提取
   - 三核心变量智能推理: {模块名}、{子模块名}、{业务场景}
   - 业务系统映射和字段设计

3. **表名验证**
   ```bash
   python3 CodeGen/Code_Gen_Guide.py --validate-table-name {表名}
   ```

### 阶段 2: 配置文件生成

1. **基础配置生成**

   - 基于 Code_Gen_Guide.json 模板
   - 包含 7 个 JeecgBoot 系统字段
   - 添加业务字段定义

2. **字段类型匹配**

   - 使用 Code_Gen_field_templates.json 模板
   - 数据字典智能匹配
   - 字段验证规则配置

3. **配置验证**
   ```bash
   python3 -m json.tool temp_config.json
   ```

### 阶段 3: 代码生成执行

1. **模块检查和创建**

   ```bash
   # 如果模块不存在，自动创建
   mvn archetype:generate -DgroupId=org.jeecg.modules.{模块名}
   ```

2. **代码生成执行**

   ```bash
   python3 CodeGen/Code_Gen_Guide.py --module-name {模块名} --form-config temp_{业务}_config.json
   ```

3. **编译验证**
   ```bash
   mvn clean compile -pl jeecg-module-{模块名}
   ```

### 阶段 4: 前端代码迁移

1. **Vue3 代码迁移**

   - 自动迁移生成的前端代码到 Vue3 项目
   - 组件路径配置和路由注册

2. **前端构建验证**
   ```bash
   cd jeecgboot-vue3 && npm run build
   ```

### 阶段 5: 权限配置和测试

1. **权限自动配置**

   - 菜单权限自动注册
   - 角色权限自动授权

2. **功能测试**
   - CRUD 操作测试
   - 权限控制测试
   - 前端页面测试

## ✅ 验证门槛

### 必须通过的验证命令

```bash
# 1. CodeGen 配置验证
python3 CodeGen/Code_Gen_Guide.py --validate-config

# 2. JeecgBoot 服务连接验证
python3 CodeGen/Code_Gen_Guide.py --test-connection

# 3. 表名格式验证
python3 CodeGen/Code_Gen_Guide.py --validate-table-name {表名}

# 4. 代码生成验证
python3 CodeGen/Code_Gen_Guide.py --module-name {模块名} --form-config {配置文件}

# 5. 后端编译验证
mvn clean compile -pl jeecg-module-{模块名}

# 6. 前端构建验证
cd jeecgboot-vue3 && npm run build

# 7. 单元测试验证
mvn test -pl jeecg-module-{模块名}
```

## 🎯 成功标准

### 后端成功标准

- [ ] 数据库表创建成功，包含所有字段和索引
- [ ] 实体类生成正确，包含 7 个系统字段
- [ ] Service 和 Controller 接口完整可用
- [ ] 权限配置正确，菜单和按钮权限生效
- [ ] 单元测试通过

### 前端成功标准

- [ ] Vue3 页面正常显示，无控制台错误
- [ ] CRUD 操作功能完整
- [ ] 表单验证规则正确
- [ ] 权限控制在前端正确显示
- [ ] 响应式设计适配

### 集成成功标准

- [ ] 前后端接口对接正常
- [ ] 数据权限控制生效
- [ ] 业务流程完整可用
- [ ] 性能指标满足要求

## 📊 质量评估

### 置信度评分标准

- **9-10 分**: 所有上下文完整，验证门槛全面，预期一次性成功
- **7-8 分**: 大部分上下文完整，少量手工调整
- **5-6 分**: 基本上下文完整，需要一定的手工完善
- **3-4 分**: 上下文不足，需要大量手工工作
- **1-2 分**: 上下文严重不足，不建议执行

### 当前 PRP 置信度评分: [待评估]/10

## 🔧 故障排除

### 常见问题和解决方案

1. **登录失败**: 检查 JeecgBoot 服务状态和配置文件
2. **表名格式错误**: 使用标准格式 us*{模块}*{子模块}\_{业务场景}
3. **模块不存在**: 脚本会自动创建 Maven 模块
4. **数据字典匹配失败**: 更新字典缓存
5. **前端编译失败**: 检查 Vue3 项目依赖和配置

## 📝 实现记录

### 执行日志

[记录实际执行过程中的关键步骤和结果]

### 问题记录

[记录遇到的问题和解决方案]

### 优化建议

[记录可以改进的地方和优化建议]

---

**模板版本**: v2.0.0 (CodeGen + PRP 集成版)
**最后更新**: 2024 年 1 月 22 日
**适用范围**: JeecgBoot 3.x + CodeGen 系统 + PRP 工作流
