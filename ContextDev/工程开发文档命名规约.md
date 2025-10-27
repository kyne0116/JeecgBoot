# JeecgBoot AI Agent 协作文件命名规范 v5.0

**版本**: v5.0  
**更新日期**: 2025-08-04  
**适用范围**: 所有 JeecgBoot AI Agent 协作项目  
**目标**: 标准化文件命名，优化 AI 协作效率

---

## 🎯 核心原则

### 📋 命名标准

- **简洁性**: 文件名简洁明了，避免冗余
- **描述性**: 文件名直接反映内容和功能
- **一致性**: 统一的命名格式和规范
- **AI 友好**: 便于 AI 识别和处理

### 🔄 协作优化

- **标准化**: 统一的 6-Agent 协作文件格式
- **可追溯**: 完整的文档追溯链
- **可识别**: 清晰的 Agent 和阶段标识
- **可扩展**: 支持项目规模扩展

---

## 📁 文件命名格式

### 🏗️ 基础格式

```
[SYSTEM]-[MODULE]-[TIMESTAMP]-[AGENT]-[TITLE].yaml
```

### 📊 组件说明

- **SYSTEM**: 系统代码 (2-4 位英文)
- **MODULE**: 模块代码 (3-8 位英文)
- **TIMESTAMP**: 时间戳 (YYYYMMDDHHMMSS)
- **AGENT**: Agent 代码 (REQ|PROTO|ARCH|DEV|TEST)
- **TITLE**: 功能标题 (4-8 个中文字符)

---

## 🎯 命名组件详解

### 1. 系统代码 (SYSTEM)

```yaml
常用系统代码:
  HAIR: 美发管理系统
  ECOM: 电商系统
  CRM: 客户关系管理
  HRM: 人力资源管理
  OA: 办公自动化
  ERP: 企业资源规划
  LMS: 学习管理系统
  CMS: 内容管理系统

命名规则:
  - 长度: 2-4位英文字母
  - 格式: 全大写
  - 语义: 业务领域缩写
  - 唯一性: 项目内唯一
```

### 2. 模块代码 (MODULE)

```yaml
模块代码示例:
  CUSTOMER: 客户管理
  BOOKING: 预约管理
  PRODUCT: 产品管理
  ORDER: 订单管理
  USER: 用户管理
  PAYMENT: 支付管理
  INVENTORY: 库存管理
  REPORT: 报表管理

命名规则:
  - 长度: 3-8位英文字母
  - 格式: 全大写
  - 语义: 功能模块名称
  - 清晰性: 业务含义明确
```

### 3. 时间戳 (TIMESTAMP)

```yaml
格式: YYYYMMDDHHMMSS
示例: 20250804143000 (2025年8月4日14:30:00)

用途:
  - 版本标识: 唯一标识文档版本
  - 时间序列: 支持时间序列分析
  - 追溯支持: 便于版本追溯
  - 冲突避免: 避免文件名冲突
```

### 4. Agent 代码 (AGENT)

```yaml
标准Agent代码:
  REQ: 需求分析 (agent-2)
  PROTO: 原型设计 (agent-3)
  ARCH: 架构设计 (agent-4)
  DEV: 开发任务 (agent-5)
  TEST: 测试设计 (agent-6)

协作映射: REQ → agent-2 (需求分析师)
  PROTO → agent-3 (原型设计师)
  ARCH → agent-4 (系统架构师)
  DEV → agent-5 (开发工程师)
  TEST → agent-6 (质量测试师)
```

### 5. 功能标题 (TITLE)

```yaml
标题命名规则:
  长度: 4-8个中文字符
  语义: 核心业务功能
  风格: 业务术语，非技术术语
  一致性: 同系统内风格统一

优秀示例: ✅ 客户信息管理
  ✅ 预约调度功能
  ✅ 订单支付处理
  ✅ 库存同步机制
  ✅ 用户权限控制

避免示例: ❌ CustomerCRUDModule (技术化)
  ❌ 客户增删改查管理系统 (冗长)
  ❌ CRM模块 (缺乏描述)
  ❌ 功能模块A (无业务含义)
```

---

## 📂 存储结构规范

### 🏗️ 目录组织

```
AIGC/
├── system_base_info_[SYSTEM].yaml           # 系统基础信息
├── requirement_baseline_[SYSTEM]_[MODULE].yaml  # 模块需求基线
└── [SYSTEM]_[MODULE]/                       # 模块协作文档
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-REQ-[TITLE].yaml
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-PROTO-[TITLE].yaml
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-ARCH-[TITLE].yaml
    ├── [SYSTEM]-[MODULE]-[TIMESTAMP]-DEV-[TITLE].yaml
    └── [SYSTEM]-[MODULE]-[TIMESTAMP]-TEST-[TITLE].yaml
```

### 📋 文件类型说明

```yaml
系统级文件:
  system_base_info_[SYSTEM].yaml:
    用途: 系统基础配置和技术栈
    示例: system_base_info_HAIR.yaml

模块级文件:
  requirement_baseline_[SYSTEM]_[MODULE].yaml:
    用途: 模块需求基线和变更管理
    示例: requirement_baseline_HAIR_CUSTOMER.yaml

协作级文件:
  [完整命名格式]:
    用途: 4-Agent协作文档链
    示例: HAIR-CUSTOMER-20250804143000-REQ-客户信息管理.yaml
```

---

