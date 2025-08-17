# ContextDev 测试场景配置指南

## 📋 概述

`test_scenario_course_management.yaml` 是 ContextDev AI 编程方法论系统的标准测试场景配置文件，用于验证 7-Agent 协作链和 A2A 协议集成的完整工作流程。

## 🎯 文件作用

### 核心功能

1. **标准化测试输入**: 为 ContextDev 7-Agent 协作链提供标准化的测试数据
2. **验证 A2A 协议**: 测试 ContextDev 与 CodeGen 系统的 A2A 协议集成
3. **质量基准**: 建立代码生成质量和系统集成的验证标准
4. **回归测试**: 确保系统更新后功能的一致性和稳定性

### 业务价值

- **端到端验证**: 从需求分析到代码生成的完整流程验证
- **质量保证**: 确保生成代码符合 JeecgBoot 规范和业务要求
- **性能基准**: 建立 A2A 协议调用和代码生成的性能标准
- **异常处理**: 验证系统在各种异常情况下的处理能力

## 🔗 与 7-Agent 协作链的集成

### Agent-1 (Context 基线师)

```yaml
agent1_input:
  scenario_type: "明确式"
  system_description: "企业培训管理系统..."
  business_domain: "企业培训管理"
  technical_constraints:
    - "JeecgBoot 3.8.1+"
    - "MySQL 8.0"
    - "Vue 3.0"
```

**作用**: 为 Agent-1 提供系统基线信息，包括业务领域、技术约束和场景类型。

### Agent-2 (需求推理师)

```yaml
agent2_input:
  business_requirements: |
    培训管理系统课程信息管理模块需求：
    1. 课程基本信息管理
    2. 课程内容管理
    3. 课程发布管理
    4. 课程查询统计
```

**作用**: 为 Agent-2 提供详细的业务需求描述，用于 EARS 需求分析和 BDD 场景设计。

### Agent-3 (设计思考师)

**输入来源**: 基于 Agent-2 的需求分析结果
**验证标准**: 通过 expected_entities 验证设计的实体结构是否合理

### Agent-4 (架构推理师)

**输入来源**: 基于前序 Agent 的输出
**验证标准**: 通过 relationships 和 business_rules 验证架构设计的合理性

### Agent-5 (实施推理师)

**核心验证**: A2A 协议集成和三核心变量推理

```yaml
expected_variables:
  CourseInfo:
    MODULE_NAME: "training"
    SUBMODULE_NAME: "course"
    BUSINESS_ENTITY: "CourseInfo"
```

### Agent-6 (验证推理师)

**验证标准**: 通过 test_criteria 验证生成代码的质量和功能完整性

## 🚀 使用场景

### 场景 1: 开发阶段验证

**使用时机**: 开发新功能或修改现有功能后
**验证目标**: 确保系统功能正常，代码生成质量符合标准

```python
# 使用示例
from ContextDev.agents.a2a.agent5_controller import Agent5Controller

# 加载测试场景
with open('test_scenario_course_management.yaml', 'r', encoding='utf-8') as f:
    test_scenario = yaml.safe_load(f)

# 执行测试
controller = Agent5Controller()
result = controller.execute_test_scenario(test_scenario)
```

### 场景 2: 回归测试

**使用时机**: 系统更新、依赖升级、环境变更后
**验证目标**: 确保系统功能没有退化，性能指标符合预期

### 场景 3: 性能基准测试

**使用时机**: 性能优化前后对比
**验证目标**: 验证 A2A 协议调用时间、代码生成速度等性能指标

### 场景 4: 异常处理验证

**使用时机**: 验证系统的健壮性和错误恢复能力
**验证目标**: 确保异常情况下的严格异常处理机制正确工作

## 🔧 调用方式

### 方式 1: 直接 Python 调用

