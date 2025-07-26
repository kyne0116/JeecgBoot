#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JeecgBoot项目自定义Subagent安装脚本 (Python版本)
自动将ContextDev/personas目录下的专业顾问文件转换为Claude Code subagents

使用方法: python3 install-personas-subagents.py

作者: Claude Code AI Assistant
版本: 1.0.0
日期: 2025-07-26
"""

import os
import sys
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 颜色定义
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

@dataclass
class PersonaInfo:
    """Persona信息数据类"""
    filename: str
    title: str
    role_name: str
    description: str
    content: str
    agent_name: str
    color: str

class PersonaParser:
    """Persona文件解析器"""
    
    # 文件名到agent名称的映射（基于文件名生成，直接使用文件的基础名称）
    FILENAME_TO_AGENT_MAPPING = {
        'analyze-expert.md': 'analyze-expert',
        'design-expert.md': 'design-expert', 
        'develop-expert.md': 'develop-expert',
        'plan-expert.md': 'plan-expert',
        'test-expert.md': 'test-expert'
    }
    
    # agent颜色映射
    COLOR_MAPPING = {
        'analyze-expert': 'green',
        'design-expert': 'purple', 
        'develop-expert': 'blue',
        'plan-expert': 'orange',
        'test-expert': 'red'
    }
    
    def __init__(self, personas_dir: str):
        self.personas_dir = Path(personas_dir)
        
    def parse_persona_file(self, filepath: Path) -> Optional[PersonaInfo]:
        """解析单个persona文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            title_match = re.search(r'^# 你是(.+)$', content, re.MULTILINE)
            if not title_match:
                logger.warning(f"无法从 {filepath.name} 提取标题")
                return None
                
            role_name = title_match.group(1).strip()
            
            # 基于文件名生成agent名称
            agent_name = self.FILENAME_TO_AGENT_MAPPING.get(filepath.name)
            if not agent_name:
                # 如果没有预定义映射，自动从文件名生成
                agent_name = self._generate_agent_name_from_filename(filepath.name)
            
            # 生成描述
            description = self._generate_description(role_name, content)
            
            # 选择颜色
            color = self.COLOR_MAPPING.get(agent_name, 'blue')
            
            return PersonaInfo(
                filename=filepath.name,
                title=f"# 你是{role_name}",
                role_name=role_name,
                description=description,
                content=content,
                agent_name=agent_name,
                color=color
            )
            
        except Exception as e:
            logger.error(f"解析文件 {filepath} 时发生错误: {e}")
            return None
    
    def _generate_agent_name_from_filename(self, filename: str) -> str:
        """从文件名自动生成agent名称"""
        # 去掉文件扩展名，保留完整的基础名称
        name = filename.replace('.md', '')
        return name.lower()
    
    def _generate_agent_name(self, role_name: str) -> str:
        """自动生成agent名称"""
        # 简化逻辑：移除常见词汇，转换为英文风格
        simplified = (role_name
                     .replace('IT', '')
                     .replace('资深', '')
                     .replace('工程师', '')
                     .replace('顾问', '')
                     .replace('WEB系统', 'web')
                     .strip())
        
        # 转换为kebab-case
        return re.sub(r'[^\w\s-]', '', simplified).replace(' ', '-').lower()
    
    def _generate_description(self, role_name: str, content: str) -> str:
        """生成简洁的描述"""
        descriptions = {
            'IT需求分析与设计规划资深顾问': '专精于需求分析、商业价值挖掘、用户体验设计和技术可行性评估的资深顾问。帮助从商业构想到技术实现的全流程专业咨询，确保项目既具备商业价值又技术可行。',
            'IT资深架构师': '企业级系统架构设计专家，擅长AI工程和大语言模型系统的复杂项目。专注于系统架构设计、技术选型、性能优化和架构治理。',
            'JeecgBoot全栈开发工程师': '精通JeecgBoot前后端技术架构的资深全栈开发工程师。专注于Spring Boot + Vue3技术栈，代码生成器应用和企业级应用开发。',
            'IT资深需求分解任务设计工程师': '专精于复杂系统项目执行规划设计的工程师。将抽象需求和技术架构转化为具体可执行的任务体系，制定科学的项目执行计划。',
            'WEB系统全栈测试工程师': '精通WEB系统前后端测试架构的资深全栈测试工程师。专注于测试策略设计、自动化测试、质量保证和缺陷管理。'
        }
        
        return descriptions.get(role_name, f"{role_name}专家，为您提供专业的技术咨询和解决方案。")
    
    def parse_all_personas(self) -> List[PersonaInfo]:
        """解析所有persona文件"""
        personas = []
        
        if not self.personas_dir.exists():
            logger.error(f"Personas目录不存在: {self.personas_dir}")
            return personas
        
        md_files = list(self.personas_dir.glob("*.md"))
        if not md_files:
            logger.warning(f"在 {self.personas_dir} 中未找到.md文件")
            return personas
        
        logger.info(f"发现 {len(md_files)} 个persona文件")
        
        for md_file in md_files:
            logger.info(f"解析文件: {md_file.name}")
            persona = self.parse_persona_file(md_file)
            if persona:
                personas.append(persona)
                logger.info(f"✓ 成功解析: {persona.role_name} -> {persona.agent_name}")
            else:
                logger.warning(f"✗ 解析失败: {md_file.name}")
        
        return personas

