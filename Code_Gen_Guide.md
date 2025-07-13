# JeecgBoot 表单工作流自动化工具 - 使用指南

## 📋 概述

本工具提供完整的 JeecgBoot 表单代码生成解决方案，包含：

- **Code_Gen_Guide.py** - 主执行脚本，负责完整的自动化流程
- **Code_Gen_Agent.md** - AI 智能助手提示词，用于需求分析和配置生成
- **Code_Gen_Guide.md** - 本使用文档
- **配置和模板文件** - 支持灵活的配置和字段模板

## 📁 文件结构

```
Code_Gen_Guide/
├── Code_Gen_Guide.py              # 🚀 主执行脚本
├── Code_Gen_Guide.md              # 📚 使用文档（本文件）
├── Code_Gen_Agent.md              # 🤖 AI智能助手提示词
├── Code_Gen_Config.json           # ⚙️ 主配置文件
├── Code_Gen_Guide.json           # 📋 基础模板文件
└── Code_Gen_field_templates.json # 🔧 字段类型模板库
```

## 🚀 主要功能

### Code_Gen_Guide.py - 核心执行脚本

**主要功能**：

- **模块名称接收**：接收业务模块名称参数（如：hrms、crm、scm、finance）
- **模块管理**：自动检查 jeecg-module-{模块名} 是否存在，如不存在则创建
- **Maven 模块创建**：使用 Maven archetype 自动创建新模块
- **项目配置更新**：自动更新主项目和启动项目的 pom.xml 配置
- **完整包名生成**：基于模块名称和实体名称自动生成正确的包名 `org.jeecg.modules.{模块名}.{实体名称}`
- **模板变量处理**：确保包名等模板变量正确传递和替换
- **完整工作流执行**：登录 → 表单创建 → 数据库同步 → 代码生成

**核心特性**：

- ✅ 智能模块管理
- ✅ 自动化 Maven 操作
- ✅ 业务包名自动生成
- ✅ 模板变量正确替换
- ✅ 完整工作流执行
- ✅ 错误处理和验证
- ✅ 跨平台兼容

### Code_Gen_Agent.md - AI 智能助手

**主要功能**：

- **需求分析**：理解用户业务需求，智能识别业务系统类型
- **表结构设计**：自动设计数据库表结构和字段配置
- **配置生成**：基于模板生成 JSON 配置文件
- **脚本调用**：自动调用 Code_Gen_Guide.py 执行完整流程

**使用方式**：

```markdown
# 将 Code_Gen_Agent.md 作为系统提示词输入到 AI 助手中

# AI 助手将能够：

1. 分析业务需求
2. 生成配置文件
3. 调用执行脚本
4. 完成整个代码生成流程
```

## ⚙️ 配置文件说明

### Code_Gen_Config.json - 主配置文件

**主要配置项**：

- **服务器配置**：JeecgBoot 服务地址、登录用户名密码
- **超时设置**：各 API 调用的超时时间
- **代码生成配置**：项目路径、包名、代码类型等
- **查询配置**：分页大小、显示设置等

**动态变量支持**：

- `{{PROJECT_PATH}}`：根据模块名动态生成项目路径
- `{{ENTITY_NAME}}`：根据表名动态生成实体名称
- `{{PACKAGE_NAME}}`：基于模块名和子模块名动态生成完整包名

## 🔧 核心变量详解

### 四个核心变量

`Code_Gen_Guide.py` 脚本需要接收以下四个核心变量来完成代码生成工作流：

1. **PROJECT_PATH_PREFIX** - 项目根路径前缀

   - 来源：配置文件 `Code_Gen_Config.json` 中的 `project.path_prefix`
   - 示例：`/Users/admin/Work/Github/JeecgBoot`
   - 用途：作为所有项目路径的基础前缀
   - 传递方式：从配置文件读取

2. **PROJECT_PATH** - 完整项目路径

   - 生成规则：`{PROJECT_PATH_PREFIX}/jeecg-boot/jeecg-module-{module_name}`
   - 示例：`/Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-module-finance`
   - 用途：指定代码生成的目标目录
   - 传递方式：基于 PROJECT_PATH_PREFIX 和模块名称动态生成

