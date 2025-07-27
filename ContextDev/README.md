# ContextDev v4.1 - JeecgBoot智能开发系统

> **需求工程驱动的5专家AI开发链路** • **扁平化模板架构** • **AIGC错误恢复系统**  
> **版本**: v4.1.0 | **技术标准**: IEEE 830 + CMMI Level 3 + JeecgBoot深度集成

---

## 🚀 核心能力

**5专家协作链路**: `需求分析` → `基线管理` → `架构设计` → `代码开发` → `质量测试`

- **开发效率**: 传统人工 → AI专家处理 (2-5倍提升)
- **质量标准**: IEEE 830 + CMMI Level 3工业级质量管理
- **框架集成**: JeecgBoot深度集成，最大化CodeGen系统利用
- **智能恢复**: 8种错误类型自动识别恢复，目标成功率≥80%

---

## 👥 5专家技术链路

| 专家 | 核心能力 | 典型场景 |
|------|----------|----------|
| `@requirements_analyst` | 业务需求分析、EARS语法规格化 | 需求挖掘、利益相关方分析 |
| `@baseline_manager` | 需求基线管理、变更控制 | 基线建立、追溯管理 |
| `@system_architect` | 系统架构设计、4+1视图 | 架构设计、数据库设计 |
| `@code_developer` | 全栈代码实现、CodeGen应用 | 功能开发、技术集成 |
| `@quality_tester` | 全面质量测试、验收评估 | 功能测试、性能验证 |

**工作流程**: 业务需求 → 需求分析 → 基线管理 → 架构设计 → 代码开发 → 质量测试 → 交付物

---

## 📁 项目结构

```
ContextDev/
├── README.md                    # 本文档
├── CLAUDE.md                    # 系统配置规范
├── experts/                     # 5专家定义文件
├── templates/                   # 扁平化模板架构
│   ├── shared/config.yaml      # 统一配置 (简化引用关系)
│   ├── requirements/           # 需求分析模板
│   ├── baseline/               # 基线管理模板  
│   ├── architecture/           # 系统架构模板
│   ├── development/            # 代码开发模板
│   └── testing/                # 质量测试模板
├── aigc/                       # AIGC错误恢复系统
│   ├── error_recovery_system.py
│   ├── test_error_recovery.py
│   └── AIGC_ERROR_RECOVERY_GUIDE.md
└── scripts/                    # 验证工具
    ├── check_template_references.sh
    └── validate_references.py
```

**架构优势**: 统一配置`config.yaml`，简化引用为`config_reference: "../shared/config.yaml"`

---

## 🎯 快速开始

### 环境要求
```yaml
JeecgBoot: 3.8.1+ | JDK: 17 | Maven: 3.9+ | MySQL: 8.0+ | Redis: 7.x
技术栈: Spring Boot 3.x + Vue 3 + TypeScript + 单体分层架构
```

### 3步使用流程

**Step 1**: 选择专家
```bash
@requirements_analyst  # 需求分析
@system_architect     # 架构设计  
@code_developer       # 代码开发
```

**Step 2**: 查看模板格式
```bash
cat templates/{expert}/input.yaml   # 输入模板
cat templates/shared/config.yaml    # 共享配置
```

**Step 3**: 专家处理
调用`@专家名称`进行任务处理，自动基于模板进行标准化输入输出。

---

## 🔧 核心功能

### AIGC错误恢复系统
- **8种错误类型**: 占位符、类型转换、格式验证、缺失字段等自动识别
- **恢复策略**: 针对性自动恢复 + 指数退避重试机制
- **测试套件**: `python3 aigc/test_error_recovery.py`

### 模板验证工具
```bash
bash scripts/check_template_references.sh    # 检查引用路径
python3 scripts/validate_references.py      # 验证引用有效性
```

---

## 📋 文件管理

### Git文件分类

**✅ 提交源文件** (框架核心19个文件)
```
README.md, CLAUDE.md, experts/*.md, templates/, aigc/, scripts/
```

**❌ 不提交生成文件**
```
stage_*_*.yaml, business_requirement.md, src/, database/, *.tmp, *.log
```

**推荐.gitignore**:
```gitignore
stage_*_*.yaml
business_requirement.md  
src/
database/
target/
node_modules/
dist/
*.tmp
*.log
```

---

## 💡 适用场景

### ✅ 完美适配
- 企业内部管理系统
- 标准业务流程系统
- 基于JeecgBoot的项目
- Spring Boot 3.x + Vue 3技术栈

### ❌ 不适用场景
- 微服务架构项目
- 非JeecgBoot技术栈
- 纯前端或移动端项目

---

## 🎉 立即开始

```bash
# 验证系统完整性
python3 scripts/validate_references.py

# 查看系统配置
cat CLAUDE.md

# 选择专家开始工作
@requirements_analyst  # 从需求分析开始
```

---

**专注需求工程，用AI专家能力驱动高质量交付！**

*版本: v4.1.0 | 更新: 2025-07-27 | 维护: ContextDev架构团队*