class SubagentInstaller:
    """Subagent安装器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.agents_dir = self.project_root / ".claude" / "agents"
        
    def check_project_environment(self) -> bool:
        """检查项目环境"""
        # 检查是否在JeecgBoot项目根目录
        if not (self.project_root / "pom.xml").exists() and not (self.project_root / "jeecg-boot").exists():
            logger.error("请在JeecgBoot项目根目录下运行此脚本")
            return False
        
        logger.info("✓ 检测到JeecgBoot项目环境")
        return True
    
    def setup_directories(self) -> bool:
        """设置目录结构"""
        try:
            self.agents_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ 创建目录: {self.agents_dir}")
            return True
        except Exception as e:
            logger.error(f"创建目录失败: {e}")
            return False
    
    def check_existing_agents(self) -> List[str]:
        """检查现有的agents"""
        existing_agents = []
        if self.agents_dir.exists():
            for agent_file in self.agents_dir.glob("*.md"):
                existing_agents.append(agent_file.stem)
        
        if existing_agents:
            logger.info(f"发现 {len(existing_agents)} 个现有agent:")
            for agent in existing_agents:
                logger.info(f"  - {agent}")
        
        return existing_agents
    
    def generate_agent_config(self, persona: PersonaInfo) -> str:
        """生成agent配置内容"""
        config = f"""---
name: {persona.agent_name}
description: {persona.description}
color: {persona.color}
---

{persona.content}
"""
        return config
    
    def install_agent(self, persona: PersonaInfo, overwrite: bool = False) -> bool:
        """安装单个agent"""
        agent_file = self.agents_dir / f"{persona.agent_name}.md"
        
        if agent_file.exists() and not overwrite:
            logger.warning(f"Agent {persona.agent_name} 已存在，跳过安装")
            return False
        
        try:
            config_content = self.generate_agent_config(persona)
            with open(agent_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            logger.info(f"✓ 安装agent: {persona.agent_name}")
            return True
        except Exception as e:
            logger.error(f"安装agent {persona.agent_name} 失败: {e}")
            return False
    
    def install_all_agents(self, personas: List[PersonaInfo], overwrite: bool = False) -> Tuple[int, int]:
        """安装所有agents"""
        installed = 0
        skipped = 0
        
        for persona in personas:
            if self.install_agent(persona, overwrite):
                installed += 1
            else:
                skipped += 1
        
        return installed, skipped
    
    def validate_agents(self) -> bool:
        """验证安装的agents"""
        logger.info("验证agent配置文件...")
        
        valid = True
        for agent_file in self.agents_dir.glob("*.md"):
            # 跳过README.md文件
            if agent_file.name == "README.md":
                continue
                
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查YAML front matter
                if not content.startswith('---'):
                    logger.error(f"{agent_file.name}: 缺少YAML front matter")
                    valid = False
                    continue
                
                # 检查必需字段
                yaml_section = content.split('---')[1]
                if 'name:' not in yaml_section:
                    logger.error(f"{agent_file.name}: 缺少name字段")
                    valid = False
                
                if 'description:' not in yaml_section:
                    logger.error(f"{agent_file.name}: 缺少description字段")
                    valid = False
                    
            except Exception as e:
                logger.error(f"验证 {agent_file.name} 时发生错误: {e}")
                valid = False
        
        if valid:
            logger.info("✓ 所有agent配置文件验证通过")
        
        return valid
    
    def show_installed_agents(self):
        """显示已安装的agents"""
        logger.info("已安装的subagents:")
        print()
        
        for agent_file in self.agents_dir.glob("*.md"):
            # 跳过README.md文件
            if agent_file.name == "README.md":
                continue
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取信息
                agent_name = agent_file.stem
                
                yaml_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    description_match = re.search(r'description:\s*(.+)', yaml_content)
                    color_match = re.search(r'color:\s*(\w+)', yaml_content)
                    
                    description = description_match.group(1).strip() if description_match else "无描述"
                    color = color_match.group(1) if color_match else "blue"
                    
                    # 根据颜色选择显示颜色
                    color_code = getattr(Colors, color.upper(), Colors.BLUE)
                    
                    print(f"  {color_code}●{Colors.NC} {Colors.BLUE}{agent_name}{Colors.NC}")
                    print(f"    {description}")
                    print()
                    
            except Exception as e:
                logger.warning(f"读取agent {agent_file.name} 信息时发生错误: {e}")
    
    def copy_claude_config(self) -> bool:
        """复制CLAUDE.md到项目根目录"""
        source_path = self.project_root / "ContextDev" / "CLAUDE.md"
        target_path = self.project_root / "CLAUDE.md"
        
        try:
            # 检查源文件是否存在
            if not source_path.exists():
                logger.warning(f"源文件不存在: {source_path}")
                return False
            
            # 检查目标文件是否已存在
            if target_path.exists():
                logger.info(f"目标文件已存在，将覆盖: {target_path}")
            
            # 复制文件
            shutil.copy2(source_path, target_path)
            logger.info(f"✓ 成功复制CLAUDE.md到项目根目录: {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"复制CLAUDE.md失败: {e}")
            return False
    
    def create_usage_documentation(self):
        """创建使用说明文档"""
        readme_path = self.agents_dir / "README.md"
        
        readme_content = """# JeecgBoot Personas Subagents 使用说明

