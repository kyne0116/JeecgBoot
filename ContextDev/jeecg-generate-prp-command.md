# JeecgBoot专用需求文档生成命令模板
# 此文件将被jeecg-ai-setup.sh脚本自动部署到.claude/commands/目录
# 版本: 2.0.0 | 行数: 242 | 三大增强特性 | 8+/10质量标准

# Create JeecgBoot Requirements PRP (Enhanced Version)

## Feature request: $ARGUMENTS

基于JeecgBoot企业级快速开发平台特点，生成专用的智能需求文档(PRP)。本命令专为JeecgBoot生态设计，遵循Context Engineering最佳实践，深度集成CodeGen系统工作流程，实现从自然语言需求到标准化项目需求文档的智能化转换。

## 🎯 JeecgBoot专用增强特性

### 1. 智能需求分类决策引擎
基于CLAUDE_JEECGBOOT.md规范第57-106行的"开发决策流程与需求分类处理机制"：

**自动需求复杂度评估**：
- 识别简单CRUD需求 → 自动配置CodeGen系统路径
- 识别复杂业务需求 → 自动启动官方文档研究路径  
- 识别混合需求 → 制定分层实现策略（先CodeGen基础，再复杂扩展）

**智能技术路径决策**：
- 业务实体数量和关系复杂度分析
- 多表关联和复杂查询识别
- 第三方系统集成需求评估
- JeecgBoot架构约束自动检查

### 2. CodeGen系统深度集成
严格遵循CLAUDE_JEECGBOOT.md规范第164-275行的"CodeGen系统强制使用原则"：

**零容忍违规检查**：
- 自动识别必须使用CodeGen的场景
- 强制禁止手动编写Entity、Controller、Service、Mapper
- 自动生成Code_Gen_Agent.md兼容配置
- 集成Code_Gen_Guide.py执行参数

**CodeGen配置智能生成**：
- MODULE_NAME、ENTITY_NAME、TABLE_NAME自动提取
- 符合us_{module}_{entity}表命名规范
- org.jeecg.modules.{module}包结构规范
- 系统字段和权限配置自动包含

### 3. 官方技术文档智能研究
对于复杂业务需求，自动查询和应用：

**context7.com技术指导**：
- 最佳实践案例自动检索
- 配置说明和参数设置研究
- 业务流程设计模式学习

**deepwiki.com深度分析**：
- 技术原理和实现机制深入理解
- 扩展开发和自定义组件指导
- 高级特性和优化技巧应用

## 📋 研究分析流程

### 阶段一：JeecgBoot代码库智能分析
1. **相似模块模式识别**
   - 搜索现有业务模块和架构模式
   - 识别相似实体、控制器和服务实现
   - 分析JeecgBoot特有的约定和设计模式
   - 检查现有模块结构用于验证方法参考

2. **CodeGen系统能力评估**
   - 验证当前CodeGen系统可用性和约束
   - 确认支持的字段类型和业务逻辑复杂度
   - 检查数据字典集成和系统配置

### 阶段二：业务需求智能解析
1. **实体关系建模**
   - 解析特征请求中的业务实体和关系
   - 区分CRUD操作与复杂业务逻辑需求
   - 确定数据模型设计模式和约束条件
   - 映射业务规则到JeecgBoot实现模式

2. **集成需求分析**
   - 分析与现有JeecgBoot模块的集成需求
   - 识别权限控制和数据权限要求
   - 评估性能和扩展性考虑因素

### 阶段三：JeecgBoot技术方案研究
1. **框架规范研究**
   - 表命名约定验证 (us_{module}_{entity})
   - 包结构模式确认 (org.jeecg.modules.{module})
   - CodeGen配置要求和参数规范
   - 权限注解和安全机制集成

2. **相似实现案例研究**
   - 在平台中搜索类似功能的实现
   - 分析最佳实践和设计模式
   - 确定可复用的组件和工具类

### 阶段四：用户需求澄清（如需要）
- 具体业务实体关系和约束确认？
- 与现有JeecgBoot模块的集成要求？
- 特殊权限或工作流要求？
- 性能或可扩展性特殊考虑？

## 🔧 智能PRP文档生成

### 模板智能应用
使用 `PRPs/templates/REQUIREMENTS_JEECGBOOT.md` 作为基础模板，动态注入：

**JeecgBoot平台上下文**：
- 当前项目结构和模块组织分析结果
- 现有实体模式和命名约定参考
- CodeGen系统能力和配置要求
- 系统管理模块集成点识别

**业务上下文智能生成**：
- 清晰的业务实体定义及关系映射
- 用户角色和权限要求规格
- 业务工作流程和处理逻辑定义
- 数据验证和业务规则规范

**技术实现上下文**：
- 遵循us_{module}_{entity}模式的表命名
- 包含系统必需字段 (id, create_by, create_time等)
- @RequiresPermissions注解的控制器模式
- MyBatis-Plus集成的服务层设计
- Vue 3前端组件要求和API接口设计