```python
import yaml
from ContextDev.agents.a2a_client import A2AProtocolClient
from ContextDev.agents.data_mapper import ContextDevCodeGenMapper

# 加载测试场景
with open('ContextDev/test_scenario_course_management.yaml', 'r', encoding='utf-8') as f:
    scenario = yaml.safe_load(f)

# 提取实体信息
entities = scenario['expected_entities']
system_context = {
    'system_name': scenario['test_scenario']['name'],
    'module_name': 'training',
    'business_domain': scenario['test_scenario']['business_domain']
}

# 构建架构信息
architecture_info = {
    'entities': entities,
    'system_context': system_context
}

# 执行A2A协议测试
client = A2AProtocolClient()
applicable, manual = client.evaluate_codegen_applicability(architecture_info)

if applicable:
    a2a_request = client.build_a2a_request(applicable, system_context)
    response = client.invoke_codegen_agent(a2a_request)
```

### 方式 2: 命令行调用

```bash
# 通过CodeGen脚本使用测试场景
python CodeGen/Code_Gen_Guide.py --test-scenario ContextDev/test_scenario_course_management.yaml

# 验证A2A协议集成
python ContextDev/agents/a2a_client.py --test-scenario ContextDev/test_scenario_course_management.yaml
```

### 方式 3: 集成测试框架调用

```python
import unittest
from ContextDev.test_framework import ContextDevTestRunner

class TestCourseManagement(unittest.TestCase):
    def setUp(self):
        self.test_runner = ContextDevTestRunner()
        self.scenario_file = 'ContextDev/test_scenario_course_management.yaml'

    def test_full_workflow(self):
        """测试完整的7-Agent工作流程"""
        result = self.test_runner.run_scenario(self.scenario_file)
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.a2a_success_rate, 0.95)

    def test_code_generation_quality(self):
        """测试代码生成质量"""
        result = self.test_runner.validate_code_quality(self.scenario_file)
        self.assertTrue(result.meets_jeecg_standards)
```

## 📊 验证标准

### A2A 协议验证

- **成功率**: ≥95%
- **响应时间**: ≤30 秒
- **错误处理**: 严格异常处理机制正确触发

### 代码生成质量

- **规范符合性**: 符合 JeecgBoot 代码规范
- **功能完整性**: 包含完整的 CRUD 操作
- **数据库兼容**: 数据库表结构正确
- **前端可用性**: 前端页面可正常访问

### 集成测试标准

- **数据库集成**: 表结构创建成功，CRUD 操作正常
- **API 集成**: RESTful API 接口正常工作
- **前端集成**: 页面正常渲染，表单提交正常

## ⚠️ 注意事项

### 环境要求

1. **JeecgBoot 服务**: 确保 JeecgBoot 服务正常运行
2. **CodeGen A2A 服务**: 确保 CodeGen A2A 服务在 8888 端口运行
3. **数据库连接**: 确保 MySQL 数据库连接正常
4. **Python 环境**: 确保所需的 Python 依赖已安装

### 测试数据管理

1. **数据隔离**: 测试数据与生产数据隔离
2. **数据清理**: 测试完成后及时清理测试数据
3. **数据备份**: 重要测试数据进行备份

### 性能考虑

1. **并发限制**: 避免同时运行多个测试场景
2. **资源监控**: 监控系统资源使用情况
3. **超时设置**: 合理设置各阶段的超时时间

## 🔄 扩展和定制

### 创建新的测试场景

1. **复制模板**: 复制`test_scenario_course_management.yaml`作为模板
2. **修改业务信息**: 更新业务领域、需求描述、实体设计
3. **调整验证标准**: 根据具体需求调整验证标准和预期结果
4. **测试验证**: 运行新场景确保配置正确

### 自定义验证标准

```yaml
# 自定义验证标准示例
custom_test_criteria:
  performance:
    max_response_time: "20秒"
    min_success_rate: "98%"

  quality:
    code_coverage: ">= 80%"
    complexity_score: "<= 10"

  business:
    user_acceptance: "满足业务需求"
    compliance: "符合行业标准"
```

---

**文档版本**: v1.0  
**最后更新**: 2025 年 8 月 5 日  
**适用系统**: ContextDev AI 编程方法论系统  
**维护团队**: ContextDev 测试团队
