# ContextDev 模板命名标准规范

> **版本**: v1.0.0  
> **创建日期**: 2025-07-27  
> **适用范围**: ContextDev v4.1 所有YAML模板文件  
> **标准依据**: IEEE 830, CMMI Level 3, ISO 9001  

---

## 🎯 规范目标

建立严格统一的模板命名规范，确保ContextDev系统的：
- **一致性**: 所有模板文件和字段命名遵循统一标准
- **可读性**: 清晰直观的命名方式，便于理解和维护
- **可追溯性**: 通过命名即可识别文件用途和层级关系
- **扩展性**: 支持系统扩展时的命名一致性

---

## 📁 文件命名规范

### 🔧 基本命名原则

```yaml
文件命名标准:
  格式: {purpose}[_{detail}].yaml
  字符集: 小写字母 + 下划线 (禁用中划线、空格、特殊字符)
  长度: 3-30个字符
  扩展名: 强制使用.yaml (禁用.yml)

命名要求:
  描述性: 文件名应清晰表达文件用途
  层级性: 体现模板在系统中的层级关系
  标准化: 遵循预定义的命名模式
  唯一性: 同目录下文件名不可重复
```

### 📋 目录级别命名标准

#### **第一层：共享基线层 (shared/)**
```yaml
命名规范:
  baseline_shared.yaml     # 共享基础信息基线
  project_context.yaml    # 项目上下文配置
  data_types.yaml         # 数据类型定义库
  business_rules.yaml     # 通用业务规则 (可选)
  
命名模式: {scope}_{function}.yaml
  scope: baseline/project/data/business
  function: shared/context/types/rules
```

#### **第二层：专家模板层**
```yaml
命名规范:
  input.yaml             # 专家输入模板 (固定命名)
  output.yaml            # 专家输出模板 (固定命名)
  process.yaml           # 专家处理流程 (可选)
  validation.yaml        # 输入验证规则 (可选)
  
目录命名: {expert_role}/
  requirements/          # 需求分析专家
  baseline/             # 需求基线管理专家
  architecture/         # 系统架构专家
  development/          # 代码开发专家
  testing/              # 质量测试专家
```

#### **第三层：特定功能模板**
```yaml
baseline/ 目录特殊文件:
  baseline_template.yaml    # 基线管理规范
  traceability_matrix.yaml # 需求追溯矩阵
  change_request.yaml      # 变更请求管理
  quality_checklist.yaml  # 质量检查清单
  
命名模式: {function}_{type}.yaml
  function: baseline/traceability/change/quality
  type: template/matrix/request/checklist
```

---

## 🏷️ 字段命名规范

### 📋 基本命名原则

```yaml
字段命名标准:
  格式: {scope}_{object}[_{detail}]
  字符集: 小写字母 + 下划线
  长度: 3-40个字符
  描述性: 字段名应清晰表达字段含义

命名层次:
  1级: 顶层分组 (如: project_info, requirement_input)
  2级: 对象分类 (如: project_identity, business_classification)
  3级: 具体字段 (如: project_id, created_date)
```

### 🎯 标准字段命名字典

#### **项目标识类字段**
```yaml
项目基础信息:
  project_id: ""           # 项目唯一标识 格式: JG-{业务域}-{序号}
  project_name: ""         # 项目名称
  project_code: ""         # 项目代码 (简短标识)
  system_name: ""          # 系统名称
  module_name: ""          # 模块名称
  
业务分类:
  business_domain: ""      # 业务领域枚举值
  functional_area: ""      # 功能领域
  complexity_level: ""     # 复杂度级别枚举值
```

#### **版本控制类字段**
```yaml
版本信息:
  current_version: ""      # 当前版本 (语义化版本)
  baseline_version: ""     # 基线版本
  change_version: ""       # 变更版本
  template_version: ""     # 模板版本
  
状态管理:
  status: ""              # 状态枚举值
  stage: ""               # 阶段枚举值
  priority: ""            # 优先级枚举值
  approval_status: ""     # 审批状态
```

#### **时间管理类字段**
```yaml
时间戳 (统一ISO 8601格式):
  created_date: ""         # 创建时间
  last_modified: ""        # 最后修改时间
  approved_date: ""        # 批准时间
  release_date: ""         # 发布时间
  planned_completion: ""   # 计划完成时间
  actual_completion: ""    # 实际完成时间
  
时间段:
  start_date: ""          # 开始时间
  end_date: ""            # 结束时间
  duration: ""            # 持续时间
```

