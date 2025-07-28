#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot代码生成JSON配置文件完整验证器
功能：
- JSON Schema验证
- 系统字段完整性验证
- orderNum连续性严格验证（防止API失败）
- 表名格式验证
- business_entity格式验证
- metadata节点验证
- 字段属性完整性验证
用于确保临时JSON配置文件完全符合JeecgBoot在线表单API要求
防止NullPointerException和其他API调用错误
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
import sys
import os
from typing import Dict, List, Tuple, Any

class CodeGenValidator:
    """代码生成配置文件验证器"""
    
    def __init__(self, schema_file: str = "Code_Gen_Schema.json"):
        """初始化验证器"""
        self.schema_file = schema_file
        self.schema = self._load_schema()
        self.required_system_fields = [
            "id", "create_by", "create_time",
            "update_by", "update_time", "sys_org_code", "del_flag"
        ]
        self.required_head_fields = [
            "tableName", "tableTxt", "business_entity", "tableType", "formCategory", "idType",
            "isCheckbox", "themeTemplate", "formTemplate", "scroll",
            "isPage", "isTree", "extConfigJson", "isDesForm", "desFormCode"
        ]
        self.required_field_attributes = [
            "dbFieldName", "dbFieldTxt", "queryShowType", "queryDictTable",
            "queryDictField", "queryDictText", "queryDefVal", "queryConfigFlag",
            "mainTable", "mainField", "fieldHref", "fieldValidType",
            "fieldMustInput", "dictTable", "dictField", "dictText",
            "isShowForm", "isShowList", "sortFlag", "isReadOnly",
            "fieldShowType", "fieldLength", "isQuery", "queryMode",
            "fieldDefaultValue", "converter", "fieldExtendJson", "fieldConfig",
            "dbLength", "dbPointLength", "dbDefaultVal", "dbType",
            "dbIsKey", "dbIsNull", "dbIsPersist", "orderNum"
        ]

        # 数据库字段长度限制（基于 onl_cgform_field 表结构）
        self.db_field_limits = {
            'queryMode': 10,
            'fieldShowType': 20,
            'queryShowType': 50,
            'fieldValidType': 300,
            'dictField': 100,
            'dictText': 100,
            'dictTable': 255,
            'dbFieldName': 32,
            'dbFieldTxt': 200,
            'fieldHref': 200,
            'fieldDefaultValue': 100,
            'converter': 255,
            'queryDefVal': 50,
            'queryDictText': 100,
            'queryDictField': 100,
            'queryDictTable': 500
        }

        # 已知的超长 queryMode 值及其修正建议
        self.invalid_query_modes = {
            'group_range': 'range',
            'date_range': 'range',
            'multi_select': 'single',
            'complex_query': 'like'
        }
    
    def _load_schema(self) -> Dict:
        """加载JSON Schema"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Schema文件不存在: {self.schema_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Schema文件格式错误: {e}")
            sys.exit(1)
    
    def validate_config(self, config_file: str) -> Tuple[bool, List[str]]:
        """验证配置文件"""
        errors = []
        
        # 1. 加载配置文件
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            return False, [f"配置文件不存在: {config_file}"]
        except json.JSONDecodeError as e:
            return False, [f"JSON格式错误: {e}"]
        
        # 2. Schema验证
        try:
            validate(instance=config, schema=self.schema)
        except ValidationError as e:
            errors.append(f"Schema验证失败: {e.message}")
        
        # 3. 自定义验证
        custom_errors = self._custom_validation(config)
        errors.extend(custom_errors)
        
        return len(errors) == 0, errors
    
    def _custom_validation(self, config: Dict) -> List[str]:
        """自定义验证规则"""
        errors = []
        
        # 验证head部分
        if 'head' not in config or config['head'] is None:
            errors.append("🚨 关键错误: head对象缺失或为null")
            return errors

        # 验证head必需字段
        head = config['head']
        for required_field in self.required_head_fields:
            if required_field not in head:
                errors.append(f"🚨 head缺少必需字段: {required_field}")

        # 验证business_entity字段（关键字段）
        if 'business_entity' not in head:
            errors.append("🚨 关键错误: head节点缺少business_entity字段")
        elif not head['business_entity']:
            errors.append("🚨 关键错误: business_entity字段不能为空")
        elif not isinstance(head['business_entity'], str):
            errors.append("🚨 关键错误: business_entity必须是字符串类型")
        else:
            # 验证business_entity格式（PascalCase）
            business_entity = head['business_entity']
            if not business_entity[0].isupper():
                errors.append(f"⚠️ business_entity应使用PascalCase格式: {business_entity}")
            if '_' in business_entity or '-' in business_entity:
                errors.append(f"⚠️ business_entity不应包含下划线或连字符: {business_entity}")
            if any(word.lower() in ['info', 'management', 'data', 'basic'] for word in business_entity.split()):
                errors.append(f"⚠️ business_entity应避免通用化命名: {business_entity}")

        # 验证tableType数据类型
        if 'tableType' in head and not isinstance(head['tableType'], int):
            errors.append("🚨 tableType必须是整数类型，不能是字符串")

        # 验证scroll数据类型
        if 'scroll' in head and not isinstance(head['scroll'], int):
            errors.append("🚨 scroll必须是整数类型，不能是字符串")
        
        # 验证fields数组
        if 'fields' not in config or config['fields'] is None:
            errors.append("🚨 关键错误: fields数组缺失或为null - 这会导致NullPointerException")
            return errors
        
        if not isinstance(config['fields'], list):
            errors.append("🚨 关键错误: fields必须是数组类型")
            return errors
        
        if len(config['fields']) == 0:
            errors.append("🚨 关键错误: fields数组为空 - 这会导致NullPointerException")
            return errors
        
        # 验证系统字段完整性
        field_names = [field.get('dbFieldName', '') for field in config['fields']]
        missing_system_fields = []
        for required_field in self.required_system_fields:
            if required_field not in field_names:
                missing_system_fields.append(required_field)
        
        if missing_system_fields:
            errors.append(f"🚨 系统字段缺失: {', '.join(missing_system_fields)}")
        
        # 验证字段orderNum连续性（严格验证）
        order_nums = []
        for i, field in enumerate(config['fields']):
            if 'orderNum' not in field:
                errors.append(f"🚨 字段{i+1} ({field.get('dbFieldName', '未知')}) 缺少orderNum")
                continue
            order_nums.append((i, field.get('dbFieldName', '未知'), field['orderNum']))

        # 检查orderNum重复
        order_values = [x[2] for x in order_nums]
        if len(set(order_values)) != len(order_values):
            errors.append("🚨 字段orderNum存在重复 - 这会导致API失败")

        # 检查orderNum连续性（必须从0开始连续递增）
        order_nums.sort(key=lambda x: x[2])
        for i, (field_index, field_name, order_num) in enumerate(order_nums):
            if order_num != i:
                errors.append(f"🚨 orderNum不连续: 字段'{field_name}' orderNum={order_num}, 期望={i} - 这会导致API失败")
        
        # 验证表名格式
        table_name = config.get('head', {}).get('tableName', '')
        if not table_name.startswith('us_') or table_name.count('_') < 3:
            errors.append(f"⚠️ 表名格式不正确: {table_name} (应为us_{{模块}}_{{子模块}}_{{实体}})")

        # 验证表名与business_entity的一致性
        if 'business_entity' in head and head['business_entity']:
            business_entity = head['business_entity']
            # 将PascalCase转换为全小写连续格式进行比较
            expected_suffix = self._pascal_to_snake_case(business_entity)
            if not table_name.endswith(expected_suffix):
                errors.append(f"⚠️ 表名后缀与business_entity不匹配: {table_name} vs {expected_suffix}")

        # 验证metadata节点（推荐但非必需）
        if 'metadata' in config:
            metadata_errors = self._validate_metadata(config['metadata'], head.get('business_entity', ''))
            errors.extend(metadata_errors)
        
        # 验证字段必需属性和长度限制
        for i, field in enumerate(config['fields']):
            field_errors = self._validate_field(field, i + 1)
            errors.extend(field_errors)

            # 验证字段长度限制
            length_errors = self._validate_field_lengths(field, i + 1)
            errors.extend(length_errors)

        # 验证是否包含indexs, deleteFieldIds, deleteIndexIds
        required_arrays = ['indexs', 'deleteFieldIds', 'deleteIndexIds']
        for array_name in required_arrays:
            if array_name not in config:
                errors.append(f"🚨 缺少必需数组: {array_name}")
            elif not isinstance(config[array_name], list):
                errors.append(f"🚨 {array_name}必须是数组类型")
        
        return errors

    def _pascal_to_snake_case(self, pascal_str: str) -> str:
        """将PascalCase转换为全小写连续格式（遵循Code_Gen_Variables.md规范）"""
        # 直接转换为全小写连续，不插入下划线
        # VehicleInfo -> vehicleinfo (不是 vehicle_info)
        return pascal_str.lower()

    def _validate_metadata(self, metadata: Dict, business_entity: str) -> List[str]:
        """验证metadata节点"""
        errors = []

        if not isinstance(metadata, dict):
            errors.append("⚠️ metadata必须是对象类型")
            return errors

        # 验证generation_info节点
        if 'generation_info' in metadata:
            gen_info = metadata['generation_info']
            if not isinstance(gen_info, dict):
                errors.append("⚠️ metadata.generation_info必须是对象类型")
            else:
                # 验证关键字段
                required_gen_fields = ['module_name', 'submodule_name', 'business_entity']
                for field in required_gen_fields:
                    if field not in gen_info:
                        errors.append(f"💡 建议添加metadata.generation_info.{field}字段")

                # 验证business_entity一致性
                if 'business_entity' in gen_info and gen_info['business_entity'] != business_entity:
                    errors.append(f"⚠️ metadata中的business_entity与head中的不一致")

        # 验证derived_formats节点
        if 'derived_formats' in metadata:
            derived = metadata['derived_formats']
            if not isinstance(derived, dict):
                errors.append("⚠️ metadata.derived_formats必须是对象类型")
            else:
                recommended_fields = ['table_suffix', 'url_path', 'frontend_path']
                for field in recommended_fields:
                    if field not in derived:
                        errors.append(f"💡 建议添加metadata.derived_formats.{field}字段")

        return errors

    def _validate_field(self, field: Dict, field_index: int) -> List[str]:
        """验证单个字段"""
        errors = []

        # 验证所有必需属性
        for attr in self.required_field_attributes:
            if attr not in field:
                errors.append(f"⚠️ 字段{field_index}: 缺少必需属性 {attr}")
            elif field[attr] is None:
                errors.append(f"⚠️ 字段{field_index}: 属性 {attr} 不能为null")
            elif attr in ['dbFieldName', 'dbFieldTxt'] and field[attr] == '':
                errors.append(f"⚠️ 字段{field_index}: {attr} 不能为空字符串")

        # 验证dbIsPersist字段存在
        if 'dbIsPersist' not in field:
            errors.append(f"🚨 字段{field_index}: 缺少关键字段 dbIsPersist")

        # 验证数据类型
        if 'dbIsKey' in field and field['dbIsKey'] not in ['0', '1']:
            errors.append(f"⚠️ 字段{field_index}: dbIsKey必须是字符串'0'或'1'")

        if 'dbIsNull' in field and field['dbIsNull'] not in ['0', '1']:
            errors.append(f"⚠️ 字段{field_index}: dbIsNull必须是字符串'0'或'1'")

        if 'dbIsPersist' in field and field['dbIsPersist'] not in ['0', '1']:
            errors.append(f"⚠️ 字段{field_index}: dbIsPersist必须是字符串'0'或'1'")

        return errors

    def _validate_field_lengths(self, field: Dict, field_index: int) -> List[str]:
        """验证字段值长度是否符合数据库限制"""
        errors = []

        for field_name, max_length in self.db_field_limits.items():
            if field_name in field:
                field_value = str(field[field_name])

                # 特殊处理 queryMode 字段
                if field_name == 'queryMode':
                    if field_value in self.invalid_query_modes:
                        suggested_value = self.invalid_query_modes[field_value]
                        errors.append(f"❌ 字段{field_index}: queryMode值'{field_value}'超过10字符限制，建议改为'{suggested_value}'")
                    elif len(field_value) > max_length:
                        errors.append(f"❌ 字段{field_index}: queryMode值'{field_value}'长度({len(field_value)})超过{max_length}字符限制")

                # 通用长度检查
                elif len(field_value) > max_length:
                    errors.append(f"❌ 字段{field_index}: {field_name}值过长({len(field_value)}字符)，超过{max_length}字符限制")

        return errors

    def generate_validation_report(self, config_file: str) -> str:
        """生成验证报告"""
        is_valid, errors = self.validate_config(config_file)
        
        report = f"""
