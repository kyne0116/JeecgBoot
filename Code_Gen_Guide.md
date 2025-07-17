# JeecgBoot Code_Gen 技术实现指南

> **文档定位**: Code_Gen 系统的技术实现指南和操作手册
> **配合文档**: Code_Gen_Agent.md (AI 行为规范和提示词框架)
> **目标用户**: AI 开发者、系统使用者、技术维护人员

---

## 📋 JSON 报文结构说明

### 🎯 完整 JSON 结构要求

基于 JeecgBoot 在线表单 API 的要求，JSON 配置文件必须包含以下完整结构：

#### **head 对象（必需）**

```json
{
  "head": {
    "tableName": "us_模块_子模块_实体", // 表名，必须符合命名规范
    "tableTxt": "表描述", // 表描述，不能为空
    "tableType": 1, // 表类型，必须是整数1
    "formCategory": "temp", // 表单类别，temp或main
    "idType": "UUID", // 主键类型
    "isCheckbox": "Y", // 是否支持复选框
    "themeTemplate": "normal", // 主题模板
    "formTemplate": "1", // 表单模板
    "scroll": 1, // 是否滚动，必须是整数
    "isPage": "Y", // 是否分页
    "isTree": "N", // 是否树形结构
    "extConfigJson": "{...}", // 扩展配置JSON字符串
    "isDesForm": "N", // 是否设计表单
    "desFormCode": "" // 设计表单代码
  }
}
```

#### **fields 数组（必需）**

每个字段对象必须包含以下属性：

```json
{
  "dbFieldName": "字段名", // 数据库字段名
  "dbFieldTxt": "字段描述", // 字段描述
  "queryShowType": "text", // 查询显示类型
  "queryDictTable": "", // 查询字典表
  "queryDictField": "", // 查询字典字段
  "queryDictText": "", // 查询字典文本
  "queryDefVal": "", // 查询默认值
  "queryConfigFlag": "0", // 查询配置标志
  "mainTable": "", // 主表
  "mainField": "", // 主字段
  "fieldHref": "", // 字段链接
  "fieldValidType": "", // 字段验证类型
  "fieldMustInput": "0", // 字段必须输入
  "dictTable": "", // 数据字典表
  "dictField": "", // 数据字典字段
  "dictText": "", // 数据字典文本
  "isShowForm": "0", // 是否在表单中显示
  "isShowList": "0", // 是否在列表中显示
  "sortFlag": "0", // 排序标志
  "isReadOnly": "0", // 是否只读
  "fieldShowType": "text", // 字段显示类型
  "fieldLength": 200, // 字段长度
  "isQuery": "0", // 是否可查询
  "queryMode": "single", // 查询模式
  "fieldDefaultValue": "", // 字段默认值
  "converter": "", // 转换器
  "fieldExtendJson": "", // 字段扩展JSON
  "fieldConfig": "", // 字段配置
  "dbLength": 36, // 数据库字段长度
  "dbPointLength": 0, // 小数点长度
  "dbDefaultVal": "", // 数据库默认值
  "dbType": "string", // 数据库字段类型
  "dbIsKey": "1", // 是否主键（字符串）
  "dbIsNull": "0", // 是否允许为空（字符串）
  "dbIsPersist": "1", // 是否持久化（关键字段！）
  "orderNum": 0 // 排序号
}
```

#### **其他必需数组**

```json
{
  "indexs": [], // 索引数组
  "deleteFieldIds": [], // 删除字段ID数组
  "deleteIndexIds": [] // 删除索引ID数组
}
```

### 🚨 关键注意事项

1. **数据类型严格要求**：

   - `tableType`: 必须是整数 1，不能是字符串"1"
   - `scroll`: 必须是整数 0 或 1，不能是字符串
   - `dbIsKey`, `dbIsNull`, `dbIsPersist`: 必须是字符串"0"或"1"

2. **必需字段不能缺失**：

   - `dbIsPersist`: 这是关键字段，缺失会导致 API 调用失败
   - 所有查询相关字段：`queryShowType`, `queryDictTable`等
   - 所有显示相关字段：`fieldShowType`, `isShowForm`等

3. **系统字段要求**：
   - 必须包含 7 个系统字段：id, create_by, create_time, update_by, update_time, sys_org_code, del_flag
   - 系统字段的 orderNum 从 0 开始递增
   - 业务字段的 orderNum 从 7 开始

## 📋 系统架构概览

### 🔄 完整工作流程

```
用户业务需求 → AI需求分析 → 变量提取 → 配置生成 → 脚本执行 → 代码生成 → 模块集成
     ↓             ↓          ↓         ↓         ↓         ↓         ↓
   自然语言    关键词识别   核心变量   JSON配置   Python脚本  完整CRUD   项目集成
```

### 🎯 文件角色定位

| 文件名称              | 角色定位     | 主要职责                                              | 功能边界                        |
| --------------------- | ------------ | ----------------------------------------------------- | ------------------------------- |
| **Code_Gen_Guide.py** | 执行工具     | 严格按照 JeecgBoot 官方 API 规范执行，不进行智能分析  | 只负责 API 调用，不做业务推理   |
| **Code_Gen_Guide.md** | 技术实现指南 | 脚本使用方法、配置文件结构、数据字典获取流程          | 技术实现、系统操作、问题排查    |
| **Code_Gen_Agent.md** | AI 智能框架  | AI 推理策略、智能分析、数据字典匹配决策、配置文件生成 | AI 理解需求、智能分析、决策制定 |

### 📋 文档协同关系

- **AI 推理阶段**: 主要参考 **Code_Gen_Agent.md**，进行业务需求分析和变量提取
- **技术实现阶段**: 主要参考 **Code_Gen_Guide.md**，进行脚本调用和配置管理
- **问题排查阶段**: 两个文档结合使用，从 AI 推理到技术实现全链路分析

### 🔄 工作流程

1. **AI 获取数据字典**: 调用 `python3 Code_Gen_Guide.py --dict` 获取最新数据字典
2. **AI 智能分析**: 基于用户需求和数据字典进行智能匹配分析
3. **AI 生成配置**: 生成包含正确字段配置的临时 JSON 文件
4. **脚本执行**: 调用 `Code_Gen_Guide.py` 执行 API 请求工作流

**重要提醒**: 本文档专注于技术实现细节，AI 推理策略和业务分析方法请参考 Code_Gen_Agent.md 文档。

### 文件依赖关系

```mermaid
graph TD
    A[Code_Gen_Guide.py] --> B[Code_Gen_Config.json]
    A --> C[Code_Gen_Guide.json]
    A --> D[Code_Gen_field_templates.json]
    A --> E[Code_Gen_DICT.json]

    C --> F[temp_{entity}_config.json]
    D --> F
    E --> F

    A --> G[jeecg-boot项目]
    F --> A

    A --> H[生成的代码文件]
    G --> H
```