## 🎯 命名示例

### 📊 完整示例

```yaml
# 美发管理系统 - 客户管理模块
系统基础: system_base_info_HAIR.yaml
模块基线: requirement_baseline_HAIR_CUSTOMER.yaml
协作文档:
  - HAIR-CUSTOMER-20250804143000-REQ-客户信息管理.yaml
  - HAIR-CUSTOMER-20250804143000-ARCH-客户信息管理.yaml
  - HAIR-CUSTOMER-20250804143000-DEV-客户信息管理.yaml
  - HAIR-CUSTOMER-20250804143000-TEST-客户信息管理.yaml

# 电商系统 - 订单管理模块
系统基础: system_base_info_ECOM.yaml
模块基线: requirement_baseline_ECOM_ORDER.yaml
协作文档:
  - ECOM-ORDER-20250804150000-REQ-订单支付处理.yaml
  - ECOM-ORDER-20250804150000-PROTO-订单支付处理.yaml
  - ECOM-ORDER-20250804150000-ARCH-订单支付处理.yaml
  - ECOM-ORDER-20250804150000-DEV-订单支付处理.yaml
  - ECOM-ORDER-20250804150000-TEST-订单支付处理.yaml
```

### 🔄 协作链示例

```yaml
# 6-Agent协作链完整示例
项目: 人力资源管理系统 - 员工管理模块

Step 1 - agent-1 (基线管理):
  输入: 业务需求描述
  输出: 系统基线和模块基线文档

Step 2 - agent-2 (需求分析):
  输入: 基线文档
  输出: HRM-EMPLOYEE-20250804143000-REQ-员工信息管理.yaml

Step 3 - agent-3 (原型设计):
  输入: HRM-EMPLOYEE-20250804143000-REQ-员工信息管理.yaml
  输出: HRM-EMPLOYEE-20250804143000-PROTO-员工信息管理.yaml

Step 4 - agent-4 (架构设计):
  输入: HRM-EMPLOYEE-20250804143000-PROTO-员工信息管理.yaml
  输出: HRM-EMPLOYEE-20250804143000-ARCH-员工信息管理.yaml

Step 5 - agent-5 (开发任务):
  输入: HRM-EMPLOYEE-20250804143000-ARCH-员工信息管理.yaml
  输出: HRM-EMPLOYEE-20250804143000-DEV-员工信息管理.yaml

Step 6 - agent-6 (测试设计):
  输入: HRM-EMPLOYEE-20250804143000-DEV-员工信息管理.yaml
  输出: HRM-EMPLOYEE-20250804143000-TEST-员工信息管理.yaml
```

---

## ✅ 质量检查清单

### 📋 命名检查

```yaml
系统代码检查: □ 长度符合规范 (2-4位)
  □ 全大写英文字母
  □ 业务语义清晰
  □ 项目内唯一

模块代码检查: □ 长度符合规范 (3-8位)
  □ 全大写英文字母
  □ 功能含义明确
  □ 系统内唯一

时间戳检查: □ 格式正确 (YYYYMMDDHHMMSS)
  □ 时间合理性
  □ 版本唯一性

Agent代码检查: □ 使用标准代码 (REQ|PROTO|ARCH|DEV|TEST)
  □ 协作顺序正确
  □ 映射关系准确

功能标题检查: □ 长度适中 (4-8个中文字符)
  □ 业务语义清晰
  □ 术语使用规范
  □ 风格保持一致
```

### 🏗️ 结构检查

```yaml
存储结构检查: □ 目录结构符合规范
  □ 文件存储位置正确
  □ 系统级文件完整
  □ 模块级文件完整
  □ 协作级文件完整

协作链检查: □ 6-Agent文档完整
  □ 时间戳保持一致
  □ 追溯关系清晰
  □ 数据传递准确
```

---

## 🚀 使用指南

### 📋 快速开始

```yaml
Step 1: 确定系统和模块
  - 选择或创建系统代码 (如: HAIR)
  - 选择或创建模块代码 (如: CUSTOMER)

Step 2: 生成时间戳
  - 使用当前时间生成14位时间戳
  - 确保在协作链中保持一致

Step 3: 选择Agent类型
  - REQ: 需求分析阶段
  - ARCH: 架构设计阶段
  - DEV: 开发任务阶段
  - TEST: 测试设计阶段

Step 4: 定义功能标题
  - 使用4-8个中文字符
  - 体现核心业务功能
  - 保持术语一致性

Step 5: 组合完整文件名
  - 按格式组合各部分
  - 验证命名规范性
  - 确认存储位置
```

### 🎯 最佳实践

```yaml
命名最佳实践:
  - 提前规划系统和模块代码
  - 建立项目术语词典
  - 保持命名风格一致
  - 定期检查命名规范

协作最佳实践:
  - 确保4-Agent协作链完整
  - 维护文档追溯关系
  - 及时更新基线文档
  - 定期清理过时文档

质量最佳实践:
  - 使用自动化检查工具
  - 建立命名规范检查清单
  - 定期进行规范培训
  - 持续改进命名规范
```

---

**版本历史**:

- v5.0 (2025-08-04): AI 协作优化版本，简化命名规范
- v4.1 (2025-08-04): AI 友好性优化，模块化设计
- v4.0 (2025-08-01): 三层架构体系引入

**维护团队**: JeecgBoot ContextDev Team  
**文档状态**: 正式发布，当前最新版本
