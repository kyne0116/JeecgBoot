# JeecgBoot 代码生成系统 - 三核心变量规范

> **文档定位**: 代码生成系统三核心变量的定义、使用规范和最佳实践  
> **配合文档**: Code_Gen_Agent.md (AI提示词文档), Code_Gen_Guide.md (技术实现指南)

---

## 📋 三核心变量概述

JeecgBoot代码生成系统基于三个核心变量构建，这三个变量共同决定了生成代码的结构、命名和组织方式。理解和正确使用这三个变量是高效使用代码生成系统的关键。

### 🎯 三核心变量定义

| 变量层级 | 变量名称 | 中文名称 | 定义 | 示例 |
|---------|---------|---------|------|------|
| 第一层 | **MODULE_NAME** | 模块名/系统名称 | 表示一级业务领域，对应业务系统类型 | finance, hrms, crm |
| 第二层 | **SUBMODULE_NAME** | 子模块名/系统模块 | 表示二级业务领域，对应业务系统内的功能模块 | invoice, payment, employee |
| 第三层 | **ENTITY_NAME** | 业务场景/实体名称 | 表示操作对象，对应具体业务实体 | management, processing, info |

### 📊 派生变量关系

三核心变量会派生出多个关键变量，用于代码生成过程：

```
MODULE_NAME + SUBMODULE_NAME + ENTITY_NAME → TABLE_NAME
                                           → PACKAGE_NAME
                                           → JAVA_ENTITY_NAME
                                           → PROJECT_PATH
```

## 🔍 三核心变量详解

### 1. MODULE_NAME (模块名/系统名称)

**定义**: 表示一级业务领域，对应业务系统类型。

**格式要求**:
- 小写英文单词
- 不包含下划线或其他特殊字符
- 必须是预定义的业务系统之一

**允许值**:
- `finance` - 财务管理系统
- `hrms` - 人力资源管理系统
- `crm` - 客户关系管理系统
- `scm` - 供应链管理系统
- `oa` - 办公自动化系统

**用途**:
- 决定生成代码的模块位置
- 构成表名的第一部分
- 构成包名的第一部分
- 决定项目路径

**示例**:
```
MODULE_NAME = "finance"
```

### 2. SUBMODULE_NAME (子模块名/系统模块)

**定义**: 表示二级业务领域，对应业务系统内的功能模块。

**格式要求**:
- 小写英文单词
- 不包含下划线或其他特殊字符
- 应当是有意义的业务功能分类

**命名建议**:
- 使用单个英文单词
- 表示业务功能领域
- 避免使用过于通用的词汇

**用途**:
- 构成表名的第二部分
- 构成包名的第二部分
- 细化业务模块分类

**示例**:
```
SUBMODULE_NAME = "invoice"
```

### 3. ENTITY_NAME (业务场景/实体名称)

**定义**: 表示操作对象，对应具体业务实体。

**格式要求**:
- 小写英文单词
- 表名中使用小写形式
- Java实体使用PascalCase形式

**命名建议**:
- 使用单个英文单词
- 表示具体业务对象
- 避免使用过于抽象的词汇

**用途**:
- 构成表名的第三部分
- 转换为Java实体名
- 决定前端路由和组件名

**示例**:
```
ENTITY_NAME = "management"
JAVA_ENTITY_NAME = "Management"
```

## 🔄 派生变量计算规则

### TABLE_NAME (表名)

**计算公式**: `us_{MODULE_NAME}_{SUBMODULE_NAME}_{ENTITY_NAME}`

**示例**:
```
MODULE_NAME = "finance"
SUBMODULE_NAME = "invoice"
ENTITY_NAME = "management"
TABLE_NAME = "us_finance_invoice_management"
```

### PACKAGE_NAME (包名)

**计算公式**: `org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}`

**示例**:
```
MODULE_NAME = "finance"
SUBMODULE_NAME = "invoice"
PACKAGE_NAME = "org.jeecg.modules.finance.invoice"
```

### JAVA_ENTITY_NAME (Java实体名)

**计算公式**: `PascalCase({ENTITY_NAME})`

**示例**:
```
ENTITY_NAME = "management"
JAVA_ENTITY_NAME = "Management"
```

### PROJECT_PATH (项目路径)

**计算公式**: `{PROJECT_PATH_PREFIX}/jeecg-boot/jeecg-boot-module/jeecg-module-{MODULE_NAME}`

**示例**:
```
PROJECT_PATH_PREFIX = "/Users/admin/Work/Github/JeecgBoot"
MODULE_NAME = "finance"
PROJECT_PATH = "/Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-finance"
```

## 📋 最佳实践

### 命名规范

1. **一致性原则**: 同一子模块下的所有表应该使用相同的MODULE_NAME和SUBMODULE_NAME
2. **单词选择**: 优先使用单个英文单词，避免复合词和下划线
3. **语义明确**: 变量名应当清晰表达其业务含义

### 常见示例

#### 财务系统示例

```
# 发票管理
MODULE_NAME = "finance"
SUBMODULE_NAME = "invoice"
ENTITY_NAME = "management"
TABLE_NAME = "us_finance_invoice_management"
PACKAGE_NAME = "org.jeecg.modules.finance.invoice"
JAVA_ENTITY_NAME = "Management"

# 付款处理
MODULE_NAME = "finance"
SUBMODULE_NAME = "payment"
ENTITY_NAME = "processing"
TABLE_NAME = "us_finance_payment_processing"
PACKAGE_NAME = "org.jeecg.modules.finance.payment"
JAVA_ENTITY_NAME = "Processing"
```

#### 人力资源系统示例

```
# 员工培训
MODULE_NAME = "hrms"
SUBMODULE_NAME = "employee"
ENTITY_NAME = "training"
TABLE_NAME = "us_hrms_employee_training"
PACKAGE_NAME = "org.jeecg.modules.hrms.employee"
JAVA_ENTITY_NAME = "Training"

# 薪资计算
MODULE_NAME = "hrms"
SUBMODULE_NAME = "payroll"
ENTITY_NAME = "calculation"
TABLE_NAME = "us_hrms_payroll_calculation"
PACKAGE_NAME = "org.jeecg.modules.hrms.payroll"
JAVA_ENTITY_NAME = "Calculation"
```

## ⚠️ 常见错误与避免方法

1. **包名使用实体名**: 包名必须使用子模块名，而不是实体名
   - ❌ `org.jeecg.modules.finance.management`
   - ✅ `org.jeecg.modules.finance.invoice`

2. **表名不完整**: 表名必须包含4个部分，缺一不可
   - ❌ `us_finance_invoice`
   - ✅ `us_finance_invoice_management`

3. **命名不一致**: 同一子模块下的表应使用相同的包名结构
   - ❌ 同一子模块下使用不同的包名
   - ✅ 同一子模块下使用相同的包名

4. **Java命名不规范**: 实体名必须符合Java驼峰命名规范
   - ❌ `management` (作为Java类名)
   - ✅ `Management` (作为Java类名)

---

## 🔄 变量处理流程

1. **变量收集**: AI分析用户需求，提取三核心变量
2. **变量验证**: 验证变量格式和业务合理性
3. **派生变量计算**: 基于三核心变量计算派生变量
4. **变量确认**: 用户确认变量正确性
5. **代码生成**: 使用确认后的变量生成代码

## 📚 参考资料

- [JeecgBoot开发手册](http://doc.jeecg.com)
- [Java命名规范](https://www.oracle.com/java/technologies/javase/codeconventions-namingconventions.html)
- [数据库表命名规范](https://dev.mysql.com/doc/refman/8.0/en/identifier-length.html)
