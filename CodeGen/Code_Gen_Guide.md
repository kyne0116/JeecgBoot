# JeecgBoot 代码生成工具使用指南 v3.0

> **功能**: 基于 JeecgBoot 在线表单 API 的完整代码生成工作流
> **版本**: v3.0 - 支持完整的端到端代码生成流程
> **配合文档**: Code_Gen_Agent.md (AI 推理规范)
> **目标用户**: 开发者、系统维护人员、AI Agent

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.7+ (推荐 3.8+)
- **JeecgBoot 服务**: 运行在 http://localhost:8080
- **Maven**: 3.6+ (用于模块创建和编译)
- **数据库**: MySQL (用于 SQL 执行)
- **操作系统**: macOS/Linux/Windows

### 📁 路径配置说明

**🚨 重要**：系统根目录路径 `/Users/admin/Work/Github/JeecgBoot` **仅在** `Code_Gen_Config.json` 文件中定义，所有脚本和工具均通过读取该配置文件的 `project.path_prefix` 变量获取路径，确保配置的统一性和可维护性。其他文件中出现的路径均为默认回退值，实际运行时以配置文件为准。

### 基本用法

```bash
# 1. 获取最新数据字典
python3 Code_Gen_Guide.py --dict

# 2. 生成代码（完整流程）
python3 Code_Gen_Guide.py --module-name finance --form-config temp_management_config.json

# 3. 验证表名格式
python3 Code_Gen_Guide.py --validate-table-name us_finance_invoice_management

# 4. 修复表名格式
python3 Code_Gen_Guide.py --fix-table-name biz_product_management

# 5. 检查配置文件字段长度限制
python3 Code_Gen_Guide.py --check-field-lengths temp_config.json
```

### 🔗 主子表关联场景用法

#### **场景说明**

当业务需求包含 1 对多关联关系时（如订单-订单明细、学生-家长信息），使用主子表关联功能：

#### **使用步骤**

```bash
# 步骤1：先生成所有子表（只创建数据库表，不生成代码）
python3 Code_Gen_Guide.py --module-name education --form-config student_parents_config.json
python3 Code_Gen_Guide.py --module-name education --form-config student_classmate_config.json

# 步骤2：最后生成主表（创建数据库表 + 生成主子表关联代码）
python3 Code_Gen_Guide.py --module-name education --form-config student_info_config.json
```

#### **智能处理机制**

- **子表处理**：自动检测到被 subList 引用，只调用前 3 个 API，跳过代码生成
- **主表处理**：检测到包含 subList，调用全部 4 个 API，生成主子表关联代码
- **独立表处理**：保持现有逻辑不变，完整调用 4 个 API

#### **配置文件要求**

- **主表配置**：必须包含 subList 数组属性
- **子表配置**：标准格式，不包含 subList 属性
- **表名规范**：所有表必须属于同一模块，遵循 4 段式命名

---

## 📋 配置文件结构

### 🚨 数据库字段长度限制规范

**重要**：配置文件中的字段值必须符合 JeecgBoot 数据库表 `onl_cgform_field` 的字段长度限制，否则会导致数据截断错误。

#### 关键字段长度限制

| 字段名称         | 数据库类型   | 最大长度     | 常用值示例                | 错误示例                           |
| ---------------- | ------------ | ------------ | ------------------------- | ---------------------------------- |
| `queryMode`      | VARCHAR(10)  | **10 字符**  | `single`, `range`, `like` | ❌ `group_range`(11 字符)          |
| `fieldShowType`  | VARCHAR(20)  | **20 字符**  | `text`, `select`, `radio` | ❌ `complex_multi_select`(20+字符) |
| `queryShowType`  | VARCHAR(50)  | **50 字符**  | `text`, `date`, `select`  | 通常不会超限                       |
| `fieldValidType` | VARCHAR(300) | **300 字符** | `mobile`, `email`, `n,p`  | 通常不会超限                       |

#### queryMode 字段特别说明

**✅ 推荐使用的 queryMode 值**：

- `single` - 单值查询（适用于大部分字段）
- `range` - 范围查询（适用于日期、数字字段）
- `like` - 模糊查询（适用于文本字段）
- `in` - 多值查询
- `between` - 区间查询

**❌ 禁止使用的 queryMode 值**：

- `group_range` - 超过 10 字符限制 ❌
- `date_range` - 正好 10 字符，建议改为 `range` ⚠️
- `multi_select` - 超过 10 字符限制 ❌

#### 自动修正机制

Code_Gen_Guide.py 脚本已内置自动修正功能：

- 检测到 `group_range` → 自动修正为 `range`
- 检测到 `date_range` → 自动修正为 `range`
- 检测到其他超长值 → 自动截断或使用默认值

### JSON 配置文件要求

#### head 对象（必需）

