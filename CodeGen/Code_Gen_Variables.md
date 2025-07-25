# JeecgBoot 代码生成系统 - 核心变量规范 (重构版)

> **文档定位**: 代码生成系统核心变量的定义、使用规范和最佳实践  
> **配合文档**: Code_Gen_Agent.md (AI 提示词文档), Code_Gen_Guide.md (技术实现指南)  
> **重构版本**: 统一为BUSINESS_ENTITY概念，消除概念重复

---

## 📋 三核心变量概述 (统一后)

JeecgBoot 代码生成系统基于三个核心变量构建，统一概念后更加清晰和高效。

### 🎯 三核心变量定义

| 变量层级 | 变量名称 | 中文名称 | 定义 | 格式 | 示例 |
|---------|----------|------|------|------|------|
| 第一层 | **MODULE_NAME** | 业务系统模块名称 | 表示一级业务领域，对应业务系统类型 | lowercase | finance, hrms, crm |
| 第二层 | **SUBMODULE_NAME** | 系统内功能子模块 | 表示二级业务领域，对应业务系统内的功能模块 | lowercase | invoice, employee, customer |
| 第三层 | **BUSINESS_ENTITY** | 业务实体语义标识符 | 业务实体的语义化标识符，作为所有格式转换的单一源头 | PascalCase | CustomerProfile, ProductCatalog |

### 📊 核心变量关系

```
MODULE_NAME + SUBMODULE_NAME + BUSINESS_ENTITY → TABLE_NAME
                                               → PACKAGE_NAME
```

## 🔄 格式转换规则

**唯一核心概念**: BUSINESS_ENTITY = "CustomerProfile" (PascalCase, 推理源头)

**派生格式** (机械转换):
- **TABLE_SUFFIX**: customer_profile (snake_case转换)
- **URL_PATH**: customer-profile (kebab-case转换)
- **FRONTEND_PATH**: customer/profile (路径分割转换)
- **FILE_NAME**: customerProfile (camelCase转换)

**直接使用场景**:
- **Java类名**: 直接使用BUSINESS_ENTITY值，无需转换
- **配置传递**: entity_name参数直接使用BUSINESS_ENTITY
- **代码生成**: JeecgBoot API接收BUSINESS_ENTITY作为实体名

## 📋 推理策略

**BUSINESS_ENTITY 智能推理**:
1. **业务层次分析**: 识别主体 (客户/产品/订单)
2. **语义特征提取**: 识别功能 (档案/目录/订单)  
3. **领域前缀映射**: 客户 → Customer
4. **特征后缀映射**: 档案 → Profile
5. **智能组合生成**: Customer + Profile = CustomerProfile

## 🔍 三核心变量详解

### 1. MODULE_NAME (模块名/系统名称)

**定义**: 表示一级业务领域，对应业务系统类型。

**格式要求**:

- 小写英文单词
- 不包含下划线或其他特殊字符
- 优先使用核心业务系统，支持智能映射扩展

**推理方法**:

- 基于语义分析和上下文推理进行智能识别
- 通过业务本质和功能特征进行系统分类
- 支持新兴业务领域的智能映射

**核心业务系统**:

- `finance` - 财务管理系统
- `hrms` - 人力资源管理系统
- `crm` - 客户关系管理系统
- `scm` - 供应链管理系统
- `oa` - 办公自动化系统

**智能映射扩展**:

- 新兴业务领域(如医疗、教育、物流等)通过语义分析智能映射到核心系统
- 基于业务本质和功能特征进行合理归类
- 详细的映射策略请参考 Code_Gen_Agent.md 文档

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

### 3. BUSINESS_ENTITY (业务实体语义标识符) - 重构后统一概念

**定义**: 业务实体的语义化标识符，作为所有格式转换的单一源头，替代原有的ENTITY_NAME概念。

**格式要求**:

- PascalCase 命名规范
- 必须是语义化的业务实体名称
- 禁止使用通用化名称 (如info、management、data等)

**命名策略**:

- 业务领域前缀 + 实体特征后缀
- 体现明确的业务语义
- 遵循五步推理算法生成

**用途**:

