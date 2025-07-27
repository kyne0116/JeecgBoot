# ContextDev 模板引用路径标准规范

> **文档版本**: v1.0.0  
> **创建日期**: 2025-07-27  
> **适用范围**: ContextDev v4.1 所有YAML模板文件  

---

## 🎯 引用路径标准化规范

### 📋 标准格式定义

#### **基本格式**
```yaml
引用格式: "../{layer}/{expert|type}/{file}.yaml#{anchor}"
```

#### **层级定义**
```yaml
layer (层级):
  - shared      # 共享基线层
  - requirements # 需求分析专家层
  - baseline    # 需求基线管理专家层
  - architecture # 系统架构专家层
  - development # 代码开发专家层
  - testing     # 质量测试专家层

expert (专家类型):
  - requirements_analyst
  - baseline_manager
  - system_architect
  - code_developer
  - quality_tester

file (文件类型):
  - input.yaml      # 输入模板
  - output.yaml     # 输出模板
  - 特殊文件名.yaml  # 如baseline_shared.yaml

anchor (锚点):
  - 使用#/跟随YAML路径
  - 示例: #/shared_baseline, #/data_types
```

### 🔧 标准引用示例

#### **引用共享基线**
```yaml
# ✅ 正确格式
baseline_reference: 
  shared_baseline: "../shared/baseline_shared.yaml#/shared_baseline"
  project_context: "../shared/project_context.yaml#/project_context"
  data_types: "../shared/data_types.yaml#/data_types"

# ❌ 错误格式
baseline_reference:
  shared_baseline: "../../shared/baseline_shared.yaml"  # 错误路径深度
  project_context: "shared/project_context.yaml"        # 缺少../
  data_types: "../shared/data_types.yaml"               # 缺少锚点
```

#### **引用专家模板**
```yaml
# ✅ 正确格式
expert_input_reference:
  requirements_input: "../requirements/input.yaml#/requirements_analyst_input"
  architecture_output: "../architecture/output.yaml#/system_architect_output"

# ❌ 错误格式
expert_input_reference:
  requirements_input: "../analyst/input.yaml"           # 错误目录名
  architecture_output: "../architecture/output.yml"    # 错误文件扩展名
```

### 📁 目录结构对应

```yaml
templates/
├── shared/                    # layer: shared
│   ├── baseline_shared.yaml   # 引用: ../shared/baseline_shared.yaml
│   ├── data_types.yaml       # 引用: ../shared/data_types.yaml
│   └── project_context.yaml  # 引用: ../shared/project_context.yaml
├── requirements/              # layer: requirements
│   ├── input.yaml            # 引用: ../requirements/input.yaml
│   └── output.yaml           # 引用: ../requirements/output.yaml
├── baseline/                  # layer: baseline
│   ├── input.yaml            # 引用: ../baseline/input.yaml
│   └── output.yaml           # 引用: ../baseline/output.yaml
├── architecture/              # layer: architecture
│   ├── input.yaml            # 引用: ../architecture/input.yaml
│   └── output.yaml           # 引用: ../architecture/output.yaml
├── development/               # layer: development
│   ├── input.yaml            # 引用: ../development/input.yaml
│   └── output.yaml           # 引用: ../development/output.yaml
└── testing/                   # layer: testing
    ├── input.yaml            # 引用: ../testing/input.yaml
    └── output.yaml           # 引用: ../testing/output.yaml
```

---

## 🔍 引用完整性检查

### 📋 检查清单

#### **格式检查**
- [ ] 所有引用使用相对路径"../"开头
- [ ] 路径深度统一为一级"../"
- [ ] 目录名称与实际目录完全匹配
- [ ] 文件名称使用".yaml"扩展名
- [ ] 锚点格式正确"#/path"

#### **有效性检查**
- [ ] 引用的文件实际存在
- [ ] 锚点指向的YAML路径有效
- [ ] 无循环引用问题
- [ ] 无死链接存在

#### **一致性检查**
- [ ] 同类引用格式统一
- [ ] 专家间引用标准一致
- [ ] 版本信息同步更新

---

## 🛠️ 自动化检查脚本

### 📜 引用路径检查脚本

```bash
#!/bin/bash
# check_template_references.sh
# 用途: 检查模板引用路径的标准性和有效性

echo "=== ContextDev 模板引用路径检查 ==="

# 1. 检查引用格式
echo "1. 检查引用格式..."
grep -r "\$ref:" templates/ --include="*.yaml" | while read line; do
  if [[ ! $line =~ \.\./[a-z_]+/[a-z_]+\.yaml#/[a-z_/]+ ]]; then
    echo "❌ 格式不符: $line"
  fi
done

# 2. 检查文件存在性
echo "2. 检查引用文件存在性..."
grep -r "\.\./.*\.yaml" templates/ --include="*.yaml" -o | sort -u | while read ref; do
  file_path="templates/${ref#../}"
  if [[ ! -f "$file_path" ]]; then
    echo "❌ 文件不存在: $ref -> $file_path"
  fi
done

# 3. 检查循环引用
echo "3. 检查循环引用..."
# TODO: 实现循环引用检测逻辑

echo "引用路径检查完成！"
```

### 🔧 引用路径修复脚本

```bash
#!/bin/bash
# fix_template_references.sh
# 用途: 自动修复不符合标准的引用路径

echo "=== ContextDev 模板引用路径修复 ==="

# 备份原文件
echo "创建备份..."
cp -r templates/ templates_backup/

# 修复常见问题
echo "修复引用路径..."

# 修复缺少../的引用
sed -i '' 's|"shared/|"../shared/|g' templates/**/*.yaml

# 修复多层../的引用
sed -i '' 's|"\.\./\.\./shared/|"../shared/|g' templates/**/*.yaml

# 修复文件扩展名
sed -i '' 's|\.yml"|.yaml"|g' templates/**/*.yaml

echo "引用路径修复完成！"
echo "备份文件位于: templates_backup/"
```

---

## 📊 合规性监控

### 🎯 合规性指标

```yaml
引用路径合规性指标:
  标准格式符合率: ≥ 100%     # 所有引用必须符合标准格式
  文件存在性: = 100%          # 所有引用文件必须存在
  锚点有效性: ≥ 95%          # 锚点指向的路径应有效
  循环引用: = 0              # 不允许循环引用
  死链接: = 0                # 不允许死链接

质量门禁:
  所有指标必须达标才能通过引用检查
  不符合标准的引用必须立即修复
  定期执行自动化检查和修复
```

### 📈 持续改进

```yaml
改进措施:
  1. 建立引用路径CI/CD检查
  2. 增加编辑器插件支持引用验证
  3. 建立引用路径可视化工具
  4. 定期进行引用路径审计

监控频率:
  实时检查: 文件保存时
  每日检查: 自动化脚本执行
  每周审计: 人工审查和优化
  版本发布: 强制性完整检查
```

---

## 🔗 相关文档

- [ContextDev 模板架构设计](README.md#三层模板架构)
- [YAML模板使用指南](templates/README.md)
- [专家协作接口标准](experts/README.md)

---

**维护责任**: ContextDev架构团队  
**更新频率**: 根据模板结构变更及时更新  
**版本控制**: 与主项目版本同步  

**使用说明**: 所有开发者在创建或修改YAML模板时，必须严格遵循本规范，确保引用路径的标准性和一致性。