3. **ENTITY_NAME** - 子模块名称

   - 生成规则：基于业务功能的英文单词命名，遵循业界最佳实践
   - 命名规范：
     - 使用单个英文单词（如：invoice、employee、customer、order）
     - 避免下划线和驼峰命名
     - 体现核心业务功能
     - 符合 RESTful API 设计规范
   - 示例：
     - 发票管理 → `invoice`
     - 员工管理 → `employee`
     - 客户管理 → `customer`
     - 订单管理 → `order`
   - 用途：
     - 前端路由路径：`/invoice/usInvoiceList`
     - 权限控制标识：`invoice:list`
     - SQL 文件中的模块名称
     - API 接口路径：`/invoice/usInvoice/list`
     - 子模块标识和包名组成
   - 传递方式：基于业务功能手动指定或智能推断

4. **PACKAGE_NAME** - 完整包名
   - 生成规则：基于模块名和子模块名生成完整包名 `org.jeecg.modules.{模块名}.{子模块名}`
   - 示例：`org.jeecg.modules.finance.invoice`
   - 用途：Java 代码包结构，用于生成正确的包路径
   - 传递方式：基于模块名称和子模块名称动态生成

### 变量命名统一说明

- **module_name**: 模块名称，如 `finance`，对应 `jeecg-module-finance`
- **entity_name**: 子模块名称，如 `invoice`，用于前端路由和权限控制
- **package_name**: 完整包名，基于模块名和子模块名生成 `org.jeecg.modules.{模块名}.{子模块名}`，如 `org.jeecg.modules.finance.invoice`，用于 Java 代码包结构

### 变量传递流程

```
Code_Gen_Guide.py 接收四个核心变量：

1. PROJECT_PATH_PREFIX (从配置文件读取)
   示例: /Users/admin/Work/Github/JeecgBoot

2. PROJECT_PATH (动态生成)
   规则: {PROJECT_PATH_PREFIX}/jeecg-boot/jeecg-module-{module_name}
   示例: /Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-module-finance

3. ENTITY_NAME (基于业务功能)
   规则: 使用英文单词体现核心业务功能
   示例: 发票管理 → invoice

4. PACKAGE_NAME (动态生成)
   规则: 基于模块名和子模块名生成完整包名 org.jeecg.modules.{模块名}.{子模块名}
   示例: org.jeecg.modules.finance.invoice

变量使用场景：
- ENTITY_NAME 用于: 前端路由、权限控制、API路径、SQL脚本、子模块标识
- PACKAGE_NAME 用于: Java代码包结构、模板变量替换
- PROJECT_PATH 用于: 代码生成目标目录
- PROJECT_PATH_PREFIX 用于: 路径计算基础
```

## 🔧 四个核心变量处理机制

### 变量说明

`Code_Gen_Guide.py` 脚本通过四个核心变量来完成完整的代码生成工作流：

1. **PROJECT_PATH_PREFIX**: 项目根路径前缀
2. **PROJECT_PATH**: 完整项目路径
3. **ENTITY_NAME**: 实体名称
4. **PACKAGE_NAME**: 完整包名

### 自动生成规则

脚本会根据传入的模块名称和配置信息自动生成这四个变量：

```
输入: 模块名称=finance, 业务功能=发票管理

生成过程:
1. PROJECT_PATH_PREFIX = 从配置文件读取 (/Users/admin/Work/Github/JeecgBoot)
2. PROJECT_PATH = {PROJECT_PATH_PREFIX}/jeecg-boot/jeecg-module-finance
3. ENTITY_NAME = invoice (基于业务功能的英文单词)
4. PACKAGE_NAME = org.jeecg.modules.finance.invoice
```

### 传递流程

1. **接收模块名称**：通过 `--module-name` 参数接收
2. **读取配置前缀**：从 `Code_Gen_Config.json` 读取 `PROJECT_PATH_PREFIX`
3. **生成项目路径**：`PROJECT_PATH = f"{PROJECT_PATH_PREFIX}/jeecg-boot/jeecg-module-{module_name}"`
4. **确定子模块名称**：基于业务功能确定 `ENTITY_NAME`（如：invoice、employee、customer）
5. **生成完整包名**：基于模块名和子模块名生成 `PACKAGE_NAME = f"org.jeecg.modules.{module_name}.{ENTITY_NAME}"`
6. **传递给 API**：在代码生成请求中包含 `"bussiPackage": PACKAGE_NAME`
7. **配置文件替换**：代码生成时临时替换 `jeecg_config.properties` 文件中的变量
8. **还原配置**：生成完毕后，还原 `jeecg_config.properties` 文件，保持为变量占位

