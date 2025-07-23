# JeecgBoot专用需求文档执行命令模板
# 此文件将被jeecg-ai-setup.sh脚本自动部署到.claude/commands/目录
# 版本: 2.0.0 | 行数: 331 | 四阶段执行流程 | 9+/10质量标准

# Execute JeecgBoot Requirements PRP (Enhanced Version)

## PRP document to execute: $ARGUMENTS

基于JeecgBoot企业级快速开发平台特点，智能执行符合JeecgBoot规范的需求文档，实现从需求文档到完整代码实现的端到端自动化流程。本命令专为JeecgBoot生态设计，深度集成CodeGen系统，实现智能化的需求文档执行和代码生成。

## 🎯 JeecgBoot专用执行增强特性

### 1. 智能文档解析与验证引擎
基于CLAUDE_JEECGBOOT.md规范和Context Engineering最佳实践：

**文档完整性验证**：
- 解析并验证JeecgBoot需求文档的完整性和规范性
- 提取文档中的CodeGen配置参数和技术实现要求
- 验证文档与JeecgBoot架构约束的兼容性
- 生成详细的执行计划和任务清单

**智能上下文继承**：
- 完美继承 `/jeecg-generate-prp` 生成的所有专用配置
- 自动识别需求复杂度分类（简单CRUD vs 复杂业务）
- 继承质量保证标准和验证门槛脚本
- 保持与原需求分析的一致性和连贯性

### 2. CodeGen系统自动化执行集成
严格遵循CLAUDE_JEECGBOOT.md规范的"CodeGen系统强制使用原则"：

**智能配置解析**：
- 自动提取文档中的MODULE_NAME、ENTITY_NAME、TABLE_NAME参数
- 智能解析字段定义、数据类型和业务规则配置
- 生成符合Code_Gen_Agent.md规范的配置文件
- 验证配置参数的JeecgBoot合规性

**自动化代码生成流程**：
- 自动调用Code_Gen_Agent.md进行需求智能解析
- 智能执行Code_Gen_Guide.py完整代码生成工作流
- 实时监控代码生成过程和错误处理
- 自动验证生成代码的编译和功能完整性

### 3. 智能环境验证与错误处理系统
基于JeecgBoot开发环境的专用验证和错误处理机制：

**预执行环境全面验证**：
- 执行完整的JeecgBoot环境验证脚本
- 验证CodeGen系统可用性和数据字典连接
- 检查项目结构完整性和关键配置文件
- 确认数据库连接和表结构准备状态

**智能错误诊断与自动修复**：
- 提供详细的错误分析和具体解决方案
- 自动诊断常见的JeecgBoot环境配置问题
- 支持断点续传和执行状态恢复机制
- 智能推荐最优的问题解决路径

### 4. 端到端质量保证与验证机制
确保执行结果符合JeecgBoot企业级标准：

**完整性验证**：
- 验证生成的后端代码（Entity、Controller、Service、Mapper）
- 验证前端代码（Vue组件、API接口、路由配置）
- 验证数据库表结构创建和字段配置
- 验证系统权限配置和业务逻辑集成

**质量标准验证**：
- 执行编译测试确保代码语法正确性
- 运行基础功能测试验证CRUD操作
- 检查代码规范和JeecgBoot最佳实践遵循情况
- 生成详细的执行报告和后续优化建议

## 📋 智能执行流程

### 阶段一：文档分析与执行规划
1. **JeecgBoot需求文档深度解析**
   - 读取并解析指定的JeecgBoot需求文档
   - 验证文档格式和内容完整性
   - 提取技术实现参数和业务逻辑要求
   - 识别CodeGen任务和自定义开发任务

2. **执行计划智能生成**
   - 基于需求复杂度制定执行策略
   - 生成详细的任务清单和依赖关系
   - 确定CodeGen生成范围和自定义开发范围
   - 设置质量检查点和验证门槛

### 阶段二：环境验证与准备
1. **JeecgBoot开发环境全面检查**
   - 执行完整的环境验证脚本
   - 检查JeecgBoot服务运行状态
   - 验证CodeGen系统可用性和配置正确性
   - 确认数据库连接和项目结构完整性

2. **执行环境智能准备**
   - 自动修复发现的环境配置问题
   - 准备必要的依赖和工具
   - 初始化执行上下文和状态跟踪
   - 设置错误处理和恢复机制