本项目配置了从ContextDev/personas目录转换而来的专业顾问Claude Code subagents。

## 可用的Subagents

### 1. requirements-analyst (需求分析专家)
- **角色**: IT需求分析与设计规划资深顾问
- **专长**: 需求分析、商业价值挖掘、用户体验设计、技术可行性评估
- **使用场景**: 项目需求分析、商业价值评估、用户研究、技术方案论证

### 2. system-architect (系统架构师)
- **角色**: IT资深架构师
- **专长**: 系统架构设计、技术选型、AI工程、分布式系统、性能优化
- **使用场景**: 系统架构设计、技术架构评审、性能优化、技术选型决策

### 3. fullstack-developer (全栈开发工程师)
- **角色**: JeecgBoot全栈开发工程师
- **专长**: JeecgBoot技术栈、Spring Boot、Vue3、代码生成器、企业级开发
- **使用场景**: JeecgBoot项目开发、代码实现、技术问题解决、最佳实践指导

### 4. task-planner (任务规划师)
- **角色**: IT资深需求分解任务设计工程师
- **专长**: 任务分解、项目规划、执行计划、工作分解结构(WBS)
- **使用场景**: 项目规划、任务分解、里程碑设计、资源规划

### 5. test-engineer (测试工程师)
- **角色**: WEB系统全栈测试工程师
- **专长**: 测试策略、自动化测试、质量保证、缺陷管理
- **使用场景**: 测试计划制定、测试用例设计、质量评估、测试自动化

## 使用方法

### 查看可用agents
```bash
/agents
```

### 明确指定使用某个agent
```
使用 requirements-analyst 帮我分析用户需求
使用 system-architect 设计系统架构
使用 fullstack-developer 实现JeecgBoot功能
使用 task-planner 制定项目计划
使用 test-engineer 设计测试方案
```

### 让Claude自动选择合适的agent
只需要描述你的问题，Claude会自动选择最合适的agent来处理。

## 开发流程建议

建议按照以下顺序使用不同的专家agent：

1. **需求分析阶段** → requirements-analyst
2. **架构设计阶段** → system-architect
3. **任务规划阶段** → task-planner
4. **开发实现阶段** → fullstack-developer
5. **测试验证阶段** → test-engineer

## 注意事项

