#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JeecgBoot CodeGen 高级验证器
专门针对AIGC生成的JSON配置文件进行严格验证
重点验证orderNum连续性和系统字段配置正确性

版本: 1.0
创建日期: 2025-07-28
适用版本: JeecgBoot 3.8.1+
"""

import json
import os
from typing import List, Dict, Any, Tuple


class AdvancedJSONValidator:
    """高级JSON配置验证器"""
    
    # 标准系统字段配置 (基于Code_Gen_Example.json)
    SYSTEM_FIELDS = [
        {
            "dbFieldName": "id",
            "orderNum": 0,
            "required_attrs": {
                "fieldMustInput": "0",
                "isReadOnly": "1",
                "dbIsNull": "0",
                "dbIsKey": "1"
            }
        },
        {
            "dbFieldName": "create_by",
            "orderNum": 1,
            "required_attrs": {
                "fieldMustInput": "1",
                "isReadOnly": "0",
                "dbIsNull": "0"
            }
        },
        {
            "dbFieldName": "create_time",
            "orderNum": 2,
            "required_attrs": {
                "fieldMustInput": "1",
                "isReadOnly": "0",
                "dbIsNull": "0"
            }
        },
        {
            "dbFieldName": "update_by",
            "orderNum": 3,
            "required_attrs": {
                "fieldMustInput": "0",
                "isReadOnly": "0",
                "dbIsNull": "1"
            }
        },
        {
            "dbFieldName": "update_time",
            "orderNum": 4,
            "required_attrs": {
                "fieldMustInput": "0",
                "isReadOnly": "0",
                "dbIsNull": "1"
            }
        },
        {
            "dbFieldName": "sys_org_code",
            "orderNum": 5,
            "required_attrs": {
                "fieldMustInput": "1",
                "isReadOnly": "0",
                "dbIsNull": "0"
            }
        },
        {
            "dbFieldName": "del_flag",
            "orderNum": 6,
            "required_attrs": {
                "fieldMustInput": "1",
                "isReadOnly": "0",
                "dbIsNull": "0"
            }
        }
    ]
    
    def __init__(self, config_file: str):
        """初始化验证器"""
        self.config_file = config_file
        self.errors = []
        self.warnings = []
        self.config_data = None
        
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_file):
                self.errors.append(f"配置文件不存在: {self.config_file}")
                return False
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON格式错误: {e}")
            return False
        except Exception as e:
            self.errors.append(f"文件读取错误: {e}")
            return False
    
    def validate_order_num_continuity(self) -> bool:
        """验证orderNum连续性 - 关键验证"""
        if not self.config_data or 'fields' not in self.config_data:
            self.errors.append("配置文件缺少fields数组")
            return False
            
        fields = self.config_data['fields']
        order_nums = []
        
        # 收集所有orderNum
        for i, field in enumerate(fields):
            if 'orderNum' not in field:
                self.errors.append(f"字段{i+1} ({field.get('dbFieldName', '未知')}) 缺少orderNum")
                continue
            order_nums.append((i, field['dbFieldName'], field['orderNum']))
        
        # 按orderNum排序
        order_nums.sort(key=lambda x: x[2])
        
        # 检查连续性
        for i, (field_index, field_name, order_num) in enumerate(order_nums):
            if order_num != i:
                self.errors.append(
                    f"❌ orderNum不连续: 字段'{field_name}' orderNum={order_num}, 期望={i}"
                )
                self.errors.append(
                    f"   位置: fields[{field_index}]"
                )
                self.errors.append(
                    f"   ⚠️  这会导致JeecgBoot API调用失败！"
                )
                return False
        
        print(f"✅ orderNum连续性验证通过: 0-{len(order_nums)-1} 连续递增")
        return True
    
    def validate_system_fields(self) -> bool:
        """验证系统字段配置"""
        if not self.config_data or 'fields' not in self.config_data:
            return False
            
        fields = self.config_data['fields']
        
        if len(fields) < 7:
            self.errors.append("字段数量不足，必须至少包含7个系统字段")
            return False
        
        # 验证前7个字段必须是标准系统字段
        for i, expected in enumerate(self.SYSTEM_FIELDS):
            if i >= len(fields):
                self.errors.append(f"缺少系统字段: {expected['dbFieldName']}")
                continue
                
            field = fields[i]
            
            # 验证字段名
            if field.get('dbFieldName') != expected['dbFieldName']:
                self.errors.append(
                    f"❌ 系统字段{i+1}错误: 期望'{expected['dbFieldName']}', 实际'{field.get('dbFieldName')}'"
                )
                continue
                
            # 验证orderNum
            if field.get('orderNum') != expected['orderNum']:
                self.errors.append(
                    f"❌ 系统字段'{expected['dbFieldName']}'的orderNum错误: 期望{expected['orderNum']}, 实际{field.get('orderNum')}"
                )
                
            # 验证关键属性
            for attr, expected_value in expected['required_attrs'].items():
                if str(field.get(attr)) != str(expected_value):
                    self.errors.append(
                        f"❌ 系统字段'{expected['dbFieldName']}'的{attr}错误: 期望'{expected_value}', 实际'{field.get(attr)}'"
                    )
        
        if not self.errors:
            print("✅ 系统字段配置验证通过")
            return True
        return False
    
    def validate_table_name(self) -> bool:
        """验证表名格式"""
        if not self.config_data or 'head' not in self.config_data:
            self.errors.append("配置文件缺少head部分")
            return False
            
        table_name = self.config_data['head'].get('tableName')
        if not table_name:
            self.errors.append("缺少tableName")
            return False
            
        # 验证4段式格式
        parts = table_name.split('_')
        if len(parts) != 4 or parts[0] != 'us':
            self.errors.append(
                f"❌ 表名格式错误: '{table_name}' 必须符合 'us_模块_子模块_实体' 4段式格式"
            )
            return False
            
        # 验证每部分都是小写
        for i, part in enumerate(parts[1:], 1):
            if not part.islower() or not part.replace('_', '').isalpha():
                self.errors.append(
                    f"❌ 表名第{i+1}部分'{part}'格式错误: 必须是全小写英文字母"
                )
                return False
        
        print(f"✅ 表名格式验证通过: {table_name}")
        return True
    
    def validate_business_entity(self) -> bool:
        """验证业务实体名称"""
        if not self.config_data or 'head' not in self.config_data:
            return False
            
        business_entity = self.config_data['head'].get('business_entity')
        if not business_entity:
            self.errors.append("缺少business_entity")
            return False
            
        # 验证PascalCase格式
        if not business_entity[0].isupper() or not business_entity.replace('_', '').isalnum():
            self.errors.append(
                f"❌ business_entity格式错误: '{business_entity}' 必须使用PascalCase格式"
            )
            return False
            
        # 检查是否使用了通用化名称
        forbidden_names = ['info', 'management', 'data', 'processing', 'handling']
        if business_entity.lower() in forbidden_names:
            self.errors.append(
                f"❌ business_entity不能使用通用化名称: '{business_entity}'"
            )
            self.warnings.append("建议使用具体的业务语义名称，如CustomerProfile, ProductCatalog等")
            return False
            
        print(f"✅ 业务实体名称验证通过: {business_entity}")
        return True
    
    def generate_validation_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("="*60)
        report.append("JeecgBoot JSON配置文件验证报告")
        report.append("="*60)
        report.append(f"文件: {self.config_file}")
        report.append(f"验证时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if self.errors:
            report.append("❌ 验证失败 - 发现以下错误:")
            report.append("-"*40)
            for i, error in enumerate(self.errors, 1):
                report.append(f"{i}. {error}")
            report.append("")
        
        if self.warnings:
            report.append("⚠️  警告信息:")
            report.append("-"*40)
            for i, warning in enumerate(self.warnings, 1):
                report.append(f"{i}. {warning}")
            report.append("")
        
        if not self.errors:
            report.append("✅ 验证通过 - 配置文件符合JeecgBoot API要求！")
            report.append("")
            report.append("📋 验证通过的项目:")
            report.append("  ✓ JSON格式正确")
            report.append("  ✓ orderNum严格连续")
            report.append("  ✓ 系统字段配置标准")
            report.append("  ✓ 表名格式符合规范")
            report.append("  ✓ 业务实体名称合规")
        else:
            report.append("🔧 修复建议:")
            report.append("  1. 使用Code_Gen_Example.json作为系统字段配置模板")
            report.append("  2. 确保orderNum从0开始严格连续递增")
            report.append("  3. 不要修改系统字段的任何配置")
            report.append("  4. 使用具体的业务语义名称作为business_entity")
        
        report.append("")
        report.append("="*60)
        
        return "\n".join(report)
    
    def validate_all(self) -> bool:
        """执行全面验证"""
        print(f"开始验证配置文件: {self.config_file}")
        print("-"*50)
        
        # 1. 加载配置文件
        if not self.load_config():
            return False
        
        # 2. 验证各个方面
        validations = [
            ("JSON格式和基本结构", lambda: self.config_data is not None),
            ("表名格式", self.validate_table_name),
            ("业务实体名称", self.validate_business_entity),
            ("orderNum连续性", self.validate_order_num_continuity),
            ("系统字段配置", self.validate_system_fields),
        ]
        
        all_passed = True
        for name, validator in validations:
            try:
                if validator():
                    print(f"✅ {name}: 通过")
                else:
                    print(f"❌ {name}: 失败")
                    all_passed = False
            except Exception as e:
                print(f"❌ {name}: 验证过程出错 - {e}")
                self.errors.append(f"{name}验证出错: {e}")
                all_passed = False
        
        print("-"*50)
        return all_passed


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JeecgBoot JSON配置文件高级验证器")
    parser.add_argument("config_file", help="要验证的JSON配置文件路径")
    parser.add_argument("--report", "-r", help="保存验证报告到文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建验证器并执行验证
    validator = AdvancedJSONValidator(args.config_file)
    is_valid = validator.validate_all()
    
    # 生成报告
    report = validator.generate_validation_report()
    
    if args.verbose or not is_valid:
        print("\n" + report)
    
    # 保存报告
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存到: {args.report}")
    
    # 返回状态码
    return 0 if is_valid else 1


if __name__ == "__main__":
    exit(main())