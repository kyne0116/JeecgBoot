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

        # 验证数据字典字段配置
        dict_field_valid, dict_field_errors = self.validate_dictionary_fields(config)
        if not dict_field_valid:
            errors.extend(dict_field_errors)

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
        """验证表名格式 - 严格三段式"""
        errors = []
        table_name = config.get('head', {}).get('tableName', '')
        
        # 严格三段式验证：必须正好有3段，不允许4段式或更多段式
        segments = table_name.split('_')
        
        if len(segments) != 3:
            errors.append(f"❌ 表名格式错误: '{table_name}' 必须严格为三段式格式 {{MODULE_NAME}}_{{SUBMODULE_NAME}}_{{ENTITY_SUFFIX}}，当前为{len(segments)}段式")
            return errors
        
        module_name, submodule_name, entity_suffix = segments
        
        # 验证各段格式
        if not re.match(r'^[a-z]+$', module_name):
            errors.append(f"❌ MODULE_NAME格式错误: '{module_name}' 必须为纯小写字母")
        
        if not re.match(r'^[a-z]+$', submodule_name):
            errors.append(f"❌ SUBMODULE_NAME格式错误: '{submodule_name}' 必须为纯小写字母")
        
        if not re.match(r'^[a-z0-9]+$', entity_suffix):
            errors.append(f"❌ ENTITY_SUFFIX格式错误: '{entity_suffix}' 必须为小写字母和数字组合")
            
        # 检查常见的四段式错误模式
        invalid_patterns = [
            "crm_customer_customer_profile",
            "education_student_student_info", 
            "finance_invoice_invoice_header"
        ]
        
        if table_name in invalid_patterns:
            errors.append(f"❌ 禁止使用四段式表名: '{table_name}' 应简化为三段式，如 'crm_customer_profile'")

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

        # 加载数据字典信息
        dict_result = self._load_and_validate_dict_codes()

        report = f"""
JSON配置验证报告
{'='*40}
文件: {config_file}
状态: {'验证通过' if is_valid else '验证失败'}

"""

        # 数据字典状态报告
        if dict_result['success']:
            report += f"数据字典状态: ✅ 正常 (共{dict_result['valid_items']}个可用字典)\n"
        else:
            report += f"数据字典状态: ❌ 异常 - {dict_result['error']}\n"
        
        report += "\n"

        if is_valid:
            report += "配置文件符合JeecgBoot API要求\n"
            report += "核心验证通过：orderNum连续性、系统字段、表名格式、数据字典字段\n"
            
            # 显示使用的数据字典
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                used_dicts = self._extract_used_dictionary_codes(config)
                if used_dicts:
                    report += f"\n使用的数据字典 ({len(used_dicts)}个):\n"
                    for dict_code in sorted(used_dicts):
                        detail = dict_result['dict_details'].get(dict_code, {})
                        dict_name = detail.get('dictName', '未知')
                        report += f"  • {dict_code} -> {dict_name}\n"
            except Exception:
                pass
                
        else:
            report += f"发现 {len(errors)} 个问题:\n\n"
            
            # 按严重程度分类错误
            critical_errors = [e for e in errors if e.startswith('❌')]
            warning_errors = [e for e in errors if e.startswith('⚠️')]
            other_errors = [e for e in errors if not e.startswith(('❌', '⚠️'))]
            
            if critical_errors:
                report += "【严重错误 - 必须修复】:\n"
                for i, error in enumerate(critical_errors, 1):
                    report += f"{i}. {error}\n"
                report += "\n"
            
            if other_errors:
                report += "【其他错误】:\n"
                for i, error in enumerate(other_errors, 1):
                    report += f"{i}. {error}\n"
                report += "\n"
            
            if warning_errors:
                report += "【建议优化】:\n"
                for i, error in enumerate(warning_errors, 1):
                    report += f"{i}. {error}\n"
                report += "\n"

            report += "修复建议:\n"
            report += "1. 【数据字典】确保所有dictField都存在于Code_Gen_DICT.json中\n"
            report += "2. 【orderNum】确保从0开始连续递增\n"
            report += "3. 【系统字段】检查前7个系统字段是否正确\n"
            report += "4. 【表名格式】验证表名格式: module_submodule_entity\n"
            report += "5. 【字段长度】确保dbFieldName长度不超过32字符\n"
            report += "6. 【字段格式】检查字段名格式: 小写字母开头，可包含数字和下划线\n"

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

        # 添加可用数据字典列表
        if dict_result['success'] and dict_result['dict_codes']:
            report += f"\n可用数据字典编码列表 (共{len(dict_result['dict_codes'])}个):\n"
            report += "=" * 50 + "\n"
            
            # 按字母顺序分组显示
            sorted_codes = sorted(dict_result['dict_codes'])
            for i in range(0, len(sorted_codes), 4):  # 每行4个
                line_codes = sorted_codes[i:i+4]
                formatted_codes = []
                for code in line_codes:
                    detail = dict_result['dict_details'].get(code, {})
                    dict_name = detail.get('dictName', '未知')
                    formatted_codes.append(f"{code:15} ({dict_name[:10]}...)" if len(dict_name) > 10 else f"{code:15} ({dict_name})")
                report += "  " + " | ".join(formatted_codes) + "\n"

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

            # 验证子表表名格式 - 严格三段式
            table_name = sub_table.get('tableName', '')
            if table_name:
                # 严格三段式验证
                segments = table_name.split('_')
                if len(segments) != 3:
                    errors.append(f"❌ subList[{i}]表名格式错误: '{table_name}' 必须严格为三段式格式 {{MODULE_NAME}}_{{SUBMODULE_NAME}}_{{ENTITY_SUFFIX}}，当前为{len(segments)}段式")
                else:
                    module_name, submodule_name, entity_suffix = segments
                    
                    # 验证各段格式
                    if not re.match(r'^[a-z]+$', module_name):
                        errors.append(f"❌ subList[{i}] MODULE_NAME格式错误: '{module_name}' 必须为纯小写字母")
                    
                    if not re.match(r'^[a-z]+$', submodule_name):
                        errors.append(f"❌ subList[{i}] SUBMODULE_NAME格式错误: '{submodule_name}' 必须为纯小写字母")
                    
                    if not re.match(r'^[a-z0-9]+$', entity_suffix):
                        errors.append(f"❌ subList[{i}] ENTITY_SUFFIX格式错误: '{entity_suffix}' 必须为小写字母和数字组合")
                
                # 检查禁用的四段式表名
                invalid_patterns = [
                    "crm_customer_customer_profile",
                    "education_student_student_info", 
                    "finance_invoice_invoice_header"
                ]
                
                if table_name in invalid_patterns:
                    errors.append(f"❌ subList[{i}]禁止使用四段式表名: '{table_name}' 应简化为三段式")

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
                
                # ✅ 新增：验证简洁格式
                main_entity = config.get('head', {}).get('business_entity', '')
                if main_entity and entity_name == main_entity:
                    errors.append(f"subList[{i}]实体名不能与主表实体名相同: {entity_name}")
                elif main_entity and entity_name.startswith(main_entity):
                    errors.append(f"subList[{i}]实体名应使用简洁格式: {entity_name}，推荐去除主表前缀")
                    errors.append(f"⚠️ 统一使用简洁格式，避免复合命名")

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

    def validate_dictionary_fields(self, config: Dict) -> Tuple[bool, List[str]]:
        """验证数据字典字段配置 - 严格校验模式"""
        errors = []
        fields = config.get('fields', [])
        
        # 严格加载系统字典编码列表和详细信息
        dict_validation_result = self._load_and_validate_dict_codes()
        if not dict_validation_result['success']:
            errors.append(f"🚨 无法加载Code_Gen_DICT.json文件: {dict_validation_result['error']}")
            return False, errors
        
        available_dict_codes = dict_validation_result['dict_codes']
        dict_details = dict_validation_result['dict_details']
        
        # 记录使用的字典编码统计
        used_dict_codes = set()

        for i, field in enumerate(fields):
            field_name = field.get('dbFieldName', '')
            dict_field = field.get('dictField', '')
            
            # 如果字段配置了数据字典
            if dict_field:
                used_dict_codes.add(dict_field)
                
                # 1. 【严格校验】验证数据字典编码是否存在 - 这是最关键的校验
                if dict_field not in available_dict_codes:
                    errors.append(f"❌ 数据字典字段{i+1}({field_name})使用了非法的dictField: '{dict_field}'")
                    errors.append(f"   该字典编码不存在于Code_Gen_DICT.json中，系统拒绝此配置！")
                    errors.append(f"   请使用以下合法的字典编码之一:")
                    
                    # 按字母顺序显示所有可用的字典编码
                    sorted_codes = sorted(available_dict_codes)
                    for j in range(0, len(sorted_codes), 5):  # 每行显示5个
                        codes_line = sorted_codes[j:j+5]
                        errors.append(f"     {', '.join(codes_line)}")
                    
                    # 显示字典详情（前10个作为参考）
                    if dict_details:
                        errors.append(f"   字典编码详细信息（示例）:")
                        for code in sorted_codes[:10]:
                            detail = dict_details.get(code, {})
                            dict_name = detail.get('dictName', '未知')
                            errors.append(f"     '{code}' -> {dict_name}")
                        if len(sorted_codes) > 10:
                            errors.append(f"     ... 共{len(sorted_codes)}个可用字典编码")
                else:
                    # 显示匹配的字典信息（用于确认）
                    detail = dict_details.get(dict_field, {})
                    dict_name = detail.get('dictName', '未知')
                    # 这里不输出成功信息，避免日志过多

                # 2. 【严格校验】验证fieldShowType必须是list
                field_show_type = field.get('fieldShowType', '')
                if field_show_type != 'list':
                    errors.append(f"❌ 数据字典字段{i+1}({field_name})的fieldShowType必须是'list'，当前值: '{field_show_type}'")
                    errors.append(f"   数据字典字段必须使用下拉选择控件")

                # 3. 【严格校验】验证queryShowType必须是list  
                query_show_type = field.get('queryShowType', '')
                if query_show_type != 'list':
                    errors.append(f"❌ 数据字典字段{i+1}({field_name})的queryShowType必须是'list'，当前值: '{query_show_type}'")
                    errors.append(f"   数据字典字段的查询条件必须使用下拉选择控件")

                # 4. 【严格校验】验证dbType必须是int
                db_type = field.get('dbType', '')
                if db_type != 'int':
                    errors.append(f"❌ 数据字典字段{i+1}({field_name})的dbType必须是'int'，当前值: '{db_type}'")
                    errors.append(f"   数据字典字段存储的是整数键值，如：1-男，2-女")

                # 5. 【严格校验】验证queryDictField必须与dictField一致
                query_dict_field = field.get('queryDictField', '')
                if query_dict_field and query_dict_field != dict_field:
                    errors.append(f"❌ 数据字典字段{i+1}({field_name})的queryDictField必须与dictField一致")
                    errors.append(f"   dictField: '{dict_field}', queryDictField: '{query_dict_field}'")
                elif not query_dict_field:
                    errors.append(f"❌ 数据字典字段{i+1}({field_name})缺少queryDictField配置")
                    errors.append(f"   queryDictField应该设置为: '{dict_field}'")

                # 6. 【规范校验】验证dictTable和dictText应该为空（使用系统默认）
                dict_table = field.get('dictTable', '')
                if dict_table:
                    errors.append(f"⚠️ 数据字典字段{i+1}({field_name})的dictTable应该为空字符串，当前值: '{dict_table}'")
                    errors.append(f"   建议使用系统默认的字典表配置")

                dict_text = field.get('dictText', '')
                if dict_text:
                    errors.append(f"⚠️ 数据字典字段{i+1}({field_name})的dictText应该为空字符串，当前值: '{dict_text}'")
                    errors.append(f"   建议使用系统默认的显示逻辑")

                # 7. 【规范校验】验证查询模式
                query_mode = field.get('queryMode', '')
                if query_mode not in ['single', 'like']:
                    errors.append(f"⚠️ 数据字典字段{i+1}({field_name})的queryMode建议使用'single'，当前值: '{query_mode}'")
                    errors.append(f"   数据字典字段通常使用精确匹配查询")

                # 8. 【规范校验】验证显示配置
                is_show_form = field.get('isShowForm', '0')
                is_show_list = field.get('isShowList', '0')
                if is_show_form == '0' and is_show_list == '0':
                    errors.append(f"⚠️ 数据字典字段{i+1}({field_name})应该至少在表单或列表中显示")

                # 9. 【规范校验】验证必填配置
                field_must_input = field.get('fieldMustInput', '0')
                if field_must_input == '0':
                    # 对于重要字典字段给出建议
                    important_fields = ['sex', 'status', 'user_status']
                    if dict_field in important_fields:
                        errors.append(f"⚠️ 数据字典字段{i+1}({field_name})建议设为必填，dictField: '{dict_field}'")

        # 输出字典使用统计
        if used_dict_codes:
            print(f"📊 本次配置使用了 {len(used_dict_codes)} 个数据字典: {', '.join(sorted(used_dict_codes))}")

        return len(errors) == 0, errors

    def _load_and_validate_dict_codes(self) -> Dict:
        """严格加载和验证Code_Gen_DICT.json文件中的所有数据字典"""
        import os
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dict_file = os.path.join(current_dir, "Code_Gen_DICT.json")
        
        # 检查文件是否存在
        if not os.path.exists(dict_file):
            return {
                'success': False,
                'error': f'Code_Gen_DICT.json文件不存在: {dict_file}',
                'dict_codes': [],
                'dict_details': {}
            }
        
        try:
            # 读取并解析JSON文件
            with open(dict_file, 'r', encoding='utf-8') as f:
                dict_data = json.load(f)
            
            # 验证文件格式
            if not isinstance(dict_data, list):
                return {
                    'success': False,
                    'error': 'Code_Gen_DICT.json文件格式错误，应该是JSON数组',
                    'dict_codes': [],
                    'dict_details': {}
                }
            
            # 完全遍历所有字典项
            dict_codes = []
            dict_details = {}
            invalid_items = []
            
            for i, item in enumerate(dict_data):
                if not isinstance(item, dict):
                    invalid_items.append(f"索引{i}: 不是有效的字典对象")
                    continue
                
                # 检查必需字段
                if 'dictCode' not in item:
                    invalid_items.append(f"索引{i}: 缺少dictCode字段")
                    continue
                
                if 'dictName' not in item:
                    invalid_items.append(f"索引{i}: 缺少dictName字段")
                    continue
                
                dict_code = item['dictCode']
                dict_name = item['dictName']
                
                # 验证dictCode格式
                if not dict_code or not isinstance(dict_code, str):
                    invalid_items.append(f"索引{i}: dictCode无效: '{dict_code}'")
                    continue
                
                # 验证dictCode唯一性
                if dict_code in dict_codes:
                    invalid_items.append(f"索引{i}: dictCode重复: '{dict_code}'")
                    continue
                
                # 收集有效的字典信息
                dict_codes.append(dict_code)
                dict_details[dict_code] = {
                    'dictName': dict_name,
                    'dictCode': dict_code,
                    'id': item.get('id', ''),
                    'type': item.get('type', 0),
                    'description': item.get('description', ''),
                    'createBy': item.get('createBy', ''),
                    'createTime': item.get('createTime', ''),
                    'index': i
                }
            
            # 构建返回结果
            result = {
                'success': True,
                'dict_codes': dict_codes,
                'dict_details': dict_details,
                'total_items': len(dict_data),
                'valid_items': len(dict_codes),
                'invalid_items': len(invalid_items)
            }
            
            # 如果有无效项，添加警告信息
            if invalid_items:
                result['warnings'] = invalid_items
                print(f"⚠️  Code_Gen_DICT.json文件中发现 {len(invalid_items)} 个无效项:")
                for warning in invalid_items[:5]:  # 只显示前5个
                    print(f"   {warning}")
                if len(invalid_items) > 5:
                    print(f"   ... 还有 {len(invalid_items) - 5} 个无效项")
            
            print(f"✅ 成功加载Code_Gen_DICT.json文件: 共{result['total_items']}项，有效{result['valid_items']}项")
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Code_Gen_DICT.json文件JSON格式错误: {str(e)}',
                'dict_codes': [],
                'dict_details': {}
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'Code_Gen_DICT.json文件不存在: {dict_file}',
                'dict_codes': [],
                'dict_details': {}
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'读取Code_Gen_DICT.json文件时发生未知错误: {str(e)}',
                'dict_codes': [],
                'dict_details': {}
            }

    def _load_available_dict_codes(self) -> List[str]:
        """保留兼容性的简单方法"""
        result = self._load_and_validate_dict_codes()
        return result.get('dict_codes', [])

    def _extract_used_dictionary_codes(self, config: Dict) -> List[str]:
        """提取配置中使用的数据字典编码"""
        used_dict_codes = []
        fields = config.get('fields', [])
        
        for field in fields:
            dict_field = field.get('dictField', '')
            if dict_field and dict_field not in used_dict_codes:
                used_dict_codes.append(dict_field)
        
        return used_dict_codes

    def show_available_dictionaries(self):
        """显示系统中所有可用的数据字典"""
        dict_result = self._load_and_validate_dict_codes()
        
        if not dict_result['success']:
            print(f"❌ 无法加载数据字典: {dict_result['error']}")
            return
        
        dict_codes = dict_result['dict_codes']
        dict_details = dict_result['dict_details']
        
        print("\n" + "="*60)
        print(f"JeecgBoot 系统数据字典列表 (共 {len(dict_codes)} 个)")
        print("="*60)
        
        # 按分类显示
        categories = {}
        for code in dict_codes:
            detail = dict_details.get(code, {})
            dict_name = detail.get('dictName', '未知')
            
            # 简单分类逻辑
            if any(keyword in dict_name for keyword in ['状态', 'status']):
                category = '状态类'
            elif any(keyword in dict_name for keyword in ['类型', 'type', '分类']):
                category = '类型分类'
            elif any(keyword in dict_name for keyword in ['权限', 'perms', '角色']):
                category = '权限管理'
            elif any(keyword in dict_name for keyword in ['消息', 'msg', '通知', '公告']):
                category = '消息通知'
            elif any(keyword in dict_name for keyword in ['用户', 'user', '性别']):
                category = '用户信息'
            else:
                category = '其他'
            
            if category not in categories:
                categories[category] = []
            categories[category].append((code, dict_name))
        
        # 显示各分类
        for category, items in sorted(categories.items()):
            print(f"\n【{category}】({len(items)}个):")
            for code, name in sorted(items):
                print(f"  • {code:20} -> {name}")
        
        print(f"\n总计: {len(dict_codes)} 个数据字典编码")
        print("="*60)

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
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 Code_Gen_Validator.py <config_file.json>           # 验证配置文件")
        print("  python3 Code_Gen_Validator.py --show-dicts                # 显示所有可用数据字典")
        print("  python3 Code_Gen_Validator.py --help                      # 显示帮助信息")
        sys.exit(1)

    validator = CodeGenValidator()
    
    # 处理命令行参数
    if sys.argv[1] == '--show-dicts':
        print("正在加载系统数据字典...")
        validator.show_available_dictionaries()
        sys.exit(0)
    elif sys.argv[1] == '--help':
        print("JeecgBoot 代码生成配置验证器")
        print("="*50)
        print("功能说明:")
        print("  1. 验证JSON配置文件的格式和内容正确性")
        print("  2. 严格校验数据字典字段是否在系统范围内")
        print("  3. 检查orderNum连续性、系统字段、表名格式等")
        print("  4. 提供详细的错误报告和修复建议")
        print()
        print("使用方法:")
        print("  python3 Code_Gen_Validator.py config.json    # 验证配置文件")
        print("  python3 Code_Gen_Validator.py --show-dicts   # 查看数据字典")
        print()
        print("数据字典严格校验:")
        print("  • 所有dictField必须存在于Code_Gen_DICT.json中")
        print("  • 不存在的字典编码将导致验证失败")
        print("  • 数据字典字段必须使用正确的配置格式")
        sys.exit(0)
    else:
        # 验证配置文件
        config_file = sys.argv[1]
        print(f"正在验证JSON配置文件: {config_file}")
        print("="*60)
        
        report = validator.generate_validation_report(config_file)
        print(report)

        is_valid, _ = validator.validate_config(config_file)
        
        if is_valid:
            print("\n✅ 配置文件验证通过，可以提交到JeecgBoot系统！")
        else:
            print("\n❌ 配置文件验证失败，请根据上述报告修复问题后重新验证。")
            
        sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