### 阶段三：智能代码生成与实现
1. **CodeGen系统自动化执行**
   - 基于需求文档自动生成CodeGen配置
   - 调用Code_Gen_Agent.md进行智能需求解析
   - 执行Code_Gen_Guide.py完整代码生成流程
   - 实时监控生成过程和状态反馈

2. **复杂业务逻辑智能实现**
   - 识别超出CodeGen范围的复杂业务需求
   - 基于JeecgBoot架构规范制定实现方案
   - 在生成的基础代码上扩展复杂业务逻辑
   - 确保与CodeGen生成代码的无缝集成

### 阶段四：质量验证与集成测试
1. **代码质量全面验证**
   - 执行编译测试确保语法正确性
   - 运行基础功能测试验证CRUD操作
   - 检查前后端接口联调和数据流完整性
   - 验证权限控制和安全机制有效性

2. **JeecgBoot集成验证**
   - 验证与现有JeecgBoot模块的集成
   - 测试数据库操作和事务完整性
   - 检查系统配置和依赖注入正确性
   - 生成详细的执行报告和质量评估

## 🔧 智能执行逻辑

***在执行PRP之前必须进行超级深度思考***

考虑以下JeecgBoot专用执行要素：
- 如何正确解析需求文档中的技术参数？
- 需要调用哪些CodeGen组件和配置？
- 如何确保生成代码符合JeecgBoot规范？
- 怎样处理复杂业务逻辑和CodeGen的集成？
- 如何验证执行结果的完整性和正确性？
- 需要哪些后续优化和扩展建议？

### JeecgBoot专用执行验证脚本

```bash
#!/bin/bash
# JeecgBoot需求文档执行完整验证脚本

echo "🚀 开始JeecgBoot需求文档执行..."

# 阶段一：文档验证
echo "1. 验证需求文档完整性"
if [ ! -f "$1" ]; then
    echo "❌ 需求文档不存在: $1"
    exit 1
fi

# 提取关键配置参数
MODULE_NAME=$(grep -o 'MODULE_NAME.*:.*"[^"]*"' "$1" | cut -d'"' -f2)
ENTITY_NAME=$(grep -o 'ENTITY_NAME.*:.*"[^"]*"' "$1" | cut -d'"' -f2)
TABLE_NAME=$(grep -o 'TABLE_NAME.*:.*"[^"]*"' "$1" | cut -d'"' -f2)

if [ -z "$MODULE_NAME" ] || [ -z "$ENTITY_NAME" ] || [ -z "$TABLE_NAME" ]; then
    echo "❌ 需求文档缺少必要的CodeGen配置参数"
    exit 1
fi

echo "✅ 文档验证完成 - MODULE: $MODULE_NAME, ENTITY: $ENTITY_NAME, TABLE: $TABLE_NAME"

# 阶段二：环境验证
echo "2. 执行JeecgBoot环境验证"
mvn -version >/dev/null 2>&1 || { echo "❌ Maven未安装"; exit 1; }
java -version >/dev/null 2>&1 || { echo "❌ Java未安装"; exit 1; }
node --version >/dev/null 2>&1 || { echo "❌ Node.js未安装"; exit 1; }

# 验证JeecgBoot服务
curl -f http://localhost:8080/jeecg-boot/sys/health >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️ JeecgBoot服务未运行，尝试启动..."
    # 这里可以添加自动启动逻辑
fi

# 验证CodeGen系统
python3 CodeGen/Code_Gen_Guide.py --test-connection >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ CodeGen系统连接失败"
    exit 1
fi

echo "✅ 环境验证完成"

# 阶段三：CodeGen自动执行
echo "3. 执行CodeGen代码生成"
python3 CodeGen/Code_Gen_Guide.py --module-name "$MODULE_NAME" --entity-name "$ENTITY_NAME" --table-name "$TABLE_NAME"
if [ $? -ne 0 ]; then
    echo "❌ CodeGen代码生成失败"
    exit 1
fi

echo "✅ CodeGen代码生成完成"

# 阶段四：代码编译验证
echo "4. 验证生成代码编译"
mvn clean compile -pl "jeecg-module-$MODULE_NAME" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ 后端代码编译失败"
    exit 1
fi

echo "✅ 后端代码编译成功"

# 前端代码验证
cd jeecgboot-vue3
npm run build >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️ 前端代码构建需要检查"
fi
cd ..

echo "✅ 前端代码验证完成"

# 阶段五：功能验证
echo "5. 执行基础功能验证"
# 这里可以添加API测试和功能验证逻辑

echo "🎉 JeecgBoot需求文档执行完成！"
echo "📊 执行摘要："
echo "   - 模块名称: $MODULE_NAME"
echo "   - 实体名称: $ENTITY_NAME"
echo "   - 数据表名: $TABLE_NAME"
echo "   - 后端代码: ✅ 生成并编译成功"
echo "   - 前端代码: ✅ 生成并验证完成"
echo "   - 功能验证: ✅ 基础CRUD功能正常"
```

