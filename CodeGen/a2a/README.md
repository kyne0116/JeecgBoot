# CodeGen Expert A2A Service

基于虚拟环境的 Python 服务，运行在端口 8888，完全支持 A2A 中台的服务发现和注册机制。

## 🚀 快速启动

```bash
# 进入目录
cd d:\02_Dev\Workspace\GitHub\JeecgBoot\CodeGen\a2a\

# 启动服务（推荐使用 uv）
uv run main.py

# 或使用 Python 直接启动
python main.py

# 指定端口
python main.py --port 8889

# 启用调试模式
python main.py --debug
```

### 🌟 增强的启动日志

服务启动时会显示完整的端点信息：

```
======================================================================
🚀 CodeGen Expert A2A Service 启动中...
======================================================================
📡 监听地址: http://127.0.0.1:8888

🔍 核心端点:
   📋 Agent Card (服务发现): http://127.0.0.1:8888/.well-known/agent.json
   💚 健康检查: http://127.0.0.1:8888/health
   📊 服务状态: http://127.0.0.1:8888/codegen/status
   🤖 A2A 协议: http://127.0.0.1:8888/codegen/a2a

🧪 测试端点:
   🔧 变量提取: http://127.0.0.1:8888/codegen/variables/extract
   ⚙️  配置生成: http://127.0.0.1:8888/codegen/config/generate

💡 快速验证:
   curl http://127.0.0.1:8888/.well-known/agent.json
======================================================================
🔍 验证路由注册...
✅ AgentCard 路由已注册
🌟 服务启动成功，等待请求...
```

## 🔍 服务发现与验证

### 📋 AgentCard - 主要服务发现端点

**AgentCard** 是符合 A2A 协议规范的核心服务发现端点，提供完整的服务元数据：

```bash
# 获取完整的 Agent 服务信息
curl http://localhost:8888/.well-known/agent.json

# 使用 PowerShell 格式化输出
Invoke-RestMethod -Uri "http://localhost:8888/.well-known/agent.json" | ConvertTo-Json -Depth 5
```

### 🧪 其他验证端点

```bash
# 健康检查
curl http://localhost:8888/health

# 详细服务状态
curl http://localhost:8888/codegen/status

# A2A 协议端点（代码生成请求）
curl -X POST http://localhost:8888/codegen/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "a2a_protocol": {
      "version": "1.0",
      "source_agent": "test-client",
      "target_agent": "codegen-expert",
      "message_type": "code_generation_request",
      "correlation_id": "test-001"
    },
    "payload": {
      "system_context": {
        "business_domain": "测试系统"
      },
      "generation_requirements": [
        {
          "entity_name": "TestEntity",
          "business_fields": [
            {"name": "name", "type": "string", "description": "名称", "required": true}
          ]
        }
      ]
    }
  }'

# 变量提取测试
curl -X POST http://localhost:8888/codegen/variables/extract \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": {
      "entity_name": "Product"
    },
    "system_context": {
      "business_domain": "电商系统"
    }
  }'
```

## 文件结构

```
CodeGen/a2a/
├── main.py              # 主启动文件
├── a2a_server.py        # A2A协议服务器
├── a2a_flask_app.py     # Flask应用
├── pyproject.toml       # uv包管理配置
├── __init__.py          # Python包标识
└── README.md            # 说明文档
```

## 依赖

- flask>=2.0.0
- flask-cors>=4.0.0
- requests>=2.25.0
- mysql-connector-python>=8.0.0

## API 端点

### 🔍 核心端点

| 端点                      | 方法 | 描述                   | 用途                             |
| ------------------------- | ---- | ---------------------- | -------------------------------- |
| `/.well-known/agent.json` | GET  | **AgentCard 服务发现** | A2A 协议核心，提供完整服务元数据 |
| `/health`                 | GET  | 健康检查               | 基础服务状态验证                 |
| `/codegen/status`         | GET  | 详细服务状态           | 组件状态和能力信息               |
| `/codegen/a2a`            | POST | A2A 协议主端点         | 代码生成请求处理                 |

### 🧪 测试端点

| 端点                         | 方法 | 描述         | 用途               |
| ---------------------------- | ---- | ------------ | ------------------ |
| `/codegen/variables/extract` | POST | 变量提取测试 | 测试三核心变量推理 |
| `/codegen/config/generate`   | POST | 配置生成测试 | 测试 JSON 配置生成 |

## 📋 AgentCard 详细规范

### A2A 协议合规性

AgentCard 端点 (`/.well-known/agent.json`) 完全符合 A2A 协议规范，提供：

- **服务发现**: 自动发现和注册机制
- **能力声明**: 完整的服务能力描述
- **协议协商**: A2A 协议版本和消息类型支持
- **端点映射**: 所有可用 API 端点的完整列表

### 响应结构 (A2A 完整技术规范)