#### **责任人类字段**
```yaml
人员信息:
  creator: ""             # 创建人
  owner: ""               # 负责人  
  reviewer: ""            # 审核人
  approver: ""            # 批准人
  developer: ""           # 开发人员
  tester: ""              # 测试人员
  
联系信息:
  contact_email: ""       # 联系邮箱
  contact_phone: ""       # 联系电话
  department: ""          # 部门
  team: ""                # 团队
```

#### **需求工程类字段**
```yaml
需求标识:
  requirement_id: ""       # 需求唯一标识
  requirement_name: ""     # 需求名称
  requirement_type: ""     # 需求类型
  requirement_source: ""   # 需求来源
  
需求内容:
  description: ""          # 需求描述
  acceptance_criteria: ""  # 验收标准
  business_rule: ""        # 业务规则
  constraint: ""           # 约束条件
  assumption: ""           # 假设条件
```

#### **技术架构类字段**
```yaml
架构信息:
  architecture_type: ""    # 架构类型
  technology_stack: ""     # 技术栈
  framework_version: ""    # 框架版本
  deployment_model: ""     # 部署模式
  
数据库设计:
  table_name: ""          # 表名 (遵循JeecgBoot约定)
  field_name: ""          # 字段名
  data_type: ""           # 数据类型
  constraint_rule: ""     # 约束规则
  
API设计:
  endpoint_url: ""        # 接口地址
  http_method: ""         # HTTP方法
  request_format: ""      # 请求格式
  response_format: ""     # 响应格式
```

#### **质量管理类字段**
```yaml
质量指标:
  quality_score: ""       # 质量评分
  test_coverage: ""       # 测试覆盖率
  defect_count: ""        # 缺陷数量
  performance_metric: ""  # 性能指标
  
测试信息:
  test_case_id: ""        # 测试用例标识
  test_type: ""           # 测试类型
  test_result: ""         # 测试结果
  execution_date: ""      # 执行时间
```

---

## 📊 枚举值标准

### 🎯 标准枚举值定义

#### **业务领域 (business_domain)**
```yaml
枚举值:
  - core                  # 核心系统
  - finance               # 财务管理
  - supply_chain          # 供应链管理
  - customer_relationship # 客户关系管理
  - human_resources       # 人力资源管理
  - inventory_management  # 库存管理
  - order_processing      # 订单处理
  - reporting_analytics   # 报表分析
  - workflow_management   # 工作流管理
  - integration_services  # 集成服务
```

#### **复杂度级别 (complexity_level)**
```yaml
枚举值:
  - simple               # 简单CRUD操作
  - standard            # 标准业务逻辑
  - complex             # 复杂业务流程
  - enterprise          # 企业级解决方案
```

#### **状态管理 (status)**
```yaml
通用状态:
  - draft               # 草稿
  - reviewing           # 审核中
  - approved            # 已批准
  - released            # 已发布
  - archived            # 已归档
  - rejected            # 已拒绝
  - suspended           # 已暂停

需求状态:
  - identified          # 已识别
  - analyzed            # 已分析
  - designed            # 已设计
  - implemented         # 已实现
  - tested              # 已测试
  - accepted            # 已验收
```

#### **优先级 (priority)**
```yaml
枚举值:
  - critical            # 紧急
  - high                # 高
  - medium              # 中等
  - low                 # 低
```

#### **需求类型 (requirement_type)**
```yaml
枚举值:
  - functional          # 功能性需求
  - non_functional      # 非功能性需求
  - business_rule       # 业务规则
  - constraint          # 约束条件
  - interface           # 接口需求
  - data_requirement    # 数据需求
```

---

## 🔧 模板结构标准

### 📋 标准模板结构

