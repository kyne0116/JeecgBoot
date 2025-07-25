# ContextDev 目录结构说明

## Context Engineering 专用架构 (v4.0)

```
ContextDev/
├── upstream/                    # 上游项目管理
│   └── context-engineering/     # Context Engineering 源码
├── config/                      # 配置管理
│   ├── context-engineering.json # Context Engineering 配置
│   └── jeecg-unified.json      # 统一配置
├── scripts/                     # 集成脚本
│   ├── sync-upstream.sh         # 上游同步
│   └── validate-integration.sh  # 集成验证
├── examples/                    # JeecgBoot示例代码
│   └── jeecgboot/              # 完整示例代码
│       ├── backend/            # 后端示例代码
│       │   ├── entity/         # 实体类示例
│       │   ├── controller/     # 控制器示例
│       │   ├── service/        # 服务层示例
│       │   └── mapper/         # 数据访问层示例
│       └── frontend/           # 前端示例代码
│           ├── views/          # 页面组件示例
│           ├── api/            # API服务示例
│           └── store/          # 状态管理示例
├── templates/                   # AI 编程模板
│   ├── CLAUDE_JEECGBOOT.md     # AI 编程规范
│   ├── REQUIREMENTS_JEECGBOOT.md # 需求分析模板
│   ├── DESIGN_JEECGBOOT.md     # 架构设计模板
│   ├── PLANNING_JEECGBOOT.md   # 项目规划模板
│   ├── TASK_JEECGBOOT.md       # 任务管理模板
│   └── TESTING_JEECGBOOT.md    # 测试计划模板
├── integration-status.json     # 集成状态
├── jeecg-ai-setup.sh           # 安装脚本
├── jeecg-ai-update.sh          # 更新脚本
├── jeecg-ai-config.json        # AI 配置
└── README.md                   # 使用文档
```

## 设计原则

- **专注集成**: Context Engineering + CodeGen 系统深度集成
- **简化架构**: 移除第三方框架依赖，专注核心能力
- **保持兼容**: 现有 CodeGen 功能 100% 兼容
- **原生增强**: 基于 JeecgBoot 原生能力进行 AI 增强

## 核心组件

### Context Engineering
- **模板系统**: 完整的 AI 编程模板集合
- **示例代码**: JeecgBoot 标准示例代码
- **工作流程**: 需求分析 → 设计 → 实现 → 测试

### CodeGen 系统
- **AI 代理**: Code_Gen_Agent.md 智能需求分析
- **代码生成**: Code_Gen_Guide.py 完整代码生成
- **配置管理**: Code_Gen_Config.json 系统配置

### 集成层
- **统一配置**: jeecg-unified.json 整合配置
- **状态管理**: integration-status.json 跟踪集成状态
- **脚本工具**: 安装、更新、验证脚本

## 文件说明

### 配置文件
- `jeecg-unified.json`: ContextDev 统一配置
- `context-engineering.json`: Context Engineering 专用配置
- `jeecg-ai-config.json`: AI 增强开发配置

### 脚本文件
- `jeecg-ai-setup.sh`: 一键安装 Context Engineering 环境
- `jeecg-ai-update.sh`: 更新维护脚本
- `sync-upstream.sh`: 同步上游 Context Engineering 项目
- `validate-integration.sh`: 验证集成状态

### 模板文件
- `CLAUDE_JEECGBOOT.md`: JeecgBoot AI 编程核心规范
- `REQUIREMENTS_JEECGBOOT.md`: 需求分析和规格说明模板
- `DESIGN_JEECGBOOT.md`: 系统设计和技术方案模板
- `PLANNING_JEECGBOOT.md`: 项目规划和架构设计模板
- `TASK_JEECGBOOT.md`: 任务管理和进度跟踪模板
- `TESTING_JEECGBOOT.md`: 测试计划和用例管理模板

### 示例代码
- `examples/jeecgboot/backend/`: 完整的后端示例代码
- `examples/jeecgboot/frontend/`: 完整的前端示例代码

## 使用流程

1. **环境初始化**: 运行 `jeecg-ai-setup.sh` 安装环境
2. **需求分析**: 使用模板创建需求文档
3. **代码生成**: 通过 CodeGen 系统生成基础代码
4. **业务开发**: 基于示例代码开发复杂业务逻辑
5. **测试验证**: 使用测试模板进行质量保证