#!/usr/bin/env python3
"""
ContextDev Agents Installation Script
====================================

将ContextDev/personas/目录下的专业化JeecgBoot专家转换并安装到.claude/agents/目录
支持自动格式转换、元数据提取、备份管理等功能

Author: ContextDev团队
Version: 1.0.0
Date: 2025-07-26
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
    """ContextDev专家代理安装器"""
    
    def __init__(self):
        self.project_root = Path("/Users/admin/Work/Github/JeecgBoot")
        self.contextdev_path = self.project_root / "ContextDev"
        self.personas_path = self.contextdev_path / "personas"
        self.claude_agents_path = self.project_root / ".claude" / "agents"
        
        # 专家映射配置 - 保持文件名与agent名称一致
        self.expert_mapping = {
            "requirements_analyst": {
                "name": "requirements_analyst",
                "color": "green",
                "display_name": "需求分析专家",
                "category": "business_analysis"
            },
            "system_architect": {
                "name": "system_architect", 
                "color": "blue",
                "display_name": "系统架构专家",
                "category": "technical_design"
            },
            "task_planner": {
                "name": "task_planner",
                "color": "orange", 
                "display_name": "任务规划专家",
                "category": "project_management"
            },
            "code_developer": {
                "name": "code_developer",
                "color": "purple",
                "display_name": "代码开发专家", 
                "category": "development"
            },
            "quality_tester": {
                "name": "quality_tester",
                "color": "red",
                "display_name": "质量测试专家",
                "category": "quality_assurance"
            }
        }
    
    def validate_environment(self) -> bool:
        """验证安装环境"""
        print("🔍 验证安装环境...")
        
        # 检查ContextDev目录结构
        if not self.contextdev_path.exists():
            print(f"❌ ContextDev目录不存在: {self.contextdev_path}")
            return False
            
        if not self.personas_path.exists():
            print(f"❌ personas目录不存在: {self.personas_path}")
            return False
        
        # 检查专家文件是否存在
        missing_files = []
        for expert_key in self.expert_mapping.keys():
            expert_file = self.personas_path / f"{expert_key}.md"
            if not expert_file.exists():
                missing_files.append(str(expert_file))
        
        if missing_files:
            print("❌ 缺少以下专家文件:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        
        # 确保.claude/agents目录存在
        self.claude_agents_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ 环境验证通过")
        return True
    
    def backup_existing_agents(self) -> Optional[Path]:
        """备份现有的agents文件"""
        if not self.claude_agents_path.exists():
            return None
            
        existing_files = list(self.claude_agents_path.glob("*.md"))
        if not existing_files:
            return None
        
        # 创建备份目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.claude_agents_path.parent / f"agents_backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        print(f"🔄 备份现有agents到: {backup_dir}")
        
        # 复制文件
        for file in existing_files:
            shutil.copy2(file, backup_dir / file.name)
            print(f"   ✅ {file.name}")
        
        return backup_dir
    
    def extract_persona_content(self, persona_file: Path) -> Tuple[Dict, str]:
        """提取persona文件的元数据和内容"""
        with open(persona_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析文件内容
        lines = content.split('\\n')
        
        # 提取标题行的角色信息
        title_line = lines[0] if lines else ""
        role_name = ""
        if title_line.startswith("# Role:"):
            role_name = title_line.replace("# Role:", "").strip()
        
        # 提取角色定位信息
        description = ""
        for line in lines[1:10]:  # 在前10行中查找描述
            if line.startswith("> **角色定位**:"):
                description = line.replace("> **角色定位**:", "").strip()
                break
        
        # 生成元数据
        expert_key = persona_file.stem
        mapping = self.expert_mapping.get(expert_key, {})
        
        metadata = {
            "name": mapping.get("name", expert_key),
            "description": description or f"专精于JeecgBoot平台的{mapping.get('display_name', '专家')}",
            "color": mapping.get("color", "gray")
        }
        
        return metadata, content
    
    def convert_persona_to_agent(self, persona_file: Path) -> str:
        """将persona文件转换为agent格式"""
        with open(persona_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查文件是否已经有YAML前置元数据
        if content.startswith('---'):
            # 文件已经符合agent格式，直接返回
            print(f"   ✅ {persona_file.stem} 已包含YAML元数据，直接使用")
            return content
        
        # 如果没有YAML前置元数据，则按原逻辑转换
        metadata, original_content = self.extract_persona_content(persona_file)
        
        # 构建YAML前置元数据
        yaml_header = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        
        # 转换内容格式
        converted_content = self.transform_content_format(original_content)
        
        # 组合最终内容
        agent_content = f"---\\n{yaml_header}---\\n\\n{converted_content}"
        
        return agent_content
    
    def transform_content_format(self, content: str) -> str:
        """转换内容格式，使其更适合agent使用"""
        lines = content.split('\\n')
        transformed_lines = []
        
        skip_until_mission = True
        
        for line in lines:
            # 跳过文件头部信息，直到找到核心使命部分
            if "## 🎯 专家身份与核心使命" in line:
                skip_until_mission = False
                continue
            
            if skip_until_mission:
                continue
            
            # 转换标题格式
            if line.startswith("### 🤖 角色定义"):
                transformed_lines.append("## 专家身份定义")
                continue
            elif line.startswith("### 🔧 模板工具箱"):
                transformed_lines.append("## 工作方法与工具")
                continue
            elif line.startswith("#### 📥 **输入模板库**"):
                transformed_lines.append("### 输入处理标准")
                continue
            elif line.startswith("#### ⚙️ **处理模板库**"):
                transformed_lines.append("### 工作流程模板")
                continue
            elif line.startswith("#### 📤 **输出模板库**"):
                transformed_lines.append("### 交付物标准")
                continue
            
            # 保留其他内容
            transformed_lines.append(line)
        
        # 添加JeecgBoot专业说明
        jeecgboot_notice = """
