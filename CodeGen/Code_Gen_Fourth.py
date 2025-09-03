#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot 第四步代码生成工具 v1.0
功能：专门用于调用JeecgBoot的登录API和第四个代码生成接口
流程：登录 → 代码生成
特性：
- 与Code_Gen_Guide.py相同的参数接收方式
- 简化的工作流，只包含登录和代码生成
- 完整的错误处理和日志记录
- 配置文件兼容性
"""

import requests
import json
import time
import argparse
import re
import platform
import sys
import os
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
            
            # Windows 控制台编码设置
            success = False
            
            try:
                result = subprocess.run(['chcp', '65001'], 
                                      capture_output=True, 
                                      check=False, 
                                      timeout=5)
                if result.returncode == 0:
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                    success = True
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                pass
            
            if not success:
                try:
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                    success = True
                except Exception:
                    pass
            
            if not success:
                try:
                    encoding = locale.getpreferredencoding()
                    sys.stdout.reconfigure(encoding=encoding, errors='replace')
                    sys.stderr.reconfigure(encoding=encoding, errors='replace')
                    EMOJI_SUPPORT = False
                except Exception:
                    EMOJI_SUPPORT = False
            else:
                current_encoding = getattr(sys.stdout, 'encoding', '').lower()
                if current_encoding in ['utf-8', 'utf8']:
                    EMOJI_SUPPORT = True
                else:
                    EMOJI_SUPPORT = False
                    
        else:
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                EMOJI_SUPPORT = True
            except Exception:
                EMOJI_SUPPORT = False
                
    except Exception:
        EMOJI_SUPPORT = False

def safe_print(text, **kwargs):
    """安全打印函数，在不支持emoji的环境下使用fallback"""
    global EMOJI_SUPPORT
    
    if not isinstance(text, str):
        text = str(text)
    
    if not EMOJI_SUPPORT and platform.system() == 'Windows':
        emoji_map = {
            '[TOOL]': '[工具]', '[OK]': '[OK]', '[FAIL]': '[FAIL]', '[CHART]': '[图表]', 
            '[TARGET]': '[目标]', '[START]': '[启动]', '[LIST]': '[清单]', '[FOLDER]': '[文件夹]',
            '[SEARCH]': '[搜索]', '[FAST]': '[闪电]', '[SUCCESS]': '[庆祝]', '[WARN]': '[警告]',
            '[TIP]': '[提示]', '[NOTE]': '[记录]', '[DATABASE]': '[数据库]', '[WEB]': '[网络]',
            '[REFRESH]': '[刷新]', '[LINK]': '[链接]', '[PACKAGE]': '[包]', '[DESIGN]': '[设计]',
            '[BUILD]': '[构建]'
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
    
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        try:
            encoded = text.encode(sys.stdout.encoding or 'utf-8', errors='replace')
            decoded = encoded.decode(sys.stdout.encoding or 'utf-8')
            print(decoded, **kwargs)
        except (UnicodeEncodeError, LookupError):
            try:
                if platform.system() == 'Windows':
                    encoded = text.encode('gbk', errors='replace')
                    decoded = encoded.decode('gbk')
                    print(decoded, **kwargs)
                else:
                    raise UnicodeEncodeError('fallback', text, 0, len(text), 'fallback to ascii')
            except (UnicodeEncodeError, LookupError):
                safe_text = ''.join(char for char in text 
                                  if ord(char) < 128 or '\u4e00' <= char <= '\u9fff')
                try:
                    print(safe_text, **kwargs)
                except UnicodeEncodeError:
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
    def normalize_path(path_str):
        """标准化路径，处理不同平台的路径分隔符"""
        return Path(path_str).resolve()

    @staticmethod
    def get_default_project_prefix():
        """获取默认项目路径前缀"""
        home = Path.home()
        if platform.system() == 'Windows':
            return str(home / 'Documents' / 'JeecgBoot')
        elif platform.system() == 'Darwin':
            return str(home / 'Work' / 'JeecgBoot')
        else:
            return str(home / 'projects' / 'JeecgBoot')

    @staticmethod
    def detect_project_root():
        """智能检测项目根目录"""
        current_path = Path.cwd()

        for path in [current_path] + list(current_path.parents):
            indicators = [
                'jeecg-boot',
                'jeecgboot-vue3',
                'CodeGen',
                'pom.xml'
            ]

            if any((path / indicator).exists() for indicator in indicators):
                return str(path)

        return str(current_path)

    @staticmethod
    def resolve_path_prefix(config_path_prefix):
        """解析路径前缀，支持相对路径、环境变量和自动检测"""
        if not config_path_prefix:
            return CrossPlatformUtils.detect_project_root()

        if config_path_prefix.startswith('$'):
            env_var = config_path_prefix[1:]
            env_value = os.environ.get(env_var)
            if env_value:
                return str(CrossPlatformUtils.normalize_path(env_value))
            else:
                safe_print(f"[WARN] 环境变量 {env_var} 未设置，使用自动检测")
                return CrossPlatformUtils.detect_project_root()

        if config_path_prefix == "AUTO_DETECT":
            return CrossPlatformUtils.detect_project_root()

        if not Path(config_path_prefix).is_absolute():
            base_path = Path(__file__).parent.parent
            return str(CrossPlatformUtils.normalize_path(base_path / config_path_prefix))

        return str(CrossPlatformUtils.normalize_path(config_path_prefix))

# 全局变量定义
MODULE_NAME = None
SUBMODULE_NAME = None
BUSINESS_ENTITY = None
TABLE_NAME = None
PACKAGE_NAME = None
PROJECT_PATH = None
CURRENT_TABLE_NAME = ""
SKIP_MODULE_MANAGEMENT = False
FORCE_SYSTEM = None
FORM_ID = None

# 配置变量
CONFIG = None
FORM_DATA_FILE = None
BASE_URL = None
LOGIN_USERNAME = None
LOGIN_PASSWORD = None
REQUEST_TIMEOUT_LOGIN = 10
REQUEST_TIMEOUT_LIST = 15
REQUEST_TIMEOUT_CODEGEN = 60
DISPLAY_TOKEN_LENGTH = 50
PAGE_SIZE = 50
PAGE_NO = 1
MAX_DISPLAY_RECORDS = 5

# 代码生成参数
JSP_MODE = "one"
JFORM_TYPE = "1"
PACKAGE_STYLE = "service"
VUE_STYLE = "vue3"
CODE_TYPES = "controller,service,dao,mapper,entity,vue"

def load_config():
    """加载配置文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'Code_Gen_Config.json')

    default_config = {
        "project": {
            "path_prefix": CrossPlatformUtils.get_default_project_prefix()
        },
        "server": {
            "base_url": os.environ.get('JEECG_BASE_URL', 'http://localhost:8080/jeecg-boot'),
            "username": os.environ.get('JEECG_USERNAME', 'admin'),
            "password": os.environ.get('JEECG_PASSWORD', '123456')
        },
        "timeouts": {
            "login": 10,
            "list": 15,
            "codegen": 60
        },
        "form": {
            "data_file": "Code_Gen_Guide.json"
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
                for section, values in user_config.items():
                    if section in default_config:
                        default_config[section].update(values)
                    else:
                        default_config[section] = values
        except Exception as e:
            safe_print(f"[WARN] 配置文件加载失败，使用默认配置: {e}")
    else:
        safe_print(f"[WARN] 配置文件不存在: {config_file}")
        safe_print(f"[TIP] 将使用默认配置运行")

    # 解析项目路径前缀
    original_path_prefix = default_config["project"]["path_prefix"]
    resolved_path_prefix = CrossPlatformUtils.resolve_path_prefix(original_path_prefix)
    default_config["project"]["path_prefix"] = resolved_path_prefix

    if original_path_prefix != resolved_path_prefix:
        safe_print(f"[FOLDER] 路径解析: {original_path_prefix} → {resolved_path_prefix}")

    # 解析环境变量
    def resolve_env_var(value):
        if isinstance(value, str) and value.startswith('$'):
            env_var = value[1:]
            env_value = os.environ.get(env_var)
            if env_value:
                return env_value
            else:
                safe_print(f"[WARN] 环境变量 {env_var} 未设置，使用默认值")
                return value
        return value

    default_config["server"]["base_url"] = resolve_env_var(default_config["server"]["base_url"])
    default_config["server"]["username"] = resolve_env_var(default_config["server"]["username"])
    default_config["server"]["password"] = resolve_env_var(default_config["server"]["password"])

    return default_config

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='JeecgBoot 第四步代码生成工具 v1.0')

    parser.add_argument('--config', '-c', default='Code_Gen_Config.json',
                       help='配置文件路径 (默认: Code_Gen_Config.json)')

    parser.add_argument('--module-name', '-m',
                       help='业务模块名称（如：hrms, crm, scm, oa, finance）')

    parser.add_argument('--form-config', '-f',
                       help='表单配置文件路径')

    parser.add_argument('--table-name', '-n',
                       help='表名（覆盖配置文件中的设置）')

    parser.add_argument('--project-path', '-p',
                       help='项目路径（覆盖配置文件中的设置）')

    parser.add_argument('--entity-name', '-e',
                       help='实体名称（覆盖配置文件中的设置）')

    parser.add_argument('--form-id', '-i',
                       help='表单ID（直接指定表单ID，跳过表单创建步骤）')

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出模式')

    parser.add_argument('--try-run', action='store_true',
                       help='试运行模式（只显示将要执行的操作，不实际执行）')

    return parser.parse_args()

def parse_table_name_components(table_name, business_entity=None):
    """解析表名并返回所有命名组件"""
    if not table_name:
        raise ValueError("表名不能为空")

    if not table_name.startswith('us_'):
        raise ValueError(f"表名格式错误: {table_name}，必须以us_开头")

    parts = table_name.split('_')

    if len(parts) < 4:
        raise ValueError(f"表名格式错误: {table_name}，必须包含至少4个部分")

    module_name = parts[1]
    sub_module = parts[2]
    business_scenario_parts = parts[3:]
    default_business_scenario = '_'.join(business_scenario_parts)

    if business_entity:
        entity_name = business_entity
        business_scenario = pascal_to_snake_case(business_entity)
    else:
        business_scenario = default_business_scenario
        entity_name = convert_to_java_entity_name(business_scenario)

    return {
        'module_name': module_name,
        'sub_module': sub_module,
        'business_scenario': business_scenario,
        'entity_name': entity_name
    }

def pascal_to_snake_case(pascal_str):
    """将PascalCase转换为snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', pascal_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def convert_to_java_entity_name(snake_case_str):
    """将snake_case转换为Java实体名（PascalCase）"""
    words = snake_case_str.split('_')
    return ''.join(word.capitalize() for word in words)

def get_business_entity_from_global_or_config(config_data=None):
    """获取业务实体名称"""
    global BUSINESS_ENTITY

    if (BUSINESS_ENTITY and
        BUSINESS_ENTITY != "defaultentity" and
        not BUSINESS_ENTITY.startswith('{{')):
        return BUSINESS_ENTITY

    if config_data:
        head = config_data.get('head', {})
        business_entity = head.get('business_entity')
        if business_entity:
            return business_entity

    return None

def extract_business_entity_from_config(config_file_path):
    """从配置文件提取业务实体"""
    safe_print(f"[LIST] 解析配置文件: {config_file_path}")

    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        safe_print(f"[OK] JSON格式解析成功")
    except json.JSONDecodeError as e:
        raise ValueError(f"[FAIL] 配置文件JSON格式错误: {e}")
    except Exception as e:
        raise ValueError(f"[FAIL] 读取配置文件失败: {e}")

    if not isinstance(config, dict):
        raise ValueError(f"[FAIL] 配置文件根节点必须是对象")

    if 'head' not in config:
        raise ValueError(f"[FAIL] 配置文件缺少head节点")

    head = config['head']
    business_entity = head.get('business_entity')
    if not business_entity:
        raise ValueError(f"[FAIL] head节点缺少business_entity字段")

    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', business_entity):
        raise ValueError(f"[FAIL] business_entity格式错误: '{business_entity}'，应为PascalCase格式")

    safe_print(f"[OK] business_entity验证通过: {business_entity}")

    return {
        'java_class_name': business_entity,
        'table_suffix': pascal_to_snake_case(business_entity),
        'url_path': pascal_to_snake_case(business_entity).replace('_', '-'),
        'frontend_path': pascal_to_snake_case(business_entity).replace('_', '-')
    }

def create_auth_headers(token):
    """创建标准的认证请求头"""
    return {
        'authorization': f'Bearer {token}',
        'x-access-token': token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def login_and_get_token():
    """登录并获取认证Token"""
    safe_print("\n[START] 正在登录...")

    try:
        login_data = {"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD}
        safe_print(f"   登录URL: {BASE_URL}/sys/mLogin")
        safe_print(f"   用户名: {LOGIN_USERNAME}")
        safe_print(f"   密码: {'*' * len(LOGIN_PASSWORD)}")

        response = requests.post(f"{BASE_URL}/sys/mLogin", json=login_data, timeout=REQUEST_TIMEOUT_LOGIN)

        safe_print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result['result']['token']
                user_info = result['result']['userInfo']
                safe_print(f"[OK] 登录成功: {user_info.get('realname', 'N/A')}")
                safe_print(f"   Token: {token[:DISPLAY_TOKEN_LENGTH]}...")
                return token
            else:
                safe_print(f"[FAIL] 登录失败: {result.get('message', '未知错误')}")
                return None
        else:
            safe_print(f"[FAIL] 登录请求失败: HTTP {response.status_code}")
            safe_print(f"   响应内容: {response.text}")
            return None

    except Exception as e:
        safe_print(f"[FAIL] 登录异常: {e}")
        return None

def get_form_id_by_table_name(token, table_name):
    """根据表名获取表单ID"""
    safe_print(f"\n[SEARCH] 正在获取表单ID...")
    safe_print(f"   表名: {table_name}")

    try:
        params = {'pageNo': PAGE_NO, 'pageSize': PAGE_SIZE, 'tableName': table_name}
        list_url = f"{BASE_URL}/online/cgform/head/list"

        safe_print(f"   查询URL: {list_url}")
        safe_print(f"   查询参数: {params}")
        safe_print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

        response = requests.get(list_url, params=params, headers=create_auth_headers(token), timeout=REQUEST_TIMEOUT_LIST)

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
                    if records:
                        safe_print(f"   现有表单列表:")
                        for i, record in enumerate(records[:MAX_DISPLAY_RECORDS]):
                            safe_print(f"      {i+1}. {record.get('tableName')} (ID: {record.get('id')})")
                        if len(records) > MAX_DISPLAY_RECORDS:
                            safe_print(f"      ... 还有 {len(records) - MAX_DISPLAY_RECORDS} 条记录")
                    else:
                        safe_print(f"   系统中没有找到任何表单")
                    return None

                safe_print(f"[OK] 表单ID: {form_id}")
                return form_id
            else:
                safe_print(f"[FAIL] 获取表单列表失败: {result.get('message', '未知错误')}")
                return None
        else:
            safe_print(f"[FAIL] 查询请求失败: HTTP {response.status_code}")
            safe_print(f"   响应内容: {response.text}")
            return None

    except Exception as e:
        safe_print(f"[FAIL] 获取表单ID异常: {e}")
        return None

def generate_code_with_form_id(token, form_id, table_name, form_config_data=None, verbose=False):
    """使用表单ID生成代码"""
    safe_print(f"\n[BUILD] 正在生成代码...")
    safe_print(f"   表单ID: {form_id}")
    safe_print(f"   表名: {table_name}")

    try:
        # 准备代码生成参数（按照JeecgBoot标准格式）
        codegen_data = build_standard_codegen_params(form_id, table_name, form_config_data)

        # 显示详细的代码生成参数信息
        print_codegen_parameters(codegen_data, form_config_data)

        # 如果是详细模式，显示完整的请求负载
        if verbose:
            print_request_payload(codegen_data)

        codegen_url = f"{BASE_URL}/online/cgform/api/codeGenerate"
        headers = create_auth_headers(token)

        safe_print(f"   [TOOL] 请求信息:")
        safe_print(f"      URL: {codegen_url}")
        safe_print(f"      方法: POST")
        safe_print(f"      Token: {token[:DISPLAY_TOKEN_LENGTH]}...")
        safe_print(f"      超时: {REQUEST_TIMEOUT_CODEGEN}秒")
        safe_print(f"      Content-Type: application/json")

        response = requests.post(codegen_url, json=codegen_data, headers=headers, timeout=REQUEST_TIMEOUT_CODEGEN)

        safe_print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                safe_print("[OK] 代码生成成功")
                safe_print(f"   响应消息: {result.get('message', 'N/A')}")
                return True
            else:
                safe_print(f"[FAIL] 代码生成失败: {result.get('message', '未知错误')}")
                safe_print(f"   完整响应: {result}")
                return False
        else:
            safe_print(f"[FAIL] 代码生成请求失败: HTTP {response.status_code}")
            safe_print(f"   响应内容: {response.text}")
            return False

    except Exception as e:
        safe_print(f"[FAIL] 代码生成异常: {e}")
        return False

def build_standard_codegen_params(form_id, table_name, form_config_data=None):
    """构建标准的JeecgBoot代码生成参数"""
    # 基础参数
    codegen_data = {
        "projectPath": PROJECT_PATH,
        "jspMode": JSP_MODE,
        "jformType": JFORM_TYPE,
        "entityName": BUSINESS_ENTITY,
        "entityPackage": SUBMODULE_NAME,
        "packageStyle": PACKAGE_STYLE,
        "vueStyle": VUE_STYLE,
        "codeTypes": CODE_TYPES,
        "code": form_id,
        "tableName": table_name
    }

    # 从表单配置中提取额外信息
    if form_config_data:
        head = form_config_data.get('head', {})

        # 添加表描述
        if head.get('tableTxt'):
            codegen_data["ftlDescription"] = head.get('tableTxt')

        # 添加临时表名（如果需要）
        codegen_data["tableName_tmp"] = table_name

        # 检查是否为主子表场景
        sub_list = form_config_data.get('subList', [])
        if sub_list:
            # 主子表场景，设置jformType为2，jspMode为jvxe
            codegen_data["jformType"] = "2"
            codegen_data["jspMode"] = "jvxe"

            # 添加子表列表
            codegen_data["subList"] = []
            for sub_table in sub_list:
                sub_item = {
                    "tableName": sub_table.get('tableName', ''),
                    "entityName": sub_table.get('entityName', ''),
                    "ftlDescription": sub_table.get('ftlDescription', ''),
                    "id": sub_table.get('id', '')
                }
                codegen_data["subList"].append(sub_item)

    return codegen_data

def print_codegen_parameters(codegen_data, form_config_data=None):
    """打印详细的代码生成参数信息（按照JeecgBoot标准格式）"""
    safe_print(f"   [LIST] 第四个接口提交参数详情 (JeecgBoot标准格式):")

    # 检查是否为主子表场景
    is_main_sub = codegen_data.get('jformType') == '2' and 'subList' in codegen_data

    if is_main_sub:
        safe_print(f"      ┌─ 主子表场景参数")
        safe_print(f"      │  projectPath     = {codegen_data.get('projectPath', 'N/A')}")
        safe_print(f"      │  jspMode         = {codegen_data.get('jspMode', 'N/A')} (主子表模式)")
        safe_print(f"      │  ftlDescription  = {codegen_data.get('ftlDescription', 'N/A')}")
        safe_print(f"      │  jformType       = {codegen_data.get('jformType', 'N/A')} (主子表)")
        safe_print(f"      │  tableName_tmp   = {codegen_data.get('tableName_tmp', 'N/A')}")
        safe_print(f"      │  entityName      = {codegen_data.get('entityName', 'N/A')}")
        safe_print(f"      │  entityPackage   = {codegen_data.get('entityPackage', 'N/A')}")
        safe_print(f"      │  packageStyle    = {codegen_data.get('packageStyle', 'N/A')}")
        safe_print(f"      │  vueStyle        = {codegen_data.get('vueStyle', 'N/A')}")
        safe_print(f"      │  codeTypes       = {codegen_data.get('codeTypes', 'N/A')}")
        safe_print(f"      │  code            = {codegen_data.get('code', 'N/A')}")
        safe_print(f"      │  tableName       = {codegen_data.get('tableName', 'N/A')}")

        # 显示子表信息
        sub_list = codegen_data.get('subList', [])
        if sub_list:
            safe_print(f"      └─ subList ({len(sub_list)}个子表):")
            for i, sub_table in enumerate(sub_list):
                prefix = "         ├─" if i < len(sub_list) - 1 else "         └─"
                safe_print(f"      {prefix} {sub_table.get('tableName', 'N/A')}")
                safe_print(f"         │    entityName     = {sub_table.get('entityName', 'N/A')}")
                safe_print(f"         │    ftlDescription = {sub_table.get('ftlDescription', 'N/A')}")
                safe_print(f"         │    id             = {sub_table.get('id', 'N/A')}")
    else:
        safe_print(f"      ┌─ 单表场景参数")
        safe_print(f"      │  projectPath     = {codegen_data.get('projectPath', 'N/A')}")
        safe_print(f"      │  jspMode         = {codegen_data.get('jspMode', 'N/A')} (单表模式)")
        safe_print(f"      │  ftlDescription  = {codegen_data.get('ftlDescription', 'N/A')}")
        safe_print(f"      │  jformType       = {codegen_data.get('jformType', 'N/A')} (单表)")
        safe_print(f"      │  entityName      = {codegen_data.get('entityName', 'N/A')}")
        safe_print(f"      │  entityPackage   = {codegen_data.get('entityPackage', 'N/A')}")
        safe_print(f"      │  packageStyle    = {codegen_data.get('packageStyle', 'N/A')}")
        safe_print(f"      │  vueStyle        = {codegen_data.get('vueStyle', 'N/A')}")
        safe_print(f"      │  codeTypes       = {codegen_data.get('codeTypes', 'N/A')}")
        safe_print(f"      │  code            = {codegen_data.get('code', 'N/A')}")
        safe_print(f"      └─ tableName       = {codegen_data.get('tableName', 'N/A')}")

    # 如果有表单配置数据，显示更多详细信息
    if form_config_data:
        print_form_config_details(form_config_data)

def print_form_config_details(form_config_data):
    """打印表单配置详细信息"""
    safe_print(f"   [DATABASE] 表单配置详情:")

    # 显示表头信息
    head = form_config_data.get('head', {})
    if head:
        safe_print(f"      ┌─ 表单基础信息")
        safe_print(f"      │  表名         = {head.get('tableName', 'N/A')}")
        safe_print(f"      │  表描述       = {head.get('tableTxt', 'N/A')}")
        safe_print(f"      │  业务实体     = {head.get('business_entity', 'N/A')}")
        safe_print(f"      │  表类型       = {head.get('tableType', 'N/A')}")
        safe_print(f"      │  表单分类     = {head.get('formCategory', 'N/A')}")
        safe_print(f"      │  主键类型     = {head.get('idType', 'N/A')}")
        safe_print(f"      │  是否分页     = {head.get('isPage', 'N/A')}")
        safe_print(f"      │  是否树形     = {head.get('isTree', 'N/A')}")
        safe_print(f"      │  表单模板     = {head.get('formTemplate', 'N/A')}")
        safe_print(f"      └─ 主题模板     = {head.get('themeTemplate', 'N/A')}")

    # 显示字段统计信息
    fields = form_config_data.get('fields', [])
    if fields:
        safe_print(f"      ┌─ 字段统计信息")
        safe_print(f"      │  总字段数     = {len(fields)}")

        # 统计不同类型的字段
        form_fields = [f for f in fields if f.get('isShowForm') == '1']
        list_fields = [f for f in fields if f.get('isShowList') == '1']
        query_fields = [f for f in fields if f.get('isQuery') == '1']
        required_fields = [f for f in fields if f.get('fieldMustInput') == '1']

        safe_print(f"      │  表单显示字段 = {len(form_fields)}")
        safe_print(f"      │  列表显示字段 = {len(list_fields)}")
        safe_print(f"      │  查询字段     = {len(query_fields)}")
        safe_print(f"      └─ 必填字段     = {len(required_fields)}")

        # 显示业务字段详情（排除系统字段）
        business_fields = [f for f in fields if not f.get('dbFieldName', '').startswith(('id', 'create_', 'update_', 'sys_', 'del_flag'))]
        if business_fields:
            safe_print(f"      ┌─ 业务字段详情 ({len(business_fields)}个)")
            for i, field in enumerate(business_fields[:10]):  # 最多显示10个字段
                field_name = field.get('dbFieldName', 'N/A')
                field_txt = field.get('dbFieldTxt', 'N/A')
                field_type = field.get('dbType', 'N/A')
                field_length = field.get('dbLength', 'N/A')
                is_required = '必填' if field.get('fieldMustInput') == '1' else '可选'
                is_show_form = '表单' if field.get('isShowForm') == '1' else ''
                is_show_list = '列表' if field.get('isShowList') == '1' else ''
                is_query = '查询' if field.get('isQuery') == '1' else ''

                display_flags = [flag for flag in [is_show_form, is_show_list, is_query] if flag]
                display_str = ','.join(display_flags) if display_flags else '隐藏'

                prefix = "│  " if i < len(business_fields) - 1 else "└─ "
                safe_print(f"      {prefix}{field_name:<20} = {field_txt} ({field_type}({field_length}), {is_required}, {display_str})")

            if len(business_fields) > 10:
                safe_print(f"      └─ ... 还有 {len(business_fields) - 10} 个字段")

    # 显示元数据信息
    metadata = form_config_data.get('metadata', {})
    if metadata:
        generation_info = metadata.get('generation_info', {})
        if generation_info:
            safe_print(f"      ┌─ 生成元数据")
            safe_print(f"      │  模块名       = {generation_info.get('module_name', 'N/A')}")
            safe_print(f"      │  子模块名     = {generation_info.get('submodule_name', 'N/A')}")
            safe_print(f"      │  推理策略     = {generation_info.get('inference_strategy', 'N/A')}")
            safe_print(f"      └─ 语义分析     = {generation_info.get('semantic_analysis', 'N/A')[:50]}...")

        derived_formats = metadata.get('derived_formats', {})
        if derived_formats:
            safe_print(f"      ┌─ 派生格式")
            safe_print(f"      │  表后缀       = {derived_formats.get('table_suffix', 'N/A')}")
            safe_print(f"      │  URL路径      = {derived_formats.get('url_path', 'N/A')}")
            safe_print(f"      └─ 前端路径     = {derived_formats.get('frontend_path', 'N/A')}")

def print_request_payload(codegen_data):
    """打印完整的请求负载（按照JeecgBoot标准格式排序）"""
    safe_print(f"   [WEB] 完整请求负载 (JeecgBoot标准JSON格式):")
    try:
        import json

        # 按照JeecgBoot标准格式重新排序参数
        ordered_data = {}

        # 标准参数顺序
        param_order = [
            "projectPath", "jspMode", "ftlDescription", "jformType",
            "tableName_tmp", "entityName", "entityPackage", "packageStyle",
            "vueStyle", "codeTypes", "code", "tableName", "subList"
        ]

        # 按顺序添加存在的参数
        for param in param_order:
            if param in codegen_data:
                ordered_data[param] = codegen_data[param]

        # 添加其他未在标准顺序中的参数
        for key, value in codegen_data.items():
            if key not in ordered_data:
                ordered_data[key] = value

        payload_json = json.dumps(ordered_data, indent=2, ensure_ascii=False)
        for line in payload_json.split('\n'):
            safe_print(f"      {line}")

        # 显示与标准格式的对比提示
        is_main_sub = codegen_data.get('jformType') == '2' and 'subList' in codegen_data
        if is_main_sub:
            safe_print(f"   [TIP] 这是主子表场景，包含 {len(codegen_data.get('subList', []))} 个子表")
        else:
            safe_print(f"   [TIP] 这是单表场景，jformType=1")

    except Exception as e:
        safe_print(f"      JSON序列化失败: {e}")
        safe_print(f"      原始数据: {codegen_data}")

def set_core_variables_from_table_name(table_name):
    """从表名设置核心变量"""
    global MODULE_NAME, SUBMODULE_NAME, BUSINESS_ENTITY
    global TABLE_NAME, PACKAGE_NAME, PROJECT_PATH, CURRENT_TABLE_NAME

    try:
        business_entity = get_business_entity_from_global_or_config()
        components = parse_table_name_components(table_name, business_entity)

        MODULE_NAME = components['module_name']
        SUBMODULE_NAME = components['sub_module']
        BUSINESS_ENTITY = components['entity_name']

        TABLE_NAME = table_name
        CURRENT_TABLE_NAME = table_name
        PACKAGE_NAME = f"org.jeecg.modules.{MODULE_NAME.lower()}.{SUBMODULE_NAME.lower()}"

        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        PROJECT_PATH = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{MODULE_NAME}"

        return True

    except Exception as e:
        safe_print(f"[FAIL] 从表名设置核心变量失败: {e}")
        return False

def print_core_variables():
    """打印核心变量信息"""
    safe_print(f"\n[LIST] 核心变量详情:")
    safe_print(f"   模块名/系统名称          = {MODULE_NAME or 'None'}")
    safe_print(f"   子模块名/系统模块        = {SUBMODULE_NAME or 'None'}")
    safe_print(f"   业务实体名称             = {BUSINESS_ENTITY or 'None'}")
    safe_print(f"   表名                     = {TABLE_NAME or 'None'}")
    safe_print(f"   包名                     = {PACKAGE_NAME or 'None'}")
    safe_print(f"   项目路径                 = {PROJECT_PATH or 'None'}")

def print_workflow_variables():
    """打印工作流变量信息"""
    safe_print(f"\n[CHART] 工作流变量信息:")
    safe_print(f"   BASE_URL                 = {BASE_URL}")
    safe_print(f"   LOGIN_USERNAME           = {LOGIN_USERNAME}")
    safe_print(f"   LOGIN_PASSWORD           = {'*' * len(LOGIN_PASSWORD)}")
    safe_print(f"   REQUEST_TIMEOUT_LOGIN    = {REQUEST_TIMEOUT_LOGIN}s")
    safe_print(f"   REQUEST_TIMEOUT_LIST     = {REQUEST_TIMEOUT_LIST}s")
    safe_print(f"   REQUEST_TIMEOUT_CODEGEN  = {REQUEST_TIMEOUT_CODEGEN}s")
    safe_print(f"   PAGE_SIZE                = {PAGE_SIZE}")
    safe_print(f"   PAGE_NO                  = {PAGE_NO}")
    safe_print(f"   DISPLAY_TOKEN_LENGTH     = {DISPLAY_TOKEN_LENGTH}")
    safe_print(f"   MAX_DISPLAY_RECORDS      = {MAX_DISPLAY_RECORDS}")

    safe_print(f"\n[PACKAGE] 代码生成参数:")
    safe_print(f"   JSP_MODE                 = {JSP_MODE}")
    safe_print(f"   JFORM_TYPE               = {JFORM_TYPE}")
    safe_print(f"   PACKAGE_STYLE            = {PACKAGE_STYLE}")
    safe_print(f"   VUE_STYLE                = {VUE_STYLE}")
    safe_print(f"   CODE_TYPES               = {CODE_TYPES}")

def fourth_step_workflow(form_config_data=None, verbose=False):
    """第四步代码生成工作流"""
    print("\n[START] 开始执行第四步代码生成工作流")
    print("=" * 50)

    # 打印工作流变量
    print_workflow_variables()
    print_core_variables()

    # 1. 登录获取Token
    token = login_and_get_token()
    if not token:
        safe_print("[FAIL] 登录失败，工作流终止")
        return False

    # 2. 获取表单ID（如果未提供）
    global FORM_ID
    if not FORM_ID:
        safe_print(f"[INFO] 未提供表单ID，将根据表名自动获取")
        FORM_ID = get_form_id_by_table_name(token, TABLE_NAME)
        if not FORM_ID:
            safe_print("[FAIL] 无法获取表单ID，工作流终止")
            safe_print("[TIP] 请确认:")
            safe_print("   1. 表名正确且表单已存在")
            safe_print("   2. 或使用 --form-id 参数直接指定表单ID")
            return False
    else:
        safe_print(f"[INFO] 使用指定的表单ID: {FORM_ID}")

    # 3. 代码生成
    success = generate_code_with_form_id(token, FORM_ID, TABLE_NAME, form_config_data, verbose)
    if success:
        safe_print("\n[SUCCESS] 第四步代码生成工作流执行成功")
        safe_print("=" * 50)
        return True
    else:
        safe_print("\n[FAIL] 第四步代码生成工作流执行失败")
        safe_print("=" * 50)
        return False

def main():
    """主函数"""
    args = parse_arguments()

    # 加载配置
    global CONFIG, FORM_DATA_FILE, BASE_URL, LOGIN_USERNAME, LOGIN_PASSWORD
    global REQUEST_TIMEOUT_LOGIN, REQUEST_TIMEOUT_LIST, REQUEST_TIMEOUT_CODEGEN, DISPLAY_TOKEN_LENGTH
    global PAGE_SIZE, PAGE_NO, MAX_DISPLAY_RECORDS
    global JSP_MODE, JFORM_TYPE, PACKAGE_STYLE, VUE_STYLE, CODE_TYPES
    global MODULE_NAME, SUBMODULE_NAME, BUSINESS_ENTITY, PROJECT_PATH, FORM_ID
    global SKIP_MODULE_MANAGEMENT, FORCE_SYSTEM, CURRENT_TABLE_NAME

    # 用于存储表单配置数据
    form_config_data = None

    if args.config != 'Code_Gen_Config.json':
        CONFIG = load_config_from_file(args.config)
    else:
        CONFIG = load_config()

    # 提取配置变量
    BASE_URL = CONFIG['server']['base_url']
    LOGIN_USERNAME = CONFIG['server']['username']
    LOGIN_PASSWORD = CONFIG['server']['password']

    REQUEST_TIMEOUT_LOGIN = CONFIG['timeouts']['login']
    REQUEST_TIMEOUT_LIST = CONFIG['timeouts']['list']
    REQUEST_TIMEOUT_CODEGEN = CONFIG['timeouts']['codegen']

    PAGE_SIZE = CONFIG['query']['page_size']
    PAGE_NO = CONFIG['query']['page_no']

    DISPLAY_TOKEN_LENGTH = CONFIG['display']['token_length']
    MAX_DISPLAY_RECORDS = CONFIG['display']['max_records']

    # 代码生成参数
    codegen_config = CONFIG['codegen']
    JSP_MODE = codegen_config['jsp_mode']
    JFORM_TYPE = codegen_config['jform_type']
    PACKAGE_STYLE = codegen_config['package_style']
    VUE_STYLE = codegen_config['vue_style']
    CODE_TYPES = codegen_config['code_types']

    # 设置全局标志
    SKIP_MODULE_MANAGEMENT = True  # 第四步不需要模块管理
    FORCE_SYSTEM = args.module_name

    # 显示工具信息
    print("JeecgBoot 第四步代码生成工具 v1.0")
    print("=" * 50)

    if args.module_name:
        safe_print(f"[TARGET] 指定业务模块: {args.module_name}")
    if args.form_config:
        safe_print(f"[LIST] 表单配置文件: {args.form_config}")
    if args.form_id:
        safe_print(f"[LIST] 指定表单ID: {args.form_id}")
        FORM_ID = args.form_id

    # 处理表单配置文件或表单ID
    if args.form_config:
        try:
            # 从配置文件提取业务实体
            formats = extract_business_entity_from_config(args.form_config)
            BUSINESS_ENTITY = formats['java_class_name']

            # 从配置文件中读取表名和模块信息
            with open(args.form_config, 'r', encoding='utf-8') as f:
                form_data = json.load(f)
                form_config_data = form_data  # 保存完整的表单配置数据
                table_name = form_data.get('head', {}).get('tableName', '')
                CURRENT_TABLE_NAME = table_name

                # 从metadata中获取模块信息
                metadata = form_data.get('metadata', {}).get('generation_info', {})
                if metadata.get('module_name'):
                    MODULE_NAME = metadata['module_name']
                if metadata.get('submodule_name'):
                    SUBMODULE_NAME = metadata['submodule_name']

                # 设置核心变量
                if table_name and set_core_variables_from_table_name(table_name):
                    safe_print("[OK] 从表名设置核心变量成功")
                else:
                    safe_print("[WARN] 从表名设置核心变量失败，使用metadata信息")
                    # 使用metadata信息设置变量
                    if MODULE_NAME and SUBMODULE_NAME:
                        TABLE_NAME = table_name
                        PACKAGE_NAME = f"org.jeecg.modules.{MODULE_NAME.lower()}.{SUBMODULE_NAME.lower()}"
                        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
                        PROJECT_PATH = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{MODULE_NAME}"

            safe_print("[OK] 从配置文件提取业务实体成功")

        except Exception as e:
            safe_print(f"[FAIL] 业务实体提取失败: {e}")
            return
    elif args.form_id:
        # 直接使用表单ID，需要其他参数
        FORM_ID = args.form_id
        if not args.table_name:
            safe_print("[FAIL] 使用表单ID时必须提供表名参数 --table-name")
            return
        CURRENT_TABLE_NAME = args.table_name

        # 尝试从表名解析模块信息
        try:
            if set_core_variables_from_table_name(args.table_name):
                safe_print("[OK] 从表名解析核心变量成功")
            else:
                safe_print("[FAIL] 从表名解析核心变量失败")
                return
        except Exception as e:
            safe_print(f"[FAIL] 表名解析失败: {e}")
            return
    else:
        safe_print("[FAIL] 必须提供配置文件参数 --form-config 或表单ID参数 --form-id")
        return

    # 处理模块名称和项目路径
    if FORCE_SYSTEM:
        MODULE_NAME = FORCE_SYSTEM
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        PROJECT_PATH = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{MODULE_NAME}"
    else:
        if not MODULE_NAME:
            project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
            PROJECT_PATH = f"{project_prefix}/jeecg-boot"

    # 命令行参数覆盖配置
    if args.project_path:
        PROJECT_PATH = args.project_path
    if args.entity_name:
        BUSINESS_ENTITY = args.entity_name

    # 试运行模式
    if args.try_run:
        safe_print("[SEARCH] 试运行模式 - 将显示操作但不执行")
        safe_print(f"[LIST] 配置文件: {args.config}")
        safe_print(f"[TARGET] 业务系统: {args.module_name or '自动识别'}")
        safe_print(f"[LIST] 表单配置: {args.form_config or '未指定'}")
        safe_print(f"[LIST] 表单ID: {args.form_id or '未指定'}")
        safe_print(f"[BUILD] 项目路径: {PROJECT_PATH}")
        safe_print(f"[PACKAGE] 实体名称: {BUSINESS_ENTITY}")

        print_core_variables()
        print_workflow_variables()

        safe_print(f"\n[TOOL] 将要执行的操作:")
        safe_print(f"   1. 登录到 {BASE_URL}")
        safe_print(f"   2. 使用表单ID {FORM_ID or '从配置文件获取'} 生成代码")
        safe_print(f"   3. 生成到项目路径: {PROJECT_PATH}")

        # 在试运行模式下也显示参数详情
        if FORM_ID and CURRENT_TABLE_NAME:
            safe_print(f"\n[PREVIEW] 试运行模式 - 参数预览:")
            codegen_data_preview = build_standard_codegen_params(FORM_ID, CURRENT_TABLE_NAME, form_config_data)
            print_codegen_parameters(codegen_data_preview, form_config_data)
            if args.verbose:
                print_request_payload(codegen_data_preview)

        return

    # 验证必需参数
    if not BUSINESS_ENTITY:
        safe_print("[FAIL] 缺少业务实体名称")
        return

    if not CURRENT_TABLE_NAME:
        safe_print("[FAIL] 缺少表名")
        return

    # 表单ID现在是可选的，如果没有提供会自动获取
    if FORM_ID:
        safe_print(f"[INFO] 将使用指定的表单ID: {FORM_ID}")
    else:
        safe_print(f"[INFO] 未指定表单ID，将根据表名自动获取: {CURRENT_TABLE_NAME}")

    # 执行第四步工作流
    success = fourth_step_workflow(form_config_data, args.verbose)

    if success:
        safe_print("\n[SUCCESS] 第四步代码生成完成！")
        safe_print(f"[TIP] 生成的代码位于: {PROJECT_PATH}")
        safe_print(f"[TIP] 实体名称: {BUSINESS_ENTITY}")
        safe_print(f"[TIP] 包名: {PACKAGE_NAME}")
        if form_config_data:
            fields_count = len(form_config_data.get('fields', []))
            business_fields = [f for f in form_config_data.get('fields', [])
                             if not f.get('dbFieldName', '').startswith(('id', 'create_', 'update_', 'sys_', 'del_flag'))]
            safe_print(f"[TIP] 总字段数: {fields_count}, 业务字段数: {len(business_fields)}")
    else:
        safe_print("\n[FAIL] 第四步代码生成失败！")
        safe_print("[TIP] 请检查配置和网络连接")

def load_config_from_file(config_file):
    """从指定文件加载配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        safe_print(f"[FAIL] 配置文件加载失败: {e}")
        return load_config()

if __name__ == "__main__":
    main()
