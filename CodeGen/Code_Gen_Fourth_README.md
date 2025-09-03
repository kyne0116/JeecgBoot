# Code_Gen_Fourth.py 使用说明

## 概述

`Code_Gen_Fourth.py` 是专门用于调用 JeecgBoot 登录 API 和第四个代码生成接口的简化工具。它与 `Code_Gen_Guide.py` 接收相同的参数，但只执行登录、获取表单 ID 和代码生成三个核心步骤。

## 功能特性

- ✅ **简化工作流**: 只包含登录、获取表单 ID 和代码生成三个步骤
- ✅ **智能获取表单 ID**: 自动根据表名查询获取表单 ID，无需手动提供
- ✅ **标准 JSON 格式**: 按照 JeecgBoot 官方标准格式构建和显示接口参数
- ✅ **主子表支持**: 自动识别并支持主子表场景，正确设置 jformType 和 subList
- ✅ **详细参数显示**: 完整显示第四个接口的所有提交参数信息
- ✅ **表单配置分析**: 自动分析表单配置文件，显示字段统计和业务字段详情
- ✅ **参数兼容**: 与 `Code_Gen_Guide.py` 相同的参数接收方式
- ✅ **配置兼容**: 使用相同的配置文件格式
- ✅ **错误处理**: 完整的错误处理和日志输出
- ✅ **跨平台**: 支持 Windows/macOS/Linux

## 使用方式

### 方式一：使用表单配置文件（自动获取表单 ID）

```bash
python3 Code_Gen_Fourth.py --form-config Code_Gen_Guide.json
```

### 方式二：使用表单配置文件 + 指定表单 ID

```bash
python3 Code_Gen_Fourth.py --form-config Code_Gen_Guide.json --form-id "your_form_id"
```

### 方式三：直接指定表单 ID 和表名

```bash
python3 Code_Gen_Fourth.py --form-id "your_form_id" --table-name "us_finance_invoice_management"
```

### 方式四：指定模块名称

```bash
python3 Code_Gen_Fourth.py --form-config Code_Gen_Guide.json --module-name finance
```

## 参数说明

| 参数             | 简写 | 说明             | 示例                                         |
| ---------------- | ---- | ---------------- | -------------------------------------------- |
| `--config`       | `-c` | 配置文件路径     | `--config Code_Gen_Config.json`              |
| `--module-name`  | `-m` | 业务模块名称     | `--module-name finance`                      |
| `--form-config`  | `-f` | 表单配置文件路径 | `--form-config Code_Gen_Guide.json`          |
| `--table-name`   | `-n` | 表名             | `--table-name us_finance_invoice_management` |
| `--project-path` | `-p` | 项目路径         | `--project-path /path/to/project`            |
| `--entity-name`  | `-e` | 实体名称         | `--entity-name InvoiceManagement`            |
| `--form-id`      | `-i` | 表单 ID          | `--form-id "abc123def456"`                   |
| `--verbose`      | `-v` | 详细输出模式     | `--verbose`                                  |
| `--try-run`      |      | 试运行模式       | `--try-run`                                  |

## 工作流程

1. **加载配置**: 读取 `Code_Gen_Config.json` 配置文件
2. **解析参数**: 处理命令行参数和表单配置
3. **登录认证**: 调用 `/sys/mLogin` 接口获取 Token
4. **获取表单 ID**: 如果未提供表单 ID，调用 `/online/cgform/head/list` 接口根据表名自动获取
5. **代码生成**: 调用 `/online/cgform/api/codeGenerate` 接口生成代码

## 配置文件

使用与 `Code_Gen_Guide.py` 相同的 `Code_Gen_Config.json` 配置文件：

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
  "timeouts": {
    "login": 10,
    "list": 15,
    "codegen": 60
  },
  "query": {
    "page_size": 50,
    "page_no": 1
  },
  "codegen": {
    "jsp_mode": "one",
    "jform_type": "1",
    "package_style": "service",
    "vue_style": "vue3",
    "code_types": "controller,service,dao,mapper,entity,vue"
  },
  "display": {
    "token_length": 50,
    "max_records": 5
  }
}
```

## 使用场景

### 场景 1：自动获取表单 ID（推荐）

当你有表单配置文件但不知道表单 ID 时，脚本会自动根据表名查询获取：

```bash
python3 Code_Gen_Fourth.py --form-config Code_Gen_Guide.json
```

### 场景 2：已有表单 ID，直接生成代码

当你已经通过其他方式创建了表单并获得了表单 ID 时：

```bash
python3 Code_Gen_Fourth.py --form-id "1234567890abcdef" --table-name "us_finance_invoice_management"
```

### 场景 3：使用配置文件 + 指定表单 ID

当你有配置文件并且想要指定特定的表单 ID 时：

```bash
python3 Code_Gen_Fourth.py --form-config alumni_members_MemberProfile_standalone_20250903102722.json --form-id "abc123def456"
```

### 场景 4：试运行模式

在实际执行前查看将要执行的操作：

```bash
python3 Code_Gen_Fourth.py --try-run --form-id "test123" --table-name "us_finance_invoice_management"
```

或者使用配置文件的试运行：

```bash
python3 Code_Gen_Fourth.py --try-run --form-config alumni_members_MemberProfile_standalone_20250903102722.json --form-id "test123456"
```

### 场景 5：详细模式查看完整参数

使用详细模式查看完整的 JSON 请求负载和表单配置分析：

```bash
python3 Code_Gen_Fourth.py --verbose --form-config alumni_members_MemberProfile_single.json --form-id "test123"
```

### 场景 6：主子表场景代码生成

处理包含子表的主子表场景：

```bash
python3 Code_Gen_Fourth.py --verbose --form-config alumni_members_MemberProfile.json --form-id "7079ee1638944fc0be93f2d6d586eeb9"
```

## 输出示例

### 试运行模式输出

```
JeecgBoot 第四步代码生成工具 v1.0
==================================================
[LIST] 表单配置文件: alumni_members_MemberProfile_standalone_20250903102722.json
[LIST] 指定表单ID: test123456
[OK] business_entity验证通过: MemberProfile
[OK] 从表名设置核心变量成功
[OK] 从配置文件提取业务实体成功