1. 每个agent都具备ultrathink超级深度思考能力，会进行全面深入的分析
2. Agent之间可以协同工作，前一个agent的输出可以作为后一个agent的输入
3. 所有agent都遵循EARS (Easy Approach to Requirements Syntax) 语法规范
4. 生成的文档将统一存储在 `/ai_docs/` 目录下

## 文档输出标准

- **需求文档**: `{LEVEL}_{NAME}_Requirements_v{VERSION}.md`
- **架构文档**: `{LEVEL}_{NAME}_Architecture_v{VERSION}.md`
- **规划文档**: `{LEVEL}_{NAME}_TaskPlan_v{VERSION}.md`
- **实现文档**: `{LEVEL}_{NAME}_Implementation_v{VERSION}.md`
- **测试文档**: `{LEVEL}_{NAME}_TestReport_v{VERSION}.md`

## 反馈与改进

如果你发现任何问题或有改进建议，请及时反馈以完善这些专业顾问的能力。
"""
        
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            logger.info(f"✓ 创建使用说明文档: {readme_path}")
        except Exception as e:
            logger.error(f"创建使用说明文档失败: {e}")

def print_header():
    """打印脚本头部信息"""
    print(f"{Colors.BLUE}")
    print("=" * 60)
    print("  JeecgBoot Personas Subagents 自动安装脚本")
    print("  将ContextDev/personas专业顾问转换为Claude Code Subagents")
    print("=" * 60)
    print(f"{Colors.NC}")

def print_success_summary(installed: int, skipped: int, total: int, claude_copied: bool = False):
    """打印安装成功摘要"""
    print()
    print(f"{Colors.GREEN}🎉 安装完成！{Colors.NC}")
    print()
    print(f"📊 安装统计:")
    print(f"  - 总计: {total} 个persona文件")
    print(f"  - 成功安装: {Colors.GREEN}{installed}{Colors.NC} 个agent")
    if skipped > 0:
        print(f"  - 跳过安装: {Colors.YELLOW}{skipped}{Colors.NC} 个agent")
    if claude_copied:
        print(f"  - CLAUDE.md配置: {Colors.GREEN}已复制到根目录{Colors.NC}")
    else:
        print(f"  - CLAUDE.md配置: {Colors.YELLOW}未复制{Colors.NC}")
    print()
    print(f"{Colors.BLUE}📖 使用方法:{Colors.NC}")
    print("  1. 运行 '/agents' 查看可用的agents")
    print("  2. 明确指定: '使用 analyze-expert 分析需求'")
    print("  3. 自动选择: 直接描述问题让Claude选择合适的agent")
    print()
    print(f"{Colors.BLUE}📚 详细说明: .claude/agents/README.md{Colors.NC}")
    if claude_copied:
        print(f"{Colors.BLUE}🔧 项目配置: CLAUDE.md (项目根目录){Colors.NC}")

def main():
    """主函数"""
    print_header()
    
    # 初始化组件
    personas_dir = "ContextDev/personas"
    parser = PersonaParser(personas_dir)
    installer = SubagentInstaller()
    
    try:
        # 1. 检查项目环境
        if not installer.check_project_environment():
            sys.exit(1)
        
        # 2. 设置目录结构
        if not installer.setup_directories():
            sys.exit(1)
        
        # 3. 检查现有agents
        existing_agents = installer.check_existing_agents()
        
        # 4. 解析personas
        logger.info(f"开始解析 {personas_dir} 目录下的persona文件...")
        personas = parser.parse_all_personas()
        
        if not personas:
            logger.error("未找到可解析的persona文件")
            sys.exit(1)
        
        logger.info(f"成功解析 {len(personas)} 个persona文件")
        
        # 5. 安装agents
        logger.info("开始安装agents...")
        installed, skipped = installer.install_all_agents(personas, overwrite=False)
        
        # 6. 验证安装
        if not installer.validate_agents():
            logger.error("Agent配置验证失败")
            sys.exit(1)
        
        # 7. 显示安装结果
        installer.show_installed_agents()
        
        # 8. 复制CLAUDE.md到项目根目录
        logger.info("复制CLAUDE.md配置文件到项目根目录...")
        claude_copied = installer.copy_claude_config()
        
        # 9. 创建使用说明
        installer.create_usage_documentation()
        
        # 10. 打印成功摘要
        print_success_summary(installed, skipped, len(personas), claude_copied)
        
    except KeyboardInterrupt:
        logger.info("用户中断安装")
        sys.exit(1)
    except Exception as e:
        logger.error(f"安装过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()