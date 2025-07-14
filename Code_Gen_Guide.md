# JeecgBoot Code_Gen 技术实现指南

> **文档定位**: Code_Gen工作流的技术实现指南和使用手册（面向AI理解优化）  
> **配合文档**: Code_Gen_Agent.md (AI行为规范)

---

## 📋 系统架构概览

### 工作流程图
```
用户业务需求 → 需求分析 → 确认与选择 → 配置生成 → 代码生成 → 完整模块
     ↓            ↓           ↓           ↓           ↓          ↓
   自然语言    关键词提取   参数确认     JSON配置   脚本执行   完整CRUD
```

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

| 组件名称 | 类型 | 功能定位 | 主要职责 |
|----------|------|----------|----------|
| **Code_Gen_Guide.py** | 执行引擎 | 主工作流脚本 | 登录、创建表单、同步数据库、生成代码 |
| **Code_Gen_Config.json** | 系统配置 | 全局参数配置 | 服务器地址、认证信息、项目路径 |
| **Code_Gen_Guide.json** | 配置模板 | 标准表单模板 | 7个系统字段定义、表单基础结构 |
| **Code_Gen_field_templates.json** | 字段模板库 | 字段类型定义 | 各种字段类型的完整配置模板 |
| **Code_Gen_DICT.json** | 数据字典 | 字典数据缓存 | 系统数据字典的本地缓存 |

---

## 🔧 核心文件详解

### 1. Code_Gen_Guide.py - 主执行脚本

**功能**: 核心工作流执行引擎，负责完整的代码生成流程

**主要函数**:
```python
def extract_business_entity_from_table_name(table_name):
    """从表名中提取业务实体名，仅支持us_{模块}_{子模块}_{场景}格式"""
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
  --module-name TEXT          模块名称 (hrms/crm/scm/oa/finance)
  --form-config TEXT          表单配置文件路径
  --dict                      更新数据字典缓存
  --help                      显示帮助信息
```

**使用示例**:
```bash
# 生成代码
python Code_Gen_Guide.py --module-name finance --form-config temp_sales_config.json

# 更新数据字典
python Code_Gen_Guide.py --dict
```

### 2. Code_Gen_Config.json - 系统配置

**功能**: 系统全局配置参数，控制脚本行为

**配置结构**:
```json
{
  "project": {
    "path_prefix": "/path/to/JeecgBoot"
  },
  "server": {
    "base_url": "http://localhost:8080/jeecg-boot",
    "username": "admin",
    "password": "123456"
  },
  "timeouts": {
    "login": 10,
    "create": 30,
    "sync": 30,
    "codegen": 60
  },
  "codegen": {
    "vue_style": "vue3",
    "code_types": "controller,service,dao,mapper,entity,vue"
  }
}
```

**可配置项说明**:
| 配置项 | 类型 | 描述 | 默认值 | 是否必填 |
|--------|------|------|--------|----------|
| `project.path_prefix` | String | JeecgBoot项目路径 | `/Users/admin/Work/Github/JeecgBoot` | ✅ |
| `server.base_url` | String | 服务器地址 | `http://localhost:8080/jeecg-boot` | ✅ |
| `server.username` | String | 登录用户名 | `admin` | ✅ |
| `server.password` | String | 登录密码 | `123456` | ✅ |
| `codegen.vue_style` | String | Vue版本 | `vue3` | ❌ |
| `codegen.code_types` | String | 生成代码类型 | `controller,service,dao,mapper,entity,vue` | ❌ |

### 3. Code_Gen_Guide.json - 配置模板

**功能**: 标准表单配置模板，包含系统必需字段

**结构说明**:
```json
{
  "head": {
    "tableName": "{{TABLE_NAME}}",        // 模板变量-表名
    "tableTxt": "{{TABLE_DESCRIPTION}}",  // 模板变量-表描述
    "tableType": 1,                       // 固定值-表类型
    "formCategory": "temp",               // 固定值-表单分类
    "idType": "UUID",                     // 固定值-主键类型
    "isCheckbox": "Y",                    // 固定值-是否支持复选
    "themeTemplate": "normal",            // 固定值-主题模板
    "formTemplate": "1",                  // 固定值-表单模板
    "scroll": 1,                          // 固定值-滚动设置
    "isPage": "Y",                        // 固定值-是否分页
    "isTree": "N"                         // 固定值-是否树形
  },
  "fields": [
    // 0-6: 7个系统字段 (不可修改)
    {
      "orderNum": 0,
      "dbFieldName": "id",
      "dbFieldTxt": "Primary Key",
      "dbType": "string",
      "dbIsKey": "1",
      "dbIsNull": "0"
    }
    // ... 其他6个系统字段
    // 7+: 业务字段区域 (可添加字段)
  ]
}
```

**使用规则**:
- 🚫 **禁止修改**: `head`部分的固定值字段
- 🚫 **禁止修改**: `fields`数组中orderNum 0-6的系统字段
- ✅ **允许替换**: `{{TABLE_NAME}}`和`{{TABLE_DESCRIPTION}}`模板变量
- ✅ **允许添加**: orderNum 7+的业务字段