### 实现蓝图智能规划

**CodeGen配置自动生成**：
```json
{
  "MODULE_NAME": "[智能提取的模块名]",
  "ENTITY_NAME": "[智能提取的实体名]", 
  "TABLE_NAME": "us_{module}_{entity}",
  "PACKAGE_NAME": "org.jeecg.modules.{module}",
  "FIELDS_CONFIG": "[基于需求分析的字段配置]",
  "DICT_CONFIG": "[数据字典集成配置]",
  "PERMISSION_CONFIG": "[权限控制配置]"
}
```

**复杂业务逻辑规划**：
- 超出基础CRUD操作的扩展功能
- 自定义业务规则和验证逻辑
- 工作流程集成和状态管理要求
- 报表和数据分析功能需求

### JeecgBoot专用验证门槛脚本

```bash
#!/bin/bash
# JeecgBoot环境完整验证脚本

echo "🔍 验证JeecgBoot开发环境..."

# 基础环境验证
echo "1. 验证基础开发环境"
mvn -version || { echo "❌ Maven未安装"; exit 1; }
java -version || { echo "❌ Java未安装"; exit 1; }
node --version || { echo "❌ Node.js未安装"; exit 1; }

# JeecgBoot服务验证
echo "2. 验证JeecgBoot服务连接"
curl -f http://localhost:8080/jeecg-boot/sys/health 2>/dev/null || echo "⚠️ JeecgBoot服务未运行"

# CodeGen系统验证  
echo "3. 验证CodeGen系统可用性"
python3 CodeGen/Code_Gen_Guide.py --test-connection 2>/dev/null || echo "⚠️ CodeGen系统需要启动"

# 项目结构验证
echo "4. 验证项目结构完整性"
test -d jeecg-boot/jeecg-module-system/ || { echo "❌ 后端模块目录不存在"; exit 1; }
test -d jeecgboot-vue3/src/ || { echo "❌ 前端源码目录不存在"; exit 1; }

# 配置文件验证
echo "5. 验证关键配置文件"
test -f jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application.yml || { echo "❌ 后端配置文件缺失"; exit 1; }
test -f jeecgboot-vue3/vite.config.ts || { echo "❌ 前端配置文件缺失"; exit 1; }

# 模板和工具验证
echo "6. 验证PRP模板和工具"
test -f PRPs/templates/REQUIREMENTS_JEECGBOOT.md || { echo "❌ JeecgBoot需求模板缺失"; exit 1; }
test -f PRPs/CLAUDE.md || { echo "❌ Claude配置文件缺失"; exit 1; }

echo "✅ JeecgBoot环境验证完成"
```

## ⚡ 关键决策逻辑

***在生成PRP之前必须进行超级深度思考***

考虑以下JeecgBoot专用要素：
- 这如何适配JeecgBoot的模块化架构？
- 需要哪些CodeGen配置来实现这个需求？
- 如何与现有系统模块集成？
- 表命名和包结构要求是什么？
- 有哪些安全和权限考虑？
- 需要哪些前端组件和API？
- 是否需要数据权限控制？ 
- 有没有工作流程集成需求？

## 📁 输出规范

**文件保存路径**: `projectDocs/REQUIREMENTS_{project-name}.md`

**命名约定**:
- 使用描述性项目名称，kebab-case格式
- 示例: `REQUIREMENTS_customer-management.md`
- 示例: `REQUIREMENTS_inventory-system.md` 
- 示例: `REQUIREMENTS_financial-reporting.md`

## ✅ JeecgBoot专用质量检查清单

**架构合规性**:
- [ ] 所有JeecgBoot架构约束已包含
- [ ] CodeGen系统集成要求已明确指定
- [ ] 表命名遵循us_{module}_{entity}模式
- [ ] 系统字段和权限已正确定义

**CodeGen兼容性**:
- [ ] 需求可直接转换为CodeGen配置
- [ ] 所有实体遵循JeecgBoot命名约定  
- [ ] 字段定义包含正确类型和约束
- [ ] 权限配置完整且可执行

**开发就绪性**:
- [ ] CodeGen任务与自定义开发任务明确分离
- [ ] 复杂业务逻辑有具体实现指导
- [ ] 为JeecgBoot开发者提供完整上下文

**质量保证**:
- [ ] 验证门槛脚本可执行且通过验证
- [ ] 反模式已明确识别并避免
- [ ] 实施成功率置信度评分8+/10

## 🎯 成功标准

**实施成功率评分**: 基于以下维度评分1-10：
1. JeecgBoot架构合规程度
2. CodeGen系统集成完整性
3. 技术方案可行性和详细程度
4. 业务需求覆盖完整性
5. 开发指导清晰度和可操作性

**目标**: 确保通过全面的JeecgBoot专用上下文和CodeGen系统集成，实现一次性实施成功率≥90%。

记住：目标是创建一个需求文档，通过comprehensive JeecgBoot-specific context和CodeGen integration实现one-pass implementation success。