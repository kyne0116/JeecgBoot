# JeecgBoot JSON 配置文件标准规范

> **文档定位**: 临时 JSON 配置文件的技术标准和约束规范  
> **适用对象**: AIGC 系统、开发人员、配置文件生成器  
> **核心目标**: 确保生成的 JSON 配置文件 100%兼容 JeecgBoot 官方 API

---

## 🚨 **核心警示 - AIGC 必读**

### ⚠️ **系统字段 orderNum 连续性 - 致命约束**

**JeecgBoot API 强制要求**：系统字段的 orderNum 必须从 0 开始**严格连续递增**，任何断裂都会导致 API 调用失败！

```json
❌ 错误配置 - 会导致API失败：
"orderNum": 990  // 第1个系统字段
"orderNum": 991  // 第2个系统字段
"orderNum": 995  // 第4个系统字段 - 跳过了992,993,994

✅ 正确配置 - API调用成功：
"orderNum": 0    // 第1个系统字段
"orderNum": 1    // 第2个系统字段
"orderNum": 2    // 第3个系统字段
"orderNum": 3    // 第4个系统字段
```

**AIGC 常见错误**：

- ❌ 使用 990+高位数值试图确保系统字段排在后面
- ❌ 认为数值大小比连续性更重要
- ✅ 正确认知：JeecgBoot 要求连续性，不是数值大小

---

## 📋 **JSON 配置文件结构标准**

### 1. **head 部分 - 表头配置**

```json
{
  "head": {
    "tableName": "us_[module]_[submodule]_[entity]", // 必须4段式
    "tableTxt": "业务描述", // 中文描述
    "business_entity": "BusinessEntity", // PascalCase格式
    "tableType": 1, // 固定值
    "formCategory": "temp", // 临时表单
    "idType": "UUID", // 主键类型
    "isCheckbox": "Y", // 复选框支持
    "themeTemplate": "normal", // 主题模板
    "formTemplate": "1", // 表单模板
    "scroll": 1, // 滚动支持
    "isPage": "Y", // 分页支持
    "isTree": "N", // 非树形结构
    "extConfigJson": "{...}", // 扩展配置JSON字符串
    "isDesForm": "N", // 非设计表单
    "desFormCode": "" // 设计表单代码
  }
}
```

### 2. **metadata 部分 - 生成信息配置（必需）**

**🚨 强制要求**: metadata 节点是前端代码迁移的关键依赖，必须完整包含以下两个子节点：

```json
{
  "metadata": {
    "generation_info": {
      "module_name": "模块名称", // 必需：一级业务模块
      "submodule_name": "子模块名称", // 必需：二级业务模块
      "business_entity": "BusinessEntity", // 必需：业务实体名（PascalCase）
      "inference_strategy": "推理策略说明", // 推荐：AI推理方法
      "semantic_analysis": "语义分析结果" // 推荐：业务语义描述
    },
    "derived_formats": {
      "table_suffix": "lowercase_entity", // 必需：表名后缀
      "url_path": "kebab-case-entity", // 必需：URL路径格式
      "frontend_path": "module/submodule" // 必需：前端路径格式
    }
  }
}
```

**metadata 节点的作用**：

- **前端代码迁移**：Code_Gen_Guide.py 依赖此信息确定前端文件迁移路径
- **调试追踪**：记录代码生成的推理过程和参数
- **一致性验证**：确保生成的代码与原始需求保持一致

### 3. **fields 部分 - 字段配置**

#### **系统字段配置 (前 7 个字段) - 强制标准**

**⚠️ 关键警告**: 系统字段配置必须严格按照`Code_Gen_Example.json`标准，**不允许任何变更**！