### 核心组件说明

| 组件名称                          | 类型       | 功能定位     | 主要职责                             |
| --------------------------------- | ---------- | ------------ | ------------------------------------ |
| **Code_Gen_Guide.py**             | 执行引擎   | 主工作流脚本 | 登录、创建表单、同步数据库、生成代码 |
| **Code_Gen_Config.json**          | 系统配置   | 全局参数配置 | 服务器地址、认证信息、项目路径       |
| **Code_Gen_Guide.json**           | 配置模板   | 标准表单模板 | 7 个系统字段定义、表单基础结构       |
| **Code_Gen_field_templates.json** | 字段模板库 | 字段类型定义 | 各种字段类型的完整配置模板           |
| **Code_Gen_DICT.json**            | 数据字典   | 字典数据缓存 | 系统数据字典的本地缓存               |

---

## 🚀 Code_Gen_Guide.py 脚本使用指南

### 📖 脚本概述

**Code_Gen_Guide.py** 是 CodeGen 系统的核心执行引擎，负责接收 AI 提取的核心变量，处理配置文件，并执行完整的代码生成流程。

### 核心功能

#### 智能编译与模块集成

- **自动创建 pom.xml**：为新生成的模块自动创建标准的 Maven 配置文件
- **智能编译策略**：优先编译新生成的模块，使用 `mvn clean install -DskipTests` 确保模块安装到本地仓库
- **编译结果验证**：验证 target/classes 目录和 jar 包是否正确生成
- **后端服务管理**：检查服务状态，验证新模块是否已加载

#### 问题解决能力

针对常见的 **404 错误问题**（模块 Controller 没有被 Spring Boot 正确加载）进行了改进：

- **根本原因**：模块代码生成正确，但没有被正确编译和安装到 Maven 本地仓库
- **解决方案**：自动重新编译模块并重启服务建议，确保新编译的模块被加载

### 🔧 脚本调用方式

#### 基本调用格式

```bash
python Code_Gen_Guide.py [OPTIONS]
```

#### 必需的输入变量

脚本需要接收以下四个核心变量：

| 变量名称                | 类型   | 描述           | 示例值                                                       |
| ----------------------- | ------ | -------------- | ------------------------------------------------------------ |
| **PROJECT_PATH_PREFIX** | String | 项目根路径前缀 | `从Code_Gen_Config.json读取project.path_prefix`              |
| **PROJECT_PATH**        | String | 完整项目路径   | `{PREFIX}/jeecg-boot/jeecg-boot-module/jeecg-module-finance` |
| **ENTITY_NAME**         | String | 实体名称       | `management`                                                 |
| **PACKAGE_NAME**        | String | 包名           | `org.jeecg.modules.finance.invoice`                          |

#### 命令行参数详解

| 参数                    | 必填 | 类型   | 描述             | 示例                            |
| ----------------------- | ---- | ------ | ---------------- | ------------------------------- |
| `--module-name`         | ✅   | String | 目标模块名称     | `finance`                       |
| `--form-config`         | ✅   | String | 配置文件路径     | `temp_management_config.json`   |
| `--dict`                | ❌   | Flag   | 获取最新数据字典 | 无参数                          |
| `--validate-table-name` | ❌   | String | 验证表名格式     | `us_finance_invoice_management` |
| `--fix-table-name`      | ❌   | String | 自动修复表名格式 | `biz_product_management`        |
| `--compile-only`        | ❌   | Flag   | 仅执行编译操作   | 无参数                          |
| `--skip-compile`        | ❌   | Flag   | 跳过编译步骤     | 无参数                          |
| `--help`                | ❌   | Flag   | 显示帮助信息     | 无参数                          |

### 📚 数据字典获取流程

#### 🚀 **外部用户必读：获取最新数据字典**

**重要提醒**: 在使用 AI 进行代码生成之前，必须先执行以下命令获取最新的系统数据字典：

```bash
# 获取最新数据字典并保存到Code_Gen_DICT.json
python3 Code_Gen_Guide.py --dict
```

**执行步骤**：

