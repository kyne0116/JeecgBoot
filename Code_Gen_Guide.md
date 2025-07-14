# JeecgBoot Code_Gen 系统技术指南

> **文档定位**: 系统技术指南 - 为AI提供完整的系统理解和操控知识
> **配合文档**: Code_Gen_Agent.md (AI行为规范)

## 📋 系统概述

Code_Gen是JeecgBoot平台的智能代码生成系统，采用业务场景驱动的设计理念，通过标准化的命名规范和模板化的配置管理，实现从业务需求到完整CRUD代码的自动化生成。

### 核心设计理念
- **业务场景驱动**: Java实体名直接反映核心业务概念
- **标准化规范**: 严格的表名格式确保一致性
- **模板化配置**: 可复用的字段模板和配置模板
- **智能化处理**: 自动模块管理和数据字典匹配

## 🏗️ 系统架构

### 核心组件关系图
```
用户需求 → AI分析(Agent.md) → 系统执行(Guide.py) → 代码生成
    ↓           ↓                    ↓              ↓
 业务描述   需求解析+配置生成    模块管理+工作流    完整CRUD代码
    ↓           ↓                    ↓              ↓
 自然语言   标准化表名设计      Maven+JeecgBoot   Java+Vue代码
```

### 数据流转过程
```
1. 用户业务需求 
   ↓
2. AI需求分析 (使用Agent.md规范)
   ├── 业务系统识别 (hrms/crm/scm/oa/finance)
   ├── 标准表名设计 (us_模块_子模块_场景)
   ├── 字段结构设计 (基于field_templates.json)
   └── 配置文件生成 (基于Guide.json模板)
   ↓
3. 系统执行 (Guide.py脚本)
   ├── 格式验证 (严格4部分验证)
   ├── 实体名提取 (business_scenario → Java实体名)
   ├── 模块管理 (自动检查/创建Maven模块)
   ├── 数据字典匹配 (基于DICT.json)
   ├── 在线表单创建 (JeecgBoot API)
   ├── 数据库同步 (结构创建)
   └── 代码生成 (完整CRUD)
   ↓
4. 输出结果
   ├── Java实体类 (org.jeecg.modules.{模块}.{场景})
   ├── Controller/Service/Mapper
   ├── Vue前端组件
   └── 数据库表结构
```

## 📁 文件系统详解

### 核心文件功能矩阵

| 文件名 | 类型 | 功能定位 | AI操作权限 | 依赖关系 |
|--------|------|----------|------------|----------|
| **Code_Gen_Guide.py** | 执行引擎 | 主工作流脚本 | 🚫 只读 | 读取所有配置文件 |
| **Code_Gen_Agent.md** | AI规范 | AI行为指南 | ✅ AI学习 | 参考Guide.md |
| **Code_Gen_Guide.md** | 技术指南 | 系统说明文档 | ✅ AI学习 | 独立文档 |
| **Code_Gen_Config.json** | 系统配置 | 全局配置参数 | 🔧 可配置 | 被Guide.py读取 |
| **Code_Gen_Guide.json** | 基础模板 | 7个系统字段模板 | 🚫 禁止修改 | 复制创建业务配置 |
| **Code_Gen_field_templates.json** | 字段模板库 | 字段类型定义 | 📖 查询参考 | 生成业务字段配置 |
| **Code_Gen_DICT.json** | 数据缓存 | 数据字典缓存 | 🤖 自动管理 | 自动获取/更新 |

### 文件详细说明

#### 1. Code_Gen_Guide.py - 执行引擎
**功能**: 系统主工作流脚本
**核心函数**:
```python
extract_business_entity_from_table_name(table_name)
# 输入: "us_finance_invoice_sales"
# 验证: 4部分格式检查
# 输出: "sales" (业务场景名)

jeecg_complete_workflow(module_name, form_config)
# 完整工作流: 登录→创建→同步→生成
```

**AI交互点**: 
- 通过命令行调用: `python Code_Gen_Guide.py --module-name {模块} --form-config {配置文件}`
- 返回执行状态和结果信息

#### 2. Code_Gen_Config.json - 系统配置
**可配置项**:
```json
{
  "project": {
    "path_prefix": "/path/to/JeecgBoot"  // ✅ 可修改
  },
  "server": {
    "base_url": "http://localhost:8080/jeecg-boot",  // ✅ 可修改
    "username": "admin",  // ✅ 可修改
    "password": "123456"  // ✅ 可修改
  },
  "codegen": {
    "vue_style": "vue3",  // 🚫 固定不变
    "code_types": "controller,service,dao,mapper,entity,vue"  // 🚫 固定不变
  }
}
```

