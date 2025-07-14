# JeecgBoot 表单代码生成工具 - 使用指南

## 🚀 快速开始

### 一条命令完成全流程
```bash
# 基础用法：指定业务系统和配置文件
python Code_Gen_Guide.py --module-name finance --form-config your_table.json

# 系统自动完成：模块检查/创建 → 表单生成 → 数据库同步 → 代码生成
```

### 使用流程
1. **准备配置文件**：基于 `Code_Gen_Guide.json` 模板创建业务表单配置
2. **执行脚本**：传入模块名和配置文件路径
3. **获得代码**：完整的CRUD代码自动生成到指定模块

## 📁 文件说明

| 文件 | 用途 | 说明 |
|------|------|------|
| `Code_Gen_Guide.py` | 主执行脚本 | 完整自动化工作流 |
| `Code_Gen_Agent.md` | AI助手提示词 | 智能需求分析和执行 |
| `Code_Gen_Config.json` | 配置文件 | 服务器、路径等配置 |
| `Code_Gen_Guide.json` | 基础模板 | 7个系统字段模板(勿改) |

## 🔧 核心变量机制

脚本通过四个核心变量完成代码生成：

| 变量 | 生成规则 | 示例 |
|------|----------|------|
| **PROJECT_PATH_PREFIX** | 从配置文件读取 | `/Users/admin/Work/Github/JeecgBoot` |
| **PROJECT_PATH** | `{前缀}/jeecg-boot/jeecg-module-{模块名}` | `.../jeecg-module-finance` |
| **ENTITY_NAME** | 业务功能英文单词 | `invoice`(发票) |
| **PACKAGE_NAME** | `org.jeecg.modules.{模块名}.{实体名}` | `org.jeecg.modules.finance.invoice` |

### 业务系统类型
- **hrms**: 人力资源 (employee, training, performance)
- **crm**: 客户管理 (customer, opportunity, contract)  
- **scm**: 供应链 (supplier, procurement, inventory)
- **oa**: 办公自动化 (approval, meeting, document)
- **finance**: 财务管理 (invoice, budget, asset)

### 字段模板类型

**基础字段**:
- `text_field`: 文本输入框
- `number_field`: 数字输入框
- `decimal_field`: 小数输入框  
- `date_field`: 日期选择器
- `datetime_field`: 日期时间选择器
- `textarea_field`: 多行文本框

**数据字典字段**:
- `dict_select_field`: 下拉选择 (关联数据字典)
- `dict_radio_field`: 单选按钮 (关联数据字典)  
- `dict_checkbox_field`: 多选框 (关联数据字典)

**高级字段类型** (新增):
- `file_upload_field`: 文件上传组件
- `image_upload_field`: 图片上传组件
- `rich_text_field`: 富文本编辑器
- `phone_field`: 手机号输入框 (带验证)
- `email_field`: 邮箱输入框 (带验证)

**模板变量**:
- `{{DICT_CODE}}`: 数据字典编码 (如: sex, status, type)
- `{{FIELD_NAME}}`: 字段名称
- `{{FIELD_DESCRIPTION}}`: 字段描述
- `{{ORDER_NUM}}`: 字段排序号
- `{{NULLABLE}}`: 是否可空 (0/1)
- `{{REQUIRED}}`: 是否必填 (0/1)

## ⚙️ 配置文件

### Code_Gen_Config.json - 主配置
```json
{
  "project": {
    "path_prefix": "/Users/admin/Work/Github/JeecgBoot"
  },
  "server": {
    "base_url": "http://localhost:8080/jeecg-boot",
    "username": "admin", 
    "password": "123456"
  },
  "codegen": {
    "vue_style": "vue3",
    "code_types": "controller,service,dao,mapper,entity,vue"
  }
}
```

### 业务表单配置文件
基于 `Code_Gen_Guide.json` 模板创建，包含：
- **表头信息**: 表名(us_前缀)、表描述
- **系统字段**: 7个固定字段(不可修改)
- **业务字段**: orderNum从7开始，使用字段模板
- **数据字典字段**: 支持从Code_Gen_DICT.json自动关联

## 📋 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--module-name, -m` | 业务模块名 | `finance`, `hrms` |
| `--form-config, -f` | 表单配置文件 | `invoice_config.json` |
| `--test` | 运行系统诊断 | 检查环境和配置 |
| `--validate` | 验证配置 | 不执行工作流 |
| `--skip-module-management` | 跳过模块管理 | 使用现有模块 |
| `--try-run` | 试运行模式 | 显示操作不执行 |
| `--dict` | 获取数据字典 | 保存到Code_Gen_DICT.json |

## 🚀 使用示例

### 示例1: 创建财务发票表
```bash
# 1. 基于模板创建配置文件 invoice_config.json
# 2. 执行生成
python Code_Gen_Guide.py --module-name finance --form-config invoice_config.json

# 脚本自动执行：
# ✓ 检查jeecg-module-finance模块
# ✓ 如不存在，创建Maven模块  
# ✓ 更新pom.xml配置
# ✓ 生成CRUD代码到finance模块
```

### 示例2: 系统诊断
```bash
python Code_Gen_Guide.py --test
# 检查：Maven环境、服务连接、配置有效性
```

### 示例3: 获取数据字典
```bash
python Code_Gen_Guide.py --dict
# 获取系统所有数据字典并保存到Code_Gen_DICT.json
```

## 🔧 高级功能

### 智能模块管理
- **自动检查**: `jeecg-module-{模块名}` 是否存在
- **自动创建**: Maven archetype创建新模块(非交互)
- **自动配置**: 更新主项目和启动项目pom.xml

### 配置文件处理
- **变量替换**: 代码生成时临时替换jeecg_config.properties变量
- **自动还原**: 生成完成后恢复模板状态

### 智能数据字典集成 (增强版)
- **自动检查**: 24小时过期检测机制，自动判断是否需要更新
- **智能匹配**: 增强算法支持精确匹配、模糊匹配、相似度计算
- **多级匹配**: 
  - 精确匹配(10分): 语义词完全对应
  - 部分匹配(8分): 包含关系匹配  
  - 模糊匹配(3-5分): 相似度算法匹配
- **自动应用**: ≥8分自动配置，5-7分显示建议
- **扩展语义**: 支持部门、职位、用户等更多业务词汇

### 错误处理
- **完整验证**: 配置、网络、数据结构验证
- **超时控制**: Maven命令5分钟超时保护
- **异常恢复**: 自动清理临时文件

## ⚠️ 重要规则

1. **表名规范**: 必须使用`us_`前缀
2. **模板保护**: `Code_Gen_Guide.json`永远保持模板状态
3. **字段顺序**: 系统字段0-6，业务字段从7开始
4. **环境要求**: Maven已安装，JeecgBoot服务运行中

## 🤖 AI助手模式

配合 `Code_Gen_Agent.md` 使用AI助手：
1. 描述业务需求："创建员工培训记录表"
2. AI自动识别系统类型(hrms)
3. 生成配置文件并执行脚本
4. 完成完整代码生成流程

---

**📚 详细技术文档**: 查看源码注释  
**🆘 问题反馈**: 检查诊断输出或提Issue