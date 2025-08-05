#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot配置文件验证器
核心功能：
- orderNum连续性验证（防止API失败）
- 系统字段完整性验证
- 表名格式验证
- 高效JSON格式验证
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
import sys
from typing import Dict, List, Tuple

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