```json
{
  "name": "CodeGen Expert",
  "description": "JeecgBoot 代码生成专家 Agent，支持完整的 CRUD 代码生成工作流",
  "url": "http://127.0.0.1:8888",
  "version": "1.0.0",
  "provider": {
    "name": "JeecgBoot Team",
    "url": "https://github.com/jeecgboot/jeecg-boot"
  },
  "capabilities": [
    {
      "name": "code_generation",
      "description": "支持Java、Vue、SQL代码生成，包含CRUD、树形、一对多等多种类型",
      "input_types": ["text/plain", "application/json"],
      "output_types": ["application/java", "application/vue", "application/sql"]
    },
    {
      "name": "jeecgboot_integration",
      "description": "JeecgBoot框架集成功能，包含在线表单创建、数据库同步、模块管理等",
      "input_types": ["application/json"],
      "output_types": ["text/plain", "application/json"]
    },
    {
      "name": "variable_extraction",
      "description": "智能变量提取和推理，支持模块名、子模块名、业务实体映射",
      "input_types": ["text/plain"],
      "output_types": ["application/json"]
    },
    {
      "name": "a2a_protocol",
      "description": "A2A协议通信支持，处理Agent间消息传递和代码生成请求",
      "input_types": ["application/json"],
      "output_types": ["application/json"]
    }
  ],
  "authentication": {
    "schemes": ["Bearer", "Basic"],
    "credentials": "支持Bearer Token和Basic认证"
  },
  "default_input_modes": ["text/plain", "application/json"],
  "default_output_modes": ["application/json", "text/plain"],
  "metadata": {
    "categories": ["development-tools", "code-generation", "enterprise"],
    "tags": ["codegen", "jeecgboot", "a2a", "expert", "crud"],
    "documentation": "https://github.com/jeecgboot/jeecg-boot/tree/master/CodeGen",
    "support": "https://github.com/jeecgboot/jeecg-boot/issues",
    "license": "Apache-2.0",
    "code_generation": {
      "output_formats": ["java", "vue", "sql"],
      "supported_databases": ["mysql", "postgresql", "oracle"],
      "supported_frameworks": ["jeecgboot", "spring-boot"],
      "supported_types": ["crud", "tree", "one_to_many"]
    },
    "jeecgboot_integration": {
      "online_form_creation": true,
      "database_synchronization": true,
      "code_generation": true,
      "module_management": true,
      "permission_authorization": true
    },
    "variable_extraction": {
      "module_name_inference": true,
      "submodule_name_inference": true,
      "business_entity_mapping": true,
      "naming_convention_validation": true
    }
  },
  "endpoints": {
    "a2a_protocol": "http://127.0.0.1:8888/codegen/a2a",
    "health": "http://127.0.0.1:8888/health",
    "status": "http://127.0.0.1:8888/codegen/status",
    "variable_extraction": "http://127.0.0.1:8888/codegen/variables/extract",
    "config_generation": "http://127.0.0.1:8888/codegen/config/generate",
    "agent_card": "http://127.0.0.1:8888/.well-known/agent.json"
  },
  "protocols": {
    "a2a": {
      "endpoint": "http://127.0.0.1:8888/codegen/a2a",
      "version": "1.0",
      "supported_message_types": [
        "task_request",
        "task_response",
        "health_check",
        "code_generation_request",
        "code_generation_response",
        "capability_inquiry"
      ]
    }
  },
  "configuration": {
    "max_concurrent_requests": 10,
    "request_timeout_seconds": 300,
    "supported_languages": ["zh-CN", "en-US"],
    "rate_limiting": {
      "enabled": false,
      "requests_per_minute": 60
    }
  },
  "status": {
    "state": "active",
    "health": "healthy",
    "uptime_seconds": 60030.094949,
    "last_updated": "2025-08-07T16:40:30.094949"
  }
}
```

### 关键字段说明 (A2A 完整技术规范)

| 字段                   | 描述                    | 用途                   |
| ---------------------- | ----------------------- | ---------------------- |
| `name`                 | Agent 名称 (根级别)     | A2A 中台服务识别       |
| `url`                  | 服务基础 URL (根级别)   | A2A 中台服务注册       |
| `version`              | 版本号 (根级别)         | A2A 中台版本管理       |
| `provider`             | **提供商信息**          | 服务提供商标识         |
| `capabilities`         | **Capability 对象数组** | A2A 规范的能力声明     |
| `authentication`       | **认证配置**            | 支持的认证方案         |
| `default_input_modes`  | **默认输入模式**        | 默认接受的输入类型     |
| `default_output_modes` | **默认输出模式**        | 默认返回的输出类型     |
| `metadata`             | 详细元数据              | 分类、标签、文档等信息 |
| `endpoints`            | API 端点映射            | 自动客户端配置         |
| `protocols.a2a`        | A2A 协议支持            | 协议版本协商           |
| `configuration`        | 服务配置信息            | 性能和限制参数         |
| `status`               | 实时状态信息            | 健康监控和负载均衡     |

