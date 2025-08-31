# ContextDev AI 编程方法论系统使用指南

## 📋 概述

ContextDev 是基于 Context Engineering 和 Chain of Thought 推理理论的 AI 原生开发方法论系统，通过 7-Agent 协作链实现从需求分析到代码生成的完整开发闭环。

## 🔄 7-Agent 协作链使用方法

### Agent-1: Context 基线师

**功能**: 建立系统基线和模块基线，为整个协作链提供稳固基础

**输入格式**:

```yaml
user_input:
  scenario_type: "探索式" | "明确式"
  system_description: "系统描述（可以是简短的需求）"
  business_domain: "业务领域"
  technical_constraints: ["技术约束列表"]
```

**调用方式**:

```python
# 探索式场景（需求不明确）
agent1_input = {
    "scenario_type": "探索式",
    "system_description": "需要一个培训管理系统",
    "business_domain": "企业培训",
    "technical_constraints": ["JeecgBoot 3.8.2+", "Vue 3.0"]
}

# 明确式场景（需求明确）
agent1_input = {
    "scenario_type": "明确式",
    "system_description": "培训管理系统，包含课程管理、学员管理、培训计划等功能模块",
    "business_domain": "企业培训管理",
    "technical_constraints": ["JeecgBoot 3.8.2+", "MySQL 8.0", "Vue 3.0"]
}
```

**输出结果**:

```yaml
system_base_info:
  document_info:
    id: "SYS-20250805-001"
    title: "培训管理系统基线"
    version: "1.0"
  system_context:
    system_name: "培训管理系统"
    business_domain: "企业培训管理"
    technical_stack: ["JeecgBoot", "Vue", "MySQL"]
  baseline_requirements:
    functional_scope: ["课程管理", "学员管理", "培训计划"]
    quality_attributes: ["可扩展性", "易用性", "安全性"]
```

### Agent-2: 需求推理师

**功能**: 基于 EARS 方法和 BDD 场景进行深度需求分析

**输入格式**:

```yaml
input:
  system_base_info: # 来自agent-1的输出
  business_requirements: "详细业务需求描述"
```

**调用方式**:

```python
agent2_input = {
    "system_base_info": agent1_output,
    "business_requirements": """
    培训管理系统需要支持：
    1. 课程信息管理：创建、编辑、删除课程
    2. 学员管理：学员注册、信息维护、学习记录
    3. 培训计划：制定培训计划、安排课程、跟踪进度
    4. 考试评估：在线考试、成绩管理、证书颁发
    """
}
```

**输出结果**:

```yaml
requirements_document:
  document_info:
    id: "REQ-20250805-001"
    title: "培训管理系统需求分析"
  ears_requirements:
    ubiquitous: ["系统应支持多用户并发访问"]
    event_driven: ["当学员完成课程时，系统应自动更新学习进度"]
    unwanted_behaviors: ["系统不应允许未授权用户访问敏感信息"]
    state_driven: ["在学员登录状态下，系统应显示个人学习仪表板"]
    optional: ["系统可以支持移动端访问"]
  bdd_scenarios:
    - scenario: "学员注册课程"
      given: "学员已登录系统"
      when: "学员选择课程并点击注册"
      then: "系统应确认注册并发送通知邮件"
```

### Agent-3: 设计思考师

**功能**: 用户体验设计和界面原型设计

**输入格式**:

```yaml
input:
  requirements_document: # 来自agent-2的输出
  design_preferences: "设计偏好和约束"
```

**调用方式**:

```python
agent3_input = {
    "requirements_document": agent2_output,
    "design_preferences": {
        "ui_style": "现代简洁",
        "color_scheme": "蓝色主题",
        "responsive": True,
        "accessibility": "WCAG 2.1 AA"
    }
}
```

**输出结果**:

```yaml
prototype_document:
  document_info:
    id: "PROTO-20250805-001"
    title: "培训管理系统原型设计"
  user_interface:
    pages:
      - name: "课程列表页"
        components: ["搜索框", "课程卡片", "分页器"]
        interactions: ["搜索", "筛选", "排序"]
      - name: "课程详情页"
        components: ["课程信息", "章节列表", "注册按钮"]
        interactions: ["查看详情", "注册课程", "收藏"]
  wireframes:
    - page: "课程列表页"
      layout: "网格布局"
      components_layout: { ... }
```

### Agent-4: 架构推理师

**功能**: 系统架构设计和技术决策

**输入格式**:

```yaml
input:
  requirements_document: # 来自agent-2的输出
  prototype_document: # 来自agent-3的输出
  architecture_constraints: "架构约束"
```

**调用方式**:

```python
agent4_input = {
    "requirements_document": agent2_output,
    "prototype_document": agent3_output,
    "architecture_constraints": {
        "framework": "JeecgBoot 3.8.2+",
        "database": "MySQL 8.0",
        "deployment": "Docker容器化",
        "scalability": "支持1000并发用户"
    }
}
```

**输出结果**:

```yaml
architecture_document:
  document_info:
    id: "ARCH-20250805-001"
    title: "培训管理系统架构设计"
  system_architecture:
    layers:
      - name: "表现层"
        components: ["Vue前端", "移动端H5"]
      - name: "业务层"
        components: ["课程服务", "学员服务", "培训计划服务"]
      - name: "数据层"
        components: ["MySQL数据库", "Redis缓存"]
  data_model:
    entities:
      - name: "CourseInfo"
        fields:
          - { name: "courseName", type: "string", required: true }
          - { name: "courseDescription", type: "text", required: false }
          - { name: "duration", type: "integer", required: true }
        relationships:
          - { target: "TrainingPlan", type: "one_to_many" }
```