### 配置文件变量替换机制

**重要说明**：代码生成时 `jeecg_config.properties` 文件进行四个核心变量的替换，生成完毕后，还原该文件，保持为变量占位。

#### 替换过程

1. **生成前状态**：

   ```properties
   project_path={{PROJECT_PATH}}
   bussi_package={{PACKAGE_NAME}}
   entity_name={{ENTITY_NAME}}
   path_prefix={{PROJECT_PATH_PREFIX}}
   ```

2. **生成时替换**：

   ```properties
   project_path=/Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-module-finance
   bussi_package=org.jeecg.modules.finance.invoice
   entity_name=invoice
   path_prefix=/Users/admin/Work/Github/JeecgBoot
   ```

3. **生成后还原**：
   ```properties
   project_path={{PROJECT_PATH}}
   bussi_package={{PACKAGE_NAME}}
   entity_name={{ENTITY_NAME}}
   path_prefix={{PROJECT_PATH_PREFIX}}
   ```

#### 目的说明

- **临时替换**：确保代码生成时使用正确的四个核心变量值
- **自动还原**：保持配置文件的通用性，支持多次不同模块的代码生成
- **变量占位**：避免硬编码特定项目路径，提高配置文件的可移植性

### 生成的代码结构

```
jeecg-module-{模块名}/
└── src/main/java/
    └── org/jeecg/modules/{模块名}/
        └── {实体名称}/
            ├── controller/
            ├── entity/
            ├── mapper/
            ├── service/
            └── vue3/
```

### Code_Gen_Guide.json - 基础模板文件

**用途**：包含 7 个必需系统字段的基础模板

- **固定系统字段**：id、create_by、create_time、update_by、update_time、sys_org_code、del_flag
- **变量占位符**：支持表名和表描述的动态替换
- **模板稳定性**：永远保持模板状态，不被修改

### Code_Gen_field_templates.json - 字段类型模板库

**支持的字段类型**：

- text_field、number_field、decimal_field
- date_field、datetime_field、select_field、textarea_field

**模板变量**：

- `{{FIELD_NAME}}`、`{{FIELD_DESCRIPTION}}`、`{{ORDER_NUM}}`
- `{{NULLABLE}}`、`{{REQUIRED}}`、`{{OPTIONS}}`等

## 🚀 使用方式

### 方式 1: AI 智能助手（推荐）

1. **准备 AI 助手**：将 Code_Gen_Agent.md 作为系统提示词输入到 AI 助手
2. **描述需求**：用自然语言描述业务需求
3. **自动执行**：AI 助手自动完成整个流程

**示例对话**：

```
用户: "我需要创建员工培训记录表，包含培训名称、时间、参与人员、效果评估等字段"

AI助手将：
1. 识别为人力资源系统(hrms)
2. 检查jeecg-module-hrms模块是否存在
3. 如不存在，自动创建Maven模块
4. 生成配置文件并执行代码生成
```

### 方式 2: 直接使用脚本

```bash
# 1. 系统诊断
python Code_Gen_Guide.py --test

# 2. 指定系统名称执行
python Code_Gen_Guide.py --system-name hrms --form-config config.json

# 3. 验证配置
python Code_Gen_Guide.py --validate
```

## 📋 命令行参数

### 主要参数

- `--system-name` / `-s`：指定业务系统名称（hrms、crm、scm、oa、finance）
- `--form-config` / `-f`：指定表单配置文件路径
- `--test`：运行系统诊断测试
- `--validate`：仅验证配置，不执行工作流
- `--skip-module-management`：跳过模块管理（使用现有配置）

### 使用示例

```bash
# 创建人力资源系统的员工表
python Code_Gen_Guide.py --system-name hrms --form-config employee_config.json

# 创建客户管理系统的客户表
python Code_Gen_Guide.py --system-name crm --form-config customer_config.json

# 跳过模块管理，直接使用现有配置
python Code_Gen_Guide.py --skip-module-management --form-config config.json
```

## ⚠️ 注意事项

### 环境要求

- 确保 Maven 已正确安装并配置环境变量
- 确保 JeecgBoot 服务正常运行
- 在 jeecg-boot 项目根目录下执行命令

