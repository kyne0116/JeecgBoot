# AIGC JSON配置生成检查清单

> **文档定位**: AIGC生成JSON配置文件的必备检查清单  
> **使用场景**: 每次生成临时JSON配置文件时必须执行  
> **核心目标**: 确保100%兼容JeecgBoot官方API，避免致命错误

---

## 🚨 **生成前必读警示**

### ⚠️ **致命约束 - 绝不可违反**

1. **系统字段orderNum连续性**：必须从0开始严格连续递增
2. **系统字段配置标准化**：必须与Code_Gen_Example.json完全一致
3. **表名格式4段式**：us_模块_子模块_实体格式

**违反任一条都会导致JeecgBoot API调用失败！**

---

## ✅ **生成前检查清单**

### **第一步：基础结构检查**
```markdown
□ JSON格式正确，无语法错误
□ 包含head和fields两个主要部分
□ head部分包含所有必需字段
□ fields数组至少包含8个字段(7个系统字段+1个业务字段)
```

### **第二步：表名规范检查** 
```markdown
□ 表名符合 us_[module]_[submodule]_[entity] 4段式格式
□ 所有部分都是小写英文字母
□ 无下划线连接符(除了4段分隔符)
□ entity部分是business_entity的全小写连续格式

示例：
✅ us_finance_invoice_customerprofile
❌ us_finance_invoice_customer_profile (多了下划线)
❌ us_Finance_Invoice_CustomerProfile (包含大写)
```

### **第三步：系统字段强制检查**
```markdown
□ 前7个字段必须是标准系统字段：
  [0] id
  [1] create_by  
  [2] create_time
  [3] update_by
  [4] update_time
  [5] sys_org_code
  [6] del_flag

□ 系统字段orderNum必须是：0,1,2,3,4,5,6
□ 系统字段配置与Code_Gen_Example.json完全一致
□ 未修改任何系统字段的属性值
```

### **第四步：orderNum连续性检查**
```markdown
□ 所有字段的orderNum从0开始连续递增
□ 无跳号：不能是 0,1,2,3,4,5,6,990,991
□ 无重复：不能有相同的orderNum值
□ 无负数：所有orderNum都是非负整数

正确示例：0,1,2,3,4,5,6,7,8,9,10...
错误示例：0,1,2,3,4,5,6,990,991,992...
```

### **第五步：业务字段规范检查**
```markdown
□ 业务字段orderNum从7开始递增
□ 业务字段配置合理(数据类型、长度等)
□ 字段名称符合数据库命名规范
□ 包含必要的显示和查询配置
```

---

## 🔧 **AIGC生成标准流程**

### **步骤1：复制系统字段**
```json
// 直接从Code_Gen_Example.json复制前7个系统字段
// 不做任何修改，保持orderNum为0,1,2,3,4,5,6
{
  "fields": [
    // 系统字段1-7: 完全复制，不修改
    {
      "dbFieldName": "id",
      "orderNum": 0,
      // ... 其他属性完全一致
    },
    // ... 复制完整的7个系统字段
```

### **步骤2：添加业务字段**
```json
    // 业务字段从orderNum: 7开始
    {
      "dbFieldName": "business_field_1",
      "orderNum": 7,
      // ... 业务字段配置
    },
    {
      "dbFieldName": "business_field_2", 
      "orderNum": 8,
      // ... 业务字段配置
    }
  ]
}
```

### **步骤3：立即自检**
```python
# 伪代码：生成后立即执行
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

---

## 🚫 **AIGC常见错误及避免**

### **错误1：orderNum不连续**
```json
❌ 错误配置：
{"orderNum": 0},  // id
{"orderNum": 1},  // create_by
{"orderNum": 990}, // create_time - 错误！跳到了990
{"orderNum": 991}, // update_by

✅ 正确配置：
{"orderNum": 0},  // id
{"orderNum": 1},  // create_by  
{"orderNum": 2},  // create_time - 正确！连续递增
{"orderNum": 3},  // update_by
```

### **错误2：修改系统字段配置**
```json
❌ 错误：修改了系统字段属性
{
  "dbFieldName": "create_by",
  "fieldMustInput": "0",  // 错误！应该是"1"
  "orderNum": 1
}

✅ 正确：完全按照标准模板
{
  "dbFieldName": "create_by", 
  "fieldMustInput": "1",  // 正确！与模板一致
  "orderNum": 1
}
```

### **错误3：表名格式错误**
```json
❌ 错误格式：
"tableName": "us_finance_invoice"  // 缺少entity部分
"tableName": "us_Finance_Invoice_Customer"  // 包含大写
"tableName": "us_finance_invoice_customer_profile"  // entity部分有下划线

✅ 正确格式：
"tableName": "us_finance_invoice_customerprofile"  // 4段式，全小写连续
```

---

## 🔍 **生成后验证命令**

### **快速验证**
```bash
# 使用高级验证器进行全面检查
python3 Code_Gen_Advanced_Validator.py temp_config.json

# 使用标准验证器检查格式
python3 Code_Gen_Validator.py temp_config.json

# JSON Schema验证
jsonschema -i temp_config.json Code_Gen_Schema.json
```

### **验证通过标准**
```
✅ orderNum连续性验证通过: 0-N 连续递增
✅ 系统字段配置验证通过
✅ 表名格式验证通过: us_module_submodule_entity
✅ 业务实体名称验证通过: PascalCase格式
✅ JSON格式验证通过
```

---

## 📚 **参考文档**

- **标准模板**: `Code_Gen_Example.json` - 系统字段配置权威参考
- **详细规范**: `Code_Gen_JSON_Standards.md` - 完整技术标准
- **验证工具**: `Code_Gen_Advanced_Validator.py` - 自动验证脚本
- **变量定义**: `Code_Gen_Variables.md` - 三核心变量规范

---

## 🎯 **记住这3个关键点**

1. **📋 复制模板**：系统字段配置完全复制Code_Gen_Example.json
2. **🔢 连续递增**：orderNum从0开始严格连续，不能跳号
3. **🔍 立即验证**：生成后立即使用验证工具检查

**遵循这3点，确保JSON配置100%兼容JeecgBoot API！**

---

**版本**: 1.0  
**创建日期**: 2025-07-28  
**适用场景**: AIGC生成临时JSON配置文件  
**维护状态**: 持续更新