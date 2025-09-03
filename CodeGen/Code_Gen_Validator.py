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

        # 验证subList配置（如果存在）
        if 'subList' in config:
            sub_list_valid, sub_list_errors = self.validate_sub_list(config['subList'])
            if not sub_list_valid:
                errors.extend(sub_list_errors)

            # 验证主子表一致性
            consistency_valid, consistency_errors = self.validate_master_sub_consistency(config)
            if not consistency_valid:
                errors.extend(consistency_errors)

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

    def _validate_table_name(self, config: Dict) -> List[str]:
        """验证表名格式"""
        errors = []
        table_name = config.get('head', {}).get('tableName', '')

        if not table_name.startswith('us_'):
            errors.append("表名必须以us_开头")

        if table_name.count('_') != 3:
            errors.append("表名必须是4段式: us_module_submodule_entity")

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
            report += "3. 验证表名格式: us_module_submodule_entity\n"

        return report

    def validate_sub_list(self, sub_list: List[Dict]) -> Tuple[bool, List[str]]:
        """验证subList配置的完整性"""
        errors = []

        if not isinstance(sub_list, list):
            errors.append("subList必须是数组类型")
            return False, errors

        if len(sub_list) == 0:
            errors.append("subList不能为空数组")
            return False, errors

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
                if not re.match(r'^us_[a-z0-9_]+$', table_name):
                    errors.append(f"subList[{i}]表名格式错误: {table_name}，应为us_开头的小写字母、数字和下划线格式")

                if table_name in used_table_names:
                    errors.append(f"subList[{i}]表名重复: {table_name}")
                else:
                    used_table_names.add(table_name)

            # 验证实体名格式
            entity_name = sub_table.get('entityName', '')
            if entity_name and not re.match(r'^[A-Z][a-zA-Z0-9]*$', entity_name):
                errors.append(f"subList[{i}]实体名格式错误: {entity_name}，应为PascalCase格式")

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
        if len(main_parts) != 4:
            errors.append(f"主表名格式错误: {main_table_name}")
            return False, errors

        main_prefix, main_module, main_submodule = main_parts[0], main_parts[1], main_parts[2]

        # 验证子表与主表的模块一致性
        for i, sub_table in enumerate(sub_list):
            sub_table_name = sub_table.get('tableName', '')
            if sub_table_name:
                sub_parts = sub_table_name.split('_')
                if len(sub_parts) == 4:
                    sub_prefix, sub_module, sub_submodule = sub_parts[0], sub_parts[1], sub_parts[2]

                    if sub_prefix != main_prefix:
                        errors.append(f"subList[{i}]前缀不一致: 主表{main_prefix}，子表{sub_prefix}")

                    if sub_module != main_module:
                        errors.append(f"subList[{i}]模块不一致: 主表{main_module}，子表{sub_module}")

                    # 子模块可以不同，但不能与主表相同
                    if sub_submodule == main_submodule:
                        errors.append(f"subList[{i}]子模块与主表相同: {sub_submodule}")

        return len(errors) == 0, errors

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