```json
{
  "head": {
    "tableName": "us_模块_子模块_实体",
    "tableTxt": "表描述",
    "tableType": 1,
    "formCategory": "temp",
    "idType": "UUID",
    "isCheckbox": "Y",
    "scroll": 1,
    "isPage": "Y",
    "isTree": "N"
  }
}
```

#### fields 数组（必需）

每个字段必须包含：

```json
{
  "dbFieldName": "字段名",
  "dbFieldTxt": "字段描述",
  "dbType": "string",
  "dbLength": 100,
  "dbIsNull": "0",
  "dbIsPersist": "1",
  "fieldShowType": "text",
  "isShowForm": "1",
  "isShowList": "1",
  "orderNum": 8
}
```

### 关键注意事项

- `tableType`和`scroll`必须是整数，不能是字符串
- `dbIsPersist`是关键字段，不能缺失
- 必须包含 7 个系统字段：id(0), create_by(1), create_time(2), update_by(3), update_time(4), sys_org_code(5), del_flag(6)
- 业务字段 orderNum 从 7 开始，确保系统字段在前，业务字段在后

---

## 🔧 命令行参数

### 基本语法

```bash
python3 Code_Gen_Guide.py [OPTIONS]
```

### 参数说明

| 参数                    | 必填 | 描述             | 示例                            |
| ----------------------- | ---- | ---------------- | ------------------------------- |
| `--module-name`         | ✅   | 目标模块名称     | `finance`                       |
| `--form-config`         | ✅   | 配置文件路径     | `temp_management_config.json`   |
| `--dict`                | ❌   | 获取最新数据字典 | 无参数                          |
| `--validate-table-name` | ❌   | 验证表名格式     | `us_finance_invoice_management` |
| `--fix-table-name`      | ❌   | 自动修复表名格式 | `biz_product_management`        |

---

## 🎯 核心功能特性

### v3.0 新增功能

1. **🏗️ 自动模块管理**

   - 自动检测模块是否存在
   - 使用 Maven archetype 创建新模块
   - 自动更新主项目和启动项目的 pom.xml
   - 智能模块集成和依赖管理

2. **📁 前端代码自动迁移**

   - 自动识别生成的 vue3 前端代码
   - 智能解析 SQL 注释获取正确前端路径
   - 两步迁移：重命名 + 移动到 views 目录
   - 支持容错搜索和路径修复

3. **🗄️ 数据库 SQL 自动执行**

   - 自动查找生成的 SQL 文件
   - 智能解析数据库连接配置
   - 自动执行 SQL 创建表结构
   - 支持多种数据库客户端

4. **🔐 权限自动授权**

   - 自动为管理员角色授权新模块权限
   - 智能权限分配和管理
   - 支持自定义角色授权

5. **🔍 编译验证**

   - 自动 Maven 编译验证
   - 智能错误检测和修复建议
   - 支持模块级和项目级编译

6. **📊 三核心变量系统**
   - MODULE_NAME (模块名)
   - SUBMODULE_NAME (子模块名)
   - BUSINESS_ENTITY (业务实体名)
   - 自动变量验证和一致性检查

---

## 📚 数据字典管理

### 获取最新数据字典

在使用 AI 进行代码生成之前，必须先获取最新的系统数据字典：

```bash
python3 Code_Gen_Guide.py --dict
```

### 数据字典文件结构

```json
[
  {
    "dictCode": "sex",
    "dictName": "性别",
    "dictItems": [
      { "itemText": "男", "itemValue": "1" },
      { "itemText": "女", "itemValue": "2" }
    ]
  }
]
```

---

## 📋 表名命名规范

### 标准格式

```
us_{模块名}_{子模块名}_{业务场景}
```

### 示例

- `us_finance_invoice_management` - 财务-发票-管理
- `us_hrms_employee_training` - 人力-员工-培训
- `us_crm_customer_service` - 客户-客户-服务

### 自动解析结果

表名 `us_finance_invoice_management` 会自动解析为：

- 模块名: `finance`
- 子模块名: `invoice`
- 业务场景: `management`
- 包名: `org.jeecg.modules.finance.invoice`

---

## 🔄 完整工作流程

### 标准执行流程

1. **📚 获取数据字典**:

   ```bash
   python3 Code_Gen_Guide.py --dict
   ```

2. **📝 准备配置文件**: 创建包含表结构和字段定义的 JSON 配置文件

3. **🚀 执行完整代码生成**:

   ```bash
   python3 Code_Gen_Guide.py --module-name finance --form-config temp_invoice_config.json
   ```

