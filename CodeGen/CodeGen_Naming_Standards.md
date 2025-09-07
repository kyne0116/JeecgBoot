# JeecgBoot CodeGen 系统命名规范文档

## 概述

本文档全面汇总了JeecgBoot CodeGen系统关于表名和对象类名的命名规范，基于对系统配置文件、模板文件、验证器和实际生成示例的深入分析。

## 1. 表名命名规范 (tableName)

### 1.1 基本格式

**标准格式**: `{MODULE_NAME}_{SUBMODULE_NAME}_{ENTITY_SUFFIX}`

- **模块名**: `{MODULE_NAME}` - 业务系统模块名，小写字母
- **子模块名**: `{SUBMODULE_NAME}` - 功能子模块名，小写字母  
- **实体后缀**: `{ENTITY_SUFFIX}` - 领域对象的实体类英文去驼峰后的全称，小写字母

### 1.2 命名规则

- **字符集**: 仅包含小写字母、数字、下划线
- **分隔符**: 使用下划线 `_` 分隔各部分
- **严格段数**: 必须正好3段（模块 + 子模块 + 实体）
- **不可扩展**: 不支持4段式或更多段式命名

### 1.3 实际示例

```
# 独立表示例
alumni_members_memberprofile
education_student_studentinfo

# 主表示例  
education_student_studentinfo

# 子表示例
education_student_parentinfo
education_student_classmateinfo
alumni_members_education
alumni_members_career
```

### 1.4 派生规则

- **MODULE_NAME**: `alumni`, `education`, `finance`, `hrms`
- **SUBMODULE_NAME**: `members`, `student`, `invoice`, `employee`
- **ENTITY_SUFFIX**: 从 `BUSINESS_ENTITY` 去驼峰转换而来（实体类英文全称转小写）
  - `CustomerProfile` → `customerprofile`
  - `StudentInfo` → `studentinfo`
  - `InvoiceHeader` → `invoiceheader`
  - `EmployeeProfile` → `employeeprofile`

## 2. Java实体类名命名规范

### 2.1 业务实体名 (business_entity)

**格式**: `PascalCase` (大驼峰命名法)

- **首字母大写**: 每个单词首字母大写
- **无分隔符**: 不使用下划线或连字符
- **字符集**: 字母和数字，以字母开头
- **语义化**: 避免使用 `Management`、`Info`、`Data` 等通用词汇

### 2.2 实际示例

```
# 主表实体名
MemberProfile        # 会员档案
StudentInfo          # 学生信息
CustomerProfile      # 客户档案
InvoiceDetail       # 发票详情

# 子表实体名
MemberEducation      # 会员教育背景
MemberCareer        # 会员职业发展
ParentInfo          # 家长信息
ClassmateInfo       # 同学信息
```

### 2.3 子表实体名 (entityName)

**subList配置中的entityName字段**:

- **格式**: `PascalCase`
- **关联性**: 通常以主表实体名为前缀
- **语义清晰**: 明确表达子表业务含义

```json
"subList": [
  {
    "tableName": "alumni_members_education",
    "entityName": "MemberEducation",
    "ftlDescription": "教育背景",
    "id": "row_1020"
  }
]
```

## 3. Java包名命名规范 (packageName)

### 3.1 标准格式

**包名模板**: `org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}`

- **固定前缀**: `org.jeecg.modules`
- **模块路径**: `{MODULE_NAME}.{SUBMODULE_NAME}`
- **全小写**: 所有字母小写
- **点分隔**: 使用点号分隔包层级

### 3.2 实际示例

```java
org.jeecg.modules.alumni.members     // 校友会员模块
org.jeecg.modules.education.student  // 教育学生模块  
org.jeecg.modules.finance.invoice    // 财务发票模块
org.jeecg.modules.hrms.employee      // 人力资源员工模块
```

### 3.3 代码生成中的应用

```java
// 生成的Controller类
package org.jeecg.modules.education.student.controller;

// 生成的Service类
package org.jeecg.modules.education.student.service;

// 生成的Entity类
package org.jeecg.modules.education.student.entity;
```

## 4. 前端路径命名规范

### 4.1 URL路径 (url_path)

**格式**: `/{MODULE_NAME}/{SUBMODULE_NAME}/{ENTITY_PATH}`

- **前导斜杠**: 以 `/` 开头
- **小驼峰**: 实体部分使用camelCase
- **RESTful风格**: 符合REST API设计规范

### 4.2 前端文件路径 (frontend_path)

**格式**: `src/views/{MODULE_NAME}/{SUBMODULE_NAME}/{ENTITY_NAME}`

