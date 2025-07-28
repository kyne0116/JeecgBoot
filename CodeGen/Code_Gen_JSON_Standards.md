# JeecgBoot JSON配置文件标准规范

> **文档定位**: 临时JSON配置文件的技术标准和约束规范  
> **适用对象**: AIGC系统、开发人员、配置文件生成器  
> **核心目标**: 确保生成的JSON配置文件100%兼容JeecgBoot官方API

---

## 🚨 **核心警示 - AIGC必读**

### ⚠️ **系统字段orderNum连续性 - 致命约束**

**JeecgBoot API强制要求**：系统字段的orderNum必须从0开始**严格连续递增**，任何断裂都会导致API调用失败！

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

**AIGC常见错误**：
- ❌ 使用990+高位数值试图确保系统字段排在后面
- ❌ 认为数值大小比连续性更重要
- ✅ 正确认知：JeecgBoot要求连续性，不是数值大小

---

## 📋 **JSON配置文件结构标准**

### 1. **head部分 - 表头配置**

```json
{
  "head": {
    "tableName": "us_[module]_[submodule]_[entity]",  // 必须4段式
    "tableTxt": "业务描述",                            // 中文描述
    "business_entity": "BusinessEntity",             // PascalCase格式
    "tableType": 1,                                  // 固定值
    "formCategory": "temp",                          // 临时表单
    "idType": "UUID",                               // 主键类型
    "isCheckbox": "Y",                              // 复选框支持
    "themeTemplate": "normal",                      // 主题模板
    "formTemplate": "1",                            // 表单模板
    "scroll": 1,                                    // 滚动支持
    "isPage": "Y",                                  // 分页支持
    "isTree": "N",                                  // 非树形结构
    "extConfigJson": "{...}",                       // 扩展配置JSON字符串
    "isDesForm": "N",                               // 非设计表单
    "desFormCode": ""                               // 设计表单代码
  }
}
```

### 2. **fields部分 - 字段配置**

#### **系统字段配置 (前7个字段) - 强制标准**

**⚠️ 关键警告**: 系统字段配置必须严格按照`Code_Gen_Example.json`标准，**不允许任何变更**！

```json
{
  "fields": [
    // 系统字段1: id (orderNum: 0)
    {
      "dbFieldName": "id",
      "dbFieldTxt": "主键",
      "fieldMustInput": "0",        // 系统字段特征
      "isReadOnly": "1",           // 系统字段特征
      "dbIsNull": "0",             // 系统字段特征
      "orderNum": 0                // 必须从0开始
    },
    // 系统字段2: create_by (orderNum: 1)
    {
      "dbFieldName": "create_by",
      "dbFieldTxt": "创建人",
      "fieldMustInput": "1",        // 系统字段特征
      "isReadOnly": "0",           // 系统字段特征
      "dbIsNull": "0",             // 系统字段特征
      "orderNum": 1                // 严格连续
    },
    // 系统字段3: create_time (orderNum: 2)
    {
      "dbFieldName": "create_time",
      "dbFieldTxt": "创建日期",
      "fieldMustInput": "1",        // 系统字段特征
      "isReadOnly": "0",           // 系统字段特征  
      "dbIsNull": "0",             // 系统字段特征
      "orderNum": 2                // 严格连续
    },
    // 系统字段4: update_by (orderNum: 3)
    {
      "dbFieldName": "update_by",
      "dbFieldTxt": "更新人",
      "fieldMustInput": "0",        // 系统字段特征
      "isReadOnly": "0",           // 系统字段特征
      "dbIsNull": "1",             // 系统字段特征
      "orderNum": 3                // 严格连续
    },
    // 系统字段5: update_time (orderNum: 4)
    {
      "dbFieldName": "update_time",
      "dbFieldTxt": "更新日期",
      "fieldMustInput": "0",        // 系统字段特征
      "isReadOnly": "0",           // 系统字段特征
      "dbIsNull": "1",             // 系统字段特征
      "orderNum": 4                // 严格连续
    },
    // 系统字段6: sys_org_code (orderNum: 5)
    {
      "dbFieldName": "sys_org_code",
      "dbFieldTxt": "所属部门",
      "fieldMustInput": "1",        // 系统字段特征
      "isReadOnly": "0",           // 系统字段特征
      "dbIsNull": "0",             // 系统字段特征
      "orderNum": 5                // 严格连续
    },
    // 系统字段7: del_flag (orderNum: 6)
    {
      "dbFieldName": "del_flag",
      "dbFieldTxt": "删除标志",
      "fieldMustInput": "1",        // 系统字段特征
      "isReadOnly": "0",           // 系统字段特征
      "dbIsNull": "0",             // 系统字段特征
      "orderNum": 6                // 严格连续
    },
    // 业务字段从 orderNum: 7 开始
    {
      "dbFieldName": "business_field_1",
      "dbFieldTxt": "业务字段1",
      "orderNum": 7                // 接续系统字段
    }
  ]
}
```