### 4. Code_Gen_field_templates.json - 字段模板库

**功能**: 提供各种字段类型的完整配置模板

**字段类型定义**:
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

**支持的字段类型**:
| 类型名称 | 用途 | 数据库类型 | 前端组件 | 特殊配置 |
|----------|------|------------|----------|----------|
| `text_field` | 文本字段 | string | input | 无 |
| `number_field` | 数字字段 | int | input-number | 无 |
| `decimal_field` | 小数字段 | decimal | input-number | 精度设置 |
| `date_field` | 日期字段 | date | date-picker | 无 |
| `datetime_field` | 日期时间字段 | datetime | datetime-picker | 无 |
| `textarea_field` | 多行文本字段 | text | textarea | 行数设置 |
| `dict_select_field` | 字典下拉字段 | string | select | 需要dictField |
| `dict_radio_field` | 字典单选字段 | string | radio | 需要dictField |
| `file_upload_field` | 文件上传字段 | string | upload | 文件类型限制 |
| `image_upload_field` | 图片上传字段 | string | upload | 图片限制 |
| `rich_text_field` | 富文本字段 | text | rich-editor | 无 |
| `phone_field` | 手机号字段 | string | input | 格式验证 |
| `email_field` | 邮箱字段 | string | input | 格式验证 |

### 5. Code_Gen_DICT.json - 数据字典

**功能**: 系统数据字典的本地缓存，用于字段类型匹配

**数据结构**:
```json
[
  {
    "dictCode": "sex",
    "dictName": "性别",
    "dictItems": [
      {"itemValue": "1", "itemText": "男"},
      {"itemValue": "2", "itemText": "女"}
    ]
  },
  {
    "dictCode": "yes_no",
    "dictName": "是否",
    "dictItems": [
      {"itemValue": "Y", "itemText": "是"},
      {"itemValue": "N", "itemText": "否"}
    ]
  }
]
```

**更新机制**:
- 缓存时间: 24小时
- 更新命令: `python Code_Gen_Guide.py --dict`
- 数据来源: JeecgBoot系统的数据字典管理

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
| 文件类型 | 主要内容 | 功能说明 |
|----------|----------|----------|
| `Entity.java` | 实体类定义、字段映射、注解配置 | 数据表的Java对象表示 |
| `Controller.java` | REST API接口、请求处理、参数验证 | 前端请求的入口点 |
| `Service.java` | 业务逻辑接口定义 | 业务逻辑的抽象 |
| `ServiceImpl.java` | 具体业务逻辑实现 | 实际的业务处理代码 |
| `Mapper.java` | 数据访问接口、SQL方法定义 | 数据库操作的接口 |
| `Mapper.xml` | SQL语句、结果映射 | 具体的SQL实现 |
| `List.vue` | 列表展示、查询、操作按钮 | 数据列表页面 |
| `Form.vue` | 表单录入、编辑、验证 | 数据录入页面 |
| `Modal.vue` | 弹窗组件、详情展示 | 弹窗式操作组件 |

---

## 📖 使用指南

### 命令行参数说明

#### 基本用法
```bash
python Code_Gen_Guide.py --module-name <模块名> --form-config <配置文件>
```

#### 参数详解
| 参数 | 必填 | 类型 | 描述 | 示例 |
|------|------|------|------|------|
| `--module-name` | ✅ | String | 目标模块名称 | `finance` |
| `--form-config` | ✅ | String | 配置文件路径 | `temp_sales_config.json` |
| `--dict` | ❌ | Flag | 更新数据字典 | 无参数 |
| `--help` | ❌ | Flag | 显示帮助信息 | 无参数 |

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
| 属性名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| `orderNum` | Integer | ✅ | 排序号(从7开始) | `7` |
| `dbFieldName` | String | ✅ | 数据库字段名 | `invoice_number` |
| `dbFieldTxt` | String | ✅ | 字段显示名 | `发票号码` |
| `dbType` | String | ✅ | 数据库类型 | `string/int/decimal/date/datetime/text` |
| `dbLength` | Integer | ✅ | 字段长度 | `50` |
| `dbPointLength` | Integer | ❌ | 小数位数 | `2` |
| `dbIsNull` | String | ✅ | 是否可空 | `0`(非空) / `1`(可空) |
| `fieldMustInput` | String | ✅ | 是否必填 | `0`(非必填) / `1`(必填) |
| `isShowForm` | String | ✅ | 表单中显示 | `0`(不显示) / `1`(显示) |
| `isShowList` | String | ✅ | 列表中显示 | `0`(不显示) / `1`(显示) |
| `fieldShowType` | String | ✅ | 前端组件类型 | `text/select/radio/textarea/date/datetime` |
| `dictField` | String | ❌ | 数据字典编码 | `invoice_status` |

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
      {"itemValue": "active", "itemText": "激活"},
      {"itemValue": "inactive", "itemText": "停用"},
      {"itemValue": "pending", "itemText": "待审核"}
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
- 实体名: 使用Java驼峰命名规范

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

**📚 技术支持**: 本文档提供Code_Gen系统的完整技术实现细节，配合Code_Gen_Agent.md使用可实现完整的代码生成功能。