```json
{
  "fields": [
    // 系统字段1: id (orderNum: 0)
    {
      "dbFieldName": "id",
      "dbFieldTxt": "主键",
      "fieldMustInput": "0", // 系统字段特征
      "isReadOnly": "1", // 系统字段特征
      "dbIsNull": "0", // 系统字段特征
      "orderNum": 0 // 必须从0开始
    },
    // 系统字段2: create_by (orderNum: 1)
    {
      "dbFieldName": "create_by",
      "dbFieldTxt": "创建人",
      "fieldMustInput": "1", // 系统字段特征
      "isReadOnly": "0", // 系统字段特征
      "dbIsNull": "0", // 系统字段特征
      "orderNum": 1 // 严格连续
    },
    // 系统字段3: create_time (orderNum: 2)
    {
      "dbFieldName": "create_time",
      "dbFieldTxt": "创建日期",
      "fieldMustInput": "1", // 系统字段特征
      "isReadOnly": "0", // 系统字段特征
      "dbIsNull": "0", // 系统字段特征
      "orderNum": 2 // 严格连续
    },
    // 系统字段4: update_by (orderNum: 3)
    {
      "dbFieldName": "update_by",
      "dbFieldTxt": "更新人",
      "fieldMustInput": "0", // 系统字段特征
      "isReadOnly": "0", // 系统字段特征
      "dbIsNull": "1", // 系统字段特征
      "orderNum": 3 // 严格连续
    },
    // 系统字段5: update_time (orderNum: 4)
    {
      "dbFieldName": "update_time",
      "dbFieldTxt": "更新日期",
      "fieldMustInput": "0", // 系统字段特征
      "isReadOnly": "0", // 系统字段特征
      "dbIsNull": "1", // 系统字段特征
      "orderNum": 4 // 严格连续
    },
    // 系统字段6: sys_org_code (orderNum: 5)
    {
      "dbFieldName": "sys_org_code",
      "dbFieldTxt": "所属部门",
      "fieldMustInput": "1", // 系统字段特征
      "isReadOnly": "0", // 系统字段特征
      "dbIsNull": "0", // 系统字段特征
      "orderNum": 5 // 严格连续
    },
    // 系统字段7: del_flag (orderNum: 6)
    {
      "dbFieldName": "del_flag",
      "dbFieldTxt": "删除标志",
      "fieldMustInput": "1", // 系统字段特征
      "isReadOnly": "0", // 系统字段特征
      "dbIsNull": "0", // 系统字段特征
      "orderNum": 6 // 严格连续
    },
    // 业务字段从 orderNum: 7 开始
    {
      "dbFieldName": "business_field_1",
      "dbFieldTxt": "业务字段1",
      "orderNum": 7 // 接续系统字段
    }
  ]
}
```

#### **业务字段配置 (第 8 个字段开始)**

业务字段的 orderNum 从 7 开始继续递增，保持整体连续性。

---

## 🔍 **验证清单 - AIGC 自检机制**

### **生成前检查清单**

```markdown
## 🔍 AIGC 生成前自检清单

### ✅ 表名规范检查

- [ ] 表名符合`us_[module]_[submodule]_[entity]`4 段式格式
- [ ] 所有部分都是小写英文，无下划线连接
- [ ] entity 部分是业务实体的全小写连续格式

### ✅ 系统字段强制检查

- [ ] 前 7 个字段必须是标准系统字段
- [ ] 系统字段 orderNum 必须是 0,1,2,3,4,5,6 连续递增
- [ ] 系统字段配置与 Code_Gen_Example.json 完全一致
- [ ] 系统字段的 fieldMustInput, isReadOnly, dbIsNull 配置正确

### ✅ 业务字段规范检查

- [ ] 业务字段 orderNum 从 7 开始递增
- [ ] 所有字段 orderNum 保持严格连续性
- [ ] 没有跳号或重复的 orderNum

### ✅ 整体配置检查

- [ ] JSON 格式正确，无语法错误
- [ ] 必需字段完整，无缺失
- [ ] 🚨 **metadata 部分必须完整包含**：generation_info 和 derived_formats 两个子节点
```

### **生成后验证机制**

```python
# 自动验证脚本示例
def validate_order_num_continuity(fields):
    """验证orderNum连续性"""
    order_nums = [field['orderNum'] for field in fields]
    order_nums.sort()

    for i, num in enumerate(order_nums):
        if num != i:
            raise ValueError(f"orderNum不连续: 期望{i}, 实际{num}")

    return True

def validate_system_fields(fields):
    """验证系统字段配置"""
    system_fields = ['id', 'create_by', 'create_time', 'update_by',
                    'update_time', 'sys_org_code', 'del_flag']

    for i, expected_field in enumerate(system_fields):
        if fields[i]['dbFieldName'] != expected_field:
            raise ValueError(f"系统字段{i}错误: 期望{expected_field}")
        if fields[i]['orderNum'] != i:
            raise ValueError(f"系统字段{expected_field}的orderNum错误")

    return True
```

---

## 📚 **AIGC 专用指导规则**

### **🚫 AIGC 严禁行为**

1. **禁止修改系统字段配置**

   - 不得更改系统字段的任何属性值
   - 不得调整系统字段的 orderNum 顺序
   - 不得删除或新增系统字段

2. **禁止使用非连续 orderNum**

   - 不得使用 990+等高位数值
   - 不得跳过任何数字
   - 不得使用负数或浮点数

3. **禁止偏离标准模板**
   - 系统字段必须与 Code_Gen_Example.json 完全一致
   - 不得进行任何"优化"或"改进"

### **✅ AIGC 推荐行为**

1. **严格模板遵循**

   - 直接复制 Code_Gen_Example.json 的系统字段配置
   - 仅修改业务字段部分
   - 保持整体结构不变

2. **连续性保证**

   - 确保 orderNum 从 0 开始严格递增
   - 业务字段从 7 开始继续递增
   - 定期验证连续性

3. **自动验证**
   - 生成后立即进行自检
   - 使用验证脚本确认配置正确性
   - 出现问题立即修正

---

## 🔧 **故障排除指南**

### **常见错误及解决方案**