#### 3. Code_Gen_Guide.json - 基础模板
**模板结构**:
```json
{
  "head": {
    "tableName": "{{TABLE_NAME}}",     // 模板变量
    "tableTxt": "{{TABLE_DESCRIPTION}}" // 模板变量
  },
  "fields": [
    // 0-6: 7个固定系统字段 (🚫 绝对不可修改)
    {
      "orderNum": 0,
      "dbFieldName": "id",
      "dbFieldTxt": "Primary Key",
      // ... 完整系统字段定义
    }
    // 7+: 业务字段区域 (✅ AI在此添加业务字段)
  ]
}
```

#### 4. Code_Gen_field_templates.json - 字段模板库
**模板类型**:
```json
{
  "text_field": { /* 文本字段模板 */ },
  "number_field": { /* 数字字段模板 */ },
  "decimal_field": { /* 小数字段模板 */ },
  "date_field": { /* 日期字段模板 */ },
  "datetime_field": { /* 日期时间字段模板 */ },
  "textarea_field": { /* 多行文本字段模板 */ },
  "dict_select_field": { /* 数据字典下拉字段模板 */ },
  "dict_radio_field": { /* 数据字典单选字段模板 */ },
  "file_upload_field": { /* 文件上传字段模板 */ },
  "image_upload_field": { /* 图片上传字段模板 */ },
  "rich_text_field": { /* 富文本字段模板 */ },
  "phone_field": { /* 手机号字段模板 */ },
  "email_field": { /* 邮箱字段模板 */ }
}
```

**模板变量系统**:
- `{{FIELD_NAME}}`: 字段名称
- `{{FIELD_DESCRIPTION}}`: 字段描述  
- `{{ORDER_NUM}}`: 排序号 (从7开始)
- `{{NULLABLE}}`: 是否可空 (0/1)
- `{{REQUIRED}}`: 是否必填 (0/1)
- `{{DICT_CODE}}`: 数据字典编码 (仅字典字段)

## 🎯 命名规范系统

### 标准格式定义
**格式**: `us_{模块名称}_{子模块名称}_{推理业务需求场景}`

**验证规则**:
1. **前缀检查**: 必须以 `us_` 开头
2. **结构检查**: 必须恰好4个部分 (用下划线分隔)
3. **实体提取**: 第4部分作为Java实体名

### 业务系统映射表

| 系统标识 | 中文名称 | 关键词 | 实体示例 | 包名格式 |
|----------|----------|--------|----------|----------|
| **hrms** | 人力资源 | 员工、薪资、考勤、培训、绩效 | training, performance | org.jeecg.modules.hrms.{实体} |
| **crm** | 客户管理 | 客户、销售、合同、商机、服务 | service, opportunity | org.jeecg.modules.crm.{实体} |
| **scm** | 供应链 | 供应商、采购、库存、物流 | management, procurement | org.jeecg.modules.scm.{实体} |
| **oa** | 办公自动化 | 审批、流程、公告、会议、文档 | workflow, approval | org.jeecg.modules.oa.{实体} |
| **finance** | 财务管理 | 财务、会计、成本、预算、发票 | sales, budget | org.jeecg.modules.finance.{实体} |

### 命名转换算法
```python
# 表名分解
table_name = "us_finance_invoice_sales"
parts = table_name.split('_')  # ['us', 'finance', 'invoice', 'sales']

# 验证和提取
if len(parts) == 4 and parts[0] == 'us':
    module = parts[1]        # 'finance'
    sub_module = parts[2]    # 'invoice'  
    business_scenario = parts[3]  # 'sales'
    
    # 生成结果
    entity_name = business_scenario  # 'sales'
    package_name = f"org.jeecg.modules.{module}.{entity_name}"
    # 'org.jeecg.modules.finance.sales'
```

## 🔄 工作流程详解

### 完整业务流程

#### 阶段1: 需求分析 (AI执行)
```
输入: 用户业务描述
处理: 
  1. 业务系统识别 (基于关键词匹配)
  2. 标准表名设计 (us_模块_子模块_场景)
  3. 字段结构分析 (基于业务需求)
  4. 数据字典匹配 (智能语义匹配)
输出: 标准化的表名和字段需求
```

#### 阶段2: 配置生成 (AI执行)
```
输入: 标准化需求
处理:
  1. 复制基础模板 (Code_Gen_Guide.json)
  2. 替换表头变量 (表名、描述)
  3. 添加业务字段 (基于field_templates.json)
  4. 配置数据字典 (基于DICT.json)
输出: temp_{实体名}_config.json
```

#### 阶段3: 系统执行 (脚本自动)
```
输入: 配置文件路径
处理:
  1. 格式验证 (extract_business_entity_from_table_name)
  2. 模块管理 (检查/创建Maven模块)
  3. 登录认证 (获取JeecgBoot Token)
  4. 表单创建 (在线表单API)
  5. 数据库同步 (结构创建)
  6. 代码生成 (完整CRUD)
输出: 完整的功能模块代码
```

