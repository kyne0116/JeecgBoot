# ContextDev - JeecgBoot AI 增强开发 v4.0 (Context Engineering 专用版)

> **版本**: v4.0.0 | **更新日期**: 2025-07-25 | **架构**: Context Engineering Only

ContextDev 是 JeecgBoot 项目的 AI 增强开发环境，专注于 **Context Engineering** 基础能力和 **CodeGen 系统** 的深度集成，为企业级快速开发提供专业化的 AI 辅助工具。

## 🎯 核心能力

- **Context Engineering (8.5/10)**：基于最佳实践的 AI 编程工作流
- **CodeGen 系统 (9.0/10)**：完整的前后端代码自动生成能力
- **JeecgBoot 原生集成**：无第三方框架依赖，纯原生能力增强

## 🚀 快速开始

### **第一步：验证环境**

```bash
# 检查 Python 3.8+
python3 --version

# 检查 Git
git --version

# 检查 JeecgBoot CodeGen 系统
ls -la CodeGen/Code_Gen_Guide.py
```

### **第二步：安装 Context Engineering 环境**

```bash
# 在项目根目录执行
cd /Users/admin/Work/Github/JeecgBoot
bash ContextDev/jeecg-ai-setup.sh
```

### **第三步：验证安装**

```bash
# 验证核心配置文件
ls -la CLAUDE.md
ls -la ContextDev/templates/
ls -la PRPs/examples/jeecgboot/

python3 CodeGen/Code_Gen_Guide.py --dict
```

### **第四步：开始使用**

```bash
# 生成需求文档
/jeecg-generate-prp 电商管理系统需求

# 执行代码生成
python3 CodeGen/Code_Gen_Guide.py --help
```

## 📁 目录结构

```
ContextDev/
├── README.md                    # 本文件
├── jeecg-ai-setup.sh           # 安装脚本
├── jeecg-ai-update.sh          # 更新脚本
├── integration-status.json     # 集成状态
├── config/                     # 配置文件
│   ├── context-engineering.json
│   └── jeecg-unified.json
├── templates/                  # AI 编程模板
│   ├── CLAUDE_JEECGBOOT.md
│   ├── REQUIREMENTS_JEECGBOOT.md
│   ├── DESIGN_JEECGBOOT.md
│   ├── PLANNING_JEECGBOOT.md
│   ├── TASK_JEECGBOOT.md
│   └── TESTING_JEECGBOOT.md
├── examples/jeecgboot/         # 示例代码
│   ├── backend/                # 后端示例
│   └── frontend/               # 前端示例
├── scripts/                    # 工具脚本
│   ├── sync-upstream.sh
│   └── validate-integration.sh
└── upstream/                   # 上游项目
    └── context-engineering/    # Context Engineering 源码
```

## 🛠️ 使用指南

### Context Engineering 工作流

1. **需求分析阶段**

   - 使用 `REQUIREMENTS_JEECGBOOT.md` 模板
   - 通过 `/jeecg-generate-prp` 命令生成需求文档

2. **设计阶段**

   - 使用 `DESIGN_JEECGBOOT.md` 模板
   - 基于 JeecgBoot 架构约束进行设计

3. **实现阶段**

   - 通过 CodeGen 系统生成基础代码
   - 基于示例代码进行复杂业务逻辑开发

4. **测试阶段**
   - 使用 `TESTING_JEECGBOOT.md` 模板
   - 完整的单元测试和集成测试

### CodeGen 系统集成

```bash
# 获取数据字典
python3 CodeGen/Code_Gen_Guide.py --dict

# 执行代码生成（基于 AI Agent 需求分析）
python3 CodeGen/Code_Gen_Guide.py --module-name finance --form-config temp_config.json

# 查看生成结果
ls -la jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/
```

## 📚 模板系统

### 核心模板文件

- **CLAUDE_JEECGBOOT.md**: JeecgBoot AI 编程规范
- **REQUIREMENTS_JEECGBOOT.md**: 需求分析模板
- **DESIGN_JEECGBOOT.md**: 架构设计模板
- **PLANNING_JEECGBOOT.md**: 项目规划模板
- **TASK_JEECGBOOT.md**: 任务管理模板
- **TESTING_JEECGBOOT.md**: 测试计划模板

### 使用模板

```bash
# 复制模板到工作目录
cp ContextDev/templates/REQUIREMENTS_JEECGBOOT.md projectDocs/REQUIREMENTS_my-project.md

# 基于模板创建项目文档
# 编辑 projectDocs/REQUIREMENTS_my-project.md
```

## 🔧 配置说明

### 主配置文件

- **CLAUDE.md**: 项目级 AI 编程配置
- **jeecg-unified.json**: ContextDev 统一配置
- **context-engineering.json**: Context Engineering 配置

### 环境变量

```bash
export JEECG_AI_ENV="development"
export CODEGEN_CONFIG_PATH="CodeGen/Code_Gen_Config.json"
export CONTEXT_DEV_VERSION="4.0.0"
```

## 🚀 高级功能

### 批量代码生成

```bash
# 批量生成多个模块
for module in user role permission; do
    python3 CodeGen/Code_Gen_Guide.py --module-name system_$module --batch
done
```

### 集成验证

```bash
# 运行集成验证
bash ContextDev/scripts/validate-integration.sh

# 检查生成代码质量
bash ContextDev/scripts/check-code-quality.sh
```

## 📈 性能优化

### Context Engineering 优化

- 使用模板缓存机制
- 并行处理多个文档
- 智能增量更新

### CodeGen 系统优化

- 预编译模板文件
- 缓存数据字典信息
- 批量文件操作

## 🔍 故障排除

### 常见问题

1. **CodeGen 系统无法找到**

   ```bash
   # 确认 CodeGen 系统存在
   ls -la CodeGen/Code_Gen_Guide.py
   ```

2. **模板文件缺失**

   ```bash
   # 重新复制模板文件
   bash ContextDev/jeecg-ai-setup.sh --examples-only
   ```

3. **配置文件错误**
   ```bash
   # 重新生成配置
   bash ContextDev/jeecg-ai-setup.sh --update-claude-config
   ```

### 调试模式

```bash
# 启用调试模式
export JEECG_AI_DEBUG=true
bash ContextDev/jeecg-ai-setup.sh --verify
```

## 📝 更新日志

### v4.0.0 (2025-07-25)

- 专注于 Context Engineering 和 CodeGen 系统集成
- 简化架构，提升稳定性
- 优化安装脚本和配置文件
- 增强 JeecgBoot 开发体验

### v3.0.0 (2025-07-24)

- Context Engineering 基础能力集成
- JeecgBoot 示例代码集成
- AI 编程模板体系建立

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 📄 许可证

本项目遵循 Apache 2.0 许可证。详情请参阅 [LICENSE](../LICENSE) 文件。

## 🔗 相关链接

- [JeecgBoot 官网](http://www.jeecg.com)
- [Context Engineering](https://github.com/context-engineering/context-engineering)
- [CodeGen 系统文档](../CodeGen/README.md)