- 构成表名的第三部分 (转换为snake_case)
- 直接作为Java实体名使用
- 生成前端路由和组件名
- 配置文件中的entity_name参数值

**正确示例**:

```
BUSINESS_ENTITY = "CustomerProfile"    # ✅ 语义化实体名称
BUSINESS_ENTITY = "ProductCatalog"     # ✅ 业务前缀+特征后缀
BUSINESS_ENTITY = "OrderHeader"        # ✅ 明确业务含义
```

**错误示例 (严禁使用)**:

```
BUSINESS_ENTITY = "info"               # ❌ 通用化名称
BUSINESS_ENTITY = "management"         # ❌ 过于抽象
BUSINESS_ENTITY = "data"               # ❌ 无业务语义
```

## 🔄 派生变量计算规则

### TABLE_NAME (表名)

**计算公式**: `us_{MODULE_NAME}_{SUBMODULE_NAME}_{TABLE_SUFFIX}`
**其中**: `TABLE_SUFFIX = pascal_to_snake_case(BUSINESS_ENTITY)`

**正确示例**:

```
MODULE_NAME = "finance"
SUBMODULE_NAME = "invoice"
BUSINESS_ENTITY = "CustomerProfile"
TABLE_SUFFIX = "customer_profile"  # 自动转换
TABLE_NAME = "us_finance_invoice_customer_profile"
```

### PACKAGE_NAME (包名)

**计算公式**: `org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}`

**示例**:

```
MODULE_NAME = "finance"
SUBMODULE_NAME = "invoice"
PACKAGE_NAME = "org.jeecg.modules.finance.invoice"
```

### Java 实体类名称

**直接使用**: `BUSINESS_ENTITY` (无需转换，已经是PascalCase格式)

**正确示例**:

```
BUSINESS_ENTITY = "CustomerProfile"     # ✅ 直接作为Java类名使用
BUSINESS_ENTITY = "ProductCatalog"      # ✅ 无需转换
BUSINESS_ENTITY = "OrderHeader"         # ✅ 已经是PascalCase格式
```

**错误示例 (严禁使用)**:

```  
ENTITY_NAME = "management"              # ❌ 旧概念，已废弃
JAVA_ENTITY_NAME = "Management"         # ❌ 通用化名称
```

### PROJECT_PATH (项目路径)

**计算公式**: `{PROJECT_PATH_PREFIX}/jeecg-boot/jeecg-boot-module/jeecg-module-{MODULE_NAME}`

**示例**:

```
PROJECT_PATH_PREFIX = "从Code_Gen_Config.json读取project.path_prefix"
MODULE_NAME = "finance"
PROJECT_PATH = "{PREFIX}/jeecg-boot/jeecg-boot-module/jeecg-module-finance"
```

## 📋 最佳实践

### 命名规范

1. **一致性原则**: 同一子模块下的所有表应该使用相同的 MODULE_NAME 和 SUBMODULE_NAME
2. **单词选择**: 优先使用单个英文单词，避免复合词和下划线
3. **语义明确**: 变量名应当清晰表达其业务含义

### 常见示例

#### 财务系统示例 (重构版 - 使用BUSINESS_ENTITY概念)

```
# 发票客户档案管理  
MODULE_NAME = "finance"
SUBMODULE_NAME = "invoice"
BUSINESS_ENTITY = "CustomerProfile"
TABLE_NAME = "us_finance_invoice_customer_profile"
PACKAGE_NAME = "org.jeecg.modules.finance.invoice"

# 付款处理流程
MODULE_NAME = "finance"
SUBMODULE_NAME = "payment"
BUSINESS_ENTITY = "ProcessRecord"
TABLE_NAME = "us_finance_payment_process_record"
PACKAGE_NAME = "org.jeecg.modules.finance.payment"
```

**❌ 错误示例对比 (旧版本 - 严禁使用)**:

```
# 错误示例 - 已废弃的通用化命名
ENTITY_NAME = "management"              # ❌ 通用化，无业务语义
JAVA_ENTITY_NAME = "Management"         # ❌ 过于抽象
ENTITY_NAME = "processing"              # ❌ 通用化，无业务语义
JAVA_ENTITY_NAME = "Processing"         # ❌ 过于抽象
```

