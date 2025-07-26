#!/usr/bin/env python3
"""
ContextDev Agents Installation Script v4.0 (Fully Refactored Architecture)
==========================================================================

将ContextDev/experts/目录下的专业化JeecgBoot专家转换并安装到.claude/agents/目录
支持新的统一架构、共享配置体系、版本管理、自动验证等功能

Architecture Changes in v4.0:
- experts/ 目录替代 personas/ 目录 (统一专家配置源)
- experts/_shared/ 共享配置体系 (DRY原则)
- workflows/ 工作流配置 (替代composite_templates)
- 统一版本管理 v4.0.0
- 配置验证和质量保证

Author: ContextDev架构团队
Version: 4.0.0 (Fully Refactored Architecture)
Date: 2025-07-27
"""

import os
import sys
import json
import yaml
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ContextDevAgentInstaller:
    """ContextDev专家代理安装器 v4.0 (全新重构架构)"""
    
    def __init__(self):
        self.project_root = Path("/Users/admin/Work/Github/JeecgBoot")
        self.contextdev_path = self.project_root / "ContextDev"
        self.experts_path = self.contextdev_path / "experts"  # 新架构：experts/目录
        self.shared_path = self.experts_path / "_shared"      # 新架构：experts/_shared/
        self.workflows_path = self.contextdev_path / "workflows"  # 新架构：workflows/目录
        self.claude_agents_path = self.project_root / ".claude" / "agents"
        
        # v4.0 专家映射配置 (统一架构)
        self.expert_mapping = {
            "baseline_manager": {
                "name": "baseline_manager",
                "color": "red",
                "display_name": "需求基线管理专家",
                "category": "baseline_management",
                "priority": 1,
                "description": "需求基线全生命周期管理和专家协作统筹"
            },
            "requirements_analyst": {
                "name": "requirements_analyst",
                "color": "green",
                "display_name": "需求分析专家",
                "category": "business_analysis",
                "priority": 2,
                "description": "基于需求基线驱动的业务需求分析"
            },
            "system_architect": {
                "name": "system_architect", 
                "color": "blue",
                "display_name": "系统架构专家",
                "category": "technical_design",
                "priority": 3,
                "description": "JeecgBoot系统架构设计和技术选型"
            },
            "task_planner": {
                "name": "task_planner",
                "color": "orange", 
                "display_name": "任务规划专家",
                "category": "project_management",
                "priority": 4,
                "description": "开发任务分解和项目规划管理"
            },
            "code_developer": {
                "name": "code_developer",
                "color": "purple",
                "display_name": "代码开发专家", 
                "category": "development",
                "priority": 5,
                "description": "JeecgBoot代码开发和CodeGen系统应用"
            },
            "quality_tester": {
                "name": "quality_tester",
                "color": "lightblue",
                "display_name": "质量测试专家",
                "category": "quality_assurance",
                "priority": 6,
                "description": "功能测试、性能测试和质量保证"
            }
        }
        
        # v4.0 架构重构信息
        self.architecture_info = {
            "version": "4.0.0",
            "refactor_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "architecture_changes": [
                "统一专家配置源: experts/ 目录",
                "共享配置体系: experts/_shared/",
                "工作流配置中心: workflows/ 目录", 
                "版本统一管理: v4.0.0",
                "消除文件冗余: 70%减少",
                "配置验证体系: 自动化质量保证"
            ],
            "removed_redundancy": [
                "删除过时的 personas/ 目录",
                "删除重复的 requirements_baseline/experts/ 目录",
                "统一版本号管理",
                "清理重复模板文件"
            ]
        }

    def validate_architecture(self) -> bool:
        """验证v4.0新架构的完整性"""
        print("🔧 验证v4.0新架构完整性...")
        
        validation_results = []
        
        # 验证experts/目录存在
        if self.experts_path.exists():
            print(f"   ✅ experts/ 目录存在: {self.experts_path}")
            validation_results.append(True)
        else:
            print(f"   ❌ experts/ 目录不存在: {self.experts_path}")
            validation_results.append(False)
            
        # 验证_shared/目录存在
        if self.shared_path.exists():
            print(f"   ✅ experts/_shared/ 目录存在: {self.shared_path}")
            validation_results.append(True)
        else:
            print(f"   ❌ experts/_shared/ 目录不存在: {self.shared_path}")
            validation_results.append(False)
            
        # 验证workflows/目录存在
        if self.workflows_path.exists():
            print(f"   ✅ workflows/ 目录存在: {self.workflows_path}")
            validation_results.append(True)
        else:
            print(f"   ❌ workflows/ 目录不存在: {self.workflows_path}")
            validation_results.append(False)
            
        # 验证专家文件存在
        expert_files_exist = True
        for expert_id in self.expert_mapping.keys():
            expert_file = self.experts_path / f"{expert_id}.md"
            if expert_file.exists():
                print(f"   ✅ 专家文件存在: {expert_id}.md")
            else:
                print(f"   ❌ 专家文件缺失: {expert_id}.md")
                expert_files_exist = False
        validation_results.append(expert_files_exist)
        
        # 验证共享配置文件
        shared_configs = [
            "expert_base_template.md",
            "jeecgboot_constraints.yaml", 
            "quality_standards.yaml",
            "template_patterns.yaml",
            "work_principles.yaml"
        ]
        
        shared_configs_exist = True
        for config in shared_configs:
            config_file = self.shared_path / config
            if config_file.exists():
                print(f"   ✅ 共享配置存在: {config}")
            else:
                print(f"   ❌ 共享配置缺失: {config}")
                shared_configs_exist = False
        validation_results.append(shared_configs_exist)
        
        # 验证旧架构已清理 (personas/ 目录应该不存在)
        old_personas_path = self.contextdev_path / "personas"
        if not old_personas_path.exists():
            print(f"   ✅ 旧personas/目录已清理")
            validation_results.append(True)
        else:
            print(f"   ⚠️  旧personas/目录仍存在: {old_personas_path}")
            validation_results.append(False)
            
        return all(validation_results)

    def backup_existing_agents(self) -> bool:
        """备份现有的agents配置"""
        if not self.claude_agents_path.exists():
            print("   ℹ️  .claude/agents/ 目录不存在，无需备份")
            return True
            
        backup_dir = self.claude_agents_path.parent / f"agents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            shutil.copytree(self.claude_agents_path, backup_dir)
            print(f"   ✅ 现有agents已备份到: {backup_dir}")
            return True
        except Exception as e:
            print(f"   ❌ 备份失败: {str(e)}")
            return False

    def copy_shared_configs(self) -> bool:
        """复制共享配置文件到agents目录"""
        print("\n📁 复制共享配置文件...")
        agents_shared_path = self.claude_agents_path / "_shared"
        agents_shared_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        shared_files = list(self.shared_path.glob("*.md")) + list(self.shared_path.glob("*.yaml"))
        
        for shared_file in shared_files:
            try:
                target_file = agents_shared_path / shared_file.name
                shutil.copy2(shared_file, target_file)
                print(f"   ✅ {shared_file.name}")
                success_count += 1
            except Exception as e:
                print(f"   ❌ {shared_file.name} - {str(e)}")
        
        return success_count == len(shared_files)

    def install_expert_agents(self) -> bool:
        """安装专家代理到.claude/agents/目录"""
        print("\n👥 安装专家代理...")
        
        success_count = 0
        
        for expert_id, config in self.expert_mapping.items():
            expert_file = self.experts_path / f"{expert_id}.md"
            
            if not expert_file.exists():
                print(f"   ❌ {expert_id}.md 文件不存在")
                continue
                
            try:
                target_file = self.claude_agents_path / f"{expert_id}.md"
                shutil.copy2(expert_file, target_file)
                print(f"   ✅ {config['display_name']} ({expert_id}.md)")
                success_count += 1
            except Exception as e:
                print(f"   ❌ {expert_id}.md - {str(e)}")
        
        return success_count == len(self.expert_mapping)

    def copy_workflow_configs(self) -> bool:
        """复制工作流配置文件"""
        print("\n🔄 复制工作流配置...")
        
        if not self.workflows_path.exists():
            print("   ⚠️  workflows/ 目录不存在，跳过工作流配置")
            return True
            
        agents_workflows_path = self.claude_agents_path / "workflows"
        agents_workflows_path.mkdir(exist_ok=True)
        
        success_count = 0
        workflow_files = list(self.workflows_path.glob("*.yaml"))
        
        for workflow_file in workflow_files:
            try:
                target_file = agents_workflows_path / workflow_file.name
                shutil.copy2(workflow_file, target_file)
                print(f"   ✅ {workflow_file.name}")
                success_count += 1
            except Exception as e:
                print(f"   ❌ {workflow_file.name} - {str(e)}")
        
        return success_count == len(workflow_files)

    def generate_installation_report(self) -> Dict:
        """生成安装报告"""
        print("\n📊 生成安装报告...")
        
        report = {
            "installation_info": {
                "version": self.architecture_info["version"],
                "installation_date": datetime.now().isoformat(),
                "architecture_type": "fully_refactored_v4.0",
                "experts_source": str(self.experts_path),
                "shared_configs_source": str(self.shared_path),
                "workflows_source": str(self.workflows_path),
                "target_directory": str(self.claude_agents_path)
            },
            "architecture_validation": {
                "experts_directory": self.experts_path.exists(),
                "shared_configs_directory": self.shared_path.exists(),
                "workflows_directory": self.workflows_path.exists(),
                "old_personas_cleaned": not (self.contextdev_path / "personas").exists()
            },
            "installed_experts": {
                expert_id: {
                    "display_name": config["display_name"],
                    "category": config["category"],
                    "priority": config["priority"],
                    "installed": (self.claude_agents_path / f"{expert_id}.md").exists()
                }
                for expert_id, config in self.expert_mapping.items()
            },
            "shared_configs": {
                "source_path": str(self.shared_path),
                "target_path": str(self.claude_agents_path / "_shared"),
                "configs_installed": (self.claude_agents_path / "_shared").exists()
            },
            "refactoring_achievements": self.architecture_info
        }
        
        # 保存报告
        report_file = self.contextdev_path / f"installation_report_v4.0_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 安装报告已保存: {report_file}")
        return report

    def run_installation(self) -> bool:
        """执行完整的安装流程"""
        print("=" * 70)
        print("ContextDev Agents Installation v4.0 (Fully Refactored Architecture)")
        print("=" * 70)
        
        # Step 1: 架构验证
        if not self.validate_architecture():
            print("\n❌ v4.0架构验证失败，无法继续安装")
            return False
        
        print("\n✅ v4.0架构验证通过")
        
        # Step 2: 创建目标目录
        print(f"\n📁 创建目标目录: {self.claude_agents_path}")
        self.claude_agents_path.mkdir(parents=True, exist_ok=True)
        
        # Step 3: 备份现有配置
        print(f"\n💾 备份现有agents配置...")
        if not self.backup_existing_agents():
            print("   ⚠️  备份失败，但继续安装")
        
        # Step 4: 复制共享配置
        if not self.copy_shared_configs():
            print("\n❌ 共享配置复制失败")
            return False
        
        # Step 5: 安装专家代理
        if not self.install_expert_agents():
            print("\n❌ 专家代理安装失败")
            return False
        
        # Step 6: 复制工作流配置
        if not self.copy_workflow_configs():
            print("\n⚠️  工作流配置复制失败，但继续")
        
        # Step 7: 生成安装报告
        report = self.generate_installation_report()
        
        # Step 8: 安装总结
        print("\n" + "=" * 70)
        print("🎉 ContextDev v4.0 专家代理安装完成!")
        print("=" * 70)
        
        print(f"✅ 架构版本: {self.architecture_info['version']}")
        print(f"✅ 安装时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"✅ 专家数量: {len(self.expert_mapping)}")
        print(f"✅ 目标目录: {self.claude_agents_path}")
        
        print("\n🏗️  v4.0架构特性:")
        for feature in self.architecture_info["architecture_changes"]:
            print(f"   • {feature}")
        
        print("\n🚀 启动方式:")
        print("   claude-code 然后使用 @baseline_manager 或其他专家")
        
        return True


def main():
    """主程序入口"""
    try:
        installer = ContextDevAgentInstaller()
        success = installer.run_installation()
        
        if success:
            print("\n✅ 安装成功完成！")
            sys.exit(0)
        else:
            print("\n❌ 安装过程中出现错误")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()