4. **✅ 自动化验证**: 脚本自动完成以下步骤
   - 🔐 登录 JeecgBoot 系统
   - 📋 创建在线表单
   - 🗄️ 同步数据库表结构
   - 💻 生成后端代码 (Controller, Service, Entity, Mapper)
   - 🎨 生成前端代码 (Vue3 组件)
   - 🏗️ 自动模块管理和集成
   - 📁 前端代码迁移到正确位置
   - 🗄️ 执行数据库 SQL 脚本
   - 🔐 自动权限授权
   - 🔍 Maven 编译验证

### 内部执行步骤详解

**阶段 1: 环境准备**

- 加载配置文件 (`Code_Gen_Config.json`)
- 验证 JeecgBoot 服务状态
- 检查目标模块是否存在，不存在则自动创建

**阶段 2: 表单创建**

- 登录 JeecgBoot 系统
- 解析配置文件并创建在线表单
- 获取表单 ID 用于后续操作

**阶段 3: 数据库同步**

- 调用 JeecgBoot API 同步数据库表结构
- 自动创建表和字段

**阶段 4: 代码生成**

- 临时替换 `jeecg_config.properties` 配置变量
- 调用 JeecgBoot 代码生成 API
- 生成完整的后端和前端代码
- 还原配置文件

**阶段 5: 后处理**

- 前端代码迁移到 `jeecgboot-vue3/src/views/` 目录
- 执行生成的 SQL 脚本
- 为管理员角色自动授权新模块权限
- Maven 编译验证

---

## 💡 使用示例

### 生成财务发票管理模块

```bash
# 1. 获取最新数据字典
python3 Code_Gen_Guide.py --dict

# 2. 生成代码
python3 Code_Gen_Guide.py --module-name finance --form-config temp_management_config.json

# 预期输出:
# ✅ 模块检查完成: jeecg-module-finance
# ✅ 登录成功: admin
# ✅ 表单创建成功: us_finance_invoice_management
# ✅ 数据库同步完成
# ✅ 代码生成完成: org.jeecg.modules.finance.invoice
```

### 验证和修复表名

```bash
# 验证表名格式
python3 Code_Gen_Guide.py --validate-table-name "biz_product_management"
# 输出: ❌ 表名格式错误，建议修改为: us_business_product_management

# 自动修复表名
python3 Code_Gen_Guide.py --fix-table-name "biz_product_management"
# 输出: ✅ 表名已修复为: us_business_product_management
```

---

## ⚠️ 常见问题与解决方案

### 1. 🔐 登录失败

**问题**: API 调用返回认证失败
**解决方案**:

- 检查 JeecgBoot 服务是否启动 (`http://localhost:8080`)
- 验证 `Code_Gen_Config.json` 中的用户名密码
- 确认服务端口配置正确

### 2. 📋 表名格式错误

**问题**: 表名不符合标准格式
**解决方案**:

- 使用标准格式：`us_{模块}_{子模块}_{业务场景}`
- 运行验证命令：`python3 Code_Gen_Guide.py --validate-table-name`
- 使用修复命令：`python3 Code_Gen_Guide.py --fix-table-name`

### 3. 🏗️ 模块不存在

**问题**: 目标模块目录不存在
**解决方案**:

- 脚本会自动使用 Maven archetype 创建模块
- 检查项目路径配置是否正确
- 确认 Maven 环境配置正常

### 4. 📚 数据字典匹配失败

**问题**: 字段类型匹配失败
**解决方案**:

- 运行 `python3 Code_Gen_Guide.py --dict` 更新字典缓存
- 检查 `Code_Gen_DICT.json` 文件是否存在
- 验证字典编码是否正确

### 5. 📁 前端代码迁移失败

**问题**: Vue3 代码未正确迁移到前端项目
**解决方案**:

- 检查 `jeecgboot-vue3/src/views/` 目录权限
- 验证前端项目路径配置
- 查看脚本日志中的详细错误信息

### 6. 🗄️ 数据库 SQL 执行失败

**问题**: 自动 SQL 执行失败
**解决方案**:

- 检查数据库连接配置
- 验证 MySQL 客户端是否可用
- 手动执行生成的 SQL 文件

### 7. 🔍 Maven 编译失败

**问题**: 生成代码编译不通过
**解决方案**:

- 检查 Java 环境配置
- 验证 Maven 依赖是否正确
- 查看编译错误日志并修复

### 8. 🔐 权限授权失败

**问题**: 自动权限授权不成功
**解决方案**:

- 检查管理员角色 ID 配置
- 验证权限 API 调用状态
- 手动在系统中配置权限

---

## 📚 相关文档

- **Code_Gen_Agent.md**: AI 推理规范和业务分析方法
- **Code_Gen_JSON_Standards.md**: 统一标准规范 (核心变量定义+JSON 标准+验证规则)
- **Code_Gen_Config.json**: 系统配置文件模板
- **Code_Gen_Guide.json**: 统一模板配置 (集成字段模板和系统常量)
- **Code_Gen_Validator.py**: 高效验证工具 (核心验证：orderNum 连续性、系统字段、表名格式)