#### 人力资源系统示例 (重构版 - 使用BUSINESS_ENTITY概念)

```
# 员工培训记录管理
MODULE_NAME = "hrms"
SUBMODULE_NAME = "employee"
BUSINESS_ENTITY = "TrainingRecord"
TABLE_NAME = "us_hrms_employee_training_record"
PACKAGE_NAME = "org.jeecg.modules.hrms.employee"

# 薪资计算报表
MODULE_NAME = "hrms"
SUBMODULE_NAME = "payroll"
BUSINESS_ENTITY = "SalaryReport"
TABLE_NAME = "us_hrms_payroll_salary_report"
PACKAGE_NAME = "org.jeecg.modules.hrms.payroll"
```

**❌ 错误示例对比 (旧版本 - 严禁使用)**:

```
# 错误示例 - 已废弃的通用化命名
ENTITY_NAME = "training"                # ❌ 过于简单，缺乏业务特征
JAVA_ENTITY_NAME = "Training"           # ❌ 不体现具体业务含义
ENTITY_NAME = "calculation"             # ❌ 通用化，无业务语义
JAVA_ENTITY_NAME = "Calculation"        # ❌ 过于抽象
```

#### 智能映射扩展示例

```
# 医疗领域 - 患者管理
用户需求: "医院患者信息管理"
智能映射: 患者管理 → 客户关系管理
五步推理: 患者(Patient) + 档案(Profile) = PatientProfile
MODULE_NAME = "crm"
SUBMODULE_NAME = "patient"
BUSINESS_ENTITY = "PatientProfile"
TABLE_NAME = "us_crm_patient_patient_profile"
PACKAGE_NAME = "org.jeecg.modules.crm.patient"

# 教育领域 - 学生管理
用户需求: "学校学生档案管理"
智能映射: 学生管理 → 客户关系管理
五步推理: 学生(Student) + 档案(Profile) = StudentProfile
MODULE_NAME = "crm"
SUBMODULE_NAME = "student"
BUSINESS_ENTITY = "StudentProfile"
TABLE_NAME = "us_crm_student_student_profile"
PACKAGE_NAME = "org.jeecg.modules.crm.student"
```

## ⚠️ 常见错误与避免方法

1. **包名使用实体名**: 包名必须使用子模块名，而不是实体名

   - ❌ `org.jeecg.modules.finance.management`
   - ✅ `org.jeecg.modules.finance.invoice`

2. **表名不完整**: 表名必须包含 4 个部分，缺一不可

   - ❌ `us_finance_invoice`
   - ✅ `us_finance_invoice_customer_profile` (基于BUSINESS_ENTITY语义化命名)

3. **命名不一致**: 同一子模块下的表应使用相同的包名结构

   - ❌ 同一子模块下使用不同的包名
   - ✅ 同一子模块下使用相同的包名

4. **BUSINESS_ENTITY 命名不规范**: 必须使用语义化的 PascalCase 命名
   - ❌ `management` (通用化，无业务语义)
   - ❌ `info` (过于抽象)
   - ✅ `CustomerProfile` (语义化，有明确业务含义)
   - ✅ `ProductCatalog` (遵循业务前缀+特征后缀模式)

---

## 🔄 智能变量处理流程

1. **语义分析**: AI 深度分析用户需求的业务本质和功能特征
2. **智能推理**: 基于语义理解和上下文推理提取三核心变量
3. **映射策略**: 优先映射到核心系统，必要时进行智能扩展
4. **变量验证**: 验证变量格式、业务合理性和映射逻辑
5. **派生变量计算**: 基于三核心变量计算派生变量
6. **置信度评估**: 对推理结果进行置信度评分
7. **用户确认**: 用户确认变量正确性和映射合理性
8. **代码生成**: 使用确认后的变量生成代码

**详细的推理策略和映射方法请参考 Code_Gen_Agent.md 文档**

## 📚 参考资料

- [JeecgBoot 开发手册](http://doc.jeecg.com)
- [Java 命名规范](https://www.oracle.com/java/technologies/javase/codeconventions-namingconventions.html)
- [数据库表命名规范](https://dev.mysql.com/doc/refman/8.0/en/identifier-length.html)
