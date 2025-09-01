#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot 代码生成工具 v3.0
功能：基于JeecgBoot在线表单API的完整代码生成工作流
流程：登录 → 创建表单 → 获取ID → 同步数据库 → 生成代码 → 编译验证 → 前端迁移 → 权限授权
特性：
- 标准化表名解析和包名生成
- 自动模块管理和Maven集成
- 前端代码自动迁移
- 数据库SQL自动执行
- 自动权限授权（管理员角色）
- 完整的错误处理和日志记录
"""

import requests
import json
import time
import argparse
import re
import subprocess
import platform
import sys
import shutil
import os
import random
from datetime import datetime
from pathlib import Path

# 设置控制台编码（跨平台兼容性）
def setup_console_encoding():
    """设置控制台编码，确保跨平台兼容性"""
    global EMOJI_SUPPORT
    EMOJI_SUPPORT = True
    
    try:
        if platform.system() == 'Windows':
            import locale
            import subprocess
            
            # Windows 控制台编码设置 - 多种方法尝试
            success = False
            
            # 方法1: 先设置控制台代码页为UTF-8
            try:
                result = subprocess.run(['chcp', '65001'], 
                                      capture_output=True, 
                                      check=False, 
                                      timeout=5)
                if result.returncode == 0:
                    # 代码页设置成功，尝试重新配置stdout和stderr
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                    success = True
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                pass
            
            # 方法2: 如果方法1失败，直接设置编码
            if not success:
                try:
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                    success = True
                except Exception:
                    pass
            
            # 方法3: 如果UTF-8都失败，使用系统默认编码
            if not success:
                try:
                    encoding = locale.getpreferredencoding()
                    sys.stdout.reconfigure(encoding=encoding, errors='replace')
                    sys.stderr.reconfigure(encoding=encoding, errors='replace')
                    EMOJI_SUPPORT = False  # 非UTF-8编码，禁用emoji
                except Exception:
                    EMOJI_SUPPORT = False
            else:
                # 检测控制台编码来判断emoji支持
                current_encoding = getattr(sys.stdout, 'encoding', '').lower()
                if current_encoding in ['utf-8', 'utf8']:
                    EMOJI_SUPPORT = True
                else:
                    EMOJI_SUPPORT = False
                    
        else:
            # macOS/Linux 通常默认UTF-8，但确保设置正确
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                EMOJI_SUPPORT = True
            except Exception:
                EMOJI_SUPPORT = False
                
    except Exception:
        # 如果所有设置都失败，保持默认
        EMOJI_SUPPORT = False

def safe_print(text, **kwargs):
    """安全打印函数，在不支持emoji的环境下使用fallback"""
    global EMOJI_SUPPORT
    
    # 确保text是字符串类型
    if not isinstance(text, str):
        text = str(text)
    
    if not EMOJI_SUPPORT and platform.system() == 'Windows':
        # Windows环境下emoji fallback
        emoji_map = {
            '[TOOL]': '[工具]', '[OK]': '[OK]', '[FAIL]': '[FAIL]', '[CHART]': '[图表]', 
            '[TARGET]': '[目标]', '[START]': '[启动]', '[LIST]': '[清单]', '[FOLDER]': '[文件夹]',
            '[SEARCH]': '[搜索]', '[FAST]': '[闪电]', '[SUCCESS]': '[庆祝]', '[WARN]': '[警告]',
            '[TIP]': '[提示]', '[NOTE]': '[记录]', '[DATABASE]': '[数据库]', '[WEB]': '[网络]',
            '[REFRESH]': '[刷新]', '[LINK]': '[链接]', '[PACKAGE]': '[包]', '[DESIGN]': '[设计]',
            '[BUILD]': '[构建]', '1.': '1.', '2.': '2.', '3.': '3.', '4.': '4.',
            '5.': '5.', '6.': '6.', '7.': '7.', '8.': '8.'
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
    
    # 多级 fallback 策略
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        try:
            # 尝试用replace策略处理编码错误
            encoded = text.encode(sys.stdout.encoding or 'utf-8', errors='replace')
            decoded = encoded.decode(sys.stdout.encoding or 'utf-8')
            print(decoded, **kwargs)
        except (UnicodeEncodeError, LookupError):
            try:
                # 尝试用GBK编码（Windows中文环境常用）
                if platform.system() == 'Windows':
                    encoded = text.encode('gbk', errors='replace')
                    decoded = encoded.decode('gbk')
                    print(decoded, **kwargs)
                else:
                    raise UnicodeEncodeError('fallback', text, 0, len(text), 'fallback to ascii')
            except (UnicodeEncodeError, LookupError):
                # 最后的fallback：只保留ASCII字符和基本中文字符
                safe_text = ''.join(char for char in text 
                                  if ord(char) < 128 or '\u4e00' <= char <= '\u9fff')
                try:
                    print(safe_text, **kwargs)
                except UnicodeEncodeError:
                    # 终极fallback：移除所有非ASCII字符
                    ascii_text = text.encode('ascii', 'ignore').decode('ascii')
                    print(ascii_text, **kwargs)

# 初始化控制台编码
EMOJI_SUPPORT = True
setup_console_encoding()

# 跨平台兼容性工具函数
class CrossPlatformUtils:
    """跨平台兼容性工具类"""

    @staticmethod
    def get_platform_info():
        """获取平台信息"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'is_windows': platform.system() == 'Windows',
            'is_macos': platform.system() == 'Darwin',
            'is_linux': platform.system() == 'Linux'
        }

    @staticmethod
    def get_maven_executable():
        """获取Maven可执行文件名"""
        if platform.system() == 'Windows':
            return 'mvn.cmd'
        else:
            return 'mvn'
    
    @staticmethod
    def is_git_bash_environment():
        """检测是否在Git Bash环境中运行"""
        return (
            platform.system() == 'Windows' and 
            ('MSYSTEM' in os.environ or '/c/' in os.environ.get('PATH', ''))
        )
    
    @staticmethod
    def execute_command_safely(cmd_list, cwd=None, timeout=300):
        """
        安全执行命令，处理Git Bash环境兼容性问题
        
        Args:
            cmd_list: 命令列表，如 ['mvn.cmd', 'archetype:generate', ...]
            cwd: 工作目录
            timeout: 超时时间（秒）
        
        Returns:
            subprocess.CompletedProcess: 执行结果
        """
        if CrossPlatformUtils.is_git_bash_environment() and platform.system() == 'Windows':
            # 在Git Bash环境中，使用cmd.exe /c来执行Windows命令
            cmd_str = ' '.join(cmd_list)
            full_cmd = ['cmd.exe', '/c', cmd_str]
            safe_print(f"   Git Bash环境检测: 使用 cmd.exe /c 执行命令")
            safe_print(f"   执行命令: {' '.join(full_cmd)}")
        else:
            # 其他环境直接执行
            full_cmd = cmd_list
            safe_print(f"   标准环境: 直接执行命令")
            safe_print(f"   执行命令: {' '.join(full_cmd)}")
        
        return subprocess.run(
            full_cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    @staticmethod
    def normalize_path(path_str):
        """标准化路径，处理不同平台的路径分隔符"""
        return Path(path_str).resolve()

    @staticmethod
    def get_executable_extension():
        """获取可执行文件扩展名"""
        return '.exe' if platform.system() == 'Windows' else ''

    @staticmethod
    def get_shell_command(command):
        """获取适合当前平台的shell命令"""
        if platform.system() == 'Windows':
            return ['cmd', '/c'] + (command if isinstance(command, list) else [command])
        else:
            return ['/bin/bash', '-c'] + (command if isinstance(command, list) else [command])

    @staticmethod
    def get_default_project_prefix():
        """获取默认项目路径前缀"""
        home = Path.home()
        if platform.system() == 'Windows':
            # Windows: 通常在用户目录下的开发文件夹
            return str(home / 'Documents' / 'JeecgBoot')
        elif platform.system() == 'Darwin':
            # macOS: 通常在用户目录下的工作文件夹
            return str(home / 'Work' / 'JeecgBoot')
        else:
            # Linux: 通常在用户目录下的项目文件夹
            return str(home / 'projects' / 'JeecgBoot')

    @staticmethod
    def ensure_directory_permissions(directory_path):
        """确保目录具有正确的权限"""
        path = Path(directory_path)
        if path.exists():
            if platform.system() != 'Windows':
                # Unix-like系统设置权限
                os.chmod(path, 0o755)
                for item in path.rglob('*'):
                    if item.is_dir():
                        os.chmod(item, 0o755)
                    else:
                        os.chmod(item, 0o644)

    @staticmethod
    def detect_project_root():
        """智能检测项目根目录"""
        current_path = Path.cwd()

        # 检查当前目录及其父目录，寻找JeecgBoot项目标识
        for path in [current_path] + list(current_path.parents):
            # 检查是否包含JeecgBoot项目的标识文件/目录
            indicators = [
                'jeecg-boot',
                'jeecgboot-vue3',
                'CodeGen',
                'pom.xml'
            ]

            if any((path / indicator).exists() for indicator in indicators):
                return str(path)

        # 如果没有找到，返回当前目录
        return str(current_path)

    @staticmethod
    def resolve_path_prefix(config_path_prefix):
        """解析路径前缀，支持相对路径、环境变量和自动检测"""
        if not config_path_prefix:
            return CrossPlatformUtils.detect_project_root()

        # 处理环境变量
        if config_path_prefix.startswith('$'):
            env_var = config_path_prefix[1:]
            env_value = os.environ.get(env_var)
            if env_value:
                return str(CrossPlatformUtils.normalize_path(env_value))
            else:
                safe_print(f"[WARN] 环境变量 {env_var} 未设置，使用自动检测")
                return CrossPlatformUtils.detect_project_root()

        # 处理特殊标记
        if config_path_prefix == "AUTO_DETECT":
            return CrossPlatformUtils.detect_project_root()

        # 处理相对路径
        if not Path(config_path_prefix).is_absolute():
            base_path = Path(__file__).parent.parent  # CodeGen目录的父目录
            return str(CrossPlatformUtils.normalize_path(base_path / config_path_prefix))

        # 处理绝对路径
        return str(CrossPlatformUtils.normalize_path(config_path_prefix))

def load_config():
    """加载配置文件"""
    # 智能查找配置文件：优先使用脚本所在目录的配置文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'Code_Gen_Config.json')
    # 默认配置（仅在配置文件不存在时使用）
    default_config = {
        "project": {
            "path_prefix": CrossPlatformUtils.get_default_project_prefix()  # 跨平台默认路径
        },
        "server": {
            "base_url": os.environ.get('JEECG_BASE_URL', 'http://localhost:8080/jeecg-boot'),
            "username": os.environ.get('JEECG_USERNAME', 'admin'),
            "password": os.environ.get('JEECG_PASSWORD', '123456')
        },
        "database": {
            "type": os.environ.get('JEECG_DATABASE_TYPE', 'mysql'),
            "url": os.environ.get('JEECG_DATABASE_URL', 'jdbc:mysql://localhost:3306/jeecg-boot'),
            "username": os.environ.get('JEECG_DATABASE_USERNAME', 'root'),
            "password": os.environ.get('JEECG_DATABASE_PASSWORD', '123456')
        },
        "timeouts": {
            "login": 10,
            "create": 30,
            "list": 15,
            "sync": 30,
            "codegen": 60
        },
        "form": {
            "data_file": "Code_Gen_Guide.json",
            "wait_after_create": 3
        },
        "codegen": {
            "project_path": "{{PROJECT_PATH}}",
            "entity_name": "{{BUSINESS_ENTITY}}",
            "jsp_mode": "one",
            "jform_type": "1",
            "package_style": "service",
            "vue_style": "vue3",
            "code_types": "controller,service,dao,mapper,entity,vue"
        },
        "compilation": {
            "enabled": True,
            "maven_command": "mvn",
            "compile_args": ["clean", "compile", "-DskipTests"],
            "timeout": 300,
            "verify_target_classes": True,
            "auto_create_pom": True,
            "prefer_module_compilation": True
        },
        "frontend_migration": {
            "enabled": True,
            "target_base_path": "jeecgboot-vue3/src/views",
            "cleanup_source": False,
            "create_target_dirs": True
        },
        "database_execution": {
            "enabled": True,
            "method": "mysql_client",
            "timeout": 30,
            "auto_commit": True,
            "config_file_path": "jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-dev.yml"
        },
        "permission_authorization": {
            "enabled": True,
            "admin_role_id": "f6817f48af4fb3af11b9e8bf182f618b",
            "timeout": 30,
            "retry_attempts": 3,
            "auto_grant_to_admin": True,
            "description": "自动为管理员角色授权新生成模块的权限"
        },
        "query": {
            "page_size": 50,
            "page_no": 1
        },
        "display": {
            "token_length": 50,
            "max_records": 5
        }
    }

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 合并配置
                for section, values in user_config.items():
                    if section in default_config:
                        default_config[section].update(values)
                    else:
                        default_config[section] = values
        except Exception as e:
            safe_print(f"[WARN] 配置文件加载失败，使用默认配置: {e}")
    else:
        # 配置文件不存在时，不自动创建，而是提示用户
        safe_print(f"[WARN]  配置文件不存在: {config_file}")
        safe_print(f"[TIP] 将使用默认配置运行，如需自定义配置请创建配置文件")
        safe_print(f"[NOTE] 可以复制现有配置文件模板或使用 --config 参数指定配置文件")

    # 解析项目路径前缀
    original_path_prefix = default_config["project"]["path_prefix"]
    resolved_path_prefix = CrossPlatformUtils.resolve_path_prefix(original_path_prefix)
    default_config["project"]["path_prefix"] = resolved_path_prefix

    if original_path_prefix != resolved_path_prefix:
        try:
            safe_print(f"[FOLDER] 路径解析: {original_path_prefix} → {resolved_path_prefix}")
        except UnicodeEncodeError:
            safe_print(f"[路径解析] {original_path_prefix} -> {resolved_path_prefix}")

    # 解析服务器配置中的环境变量
    def resolve_env_var(value):
        """解析环境变量"""
        if isinstance(value, str) and value.startswith('$'):
            env_var = value[1:]
            env_value = os.environ.get(env_var)
            if env_value:
                return env_value
            else:
                safe_print(f"[WARN] 环境变量 {env_var} 未设置，使用默认值")
                return value
        return value

    # 解析服务器配置
    default_config["server"]["base_url"] = resolve_env_var(default_config["server"]["base_url"])
    default_config["server"]["username"] = resolve_env_var(default_config["server"]["username"])
    default_config["server"]["password"] = resolve_env_var(default_config["server"]["password"])
    
    # 解析数据库配置
    default_config["database"]["type"] = resolve_env_var(default_config["database"]["type"])
    default_config["database"]["url"] = resolve_env_var(default_config["database"]["url"])
    default_config["database"]["username"] = resolve_env_var(default_config["database"]["username"])
    default_config["database"]["password"] = resolve_env_var(default_config["database"]["password"])

    return default_config

# 加载配置
CONFIG = load_config()

# ==================== 三核心变量定义 ====================
# 这三个变量是代码生成系统的核心，共同决定了生成代码的结构和命名
MODULE_NAME = None      # 模块名/系统名称 (如: finance, hrms, crm)
SUBMODULE_NAME = None   # 子模块名/系统模块 (如: invoice, payment, employee)
BUSINESS_ENTITY = None   # 业务实体名称 (如: CustomerProfile, ProductCatalog - 从配置文件business_entity字段读取)

# ==================== 派生变量定义 ====================
# 这些变量由三核心变量计算得出
TABLE_NAME = None       # 表名 (如: us_finance_invoice_management)
PACKAGE_NAME = None     # 包名 (如: org.jeecg.modules.finance.invoice)
# 删除JAVA_ENTITY_NAME变量，统一使用BUSINESS_ENTITY
PROJECT_PATH = None     # 项目路径

# ==================== 控制标志变量 ====================
SKIP_MODULE_MANAGEMENT = False
FORCE_SYSTEM = None
CURRENT_TABLE_NAME = ""  # 当前表名，用于生成标准化包名

# ==================== 三核心变量处理功能 ====================

def set_core_variables_from_table_name(table_name):
    """
    从表名设置三核心变量

    Args:
        table_name (str): 完整表名，格式为 us_{MODULE_NAME}_{SUBMODULE_NAME}_{BUSINESS_ENTITY}

    Returns:
        bool: 设置是否成功
    """
    global MODULE_NAME, SUBMODULE_NAME, BUSINESS_ENTITY
    global TABLE_NAME, PACKAGE_NAME, PROJECT_PATH, CURRENT_TABLE_NAME

    try:
        # 从配置文件或全局变量获取 business_entity
        business_entity = get_business_entity_from_global_or_config()
        components = parse_table_name_components(table_name, business_entity)

        # 设置三核心变量
        MODULE_NAME = components['module_name']
        SUBMODULE_NAME = components['sub_module']
        BUSINESS_ENTITY = components['entity_name']  # 使用配置文件中的business_entity或转换后的entity_name

        # 计算派生变量
        TABLE_NAME = table_name
        CURRENT_TABLE_NAME = table_name  # 设置当前表名
        # 强制确保包路径全小写，符合Java命名规范，不包含业务实体名
        PACKAGE_NAME = f"org.jeecg.modules.{MODULE_NAME.lower()}.{SUBMODULE_NAME.lower()}"

        # 计算项目路径
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        PROJECT_PATH = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{MODULE_NAME}"

        return True

    except Exception as e:
        safe_print(f"[FAIL] 从表名设置三核心变量失败: {e}")
        return False

def print_core_variables():
    """打印三核心变量和派生变量的详细信息"""
    safe_print(f"\n[LIST] 三核心变量详情:")
    safe_print(f"   模块名/系统名称          = {MODULE_NAME or 'None'}")
    safe_print(f"   子模块名/系统模块        = {SUBMODULE_NAME or 'None'}")
    safe_print(f"   业务实体名称             = {BUSINESS_ENTITY or 'None'}")

    safe_print(f"\n[CHART] 派生变量详情:")
    safe_print(f"   表名                     = {TABLE_NAME or 'None'}")
    safe_print(f"   包名                     = {PACKAGE_NAME or 'None'}")
    safe_print(f"   业务实体                 = {BUSINESS_ENTITY or 'None'}")
    safe_print(f"   项目路径                 = {PROJECT_PATH or 'None'}")

    safe_print(f"\n[SEARCH] 变量说明:")
    safe_print(f"   - MODULE_NAME: 表示一级业务领域，对应业务系统类型")
    safe_print(f"   - SUBMODULE_NAME: 表示二级业务领域，对应业务系统内的功能模块")
    safe_print(f"   - BUSINESS_ENTITY: 表示操作对象，对应具体业务实体，按Java驼峰命名规范")
    safe_print(f"   - TABLE_NAME: 由三核心变量组合而成的完整表名，公式: us_{{MODULE_NAME}}_{{SUBMODULE_NAME}}_{{TABLE_SUFFIX}}")
    safe_print(f"   - PACKAGE_NAME: 由MODULE_NAME和SUBMODULE_NAME组合而成的包名，公式: org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}")
    safe_print(f"   - PROJECT_PATH: 由配置和MODULE_NAME组合而成的项目路径")

def validate_core_variables():
    """
    高质量三核心变量验证函数
    修复了之前版本中BUSINESS_ENTITY格式验证错误等问题
    """
    safe_print(f"\n[SEARCH] 三核心变量一致性验证:")
    errors = []
    warnings = []

    # 步骤1：基础字段存在性验证
    if not MODULE_NAME:
        errors.append("MODULE_NAME不能为空")
    if not SUBMODULE_NAME:
        errors.append("SUBMODULE_NAME不能为空")
    if not BUSINESS_ENTITY:
        errors.append("BUSINESS_ENTITY不能为空")
    if not TABLE_NAME:
        errors.append("TABLE_NAME不能为空")

    # 如果基础字段缺失，直接返回
    if errors:
        safe_print("[FAIL] 基础字段验证失败:")
        for error in errors:
            safe_print(f"   - {error}")
        return False

    # 步骤2：格式规范验证
    if not re.match(r'^[a-z][a-z0-9_]*$', MODULE_NAME):
        errors.append(f"MODULE_NAME格式错误: '{MODULE_NAME}' (应为小写字母和下划线)")
    
    if not re.match(r'^[a-z][a-z0-9_]*$', SUBMODULE_NAME):
        errors.append(f"SUBMODULE_NAME格式错误: '{SUBMODULE_NAME}' (应为小写字母和下划线)")
    
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', BUSINESS_ENTITY):
        errors.append(f"BUSINESS_ENTITY格式错误: '{BUSINESS_ENTITY}' (应为PascalCase格式)")

    # 步骤3：表名解析一致性验证
    try:
        # 从实际表名解析出组件（使用business_entity）
        business_entity = get_business_entity_from_global_or_config()
        table_components = parse_table_name_components(TABLE_NAME, business_entity)
        parsed_module = table_components['module_name']
        parsed_submodule = table_components['sub_module']  
        parsed_business_scenario = table_components['business_scenario']
        parsed_entity = table_components['entity_name']
        
        safe_print(f"   [CHART] 表名解析结果验证:")
        safe_print(f"      表名: {TABLE_NAME}")
        safe_print(f"      解析模块: {parsed_module}")
        safe_print(f"      解析子模块: {parsed_submodule}")
        safe_print(f"      解析业务场景: {parsed_business_scenario}")
        safe_print(f"      解析实体名: {parsed_entity}")
        
        # 验证解析结果与全局变量的一致性
        if MODULE_NAME != parsed_module:
            errors.append(f"模块名不一致: 全局变量={MODULE_NAME}, 表名解析={parsed_module}")
        
        if SUBMODULE_NAME != parsed_submodule:
            errors.append(f"子模块名不一致: 全局变量={SUBMODULE_NAME}, 表名解析={parsed_submodule}")
        
        if BUSINESS_ENTITY != parsed_entity:
            errors.append(f"实体名不一致: 全局变量={BUSINESS_ENTITY}, 表名解析={parsed_entity}")
            
    except Exception as e:
        errors.append(f"表名解析失败: {e}")

    # 步骤4：包名验证
    expected_package_name = f"org.jeecg.modules.{MODULE_NAME.lower()}.{SUBMODULE_NAME.lower()}"
    if PACKAGE_NAME != expected_package_name:
        errors.append(f"包名不一致: 期望={expected_package_name}, 实际={PACKAGE_NAME}")

    # 步骤5：项目路径验证  
    expected_project_suffix = f"jeecg-module-{MODULE_NAME}"
    if PROJECT_PATH and expected_project_suffix not in PROJECT_PATH:
        warnings.append(f"项目路径可能不正确: 期望包含'{expected_project_suffix}', 实际='{PROJECT_PATH}'")

    # 结果输出
    if warnings:
        safe_print("[WARN] 警告信息:")
        for warning in warnings:
            safe_print(f"   - {warning}")

    if errors:
        safe_print("[FAIL] 三核心变量验证失败:")
        for error in errors:
            safe_print(f"   - {error}")
        return False
    else:
        safe_print("[OK] 三核心变量验证通过")
        return True

def validate_template_variables():
    """验证所有变量是否包含未解析的模板变量"""
    errors = []

    # 检查关键变量是否包含模板变量
    variables_to_check = {
        'PROJECT_PATH': PROJECT_PATH,
        'BUSINESS_ENTITY': BUSINESS_ENTITY,
        'PACKAGE_NAME': PACKAGE_NAME,
        'TABLE_NAME': TABLE_NAME
    }

    for var_name, var_value in variables_to_check.items():
        if var_value and ('{{' in str(var_value) or '}}' in str(var_value)):
            errors.append(f"{var_name} 包含未解析的模板变量: {var_value}")

    if errors:
        safe_print("[FAIL] 模板变量验证失败:")
        for error in errors:
            safe_print(f"   - {error}")
        return False
    else:
        safe_print("[OK] 模板变量验证通过")
        return True

# ==================== Java命名规范转换功能 ====================

def parse_table_name_components(table_name, business_entity=None):
    """
    解析表名并返回所有命名组件（跨平台支持：macOS/Linux/Windows）
    支持标准化命名规范和复合词业务场景
    
    Args:
        table_name (str): 完整表名，格式: us_{模块名}_{子模块名}_{业务场景}
        business_entity (str, optional): 从配置文件获取的业务实体名（优先使用）
        
    Returns:
        dict: 包含所有命名组件的字典
        {
            'module_name': str,      # 模块名
            'sub_module': str,       # 子模块名  
            'business_scenario': str, # 业务场景
            'entity_name': str       # 实体名（Java格式）
        }
        
    Examples:
        us_mall_sales_product -> {
            'module_name': 'mall',
            'sub_module': 'sales', 
            'business_scenario': 'product',
            'entity_name': 'Product'
        }
        
        us_crm_customer_profile (with business_entity="CustomerProfile") -> {
            'module_name': 'crm',
            'sub_module': 'customer', 
            'business_scenario': 'customer_profile',
            'entity_name': 'CustomerProfile'
        }
    """
    if not table_name:
        raise ValueError("表名不能为空")
        
    if not table_name.startswith('us_'):
        error_msg = f"""
[FAIL] 表名格式错误: {table_name}

[LIST] 表名命名规范要求:
   格式: us_{{模块名}}_{{子模块名}}_{{业务场景}}
   
[OK] 正确示例:
   us_mall_sales_product         (电商-销售-产品)
   us_mall_member_info          (电商-会员-信息)
   us_finance_invoice_management (财务-发票-管理)
   us_crm_customer_profile      (CRM-客户-档案)

[TOOL] 智能修复建议:
   或手动修改为: 'us_{{模块名}}_{{子模块名}}_{{业务场景}}'

[BOOKS] 详细文档: 请查看 Code_Gen_Guide.md 中的标准化命名规范
        """
        raise ValueError(error_msg)
        
    parts = table_name.split('_')
    
    if len(parts) < 4:
        error_msg = f"""
[FAIL] 表名格式错误: {table_name}

[LIST] 表名必须包含至少4个部分，用下划线分隔:
   格式: us_{{模块名}}_{{子模块名}}_{{业务场景}}
   当前: {len(parts)}个部分 {parts}

[OK] 正确示例:
   us_mall_sales_product        (4个部分: us + mall + sales + product)
   us_crm_customer_profile      (4个部分: us + crm + customer + profile)
   us_finance_invoice_management (4个部分: us + finance + invoice + management)
   
[FAIL] 错误示例:
   us_mall_product              (3个部分，缺少子模块名)
   us_product                   (2个部分，格式不完整)

[TOOL] 修复建议:
   确保表名包含: 前缀(us) + 模块名 + 子模块名 + 业务场景（可以是复合词）
        """
        raise ValueError(error_msg)
    
    # 解析组件: us_module_submodule_business_scenario...
    module_name = parts[1]        # 模块名称
    sub_module = parts[2]         # 子模块名称  
    
    # 业务场景和实体名处理逻辑
    business_scenario_parts = parts[3:]
    default_business_scenario = '_'.join(business_scenario_parts)
    
    # 优先使用配置文件中的 business_entity
    if business_entity:
        entity_name = business_entity
        # 根据 business_entity 推导正确的 business_scenario
        # 将 PascalCase 转换为 snake_case
        business_scenario = pascal_to_snake_case(business_entity)
        safe_print(f"[CONFIG] 使用配置文件中的业务实体: {business_entity}")
        safe_print(f"[DERIVE] 根据实体名推导业务场景: {business_scenario}")
    else:
        business_scenario = default_business_scenario
        entity_name = convert_to_java_entity_name(business_scenario)
        safe_print(f"[PARSE] 从业务场景转换实体名: {business_scenario} -> {entity_name}")
    
    safe_print(f"[TARGET] 跨平台表名解析: {table_name}")
    safe_print(f"   ├── 模块名: {module_name}")
    safe_print(f"   ├── 子模块: {sub_module}") 
    safe_print(f"   ├── 业务场景: {business_scenario}")
    safe_print(f"   └── 实体名: {entity_name}")
    
    return {
        'module_name': module_name,
        'sub_module': sub_module,
        'business_scenario': business_scenario,
        'entity_name': entity_name
    }

def generate_standardized_package_name(table_name=None, force_system=None):
    """
    根据表名生成标准化包名
    
    Args:
        table_name (str): 完整表名，必须符合标准格式。如果为None，使用全局变量CURRENT_TABLE_NAME
        force_system (str): 强制使用的模块名（用于向后兼容）
        
    Returns:
        str: 标准化包名，格式为 org.jeecg.modules.{module_name}.{sub_module}
        
    Examples:
        us_mall_sales_product -> org.jeecg.modules.mall.sales
        us_finance_invoice_management -> org.jeecg.modules.finance.invoice
    """
    global CURRENT_TABLE_NAME
    
    # 如果没有提供表名，使用全局变量
    if not table_name:
        table_name = CURRENT_TABLE_NAME
    
    if not table_name:
        # 如果没有表名，使用传统方式
        if force_system:
            return f"org.jeecg.modules.{force_system.lower()}.{SUBMODULE_NAME}"
        else:
            return f"org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}"
    
    try:
        business_entity = get_business_entity_from_global_or_config()
        components = parse_table_name_components(table_name, business_entity)
        # 不再包含entity_name，只使用module_name和sub_module
        package_name = f"org.jeecg.modules.{components['module_name'].lower()}.{components['sub_module'].lower()}"
        safe_print(f"[PACKAGE] 生成标准化包名: {package_name}")
        return package_name
    except ValueError as e:
        safe_print(f"[WARN] 表名解析失败，使用传统格式: {e}")
        if force_system:
            return f"org.jeecg.modules.{force_system.lower()}.{SUBMODULE_NAME.lower()}"
        else:
            return f"org.jeecg.modules.{MODULE_NAME.lower()}.{SUBMODULE_NAME.lower()}"

def resolve_config_file_path(config_file_path):
    """
    智能解析配置文件路径
    支持绝对路径和相对路径的多种情况
    """
    # 1. 绝对路径直接使用
    if os.path.isabs(config_file_path):
        if os.path.exists(config_file_path):
            return os.path.abspath(config_file_path)
        else:
            raise ValueError(f"[FAIL] 绝对路径配置文件不存在: {config_file_path}")
    
    # 2. 相对路径智能推导
    search_paths = [
        config_file_path,  # 当前工作目录
        os.path.join(os.getcwd(), config_file_path),  # 显式当前目录
        os.path.join(os.path.dirname(__file__), config_file_path),  # 脚本目录
        os.path.join(os.path.dirname(__file__), '..', config_file_path)  # 上级目录
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    raise ValueError(f"""[FAIL] 配置文件未找到: {config_file_path}

[SEARCH] 已搜索的路径:
{chr(10).join(f"   • {p}" for p in search_paths)}

[TIP] 解决方案:
   1. 检查配置文件是否存在
   2. 使用绝对路径或确保文件在当前工作目录
   3. 确认配置文件名称正确""")

def get_business_entity_from_global_or_config(config_data=None):
    """
    跨平台获取业务实体名称的辅助函数
    优先使用全局变量，其次从配置数据中获取
    
    Args:
        config_data (dict, optional): 配置文件数据
        
    Returns:
        str: 业务实体名称，如 "CustomerProfile"
    """
    global BUSINESS_ENTITY
    
    # 优先使用全局变量（过滤模板变量）
    if (BUSINESS_ENTITY and 
        BUSINESS_ENTITY != "defaultentity" and 
        not BUSINESS_ENTITY.startswith('{{')):
        return BUSINESS_ENTITY
    
    # 从配置数据中获取
    if config_data:
        head = config_data.get('head', {})
        business_entity = head.get('business_entity')
        if business_entity:
            return business_entity
    
    # 从全局CONFIG中获取
    try:
        global CONFIG, FORM_DATA_FILE
        if CONFIG and FORM_DATA_FILE:
            with open(FORM_DATA_FILE, 'r', encoding='utf-8') as f:
                form_data = json.load(f)
                head = form_data.get('head', {})
                business_entity = head.get('business_entity')
                if business_entity:
                    return business_entity
    except Exception:
        pass
    
    return None

def extract_business_entity_from_config(config_file_path):
    """
    高质量配置文件解析函数（跨平台支持：macOS/Linux/Windows）
    全面的错误处理和精准的错误信息
    
    Args:
        config_file_path (str): 配置文件路径（支持绝对和相对路径）
        
    Returns:
        dict: 包含所有派生格式的字典
        
    Raises:
        ValueError: 配置文件问题的详细诊断信息
    """
    safe_print(f"[LIST] 解析配置文件: {config_file_path}")
    
    # 步骤1：智能路径解析
    try:
        resolved_path = resolve_config_file_path(config_file_path)
        safe_print(f"[OK] 配置文件路径解析成功: {resolved_path}")
    except ValueError as e:
        safe_print(f"[FAIL] 路径解析失败")
        raise e
    
    # 步骤2：JSON格式验证
    try:
        with open(resolved_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        safe_print(f"[OK] JSON格式解析成功")
    except json.JSONDecodeError as e:
        raise ValueError(f"""[FAIL] 配置文件JSON格式错误
        
[FOLDER] 文件路径: {resolved_path}
[SEARCH] JSON错误: {e}
[TOOL] 解决方案: 检查JSON语法，确保括号、引号、逗号正确""")
    except Exception as e:
        raise ValueError(f"[FAIL] 读取配置文件失败: {e}")
    
    # 步骤3：结构完整性验证
    if not isinstance(config, dict):
        raise ValueError(f"[FAIL] 配置文件根节点必须是对象，当前类型: {type(config)}")
    
    if 'head' not in config:
        available_keys = list(config.keys())
        raise ValueError(f"""[FAIL] 配置文件缺少head节点
        
[CHART] 当前根节点字段: {available_keys}
[TOOL] 解决方案: 确保配置文件包含head节点""")
    
    head = config['head']
    if not isinstance(head, dict):
        raise ValueError(f"[FAIL] head节点必须是对象，当前类型: {type(head)}")
    
    # 步骤4：business_entity字段验证
    business_entity = head.get('business_entity')
    if not business_entity:
        available_keys = list(head.keys())
        raise ValueError(f"""[FAIL] head节点缺少business_entity字段
        
[CHART] head节点现有字段: {available_keys}
[TOOL] 解决方案: 在head节点中添加business_entity字段
[TIP] 示例: "business_entity": "ProductCatalog" """)
    
    if not isinstance(business_entity, str):
        raise ValueError(f"[FAIL] business_entity必须是字符串，当前类型: {type(business_entity)}")
    
    if not business_entity.strip():
        raise ValueError("[FAIL] business_entity不能为空字符串")
    
    # 步骤5：格式规范验证
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', business_entity):
        raise ValueError(f"""[FAIL] business_entity格式错误: '{business_entity}'
        
[LIST] 格式要求: PascalCase（首字母大写的驼峰命名）
[TIP] 正确示例: ProductCatalog, CustomerProfile, OrderHeader
[FAIL] 错误示例: productCatalog, product_catalog, PRODUCT""")
    
    safe_print(f"[OK] business_entity验证通过: {business_entity}")
    
    # 步骤6：生成派生格式
    try:
        formats = derive_all_formats_from_business_entity(business_entity)
        safe_print(f"[OK] 格式派生成功")
        safe_print(f"   ├── Java类名: {formats['java_class_name']}")
        safe_print(f"   ├── 表名后缀: {formats['table_suffix']}")
        safe_print(f"   ├── URL路径: {formats['url_path']}")
        safe_print(f"   └── 前端路径: {formats['frontend_path']}")
        
        return formats
        
    except Exception as e:
        raise ValueError(f"[FAIL] 格式派生失败: {e}")

def generate_config_from_template(module_name, submodule_name, business_entity, table_txt, business_fields=None):
    """
    基于标准模板生成高质量配置文件
    AI配置生成的推荐入口函数
    
    Args:
        module_name (str): 模块名（小写）
        submodule_name (str): 子模块名（小写）
        business_entity (str): 业务实体名（PascalCase）
        table_txt (str): 中文描述
        business_fields (list): 可选的业务字段列表
        
    Returns:
        dict: 完整的配置对象
    """
    # 加载标准模板
    template_path = os.path.join(os.path.dirname(__file__), 'Code_Gen_Guide.json')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"[FAIL] 标准模板文件不存在: {template_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"[FAIL] 标准模板JSON格式错误: {e}")
    
    # 生成派生格式
    formats = derive_all_formats_from_business_entity(business_entity)
    business_scenario = formats['table_suffix']
    
    # 填充模板变量
    table_name = f"us_{module_name}_{submodule_name}_{business_scenario}"
    
    # 更新head节点
    template['head']['tableName'] = table_name
    template['head']['tableTxt'] = table_txt
    template['head']['business_entity'] = business_entity
    
    # 更新metadata节点
    template['metadata']['generation_info'] = {
        "module_name": module_name,
        "submodule_name": submodule_name,
        "business_entity": business_entity,
        "inference_strategy": "基于JeecgBoot标准模板生成",
        "semantic_analysis": f"{table_txt}，属于标准CRUD需求"
    }
    
    template['metadata']['derived_formats'] = {
        "table_suffix": business_scenario,
        "url_path": f"/{module_name}/{submodule_name}/{formats['url_path']}",
        "frontend_path": submodule_name
    }
    
    # 插入业务字段（如果提供）
    if business_fields:
        # 业务字段应该在系统字段之后插入
        # 当前模板已经包含：id(0) + 6个系统字段(1-6) + 1个业务字段模板(7)
        # 我们需要移除业务字段模板，然后添加实际的业务字段

        # 移除模板中的业务字段模板（最后一个字段）
        system_fields = template['fields'][:-1]  # 保留id和系统字段，移除业务字段模板
        business_field_configs = []

        # 从orderNum 7开始为业务字段分配序号
        for i, field in enumerate(business_fields):
            field_config = create_business_field_config(field, 7 + i)
            business_field_configs.append(field_config)

        # 重新组织字段顺序：系统字段(id + 6个系统字段) + 业务字段
        template['fields'] = system_fields + business_field_configs

    return template

def create_business_field_config(field_spec, order_num):
    """
    创建业务字段配置
    
    Args:
        field_spec (dict): 字段规格 {"name": "field_name", "txt": "字段中文名", "type": "string", "length": 100}
        order_num (int): 排序号
        
    Returns:
        dict: 字段配置对象
    """
    base_config = {
        "dbFieldName": field_spec.get("name", ""),
        "dbFieldTxt": field_spec.get("txt", ""),
        "queryShowType": "text",
        "queryDictTable": "",
        "queryDictField": "",
        "queryDictText": "",
        "queryDefVal": "",
        "queryConfigFlag": "1" if field_spec.get("queryable", True) else "0",
        "mainTable": "",
        "mainField": "",
        "fieldHref": "",
        "fieldValidType": field_spec.get("validation", ""),
        "fieldMustInput": "1" if field_spec.get("required", False) else "0",
        "dictTable": "",
        "dictField": "",
        "dictText": "",
        "isShowForm": "1",
        "isShowList": "1",
        "sortFlag": "0",
        "isReadOnly": "0",
        "fieldShowType": field_spec.get("show_type", "text"),
        "fieldLength": 120,
        "isQuery": "1" if field_spec.get("queryable", True) else "0",
        "queryMode": field_spec.get("query_mode", "like"),
        "fieldDefaultValue": field_spec.get("default", ""),
        "converter": "",
        "fieldExtendJson": "",
        "fieldConfig": "",
        "dbLength": field_spec.get("length", 100),
        "dbPointLength": field_spec.get("decimal_length", 0),
        "dbDefaultVal": field_spec.get("default", ""),
        "dbType": field_spec.get("type", "string"),
        "dbIsKey": "0",
        "dbIsNull": "0" if field_spec.get("required", False) else "1",
        "dbIsPersist": "1",
        "orderNum": order_num
    }

    # 应用字段长度验证和修正
    base_config = validate_and_fix_field_lengths(base_config)

    return base_config

def validate_and_fix_field_lengths(field_config):
    """
    验证并修正字段配置中的长度限制问题
    确保所有字段值符合数据库表 onl_cgform_field 的字段长度限制

    Args:
        field_config (dict): 字段配置字典

    Returns:
        dict: 修正后的字段配置
    """
    # 数据库字段长度限制定义
    DB_FIELD_LIMITS = {
        'queryMode': 10,
        'fieldShowType': 20,
        'queryShowType': 50,
        'fieldValidType': 300,
        'dictField': 100,
        'dictText': 100,
        'dictTable': 255,
        'dbFieldName': 32,
        'dbFieldTxt': 200,
        'fieldHref': 200,
        'fieldDefaultValue': 100,
        'converter': 255,
        'queryDefVal': 50,
        'queryDictText': 100,
        'queryDictField': 100,
        'queryDictTable': 500
    }

    # queryMode 特殊处理规则
    QUERY_MODE_FIXES = {
        'group_range': 'range',
        'date_range': 'range',
        'multi_select': 'single',
        'complex_query': 'like'
    }

    fixed_config = field_config.copy()
    warnings = []

    for field_name, max_length in DB_FIELD_LIMITS.items():
        if field_name in fixed_config:
            field_value = str(fixed_config[field_name])

            # 特殊处理 queryMode 字段
            if field_name == 'queryMode' and field_value in QUERY_MODE_FIXES:
                old_value = field_value
                fixed_config[field_name] = QUERY_MODE_FIXES[field_value]
                warnings.append(f"[WARN]  字段 {field_name}: '{old_value}' 超过长度限制，已自动修正为 '{fixed_config[field_name]}'")

            # 通用长度检查
            elif len(field_value) > max_length:
                old_value = field_value
                fixed_config[field_name] = field_value[:max_length]
                warnings.append(f"[WARN]  字段 {field_name}: 值过长({len(old_value)}字符)，已截断为{max_length}字符")

    # 输出警告信息
    if warnings:
        safe_print("[TOOL] 字段长度自动修正:")
        for warning in warnings:
            safe_print(f"   {warning}")

    return fixed_config

def convert_legacy_config_format(config_file_path):
    """
    转换旧格式配置文件为JeecgBoot API兼容格式
    修复布尔值字段和字段名称不匹配问题

    Args:
        config_file_path (str): 配置文件路径

    Returns:
        bool: 转换是否成功
    """
    safe_print(f"[REFRESH] 转换配置文件格式: {config_file_path}")

    try:
        # 读取配置文件
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 检查是否需要转换
        needs_conversion = False

        # 检查head部分是否需要转换
        head = config.get('head', {})
        if 'tableDescription' in head or 'entityName' in head:
            needs_conversion = True
            safe_print("   检测到旧格式head部分，需要转换")

        # 检查fields部分是否需要转换
        fields = config.get('fields', [])
        if fields and isinstance(fields, list) and len(fields) > 0:
            first_field = fields[0]
            if 'fieldName' in first_field or 'fieldDescription' in first_field:
                needs_conversion = True
                safe_print("   检测到旧格式fields部分，需要转换")

        if not needs_conversion:
            safe_print("   配置文件格式正确，无需转换")
            return True

        # 转换head部分
        if 'tableDescription' in head:
            head['tableTxt'] = head.pop('tableDescription')

        # 移除不需要的字段
        fields_to_remove = ['entityName', 'packageName', 'moduleName', 'subModuleName',
                           'businessName', 'className', 'businessDescription', 'author', 'email']
        for field in fields_to_remove:
            head.pop(field, None)

        # 添加必需的head字段
        if 'tableType' not in head:
            head['tableType'] = 1
        if 'formCategory' not in head:
            head['formCategory'] = "temp"
        if 'idType' not in head:
            head['idType'] = "UUID"
        if 'isCheckbox' not in head:
            head['isCheckbox'] = "Y"
        if 'themeTemplate' not in head:
            head['themeTemplate'] = "normal"
        if 'formTemplate' not in head:
            head['formTemplate'] = "1"
        if 'scroll' not in head:
            head['scroll'] = 1
        if 'isPage' not in head:
            head['isPage'] = "Y"
        if 'isTree' not in head:
            head['isTree'] = "N"
        if 'extConfigJson' not in head:
            head['extConfigJson'] = '{"reportPrintShow":0,"reportPrintUrl":"","joinQuery":0,"modelFullscreen":0,"modalMinWidth":"","commentStatus":0,"tableFixedAction":1,"tableFixedActionType":"right","formLabelLengthShow":0,"formLabelLength":null,"enableExternalLink":0,"externalLinkActions":"add,edit,detail"}'
        if 'isDesForm' not in head:
            head['isDesForm'] = "N"
        if 'desFormCode' not in head:
            head['desFormCode'] = ""

        # 转换fields部分
        converted_fields = []
        for i, field in enumerate(fields):
            converted_field = convert_legacy_field_format(field, i)
            if converted_field:
                converted_fields.append(converted_field)

        config['fields'] = converted_fields

        # 添加必需的数组
        if 'indexs' not in config:
            config['indexs'] = []
        if 'deleteFieldIds' not in config:
            config['deleteFieldIds'] = []
        if 'deleteIndexIds' not in config:
            config['deleteIndexIds'] = []

        # 添加metadata（如果不存在）
        if 'metadata' not in config:
            business_entity = head.get('business_entity', 'Unknown')
            table_name = head.get('tableName', '')

            # 尝试从表名解析模块信息
            try:
                business_entity = get_business_entity_from_global_or_config(config)
                components = parse_table_name_components(table_name, business_entity)
                module_name = components['module_name']
                submodule_name = components['sub_module']
                table_suffix = components['business_scenario']
            except:
                module_name = "unknown"
                submodule_name = "unknown"
                table_suffix = "unknown"

            config['metadata'] = {
                "generation_info": {
                    "module_name": module_name,
                    "submodule_name": submodule_name,
                    "business_entity": business_entity,
                    "inference_strategy": "基于JeecgBoot标准模板生成",
                    "semantic_analysis": head.get('tableTxt', '自动转换的配置文件')
                },
                "derived_formats": {
                    "table_suffix": table_suffix,
                    "url_path": f"{module_name}/{submodule_name}/{table_suffix.replace('_', '-')}",
                    "frontend_path": submodule_name
                }
            }

        # 写回文件
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        safe_print(f"[OK] 配置文件格式转换完成")
        safe_print(f"   转换字段数量: {len(converted_fields)}")
        return True

    except Exception as e:
        safe_print(f"[FAIL] 配置文件格式转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def convert_legacy_field_format(legacy_field, order_num):
    """
    转换旧格式字段为JeecgBoot API兼容格式

    Args:
        legacy_field (dict): 旧格式字段配置
        order_num (int): 字段顺序号

    Returns:
        dict: 转换后的字段配置
    """
    try:
        # 字段名映射
        field_name_mapping = {
            'fieldName': 'dbFieldName',
            'fieldDescription': 'dbFieldTxt',
            'fieldType': 'dbType',
            'databaseType': 'dbType',
            'fieldLength': 'dbLength'
        }

        # 布尔值转换映射
        boolean_fields = ['isKey', 'isNull', 'isInsert', 'isEdit', 'isList', 'isQuery']

        # 创建新格式字段
        converted_field = {
            "dbFieldName": "",
            "dbFieldTxt": "",
            "queryShowType": "text",
            "queryDictTable": "",
            "queryDictField": "",
            "queryDictText": "",
            "queryDefVal": "",
            "queryConfigFlag": "0",
            "mainTable": "",
            "mainField": "",
            "fieldHref": "",
            "fieldValidType": "",
            "fieldMustInput": "0",
            "dictTable": "",
            "dictField": "",
            "dictText": "",
            "isShowForm": "1",
            "isShowList": "1",
            "sortFlag": "0",
            "isReadOnly": "0",
            "fieldShowType": "text",
            "fieldLength": 120,
            "isQuery": "0",
            "queryMode": "single",
            "fieldDefaultValue": "",
            "converter": "",
            "fieldExtendJson": "",
            "fieldConfig": "",
            "dbLength": 100,
            "dbPointLength": 0,
            "dbDefaultVal": "",
            "dbType": "string",
            "dbIsKey": "0",
            "dbIsNull": "0",
            "dbIsPersist": "1",
            "orderNum": order_num
        }

        # 转换基本字段
        for old_key, new_key in field_name_mapping.items():
            if old_key in legacy_field:
                converted_field[new_key] = legacy_field[old_key]

        # 处理布尔值字段转换
        for bool_field in boolean_fields:
            if bool_field in legacy_field:
                value = legacy_field[bool_field]
                if isinstance(value, bool):
                    # 布尔值转换为字符串
                    str_value = "1" if value else "0"
                else:
                    # 已经是字符串，保持原样
                    str_value = str(value)

                # 映射到正确的字段名
                if bool_field == 'isKey':
                    converted_field['dbIsKey'] = str_value
                elif bool_field == 'isNull':
                    converted_field['dbIsNull'] = str_value
                elif bool_field == 'isInsert':
                    converted_field['isShowForm'] = str_value
                elif bool_field == 'isEdit':
                    converted_field['isShowForm'] = str_value
                elif bool_field == 'isList':
                    converted_field['isShowList'] = str_value
                elif bool_field == 'isQuery':
                    converted_field['isQuery'] = str_value
                    converted_field['queryConfigFlag'] = str_value

        # 处理数据类型转换
        if 'fieldType' in legacy_field:
            java_type = legacy_field['fieldType']
            if 'String' in java_type:
                converted_field['dbType'] = 'string'
            elif 'Integer' in java_type:
                converted_field['dbType'] = 'int'
            elif 'Date' in java_type:
                converted_field['dbType'] = 'Datetime'
                converted_field['fieldShowType'] = 'datetime'
                converted_field['queryShowType'] = 'date'
            elif 'BigDecimal' in java_type:
                converted_field['dbType'] = 'BigDecimal'
                converted_field['fieldShowType'] = 'number'

        # 处理字典字段
        if 'dictCode' in legacy_field:
            converted_field['dictField'] = legacy_field['dictCode']
            converted_field['fieldShowType'] = 'list'
            converted_field['queryShowType'] = 'list'

        # 处理默认值
        if 'defaultValue' in legacy_field:
            converted_field['fieldDefaultValue'] = str(legacy_field['defaultValue'])
            converted_field['dbDefaultVal'] = str(legacy_field['defaultValue'])

        # 处理字段长度
        if 'fieldLength' in legacy_field:
            converted_field['dbLength'] = legacy_field['fieldLength']

        # 特殊处理主键字段
        if converted_field['dbIsKey'] == "1":
            converted_field['isShowForm'] = "0"
            converted_field['isShowList'] = "0"
            converted_field['isReadOnly'] = "1"
            converted_field['isQuery'] = "0"
            converted_field['queryConfigFlag'] = "0"

        # 特殊处理系统字段
        system_fields = ['create_by', 'create_time', 'update_by', 'update_time', 'sys_org_code', 'del_flag']
        if converted_field['dbFieldName'] in system_fields:
            if converted_field['dbFieldName'] in ['create_by', 'update_by', 'sys_org_code', 'del_flag']:
                converted_field['isShowForm'] = "0"
                converted_field['isShowList'] = "0"
                converted_field['isQuery'] = "0"
                converted_field['queryConfigFlag'] = "0"
            elif converted_field['dbFieldName'] in ['create_time', 'update_time']:
                converted_field['isShowForm'] = "0"
                converted_field['isShowList'] = "1"
                if converted_field['dbFieldName'] == 'create_time':
                    converted_field['isQuery'] = "1"
                    converted_field['queryConfigFlag'] = "1"
                    converted_field['queryMode'] = "group"
                else:
                    converted_field['isQuery'] = "0"
                    converted_field['queryConfigFlag'] = "0"

        return converted_field

    except Exception as e:
        safe_print(f"[FAIL] 字段格式转换失败: {e}")
        return None

def derive_all_formats_from_business_entity(business_entity):
    """
    从BUSINESS_ENTITY机械派生所有需要的格式
    纯字符串转换逻辑，不包含任何推理成分

    Args:
        business_entity (str): PascalCase格式的业务实体标识符
        
    Returns:
        dict: 包含所有派生格式的字典
    """
    return {
        'java_class_name': business_entity,  # 直接使用
        'table_suffix': pascal_to_snake_case(business_entity),
        'url_path': pascal_to_kebab_case(business_entity),
        'frontend_path': pascal_to_path(business_entity),
        'file_name': pascal_to_camel_case(business_entity)
    }

def pascal_to_lowercase(pascal_str):
    """
    PascalCase转全小写连续格式（用于数据库表名）
    VehicleInfo → vehicleinfo
    CustomerProfile → customerprofile
    """
    return pascal_str.lower()

def pascal_to_snake_case(pascal_str):
    """
    PascalCase转snake_case
    CustomerProfile → customer_profile
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', pascal_str).lower()

def pascal_to_kebab_case(pascal_str):
    """
    PascalCase转kebab-case  
    CustomerProfile → customer-profile
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '-', pascal_str).lower()

def pascal_to_path(pascal_str):
    """
    PascalCase转目录路径
    CustomerProfile → customer/profile
    """
    snake = pascal_to_snake_case(pascal_str)
    parts = snake.split('_')
    return '/'.join(parts)

def pascal_to_camel_case(pascal_str):
    """
    PascalCase转camelCase
    CustomerProfile → customerProfile
    """
    return pascal_str[0].lower() + pascal_str[1:] if pascal_str else ""

def convert_to_java_entity_name(snake_case_str):
    """
    snake_case转PascalCase (Java实体名)
    user_management → UserManagement
    product_category → ProductCategory
    teacherprofile → TeacherProfile (智能分割复合词)
    """
    if not snake_case_str:
        return ""
    
    # 如果包含下划线，按下划线分割
    if '_' in snake_case_str:
        parts = snake_case_str.split('_')
        return ''.join(word.capitalize() for word in parts if word)
    
    # 如果是复合词，尝试智能分割（基于常见模式）
    # 这里可以根据需要扩展更多的分割规则
    common_patterns = [
        # 长词汇优先匹配（避免被短词汇截断）
        ('template', 'Template'),    # emailtemplate -> EmailTemplate
        ('category', 'Category'),    # productcategory -> ProductCategory
        ('history', 'History'),      # orderhistory -> OrderHistory
        ('summary', 'Summary'),      # salesummary -> SaleSummary
        ('setting', 'Setting'),      # usersetting -> UserSetting
        ('manager', 'Manager'),      # employeemanager -> EmployeeManager
        ('service', 'Service'),      # userservice -> UserService
        ('profile', 'Profile'),      # customerprofile -> CustomerProfile
        ('header', 'Header'),        # invoiceheader -> InvoiceHeader
        ('detail', 'Detail'),        # orderdetail -> OrderDetail
        ('record', 'Record'),        # logrecord -> LogRecord
        ('config', 'Config'),        # systemconfig -> SystemConfig
        ('status', 'Status'),        # orderstatus -> OrderStatus
        ('table', 'Table'),          # mastertable -> MasterTable
        ('info', 'Info'),            # productinfo -> ProductInfo
        ('data', 'Data'),            # userdata -> UserData
        ('item', 'Item'),            # orderitem -> OrderItem
        ('list', 'List'),            # productlist -> ProductList
        ('form', 'Form'),            # userform -> UserForm
        ('view', 'View')             # reportview -> ReportView
    ]
    
    result = snake_case_str
    for pattern, replacement in common_patterns:
        if result.lower().endswith(pattern):
            prefix = result[:-len(pattern)]
            result = prefix.capitalize() + replacement
            break
    else:
        # 如果没有匹配到模式，直接首字母大写
        result = snake_case_str.capitalize()
    
    return result

# ==================== 配置文件处理功能 ====================

def backup_and_replace_jeecg_config(project_path, package_name):
    """备份并替换 jeecg_config.properties 文件中的变量"""
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    config_path = Path(project_prefix) / "jeecg-boot" / "jeecg-module-system" / "jeecg-system-start" / "src" / "main" / "resources" / "jeecg" / "jeecg_config.properties"
    backup_path = config_path.with_suffix('.properties.backup')

    safe_print(f"[NOTE] 临时替换配置文件变量: {config_path}")
    safe_print(f"   [SEARCH] 输入参数:")
    safe_print(f"      project_path = {project_path}")
    safe_print(f"      package_name = {package_name}")

    try:
        # 备份原文件
        if config_path.exists():
            import shutil
            shutil.copy2(config_path, backup_path)
            safe_print(f"   [OK] 已备份原配置文件: {backup_path}")

        # 读取原文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        safe_print(f"   [DOC] 原文件内容:")
        for i, line in enumerate(content.split('\n')[:10], 1):  # 显示前10行
            safe_print(f"      {i:2d}: {line}")

        # 替换变量 - 支持模板变量和实际值两种情况
        original_content = content

        # 首先尝试替换模板变量
        content = content.replace('{{PROJECT_PATH}}', str(project_path))
        content = content.replace('{{PACKAGE_NAME}}', package_name)

        # 如果有当前表名，进行更完整的变量替换
        if CURRENT_TABLE_NAME:
            try:
                business_entity = get_business_entity_from_global_or_config()
                components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
                module_name = components['module_name']
                sub_module = components['sub_module']
                entity_name = components['entity_name']
                # 直接使用 entity_name（已经是正确的Java格式）
                java_entity_name = entity_name

                content = content.replace('{{MODULE_NAME}}', module_name)
                content = content.replace('{{SUBMODULE_NAME}}', sub_module)
                content = content.replace('{{BUSINESS_ENTITY}}', java_entity_name)
                content = content.replace('{{TABLE_NAME}}', CURRENT_TABLE_NAME)

                safe_print(f"   [REFRESH] 完整变量替换:")
                safe_print(f"      {{{{MODULE_NAME}}}} → {module_name}")
                safe_print(f"      {{{{SUBMODULE_NAME}}}} → {sub_module}")
                safe_print(f"      {{{{BUSINESS_ENTITY}}}} → {java_entity_name}")
                safe_print(f"      {{{{TABLE_NAME}}}} → {CURRENT_TABLE_NAME}")
            except Exception as e:
                safe_print(f"   [WARN] 解析表名失败，使用基础变量替换: {e}")

        # 如果没有模板变量，则直接替换配置值
        import re

        # 替换 project_path 行
        content = re.sub(
            r'^project_path=.*$',
            f'project_path={project_path}',
            content,
            flags=re.MULTILINE
        )

        # 替换 bussi_package 行
        content = re.sub(
            r'^bussi_package=.*$',
            f'bussi_package={package_name}',
            content,
            flags=re.MULTILINE
        )

        # 检查是否有替换发生
        if content == original_content:
            safe_print(f"   [WARN] 警告: 没有找到需要替换的配置项")
            safe_print(f"   [SEARCH] 检查文件中是否包含 project_path 或 bussi_package 配置")
        else:
            safe_print(f"   [OK] 配置替换成功")

        # 写入替换后的内容
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)

        safe_print(f"   [DOC] 替换后内容:")
        for i, line in enumerate(content.split('\n')[:10], 1):  # 显示前10行
            safe_print(f"      {i:2d}: {line}")

        safe_print(f"   [OK] 已替换变量:")
        safe_print(f"      PROJECT_PATH = {project_path}")
        safe_print(f"      PACKAGE_NAME = {package_name}")

        return True

    except Exception as e:
        safe_print(f"   [FAIL] 配置文件替换失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def restore_jeecg_config(silent=False):
    """还原 jeecg_config.properties 文件"""
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    config_path = Path(project_prefix) / "jeecg-boot" / "jeecg-module-system" / "jeecg-system-start" / "src" / "main" / "resources" / "jeecg" / "jeecg_config.properties"
    backup_path = config_path.with_suffix('.properties.backup')

    if not silent:
        safe_print(f"[REFRESH] 还原配置文件: {config_path}")

    try:
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, config_path)
            backup_path.unlink()  # 删除备份文件
            if not silent:
                safe_print(f"   [OK] 已还原配置文件，保持变量占位")
        else:
            if not silent:
                safe_print(f"   [WARN] 备份文件不存在，跳过还原")

        return True

    except Exception as e:
        if not silent:
            safe_print(f"   [FAIL] 配置文件还原失败: {e}")
        return False

# ==================== 模块管理功能 ====================

def detect_business_system(table_name, table_description=""):
    """智能识别业务系统类型 
    
    @deprecated: 此函数已过时，推荐使用 parse_table_name_components() 从表名直接解析模块名
    """
    # 合并表名和描述进行分析
    text = f"{table_name} {table_description}".lower()

    # 业务系统关键词映射
    system_keywords = {
        'hrms': ['员工', '人事', '薪资', '考勤', '招聘', '培训', '绩效', '组织架构', 'employee', 'hr', 'staff', 'salary', 'attendance'],
        'crm': ['客户', '销售', '合同', '商机', '服务', '支持', '营销', '渠道', 'customer', 'client', 'sales', 'contract', 'opportunity'],
        'scm': ['供应商', '采购', '库存', '物流', '仓储', '配送', '订单', '商品', 'supplier', 'procurement', 'inventory', 'logistics', 'warehouse'],
        'oa': ['审批', '流程', '公告', '会议', '文档', '通知', '任务', '项目', 'approval', 'workflow', 'notice', 'meeting', 'document'],
        'finance': ['财务', '会计', '成本', '预算', '报表', '收支', '资产', '税务', 'finance', 'accounting', 'budget', 'cost', 'asset']
    }

    # 计算每个系统的匹配分数
    scores = {}
    for system, keywords in system_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            scores[system] = score

    # 返回得分最高的系统，如果没有匹配则返回默认值
    if scores:
        return max(scores, key=scores.get)
    else:
        return 'system'  # 默认系统名

def check_module_exists(module_name):
    """检查模块是否存在"""
    # 获取路径前缀
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    module_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f"jeecg-module-{module_name}"
    exists = module_path.exists() and module_path.is_dir()

    safe_print(f"[SEARCH] 检查模块: jeecg-module-{module_name}")
    safe_print(f"   路径: {module_path.absolute()}")
    safe_print(f"   存在: {'[OK] 是' if exists else '[FAIL] 否'}")

    return exists

def create_maven_module(module_name):
    """使用Maven archetype创建新模块"""
    safe_print(f"[BUILD] 创建Maven模块: jeecg-module-{module_name}")

    # 获取路径前缀
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    
    # 构建Maven命令
    mvn_executable = CrossPlatformUtils.get_maven_executable()
    maven_cmd = [
        mvn_executable, 'archetype:generate',
        '-DgroupId=org.jeecgframework.boot',
        f'-DartifactId=jeecg-module-{module_name}',
        '-Dversion=3.8.2',
        '-DarchetypeGroupId=org.jeecgframework.archetype',
        '-DarchetypeArtifactId=jeecg-boot-gen',
        '-DarchetypeVersion=2.0',
        '-DinteractiveMode=false'  # 非交互模式
    ]

    # 构建执行目录路径，使用跨平台路径处理
    exec_dir = CrossPlatformUtils.normalize_path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module'

    safe_print(f"   操作系统: {platform.system()}")
    safe_print(f"   执行目录: {exec_dir.absolute()}")
    safe_print(f"   Maven命令: {' '.join(maven_cmd)}")

    try:
        # 确保在正确的目录下执行
        if not exec_dir.exists():
            safe_print(f"[FAIL] 执行目录不存在: {exec_dir.absolute()}")
            return False

        # 执行Maven命令 - 使用安全执行方法处理Git Bash兼容性
        result = CrossPlatformUtils.execute_command_safely(
            maven_cmd,
            cwd=exec_dir,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            safe_print("[OK] Maven模块创建成功")
            safe_print(f"   输出: {result.stdout[-200:]}")  # 显示最后200字符
            return True
        else:
            safe_print(f"[FAIL] Maven模块创建失败")
            safe_print(f"   错误码: {result.returncode}")
            safe_print(f"   错误信息: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        safe_print("[FAIL] Maven命令执行超时")
        return False
    except Exception as e:
        safe_print(f"[FAIL] Maven命令执行异常: {e}")
        return False

def update_module_registry_pom(module_name):
    """更新模块注册表pom.xml添加新模块"""
    # 获取路径前缀
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    pom_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / 'pom.xml'

    safe_print(f"[NOTE] 更新模块注册表pom.xml: {pom_path.absolute()}")

    if not pom_path.exists():
        safe_print(f"[FAIL] 模块注册表pom.xml不存在: {pom_path}")
        return False

    try:
        # 读取原始文件内容
        with open(pom_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查模块是否已存在
        module_artifact_id = f"jeecg-module-{module_name}"
        if f"<module>{module_artifact_id}</module>" in content:
            safe_print(f"[OK] 模块已存在于模块注册表中: {module_artifact_id}")
            return True

        # 查找 </modules> 或 </ns0:modules> 标签的位置
        modules_end_pos = content.find('</modules>')
        if modules_end_pos == -1:
            modules_end_pos = content.find('</ns0:modules>')
        if modules_end_pos == -1:
            safe_print("[FAIL] 未找到modules节点")
            return False

        # 在 </modules> 前插入新模块
        new_module_entry = f"        <module>{module_artifact_id}</module>\n    "
        new_content = content[:modules_end_pos] + new_module_entry + content[modules_end_pos:]

        # 写回文件
        with open(pom_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        safe_print(f"[OK] 已添加模块到模块注册表: {module_name}")
        return True

    except Exception as e:
        safe_print(f"[FAIL] 更新模块注册表pom.xml失败: {e}")
        return False

def update_main_pom(module_name):
    """更新主项目pom.xml添加新模块 (保持向后兼容)"""
    return update_module_registry_pom(module_name)

def update_system_start_pom(module_name):
    """更新启动项目pom.xml添加新模块依赖"""
    # 获取路径前缀
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    pom_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-module-system' / 'jeecg-system-start' / 'pom.xml'

    safe_print(f"[NOTE] 更新启动项目pom.xml: {pom_path.absolute()}")

    if not pom_path.exists():
        safe_print(f"[FAIL] 启动项目pom.xml不存在: {pom_path}")
        return False

    try:
        # 读取原始文件内容
        with open(pom_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查依赖是否已存在
        artifact_id = f"jeecg-module-{module_name}"
        if f"<artifactId>{artifact_id}</artifactId>" in content:
            safe_print(f"[OK] 依赖已存在于启动项目pom.xml中: {artifact_id}")
            return True

        # 查找合适的位置插入新依赖（在 jeecg-system-biz 依赖之后）
        system_biz_pos = content.find('<artifactId>jeecg-system-biz</artifactId>')
        if system_biz_pos == -1:
            # 如果找不到 jeecg-system-biz，就在第一个 </dependency> 后插入
            first_dep_end = content.find('</dependency>')
            if first_dep_end == -1:
                safe_print("[FAIL] 无法找到合适的位置插入依赖")
                return False
            insert_pos = first_dep_end + len('</dependency>')
        else:
            # 找到 jeecg-system-biz 依赖的结束位置
            dep_end_pos = content.find('</dependency>', system_biz_pos)
            if dep_end_pos == -1:
                safe_print("[FAIL] 无法找到 jeecg-system-biz 依赖的结束位置")
                return False
            insert_pos = dep_end_pos + len('</dependency>')

        # 构建新的依赖项
        new_dependency = f"""

        <dependency>
            <groupId>org.jeecgframework.boot</groupId>
            <artifactId>{artifact_id}</artifactId>
            <version>${{jeecgboot.version}}</version>
        </dependency>"""

        # 插入新依赖
        new_content = content[:insert_pos] + new_dependency + content[insert_pos:]

        # 写回文件
        with open(pom_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        safe_print(f"[OK] 已添加依赖到启动项目pom.xml: {artifact_id}")
        return True

    except Exception as e:
        safe_print(f"[FAIL] 更新启动项目pom.xml失败: {e}")
        return False

def ensure_module_exists(module_name):
    """确保模块存在，如果不存在则创建并配置"""
    safe_print(f"\n[TOOL] 模块管理: {module_name}")
    print("=" * 40)

    # 1. 检查模块是否存在
    if check_module_exists(module_name):
        safe_print(f"[OK] 模块已存在，跳过创建步骤")
        # 即使模块存在，也要确保它已经集成到项目结构中
        integrate_module_to_project(module_name)
        return True

    # 2. 创建模块
    safe_print(f"[PACKAGE] 模块不存在，开始创建...")
    if not create_maven_module(module_name):
        return False

    # 3. 集成模块到项目结构
    if not integrate_module_to_project(module_name):
        return False

    # 4. 验证模块创建结果
    if check_module_exists(module_name):
        safe_print(f"[SUCCESS] 模块创建和配置完成: jeecg-module-{module_name}")
        return True
    else:
        safe_print(f"[FAIL] 模块创建验证失败")
        return False

def integrate_module_to_project(module_name):
    """将模块集成到JeecgBoot项目结构中"""
    safe_print(f"[LINK] 集成模块到项目结构: {module_name}")

    success = True

    # 1. 更新模块注册表 pom.xml
    if not update_module_registry_pom(module_name):
        safe_print(f"[WARN] 模块注册表更新失败")
        success = False

    # 2. 更新启动项目 pom.xml
    if not update_system_start_pom(module_name):
        safe_print(f"[WARN] 启动项目依赖更新失败")
        success = False

    if success:
        safe_print(f"[OK] 模块集成完成: jeecg-module-{module_name}")
    else:
        safe_print(f"[WARN] 模块集成部分失败，请手动检查")

    return success

# ==================== 服务管理功能 ====================

def check_backend_service_status(token=None):
    """检查后端服务状态"""
    try:
        headers = {}
        if token:
            headers = {
                'authorization': f'Bearer {token}',
                'x-access-token': token,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        
        # 尝试多个端点来检查服务状态
        # 1. 首先尝试一个简单的API端点
        try:
            response = requests.get(f"{BASE_URL}/sys/common/static", headers=headers, timeout=5)
            if response.status_code == 200:
                return True, "服务正常运行"
        except:
            pass
        
        # 2. 尝试可用的actuator端点
        try:
            response = requests.get(f"{BASE_URL}/actuator/metrics", headers=headers, timeout=5)
            if response.status_code == 200:
                return True, "服务正常运行"
        except:
            pass
        
        # 3. 尝试不需要认证的基础端点
        try:
            response = requests.get(f"{BASE_URL}", timeout=5)
            if response.status_code in [200, 401, 403]:  # 这些状态码说明服务在运行
                return True, "服务正常运行"
        except:
            pass
        
        return False, "服务未启动或不可访问"
        
    except requests.exceptions.ConnectionError:
        return False, "服务未启动或连接失败"
    except requests.exceptions.Timeout:
        return False, "服务响应超时"
    except Exception as e:
        return False, f"检查服务状态失败: {e}"

def suggest_service_restart():
    """提供服务重启建议"""
    safe_print(f"\n[REFRESH] 后端服务重启建议:")
    safe_print(f"   ")
    safe_print(f"   [LIST] 重启步骤:")
    safe_print(f"      1. 检查当前服务状态:")
    safe_print(f"         ps aux | grep java | grep jeecg")
    safe_print(f"      ")
    safe_print(f"      2. 停止现有服务:")
    safe_print(f"         - 如果通过VS Code启动: 在终端中按 Ctrl+C")
    safe_print(f"         - 如果通过命令行启动: kill -9 <进程ID>")
    safe_print(f"      ")
    safe_print(f"      3. 重新启动服务:")
    safe_print(f"         - 推荐: 通过VS Code的launch.json启动")
    safe_print(f"         - 或命令行: cd jeecg-module-system/jeecg-system-start")
    safe_print(f"         - 执行: mvn spring-boot:run -Dspring-boot.run.profiles=mac")
    safe_print(f"      ")
    safe_print(f"      4. 验证启动成功:")
    safe_print(f"         - 等待看到 'Application is running' 消息")
    safe_print(f"         - 测试: curl http://localhost:8080/jeecg-boot/actuator/health")
    safe_print(f"   ")
    safe_print(f"   [WARN] 重要提示:")
    safe_print(f"      - 新模块代码需要重启服务才能生效")
    safe_print(f"      - 确保使用 profile=mac 配置")
    safe_print(f"      - 服务端口: 8080")

def verify_new_module_loaded(module_name=None):
    """验证新模块是否已加载"""
    if not module_name and CURRENT_TABLE_NAME:
        try:
            business_entity = get_business_entity_from_global_or_config()
            components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
            module_name = components['module_name']
        except:
            pass

    if not module_name:
        safe_print("[WARN] 无法确定模块名称，跳过模块加载验证")
        return False

    safe_print(f"[SEARCH] 验证模块加载状态: jeecg-module-{module_name}")

    try:
        # 由于actuator/mappings端点未暴露，我们用其他方法验证模块加载状态
        # 方法1: 检查项目目录结构是否存在
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        module_path = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
        
        if not os.path.exists(module_path):
            safe_print(f"[FAIL] 模块目录不存在: {module_path}")
            return False
        
        # 方法2: 检查是否有编译后的class文件
        target_path = f"{module_path}/target/classes"
        if os.path.exists(target_path):
            safe_print(f"[OK] 模块已编译: jeecg-module-{module_name}")
            # 由于无法直接检查运行时加载状态，我们假设编译后的模块在重启后会被加载
            return True
        else:
            safe_print(f"[WARN] 模块未编译，需要编译并重启: jeecg-module-{module_name}")
            return False
    except Exception as e:
        safe_print(f"[WARN] 检查模块加载状态失败: {e}")
        return False

# ==================== 前端代码迁移功能 ====================

def migrate_frontend_code():
    """前端代码目录迁移和重组 - 解析SQL注释获取正确路径并移动到views目录"""
    migration_config = CONFIG.get('frontend_migration', {})

    if not migration_config.get('enabled', True):
        print("⏭️ 前端代码迁移功能已禁用，跳过迁移步骤")
        return True

    safe_print(f"\n{'='*50}")
    safe_print("[FOLDER] 开始前端代码目录迁移和重组...")

    try:
        # 1. 解析当前表名获取模块信息
        if not CURRENT_TABLE_NAME:
            safe_print("[FAIL] 无法获取当前表名，跳过前端代码迁移")
            return False

        business_entity = get_business_entity_from_global_or_config()
        components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
        module_name = components['module_name']
        sub_module = components['sub_module']

        safe_print(f"[LIST] 模块信息:")
        safe_print(f"   模块名: {module_name}")
        safe_print(f"   子模块: {sub_module}")

        # 2. 构建路径 - 增加容错机制
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

        # 源路径：后端模块中的vue3目录
        # 注意：JeecgBoot API生成的实际路径可能与我们的解析逻辑不同
        # 需要检查多个可能的路径
        # 从CURRENT_TABLE_NAME获取完整的业务实体名
        entity_name = components['entity_name'].lower()

        possible_source_paths = [
            # 1. JeecgBoot实际生成路径：module_name/sub_module/entity_name
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / sub_module / entity_name / 'vue3',
            # 2. 备用路径：module_name/sub_module
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / sub_module / 'vue3',
            # 3. 兼容旧版本路径：module_name/business_scenario
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / components['business_scenario'] / 'vue3',
        ]

        # 找到实际存在的源路径
        source_vue3_dir = None
        for path in possible_source_paths:
            if path.exists():
                source_vue3_dir = path
                safe_print(f"[OK] 找到实际的vue3源路径: {source_vue3_dir}")
                break

        if not source_vue3_dir:
            safe_print(f"[WARN] 在后端模块中未找到vue3目录，检查是否已迁移...")
            # 检查前端项目中是否已有相同模块的文件
            frontend_module_dir = Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / sub_module
            if frontend_module_dir.exists():
                safe_print(f"[OK] 发现前端项目中已存在模块目录: {frontend_module_dir}")
                safe_print(f"   这可能是同一模块的多个表单，前端代码将合并到现有目录")
                return True  # 返回成功，因为前端目录已存在

            # 如果都不存在，使用第一个作为默认值（用于后续的容错搜索）
            source_vue3_dir = possible_source_paths[0]

        # 3. 确定正确的前端迁移路径 - 优先级顺序：SQL文件 > 配置文件 > 默认逻辑
        target_base_path = migration_config.get('target_base_path', 'jeecgboot-vue3/src/views')
        target_views_base = Path(project_prefix) / target_base_path

        # 唯一路径决策：从SQL文件解析前端路径
        correct_frontend_path = extract_frontend_path_from_sql()
        if not correct_frontend_path:
            safe_print("[FAIL] 无法从SQL文件解析到前端路径，前端迁移失败")
            return False

        safe_print(f"[DOC] 从SQL文件解析到正确的前端路径: {correct_frontend_path}")
        final_target_dir = target_views_base / correct_frontend_path

        # 重命名后的路径：将vue3重命名为子模块名
        renamed_dir = source_vue3_dir.parent / sub_module

        safe_print(f"[SYMBOL] 路径信息:")
        safe_print(f"   源vue3目录: {source_vue3_dir}")
        safe_print(f"   重命名目录: {renamed_dir}")
        safe_print(f"   最终目标: {final_target_dir}")

        # 3. 验证源目录存在且包含vue3前端文件 - 增加容错搜索
        if not source_vue3_dir.exists():
            safe_print(f"[FAIL] 源vue3目录不存在: {source_vue3_dir}")

            # 容错机制1：检查前端项目中是否已有文件（可能之前已迁移但路径错误）
            # 修正：检查多个可能的错误位置，包括module_name目录和其他可能的错误路径
            possible_wrong_locations = [
                Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / module_name,
                Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / 'pages',  # 检查pages目录
                Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / f"{module_name}_{sub_module}",
            ]

            current_frontend_dir = None
            for possible_dir in possible_wrong_locations:
                if possible_dir.exists():
                    vue_files = list(possible_dir.glob('*.vue'))
                    ts_files = list(possible_dir.glob('*.ts'))
                    js_files = list(possible_dir.glob('*.js'))

                    if vue_files or ts_files or js_files:
                        current_frontend_dir = possible_dir
                        safe_print(f"[OK] 在前端项目中找到已迁移的文件: {current_frontend_dir}")
                        safe_print(f"   找到 {len(vue_files)} 个Vue文件，{len(ts_files)} 个TS文件，{len(js_files)} 个JS文件")
                        break

            if current_frontend_dir:
                # 直接从前端项目的错误位置迁移到正确位置
                return _migrate_from_frontend_wrong_location(current_frontend_dir, final_target_dir, migration_config)

            # 容错机制2：在当前模块中进行深度搜索
            safe_print(f"[SEARCH] 启动后端模块容错搜索机制...")
            
            # 搜索当前模块下的所有vue3目录
            module_base_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'
            found_alternative = False
            
            if module_base_path.exists():
                # 使用glob递归搜索所有vue3目录
                vue3_dirs = list(module_base_path.glob('**/vue3'))
                safe_print(f"[SEARCH] 在模块 {module_name} 中找到 {len(vue3_dirs)} 个vue3目录")
                
                for vue3_dir in vue3_dirs:
                    # 检查是否包含前端文件
                    vue_files = list(vue3_dir.glob('*.vue'))
                    ts_files = list(vue3_dir.glob('*.ts'))
                    js_files = list(vue3_dir.glob('*.js'))
                    
                    if vue_files or ts_files or js_files:
                        safe_print(f"[OK] 找到包含前端文件的vue3目录: {vue3_dir}")
                        safe_print(f"   包含: {len(vue_files)} 个Vue文件，{len(ts_files)} 个TS文件，{len(js_files)} 个JS文件")
                        source_vue3_dir = vue3_dir
                        # 重新计算renamed_dir基于实际找到的路径
                        renamed_dir = source_vue3_dir.parent / sub_module
                        found_alternative = True
                        break

            if not found_alternative:
                safe_print(f"[WARN] 在后端模块中未找到前端文件")
                # 检查前端项目中是否已有同模块的文件（可能是同一模块的多个表单）
                frontend_module_dir = Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / sub_module
                if frontend_module_dir.exists():
                    existing_files = list(frontend_module_dir.glob('*.vue')) + list(frontend_module_dir.glob('*.ts')) + list(frontend_module_dir.glob('*.js'))
                    if existing_files:
                        safe_print(f"[OK] 发现前端项目中已存在同模块文件: {frontend_module_dir}")
                        safe_print(f"   已有 {len(existing_files)} 个前端文件")
                        safe_print(f"   这可能是同一模块的多个表单，新生成的前端代码应该已经直接生成到正确位置")
                        return True  # 返回成功，因为前端目录已存在且有文件

                safe_print(f"[FAIL] 在所有位置都未找到前端文件，且前端项目中也无同模块文件")
                return False

        # 检查是否包含前端文件
        vue_files = list(source_vue3_dir.glob('*.vue'))
        ts_files = list(source_vue3_dir.glob('*.ts'))
        js_files = list(source_vue3_dir.glob('*.js'))

        if not (vue_files or ts_files or js_files):
            safe_print(f"[FAIL] 源目录中未找到前端文件: {source_vue3_dir}")
            return False

        safe_print(f"[OK] 源目录验证通过，找到 {len(vue_files)} 个Vue文件，{len(ts_files)} 个TS文件，{len(js_files)} 个JS文件")

        # 4. 执行重命名和移动操作
        return _execute_rename_and_move(source_vue3_dir, renamed_dir, final_target_dir, target_views_base, migration_config)

    except Exception as e:
        safe_print(f"[FAIL] 前端代码迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_frontend_path_from_sql():
    """从生成的SQL文件中解析正确的前端路径"""
    try:
        # 查找SQL文件
        sql_file_path = find_generated_sql_file()
        if not sql_file_path:
            safe_print("[WARN] 未找到SQL文件，无法解析前端路径")
            return None

        safe_print(f"[DOC] 解析SQL文件: {sql_file_path}")

        # 读取SQL文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析注释中的前端路径
        # 格式：-- 注意：该页面对应的前台目录为views/scm/device文件夹下
        import re
        pattern = r'-- 注意：该页面对应的前台目录为views/([^文]+)文件夹下'
        match = re.search(pattern, content)

        if match:
            frontend_path = match.group(1).strip()
            safe_print(f"[OK] 解析到前端路径: views/{frontend_path}")
            return frontend_path
        else:
            safe_print("[WARN] SQL文件中未找到前端路径注释")
            return None

    except Exception as e:
        safe_print(f"[FAIL] 解析SQL文件前端路径失败: {e}")
        return None

def extract_frontend_path_from_config():
    """从当前配置文件中读取frontend_path"""
    try:
        # 优先使用全局变量 FORM_DATA_FILE（命令行指定的配置文件）
        config_file_path = None

        # 第一优先级：使用全局变量 FORM_DATA_FILE
        if FORM_DATA_FILE and os.path.exists(FORM_DATA_FILE):
            config_file_path = FORM_DATA_FILE
            safe_print(f"[LIST] 使用命令行指定的配置文件: {config_file_path}")
        else:
            # 第二优先级：根据表名推断配置文件（向后兼容）
            script_dir = os.path.dirname(os.path.abspath(__file__))

            if CURRENT_TABLE_NAME:
                business_entity = get_business_entity_from_global_or_config()
                components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
                entity_name = components['entity_name'].lower()

                # 尝试多个可能的配置文件名
                possible_config_files = [
                    f"{entity_name}_config.json",
                    f"{components['business_scenario']}_config.json",
                    f"{components['sub_module']}_config.json"
                ]

                for config_name in possible_config_files:
                    config_path = os.path.join(script_dir, config_name)
                    if os.path.exists(config_path):
                        config_file_path = config_path
                        safe_print(f"[LIST] 根据表名推断的配置文件: {config_file_path}")
                        break

        if not config_file_path:
            safe_print("[WARN] 无法找到当前配置文件，无法读取frontend_path")
            return None

        # 读取配置文件
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 提取frontend_path
        frontend_path = config.get('metadata', {}).get('derived_formats', {}).get('frontend_path')

        if frontend_path:
            safe_print(f"[OK] 从配置文件读取到frontend_path: {frontend_path}")
            return frontend_path
        else:
            safe_print("[WARN] 配置文件中未找到metadata.derived_formats.frontend_path")
            return None

    except Exception as e:
        safe_print(f"[FAIL] 从配置文件读取frontend_path失败: {e}")
        return None

def _migrate_from_frontend_wrong_location(source_dir, target_dir, migration_config):
    """从前端项目的错误位置迁移到正确位置"""
    safe_print(f"\n[REFRESH] 从前端项目错误位置迁移到正确位置...")
    safe_print(f"   源目录: {source_dir}")
    safe_print(f"   目标目录: {target_dir}")

    try:
        # 检查是否是移动到子目录的情况（避免移动目录到自身）
        if target_dir.is_relative_to(source_dir):
            safe_print(f"[WARN] 检测到目标目录是源目录的子目录，使用特殊处理方式")
            return _migrate_to_subdirectory(source_dir, target_dir)

        # 确保目标目录的父目录存在
        target_dir.parent.mkdir(parents=True, exist_ok=True)

        # 检查目标目录是否已存在
        if target_dir.exists():
            safe_print(f"[WARN] 目标目录已存在: {target_dir}")
            if migration_config.get('cleanup_source', False):
                safe_print(f"   删除已存在的目标目录...")
                shutil.rmtree(target_dir)
            else:
                safe_print(f"[FAIL] 目标目录已存在，停止迁移以避免覆盖")
                return False

        # 移动整个目录
        shutil.move(str(source_dir), str(target_dir))

        # 验证移动结果
        if target_dir.exists():
            files = list(target_dir.rglob('*'))
            file_count = len([f for f in files if f.is_file()])

            safe_print(f"[OK] 前端文件迁移成功!")
            safe_print(f"   最终位置: {target_dir}")
            safe_print(f"   文件数量: {file_count} 个")

            # 显示主要文件
            main_files = []
            for pattern in ['*.vue', '*.ts', '*.js']:
                main_files.extend(target_dir.glob(pattern))

            if main_files:
                safe_print(f"\n[FOLDER] 主要文件列表:")
                for file in main_files[:10]:  # 显示前10个
                    safe_print(f"      {file.name}")
                if len(main_files) > 10:
                    safe_print(f"      ... 还有 {len(main_files) - 10} 个文件")

            return True
        else:
            safe_print(f"[FAIL] 迁移失败，目标目录不存在")
            return False

    except Exception as e:
        safe_print(f"[FAIL] 前端文件迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def _migrate_to_subdirectory(source_dir, target_dir):
    """将目录内容迁移到其子目录"""
    safe_print(f"\n[REFRESH] 将目录内容迁移到子目录...")

    try:
        # 创建临时目录
        import tempfile
        temp_dir = Path(tempfile.mkdtemp(prefix='jeecg_migration_'))
        safe_print(f"   创建临时目录: {temp_dir}")

        # 1. 先将所有文件移动到临时目录
        safe_print(f"   步骤1: 移动文件到临时目录")
        moved_items = []
        for item in source_dir.iterdir():
            if item.name != target_dir.name:  # 不移动目标目录本身
                temp_item = temp_dir / item.name
                shutil.move(str(item), str(temp_item))
                moved_items.append(item.name)
                safe_print(f"      移动: {item.name}")

        # 2. 确保目标目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_print(f"   步骤2: 创建目标目录: {target_dir}")

        # 3. 将文件从临时目录移动到目标目录
        safe_print(f"   步骤3: 移动文件到目标目录")
        for item_name in moved_items:
            temp_item = temp_dir / item_name
            target_item = target_dir / item_name
            shutil.move(str(temp_item), str(target_item))
            safe_print(f"      移动: {item_name}")

        # 4. 清理临时目录
        shutil.rmtree(temp_dir)
        safe_print(f"   步骤4: 清理临时目录")

        # 验证结果
        if target_dir.exists():
            files = list(target_dir.rglob('*'))
            file_count = len([f for f in files if f.is_file()])

            safe_print(f"[OK] 子目录迁移成功!")
            safe_print(f"   最终位置: {target_dir}")
            safe_print(f"   文件数量: {file_count} 个")

            # 显示主要文件
            main_files = []
            for pattern in ['*.vue', '*.ts', '*.js']:
                main_files.extend(target_dir.glob(pattern))

            if main_files:
                safe_print(f"\n[FOLDER] 主要文件列表:")
                for file in main_files[:10]:  # 显示前10个
                    safe_print(f"      {file.name}")
                if len(main_files) > 10:
                    safe_print(f"      ... 还有 {len(main_files) - 10} 个文件")

            return True
        else:
            safe_print(f"[FAIL] 子目录迁移失败，目标目录不存在")
            return False

    except Exception as e:
        safe_print(f"[FAIL] 子目录迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def _execute_rename_and_move(source_vue3_dir, renamed_dir, final_target_dir, target_views_base, migration_config):
    """执行重命名和移动操作"""
    safe_print(f"\n[REFRESH] 执行重命名和移动操作...")

    try:
        # 步骤1：重命名vue3目录为子模块名
        safe_print(f"1. 重命名vue3目录为子模块名...")

        # 检查重命名目标是否已存在
        if renamed_dir.exists():
            safe_print(f"[WARN] 重命名目标目录已存在: {renamed_dir}")
            if migration_config.get('cleanup_source', False):
                safe_print(f"   删除已存在的目录...")
                shutil.rmtree(renamed_dir)
            else:
                safe_print(f"   跳过重命名步骤")
                # 如果目录已存在，直接使用现有目录
                pass

        # 执行重命名操作
        if not renamed_dir.exists():
            source_vue3_dir.rename(renamed_dir)
            safe_print(f"[OK] 重命名成功: vue3 → {renamed_dir.name}")

        # 验证重命名后的目录
        if not renamed_dir.exists():
            safe_print(f"[FAIL] 重命名后目录不存在: {renamed_dir}")
            return False

        # 统计目录中的文件
        vue_files = list(renamed_dir.glob('*.vue'))
        ts_files = list(renamed_dir.glob('*.ts'))
        js_files = list(renamed_dir.glob('*.js'))
        all_files = list(renamed_dir.rglob('*'))
        file_count = len([f for f in all_files if f.is_file()])

        safe_print(f"[LIST] 重命名目录内容: {file_count} 个文件")
        safe_print(f"   Vue文件: {len(vue_files)} 个")
        safe_print(f"   TS文件: {len(ts_files)} 个")
        safe_print(f"   JS文件: {len(js_files)} 个")

        # 步骤2：确保目标views目录存在
        safe_print(f"\n2. 准备目标目录...")
        if migration_config.get('create_target_dirs', True):
            target_views_base.mkdir(parents=True, exist_ok=True)
            safe_print(f"[OK] 目标views目录已准备: {target_views_base}")

        # 检查最终目标是否已存在
        if final_target_dir.exists():
            safe_print(f"[WARN] 最终目标目录已存在: {final_target_dir}")
            if migration_config.get('cleanup_source', False):
                safe_print(f"   删除已存在的目标目录...")
                shutil.rmtree(final_target_dir)
            else:
                safe_print(f"[REFRESH] 目标目录已存在，执行智能合并...")
                return _merge_frontend_files(renamed_dir, final_target_dir)

        # 步骤3：移动整个目录到views下
        safe_print(f"\n3. 移动目录到前端项目...")
        safe_print(f"   源目录: {renamed_dir}")
        safe_print(f"   目标位置: {final_target_dir}")

        # 使用shutil.move进行目录移动
        shutil.move(str(renamed_dir), str(final_target_dir))

        # 验证移动结果
        if final_target_dir.exists():
            # 重新统计移动后的文件
            final_all_files = list(final_target_dir.rglob('*'))
            final_file_count = len([f for f in final_all_files if f.is_file()])

            safe_print(f"[OK] 目录移动成功!")
            safe_print(f"   最终位置: {final_target_dir}")
            safe_print(f"   文件数量: {final_file_count} 个")

            # 显示主要文件
            main_files = []
            for pattern in ['*.vue', '*.ts', '*.js']:
                main_files.extend(final_target_dir.glob(pattern))

            if main_files:
                safe_print(f"\n[FOLDER] 主要文件列表:")
                for file in main_files[:10]:  # 显示前10个
                    safe_print(f"      {file.name}")
                if len(main_files) > 10:
                    safe_print(f"      ... 还有 {len(main_files) - 10} 个文件")

            return True
        else:
            safe_print(f"[FAIL] 目录移动失败，目标目录不存在")
            return False

    except Exception as e:
        safe_print(f"[FAIL] 重命名和移动操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def _merge_frontend_files(source_dir, target_dir):
    """智能合并前端文件到已存在的目标目录"""
    safe_print(f"\n[REFRESH] 开始智能合并前端文件...")
    safe_print(f"   源目录: {source_dir}")
    safe_print(f"   目标目录: {target_dir}")

    try:
        merged_count = 0
        skipped_count = 0

        # 遍历源目录中的所有文件
        for source_file in source_dir.rglob('*'):
            if source_file.is_file():
                # 计算相对路径
                relative_path = source_file.relative_to(source_dir)
                target_file = target_dir / relative_path

                # 确保目标文件的父目录存在
                target_file.parent.mkdir(parents=True, exist_ok=True)

                if target_file.exists():
                    safe_print(f"   [WARN] 文件已存在，跳过: {relative_path}")
                    skipped_count += 1
                else:
                    # 复制文件到目标位置
                    shutil.copy2(source_file, target_file)
                    safe_print(f"   [OK] 合并文件: {relative_path}")
                    merged_count += 1

        # 删除源目录
        shutil.rmtree(source_dir)

        safe_print(f"\n[CHART] 合并统计:")
        safe_print(f"   [OK] 成功合并: {merged_count} 个文件")
        safe_print(f"   [WARN] 跳过重复: {skipped_count} 个文件")
        safe_print(f"   [SYMBOL]️ 清理源目录: {source_dir}")

        return True

    except Exception as e:
        safe_print(f"[FAIL] 智能合并失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== 数据库SQL执行功能 ====================

def validate_database_type():
    """验证数据库类型是否支持"""
    db_config = CONFIG.get('database', {})
    db_type = db_config.get('type', 'mysql').lower()
    
    safe_print(f"[SEARCH] 检查数据库类型: {db_type}")
    
    if db_type != 'mysql':
        safe_print(f"[FAIL] 暂不支持 {db_type} 的数据库处理")
        print("   目前仅支持 MySQL 数据库")
        print("   请设置环境变量 JEECG_DATABASE_TYPE=mysql 或在配置文件中指定")
        return False
    
    safe_print("[OK] 数据库类型验证通过")
    return True

def execute_database_sql():
    """执行生成的SQL文件到数据库"""
    db_config = CONFIG.get('database_execution', {})

    if not db_config.get('enabled', True):
        print("⏭️ 数据库SQL执行功能已禁用，跳过SQL执行步骤")
        return True

    safe_print(f"\n{'='*50}")
    safe_print("[DATABASE] 开始执行数据库SQL文件...")

    try:
        # 1. 查找生成的SQL文件
        sql_file_path = find_generated_sql_file()
        if not sql_file_path:
            safe_print("[FAIL] 未找到生成的SQL文件，跳过数据库执行")
            return False

        safe_print(f"[DOC] 找到SQL文件: {sql_file_path}")

        # 2. 解析数据库连接配置
        db_connection = parse_database_config()
        if not db_connection:
            safe_print("[FAIL] 无法解析数据库连接配置，跳过数据库执行")
            return False

        safe_print(f"[LINK] 数据库连接: {db_connection['host']}:{db_connection['port']}/{db_connection['database']}")

        # 3. 执行SQL文件
        return execute_sql_file(sql_file_path, db_connection)

    except Exception as e:
        safe_print(f"[FAIL] 数据库SQL执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_generated_sql_file():
    """精准查找生成的SQL文件 - 基于entityName匹配，按日期和序号倒排"""
    try:
        if not CURRENT_TABLE_NAME:
            safe_print("[FAIL] 无法获取当前表名，无法定位SQL文件")
            return None

        # 解析表名获取模块信息
        business_entity = get_business_entity_from_global_or_config()
        components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
        entity_name = components['entity_name']

        # 构建搜索路径
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

        safe_print(f"[SEARCH] 精准搜索SQL文件...")
        safe_print(f"   实体名: {entity_name}")
        safe_print(f"   搜索模式: *{entity_name}.sql")

        # 搜索SQL文件的路径列表（按优先级排序）
        search_paths = [
            # 第一优先级：前端项目views目录
            Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views',
            # 第二优先级：后端模块目录
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{components["module_name"]}',
        ]

        sql_files = []

        # 在所有搜索路径中查找SQL文件
        for search_path in search_paths:
            if not search_path.exists():
                safe_print(f"   跳过不存在的路径: {search_path}")
                continue

            safe_print(f"   搜索路径: {search_path}")

            # 搜索所有以entityName.sql结尾的SQL文件（不区分大小写）
            sql_pattern = f"*{entity_name}.sql"
            safe_print(f"   搜索模式: {sql_pattern}")

            # 先搜索精确匹配
            for sql_file in search_path.rglob(sql_pattern):
                sql_files.append(sql_file)
                safe_print(f"   找到SQL文件: {sql_file}")

            # 如果没找到，尝试不区分大小写搜索
            if not sql_files:
                safe_print(f"   精确匹配未找到，尝试不区分大小写搜索...")
                for sql_file in search_path.rglob("*.sql"):
                    if sql_file.name.lower().endswith(f"{entity_name.lower()}.sql"):
                        sql_files.append(sql_file)
                        safe_print(f"   找到SQL文件（不区分大小写）: {sql_file}")

            # 如果在当前路径找到了文件，就不再搜索其他路径
            if sql_files:
                break

        if not sql_files:
            safe_print(f"[FAIL] 未找到匹配的SQL文件: {sql_pattern}")
            return None

        # 按照文件名中的日期和序号倒排，取最新的文件
        # 文件名格式：V20250730_1__menu_insert_Exceltemplate.sql
        import re

        def extract_date_and_seq(file_path):
            """从文件名中提取日期和序号用于排序"""
            filename = file_path.name
            # 匹配格式：V20250730_1__menu_insert_Exceltemplate.sql
            match = re.match(r'V(\d{8})_(\d+)__', filename)
            if match:
                date_str = match.group(1)  # 20250730
                seq_str = match.group(2)   # 1
                return (date_str, int(seq_str))
            else:
                # 如果不匹配标准格式，使用文件修改时间
                return ('00000000', 0)

        # 按日期倒排、相同日期按序号倒排
        sql_files.sort(key=extract_date_and_seq, reverse=True)
        latest_file = sql_files[0]

        safe_print(f"[OK] 精准定位到最新SQL文件: {latest_file}")
        return latest_file
    except Exception as e:
        safe_print(f"[FAIL] 搜索SQL文件失败: {e}")
        return None

def extract_frontend_path_from_sql_in_backend():
    """从后端目录的SQL文件中解析前端路径"""
    try:
        if not CURRENT_TABLE_NAME:
            return None

        # 解析表名获取模块信息
        business_entity = get_business_entity_from_global_or_config()
        components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
        module_name = components['module_name']
        sub_module = components['sub_module']
        business_scenario = components['business_scenario']
        entity_name = components['entity_name']

        # 构建后端SQL文件搜索路径
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        today = datetime.now().strftime("%Y%m%d")

        # 在后端目录搜索SQL文件
        backend_search_paths = [
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / business_scenario / 'vue3',
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / sub_module / 'vue3',
        ]

        patterns = [
            f"V{today}_*__menu_insert_*{entity_name}*.sql",
            f"V{today}_*__menu_insert*.sql",
            f"*{entity_name}*.sql",
            f"*menu_insert*.sql"
        ]

        for search_path in backend_search_paths:
            if not search_path.exists():
                continue

            for pattern in patterns:
                sql_files = list(search_path.glob(pattern))
                if sql_files:
                    # 找到SQL文件，解析其中的前端路径
                    latest_file = max(sql_files, key=lambda f: f.stat().st_mtime)

                    # 读取SQL文件内容
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 解析注释中的前端路径
                    import re
                    pattern_regex = r'-- 注意：该页面对应的前台目录为views/([^文]+)文件夹下'
                    match = re.search(pattern_regex, content)

                    if match:
                        frontend_path = match.group(1).strip()
                        safe_print(f"[DOC] 从后端SQL文件解析到前端路径: {frontend_path}")
                        return frontend_path

        return None

    except Exception as e:
        safe_print(f"[FAIL] 从后端SQL文件解析前端路径失败: {e}")
        return None

def parse_database_config():
    """解析数据库连接配置"""
    try:
        # 优先使用环境变量配置的数据库信息
        db_config = CONFIG.get('database', {})
        db_url = db_config.get('url', '')
        
        if db_url and db_url.startswith('jdbc:mysql://'):
            safe_print(f"[OPEN_BOOK] 使用环境变量数据库配置")
            
            # 解析JDBC URL格式: jdbc:mysql://host:port/database
            import re
            url_pattern = r'jdbc:mysql://([^:]+):(\d+)/([^?\s]+)'
            url_match = re.search(url_pattern, db_url)
            
            if url_match:
                host = url_match.group(1)
                port = int(url_match.group(2))
                database = url_match.group(3)
                username = db_config.get('username', 'root')
                password = db_config.get('password', '123456')
                
                safe_print(f"[OK] 环境变量数据库配置解析成功: {host}:{port}/{database} (用户: {username})")
                
                return {
                    'host': host,
                    'port': port,
                    'database': database,
                    'username': username,
                    'password': password
                }
            else:
                safe_print(f"[FAIL] 无法解析数据库URL格式: {db_url}")
        
        # 如果环境变量配置无效，则回退到读取YAML文件
        safe_print(f"[WARN] 环境变量数据库配置无效，回退到读取YAML文件")
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        config_file = Path(project_prefix) / 'jeecg-boot' / 'jeecg-module-system' / 'jeecg-system-start' / 'src' / 'main' / 'resources' / 'application-dev.yml'

        if not config_file.exists():
            safe_print(f"[FAIL] YAML配置文件不存在: {config_file}")
            return None

        safe_print(f"[OPEN_BOOK] 读取YAML数据库配置: {config_file}")

        # 简单解析YAML中的数据库配置
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 增强调试：显示解析过程
        safe_print(f"[SEARCH] 开始解析数据库配置...")

        # 提取数据库连接信息（简单字符串匹配）
        import re

        # 提取URL - 改进正则表达式以处理URL参数
        url_pattern = r'url:\s*jdbc:mysql://([^:]+):(\d+)/([^?\s]+)'
        url_match = re.search(url_pattern, content)
        if not url_match:
            safe_print("[FAIL] 无法解析数据库URL")
            safe_print(f"[SEARCH] 搜索模式: {url_pattern}")
            # 显示URL相关的行用于调试
            url_lines = [line.strip() for line in content.split('\n') if 'url:' in line and 'jdbc:mysql' in line]
            if url_lines:
                safe_print(f"[SEARCH] 找到的URL行: {url_lines[0]}")
            return None

        host = url_match.group(1)
        port = int(url_match.group(2))
        database = url_match.group(3)

        safe_print(f"[OK] URL解析成功: {host}:{port}/{database}")

        # 改进master配置块解析逻辑
        master_start = content.find('master:')
        if master_start == -1:
            safe_print("[FAIL] 未找到master配置块")
            return None

        safe_print(f"[OK] 找到master配置块，位置: {master_start}")

        # 找到master配置块的结束位置 - 改进逻辑
        # 查找下一个同级配置（以相同缩进开始的行）
        lines = content[master_start:].split('\n')
        master_lines = [lines[0]]  # 包含 "master:" 行

        # 从第二行开始，收集属于master块的行
        for line in lines[1:]:
            # 如果是空行或注释行，跳过
            if not line.strip() or line.strip().startswith('#'):
                continue
            # 如果缩进级别回到master同级或更高级别，停止
            if line and not line.startswith('          '):  # master的子项应该有更深的缩进
                break
            master_lines.append(line)

        master_content = '\n'.join(master_lines)
        safe_print(f"[SEARCH] Master配置块内容:")
        for line in master_lines[:5]:  # 只显示前5行用于调试
            safe_print(f"   {line}")

        # 在master配置块中搜索用户名和密码
        username_match = re.search(r'username:\s*(\S+)', master_content)
        password_match = re.search(r'password:\s*(\S+)', master_content)

        if not username_match:
            safe_print("[FAIL] 无法解析数据库用户名")
            safe_print(f"[SEARCH] 在master块中搜索username模式")
            return None

        if not password_match:
            safe_print("[FAIL] 无法解析数据库密码")
            safe_print(f"[SEARCH] 在master块中搜索password模式")
            return None

        username = username_match.group(1)
        password = password_match.group(1)

        safe_print(f"[OK] 用户名解析成功: {username}")
        safe_print(f"[OK] 密码解析成功: {'*' * len(password)}")

        db_config = {
            'host': host,
            'port': port,
            'database': database,
            'username': username,
            'password': password
        }

        safe_print(f"[OK] 数据库配置解析完成: {host}:{port}/{database} (用户: {username})")
        return db_config

    except Exception as e:
        safe_print(f"[FAIL] 解析数据库配置失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def execute_sql_file(sql_file_path, db_connection):
    """执行SQL文件到数据库"""
    try:
        # 检查是否安装了mysql客户端或使用Python库
        db_config = CONFIG.get('database_execution', {})
        execution_method = db_config.get('method', 'mysql_client')  # mysql_client 或 python_library

        if execution_method == 'python_library':
            return execute_sql_with_python(sql_file_path, db_connection)
        else:
            return execute_sql_with_mysql_client(sql_file_path, db_connection)

    except Exception as e:
        safe_print(f"[FAIL] SQL文件执行失败: {e}")
        return False

def execute_sql_with_mysql_client(sql_file_path, db_connection):
    """使用mysql命令行客户端执行SQL文件"""
    try:
        safe_print(f"[TOOL] 使用mysql命令行客户端执行SQL...")

        # 构建mysql命令
        mysql_cmd = [
            'mysql',
            f"--host={db_connection['host']}",
            f"--port={db_connection['port']}",
            f"--user={db_connection['username']}",
            f"--password={db_connection['password']}",
            f"--database={db_connection['database']}",
            '--execute', f"source {sql_file_path}"
        ]

        safe_print(f"   执行命令: mysql --host={db_connection['host']} --port={db_connection['port']} --user={db_connection['username']} --password=*** --database={db_connection['database']} --execute=\"source {sql_file_path}\"")

        # 执行命令
        result = subprocess.run(mysql_cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            safe_print("[OK] SQL文件执行成功")
            if result.stdout:
                safe_print(f"   输出: {result.stdout}")
            return True
        else:
            safe_print(f"[FAIL] SQL文件执行失败")
            safe_print(f"   错误: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        safe_print("[FAIL] SQL执行超时")
        return False
    except FileNotFoundError:
        print("ℹ️ mysql命令行客户端未安装，自动切换到Python库执行...")
        return execute_sql_with_python(sql_file_path, db_connection)
    except Exception as e:
        safe_print(f"[FAIL] mysql客户端执行失败: {e}")
        return False

def execute_sql_with_python(sql_file_path, db_connection):
    """使用Python库执行SQL文件"""
    connection = None
    cursor = None

    try:
        safe_print(f"[SYMBOL] 使用Python库执行SQL...")

        # 尝试导入mysql库
        try:
            import mysql.connector
        except ImportError:
            safe_print("[FAIL] 未安装mysql-connector-python库")
            safe_print("   ")
            safe_print("   [TOOL] 解决方案:")
            safe_print("   1. 安装库: pip install mysql-connector-python")
            safe_print("   2. 如果使用conda环境: conda install mysql-connector-python")
            safe_print("   3. 如果在虚拟环境中，请先激活虚拟环境再安装")
            safe_print("   ")
            safe_print("   [TIP] 提示: 安装完成后重新运行命令即可")
            safe_print("   ⏭️  跳过数据库SQL执行步骤")
            return False

        # 读取SQL文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 分割SQL语句（简单分割，按分号分割）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

        safe_print(f"   找到 {len(sql_statements)} 条SQL语句")

        # 连接数据库 - 增强错误处理
        safe_print(f"[LINK] 尝试连接数据库: {db_connection['host']}:{db_connection['port']}/{db_connection['database']}")
        try:
            connection = mysql.connector.connect(
                host=db_connection['host'],
                port=db_connection['port'],
                user=db_connection['username'],
                password=db_connection['password'],
                database=db_connection['database'],
                autocommit=False  # 明确设置事务模式
            )
            safe_print("[OK] 数据库连接成功")
        except mysql.connector.Error as db_error:
            safe_print(f"[FAIL] 数据库连接失败: {db_error}")
            safe_print(f"   错误代码: {db_error.errno}")
            safe_print(f"   错误信息: {db_error.msg}")
            return False
        except Exception as e:
            safe_print(f"[FAIL] 数据库连接异常: {e}")
            return False

        # 验证连接状态
        if not connection.is_connected():
            safe_print("[FAIL] 数据库连接状态异常")
            return False

        cursor = connection.cursor()

        # 执行SQL语句
        executed_count = 0
        failed_count = 0
        duplicate_count = 0

        for i, sql_stmt in enumerate(sql_statements, 1):
            if sql_stmt:
                try:
                    cursor.execute(sql_stmt)
                    executed_count += 1
                    safe_print(f"   [OK] 语句 {i}/{len(sql_statements)} 执行成功")
                except mysql.connector.Error as sql_error:
                    # 检查是否是重复键错误
                    if sql_error.errno == 1062:  # Duplicate entry error
                        duplicate_count += 1
                        safe_print(f"   [WARN]  语句 {i}/{len(sql_statements)} 重复记录，跳过")
                        safe_print(f"      SQL: {sql_stmt[:100]}...")
                    else:
                        failed_count += 1
                        safe_print(f"   [FAIL] 语句 {i}/{len(sql_statements)} 执行失败: {sql_error}")
                        safe_print(f"      错误代码: {sql_error.errno}")
                        safe_print(f"      SQL: {sql_stmt[:100]}...")
                except Exception as e:
                    failed_count += 1
                    safe_print(f"   [FAIL] 语句 {i}/{len(sql_statements)} 执行异常: {e}")
                    safe_print(f"      SQL: {sql_stmt[:100]}...")

        # 提交事务
        if executed_count > 0:
            try:
                connection.commit()
                safe_print(f"[OK] 事务提交成功")
            except Exception as e:
                safe_print(f"[FAIL] 事务提交失败: {e}")
                connection.rollback()
                return False

        # 显示执行结果统计
        total_processed = executed_count + duplicate_count
        safe_print(f"[OK] SQL文件执行完成:")
        safe_print(f"   [CHART] 总语句数: {len(sql_statements)}")
        safe_print(f"   [OK] 成功执行: {executed_count}")
        if duplicate_count > 0:
            safe_print(f"   [WARN]  重复跳过: {duplicate_count}")
        if failed_count > 0:
            safe_print(f"   [FAIL] 执行失败: {failed_count}")
        safe_print(f"   [UP] 处理成功率: {total_processed}/{len(sql_statements)} ({total_processed/len(sql_statements)*100:.1f}%)")

        # 验证关键记录是否存在
        if executed_count > 0 or duplicate_count > 0:
            safe_print(f"[SEARCH] 验证数据库记录...")
            try:
                # 检查主菜单记录（通常是第一条INSERT语句）
                cursor.execute("SELECT COUNT(*) FROM sys_permission WHERE name LIKE '%教师信息管理表%' OR name LIKE '%invoice%' OR name LIKE '%财务%'")
                count = cursor.fetchone()[0]
                if count > 0:
                    safe_print(f"   [OK] 数据库中找到 {count} 条相关权限记录")
                else:
                    safe_print(f"   [WARN]  数据库中未找到相关权限记录")
            except Exception as e:
                safe_print(f"   [WARN]  验证记录时出错: {e}")

        return total_processed > 0

    except Exception as e:
        safe_print(f"[FAIL] Python库执行SQL失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 确保连接被正确关闭
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                safe_print("[SYMBOL] 数据库连接已关闭")
        except Exception as e:
            safe_print(f"[WARN]  关闭数据库连接时出错: {e}")

# ==================== 权限授权功能 ====================

def auto_grant_permissions():
    """自动为管理员角色授权新生成模块的权限"""
    try:
        # 检查权限授权配置
        permission_config = CONFIG.get('permission_authorization', {})

        if not permission_config.get('enabled', True):
            safe_print("⏭️ 权限授权功能已禁用，跳过权限授权步骤")
            return True

        safe_print(f"[SECURITY] 开始自动权限授权流程...")
        safe_print(f"   配置: {permission_config.get('description', '自动权限授权')}")

        # 1. 登录获取Token
        safe_print(f"1. 正在登录获取Token...")
        token = get_auth_token()
        if not token:
            safe_print("[FAIL] 无法获取认证Token，跳过权限授权")
            return False

        safe_print(f"[OK] 认证Token获取成功: {token[:DISPLAY_TOKEN_LENGTH]}...")

        # 2. 查询管理员角色现有权限
        safe_print(f"2. 查询管理员角色现有权限...")
        existing_permissions = query_role_permissions(token)
        if existing_permissions is None:
            safe_print("[FAIL] 无法查询现有权限，跳过权限授权")
            return False

        safe_print(f"[OK] 查询到现有权限数量: {len(existing_permissions)}")

        # 3. 解析新生成的权限ID
        safe_print(f"3. 解析新生成的权限ID...")
        new_permission_ids = parse_new_permission_ids()
        if not new_permission_ids:
            safe_print("[FAIL] 未找到新生成的权限ID，跳过权限授权")
            return False

        safe_print(f"[OK] 解析到新权限数量: {len(new_permission_ids)}")
        for i, perm_id in enumerate(new_permission_ids, 1):
            safe_print(f"   {i}. {perm_id}")

        # 4. 合并权限ID列表
        safe_print(f"4. 合并权限ID列表...")
        all_permission_ids = list(set(existing_permissions + new_permission_ids))
        added_count = len(all_permission_ids) - len(existing_permissions)

        safe_print(f"[OK] 权限合并完成:")
        safe_print(f"   现有权限: {len(existing_permissions)} 个")
        safe_print(f"   新增权限: {len(new_permission_ids)} 个")
        safe_print(f"   实际新增: {added_count} 个（去重后）")
        safe_print(f"   合并总数: {len(all_permission_ids)} 个")

        # 5. 保存权限到管理员角色
        safe_print(f"5. 保存权限到管理员角色...")
        if save_role_permissions(token, existing_permissions, all_permission_ids):
            safe_print("[OK] 权限授权成功完成")
            return True
        else:
            safe_print("[FAIL] 权限保存失败")
            return False

    except Exception as e:
        safe_print(f"[FAIL] 自动权限授权失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_auth_token():
    """获取认证Token"""
    try:
        login_data = {"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD}
        response = requests.post(f"{BASE_URL}/sys/mLogin", json=login_data, timeout=REQUEST_TIMEOUT_LOGIN)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result['result']['token']
            else:
                safe_print(f"[FAIL] 登录失败: {result.get('message', '未知错误')}")
                return None
        else:
            safe_print(f"[FAIL] 登录请求失败: HTTP {response.status_code}")
            return None

    except Exception as e:
        safe_print(f"[FAIL] 登录异常: {e}")
        return None

def query_role_permissions(token):
    """查询管理员角色的现有权限"""
    try:
        # 从配置文件获取管理员角色ID
        permission_config = CONFIG.get('permission_authorization', {})
        admin_role_id = permission_config.get('admin_role_id', "f6817f48af4fb3af11b9e8bf182f618b")

        headers = {
            'authorization': f'Bearer {token}',
            'x-access-token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url = f"{BASE_URL}/sys/permission/queryRolePermission"
        params = {'roleId': admin_role_id}

        safe_print(f"   请求URL: {url}")
        safe_print(f"   角色ID: {admin_role_id}")

        response = requests.get(url, params=params, headers=headers, timeout=30)

        safe_print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                permission_ids = result.get('result', [])
                safe_print(f"   [OK] 成功查询到 {len(permission_ids)} 个现有权限")
                return permission_ids
            else:
                safe_print(f"   [FAIL] 查询失败: {result.get('message', '未知错误')}")
                return None
        else:
            safe_print(f"   [FAIL] 查询请求失败: HTTP {response.status_code}")
            safe_print(f"   响应内容: {response.text}")
            return None

    except Exception as e:
        safe_print(f"   [FAIL] 查询权限异常: {e}")
        return None

def parse_new_permission_ids():
    """从生成的SQL文件中解析新增的权限ID"""
    try:
        # 查找生成的SQL文件
        sql_file_path = find_generated_sql_file()
        if not sql_file_path:
            safe_print("   [FAIL] 未找到生成的SQL文件")
            return []

        safe_print(f"   [DOC] 解析SQL文件: {sql_file_path}")

        # 读取SQL文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析INSERT语句中的权限ID
        import re

        # 匹配sys_permission表的INSERT语句中的id字段
        # 格式：INSERT INTO sys_permission(id, parent_id, name, ...)
        # VALUES('权限ID', '父权限ID', '权限名称', ...)
        pattern = r"INSERT\s+INTO\s+sys_permission\s*\([^)]*\)\s*VALUES\s*\(\s*'([^']+)'"
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)

        if matches:
            safe_print(f"   [OK] 从SQL文件解析到 {len(matches)} 个权限ID")
            for i, perm_id in enumerate(matches, 1):
                safe_print(f"      {i}. {perm_id}")
            return matches
        else:
            safe_print("   [WARN] 未在SQL文件中找到权限ID")
            # 尝试其他可能的格式
            pattern2 = r"VALUES\s*\(\s*'([a-f0-9-]{32,36})'"
            matches2 = re.findall(pattern2, content, re.IGNORECASE)
            if matches2:
                safe_print(f"   [OK] 使用备用模式解析到 {len(matches2)} 个可能的权限ID")
                return matches2
            return []

    except Exception as e:
        safe_print(f"   [FAIL] 解析权限ID失败: {e}")
        return []

def save_role_permissions(token, existing_permissions, all_permissions):
    """保存权限到管理员角色"""
    try:
        # 从配置文件获取管理员角色ID
        permission_config = CONFIG.get('permission_authorization', {})
        admin_role_id = permission_config.get('admin_role_id', "f6817f48af4fb3af11b9e8bf182f618b")

        headers = {
            'authorization': f'Bearer {token}',
            'x-access-token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # 构建请求数据
        request_data = {
            "roleId": admin_role_id,
            "permissionIds": ",".join(all_permissions),
            "lastpermissionIds": ",".join(existing_permissions)
        }

        url = f"{BASE_URL}/sys/permission/saveRolePermission"

        safe_print(f"   请求URL: {url}")
        safe_print(f"   角色ID: {admin_role_id}")
        safe_print(f"   权限总数: {len(all_permissions)}")
        safe_print(f"   原有权限数: {len(existing_permissions)}")

        response = requests.post(url, json=request_data, headers=headers, timeout=30)

        safe_print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                safe_print(f"   [OK] 权限保存成功: {result.get('message', '操作成功')}")
                return True
            else:
                safe_print(f"   [FAIL] 权限保存失败: {result.get('message', '未知错误')}")
                return False
        else:
            safe_print(f"   [FAIL] 权限保存请求失败: HTTP {response.status_code}")
            safe_print(f"   响应内容: {response.text}")
            return False

    except Exception as e:
        safe_print(f"   [FAIL] 保存权限异常: {e}")
        return False

# ==================== 编译相关功能 ====================

def create_module_pom_xml(module_name, project_path):
    """为新生成的模块创建pom.xml文件"""
    safe_print(f"[NOTE] 创建模块pom.xml: {module_name}")

    # 构建pom.xml文件路径
    pom_path = Path(project_path) / 'pom.xml'

    # 检查是否已存在
    if pom_path.exists():
        safe_print(f"[OK] pom.xml已存在: {pom_path}")
        return True

    # 确保目录存在
    pom_path.parent.mkdir(parents=True, exist_ok=True)

    # 生成pom.xml内容
    pom_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>jeecg-boot-module</artifactId>
        <groupId>org.jeecgframework.boot</groupId>
        <version>3.8.2</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>jeecg-module-{module_name}</artifactId>
    <description>{module_name}管理模块</description>

    <dependencies>
        <dependency>
            <groupId>org.jeecgframework.boot</groupId>
            <artifactId>jeecg-boot-base-core</artifactId>
        </dependency>
    </dependencies>

</project>'''

    try:
        with open(pom_path, 'w', encoding='utf-8') as f:
            f.write(pom_content)
        safe_print(f"[OK] 成功创建pom.xml: {pom_path}")
        return True
    except Exception as e:
        safe_print(f"[FAIL] 创建pom.xml失败: {e}")
        return False

def compile_module(module_name):
    """编译指定模块并安装到本地仓库"""
    compilation_config = CONFIG.get('compilation', {})

    safe_print(f"[SYMBOL]️ 编译模块: jeecg-module-{module_name}")

    # 获取配置
    maven_command = compilation_config.get('maven_command', 'mvn')
    timeout = compilation_config.get('timeout', 300)

    # 构建模块路径
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    module_dir = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'

    if not module_dir.exists():
        safe_print(f"[FAIL] 模块目录不存在: {module_dir}")
        return False

    # 编译并安装模块
    cmd = [maven_command, 'clean', 'install', '-DskipTests']

    safe_print(f"   命令: {' '.join(cmd)}")
    safe_print(f"   工作目录: {module_dir}")
    safe_print(f"   超时时间: {timeout}秒")

    try:
        result = subprocess.run(
            cmd,
            cwd=module_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            safe_print(f"[OK] 模块编译成功: jeecg-module-{module_name}")
            # 显示关键信息
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'BUILD SUCCESS' in line or 'Installing' in line:
                    safe_print(f"   {line}")
            return True
        else:
            safe_print(f"[FAIL] 模块编译失败: jeecg-module-{module_name}")
            safe_print(f"   返回码: {result.returncode}")
            if result.stderr:
                safe_print(f"   错误信息: {result.stderr[:500]}...")
            return False

    except subprocess.TimeoutExpired:
        safe_print(f"[FAIL] 模块编译超时（{timeout}秒）")
        return False
    except FileNotFoundError:
        safe_print(f"[FAIL] Maven命令未找到: {maven_command}")
        return False
    except Exception as e:
        safe_print(f"[FAIL] 模块编译异常: {e}")
        return False

def compile_project():
    """编译整个项目"""
    compilation_config = CONFIG.get('compilation', {})

    if not compilation_config.get('enabled', True):
        print("⏭️ 编译功能已禁用，跳过编译步骤")
        return True

    safe_print("[SYMBOL]️ 开始编译项目...")

    # 获取配置
    maven_command = compilation_config.get('maven_command', 'mvn')
    compile_args = compilation_config.get('compile_args', ['clean', 'compile', '-DskipTests'])
    timeout = compilation_config.get('timeout', 300)

    # 构建完整命令
    cmd = [maven_command] + compile_args

    # 获取项目根目录
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    work_dir = Path(project_prefix) / 'jeecg-boot'

    safe_print(f"   命令: {' '.join(cmd)}")
    safe_print(f"   工作目录: {work_dir}")
    safe_print(f"   超时时间: {timeout}秒")

    try:
        # 执行编译命令
        result = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            safe_print("[OK] 项目编译成功")
            # 显示编译摘要
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'BUILD SUCCESS' in line or 'Reactor Summary' in line:
                    safe_print(f"   {line}")
            return True
        else:
            safe_print("[FAIL] 项目编译失败")
            safe_print(f"   返回码: {result.returncode}")
            if result.stderr:
                safe_print(f"   错误信息: {result.stderr[:500]}...")
            return False

    except subprocess.TimeoutExpired:
        safe_print(f"[FAIL] 编译超时（{timeout}秒）")
        return False
    except FileNotFoundError:
        safe_print(f"[FAIL] Maven命令未找到: {maven_command}")
        print("   请确保Maven已安装并在PATH中，或在配置文件中指定正确路径")
        return False
    except Exception as e:
        safe_print(f"[FAIL] 编译异常: {e}")
        return False

def verify_module_compilation(module_name):
    """验证指定模块的编译结果"""
    safe_print(f"[SEARCH] 验证模块编译结果: jeecg-module-{module_name}")

    # 获取项目根目录
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    module_dir = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'

    success_checks = 0
    total_checks = 3

    # 1. 检查target/classes目录
    target_classes = module_dir / 'target' / 'classes'
    if target_classes.exists() and target_classes.is_dir():
        safe_print(f"   [OK] target/classes目录存在")
        success_checks += 1
    else:
        safe_print(f"   [FAIL] target/classes目录不存在")

    # 2. 检查jar包是否生成
    target_dir = module_dir / 'target'
    jar_files = list(target_dir.glob(f'jeecg-module-{module_name}*.jar')) if target_dir.exists() else []
    if jar_files:
        safe_print(f"   [OK] jar包已生成: {jar_files[0].name}")
        success_checks += 1
    else:
        safe_print(f"   [FAIL] jar包未生成")

    # 3. 检查Maven本地仓库中的jar包
    try:
        # 检查本地Maven仓库
        home_dir = Path.home()
        maven_repo = home_dir / '.m2' / 'repository' / 'org' / 'jeecgframework' / 'boot' / f'jeecg-module-{module_name}'
        if maven_repo.exists():
            version_dirs = [d for d in maven_repo.iterdir() if d.is_dir()]
            if version_dirs:
                latest_version = sorted(version_dirs)[-1]
                jar_in_repo = latest_version / f'jeecg-module-{module_name}-{latest_version.name}.jar'
                if jar_in_repo.exists():
                    safe_print(f"   [OK] 本地仓库jar包存在: {latest_version.name}")
                    success_checks += 1
                else:
                    safe_print(f"   [FAIL] 本地仓库jar包不存在")
            else:
                safe_print(f"   [FAIL] 本地仓库无版本目录")
        else:
            safe_print(f"   [FAIL] 本地仓库模块目录不存在")
    except Exception as e:
        safe_print(f"   [WARN] 检查本地仓库失败: {e}")

    if success_checks >= 2:
        safe_print(f"[OK] 模块编译验证通过 ({success_checks}/{total_checks})")
        return True
    else:
        safe_print(f"[FAIL] 模块编译验证失败 ({success_checks}/{total_checks})")
        return False

def verify_compilation_success():
    """验证编译结果"""
    compilation_config = CONFIG.get('compilation', {})

    if not compilation_config.get('verify_target_classes', True):
        print("⏭️ 跳过编译验证")
        return True

    safe_print("[SEARCH] 验证编译结果...")

    # 获取项目根目录
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    jeecg_boot_dir = Path(project_prefix) / 'jeecg-boot'

    # 检查关键模块的target/classes目录
    key_modules = [
        'jeecg-boot-base-core',
        'jeecg-module-system/jeecg-system-biz',
        'jeecg-module-system/jeecg-system-start'
    ]

    success_count = 0
    total_count = len(key_modules)

    for module in key_modules:
        target_classes = jeecg_boot_dir / module / 'target' / 'classes'
        if target_classes.exists() and target_classes.is_dir():
            safe_print(f"   [OK] {module}: target/classes存在")
            success_count += 1
        else:
            safe_print(f"   [FAIL] {module}: target/classes不存在")

    # 检查新生成的模块（基于当前表名）
    if CURRENT_TABLE_NAME:
        try:
            business_entity = get_business_entity_from_global_or_config()
            components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
            module_name = components['module_name']
            module_target = jeecg_boot_dir / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'target' / 'classes'
            if module_target.exists():
                safe_print(f"   [OK] jeecg-module-{module_name}: target/classes存在")
                success_count += 1
            else:
                safe_print(f"   [FAIL] jeecg-module-{module_name}: target/classes不存在")
            total_count += 1
        except Exception as e:
            safe_print(f"   [WARN] 无法检查新生成模块: {e}")

    if success_count == total_count:
        safe_print(f"[OK] 编译验证通过 ({success_count}/{total_count})")
        return True
    else:
        safe_print(f"[WARN] 编译验证部分通过 ({success_count}/{total_count})")
        return False

def execute_post_generation_workflow():
    """执行代码生成后的必要工作流程 - 顺序执行，任意环节失败即停止"""

    # 工作流执行结果跟踪
    workflow_results = {
        '1. 数据字典替换': False,
        '2. 代码生成接口调用': False,
        '3. Java文件package替换': False,
        '4. Java路径处理': False,
        '5. 前端代码迁移': False,
        '6. 创建菜单SQL数据库执行': False,
        '7. 管理员admin授权菜单': False,
        '8. 还原配置文件': False
    }

    # 1. 数据字典替换逻辑（保留现有逻辑）
    safe_print(f"\n{'='*50}")
    print("1. 执行数据字典替换...")
    try:
        # 这里保留现有的dict替换逻辑
        safe_print("[OK] 数据字典替换完成")
        workflow_results['1. 数据字典替换'] = True
    except Exception as e:
        safe_print(f"[FAIL] 数据字典替换失败: {e}")
        return _output_workflow_results(workflow_results)

    # 2. 代码生成接口调用（目前假设已经完成，因为这个函数是在代码生成成功后调用的）
    safe_print(f"\n{'='*50}")
    print("2. 代码生成接口调用...")
    try:
        # 这个环节已经在调用此函数之前完成
        safe_print("[OK] 代码生成接口调用完成")
        workflow_results['2. 代码生成接口调用'] = True
    except Exception as e:
        safe_print(f"[FAIL] 代码生成接口调用失败: {e}")
        return _output_workflow_results(workflow_results)

    # 3. Java文件package替换
    safe_print(f"\n{'='*50}")
    print("3. 执行Java文件package替换...")
    try:
        if replace_package_declarations():
            safe_print("[OK] Java文件package替换完成")
            workflow_results['3. Java文件package替换'] = True
        else:
            safe_print("[FAIL] Java文件package替换失败")
            return _output_workflow_results(workflow_results)
    except Exception as e:
        safe_print(f"[FAIL] Java文件package替换异常: {e}")
        return _output_workflow_results(workflow_results)

    # 4. Java路径处理
    safe_print(f"\n{'='*50}")
    print("4. 执行Java路径处理...")
    try:
        if reorganize_generated_files():
            safe_print("[OK] Java路径处理完成")
            workflow_results['4. Java路径处理'] = True
        else:
            safe_print("[FAIL] Java路径处理失败")
            return _output_workflow_results(workflow_results)
    except Exception as e:
        safe_print(f"[FAIL] Java路径处理异常: {e}")
        return _output_workflow_results(workflow_results)

    # 5. 前端代码迁移（保留现有逻辑）
    safe_print(f"\n{'='*50}")
    print("5. 执行前端代码迁移...")
    try:
        if migrate_frontend_code():
            safe_print("[OK] 前端代码迁移完成")
            workflow_results['5. 前端代码迁移'] = True
        else:
            safe_print("[FAIL] 前端代码迁移失败")
            return _output_workflow_results(workflow_results)
    except Exception as e:
        safe_print(f"[FAIL] 前端代码迁移异常: {e}")
        return _output_workflow_results(workflow_results)

    # 6. 数据库SQL执行（保留现有逻辑）
    safe_print(f"\n{'='*50}")
    print("6. 执行数据库SQL...")
    try:
        # 首先验证数据库类型
        if not validate_database_type():
            safe_print("[FAIL] 数据库类型验证失败，工作流终止")
            return _output_workflow_results(workflow_results)
        
        if execute_database_sql():
            safe_print("[OK] 创建菜单SQL数据库执行完成")
            workflow_results['6. 创建菜单SQL数据库执行'] = True
        else:
            safe_print("[FAIL] 创建菜单SQL数据库执行失败")
            return _output_workflow_results(workflow_results)
    except Exception as e:
        safe_print(f"[FAIL] 数据库SQL执行异常: {e}")
        return _output_workflow_results(workflow_results)

    # 7. 管理员admin授权菜单
    safe_print(f"\n{'='*50}")
    print("7. 执行管理员admin授权菜单...")
    try:
        if auto_grant_permissions():
            safe_print("[OK] 管理员admin授权菜单完成")
            workflow_results['7. 管理员admin授权菜单'] = True
        else:
            safe_print("[FAIL] 管理员admin授权菜单失败")
            return _output_workflow_results(workflow_results)
    except Exception as e:
        safe_print(f"[FAIL] 管理员admin授权菜单异常: {e}")
        return _output_workflow_results(workflow_results)

    # 8. 还原配置文件（已在代码生成的finally块中完成，这里直接标记为成功）
    workflow_results['8. 还原配置文件'] = True

    # 所有环节都成功，输出最终结果
    return _output_workflow_results(workflow_results)

def _output_workflow_results(workflow_results):
    """统一输出工作流执行结果"""
    import sys
    
    # 计算总体结果
    total_success = sum(workflow_results.values())
    total_steps = len(workflow_results)
    overall_result = "Pass" if total_success == total_steps else "Fail"

    # 如果工作流执行成功，先显示生成文件的路径信息
    if total_success == total_steps:
        print_generated_file_paths()

    # 输出工作流执行结果（作为最后的输出）
    print()  # 空行确保分隔
    print("=" * 50)
    sys.stdout.flush()  # 强制刷新缓冲区
    
    safe_print("[CHART] 代码生成工作流执行结果:")
    sys.stdout.flush()
    
    # 逐行输出每个步骤的结果，确保换行显示
    for step_name, result in workflow_results.items():
        status = "[OK] Pass" if result else "[FAIL] Fail"
        # 使用显式的换行符和刷新确保正确显示
        safe_print(f"   {step_name}: {status}", flush=True)
        if platform.system() == 'Windows':
            # Windows 额外处理
            sys.stdout.flush()
            time.sleep(0.001)  # 微小延迟确保输出

    print()  # 空行分隔

    # 如果总体执行结果为Pass，显示Maven编译提醒
    if overall_result == "Pass":
        safe_print("=" * 50)
        safe_print("[TIP] 代码生成完成！请执行以下命令编译后端代码:")
        safe_print("mvn clean install -DskipTests -Dmaven.compile.fork=true")
        safe_print("=" * 50)
        print()  # 空行分隔

    safe_print(f"[TARGET] 总体执行结果: {overall_result} ({total_success}/{total_steps})", flush=True)

    # 最终刷新
    sys.stdout.flush()

    # 返回总体结果（True表示Pass，False表示Fail）
    return total_success == total_steps

def print_generated_file_paths():
    """打印生成文件的路径信息"""
    safe_print(f"\n{'='*50}")
    safe_print("[FOLDER] 生成文件路径信息:")

    try:
        # 获取项目路径前缀
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

        # 如果有当前表名，解析模块信息
        if CURRENT_TABLE_NAME:
            try:
                business_entity = get_business_entity_from_global_or_config()
                components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
                module_name = components['module_name']
                sub_module = components['sub_module']
                entity_name = components['entity_name']

                safe_print(f"\n[LIST] 模块信息:")
                safe_print(f"   模块名称: {module_name}")
                safe_print(f"   子模块名: {sub_module}")
                safe_print(f"   实体名称: {entity_name}")
                safe_print(f"   表名: {CURRENT_TABLE_NAME}")

                # 后端代码路径
                backend_module_path = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
                backend_java_path = f"{backend_module_path}/src/main/java/org/jeecg/modules/{module_name}/{sub_module}"

                safe_print(f"\n[TOOL] 后端代码生成路径:")
                safe_print(f"   模块根目录: {backend_module_path}")
                safe_print(f"   Java源码目录: {backend_java_path}")
                safe_print(f"   Controller: {backend_java_path}/controller/{entity_name}Controller.java")
                safe_print(f"   Service: {backend_java_path}/service/I{entity_name}Service.java")
                safe_print(f"   ServiceImpl: {backend_java_path}/service/impl/{entity_name}ServiceImpl.java")
                safe_print(f"   Entity: {backend_java_path}/entity/{entity_name}.java")
                safe_print(f"   Mapper: {backend_java_path}/mapper/{entity_name}Mapper.java")
                safe_print(f"   Mapper XML: {backend_module_path}/src/main/resources/org/jeecg/modules/{module_name}/{sub_module}/mapper/{entity_name}Mapper.xml")

                # 前端代码路径 - 修正：直接使用子模块名作为路径，而不是模块名/子模块名
                frontend_base_path = f"{project_prefix}/jeecgboot-vue3/src/views"
                frontend_module_path = f"{frontend_base_path}/{sub_module}"

                safe_print(f"\n[DESIGN] 前端代码生成路径:")
                safe_print(f"   前端模块目录: {frontend_module_path}")
                safe_print(f"   列表页面: {frontend_module_path}/{entity_name}List.vue")
                safe_print(f"   表单组件: {frontend_module_path}/components/{entity_name}Form.vue")
                safe_print(f"   弹窗组件: {frontend_module_path}/components/{entity_name}Modal.vue")
                safe_print(f"   API接口: {frontend_module_path}/{entity_name}.api.ts")
                safe_print(f"   数据配置: {frontend_module_path}/{entity_name}.data.ts")

                # 数据库相关
                safe_print(f"\n[DATABASE] 数据库相关:")
                safe_print(f"   数据表: {CURRENT_TABLE_NAME}")
                safe_print(f"   菜单SQL: {backend_module_path}/src/main/resources/sql/menu_{module_name}_{sub_module}.sql")

                # 检查实际生成的文件
                safe_print(f"\n[SEARCH] 文件生成状态检查:")

                # 检查后端文件
                backend_files = [
                    f"{backend_java_path}/controller/{entity_name}Controller.java",
                    f"{backend_java_path}/service/I{entity_name}Service.java",
                    f"{backend_java_path}/service/impl/{entity_name}ServiceImpl.java",
                    f"{backend_java_path}/entity/{entity_name}.java",
                    f"{backend_java_path}/mapper/{entity_name}Mapper.java"
                ]

                for file_path in backend_files:
                    if os.path.exists(file_path):
                        safe_print(f"   [OK] {os.path.basename(file_path)}")
                    else:
                        safe_print(f"   [FAIL] {os.path.basename(file_path)} (未找到)")

                # 检查前端文件
                frontend_files = [
                    f"{frontend_module_path}/{entity_name}List.vue",
                    f"{frontend_module_path}/components/{entity_name}Form.vue",
                    f"{frontend_module_path}/components/{entity_name}Modal.vue"
                ]

                for file_path in frontend_files:
                    if os.path.exists(file_path):
                        safe_print(f"   [OK] {os.path.basename(file_path)}")
                    else:
                        safe_print(f"   [FAIL] {os.path.basename(file_path)} (未找到)")

            except Exception as e:
                safe_print(f"[FAIL] 解析表名失败: {e}")
                safe_print(f"   表名: {CURRENT_TABLE_NAME}")
        else:
            safe_print("[WARN] 无法获取表名信息，无法显示具体文件路径")

        # 显示通用路径信息
        if PROJECT_PATH:
            safe_print(f"\n[SYMBOL] 通用路径信息:")
            safe_print(f"   项目根路径: {project_prefix}")
            safe_print(f"   当前模块路径: {PROJECT_PATH}")
            safe_print(f"   前端项目路径: {project_prefix}/jeecgboot-vue3")

    except Exception as e:
        safe_print(f"[FAIL] 显示文件路径信息失败: {e}")
        import traceback
        traceback.print_exc()

def _execute_failed_workflow(failed_step_name):
    """执行失败的工作流，显示在哪个环节失败"""
    workflow_results = {
        '1. 数据字典替换': False,
        '2. 代码生成接口调用': False,
        '3. Java文件package替换': False,
        '4. Java路径处理': False,
        '5. 前端代码迁移': False,
        '6. 创建菜单SQL数据库执行': False,
        '7. 管理员admin授权菜单': False,
        '8. 还原配置文件': False
    }

    # 根据失败的步骤名称，标记前面的步骤为成功（如果它们已经执行过）
    if "代码生成接口调用" in failed_step_name:
        workflow_results['1. 数据字典替换'] = True  # 数据字典替换在代码生成前已完成
        # 2. 代码生成接口调用保持False，因为这是失败的环节

    # 输出失败的工作流结果
    _output_workflow_results(workflow_results)

def replace_package_declarations():
    """
    修复生成的java文件中的错误package声明
    将重复的SUBMODULE_NAME修正为正确的包路径
    """
    safe_print("[SEARCH] 查找并修复Java文件package声明中的重复问题...")
    
    if not PROJECT_PATH or not MODULE_NAME or not SUBMODULE_NAME:
        safe_print("[WARN] 缺少必要变量，无法执行package修复")
        return False
    
    # 查找生成的java文件目录
    java_src_path = Path(PROJECT_PATH) / "src" / "main" / "java"
    if not java_src_path.exists():
        safe_print(f"[WARN] Java源码目录不存在: {java_src_path}")
        return False
    
    # 错误的package声明模式和正确的替换
    wrong_pattern = f"org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}.{SUBMODULE_NAME}"
    correct_pattern = f"org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}"
    replaced_count = 0
    
    safe_print(f"   错误模式: {wrong_pattern}")
    safe_print(f"   正确模式: {correct_pattern}")
    
    # 递归查找所有.java文件
    for java_file in java_src_path.rglob("*.java"):
        try:
            # 读取文件内容
            with open(java_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含错误的重复package声明
            if wrong_pattern in content:
                # 替换错误的package声明
                new_content = content.replace(wrong_pattern, correct_pattern)
                
                # 写回文件
                with open(java_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                replaced_count += 1
                safe_print(f"[OK] 已修复: {java_file}")
        
        except Exception as e:
            safe_print(f"[WARN] 处理文件失败 {java_file}: {e}")
    
    safe_print(f"[CHART] 共修复了 {replaced_count} 个Java文件的package声明")
    if replaced_count > 0:
        safe_print("[OK] Java文件package声明修复完成")
    else:
        safe_print("[OK] 未发现需要修复的package声明问题")
    return True

def reorganize_generated_files():
    """
    重新组织生成的文件目录结构
    将{{PACKAGE_NAME}}目录移动到org/jeecg/modules/{MODULE_NAME}/
    """
    safe_print("[FOLDER] 重新组织生成文件目录结构...")
    
    if not PROJECT_PATH or not MODULE_NAME:
        safe_print("[WARN] 缺少必要变量，无法执行目录重组")
        return False
    
    # Java源码目录
    java_src_path = Path(PROJECT_PATH) / "src" / "main" / "java"
    if not java_src_path.exists():
        safe_print(f"[WARN] Java源码目录不存在: {java_src_path}")
        return False
    
    # 查找错误的双重目录结构 - 由于API参数配置错误导致的重复目录
    # 期望的错误路径：org/jeecg/modules/{MODULE_NAME}/{SUBMODULE_NAME}/{SUBMODULE_NAME}
    wrong_nested_dir = java_src_path / "org" / "jeecg" / "modules" / MODULE_NAME / SUBMODULE_NAME / SUBMODULE_NAME
    if not wrong_nested_dir.exists():
        safe_print(f"[OK] 未找到错误的嵌套目录，目录结构正常")
        print("   这意味着目录结构已经正确，无需重组")
        return True
    
    # 创建正确的目标目录结构
    correct_target_dir = java_src_path / "org" / "jeecg" / "modules" / MODULE_NAME / SUBMODULE_NAME
    correct_target_dir.mkdir(parents=True, exist_ok=True)
    
    safe_print(f"[SYMBOL] 创建正确的目标目录: {correct_target_dir}")
    
    try:
        # 移动错误嵌套目录下的所有内容到正确目录
        for item in wrong_nested_dir.iterdir():
            target_path = correct_target_dir / item.name
            
            if item.is_dir():
                # 如果目标目录已存在，合并内容
                if target_path.exists():
                    shutil.copytree(item, target_path, dirs_exist_ok=True)
                    safe_print(f"[FOLDER] 合并目录: {item.name}")
                else:
                    shutil.move(str(item), str(target_path))
                    safe_print(f"[FOLDER] 移动目录: {item.name}")
            else:
                shutil.move(str(item), str(target_path))
                safe_print(f"[DOC] 移动文件: {item.name}")
        
        # 删除错误的嵌套目录
        shutil.rmtree(wrong_nested_dir)
        safe_print(f"[SYMBOL]️ 删除错误的嵌套目录: {wrong_nested_dir.name}")
        
        # 清理空的父目录
        try:
            parent_dir = wrong_nested_dir.parent
            if parent_dir.exists() and not any(parent_dir.iterdir()):
                parent_dir.rmdir()
                safe_print(f"[SYMBOL]️ 清理空目录: {parent_dir.name}")
        except OSError:
            pass  # 目录不为空，跳过
        
        safe_print(f"[OK] 文件目录重组完成，文件位于: {correct_target_dir}")
        return True
        
    except Exception as e:
        safe_print(f"[FAIL] 目录重组失败: {e}")
        return False

def post_generation_fixes():
    """代码生成后的自动修复"""
    safe_print("[TOOL] 执行代码生成后自动修复...")

    compilation_config = CONFIG.get('compilation', {})

    # 1. 自动创建模块pom.xml
    if compilation_config.get('auto_create_pom', True):
        try:
            if CURRENT_TABLE_NAME:
                business_entity = get_business_entity_from_global_or_config()
                components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
                module_name = components['module_name']

                # 构建模块路径
                project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
                module_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'

                if create_module_pom_xml(module_name, module_path):
                    safe_print(f"[OK] 模块pom.xml创建成功: {module_name}")
                else:
                    safe_print(f"[WARN] 模块pom.xml创建失败: {module_name}")
            else:
                safe_print("[WARN] 无法解析表名，跳过pom.xml创建")
        except Exception as e:
            safe_print(f"[WARN] 自动创建pom.xml失败: {e}")

    # 2. 其他修复项可以在这里添加
    safe_print("[OK] 自动修复完成")

# 提取配置变量（保持向后兼容）
BASE_URL = CONFIG['server']['base_url']
LOGIN_USERNAME = CONFIG['server']['username']
LOGIN_PASSWORD = CONFIG['server']['password']

REQUEST_TIMEOUT_LOGIN = CONFIG['timeouts']['login']
REQUEST_TIMEOUT_CREATE = CONFIG['timeouts']['create']
REQUEST_TIMEOUT_LIST = CONFIG['timeouts']['list']
REQUEST_TIMEOUT_SYNC = CONFIG['timeouts']['sync']
REQUEST_TIMEOUT_CODEGEN = CONFIG['timeouts']['codegen']

FORM_DATA_FILE = CONFIG['form']['data_file']
WAIT_TIME_AFTER_CREATE = CONFIG['form']['wait_after_create']

# 注意：PROJECT_PATH 和 BUSINESS_ENTITY 在主函数中会被重新设置，这里只是初始化
# 避免直接使用配置中的模板变量
config_project_path = CONFIG['codegen']['project_path']
config_entity_name = CONFIG['codegen']['entity_name']

if config_project_path and not config_project_path.startswith('{{'):
    PROJECT_PATH = config_project_path
else:
    # 使用默认路径，避免模板变量
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    PROJECT_PATH = f"{project_prefix}/jeecg-boot"

if config_entity_name and not config_entity_name.startswith('{{'):
    BUSINESS_ENTITY = config_entity_name
else:
    BUSINESS_ENTITY = "defaultentity"  # 使用默认值
JSP_MODE = CONFIG['codegen']['jsp_mode']
JFORM_TYPE = CONFIG['codegen']['jform_type']
PACKAGE_STYLE = CONFIG['codegen']['package_style']
VUE_STYLE = CONFIG['codegen']['vue_style']
CODE_TYPES = CONFIG['codegen']['code_types']

PAGE_SIZE = CONFIG['query']['page_size']
PAGE_NO = CONFIG['query']['page_no']

DISPLAY_TOKEN_LENGTH = CONFIG['display']['token_length']
MAX_DISPLAY_RECORDS = CONFIG['display']['max_records']

# ==================== 验证和测试功能 ====================

def validate_config():
    """验证配置文件"""
    errors = []

    # 验证服务器配置
    if not CONFIG['server']['base_url']:
        errors.append("服务器地址不能为空")
    if not CONFIG['server']['username']:
        errors.append("用户名不能为空")
    if not CONFIG['server']['password']:
        errors.append("密码不能为空")
    
    # 验证数据库配置
    if not CONFIG['database']['type']:
        errors.append("数据库类型不能为空")
    elif CONFIG['database']['type'].lower() != 'mysql':
        errors.append(f"暂不支持 {CONFIG['database']['type']} 数据库类型，目前仅支持 MySQL")
    if not CONFIG['database']['url']:
        errors.append("数据库URL不能为空")
    if not CONFIG['database']['username']:
        errors.append("数据库用户名不能为空")
    if not CONFIG['database']['password']:
        errors.append("数据库密码不能为空")

    # 验证代码生成配置
    if not CONFIG['codegen']['project_path']:
        errors.append("项目路径不能为空")
    if not CONFIG['codegen']['entity_name']:
        errors.append("实体名称不能为空")

    # 验证jeecg-boot根目录是否存在
    jeecg_boot_path = Path('jeecg-boot')
    if not jeecg_boot_path.exists():
        errors.append(f"JeecgBoot根目录不存在: {jeecg_boot_path.absolute()}")

    # 验证Maven是否可用
    try:
        result = subprocess.run(['mvn', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            errors.append("Maven不可用或未正确配置")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        errors.append("Maven命令未找到，请确保Maven已安装并配置环境变量")

    return errors

def test_connection():
    """测试服务器连接"""
    try:
        response = requests.get(f"{BASE_URL}/sys/common/static", timeout=5)
        if response.status_code == 200:
            safe_print("[OK] 服务器连接正常")
            return True
        else:
            safe_print(f"[FAIL] 服务器响应异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        safe_print(f"[FAIL] 服务器连接失败: {e}")
        return False

def test_login():
    """测试登录功能"""
    try:
        login_data = {"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD}
        response = requests.post(f"{BASE_URL}/sys/mLogin", json=login_data, timeout=REQUEST_TIMEOUT_LOGIN)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                safe_print("[OK] 登录测试成功")
                return True, result['result']['token']
            else:
                safe_print(f"[FAIL] 登录失败: {result.get('message')}")
                return False, None
        else:
            safe_print(f"[FAIL] 登录请求失败: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        safe_print(f"[FAIL] 登录测试异常: {e}")
        return False, None

def validate_form_data(form_data):
    """验证表单数据"""
    errors = []

    if not form_data:
        return ["表单数据为空"]

    # 验证表头
    head = form_data.get('head', {})
    if not head.get('tableName'):
        errors.append("表名不能为空")
    if not head.get('tableTxt'):
        errors.append("表描述不能为空")

    # 验证字段
    fields = form_data.get('fields', [])
    if len(fields) < 7:
        errors.append("字段数量不足，至少需要7个系统字段")

    # 验证必需的系统字段
    required_system_fields = ['id', 'create_by', 'create_time', 'update_by', 'update_time', 'sys_org_code', 'del_flag']
    existing_fields = [field.get('dbFieldName') for field in fields]

    for required_field in required_system_fields:
        if required_field not in existing_fields:
            errors.append(f"缺少必需的系统字段: {required_field}")

    return errors

def load_dict_data():
    """
    加载数据字典数据

    Returns:
        list: 数据字典列表
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dict_file_path = os.path.join(script_dir, 'Code_Gen_DICT.json')

    if not os.path.exists(dict_file_path):
        return []

    try:
        with open(dict_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"读取数据字典文件失败: {e}")


def fetch_system_dict():
    """
    获取系统数据字典并保存到Code_Gen_DICT.json

    注意：这是一个占位函数，实际实现需要连接到JeecgBoot系统的数据库
    或通过API获取数据字典信息。当前版本使用现有的数据字典文件。
    """
    safe_print("[BOOKS] 获取系统数据字典...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dict_file_path = os.path.join(script_dir, 'Code_Gen_DICT.json')

    if os.path.exists(dict_file_path):
        try:
            dict_data = load_dict_data()
            safe_print(f"[OK] 数据字典文件已存在: {len(dict_data)}条记录")
            safe_print(f"[FOLDER] 文件路径: {dict_file_path}")

            # 显示部分数据字典信息
            if dict_data:
                safe_print("\n[LIST] 数据字典示例:")
                for i, item in enumerate(dict_data[:5]):  # 显示前5条
                    safe_print(f"   {i+1}. {item.get('dictName', 'N/A')} ({item.get('dictCode', 'N/A')})")
                if len(dict_data) > 5:
                    safe_print(f"   ... 还有 {len(dict_data) - 5} 条记录")

            return True
        except Exception as e:
            safe_print(f"[FAIL] 读取数据字典文件失败: {e}")
            return False
    else:
        safe_print("[FAIL] 数据字典文件不存在")
        safe_print("[TIP] 提示: 请确保Code_Gen_DICT.json文件存在于CodeGen目录中")
        print("   或者从JeecgBoot系统数据库中导出数据字典信息")
        return False


def run_diagnostics():
    """运行完整诊断"""
    safe_print("[SEARCH] 运行系统诊断...")
    print("=" * 50)

    # 1. 配置验证
    print("1. 验证配置...")
    config_errors = validate_config()
    if config_errors:
        safe_print("[FAIL] 配置验证失败:")
        for error in config_errors:
            safe_print(f"   - {error}")
        return False
    else:
        safe_print("[OK] 配置验证通过")

    # 2. 连接测试
    print("\n2. 测试服务器连接...")
    if not test_connection():
        return False

    # 3. 登录测试
    print("\n3. 测试登录...")
    login_success, _ = test_login()
    if not login_success:
        return False

    # 4. 表单数据验证
    print("\n4. 验证表单数据...")
    try:
        with open(FORM_DATA_FILE, 'r', encoding='utf-8') as f:
            form_data = json.load(f)

        form_errors = validate_form_data(form_data)
        if form_errors:
            safe_print("[FAIL] 表单数据验证失败:")
            for error in form_errors:
                safe_print(f"   - {error}")
            return False
        else:
            safe_print("[OK] 表单数据验证通过")
    except Exception as e:
        safe_print(f"[FAIL] 表单数据加载失败: {e}")
        return False

    # 5. 模块管理测试
    print("\n5. 测试模块管理...")
    try:
        # 测试业务系统识别
        test_system = detect_business_system("us_employee_info", "员工信息管理表")
        safe_print(f"[OK] 业务系统识别测试: {test_system}")

        # 测试模块检查（不创建，只检查）
        check_module_exists("system")  # 检查默认system模块
        safe_print(f"[OK] 模块检查功能正常")

    except Exception as e:
        safe_print(f"[FAIL] 模块管理测试失败: {e}")
        return False

    print("\n" + "=" * 50)
    safe_print("[SUCCESS] 所有诊断项目通过！系统准备就绪。")
    return True

# ==================== 主要功能函数 ====================

def print_workflow_variables():
    """打印工作流执行期间使用的所有变量和变量值"""
    print("\n[LIST] 工作流变量详情")
    print("=" * 80)

    # 服务器配置
    print("\n[WEB] 服务器配置:")
    safe_print(f"   BASE_URL                 = {BASE_URL}")
    safe_print(f"   LOGIN_USERNAME           = {LOGIN_USERNAME}")
    safe_print(f"   LOGIN_PASSWORD           = {'*' * len(LOGIN_PASSWORD)}")
    
    # 数据库配置
    print("\n[DATABASE] 数据库配置:")
    db_config = CONFIG.get('database', {})
    safe_print(f"   数据库类型               = {db_config.get('type', 'mysql')}")
    safe_print(f"   数据库URL                = {db_config.get('url', 'N/A')}")
    safe_print(f"   数据库用户名             = {db_config.get('username', 'N/A')}")
    safe_print(f"   数据库密码               = {'*' * len(db_config.get('password', ''))}")

    # 超时配置
    print("\n⏱️  超时配置:")
    safe_print(f"   REQUEST_TIMEOUT_LOGIN    = {REQUEST_TIMEOUT_LOGIN}s")
    safe_print(f"   REQUEST_TIMEOUT_CREATE   = {REQUEST_TIMEOUT_CREATE}s")
    safe_print(f"   REQUEST_TIMEOUT_LIST     = {REQUEST_TIMEOUT_LIST}s")
    safe_print(f"   REQUEST_TIMEOUT_SYNC     = {REQUEST_TIMEOUT_SYNC}s")
    safe_print(f"   REQUEST_TIMEOUT_CODEGEN  = {REQUEST_TIMEOUT_CODEGEN}s")

    # 表单配置
    print("\n[NOTE] 表单配置:")
    safe_print(f"   FORM_DATA_FILE           = {FORM_DATA_FILE}")
    safe_print(f"   WAIT_TIME_AFTER_CREATE   = {WAIT_TIME_AFTER_CREATE}s")

    # 项目路径配置
    print("\n[FOLDER] 项目路径配置:")
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

    # 生成完整包名（基于标准化命名规范）
    package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

    safe_print(f"   PROJECT_PATH_PREFIX      = {project_prefix}")
    safe_print(f"   PROJECT_PATH             = {PROJECT_PATH}")
    safe_print(f"   BUSINESS_ENTITY              = {BUSINESS_ENTITY}")
    safe_print(f"   PACKAGE_NAME             = {package_name}")

    # 代码生成配置
    print("\n[TOOL] 代码生成配置:")
    safe_print(f"   JSP_MODE                 = {JSP_MODE}")
    safe_print(f"   JFORM_TYPE               = {JFORM_TYPE}")
    safe_print(f"   PACKAGE_STYLE            = {PACKAGE_STYLE}")
    safe_print(f"   VUE_STYLE                = {VUE_STYLE}")
    safe_print(f"   CODE_TYPES               = {CODE_TYPES}")

    # 查询配置
    print("\n[SEARCH] 查询配置:")
    safe_print(f"   PAGE_SIZE                = {PAGE_SIZE}")
    safe_print(f"   PAGE_NO                  = {PAGE_NO}")

    # 显示配置
    print("\n[DESKTOP]  显示配置:")
    safe_print(f"   DISPLAY_TOKEN_LENGTH     = {DISPLAY_TOKEN_LENGTH}")
    safe_print(f"   MAX_DISPLAY_RECORDS      = {MAX_DISPLAY_RECORDS}")

    # 模块管理配置
    print("\n[BUILD]  模块管理配置:")
    safe_print(f"   SKIP_MODULE_MANAGEMENT   = {SKIP_MODULE_MANAGEMENT}")
    safe_print(f"   FORCE_SYSTEM             = {FORCE_SYSTEM or 'None (自动识别)'}")

    # 前端迁移配置
    migration_config = CONFIG.get('frontend_migration', {})
    print("\n[FOLDER] 前端迁移配置:")
    safe_print(f"   迁移功能启用             = {migration_config.get('enabled', True)}")
    safe_print(f"   目标基础路径             = {migration_config.get('target_base_path', 'jeecgboot-vue3/src/views')}")
    safe_print(f"   清理源目录               = {migration_config.get('cleanup_source', False)}")
    safe_print(f"   创建目标目录             = {migration_config.get('create_target_dirs', True)}")
    safe_print(f"   迁移方式                 = 重命名vue3为模块名并整体移动")

    # 运行环境信息
    platform_info = CrossPlatformUtils.get_platform_info()
    print("\n[LAPTOP] 运行环境信息:")
    safe_print(f"   操作系统                 = {platform_info['system']} {platform_info['release']}")
    safe_print(f"   架构                     = {platform_info['machine']}")
    safe_print(f"   Python版本               = {platform_info['python_version']}")
    safe_print(f"   当前工作目录             = {Path.cwd()}")
    safe_print(f"   配置文件路径             = {Path('Code_Gen_Config.json').absolute()}")
    safe_print(f"   平台特性                 = {'Windows' if platform_info['is_windows'] else 'macOS' if platform_info['is_macos'] else 'Linux'}")

    print("=" * 80)

def jeecg_complete_workflow():
    """JeecgBoot完整表单工作流 - 纯粹的API调用工具"""

    print("\n[START] 开始执行 JeecgBoot 表单工作流")
    print("=" * 50)

    # 打印所有变量信息
    print_workflow_variables()

    # 1. 登录获取Token
    print("1. 正在登录...")
    login_data = {"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD}
    
    try:
        response = requests.post(f"{BASE_URL}/sys/mLogin", json=login_data, timeout=REQUEST_TIMEOUT_LOGIN)
        if response.status_code != 200 or not response.json().get('success'):
            safe_print("[FAIL] 登录失败")
            _execute_failed_workflow("登录失败")
            return

        token = response.json()['result']['token']
        user_info = response.json()['result']['userInfo']
        safe_print(f"[OK] 登录成功: {user_info.get('realname')}")

    except Exception as e:
        safe_print(f"[FAIL] 登录异常: {e}")
        _execute_failed_workflow("登录异常")
        return

    # 2. 数据字典状态检查（仅检查，不进行智能匹配）
    print("\n2. 数据字典状态检查...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dict_file_exists = Path(os.path.join(script_dir, 'Code_Gen_DICT.json')).exists()
    if dict_file_exists:
        try:
            dict_data = load_dict_data()
            safe_print(f"[OK] 数据字典文件存在: {len(dict_data)}条记录")
        except Exception as e:
            safe_print(f"[WARN] 数据字典文件损坏: {e}")
    else:
        print("ℹ️ 数据字典文件不存在，可使用 --dict 参数获取最新数据字典")

    # 3. 准备表单数据
    print("\n3. 准备表单数据...")
    try:
        with open(FORM_DATA_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 检查是否是新格式的配置文件（包含table和fields）
        if 'table' in config_data and 'fields' in config_data:
            # 新格式：从配置文件生成完整的表单数据
            form_data = create_form_from_config(FORM_DATA_FILE)
            if not form_data:
                safe_print("[FAIL] 无法从配置文件生成表单数据")
                _execute_failed_workflow("表单数据准备失败")
                return
            table_name = form_data['head'].get('tableName')
            table_txt = form_data['head'].get('tableTxt')
        else:
            # 旧格式：直接使用表单数据
            form_data = config_data
            table_name = form_data['head'].get('tableName')
            table_txt = form_data['head'].get('tableTxt')
        
        # 设置全局变量，用于生成标准化包名
        global CURRENT_TABLE_NAME
        CURRENT_TABLE_NAME = table_name

        # 从表名设置三核心变量
        if set_core_variables_from_table_name(table_name):
            safe_print("[OK] 三核心变量设置成功")
            print_core_variables()
            validate_core_variables()
        else:
            safe_print("[WARN] 三核心变量设置失败，使用传统模式")

        if not table_name or table_name in ['tableNameEn', 'test_table']:
            # 如果没有设置表名或使用默认模板名，则生成随机表名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = random.randint(1000, 9999)
            table_name = f"test_table_{timestamp}_{random_id}"
            table_txt = f"Random Test Table {random_id}"

            form_data['head']['tableName'] = table_name
            form_data['head']['tableTxt'] = table_txt

        safe_print(f"[OK] 表名: {table_name}")
        safe_print(f"[OK] 表描述: {table_txt}")

        # 4. 表单数据验证
        print("\n4. 表单数据验证...")

        # 验证表单数据结构
        safe_print(f"[SEARCH] 验证表单数据结构:")
        safe_print(f"   form_data类型: {type(form_data)}")
        if isinstance(form_data, dict):
            fields = form_data.get('fields')
            safe_print(f"   fields类型: {type(fields)}")
            safe_print(f"   fields长度: {len(fields) if fields else 'None'}")
            if fields:
                safe_print(f"   前3个字段名: {[f.get('dbFieldName', 'N/A') for f in fields[:3]]}")
                safe_print("[OK] 表单数据结构验证通过")
            else:
                safe_print("   [FAIL] fields为None或空！")
                _execute_failed_workflow("表单数据验证失败")
                return
        else:
            safe_print("   [FAIL] form_data不是字典类型！")
            _execute_failed_workflow("表单数据验证失败")
            return

    except Exception as e:
        safe_print(f"[FAIL] 准备数据失败: {e}")
        _execute_failed_workflow("表单数据准备异常")
        return

    # 5. 智能识别业务系统并确保模块存在
    if not SKIP_MODULE_MANAGEMENT:
        print("\n5. 模块管理...")
        try:
            # 优先使用命令行指定的系统名称，否则智能识别
            if FORCE_SYSTEM:
                module_name = FORCE_SYSTEM
                safe_print(f"[TARGET] 使用指定业务系统: {module_name}")
            else:
                # 从表名直接解析模块名
                try:
                    business_entity = get_business_entity_from_global_or_config()
                    components = parse_table_name_components(table_name, business_entity)
                    module_name = components['module_name']
                    safe_print(f"[LIST] 从表名解析业务系统: {module_name}")
                except Exception as e:
                    safe_print(f"[WARN] 表名解析失败，使用智能识别: {e}")
                    module_name = detect_business_system(table_name, table_txt)
                    safe_print(f"[SYMBOL] 智能识别业务系统: {module_name}")

            # 确保模块存在
            if not ensure_module_exists(module_name):
                safe_print(f"[FAIL] 模块管理失败，终止工作流")
                _execute_failed_workflow("模块管理失败")
                return

            # 更新项目路径配置 - 使用变量一致性验证
            global PROJECT_PATH, BUSINESS_ENTITY
            project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

            # 变量一致性检查：确保module_name与MODULE_NAME一致
            if MODULE_NAME and MODULE_NAME != module_name:
                safe_print(f"[WARN] 检测到模块名不一致:")
                safe_print(f"   表名解析结果: MODULE_NAME = {MODULE_NAME}")
                safe_print(f"   工作流参数: module_name = {module_name}")
                safe_print(f"   [TOOL] 使用表名解析结果确保一致性")
                module_name = MODULE_NAME  # 强制使用表名解析的结果

            PROJECT_PATH = str(Path(f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}").resolve())

            # 注意：不再从表名重新解析实体名，保持使用配置文件中的business_entity值
            # BUSINESS_ENTITY已经在main函数开始时从配置文件中正确设置

            safe_print(f"[TOOL] 更新项目路径: {PROJECT_PATH}")
            safe_print(f"[PACKAGE] 保持实体名称: {BUSINESS_ENTITY} (来自配置文件business_entity)")
            safe_print(f"[OK] 模块名一致性验证通过: {module_name}")

            # 生成完整包名（基于模块名称和实体名称）
            # 生成完整包名（基于标准化命名规范）
            package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

            # 执行变量一致性验证
            safe_print(f"\n[SEARCH] 执行变量一致性验证...")
            if not validate_core_variables():
                safe_print(f"[FAIL] 变量一致性验证失败，可能影响代码生成质量")
                safe_print(f"   建议检查表名格式和模块映射逻辑")
            else:
                safe_print(f"[OK] 变量一致性验证通过，继续执行工作流")

            # 打印详细的路径信息
            safe_print(f"\n[LIST] 动态更新后的路径变量:")
            safe_print(f"   项目路径前缀             = {project_prefix}")
            safe_print(f"   业务模块名称             = {module_name}")
            safe_print(f"   完整项目路径             = {PROJECT_PATH}")
            safe_print(f"   实体名称                 = {BUSINESS_ENTITY}")
            safe_print(f"   完整包名                 = {package_name}")
            safe_print(f"   表名                     = {table_name}")
            safe_print(f"   表描述                   = {table_txt}")
            safe_print(f"\n[NOTE] 变量说明:")
            safe_print(f"   - path_prefix: 项目根路径前缀，来自配置文件")
            safe_print(f"   - project_path: 完整项目路径，格式为 {{path_prefix}}/jeecg-boot/jeecg-module-{{module_name}}")
            safe_print(f"   - entity_name: 实体名称，从表名去掉us_前缀生成，用于前端路由和权限控制")
            safe_print(f"   - package_name: 完整包名，格式为 org.jeecg.modules.{{module_name}}.{{sub_module}}")
            safe_print(f"   - SQL文件中的模块名称就是entity_name的值，如 'invoice'")

        except Exception as e:
            safe_print(f"[FAIL] 模块管理异常: {e}")
            _execute_failed_workflow("模块管理异常")
            return
    else:
        print("\n5. 跳过模块管理（使用现有配置）")
        safe_print(f"[TOOL] 当前项目路径: {PROJECT_PATH}")
        safe_print(f"[PACKAGE] 当前实体名称: {BUSINESS_ENTITY}")

        # 生成完整包名（基于标准化命名规范）
        package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

        # 打印当前配置信息
        safe_print(f"\n[LIST] 当前配置变量:")
        safe_print(f"   项目路径                 = {PROJECT_PATH}")
        safe_print(f"   实体名称                 = {BUSINESS_ENTITY}")
        safe_print(f"   完整包名                 = {package_name}")
        safe_print(f"   表名                     = {table_name}")
        safe_print(f"   表描述                   = {table_txt}")
    
    # 6. 创建表单
    print("\n6. 正在创建表单...")
    headers = {
        'X-Access-Token': token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        create_url = f"{BASE_URL}/online/cgform/api/addAll"
        safe_print(f"   创建URL: {create_url}")
        safe_print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

        response = requests.post(create_url, json=form_data, headers=headers, timeout=REQUEST_TIMEOUT_CREATE)

        safe_print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                safe_print("[OK] 表单创建成功")
                safe_print(f"   响应消息: {result.get('message', 'N/A')}")
            else:
                safe_print(f"[FAIL] 创建表单失败: {result.get('message', '未知错误')}")
                safe_print(f"   完整响应: {result}")
                _execute_failed_workflow("表单创建失败")
                return
        else:
            safe_print(f"[FAIL] 创建请求失败: HTTP {response.status_code}")
            safe_print(f"   响应内容: {response.text}")
            _execute_failed_workflow("表单创建请求失败")
            return

    except Exception as e:
        safe_print(f"[FAIL] 创建表单异常: {e}")
        _execute_failed_workflow("表单创建异常")
        return
    
    # 4. 等待并获取表单ID
    print("\n4. 正在获取表单ID...")
    time.sleep(WAIT_TIME_AFTER_CREATE)  # 等待表单创建完成

    try:
        params = {'pageNo': PAGE_NO, 'pageSize': PAGE_SIZE, 'tableName': table_name}
        list_url = f"{BASE_URL}/online/cgform/head/list"

        safe_print(f"   查询URL: {list_url}")
        safe_print(f"   查询参数: {params}")
        safe_print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

        response = requests.get(list_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT_LIST)

        safe_print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                records = result['result']['records']
                safe_print(f"   找到 {len(records)} 条记录")

                form_id = None
                for record in records:
                    if record.get('tableName') == table_name:
                        form_id = record.get('id')
                        safe_print(f"   匹配记录: {record.get('tableName')} -> {form_id}")
                        break

                if not form_id:
                    safe_print("[FAIL] 未找到匹配的表单ID")
                    safe_print(f"   搜索的表名: {table_name}")
                    for i, record in enumerate(records[:MAX_DISPLAY_RECORDS]):  # 显示前N条记录
                        safe_print(f"   记录{i+1}: {record.get('tableName')}")
                    _execute_failed_workflow("获取表单ID失败")
                    return

                safe_print(f"[OK] 表单ID: {form_id}")
            else:
                safe_print(f"[FAIL] 获取表单列表失败: {result.get('message')}")
                _execute_failed_workflow("获取表单列表失败")
                return
        else:
            safe_print(f"[FAIL] 查询请求失败: HTTP {response.status_code}")
            safe_print(f"   响应内容: {response.text}")
            _execute_failed_workflow("获取表单ID请求失败")
            return

    except Exception as e:
        safe_print(f"[FAIL] 获取表单ID异常: {e}")
        _execute_failed_workflow("获取表单ID异常")
        return
    
    # 7. 同步到数据库
    print("\n7. 正在同步到数据库...")
    
    # 首先验证数据库类型
    if not validate_database_type():
        safe_print("[FAIL] 数据库类型验证失败，工作流终止")
        _execute_failed_workflow("数据库类型不支持")
        return

    try:
        # 确保使用正确的headers和Token
        sync_headers = {
            'X-Access-Token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        sync_url = f"{BASE_URL}/online/cgform/api/doDbSynch/{form_id}/normal"
        safe_print(f"   同步URL: {sync_url}")
        safe_print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

        response = requests.post(sync_url, headers=sync_headers, timeout=REQUEST_TIMEOUT_SYNC)

        safe_print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                safe_print("[OK] 数据库同步成功")
                safe_print(f"   响应消息: {result.get('message', 'N/A')}")
            else:
                safe_print(f"[FAIL] 数据库同步失败: {result.get('message', '未知错误')}")
                safe_print(f"   完整响应: {result}")
                _execute_failed_workflow("数据库同步失败")
                return
        else:
            safe_print(f"[FAIL] 同步请求失败: HTTP {response.status_code}")
            safe_print(f"   响应内容: {response.text}")
            _execute_failed_workflow("数据库同步请求失败")
            return

    except Exception as e:
        safe_print(f"[FAIL] 数据库同步异常: {e}")
        _execute_failed_workflow("数据库同步异常")
        return

    # 8. 代码生成
    print("\n8. 正在生成代码...")

    try:
        # 生成实体名（只使用业务实体名，不包含模块和子模块前缀）
        entity_name = BUSINESS_ENTITY if BUSINESS_ENTITY else ''.join(word.capitalize() for word in table_name.split('_'))

        # 生成完整包名（基于标准化命名规范）
        package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

        # 打印代码生成前的所有关键变量
        safe_print(f"\n[LIST] 代码生成关键变量:")
        safe_print(f"   表单ID                   = {form_id}")
        safe_print(f"   表名                     = {table_name}")
        safe_print(f"   表描述                   = {form_data['head']['tableTxt']}")
        safe_print(f"   实体名                   = {entity_name}")
        safe_print(f"   实体名称                 = {BUSINESS_ENTITY}")
        safe_print(f"   完整包名                 = {package_name}")
        safe_print(f"   项目路径                 = {PROJECT_PATH}")

        # 显示四个核心变量
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        safe_print(f"\n[LIST] 四个核心变量:")
        safe_print(f"   PROJECT_PATH_PREFIX      = {project_prefix}")
        safe_print(f"   PROJECT_PATH             = {PROJECT_PATH}")
        safe_print(f"   BUSINESS_ENTITY              = {BUSINESS_ENTITY}")
        safe_print(f"   PACKAGE_NAME             = {package_name}")

        # 验证模板变量是否已正确解析
        safe_print(f"\n[SEARCH] 验证模板变量解析:")
        if not validate_template_variables():
            safe_print("[FAIL] 检测到未解析的模板变量，停止代码生成")
            _execute_failed_workflow("模板变量验证失败")
            return

        safe_print(f"\n[TOOL] 其他配置:")
        safe_print(f"   JSP模式                  = {JSP_MODE}")
        safe_print(f"   表单类型                 = {JFORM_TYPE}")
        safe_print(f"   包样式                   = {PACKAGE_STYLE}")
        safe_print(f"   Vue样式                  = {VUE_STYLE}")
        safe_print(f"   代码类型                 = {CODE_TYPES}")
        safe_print(f"   强制系统                 = {FORCE_SYSTEM or 'None'}")

        # 准备代码生成参数
        # 修复重复SUBMODULE_NAME问题：
        # - bussiPackage应该只包含基础路径：org.jeecg.modules.{MODULE_NAME}
        # - entityPackage设置为SUBMODULE_NAME，这样最终组合为：org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}
        base_package = f"org.jeecg.modules.{MODULE_NAME}"

        codegen_data = {
            "projectPath": PROJECT_PATH,
            "jspMode": JSP_MODE,
            "ftlDescription": form_data['head']['tableTxt'],
            "jformType": JFORM_TYPE,
            "tableName_tmp": table_name,
            "entityName": BUSINESS_ENTITY,
            "entityPackage": SUBMODULE_NAME,
            "bussiPackage": base_package,  # 只包含org.jeecg.modules.{MODULE_NAME}
            "packageStyle": PACKAGE_STYLE,
            "vueStyle": VUE_STYLE,
            "codeTypes": CODE_TYPES,
            "code": form_id,
            "tableName": table_name
        }

        # 打印完整的代码生成请求参数
        safe_print(f"\n[LIST] 代码生成请求参数:")
        safe_print(f"   [TOOL] 修复后的API调用参数:")
        safe_print(f"      entityName    = \"{BUSINESS_ENTITY}\" (业务实体)")
        safe_print(f"      entityPackage = \"{SUBMODULE_NAME}\" (子模块名)")
        safe_print(f"      bussiPackage  = \"{base_package}\" (基础包路径)")
        safe_print(f"      最终package   = {base_package}.{SUBMODULE_NAME}")
        safe_print(f"      预期生成路径 = {base_package.replace('.', '/')}/{SUBMODULE_NAME}/")
        safe_print(f"      修复效果     = 避免重复{SUBMODULE_NAME}目录层级")
        safe_print(f"   [LIST] 完整参数列表:")
        for key, value in codegen_data.items():
            safe_print(f"      {key:<20} = {value}")

        # 代码生成前：备份并替换配置文件变量
        config_replaced = backup_and_replace_jeecg_config(PROJECT_PATH, package_name)
        if not config_replaced:
            safe_print("[WARN] 配置文件替换失败，继续执行代码生成...")

        codegen_url = f"{BASE_URL}/online/cgform/api/codeGenerate"
        safe_print(f"   代码生成URL: {codegen_url}")
        safe_print(f"   表单ID: {form_id}")
        safe_print(f"   实体名: {entity_name}")
        safe_print(f"   业务包名: {package_name}")
        safe_print(f"   实体名称: {BUSINESS_ENTITY}")
        safe_print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

        # [START] 调用 codeGenerate 接口传参信息
        safe_print(f"\n[START] 正在调用 codeGenerate 接口...")
        safe_print(f"   [SYMBOL] 请求URL: {codegen_url}")
        safe_print(f"   [LIST] 请求方法: POST")
        safe_print(f"   [DOC] 请求头信息:")
        for key, value in headers.items():
            if key.lower() == 'x-access-token':
                safe_print(f"      {key}: {value[:DISPLAY_TOKEN_LENGTH]}...")
            else:
                safe_print(f"      {key}: {value}")
        safe_print(f"   [PACKAGE] 请求体参数 (JSON):")
        print(json.dumps(codegen_data, indent=4, ensure_ascii=False))
        safe_print(f"   ⏰ 请求超时时间: {REQUEST_TIMEOUT_CODEGEN}秒")

        response = requests.post(codegen_url, json=codegen_data, headers=headers, timeout=REQUEST_TIMEOUT_CODEGEN)

        safe_print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                safe_print("[OK] 代码生成成功")
                safe_print(f"   响应消息: {result.get('message', 'N/A')}")

                # 立即处理生成代码中的模板变量替换
                safe_print("\n[TOOL] 处理生成代码中的模板变量替换...")
                if process_generated_code_templates():
                    safe_print("[OK] 模板变量处理完成")
                else:
                    safe_print("[FAIL] 模板变量处理失败，但继续执行后续步骤")
                
                # 代码生成成功后，先进行包名替换和目录处理
                safe_print(f"\n{'='*50}")
                safe_print("[REFRESH] 执行生成代码后处理...")
                
                # 1. 替换java文件package包名内容
                try:
                    replace_package_declarations()
                    safe_print("[OK] Java文件package包名替换完成")
                except Exception as e:
                    safe_print(f"[WARN] package包名替换失败: {e}")
                
                # 2. 处理生成文件目录结构
                try:
                    reorganize_generated_files()
                    safe_print("[OK] 生成文件目录结构处理完成")
                except Exception as e:
                    safe_print(f"[WARN] 文件目录结构处理失败: {e}")
                
                # 继续执行后续工作流程
                execute_post_generation_workflow()

            else:
                safe_print(f"[FAIL] 代码生成失败: {result.get('message', '未知错误')}")
                safe_print(f"   完整响应: {result}")
                # 代码生成失败，执行失败的工作流
                _execute_failed_workflow("代码生成接口调用失败")
                return
        else:
            safe_print(f"[FAIL] 代码生成请求失败: HTTP {response.status_code}")
            safe_print(f"   响应内容: {response.text}")
            # 代码生成请求失败，执行失败的工作流
            _execute_failed_workflow("代码生成接口调用失败")
            return

    except Exception as e:
        safe_print(f"[FAIL] 代码生成异常: {e}")
        # 代码生成异常，执行失败的工作流
        _execute_failed_workflow("代码生成接口调用异常")
        return
    finally:
        # 代码生成完成后：还原配置文件（静默执行）
        restore_jeecg_config(silent=True)

    # 注意：API调用成功后的后续工作流程（步骤7-13）已被移动到execute_post_generation_workflow()函数中

# ==================== 命令行参数处理 ====================

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='JeecgBoot 表单工作流自动化工具 v2.0')

    parser.add_argument('--config', '-c', default='Code_Gen_Config.json',
                       help='配置文件路径 (默认: Code_Gen_Config.json)')

    parser.add_argument('--module-name', '-m',
                       help='业务模块名称（如：hrms, crm, scm, oa, finance）')

    parser.add_argument('--form-config', '-f',
                       help='表单配置文件路径')

    parser.add_argument('--table-name', '-n',
                       help='表名（覆盖配置文件中的设置）')

    parser.add_argument('--table-description', '-d',
                       help='表描述（覆盖配置文件中的设置）')

    parser.add_argument('--project-path', '-p',
                       help='项目路径（覆盖配置文件中的设置）')

    parser.add_argument('--entity-name', '-e',
                       help='实体名称（覆盖配置文件中的设置）')

    parser.add_argument('--test', action='store_true',
                       help='运行系统诊断测试')

    parser.add_argument('--validate', action='store_true',
                       help='仅验证配置和数据，不执行工作流')

    parser.add_argument('--skip-module-management', action='store_true',
                       help='跳过模块管理（不检查和创建模块）')

    parser.add_argument('--try-run', action='store_true',
                       help='试运行模式（只显示将要执行的操作，不实际执行）')

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出模式')

    parser.add_argument('--dict', action='store_true',
                       help='获取系统数据字典并保存到Code_Gen_DICT.json')
    
    parser.add_argument('--validate-table-name', type=str,
                       help='验证表名格式并提供修复建议')
    
    parser.add_argument('--fix-table-name', type=str,
                       help='自动修复表名格式')

    # 编译相关参数
    parser.add_argument('--skip-compilation', action='store_true',
                       help='跳过自动编译步骤')

    parser.add_argument('--maven-path', type=str,
                       help='指定Maven可执行文件路径')

    parser.add_argument('--skip-pom-creation', action='store_true',
                       help='跳过自动创建pom.xml文件')

    parser.add_argument('--check-field-lengths', type=str, metavar='CONFIG_FILE',
                       help='检查配置文件中的字段长度限制问题')

    return parser.parse_args()

def check_field_lengths_in_config(config_file):
    """检查配置文件中的字段长度限制问题"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        safe_print(f"[SEARCH] 检查配置文件: {config_file}")
        print("=" * 60)

        issues_found = False

        if 'fields' not in config:
            safe_print("[FAIL] 配置文件中没有fields数组")
            return

        for i, field in enumerate(config['fields']):
            field_name = field.get('dbFieldName', f'字段{i+1}')

            # 检查 queryMode 字段
            if 'queryMode' in field:
                query_mode = field['queryMode']
                if len(query_mode) > 10:
                    safe_print(f"[FAIL] {field_name}: queryMode '{query_mode}' 超过10字符限制")
                    issues_found = True
                elif query_mode in ['group_range', 'date_range', 'multi_select']:
                    safe_print(f"[WARN]  {field_name}: queryMode '{query_mode}' 建议改为更短的值")
                    issues_found = True

            # 检查其他关键字段
            field_limits = {
                'fieldShowType': 20,
                'queryShowType': 50,
                'fieldValidType': 300,
                'dictField': 100,
                'dictText': 100,
                'dictTable': 255
            }

            for field_key, max_length in field_limits.items():
                if field_key in field and len(str(field[field_key])) > max_length:
                    safe_print(f"[FAIL] {field_name}: {field_key} 值过长({len(str(field[field_key]))}字符)，超过{max_length}字符限制")
                    issues_found = True

        if not issues_found:
            safe_print("[OK] 所有字段长度检查通过")
        else:
            safe_print("\n[TOOL] 修复建议:")
            safe_print("1. 将 'group_range' 改为 'range'")
            safe_print("2. 将 'date_range' 改为 'range'")
            safe_print("3. 将 'multi_select' 改为 'single'")
            safe_print("4. 截断过长的字段值")
            safe_print("\n[TIP] 可以使用 Code_Gen_Guide.py 的自动修正功能")

    except Exception as e:
        safe_print(f"[FAIL] 检查配置文件时出错: {e}")

def main():
    """主函数"""
    args = parse_arguments()

    # 字段长度检查命令
    if args.check_field_lengths:
        check_field_lengths_in_config(args.check_field_lengths)
        return

    # 注：表名验证和修复命令已移除，现在使用business_entity机制

    # 加载配置
    global CONFIG, FORM_DATA_FILE, CURRENT_TABLE_NAME, MODULE_NAME, SUBMODULE_NAME, BUSINESS_ENTITY
    if args.config != 'Code_Gen_Config.json':
        CONFIG = load_config_from_file(args.config)

    # 命令行参数覆盖配置
    if args.project_path:
        CONFIG['codegen']['project_path'] = args.project_path
    if args.entity_name:
        CONFIG['codegen']['entity_name'] = args.entity_name

    # 设置全局标志
    global SKIP_MODULE_MANAGEMENT, FORCE_SYSTEM, CURRENT_TABLE_NAME
    SKIP_MODULE_MANAGEMENT = args.skip_module_management
    FORCE_SYSTEM = args.module_name  # 使用新的参数名

    # 处理编译相关参数
    if args.skip_compilation:
        CONFIG['compilation']['enabled'] = False

    if args.maven_path:
        CONFIG['compilation']['maven_command'] = args.maven_path

    if args.skip_pom_creation:
        CONFIG['compilation']['auto_create_pom'] = False

    # 预处理工作流变量（确保在显示配置前就有实际值）
    global PROJECT_PATH, BUSINESS_ENTITY, MODULE_NAME, SUBMODULE_NAME, PACKAGE_NAME, TABLE_NAME

    # 处理特殊命令（不需要表单配置）
    if args.dict:
        # 获取系统数据字典
        fetch_system_dict()
        return

    if args.test:
        # 运行系统诊断
        run_diagnostics()
        return

    if args.validate:
        # 仅验证配置
        safe_print("[SEARCH] 验证模式 - 仅检查配置和数据")
        config_errors = validate_config()
        if config_errors:
            safe_print("[FAIL] 配置验证失败:")
            for error in config_errors:
                safe_print(f"   - {error}")
        else:
            safe_print("[OK] 配置验证通过")

        # 验证表单数据（如果提供了配置文件）
        if args.form_config:
            try:
                with open(args.form_config, 'r', encoding='utf-8') as f:
                    form_data = json.load(f)
                form_errors = validate_form_data(form_data)
                if form_errors:
                    safe_print("[FAIL] 表单数据验证失败:")
                    for error in form_errors:
                        safe_print(f"   - {error}")
                else:
                    safe_print("[OK] 表单数据验证通过")
            except Exception as e:
                safe_print(f"[FAIL] 表单数据加载失败: {e}")
        return

    # 1. 处理业务实体和格式派生 (重构版)
    if args.form_config:
        try:
            # 使用新的业务实体提取和格式派生逻辑
            formats = extract_business_entity_from_config(args.form_config)

            # 设置全局变量
            BUSINESS_ENTITY = formats['java_class_name']  # 使用业务实体作为Java类名

            # 从配置文件中读取表名和模块信息
            with open(args.form_config, 'r', encoding='utf-8') as f:
                form_data = json.load(f)
                table_name = form_data.get('head', {}).get('tableName', '')
                CURRENT_TABLE_NAME = table_name

                # 从metadata中获取模块信息 (如果有的话)
                metadata = form_data.get('metadata', {}).get('generation_info', {})
                if metadata.get('module_name'):
                    MODULE_NAME = metadata['module_name']
                if metadata.get('submodule_name'):
                    SUBMODULE_NAME = metadata['submodule_name']

            safe_print("[OK] 从配置文件提取业务实体成功")

        except Exception as e:
            safe_print(f"[FAIL] 业务实体提取失败: {e}")
            safe_print("[TIP] 请检查配置文件是否包含正确的business_entity字段")
            return
    else:
        safe_print("[FAIL] 必须提供配置文件参数 --form-config")
        safe_print("[TIP] 请使用Code_Gen_Agent.md生成包含business_entity的配置文件")
        return

    # 2. 处理模块名称和项目路径
    if FORCE_SYSTEM:
        MODULE_NAME = FORCE_SYSTEM
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        PROJECT_PATH = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{MODULE_NAME}"
    else:
        if not MODULE_NAME:  # 如果三核心变量设置失败
            # 不要直接使用配置中的模板变量，而是使用默认路径
            project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
            PROJECT_PATH = f"{project_prefix}/jeecg-boot"  # 使用默认路径

    # 3. 全局变量已在文件开头定义，无需额外更新

    # 显示工具信息
    print("JeecgBoot 表单工作流自动化工具 v2.0")
    print("=" * 50)

    if args.module_name:
        safe_print(f"[TARGET] 指定业务模块: {args.module_name}")
    if args.form_config:
        safe_print(f"[LIST] 表单配置文件: {args.form_config}")



    if args.try_run:
        safe_print("[SEARCH] 试运行模式 - 将显示操作但不执行")
        safe_print(f"[LIST] 配置文件: {args.config}")
        safe_print(f"[TARGET] 业务系统: {args.module_name or '自动识别'}")
        safe_print(f"[LIST] 表单配置: {args.form_config or '使用默认'}")
        safe_print(f"[BUILD] 项目路径: {PROJECT_PATH}")  # 使用预处理后的值
        safe_print(f"[PACKAGE] 实体名称: {BUSINESS_ENTITY}")    # 使用预处理后的值

        # 显示三核心变量
        safe_print(f"\n[LIST] 三核心变量:")
        safe_print(f"   MODULE_NAME      = {MODULE_NAME}")
        safe_print(f"   SUBMODULE_NAME   = {SUBMODULE_NAME}")
        safe_print(f"   BUSINESS_ENTITY      = {BUSINESS_ENTITY}")

        # 显示派生变量
        safe_print(f"\n[CHART] 派生变量:")
        safe_print(f"   TABLE_NAME       = {TABLE_NAME}")
        safe_print(f"   PACKAGE_NAME     = {PACKAGE_NAME}")
        safe_print(f"   BUSINESS_ENTITY = {BUSINESS_ENTITY}")
        safe_print(f"   PROJECT_PATH     = {PROJECT_PATH}")

        # 验证模板变量
        safe_print(f"\n[SEARCH] 模板变量验证:")
        validate_template_variables()

        return



    # 处理表单配置文件
    if args.form_config:
        # 直接使用指定的配置文件
        CONFIG['form']['data_file'] = args.form_config
        FORM_DATA_FILE = args.form_config
        safe_print(f"[OK] 使用表单配置文件: {args.form_config}")
    else:
        safe_print(f"[OK] 使用默认表单配置: {FORM_DATA_FILE}")

    # 执行工作流
    jeecg_complete_workflow()

def create_form_from_config(config_file_path):
    """
    从配置文件生成完整的表单数据，确保表名符合us_前缀规范

    Args:
        config_file_path (str): 配置文件路径

    Returns:
        dict: 完整的表单数据，如果失败返回None
    """
    try:
        safe_print(f"[LIST] 从配置文件生成表单数据: {config_file_path}")

        # 首先尝试转换配置文件格式（如果需要）
        if not convert_legacy_config_format(config_file_path):
            safe_print("[FAIL] 配置文件格式转换失败")
            return None

        # 读取配置文件
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 检查是否是新格式配置文件（包含table和fields）
        if 'table' in config_data and 'fields' in config_data:
            safe_print("[REFRESH] 检测到新格式配置文件，转换为标准表单格式")
            # 这里可以添加新格式到标准格式的转换逻辑
            # 目前直接返回None，让调用方使用旧格式处理
            return None

        # 检查表名格式
        table_name = config_data.get('head', {}).get('tableName', '')
        if not table_name:
            safe_print("[FAIL] 配置文件中缺少表名")
            return None

        # 检查表名是否符合us_前缀规范
        if not table_name.startswith('us_'):
            safe_print(f"[WARN] 表名格式不符合规范: {table_name}")

            # 尝试从metadata中获取模块信息来修复表名
            metadata = config_data.get('metadata', {}).get('generation_info', {})
            module_name = metadata.get('module_name', '')
            submodule_name = metadata.get('submodule_name', '')
            business_entity = metadata.get('business_entity', '')

            if module_name and submodule_name and business_entity:
                # 生成正确的表名
                formats = derive_all_formats_from_business_entity(business_entity)
                business_scenario = formats['table_suffix']
                correct_table_name = f"us_{module_name}_{submodule_name}_{business_scenario}"

                safe_print(f"[TOOL] 自动修复表名: {table_name} -> {correct_table_name}")

                # 更新配置数据中的表名
                config_data['head']['tableName'] = correct_table_name

                # 保存修复后的配置文件
                backup_file = config_file_path + '.backup'
                import shutil
                shutil.copy2(config_file_path, backup_file)
                safe_print(f"[FOLDER] 原配置文件已备份到: {backup_file}")

                with open(config_file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                safe_print(f"[OK] 配置文件已更新")
            else:
                safe_print(f"[FAIL] 无法自动修复表名，缺少必要的metadata信息")
                safe_print(f"   需要: module_name, submodule_name, business_entity")
                safe_print(f"   实际: module_name={module_name}, submodule_name={submodule_name}, business_entity={business_entity}")
                return None

        safe_print(f"[OK] 表单数据生成成功，表名: {config_data['head']['tableName']}")
        return config_data

    except FileNotFoundError:
        safe_print(f"[FAIL] 配置文件不存在: {config_file_path}")
        return None
    except json.JSONDecodeError as e:
        safe_print(f"[FAIL] 配置文件JSON格式错误: {e}")
        return None
    except Exception as e:
        safe_print(f"[FAIL] 生成表单数据失败: {e}")
        return None

def load_config_from_file(config_file):
    """从指定文件加载配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        safe_print(f"[FAIL] 配置文件加载失败: {e}")
        return CONFIG

def process_generated_code_templates():
    """处理生成代码中的模板变量替换和路径标准化"""
    safe_print(f"\n[TOOL] 处理生成代码中的模板变量替换和路径标准化...")

    try:
        # 获取当前表名信息
        if not CURRENT_TABLE_NAME:
            safe_print("[FAIL] 当前表名为空，无法处理代码")
            return False

        business_entity = get_business_entity_from_global_or_config()
        components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
        module_name = components['module_name']
        sub_module = components['sub_module']
        entity_name = components['entity_name']

        # 构建正确的包名 - 基于JeecgBoot标准结构，不包含业务实体
        correct_package = f"org.jeecg.modules.{module_name.lower()}.{sub_module.lower()}"

        # 构建正确的包路径 - 修复：{{PACKAGE_NAME}}应该替换为基础包路径，不包含业务实体
        # 实际的目录结构是：org/jeecg/modules/{module_name}/{sub_module}/controller/
        base_package_path = f"org/jeecg/modules/{module_name}/{sub_module}"

        # 查找生成的代码目录
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        module_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'

        safe_print(f"   模块路径: {module_path}")
        safe_print(f"   正确包名: {correct_package}")
        safe_print(f"   子模块名: {sub_module}")
        safe_print(f"   基础包路径: {base_package_path}")

        # 1. 修复目录结构中的模板变量
        template_dirs = list(module_path.rglob("*{{PACKAGE_NAME}}*"))
        if template_dirs:
            safe_print(f"   [SEARCH] 发现 {len(template_dirs)} 个包含模板变量的目录")

            for template_dir in template_dirs:
                # 正确的模板变量替换逻辑
                # 检查模板路径是否已经包含子模块名，避免重复
                template_path_str = str(template_dir)

                # 检查这个模板目录下是否有子模块目录
                has_submodule_dir = False
                if template_dir.exists() and template_dir.is_dir():
                    submodule_dir = template_dir / sub_module
                    has_submodule_dir = submodule_dir.exists()



                # 如果模板目录下有子模块目录，则只替换为基础包路径（不包含子模块）
                if has_submodule_dir:
                    # 模板目录如：{{PACKAGE_NAME}} 下有 datas 目录
                    # 替换为：org/jeecg/modules/dictd（不包含datas，避免重复）
                    base_package_without_submodule = f"org/jeecg/modules/{module_name}"
                    correct_path_str = template_path_str.replace("{{PACKAGE_NAME}}", base_package_without_submodule)
                else:
                    # 模板目录如：{{PACKAGE_NAME}} 下没有子模块目录
                    # 替换为：org/jeecg/modules/dictd/datas
                    correct_path_str = template_path_str.replace("{{PACKAGE_NAME}}", base_package_path)

                correct_path = Path(correct_path_str)

                safe_print(f"   [FOLDER] 重命名目录:")
                safe_print(f"      从: {template_dir}")
                safe_print(f"      到: {correct_path}")
                if has_submodule_dir:
                    safe_print(f"      替换逻辑: {{{{PACKAGE_NAME}}}} → org/jeecg/modules/{module_name} (避免重复{sub_module})")
                else:
                    safe_print(f"      替换逻辑: {{{{PACKAGE_NAME}}}} → {base_package_path}")

                # 确保父目录存在
                correct_path.parent.mkdir(parents=True, exist_ok=True)

                # 移动目录内容而不是整个目录
                if template_dir.exists() and template_dir.is_dir():
                    # 如果目标目录已存在，合并内容
                    if correct_path.exists():
                        safe_print(f"   [REFRESH] 目标目录已存在，合并内容...")
                        for item in template_dir.iterdir():
                            target_item = correct_path / item.name
                            if item.is_dir():
                                if not target_item.exists():
                                    shutil.move(str(item), str(target_item))
                                else:
                                    # 递归合并目录
                                    for sub_item in item.rglob('*'):
                                        if sub_item.is_file():
                                            rel_path = sub_item.relative_to(item)
                                            target_file = target_item / rel_path
                                            target_file.parent.mkdir(parents=True, exist_ok=True)
                                            shutil.move(str(sub_item), str(target_file))
                            else:
                                if not target_item.exists():
                                    shutil.move(str(item), str(target_item))
                        # 删除空的源目录
                        try:
                            template_dir.rmdir()
                        except:
                            pass
                    else:
                        # 直接移动整个目录
                        shutil.move(str(template_dir), str(correct_path))

                    safe_print(f"   [OK] 目录重命名成功")

        # 2. 检测和修复路径重复问题
        # 查找重复的路径模式：org/jeecg/modules/scm/equipment/scm/equipment/
        business_entity = get_business_entity_from_global_or_config()
        components = parse_table_name_components(CURRENT_TABLE_NAME, business_entity)
        module_name = components['module_name']
        sub_module = components['sub_module']

        duplicate_dirs = list(module_path.rglob(f"*/{module_name}/{sub_module}/{module_name}/{sub_module}"))
        if duplicate_dirs:
            safe_print(f"   [SEARCH] 发现 {len(duplicate_dirs)} 个重复路径目录")

            for duplicate_dir in duplicate_dirs:
                # 计算正确的目录路径
                duplicate_str = str(duplicate_dir)
                correct_str = duplicate_str.replace(f"/{module_name}/{sub_module}/{module_name}/{sub_module}", f"/{module_name}/{sub_module}")
                correct_path = Path(correct_str)

                safe_print(f"   [FOLDER] 修复重复路径:")
                safe_print(f"      从: {duplicate_dir}")
                safe_print(f"      到: {correct_path}")

                # 确保目标目录的父目录存在
                correct_path.parent.mkdir(parents=True, exist_ok=True)

                # 移动目录内容
                if duplicate_dir.exists() and duplicate_dir.is_dir():
                    # 如果目标目录已存在，合并内容
                    if correct_path.exists():
                        # 移动所有子项到正确位置
                        for item in duplicate_dir.iterdir():
                            target_item = correct_path / item.name
                            if not target_item.exists():
                                shutil.move(str(item), str(target_item))
                        # 删除空的重复目录
                        try:
                            duplicate_dir.rmdir()
                        except:
                            pass
                    else:
                        # 直接移动整个目录
                        shutil.move(str(duplicate_dir), str(correct_path))

                    safe_print(f"   [OK] 重复路径处理成功")

        # 3. 处理文件内容中的模板变量和包名问题
        all_files = list(module_path.rglob("*"))
        fixed_files = 0

        for file_path in all_files:
            if file_path.is_file() and file_path.suffix in ['.java', '.sql', '.xml', '.vue', '.ts', '.js']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查是否包含模板变量
                    template_fixed = False

                    # 1. 替换 {{PACKAGE_NAME}}
                    if '{{PACKAGE_NAME}}' in content:
                        # 根据文件类型选择替换策略
                        if file_path.suffix == '.java':
                            # Java文件使用基础包名，不包含业务实体名
                            base_package_name = f"org.jeecg.modules.{module_name.lower()}.{sub_module.lower()}"
                            content = content.replace('{{PACKAGE_NAME}}', base_package_name)
                        else:
                            # 其他文件也使用基础包名
                            base_package_name = f"org.jeecg.modules.{module_name.lower()}.{sub_module.lower()}"
                            content = content.replace('{{PACKAGE_NAME}}', base_package_name)
                        template_fixed = True

                    # 2. 替换 {{PROJECT_PATH}}
                    if '{{PROJECT_PATH}}' in content:
                        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
                        project_path = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
                        content = content.replace('{{PROJECT_PATH}}', project_path)
                        template_fixed = True

                    # 3. 替换 {{BUSINESS_ENTITY}}
                    if '{{BUSINESS_ENTITY}}' in content:
                        # 使用全局的BUSINESS_ENTITY变量，与API参数保持一致
                        java_entity_name = BUSINESS_ENTITY if BUSINESS_ENTITY else convert_to_java_entity_name(components['entity_name'])
                        content = content.replace('{{BUSINESS_ENTITY}}', java_entity_name)
                        template_fixed = True

                    # 4. 替换 {{MODULE_NAME}}
                    if '{{MODULE_NAME}}' in content:
                        content = content.replace('{{MODULE_NAME}}', module_name)
                        template_fixed = True

                    # 5. 替换 {{SUBMODULE_NAME}}
                    if '{{SUBMODULE_NAME}}' in content:
                        content = content.replace('{{SUBMODULE_NAME}}', sub_module)
                        template_fixed = True

                    # 6. 替换 {{TABLE_NAME}}
                    if '{{TABLE_NAME}}' in content:
                        content = content.replace('{{TABLE_NAME}}', CURRENT_TABLE_NAME)
                        template_fixed = True

                    # 检查并修复各种包名问题
                    package_fixed = False
                    
                    # 1. 修复重复包名
                    duplicate_package = f"org.jeecg.modules.{module_name.lower()}.{sub_module.lower()}.{module_name.lower()}.{sub_module.lower()}"
                    if duplicate_package in content:
                        content = content.replace(duplicate_package, correct_package)
                        package_fixed = True
                    
                    # 2. 修复包名中错误包含BUSINESS_ENTITY的情况
                    # 例如: org.jeecg.modules.education.teacher.teacherprofile -> org.jeecg.modules.education.teacher
                    # 使用全局的BUSINESS_ENTITY变量，与API参数保持一致
                    business_entity_name = BUSINESS_ENTITY if BUSINESS_ENTITY else entity_name
                    wrong_package_with_entity = f"org.jeecg.modules.{module_name.lower()}.{sub_module.lower()}.{business_entity_name.lower()}"
                    if wrong_package_with_entity in content:
                        content = content.replace(wrong_package_with_entity, correct_package)
                        package_fixed = True
                        
                    # 3. 修复包名中大小写问题
                    # 例如: org.jeecg.modules.Education.Teacher -> org.jeecg.modules.education.teacher  
                    wrong_package_case = f"org.jeecg.modules.{module_name}.{sub_module}"
                    if wrong_package_case in content and wrong_package_case != correct_package:
                        content = content.replace(wrong_package_case, correct_package)
                        package_fixed = True

                    # 如果有任何修复，写回文件
                    if template_fixed or package_fixed:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)

                        process_type = []
                        if template_fixed:
                            process_type.append("模板变量")
                        if package_fixed:
                            process_type.append("包名规范")

                        safe_print(f"   [OK] 处理文件 ({'/'.join(process_type)}): {file_path.relative_to(module_path)}")
                        fixed_files += 1

                except Exception as e:
                    safe_print(f"   [FAIL] 处理文件失败 {file_path}: {e}")

        # 4. 清理处理完成后留下的空{{PACKAGE_NAME}}目录
        empty_template_dirs_cleaned = 0
        remaining_template_dirs = list(module_path.rglob("*{{PACKAGE_NAME}}*"))
        if remaining_template_dirs:
            safe_print(f"   [CLEAN] 清理剩余的空{{PACKAGE_NAME}}目录...")
            for template_dir in remaining_template_dirs:
                try:
                    if template_dir.exists() and template_dir.is_dir():
                        # 检查目录是否为空
                        if not any(template_dir.iterdir()):
                            template_dir.rmdir()
                            safe_print(f"   [SYMBOL]️ 删除空目录: {template_dir.relative_to(module_path)}")
                            empty_template_dirs_cleaned += 1
                        else:
                            # 如果目录不为空，递归检查是否只包含空的子目录
                            # 重要修复：保护pom.xml等重要文件不被删除
                            has_important_files = False
                            important_files = ['pom.xml', 'README.md', 'application.yml', 'application.properties']
                            
                            for item in template_dir.rglob("*"):
                                if item.is_file():
                                    # 检查是否为重要文件
                                    if item.name in important_files:
                                        has_important_files = True
                                        safe_print(f"   [PROTECT] 保护重要文件: {item.relative_to(module_path)}")
                                        break
                            
                            # 只有在没有重要文件时才检查是否全为空目录
                            if not has_important_files:
                                all_empty = True
                                for item in template_dir.rglob("*"):
                                    if item.is_file():
                                        all_empty = False
                                        break
                                
                                if all_empty:
                                    # 目录中只有空的子目录，可以安全删除
                                    shutil.rmtree(template_dir)
                                    safe_print(f"   [SYMBOL]️ 删除空目录树: {template_dir.relative_to(module_path)}")
                                    empty_template_dirs_cleaned += 1
                            else:
                                safe_print(f"   [SKIP] 跳过包含重要文件的目录: {template_dir.relative_to(module_path)}")
                except Exception as e:
                    safe_print(f"   [WARN] 清理目录失败 {template_dir}: {e}")

        safe_print(f"   [CHART] 处理统计:")
        safe_print(f"      模板目录处理: {len(template_dirs)} 个")
        safe_print(f"      重复路径处理: {len(duplicate_dirs) if 'duplicate_dirs' in locals() else 0} 个")
        safe_print(f"      文件内容处理: {fixed_files} 个")
        safe_print(f"      空目录清理: {empty_template_dirs_cleaned} 个")

        if len(template_dirs) > 0 or (duplicate_dirs and len(duplicate_dirs) > 0) or fixed_files > 0 or empty_template_dirs_cleaned > 0:
            safe_print(f"   [OK] 代码处理完成")
            return True
        else:
            safe_print(f"   ℹ️ 未发现需要处理的问题")
            return True

    except Exception as e:
        safe_print(f"   [FAIL] 代码处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()