#### **业务字段配置 (第8个字段开始)**

业务字段的orderNum从7开始继续递增，保持整体连续性。

---

## 🔍 **验证清单 - AIGC自检机制**

### **生成前检查清单**

```markdown
## 🔍 AIGC生成前自检清单

### ✅ 表名规范检查
- [ ] 表名符合`us_[module]_[submodule]_[entity]`4段式格式
- [ ] 所有部分都是小写英文，无下划线连接
- [ ] entity部分是业务实体的全小写连续格式

### ✅ 系统字段强制检查  
- [ ] 前7个字段必须是标准系统字段
- [ ] 系统字段orderNum必须是0,1,2,3,4,5,6连续递增
- [ ] 系统字段配置与Code_Gen_Example.json完全一致
- [ ] 系统字段的fieldMustInput, isReadOnly, dbIsNull配置正确

### ✅ 业务字段规范检查
- [ ] 业务字段orderNum从7开始递增
- [ ] 所有字段orderNum保持严格连续性
- [ ] 没有跳号或重复的orderNum

### ✅ 整体配置检查
- [ ] JSON格式正确，无语法错误
- [ ] 必需字段完整，无缺失
- [ ] metadata部分包含完整的生成信息
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

## 📚 **AIGC专用指导规则**

### **🚫 AIGC严禁行为**

1. **禁止修改系统字段配置**
   - 不得更改系统字段的任何属性值
   - 不得调整系统字段的orderNum顺序
   - 不得删除或新增系统字段

2. **禁止使用非连续orderNum**
   - 不得使用990+等高位数值
   - 不得跳过任何数字
   - 不得使用负数或浮点数

3. **禁止偏离标准模板**
   - 系统字段必须与Code_Gen_Example.json完全一致
   - 不得进行任何"优化"或"改进"

### **✅ AIGC推荐行为**

1. **严格模板遵循**
   - 直接复制Code_Gen_Example.json的系统字段配置
   - 仅修改业务字段部分
   - 保持整体结构不变

2. **连续性保证**
   - 确保orderNum从0开始严格递增
   - 业务字段从7开始继续递增
   - 定期验证连续性

3. **自动验证**
   - 生成后立即进行自检
   - 使用验证脚本确认配置正确性
   - 出现问题立即修正

---

## 🔧 **故障排除指南**

### **常见错误及解决方案**

| 错误类型 | 错误现象 | 根本原因 | 解决方案 |
|---------|---------|---------|---------|
| API调用失败 | 表单创建返回错误 | orderNum不连续 | 重新生成，确保连续性 |
| 系统字段错误 | 数据库同步失败 | 系统字段配置错误 | 对比标准模板，完全复制 |
| 表名格式错误 | 表名验证失败 | 表名不符合4段式 | 按us_module_submodule_entity格式重新生成 |

### **调试流程**

1. **JSON格式验证** → 使用JSON Schema验证
2. **系统字段检查** → 对比Code_Gen_Example.json
3. **orderNum连续性** → 使用验证脚本检查
4. **API兼容性测试** → 调用JeecgBoot API验证

---

## 📖 **参考资料**

- **标准模板**: `Code_Gen_Example.json` - 权威配置参考
- **验证工具**: `Code_Gen_Validator.py` - 自动验证脚本  
- **Schema定义**: `Code_Gen_Schema.json` - JSON结构约束
- **变量规范**: `Code_Gen_Variables.md` - 三核心变量定义

---

**版本**: 1.0  
**创建日期**: 2025-07-28  
**适用版本**: JeecgBoot 3.8.1+  
**维护状态**: 持续更新