#### **所有模板共同结构**
```yaml
# 模板文件头部注释 (强制要求)
# 模板名称和用途说明
# ========================================================================
# 版本: v1.0.0 | 创建日期: YYYY-MM-DD
# 专家: {expert_name} (专家模板必需)
# 用途: 详细描述模板用途和使用场景
# 引用方式: 如何引用此模板 (共享模板必需)

{template_root_key}:
  # 第一级: 基线引用 (引用共享基线的模板必需)
  baseline_reference:
    shared_baseline: "../shared/baseline_shared.yaml#/shared_baseline"
    project_context: "../shared/project_context.yaml#/project_context"
    data_types: "../shared/data_types.yaml#/data_types"
  
  # 第二级: 核心内容区域
  {main_content_section}:
    # 具体字段定义
    
  # 第三级: 元数据区域
  metadata:
    template_version: "1.0.0"
    last_updated: ""
    maintained_by: ""
```

#### **专家输入模板结构 (input.yaml)**
```yaml
{expert_name}_input:
  baseline_reference: {}      # 基线引用
  project_info: {}           # 项目基础信息
  {specific_input_section}: {}  # 专家特定输入区域
  validation_rules: {}       # 输入验证规则
  metadata: {}               # 模板元数据
```

#### **专家输出模板结构 (output.yaml)**
```yaml
{expert_name}_output:
  baseline_reference: {}      # 基线引用
  input_summary: {}          # 输入信息摘要
  {specific_output_section}: {} # 专家特定输出区域
  quality_metrics: {}        # 质量指标
  next_stage_input: {}       # 下游专家输入
  metadata: {}               # 模板元数据
```

---

## 🔍 引用标准规范

### 📋 模板引用命名

#### **引用路径标准**
```yaml
引用格式: "../{layer}/{file}.yaml#/{anchor}"

层级定义:
  shared/                # 共享基线层
  requirements/          # 需求分析专家层
  baseline/             # 需求基线管理专家层
  architecture/         # 系统架构专家层
  development/          # 代码开发专家层
  testing/              # 质量测试专家层

锚点命名:
  #{root_key}            # 根级锚点
  #{root_key}/{sub_key}  # 子级锚点
```

#### **内部引用标准**
```yaml
内部引用格式: "$ref:{source}.{path}"

示例:
  "$ref:shared_baseline.project_identity.project_id"
  "$ref:project_context.jeecgboot_constraints.framework_version"
  "$ref:data_types.common_fields.timestamp_format"
```

---

## ✅ 验证检查清单

### 📋 文件命名检查

```yaml
文件命名验证:
  - [ ] 文件名使用小写字母和下划线
  - [ ] 扩展名使用.yaml而非.yml
  - [ ] 文件名长度在3-30字符之间
  - [ ] 文件名具有描述性和唯一性
  - [ ] 遵循{purpose}[_{detail}].yaml格式

目录结构验证:
  - [ ] 专家目录命名符合标准
  - [ ] 共享基线文件命名正确
  - [ ] 特殊功能模板命名规范
```

### 📋 字段命名检查

```yaml
字段命名验证:
  - [ ] 字段名使用小写字母和下划线
  - [ ] 字段名长度在3-40字符之间
  - [ ] 字段名具有描述性
  - [ ] 遵循{scope}_{object}[_{detail}]格式
  - [ ] 使用标准枚举值

结构完整性验证:
  - [ ] 包含必需的头部注释
  - [ ] 基线引用格式正确
  - [ ] 模板结构符合标准
  - [ ] 元数据信息完整
```

### 📋 引用规范检查

```yaml
引用格式验证:
  - [ ] 外部引用路径格式正确
  - [ ] 锚点命名符合标准
  - [ ] 内部引用语法正确
  - [ ] 引用目标文件存在
  - [ ] 锚点路径有效
```

---

## 🛠️ 自动化检查工具

### 📜 命名规范检查脚本

```bash
#!/bin/bash
# validate_naming_standards.sh
# 用途: 自动检查模板命名规范符合性

echo "=== ContextDev 模板命名规范检查 ==="

# 1. 检查文件命名规范
echo "1. 检查文件命名规范..."
find templates/ -name "*.yml" | while read file; do
    echo "❌ 错误扩展名: $file (应使用.yaml)"
done

find templates/ -name "*-*" | while read file; do
    echo "❌ 包含中划线: $file (应使用下划线)"
done

# 2. 检查字段命名规范
echo "2. 检查字段命名规范..."
grep -r "[A-Z]" templates/ --include="*.yaml" | while read line; do
    echo "⚠️  可能包含大写字母: $line"
done

# 3. 检查枚举值使用
echo "3. 检查枚举值标准..."
# 实现具体的枚举值检查逻辑

echo "命名规范检查完成！"
```

