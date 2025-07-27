#!/usr/bin/env python3
"""
ContextDev 模板命名规范验证工具
版本: v1.0.0
用途: 全面验证模板文件和字段命名的规范性
"""

import re
import yaml
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ValidationResult:
    """验证结果数据结构"""
    file_path: str
    check_type: str
    severity: str  # error, warning, info
    message: str
    line_number: int = 0
    suggestion: str = ""

class NamingStandardsValidator:
    """ContextDev模板命名规范验证器"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "templates"
        self.results: List[ValidationResult] = []
        
        # 标准枚举值定义
        self.standard_enums = {
            "business_domain": [
                "core", "finance", "supply_chain", "customer_relationship",
                "human_resources", "inventory_management", "order_processing",
                "reporting_analytics", "workflow_management", "integration_services"
            ],
            "complexity_level": ["simple", "standard", "complex", "enterprise"],
            "status": ["draft", "reviewing", "approved", "released", "archived", "rejected", "suspended"],
            "priority": ["critical", "high", "medium", "low"],
            "requirement_type": ["functional", "non_functional", "business_rule", "constraint", "interface", "data_requirement"]
        }
        
        # 标准字段名模式
        self.standard_field_patterns = {
            "id_fields": re.compile(r"^[a-z]+_id$"),
            "name_fields": re.compile(r"^[a-z]+_name$"),
            "date_fields": re.compile(r"^[a-z]+_date$"),
            "version_fields": re.compile(r"^[a-z]+_version$"),
            "status_fields": re.compile(r"^[a-z]+_status$")
        }
    
    def add_result(self, file_path: str, check_type: str, severity: str, 
                   message: str, line_number: int = 0, suggestion: str = ""):
        """添加验证结果"""
        result = ValidationResult(
            file_path=str(file_path),
            check_type=check_type,
            severity=severity,
            message=message,
            line_number=line_number,
            suggestion=suggestion
        )
        self.results.append(result)
    
    def validate_file_naming(self):
        """验证文件命名规范"""
        print("🔍 检查文件命名规范...")
        
        yaml_files = list(self.templates_path.rglob("*.yaml"))
        yml_files = list(self.templates_path.rglob("*.yml"))
        
        # 检查.yml扩展名
        for file_path in yml_files:
            self.add_result(
                file_path, "file_naming", "error",
                f"使用了错误的扩展名 .yml，应使用 .yaml",
                suggestion="重命名文件扩展名为.yaml"
            )
        
        # 检查所有YAML文件的命名
        for file_path in yaml_files:
            filename = file_path.name
            
            # 检查文件名格式：小写字母、数字、下划线
            if not re.match(r'^[a-z][a-z0-9_]*\.yaml$', filename):
                issues = []
                if re.search(r'[A-Z]', filename):
                    issues.append("包含大写字母")
                if re.search(r'-', filename):
                    issues.append("包含中划线")
                if re.search(r'[^a-z0-9_.]', filename):
                    issues.append("包含特殊字符")
                
                self.add_result(
                    file_path, "file_naming", "error",
                    f"文件名格式不规范: {', '.join(issues)}",
                    suggestion="使用小写字母、数字和下划线，如: baseline_shared.yaml"
                )
            
            # 检查文件名长度
            base_name = filename.replace('.yaml', '')
            if len(base_name) < 3:
                self.add_result(
                    file_path, "file_naming", "warning",
                    f"文件名过短 ({len(base_name)}字符)，建议至少3个字符",
                    suggestion="使用更具描述性的文件名"
                )
            elif len(base_name) > 30:
                self.add_result(
                    file_path, "file_naming", "warning",
                    f"文件名过长 ({len(base_name)}字符)，建议不超过30个字符",
                    suggestion="简化文件名，使用缩写或分层"
                )
    
    def validate_directory_structure(self):
        """验证目录结构规范"""
        print("🔍 检查目录结构规范...")
        
        # 检查必需的共享基线文件
        required_shared_files = ["baseline_shared.yaml", "project_context.yaml", "data_types.yaml"]
        shared_path = self.templates_path / "shared"
        
        if not shared_path.exists():
            self.add_result(
                shared_path, "directory_structure", "error",
                "缺少共享基线目录 templates/shared/",
                suggestion="创建shared目录并添加必需文件"
            )
        else:
            for required_file in required_shared_files:
                file_path = shared_path / required_file
                if not file_path.exists():
                    self.add_result(
                        file_path, "directory_structure", "error",
                        f"缺少必需的共享基线文件: {required_file}",
                        suggestion=f"创建{required_file}文件"
                    )
        
        # 检查专家目录结构
        expert_dirs = ["requirements", "baseline", "architecture", "development", "testing"]
        for expert_dir in expert_dirs:
            expert_path = self.templates_path / expert_dir
            
            if not expert_path.exists():
                self.add_result(
                    expert_path, "directory_structure", "error",
                    f"缺少专家目录: {expert_dir}/",
                    suggestion=f"创建{expert_dir}目录"
                )
                continue
            
            # 检查必需的input.yaml和output.yaml
            for required_file in ["input.yaml", "output.yaml"]:
                file_path = expert_path / required_file
                if not file_path.exists():
                    self.add_result(
                        file_path, "directory_structure", "error",
                        f"专家目录{expert_dir}/缺少必需文件: {required_file}",
                        suggestion=f"在{expert_dir}/目录中创建{required_file}"
                    )
    
    def validate_yaml_syntax(self):
        """验证YAML语法"""
        print("🔍 检查YAML语法...")
        
        yaml_files = list(self.templates_path.rglob("*.yaml"))
        
        for file_path in yaml_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                # YAML语法正确，不需要记录
            except yaml.YAMLError as e:
                line_number = getattr(e, 'problem_mark', None)
                line_num = line_number.line + 1 if line_number else 0
                
                self.add_result(
                    file_path, "yaml_syntax", "error",
                    f"YAML语法错误: {str(e)}",
                    line_number=line_num,
                    suggestion="修复YAML语法错误，检查缩进和引号"
                )
            except Exception as e:
                self.add_result(
                    file_path, "yaml_syntax", "error",
                    f"文件读取错误: {str(e)}",
                    suggestion="检查文件编码和权限"
                )
    
    def validate_template_headers(self):
        """验证模板头部注释"""
        print("🔍 检查模板头部注释...")
        
        yaml_files = list(self.templates_path.rglob("*.yaml"))
        
        for file_path in yaml_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # 检查前10行是否包含标准头部注释
                header_content = '\n'.join(lines[:10])
                
                required_elements = ["版本:", "创建日期:"]
                missing_elements = []
                
                for element in required_elements:
                    if element not in header_content:
                        missing_elements.append(element)
                
                if missing_elements:
                    self.add_result(
                        file_path, "template_header", "warning",
                        f"缺少标准头部注释元素: {', '.join(missing_elements)}",
                        suggestion="添加包含版本和创建日期的头部注释"
                    )
                
            except Exception as e:
                self.add_result(
                    file_path, "template_header", "error",
                    f"无法读取文件检查头部: {str(e)}"
                )
    
    def validate_field_naming(self):
        """验证字段命名规范"""
        print("🔍 检查字段命名规范...")
        
        yaml_files = list(self.templates_path.rglob("*.yaml"))
        
        for file_path in yaml_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                
                self._check_field_names_recursive(content, file_path, "")
                
            except Exception as e:
                # YAML语法错误会在yaml_syntax检查中处理
                pass
    
    def _check_field_names_recursive(self, obj: Any, file_path: Path, path: str):
        """递归检查字段名"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # 检查字段命名格式
                if not re.match(r'^[a-z][a-z0-9_]*$', key):
                    issues = []
                    if re.search(r'[A-Z]', key):
                        issues.append("包含大写字母")
                    if re.search(r'-', key):
                        issues.append("包含中划线")
                    if re.search(r'[^a-z0-9_]', key):
                        issues.append("包含特殊字符")
                    
                    self.add_result(
                        file_path, "field_naming", "error",
                        f"字段名格式不规范 '{key}': {', '.join(issues)}",
                        suggestion="使用小写字母、数字和下划线，如: project_id"
                    )
                
                # 检查字段名长度
                if len(key) < 2:
                    self.add_result(
                        file_path, "field_naming", "warning",
                        f"字段名过短 '{key}' ({len(key)}字符)",
                        suggestion="使用更具描述性的字段名"
                    )
                elif len(key) > 40:
                    self.add_result(
                        file_path, "field_naming", "warning",
                        f"字段名过长 '{key}' ({len(key)}字符)",
                        suggestion="简化字段名或使用缩写"
                    )
                
                # 递归检查子对象
                self._check_field_names_recursive(value, file_path, current_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._check_field_names_recursive(item, file_path, f"{path}[{i}]")
    
    def validate_enum_values(self):
        """验证枚举值使用"""
        print("🔍 检查枚举值标准...")
        
        yaml_files = list(self.templates_path.rglob("*.yaml"))
        
        for file_path in yaml_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                
                self._check_enum_values_recursive(content, file_path, "")
                
            except Exception as e:
                pass
    
    def _check_enum_values_recursive(self, obj: Any, file_path: Path, path: str):
        """递归检查枚举值"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # 检查已知的枚举字段
                for enum_key, valid_values in self.standard_enums.items():
                    if key.endswith(enum_key) or key == enum_key:
                        if isinstance(value, str) and value and value not in valid_values:
                            self.add_result(
                                file_path, "enum_values", "warning",
                                f"字段 '{key}' 使用了非标准枚举值 '{value}'",
                                suggestion=f"建议使用标准值: {', '.join(valid_values)}"
                            )
                
                self._check_enum_values_recursive(value, file_path, current_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._check_enum_values_recursive(item, file_path, f"{path}[{i}]")
    
    def validate_reference_format(self):
        """验证引用格式"""
        print("🔍 检查模板引用格式...")
        
        yaml_files = list(self.templates_path.rglob("*.yaml"))
        
        for file_path in yaml_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # 检查引用路径格式
                for line_num, line in enumerate(lines, 1):
                    # 查找形如 "../path/file.yaml#/anchor" 的引用
                    ref_matches = re.finditer(r'"(\.\./[^/]+/[^"]+\.yaml(?:#/[^"]+)?)"', line)
                    
                    for match in ref_matches:
                        ref_path = match.group(1)
                        
                        # 检查引用格式是否符合标准
                        if not re.match(r'^\.\./[a-z_]+/[a-z_]+\.yaml(?:#/[a-z_/]+)?$', ref_path):
                            self.add_result(
                                file_path, "reference_format", "warning",
                                f"引用路径格式可能不规范: {ref_path}",
                                line_number=line_num,
                                suggestion="使用标准格式: ../layer/file.yaml#/anchor"
                            )
                
                # 检查$ref格式的内部引用
                internal_refs = re.finditer(r'\$ref:([^"]+)', content)
                for match in internal_refs:
                    ref_value = match.group(1)
                    if not re.match(r'^[a-z_]+\.[a-z_]+(?:\.[a-z_]+)*$', ref_value):
                        self.add_result(
                            file_path, "reference_format", "warning",
                            f"内部引用格式可能不规范: $ref:{ref_value}",
                            suggestion="使用标准格式: $ref:source.path.field"
                        )
                        
            except Exception as e:
                pass
    
    def generate_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        errors = [r for r in self.results if r.severity == "error"]
        warnings = [r for r in self.results if r.severity == "warning"]
        
        # 按检查类型分组统计
        check_type_stats = {}
        for result in self.results:
            check_type = result.check_type
            if check_type not in check_type_stats:
                check_type_stats[check_type] = {"errors": 0, "warnings": 0}
            check_type_stats[check_type][result.severity + "s"] += 1
        
        # 按文件分组统计
        file_stats = {}
        for result in self.results:
            file_path = result.file_path
            if file_path not in file_stats:
                file_stats[file_path] = {"errors": 0, "warnings": 0}
            file_stats[file_path][result.severity + "s"] += 1
        
        yaml_file_count = len(list(self.templates_path.rglob("*.yaml")))
        
        report = {
            "execution_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_files_checked": yaml_file_count,
                "total_issues": len(self.results),
                "errors": len(errors),
                "warnings": len(warnings),
                "check_passed": len(errors) == 0
            },
            "check_type_statistics": check_type_stats,
            "file_statistics": file_stats,
            "detailed_results": [asdict(r) for r in self.results]
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """打印验证结果摘要"""
        summary = report["summary"]
        
        print(f"\n{'='*60}")
        print("📋 验证结果摘要")
        print('='*60)
        
        print(f"📊 统计信息:")
        print(f"   - 检查的YAML文件总数: {summary['total_files_checked']}")
        print(f"   - 发现的问题总数: {summary['total_issues']}")
        print(f"   - 错误数量: {summary['errors']}")
        print(f"   - 警告数量: {summary['warnings']}")
        
        # 按检查类型显示统计
        print(f"\n🔍 各检查项统计:")
        for check_type, stats in report["check_type_statistics"].items():
            print(f"   - {check_type}: {stats['errors']}错误, {stats['warnings']}警告")
        
        # 显示错误详情
        if summary['errors'] > 0:
            print(f"\n🚨 错误详情:")
            errors = [r for r in report["detailed_results"] if r["severity"] == "error"]
            for error in errors[:10]:  # 只显示前10个错误
                line_info = f":{error['line_number']}" if error['line_number'] > 0 else ""
                print(f"   ❌ {error['file_path']}{line_info}")
                print(f"      {error['message']}")
                if error['suggestion']:
                    print(f"      💡 建议: {error['suggestion']}")
            
            if len(errors) > 10:
                print(f"   ... 还有 {len(errors) - 10} 个错误 (详见完整报告)")
        
        # 总结
        if summary['check_passed']:
            print(f"\n🎉 所有关键命名规范检查通过！")
        else:
            print(f"\n⚠️  发现 {summary['errors']} 个错误，需要修复")
        
        if summary['warnings'] > 0:
            print(f"ℹ️  发现 {summary['warnings']} 个警告，建议优化")
    
    def run_validation(self) -> bool:
        """运行完整验证流程"""
        print("🚀 开始ContextDev模板命名规范验证...")
        print(f"检查目录: {self.templates_path}")
        
        if not self.templates_path.exists():
            print(f"❌ 模板目录不存在: {self.templates_path}")
            return False
        
        # 执行各项检查
        self.validate_file_naming()
        self.validate_directory_structure()
        self.validate_yaml_syntax()
        self.validate_template_headers()
        self.validate_field_naming()
        self.validate_enum_values()
        self.validate_reference_format()
        
        # 生成和显示报告
        report = self.generate_report()
        self.print_summary(report)
        
        # 导出详细报告
        report_path = self.base_path / "scripts" / "naming_standards_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 详细报告已导出: {report_path}")
        print(f"📚 完整规范文档: TEMPLATE_NAMING_STANDARDS.md")
        
        return report["summary"]["check_passed"]

def main():
    """主函数"""
    validator = NamingStandardsValidator()
    success = validator.run_validation()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())