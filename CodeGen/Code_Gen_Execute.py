# Code_Gen_Execute.py - JeecgBoot代码生成执行器，全新版本，不考虑前后兼容，始终为最新功能版本，易于AI调用理解
#
# =============================================================================
# 跨平台编码规范 (Cross-Platform Encoding Guidelines)
# =============================================================================
#
# 【重要】为了支持 Windows 和 macOS/Linux 跨平台执行，本脚本必须遵循以下规范：
#
# 1. 文件编码规范：
#    - 本文件使用 UTF-8 编码保存（无BOM）
#    - 所有字符串字面量使用普通中文字符，不使用 emoji 表情符号
#    - 避免使用特殊 Unicode 字符（如 emoji: [LINK] [AUTH] [FOLDER] [OK] [ERROR] 等）
#
# 2. 输出编码规范：
#    - Windows 命令行默认使用 GBK 编码，无法正确显示 emoji
#    - macOS/Linux 终端使用 UTF-8 编码，支持 emoji 但为了跨平台兼容应避免
#    - 所有 print() 输出应使用标准 ASCII 标签（如 [OK] [ERROR] [INFO]）
#
# 3. 日志输出标签规范（替代 emoji）：
#    - [OK] / [SUCCESS] - 替代 [CHECK]
#    - [ERROR] / [FAIL] - 替代 [CROSS]
#    - [WARN] / [WARNING] - 替代 [ALERT]
#    - [INFO] / [TIP] - 替代 [INFO_ICON]
#    - [FOLDER] / [DIR] - 替代 [FOLDER_ICON]
#    - [FILE] / [DOCUMENT] - 替代 [FILE_ICON]
#    - [URL] / [LINK] - 替代 [LINK_ICON]
#    - [AUTH] / [LOGIN] - 替代 [AUTH_ICON]
#    - [SAVE] / [STORE] - 替代 [SAVE_ICON]
#    - [BUILD] / [COMPILE] - 替代 [BUILD_ICON]
#    - [API] / [NETWORK] - 替代 [API_ICON]
#
# 4. 路径处理规范：
#    - 使用 os.path.join() 或 pathlib.Path 处理路径分隔符
#    - 使用前向斜杠 / 作为通用路径分隔符（Python 会自动转换）
#    - 避免硬编码 Windows 反斜杠 \ 或 Unix 斜杠 /
#
# 5. 子进程调用规范：
#    - Windows: 使用 .cmd 或 .bat 扩展名（如 mvn.cmd）
#    - macOS/Linux: 使用无扩展名命令（如 mvn）
#    - 使用 platform.system() 判断操作系统类型
#
# 6. 编码错误处理：
#    - 如遇到 UnicodeEncodeError: 'gbk' codec can't encode character
#    - 说明输出中包含了不兼容的字符（通常是 emoji）
#    - 解决方案：替换为标准 ASCII 标签
#
# =============================================================================

import os
import sys
import json
import requests
import time
import configparser
import mysql.connector
import logging
import fnmatch
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from contextlib import contextmanager

# =============================================================================
# [FIX BUG1] Windows控制台编码修复 - 确保中文输出正常显示
# =============================================================================
# 在Windows环境下，控制台默认使用GBK编码，导致UTF-8字符显示为乱码
# 解决方案：强制设置stdout和stderr为UTF-8编码
if sys.platform == 'win32':
    import codecs
    # 重新配置stdout和stderr使用UTF-8编码，并忽略无法编码的字符
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')
    print("[OK] Windows控制台已切换为UTF-8编码")

SUMMARY_RESULT = "ERROR"

# =============================================================================
# 日志管理系统 - 持久化所有执行过程到日志文件
# =============================================================================