| 错误类型     | 错误现象         | 根本原因          | 解决方案                                   |
| ------------ | ---------------- | ----------------- | ------------------------------------------ |
| API 调用失败 | 表单创建返回错误 | orderNum 不连续   | 重新生成，确保连续性                       |
| 系统字段错误 | 数据库同步失败   | 系统字段配置错误  | 对比标准模板，完全复制                     |
| 表名格式错误 | 表名验证失败     | 表名不符合 4 段式 | 按 us_module_submodule_entity 格式重新生成 |

### **调试流程**

1. **JSON 格式验证** → 使用 JSON Schema 验证
2. **系统字段检查** → 对比 Code_Gen_Example.json
3. **orderNum 连续性** → 使用验证脚本检查
4. **API 兼容性测试** → 调用 JeecgBoot API 验证

---

## ✅ **AIGC 5 步快速检查流程**

### **生成前必须执行的检查步骤**

**第一步：基础结构检查**

- [ ] JSON 格式正确，无语法错误
- [ ] 包含 head 和 fields 两个主要部分
- [ ] head 部分包含所有必需字段
- [ ] fields 数组至少包含 8 个字段(7 个系统字段+1 个业务字段)

**第二步：表名规范检查**

- [ ] 表名符合 us*[module]*[submodule]\_[entity] 4 段式格式
- [ ] 所有部分都是小写英文字母
- [ ] 无下划线连接符(除了 4 段分隔符)
- [ ] entity 部分是 business_entity 的全小写连续格式

**第三步：系统字段强制检查**

- [ ] 前 7 个字段必须是标准系统字段：id, create_by, create_time, update_by, update_time, sys_org_code, del_flag
- [ ] 系统字段 orderNum 必须是：0,1,2,3,4,5,6
- [ ] 系统字段配置与 Code_Gen_Example.json 完全一致
- [ ] 未修改任何系统字段的属性值

**第四步：orderNum 连续性检查**

- [ ] 所有字段的 orderNum 从 0 开始连续递增
- [ ] 无跳号：不能是 0,1,2,3,4,5,6,990,991
- [ ] 无重复：不能有相同的 orderNum 值
- [ ] 无负数：所有 orderNum 都是非负整数

**第五步：业务字段规范检查**

- [ ] 业务字段 orderNum 从 7 开始递增
- [ ] 业务字段配置合理(数据类型、长度等)
- [ ] 字段名称符合数据库命名规范
- [ ] 包含必要的显示和查询配置

### **AIGC 生成标准流程**

**步骤 1：复制系统字段**

```json
// 直接从Code_Gen_Example.json复制前7个系统字段
// 不做任何修改，保持orderNum为0,1,2,3,4,5,6
{
  "fields": [
    // 系统字段1-7: 完全复制，不修改
    {
      "dbFieldName": "id",
      "orderNum": 0
      // ... 其他属性完全一致
    }
    // ... 复制完整的7个系统字段
  ]
}
```

**步骤 2：添加业务字段**

```json
// 业务字段从orderNum: 7开始
{
  "dbFieldName": "business_field_1",
  "orderNum": 7
  // ... 业务字段配置
}
```

**步骤 3：立即自检**

```python
# 生成后立即执行验证
def aigc_self_check(config):
    # 检查orderNum连续性
    order_nums = [field['orderNum'] for field in config['fields']]
    for i, num in enumerate(sorted(order_nums)):
        if num != i:
            raise Error(f"orderNum不连续: 期望{i}, 实际{num}")

    # 检查系统字段
    system_fields = ['id', 'create_by', 'create_time', 'update_by',
                    'update_time', 'sys_org_code', 'del_flag']
    for i, expected in enumerate(system_fields):
        if config['fields'][i]['dbFieldName'] != expected:
            raise Error(f"系统字段{i}错误")
```

### **快速验证命令**

```bash
# 使用标准验证器检查格式和连续性
python3 Code_Gen_Validator.py temp_config.json

# JSON Schema验证
jsonschema -i temp_config.json Code_Gen_Schema.json
```

### **🎯 AIGC 核心要点（必记）**

1. **📋 复制模板**：系统字段配置完全复制 Code_Gen_Example.json
2. **🔢 连续递增**：orderNum 从 0 开始严格连续，不能跳号
3. **🔍 立即验证**：生成后立即使用验证工具检查

**遵循这 3 点，确保 JSON 配置 100%兼容 JeecgBoot API！**

---

## 📖 **参考资料**

- **标准模板**: `Code_Gen_Example.json` - 权威配置参考
- **验证工具**: `Code_Gen_Validator.py` - 自动验证脚本
- **Schema 定义**: `Code_Gen_Schema.json` - JSON 结构约束
- **变量规范**: `Code_Gen_Variables.md` - 三核心变量定义

---

**版本**: 1.0  
**创建日期**: 2025-07-28  
**适用版本**: JeecgBoot 3.8.1+  
**维护状态**: 持续更新
