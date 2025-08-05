# ContextDev A2A 协议指南

## 📋 概述

本文档是 ContextDev 与 CodeGen 系统 A2A (Agent-to-Agent) 协议指南，包含协议规范、集成实施和使用说明。

## 🎯 协议目标

### 核心目标

- **智能协作**: 实现 ContextDev 与 CodeGen 系统的无缝集成
- **提升效率**: 基础 CRUD 功能开发时间减少 80%
- **保证质量**: 统一的代码风格和架构模式
- **风险控制**: 完善的降级策略和异常处理

### 技术指标

- **代码生成覆盖率**: 70-80%的基础功能自动生成
- **集成成功率**: A2A 协议调用成功率 ≥95%
- **响应时间**: A2A 协议调用响应时间 ≤30 秒
- **错误恢复**: 100%的 CodeGen 失败场景有降级策略

## 🔗 协议规范

### 协议信息

- **协议名称**: ContextDev-CodeGen A2A Integration Protocol
- **版本**: v1.0
- **传输协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

### 系统角色

#### ContextDev 系统

- **角色**: AI 编程方法论主导者
- **职责**: 需求分析、架构设计、任务分解、质量保证
- **核心 Agent**: agent-5 (实施推理师)

#### CodeGen 系统

- **角色**: 代码生成执行者
- **职责**: CRUD 代码自动生成、JeecgBoot API 调用
- **核心 Agent**: CodeGen-Expert

### 协议消息格式

#### A2A 请求格式

```json
{
  "a2a_protocol": {
    "version": "1.0",
    "source_agent": "code-developer",
    "target_agent": "codegen-expert",
    "message_type": "code_generation_request",
    "timestamp": "2025-08-05T15:30:00Z",
    "correlation_id": "uuid-string"
  },
  "payload": {
    "system_context": {
      "system_name": "系统名称",
      "module_name": "模块名称",
      "business_domain": "业务领域"
    },
    "generation_requirements": [
      {
        "entity_name": "实体名称",
        "table_name": "表名",
        "business_fields": [
          {
            "name": "字段名",
            "type": "字段类型",
            "required": true,
            "description": "字段描述"
          }
        ],
        "module_variables": {
          "MODULE_NAME": "模块名",
          "SUBMODULE_NAME": "子模块名",
          "BUSINESS_ENTITY": "业务实体名"
        },
        "quality_requirements": {
          "code_style": "standard",
          "test_coverage": "basic",
          "documentation": "required"
        }
      }
    ]
  }
}
```

#### A2A 响应格式

```json
{
  "a2a_protocol": {
    "version": "1.0",
    "source_agent": "codegen-expert",
    "target_agent": "code-developer",
    "message_type": "code_generation_response",
    "timestamp": "2025-08-05T15:35:00Z",
    "correlation_id": "uuid-string"
  },
  "payload": {
    "execution_status": {
      "overall_result": "Pass|Fail",
      "execution_time": "2025-08-05T15:35:00Z",
      "generated_modules": ["模块列表"]
    },
    "generation_results": [
      {
        "entity": "实体名称",
        "status": "success|failed",
        "generated_files": {
          "backend_files": ["文件列表"],
          "frontend_files": ["文件列表"],
          "database_files": ["文件列表"]
        },
        "customization_needs": ["定制需求列表"]
      }
    ],
    "post_generation_tasks": {
      "manual_customizations": ["手动定制任务"],
      "integration_tasks": ["集成任务"],
      "testing_recommendations": ["测试建议"]
    }
  }
}
```

## 🔧 技术实施

### 1. ContextDev Agent-5 增强

#### 核心组件

- **A2AProtocolClient**: A2A 协议客户端
- **ContextDevCodeGenMapper**: 数据映射器
- **StrictExceptionHandler**: 严格异常处理器

#### 关键方法

```python
class Agent5Controller:
    def evaluate_codegen_applicability(self, architecture_info):
        """评估架构组件的CodeGen适用性"""

    def invoke_codegen_via_a2a(self, applicable_components):
        """通过A2A协议调用CodeGen"""

    def handle_codegen_failure(self, error, context):
        """处理CodeGen调用失败"""
```

### 2. CodeGen 系统集成

#### A2A 服务端

- **端口**: 8888 (避免与 JeecgBoot 冲突)
- **路径**: `/codegen/a2a`
- **协议**: HTTP POST

#### 核心功能

- 接收 A2A 协议请求
- 解析生成需求
- 调用 JeecgBoot API
- 执行代码生成
- 返回标准化响应

## 🚀 使用指南

### 1. 环境准备

#### 启动 CodeGen A2A 服务

```bash
cd CodeGen
python a2a_flask_app.py
```

#### 验证服务状态

```bash
curl http://localhost:8888/health
```

### 2. 集成调用

#### Python 调用示例

```python
from ContextDev.agents.a2a_client import A2AProtocolClient
from ContextDev.agents.data_mapper import ContextDevCodeGenMapper

# 初始化客户端
client = A2AProtocolClient("http://localhost:8888/codegen/a2a")
mapper = ContextDevCodeGenMapper()

# 准备架构信息
architecture_info = {
    'entities': [
        {
            'name': 'UserInfo',
            'description': '用户信息管理',
            'fields': [
                {'name': 'userName', 'type': 'string', 'required': True},
                {'name': 'email', 'type': 'string', 'required': True}
            ]
        }
    ],
    'system_context': {
        'system_name': '用户管理系统',
        'module_name': 'user',
        'business_domain': 'user management'
    }
}

# 评估适用性
applicable, manual = client.evaluate_codegen_applicability(architecture_info)

# 构建A2A请求
if applicable:
    a2a_request = client.build_a2a_request(applicable, architecture_info['system_context'])

    # 发送请求
    response = client.invoke_codegen_agent(a2a_request)

    # 处理响应
    if response['success']:
        print("代码生成成功")
    else:
        print("代码生成失败")
```

### 3. 异常处理

#### 严格停止策略

当 A2A 协议调用失败时，系统执行严格停止策略：

1. 立即终止 6-Agent 工作流
2. 记录详细错误信息
3. 提供用户确认选项
4. 不执行自动降级

#### 用户确认选项

- **MANUAL_DEVELOPMENT**: 转为手动开发
- **RETRY_LATER**: 稍后重试
- **SKIP_CODEGEN**: 跳过代码生成

## 📊 监控和维护

### 性能监控

- A2A 协议调用成功率
- 平均响应时间
- 错误类型分布
- 代码生成质量指标

### 日志管理

- 协议调用日志
- 错误详情记录
- 性能指标统计
- 用户操作追踪

### 故障排除

1. **网络连接问题**: 检查服务状态和端口配置
2. **认证失败**: 验证 JeecgBoot 登录凭据
3. **数据格式错误**: 检查 A2A 协议消息格式
4. **代码生成失败**: 查看 CodeGen 服务日志

## 🔄 版本更新

### v1.0 (当前版本)

- 基础 A2A 协议实现
- ContextDev 与 CodeGen 集成
- 严格异常处理机制
- 跨平台兼容性支持

### 后续版本规划

- v1.1: 增强错误恢复机制
- v1.2: 支持批量代码生成
- v1.3: 集成测试自动化
- v2.0: 支持更多代码生成框架

## 📞 技术支持

如遇问题，请检查：

1. 服务状态和网络连接
2. 协议消息格式
3. 系统日志和错误信息
4. 环境配置和依赖项

---

**文档版本**: v1.0  
**最后更新**: 2025 年 8 月 5 日  
**维护团队**: ContextDev 开发团队