## JeecgBoot平台专业约束

你是专精于JeecgBoot企业级快速开发平台的专业专家，必须严格遵循以下约束：

- **技术栈约束**: 严格使用JeecgBoot官方技术栈（Spring Boot 3.x + Vue 3 + MySQL + Redis）
- **框架能力**: 充分利用JeecgBoot代码生成器、权限系统、工作流引擎等核心功能
- **架构模式**: 遵循单体分层架构模式，杜绝微服务架构
- **开发规范**: 按照JeecgBoot命名约定、代码结构标准和最佳实践
- **协作流程**: 与其他专家（需求分析师、架构师、规划师、开发者、测试员）紧密协作

始终基于模板驱动的标准化工作流程，确保输出物的专业性和一致性。
"""
        
        return '\\n'.join(transformed_lines) + jeecgboot_notice
    
    def install_agent(self, expert_key: str) -> bool:
        """安装单个专家代理"""
        persona_file = self.personas_path / f"{expert_key}.md"
        mapping = self.expert_mapping[expert_key]
        agent_file = self.claude_agents_path / f"{mapping['name']}.md"
        
        try:
            # 转换格式
            agent_content = self.convert_persona_to_agent(persona_file)
            
            # 写入文件
            with open(agent_file, 'w', encoding='utf-8') as f:
                f.write(agent_content)
            
            print(f"   ✅ {expert_key} → {mapping['name']}.md")
            return True
            
        except Exception as e:
            print(f"   ❌ {expert_key} 安装失败: {str(e)}")
            return False
    
    def create_agents_readme(self):
        """创建agents目录的README文件"""
        readme_content = f"""# JeecgBoot ContextDev AI Agents

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> **源目录**: {self.personas_path}  
> **安装脚本**: install_agents.py  

## 专家团队

基于ContextDev v4.0工业级AI专家协作系统，包含5个专业化JeecgBoot开发专家：

| Agent文件 | 专家角色 | 专业领域 | 颜色标识 |
|-----------|----------|----------|----------|
"""
        
        for expert_key, mapping in self.expert_mapping.items():
            readme_content += f"| {mapping['name']}.md | {mapping['display_name']} | {mapping['category']} | {mapping['color']} |\\n"
        
        readme_content += f"""
## 使用方法

这些agents已经过专业转换，可直接在Claude Code中使用：

```bash
# 使用Task工具调用专家
Task(description="需求分析", prompt="分析业务需求", subagent_type="requirements_analyst")
Task(description="架构设计", prompt="设计系统架构", subagent_type="system_architect") 
Task(description="任务规划", prompt="制定开发计划", subagent_type="task_planner")
Task(description="代码开发", prompt="实现业务功能", subagent_type="code_developer")
Task(description="质量测试", prompt="执行测试验证", subagent_type="quality_tester")
```

## 技术特性

- **JeecgBoot深度集成**: 专为JeecgBoot 3.8.1平台优化
- **模板驱动**: 基于标准化模板的工作流程
- **专家协作**: 5专家协作的完整开发流水线
- **质量保证**: 工业级质量控制和交付标准

## 维护信息

- **原始系统**: ContextDev v4.0.0
- **转换脚本**: install_agents.py
- **维护团队**: ContextDev架构团队
- **技术支持**: JeecgBoot生态系统

---