---

## 🔧 高级配置

### 配置文件详解

**Code_Gen_Config.json 主要配置项**:

```json
{
  "project": {
    "path_prefix": "/Users/admin/Work/Github/JeecgBoot"
  },
  "server": {
    "base_url": "http://localhost:8080/jeecg-boot",
    "username": "admin",
    "password": "123456"
  },
  "compilation": {
    "enabled": true,
    "maven_command": "mvn",
    "timeout": 300
  },
  "frontend_migration": {
    "enabled": true,
    "target_base_path": "jeecgboot-vue3/src/views"
  },
  "database_execution": {
    "enabled": true,
    "method": "mysql_client"
  },
  "permission_authorization": {
    "enabled": true,
    "admin_role_id": "f6817f48af4fb3af11b9e8bf182f618b"
  }
}
```

### 功能开关控制

可以通过配置文件控制各个功能模块的启用状态：

- `compilation.enabled`: 控制是否执行 Maven 编译验证
- `frontend_migration.enabled`: 控制是否执行前端代码迁移
- `database_execution.enabled`: 控制是否执行数据库 SQL
- `permission_authorization.enabled`: 控制是否执行权限授权

---

## 📈 版本更新说明

### v3.0 主要更新

**🎯 完整的端到端代码生成工作流**

- 从单纯的代码生成扩展为完整的项目集成流程
- 实现了真正的"一键生成"体验

**🏗️ 自动模块管理**

- 智能检测模块是否存在
- 自动使用 Maven archetype 创建新模块
- 自动更新项目依赖和集成配置

**📁 智能前端代码迁移**

- 自动识别生成的 Vue3 前端代码
- 解析 SQL 注释获取正确的前端路径
- 两步迁移确保代码正确放置

**🗄️ 数据库自动化**

- 自动执行生成的 SQL 脚本
- 智能解析数据库连接配置
- 验证表结构创建结果

**🔐 权限自动授权**

- 自动为管理员角色授权新模块权限
- 确保生成的功能立即可用

**🔍 编译验证**

- 自动 Maven 编译验证
- 确保生成代码的质量

**📊 三核心变量系统**

- 标准化的变量命名和验证机制
- 确保生成代码的一致性和规范性

### 向后兼容性

v3.0 完全向后兼容之前的版本，所有现有的配置文件和使用方式都继续有效。新功能通过配置开关控制，可以根据需要启用或禁用。

---

## 🎯 总结

Code_Gen_Guide.py v3.0 是一个功能完整的 JeecgBoot 代码生成工具，它不仅能生成代码，还能自动完成项目集成的所有必要步骤。通过智能化的自动处理，大大提升了开发效率，实现了真正的"一键生成，立即可用"的开发体验。

**核心优势**：

- ✅ **完整性**：端到端的完整工作流
- ✅ **智能化**：自动处理复杂的集成步骤
- ✅ **可靠性**：完善的错误处理和验证机制
- ✅ **易用性**：简单的命令行接口
- ✅ **灵活性**：丰富的配置选项和功能开关

---

## 🔧 故障排除

### 常见错误及解决方案

#### 1. 数据截断错误 (Data truncation)

**错误信息**：

```
java.sql.BatchUpdateException: Data truncation: Data too long for column 'query_mode' at row 1
```

**原因**：配置文件中的字段值超过了数据库字段长度限制

**解决方案**：

```bash
# 检查配置文件中的字段长度问题
python3 Code_Gen_Guide.py --check-field-lengths temp_config.json

# 使用验证器进行完整检查
python3 Code_Gen_Validator.py temp_config.json
```

**常见超长字段值**：

- `queryMode: "group_range"` → 改为 `"range"`
- `queryMode: "date_range"` → 改为 `"range"`
- `queryMode: "multi_select"` → 改为 `"single"`

#### 2. 自动修正机制

Code_Gen_Guide.py 已内置自动修正功能，会自动处理：

- 超长的 queryMode 值
- 不符合规范的字段值
- 包路径大小写问题

#### 3. 预防措施

**在生成配置文件时**：

1. 使用推荐的 queryMode 值：`single`, `range`, `like`
2. 避免使用超长的字段值
3. 生成后立即运行验证器检查

**验证流程**：

```bash
# 1. 生成配置文件后立即验证
python3 Code_Gen_Validator.py temp_config.json

# 2. 检查字段长度限制
python3 Code_Gen_Guide.py --check-field-lengths temp_config.json

# 3. 确认无误后执行代码生成
python3 Code_Gen_Guide.py --module-name xxx --form-config temp_config.json
```

---

**注意**: 本指南为 JeecgBoot 代码生成工具的完整技术文档，配合 Code_Gen_Agent.md 使用可实现智能化的代码生成流程。