### 执行命令格式
```bash
python Code_Gen_Guide.py --module-name {模块名} --form-config {配置文件}

# 示例
python Code_Gen_Guide.py --module-name finance --form-config temp_sales_config.json
```

### 执行结果结构
```
生成路径: /jeecg-boot/jeecg-module-{模块名}/src/main/java/org/jeecg/modules/{模块名}/{实体名}/

文件结构:
├── entity/
│   └── {EntityName}.java           # 实体类
├── controller/
│   └── {EntityName}Controller.java # 控制器
├── service/
│   ├── I{EntityName}Service.java   # 服务接口
│   └── impl/
│       └── {EntityName}ServiceImpl.java # 服务实现
├── mapper/
│   └── {EntityName}Mapper.java     # 数据访问
└── vue/
    ├── {EntityName}List.vue        # 列表页面
    ├── {EntityName}Form.vue        # 表单页面
    └── {EntityName}Modal.vue       # 弹窗组件
```

## 🔧 技术实现细节

### 数据字典集成机制
```python
# 自动获取和匹配流程
1. 检查Code_Gen_DICT.json状态 (24小时过期机制)
2. 如过期，自动调用 python Code_Gen_Guide.py --dict
3. 加载数据字典到内存
4. 基于字段描述进行智能匹配:
   - 精确匹配: 字段名直接对应字典编码 (10分)
   - 部分匹配: 字段描述包含字典名称 (8分) 
   - 语义匹配: 相似度算法计算 (3-5分)
5. ≥8分自动应用，5-7分提示建议
```

### Maven模块管理机制
```python
# 自动模块创建流程
1. 检查路径: /jeecg-boot/jeecg-module-{模块名}
2. 如不存在，执行Maven命令:
   mvn archetype:generate \
     -DgroupId=org.jeecgframework.boot \
     -DartifactId=jeecg-module-{模块名} \
     -DarchetypeArtifactId=maven-archetype-quickstart \
     -DinteractiveMode=false
3. 更新父项目pom.xml添加模块引用
4. 更新启动项目pom.xml添加依赖
```

### 错误处理机制
```python
# 格式验证错误
if not table_name.startswith('us_'):
    raise ValueError("表名必须以 'us_' 开头")

if len(parts) != 4:
    raise ValueError("必须为 us_{模块}_{子模块}_{业务场景} 格式")

# 执行超时控制
subprocess.run(command, timeout=300)  # 5分钟超时

# 配置文件保护机制
backup_config()  # 备份原配置
try:
    replace_variables()  # 临时替换变量
    execute_generation()  # 执行生成
finally:
    restore_config()  # 恢复原配置
```

## 📊 系统监控点

### 关键执行节点
1. **格式验证**: 表名格式是否符合标准
2. **模块检查**: Maven模块是否存在/创建成功
3. **服务连接**: JeecgBoot服务是否可访问
4. **认证状态**: Token是否有效
5. **API响应**: 各API调用是否成功
6. **文件生成**: 代码文件是否正确生成

### 状态码含义
- **0**: 执行成功
- **1**: 格式验证失败
- **2**: 模块管理失败
- **3**: 服务连接失败  
- **4**: 认证失败
- **5**: API调用失败
- **6**: 代码生成失败

## 🎯 AI操作指南

### AI可执行操作
1. **✅ 需求分析**: 解析用户业务描述
2. **✅ 系统识别**: 基于关键词匹配业务系统
3. **✅ 表名设计**: 生成标准格式表名
4. **✅ 配置生成**: 创建temp_配置文件
5. **✅ 脚本调用**: 执行Code_Gen_Guide.py
6. **✅ 结果验证**: 检查生成结果

### AI禁止操作
1. **🚫 修改Guide.json**: 系统字段模板
2. **🚫 修改Guide.py**: 核心脚本逻辑
3. **🚫 修改field_templates.json**: 字段模板库
4. **🚫 直接操作数据库**: 数据库直接修改
5. **🚫 修改生成的代码**: 已生成的Java/Vue代码

### AI决策树
```
用户需求输入
    ↓
关键词识别 → 业务系统映射
    ↓
表名格式设计 → 格式验证
    ↓
字段需求分析 → 字段类型映射
    ↓
数据字典匹配 → 智能推荐
    ↓
配置文件生成 → 模板变量替换
    ↓
脚本执行命令 → 结果监控
    ↓
成功/失败处理 → 用户反馈
```

---

**📝 注意**: 本文档为AI提供系统理解基础，具体的AI行为规范请参考 `Code_Gen_Agent.md`