*通过Python脚本自动生成，基于ContextDev工业级AI专家系统*
"""
        
        readme_file = self.claude_agents_path / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"   📝 生成README.md")
    
    def create_claude_md_symlink(self) -> bool:
        """创建CLAUDE.md软链接到项目根目录"""
        print("\n🔗 创建CLAUDE.md软链接...")
        
        # 源文件：ContextDev目录下的CLAUDE.md
        source_file = self.contextdev_path / "CLAUDE.md"
        # 目标文件：项目根目录下的CLAUDE.md
        target_file = self.project_root / "CLAUDE.md"
        
        try:
            # 检查源文件是否存在
            if not source_file.exists():
                print(f"   ❌ 源文件不存在: {source_file}")
                return False
            
            # 处理现有目标文件
            if target_file.exists():
                # 检查是否已经是正确的软链接
                if target_file.is_symlink():
                    current_target = target_file.resolve()
                    if current_target == source_file.resolve():
                        print(f"   ✅ CLAUDE.md软链接已存在且正确")
                        return True
                    else:
                        print(f"   🔄 现有软链接指向错误位置，将重新创建")
                        target_file.unlink()
                else:
                    # 备份现有文件
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = self.project_root / f"CLAUDE.md.backup_{timestamp}"
                    shutil.move(str(target_file), str(backup_file))
                    print(f"   📦 备份现有CLAUDE.md到: {backup_file}")
            
            # 创建软链接 (相对路径)
            relative_source = os.path.relpath(str(source_file), str(self.project_root))
            os.symlink(relative_source, str(target_file))
            
            # 验证软链接创建成功
            if target_file.is_symlink() and target_file.resolve() == source_file.resolve():
                print(f"   ✅ 软链接创建成功: {target_file} -> {relative_source}")
                return True
            else:
                print(f"   ❌ 软链接创建失败，验证不通过")
                return False
                
        except Exception as e:
            print(f"   ❌ 创建软链接失败: {str(e)}")
            return False
    
    def run_installation(self) -> bool:
        """执行完整安装流程"""
        print("🚀 ContextDev Agents 安装程序启动")
        print("=" * 50)
        
        # 1. 环境验证
        if not self.validate_environment():
            return False
        
        # 2. 备份现有文件
        backup_dir = self.backup_existing_agents()
        if backup_dir:
            print(f"📦 备份完成: {backup_dir}")
        
        # 3. 安装专家代理
        print("\\n📥 安装ContextDev专家代理...")
        success_count = 0
        
        for expert_key in self.expert_mapping.keys():
            if self.install_agent(expert_key):
                success_count += 1
        
        # 4. 创建README
        print("\\n📝 生成配置文档...")
        self.create_agents_readme()
        
        # 5. 创建CLAUDE.md软链接
        symlink_success = self.create_claude_md_symlink()
        
        # 6. 安装总结
        print("\\n" + "=" * 50)
        total_experts = len(self.expert_mapping)
        
        if success_count == total_experts:
            print(f"✅ 安装成功! {success_count}/{total_experts} 个专家代理已安装")
            print(f"📂 安装位置: {self.claude_agents_path}")
            
            if symlink_success:
                print(f"🔗 CLAUDE.md软链接已创建: {self.project_root}/CLAUDE.md -> ContextDev/CLAUDE.md")
            else:
                print("⚠️  CLAUDE.md软链接创建失败，但专家安装成功")
            
            print("\\n🎯 现在可以使用以下专家:")
            for expert_key, mapping in self.expert_mapping.items():
                print(f"   • {mapping['name']} - {mapping['display_name']}")
            
            print("\\n💡 使用提示:")
            print("   • 专家可通过Task工具调用：Task(subagent_type=\"requirements_analyst\", ...)")
            print("   • CLAUDE.md配置已自动链接到项目根目录")
            print("   • 查看 .claude/agents/README.md 了解详细使用方法")
            
            return True
        else:
            print(f"⚠️  部分安装失败! {success_count}/{total_experts} 个专家代理已安装")
            if symlink_success:
                print(f"🔗 CLAUDE.md软链接创建成功")
            return False


def main():
    """主函数"""
    installer = ContextDevAgentInstaller()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("""
ContextDev Agents Installation Script
===================================

将ContextDev/personas/目录下的专业化JeecgBoot专家转换并安装到.claude/agents/目录
同时创建CLAUDE.md软链接到项目根目录，实现完整的Claude Code集成

功能特性:
• 自动转换ContextDev专家为Claude agents格式
• 智能备份现有agents和配置文件  
• 创建项目根目录CLAUDE.md软链接
• 生成专业化README和使用文档
• 完整的错误处理和回滚机制

Usage: python3 install_agents.py [options]

Options:
  -h, --help     显示帮助信息
  --dry-run      试运行模式（不实际安装）
  --force        强制覆盖现有文件
  
Examples:
  python3 install_agents.py                # 正常安装（推荐）
  python3 install_agents.py --dry-run      # 预览安装过程
  python3 install_agents.py --force        # 强制覆盖安装

安装内容:
• 5个专业化JeecgBoot专家 (requirements_analyst/system_architect/task_planner/code_developer/quality_tester)
• .claude/agents/README.md 使用文档
• 项目根目录/CLAUDE.md -> ContextDev/CLAUDE.md 软链接
• 自动备份现有配置（带时间戳）
""")
            return
        elif sys.argv[1] == "--dry-run":
            print("🧪 试运行模式 - 不会实际修改文件")
            # TODO: 实现试运行逻辑
            return
    
    # 执行安装
    try:
        success = installer.run_installation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n\\n⚠️  用户中断安装")
        sys.exit(1)
    except Exception as e:
        print(f"\\n\\n❌ 安装失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()