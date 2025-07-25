# ContextDev 目录结构说明

## 集成层架构 (v3.0)

```
ContextDev/
├── upstream/                    # 上游项目管理
│   ├── context-engineering/     # Context Engineering 源码
│   └── superclaude/            # SuperClaude 源码
├── integration/                # 集成配置层
│   ├── commands/               # 统一命令映射
│   ├── personas/               # JeecgBoot专用Persona
│   ├── mcp-servers/           # MCP服务器配置
│   └── workflows/             # 工作流集成
├── config/                     # 分层配置管理
│   ├── context-engineering.json
│   ├── superclaude.json
│   └── jeecg-unified.json     # 统一配置
├── scripts/                    # 集成脚本
│   ├── sync-upstream.sh        # 上游同步
│   ├── install-superclaude.sh  # SuperClaude安装
│   └── validate-integration.sh # 集成验证
├── examples/                   # JeecgBoot示例代码 (现有)
│   └── jeecgboot/             # 完整示例代码
└── templates/                  # 6个核心模板 (现有)
    ├── CLAUDE_JEECGBOOT.md
    ├── REQUIREMENTS_JEECGBOOT.md
    └── ...
```

## 设计原则

- **隔离集成**: 两个上游项目完全独立
- **统一接口**: ContextDev 作为集成层
- **保持兼容**: 现有功能 100% 兼容
- **渐进增强**: 分阶段功能集成