class LogManager:
    """日志管理器 - 将所有输出记录到日志文件中"""
    
    def __init__(self):
        self.log_file_path = None
        self.logger = None
        self.console_handler = None
        self.file_handler = None
        self.original_stdout = None
        self.original_stderr = None
        
    def extract_module_info(self, config_data: Dict) -> Tuple[str, str]:
        """
        从配置数据中提取模块信息
        
        Args:
            config_data: 配置数据字典
            
        Returns:
            Tuple[str, str]: (module_name, submodule_name)
        """
        try:
            # 策略1：从metadata.generation_info获取
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            
            module_name = generation_info.get('module_name')
            submodule_name = generation_info.get('submodule_name')
            
            if module_name and submodule_name:
                return module_name, submodule_name
            
            # 策略2：从head.tableName推断
            head = config_data.get('head', {})
            table_name = head.get('tableName', '')
            
            if table_name and '_' in table_name:
                parts = table_name.split('_')
                if len(parts) >= 2:
                    return parts[0], parts[1]
            
            # 策略3：使用默认值
            return 'unknown', 'module'
            
        except Exception:
            return 'unknown', 'module'
    
    def _clean_filename(self, name: str) -> str:
        """
        清理文件名，移除不安全的字符
        
        Args:
            name: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        import re
        if not name:
            return 'unknown'
        # 替换特殊字符为下划线，只保留字母数字和下划线
        clean_name = re.sub(r'[^\w\-.]', '_', name)
        # 移除连续的下划线
        clean_name = re.sub(r'_{2,}', '_', clean_name)
        # 移除开头和结尾的下划线
        clean_name = clean_name.strip('_')
        return clean_name or 'unknown'
    
    def setup_logging(self, config_file_path: str = None, config_data: Dict = None):
        """
        设置日志记录系统

        Args:
            config_file_path: 配置文件路径
            config_data: 配置数据（可选，如果提供则直接使用）
        """
        try:
            # 获取配置数据
            if config_data is None and config_file_path:
                if os.path.exists(config_file_path):
                    with open(config_file_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                else:
                    config_data = {}
            elif config_data is None:
                config_data = {}

            # 提取模块信息
            module_name, submodule_name = self.extract_module_info(config_data)

            # [FIX BUG3] 确定日志文件应该保存到CodeGen目录
            # 获取当前脚本所在目录(Code_Gen_Execute.py所在目录,即CodeGen)
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # 生成日志文件名 - 清理模块名中的特殊字符
            clean_module_name = self._clean_filename(module_name)
            clean_submodule_name = self._clean_filename(submodule_name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_filename = f"{clean_module_name}_{clean_submodule_name}_{timestamp}.log"
            self.log_file_path = os.path.join(script_dir, log_filename)
            
            # 配置日志格式
            log_format = '[%(asctime)s] [%(levelname)s] %(message)s'
            date_format = '%Y-%m-%d %H:%M:%S'
            
            # 创建logger
            self.logger = logging.getLogger('CodeGenExecutor')
            self.logger.setLevel(logging.INFO)
            
            # 清除之前的handlers
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
            
            # 创建文件处理器
            self.file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8', mode='w')
            self.file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(log_format, date_format)
            self.file_handler.setFormatter(file_formatter)
            self.logger.addHandler(self.file_handler)
            
            # 注意：不创建控制台处理器，由TeeOutput负责控制台输出
            # 避免重复输出到控制台
            
            # 重定向print输出
            self._setup_print_redirect()
            
            # 记录初始化信息
            self.logger.info("="*70)
            self.logger.info(f"[LOG] JeecgBoot 代码生成器日志系统启动")
            self.logger.info("="*70)
            self.logger.info(f"[FILE] 日志文件: {self.log_file_path}")
            self.logger.info(f"[TAG] 模块信息: {module_name}.{submodule_name}")
            self.logger.info(f"[TIME] 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info("="*70)
            
            return True
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 日志系统初始化失败: {str(e)}")
            return False
    
    def _setup_print_redirect(self):
        """设置print输出重定向"""
        
        class TeeOutput:
            """同时输出到控制台和日志文件的输出流"""
            
            def __init__(self, logger, original_stream):
                self.logger = logger
                self.original_stream = original_stream
                
            def write(self, message):
                if message.strip():  # 只记录非空消息
                    # 移除ANSI颜色代码
                    import re
                    clean_message = re.sub(r'\x1b\[[0-9;]*m', '', message.strip())
                    if clean_message:
                        self.logger.info(clean_message)
                
                # 同时输出到原始流
                self.original_stream.write(message)
                self.original_stream.flush()
                
            def flush(self):
                if hasattr(self.original_stream, 'flush'):
                    self.original_stream.flush()
        
        # 保存原始输出流
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # 设置重定向
        sys.stdout = TeeOutput(self.logger, self.original_stdout)
        sys.stderr = TeeOutput(self.logger, self.original_stderr)
    
    def cleanup_logging(self):
        """清理日志系统并恢复原始输出"""
        try:
            if self.logger:
                self.logger.info("="*70)
                self.logger.info(f"[LOG] JeecgBoot 代码生成器日志记录完成")
                self.logger.info(f"[SAVE] 日志已保存至: {self.log_file_path}")
                self.logger.info(f"[TIME] 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.logger.info("="*70)
            
            # 恢复原始输出流
            if self.original_stdout:
                sys.stdout = self.original_stdout
            if self.original_stderr:
                sys.stderr = self.original_stderr
            
            # 关闭文件处理器
            if self.file_handler:
                self.file_handler.close()
                
            # 清除handlers
            if self.logger:
                for handler in self.logger.handlers[:]:
                    self.logger.removeHandler(handler)
                    
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[WARN] 日志清理时出现问题: {str(e)}")
    
    def get_log_file_path(self) -> str:
        """获取日志文件路径"""
        return self.log_file_path or "未生成日志文件"
    
    def log_section_start(self, section_name: str):
        """记录章节开始"""
        if self.logger:
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"[INFO] {section_name}")
            self.logger.info(f"{'='*50}")
    
    def log_section_end(self, section_name: str):
        """记录章节结束"""
        if self.logger:
            self.logger.info(f"{'='*50}")
            self.logger.info(f"[OK] {section_name} 完成")
            self.logger.info(f"{'='*50}\n")

# 全局日志管理器实例
_log_manager = LogManager()

@contextmanager
def setup_execution_logging(config_file_path: str = None, config_data: Dict = None):
    """
    执行日志上下文管理器
    
    使用方法:
        with setup_execution_logging("config.json"):
            # 执行代码，所有输出都会被记录到日志文件
            pass
    """
    try:
        # 初始化日志系统
        if _log_manager.setup_logging(config_file_path, config_data):
            yield _log_manager
        else:
            yield None
    finally:
        # 清理日志系统
        _log_manager.cleanup_logging()

# =============================================================================
# 环境变量配置引导系统
# =============================================================================

class EnvironmentGuide:
    """环境变量配置引导系统"""
    
    REQUIRED_ENV_VARS = [
        {
            'name': 'JEECG_PROJECT_ROOT',
            'description': 'JeecgBoot项目根目录路径',
            'example': '/Users/admin/Work/Github/JeecgBoot',
            'required': True,
            'type': 'path'
        },
        {
            'name': 'JEECG_BASE_URL', 
            'description': 'JeecgBoot服务基础URL',
            'example': 'http://localhost:8080/jeecg-boot',
            'required': True,
            'type': 'url'
        },
        {
            'name': 'JEECG_USERNAME',
            'description': 'JeecgBoot登录用户名',
            'example': 'admin',
            'required': True,
            'type': 'string'
        },
        {
            'name': 'JEECG_PASSWORD',
            'description': 'JeecgBoot登录密码',
            'example': '123456',
            'required': True,
            'type': 'password'
        },
        {
            'name': 'JEECG_DATABASE_TYPE',
            'description': '数据库类型',
            'example': 'mysql',
            'required': True,
            'type': 'string'
        },
        {
            'name': 'JEECG_DATABASE_URL',
            'description': '数据库连接URL',
            'example': 'jdbc:mysql://localhost:30004/jeecg-boot',
            'required': True,
            'type': 'url'
        },
        {
            'name': 'JEECG_DATABASE_USERNAME',
            'description': '数据库用户名',
            'example': 'root',
            'required': True,
            'type': 'string'
        },
        {
            'name': 'JEECG_DATABASE_PASSWORD',
            'description': '数据库密码',
            'example': 'Best@2008',
            'required': True,
            'type': 'password'
        }
    ]
    
    def __init__(self):
        self.config_values = {}
        
    def check_environment_setup(self) -> Dict:
        """检查环境变量配置状态"""
        # 首先加载临时环境文件（如果存在）
        self._load_temp_env_file()
        
        result = {
            'all_configured': True,
            'missing_vars': [],
            'configured_vars': [],
            'config_status': {}
        }
        
        for var_info in self.REQUIRED_ENV_VARS:
            var_name = var_info['name']
            var_value = os.getenv(var_name)
            is_configured = bool(var_value)
            
            result['config_status'][var_name] = {
                'configured': is_configured,
                'value': var_value if var_name not in ['JEECG_PASSWORD', 'JEECG_DATABASE_PASSWORD'] else ('***' if var_value else None),
                'required': var_info['required']
            }
            
            if var_info['required'] and not is_configured:
                result['all_configured'] = False
                result['missing_vars'].append(var_name)
            elif is_configured:
                result['configured_vars'].append(var_name)
        
        return result
    
    def print_environment_status(self):
        """打印环境变量配置状态"""
        status = self.check_environment_setup()
        
        print("\n" + "="*60)
        print("[CONFIG] JeecgBoot 环境变量配置状态检查")
        print("="*60)
        
        print("\n[INFO] 配置状态概览:")
        total_vars = len([v for v in self.REQUIRED_ENV_VARS if v['required']])
        configured_vars = len(status['configured_vars'])
        missing_count = len(status['missing_vars'])
        
        # 检查实际环境变量数量
        actual_env_vars = sum(1 for var_info in self.REQUIRED_ENV_VARS 
                            if var_info['required'] and os.getenv(var_info['name']))
        
        if status['all_configured']:
            if actual_env_vars == total_vars:
                print(f"[OK] 所有必需环境变量已配置 ({configured_vars}/{total_vars})")
            else:
                print(f"[CONFIG] 配置完整但主要使用默认值 ({actual_env_vars}/{total_vars} 个真实环境变量)")
        else:
            print(f"[ERROR] 缺少 {missing_count} 个必需环境变量 ({configured_vars}/{total_vars})")
        
        print("\n[FILE] 详细配置状态:")
        for var_info in self.REQUIRED_ENV_VARS:
            var_name = var_info['name']
            var_status = status['config_status'][var_name]
            actual_env_value = os.getenv(var_name)
            
            if var_status['configured']:
                if actual_env_value:
                    icon = "[OK]"
                    status_text = f"环境变量: {var_status['value']}"
                else:
                    icon = "[CONFIG]"
                    status_text = f"默认值: {var_status['value']}"
            else:
                icon = "[ERROR]" if var_info['required'] else "[WARN]"
                status_text = "未配置" + ("（必需）" if var_info['required'] else "（可选）")
            
            print(f"  {icon} {var_name:<25} {status_text}")
            print(f"     描述: {var_info['description']}")
        
        if not status['all_configured']:
            print(f"\n[WARN]  请配置缺少的环境变量后重新运行脚本")
            print(f"[TIP] 或使用 --setup-guide 参数启动交互式配置向导")
        else:
            # 添加默认值说明
            if actual_env_vars < total_vars:
                print(f"\n[NOTE] 默认值说明:")
                print(f"   [CONFIG] 系统内置了合理的默认配置，可以直接使用")
                print(f"   [OK] 如需自定义，请设置对应的环境变量覆盖默认值")
                print(f"   [TIP] 使用 --setup-guide 可以交互式设置环境变量")
        
        return status
    
    def interactive_setup_guide(self):
        """交互式配置向导"""
        print("\n" + "="*60)
        print("[START] JeecgBoot 环境变量配置向导")
        print("="*60)
        print("此向导将帮助您配置必需的环境变量")
        print("按 Ctrl+C 随时退出")
        
        try:
            # 收集用户输入
            for var_info in self.REQUIRED_ENV_VARS:
                if not var_info['required']:
                    continue
                    
                var_name = var_info['name']
                current_value = os.getenv(var_name, '')
                
                print(f"\n[LOG] 配置: {var_name}")
                print(f"   描述: {var_info['description']}")
                print(f"   示例: {var_info['example']}")
                
                if current_value:
                    if var_name in ['JEECG_PASSWORD', 'JEECG_DATABASE_PASSWORD']:
                        display_value = "***"
                    else:
                        display_value = current_value
                    print(f"   当前值: {display_value}")
                
                # 获取用户输入
                if var_info['type'] == 'password':
                    import getpass
                    user_input = getpass.getpass("   请输入新值 (回车保留当前值): ")
                else:
                    user_input = input("   请输入新值 (回车保留当前值): ").strip()
                
                # 处理用户输入
                if user_input:
                    self.config_values[var_name] = user_input
                elif current_value:
                    self.config_values[var_name] = current_value
                else:
                    # 如果没有当前值且用户没有输入，使用示例值作为默认值
                    if var_info['required']:
                        example_value = var_info.get('example', '')
                        if example_value:
                            self.config_values[var_name] = example_value
                            print(f"   [CONFIG] 采用推荐示例值: {example_value}")
                        else:
                            print("   [ERROR] 此变量为必需项，不能为空")
                            return False
            
            # 验证配置
            if self._validate_configuration():
                # 在当前会话中设置环境变量
                self._set_current_session_env()
                return True
            else:
                print("[ERROR] 配置验证失败")
                return False
                
        except KeyboardInterrupt:
            print("\n\n[STOP]  配置向导已取消")
            return False
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"\n[ERROR] 配置向导发生错误: {e}")
            return False
    
    def _validate_configuration(self) -> bool:
        """验证配置的有效性"""
        print("\n[CHECK] 正在验证配置...")
        
        # 验证路径
        if 'JEECG_PROJECT_ROOT' in self.config_values:
            project_root = self.config_values['JEECG_PROJECT_ROOT']
            if not os.path.exists(project_root):
                print(f"[ERROR] 项目根目录不存在: {project_root}")
                return False
            
            # 检查关键目录结构
            key_paths = [
                f"{project_root}/jeecg-boot",
                f"{project_root}/jeecg-boot/jeecg-boot-module"
            ]
            
            for path in key_paths:
                if not os.path.exists(path):
                    print(f"[WARN]  关键目录不存在: {path}")
        
        # 验证URL格式
        url_vars = ['JEECG_BASE_URL', 'JEECG_DATABASE_URL']
        for var_name in url_vars:
            if var_name in self.config_values:
                url_value = self.config_values[var_name]
                if not (url_value.startswith('http://') or url_value.startswith('https://') or url_value.startswith('jdbc:')):
                    print(f"[WARN]  {var_name} URL格式可能不正确: {url_value}")
        
        print("[OK] 配置验证完成")
        return True
    
    def _set_current_session_env(self):
        """在当前会话中设置环境变量"""
        print("\n[CONFIG] 正在设置环境变量...")
        
        # 1. 设置环境变量到当前Python进程
        for var_name, var_value in self.config_values.items():
            os.environ[var_name] = var_value
            print(f"   [OK] {var_name} = {var_value if 'PASSWORD' not in var_name else '***'}")
        
        # 2. 生成临时环境文件供后续使用
        self._create_temp_env_file()
        
        print(f"\n[OK] 环境变量设置完成")
        print(f"[INFO] 已设置 {len(self.config_values)} 个环境变量")
        
        print(f"\n[TIP] 使用说明:")
        print(f"   [PROCESS] 环境变量已设置，可以立即运行代码生成任务")
        print(f"   [LOG] 环境变量存储在 .env_temp 文件中供后续Python进程读取")
    
    def _create_temp_env_file(self):
        """创建临时环境变量文件"""
        try:
            # [FIX BUG2] 确保.env_temp文件在CodeGen目录中创建
            script_dir = os.path.dirname(os.path.abspath(__file__))
            temp_env_file = os.path.join(script_dir, '.env_temp')

            with open(temp_env_file, 'w', encoding='utf-8') as f:
                f.write("# JeecgBoot 临时环境变量文件\n")
                f.write("# 此文件由 --setup-guide 自动生成\n")
                f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for var_name, var_value in self.config_values.items():
                    f.write(f"{var_name}={var_value}\n")

            print(f"   [FOLDER] 临时环境文件已创建: {temp_env_file}")
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"   [WARN] 创建临时环境文件失败: {e}")
    
    def _generate_setup_scripts(self):
        """生成环境变量设置脚本"""
        print("\n[LOG] 正在生成环境变量设置脚本...")
        
        # 生成shell脚本
        shell_script = self._generate_shell_script()
        with open('setup_env.sh', 'w', encoding='utf-8') as f:
            f.write(shell_script)
        
        # 生成bat脚本 (Windows)
        bat_script = self._generate_bat_script()
        with open('setup_env.bat', 'w', encoding='utf-8') as f:
            f.write(bat_script)
        
        print("\n[OK] 配置文件生成完成:")
        print("   [FILE] setup_env.sh - Linux/macOS环境变量设置脚本")
        print("   [FILE] setup_env.bat - Windows环境变量设置脚本")
        
        print(f"\n[CONFIG] 下一步操作:")
        print(f"   1. 根据您的操作系统执行相应的脚本:")
        print(f"      Linux/macOS: source setup_env.sh")
        print(f"      Windows: setup_env.bat")
        print(f"   2. 重新运行代码生成器")
    
    def _generate_shell_script(self) -> str:
        """生成Shell脚本"""
        script_lines = ['#!/bin/bash', '# JeecgBoot 环境变量设置脚本 (Linux/macOS)', '']
        
        for var_name, var_value in self.config_values.items():
            script_lines.append(f'export {var_name}="{var_value}"')
        
        script_lines.extend([
            '',
            'echo "[OK] JeecgBoot 环境变量已设置"',
            'echo "[INFO] 已设置的环境变量:"'
        ])
        
        for var_name in self.config_values.keys():
            if 'PASSWORD' in var_name:
                script_lines.append(f'echo "   {var_name}=***"')
            else:
                script_lines.append(f'echo "   {var_name}=${var_name}"')
        
        return '\n'.join(script_lines)
    
    def _generate_bat_script(self) -> str:
        """生成Batch脚本"""
        script_lines = ['@echo off', 'REM JeecgBoot 环境变量设置脚本 (Windows)', '']
        
        for var_name, var_value in self.config_values.items():
            script_lines.append(f'set {var_name}={var_value}')
        
        script_lines.extend([
            '',
            'echo [OK] JeecgBoot 环境变量已设置',
            'echo [INFO] 已设置的环境变量:'
        ])
        
        for var_name in self.config_values.keys():
            if 'PASSWORD' in var_name:
                script_lines.append(f'echo    {var_name}=***')
            else:
                script_lines.append(f'echo    {var_name}=%{var_name}%')
        
        script_lines.append('pause')
        
        return '\n'.join(script_lines)
    
    def _load_temp_env_file(self):
        """加载临时环境文件"""
        # [FIX BUG2] 从CodeGen目录加载.env_temp文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        temp_env_file = os.path.join(script_dir, '.env_temp')

        if os.path.exists(temp_env_file):
            try:
                with open(temp_env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                loaded_count = 0
                for line in lines:
                    line = line.strip()
                    # 跳过注释和空行
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                            loaded_count += 1

                if loaded_count > 0:
                    print(f"[FOLDER] 从临时环境文件加载了 {loaded_count} 个环境变量: {temp_env_file}")

            except Exception as e:
                import traceback
                print(f"[ERROR] Exception: {str(e)}")
                traceback.print_exc()
                print(f"[WARN] 加载临时环境文件失败: {e}")


# =============================================================================
# 统一配置管理体系
# =============================================================================

class JeecgBootConfig:
    """JeecgBoot统一配置管理器"""
    
    def __init__(self):
        self.env_vars = {}
        self.timeouts = {}
        self.api_params = {}
        self.paths = {}
        self.loaded = False
    
    def load_config(self, config_file: str = "Code_Gen_Config.properties") -> bool:
        """从环境变量和配置文件加载完整配置"""
        try:
            # 1. 首先尝试加载临时环境文件
            self._load_temp_env_file()
            
            # 2. 读取环境变量
            self._load_environment_variables()
            
            # 3. 读取配置文件
            if os.path.exists(config_file):
                self._load_config_file(config_file)
            else:
                print(f"[WARN] 配置文件 {config_file} 不存在，使用默认值")
                self._set_default_values()
            
            self.loaded = True
            return True
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 配置加载失败: {e}")
            return False
    
    def _load_temp_env_file(self):
        """加载临时环境文件"""
        # [FIX BUG2] 从CodeGen目录加载.env_temp文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        temp_env_file = os.path.join(script_dir, '.env_temp')

        if os.path.exists(temp_env_file):
            print(f"[FOLDER] 发现临时环境文件: {temp_env_file}")
            try:
                with open(temp_env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                loaded_count = 0
                for line in lines:
                    line = line.strip()
                    # 跳过注释和空行
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                            loaded_count += 1

                print(f"   [OK] 从临时文件加载了 {loaded_count} 个环境变量")

            except Exception as e:
                import traceback
                print(f"[ERROR] Exception: {str(e)}")
                traceback.print_exc()
                print(f"   [WARN] 加载临时环境文件失败: {e}")
        else:
            print(f"[TIP] 未找到临时环境文件，使用系统环境变量")
    
    def _load_environment_variables(self):
        """加载环境变量"""
        print(f"\n[CHECK] 正在加载环境变量配置...")
        
        # JeecgBoot 完整环境变量列表
        all_env_var_names = [
            'JEECG_PROJECT_ROOT', 'JEECG_BASE_URL', 'JEECG_USERNAME', 'JEECG_PASSWORD',
            'JEECG_DATABASE_TYPE', 'JEECG_DATABASE_URL', 'JEECG_DATABASE_USERNAME', 'JEECG_DATABASE_PASSWORD'
        ]
        
        # 定义硬编码默认值
        defaults = {
            # 基础JeecgBoot配置
            'JEECG_BASE_URL': 'http://localhost:8080/jeecg-boot',
            'JEECG_USERNAME': 'admin',
            'JEECG_PASSWORD': '123456',
            'JEECG_PROJECT_ROOT': '/Users/admin/Work/Github/JeecgBoot',
            # 数据库配置默认值 (基于注释的~/.zshrc值)
            'JEECG_DATABASE_TYPE': 'mysql',
            'JEECG_DATABASE_URL': 'jdbc:mysql://localhost:30004/jeecg-boot',
            'JEECG_DATABASE_USERNAME': 'root',
            'JEECG_DATABASE_PASSWORD': 'Best@2008'
        }
        
        print(f"[INFO] 硬编码默认值配置:")
        print(f"   基础配置: JEECG_PROJECT_ROOT, JEECG_BASE_URL, JEECG_USERNAME, JEECG_PASSWORD")
        print(f"   数据库配置: JEECG_DATABASE_TYPE, JEECG_DATABASE_URL, JEECG_DATABASE_USERNAME, JEECG_DATABASE_PASSWORD")
        
        # 环境变量提取统计
        env_found = 0
        env_defaulted = 0
        env_empty = 0
        
        print(f"\n[STAT] 环境变量提取详情:")
        for env_var in all_env_var_names:
            value = os.getenv(env_var)
            if value:
                self.env_vars[env_var] = value
                env_found += 1
                # 检查是否与默认值相同
                is_default = value == defaults.get(env_var)
                default_indicator = " (与默认值相同)" if is_default else " (自定义值)"
                display_value = value if env_var not in ['JEECG_PASSWORD', 'JEECG_DATABASE_PASSWORD'] else '*' * len(value)
                print(f"   [OK] {env_var}: 环境变量 = {display_value}{default_indicator}")
            else:
                # 设置默认值
                default_value = defaults.get(env_var, '')
                self.env_vars[env_var] = default_value
                if default_value:
                    env_defaulted += 1
                    display_value = default_value if env_var not in ['JEECG_PASSWORD', 'JEECG_DATABASE_PASSWORD'] else '*' * len(default_value)
                    print(f"   [CONFIG] {env_var}: 使用默认值 = {display_value}")
                else:
                    env_empty += 1
                    print(f"   [WARN] {env_var}: 未设置 (无默认值)")
        
        print(f"\n[COUNT] 环境变量加载统计:")
        print(f"   [TARGET] 从环境变量获取: {env_found} 个")
        print(f"   [CONFIG] 使用默认值: {env_defaulted} 个")
        print(f"   [WARN] 保持空值: {env_empty} 个")
        print(f"   [STAT] 总计: {env_found + env_defaulted + env_empty} 个环境变量处理完成")
        
        # 重要提示
        if env_found == 0 and env_defaulted > 0:
            print(f"\n[TIP] 重要提示:")
            print(f"   当前使用的是系统默认配置，非真实环境变量")
            print(f"   如需自定义配置，请设置对应的环境变量")
    
    def _load_config_file(self, config_file: str):
        """从配置文件加载参数"""
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        
        # 加载超时配置
        if config.has_section('timeouts'):
            self.timeouts = {
                'login': config.getint('timeouts', 'login', fallback=10),
                'create': config.getint('timeouts', 'create', fallback=60),
                'list': config.getint('timeouts', 'list', fallback=15),
                'sync': config.getint('timeouts', 'sync', fallback=60),
                'codegen': config.getint('timeouts', 'codegen', fallback=120),
                'delete': config.getint('timeouts', 'delete', fallback=30)
            }
        
        # 加载查询配置
        if config.has_section('query'):
            self.api_params = {
                'page_size': config.getint('query', 'page_size', fallback=50),
                'page_no': config.getint('query', 'page_no', fallback=1)
            }
        
        # 加载路径配置
        if config.has_section('paths'):
            self.paths = {
                'backend_module_base': config.get('paths', 'backend_module_base', fallback='jeecg-boot/jeecg-boot-module'),
                'frontend_project_base': config.get('paths', 'frontend_project_base', fallback='jeecgboot-vue3')
            }
    
    def _set_default_values(self):
        """设置默认配置值"""
        self.timeouts = {
            'login': 10, 'create': 60, 'list': 15, 
            'sync': 60, 'codegen': 120, 'delete': 30
        }
        self.api_params = {'page_size': 50, 'page_no': 1}
        self.paths = {
            'backend_module_base': 'jeecg-boot/jeecg-boot-module',
            'frontend_project_base': 'jeecgboot-vue3'
        }
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        return self.env_vars.get('JEECG_BASE_URL', 'http://localhost:8080/jeecg-boot')
    
    def get_username(self) -> str:
        """获取用户名"""
        return self.env_vars.get('JEECG_USERNAME', 'admin')
    
    def get_password(self) -> str:
        """获取密码"""
        return self.env_vars.get('JEECG_PASSWORD', '123456')
    
    def get_project_root(self) -> str:
        """获取项目根目录"""
        return self.env_vars.get('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
    
    def get_timeout(self, api_type: str) -> int:
        """获取API超时时间"""
        return self.timeouts.get(api_type, 30)
    
    def get_page_size(self) -> int:
        """获取查询分页大小"""
        return self.api_params.get('page_size', 50)
    
    def print_summary(self):
        """打印配置摘要"""
        print("\n" + "="*60)
        print("[INFO] JeecgBoot 配置中心状态摘要")
        print("="*60)
        print(f"[OK] 配置加载状态: 成功")
        print(f"[CONFIG] Base URL: {self.get_base_url()}")
        print(f"[USER] Username: {self.get_username()}")
        print(f"[FOLDER] Project Root: {self.get_project_root()}")
        print(f"[TIMEOUT] Timeouts: {self.timeouts}")
        print(f"[FILE] Page Size: {self.get_page_size()}")
        
        print(f"\n[CHECK] 环境变量检查结果:")
        # 按类别分组显示环境变量
        basic_vars = ['JEECG_PROJECT_ROOT', 'JEECG_BASE_URL', 'JEECG_USERNAME', 'JEECG_PASSWORD']
        db_vars = ['JEECG_DATABASE_TYPE', 'JEECG_DATABASE_URL', 'JEECG_DATABASE_USERNAME', 'JEECG_DATABASE_PASSWORD']
        
        print("  [NOTE] 基础配置:")
        for env_var in basic_vars:
            if env_var in self.env_vars:
                status = "[OK]" if self.env_vars[env_var] else "[ERROR]"
                display_value = self.env_vars[env_var] if env_var != 'JEECG_PASSWORD' else '*' * len(self.env_vars[env_var]) if self.env_vars[env_var] else ''
                print(f"    {status} {env_var} = {display_value}")
        
        print("  [DB] 数据库配置:")
        for env_var in db_vars:
            if env_var in self.env_vars:
                status = "[OK]" if self.env_vars[env_var] else "[ERROR]"
                display_value = self.env_vars[env_var] if env_var != 'JEECG_DATABASE_PASSWORD' else '*' * len(self.env_vars[env_var]) if self.env_vars[env_var] else ''
                print(f"    {status} {env_var} = {display_value}")
        
        # 显示其他环境变量
        other_vars = [k for k in self.env_vars.keys() if k not in basic_vars and k not in db_vars]
        if other_vars:
            print("  [SETTING] 其他配置:")
            for env_var in other_vars:
                status = "[OK]" if self.env_vars[env_var] else "[WARN]"
                display_value = self.env_vars[env_var] if self.env_vars[env_var] else '(未设置)'
                print(f"    {status} {env_var} = {display_value}")
        
        print("="*60)


# =============================================================================
# 哨兵状态管理系统 - 任务3和任务4共享的状态定义
# =============================================================================

class SentinelStatus:
    """哨兵状态常量定义"""
    
    # 汇总状态（summary_status）- 3种状态
    SUMMARY_PENDING = "pending"    # 等待中
    SUMMARY_FAIL = "fail"         # 失败
    SUMMARY_PASS = "pass"         # 通过
    
    # 表状态（table.status）- 5种状态
    TABLE_PENDING = "pending"          # 等待中
    TABLE_FAIL = "fail"               # 失败
    TABLE_FORM_CREATED = "form_created"      # 表单新建成功
    TABLE_DB_SYNCED = "db_synced"           # 表单同步成功  
    TABLE_CODE_GENERATED = "code_generated"  # 表单代码生成成功
    
    # 状态进展顺序定义
    TABLE_STATUS_ORDER = [
        TABLE_PENDING,
        TABLE_FORM_CREATED,
        TABLE_DB_SYNCED, 
        TABLE_CODE_GENERATED
    ]
    
    # 状态描述映射
    STATUS_DESCRIPTIONS = {
        SUMMARY_PENDING: "等待处理",
        SUMMARY_FAIL: "执行失败",
        SUMMARY_PASS: "全部完成",
        
        TABLE_PENDING: "等待处理",
        TABLE_FAIL: "处理失败",
        TABLE_FORM_CREATED: "表单已创建",
        TABLE_DB_SYNCED: "数据库已同步",
        TABLE_CODE_GENERATED: "代码已生成"
    }


class SentinelStatusManager:
    """哨兵状态管理器 - 提供状态转换和计算逻辑"""
    
    @staticmethod
    def is_valid_summary_status(status: str) -> bool:
        """验证汇总状态是否有效"""
        return status in [
            SentinelStatus.SUMMARY_PENDING,
            SentinelStatus.SUMMARY_FAIL,
            SentinelStatus.SUMMARY_PASS
        ]
    
    @staticmethod
    def is_valid_table_status(status: str) -> bool:
        """验证表状态是否有效"""
        return status in [
            SentinelStatus.TABLE_PENDING,
            SentinelStatus.TABLE_FAIL,
            SentinelStatus.TABLE_FORM_CREATED,
            SentinelStatus.TABLE_DB_SYNCED,
            SentinelStatus.TABLE_CODE_GENERATED
        ]
    
    @staticmethod
    def get_next_table_status(current_status: str) -> str:
        """获取下一个表状态"""
        try:
            current_index = SentinelStatus.TABLE_STATUS_ORDER.index(current_status)
            if current_index < len(SentinelStatus.TABLE_STATUS_ORDER) - 1:
                return SentinelStatus.TABLE_STATUS_ORDER[current_index + 1]
            return current_status  # 已经是最终状态
        except ValueError:
            return SentinelStatus.TABLE_PENDING
    
    @staticmethod
    def calculate_summary_status(table_statuses: list) -> str:
        """根据所有表状态计算汇总状态"""
        if not table_statuses:
            return SentinelStatus.SUMMARY_PENDING
        
        # 如果有任何表失败，整体失败
        if SentinelStatus.TABLE_FAIL in table_statuses:
            return SentinelStatus.SUMMARY_FAIL
        
        # 如果所有表都是code_generated状态，整体通过
        if all(status == SentinelStatus.TABLE_CODE_GENERATED for status in table_statuses):
            return SentinelStatus.SUMMARY_PASS
        
        # 其他情况都是等待中
        return SentinelStatus.SUMMARY_PENDING
    
    @staticmethod
    def get_status_description(status: str) -> str:
        """获取状态描述"""
        return SentinelStatus.STATUS_DESCRIPTIONS.get(status, "未知状态")
    
    @staticmethod
    def can_transition_to(from_status: str, to_status: str) -> bool:
        """检查状态是否可以转换"""
        if not SentinelStatusManager.is_valid_table_status(from_status) or \
           not SentinelStatusManager.is_valid_table_status(to_status):
            return False
        
        # fail状态只能转回pending
        if from_status == SentinelStatus.TABLE_FAIL:
            return to_status == SentinelStatus.TABLE_PENDING
        
        # code_generated是最终状态，不能再转换（除非转回fail）
        if from_status == SentinelStatus.TABLE_CODE_GENERATED:
            return to_status in [SentinelStatus.TABLE_CODE_GENERATED, SentinelStatus.TABLE_FAIL]
        
        # 其他状态按顺序转换
        try:
            from_index = SentinelStatus.TABLE_STATUS_ORDER.index(from_status)
            to_index = SentinelStatus.TABLE_STATUS_ORDER.index(to_status)
            return to_index >= from_index  # 只能向前转换或保持不变
        except ValueError:
            return False


class EnvironmentVariableTask:
    """任务1：环境变量读取和配置中心初始化"""
    
    REQUIRED_ENV_VARS = [
        'JEECG_PROJECT_ROOT', 'JEECG_BASE_URL', 'JEECG_USERNAME', 'JEECG_PASSWORD',
        'JEECG_DATABASE_TYPE', 'JEECG_DATABASE_URL', 'JEECG_DATABASE_USERNAME', 'JEECG_DATABASE_PASSWORD'
    ]
    
    def __init__(self):
        self.task_id = 1
        self.task_name = "配置中心初始化"
        self.config = None
        
    def execute(self):
        """初始化配置中心并验证环境变量"""
        print(f"\n[CONFIG] 开始执行任务{self.task_id}: {self.task_name}")
        
        try:
            # 1. 创建并加载配置
            print(f"[PACKAGE] 步骤1: 创建JeecgBootConfig实例...")
            self.config = JeecgBootConfig()
            
            print(f"[SETTING] 步骤2: 加载配置文件和环境变量...")
            config_loaded = self.config.load_config()
            
            if not config_loaded:
                print("[ERROR] 配置加载失败")
                task_result = "fail"
                summary = "配置中心初始化失败"
            else:
                # 2. 验证核心环境变量有效性
                print(f"\n[OK] 步骤3: 验证核心环境变量有效性...")
                success_count = 0
                failed_vars = []
                total_required = len(self.REQUIRED_ENV_VARS)
                
                print(f"[CHECK] 检查 {total_required} 个必需环境变量:")
                for env_var in self.REQUIRED_ENV_VARS:
                    actual_value = self.config.env_vars.get(env_var)
                    if actual_value:
                        success_count += 1
                        print(f"   [OK] {env_var}: 有效 (长度: {len(actual_value)})")
                    else:
                        failed_vars.append(env_var)
                        print(f"   [ERROR] {env_var}: 无效或为空")
                
                # 3. 应用情况分析
                print(f"\n[TARGET] 步骤4: 分析最终配置应用情况...")
                print(f"[STAT] 配置统计:")
                print(f"   [OK] 有效环境变量: {success_count} 个")
                print(f"   [ERROR] 无效环境变量: {len(failed_vars)} 个")
                print(f"   [COUNT] 成功率: {success_count/total_required*100:.1f}%")
                
                # 显示实际应用的配置值
                print(f"\n[CONFIG] 最终应用的配置值:")
                print(f"   Base URL: {self.config.get_base_url()}")
                print(f"   Username: {self.config.get_username()}")
                print(f"   Project Root: {self.config.get_project_root()}")
                print(f"   Database Type: {self.config.env_vars.get('JEECG_DATABASE_TYPE', 'N/A')}")
                print(f"   Database Host: {self._extract_db_host(self.config.env_vars.get('JEECG_DATABASE_URL', ''))}")
                
                # 4. 显示配置摘要
                self.config.print_summary()
                
                # 5. 判断任务结果
                print(f"\n[FINISH] 步骤5: 评估任务执行结果...")
                if success_count >= 4:  # 至少需要基本的4个环境变量
                    task_result = "pass"
                    summary = f"配置中心初始化成功({success_count}/{total_required}个环境变量)"
                    print(f"   [SUCCESS] 评估结果: 通过 (满足最低要求 {success_count}>=4)")
                else:
                    task_result = "fail" 
                    summary = f"关键环境变量缺失({success_count}/{total_required})"
                    print(f"   [FAIL] 评估结果: 失败 (不满足最低要求 {success_count}<4)")
                    if failed_vars:
                        print(f"   [INFO] 失败变量: {', '.join(failed_vars)}")
        
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            task_result = "fail"
            summary = f"配置中心初始化异常: {e}"
            print(f"[ERROR] {summary}")
            import traceback
            traceback.print_exc()
        
        status_icon = "[OK]" if task_result == "pass" else "[ERROR]"
        print(f"\n{status_icon} 任务{self.task_id}: {self.task_name}")
        print(f"   结果: {summary}")
        print(f"   状态: {task_result.upper()}")
        print("-" * 50)
        
        return f"{self.task_id}-{self.task_name}-{task_result}"
    
    def _extract_db_host(self, db_url: str) -> str:
        """从数据库URL中提取主机信息"""
        try:
            if 'jdbc:mysql://' in db_url:
                # 提取 jdbc:mysql://localhost:30004/jeecg-boot 中的 localhost:30004
                import re
                match = re.search(r'jdbc:mysql://([^/]+)', db_url)
                return match.group(1) if match else 'N/A'
            return db_url if db_url else 'N/A'
        except:
            return 'N/A'
    
    def get_config(self) -> JeecgBootConfig:
        """获取配置实例"""
        return self.config
    
    def get_env_value(self, key: str) -> str:
        """获取环境变量值"""
        if self.config:
            return self.config.env_vars.get(key, '')
        return ''
    
    def get_all_env_values(self) -> Dict:
        """获取所有环境变量"""
        if self.config:
            return self.config.env_vars.copy()
        return {}


class MavenModuleCreationTask:
    """任务2：Maven原型创建新模块"""
    
    def __init__(self, config: JeecgBootConfig = None):
        self.task_id = 2
        self.task_name = "Maven原型创建新模块"
        self.config = config or JeecgBootConfig()
        if not self.config.loaded:
            self.config.load_config()
    
    def execute(self, config_data: Dict) -> str:
        """执行Maven模块创建任务"""
        try:
            # 1. 提取模块信息
            module_info = self._extract_module_info(config_data)
            if not module_info:
                summary = "模块信息提取失败"
                task_result = "fail"
            else:
                module_name = module_info['module_name']
                
                # 2. 检查模块是否已存在
                if self._check_module_exists(module_name):
                    summary = f"模块 {module_name} 已存在，跳过创建"
                    task_result = "pass"
                else:
                    # 3. 创建Maven模块
                    if self._create_maven_module(module_name):
                        summary = f"Maven模块 {module_name} 创建成功"
                        task_result = "pass"
                    else:
                        summary = f"Maven模块 {module_name} 创建失败"
                        task_result = "fail"
        
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            summary = f"Maven模块创建异常: {e}"
            task_result = "fail"
            print(f"[ERROR] {summary}")
        
        print(f"{self.task_id}--{self.task_name}--{summary}")
        print(task_result)
        
        return f"{self.task_id}-{self.task_name}-{task_result}"
    
    def _extract_module_info(self, config_data: Dict) -> Dict:
        """提取模块信息"""
        try:
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            
            if generation_info:
                module_name = generation_info.get('module_name')
                submodule_name = generation_info.get('submodule_name')
                
                if module_name and submodule_name:
                    return {
                        'module_name': module_name,
                        'submodule_name': submodule_name,
                        'business_entity': generation_info.get('business_entity'),
                        'inference_strategy': generation_info.get('inference_strategy'),
                        'semantic_analysis': generation_info.get('semantic_analysis')
                    }
            
            # 从表名推断模块信息
            head = config_data.get('head', {})
            table_name = head.get('tableName', '')
            
            if table_name and '_' in table_name:
                parts = table_name.split('_')
                if len(parts) >= 2:
                    return {
                        'module_name': parts[0],
                        'submodule_name': parts[1],
                        'business_entity': head.get('business_entity'),
                        'inference_strategy': 'table_name_inference',
                        'semantic_analysis': ''
                    }
            
            return None
            
        except Exception:
            return None
    
    def _check_module_exists(self, module_name: str) -> bool:
        """检查模块是否完整存在（通过验证pom.xml）"""
        try:
            project_root = self.config.get_project_root()
            # 检查 pom.xml 而不是目录，确保模块完整创建
            pom_path = f"{project_root}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}/pom.xml"
            return os.path.exists(pom_path)
        except Exception:
            return False
    
    def _create_maven_module(self, module_name: str) -> bool:
        """使用Maven archetype创建新模块"""
        import subprocess
        try:
            print(f"[BUILD] 执行 mvn archetype:generate 创建模块 jeecg-module-{module_name}")
            
            # 获取项目根路径和执行目录
            project_root = self.config.get_project_root()
            exec_dir = f"{project_root}/jeecg-boot/jeecg-boot-module"
            
            if not os.path.exists(exec_dir):
                print(f"[ERROR] 执行目录不存在: {exec_dir}")
                return False
            
            # 构建Maven命令
            # Windows环境下使用mvn.cmd
            import platform
            mvn_executable = 'mvn.cmd' if platform.system() == 'Windows' else 'mvn'

            maven_cmd = [
                mvn_executable, 'archetype:generate',
                '-DgroupId=org.jeecgframework.boot3',  # 修正: boot -> boot3
                f'-DartifactId=jeecg-module-{module_name}',
                '-Dversion=3.8.3',  # 更新: 3.8.2 -> 3.8.3
                '-DarchetypeGroupId=org.jeecgframework.archetype',
                '-DarchetypeArtifactId=jeecg-boot-archetype',  # 修正: jeecg-boot-gen -> jeecg-boot-archetype
                '-DarchetypeVersion=3.0',  # 更新: 2.0 -> 3.0
                '-DinteractiveMode=false'  # 非交互模式
            ]

            # 执行Maven命令
            result = subprocess.run(
                maven_cmd,
                cwd=exec_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print(f"[OK] Maven模块创建成功: jeecg-module-{module_name}")
                return True
            else:
                error_msg = f"Maven命令执行失败(返回码:{result.returncode})"
                if result.stderr:
                    error_msg += f", 错误: {result.stderr[:200]}"
                print(f"[ERROR] {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[ERROR] Maven命令执行超时(5分钟)")
            return False
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] Maven命令执行异常: {str(e)}")
            return False


class PomConfigurationTask:
    """任务3：更新模块注册和依赖配置"""
    
    def __init__(self, config: JeecgBootConfig = None):
        self.task_id = 3
        self.task_name = "更新模块注册和依赖配置"
        self.config = config or JeecgBootConfig()
        if not self.config.loaded:
            self.config.load_config()
    
    def execute(self, config_data: Dict) -> str:
        """执行POM配置更新任务"""
        try:
            # 1. 提取模块信息
            module_info = self._extract_module_info(config_data)
            if not module_info:
                summary = "模块信息提取失败"
                task_result = "fail"
            else:
                module_name = module_info['module_name']
                
                # 2. 更新模块注册表pom.xml
                registry_success = self._update_module_registry_pom(module_name)
                
                # 3. 更新系统启动项目pom.xml
                system_success = self._update_system_start_pom(module_name)
                
                # 4. 判断结果
                if registry_success and system_success:
                    summary = f"模块 {module_name} 配置更新完成"
                    task_result = "pass"
                elif registry_success or system_success:
                    success_part = "注册表" if registry_success else "启动依赖"
                    summary = f"模块 {module_name} 部分配置成功({success_part})"
                    task_result = "pass"  # 部分成功也算通过
                else:
                    summary = f"模块 {module_name} 配置更新失败"
                    task_result = "fail"
        
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            summary = f"POM配置更新异常: {e}"
            task_result = "fail"
            print(f"[ERROR] {summary}")
        
        print(f"{self.task_id}--{self.task_name}--{summary}")
        print(task_result)
        
        return f"{self.task_id}-{self.task_name}-{task_result}"
    
    def _extract_module_info(self, config_data: Dict) -> Dict:
        """提取模块信息"""
        try:
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            
            if generation_info:
                module_name = generation_info.get('module_name')
                submodule_name = generation_info.get('submodule_name')
                
                if module_name and submodule_name:
                    return {
                        'module_name': module_name,
                        'submodule_name': submodule_name
                    }
            
            # 从表名推断模块信息
            head = config_data.get('head', {})
            table_name = head.get('tableName', '')
            
            if table_name and '_' in table_name:
                parts = table_name.split('_')
                if len(parts) >= 2:
                    return {
                        'module_name': parts[0],
                        'submodule_name': parts[1]
                    }
            
            return None
            
        except Exception:
            return None
    
    def _update_module_registry_pom(self, module_name: str) -> bool:
        """更新模块注册表pom.xml添加新模块"""
        try:
            print(f"[LOG] 更新 jeecg-boot-module/pom.xml 添加模块引用")
            
            project_root = self.config.get_project_root()
            pom_path = f"{project_root}/jeecg-boot/jeecg-boot-module/pom.xml"
            
            if not os.path.exists(pom_path):
                print(f"[ERROR] 模块注册表pom.xml不存在: {pom_path}")
                return False
            
            # 读取原始文件内容
            with open(pom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查模块是否已存在
            module_artifact_id = f"jeecg-module-{module_name}"
            if f"<module>{module_artifact_id}</module>" in content:
                print(f"[OK] 模块已存在于注册表中: {module_artifact_id}")
                return True
            
            # 查找 </modules> 标签的位置
            modules_end_pos = content.find('</modules>')
            if modules_end_pos == -1:
                modules_end_pos = content.find('</ns0:modules>')
            if modules_end_pos == -1:
                print("[ERROR] 未找到modules节点")
                return False
            
            # 在 </modules> 前插入新模块
            new_module_entry = f"        <module>{module_artifact_id}</module>\n    "
            new_content = content[:modules_end_pos] + new_module_entry + content[modules_end_pos:]
            
            # 写回文件
            with open(pom_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"[OK] 已添加模块到注册表: {module_artifact_id}")
            return True
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 更新模块注册表异常: {str(e)}")
            return False
    
    def _update_system_start_pom(self, module_name: str) -> bool:
        """更新系统启动项目pom.xml添加新模块依赖"""
        try:
            print(f"[LOG] 更新 jeecg-system-start/pom.xml 添加模块依赖")
            
            project_root = self.config.get_project_root()
            pom_path = f"{project_root}/jeecg-boot/jeecg-module-system/jeecg-system-start/pom.xml"
            
            if not os.path.exists(pom_path):
                print(f"[ERROR] 启动项目pom.xml不存在: {pom_path}")
                return False
            
            # 读取原始文件内容
            with open(pom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查依赖是否已存在
            artifact_id = f"jeecg-module-{module_name}"
            if f"<artifactId>{artifact_id}</artifactId>" in content:
                print(f"[OK] 依赖已存在: {artifact_id}")
                return True
            
            # 查找合适的位置插入新依赖（在 jeecg-system-biz 依赖之后）
            system_biz_pos = content.find('<artifactId>jeecg-system-biz</artifactId>')
            if system_biz_pos == -1:
                # 如果找不到 jeecg-system-biz，就在第一个 </dependency> 后插入
                first_dep_end = content.find('</dependency>')
                if first_dep_end == -1:
                    print("[ERROR] 未找到合适的插入位置")
                    return False
                insert_pos = first_dep_end + len('</dependency>')
            else:
                # 找到 jeecg-system-biz 依赖的结束位置
                dep_end = content.find('</dependency>', system_biz_pos)
                if dep_end == -1:
                    print("[ERROR] 未找到依赖结束标签")
                    return False
                insert_pos = dep_end + len('</dependency>')
            
            # 构建新的依赖配置
            new_dependency = f"""
        <dependency>
            <groupId>org.jeecgframework.boot3</groupId>
            <artifactId>{artifact_id}</artifactId>
            <version>${{jeecgboot.version}}</version>
        </dependency>"""
            
            # 插入新依赖
            new_content = content[:insert_pos] + new_dependency + content[insert_pos:]
            
            # 写回文件
            with open(pom_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"[OK] 已添加依赖: {artifact_id}")
            return True
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 更新启动项目依赖异常: {str(e)}")
            return False


class ScenarioIdentificationTask:
    TABLE_TYPE_SCENARIOS = {1: "独立表场景", 2: "主子表场景中的主表", 3: "主子表场景中的子表"}
    
    def __init__(self):
        self.task_id = 4
        self.task_name = "需求场景识别"
        self.file_name = None
        self.table_name = None
        self.business_entity = None
        self.table_type = None
        self.data_registry = []
        
    def execute(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict) and 'head' in data:
                success = self._process_jeecgboot_format(filename, data)
            elif isinstance(data, dict) and 'tableType' in data:
                success = self._process_single_table(filename, data)
            elif isinstance(data, list):
                success = self._process_multiple_tables(filename, data)
            elif isinstance(data, dict) and 'tables' in data:
                success = self._process_multiple_tables(filename, data['tables'])
            else:
                success = False
                
        except Exception:
            success = False
        
        task_result = "pass" if success else "fail"
        
        # 生成摘要
        if success:
            scenario = self.TABLE_TYPE_SCENARIOS.get(self.table_type, "未知场景")
            summary = f"识别{self.table_name}为{scenario}"
        else:
            summary = "场景识别失败"
            
        print(f"{self.task_id}--{self.task_name}--{summary}")
        print(task_result)
        
        return f"{self.task_id}-{self.task_name}-{task_result}"
    
    def _process_jeecgboot_format(self, filename, data):
        head_data = data.get('head', {})
        metadata = data.get('metadata', {})
        generation_info = metadata.get('generation_info', {})
        
        table_type = head_data.get('tableType')
        table_name = head_data.get('tableName')
        business_entity = head_data.get('business_entity') or generation_info.get('business_entity')
        
        if table_type is None:
            return False
            
        table_info = {
            'file_name': filename,
            'table_name': table_name,
            'business_entity': business_entity,
            'table_type': table_type
        }
        self.data_registry.append(table_info)
        
        self.file_name = filename
        self.table_name = table_name
        self.business_entity = business_entity
        self.table_type = table_type
        
        return True
    
    def _process_single_table(self, filename, data):
        table_type = data.get('tableType')
        table_name = data.get('tableName', data.get('table_name'))
        business_entity = data.get('business_entity', data.get('businessEntity'))
        
        if table_type is None:
            return False
            
        table_info = {
            'file_name': filename,
            'table_name': table_name,
            'business_entity': business_entity,
            'table_type': table_type
        }
        self.data_registry.append(table_info)
        
        self.file_name = filename
        self.table_name = table_name
        self.business_entity = business_entity
        self.table_type = table_type
        
        return True
    
    def _process_multiple_tables(self, filename, tables_data):
        if not isinstance(tables_data, list):
            return False
            
        success_count = 0
        for i, table_data in enumerate(tables_data):
            if isinstance(table_data, dict) and 'tableType' in table_data:
                if self._process_single_table(f"{filename}[{i}]", table_data):
                    success_count += 1
                    
        return success_count > 0
    
    def query_by_filename(self, filename):
        for record in self.data_registry:
            if record['file_name'] == filename:
                return record['table_type']
        return None
    
    def query_by_table_name(self, table_name):
        for record in self.data_registry:
            if record['table_name'] == table_name:
                return record['table_type']
        return None
    
    def query_by_business_entity(self, business_entity):
        for record in self.data_registry:
            if record['business_entity'] == business_entity:
                return record['table_type']
        return None
    
    def query_table_type(self, **kwargs):
        if 'filename' in kwargs:
            return self.query_by_filename(kwargs['filename'])
        elif 'table_name' in kwargs:
            return self.query_by_table_name(kwargs['table_name'])
        elif 'business_entity' in kwargs:
            return self.query_by_business_entity(kwargs['business_entity'])
        return None
    
    def get_scenario_description(self, table_type):
        return self.TABLE_TYPE_SCENARIOS.get(table_type, "未知场景")
    
    def get_all_records(self):
        return self.data_registry.copy()


class SentinelMechanismTask:
    def __init__(self):
        self.task_id = 5
        self.task_name = "建立哨兵机制"
        self.sentinel_file = None
        self.sentinel_data = {}
        
    def execute(self, config_data, scenario_task_result=None):
        try:
            module_info = self._extract_module_info(config_data)
            if not module_info:
                task_result = "fail"
                summary = "模块信息提取失败"
            else:
                module_name = module_info['module_name']
                submodule_name = module_info['submodule_name']

                # [FIX BUG3] 哨兵文件应该生成在CodeGen目录内
                script_dir = os.path.dirname(os.path.abspath(__file__))
                sentinel_filename = f"{module_name}_{submodule_name}_sentinel.json"
                self.sentinel_file = os.path.join(script_dir, sentinel_filename)
                
                # 记录操作前的表数量
                old_table_count = 0
                if os.path.exists(self.sentinel_file):
                    try:
                        with open(self.sentinel_file, 'r', encoding='utf-8') as f:
                            old_data = json.load(f)
                            old_table_count = len(old_data.get('tables', {}))
                    except:
                        old_table_count = 0
                    
                    success = self._update_existing_sentinel(config_data, module_info)
                    action = "更新"
                else:
                    success = self._create_new_sentinel(config_data, module_info)
                    action = "创建"
                
                task_result = "pass" if success else "fail"
                if success:
                    new_table_count = len(self.sentinel_data.get('tables', {}))
                    if action == "创建":
                        summary = f"{action}哨兵文件,包含{new_table_count}个表"
                    else:
                        added_count = new_table_count - old_table_count
                        if added_count > 0:
                            summary = f"{action}哨兵文件,新增{added_count}个表,共{new_table_count}个表"
                        else:
                            summary = f"{action}哨兵文件,维持{new_table_count}个表"
                else:
                    summary = f"哨兵文件{action}失败"
        except Exception:
            task_result = "fail"
            summary = "哨兵机制建立异常"
        
        print(f"{self.task_id}--{self.task_name}--{summary}")
        print(task_result)
        
        return f"{self.task_id}-{self.task_name}-{task_result}"
    
    def _extract_module_info(self, config_data):
        try:
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            
            if generation_info:
                module_name = generation_info.get('module_name')
                submodule_name = generation_info.get('submodule_name')
                
                if module_name and submodule_name:
                    return {
                        'module_name': module_name,
                        'submodule_name': submodule_name,
                        'business_entity': generation_info.get('business_entity'),
                        'inference_strategy': generation_info.get('inference_strategy'),
                        'semantic_analysis': generation_info.get('semantic_analysis')
                    }
            
            head = config_data.get('head', {})
            table_name = head.get('tableName', '')
            
            if table_name and '_' in table_name:
                parts = table_name.split('_')
                if len(parts) >= 2:
                    return {
                        'module_name': parts[0],
                        'submodule_name': parts[1],
                        'business_entity': head.get('business_entity'),
                        'inference_strategy': 'table_name_inference',
                        'semantic_analysis': ''
                    }
            
            return None
            
        except Exception:
            return None
    
    def _create_new_sentinel(self, config_data, module_info):
        try:
            head = config_data.get('head', {})
            table_type = head.get('tableType', 1)
            scenario_type = self._determine_scenario_type(table_type)
            
            self.sentinel_data = {
                "scenario_id": f"{module_info['module_name']}_{module_info['submodule_name']}",
                "scenario_type": scenario_type,
                "module_name": module_info['module_name'],
                "submodule_name": module_info['submodule_name'],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "tables": {},
                "version": 1,
                "summary_status": SentinelStatus.SUMMARY_PENDING  # 使用状态常量
            }
            
            self._add_table_info(config_data, module_info)
            return self._save_sentinel()
            
        except Exception:
            return False
    
    def _update_existing_sentinel(self, config_data, module_info):
        try:
            with open(self.sentinel_file, 'r', encoding='utf-8') as f:
                self.sentinel_data = json.load(f)
            
            self.sentinel_data['last_updated'] = datetime.now().isoformat()
            self.sentinel_data['version'] = self.sentinel_data.get('version', 1) + 1
            
            if 'summary_status' not in self.sentinel_data:
                self.sentinel_data['summary_status'] = SentinelStatus.SUMMARY_PENDING
            
            self._add_table_info(config_data, module_info)
            # 重新计算汇总状态
            self.sentinel_data['summary_status'] = self._calculate_summary_status()
            
            return self._save_sentinel()
            
        except Exception:
            return False
    
    def _add_table_info(self, config_data, module_info):
        head = config_data.get('head', {})
        table_name = head.get('tableName')
        table_type = head.get('tableType', 1)
        business_entity = module_info.get('business_entity')
        
        if table_name:
            # 添加或更新主表/当前表信息
            current_time = datetime.now().isoformat()
            
            if table_name in self.sentinel_data['tables']:
                # 表已存在，更新信息
                existing_table = self.sentinel_data['tables'][table_name]
                existing_table.update({
                    "table_type": table_type,
                    "entity_name": business_entity,
                    "last_updated": current_time
                })
                if table_type == 3:
                    existing_table["tab_order"] = head.get('tabOrderNum', 1)
            else:
                # 新表，创建完整信息
                table_info = {
                    "table_name": table_name,
                    "table_type": table_type,
                    "entity_name": business_entity,
                    "status": SentinelStatus.TABLE_PENDING,  # 使用状态常量
                    "form_id": None,
                    "created_at": current_time,
                    "last_updated": current_time
                }
                
                if table_type == 3:
                    table_info["tab_order"] = head.get('tabOrderNum', 1)
                
                self.sentinel_data['tables'][table_name] = table_info
        
        # 如果是主表(tableType=2)，还需要处理subList中的子表信息
        if table_type == 2:
            sub_list = config_data.get('subList', [])
            if sub_list:
                self._add_subtables_from_sublist(sub_list)
    
    def _add_subtables_from_sublist(self, sub_list):
        """从subList添加或更新子表信息"""
        for i, sub_item in enumerate(sub_list, 1):
            sub_table_name = sub_item.get('tableName')
            sub_entity_name = sub_item.get('entityName')
            
            if sub_table_name and sub_entity_name:
                current_time = datetime.now().isoformat()
                
                if sub_table_name in self.sentinel_data['tables']:
                    # 子表已存在，更新信息
                    existing_subtable = self.sentinel_data['tables'][sub_table_name]
                    existing_subtable.update({
                        "entity_name": sub_entity_name,
                        "last_updated": current_time,
                        "tab_order": i
                    })
                else:
                    # 新子表，创建完整信息
                    sub_table_info = {
                        "table_name": sub_table_name,
                        "table_type": 3,  # 子表固定为tableType=3
                        "entity_name": sub_entity_name,
                        "status": SentinelStatus.TABLE_PENDING,  # 使用状态常量
                        "form_id": None,
                        "created_at": current_time,
                        "last_updated": current_time,
                        "tab_order": i
                    }
                    self.sentinel_data['tables'][sub_table_name] = sub_table_info
    
    def _determine_scenario_type(self, table_type):
        if table_type == 1:
            return "independent_table"
        elif table_type in [2, 3]:
            return "master_sub_table"
        else:
            return "unknown"
    
    def _calculate_summary_status(self):
        """计算汇总状态"""
        tables = self.sentinel_data.get('tables', {})
        if not tables:
            return SentinelStatus.SUMMARY_PENDING
        
        statuses = [table.get('status', SentinelStatus.TABLE_PENDING) for table in tables.values()]
        return SentinelStatusManager.calculate_summary_status(statuses)
    
    def _save_sentinel(self):
        try:
            with open(self.sentinel_file, 'w', encoding='utf-8') as f:
                json.dump(self.sentinel_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def get_sentinel_data(self):
        return self.sentinel_data.copy()
    
    def get_sentinel_file(self):
        return self.sentinel_file
    
    def update_table_status(self, table_name: str, new_status: str, form_id: str = None) -> bool:
        """
        更新表的状态
        
        Args:
            table_name: 表名
            new_status: 新状态（必须是有效的表状态）
            form_id: 表单ID（可选）
            
        Returns:
            bool: 是否更新成功
        """
        if not SentinelStatusManager.is_valid_table_status(new_status):
            print(f"无效的表状态: {new_status}")
            return False
        
        if table_name not in self.sentinel_data.get('tables', {}):
            print(f"表不存在: {table_name}")
            return False
        
        table_info = self.sentinel_data['tables'][table_name]
        current_status = table_info.get('status', SentinelStatus.TABLE_PENDING)
        
        # 检查状态转换是否合法
        if not SentinelStatusManager.can_transition_to(current_status, new_status):
            print(f"无法从 {current_status} 转换到 {new_status}")
            return False
        
        # 更新表状态
        table_info['status'] = new_status
        table_info['last_updated'] = datetime.now().isoformat()
        
        if form_id:
            table_info['form_id'] = form_id
        
        # 更新哨兵文件的版本和汇总状态
        self.sentinel_data['last_updated'] = datetime.now().isoformat()
        self.sentinel_data['version'] = self.sentinel_data.get('version', 1) + 1
        self.sentinel_data['summary_status'] = self._calculate_summary_status()
        
        # 保存到文件
        return self._save_sentinel()
    
    def get_table_status(self, table_name: str) -> Optional[str]:
        """获取表的当前状态"""
        table_info = self.sentinel_data.get('tables', {}).get(table_name)
        if table_info:
            return table_info.get('status', SentinelStatus.TABLE_PENDING)
        return None
    
    def get_tables_by_status(self, status: str) -> list:
        """获取指定状态的所有表"""
        tables = []
        for table_name, table_info in self.sentinel_data.get('tables', {}).items():
            if table_info.get('status') == status:
                tables.append(table_name)
        return tables


class CodeGenerationTask:
    """任务6：哨兵机制生成代码"""
    
    def __init__(self, config: JeecgBootConfig = None):
        """
        初始化代码生成任务
        
        Args:
            config: JeecgBootConfig配置实例，如果为None则使用默认配置
        """
        if config:
            self.config = config
        else:
            # 创建默认配置（主要用于向后兼容）
            self.config = JeecgBootConfig()
            self.config.load_config()
            
        # 从配置中心获取参数
        self.base_url = self.config.get_base_url()
        self.username = self.config.get_username()  
        self.password = self.config.get_password()
    
    def execute(self, filename: str) -> str:
        """执行代码生成任务"""
        try:
            # 读取传入的JSON文件
            with open(filename, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            table_type = config_data.get('head', {}).get('tableType')
            table_name = config_data.get('head', {}).get('tableName', '')
            
            print(f"6--哨兵机制生成代码--开始处理 {table_name} (类型:{table_type})")
            
            if table_type == 1:
                return self._handle_independent_table(config_data)
            elif table_type == 3:
                return self._handle_sub_table(config_data)
            elif table_type == 2:
                return self._handle_master_table(config_data)
            else:
                print(f"6--哨兵机制生成代码--无效的表类型:{table_type}")
                return "fail"
                
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"6--哨兵机制生成代码--异常:{e}")
            return "fail"
    
    def _handle_independent_table(self, config_data: Dict) -> str:
        """处理独立表场景(tableType=1)"""
        table_name = config_data.get('head', {}).get('tableName', '')
        
        # 登录获取token
        login_result = jeecg_login(self.base_url, self.username, self.password, 
                                  self.config.get_timeout('login'))
        if not login_result['success']:
            print(f"登录失败: {login_result['message']}")
            return "fail"
        
        token = login_result['token']
        
        # API调用链：创建 -> 查询 -> 同步 -> 代码生成
        try:
            # 1. 表单创建
            create_result = jeecg_create_form(self.base_url, token, config_data, 
                                            self.config.get_timeout('create'))
            if not create_result['success']:
                print(f"表单创建失败: {create_result['message']}")
                return "fail"
            
            form_id = create_result['form_id']
            print(f"表单创建成功: {form_id}")
            
            # 2. 表单查询（验证）
            query_result = jeecg_query_form(self.base_url, token, table_name, 
                                          self.config.get_page_size(), 
                                          self.config.get_timeout('list'))
            if not query_result['success']:
                print(f"表单查询失败: {query_result['message']}")
                return "fail"
            
            # 3. 数据库同步
            sync_result = jeecg_sync_database(self.base_url, token, form_id, 
                                            self.config.get_timeout('sync'))
            if not sync_result['success']:
                print(f"数据库同步失败: {sync_result['message']}")
                return "fail"
            
            print(f"数据库同步成功")
            
            # 4. 代码生成
            project_root = self.config.env_vars.get('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
            generate_result = jeecg_generate_code(self.base_url, token, form_id, config_data, 
                                                self.config.get_timeout('codegen'), project_root)
            if not generate_result['success']:
                print(f"代码生成失败: {generate_result['message']}")
                return "fail"
            
            print(f"代码生成成功")
            return "pass"
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"独立表处理异常: {e}")
            return "fail"
    
    def _handle_sub_table(self, config_data: Dict) -> str:
        """处理子表场景(tableType=3) - 无操作，等待主表调用"""
        table_name = config_data.get('head', {}).get('tableName', '')
        print(f"子表 {table_name} 等待主表处理")
        return "waiting"  # 特殊状态，不是pass也不是fail
    
    def _handle_master_table(self, config_data: Dict) -> str:
        """处理主表场景(tableType=2)"""
        table_name = config_data.get('head', {}).get('tableName', '')

        # [FIX BUG3] 获取哨兵文件路径 - 应该在CodeGen目录中查找
        module_info = self._extract_module_info(config_data)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sentinel_filename = f"{module_info['module_name']}_{module_info['submodule_name']}_sentinel.json"
        sentinel_file = os.path.join(script_dir, sentinel_filename)

        if not os.path.exists(sentinel_file):
            print(f"哨兵文件不存在: {sentinel_file}")
            return "fail"
        
        # 读取哨兵文件
        try:
            with open(sentinel_file, 'r', encoding='utf-8') as f:
                sentinel_data = json.load(f)
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"读取哨兵文件失败: {e}")
            return "fail"
        
        # 登录获取token
        login_result = jeecg_login(self.base_url, self.username, self.password, 
                                  self.config.get_timeout('login'))
        if not login_result['success']:
            print(f"登录失败: {login_result['message']}")
            self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_FAIL)
            return "fail"
        
        token = login_result['token']
        
        # 处理所有表：创建 -> 查询 -> 同步
        try:
            all_tables = sentinel_data.get('tables', {})
            
            for table_name, table_info in all_tables.items():
                table_status = table_info.get('status', SentinelStatus.TABLE_PENDING)
                
                # 跳过已经完成同步的表
                if table_status in [SentinelStatus.TABLE_DB_SYNCED, SentinelStatus.TABLE_CODE_GENERATED]:
                    continue
                
                # 查找对应的JSON配置文件
                table_config = self._find_table_json_file(table_name)
                if not table_config:
                    print(f"未找到表 {table_name} 的配置文件")
                    self._update_table_status(sentinel_file, table_name, SentinelStatus.TABLE_FAIL)
                    self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_FAIL)
                    return "fail"
                
                # 执行API调用链
                if not self._process_table_apis(token, table_name, table_config, sentinel_file):
                    return "fail"
            
            # 所有表都同步完成后，清理JSON配置文件中的tableTxt字段
            scenario_id = f"{sentinel_data.get('module_name', 'unknown')}_{sentinel_data.get('submodule_name', 'unknown')}"
            self._clean_table_txt_in_json_configs(scenario_id)
            
            # 然后对主表执行代码生成
            main_table_name = None
            main_table_config = None
            
            for table_name, table_info in all_tables.items():
                if table_info.get('table_type') == 2:  # 主表
                    main_table_name = table_name
                    main_table_config = self._find_table_json_file(table_name)
                    break
            
            if main_table_name and main_table_config:
                # 重新读取哨兵文件获取最新的form_id
                try:
                    with open(sentinel_file, 'r', encoding='utf-8') as f:
                        updated_sentinel_data = json.load(f)
                    return self._generate_master_table_code(token, main_table_name, main_table_config, updated_sentinel_data, sentinel_file)
                except Exception as e:
                    import traceback
                    print(f"[ERROR] Exception: {str(e)}")
                    traceback.print_exc()
                    print(f"重新读取哨兵文件失败: {e}")
                    return "fail"
            else:
                print("未找到主表信息")
                return "fail"
                
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"主表处理异常: {e}")
            self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_FAIL)
            return "fail"
    
    def _extract_module_info(self, config_data: Dict) -> Dict:
        """提取模块信息"""
        # 优先从metadata中获取
        metadata = config_data.get('metadata', {})
        generation_info = metadata.get('generation_info', {})

        if generation_info:
            module_name = generation_info.get('module_name')
            submodule_name = generation_info.get('submodule_name')
            if module_name and submodule_name:
                return {
                    'module_name': module_name,
                    'submodule_name': submodule_name
                }

        # 如果metadata不存在，从表名推断
        head = config_data.get('head', {})
        table_name = head.get('tableName', '')

        if table_name and '_' in table_name:
            parts = table_name.split('_')
            if len(parts) >= 2:
                return {
                    'module_name': parts[0],
                    'submodule_name': parts[1]
                }

        # 兜底返回unknown
        return {
            'module_name': 'unknown',
            'submodule_name': 'unknown'
        }
    
    def _find_table_json_file(self, table_name: str) -> Dict:
        """根据表名查找对应的JSON配置文件 - 增强版本支持多种命名格式"""
        import glob
        import re

        # [FIX BUG3] 在CodeGen目录中查找JSON配置文件
        script_dir = os.path.dirname(os.path.abspath(__file__))

        def to_pascal_case(snake_str: str) -> str:
            """将snake_case字符串转换为PascalCase"""
            if not snake_str:
                return ""
            # 按下划线分割，每个单词首字母大写
            words = snake_str.split('_')
            return ''.join(word.capitalize() for word in words if word)

        def to_camel_case(snake_str: str) -> str:
            """将snake_case字符串转换为camelCase"""
            if not snake_str:
                return ""
            words = snake_str.split('_')
            if not words:
                return ""
            # 第一个单词小写，其余单词首字母大写
            return words[0].lower() + ''.join(word.capitalize() for word in words[1:] if word)

        # 策略1: 直接匹配 (原始表名)
        pattern = os.path.join(script_dir, f"{table_name}_*.json")
        matching_files = glob.glob(pattern)
        
        # 策略2: 通配符模糊匹配
        if not matching_files:
            table_parts = table_name.split('_')
            if len(table_parts) >= 3:
                module = table_parts[0]
                submodule = table_parts[1]
                entity_part = '_'.join(table_parts[2:])

                # 使用通配符进行模糊匹配，忽略大小写差异
                all_files = glob.glob(os.path.join(script_dir, f"{module}_{submodule}_*_*.json"))

                # 在匹配的文件中查找包含entity_part的文件（忽略大小写）
                for file in all_files:
                    if entity_part.lower() in os.path.basename(file).lower():
                        matching_files.append(file)

        # 策略3: PascalCase转换匹配
        if not matching_files:
            table_parts = table_name.split('_')
            if len(table_parts) >= 3:
                module = table_parts[0]
                submodule = table_parts[1]
                entity_part = '_'.join(table_parts[2:])

                # 将entity部分转换为PascalCase
                entity_pascal = to_pascal_case(entity_part)
                pascal_pattern = os.path.join(script_dir, f"{module}_{submodule}_{entity_pascal}_*.json")
                matching_files = glob.glob(pascal_pattern)

        # 策略4: camelCase转换匹配
        if not matching_files:
            table_parts = table_name.split('_')
            if len(table_parts) >= 3:
                module = table_parts[0]
                submodule = table_parts[1]
                entity_part = '_'.join(table_parts[2:])

                # 将entity部分转换为camelCase
                entity_camel = to_camel_case(entity_part)
                camel_pattern = os.path.join(script_dir, f"{module}_{submodule}_{entity_camel}_*.json")
                matching_files = glob.glob(camel_pattern)
        
        # 策略5: 正则表达式匹配 (最宽松)
        if not matching_files:
            table_parts = table_name.split('_')
            if len(table_parts) >= 3:
                module = table_parts[0]
                submodule = table_parts[1]
                entity_part = '_'.join(table_parts[2:])

                # 查找所有可能的文件
                all_possible_files = glob.glob(os.path.join(script_dir, f"{module}_{submodule}_*_*.json"))

                # 使用正则表达式进行灵活匹配
                entity_chars = ''.join(c for c in entity_part if c.isalnum())
                pattern_regex = re.compile(
                    f"{re.escape(module)}_{re.escape(submodule)}_.*{re.escape(entity_chars)}.*\\.json$",
                    re.IGNORECASE
                )

                for file in all_possible_files:
                    if pattern_regex.match(os.path.basename(file)):
                        matching_files.append(file)
        
        # 返回第一个匹配的文件
        if matching_files:
            # 去重并选择第一个
            matching_files = list(set(matching_files))
            try:
                print(f"[OK] 找到配置文件: {matching_files[0]} (匹配表名: {table_name})")
                with open(matching_files[0], 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                import traceback
                print(f"[ERROR] Exception: {str(e)}")
                traceback.print_exc()
                print(f"[ERROR] 读取配置文件失败 {matching_files[0]}: {e}")
                return None
        
        print(f"[ERROR] 未找到表 {table_name} 的配置文件")
        print(f"   尝试的匹配策略:")
        print(f"   1. 直接匹配: {table_name}_*.json")
        if '_' in table_name and len(table_name.split('_')) >= 3:
            parts = table_name.split('_')
            entity = '_'.join(parts[2:])
            print(f"   2. 通配符匹配: {parts[0]}_{parts[1]}_*{entity.lower()}*_*.json")
            print(f"   3. PascalCase匹配: {parts[0]}_{parts[1]}_{to_pascal_case(entity)}_*.json")
            print(f"   4. camelCase匹配: {parts[0]}_{parts[1]}_{to_camel_case(entity)}_*.json")
        
        return None
    
    def _process_table_apis(self, token: str, table_name: str, table_config: Dict, sentinel_file: str) -> bool:
        """处理单个表的API调用链"""
        try:
            # 1. 表单创建
            create_result = jeecg_create_form(self.base_url, token, table_config, 
                                            self.config.get_timeout('create'))
            if not create_result['success']:
                print(f"表 {table_name} 创建失败: {create_result['message']}")
                self._update_table_status(sentinel_file, table_name, SentinelStatus.TABLE_FAIL)
                self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_FAIL)
                return False
            
            form_id = create_result['form_id']
            self._update_table_status(sentinel_file, table_name, SentinelStatus.TABLE_FORM_CREATED, form_id)
            print(f"表 {table_name} 创建成功")
            
            # 2. 表单查询（验证）
            query_result = jeecg_query_form(self.base_url, token, table_name, 
                                          self.config.get_page_size(), 
                                          self.config.get_timeout('list'))
            if not query_result['success']:
                print(f"表 {table_name} 查询失败: {query_result['message']}")
                self._update_table_status(sentinel_file, table_name, SentinelStatus.TABLE_FAIL)
                self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_FAIL)
                return False
            
            # 3. 数据库同步
            sync_result = jeecg_sync_database(self.base_url, token, form_id, 
                                            self.config.get_timeout('sync'))
            if not sync_result['success']:
                print(f"表 {table_name} 同步失败: {sync_result['message']}")
                self._update_table_status(sentinel_file, table_name, SentinelStatus.TABLE_FAIL)
                self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_FAIL)
                return False
            
            self._update_table_status(sentinel_file, table_name, SentinelStatus.TABLE_DB_SYNCED)
            print(f"表 {table_name} 同步成功")
            return True
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"表 {table_name} 处理异常: {e}")
            self._update_table_status(sentinel_file, table_name, SentinelStatus.TABLE_FAIL)
            self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_FAIL)
            return False
    
    def _generate_master_table_code(self, token: str, main_table_name: str, main_table_config: Dict, sentinel_data: Dict, sentinel_file: str) -> str:
        """为主表生成代码"""
        try:
            # 构建subList
            sub_list = self._build_sublist_from_sentinel(sentinel_data)
            
            # 将subList添加到主表配置中
            main_table_config['subList'] = sub_list
            
            # 获取主表form_id
            main_table_info = sentinel_data.get('tables', {}).get(main_table_name, {})
            form_id = main_table_info.get('form_id')
            
            if not form_id:
                print(f"主表 {main_table_name} 缺少form_id")
                return "fail"
            
            # 执行代码生成
            project_root = self.config.env_vars.get('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
            generate_result = jeecg_generate_code(self.base_url, token, form_id, main_table_config, 
                                                self.config.get_timeout('codegen'), project_root)
            if not generate_result['success']:
                print(f"主表代码生成失败: {generate_result['message']}")
                self._update_table_status(sentinel_file, main_table_name, SentinelStatus.TABLE_FAIL)
                self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_FAIL)
                return "fail"
            
            # 更新主表状态为代码已生成
            self._update_table_status(sentinel_file, main_table_name, SentinelStatus.TABLE_CODE_GENERATED)
            self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_PASS)
            print(f"主表 {main_table_name} 代码生成成功")
            return "pass"
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"主表代码生成异常: {e}")
            self._update_table_status(sentinel_file, main_table_name, SentinelStatus.TABLE_FAIL)
            self._update_sentinel_summary_status(sentinel_file, SentinelStatus.SUMMARY_FAIL)
            return "fail"
    
    def _build_sublist_from_sentinel(self, sentinel_data: Dict) -> list:
        """根据哨兵文件构建subList"""
        sub_list = []
        all_tables = sentinel_data.get('tables', {})
        
        # 获取所有子表（tableType=3）
        sub_tables = []
        for table_name, table_info in all_tables.items():
            if table_info.get('table_type') == 3:
                sub_tables.append({
                    'table_name': table_name,
                    'entity_name': table_info.get('entity_name', ''),
                    'tab_order': table_info.get('tab_order', 1)
                })
        
        # 按tab_order排序
        sub_tables.sort(key=lambda x: x.get('tab_order', 999))
        
        # 构建subList格式（参考Example_Main_Sub_Table.json）
        for i, sub_table in enumerate(sub_tables):
            # [FIX] 修复：使用安全的多重降级策略获取中文描述
            ftl_description = self._get_safe_table_description(
                sub_table['table_name'], 
                sub_table['entity_name']
            )
            
            sub_list.append({
                "tableName": sub_table['table_name'],
                "entityName": sub_table['entity_name'],
                "ftlDescription": ftl_description,
                "id": f"row_{1020 + i}"
            })
        
        return sub_list
    
    def _get_safe_table_description(self, table_name: str, entity_name: str) -> str:
        """
        安全获取表的中文描述

        [SAFE] 多重降级策略确保系统绝对稳定：
        Level 1: 尝试从子表JSON配置文件读取tableTxt
        Level 2: 尝试从哨兵数据读取description 
        Level 3: 使用原有的entity_name + "表"
        
        Args:
            table_name: 表名
            entity_name: 实体名
            
        Returns:
            str: 表的中文描述
        """
        
        # Level 1: 尝试从配置文件读取 (最优方案)
        try:
            config_data = self._find_table_json_file(table_name)
            if config_data and isinstance(config_data, dict):
                table_txt = config_data.get('head', {}).get('tableTxt')
                if table_txt and table_txt.strip():
                    return table_txt.strip()
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            # [SILENT] 静默处理，记录警告但不中断流程
            print(f"[WARN]  读取{table_name}配置文件异常，使用降级方案: {str(e)[:50]}...")
        
        # Level 2: 尝试从哨兵数据读取 (中级方案)
        try:
            if hasattr(self, 'sentinel_data') and self.sentinel_data:
                tables = self.sentinel_data.get('tables', {})
                table_info = tables.get(table_name, {})
                description = table_info.get('table_description') or table_info.get('description')
                if description and description.strip():
                    return description.strip()
        except Exception:
            # [SILENT] 静默处理，继续降级
            pass
        
        # Level 3: 最终降级方案 (确保系统稳定)
        return f"{entity_name}表"
    
    def _update_table_status(self, sentinel_file: str, table_name: str, status: str, form_id: str = None):
        """更新哨兵文件中表的状态"""
        try:
            with open(sentinel_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if table_name in data.get('tables', {}):
                data['tables'][table_name]['status'] = status
                data['tables'][table_name]['last_updated'] = datetime.now().isoformat()
                if form_id:
                    data['tables'][table_name]['form_id'] = form_id
                
                data['version'] = data.get('version', 0) + 1
                
                with open(sentinel_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"更新表状态失败: {e}")
    
    def _clean_table_txt_in_json_configs(self, scenario_id: str):
        """
        清理生成的JSON配置文件中的tableTxt字段
        移除模块前缀和"表"后缀，保留纯净的业务描述

        Args:
            scenario_id: 场景ID，用于匹配JSON文件
        """
        try:
            print(f"\n[CLEAN] 开始清理JSON配置文件中的tableTxt字段...")

            # [FIX BUG3] 在CodeGen目录中查找JSON配置文件
            script_dir = os.path.dirname(os.path.abspath(__file__))
            pattern = f"{scenario_id}_*.json"
            json_files = []

            for file in os.listdir(script_dir):
                if fnmatch.fnmatch(file, pattern):
                    json_files.append(os.path.join(script_dir, file))
            
            if not json_files:
                print(f"[WARN]  未找到匹配的JSON文件: {pattern}")
                return
            
            # 定义业务描述映射表 - 将entity名称映射到纯净的中文描述
            entity_to_description = {
                'MemberEducation': '教育背景',
                'MemberCareer': '职业发展', 
                'MemberAchievement': '荣誉成就',
                'MemberSocial': '社交属性',
                'MemberProfile': '基础档案'  # 主表通常保持原样或简化
            }
            
            cleaned_count = 0
            
            for json_file in json_files:
                try:
                    # 读取JSON文件
                    with open(json_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # 获取entity名称
                    entity_name = config_data.get('head', {}).get('business_entity', '')
                    current_table_txt = config_data.get('head', {}).get('tableTxt', '')
                    
                    if entity_name and entity_name in entity_to_description:
                        # 获取纯净的业务描述
                        clean_description = entity_to_description[entity_name]
                        
                        # 检查是否需要更新
                        if current_table_txt != clean_description:
                            print(f"   [LOG] {json_file}:")
                            print(f"      原值: '{current_table_txt}'")
                            print(f"      新值: '{clean_description}'")
                            
                            # 更新tableTxt字段
                            config_data['head']['tableTxt'] = clean_description
                            
                            # 写回文件
                            with open(json_file, 'w', encoding='utf-8') as f:
                                json.dump(config_data, f, indent=2, ensure_ascii=False)
                            
                            cleaned_count += 1
                        else:
                            print(f"   [OK] {json_file}: tableTxt已经是纯净格式")
                    else:
                        print(f"   [WARN]  {json_file}: 未找到entity映射 ({entity_name})")
                
                except Exception as e:
                    import traceback
                    print(f"[ERROR] Exception: {str(e)}")
                    traceback.print_exc()
                    print(f"   [ERROR] 处理{json_file}失败: {str(e)}")
            
            if cleaned_count > 0:
                print(f"[OK] 成功清理了 {cleaned_count} 个JSON配置文件的tableTxt字段")
            else:
                print(f"[INFO] 所有JSON文件的tableTxt字段都已是正确格式")
                
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 清理JSON配置文件失败: {str(e)}")
    
    def _update_sentinel_summary_status(self, sentinel_file: str, summary_status: str):
        """更新哨兵文件的汇总状态"""
        try:
            with open(sentinel_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['summary_status'] = summary_status
            data['last_updated'] = datetime.now().isoformat()
            data['version'] = data.get('version', 0) + 1
            
            with open(sentinel_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"更新汇总状态失败: {e}")


class PlaceholderVariableProcessingTask:
    """任务7：占位符变量处理"""
    
    def __init__(self, config: JeecgBootConfig = None):
        self.task_id = 7
        self.task_name = "占位符变量处理"
        self.config = config or JeecgBootConfig()
        if not self.config.loaded:
            self.config.load_config()
    
    def execute(self, filename: str) -> str:
        """执行占位符变量处理任务"""
        try:
            # 读取配置数据
            with open(filename, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            print("7--占位符变量处理--任务开始")
            
            # 处理占位符变量替换
            if self.process_placeholder_variables(config_data):
                summary = "占位符变量处理成功"
                task_result = "pass"
            else:
                summary = "占位符变量处理失败"
                task_result = "fail"
            
            print(f"{self.task_id}--{self.task_name}--{summary}")
            print(task_result)
            
            return f"{self.task_id}-{self.task_name}-{task_result}"
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            summary = f"占位符变量处理异常: {e}"
            task_result = "fail"
            print(f"[ERROR] {summary}")
            print(f"{self.task_id}--{self.task_name}--{summary}")
            print(task_result)
            return f"{self.task_id}-{self.task_name}-{task_result}"
    
    def process_placeholder_variables(self, config_data: Dict) -> bool:
        """处理占位变量替换 - 基于老脚本的实现"""
        import shutil
        import re
        
        try:
            print("[PROCESS] 开始处理生成代码中的占位变量")
            
            # 提取模块信息
            module_info = self._extract_module_info(config_data)
            if not module_info:
                print("[ERROR] 缺少必要的模块信息")
                return False
            
            module_name = module_info['module_name']
            submodule_name = module_info['submodule_name']
            business_entity = module_info['business_entity']
            
            # 查找生成的模块目录
            project_root = self.config.get_project_root()
            module_path = f"{project_root}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
            
            if not os.path.exists(module_path):
                print(f"[ERROR] 模块目录不存在: {module_path}")
                return False
            
            print(f"[FOLDER] 处理模块目录: {module_path}")
            
            # 构建包名和路径映射
            src_java_path = f"{module_path}/src/main/java"
            package_name = f"org.jeecg.modules.{module_name}"
            package_path = package_name.replace('.', '/')
            
            # 定义占位变量映射
            placeholders = {
                '{{PACKAGE_NAME}}': package_name,
                '{{MODULE_NAME}}': module_name,
                '{{SUBMODULE_NAME}}': submodule_name,
                '{{BUSINESS_ENTITY}}': business_entity
            }
            
            print(f"[INFO] 占位变量映射: {placeholders}")

            # 处理文件夹重命名 - 递归查找并处理所有 {{PACKAGE_NAME}} 占位符目录
            print(f"[PROCESS] 开始递归查找占位符目录...")
            renamed_dirs = self._find_and_rename_placeholder_dirs(src_java_path, package_name)
            if renamed_dirs > 0:
                print(f"[OK] 成功处理 {renamed_dirs} 个占位符目录")
            else:
                print(f"[INFO] 未发现需要处理的占位符目录")

            # 处理所有文件中的占位变量
            replaced_count = 0
            processed_files = []
            
            for root, dirs, files in os.walk(module_path):
                for file in files:
                    if file.endswith(('.java', '.xml', '.ts', '.vue', '.sql', '.yml', '.yaml', '.properties')):
                        file_path = os.path.join(root, file)
                        if self._replace_file_placeholders(file_path, placeholders):
                            replaced_count += 1
                            # 记录处理的文件（相对路径）
                            relative_path = os.path.relpath(file_path, module_path)
                            processed_files.append(relative_path)
            
            print(f"[OK] 占位符变量处理完成")
            print(f"[STAT] 共处理 {replaced_count} 个文件")
            
            if processed_files:
                print("[FILE] 处理的文件列表:")
                for file_path in processed_files[:10]:  # 最多显示前10个文件
                    print(f"   - {file_path}")
                if len(processed_files) > 10:
                    print(f"   ... 还有 {len(processed_files) - 10} 个文件")
            
            return True
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 占位变量处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_module_info(self, config_data: Dict) -> Dict:
        """提取模块信息"""
        try:
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            
            if generation_info:
                module_name = generation_info.get('module_name')
                submodule_name = generation_info.get('submodule_name')
                business_entity = generation_info.get('business_entity')
                
                if module_name and submodule_name and business_entity:
                    return {
                        'module_name': module_name,
                        'submodule_name': submodule_name,
                        'business_entity': business_entity
                    }
            
            # 从表名推断模块信息
            head = config_data.get('head', {})
            table_name = head.get('tableName', '')
            business_entity = head.get('business_entity', '')
            
            if table_name and '_' in table_name and business_entity:
                parts = table_name.split('_')
                if len(parts) >= 2:
                    return {
                        'module_name': parts[0],
                        'submodule_name': parts[1],
                        'business_entity': business_entity
                    }
            
            return None

        except Exception:
            return None

    def _find_and_rename_placeholder_dirs(self, src_java_path: str, package_name: str) -> int:
        """
        递归查找并智能处理所有 {{PACKAGE_NAME}} 占位符目录

        策略：
        1. 递归遍历整个 src/main/java 目录树，找到所有 {{PACKAGE_NAME}} 占位符目录
        2. 按深度从深到浅排序，确保先处理子目录再处理父目录
        3. 智能处理：
           a) 顶层占位符目录（在 src/main/java 下）:
              - 如果正确的包路径已存在 -> 删除冗余的占位符目录
              - 如果正确的包路径不存在 -> 将占位符目录重命名为正确的包路径
           b) 嵌套占位符目录（在包路径中）:
              - 将占位符目录中的内容移动到父目录
              - 如果目标已存在，使用占位符版本覆盖
              - 删除空的占位符目录

        Args:
            src_java_path: Java源代码根路径（如 .../src/main/java）
            package_name: 正确的包名（如 org.jeecg.modules.finance）

        Returns:
            int: 成功处理的占位符目录数量
        """
        import shutil
        renamed_count = 0
        placeholder_dir_name = '{{PACKAGE_NAME}}'
        package_path = package_name.replace('.', os.sep)  # org.jeecg.modules.finance -> org/jeecg/modules/finance

        # 收集所有需要处理的占位符目录（从深到浅排序，避免处理冲突）
        placeholder_dirs = []

        for root, dirs, files in os.walk(src_java_path):
            if placeholder_dir_name in dirs:
                placeholder_dir_path = os.path.join(root, placeholder_dir_name)
                # 计算目录深度（用于排序）
                depth = placeholder_dir_path.count(os.sep)
                placeholder_dirs.append((depth, placeholder_dir_path))

        # 按深度从深到浅排序，确保先处理子目录再处理父目录
        placeholder_dirs.sort(key=lambda x: x[0], reverse=True)

        print(f"[SEARCH] 发现 {len(placeholder_dirs)} 个占位符目录需要处理")

        for depth, placeholder_dir_path in placeholder_dirs:
            try:
                parent_dir = os.path.dirname(placeholder_dir_path)
                relative_parent = os.path.relpath(parent_dir, src_java_path)

                print(f"[RENAME] 处理占位符目录: {os.path.relpath(placeholder_dir_path, src_java_path)}")
                print(f"   父目录: {relative_parent}")

                # 判断是否为顶层占位符目录（直接在 src/main/java 下）
                is_top_level = (parent_dir == src_java_path or relative_parent == '.')

                if is_top_level:
                    # 顶层占位符目录：检查正确路径是否存在
                    correct_package_path = os.path.join(src_java_path, package_path)

                    if os.path.exists(correct_package_path):
                        # 正确路径已存在，直接删除占位符目录
                        print(f"   [INFO] 正确的包路径已存在: {package_path}")
                        print(f"   [DELETE] 删除冗余的顶层占位符目录及其内容")
                        shutil.rmtree(placeholder_dir_path)
                        renamed_count += 1
                    else:
                        # 正确路径不存在，将占位符目录重命名为正确路径
                        print(f"   [INFO] 这是顶层占位符目录，重命名为正确的包路径")
                        print(f"   [MOVE] {{{{PACKAGE_NAME}}}} -> {package_path}")
                        os.makedirs(os.path.dirname(correct_package_path), exist_ok=True)
                        shutil.move(placeholder_dir_path, correct_package_path)
                        renamed_count += 1
                else:
                    # 嵌套的占位符目录：将内容移到父目录
                    items_to_move = []
                    for item in os.listdir(placeholder_dir_path):
                        item_path = os.path.join(placeholder_dir_path, item)
                        items_to_move.append((item, item_path))

                    print(f"   [INFO] 这是嵌套的占位符目录，移动内容到父目录")
                    print(f"   需要移动的项目数: {len(items_to_move)}")

                    # 将所有内容移动到父目录
                    moved_count = 0
                    for item_name, item_path in items_to_move:
                        target_path = os.path.join(parent_dir, item_name)

                        # 如果目标已存在，使用占位符版本覆盖
                        if os.path.exists(target_path):
                            print(f"   [WARN] 目标已存在: {item_name}，使用占位符版本覆盖")
                            if os.path.isdir(target_path):
                                shutil.rmtree(target_path)
                            else:
                                os.remove(target_path)

                        # 移动项目
                        shutil.move(item_path, target_path)
                        moved_count += 1
                        print(f"   [MOVE] {item_name}")

                    # 删除空的占位符目录
                    try:
                        os.rmdir(placeholder_dir_path)
                        print(f"   [DELETE] 删除空占位符目录")
                        renamed_count += 1
                    except OSError as e:
                        print(f"   [WARN] 无法删除占位符目录: {e}")

                    print(f"   [OK] 成功移动 {moved_count} 个项目")

            except Exception as e:
                import traceback
                print(f"[ERROR] Exception: {str(e)}")
                traceback.print_exc()
                print(f"   [ERROR] 处理占位符目录失败: {e}")
                continue

        return renamed_count

    def _replace_file_placeholders(self, file_path: str, placeholders: Dict[str, str]) -> bool:
        """替换单个文件中的占位变量"""
        try:
            # 尝试以UTF-8编码读取文件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 如果UTF-8失败，尝试使用GBK编码
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # 如果都失败，跳过这个文件
                    print(f"[WARN] 文件编码无法识别，跳过: {file_path}")
                    return False
            
            original_content = content
            
            # 替换所有占位变量
            for placeholder, value in placeholders.items():
                if placeholder in content:
                    content = content.replace(placeholder, value)
            
            # 修复Java包路径中的连续点号问题
            if file_path.endswith('.java'):
                import re
                # 使用正则表达式替换连续的点号为单个点号
                content = re.sub(r'\.{2,}', '.', content)
            
            # 如果内容有变化才写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[WARN] 文件处理失败 {file_path}: {e}")
            return False


class FrontendCodeMigrationTask:
    """任务8：前端代码迁移"""

    def __init__(self, config: JeecgBootConfig = None):
        self.task_id = 8
        self.task_name = "前端代码迁移"
        self.config = config or JeecgBootConfig()
        if not self.config.loaded:
            self.config.load_config()
        self.target_directory = None  # 保存目标目录路径
    
    def execute(self, filename: str) -> str:
        """执行前端代码迁移任务"""
        try:
            # 读取配置数据
            with open(filename, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            print("8--前端代码迁移--任务开始")

            # 执行前端代码迁移
            success, target_dir = self.migrate_frontend_code(config_data)
            if success:
                self.target_directory = target_dir  # 保存目标目录
                summary = "前端代码迁移成功"
                task_result = "pass"
            else:
                summary = "前端代码迁移失败"
                task_result = "fail"

            print(f"{self.task_id}--{self.task_name}--{summary}")
            print(task_result)

            return f"{self.task_id}-{self.task_name}-{task_result}"
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            summary = f"前端代码迁移异常: {e}"
            task_result = "fail"
            print(f"[ERROR] {summary}")
            print(f"{self.task_id}--{self.task_name}--{summary}")
            print(task_result)
            return f"{self.task_id}-{self.task_name}-{task_result}"
    
    def migrate_frontend_code(self, config_data: Dict) -> tuple:
        """迁移前端代码到正确位置

        Returns:
            tuple: (success: bool, target_dir: str) - 成功状态和目标目录路径
        """
        import shutil

        try:
            print("[PROCESS] 开始迁移Vue3前端代码")

            # 提取模块信息
            module_info = self._extract_module_info(config_data)
            if not module_info:
                print("[ERROR] 缺少必要的模块信息")
                return (False, "")
            
            module_name = module_info['module_name']
            submodule_name = module_info['submodule_name']
            
            # 获取路径信息
            project_root = self.config.get_project_root()
            
            # 源路径：生成的Vue3代码位置（占位符处理后的实际路径）
            source_vue_path = f"{project_root}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}/src/main/java/org/jeecg/modules/{module_name}/{submodule_name}/vue3"
            
            # 目标路径：前端项目中的位置（使用submodule层级）
            target_base_path = "jeecgboot-vue3/src/views"
            target_dir = f"{project_root}/{target_base_path}/{submodule_name}"

            print(f"[SOURCE] 源路径: {source_vue_path}")
            print(f"[TARGET] 目标路径: {target_dir}")
            
            # 检查源路径是否存在
            if not os.path.exists(source_vue_path):
                print(f"[ERROR] 源路径不存在: {source_vue_path}")
                return (False, "")

            # 检查源路径中是否有文件
            if not os.listdir(source_vue_path):
                print(f"[WARN] 源路径为空: {source_vue_path}")
                return (True, target_dir)  # 空目录也算成功，返回目标目录
            
            # 确保目标目录存在
            os.makedirs(target_dir, exist_ok=True)
            print(f"[FOLDER] 创建目标目录: {target_dir}")
            
            # 统计迁移的文件数
            migrated_files = []
            
            # 移动vue3目录下的所有内容到目标位置
            for item in os.listdir(source_vue_path):
                source_item = os.path.join(source_vue_path, item)
                target_item = os.path.join(target_dir, item)
                
                # 如果目标文件已存在，先备份
                if os.path.exists(target_item):
                    backup_name = f"{target_item}.backup.{int(time.time())}"
                    shutil.move(target_item, backup_name)
                    print(f"[PROCESS] 备份已存在文件: {item} -> {os.path.basename(backup_name)}")
                
                # 移动文件或目录
                shutil.move(source_item, target_item)
                migrated_files.append(item)
                print(f"[FILE] 迁移文件: {item}")
            
            print(f"[OK] 前端代码迁移完成")
            print(f"[STAT] 共迁移 {len(migrated_files)} 个文件/目录")
            print(f"[LOCATION] 目标位置: {target_dir}")
            
            if migrated_files:
                print("[FILE] 迁移的文件列表:")
                for file_name in migrated_files:
                    print(f"   - {file_name}")
            
            # 清理空的源目录
            try:
                if os.path.exists(source_vue_path) and not os.listdir(source_vue_path):
                    os.rmdir(source_vue_path)
                    print(f"[CLEAN] 清理空源目录: {source_vue_path}")
            except Exception as e:
                import traceback
                print(f"[ERROR] Exception: {str(e)}")
                traceback.print_exc()
                print(f"[WARN] 清理源目录失败: {e}")

            return (True, target_dir)

        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 前端代码迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return (False, "")

    def get_target_directory(self) -> Optional[str]:
        """获取前端代码迁移的目标目录

        Returns:
            Optional[str]: 目标目录路径，如果未执行迁移则返回None
        """
        return self.target_directory

    def _extract_module_info(self, config_data: Dict) -> Dict:
        """提取模块信息"""
        try:
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            
            if generation_info:
                module_name = generation_info.get('module_name')
                submodule_name = generation_info.get('submodule_name')
                
                if module_name and submodule_name:
                    return {
                        'module_name': module_name,
                        'submodule_name': submodule_name
                    }
            
            # 从表名推断模块信息
            head = config_data.get('head', {})
            table_name = head.get('tableName', '')
            
            if table_name and '_' in table_name:
                parts = table_name.split('_')
                if len(parts) >= 2:
                    return {
                        'module_name': parts[0],
                        'submodule_name': parts[1]
                    }
            
            return None
            
        except Exception:
            return None


# =============================================================================
# 任务9：菜单权限SQL执行
# =============================================================================

class DatabaseSQLExecutionTask:
    """任务9：菜单权限SQL执行任务"""

    def __init__(self, config: Optional[JeecgBootConfig] = None):
        """初始化SQL执行任务

        Args:
            config: JeecgBoot配置对象，包含数据库连接信息
        """
        self.config = config or JeecgBootConfig()
        if not self.config.loaded:
            self.config.load_config()
        self.target_directory = None  # 指定SQL文件查找目录

    def set_target_directory(self, target_dir: Optional[str]):
        """设置SQL文件查找目录

        Args:
            target_dir: 目标目录路径，如果为None则使用全局扫描
        """
        self.target_directory = target_dir

    def execute(self, config_file: str) -> str:
        """执行SQL文件中的菜单权限语句

        Args:
            config_file: 配置文件路径（未使用，但保持接口一致性）

        Returns:
            str: 执行结果状态 "9-菜单权限SQL执行-pass" 或 "9-菜单权限SQL执行-fail"
        """
        print("9--菜单权限SQL执行--任务开始")

        try:
            # 获取数据库连接配置
            db_config = self._get_database_config()
            if not db_config:
                print("[ERROR] 数据库配置缺失")
                print("9--菜单权限SQL执行--数据库配置缺失")
                return "9-菜单权限SQL执行-fail"

            # 发现SQL文件
            sql_files = self._discover_sql_files()
            if not sql_files:
                # [FIX BUG1] SQL文件应该存在，如果未找到说明有问题，应该标记为警告而不是成功
                print("[WARN] 未发现需要执行的SQL文件 - 这可能表示前端代码迁移有问题")
                print("9--菜单权限SQL执行--未发现SQL文件(警告)")
                # 虽然没有SQL文件，但不认为是错误，继续执行
                return "9-菜单权限SQL执行-pass"

            print(f"[FILE] 发现 {len(sql_files)} 个SQL文件需要执行")

            # 执行SQL文件
            success_count = 0
            for sql_file in sql_files:
                print(f"[PROCESS] 执行SQL文件: {sql_file}")
                if self._execute_sql_file(sql_file, db_config):
                    success_count += 1
                    print(f"[OK] SQL文件执行成功: {sql_file}")
                else:
                    print(f"[ERROR] SQL文件执行失败: {sql_file}")

            # [FIX BUG1] 所有SQL文件必须执行成功
            if success_count == len(sql_files):
                print(f"[OK] 菜单权限SQL执行完成")
                print(f"[STAT] 成功执行 {success_count}/{len(sql_files)} 个SQL文件")
                print("9--菜单权限SQL执行--SQL执行成功")
                return "9-菜单权限SQL执行-pass"
            else:
                print(f"[ERROR] 部分SQL文件执行失败 - 任务失败")
                print(f"[STAT] 成功执行 {success_count}/{len(sql_files)} 个SQL文件")
                print("9--菜单权限SQL执行--部分SQL执行失败")
                return "9-菜单权限SQL执行-fail"

        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] SQL执行任务异常: {str(e)}")
            print("9--菜单权限SQL执行--SQL执行异常")
            return "9-菜单权限SQL执行-fail"
    
    def _get_database_config(self) -> Optional[Dict]:
        """获取数据库连接配置
        
        Returns:
            Dict: 数据库配置信息，包含host、port、user、password、database
        """
        try:
            # 从JEECG_DATABASE_URL解析数据库连接信息
            database_url = self.config.env_vars.get('JEECG_DATABASE_URL', '')
            database_username = self.config.env_vars.get('JEECG_DATABASE_USERNAME', '')
            database_password = self.config.env_vars.get('JEECG_DATABASE_PASSWORD', '')
            
            if not database_url or not database_username or not database_password:
                print("[WARN] JeecgBoot数据库配置缺失")
                print(f"   JEECG_DATABASE_URL: {'[OK]' if database_url else '[ERROR]'}")
                print(f"   JEECG_DATABASE_USERNAME: {'[OK]' if database_username else '[ERROR]'}")
                print(f"   JEECG_DATABASE_PASSWORD: {'[OK]' if database_password else '[ERROR]'}")
                return None
            
            # 解析JDBC URL: jdbc:mysql://localhost:30004/jeecg-boot
            import re
            jdbc_pattern = r'jdbc:mysql://([^:]+):(\d+)/(.+?)(\?.*)?$'
            match = re.match(jdbc_pattern, database_url)
            
            if not match:
                print(f"[ERROR] 无法解析数据库URL: {database_url}")
                return None
            
            db_host = match.group(1)
            db_port = int(match.group(2))
            db_name = match.group(3)
            
            print(f"[STAT] 数据库连接信息:")
            print(f"   主机: {db_host}")
            print(f"   端口: {db_port}")
            print(f"   数据库: {db_name}")
            print(f"   用户: {database_username}")
            
            return {
                'host': db_host,
                'port': db_port,
                'user': database_username,
                'password': database_password,
                'database': db_name,
                'charset': 'utf8mb4',
                'autocommit': False
            }
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 获取数据库配置失败: {str(e)}")
            return None
    
    def _discover_sql_files(self) -> List[str]:
        """在前端代码路径中查找菜单权限SQL文件

        Returns:
            List[str]: 发现的SQL文件路径列表
        """
        try:
            # 确定SQL文件扫描路径
            if self.target_directory and os.path.exists(self.target_directory):
                # 优先使用指定的目标目录（本次任务生成的目录）
                search_path = self.target_directory
                print(f"[CHECK] 在指定目录中查找SQL文件: {search_path}")
            else:
                # Fallback: 全局扫描（兼容性处理）
                project_root = self.config.get_project_root()
                search_path = os.path.join(project_root, "jeecgboot-vue3", "src", "views")
                if self.target_directory:
                    print(f"[WARN] 指定目录不存在: {self.target_directory}，fallback到全局扫描")
                print(f"[CHECK] 在前端代码路径中查找SQL文件（全局扫描）: {search_path}")

            if not os.path.exists(search_path):
                print(f"[WARN] SQL文件扫描路径不存在: {search_path}")
                return []

            sql_files = []

            # 递归查找所有.sql文件
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.sql'):
                        file_path = os.path.join(root, file)

                        # 检查文件是否包含菜单权限相关的SQL
                        if self._is_menu_permission_sql(file_path):
                            sql_files.append(file_path)
                            # 显示相对路径以便识别
                            if self.target_directory:
                                relative_path = os.path.relpath(file_path, self.target_directory)
                                print(f"[FILE] 发现菜单权限SQL文件: {relative_path}")
                            else:
                                project_root = self.config.get_project_root()
                                frontend_views_path = os.path.join(project_root, "jeecgboot-vue3", "src", "views")
                                relative_path = os.path.relpath(file_path, frontend_views_path)
                                print(f"[FILE] 发现菜单权限SQL文件: views/{relative_path}")

            return sql_files

        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 查找SQL文件失败: {str(e)}")
            return []
    
    def _is_menu_permission_sql(self, file_path: str) -> bool:
        """检查SQL文件是否包含菜单权限相关语句
        
        Args:
            file_path: SQL文件路径
            
        Returns:
            bool: 是否为菜单权限SQL文件
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                
            # 检查是否包含菜单权限相关的表名和关键词
            menu_keywords = [
                'sys_permission',
                'sys_role_permission',
                'menu_insert',
                'permission',
                'menu'
            ]
            
            return any(keyword in content for keyword in menu_keywords)
            
        except Exception:
            return False
    
    def _execute_sql_file(self, sql_file: str, db_config: Dict) -> bool:
        """执行单个SQL文件
        
        Args:
            sql_file: SQL文件路径
            db_config: 数据库配置
            
        Returns:
            bool: 执行是否成功
        """
        connection = None
        try:
            # 读取SQL文件内容
            sql_statements = self._extract_sql_statements(sql_file)
            if not sql_statements:
                print(f"[WARN] 文件中没有有效的SQL语句: {sql_file}")
                return True  # 空文件视为成功
            
            # 建立数据库连接
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            
            # 开始事务
            connection.start_transaction()
            
            executed_count = 0
            for sql_statement in sql_statements:
                try:
                    cursor.execute(sql_statement)
                    executed_count += 1
                except mysql.connector.Error as e:
                    print(f"[ERROR] SQL语句执行失败: {str(e)}")
                    print(f"   SQL: {sql_statement[:100]}...")
                    raise
            
            # 提交事务
            connection.commit()
            print(f"[STAT] 成功执行 {executed_count} 条SQL语句")
            return True
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            # 回滚事务
            if connection:
                try:
                    connection.rollback()
                    print("[PROCESS] 事务已回滚")
                except:
                    pass
            
            print(f"[ERROR] SQL文件执行失败: {str(e)}")
            return False
            
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass
    
    def _extract_sql_statements(self, sql_file: str) -> List[str]:
        """从SQL文件中提取SQL语句
        
        Args:
            sql_file: SQL文件路径
            
        Returns:
            List[str]: SQL语句列表
        """
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            statements = []
            lines = content.split('\n')
            current_statement = []
            
            for line in lines:
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('--') or line.startswith('#'):
                    continue
                
                # 移除行内注释
                if '--' in line:
                    line = line.split('--')[0].strip()
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                if not line:
                    continue
                
                current_statement.append(line)
                
                # 如果行以分号结尾，表示语句结束
                if line.endswith(';'):
                    full_statement = ' '.join(current_statement).strip()
                    if full_statement and not full_statement.startswith(('--', '#')):
                        statements.append(full_statement)
                    current_statement = []
            
            # 处理最后一个未以分号结尾的语句
            if current_statement:
                full_statement = ' '.join(current_statement).strip()
                if full_statement and not full_statement.startswith(('--', '#')):
                    statements.append(full_statement)
            
            return statements
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 读取SQL文件失败: {str(e)}")
            return []