📋 JSON配置文件验证报告
{'='*50}
文件: {config_file}
状态: {'✅ 验证通过' if is_valid else '❌ 验证失败'}
时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        if is_valid:
            report += "🎉 配置文件完全符合JeecgBoot在线表单API要求\n"
            report += "✅ 通过完整验证：JSON Schema、系统字段、orderNum连续性、表名格式等\n"
            report += "✅ 可以安全地调用Code_Gen_Guide.py执行代码生成\n"
        else:
            report += f"❌ 发现 {len(errors)} 个问题:\n\n"
            for i, error in enumerate(errors, 1):
                report += f"{i}. {error}\n"
            
            report += "\n🔧 修复建议:\n"
            report += "1. 检查fields数组是否存在且不为空\n"
            report += "2. 确保包含所有7个系统字段\n"
            report += "3. 验证orderNum从0开始连续递增（关键！）\n"
            report += "4. 验证字段属性完整性\n"
            report += "5. 检查表名格式是否正确\n"
            report += "6. 确保business_entity使用PascalCase格式\n"
            report += "7. 🚨 检查字段值长度限制（特别是queryMode不超过10字符）\n"
            report += "8. 将'group_range'改为'range'，'date_range'改为'range'\n"
        
        return report

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python3 Code_Gen_Validator.py <config_file.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    validator = CodeGenValidator()
    
    print("🔍 开始验证JSON配置文件...")
    report = validator.generate_validation_report(config_file)
    print(report)
    
    is_valid, _ = validator.validate_config(config_file)
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