### 🌐 CORS 配置 (A2A 中台访问支持)

为了支持 A2A 中台访问，Agent 已配置了符合技术规范的 CORS 设置：

```python
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:9000",    # A2A中台地址
            "http://127.0.0.1:9000",   # A2A中台地址
            "http://localhost:8080",    # JeecgBoot后端
            "http://127.0.0.1:8080",   # JeecgBoot后端
            "http://localhost:3000",    # 前端开发服务器
            "http://127.0.0.1:3000",   # 前端开发服务器
        ],
        "supports_credentials": True,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})
```

**CORS 配置说明**:

- ✅ **A2A 中台访问**: 允许来自 `localhost:9000` 和 `127.0.0.1:9000` 的请求
- ✅ **凭据支持**: `supports_credentials: True` 支持认证信息传递
- ✅ **完整方法支持**: 支持所有 RESTful HTTP 方法
- ✅ **标准头部**: 支持 A2A 协议要求的所有头部字段

### 📋 Capability 对象结构

每个 Capability 对象包含以下字段：

| 字段           | 描述           | 示例                                    |
| -------------- | -------------- | --------------------------------------- |
| `name`         | 能力名称       | "code_generation"                       |
| `description`  | 能力描述       | "支持 Java、Vue、SQL 代码生成"          |
| `input_types`  | 支持的输入类型 | ["text/plain", "application/json"]      |
| `output_types` | 支持的输出类型 | ["application/java", "application/vue"] |

### 🔄 结构变更说明

**变更原因**: 为了符合 A2A 规范，将 Agent 基本信息提升到根级别，并将 capabilities 调整为 Capability 对象数组。

**第一次变更 (扁平化结构)**:

- ✅ `name` 字段提升到根级别 (原 `agent.name`)
- ✅ `url` 字段提升到根级别 (新增，指向服务基础 URL)
- ✅ `version` 字段提升到根级别 (原 `agent.version`)
- ✅ `id` 字段提升到根级别 (原 `agent.id`)

**第二次变更 (Capability 对象数组)**:

- ✅ `capabilities` 从嵌套对象改为 **Capability 对象数组**
- ✅ 每个 Capability 包含 `name`, `description`, `input_types`, `output_types`
- ✅ 原有详细配置信息移至 `metadata` 字段保持向后兼容
- ✅ 符合 A2A 规范的标准 Capability 模型定义

**兼容性保证**:

- ✅ 所有原有信息通过 `metadata` 字段保留
- ✅ 新格式完全符合 A2A 中台期望
- ✅ 支持渐进式迁移和向后兼容

## 🔗 A2A 协议集成

### 服务发现工作流

1. **自动发现**: 客户端访问 `/.well-known/agent.json` 获取服务信息
2. **能力匹配**: 根据 `capabilities` 字段确定服务是否满足需求
3. **协议协商**: 检查 `protocols.a2a.version` 确保兼容性
4. **端点配置**: 使用 `endpoints` 字段自动配置客户端
5. **状态监控**: 定期检查 `status` 字段进行健康监控

### 与 ContextDev 系统集成

```bash
# ContextDev 系统发现 CodeGen Expert 服务
curl http://codegen-expert-service/.well-known/agent.json

# 基于 AgentCard 信息自动配置 A2A 客户端
# 然后发送代码生成请求到 A2A 端点
curl -X POST http://codegen-expert-service/codegen/a2a \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 最佳实践

- **优先使用 AgentCard**: 始终从 `/.well-known/agent.json` 开始服务发现
- **缓存服务信息**: AgentCard 信息可以缓存，但应定期刷新状态
- **错误处理**: 实现优雅的降级机制，当 AgentCard 不可用时使用备用发现方法
- **版本兼容**: 检查 A2A 协议版本确保兼容性
- **负载均衡**: 使用 `status` 信息进行智能负载分配

## 🛠️ 开发和调试

### 本地开发

```bash
# 开发模式启动（带详细日志）
python main.py --debug

# 指定不同端口避免冲突
python main.py --port 8889

# 验证 AgentCard 端点
curl http://localhost:8888/.well-known/agent.json | python -m json.tool
```

### 故障排除

1. **AgentCard 返回 404**:

   - 检查服务是否正确启动
   - 确认路由注册（启动日志会显示验证结果）
   - 清理旧的 Python 进程：`taskkill /f /im python.exe`

2. **端口冲突**:

   - 使用 `netstat -ano | findstr :8888` 检查端口占用
   - 指定其他端口：`python main.py --port 8889`

3. **模块导入错误**:
   - 确保在正确目录运行：`CodeGen/a2a/`
   - 检查依赖安装：`pip install flask flask-cors requests mysql-connector-python`