1. **打开终端/命令行**，切换到 JeecgBoot 项目根目录
2. **确保 JeecgBoot 服务正在运行** (http://localhost:8080/jeecg-boot)
3. **执行数据字典获取命令**：
   ```bash
   python3 Code_Gen_Guide.py --dict
   ```
4. **等待执行完成**，看到 "🎉 数据字典获取完成！" 提示

**执行结果**：

- ✅ 自动登录 JeecgBoot 系统
- ✅ 调用数据字典 API 获取最新数据
- ✅ 保存到`Code_Gen_DICT.json`文件
- ✅ 输出数据字典条目数量和预览信息

**成功标志**：

- 项目根目录下生成/更新了 `Code_Gen_DICT.json` 文件
- 控制台显示类似 "总共获取到 XX 条数据字典记录" 的信息

**数据字典文件结构**：

```json
[
  {
    "dictCode": "sex",
    "dictName": "性别",
    "dictItems": [
      { "itemText": "男", "itemValue": "1" },
      { "itemText": "女", "itemValue": "2" }
    ]
  },
  {
    "dictCode": "yes_no",
    "dictName": "是否",
    "dictItems": [
      { "itemText": "是", "itemValue": "Y" },
      { "itemText": "否", "itemValue": "N" }
    ]
  }
]
```

#### AI 使用数据字典的流程

1. **获取数据字典**: 调用`--dict`参数获取最新数据字典
2. **分析用户需求**: 理解用户的业务字段需求
3. **智能匹配**: 将业务字段与数据字典进行语义匹配
4. **生成配置**: 在临时 JSON 文件中应用匹配的数据字典配置
5. **执行脚本**: 使用生成的配置文件调用脚本执行

#### 🧠 数据字典智能匹配逻辑

**匹配算法实现**：

```yaml
字段匹配流程:
  1. 精确匹配检查:
     - 字段描述 == 数据字典名称 → 置信度 100%
     - 示例: "性别" → dictCode "sex"

  2. 语义匹配检查:
     - 关键词相似度分析 → 置信度 70-90%
     - 示例: "状态" → dictCode "status", "state"

  3. 模糊匹配检查:
     - 部分关键词匹配 → 置信度 50-70%
     - 示例: "用户类型" → dictCode "user_type", "type"

  4. 字段类型决策:
     - 置信度 >= 70%: 使用 dict_select_field
     - 置信度 >= 50%: 提示用户确认
     - 置信度 < 50%: 使用普通字段类型
```

**数据字典字段配置示例**：

```json
{
  "orderNum": 8,
  "dbFieldName": "status",
  "dbFieldTxt": "状态",
  "dbType": "string",
  "dbLength": 20,
  "fieldShowType": "select",
  "dictField": "invoice_status", // 匹配的数据字典编码
  "isShowForm": "1",
  "isShowList": "1"
}
```

### 🔄 脚本执行流程

#### 步骤 1: 变量接收与验证

```python
def receive_core_variables():
    """接收并验证核心变量"""
    # 1. 从命令行参数或配置文件读取核心变量
    # 2. 验证变量格式和完整性
    # 3. 打印变量值供调试使用
    # 4. 返回验证通过的变量集合
```

#### 步骤 2: 配置文件处理

```python
def process_config_files():
    """处理配置文件"""
    # 1. 读取Code_Gen_Config.json系统配置
    # 2. 加载temp_*_config.json表单配置
    # 3. 临时修改jeecg_config.properties
    # 4. 验证配置文件完整性
```

#### 步骤 3: 环境检查

```python
def check_environment():
    """检查执行环境"""
    # 1. 验证JeecgBoot服务状态
    # 2. 检查Maven配置
    # 3. 验证数据库连接
    # 4. 确认项目路径存在
```

#### 步骤 4: 模块管理

```python
def manage_module():
    """管理Maven模块"""
    # 1. 检查目标模块是否存在
    # 2. 如不存在则创建Maven模块
    # 3. 更新父级pom.xml
    # 4. 更新系统依赖配置
```

#### 步骤 5: 代码生成执行

```python
def execute_code_generation():
    """执行代码生成"""
    # 1. 登录JeecgBoot系统
    # 2. 创建在线表单
    # 3. 同步数据库结构
    # 4. 生成完整CRUD代码
```

#### 步骤 6: 编译与验证

```python
def compile_and_verify():
    """编译模块并验证结果"""
    # 1. 自动创建模块pom.xml（如果不存在）
    # 2. 执行Maven编译：mvn clean install -DskipTests
    # 3. 验证target/classes目录和jar包
    # 4. 检查Maven本地仓库中的jar包
```

#### 步骤 7: 配置恢复

```python
def restore_configuration():
    """恢复配置文件"""
    # 1. 恢复jeecg_config.properties为模板状态
    # 2. 清理临时配置文件
    # 3. 输出执行结果报告
    # 4. 提供服务重启建议
```

### 💡 具体使用示例

#### 示例 1: 生成财务发票管理模块

```bash
# 前置条件: 已有temp_management_config.json配置文件
python Code_Gen_Guide.py --module-name finance --form-config temp_management_config.json

# 执行过程:
# 1. 读取核心变量: MODULE_NAME=finance, ENTITY_NAME=management
# 2. 验证表名: us_finance_invoice_management
# 3. 创建/检查jeecg-module-finance模块
# 4. 登录JeecgBoot系统
# 5. 创建在线表单
# 6. 同步数据库结构
# 7. 生成完整CRUD代码

# 预期输出:
# ✅ 模块检查完成: jeecg-module-finance
# ✅ 登录成功: admin
# ✅ 表单创建成功: us_finance_invoice_management
# ✅ 数据库同步完成
# ✅ 代码生成完成: org.jeecg.modules.finance.invoice
```

#### 示例 2: 生成人力资源培训模块

```bash
python Code_Gen_Guide.py --module-name hrms --form-config temp_training_config.json

# 核心变量:
# PROJECT_PATH_PREFIX: 从Code_Gen_Config.json读取project.path_prefix
# PROJECT_PATH: {PREFIX}/jeecg-boot/jeecg-boot-module/jeecg-module-hrms
# ENTITY_NAME: training
# PACKAGE_NAME: org.jeecg.modules.hrms.employee
```

#### 示例 3: 更新数据字典

```bash
python Code_Gen_Guide.py --dict

# 执行过程:
# 1. 连接JeecgBoot系统
# 2. 获取最新数据字典
# 3. 更新Code_Gen_DICT.json缓存
# 4. 输出更新结果
```

#### 示例 4: 验证和修复表名

```bash
# 验证表名格式
python Code_Gen_Guide.py --validate-table-name "biz_product_management"
# 输出: ❌ 表名格式错误，建议修改为: us_business_product_management

# 自动修复表名
python Code_Gen_Guide.py --fix-table-name "biz_product_management"
# 输出: ✅ 表名已修复为: us_business_product_management
```

## 📋 命名规范参考

**说明**: 以下命名规范供技术实现参考，详细的 AI 推理策略请参考 Code_Gen_Agent.md 文档。

### 🎯 标准命名格式

- **表名格式**: `us_{模块名}_{子模块名}_{业务场景}`
- **包名格式**: `org.jeecg.modules.{模块名}.{子模块名}`
- **实体名格式**: `{业务场景}` (Java 驼峰命名)

### 📋 命名格式示例

```bash
# 基本格式示例
us_finance_invoice_management     → org.jeecg.modules.finance.invoice, 实体: Management
us_hrms_employee_training         → org.jeecg.modules.hrms.employee, 实体: Training
us_crm_customer_service           → org.jeecg.modules.crm.customer, 实体: Service
```

### 🔧 命名组件说明

- **模块名**: 顶级业务领域 (finance, hrms, crm, scm, oa)
- **子模块名**: 具体功能模块 (invoice, employee, customer 等)
- **业务场景**: 具体业务对象/操作 (management, training, service 等)

**注意**:

- 详细的命名推理策略和业务分析方法请参考 **Code_Gen_Agent.md** 文档
- 三核心变量的完整定义和使用规范请参考 **Code_Gen_Variables.md** 文档

**主要函数**:

```python
def extract_business_entity_from_table_name(table_name):
    """从表名中提取业务实体名，严格遵循us_{模块}_{子模块}_{场景}格式"""
    # 输入: "us_finance_invoice_sales"
    # 输出: "sales"

def jeecg_complete_workflow(module_name, form_config):
    """完整工作流程: 登录→创建表单→同步数据库→生成代码"""
    # 1. 登录JeecgBoot系统
    # 2. 创建在线表单
    # 3. 同步数据库结构
    # 4. 生成完整代码

def load_config():
    """加载系统配置"""
    # 加载Code_Gen_Config.json配置文件
    # 合并用户配置和默认配置
```

**命令行参数**:

```bash
python Code_Gen_Guide.py [OPTIONS]

OPTIONS:
  --module-name TEXT          模块名称 (hrms/crm/scm/oa/finance/business)
  --form-config TEXT          表单配置文件路径
  --dict                      更新数据字典缓存
  --validate-table-name TEXT  验证表名格式并提供修复建议
  --fix-table-name TEXT       自动修复表名格式
  --help                      显示帮助信息
```

**使用示例**:

```bash
# 生成代码
python Code_Gen_Guide.py --module-name finance --form-config temp_sales_config.json

# 更新数据字典
python Code_Gen_Guide.py --dict

# 验证表名格式
python Code_Gen_Guide.py --validate-table-name "biz_product_management"

# 自动修复表名
python Code_Gen_Guide.py --fix-table-name "biz_product_management"
```

---

## 📁 Code*Gen*\*.json 配置文件详解

### 1. Code_Gen_Config.json - 系统全局配置

#### 📖 配置文件概述

**Code_Gen_Config.json** 是系统的全局配置文件，控制脚本的执行行为、服务器连接、项目路径等核心参数。

#### 🔧 完整配置结构

```json
{
  "project": {
    "path_prefix": "{{PROJECT_ROOT_PATH}}",
    "module_template": "jeecg-module-{module_name}",
    "backup_enabled": true
  },
  "server": {
    "base_url": "http://localhost:8080/jeecg-boot",
    "username": "admin",
    "password": "123456",
    "verify_ssl": false
  },
  "timeouts": {
    "login": 10,
    "create": 30,
    "sync": 30,
    "codegen": 60,
    "connection": 5
  },
  "codegen": {
    "vue_style": "vue3",
    "code_types": "controller,service,dao,mapper,entity,vue",
    "package_style": "service",
    "jsp_mode": "one",
    "jform_type": "1"
  },
  "compilation": {
    "enabled": true,
    "maven_command": "mvn",
    "compile_args": ["clean", "install", "-DskipTests"],
    "timeout": 300,
    "verify_target_classes": true,
    "auto_create_pom": true,
    "prefer_module_compilation": true
  },
  "logging": {
    "level": "INFO",
    "file_enabled": true,
    "console_enabled": true
  }
}
```

#### 📋 配置项详细说明

##### Project 配置

| 配置项                    | 类型    | 描述                     | 示例值                       | 必填 |
| ------------------------- | ------- | ------------------------ | ---------------------------- | ---- |
| `project.path_prefix`     | String  | JeecgBoot 项目根路径前缀 | `{{PROJECT_ROOT_PATH}}`      | ✅   |
| `project.module_template` | String  | 模块目录命名模板         | `jeecg-module-{module_name}` | ❌   |
| `project.backup_enabled`  | Boolean | 是否启用配置备份         | `true`                       | ❌   |

##### Server 配置

| 配置项              | 类型    | 描述                 | 示例值                             | 必填 |
| ------------------- | ------- | -------------------- | ---------------------------------- | ---- |
| `server.base_url`   | String  | JeecgBoot 服务器地址 | `http://localhost:8080/jeecg-boot` | ✅   |
| `server.username`   | String  | 登录用户名           | `admin`                            | ✅   |
| `server.password`   | String  | 登录密码             | `123456`                           | ✅   |
| `server.verify_ssl` | Boolean | 是否验证 SSL 证书    | `false`                            | ❌   |

##### CodeGen 配置

| 配置项                  | 类型   | 描述         | 默认值                                     | 必填 |
| ----------------------- | ------ | ------------ | ------------------------------------------ | ---- |
| `codegen.vue_style`     | String | Vue 版本选择 | `vue3`                                     | ❌   |
| `codegen.code_types`    | String | 生成代码类型 | `controller,service,dao,mapper,entity,vue` | ❌   |
| `codegen.package_style` | String | 包结构风格   | `service`                                  | ❌   |

##### Compilation 配置

| 配置项                                  | 类型    | 描述               | 默认值                                | 必填 |
| --------------------------------------- | ------- | ------------------ | ------------------------------------- | ---- |
| `compilation.enabled`                   | Boolean | 是否启用自动编译   | `true`                                | ❌   |
| `compilation.maven_command`             | String  | Maven 命令         | `mvn`                                 | ❌   |
| `compilation.compile_args`              | Array   | 编译参数           | `["clean", "install", "-DskipTests"]` | ❌   |
| `compilation.timeout`                   | Integer | 编译超时时间（秒） | `300`                                 | ❌   |
| `compilation.verify_target_classes`     | Boolean | 验证编译结果       | `true`                                | ❌   |
| `compilation.auto_create_pom`           | Boolean | 自动创建 pom.xml   | `true`                                | ❌   |
| `compilation.prefer_module_compilation` | Boolean | 优先编译单个模块   | `true`                                | ❌   |

#### 🌍 环境差异配置

##### Mac 环境配置示例

```json
{
  "project": {
    "path_prefix": "{{PROJECT_ROOT_PATH}}"
  }
}
```

##### Windows 环境配置示例

```json
{
  "project": {
    "path_prefix": "D:\\Dev\\Workspace\\JeecgBoot"
  }
}
```

#### ⚡ PROJECT_PATH_PREFIX 的作用机制

**PROJECT_PATH_PREFIX** 是整个系统的核心配置，影响所有路径相关的操作：

1. **模块路径生成**: `{PROJECT_PATH_PREFIX}/jeecg-boot/jeecg-boot-module/jeecg-module-{MODULE_NAME}`
2. **代码输出路径**: 基于 PROJECT_PATH_PREFIX 确定代码生成的目标目录
3. **Maven 配置更新**: 用于更新父级 pom.xml 和依赖配置的路径
4. **临时文件处理**: 临时配置文件的存储和清理路径

### 2. Code_Gen_Guide.json - 标准表单模板

#### 📖 模板文件概述

**Code_Gen_Guide.json** 是标准表单配置模板，包含 JeecgBoot 系统必需的 7 个系统字段和表单基础结构。AI 推理生成的 temp\_\*\_config.json 文件都基于此模板创建。

#### 🔧 文件结构详解

**结构说明**:

```json
{
  "head": {
    "tableName": "{{TABLE_NAME}}", // 模板变量-表名
    "tableTxt": "{{TABLE_DESCRIPTION}}", // 模板变量-表描述
    "tableType": "1", // 固定值-表类型
    "tableVersion": "1", // 固定值-表版本
    "idType": "UUID", // 固定值-主键类型
    "isCheckbox": "Y", // 固定值-是否支持复选
    "isDbSynch": "Y", // 固定值-数据库同步
    "isPage": "Y", // 固定值-是否分页
    "isTree": "N", // 固定值-是否树形
    "queryMode": "single", // 固定值-查询模式
    "relationType": "0" // 固定值-关联类型
  },
  "fields": [
    // 1-7: 7个系统字段 (按orderNum顺序排列，不可修改)
    {
      "orderNum": 1,
      "dbFieldName": "id",
      "dbFieldTxt": "主键",
      "dbType": "VARCHAR",
      "dbIsKey": 1,
      "dbIsNull": 0
    },
    {
      "orderNum": 2,
      "dbFieldName": "create_by",
      "dbFieldTxt": "创建人"
    },
    // ... 其他5个系统字段 (create_time, update_by, update_time, sys_org_code, del_flag)

    // 8+: 业务字段区域 (可基于BUSINESS_FIELD模板添加字段)
    {
      "orderNum": 8,
      "dbFieldName": "{{BUSINESS_FIELD}}",
      "dbFieldTxt": "{{BUSINESS_FIELD_DESC}}"
    }
  ]
}
```

**使用规则**:

- 🚫 **禁止修改**: `head`部分的固定值字段
- 🚫 **禁止修改**: `fields`数组中 orderNum 1-7 的系统字段（按顺序排列）
- ✅ **允许替换**: `{{TABLE_NAME}}`和`{{TABLE_DESCRIPTION}}`模板变量
- ✅ **允许基于模板添加**: orderNum 8+的业务字段（基于`{{BUSINESS_FIELD}}`模板）

**重要提醒：保持模板通用性**

`Code_Gen_Guide.json` 必须保持通用的变量占位符格式，不能硬编码具体值：

```json
// ✅ 正确：使用通用占位符
{
  "head": {
    "tableName": "{{TABLE_NAME}}",
    "tableTxt": "{{TABLE_DESCRIPTION}}"
  },
  "fields": [
    // 7个系统字段按orderNum 1-7顺序排列
    { "orderNum": 1, "dbFieldName": "id" },
    { "orderNum": 2, "dbFieldName": "create_by" },
    // 业务字段基于模板添加
    {
      "orderNum": 8,
      "dbFieldName": "{{BUSINESS_FIELD}}",
      "dbFieldTxt": "{{BUSINESS_FIELD_DESC}}"
    }
  ]
}
```

硬编码具体值会破坏模板的通用性，使其只能用于特定场景。

#### 📋 Head 部分配置说明

| 字段名称       | 类型   | 描述         | 可修改 | 说明                         |
| -------------- | ------ | ------------ | ------ | ---------------------------- |
| `tableName`    | String | 数据库表名   | ✅     | 由 AI 推理的 TABLE_NAME 替换 |
| `tableTxt`     | String | 表的中文描述 | ✅     | 由 AI 推理的业务描述替换     |
| `tableType`    | String | 表类型       | ❌     | 固定值"1"，表示普通表        |
| `tableVersion` | String | 表版本       | ❌     | 固定值"1"                    |
| `idType`       | String | 主键类型     | ❌     | 固定值"UUID"                 |
| `isCheckbox`   | String | 是否支持复选 | ❌     | 固定值"Y"                    |
| `isDbSynch`    | String | 数据库同步   | ❌     | 固定值"Y"                    |
| `isPage`       | String | 是否分页     | ❌     | 固定值"Y"                    |
| `isTree`       | String | 是否树形     | ❌     | 固定值"N"                    |
| `queryMode`    | String | 查询模式     | ❌     | 固定值"single"               |
| `relationType` | String | 关联类型     | ❌     | 固定值"0"                    |

#### 📋 Fields 部分配置说明

**系统字段（orderNum 1-7）**：按顺序排列，不可修改

| orderNum | 字段名称       | 中文名称 | 说明                    |
| -------- | -------------- | -------- | ----------------------- |
| 1        | `id`           | 主键     | UUID 主键，必须字段     |
| 2        | `create_by`    | 创建人   | 记录创建者              |
| 3        | `create_time`  | 创建时间 | 记录创建时间            |
| 4        | `update_by`    | 更新人   | 记录最后更新者          |
| 5        | `update_time`  | 更新时间 | 记录最后更新时间        |
| 6        | `sys_org_code` | 组织机构 | 组织机构代码            |
| 7        | `del_flag`     | 删除标志 | 逻辑删除标志，默认值"0" |

**业务字段（orderNum 8+）**：基于 `{{BUSINESS_FIELD}}` 模板添加

#### 🔧 如何基于模板生成 temp\_\*\_config.json

##### 步骤 1: 复制基础模板

```python
def copy_base_template():
    """复制Code_Gen_Guide.json作为基础模板"""
    with open('Code_Gen_Guide.json', 'r', encoding='utf-8') as f:
        template = json.load(f)
    return template
```

##### 步骤 2: 替换模板变量

```python
def replace_template_variables(template, table_name, table_description):
    """替换{{TABLE_NAME}}和{{TABLE_DESCRIPTION}}"""
    template['head']['tableName'] = table_name
    template['head']['tableTxt'] = table_description
    return template
```

##### 步骤 3: 添加业务字段

```python
def add_business_fields(template, fields_config):
    """添加orderNum>=7的业务字段"""
    order_num = 7  # 从7开始
    for field in fields_config:
        field_config = create_field_config(field, order_num)
        template['fields'].append(field_config)
        order_num += 1
    return template
```

#### ⚡ 参数传递协同机制

**配置文件与脚本执行的协同关系**:

1. **AI 推理阶段**: Code_Gen_Agent.md 指导 AI 从用户需求中提取核心变量
2. **配置生成阶段**: 基于 Code_Gen_Guide.json 模板和 AI 推理结果生成 temp_config.json
3. **脚本执行阶段**: Code_Gen_Guide.py 读取配置文件并执行代码生成
4. **变量传递链路**: 用户需求 → AI 推理 → 核心变量 → 配置文件 → 脚本执行

### 3. Code_Gen_field_templates.json - 字段模板库

#### 📖 字段模板概述

**Code_Gen_field_templates.json** 提供 13 种标准字段类型的完整配置模板，AI 在生成业务字段时会根据字段语义智能选择合适的模板类型。

#### 🔧 13 种标准字段类型定义

```json
{
  "text_field": {
    "queryShowType": "text",
    "fieldShowType": "text",
    "dbType": "string",
    "dbLength": 100,
    "dbPointLength": 0,
    "dbIsNull": "1",
    "isShowForm": "1",
    "isShowList": "1",
    "fieldMustInput": "0"
  },
  "number_field": {
    "queryShowType": "text",
    "fieldShowType": "text",
    "dbType": "int",
    "dbLength": 10,
    "dbPointLength": 0,
    "dbIsNull": "1",
    "isShowForm": "1",
    "isShowList": "1",
    "fieldMustInput": "0"
  },
  "dict_select_field": {
    "queryShowType": "select",
    "fieldShowType": "select",
    "dbType": "string",
    "dbLength": 50,
    "dbPointLength": 0,
    "dbIsNull": "1",
    "isShowForm": "1",
    "isShowList": "1",
    "fieldMustInput": "0",
    "dictField": "{{DICT_CODE}}"
  }
}
```

#### 📋 字段类型详细说明

| 类型名称             | 用途         | 数据库类型 | 前端组件        | 特殊配置       | 应用场景               |
| -------------------- | ------------ | ---------- | --------------- | -------------- | ---------------------- |
| `text_field`         | 文本字段     | string     | input           | 无             | 姓名、编号、标题等     |
| `number_field`       | 数字字段     | int        | input-number    | 无             | 数量、年龄、排序等     |
| `decimal_field`      | 小数字段     | decimal    | input-number    | 精度设置       | 金额、比率、分数等     |
| `date_field`         | 日期字段     | date       | date-picker     | 无             | 生日、截止日期等       |
| `datetime_field`     | 日期时间字段 | datetime   | datetime-picker | 无             | 创建时间、预约时间等   |
| `textarea_field`     | 多行文本字段 | text       | textarea        | 行数设置       | 描述、备注、说明等     |
| `dict_select_field`  | 字典下拉字段 | string     | select          | 需要 dictField | 状态、类型、分类等     |
| `dict_radio_field`   | 字典单选字段 | string     | radio           | 需要 dictField | 性别、是否、级别等     |
| `file_upload_field`  | 文件上传字段 | string     | upload          | 文件类型限制   | 附件、文档、证书等     |
| `image_upload_field` | 图片上传字段 | string     | upload          | 图片限制       | 头像、照片、图标等     |
| `rich_text_field`    | 富文本字段   | text       | rich-editor     | 无             | 详细描述、公告内容等   |
| `phone_field`        | 手机号字段   | string     | input           | 格式验证       | 联系电话、紧急联系人等 |
| `email_field`        | 邮箱字段     | string     | input           | 格式验证       | 邮箱地址、通知邮箱等   |

#### 🎯 字段模板的应用场景和选择原则

##### 基础字段选择原则

```yaml
文本类数据:
  - 短文本(≤100字符): text_field
  - 长文本(>100字符): textarea_field
  - 富文本内容: rich_text_field

数值类数据:
  - 整数: number_field
  - 小数: decimal_field (设置精度)

时间类数据:
  - 仅日期: date_field
  - 日期+时间: datetime_field

选择类数据:
  - 下拉选择: dict_select_field
  - 单选按钮: dict_radio_field

文件类数据:
  - 通用文件: file_upload_field
  - 图片文件: image_upload_field

格式验证数据:
  - 手机号: phone_field
  - 邮箱: email_field
```

**注意**: 字段类型的智能推理策略请参考 Code_Gen_Agent.md 文档。

### 5. Code_Gen_DICT.json - 数据字典

**功能**: 系统数据字典的本地缓存，用于字段类型匹配

**数据结构**:

```json
[
  {
    "dictCode": "sex",
    "dictName": "性别",
    "dictItems": [
      { "itemValue": "1", "itemText": "男" },
      { "itemValue": "2", "itemText": "女" }
    ]
  },
  {
    "dictCode": "yes_no",
    "dictName": "是否",
    "dictItems": [
      { "itemValue": "Y", "itemText": "是" },
      { "itemValue": "N", "itemText": "否" }
    ]
  }
]
```

**更新机制**:

- 缓存时间: 24 小时
- 更新命令: `python Code_Gen_Guide.py --dict`
- 数据来源: JeecgBoot 系统的数据字典管理

---

## 🔄 工作流程详解

### 配置文件生成流程

#### 1. 模板复制

```python
def copy_base_template():
    """复制基础配置模板"""
    with open('Code_Gen_Guide.json', 'r', encoding='utf-8') as f:
        template = json.load(f)
    return template
```

#### 2. 变量替换

```python
def replace_template_variables(template, table_name, table_description):
    """替换模板变量"""
    template['head']['tableName'] = table_name
    template['head']['tableTxt'] = table_description
    return template
```

#### 3. 字段添加

```python
def add_business_fields(template, fields_config):
    """添加业务字段"""
    order_num = 7  # 从7开始（0-6为系统字段）

    for field in fields_config:
        field_template = load_field_template(field['type'])
        field_config = {
            "orderNum": order_num,
            "dbFieldName": field['name'],
            "dbFieldTxt": field['description'],
            "dbType": field_template['dbType'],
            "dbLength": field_template['dbLength'],
            "dbIsNull": field.get('nullable', 1),
            "fieldMustInput": field.get('required', 0),
            "isShowForm": "1",
            "isShowList": "1"
        }

        # 数据字典字段特殊处理
        if field.get('dict_code'):
            field_config['dictField'] = field['dict_code']

        template['fields'].append(field_config)
        order_num += 1

    return template
```

#### 4. 文件保存

```python
def save_config_file(config, entity_name):
    """保存配置文件"""
    filename = f"temp_{entity_name}_config.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return filename
```

### 代码生成执行流程

#### 1. 模块管理

```python
def ensure_module_exists(module_name):
    """确保Maven模块存在"""
    module_path = f"/jeecg-boot/jeecg-module-{module_name}"

    if not os.path.exists(module_path):
        # 创建Maven模块
        create_maven_module(module_name)
        update_parent_pom(module_name)
        update_main_pom(module_name)
```

#### 2. 系统认证

```python
def login_jeecg_system():
    """登录JeecgBoot系统"""
    config = load_config()
    login_url = f"{config['server']['base_url']}/sys/login"

    response = requests.post(login_url, json={
        "username": config['server']['username'],
        "password": config['server']['password']
    })

    if response.status_code == 200:
        return response.json()['result']['token']
    else:
        raise Exception("登录失败")
```

#### 3. 表单创建

```python
def create_online_form(token, config_data):
    """创建在线表单"""
    create_url = f"{config['server']['base_url']}/online/cgform/api/create"

    headers = {"X-Access-Token": token}
    response = requests.post(create_url, json=config_data, headers=headers)

    if response.status_code == 200:
        return response.json()['result']['id']
    else:
        raise Exception("表单创建失败")
```

#### 4. 数据库同步

```python
def sync_database(token, form_id):
    """同步数据库结构"""
    sync_url = f"{config['server']['base_url']}/online/cgform/api/syncDb/{form_id}"

    headers = {"X-Access-Token": token}
    response = requests.post(sync_url, headers=headers)

    return response.status_code == 200
```

#### 5. 代码生成

```python
def generate_code(token, form_id, module_name):
    """生成代码"""
    codegen_url = f"{config['server']['base_url']}/online/cgform/api/generateCode"

    headers = {"X-Access-Token": token}
    data = {
        "ids": form_id,
        "packageName": f"org.jeecg.modules.{module_name}",
        "entityName": extract_entity_name(form_id),
        "jspMode": "one",
        "jformType": "1",
        "packageStyle": "service",
        "vueStyle": "vue3",
        "codeTypes": "controller,service,dao,mapper,entity,vue"
    }

    response = requests.post(codegen_url, json=data, headers=headers)
    return response.status_code == 200
```

### 文件输出结构说明

#### 生成的文件结构

```
/jeecg-boot/jeecg-module-{模块名}/
├── src/main/java/org/jeecg/modules/{模块名}/{实体名}/
│   ├── entity/
│   │   └── {EntityName}.java              # 实体类
│   ├── controller/
│   │   └── {EntityName}Controller.java    # 控制器
│   ├── service/
│   │   ├── I{EntityName}Service.java      # 服务接口
│   │   └── impl/
│   │       └── {EntityName}ServiceImpl.java # 服务实现
│   ├── mapper/
│   │   ├── {EntityName}Mapper.java        # 数据访问层
│   │   └── xml/
│   │       └── {EntityName}Mapper.xml     # SQL映射文件
│   └── vue/
│       ├── {EntityName}List.vue           # 列表页面
│       ├── {EntityName}Form.vue           # 表单页面
│       └── {EntityName}Modal.vue          # 弹窗组件
```

#### 文件内容说明

| 文件类型           | 主要内容                          | 功能说明               |
| ------------------ | --------------------------------- | ---------------------- |
| `Entity.java`      | 实体类定义、字段映射、注解配置    | 数据表的 Java 对象表示 |
| `Controller.java`  | REST API 接口、请求处理、参数验证 | 前端请求的入口点       |
| `Service.java`     | 业务逻辑接口定义                  | 业务逻辑的抽象         |
| `ServiceImpl.java` | 具体业务逻辑实现                  | 实际的业务处理代码     |
| `Mapper.java`      | 数据访问接口、SQL 方法定义        | 数据库操作的接口       |
| `Mapper.xml`       | SQL 语句、结果映射                | 具体的 SQL 实现        |
| `List.vue`         | 列表展示、查询、操作按钮          | 数据列表页面           |
| `Form.vue`         | 表单录入、编辑、验证              | 数据录入页面           |
| `Modal.vue`        | 弹窗组件、详情展示                | 弹窗式操作组件         |

---

## 📖 使用指南

### 命令行参数说明

#### 基本用法

```bash
python Code_Gen_Guide.py --module-name <模块名> --form-config <配置文件>
```

#### 参数详解

| 参数            | 必填 | 类型   | 描述         | 示例                     |
| --------------- | ---- | ------ | ------------ | ------------------------ |
| `--module-name` | ✅   | String | 目标模块名称 | `finance`                |
| `--form-config` | ✅   | String | 配置文件路径 | `temp_sales_config.json` |
| `--dict`        | ❌   | Flag   | 更新数据字典 | 无参数                   |
| `--help`        | ❌   | Flag   | 显示帮助信息 | 无参数                   |

#### 使用示例

```bash
# 生成财务模块的销售管理代码
python Code_Gen_Guide.py --module-name finance --form-config temp_sales_config.json

# 生成人力资源模块的培训管理代码
python Code_Gen_Guide.py --module-name hrms --form-config temp_training_config.json

# 更新数据字典缓存
python Code_Gen_Guide.py --dict
```

### 配置文件格式规范

#### 标准配置文件结构

```json
{
  "head": {
    "tableName": "us_finance_invoice_sales",
    "tableTxt": "财务发票销售管理",
    "tableType": 1,
    "formCategory": "temp",
    "idType": "UUID",
    "isCheckbox": "Y",
    "themeTemplate": "normal",
    "formTemplate": "1",
    "scroll": 1,
    "isPage": "Y",
    "isTree": "N"
  },
  "fields": [
    {
      "orderNum": 7,
      "dbFieldName": "invoice_number",
      "dbFieldTxt": "发票号码",
      "dbType": "string",
      "dbLength": 50,
      "dbIsNull": "0",
      "fieldMustInput": "1",
      "isShowForm": "1",
      "isShowList": "1",
      "fieldShowType": "text"
    },
    {
      "orderNum": 8,
      "dbFieldName": "invoice_amount",
      "dbFieldTxt": "发票金额",
      "dbType": "decimal",
      "dbLength": 18,
      "dbPointLength": 2,
      "dbIsNull": "0",
      "fieldMustInput": "1",
      "isShowForm": "1",
      "isShowList": "1",
      "fieldShowType": "text"
    },
    {
      "orderNum": 9,
      "dbFieldName": "invoice_status",
      "dbFieldTxt": "发票状态",
      "dbType": "string",
      "dbLength": 20,
      "dbIsNull": "1",
      "fieldMustInput": "0",
      "isShowForm": "1",
      "isShowList": "1",
      "fieldShowType": "select",
      "dictField": "invoice_status"
    }
  ]
}
```

#### 字段配置规范

| 属性名           | 类型    | 必填 | 描述              | 示例值                                     |
| ---------------- | ------- | ---- | ----------------- | ------------------------------------------ |
| `orderNum`       | Integer | ✅   | 排序号(从 7 开始) | `7`                                        |
| `dbFieldName`    | String  | ✅   | 数据库字段名      | `invoice_number`                           |
| `dbFieldTxt`     | String  | ✅   | 字段显示名        | `发票号码`                                 |
| `dbType`         | String  | ✅   | 数据库类型        | `string/int/decimal/date/datetime/text`    |
| `dbLength`       | Integer | ✅   | 字段长度          | `50`                                       |
| `dbPointLength`  | Integer | ❌   | 小数位数          | `2`                                        |
| `dbIsNull`       | String  | ✅   | 是否可空          | `0`(非空) / `1`(可空)                      |
| `fieldMustInput` | String  | ✅   | 是否必填          | `0`(非必填) / `1`(必填)                    |
| `isShowForm`     | String  | ✅   | 表单中显示        | `0`(不显示) / `1`(显示)                    |
| `isShowList`     | String  | ✅   | 列表中显示        | `0`(不显示) / `1`(显示)                    |
| `fieldShowType`  | String  | ✅   | 前端组件类型      | `text/select/radio/textarea/date/datetime` |
| `dictField`      | String  | ❌   | 数据字典编码      | `invoice_status`                           |

### 常见问题处理

#### 1. 模块不存在错误

```
错误: 模块 'finance' 不存在
解决: 脚本会自动创建Maven模块，检查项目路径配置
```

#### 2. 登录失败

```
错误: 登录JeecgBoot系统失败
解决: 检查Code_Gen_Config.json中的服务器地址和认证信息
```

#### 3. 表名格式错误

```
错误: 表名格式不符合 us_{模块}_{子模块}_{场景} 标准
解决: 修改配置文件中的tableName字段
```

#### 4. 字段类型不支持

```
错误: 字段类型 'custom_field' 不存在
解决: 使用Code_Gen_field_templates.json中定义的标准字段类型
```

#### 5. 数据字典匹配失败

```
错误: 数据字典 'custom_status' 不存在
解决: 运行 python Code_Gen_Guide.py --dict 更新字典缓存
```

#### 6. 编译失败问题

```
错误: Maven编译失败
解决方案:
  1. 检查Maven是否正确安装: mvn --version
  2. 检查项目路径是否正确
  3. 手动执行: mvn clean install -DskipTests
  4. 检查pom.xml文件是否存在和格式正确
```

#### 7. 404 错误问题

```
问题: 前端请求返回404而不是401，Controller未被加载
根本原因: 模块代码生成正确，但没有被正确编译和安装到Maven本地仓库
解决步骤:
  1. 重新编译模块: mvn clean install -DskipTests
  2. 重启后端服务
  3. 验证模块是否正确加载
```

#### 8. 服务状态检查

```
功能: 检查后端服务状态和新模块加载情况
命令: python Code_Gen_Guide.py --check-service
检查项:
  - 服务是否正常运行
  - 新模块Controller是否已注册
  - 接口路径是否可访问
```

---

## 🔧 扩展开发指南

### 字段类型扩展方法

#### 1. 添加新字段类型

在`Code_Gen_field_templates.json`中添加新的字段类型定义：

```json
{
  "custom_field": {
    "queryShowType": "text",
    "fieldShowType": "custom-component",
    "dbType": "string",
    "dbLength": 200,
    "dbPointLength": 0,
    "dbIsNull": "1",
    "isShowForm": "1",
    "isShowList": "1",
    "fieldMustInput": "0",
    "fieldExtendJson": "{\"componentName\":\"CustomComponent\"}"
  }
}
```

#### 2. 扩展字段属性

添加特殊字段属性：

```json
{
  "enhanced_text_field": {
    "queryShowType": "text",
    "fieldShowType": "text",
    "dbType": "string",
    "dbLength": 100,
    "dbIsNull": "1",
    "isShowForm": "1",
    "isShowList": "1",
    "fieldMustInput": "0",
    "fieldValidType": "string",
    "fieldExtendJson": "{\"minLength\":2,\"maxLength\":100,\"placeholder\":\"请输入内容\"}"
  }
}
```

### 模板定制说明

#### 1. 自定义表单模板

修改`Code_Gen_Guide.json`中的基础配置：

```json
{
  "head": {
    "themeTemplate": "custom",
    "formTemplate": "2",
    "extConfigJson": "{\"customStyle\":\"modern\",\"enableValidation\":true}"
  }
}
```

#### 2. 自定义字段默认值

为字段添加默认值配置：

```json
{
  "orderNum": 7,
  "dbFieldName": "status",
  "dbFieldTxt": "状态",
  "dbType": "string",
  "dbLength": 20,
  "dbDefaultVal": "active",
  "fieldDefaultValue": "active"
}
```

### 数据字典维护

#### 1. 手动更新字典缓存

```bash
python Code_Gen_Guide.py --dict
```

#### 2. 自定义字典数据

在`Code_Gen_DICT.json`中添加自定义字典：

```json
[
  {
    "dictCode": "custom_status",
    "dictName": "自定义状态",
    "dictItems": [
      { "itemValue": "active", "itemText": "激活" },
      { "itemValue": "inactive", "itemText": "停用" },
      { "itemValue": "pending", "itemText": "待审核" }
    ]
  }
]
```

#### 3. 字典匹配优化

为提高字典匹配准确率，建议：

- 使用标准的字典命名规范
- 保持字典项文本的一致性
- 定期更新字典缓存

---

## 🎯 最佳实践

### 1. 命名规范

- 表名: `us_{模块}_{子模块}_{业务场景}`
- 字段名: 使用下划线分隔，见名知意
- 实体名: 使用 Java 驼峰命名规范

### 2. 配置管理

- 定期备份配置文件
- 使用版本控制管理配置变更
- 建立配置文件的标准化模板

### 3. 错误处理

- 详细记录执行日志
- 建立错误码映射表
- 提供清晰的错误信息和解决方案

### 4. 性能优化

- 合理设置超时时间
- 优化数据库字段类型和长度
- 使用缓存减少重复请求

---

## 🤝 与 Code_Gen_Agent.md 的协同学习指南

### 📚 文件角色定位详解

#### Code_Gen_Agent.md - AI 行为规范和提示词框架

**定位**: AI 理解和推理的行为规范文档
**主要内容**:

- AI 推理策略和变量提取规则
- 业务系统识别和分类方法
- 标准化命名规范和验证机制
- 用户需求分析和确认流程

**使用场景**:

- AI 理解用户的自然语言业务需求
- 从业务描述中提取核心变量(MODULE_NAME, SUBMODULE_NAME, ENTITY_NAME)
- 进行业务系统分类和字段类型推理
- 生成标准化的配置参数

#### Code_Gen_Guide.md - 技术实现指南和操作手册

**定位**: 技术实现和系统操作的详细指南
**主要内容**:

- Code_Gen_Guide.py 脚本的使用方法和参数说明
- 配置文件的结构、字段含义和配置方法
- 代码生成的执行流程和环境要求
- 问题排查和最佳实践指导

**使用场景**:

- 了解脚本的调用方式和参数配置
- 理解配置文件的结构和作用机制
- 排查代码生成过程中的技术问题
- 进行系统维护和功能扩展

### 🏗️ CodeGen 系统整体架构

#### 完整的代码生成链路

```
用户业务需求 → Code_Gen_Agent.md → AI需求分析 → 关键词识别 → 变量提取 → 核心变量确认
     ↓
Code_Gen_Guide.json模板 → temp_*_config.json生成 → Code_Gen_Guide.py脚本
     ↓
环境检查 → 模块管理 → JeecgBoot登录 → 表单创建 → 数据库同步 → 代码生成 → 模块集成
     ↓
完整CRUD模块
```

#### 各文件在代码生成流程中的作用

| 阶段         | 主要文件                      | 作用                 | 输入                | 输出                     |
| ------------ | ----------------------------- | -------------------- | ------------------- | ------------------------ |
| **需求分析** | Code_Gen_Agent.md             | 指导 AI 理解业务需求 | 用户自然语言描述    | 核心变量(MODULE_NAME 等) |
| **配置生成** | Code_Gen_Guide.json           | 提供标准模板         | 核心变量 + 字段配置 | temp\_\*\_config.json    |
| **字段处理** | Code_Gen_field_templates.json | 提供字段模板         | 字段类型需求        | 完整字段配置             |
| **脚本执行** | Code_Gen_Guide.py             | 执行代码生成         | 配置文件 + 核心变量 | 完整 CRUD 代码           |
| **系统配置** | Code_Gen_Config.json          | 提供系统参数         | 环境配置需求        | 系统运行参数             |

### 🎯 协同使用最佳实践

#### 文档配合使用建议

1. **需求分析阶段**: 主要参考 Code_Gen_Agent.md，理解 AI 推理策略
2. **技术实现阶段**: 主要参考 Code_Gen_Guide.md，掌握操作方法
3. **问题排查阶段**: 两个文档结合使用，从 AI 推理到技术实现全链路排查
4. **系统优化阶段**: 深入理解两个文档的设计理念，进行针对性改进

#### 学习效果验证

- 能够独立完成从用户需求到代码生成的完整流程
- 具备 AI 推理结果的验证和优化能力
- 掌握系统配置和环境搭建的方法
- 具备常见问题的快速排查和解决能力

---

**📚 技术支持**: 本文档提供 Code_Gen 系统的完整技术实现细节，配合 Code_Gen_Agent.md 使用可实现完整的代码生成功能。
