#!/usr/bin/env python3
"""
ContextDev Configuration Validation Tool v4.0
==============================================

验证ContextDev v4.0重构架构的配置完整性和一致性
- 验证目录结构完整性
- 验证版本号一致性
- 验证配置文件引用完整性
- 验证专家文件格式正确性
- 生成验证报告

Author: ContextDev架构团队
Version: 4.0.0
Date: 2025-07-27
"""

import os
import re
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ContextDevConfigValidator:
    """ContextDev v4.0 配置验证器"""
    
    def __init__(self):
        self.project_root = Path("/Users/admin/Work/Github/JeecgBoot")
        self.contextdev_path = self.project_root / "ContextDev"
        self.experts_path = self.contextdev_path / "experts"
        self.shared_path = self.experts_path / "_shared"
        self.workflows_path = self.contextdev_path / "workflows"
        self.templates_path = self.contextdev_path / "templates"
        
        self.expected_version = "v4.0.0"
        self.validation_results = {}
        
    def validate_directory_structure(self) -> Dict:
        """验证目录结构完整性"""
        print("🏗️  验证目录结构完整性...")
        
        results = {
            "status": "success",
            "issues": [],
            "directories": {}
        }
        
        required_directories = {
            "experts": self.experts_path,
            "experts/_shared": self.shared_path,
            "workflows": self.workflows_path,
            "templates": self.templates_path
        }
        
        for dir_name, dir_path in required_directories.items():
            if dir_path.exists():
                print(f"   ✅ {dir_name}/ 目录存在")
                results["directories"][dir_name] = {
                    "exists": True,
                    "path": str(dir_path),
                    "file_count": len(list(dir_path.glob("*")))
                }
            else:
                print(f"   ❌ {dir_name}/ 目录缺失")
                results["issues"].append(f"目录缺失: {dir_name}")
                results["directories"][dir_name] = {
                    "exists": False,
                    "path": str(dir_path)
                }
                results["status"] = "failed"
        
        # 验证过时目录已清理
        obsolete_directories = [
            self.contextdev_path / "personas",
            self.contextdev_path / "requirements_baseline" / "global_configs" / "experts",
            self.templates_path / "composite_templates"
        ]
        
        for obs_dir in obsolete_directories:
            if obs_dir.exists():
                print(f"   ⚠️  过时目录仍存在: {obs_dir.name}")
                results["issues"].append(f"过时目录未清理: {obs_dir}")
                results["status"] = "warning" if results["status"] == "success" else results["status"]
            else:
                print(f"   ✅ 过时目录已清理: {obs_dir.name}")
        
        return results
    
    def validate_expert_files(self) -> Dict:
        """验证专家文件完整性"""
        print("\n👥 验证专家文件完整性...")
        
        results = {
            "status": "success",
            "issues": [],
            "experts": {}
        }
        
        expected_experts = [
            "baseline_manager.md",
            "requirements_analyst.md", 
            "system_architect.md",
            "task_planner.md",
            "code_developer.md",
            "quality_tester.md"
        ]
        
        for expert_file in expected_experts:
            expert_path = self.experts_path / expert_file
            expert_id = expert_file.replace('.md', '')
            
            if expert_path.exists():
                print(f"   ✅ {expert_file} 存在")
                
                # 验证文件内容格式
                try:
                    with open(expert_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查YAML前置数据
                    yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if yaml_match:
                        yaml_data = yaml.safe_load(yaml_match.group(1))
                        results["experts"][expert_id] = {
                            "exists": True,
                            "yaml_valid": True,
                            "name": yaml_data.get("name"),
                            "description": yaml_data.get("description"),
                            "color": yaml_data.get("color"),
                            "file_size": expert_path.stat().st_size
                        }
                    else:
                        print(f"   ⚠️  {expert_file} 缺少YAML前置数据")
                        results["issues"].append(f"{expert_file} 缺少YAML前置数据")
                        results["experts"][expert_id] = {
                            "exists": True,
                            "yaml_valid": False
                        }
                        results["status"] = "warning" if results["status"] == "success" else results["status"]
                        
                except Exception as e:
                    print(f"   ❌ {expert_file} 文件读取错误: {str(e)}")
                    results["issues"].append(f"{expert_file} 读取错误: {str(e)}")
                    results["status"] = "failed"
                    
            else:
                print(f"   ❌ {expert_file} 缺失")
                results["issues"].append(f"专家文件缺失: {expert_file}")
                results["experts"][expert_id] = {"exists": False}
                results["status"] = "failed"
        
        return results
    
    def validate_shared_configs(self) -> Dict:
        """验证共享配置文件"""
        print("\n🔧 验证共享配置文件...")
        
        results = {
            "status": "success", 
            "issues": [],
            "configs": {}
        }
        
        expected_configs = {
            "expert_base_template.md": "markdown",
            "jeecgboot_constraints.yaml": "yaml",
            "quality_standards.yaml": "yaml", 
            "template_patterns.yaml": "yaml",
            "work_principles.yaml": "yaml"
        }
        
        for config_file, file_type in expected_configs.items():
            config_path = self.shared_path / config_file
            
            if config_path.exists():
                print(f"   ✅ {config_file} 存在")
                
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 验证YAML格式
                    if file_type == "yaml":
                        yaml.safe_load(content)
                        
                    results["configs"][config_file] = {
                        "exists": True,
                        "valid": True,
                        "file_size": config_path.stat().st_size
                    }
                    
                except yaml.YAMLError as e:
                    print(f"   ❌ {config_file} YAML格式错误: {str(e)}")
                    results["issues"].append(f"{config_file} YAML格式错误")
                    results["configs"][config_file] = {
                        "exists": True,
                        "valid": False
                    }
                    results["status"] = "failed"
                    
                except Exception as e:
                    print(f"   ❌ {config_file} 读取错误: {str(e)}")
                    results["issues"].append(f"{config_file} 读取错误: {str(e)}")
                    results["status"] = "failed"
                    
            else:
                print(f"   ❌ {config_file} 缺失")
                results["issues"].append(f"共享配置缺失: {config_file}")
                results["configs"][config_file] = {"exists": False}
                results["status"] = "failed"
        
        return results
    
    def validate_version_consistency(self) -> Dict:
        """验证版本号一致性"""
        print("\n🔢 验证版本号一致性...")
        
        results = {
            "status": "success",
            "issues": [],
            "versions": {}
        }
        
        # 检查所有配置文件的版本号
        files_to_check = []
        
        # 专家文件
        files_to_check.extend(self.experts_path.glob("*.md"))
        
        # 共享配置文件
        files_to_check.extend(self.shared_path.glob("*.md"))
        files_to_check.extend(self.shared_path.glob("*.yaml"))
        
        # 模板文件
        files_to_check.extend(self.templates_path.rglob("*.yaml"))
        
        # 工作流文件
        if self.workflows_path.exists():
            files_to_check.extend(self.workflows_path.glob("*.yaml"))
        
        # CLAUDE.md
        files_to_check.append(self.contextdev_path / "CLAUDE.md")
        
        version_pattern = re.compile(r'[vV]ersion:?\s*([vV]?\d+\.\d+\.\d+)')
        
        for file_path in files_to_check:
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                versions_found = version_pattern.findall(content)
                
                if versions_found:
                    for version in versions_found:
                        version = version.strip()
                        if not version.startswith('v'):
                            version = 'v' + version
                            
                        relative_path = str(file_path.relative_to(self.contextdev_path))
                        results["versions"][relative_path] = version
                        
                        if version != self.expected_version:
                            print(f"   ⚠️  {relative_path}: {version} (期望: {self.expected_version})")
                            results["issues"].append(f"版本不一致: {relative_path} = {version}")
                            results["status"] = "warning" if results["status"] == "success" else results["status"]
                        else:
                            print(f"   ✅ {relative_path}: {version}")
                else:
                    relative_path = str(file_path.relative_to(self.contextdev_path))
                    print(f"   ⚠️  {relative_path}: 无版本信息")
                    results["issues"].append(f"缺少版本信息: {relative_path}")
                    results["status"] = "warning" if results["status"] == "success" else results["status"]
                    
            except Exception as e:
                print(f"   ❌ {file_path}: 读取错误 - {str(e)}")
                results["issues"].append(f"文件读取错误: {file_path}")
                results["status"] = "failed"
        
        return results
    
    def validate_config_references(self) -> Dict:
        """验证配置文件引用完整性"""
        print("\n🔗 验证配置文件引用完整性...")
        
        results = {
            "status": "success",
            "issues": [],
            "references": {}
        }
        
        # 检查专家文件中的共享配置引用
        shared_ref_pattern = re.compile(r'\[.*?\]\(/_shared/(.*?)\)')
        
        for expert_file in self.experts_path.glob("*.md"):
            try:
                with open(expert_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                references = shared_ref_pattern.findall(content)
                expert_name = expert_file.name
                results["references"][expert_name] = []
                
                for ref in references:
                    ref_path = self.shared_path / ref
                    if ref_path.exists():
                        print(f"   ✅ {expert_name} → /_shared/{ref}")
                        results["references"][expert_name].append({
                            "reference": ref,
                            "exists": True
                        })
                    else:
                        print(f"   ❌ {expert_name} → /_shared/{ref} (不存在)")
                        results["issues"].append(f"引用缺失: {expert_name} → /_shared/{ref}")
                        results["references"][expert_name].append({
                            "reference": ref,
                            "exists": False
                        })
                        results["status"] = "failed"
                        
            except Exception as e:
                print(f"   ❌ {expert_file}: 引用检查错误 - {str(e)}")
                results["issues"].append(f"引用检查错误: {expert_file}")
                results["status"] = "failed"
        
        return results
    
    def generate_validation_report(self) -> Dict:
        """生成完整的验证报告"""
        print("\n📊 生成验证报告...")
        
        report = {
            "validation_info": {
                "version": "4.0.0",
                "validation_date": datetime.now().isoformat(),
                "expected_version": self.expected_version,
                "contextdev_path": str(self.contextdev_path)
            },
            "results": self.validation_results,
            "summary": {
                "total_checks": len(self.validation_results),
                "passed": sum(1 for r in self.validation_results.values() if r["status"] == "success"),
                "warnings": sum(1 for r in self.validation_results.values() if r["status"] == "warning"),
                "failures": sum(1 for r in self.validation_results.values() if r["status"] == "failed"),
                "overall_status": "success"
            }
        }
        
        # 计算总体状态
        if report["summary"]["failures"] > 0:
            report["summary"]["overall_status"] = "failed"
        elif report["summary"]["warnings"] > 0:
            report["summary"]["overall_status"] = "warning"
        
        # 收集所有问题
        all_issues = []
        for result in self.validation_results.values():
            all_issues.extend(result.get("issues", []))
        report["all_issues"] = all_issues
        
        # 保存报告
        report_file = self.contextdev_path / f"validation_report_v4.0_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 验证报告已保存: {report_file}")
        return report
    
    def run_validation(self) -> bool:
        """运行完整的配置验证"""
        print("=" * 70)
        print("ContextDev v4.0 Configuration Validation")
        print("=" * 70)
        
        # 执行各项验证
        self.validation_results["directory_structure"] = self.validate_directory_structure()
        self.validation_results["expert_files"] = self.validate_expert_files()
        self.validation_results["shared_configs"] = self.validate_shared_configs()
        self.validation_results["version_consistency"] = self.validate_version_consistency()
        self.validation_results["config_references"] = self.validate_config_references()
        
        # 生成报告
        report = self.generate_validation_report()
        
        # 输出总结
        print("\n" + "=" * 70)
        print("🎯 验证结果总结")
        print("=" * 70)
        
        summary = report["summary"]
        print(f"✅ 总体状态: {summary['overall_status'].upper()}")
        print(f"📊 检查项目: {summary['total_checks']}")
        print(f"✅ 通过: {summary['passed']}")
        print(f"⚠️  警告: {summary['warnings']}")  
        print(f"❌ 失败: {summary['failures']}")
        
        if report["all_issues"]:
            print(f"\n⚠️  发现问题 ({len(report['all_issues'])}):")
            for issue in report["all_issues"][:10]:  # 只显示前10个问题
                print(f"   • {issue}")
            if len(report["all_issues"]) > 10:
                print(f"   ... 还有 {len(report['all_issues']) - 10} 个问题")
        else:
            print("\n🎉 所有验证项目均通过！")
        
        return summary["overall_status"] in ["success", "warning"]


def main():
    """主程序入口"""
    try:
        validator = ContextDevConfigValidator()
        success = validator.run_validation()
        
        if success:
            print("\n✅ 配置验证完成！")
            sys.exit(0)
        else:
            print("\n❌ 配置验证发现关键问题")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断验证")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()