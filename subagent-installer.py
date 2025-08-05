#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubAgent 安装助手
生成可在 Claude Code 中执行的 subagent 创建命令
支持 Windows、macOS、Linux 三个平台
"""

import os
import sys
import yaml
import platform
import json
import time
import subprocess
import psutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SubAgentInfo:
    """SubAgent 信息数据类"""
    name: str
    description: str
    color: str = "#4CAF50"
    icon: str = "🤖"
    version: str = "1.0"
    category: str = "Development"
    tags: List[str] = None
    file_path: str = ""

class SubAgentHelper:
    """SubAgent 助手"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.agents_dirs = [
            self.project_root / "ContextDev" / "agents",
            self.project_root / "CodeGen"
        ]
        self.platform_info = self.detect_platform()
        self.claude_process = None
    
    def detect_platform(self) -> Dict[str, str]:
        """检测当前平台信息"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # 平台标准化
        if system == "darwin":
            platform_name = "macOS"
        elif system == "windows":
            platform_name = "Windows"
        elif system == "linux":
            platform_name = "Linux"
        else:
            platform_name = system.title()
        
        # 架构标准化
        if machine in ["x86_64", "amd64"]:
            arch = "x64"
        elif machine in ["aarch64", "arm64"]:
            arch = "arm64"
        elif machine.startswith("arm"):
            arch = "arm"
        else:
            arch = machine
        
        return {
            "system": system,
            "platform": platform_name,
            "machine": machine,
            "arch": arch,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "encoding": sys.getdefaultencoding()
        }
    
    def print_message(self, message: str, use_emoji: bool = None):
        """跨平台兼容的消息输出"""
        if use_emoji is None:
            # Windows CMD 默认不支持 emoji，其他平台支持
            use_emoji = self.platform_info["system"] != "windows"
        
        try:
            print(message)
        except UnicodeEncodeError:
            # 如果输出编码有问题，尝试ASCII安全输出
            safe_message = message.encode('ascii', 'ignore').decode('ascii')
            print(safe_message)
    
    def parse_md_frontmatter(self, file_path: Path) -> Optional[Dict]:
        """解析 Markdown 文件的 frontmatter（跨平台兼容）"""
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                if not content.startswith('---'):
                    return None
                    
                # 找到第二个 --- 的位置
                end_pos = content.find('---', 3)
                if end_pos == -1:
                    return None
                    
                frontmatter = content[3:end_pos].strip()
                return yaml.safe_load(frontmatter)
                
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.print_message(f"WARNING: 解析文件 {file_path} 失败: {e}")
                return None
        
        self.print_message(f"ERROR: 无法解析文件 {file_path}，尝试了多种编码")
        return None
    
    def discover_subagents(self) -> List[SubAgentInfo]:
        """发现项目中的 subagent 定义文件"""
        agents = []
        
        for agents_dir in self.agents_dirs:
            if not agents_dir.exists():
                continue
                
            # 查找 .md 文件
            for md_file in agents_dir.glob("*.md"):
                # 跳过常见的说明文件
                skip_files = [
                    'readme.md', 'index.md', 'guide.md', 'config.md',
                    'code_gen_guide.md', 'code_gen_json_standards.md', 'config_guide.md'
                ]
                if md_file.name.lower() in skip_files:
                    continue
                    
                frontmatter = self.parse_md_frontmatter(md_file)
                if not frontmatter or 'name' not in frontmatter:
                    continue
                
                agent_info = SubAgentInfo(
                    name=frontmatter.get('name', ''),
                    description=frontmatter.get('description', ''),
                    color=frontmatter.get('color', '#4CAF50'),
                    icon=frontmatter.get('icon', '🤖'),
                    version=frontmatter.get('version', '1.0'),
                    category=frontmatter.get('category', 'Development'),
                    tags=frontmatter.get('tags', []),
                    file_path=str(md_file)
                )
                agents.append(agent_info)
        
        return agents
    
    def generate_creation_commands(self) -> str:
        """生成创建 subagent 的命令（跨平台兼容）"""
        agents = self.discover_subagents()
        
        if not agents:
            return "# 未发现任何 subagent 定义文件"
        
        commands = []
        
        # 添加平台信息头部
        commands.append(f"# SubAgent 创建命令 - {self.platform_info['platform']} {self.platform_info['arch']}")
        commands.append(f"# Python {self.platform_info['python_version']} | 编码: {self.platform_info['encoding']}")
        commands.append("# 请在 Claude Code 中逐个执行以下命令")
        
        # 添加使用说明
        if self.platform_info["system"] == "windows":
            commands.append("# Windows 用户提示: 如果出现编码问题，请确保终端支持 UTF-8")
        elif self.platform_info["system"] == "darwin":
            commands.append("# macOS 用户提示: 建议使用 Terminal.app 或 iTerm2")
        else:
            commands.append("# Linux 用户提示: 确保终端支持 UTF-8 编码")
        
        commands.append("")
        
        for i, agent in enumerate(agents, 1):
            commands.append(f"# {i}. {agent.name}")
            commands.append(f"# 描述: {agent.description}")
            
            # 根据平台调整路径显示
            if self.platform_info["system"] == "windows":
                file_path = str(Path(agent.file_path)).replace('/', '\\')
            else:
                file_path = str(Path(agent.file_path)).replace('\\', '/')
            
            commands.append(f"# 文件: {file_path}")
            
            # 生成 /agents create 命令，确保描述中的特殊字符被正确处理
            description = agent.description.replace('"', '\\"')
            cmd = f'/agents create {agent.name} "{description}"'
            commands.append(cmd)
            commands.append("")
        
        commands.append("# 创建完成后，可以使用 /agents 命令查看已创建的 subagent")
        commands.append(f"# 脚本运行平台: {self.platform_info['platform']} ({self.platform_info['system']})")
        
        return "\n".join(commands)
    
    def generate_status_report(self) -> str:
        """生成状态报告（跨平台兼容）"""
        agents = self.discover_subagents()
        
        report = []
        report.append("# SubAgent 发现报告")
        report.append("=" * 60)
        
        # 添加平台信息
        report.append(f"# 运行环境: {self.platform_info['platform']} {self.platform_info['arch']}")
        report.append(f"# Python 版本: {self.platform_info['python_version']}")
        report.append(f"# 默认编码: {self.platform_info['encoding']}")
        report.append(f"# 项目根目录: {self.project_root}")
        report.append("")
        
        report.append(f"发现 {len(agents)} 个 subagent 定义文件")
        report.append("-" * 40)
        
        if not agents:
            report.append("未找到任何 subagent 定义文件")
            report.append("请检查以下目录:")
            for agents_dir in self.agents_dirs:
                report.append(f"  - {agents_dir}")
            return "\n".join(report)
        
        for i, agent in enumerate(agents, 1):
            report.append(f"{i}. **{agent.name}**")
            report.append(f"   - 描述: {agent.description}")
            report.append(f"   - 版本: {agent.version}")
            report.append(f"   - 分类: {agent.category}")
            report.append(f"   - 图标: {agent.icon}")
            report.append(f"   - 颜色: {agent.color}")
            report.append(f"   - 标签: {', '.join(agent.tags) if agent.tags else '无'}")
            
            # 根据平台调整路径显示
            if self.platform_info["system"] == "windows":
                file_path = str(Path(agent.file_path)).replace('/', '\\')
            else:
                file_path = str(Path(agent.file_path)).replace('\\', '/')
            
            report.append(f"   - 文件: {file_path}")
            report.append("")
        
        return "\n".join(report)
    
    def copy_to_clipboard(self, text: str) -> bool:
        """将文本复制到剪贴板（跨平台）"""
        try:
            if self.platform_info["system"] == "windows":
                import subprocess
                subprocess.run(['clip'], input=text.encode('utf-8'), check=True)
            elif self.platform_info["system"] == "darwin":
                import subprocess
                subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
            else:  # Linux
                try:
                    import subprocess
                    subprocess.run(['xclip', '-selection', 'clipboard'], 
                                 input=text.encode('utf-8'), check=True)
                except FileNotFoundError:
                    # 尝试使用 xsel
                    subprocess.run(['xsel', '--clipboard', '--input'], 
                                 input=text.encode('utf-8'), check=True)
            return True
        except Exception as e:
            self.print_message(f"WARNING: 复制到剪贴板失败: {e}")
            return False
    
    def generate_batch_script(self) -> str:
        """生成批处理脚本文件内容"""
        agents = self.discover_subagents()
        
        if not agents:
            return "# 未发现任何 subagent 定义文件"
        
        if self.platform_info["system"] == "windows":
            script_lines = [
                "@echo off",
                "echo SubAgent 自动安装脚本",
                "echo ================================",
                "echo 请确保已在 Claude Code 环境中运行此脚本",
                "pause",
                ""
            ]
            
            for agent in agents:
                description = agent.description.replace('"', '""')  # Windows batch 转义
                script_lines.append(f'echo 正在创建: {agent.name}')
                script_lines.append(f'claude agents create {agent.name} "{description}"')
                script_lines.append("echo.")
            
            script_lines.extend([
                "echo ================================",
                "echo 所有 SubAgent 创建完成！",
                "pause"
            ])
            
            return "\n".join(script_lines)
        
        else:  # Unix-like systems
            script_lines = [
                "#!/bin/bash",
                "echo 'SubAgent 自动安装脚本'",
                "echo '================================'",
                "echo '请确保已在 Claude Code 环境中运行此脚本'",
                "read -p '按 Enter 继续...'",
                ""
            ]
            
            for agent in agents:
                description = agent.description.replace("'", "'\"'\"'")  # Shell 转义
                script_lines.append(f"echo '正在创建: {agent.name}'")
                script_lines.append(f"claude agents create {agent.name} '{description}'")
                script_lines.append("echo")
            
            script_lines.extend([
                "echo '================================'",
                "echo '所有 SubAgent 创建完成！'",
                "read -p '按 Enter 退出...'"
            ])
            
            return "\n".join(script_lines)
    
    def find_claude_code_process(self) -> Optional[Dict]:
        """查找正在运行的Claude Code进程"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    name = proc_info['name'].lower()
                    cmdline = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                    
                    # 检测Claude Code相关进程
                    if ('claude' in name and 'code' in name) or \
                       ('claude-code' in name) or \
                       ('claude' in cmdline and 'code' in cmdline):
                        return {
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cmdline': cmdline
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return None
        except Exception as e:
            self.print_message(f"WARNING: 检测Claude Code进程失败: {e}")
            return None
    
    def check_claude_code_environment(self) -> bool:
        """检查是否在Claude Code环境中运行"""
        # 方法1: 检查环境变量
        claude_env_vars = [
            'CLAUDE_CODE', 'ANTHROPIC_API_KEY', 'CLAUDE_SESSION',
            'CLAUDE_WORKSPACE', 'CLAUDE_PROJECT'
        ]
        
        for env_var in claude_env_vars:
            if env_var in os.environ:
                self.print_message(f"检测到Claude Code环境变量: {env_var}")
                return True
        
        # 方法2: 检查Claude Code进程
        self.claude_process = self.find_claude_code_process()
        if self.claude_process:
            self.print_message(f"检测到Claude Code进程: {self.claude_process['name']} (PID: {self.claude_process['pid']})")
            return True
        
        # 方法3: 尝试调用claude命令
        try:
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.print_message("检测到claude命令行工具")
                return True
        except Exception:
            pass
        
        return False
    
    def execute_claude_command(self, command: str) -> bool:
        """执行Claude Code命令"""
        try:
            # 方法1: 直接调用claude命令
            cmd_parts = command.split()
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.print_message(f"✅ 命令执行成功: {command}")
                return True
            else:
                self.print_message(f"❌ 命令执行失败: {command}")
                self.print_message(f"错误信息: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.print_message(f"⏰ 命令执行超时: {command}")
            return False
        except Exception as e:
            self.print_message(f"❌ 命令执行异常: {command} - {e}")
            return False
    
    def install_agents_to_directory(self) -> Dict[str, bool]:
        """复制SubAgent文件到Claude Code目录"""
        agents = self.discover_subagents()
        results = {}
        
        if not agents:
            self.print_message("WARNING: 未发现任何 subagent 定义文件")
            return results
        
        # 确定Claude Code agents目录
        home_dir = Path.home()
        claude_agents_dir = home_dir / ".claude" / "agents"
        
        self.print_message(f"🚀 开始安装 {len(agents)} 个 SubAgent 到目录...")
        self.print_message(f"目标目录: {claude_agents_dir}")
        self.print_message("=" * 50)
        
        # 创建目录（如果不存在）
        try:
            claude_agents_dir.mkdir(parents=True, exist_ok=True)
            self.print_message(f"✅ Claude Code agents目录已准备: {claude_agents_dir}")
        except Exception as e:
            self.print_message(f"❌ 无法创建Claude Code目录: {e}")
            return results
        
        success_count = 0
        failed_count = 0
        
        for i, agent in enumerate(agents, 1):
            self.print_message(f"[{i}/{len(agents)}] 正在安装: {agent.name}")
            self.print_message(f"源文件: {agent.file_path}")
            
            try:
                source_file = Path(agent.file_path)
                target_file = claude_agents_dir / f"{agent.name}.md"
                
                # 检查是否已存在同名文件
                if target_file.exists():
                    self.print_message(f"⚠️  发现已存在文件，将进行覆盖: {target_file}")
                
                # 确保目标文件名规范化
                safe_name = agent.name.replace(' ', '-').replace('_', '-').lower()
                if safe_name != agent.name:
                    self.print_message(f"📝 文件名规范化: {agent.name} -> {safe_name}")
                    target_file = claude_agents_dir / f"{safe_name}.md"
                
                # 复制文件（覆盖模式）
                import shutil
                shutil.copy2(source_file, target_file)
                
                # 验证文件确实被写入
                if target_file.exists() and target_file.stat().st_size > 0:
                    results[agent.name] = True
                    success_count += 1
                    self.print_message(f"✅ {agent.name} 安装成功 -> {target_file}")
                    self.print_message(f"   文件大小: {target_file.stat().st_size} 字节")
                else:
                    results[agent.name] = False
                    failed_count += 1
                    self.print_message(f"❌ {agent.name} 安装失败: 文件验证失败")
                
            except Exception as e:
                results[agent.name] = False
                failed_count += 1
                self.print_message(f"❌ {agent.name} 安装失败: {e}")
            
            self.print_message("-" * 30)
        
        # 显示安装结果
        self.print_message("=" * 50)
        self.print_message(f"📊 复制完成统计:")
        self.print_message(f"✅ 成功: {success_count} 个")
        self.print_message(f"❌ 失败: {failed_count} 个")
        
        if success_count > 0:
            self.print_message("\n🎉 成功复制的 SubAgent:")
            for name, success in results.items():
                if success:
                    self.print_message(f"  - {name}")
            
            self.print_message(f"\n📁 SubAgent文件已复制到: {claude_agents_dir}")
            self.print_message("🔄 请重启Claude Code以加载新的SubAgent")
            self.print_message("🔍 然后可以使用 /agents 命令查看已安装的subagent")
        
        if failed_count > 0:
            self.print_message("\n⚠️ 复制失败的 SubAgent:")
            for name, success in results.items():
                if not success:
                    self.print_message(f"  - {name}")
        
        return results
    
    def clean_existing_agents(self) -> bool:
        """强力清理已安装的SubAgent文件和缓存"""
        home_dir = Path.home()
        claude_agents_dir = home_dir / ".claude" / "agents"
        
        if not claude_agents_dir.exists():
            self.print_message("📁 Claude Code agents目录不存在，无需清理")
            return True
        
        try:
            # 查找所有文件（不仅仅是.md）
            all_files = list(claude_agents_dir.glob("*"))
            
            if not all_files:
                self.print_message("📁 未发现已安装的文件，无需清理")
                return True
            
            self.print_message(f"🧹 发现 {len(all_files)} 个文件，准备强力清理...")
            
            cleaned_count = 0
            for file_path in all_files:
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        cleaned_count += 1
                        self.print_message(f"🗑️  已删除文件: {file_path.name}")
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                        cleaned_count += 1
                        self.print_message(f"🗑️  已删除目录: {file_path.name}")
                except Exception as e:
                    self.print_message(f"❌ 删除失败: {file_path.name} - {e}")
            
            # 额外等待，确保文件系统同步
            import time
            time.sleep(0.5)
            
            # 验证清理结果
            remaining_files = list(claude_agents_dir.glob("*"))
            if remaining_files:
                self.print_message(f"⚠️  仍有 {len(remaining_files)} 个文件未清理: {[f.name for f in remaining_files]}")
            else:
                self.print_message("✅ 目录已完全清理")
            
            self.print_message(f"✅ 强力清理完成，共删除 {cleaned_count} 个文件")
            
            # 尝试清理可能的Claude Code缓存目录
            self.clean_claude_cache()
            
            return True
            
        except Exception as e:
            self.print_message(f"❌ 清理过程中发生错误: {e}")
            return False
    
    def clean_claude_cache(self):
        """尝试清理Claude Code可能的缓存"""
        home_dir = Path.home()
        
        # 可能的Claude Code缓存目录
        potential_cache_dirs = [
            home_dir / ".claude" / "cache",
            home_dir / ".claude" / "tmp", 
            home_dir / ".claude" / ".cache",
            home_dir / "AppData" / "Local" / "Claude" / "cache" if self.platform_info["system"] == "windows" else None,
            home_dir / "Library" / "Caches" / "Claude" if self.platform_info["system"] == "darwin" else None,
            home_dir / ".cache" / "claude" if self.platform_info["system"] == "linux" else None
        ]
        
        cache_cleaned = False
        for cache_dir in potential_cache_dirs:
            if cache_dir and cache_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(cache_dir)
                    self.print_message(f"🧹 已清理缓存目录: {cache_dir}")
                    cache_cleaned = True
                except Exception as e:
                    self.print_message(f"⚠️  无法清理缓存目录 {cache_dir}: {e}")
        
        if not cache_cleaned:
            self.print_message("📝 未发现可清理的缓存目录")
        
        self.print_message("🔄 建议完全退出并重新启动Claude Code以清除内存缓存")

def main():
    """主函数（跨平台兼容）"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='SubAgent 安装助手 - 支持 Windows/macOS/Linux',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python subagent-installer.py                 # 自动安装（清理+安装，推荐）
  python subagent-installer.py --report        # 仅显示发现报告
  python subagent-installer.py --commands      # 仅显示创建命令
  python subagent-installer.py --copy          # 生成命令并复制到剪贴板
  python subagent-installer.py --install       # 仅安装（覆盖模式）
  python subagent-installer.py --clean         # 仅清理已安装的SubAgent
  python subagent-installer.py --platform      # 显示平台信息
        '''
    )
    parser.add_argument('--project-root', default='.', help='项目根目录路径')
    parser.add_argument('--commands', action='store_true', help='生成创建命令')
    parser.add_argument('--report', action='store_true', help='生成状态报告')
    parser.add_argument('--platform', action='store_true', help='显示平台信息')
    parser.add_argument('--install', action='store_true', help='复制SubAgent文件到Claude Code目录（推荐）')
    parser.add_argument('--copy', action='store_true', help='生成命令并复制到剪贴板')
    parser.add_argument('--batch', action='store_true', help='生成批处理脚本文件')
    parser.add_argument('--clean', action='store_true', help='清理已安装的SubAgent文件')
    
    args = parser.parse_args()
    
    try:
        helper = SubAgentHelper(args.project_root)
        
        if args.platform:
            # 显示平台信息
            info = helper.platform_info
            helper.print_message("# 平台信息")
            helper.print_message(f"操作系统: {info['platform']} ({info['system']})")
            helper.print_message(f"架构: {info['arch']} ({info['machine']})")
            helper.print_message(f"Python 版本: {info['python_version']}")
            helper.print_message(f"默认编码: {info['encoding']}")
            helper.print_message(f"项目根目录: {helper.project_root}")
            
        elif args.install:
            # 复制SubAgent文件到Claude Code目录
            helper.print_message("🚀 开始安装 SubAgent 到Claude Code目录...")
            results = helper.install_agents_to_directory()
            
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            if success_count == total_count and total_count > 0:
                helper.print_message(f"\n🎉 所有 {total_count} 个 SubAgent 安装成功！")
            elif success_count > 0:
                helper.print_message(f"\n⚠️  部分安装成功: {success_count}/{total_count}")
            else:
                helper.print_message(f"\n❌ 安装失败，请检查Claude Code环境")
                
        elif args.clean:
            # 清理已安装的SubAgent文件
            helper.print_message("🧹 开始清理已安装的 SubAgent...")
            if helper.clean_existing_agents():
                helper.print_message("✅ 清理操作完成")
            else:
                helper.print_message("❌ 清理操作失败")
                
        elif args.copy:
            # 生成命令并复制到剪贴板
            commands = helper.generate_creation_commands()
            helper.print_message("正在生成 SubAgent 创建命令...")
            helper.print_message(commands)
            
            if helper.copy_to_clipboard(commands):
                helper.print_message("\n✅ 创建命令已复制到剪贴板！")
                helper.print_message("请在 Claude Code 中粘贴并执行这些命令")
            else:
                helper.print_message("\n⚠️  自动复制失败，请手动复制上述命令")
                
        elif args.batch:
            # 生成批处理脚本文件
            script_content = helper.generate_batch_script()
            script_ext = ".bat" if helper.platform_info["system"] == "windows" else ".sh"
            script_name = f"install_subagents{script_ext}"
            
            with open(script_name, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            helper.print_message(f"✅ 批处理脚本已生成: {script_name}")
            helper.print_message("请在 Claude Code 环境中执行此脚本")
            
            if helper.platform_info["system"] != "windows":
                import os
                os.chmod(script_name, 0o755)
                helper.print_message(f"已设置执行权限: chmod +x {script_name}")
            
        elif args.commands:
            output = helper.generate_creation_commands()
            helper.print_message(output)
            
        elif args.report:
            output = helper.generate_status_report()
            helper.print_message(output)
            
        else:
            # 默认执行：先清理再安装
            helper.print_message("🚀 开始 SubAgent 自动化安装流程...")
            helper.print_message("=" * 60)
            
            # 步骤1: 清理已存在的SubAgent
            helper.print_message("📋 步骤1: 清理已安装的 SubAgent...")
            clean_success = helper.clean_existing_agents()
            
            if clean_success:
                helper.print_message("✅ 清理完成")
            else:
                helper.print_message("⚠️  清理过程中出现问题，但继续安装...")
            
            helper.print_message("\n" + "-" * 60)
            
            # 步骤2: 安装SubAgent
            helper.print_message("📋 步骤2: 安装 SubAgent 到Claude Code目录...")
            results = helper.install_agents_to_directory()
            
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            helper.print_message("\n" + "=" * 60)
            helper.print_message("📊 自动化安装流程完成")
            
            if success_count == total_count and total_count > 0:
                helper.print_message(f"🎉 所有 {total_count} 个 SubAgent 安装成功！")
                helper.print_message("🔄 请重启Claude Code以清除缓存并加载新的SubAgent")
                helper.print_message("🔍 然后可以使用 /agents 命令查看已安装的subagent")
                helper.print_message("⚠️  如果仍看到重复，请完全关闭并重新启动Claude Code")
            elif success_count > 0:
                helper.print_message(f"⚠️  部分安装成功: {success_count}/{total_count}")
            else:
                helper.print_message("❌ 安装失败，请检查权限和目录")
                
            helper.print_message(f"\n💡 下次更新时，直接运行: python {sys.argv[0]}")
            
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: 执行过程中发生错误: {e}")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()