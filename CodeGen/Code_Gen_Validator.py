#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot配置文件验证器
核心功能：
- orderNum连续性验证（防止API失败）
- 系统字段完整性验证
- 表名格式验证
- 高效JSON格式验证
- subList配置完整性验证（主子表场景）
- 主子表一致性检查
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
import sys
import re
from typing import Dict, List, Tuple, Optional

class CodeGenValidator:
    """高效配置文件验证器"""

    def __init__(self, schema_file: str = None):
        """初始化验证器"""
        if schema_file is None:
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            schema_file = os.path.join(current_dir, "Code_Gen_Schema.json")
        self.schema_file = schema_file
        self.schema = self._load_schema()
        # 核心常量
        self.system_fields = ["id", "create_by", "create_time", "update_by", "update_time", "sys_org_code", "del_flag"]

    def _load_schema(self) -> Dict:
        """加载JSON Schema"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Schema文件不存在: {self.schema_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Schema文件格式错误: {e}")
            return {}

    def validate_config(self, config_file: str) -> Tuple[bool, List[str]]:
        """验证配置文件"""
        errors = []

        # 加载配置文件
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            return False, [f"配置文件不存在: {config_file}"]
        except json.JSONDecodeError as e:
            return False, [f"JSON格式错误: {e}"]

        # 核心验证
        errors.extend(self._validate_order_num(config))
        errors.extend(self._validate_system_fields(config))
        errors.extend(self._validate_table_name(config))
        errors.extend(self._validate_field_names(config))
        errors.extend(self._validate_field_length_limits(config))

        # 验证表类型参数
        table_type_valid, table_type_errors = self.validate_table_type_params(config)
        if not table_type_valid:
            errors.extend(table_type_errors)

        # 智能验证subList配置（根据表类型）
        table_type = config.get('head', {}).get('tableType', 1)
        has_sub_list = 'subList' in config
        
        if table_type == 1:  # 独立表
            if has_sub_list:
                errors.append("独立表不应包含subList配置")
        elif table_type == 2:  # 主表
            if has_sub_list:
                # 主表可以有subList，但如果存在就需要验证
                sub_list_valid, sub_list_errors = self.validate_sub_list_for_master_table(config['subList'], config)
                if not sub_list_valid:
                    errors.extend(sub_list_errors)
                
                # 验证主子表一致性
                consistency_valid, consistency_errors = self.validate_master_sub_consistency(config)
                if not consistency_valid:
                    errors.extend(consistency_errors)
        elif table_type == 3:  # 子表
            if has_sub_list:
                errors.append("子表不应包含subList配置")

        return len(errors) == 0, errors

    def _validate_order_num(self, config: Dict) -> List[str]:
        """验证orderNum连续性（核心验证）"""
        errors = []
        fields = config.get('fields', [])

        if not fields:
            return ["🚨 fields数组为空"]

        # 获取所有orderNum
        order_nums = []
        for i, field in enumerate(fields):
            if 'orderNum' not in field:
                errors.append(f"🚨 字段{i+1}缺少orderNum")
                continue
            order_nums.append(field['orderNum'])

        # 检查连续性
        order_nums.sort()
        for i, num in enumerate(order_nums):
            if num != i:
                errors.append(f"🚨 orderNum不连续: 期望{i}, 实际{num} - 这会导致API失败")

        return errors

    def _validate_system_fields(self, config: Dict) -> List[str]:
        """验证系统字段完整性"""
        errors = []
        fields = config.get('fields', [])

        if len(fields) < 7:
            return ["🚨 字段数量不足，至少需要7个系统字段"]

        # 检查前7个字段是否为系统字段
        for i, expected_field in enumerate(self.system_fields):
            if i >= len(fields):
                errors.append(f"🚨 缺少系统字段: {expected_field}")
                continue

            actual_field = fields[i].get('dbFieldName', '')
            if actual_field != expected_field:
                errors.append(f"🚨 系统字段{i}错误: 期望{expected_field}, 实际{actual_field}")

        return errors

    def _validate_field_names(self, config: Dict) -> List[str]:
        """验证字段名长度和格式（重点关注db_field_name的32字符限制）"""
        errors = []
        fields = config.get('fields', [])

        for i, field in enumerate(fields):
            field_name = field.get('dbFieldName', '')
            if not field_name:
                errors.append(f"🚨 字段{i+1}缺少dbFieldName")
                continue

            # 检查字段名长度（重要：对应数据库onl_cgform_field.db_field_name varchar(32)限制）
            if len(field_name) > 32:
                errors.append(f"🚨 字段{i+1}的dbFieldName超长: '{field_name}' ({len(field_name)}字符 > 32字符限制) - 这会导致数据库插入失败")

            # 检查字段名格式
            if not re.match(r'^[a-z][a-z0-9_]*$', field_name):
                errors.append(f"🚨 字段{i+1}的dbFieldName格式错误: '{field_name}' (应为小写字母开头，可包含数字和下划线)")

            # 检查是否包含连续下划线
            if '__' in field_name:
                errors.append(f"⚠️ 字段{i+1}的dbFieldName包含连续下划线: '{field_name}' (建议避免使用)")

        return errors

    def _validate_table_name(self, config: Dict) -> List[str]:
        """验证表名格式"""
        errors = []
        table_name = config.get('head', {}).get('tableName', '')

        if table_name.count('_') < 2:
            errors.append("表名必须至少是3段式: module_submodule_entity（支持更多段）")

        return errors

    def _validate_field_length_limits(self, config: Dict) -> List[str]:
        """验证字段长度限制"""
        errors = []
        fields = config.get('fields', [])

        # 字段长度限制定义（除了dbFieldName，它在_validate_field_names中专门处理）
        length_limits = {
            'queryMode': 10,
            'fieldShowType': 20,
            'queryShowType': 50,
            'fieldValidType': 300
        }

        for i, field in enumerate(fields):
            for field_name, max_length in length_limits.items():
                if field_name in field:
                    value = field[field_name]
                    if isinstance(value, str) and len(value) > max_length:
                        errors.append(f"🚨 字段{i+1}的{field_name}超长: {len(value)}字符 > {max_length}字符限制")

        return errors

    def generate_validation_report(self, config_file: str) -> str:
        """生成验证报告"""
        is_valid, errors = self.validate_config(config_file)

        report = f"""
