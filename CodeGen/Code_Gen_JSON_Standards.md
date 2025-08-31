# JeecgBoot 代码生成系统 - 统一标准规范

> **文档定位**: 代码生成系统的完整标准规范，包含变量定义、JSON 配置标准和验证规则
> **适用对象**: AIGC 系统、开发人员、配置文件生成器
> **核心目标**: 确保生成的配置文件 100%兼容 JeecgBoot API，统一变量规范

---

## 📋 **三核心变量定义**

### 🎯 核心变量规范

| 变量层级 | 变量名称            | 格式       | 示例                    | 用途               |
| -------- | ------------------- | ---------- | ----------------------- | ------------------ |
| 第一层   | **MODULE_NAME**     | lowercase  | dictd, finance, hrms    | 业务系统模块名称   |
| 第二层   | **SUBMODULE_NAME**  | lowercase  | datas, pages, invoice   | 系统内功能子模块   |
| 第三层   | **BUSINESS_ENTITY** | PascalCase | ExcelTemplate, PageInfo | 业务实体语义标识符 |

### 🔄 格式转换规则

**唯一核心概念**: BUSINESS_ENTITY (PascalCase, 推理源头)

**派生格式** (自动转换):

- **TABLE_SUFFIX**: exceltemplate (全小写连续)
- **URL_PATH**: excel-template (kebab-case)
- **FRONTEND_PATH**: datas/exceltemplate (路径分割)

**表名计算**: `us_{MODULE_NAME}_{SUBMODULE_NAME}_{TABLE_SUFFIX}`

---

## 🚨 **JSON 配置核心约束**

### ⚠️ **orderNum 连续性 - 致命约束**

**JeecgBoot API 强制要求**：字段 orderNum 必须从 0 开始**严格连续递增**！

```json
❌ 错误 - 导致API失败：
"orderNum": 0, 1, 2, 5, 6  // 跳过了3,4

✅ 正确 - API成功：
"orderNum": 0, 1, 2, 3, 4  // 严格连续
```

### 🏗️ **系统字段标准配置**

**7 个系统字段**（orderNum: 0-6，严格连续）：

```json
[
  "id",
  "create_by",
  "create_time",
  "update_by",
  "update_time",
  "sys_org_code",
  "del_flag"
]
```

### 📝 **JSON 配置结构**

```json
{
  "head": {
    "tableName": "us_{MODULE_NAME}_{SUBMODULE_NAME}_{TABLE_SUFFIX}",
    "tableTxt": "业务描述",
    "business_entity": "{BUSINESS_ENTITY}",
    "tableType": 1,
    "formCategory": "temp",
    "idType": "UUID",
    "isCheckbox": "Y",
    "themeTemplate": "normal",
    "formTemplate": "1",
    "scroll": 1,
    "isPage": "Y",
    "isTree": "N",
    "extConfigJson": "{...}",
    "isDesForm": "N",
    "desFormCode": ""
  },
  "metadata": {
    "generation_info": {
      "module_name": "{MODULE_NAME}",
      "submodule_name": "{SUBMODULE_NAME}",
      "business_entity": "{BUSINESS_ENTITY}",
      "inference_strategy": "推理策略",
      "semantic_analysis": "语义分析"
    },
    "derived_formats": {
      "table_suffix": "{TABLE_SUFFIX}",
      "url_path": "{URL_PATH}",
      "frontend_path": "{FRONTEND_PATH}"
    }
  },
  "fields": [
    // 7个系统字段 (orderNum: 0-6)
    // 业务字段 (orderNum: 7+)
  ],
  "indexs": [],
  "deleteFieldIds": [],
  "deleteIndexIds": []
}
```

## 🔍 **AIGC 验证清单**

### ✅ **5 步快速检查**

1. **表名格式**: `us_{module}_{submodule}_{entity}` 4 段式
2. **系统字段**: 前 7 个字段必须是标准系统字段
3. **orderNum 连续性**: 从 0 开始严格连续递增，无跳号
4. **metadata 完整性**: 包含 generation_info 和 derived_formats
5. **JSON 格式**: 语法正确，必需字段完整

### 🚫 **常见错误**

- ❌ orderNum 跳号: `0,1,2,5,6` → ✅ `0,1,2,3,4`
- ❌ 表名格式错误: `us_finance_invoice` → ✅ `us_finance_invoice_customerprofile`
- ❌ business_entity 通用化: `Management` → ✅ `CustomerProfile`
- ❌ 缺少 metadata 节点 → ✅ 完整包含两个子节点

### 🔧 **验证命令**

```bash
# 使用验证器检查
python3 Code_Gen_Validator.py temp_config.json
```

## 🎯 **AIGC 核心要点**

### **3 个关键原则**

1. **📋 严格模板**: 系统字段配置完全复制标准模板
2. **🔢 连续递增**: orderNum 从 0 开始严格连续，不能跳号
3. **🔍 立即验证**: 生成后立即使用验证工具检查

### **推理策略示例**

```
用户需求: "数据模版信息管理"
↓
MODULE_NAME: dictd (数据中台)
SUBMODULE_NAME: datas (数据管理)
BUSINESS_ENTITY: ExcelTemplate (Excel模版)
↓
TABLE_NAME: us_dictd_datas_exceltemplate
```

---

**版本**: 2.0
**创建日期**: 2025-07-30
**适用版本**: JeecgBoot 3.8.2+