[SEARCH] 试运行模式 - 将显示操作但不执行

[LIST] 核心变量详情:
   模块名/系统名称          = demo
   子模块名/系统模块        = users
   业务实体名称             = MemberProfile
   表名                     = us_demo_users_user_info
   包名                     = org.jeecg.modules.demo.users
   项目路径                 = /Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-demo

[CHART] 工作流变量信息:
   BASE_URL                 = http://localhost:8080/jeecg-boot
   LOGIN_USERNAME           = admin
   REQUEST_TIMEOUT_LOGIN    = 10s
   REQUEST_TIMEOUT_CODEGEN  = 60s

[PACKAGE] 代码生成参数:
   JSP_MODE                 = one
   JFORM_TYPE               = 1
   PACKAGE_STYLE            = service
   VUE_STYLE                = vue3
   CODE_TYPES               = controller,service,dao,mapper,entity,vue

[TOOL] 将要执行的操作:
   1. 登录到 http://localhost:8080/jeecg-boot
   2. 使用表单ID test123456 生成代码
   3. 生成到项目路径: /Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-demo
```

### 实际执行输出

```
JeecgBoot 第四步代码生成工具 v1.0
==================================================
[LIST] 指定表单ID: abc123def456

[START] 正在登录...
   登录URL: http://localhost:8080/jeecg-boot/sys/mLogin
   用户名: admin
   响应状态码: 200
[OK] 登录成功: 管理员

[BUILD] 正在生成代码...
   表单ID: abc123def456
   表名: us_demo_users_user_info
   [LIST] 代码生成参数:
      projectPath   = /Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-demo
      entityName    = MemberProfile
      entityPackage = users
      jspMode       = one
      jformType     = 1
   响应状态码: 200
[OK] 代码生成成功

[SUCCESS] 第四步代码生成完成！
[TIP] 生成的代码位于: /Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-demo
```

### 详细模式输出（新增功能）

```
[BUILD] 正在生成代码...
   表单ID: test123
   表名: us_alumni_members_member_profile
   [LIST] 第四个接口提交参数详情:
      ┌─ 基础参数
      │  projectPath   = /Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-alumni
      │  entityName    = MemberProfile
      │  entityPackage = members
      │  code          = test123
      │  tableName     = us_alumni_members_member_profile
      ├─ 生成配置
      │  jspMode       = one
      │  jformType     = 1
      │  packageStyle  = service
      │  vueStyle      = vue3
      └─ 代码类型     = controller,service,dao,mapper,entity,vue
   [DATABASE] 表单配置详情:
      ┌─ 表单基础信息
      │  表名         = us_alumni_members_member_profile
      │  表描述       = 校友基础档案
      │  业务实体     = MemberProfile
      │  表类型       = 1
      │  表单分类     = temp
      │  主键类型     = UUID
      │  是否分页     = Y
      │  是否树形     = N
      │  表单模板     = 1
      └─ 主题模板     = normal
      ┌─ 字段统计信息
      │  总字段数     = 12
      │  表单显示字段 = 5
      │  列表显示字段 = 5
      │  查询字段     = 4
      └─ 必填字段     = 6
      ┌─ 业务字段详情 (4个)
      │  join_date            = 入会时间 (Date(0), 必填, 表单,列表,查询)
      │  referrer_account     = 推荐人账号 (string(100), 可选, 表单,列表,查询)
      │  wechat_account       = 微信号 (string(100), 可选, 表单,列表,查询)
      └─ wechat_unionid       = 微信UnionID (string(128), 可选, 表单)
      ┌─ 生成元数据
      │  模块名       = alumni
      │  子模块名     = members
      │  推理策略     = 主子表关联场景
      └─ 语义分析     = 校友会会员管理系统主表，包含基础档案信息和与系统用户的1:1关联...
      ┌─ 派生格式
      │  表后缀       = member_profile
      │  URL路径      = /alumni/members/memberProfile
      └─ 前端路径     = src/views/alumni/members/MemberProfile
   [WEB] 完整请求负载 (JSON):
      {
        "projectPath": "/Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-alumni",
        "entityName": "MemberProfile",
        "entityPackage": "members",
        "jspMode": "one",
        "jformType": "1",
        "packageStyle": "service",
        "vueStyle": "vue3",
        "codeTypes": "controller,service,dao,mapper,entity,vue",
        "code": "test123",
        "tableName": "us_alumni_members_member_profile"
      }