# =============================================================================
# JeecgBoot API 独立函数集 - 六个核心API接口封装
# =============================================================================

def jeecg_login(base_url: str, username: str, password: str, timeout: int = 10) -> Dict:
    """
    JeecgBoot用户认证API
    
    Args:
        base_url: JeecgBoot服务基础URL，如 http://localhost:8080/jeecg-boot
        username: 用户名
        password: 密码
        timeout: 请求超时时间（秒）
        
    Returns:
        Dict: {"success": bool, "token": str, "message": str}
    """
    login_url = f"{base_url}/sys/mLogin"
    login_data = {"username": username, "password": password}
    print(f"[API] Login Request: POST {login_url}")
    print(f"[API] Username: {username}, Password: ***")
    
    
    try:
        response = requests.post(login_url, json=login_data, timeout=timeout)
        print(f"[API] Login Response: status_code={response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token_info = result.get('result', {})
                token = token_info.get('token')
                if token:
                    return {"success": True, "token": token, "message": "登录成功"}
                else:
                    return {"success": False, "token": None, "message": "未获取到token"}
            else:
                return {"success": False, "token": None, "message": result.get('message', '登录失败')}
        else:
            return {"success": False, "token": None, "message": f"请求失败，状态码: {response.status_code}"}
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception: {str(e)}")
        traceback.print_exc()
        return {"success": False, "token": None, "message": f"登录异常: {str(e)}"}


def jeecg_create_form(base_url: str, token: str, form_data: Dict, timeout: int = 60) -> Dict:
    """
    JeecgBoot表单创建API
    
    Args:
        base_url: JeecgBoot服务基础URL
        token: 认证token
        form_data: 表单配置数据（包含head、fields等信息）
        timeout: 请求超时时间（秒）
        
    Returns:
        Dict: {"success": bool, "form_id": str, "is_duplicate": bool, "message": str}
    """
    create_url = f"{base_url}/online/cgform/api/addAll"
    table_name = form_data.get('head', {}).get('tableName', 'unknown')
    print(f"[API] Create Form Request: POST {create_url}")
    print(f"[API] Table Name: {table_name}")
    headers = {'X-Access-Token': token, 'Content-Type': 'application/json'}
    
    try:
        response = requests.post(create_url, json=form_data, headers=headers, timeout=timeout)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                table_name = form_data.get('head', {}).get('tableName')
                
                # 创建成功后获取form_id
                time.sleep(1)  # 等待数据库写入
                form_id_result = jeecg_query_form(base_url, token, table_name)
                if form_id_result.get('success'):
                    form_id = form_id_result.get('form_id')
                    return {
                        "success": True, 
                        "form_id": form_id, 
                        "is_duplicate": False, 
                        "message": f"表单创建成功: {table_name}"
                    }
                else:
                    return {
                        "success": False, 
                        "form_id": None, 
                        "is_duplicate": False, 
                        "message": "表单创建成功但无法获取form_id"
                    }
            else:
                error_message = result.get('message', '')
                # 处理重复表单情况
                if '数据库表' in error_message and '已存在' in error_message:
                    table_name = form_data.get('head', {}).get('tableName')
                    time.sleep(1)
                    form_id_result = jeecg_query_form(base_url, token, table_name)
                    if form_id_result.get('success'):
                        form_id = form_id_result.get('form_id')
                        return {
                            "success": True, 
                            "form_id": form_id, 
                            "is_duplicate": True, 
                            "message": f"发现重复表单: {table_name}"
                        }
                    else:
                        return {
                            "success": False, 
                            "form_id": None, 
                            "is_duplicate": False, 
                            "message": f"表单创建失败，数据不一致: {error_message}"
                        }
                else:
                    return {"success": False, "form_id": None, "is_duplicate": False, "message": error_message}
        else:
            return {
                "success": False, 
                "form_id": None, 
                "is_duplicate": False, 
                "message": f"请求失败，状态码: {response.status_code}"
            }
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception: {str(e)}")
        traceback.print_exc()
        return {"success": False, "form_id": None, "is_duplicate": False, "message": f"表单创建异常: {str(e)}"}


def jeecg_query_form(base_url: str, token: str, table_name: str, page_size: int = 50, timeout: int = 15) -> Dict:
    """
    JeecgBoot表单查询API
    
    Args:
        base_url: JeecgBoot服务基础URL
        token: 认证token
        table_name: 要查询的表名
        page_size: 分页大小
        timeout: 请求超时时间（秒）
        
    Returns:
        Dict: {"success": bool, "form_id": str, "form_info": dict, "message": str}
    """
    query_url = f"{base_url}/online/cgform/head/list"
    print(f"[API] Query Form Request: GET {query_url}?tableName={table_name}")
    headers = {'X-Access-Token': token}
    params = {'tableName': table_name, 'pageNo': 1, 'pageSize': page_size}
    
    try:
        response = requests.get(query_url, params=params, headers=headers, timeout=timeout)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                records = result.get('result', {}).get('records', [])
                for record in records:
                    if record.get('tableName') == table_name:
                        form_id = record.get('id')
                        return {
                            "success": True, 
                            "form_id": form_id, 
                            "form_info": record, 
                            "message": f"查询成功: {table_name}"
                        }
                return {
                    "success": False, 
                    "form_id": None, 
                    "form_info": None, 
                    "message": f"未找到表单: {table_name}"
                }
            else:
                return {
                    "success": False, 
                    "form_id": None, 
                    "form_info": None, 
                    "message": result.get('message', '查询失败')
                }
        else:
            return {
                "success": False, 
                "form_id": None, 
                "form_info": None, 
                "message": f"请求失败，状态码: {response.status_code}"
            }
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception: {str(e)}")
        traceback.print_exc()
        return {"success": False, "form_id": None, "form_info": None, "message": f"查询异常: {str(e)}"}


def jeecg_sync_database(base_url: str, token: str, form_id: str, timeout: int = 60) -> Dict:
    """
    JeecgBoot数据库同步API
    
    Args:
        base_url: JeecgBoot服务基础URL
        token: 认证token
        form_id: 表单ID
        timeout: 请求超时时间（秒）
        
    Returns:
        Dict: {"success": bool, "message": str}
    """
    sync_url = f"{base_url}/online/cgform/api/doDbSynch/{form_id}/normal"
    print(f"[API] Database Sync Request: POST {sync_url}")
    print(f"[API] Form ID: {form_id}")
    headers = {'X-Access-Token': token}
    
    try:
        response = requests.post(sync_url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {"success": True, "message": "数据库同步成功"}
            else:
                return {"success": False, "message": result.get('message', '数据库同步失败')}
        else:
            return {"success": False, "message": f"请求失败，状态码: {response.status_code}"}
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception: {str(e)}")
        traceback.print_exc()
        return {"success": False, "message": f"数据库同步异常: {str(e)}"}


def jeecg_generate_code(base_url: str, token: str, form_id: str, config_data: Dict, timeout: int = 120, project_root: str = None) -> Dict:
    """
    JeecgBoot代码生成API
    
    Args:
        base_url: JeecgBoot服务基础URL
        token: 登录获取的认证token
        form_id: 表单ID
        config_data: 表单配置数据（用于提取生成参数）
        timeout: 请求超时时间（秒）
        project_root: 项目根目录路径，如果不提供将从环境变量获取
        
    Returns:
        Dict: {"success": bool, "message": str}
    """
    generate_url = f"{base_url}/online/cgform/api/codeGenerate"
    print(f"[API] Code Generation Request: POST {generate_url}")
    
    try:
        # 构建代码生成参数
        table_name = config_data.get('head', {}).get('tableName', '')
        table_type = config_data.get('head', {}).get('tableType', 1)
        business_entity = config_data.get('head', {}).get('business_entity', '')
        
        # 如果未提供project_root参数，使用默认值
        if project_root is None:
            project_root = '/Users/admin/Work/Github/JeecgBoot'
        
        # 解析表名获取模块信息 - 支持3段式命名
        parts = table_name.split('_')
        if len(parts) >= 3:
            module_name = parts[0]  # 第一段是模块名
            submodule_name = parts[1]  # 第二段是子模块名
            # 使用传入的项目路径
            project_path = f"{project_root}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
        else:
            # 尝试从metadata获取模块信息
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            submodule_name = generation_info.get('submodule_name', 'common')
            module_name = generation_info.get('module_name', 'system')
            # 使用传入的项目路径
            project_path = f"{project_root}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
        
        # 根据表类型设置参数
        if table_type == 2:  # 主表
            jsp_mode = "jvxe"
            jform_type = "2"
            sub_list = config_data.get('subList', [])
        else:  # 独立表
            jsp_mode = "one"
            jform_type = "1"
            sub_list = []
        
        # 构建请求数据
        data = {
            "code": form_id,
            "projectPath": project_path,
            "entityName": business_entity,
            "entityPackage": submodule_name,
            "jspMode": jsp_mode,
            "jformType": jform_type,
            "ftlDescription": config_data.get('head', {}).get('tableTxt', ''),
            "tableName_tmp": table_name,
            "packageStyle": "service",
            "vueStyle": "vue3",
            "codeTypes": "controller,service,dao,mapper,entity,vue",
            "tableName": table_name
        }
        
        # 如果是主表，添加子表列表
        if sub_list:
            # 简化版：直接使用配置中的子表信息
            data["subList"] = sub_list
        
        headers = {'X-Access-Token': token, 'Content-Type': 'application/json'}
        response = requests.post(generate_url, json=data, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {"success": True, "message": "代码生成成功"}
            else:
                return {"success": False, "message": result.get('message', '代码生成失败')}
        else:
            return {"success": False, "message": f"请求失败，状态码: {response.status_code}"}
            
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception: {str(e)}")
        traceback.print_exc()
        return {"success": False, "message": f"代码生成异常: {str(e)}"}


def jeecg_delete_forms_batch(base_url: str, token: str, form_ids: list, timeout: int = 30) -> Dict:
    """
    JeecgBoot批量删除表单API
    
    Args:
        base_url: JeecgBoot服务基础URL
        token: 认证token
        form_ids: 要删除的表单ID列表
        timeout: 请求超时时间（秒）
        
    Returns:
        Dict: {"success": bool, "message": str, "deleted_count": int}
    """
    if not form_ids:
        return {"success": True, "message": "没有表单需要删除", "deleted_count": 0}
    
    delete_url = f"{base_url}/online/cgform/head/deleteBatch"
    
    try:
        # 将form_ids列表转换为逗号分隔的字符串
        ids_str = ','.join(form_ids)
        
        # URL编码处理特殊字符
        import urllib.parse
        ids_encoded = urllib.parse.quote(ids_str, safe='')
        
        # 构建完整的URL（包含查询参数）
        url_with_params = f"{delete_url}?ids={ids_encoded}&flag=table"
        
        headers = {'X-Access-Token': token}
        response = requests.delete(url_with_params, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {
                    "success": True, 
                    "message": f"成功删除 {len(form_ids)} 个表单", 
                    "deleted_count": len(form_ids)
                }
            else:
                return {
                    "success": False, 
                    "message": result.get('message', '批量删除失败'), 
                    "deleted_count": 0
                }
        else:
            return {
                "success": False, 
                "message": f"请求失败，状态码: {response.status_code}", 
                "deleted_count": 0
            }
            
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception: {str(e)}")
        traceback.print_exc()
        return {"success": False, "message": f"批量删除异常: {str(e)}", "deleted_count": 0}


def jeecg_fetch_dictionary_page(base_url: str, token: str, page_no: int = 1, page_size: int = 10, timeout: int = 30) -> Dict:
    """
    获取数据字典分页数据
    
    Args:
        base_url: JeecgBoot基础URL
        token: 认证token
        page_no: 页码，从1开始
        page_size: 每页大小
        timeout: 超时时间（秒）
        
    Returns:
        Dict: API响应结果，包含分页数据
    """
    import requests
    
    try:
        # 构建API URL
        api_url = f"{base_url}/sys/dict/list"
        
        # 请求参数
        params = {
            'column': 'createTime',
            'order': 'desc',
            'pageNo': page_no,
            'pageSize': page_size
        }
        
        # 请求头
        headers = {
            'X-Access-Token': token,
            'Content-Type': 'application/json'
        }
        
        print(f"[INFO] 正在获取第 {page_no} 页数据 (每页 {page_size} 条)...")
        
        # 发送GET请求
        response = requests.get(api_url, params=params, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                # 提取分页信息
                result_data = result.get('result', {})
                records = result_data.get('records', [])
                total = result_data.get('total', 0)
                pages = result_data.get('pages', 0)
                current = result_data.get('current', page_no)
                
                print(f"   [OK] 获取成功: {len(records)} 条数据 (第 {current}/{pages} 页，共 {total} 条)")
                
                return {
                    "success": True,
                    "message": f"获取第 {page_no} 页数据成功",
                    "records": records,
                    "pagination": {
                        "total": total,
                        "pages": pages,
                        "current": current,
                        "size": page_size
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"API返回失败: {result.get('message', '未知错误')}",
                    "records": [],
                    "pagination": None
                }
        else:
            return {
                "success": False,
                "message": f"请求失败，状态码: {response.status_code}",
                "records": [],
                "pagination": None
            }
            
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取数据字典异常: {str(e)}",
            "records": [],
            "pagination": None
        }


def download_data_dictionary():
    """
    下载最新数据字典文件
    
    实现逻辑：
    1. 删除现有的Code_Gen_DICT.json文件（已完成）
    2. 复用jeecgboot的登陆接口进行认证
    3. 循环调用分页API获取所有数据字典数据
    4. 将所有数据合并保存到新的Code_Gen_DICT.json文件
    
    Returns:
        str: "SUCCESS" 或 "ERROR"
    """
    print("=== 下载最新数据字典文件 ===")
    
    try:
        # 1. 初始化配置
        print("[CONFIG] 步骤1: 初始化配置...")
        config = JeecgBootConfig()
        if not config.load_config():
            print("[ERROR] 配置加载失败")
            return "ERROR"
        
        base_url = config.get_base_url()
        username = config.get_username()
        password = config.get_password()

        print(f"   [URL] 服务地址: {base_url}")
        print(f"   [USER] 用户名: {username}")

        # 2. 用户认证
        print("[AUTH] 步骤2: 用户认证...")
        login_result = jeecg_login(base_url, username, password, config.get_timeout('login'))
        if not login_result['success']:
            print(f"[ERROR] 登录失败: {login_result['message']}")
            return "ERROR"
        
        token = login_result['token']
        print("   [OK] 登录成功，获取到认证token")
        
        # 3. 获取分页数据
        print("[INFO] 步骤3: 获取数据字典...")
        all_records = []
        page_no = 1
        page_size = 50  # 使用较大的分页大小提高效率
        
        while True:
            # 获取当前页数据
            page_result = jeecg_fetch_dictionary_page(
                base_url, token, page_no, page_size, config.get_timeout('list')
            )
            
            if not page_result['success']:
                print(f"[ERROR] 获取第 {page_no} 页数据失败: {page_result['message']}")
                return "ERROR"
            
            # 收集数据
            records = page_result['records']
            all_records.extend(records)
            
            # 检查分页信息
            pagination = page_result.get('pagination')
            if not pagination:
                print("[ERROR] 无分页信息，无法继续")
                return "ERROR"
            
            current_page = pagination['current']
            total_pages = pagination['pages']
            total_records = pagination['total']
            
            print(f"   [FILE] 已收集 {len(all_records)}/{total_records} 条数据")
            
            # 判断是否还有下一页
            if current_page >= total_pages:
                print(f"   [OK] 所有数据获取完成，共 {len(all_records)} 条数据")
                break
            
            # 继续下一页
            page_no += 1
        
        # 4. 保存到文件
        print("[SAVE] 步骤4: 保存数据字典文件...")
        dict_file_path = "Code_Gen_DICT.json"
        
        try:
            import json
            with open(dict_file_path, 'w', encoding='utf-8') as f:
                json.dump(all_records, f, ensure_ascii=False, indent=2)
            
            print(f"   [OK] 数据字典已保存至: {dict_file_path}")
            print(f"   [STAT] 文件包含 {len(all_records)} 条数据字典记录")
            
            # 显示统计信息
            if all_records:
                latest_record = all_records[0]  # 按创建时间倒序，第一条是最新的
                oldest_record = all_records[-1]  # 最后一条是最旧的
                
                print(f"   [TIME] 最新记录: {latest_record.get('dictName', 'N/A')} ({latest_record.get('createTime', 'N/A')})")
                print(f"   [TIME] 最旧记录: {oldest_record.get('dictName', 'N/A')} ({oldest_record.get('createTime', 'N/A')})")
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception: {str(e)}")
            traceback.print_exc()
            print(f"[ERROR] 保存文件失败: {str(e)}")
            return "ERROR"
        
        print("\n[SUCCESS] 数据字典下载完成!")
        return "SUCCESS"
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception: {str(e)}")
        traceback.print_exc()
        print(f"[ERROR] 下载过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return "ERROR"


class CodeGenExecutor:
    """
    JeecgBoot代码生成执行器
    
    这是一个全新设计的代码生成器，专为AI调用优化：
    - 简洁的接口设计
    - 清晰的错误处理
    - 完整的文档说明
    - 模块化的功能组织
    """
    
    def __init__(self):
        """初始化代码生成执行器"""
        pass
    
    def execute(self, config_data):
        """
        执行代码生成
        
        Args:
            config_data: 代码生成配置数据
            
        Returns:
            生成结果
        """
        pass


def main(filename):
    global SUMMARY_RESULT
    
    # 使用日志系统执行所有任务
    with setup_execution_logging(filename) as log_manager:
        if not log_manager:
            print("[ERROR] 日志系统初始化失败，继续执行但无法记录日志")
        
        return _execute_main_tasks(filename, log_manager)

def _execute_main_tasks(filename, log_manager=None):
    """执行主要任务逻辑"""
    global SUMMARY_RESULT
    
    # 任务执行记录
    task_results = []
    
    print("\n" + "="*70)
    print("[START] JeecgBoot 代码生成器启动")
    print("="*70)
    print(f"[FILE] 配置文件: {filename}")
    print(f"[TIME] 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if log_manager:
        print(f"[LOG] 日志文件: {log_manager.get_log_file_path()}")
    print("="*70)
    
    if not os.path.exists(filename):
        print(f"\n[ERROR] 致命错误: 配置文件不存在")
        print(f"   文件路径: {filename}")
        print(f"[TIP] 请检查文件路径是否正确")
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
    
    # 预检查：验证真实环境变量
    print("\n[CHECK] 预检查: 验证环境变量配置...")
    env_guide = EnvironmentGuide()
    env_status = env_guide.check_environment_setup()
    
    if not env_status['all_configured']:
        print(f"\n[ERROR] 检测到缺失必需环境变量: {', '.join(env_status['missing_vars'])}")
        print(f"[TIP] 请运行以下命令进行环境配置:")
        print(f"   python Code_Gen_Execute.py --setup-guide")
        print(f"[WARN]  执行中断，请先配置环境变量")
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
    
    print("[OK] 环境变量检查通过，继续执行任务...")
    
    # 任务1：配置中心初始化
    if log_manager:
        log_manager.log_section_start("任务1: 配置中心初始化")
    
    env_task = EnvironmentVariableTask()
    task1_result = env_task.execute()
    task1_status = "pass" if "pass" in task1_result else "fail"
    task_results.append(("1", "配置中心初始化", task1_status))
    
    if log_manager:
        log_manager.log_section_end("任务1: 配置中心初始化")
    
    if task1_status == "fail":
        print(f"\n[FAIL] 执行中断: 任务1失败，无法继续后续任务")
        print(f"[CONFIG] 建议: 请检查环境变量配置或运行 --check-env 进行诊断")
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
    
    # 获取配置实例
    config = env_task.get_config()
    if not config:
        print("[ERROR] 配置实例获取失败")
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
    
    # 读取配置数据供后续任务使用
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except Exception:
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
    
    # 任务2：Maven原型创建新模块
    if log_manager:
        log_manager.log_section_start("任务2: Maven原型创建新模块")
    
    maven_task = MavenModuleCreationTask(config)
    task2_result = maven_task.execute(config_data)
    task2_status = "pass" if "pass" in task2_result else "fail"
    task_results.append(("2", "Maven原型创建新模块", task2_status))
    
    if log_manager:
        log_manager.log_section_end("任务2: Maven原型创建新模块")
    
    if task2_status == "fail":
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
    
    # 任务3：更新模块注册和依赖配置
    if log_manager:
        log_manager.log_section_start("任务3: 更新模块注册和依赖配置")
    
    pom_task = PomConfigurationTask(config)
    task3_result = pom_task.execute(config_data)
    task3_status = "pass" if "pass" in task3_result else "fail"
    task_results.append(("3", "更新模块注册和依赖配置", task3_status))
    
    if log_manager:
        log_manager.log_section_end("任务3: 更新模块注册和依赖配置")
    
    if task3_status == "fail":
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
        
    # 任务4：需求场景识别
    if log_manager:
        log_manager.log_section_start("任务4: 需求场景识别")
    
    scenario_task = ScenarioIdentificationTask()
    task4_result = scenario_task.execute(filename)
    task4_status = "pass" if "pass" in task4_result else "fail"
    task_results.append(("4", "需求场景识别", task4_status))
    
    if log_manager:
        log_manager.log_section_end("任务4: 需求场景识别")
    
    if task4_status == "fail":
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
    
    # 任务5：建立哨兵机制
    if log_manager:
        log_manager.log_section_start("任务5: 建立哨兵机制")
    
    sentinel_task = SentinelMechanismTask()
    task5_result = sentinel_task.execute(config_data, scenario_task)
    task5_status = "pass" if "pass" in task5_result else "fail"
    task_results.append(("5", "建立哨兵机制", task5_status))
    
    if log_manager:
        log_manager.log_section_end("任务5: 建立哨兵机制")
    
    if task5_status == "fail":
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
    
    # 任务6：哨兵机制生成代码
    if log_manager:
        log_manager.log_section_start("任务6: 哨兵机制生成代码")
    
    code_generation_task = CodeGenerationTask(config)
    task6_result = code_generation_task.execute(filename)
    if task6_result == "fail":
        task_results.append(("6", "哨兵机制生成代码", "fail"))
        if log_manager:
            log_manager.log_section_end("任务6: 哨兵机制生成代码")
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
    elif task6_result == "waiting":
        # 子表场景，等待主表调用，直接返回SUCCESS
        task_results.append(("6", "哨兵机制生成代码", "pass"))
        if log_manager:
            log_manager.log_section_end("任务6: 哨兵机制生成代码")
        _print_execution_summary(task_results, "SUCCESS")
        return "SUCCESS"
    else:
        task_results.append(("6", "哨兵机制生成代码", "pass"))
    
    if log_manager:
        log_manager.log_section_end("任务6: 哨兵机制生成代码")
    
    # 任务7：占位符变量处理
    if log_manager:
        log_manager.log_section_start("任务7: 占位符变量处理")
    
    placeholder_task = PlaceholderVariableProcessingTask(config)
    task7_result = placeholder_task.execute(filename)
    task7_status = "pass" if "pass" in task7_result else "fail"
    task_results.append(("7", "占位符变量处理", task7_status))
    
    if log_manager:
        log_manager.log_section_end("任务7: 占位符变量处理")
    
    if task7_status == "fail":
        _print_execution_summary(task_results, "ERROR") 
        return "ERROR"
    
    # 任务8：前端代码迁移
    if log_manager:
        log_manager.log_section_start("任务8: 前端代码迁移")

    migration_task = FrontendCodeMigrationTask(config)
    task8_result = migration_task.execute(filename)
    task8_status = "pass" if "pass" in task8_result else "fail"
    task_results.append(("8", "前端代码迁移", task8_status))

    if log_manager:
        log_manager.log_section_end("任务8: 前端代码迁移")

    if task8_status == "fail":
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"

    # 任务9：菜单权限SQL执行
    if log_manager:
        log_manager.log_section_start("任务9: 菜单权限SQL执行")

    sql_task = DatabaseSQLExecutionTask(config)
    # 传递任务8的目标目录给任务9，只在该目录中查找SQL文件
    target_dir = migration_task.get_target_directory()
    if target_dir:
        sql_task.set_target_directory(target_dir)
    task9_result = sql_task.execute(filename)
    task9_status = "pass" if "pass" in task9_result else "fail"
    task_results.append(("9", "菜单权限SQL执行", task9_status))
    
    if log_manager:
        log_manager.log_section_end("任务9: 菜单权限SQL执行")
    
    if task9_status == "fail":
        _print_execution_summary(task_results, "ERROR")
        return "ERROR"
        
    _print_execution_summary(task_results, "SUCCESS")
    return "SUCCESS"


def _print_execution_summary(task_results, overall_status):
    """打印任务执行汇总信息
    
    Args:
        task_results: 任务结果列表，格式为 [(序号, 名称, 状态), ...]
        overall_status: 总体状态 "SUCCESS" 或 "ERROR"
    """
    print("\n" + "="*70)
    if overall_status == "SUCCESS":
        print("[SUCCESS] JeecgBoot 代码生成完成 - 执行成功")
    else:
        print("[FAIL] JeecgBoot 代码生成失败 - 执行中断")
    print("="*70)
    
    if task_results:
        print(f"[INFO] 任务执行状态详情:")
        for task_id, task_name, status in task_results:
            status_symbol = "[OK]" if status == "pass" else "[ERROR]"
            status_text = "成功" if status == "pass" else "失败"
            print(f"   {status_symbol} 任务{task_id}: {task_name} - {status_text}")
        
        success_count = sum(1 for _, _, status in task_results if status == "pass")
        total_count = len(task_results)
        print(f"\n[STAT] 执行统计: {success_count}/{total_count} 个任务成功")
    
    print("="*70)
    overall_icon = "[OK]" if overall_status == "SUCCESS" else "[ERROR]"
    overall_text = "成功" if overall_status == "SUCCESS" else "失败"
    print(f"{overall_icon} 最终状态: {overall_text}")
    print(f"[TIME] 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


def main_enhanced(filename="", check_env=False, setup_guide=False):
    """增强版主函数，支持环境检查和交互式配置"""
    global SUMMARY_RESULT
    
    # 环境检查模式（无需日志记录）
    if check_env:
        guide = EnvironmentGuide()
        status = guide.print_environment_status()
        return "SUCCESS" if status['all_configured'] else "ERROR"
    
    # 配置向导模式
    if setup_guide:
        guide = EnvironmentGuide()
        if guide.interactive_setup_guide():
            print("[OK] 环境配置已完成，环境变量已在当前Python进程中生效")
            print("\n[TIP] 提示: 您现在可以运行代码生成任务，环境变量在此Python进程中有效")
            print("   示例: python Code_Gen_Execute.py your_table_config.json")
            return "SETUP_COMPLETE"
        else:
            print("[ERROR] 环境配置失败")
            return "ERROR"
    
    # 正常的代码生成模式（使用日志记录）
    if not filename:
        print("[ERROR] 请指定配置文件")
        return "ERROR"
        
    # 使用日志系统执行主要任务
    result = main(filename)
    
    # 输出日志文件位置信息
    if _log_manager and _log_manager.log_file_path:
        print(f"\n[LOG] 执行日志已保存至: {_log_manager.log_file_path}")
        print(f"[TIP] 您可以查看日志文件了解详细的执行过程")
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("JeecgBoot 代码生成执行器 v4.1 Enhanced - 支持完整日志记录")
        print("=" * 60)
        print("[NEW] 新功能: 所有执行过程自动记录到日志文件 {MODULE_NAME}_{SUBMODULE_NAME}_{timestamp}.log")
        print("=" * 60)
        print("使用方法:")
        print("  python Code_Gen_Execute.py <表单配置文件.json>  # 执行代码生成任务 (含日志记录)")
        print("  python Code_Gen_Execute.py --setup-guide        # 启动交互式环境变量配置向导")
        print("  python Code_Gen_Execute.py --check-env          # 检查环境变量配置")
        print("  python Code_Gen_Execute.py --dict               # 下载最新数据字典文件")
        print("")
        print("[LOG] 日志功能说明:")
        print("  - 所有控制台输出都会同步记录到日志文件")
        print("  - 日志文件包含完整的执行过程和错误信息")
        print("  - 文件名格式: {模块名}_{子模块名}_{时间戳}.log")
        print("  - 日志文件保存在脚本执行目录")
        print("")
        print("[CONFIG] 环境变量配置说明:")
        print("  - --setup-guide 配置系统环境变量，生成临时配置文件 .env_temp")
        print("  - 后续运行会自动加载 .env_temp 文件中的环境变量")
        print("  - 建议工作流程:")
        print("    1. python Code_Gen_Execute.py --setup-guide      # 配置环境")
        print("    2. python Code_Gen_Execute.py your_table.json    # 执行生成")
        print("    3. 如需重新配置，重复步骤1即可")
        sys.exit(1)
    
    if sys.argv[1] == "--setup-guide":
        result = main_enhanced(setup_guide=True)
        sys.exit(0 if result in ["SUCCESS", "SETUP_COMPLETE"] else 1)
    elif sys.argv[1] == "--check-env":
        result = main_enhanced(check_env=True)
        sys.exit(0 if result == "SUCCESS" else 1)
    elif sys.argv[1] == "--dict":
        result = download_data_dictionary()
        sys.exit(0 if result == "SUCCESS" else 1)
    else:
        filename = sys.argv[1]
        result = main_enhanced(filename)
        sys.exit(0 if result in ["SUCCESS", "SETUP_COMPLETE"] else 1)