JSON配置验证报告
{'='*40}
文件: {config_file}
状态: {'验证通过' if is_valid else '验证失败'}

"""

        if is_valid:
            report += "配置文件符合JeecgBoot API要求\n"
            report += "核心验证通过：orderNum连续性、系统字段、表名格式\n"
        else:
            report += f"发现 {len(errors)} 个问题:\n\n"
            for i, error in enumerate(errors, 1):
                report += f"{i}. {error}\n"

            report += "\n修复建议:\n"
            report += "1. 确保orderNum从0开始连续递增\n"
            report += "2. 检查前7个系统字段是否正确\n"
            report += "3. 验证表名格式: module_submodule_entity\n"
            report += "4. 确保dbFieldName长度不超过32字符(数据库限制)\n"
            report += "5. 检查字段名格式: 小写字母开头，可包含数字和下划线\n"

            # 添加字段名修正建议
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                suggestions = self.suggest_field_name_corrections(config)
                if suggestions:
                    report += "\n字段名修正建议:\n"
                    for field_key, suggestion in suggestions.items():
                        report += f"  {field_key}: {suggestion}\n"
            except Exception as e:
                report += f"\n无法生成字段名修正建议: {e}\n"

        return report

    def validate_sub_list_for_master_table(self, sub_list: List[Dict], config: Dict = None) -> Tuple[bool, List[str]]:
        """验证主表的subList配置 - 允许空数组"""
        errors = []

        if not isinstance(sub_list, list):
            errors.append("subList必须是数组类型")
            return False, errors

        # 主表允许空的subList（表示暂时没有子表）
        if len(sub_list) == 0:
            return True, []

        # 如果不为空，则使用标准验证逻辑
        return self._validate_sub_list_content(sub_list, config)

    def validate_sub_list(self, sub_list: List[Dict]) -> Tuple[bool, List[str]]:
        """验证subList配置的完整性 - 子表场景（不允许空数组）"""
        errors = []

        if not isinstance(sub_list, list):
            errors.append("subList必须是数组类型")
            return False, errors

        if len(sub_list) == 0:
            errors.append("subList不能为空数组")
            return False, errors

        return self._validate_sub_list_content(sub_list)

    def _validate_sub_list_content(self, sub_list: List[Dict], config: Dict = None) -> Tuple[bool, List[str]]:
        """验证subList内容的通用逻辑"""
        errors = []

        # 验证必需字段
        required_fields = ['tableName', 'entityName', 'ftlDescription', 'id']
        used_ids = set()
        used_table_names = set()

        for i, sub_table in enumerate(sub_list):
            if not isinstance(sub_table, dict):
                errors.append(f"subList[{i}]必须是对象类型")
                continue

            # 检查必需字段
            for field in required_fields:
                if field not in sub_table or not sub_table[field]:
                    errors.append(f"subList[{i}]缺少必需字段: {field}")

            # 验证表名格式
            table_name = sub_table.get('tableName', '')
            if table_name:
                if not re.match(r'^[a-z0-9_]+$', table_name):
                    errors.append(f"subList[{i}]表名格式错误: {table_name}，应为小写字母、数字和下划线格式")

                if table_name in used_table_names:
                    errors.append(f"subList[{i}]表名重复: {table_name}")
                else:
                    used_table_names.add(table_name)

            # 验证实体名格式
            entity_name = sub_table.get('entityName', '')
            if entity_name:
                # 基础格式验证
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', entity_name):
                    errors.append(f"subList[{i}]实体名格式错误: {entity_name}，应为PascalCase格式")
                
                # ✅ 新增：验证完整复合格式
                main_entity = config.get('head', {}).get('business_entity', '')
                if main_entity and not entity_name.startswith(main_entity):
                    errors.append(f"subList[{i}]实体名格式错误: {entity_name}，应为完整复合格式: {main_entity}XxxInfo")
                    errors.append(f"⚠️ JeecgBoot API要求subList entityName必须为主表实体名+子表实体名的复合格式")
                elif main_entity and entity_name == main_entity:
                    errors.append(f"subList[{i}]实体名不能与主表相同: {entity_name}，应为: {main_entity}XxxInfo")

            # 验证ID格式
            sub_id = sub_table.get('id', '')
            if sub_id:
                if not re.match(r'^row_[0-9]{4}$', sub_id):
                    errors.append(f"subList[{i}]的id格式错误: {sub_id}，应为row_xxxx格式")

                if sub_id in used_ids:
                    errors.append(f"subList[{i}]的id重复: {sub_id}")
                else:
                    used_ids.add(sub_id)

        # 验证ID连续性（从row_1020开始）
        if used_ids:
            id_numbers = []
            for sub_id in used_ids:
                if re.match(r'^row_[0-9]{4}$', sub_id):
                    id_numbers.append(int(sub_id[4:]))

            if id_numbers:
                id_numbers.sort()
                expected_start = 1020
                for i, num in enumerate(id_numbers):
                    if num != expected_start + i:
                        errors.append(f"subList的id不连续，期望row_{expected_start + i:04d}，实际row_{num:04d}")
                        break

        return len(errors) == 0, errors

    def validate_master_sub_consistency(self, config: Dict) -> Tuple[bool, List[str]]:
        """验证主子表配置的一致性"""
        errors = []

        # 检查是否包含subList
        if 'subList' not in config:
            return True, []  # 不是主子表场景，跳过验证

        sub_list = config['subList']
        if not sub_list:
            return True, []  # 空subList，跳过验证

        # 获取主表信息
        head = config.get('head', {})
        main_table_name = head.get('tableName', '')

        if not main_table_name:
            errors.append("主表缺少tableName")
            return False, errors

        # 解析主表的模块信息
        main_parts = main_table_name.split('_')
        if len(main_parts) < 3:
            errors.append(f"主表名格式错误: {main_table_name}（至少需要3段）")
            return False, errors

        main_module, main_submodule = main_parts[0], main_parts[1]

        # 验证子表与主表的模块一致性
        for i, sub_table in enumerate(sub_list):
            sub_table_name = sub_table.get('tableName', '')
            if sub_table_name:
                sub_parts = sub_table_name.split('_')
                if len(sub_parts) >= 3:
                    sub_module, sub_submodule = sub_parts[0], sub_parts[1]

                    if sub_module != main_module:
                        errors.append(f"subList[{i}]模块不一致: 主表{main_module}，子表{sub_module}")

                    if sub_submodule != main_submodule:
                        errors.append(f"subList[{i}]子模块不一致: 主表{main_submodule}，子表{sub_submodule}")

        return len(errors) == 0, errors

    def validate_table_type_params(self, config: Dict) -> Tuple[bool, List[str]]:
        """验证表类型参数（tableType、relationType、tabOrderNum）"""
        errors = []

        head = config.get('head', {})
        table_type = head.get('tableType')
        relation_type = head.get('relationType')
        tab_order_num = head.get('tabOrderNum')
        sub_list = config.get('subList', [])

        # 验证tableType
        if table_type is None:
            errors.append("head.tableType 字段缺失")
        elif not isinstance(table_type, int) or table_type not in [1, 2, 3]:
            errors.append(f"head.tableType 必须是整数 1、2 或 3，当前值: {table_type}")

        # 根据tableType验证其他参数
        if table_type == 1:  # 独立表
            if relation_type is not None:
                errors.append(f"独立表的 relationType 必须为 null，当前值: {relation_type}")
            if tab_order_num is not None:
                errors.append(f"独立表的 tabOrderNum 必须为 null，当前值: {tab_order_num}")
            if sub_list:
                errors.append("独立表不应包含 subList 配置")

        elif table_type == 2:  # 主表
            if relation_type is not None:
                errors.append(f"主表的 relationType 必须为 null，当前值: {relation_type}")
            if tab_order_num is not None:
                errors.append(f"主表的 tabOrderNum 必须为 null，当前值: {tab_order_num}")
            # 主表可以有subList，这是正常的

        elif table_type == 3:  # 子表
            if relation_type is None:
                errors.append("子表的 relationType 不能为 null")
            elif not isinstance(relation_type, int) or relation_type not in [0, 1]:
                errors.append(f"子表的 relationType 必须是 0（一对多）或 1（一对一），当前值: {relation_type}")

            if tab_order_num is None:
                errors.append("子表的 tabOrderNum 不能为 null")
            elif not isinstance(tab_order_num, int) or tab_order_num < 1:
                errors.append(f"子表的 tabOrderNum 必须是大于0的整数，当前值: {tab_order_num}")

            if sub_list:
                errors.append("子表不应包含 subList 配置")

            # 验证外键字段
            foreign_key_valid, foreign_key_errors = self.validate_foreign_key_fields(config)
            if not foreign_key_valid:
                errors.extend(foreign_key_errors)

        return len(errors) == 0, errors

    def validate_foreign_key_fields(self, config: Dict) -> Tuple[bool, List[str]]:
        """验证子表的外键字段"""
        errors = []

        fields = config.get('fields', [])
        foreign_key_found = False

        for field in fields:
            field_name = field.get('dbFieldName', '')
            main_table = field.get('mainTable', '')
            main_field = field.get('mainField', '')

            # 检查是否有外键字段（以_id结尾且有mainTable配置）
            if field_name.endswith('_id') and main_table and main_field:
                foreign_key_found = True

                # 验证外键字段配置
                if main_field != 'id':
                    errors.append(f"外键字段 {field_name} 的 mainField 应该是 'id'，当前值: {main_field}")

                # 验证字段类型
                db_type = field.get('dbType', '')
                if db_type != 'string':
                    errors.append(f"外键字段 {field_name} 的 dbType 应该是 'string'，当前值: {db_type}")

                # 验证字段长度
                db_length = field.get('dbLength', 0)
                if db_length != 36:
                    errors.append(f"外键字段 {field_name} 的 dbLength 应该是 36（UUID长度），当前值: {db_length}")

        if not foreign_key_found:
            errors.append("子表必须包含至少一个外键字段（字段名以_id结尾，且配置了mainTable和mainField）")

        return len(errors) == 0, errors

    def suggest_field_name_corrections(self, config: Dict) -> Dict[str, str]:
        """为过长的字段名提供修正建议"""
        suggestions = {}
        fields = config.get('fields', [])

        # 常见缩写映射
        abbreviations = {
            'information': 'info',
            'profile': 'prof', 
            'description': 'desc',
            'configuration': 'config',
            'management': 'mgmt',
            'customer': 'cust',
            'employee': 'emp',
            'department': 'dept',
            'organization': 'org',
            'telephone': 'tel',
            'address': 'addr',
            'reference': 'ref',
            'category': 'cat',
            'status': 'stat',
            'number': 'num',
            'identifier': 'id',
            'timestamp': 'ts',
            'created': 'crt',
            'updated': 'upd',
            'modified': 'mod'
        }

        for i, field in enumerate(fields):
            field_name = field.get('dbFieldName', '')
            if len(field_name) > 32:
                # 尝试自动缩短字段名
                shortened = field_name
                
                # 应用常见缩写
                for full, abbr in abbreviations.items():
                    shortened = shortened.replace(full, abbr)
                
                # 移除连续下划线
                while '__' in shortened:
                    shortened = shortened.replace('__', '_')
                
                # 如果仍然太长，进行进一步缩短
                if len(shortened) > 32:
                    # 尝试移除元音字母（保留第一个字符和下划线后的首字符）
                    parts = shortened.split('_')
                    new_parts = []
                    for part in parts:
                        if len(part) > 3:
                            # 保留首字符和辅音
                            consonants = part[0] + ''.join([c for c in part[1:] if c not in 'aeiou'])
                            new_parts.append(consonants[:6])  # 限制每部分最多6字符
                        else:
                            new_parts.append(part)
                    shortened = '_'.join(new_parts)
                
                # 确保不超过32字符
                if len(shortened) > 32:
                    shortened = shortened[:32]
                
                suggestions[f"field_{i+1}_dbFieldName"] = f"'{field_name}' -> '{shortened}'"

        return suggestions

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python3 Code_Gen_Validator.py <config_file.json>")
        sys.exit(1)

    config_file = sys.argv[1]
    validator = CodeGenValidator()

    print("验证JSON配置文件...")
    report = validator.generate_validation_report(config_file)
    print(report)

    is_valid, _ = validator.validate_config(config_file)
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