### 🐍 Python版本验证工具

```python
#!/usr/bin/env python3
"""
模板命名规范验证工具
用途: 全面验证模板文件和字段命名的规范性
"""

import re
import yaml
from pathlib import Path

class NamingStandardsValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_file_naming(self, file_path):
        """验证文件命名规范"""
        filename = file_path.name
        
        # 检查扩展名
        if not filename.endswith('.yaml'):
            self.errors.append(f"文件扩展名错误: {file_path}")
            
        # 检查命名格式
        if not re.match(r'^[a-z][a-z0-9_]*\.yaml$', filename):
            self.errors.append(f"文件命名格式错误: {file_path}")
            
    def validate_field_naming(self, yaml_content, file_path):
        """验证字段命名规范"""
        def check_keys(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 检查字段命名格式
                    if not re.match(r'^[a-z][a-z0-9_]*$', key):
                        self.errors.append(f"字段命名错误: {current_path} in {file_path}")
                    
                    check_keys(value, current_path)
                    
        check_keys(yaml_content)
        
    def run_validation(self):
        """运行完整验证"""
        template_files = Path("templates").rglob("*.yaml")
        
        for file_path in template_files:
            self.validate_file_naming(file_path)
            
            try:
                with open(file_path, 'r') as f:
                    content = yaml.safe_load(f)
                    self.validate_field_naming(content, file_path)
            except Exception as e:
                self.errors.append(f"文件读取错误: {file_path} - {e}")
                
        return len(self.errors) == 0

if __name__ == "__main__":
    validator = NamingStandardsValidator()
    success = validator.run_validation()
    
    if success:
        print("✅ 所有命名规范检查通过！")
    else:
        print("❌ 发现命名规范问题:")
        for error in validator.errors:
            print(f"  {error}")
```

---

## 📚 实施指导

### 🎯 实施步骤

```yaml
第一阶段 - 规范制定 (已完成):
  1. 制定文件命名标准
  2. 制定字段命名标准
  3. 定义枚举值规范
  4. 建立模板结构标准

第二阶段 - 现有模板整改:
  1. 审查现有模板文件命名
  2. 检查字段命名合规性
  3. 统一枚举值使用
  4. 完善模板结构

第三阶段 - 工具集成:
  1. 集成自动化检查脚本
  2. 建立CI/CD验证流程
  3. 设置开发工具插件
  4. 建立持续监控机制

第四阶段 - 团队培训:
  1. 团队规范培训
  2. 最佳实践分享
  3. 常见问题解答
  4. 定期规范审查
```

### 💡 最佳实践建议

```yaml
开发实践:
  1. 新建模板前先查阅命名规范
  2. 使用自动化工具验证命名
  3. 定期运行规范检查脚本
  4. 在代码审查中检查命名规范

维护实践:
  1. 定期更新标准枚举值
  2. 根据实际使用优化规范
  3. 建立命名规范变更流程
  4. 保持文档同步更新

质量保证:
  1. 设置命名规范检查门禁
  2. 建立规范违规告警机制
  3. 跟踪规范符合度指标
  4. 持续改进命名标准
```

---

## 📈 监控指标

### 🎯 规范符合度指标

```yaml
文件命名符合率:
  目标: ≥ 100%
  计算: 符合规范的文件数 / 总文件数
  
字段命名符合率:
  目标: ≥ 95%
  计算: 符合规范的字段数 / 总字段数
  
枚举值标准化率:
  目标: ≥ 90%
  计算: 使用标准枚举值的字段数 / 枚举字段总数
  
模板结构完整率:
  目标: ≥ 100%
  计算: 结构完整的模板数 / 总模板数
```

---

## 🔗 相关文档

- [ContextDev 系统架构文档](README.md)
- [模板引用路径标准](TEMPLATE_REFERENCE_STANDARD.md)
- [AIGC错误恢复系统指南](aigc/AIGC_ERROR_RECOVERY_GUIDE.md)
- [系统评估报告](EVALUATION_REPORT.md)

---

**维护责任**: ContextDev架构团队  
**更新频率**: 根据系统发展需要及时更新  
**版本控制**: 与主项目版本同步  

**重要提醒**: 本规范是ContextDev系统质量保证的重要组成部分，所有开发者在创建或修改模板时必须严格遵循，确保系统的一致性和可维护性。