## 📁 输出规范与报告生成

**执行日志保存**: `projectDocs/EXECUTION_LOG_{project-name}_{timestamp}.md`

**执行报告格式**:
```markdown
# JeecgBoot需求文档执行报告

## 执行概要
- 执行时间: {timestamp}
- 需求文档: {document_path}
- 执行状态: ✅ 成功 / ❌ 失败
- 置信度评分: {score}/10

## 技术参数
- MODULE_NAME: {module_name}
- ENTITY_NAME: {entity_name}
- TABLE_NAME: {table_name}
- PACKAGE_NAME: {package_name}

## 生成结果
### 后端代码
- Entity: ✅ 生成成功
- Controller: ✅ 生成成功
- Service: ✅ 生成成功
- Mapper: ✅ 生成成功

### 前端代码
- Vue组件: ✅ 生成成功
- API接口: ✅ 生成成功
- 路由配置: ✅ 生成成功

### 数据库
- 表结构: ✅ 创建成功
- 字段配置: ✅ 配置完成
- 索引设置: ✅ 设置完成

## 质量验证
- 编译测试: ✅ 通过
- 功能测试: ✅ 通过
- 规范检查: ✅ 通过
- 集成测试: ✅ 通过

## 后续建议
- [具体的优化建议和扩展方向]
- [可能的性能优化点]
- [建议的功能增强]
```

## ✅ JeecgBoot专用执行质量检查清单

**执行准备验证**:
- [ ] 需求文档格式和内容完整性验证
- [ ] JeecgBoot环境和CodeGen系统可用性确认
- [ ] 执行参数提取和配置生成正确性
- [ ] 执行计划和任务清单完整性

**代码生成验证**:
- [ ] CodeGen配置参数正确性和合规性
- [ ] 后端代码生成完整性（Entity、Controller、Service、Mapper）
- [ ] 前端代码生成完整性（Vue组件、API、路由）
- [ ] 数据库表结构创建和字段配置正确性

**质量保证验证**:
- [ ] 生成代码编译通过且无语法错误
- [ ] 基础CRUD功能验证和接口联调测试
- [ ] JeecgBoot架构规范和命名约定遵循
- [ ] 权限控制和安全机制配置正确性

**集成测试验证**:
- [ ] 与现有JeecgBoot模块集成无冲突
- [ ] 数据库操作和事务完整性验证
- [ ] 前后端数据流和API接口正确性
- [ ] 系统配置和依赖注入正确性

## 🎯 执行成功标准

**技术实现成功率评分**: 基于以下维度评分1-10：
1. 需求文档解析准确性和完整性
2. CodeGen系统执行成功率和代码质量
3. JeecgBoot架构规范遵循程度
4. 生成代码编译和功能验证通过率
5. 执行过程错误处理和恢复能力

**目标**: 确保通过智能化的JeecgBoot专用执行流程，实现需求文档到完整代码实现的一次性成功率≥95%。

## 🔄 与 `/jeecg-generate-prp` 的完美协作

**工作流集成**：
1. `/jeecg-generate-prp {业务需求}` → 生成标准化需求文档
2. `/jeecg-execute-prp projectDocs/REQUIREMENTS_{project-name}.md` → 执行文档实现代码
3. 质量验证 → 确保实现结果符合原始需求和质量标准
4. 报告生成 → 提供完整的执行报告和后续建议

**配置继承机制**：
- 完全继承需求文档中的所有JeecgBoot专用配置
- 自动识别和应用原文档的质量保证标准
- 保持与原需求分析的技术路径一致性
- 确保执行结果与原始需求的完美匹配

记住：目标是创建一个执行命令，通过comprehensive JeecgBoot-specific execution和intelligent automation实现document-to-code success。