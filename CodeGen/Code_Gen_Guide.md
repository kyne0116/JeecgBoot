# JeecgBoot 代码生成工具使用指南

> **功能**: 基于 JeecgBoot 在线表单 API 的完整代码生成工作流
> **配合文档**: Code_Gen_Agent.md (AI 推理规范)
> **目标用户**: 开发者、系统维护人员

---

## 🚀 快速开始

### 环境要求

- Python 3.7+
- JeecgBoot 后端服务运行在 http://localhost:8080
- Maven 3.6+

### 基本用法

```bash
# 1. 获取最新数据字典
python3 Code_Gen_Guide.py --dict

# 2. 生成代码
python3 Code_Gen_Guide.py --module-name finance --form-config temp_management_config.json

# 3. 验证表名格式
python3 Code_Gen_Guide.py --validate-table-name us_finance_invoice_management
```

---

## 📋 配置文件结构

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
- 必须包含 7 个系统字段：id, create_by, create_time, update_by, update_time, sys_org_code, del_flag
- 业务字段 orderNum 从 8 开始

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

## 🔄 工作流程

1. **获取数据字典**:

   ```bash
   python3 Code_Gen_Guide.py --dict
   ```

2. **准备配置文件**: 创建包含表结构和字段定义的 JSON 配置文件

3. **执行代码生成**:

   ```bash
   python3 Code_Gen_Guide.py --module-name finance --form-config temp_invoice_config.json
   ```

4. **验证生成结果**: 检查生成的代码和数据库表

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

## ⚠️ 常见问题

### 1. 登录失败

- 检查 JeecgBoot 服务是否启动
- 验证 Code_Gen_Config.json 中的用户名密码

### 2. 表名格式错误

- 使用标准格式：`us_{模块}_{子模块}_{业务场景}`
- 运行验证命令检查格式

### 3. 模块不存在

- 脚本会自动创建 Maven 模块
- 检查项目路径配置是否正确

### 4. 数据字典匹配失败

- 运行 `python3 Code_Gen_Guide.py --dict` 更新字典缓存
- 检查字典编码是否存在

---

## 📚 相关文档

- **Code_Gen_Agent.md**: AI 推理规范和业务分析方法
- **Code_Gen_Variables.md**: 核心变量定义和使用规范
- **Code_Gen_Validator.py**: 配置文件验证工具