### Agent-5: 实施推理师 (含 Subagent 集成)

**功能**: 开发任务分解和 @codegen-expert subagent 代码生成

**输入格式**:

```yaml
input:
  architecture_document: # 来自agent-4的输出
  implementation_preferences: "实施偏好"
```

**调用方式**:

```python
agent5_input = {
    "architecture_document": agent4_output,
    "implementation_preferences": {
        "development_approach": "敏捷开发",
        "code_generation": "优先使用@codegen-expert subagent",
        "testing_strategy": "TDD测试驱动开发"
    }
}
```

**Subagent 集成执行流程**:

```python
# 1. 评估CodeGen适用性
applicable_components, manual_components = agent5.evaluate_codegen_applicability(architecture_info)

# 2. 构建Subagent调用请求
subagent_request = agent5.build_subagent_request(applicable_components, system_context)

# 3. 调用@codegen-expert Subagent
try:
    codegen_response = agent5.invoke_codegen_subagent(subagent_request)
    # 处理成功响应
except Exception as e:
    # 智能异常处理：提供多种解决方案
    solution_options = agent5.handle_intelligent_failure(e, context)
    # 提供用户指导
```

**输出结果**:

```yaml
development_document:
  document_info:
    id: "DEV-20250805-001"
    title: "培训管理系统开发计划"
  subagent_codegen_execution:
    status: "SUCCESS" | "RETRY_AVAILABLE"
    applicable_components:
      - entity: "CourseInfo"
        confidence: 0.9
        generation_type: "crud"
    codegen_response:
      successful:
        - entity: "CourseInfo"
          status: "success"
          generated_files:
            backend_files: ["CourseController.java", "CourseService.java"]
            frontend_files: ["CourseList.vue", "CourseForm.vue"]
  manual_development_tasks:
    - component: "复杂业务逻辑"
      reason: "超出CodeGen能力范围"
      estimated_effort: "3天"
```

### Agent-6: 验证推理师

**功能**: 测试策略设计和质量保证

**输入格式**:

```yaml
input:
  development_document: # 来自agent-5的输出
  quality_requirements: "质量要求"
```

**调用方式**:

```python
agent6_input = {
    "development_document": agent5_output,
    "quality_requirements": {
        "code_coverage": "≥80%",
        "performance": "响应时间<2秒",
        "security": "OWASP Top 10合规"
    }
}
```

**输出结果**:

```yaml
testing_document:
  document_info:
    id: "TEST-20250805-001"
    title: "培训管理系统测试计划"
  test_strategy:
    unit_tests:
      - component: "CourseService"
        test_cases: ["创建课程", "查询课程", "更新课程"]
    integration_tests:
      - scenario: "课程注册流程"
        test_steps: ["登录", "选择课程", "确认注册", "验证结果"]
  quality_gates:
    - metric: "代码覆盖率"
      threshold: "≥80%"
      status: "PASS"
```

## 🔗 Subagent 集成使用方法

### 1. 使用 @codegen-expert Subagent

```bash
# 在 Claude Code 中直接调用
@codegen-expert 请根据以下架构信息生成代码：
- 系统模块：finance
- 功能模块：invoice
- 业务实体：InvoiceInfo
```

### 2. 完整 Subagent 集成使用流程

```python
# 1. 在 Agent-5 中集成 Subagent 调用
# 通过自然语言与 @codegen-expert 交互
subagent_request = f"""
@codegen-expert 请生成以下模块的代码：
系统：{system_name}
模块：{module_name}
实体：{entity_name}
"""

# 2. 处理 Subagent 响应
# @codegen-expert 会返回生成的代码和配置
# 然后继续后续的开发流程
```

### 3. 智能异常处理机制

**触发条件**:

- Subagent 调用失败
- CodeGen 配置错误
- 代码生成不完整
- 业务逻辑复杂度超出范围

**处理流程**:

```python
# 异常处理示例
try:
    codegen_response = invoke_codegen_subagent(subagent_request)
except Exception as e:
    # 1. 提供多种解决方案
    solution_options = {
        'status': 'RETRY_AVAILABLE',
        'error_type': 'SUBAGENT_CALL_FAILURE',
        'available_solutions': [
            'ADJUST_CONFIGURATION',  # 调整配置重试
            'MANUAL_DEVELOPMENT',    # 手动开发
            'SIMPLIFY_REQUIREMENTS', # 简化需求
            'HYBRID_APPROACH'        # 混合开发
        ],
        'recommendation': '建议先调整配置重试，如仍失败则采用混合开发方式'
    }

    # 2. 继续工作流程
    return {
        'workflow_status': 'CONTINUE_WITH_OPTIONS',
        'solution_options': solution_options
    }
```

## 📝 最佳实践

### 1. 输入准备最佳实践

- **明确需求**: 提供详细的业务需求描述
- **技术约束**: 明确技术栈和性能要求
- **质量标准**: 定义代码质量和测试覆盖率要求

### 2. 协作链使用最佳实践

- **顺序执行**: 严格按照 agent-1 到 agent-6 的顺序执行
- **输出验证**: 每个 Agent 的输出都应该验证格式和完整性
- **异常处理**: 及时处理 Subagent 调用异常

### 3. Subagent 集成最佳实践

- **清晰表达**: 使用清晰的自然语言与 @codegen-expert 交互
- **错误处理**: 准备 Subagent 调用失败的多种解决方案
- **灵活调整**: 根据生成结果灵活调整开发策略

通过以上详细的使用方法说明，用户可以完整地使用 ContextDev AI 编程方法论系统，实现从需求分析到代码生成的完整开发闭环。