- **固定前缀**: `src/views/`
- **目录结构**: 按模块层级组织
- **PascalCase**: 实体名保持大驼峰

### 4.3 实际示例

```javascript
// URL路径示例
/alumni/members/memberProfile
/education/student/studentInfo
/education/student/parentInfo

// 前端文件路径示例  
src/views/alumni/members/MemberProfile
src/views/education/student/StudentInfo
src/views/education/student/ParentInfo
```

## 5. 核心变量系统

### 5.1 三核心变量

CodeGen系统基于三个核心变量自动派生所有命名:

```json
{
  "MODULE_NAME": "education",        // 业务模块名
  "SUBMODULE_NAME": "student",       // 功能子模块名  
  "BUSINESS_ENTITY": "StudentInfo"   // 核心业务实体
}
```

### 5.2 自动派生格式

```json
{
  "TABLE_SUFFIX": "studentinfo",              // 表后缀 (BUSINESS_ENTITY → lowercase)
  "URL_PATH": "/education/student/studentInfo", // URL路径 (camelCase)
  "FRONTEND_PATH": "src/views/education/student/StudentInfo", // 前端路径 (PascalCase)
  "PACKAGE_NAME": "org.jeecg.modules.education.student"       // Java包名 (lowercase)
}
```

## 6. 主子表特殊命名规则

### 6.1 主表配置

主表需要在 `subTableStr` 中声明所有子表:

```json
{
  "head": {
    "tableName": "education_student_studentinfo",
    "business_entity": "StudentInfo", 
    "tableType": 2,
    "subTableStr": "education_student_parentinfo,education_student_classmateinfo"
  }
}
```

### 6.2 子表配置

子表需要正确的关联配置:

```json
{
  "head": {
    "tableName": "education_student_parentinfo",
    "business_entity": "ParentInfo",
    "tableType": 3,
    "relationType": 0,       // 一对多关系
    "tabOrderNum": 1         // 显示顺序
  }
}
```

### 6.3 subList ID规则

子表ID必须从 `row_1020` 开始连续递增:

```json
"subList": [
  {"id": "row_1020"},  // 第一个子表
  {"id": "row_1021"},  // 第二个子表  
  {"id": "row_1022"}   // 第三个子表
]
```

## 7. 字段名命名约束

### 7.1 数据库字段名 (dbFieldName)

**重要约束**: 最大长度 **32字符**

- **原因**: 对应数据库表 `onl_cgform_field.db_field_name varchar(32)`
- **格式**: 小写字母开头，可包含数字和下划线
- **模式**: `^[a-z][a-z0-9_]*$`

### 7.2 常见缩写建议

为避免字段名超长，建议使用标准缩写:

```
information → info
description → desc
configuration → config
management → mgmt
customer → cust
employee → emp
department → dept
organization → org
```

## 8. 验证规则

### 8.1 核心验证项

CodeGen_Validator.py 执行以下关键验证:

1. **表名格式验证**: 必须符合3段式格式
2. **实体名格式验证**: 必须为PascalCase
3. **字段名长度验证**: 不能超过32字符
4. **orderNum连续性验证**: 防止API调用失败
5. **主子表一致性验证**: 模块名必须匹配

### 8.2 自动修正建议

系统提供智能字段名缩短建议:

```
customer_profile_information_description → cust_prof_info_desc
student_academic_performance_evaluation → stud_acad_perf_eval
```

## 9. 最佳实践建议

### 9.1 命名原则

1. **语义清晰**: 名称能清楚表达业务含义
2. **一致性**: 整个系统使用统一的命名规范
3. **简洁性**: 在表达清楚的前提下尽量简洁
4. **可扩展性**: 便于后续功能扩展

### 9.2 常见陷阱

1. **避免通用词**: 不使用 `Management`、`System`、`Data` 等
2. **注意长度限制**: 特别是字段名的32字符限制
3. **保持模块一致性**: 主子表必须在同一模块下
4. **orderNum连续性**: 必须从0开始严格连续递增
5. **表名简洁性**: 使用3段式结构，实体后缀采用全小写连续字符
6. **严禁四段式**: 禁止使用如 `crm_customer_customer_profile`、`education_student_student_info`、`finance_invoice_invoice_header` 等四段式表名

### 9.3 实施建议

1. 使用 `Code_Gen_Validator.py` 进行配置验证
2. 参考 `Example_Independent_Table.json` 和 `Example_Main_Sub_Table.json` 示例
3. 遵循 `Code_Gen_Spec.json` 中的AI生成指导
4. 定期检查生成结果的命名一致性

---

**文档版本**: v1.0  
**最后更新**: 2025-09-06  
**适用版本**: JeecgBoot 3.8.2+