### 重要规则

- `Code_Gen_Guide.json` 是永久模板文件，请勿修改
- 业务配置文件必须保持 7 个系统字段不变
- 表名必须使用 `us_` 前缀
- 业务字段的 orderNum 从 7 开始

### 自动化功能

- **智能系统识别**：基于表名和描述自动识别业务系统类型
- **模块存在性检查**：自动检查 `jeecg-boot/jeecg-module-{系统名}` 是否存在
- **Maven 模块创建**：使用 Maven archetype 自动创建新模块（非交互模式）
- **项目配置更新**：自动更新主项目和启动项目的 pom.xml 文件
- **跨平台兼容**：支持 Windows/Linux/Mac 平台
- **错误处理**：完整的异常捕获和错误报告机制
- **超时控制**：Maven 命令执行 5 分钟超时保护

## 🔧 技术实现细节

### 核心功能模块

1. **detect_business_system()** - 智能业务系统识别

   - 支持系统：HRMS、CRM、SCM、OA、Finance
   - 算法：关键词匹配计分系统

2. **check_module_exists()** - 模块存在性检查

   - 检查路径：`jeecg-boot/jeecg-module-{system_name}`
   - 输出详细的检查结果和路径信息

3. **create_maven_module()** - Maven 模块创建

   - 使用非交互模式：`-DinteractiveMode=false`
   - 5 分钟执行超时控制
   - 完整的异常捕获和错误报告

4. **update_main_pom() / update_system_start_pom()** - 项目配置更新

   - 使用 ElementTree 安全解析和修改 XML
   - 自动处理 XML 命名空间
   - 检查重复模块避免重复添加

5. **ensure_module_exists()** - 完整模块管理流程
   - 执行步骤：检查 → 创建 → 配置 → 验证
   - 任何步骤失败都会终止流程

### 动态配置更新

脚本会根据识别的系统名称和表名动态生成四个核心变量：

```python
# 1. 读取项目路径前缀
PROJECT_PATH_PREFIX = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

# 2. 生成完整项目路径
PROJECT_PATH = f"{PROJECT_PATH_PREFIX}/jeecg-boot/jeecg-module-{system_name}"

# 3. 基于业务功能确定子模块名称
# 推荐使用英文单词，如：invoice、employee、customer、order
ENTITY_NAME = "invoice"  # 示例：发票管理

# 4. 生成完整包名
PACKAGE_NAME = f"org.jeecg.modules.{system_name}.{ENTITY_NAME}"

# 打印四个核心变量用于调试
print(f"四个核心变量:")
print(f"  PROJECT_PATH_PREFIX: {PROJECT_PATH_PREFIX}")
print(f"  PROJECT_PATH: {PROJECT_PATH}")
print(f"  ENTITY_NAME: {ENTITY_NAME}")
print(f"  PACKAGE_NAME: {PACKAGE_NAME}")
```

## 🚀 完整使用流程

### 标准流程（推荐）

1. **环境检查**

   ```bash
   python Code_Gen_Guide.py --test
   ```

2. **准备配置文件**

   - 基于 `Code_Gen_Guide.json` 模板创建业务配置
   - 或使用现有示例如 `form_config_training_subject.json`

3. **执行代码生成**

   ```bash
   python Code_Gen_Guide.py --system-name hrms --form-config your_config.json
   ```

4. **验证结果**
   - 检查生成的代码文件
   - 启动 JeecgBoot 验证功能

### AI 助手流程

1. **准备 AI 助手**

   - 将 `Code_Gen_Agent.md` 作为系统提示词

2. **描述业务需求**

   ```
   "我需要创建员工培训记录表，包含培训名称、时间、参与人员、效果评估等字段"
   ```

3. **自动执行**
   - AI 助手自动识别系统类型
   - 生成配置文件
   - 调用脚本执行完整流程

## 📊 执行结果

脚本执行成功后会显示：

- 📋 表名和表单 ID
- 🏗️ 实体名和包名
- 🏗️ 项目路径
- ✅ 执行状态和完成时间

生成的代码包含：

- **Controller** - REST API 接口
- **Service** - 业务逻辑层
- **DAO/Mapper** - 数据访问层
- **Entity** - 实体类
- **Vue** - 前端页面组件