```

## 错误处理

脚本包含完整的错误处理机制：

- **登录失败**: 检查用户名密码和服务器连接
- **配置文件错误**: 检查 JSON 格式和必需字段
- **参数缺失**: 提示缺少的必需参数
- **网络错误**: 显示详细的网络错误信息

## 与 Code_Gen_Guide.py 的区别

| 功能       | Code_Gen_Guide.py | Code_Gen_Fourth.py |
| ---------- | ----------------- | ------------------ |
| 表单创建   | ✅                | ❌                 |
| 表单查询   | ✅                | ❌                 |
| 数据库同步 | ✅                | ❌                 |
| 代码生成   | ✅                | ✅                 |
| 模块管理   | ✅                | ❌                 |
| 前端迁移   | ✅                | ❌                 |
| 权限授权   | ✅                | ❌                 |
| 编译验证   | ✅                | ❌                 |
| 登录认证   | ✅                | ✅                 |

## 注意事项

1. **表单 ID 必需**: 使用此脚本前，表单必须已经存在并获得表单 ID
2. **服务器运行**: 确保 JeecgBoot 服务器正在运行
3. **权限验证**: 确保登录用户有代码生成权限
4. **路径正确**: 确保项目路径配置正确

## 故障排除

### 常见问题

1. **登录失败**: 检查用户名密码和服务器地址
2. **表单 ID 无效**: 确认表单 ID 存在且格式正确
3. **路径错误**: 检查项目路径配置
4. **网络超时**: 增加超时时间配置

### 调试模式

使用 `--verbose` 参数获取详细输出：

```bash
python3 Code_Gen_Fourth.py --verbose --form-id "your_form_id" --table-name "your_table_name"
```

## 主子表场景输出示例

### 主子表参数显示

```
[PREVIEW] 试运行模式 - 参数预览:
   [LIST] 第四个接口提交参数详情 (JeecgBoot标准格式):
      ┌─ 主子表场景参数
      │  projectPath     = /Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-alumni
      │  jspMode         = jvxe (主子表模式)
      │  ftlDescription  = 校友基础档案
      │  jformType       = 2 (主子表)
      │  tableName_tmp   = us_alumni_members_member_profile
      │  entityName      = MemberProfile
      │  entityPackage   = members
      │  packageStyle    = service
      │  vueStyle        = vue3
      │  codeTypes       = controller,service,dao,mapper,entity,vue
      │  code            = 7079ee1638944fc0be93f2d6d586eeb9
      │  tableName       = us_alumni_members_member_profile
      └─ subList (4个子表):
               ├─ us_alumni_members_member_education
         │    entityName     = MemberEducation
         │    ftlDescription = 教育背景
         │    id             = row_1020
               ├─ us_alumni_members_member_career
         │    entityName     = MemberCareer
         │    ftlDescription = 职业发展
         │    id             = row_1021
               └─ ... 还有2个子表
```

### 标准 JSON 格式输出

```json
{
  "projectPath": "/Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-alumni",
  "jspMode": "jvxe",
  "ftlDescription": "校友基础档案",
  "jformType": "2",
  "tableName_tmp": "us_alumni_members_member_profile",
  "entityName": "MemberProfile",
  "entityPackage": "members",
  "packageStyle": "service",
  "vueStyle": "vue3",
  "codeTypes": "controller,service,dao,mapper,entity,vue",
  "code": "7079ee1638944fc0be93f2d6d586eeb9",
  "tableName": "us_alumni_members_member_profile",
  "subList": [
    {
      "tableName": "us_alumni_members_member_education",
      "entityName": "MemberEducation",
      "ftlDescription": "教育背景",
      "id": "row_1020"
    },
    {
      "tableName": "us_alumni_members_member_career",
      "entityName": "MemberCareer",
      "ftlDescription": "职业发展",
      "id": "row_1021"
    }
  ]
}
```

## 与标准格式对比

脚本生成的 JSON 格式完全符合 JeecgBoot 官方标准：

- ✅ **参数顺序**: 按照官方标准顺序排列
- ✅ **主子表支持**: 自动识别并设置 `jformType: "2"` 和 `jspMode: "jvxe"`
- ✅ **子表结构**: 正确构建 `subList` 数组
- ✅ **字段完整**: 包含所有必需的字段和描述信息
