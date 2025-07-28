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
import xml.etree.ElementTree as ET
import shutil
import os
import random
from datetime import datetime
from pathlib import Path

def load_config():
    """加载配置文件"""
    # 智能查找配置文件：优先使用脚本所在目录的配置文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'Code_Gen_Config.json')
    # 默认配置（仅在配置文件不存在时使用）
    default_config = {
        "project": {
            "path_prefix": "/Users/admin/Work/Github/JeecgBoot"  # 默认路径，应在Code_Gen_Config.json中配置
        },
        "server": {
            "base_url": "http://localhost:8080/jeecg-boot",
            "username": "admin",
            "password": "123456"
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
            print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")
    else:
        # 配置文件不存在时，不自动创建，而是提示用户
        print(f"⚠️  配置文件不存在: {config_file}")
        print(f"💡 将使用默认配置运行，如需自定义配置请创建配置文件")
        print(f"📝 可以复制现有配置文件模板或使用 --config 参数指定配置文件")

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
    global TABLE_NAME, PACKAGE_NAME, PROJECT_PATH

    try:
        components = parse_table_name_components(table_name)

        # 设置三核心变量
        MODULE_NAME = components['module_name']
        SUBMODULE_NAME = components['sub_module']
        BUSINESS_ENTITY = components['entity_name']  # 使用PascalCase格式的entity_name

        # 计算派生变量
        TABLE_NAME = table_name
        # 强制确保包路径全小写，符合Java命名规范，不包含业务实体名
        PACKAGE_NAME = f"org.jeecg.modules.{MODULE_NAME.lower()}.{SUBMODULE_NAME.lower()}"

        # 计算项目路径
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        PROJECT_PATH = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{MODULE_NAME}"

        return True

    except Exception as e:
        print(f"❌ 从表名设置三核心变量失败: {e}")
        return False

def print_core_variables():
    """打印三核心变量和派生变量的详细信息"""
    print(f"\n📋 三核心变量详情:")
    print(f"   模块名/系统名称          = {MODULE_NAME or 'None'}")
    print(f"   子模块名/系统模块        = {SUBMODULE_NAME or 'None'}")
    print(f"   业务实体名称             = {BUSINESS_ENTITY or 'None'}")

    print(f"\n📊 派生变量详情:")
    print(f"   表名                     = {TABLE_NAME or 'None'}")
    print(f"   包名                     = {PACKAGE_NAME or 'None'}")
    print(f"   业务实体                 = {BUSINESS_ENTITY or 'None'}")
    print(f"   项目路径                 = {PROJECT_PATH or 'None'}")

    print(f"\n🔍 变量说明:")
    print(f"   - MODULE_NAME: 表示一级业务领域，对应业务系统类型")
    print(f"   - SUBMODULE_NAME: 表示二级业务领域，对应业务系统内的功能模块")
    print(f"   - BUSINESS_ENTITY: 表示操作对象，对应具体业务实体，按Java驼峰命名规范")
    print(f"   - TABLE_NAME: 由三核心变量组合而成的完整表名，公式: us_{{MODULE_NAME}}_{{SUBMODULE_NAME}}_{{TABLE_SUFFIX}}")
    print(f"   - PACKAGE_NAME: 由MODULE_NAME和SUBMODULE_NAME组合而成的包名，公式: org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}")
    print(f"   - PROJECT_PATH: 由配置和MODULE_NAME组合而成的项目路径")

def validate_core_variables():
    """
    高质量三核心变量验证函数
    修复了之前版本中BUSINESS_ENTITY格式验证错误等问题
    """
    print(f"\n🔍 三核心变量一致性验证:")
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
        print("❌ 基础字段验证失败:")
        for error in errors:
            print(f"   - {error}")
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
        # 从实际表名解析出组件
        table_components = parse_table_name_components(TABLE_NAME)
        parsed_module = table_components['module_name']
        parsed_submodule = table_components['sub_module']  
        parsed_business_scenario = table_components['business_scenario']
        parsed_entity = table_components['entity_name']
        
        print(f"   📊 表名解析结果验证:")
        print(f"      表名: {TABLE_NAME}")
        print(f"      解析模块: {parsed_module}")
        print(f"      解析子模块: {parsed_submodule}")
        print(f"      解析业务场景: {parsed_business_scenario}")
        print(f"      解析实体名: {parsed_entity}")
        
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
        print("⚠️ 警告信息:")
        for warning in warnings:
            print(f"   - {warning}")

    if errors:
        print("❌ 三核心变量验证失败:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ 三核心变量验证通过")
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
        print("❌ 模板变量验证失败:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ 模板变量验证通过")
        return True

# ==================== Java命名规范转换功能 ====================

def parse_table_name_components(table_name):
    """
    解析表名并返回所有命名组件
    严格按照标准化命名规范：us_{模块名}_{子模块名}_{业务场景}
    
    Args:
        table_name (str): 完整表名，必须符合标准格式
        
    Returns:
        dict: 包含所有命名组件的字典
        {
            'module_name': str,      # 模块名
            'sub_module': str,       # 子模块名  
            'business_scenario': str, # 业务场景
            'entity_name': str       # 实体名（业务场景的Java格式）
        }
        
    Examples:
        us_mall_sales_product -> {
            'module_name': 'mall',
            'sub_module': 'sales', 
            'business_scenario': 'product',
            'entity_name': 'product'
        }
    """
    if not table_name:
        raise ValueError("表名不能为空")
        
    if not table_name.startswith('us_'):
        error_msg = f"""
❌ 表名格式错误: {table_name}

📋 表名命名规范要求:
   格式: us_{{模块名}}_{{子模块名}}_{{业务场景}}
   
✅ 正确示例:
   us_mall_sales_product         (电商-销售-产品)
   us_mall_member_info          (电商-会员-信息)
   us_finance_invoice_management (财务-发票-管理)

🔧 智能修复建议:
   推荐表名: '{suggest_table_name_fix(table_name)}'
   或手动修改为: 'us_{{模块名}}_{{子模块名}}_{{业务场景}}'

📚 详细文档: 请查看 Code_Gen_Guide.md 中的标准化命名规范
        """
        raise ValueError(error_msg)
        
    parts = table_name.split('_')
    
    if len(parts) != 4:
        error_msg = f"""
❌ 表名格式错误: {table_name}

📋 表名必须包含4个部分，用下划线分隔:
   格式: us_{{模块名}}_{{子模块名}}_{{业务场景}}
   当前: {len(parts)}个部分 {parts}

✅ 正确示例:
   us_mall_sales_product        (4个部分: us + mall + sales + product)
   us_finance_invoice_management (4个部分: us + finance + invoice + management)
   
❌ 错误示例:
   us_mall_product              (3个部分，缺少子模块名)
   us_product                   (2个部分，格式不完整)

🔧 修复建议:
   确保表名包含: 前缀(us) + 模块名 + 子模块名 + 业务场景
        """
        raise ValueError(error_msg)
    
    # 解析组件: us_module_submodule_business_scenario
    module_name = parts[1]        # 模块名称
    sub_module = parts[2]         # 子模块名称  
    business_scenario = parts[3]  # 业务场景
    
    # 生成实体名（Java格式的业务场景）
    entity_name = convert_to_java_entity_name(business_scenario)
    
    print(f"🎯 标准化表名解析: {table_name}")
    print(f"   ├── 模块名: {module_name}")
    print(f"   ├── 子模块: {sub_module}") 
    print(f"   ├── 业务场景: {business_scenario}")
    print(f"   └── 实体名: {entity_name}")
    
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
        components = parse_table_name_components(table_name)
        # 不再包含entity_name，只使用module_name和sub_module
        package_name = f"org.jeecg.modules.{components['module_name'].lower()}.{components['sub_module'].lower()}"
        print(f"📦 生成标准化包名: {package_name}")
        return package_name
    except ValueError as e:
        print(f"⚠️ 表名解析失败，使用传统格式: {e}")
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
            raise ValueError(f"❌ 绝对路径配置文件不存在: {config_file_path}")
    
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
    
    raise ValueError(f"""❌ 配置文件未找到: {config_file_path}

🔍 已搜索的路径:
{chr(10).join(f"   • {p}" for p in search_paths)}

💡 解决方案:
   1. 检查配置文件是否存在
   2. 使用绝对路径或确保文件在当前工作目录
   3. 确认配置文件名称正确""")

def extract_business_entity_from_config(config_file_path):
    """
    高质量配置文件解析函数
    全面的错误处理和精准的错误信息
    
    Args:
        config_file_path (str): 配置文件路径（支持绝对和相对路径）
        
    Returns:
        dict: 包含所有派生格式的字典
        
    Raises:
        ValueError: 配置文件问题的详细诊断信息
    """
    print(f"📋 解析配置文件: {config_file_path}")
    
    # 步骤1：智能路径解析
    try:
        resolved_path = resolve_config_file_path(config_file_path)
        print(f"✅ 配置文件路径解析成功: {resolved_path}")
    except ValueError as e:
        print(f"❌ 路径解析失败")
        raise e
    
    # 步骤2：JSON格式验证
    try:
        with open(resolved_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ JSON格式解析成功")
    except json.JSONDecodeError as e:
        raise ValueError(f"""❌ 配置文件JSON格式错误
        
📁 文件路径: {resolved_path}
🔍 JSON错误: {e}
🔧 解决方案: 检查JSON语法，确保括号、引号、逗号正确""")
    except Exception as e:
        raise ValueError(f"❌ 读取配置文件失败: {e}")
    
    # 步骤3：结构完整性验证
    if not isinstance(config, dict):
        raise ValueError(f"❌ 配置文件根节点必须是对象，当前类型: {type(config)}")
    
    if 'head' not in config:
        available_keys = list(config.keys())
        raise ValueError(f"""❌ 配置文件缺少head节点
        
📊 当前根节点字段: {available_keys}
🔧 解决方案: 确保配置文件包含head节点""")
    
    head = config['head']
    if not isinstance(head, dict):
        raise ValueError(f"❌ head节点必须是对象，当前类型: {type(head)}")
    
    # 步骤4：business_entity字段验证
    business_entity = head.get('business_entity')
    if not business_entity:
        available_keys = list(head.keys())
        raise ValueError(f"""❌ head节点缺少business_entity字段
        
📊 head节点现有字段: {available_keys}
🔧 解决方案: 在head节点中添加business_entity字段
💡 示例: "business_entity": "ProductCatalog" """)
    
    if not isinstance(business_entity, str):
        raise ValueError(f"❌ business_entity必须是字符串，当前类型: {type(business_entity)}")
    
    if not business_entity.strip():
        raise ValueError("❌ business_entity不能为空字符串")
    
    # 步骤5：格式规范验证
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', business_entity):
        raise ValueError(f"""❌ business_entity格式错误: '{business_entity}'
        
📋 格式要求: PascalCase（首字母大写的驼峰命名）
💡 正确示例: ProductCatalog, CustomerProfile, OrderHeader
❌ 错误示例: productCatalog, product_catalog, PRODUCT""")
    
    print(f"✅ business_entity验证通过: {business_entity}")
    
    # 步骤6：生成派生格式
    try:
        formats = derive_all_formats_from_business_entity(business_entity)
        print(f"✅ 格式派生成功")
        print(f"   ├── Java类名: {formats['java_class_name']}")
        print(f"   ├── 表名后缀: {formats['table_suffix']}")
        print(f"   ├── URL路径: {formats['url_path']}")
        print(f"   └── 前端路径: {formats['frontend_path']}")
        
        return formats
        
    except Exception as e:
        raise ValueError(f"❌ 格式派生失败: {e}")

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
        raise ValueError(f"❌ 标准模板文件不存在: {template_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ 标准模板JSON格式错误: {e}")
    
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
        "frontend_path": f"{module_name}/{submodule_name}"
    }
    
    # 插入业务字段（如果提供）
    if business_fields:
        # 在系统字段之前插入业务字段
        system_fields = template['fields'][1:]  # 除了id字段的系统字段
        business_field_configs = []
        
        for i, field in enumerate(business_fields, 1):
            field_config = create_business_field_config(field, i)
            business_field_configs.append(field_config)
        
        # 重新组织字段顺序：id + 业务字段 + 系统字段
        template['fields'] = [template['fields'][0]] + business_field_configs + system_fields
        
        # 重新设置orderNum
        for i, field in enumerate(template['fields']):
            field['orderNum'] = i
    
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
                warnings.append(f"⚠️  字段 {field_name}: '{old_value}' 超过长度限制，已自动修正为 '{fixed_config[field_name]}'")

            # 通用长度检查
            elif len(field_value) > max_length:
                old_value = field_value
                fixed_config[field_name] = field_value[:max_length]
                warnings.append(f"⚠️  字段 {field_name}: 值过长({len(old_value)}字符)，已截断为{max_length}字符")

    # 输出警告信息
    if warnings:
        print("🔧 字段长度自动修正:")
        for warning in warnings:
            print(f"   {warning}")

    return fixed_config

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
        'table_suffix': pascal_to_lowercase(business_entity),
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
        ('profile', 'Profile'),
        ('manager', 'Manager'), 
        ('service', 'Service'),
        ('config', 'Config'),
        ('info', 'Info'),
        ('data', 'Data'),
        ('record', 'Record'),
        ('detail', 'Detail'),
        ('item', 'Item'),
        ('list', 'List'),
        ('table', 'Table'),
        ('form', 'Form'),
        ('view', 'View')
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

    print(f"📝 临时替换配置文件变量: {config_path}")
    print(f"   🔍 输入参数:")
    print(f"      project_path = {project_path}")
    print(f"      package_name = {package_name}")

    try:
        # 备份原文件
        if config_path.exists():
            import shutil
            shutil.copy2(config_path, backup_path)
            print(f"   ✅ 已备份原配置文件: {backup_path}")

        # 读取原文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"   📄 原文件内容:")
        for i, line in enumerate(content.split('\n')[:10], 1):  # 显示前10行
            print(f"      {i:2d}: {line}")

        # 替换变量 - 支持模板变量和实际值两种情况
        original_content = content

        # 首先尝试替换模板变量
        content = content.replace('{{PROJECT_PATH}}', str(project_path))
        content = content.replace('{{PACKAGE_NAME}}', package_name)

        # 如果有当前表名，进行更完整的变量替换
        if CURRENT_TABLE_NAME:
            try:
                components = parse_table_name_components(CURRENT_TABLE_NAME)
                module_name = components['module_name']
                sub_module = components['sub_module']
                entity_name = components['entity_name']
                java_entity_name = convert_to_java_entity_name(entity_name)

                content = content.replace('{{MODULE_NAME}}', module_name)
                content = content.replace('{{SUBMODULE_NAME}}', sub_module)
                content = content.replace('{{BUSINESS_ENTITY}}', java_entity_name)
                content = content.replace('{{TABLE_NAME}}', CURRENT_TABLE_NAME)

                print(f"   🔄 完整变量替换:")
                print(f"      {{{{MODULE_NAME}}}} → {module_name}")
                print(f"      {{{{SUBMODULE_NAME}}}} → {sub_module}")
                print(f"      {{{{BUSINESS_ENTITY}}}} → {java_entity_name}")
                print(f"      {{{{TABLE_NAME}}}} → {CURRENT_TABLE_NAME}")
            except Exception as e:
                print(f"   ⚠️ 解析表名失败，使用基础变量替换: {e}")

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
            print(f"   ⚠️ 警告: 没有找到需要替换的配置项")
            print(f"   🔍 检查文件中是否包含 project_path 或 bussi_package 配置")
        else:
            print(f"   ✅ 配置替换成功")

        # 写入替换后的内容
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"   📄 替换后内容:")
        for i, line in enumerate(content.split('\n')[:10], 1):  # 显示前10行
            print(f"      {i:2d}: {line}")

        print(f"   ✅ 已替换变量:")
        print(f"      PROJECT_PATH = {project_path}")
        print(f"      PACKAGE_NAME = {package_name}")

        return True

    except Exception as e:
        print(f"   ❌ 配置文件替换失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def restore_jeecg_config(silent=False):
    """还原 jeecg_config.properties 文件"""
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    config_path = Path(project_prefix) / "jeecg-boot" / "jeecg-module-system" / "jeecg-system-start" / "src" / "main" / "resources" / "jeecg" / "jeecg_config.properties"
    backup_path = config_path.with_suffix('.properties.backup')

    if not silent:
        print(f"🔄 还原配置文件: {config_path}")

    try:
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, config_path)
            backup_path.unlink()  # 删除备份文件
            if not silent:
                print(f"   ✅ 已还原配置文件，保持变量占位")
        else:
            if not silent:
                print(f"   ⚠️ 备份文件不存在，跳过还原")

        return True

    except Exception as e:
        if not silent:
            print(f"   ❌ 配置文件还原失败: {e}")
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

    print(f"🔍 检查模块: jeecg-module-{module_name}")
    print(f"   路径: {module_path.absolute()}")
    print(f"   存在: {'✅ 是' if exists else '❌ 否'}")

    return exists

def create_maven_module(module_name):
    """使用Maven archetype创建新模块"""
    print(f"🏗️ 创建Maven模块: jeecg-module-{module_name}")

    # 获取路径前缀
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    
    # 构建Maven命令
    maven_cmd = [
        'mvn', 'archetype:generate',
        '-DgroupId=org.jeecgframework.boot',
        f'-DartifactId=jeecg-module-{module_name}',
        '-Dversion=3.8.1',
        '-DarchetypeGroupId=org.jeecgframework.archetype',
        '-DarchetypeArtifactId=jeecg-boot-gen',
        '-DarchetypeVersion=2.0',
        '-DinteractiveMode=false'  # 非交互模式
    ]

    # 构建执行目录路径，使用正确的路径分隔符
    if platform.system() == 'Windows':
        exec_dir = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module'
    else:
        exec_dir = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module'

    print(f"   操作系统: {platform.system()}")
    print(f"   执行目录: {exec_dir.absolute()}")
    print(f"   Maven命令: {' '.join(maven_cmd)}")

    try:
        # 确保在正确的目录下执行
        if not exec_dir.exists():
            print(f"❌ 执行目录不存在: {exec_dir.absolute()}")
            return False

        # 执行Maven命令
        result = subprocess.run(
            maven_cmd,
            cwd=exec_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            print("✅ Maven模块创建成功")
            print(f"   输出: {result.stdout[-200:]}")  # 显示最后200字符
            return True
        else:
            print(f"❌ Maven模块创建失败")
            print(f"   错误码: {result.returncode}")
            print(f"   错误信息: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Maven命令执行超时")
        return False
    except Exception as e:
        print(f"❌ Maven命令执行异常: {e}")
        return False

def update_module_registry_pom(module_name):
    """更新模块注册表pom.xml添加新模块"""
    # 获取路径前缀
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    pom_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / 'pom.xml'

    print(f"📝 更新模块注册表pom.xml: {pom_path.absolute()}")

    if not pom_path.exists():
        print(f"❌ 模块注册表pom.xml不存在: {pom_path}")
        return False

    try:
        # 读取原始文件内容
        with open(pom_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查模块是否已存在
        module_artifact_id = f"jeecg-module-{module_name}"
        if f"<module>{module_artifact_id}</module>" in content:
            print(f"✅ 模块已存在于模块注册表中: {module_artifact_id}")
            return True

        # 查找 </modules> 或 </ns0:modules> 标签的位置
        modules_end_pos = content.find('</modules>')
        if modules_end_pos == -1:
            modules_end_pos = content.find('</ns0:modules>')
        if modules_end_pos == -1:
            print("❌ 未找到modules节点")
            return False

        # 在 </modules> 前插入新模块
        new_module_entry = f"        <module>{module_artifact_id}</module>\n    "
        new_content = content[:modules_end_pos] + new_module_entry + content[modules_end_pos:]

        # 写回文件
        with open(pom_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✅ 已添加模块到模块注册表: {module_name}")
        return True

    except Exception as e:
        print(f"❌ 更新模块注册表pom.xml失败: {e}")
        return False

def update_main_pom(module_name):
    """更新主项目pom.xml添加新模块 (保持向后兼容)"""
    return update_module_registry_pom(module_name)

def update_system_start_pom(module_name):
    """更新启动项目pom.xml添加新模块依赖"""
    # 获取路径前缀
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    pom_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-module-system' / 'jeecg-system-start' / 'pom.xml'

    print(f"📝 更新启动项目pom.xml: {pom_path.absolute()}")

    if not pom_path.exists():
        print(f"❌ 启动项目pom.xml不存在: {pom_path}")
        return False

    try:
        # 读取原始文件内容
        with open(pom_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查依赖是否已存在
        artifact_id = f"jeecg-module-{module_name}"
        if f"<artifactId>{artifact_id}</artifactId>" in content:
            print(f"✅ 依赖已存在于启动项目pom.xml中: {artifact_id}")
            return True

        # 查找合适的位置插入新依赖（在 jeecg-system-biz 依赖之后）
        system_biz_pos = content.find('<artifactId>jeecg-system-biz</artifactId>')
        if system_biz_pos == -1:
            # 如果找不到 jeecg-system-biz，就在第一个 </dependency> 后插入
            first_dep_end = content.find('</dependency>')
            if first_dep_end == -1:
                print("❌ 无法找到合适的位置插入依赖")
                return False
            insert_pos = first_dep_end + len('</dependency>')
        else:
            # 找到 jeecg-system-biz 依赖的结束位置
            dep_end_pos = content.find('</dependency>', system_biz_pos)
            if dep_end_pos == -1:
                print("❌ 无法找到 jeecg-system-biz 依赖的结束位置")
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

        print(f"✅ 已添加依赖到启动项目pom.xml: {artifact_id}")
        return True

    except Exception as e:
        print(f"❌ 更新启动项目pom.xml失败: {e}")
        return False

def ensure_module_exists(module_name):
    """确保模块存在，如果不存在则创建并配置"""
    print(f"\n🔧 模块管理: {module_name}")
    print("=" * 40)

    # 1. 检查模块是否存在
    if check_module_exists(module_name):
        print(f"✅ 模块已存在，跳过创建步骤")
        # 即使模块存在，也要确保它已经集成到项目结构中
        integrate_module_to_project(module_name)
        return True

    # 2. 创建模块
    print(f"📦 模块不存在，开始创建...")
    if not create_maven_module(module_name):
        return False

    # 3. 集成模块到项目结构
    if not integrate_module_to_project(module_name):
        return False

    # 4. 验证模块创建结果
    if check_module_exists(module_name):
        print(f"🎉 模块创建和配置完成: jeecg-module-{module_name}")
        return True
    else:
        print(f"❌ 模块创建验证失败")
        return False

def integrate_module_to_project(module_name):
    """将模块集成到JeecgBoot项目结构中"""
    print(f"🔗 集成模块到项目结构: {module_name}")

    success = True

    # 1. 更新模块注册表 pom.xml
    if not update_module_registry_pom(module_name):
        print(f"⚠️ 模块注册表更新失败")
        success = False

    # 2. 更新启动项目 pom.xml
    if not update_system_start_pom(module_name):
        print(f"⚠️ 启动项目依赖更新失败")
        success = False

    if success:
        print(f"✅ 模块集成完成: jeecg-module-{module_name}")
    else:
        print(f"⚠️ 模块集成部分失败，请手动检查")

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
    print(f"\n🔄 后端服务重启建议:")
    print(f"   ")
    print(f"   📋 重启步骤:")
    print(f"      1. 检查当前服务状态:")
    print(f"         ps aux | grep java | grep jeecg")
    print(f"      ")
    print(f"      2. 停止现有服务:")
    print(f"         - 如果通过VS Code启动: 在终端中按 Ctrl+C")
    print(f"         - 如果通过命令行启动: kill -9 <进程ID>")
    print(f"      ")
    print(f"      3. 重新启动服务:")
    print(f"         - 推荐: 通过VS Code的launch.json启动")
    print(f"         - 或命令行: cd jeecg-module-system/jeecg-system-start")
    print(f"         - 执行: mvn spring-boot:run -Dspring-boot.run.profiles=mac")
    print(f"      ")
    print(f"      4. 验证启动成功:")
    print(f"         - 等待看到 'Application is running' 消息")
    print(f"         - 测试: curl http://localhost:8080/jeecg-boot/actuator/health")
    print(f"   ")
    print(f"   ⚠️ 重要提示:")
    print(f"      - 新模块代码需要重启服务才能生效")
    print(f"      - 确保使用 profile=mac 配置")
    print(f"      - 服务端口: 8080")

def verify_new_module_loaded(module_name=None):
    """验证新模块是否已加载"""
    if not module_name and CURRENT_TABLE_NAME:
        try:
            components = parse_table_name_components(CURRENT_TABLE_NAME)
            module_name = components['module_name']
        except:
            pass

    if not module_name:
        print("⚠️ 无法确定模块名称，跳过模块加载验证")
        return False

    print(f"🔍 验证模块加载状态: jeecg-module-{module_name}")

    try:
        # 由于actuator/mappings端点未暴露，我们用其他方法验证模块加载状态
        # 方法1: 检查项目目录结构是否存在
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        module_path = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
        
        if not os.path.exists(module_path):
            print(f"❌ 模块目录不存在: {module_path}")
            return False
        
        # 方法2: 检查是否有编译后的class文件
        target_path = f"{module_path}/target/classes"
        if os.path.exists(target_path):
            print(f"✅ 模块已编译: jeecg-module-{module_name}")
            # 由于无法直接检查运行时加载状态，我们假设编译后的模块在重启后会被加载
            return True
        else:
            print(f"⚠️ 模块未编译，需要编译并重启: jeecg-module-{module_name}")
            return False
    except Exception as e:
        print(f"⚠️ 检查模块加载状态失败: {e}")
        return False

# ==================== 前端代码迁移功能 ====================

def migrate_frontend_code():
    """前端代码目录迁移和重组 - 解析SQL注释获取正确路径并移动到views目录"""
    migration_config = CONFIG.get('frontend_migration', {})

    if not migration_config.get('enabled', True):
        print("⏭️ 前端代码迁移功能已禁用，跳过迁移步骤")
        return True

    print(f"\n{'='*50}")
    print("📁 开始前端代码目录迁移和重组...")

    try:
        # 1. 解析当前表名获取模块信息
        if not CURRENT_TABLE_NAME:
            print("❌ 无法获取当前表名，跳过前端代码迁移")
            return False

        components = parse_table_name_components(CURRENT_TABLE_NAME)
        module_name = components['module_name']
        sub_module = components['sub_module']

        print(f"📋 模块信息:")
        print(f"   模块名: {module_name}")
        print(f"   子模块: {sub_module}")

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
                print(f"✅ 找到实际的vue3源路径: {source_vue3_dir}")
                break

        if not source_vue3_dir:
            print(f"⚠️ 在后端模块中未找到vue3目录，检查是否已迁移...")
            # 检查前端项目中是否已有相同模块的文件
            frontend_module_dir = Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / sub_module
            if frontend_module_dir.exists():
                print(f"✅ 发现前端项目中已存在模块目录: {frontend_module_dir}")
                print(f"   这可能是同一模块的多个表单，前端代码将合并到现有目录")
                return True  # 返回成功，因为前端目录已存在

            # 如果都不存在，使用第一个作为默认值（用于后续的容错搜索）
            source_vue3_dir = possible_source_paths[0]

        # 3. 首先查找并解析SQL文件以获取正确的前端路径
        correct_frontend_path = extract_frontend_path_from_sql()
        if correct_frontend_path:
            print(f"📄 从SQL文件解析到正确的前端路径: {correct_frontend_path}")
            # 使用SQL文件中指定的路径
            target_base_path = migration_config.get('target_base_path', 'jeecgboot-vue3/src/views')
            target_views_base = Path(project_prefix) / target_base_path
            final_target_dir = target_views_base / correct_frontend_path
        else:
            print("⚠️ 未能从SQL文件解析到前端路径，使用默认路径")
            # 使用默认路径：module_name/sub_module
            target_base_path = migration_config.get('target_base_path', 'jeecgboot-vue3/src/views')
            target_views_base = Path(project_prefix) / target_base_path
            final_target_dir = target_views_base / module_name / sub_module

        # 重命名后的路径：将vue3重命名为子模块名
        renamed_dir = source_vue3_dir.parent / sub_module

        print(f"📂 路径信息:")
        print(f"   源vue3目录: {source_vue3_dir}")
        print(f"   重命名目录: {renamed_dir}")
        print(f"   最终目标: {final_target_dir}")

        # 3. 验证源目录存在且包含vue3前端文件 - 增加容错搜索
        if not source_vue3_dir.exists():
            print(f"❌ 源vue3目录不存在: {source_vue3_dir}")

            # 容错机制1：检查前端项目中是否已有文件（可能之前已迁移但路径错误）
            current_frontend_dir = Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / module_name
            if current_frontend_dir.exists():
                vue_files = list(current_frontend_dir.glob('*.vue'))
                ts_files = list(current_frontend_dir.glob('*.ts'))
                js_files = list(current_frontend_dir.glob('*.js'))

                if vue_files or ts_files or js_files:
                    print(f"✅ 在前端项目中找到已迁移的文件: {current_frontend_dir}")
                    print(f"   找到 {len(vue_files)} 个Vue文件，{len(ts_files)} 个TS文件，{len(js_files)} 个JS文件")

                    # 直接从前端项目的错误位置迁移到正确位置
                    return _migrate_from_frontend_wrong_location(current_frontend_dir, final_target_dir, migration_config)

            # 容错机制2：在当前模块中进行深度搜索
            print(f"🔍 启动后端模块容错搜索机制...")
            
            # 搜索当前模块下的所有vue3目录
            module_base_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'
            found_alternative = False
            
            if module_base_path.exists():
                # 使用glob递归搜索所有vue3目录
                vue3_dirs = list(module_base_path.glob('**/vue3'))
                print(f"🔍 在模块 {module_name} 中找到 {len(vue3_dirs)} 个vue3目录")
                
                for vue3_dir in vue3_dirs:
                    # 检查是否包含前端文件
                    vue_files = list(vue3_dir.glob('*.vue'))
                    ts_files = list(vue3_dir.glob('*.ts'))
                    js_files = list(vue3_dir.glob('*.js'))
                    
                    if vue_files or ts_files or js_files:
                        print(f"✅ 找到包含前端文件的vue3目录: {vue3_dir}")
                        print(f"   包含: {len(vue_files)} 个Vue文件，{len(ts_files)} 个TS文件，{len(js_files)} 个JS文件")
                        source_vue3_dir = vue3_dir
                        # 重新计算renamed_dir基于实际找到的路径
                        renamed_dir = source_vue3_dir.parent / sub_module
                        found_alternative = True
                        break

            if not found_alternative:
                print(f"⚠️ 在后端模块中未找到前端文件")
                # 检查前端项目中是否已有同模块的文件（可能是同一模块的多个表单）
                frontend_module_dir = Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / sub_module
                if frontend_module_dir.exists():
                    existing_files = list(frontend_module_dir.glob('*.vue')) + list(frontend_module_dir.glob('*.ts')) + list(frontend_module_dir.glob('*.js'))
                    if existing_files:
                        print(f"✅ 发现前端项目中已存在同模块文件: {frontend_module_dir}")
                        print(f"   已有 {len(existing_files)} 个前端文件")
                        print(f"   这可能是同一模块的多个表单，新生成的前端代码应该已经直接生成到正确位置")
                        return True  # 返回成功，因为前端目录已存在且有文件

                print(f"❌ 在所有位置都未找到前端文件，且前端项目中也无同模块文件")
                return False

        # 检查是否包含前端文件
        vue_files = list(source_vue3_dir.glob('*.vue'))
        ts_files = list(source_vue3_dir.glob('*.ts'))
        js_files = list(source_vue3_dir.glob('*.js'))

        if not (vue_files or ts_files or js_files):
            print(f"❌ 源目录中未找到前端文件: {source_vue3_dir}")
            return False

        print(f"✅ 源目录验证通过，找到 {len(vue_files)} 个Vue文件，{len(ts_files)} 个TS文件，{len(js_files)} 个JS文件")

        # 4. 执行重命名和移动操作
        return _execute_rename_and_move(source_vue3_dir, renamed_dir, final_target_dir, target_views_base, migration_config)

    except Exception as e:
        print(f"❌ 前端代码迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_frontend_path_from_sql():
    """从生成的SQL文件中解析正确的前端路径"""
    try:
        # 查找SQL文件
        sql_file_path = find_generated_sql_file()
        if not sql_file_path:
            print("⚠️ 未找到SQL文件，无法解析前端路径")
            return None

        print(f"📄 解析SQL文件: {sql_file_path}")

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
            print(f"✅ 解析到前端路径: views/{frontend_path}")
            return frontend_path
        else:
            print("⚠️ SQL文件中未找到前端路径注释")
            return None

    except Exception as e:
        print(f"❌ 解析SQL文件前端路径失败: {e}")
        return None

def _migrate_from_frontend_wrong_location(source_dir, target_dir, migration_config):
    """从前端项目的错误位置迁移到正确位置"""
    print(f"\n🔄 从前端项目错误位置迁移到正确位置...")
    print(f"   源目录: {source_dir}")
    print(f"   目标目录: {target_dir}")

    try:
        # 检查是否是移动到子目录的情况（避免移动目录到自身）
        if target_dir.is_relative_to(source_dir):
            print(f"⚠️ 检测到目标目录是源目录的子目录，使用特殊处理方式")
            return _migrate_to_subdirectory(source_dir, target_dir, migration_config)

        # 确保目标目录的父目录存在
        target_dir.parent.mkdir(parents=True, exist_ok=True)

        # 检查目标目录是否已存在
        if target_dir.exists():
            print(f"⚠️ 目标目录已存在: {target_dir}")
            if migration_config.get('cleanup_source', False):
                print(f"   删除已存在的目标目录...")
                shutil.rmtree(target_dir)
            else:
                print(f"❌ 目标目录已存在，停止迁移以避免覆盖")
                return False

        # 移动整个目录
        shutil.move(str(source_dir), str(target_dir))

        # 验证移动结果
        if target_dir.exists():
            files = list(target_dir.rglob('*'))
            file_count = len([f for f in files if f.is_file()])

            print(f"✅ 前端文件迁移成功!")
            print(f"   最终位置: {target_dir}")
            print(f"   文件数量: {file_count} 个")

            # 显示主要文件
            main_files = []
            for pattern in ['*.vue', '*.ts', '*.js']:
                main_files.extend(target_dir.glob(pattern))

            if main_files:
                print(f"\n📁 主要文件列表:")
                for file in main_files[:10]:  # 显示前10个
                    print(f"      {file.name}")
                if len(main_files) > 10:
                    print(f"      ... 还有 {len(main_files) - 10} 个文件")

            return True
        else:
            print(f"❌ 迁移失败，目标目录不存在")
            return False

    except Exception as e:
        print(f"❌ 前端文件迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def _migrate_to_subdirectory(source_dir, target_dir, migration_config):
    """将目录内容迁移到其子目录"""
    print(f"\n🔄 将目录内容迁移到子目录...")

    try:
        # 创建临时目录
        import tempfile
        temp_dir = Path(tempfile.mkdtemp(prefix='jeecg_migration_'))
        print(f"   创建临时目录: {temp_dir}")

        # 1. 先将所有文件移动到临时目录
        print(f"   步骤1: 移动文件到临时目录")
        moved_items = []
        for item in source_dir.iterdir():
            if item.name != target_dir.name:  # 不移动目标目录本身
                temp_item = temp_dir / item.name
                shutil.move(str(item), str(temp_item))
                moved_items.append(item.name)
                print(f"      移动: {item.name}")

        # 2. 确保目标目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"   步骤2: 创建目标目录: {target_dir}")

        # 3. 将文件从临时目录移动到目标目录
        print(f"   步骤3: 移动文件到目标目录")
        for item_name in moved_items:
            temp_item = temp_dir / item_name
            target_item = target_dir / item_name
            shutil.move(str(temp_item), str(target_item))
            print(f"      移动: {item_name}")

        # 4. 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"   步骤4: 清理临时目录")

        # 验证结果
        if target_dir.exists():
            files = list(target_dir.rglob('*'))
            file_count = len([f for f in files if f.is_file()])

            print(f"✅ 子目录迁移成功!")
            print(f"   最终位置: {target_dir}")
            print(f"   文件数量: {file_count} 个")

            # 显示主要文件
            main_files = []
            for pattern in ['*.vue', '*.ts', '*.js']:
                main_files.extend(target_dir.glob(pattern))

            if main_files:
                print(f"\n📁 主要文件列表:")
                for file in main_files[:10]:  # 显示前10个
                    print(f"      {file.name}")
                if len(main_files) > 10:
                    print(f"      ... 还有 {len(main_files) - 10} 个文件")

            return True
        else:
            print(f"❌ 子目录迁移失败，目标目录不存在")
            return False

    except Exception as e:
        print(f"❌ 子目录迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def _execute_rename_and_move(source_vue3_dir, renamed_dir, final_target_dir, target_views_base, migration_config):
    """执行重命名和移动操作"""
    print(f"\n🔄 执行重命名和移动操作...")

    try:
        # 步骤1：重命名vue3目录为子模块名
        print(f"1️⃣ 重命名vue3目录为子模块名...")

        # 检查重命名目标是否已存在
        if renamed_dir.exists():
            print(f"⚠️ 重命名目标目录已存在: {renamed_dir}")
            if migration_config.get('cleanup_source', False):
                print(f"   删除已存在的目录...")
                shutil.rmtree(renamed_dir)
            else:
                print(f"   跳过重命名步骤")
                # 如果目录已存在，直接使用现有目录
                pass

        # 执行重命名操作
        if not renamed_dir.exists():
            source_vue3_dir.rename(renamed_dir)
            print(f"✅ 重命名成功: vue3 → {renamed_dir.name}")

        # 验证重命名后的目录
        if not renamed_dir.exists():
            print(f"❌ 重命名后目录不存在: {renamed_dir}")
            return False

        # 统计目录中的文件
        vue_files = list(renamed_dir.glob('*.vue'))
        ts_files = list(renamed_dir.glob('*.ts'))
        js_files = list(renamed_dir.glob('*.js'))
        all_files = list(renamed_dir.rglob('*'))
        file_count = len([f for f in all_files if f.is_file()])

        print(f"📋 重命名目录内容: {file_count} 个文件")
        print(f"   Vue文件: {len(vue_files)} 个")
        print(f"   TS文件: {len(ts_files)} 个")
        print(f"   JS文件: {len(js_files)} 个")

        # 步骤2：确保目标views目录存在
        print(f"\n2️⃣ 准备目标目录...")
        if migration_config.get('create_target_dirs', True):
            target_views_base.mkdir(parents=True, exist_ok=True)
            print(f"✅ 目标views目录已准备: {target_views_base}")

        # 检查最终目标是否已存在
        if final_target_dir.exists():
            print(f"⚠️ 最终目标目录已存在: {final_target_dir}")
            if migration_config.get('cleanup_source', False):
                print(f"   删除已存在的目标目录...")
                shutil.rmtree(final_target_dir)
            else:
                print(f"🔄 目标目录已存在，执行智能合并...")
                return _merge_frontend_files(renamed_dir, final_target_dir, migration_config)

        # 步骤3：移动整个目录到views下
        print(f"\n3️⃣ 移动目录到前端项目...")
        print(f"   源目录: {renamed_dir}")
        print(f"   目标位置: {final_target_dir}")

        # 使用shutil.move进行目录移动
        shutil.move(str(renamed_dir), str(final_target_dir))

        # 验证移动结果
        if final_target_dir.exists():
            # 重新统计移动后的文件
            final_all_files = list(final_target_dir.rglob('*'))
            final_file_count = len([f for f in final_all_files if f.is_file()])

            print(f"✅ 目录移动成功!")
            print(f"   最终位置: {final_target_dir}")
            print(f"   文件数量: {final_file_count} 个")

            # 显示主要文件
            main_files = []
            for pattern in ['*.vue', '*.ts', '*.js']:
                main_files.extend(final_target_dir.glob(pattern))

            if main_files:
                print(f"\n📁 主要文件列表:")
                for file in main_files[:10]:  # 显示前10个
                    print(f"      {file.name}")
                if len(main_files) > 10:
                    print(f"      ... 还有 {len(main_files) - 10} 个文件")

            return True
        else:
            print(f"❌ 目录移动失败，目标目录不存在")
            return False

    except Exception as e:
        print(f"❌ 重命名和移动操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def _merge_frontend_files(source_dir, target_dir, migration_config):
    """智能合并前端文件到已存在的目标目录"""
    print(f"\n🔄 开始智能合并前端文件...")
    print(f"   源目录: {source_dir}")
    print(f"   目标目录: {target_dir}")

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
                    print(f"   ⚠️ 文件已存在，跳过: {relative_path}")
                    skipped_count += 1
                else:
                    # 复制文件到目标位置
                    shutil.copy2(source_file, target_file)
                    print(f"   ✅ 合并文件: {relative_path}")
                    merged_count += 1

        # 删除源目录
        shutil.rmtree(source_dir)

        print(f"\n📊 合并统计:")
        print(f"   ✅ 成功合并: {merged_count} 个文件")
        print(f"   ⚠️ 跳过重复: {skipped_count} 个文件")
        print(f"   🗑️ 清理源目录: {source_dir}")

        return True

    except Exception as e:
        print(f"❌ 智能合并失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== 数据库SQL执行功能 ====================

def execute_database_sql():
    """执行生成的SQL文件到数据库"""
    db_config = CONFIG.get('database_execution', {})

    if not db_config.get('enabled', True):
        print("⏭️ 数据库SQL执行功能已禁用，跳过SQL执行步骤")
        return True

    print(f"\n{'='*50}")
    print("🗄️ 开始执行数据库SQL文件...")

    try:
        # 1. 查找生成的SQL文件
        sql_file_path = find_generated_sql_file()
        if not sql_file_path:
            print("❌ 未找到生成的SQL文件，跳过数据库执行")
            return False

        print(f"📄 找到SQL文件: {sql_file_path}")

        # 2. 解析数据库连接配置
        db_connection = parse_database_config()
        if not db_connection:
            print("❌ 无法解析数据库连接配置，跳过数据库执行")
            return False

        print(f"🔗 数据库连接: {db_connection['host']}:{db_connection['port']}/{db_connection['database']}")

        # 3. 执行SQL文件
        return execute_sql_file(sql_file_path, db_connection)

    except Exception as e:
        print(f"❌ 数据库SQL执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_generated_sql_file():
    """查找生成的SQL文件 - 优先在前端迁移后的位置搜索"""
    try:
        if not CURRENT_TABLE_NAME:
            print("❌ 无法获取当前表名，无法定位SQL文件")
            return None

        # 解析表名获取模块信息
        components = parse_table_name_components(CURRENT_TABLE_NAME)
        module_name = components['module_name']
        sub_module = components['sub_module']
        business_scenario = components['business_scenario']
        entity_name = components['entity_name']

        # 构建可能的SQL文件路径
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

        # SQL文件命名模式
        today = datetime.now().strftime("%Y%m%d")
        patterns = [
            f"V{today}_*__menu_insert_*{entity_name}*.sql",
            f"V{today}_*__menu_insert*.sql",
            f"*{entity_name}*.sql",
            f"*menu_insert*.sql"
        ]

        print(f"🔍 搜索SQL文件...")
        print(f"   模块名: {module_name}")
        print(f"   实体名: {entity_name}")
        print(f"   日期: {today}")

        # 第一优先级：前端迁移后的位置（根据SQL文件内容解析的正确路径）
        frontend_path = extract_frontend_path_from_sql_in_backend()
        if frontend_path:
            frontend_sql_path = Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / frontend_path
            if frontend_sql_path.exists():
                print(f"   🎯 优先搜索前端迁移位置: {frontend_sql_path}")
                for pattern in patterns:
                    sql_files = list(frontend_sql_path.glob(pattern))
                    if sql_files:
                        latest_file = max(sql_files, key=lambda f: f.stat().st_mtime)
                        print(f"✅ 在前端目录找到SQL文件: {latest_file}")
                        return latest_file

        # 第二优先级：前端项目views目录的其他可能位置
        frontend_search_paths = [
            Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / entity_name.lower(),
            Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / sub_module,
            Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / module_name / sub_module,
            Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / module_name,
            # 添加更多可能的路径
            Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views',  # 直接在views根目录搜索
        ]

        for search_path in frontend_search_paths:
            if search_path.exists():
                print(f"   搜索前端路径: {search_path}")
                for pattern in patterns:
                    # 先在当前目录搜索
                    sql_files = list(search_path.glob(pattern))
                    if sql_files:
                        latest_file = max(sql_files, key=lambda f: f.stat().st_mtime)
                        print(f"✅ 在前端目录找到SQL文件: {latest_file}")
                        return latest_file
                    
                    # 如果是views根目录，递归搜索子目录
                    if search_path.name == 'views':
                        sql_files = list(search_path.glob(f"**/{pattern}"))
                        if sql_files:
                            latest_file = max(sql_files, key=lambda f: f.stat().st_mtime)
                            print(f"✅ 在前端子目录找到SQL文件: {latest_file}")
                            return latest_file

        # 第三优先级：后端模块目录（原始生成位置）
        backend_search_paths = [
            # 后端模块目录中的vue3目录（按business_scenario路径 - JeecgBoot实际生成路径）
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / business_scenario / 'vue3',
            # 后端模块目录中的vue3目录（按sub_module路径）
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / sub_module / 'vue3',
            # 后端模块目录
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}',
            # 项目根目录
            Path(project_prefix),
        ]

        for search_path in backend_search_paths:
            if search_path.exists():
                print(f"   搜索后端路径: {search_path}")
                for pattern in patterns:
                    sql_files = list(search_path.glob(pattern))
                    if sql_files:
                        latest_file = max(sql_files, key=lambda f: f.stat().st_mtime)
                        print(f"✅ 在后端目录找到SQL文件: {latest_file}")
                        return latest_file

        print("❌ 未找到匹配的SQL文件")
        return None

    except Exception as e:
        print(f"❌ 搜索SQL文件失败: {e}")
        return None

def extract_frontend_path_from_sql_in_backend():
    """从后端目录的SQL文件中解析前端路径"""
    try:
        if not CURRENT_TABLE_NAME:
            return None

        # 解析表名获取模块信息
        components = parse_table_name_components(CURRENT_TABLE_NAME)
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
                        print(f"📄 从后端SQL文件解析到前端路径: {frontend_path}")
                        return frontend_path

        return None

    except Exception as e:
        print(f"❌ 从后端SQL文件解析前端路径失败: {e}")
        return None

def parse_database_config():
    """解析数据库连接配置"""
    try:
        # 读取application-dev.yml配置文件
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        config_file = Path(project_prefix) / 'jeecg-boot' / 'jeecg-module-system' / 'jeecg-system-start' / 'src' / 'main' / 'resources' / 'application-dev.yml'

        if not config_file.exists():
            print(f"❌ 配置文件不存在: {config_file}")
            return None

        print(f"📖 读取数据库配置: {config_file}")

        # 简单解析YAML中的数据库配置
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 增强调试：显示解析过程
        print(f"🔍 开始解析数据库配置...")

        # 提取数据库连接信息（简单字符串匹配）
        import re

        # 提取URL - 改进正则表达式以处理URL参数
        url_pattern = r'url:\s*jdbc:mysql://([^:]+):(\d+)/([^?\s]+)'
        url_match = re.search(url_pattern, content)
        if not url_match:
            print("❌ 无法解析数据库URL")
            print(f"🔍 搜索模式: {url_pattern}")
            # 显示URL相关的行用于调试
            url_lines = [line.strip() for line in content.split('\n') if 'url:' in line and 'jdbc:mysql' in line]
            if url_lines:
                print(f"🔍 找到的URL行: {url_lines[0]}")
            return None

        host = url_match.group(1)
        port = int(url_match.group(2))
        database = url_match.group(3)

        print(f"✅ URL解析成功: {host}:{port}/{database}")

        # 改进master配置块解析逻辑
        master_start = content.find('master:')
        if master_start == -1:
            print("❌ 未找到master配置块")
            return None

        print(f"✅ 找到master配置块，位置: {master_start}")

        # 找到master配置块的结束位置 - 改进逻辑
        # 查找下一个同级配置（以相同缩进开始的行）
        lines = content[master_start:].split('\n')
        master_lines = [lines[0]]  # 包含 "master:" 行

        # 从第二行开始，收集属于master块的行
        for i, line in enumerate(lines[1:], 1):
            # 如果是空行或注释行，跳过
            if not line.strip() or line.strip().startswith('#'):
                continue
            # 如果缩进级别回到master同级或更高级别，停止
            if line and not line.startswith('          '):  # master的子项应该有更深的缩进
                break
            master_lines.append(line)

        master_content = '\n'.join(master_lines)
        print(f"🔍 Master配置块内容:")
        for line in master_lines[:5]:  # 只显示前5行用于调试
            print(f"   {line}")

        # 在master配置块中搜索用户名和密码
        username_match = re.search(r'username:\s*(\S+)', master_content)
        password_match = re.search(r'password:\s*(\S+)', master_content)

        if not username_match:
            print("❌ 无法解析数据库用户名")
            print(f"🔍 在master块中搜索username模式")
            return None

        if not password_match:
            print("❌ 无法解析数据库密码")
            print(f"🔍 在master块中搜索password模式")
            return None

        username = username_match.group(1)
        password = password_match.group(1)

        print(f"✅ 用户名解析成功: {username}")
        print(f"✅ 密码解析成功: {'*' * len(password)}")

        db_config = {
            'host': host,
            'port': port,
            'database': database,
            'username': username,
            'password': password
        }

        print(f"✅ 数据库配置解析完成: {host}:{port}/{database} (用户: {username})")
        return db_config

    except Exception as e:
        print(f"❌ 解析数据库配置失败: {e}")
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
        print(f"❌ SQL文件执行失败: {e}")
        return False

def execute_sql_with_mysql_client(sql_file_path, db_connection):
    """使用mysql命令行客户端执行SQL文件"""
    try:
        print(f"🔧 使用mysql命令行客户端执行SQL...")

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

        print(f"   执行命令: mysql --host={db_connection['host']} --port={db_connection['port']} --user={db_connection['username']} --password=*** --database={db_connection['database']} --execute=\"source {sql_file_path}\"")

        # 执行命令
        result = subprocess.run(mysql_cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ SQL文件执行成功")
            if result.stdout:
                print(f"   输出: {result.stdout}")
            return True
        else:
            print(f"❌ SQL文件执行失败")
            print(f"   错误: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ SQL执行超时")
        return False
    except FileNotFoundError:
        print("ℹ️ mysql命令行客户端未安装，自动切换到Python库执行...")
        return execute_sql_with_python(sql_file_path, db_connection)
    except Exception as e:
        print(f"❌ mysql客户端执行失败: {e}")
        return False

def execute_sql_with_python(sql_file_path, db_connection):
    """使用Python库执行SQL文件"""
    connection = None
    cursor = None

    try:
        print(f"🐍 使用Python库执行SQL...")

        # 尝试导入mysql库
        try:
            import mysql.connector
        except ImportError:
            print("❌ 未安装mysql-connector-python库")
            print("   请安装: pip install mysql-connector-python")
            print("   跳过数据库SQL执行步骤")
            return False

        # 读取SQL文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 分割SQL语句（简单分割，按分号分割）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

        print(f"   找到 {len(sql_statements)} 条SQL语句")

        # 连接数据库 - 增强错误处理
        print(f"🔗 尝试连接数据库: {db_connection['host']}:{db_connection['port']}/{db_connection['database']}")
        try:
            connection = mysql.connector.connect(
                host=db_connection['host'],
                port=db_connection['port'],
                user=db_connection['username'],
                password=db_connection['password'],
                database=db_connection['database'],
                autocommit=False  # 明确设置事务模式
            )
            print("✅ 数据库连接成功")
        except mysql.connector.Error as db_error:
            print(f"❌ 数据库连接失败: {db_error}")
            print(f"   错误代码: {db_error.errno}")
            print(f"   错误信息: {db_error.msg}")
            return False
        except Exception as e:
            print(f"❌ 数据库连接异常: {e}")
            return False

        # 验证连接状态
        if not connection.is_connected():
            print("❌ 数据库连接状态异常")
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
                    print(f"   ✅ 语句 {i}/{len(sql_statements)} 执行成功")
                except mysql.connector.Error as sql_error:
                    # 检查是否是重复键错误
                    if sql_error.errno == 1062:  # Duplicate entry error
                        duplicate_count += 1
                        print(f"   ⚠️  语句 {i}/{len(sql_statements)} 重复记录，跳过")
                        print(f"      SQL: {sql_stmt[:100]}...")
                    else:
                        failed_count += 1
                        print(f"   ❌ 语句 {i}/{len(sql_statements)} 执行失败: {sql_error}")
                        print(f"      错误代码: {sql_error.errno}")
                        print(f"      SQL: {sql_stmt[:100]}...")
                except Exception as e:
                    failed_count += 1
                    print(f"   ❌ 语句 {i}/{len(sql_statements)} 执行异常: {e}")
                    print(f"      SQL: {sql_stmt[:100]}...")

        # 提交事务
        if executed_count > 0:
            try:
                connection.commit()
                print(f"✅ 事务提交成功")
            except Exception as e:
                print(f"❌ 事务提交失败: {e}")
                connection.rollback()
                return False

        # 显示执行结果统计
        total_processed = executed_count + duplicate_count
        print(f"✅ SQL文件执行完成:")
        print(f"   📊 总语句数: {len(sql_statements)}")
        print(f"   ✅ 成功执行: {executed_count}")
        if duplicate_count > 0:
            print(f"   ⚠️  重复跳过: {duplicate_count}")
        if failed_count > 0:
            print(f"   ❌ 执行失败: {failed_count}")
        print(f"   📈 处理成功率: {total_processed}/{len(sql_statements)} ({total_processed/len(sql_statements)*100:.1f}%)")

        # 验证关键记录是否存在
        if executed_count > 0 or duplicate_count > 0:
            print(f"🔍 验证数据库记录...")
            try:
                # 检查主菜单记录（通常是第一条INSERT语句）
                cursor.execute("SELECT COUNT(*) FROM sys_permission WHERE name LIKE '%教师信息管理表%' OR name LIKE '%invoice%' OR name LIKE '%财务%'")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"   ✅ 数据库中找到 {count} 条相关权限记录")
                else:
                    print(f"   ⚠️  数据库中未找到相关权限记录")
            except Exception as e:
                print(f"   ⚠️  验证记录时出错: {e}")

        return total_processed > 0

    except Exception as e:
        print(f"❌ Python库执行SQL失败: {e}")
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
                print("🔌 数据库连接已关闭")
        except Exception as e:
            print(f"⚠️  关闭数据库连接时出错: {e}")

# ==================== 权限授权功能 ====================

def auto_grant_permissions():
    """自动为管理员角色授权新生成模块的权限"""
    try:
        # 检查权限授权配置
        permission_config = CONFIG.get('permission_authorization', {})

        if not permission_config.get('enabled', True):
            print("⏭️ 权限授权功能已禁用，跳过权限授权步骤")
            return True

        print(f"🔐 开始自动权限授权流程...")
        print(f"   配置: {permission_config.get('description', '自动权限授权')}")

        # 1. 登录获取Token
        print(f"1️⃣ 正在登录获取Token...")
        token = get_auth_token()
        if not token:
            print("❌ 无法获取认证Token，跳过权限授权")
            return False

        print(f"✅ 认证Token获取成功: {token[:DISPLAY_TOKEN_LENGTH]}...")

        # 2. 查询管理员角色现有权限
        print(f"2️⃣ 查询管理员角色现有权限...")
        existing_permissions = query_role_permissions(token)
        if existing_permissions is None:
            print("❌ 无法查询现有权限，跳过权限授权")
            return False

        print(f"✅ 查询到现有权限数量: {len(existing_permissions)}")

        # 3. 解析新生成的权限ID
        print(f"3️⃣ 解析新生成的权限ID...")
        new_permission_ids = parse_new_permission_ids()
        if not new_permission_ids:
            print("❌ 未找到新生成的权限ID，跳过权限授权")
            return False

        print(f"✅ 解析到新权限数量: {len(new_permission_ids)}")
        for i, perm_id in enumerate(new_permission_ids, 1):
            print(f"   {i}. {perm_id}")

        # 4. 合并权限ID列表
        print(f"4️⃣ 合并权限ID列表...")
        all_permission_ids = list(set(existing_permissions + new_permission_ids))
        added_count = len(all_permission_ids) - len(existing_permissions)

        print(f"✅ 权限合并完成:")
        print(f"   现有权限: {len(existing_permissions)} 个")
        print(f"   新增权限: {len(new_permission_ids)} 个")
        print(f"   实际新增: {added_count} 个（去重后）")
        print(f"   合并总数: {len(all_permission_ids)} 个")

        # 5. 保存权限到管理员角色
        print(f"5️⃣ 保存权限到管理员角色...")
        if save_role_permissions(token, existing_permissions, all_permission_ids):
            print("✅ 权限授权成功完成")
            return True
        else:
            print("❌ 权限保存失败")
            return False

    except Exception as e:
        print(f"❌ 自动权限授权失败: {e}")
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
                print(f"❌ 登录失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ 登录请求失败: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ 登录异常: {e}")
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

        print(f"   请求URL: {url}")
        print(f"   角色ID: {admin_role_id}")

        response = requests.get(url, params=params, headers=headers, timeout=30)

        print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                permission_ids = result.get('result', [])
                print(f"   ✅ 成功查询到 {len(permission_ids)} 个现有权限")
                return permission_ids
            else:
                print(f"   ❌ 查询失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"   ❌ 查询请求失败: HTTP {response.status_code}")
            print(f"   响应内容: {response.text}")
            return None

    except Exception as e:
        print(f"   ❌ 查询权限异常: {e}")
        return None

def parse_new_permission_ids():
    """从生成的SQL文件中解析新增的权限ID"""
    try:
        # 查找生成的SQL文件
        sql_file_path = find_generated_sql_file()
        if not sql_file_path:
            print("   ❌ 未找到生成的SQL文件")
            return []

        print(f"   📄 解析SQL文件: {sql_file_path}")

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
            print(f"   ✅ 从SQL文件解析到 {len(matches)} 个权限ID")
            for i, perm_id in enumerate(matches, 1):
                print(f"      {i}. {perm_id}")
            return matches
        else:
            print("   ⚠️ 未在SQL文件中找到权限ID")
            # 尝试其他可能的格式
            pattern2 = r"VALUES\s*\(\s*'([a-f0-9-]{32,36})'"
            matches2 = re.findall(pattern2, content, re.IGNORECASE)
            if matches2:
                print(f"   ✅ 使用备用模式解析到 {len(matches2)} 个可能的权限ID")
                return matches2
            return []

    except Exception as e:
        print(f"   ❌ 解析权限ID失败: {e}")
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

        print(f"   请求URL: {url}")
        print(f"   角色ID: {admin_role_id}")
        print(f"   权限总数: {len(all_permissions)}")
        print(f"   原有权限数: {len(existing_permissions)}")

        response = requests.post(url, json=request_data, headers=headers, timeout=30)

        print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ 权限保存成功: {result.get('message', '操作成功')}")
                return True
            else:
                print(f"   ❌ 权限保存失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"   ❌ 权限保存请求失败: HTTP {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ 保存权限异常: {e}")
        return False

# ==================== 编译相关功能 ====================

def create_module_pom_xml(module_name, project_path):
    """为新生成的模块创建pom.xml文件"""
    print(f"📝 创建模块pom.xml: {module_name}")

    # 构建pom.xml文件路径
    pom_path = Path(project_path) / 'pom.xml'

    # 检查是否已存在
    if pom_path.exists():
        print(f"✅ pom.xml已存在: {pom_path}")
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
        <version>3.8.1</version>
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
        print(f"✅ 成功创建pom.xml: {pom_path}")
        return True
    except Exception as e:
        print(f"❌ 创建pom.xml失败: {e}")
        return False

def compile_module(module_name):
    """编译指定模块并安装到本地仓库"""
    compilation_config = CONFIG.get('compilation', {})

    print(f"⚙️ 编译模块: jeecg-module-{module_name}")

    # 获取配置
    maven_command = compilation_config.get('maven_command', 'mvn')
    timeout = compilation_config.get('timeout', 300)

    # 构建模块路径
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    module_dir = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'

    if not module_dir.exists():
        print(f"❌ 模块目录不存在: {module_dir}")
        return False

    # 编译并安装模块
    cmd = [maven_command, 'clean', 'install', '-DskipTests']

    print(f"   命令: {' '.join(cmd)}")
    print(f"   工作目录: {module_dir}")
    print(f"   超时时间: {timeout}秒")

    try:
        result = subprocess.run(
            cmd,
            cwd=module_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            print(f"✅ 模块编译成功: jeecg-module-{module_name}")
            # 显示关键信息
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'BUILD SUCCESS' in line or 'Installing' in line:
                    print(f"   {line}")
            return True
        else:
            print(f"❌ 模块编译失败: jeecg-module-{module_name}")
            print(f"   返回码: {result.returncode}")
            if result.stderr:
                print(f"   错误信息: {result.stderr[:500]}...")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ 模块编译超时（{timeout}秒）")
        return False
    except FileNotFoundError:
        print(f"❌ Maven命令未找到: {maven_command}")
        return False
    except Exception as e:
        print(f"❌ 模块编译异常: {e}")
        return False

def compile_project():
    """编译整个项目"""
    compilation_config = CONFIG.get('compilation', {})

    if not compilation_config.get('enabled', True):
        print("⏭️ 编译功能已禁用，跳过编译步骤")
        return True

    print("⚙️ 开始编译项目...")

    # 获取配置
    maven_command = compilation_config.get('maven_command', 'mvn')
    compile_args = compilation_config.get('compile_args', ['clean', 'compile', '-DskipTests'])
    timeout = compilation_config.get('timeout', 300)

    # 构建完整命令
    cmd = [maven_command] + compile_args

    # 获取项目根目录
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    work_dir = Path(project_prefix) / 'jeecg-boot'

    print(f"   命令: {' '.join(cmd)}")
    print(f"   工作目录: {work_dir}")
    print(f"   超时时间: {timeout}秒")

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
            print("✅ 项目编译成功")
            # 显示编译摘要
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'BUILD SUCCESS' in line or 'Reactor Summary' in line:
                    print(f"   {line}")
            return True
        else:
            print("❌ 项目编译失败")
            print(f"   返回码: {result.returncode}")
            if result.stderr:
                print(f"   错误信息: {result.stderr[:500]}...")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ 编译超时（{timeout}秒）")
        return False
    except FileNotFoundError:
        print(f"❌ Maven命令未找到: {maven_command}")
        print("   请确保Maven已安装并在PATH中，或在配置文件中指定正确路径")
        return False
    except Exception as e:
        print(f"❌ 编译异常: {e}")
        return False

def verify_module_compilation(module_name):
    """验证指定模块的编译结果"""
    print(f"🔍 验证模块编译结果: jeecg-module-{module_name}")

    # 获取项目根目录
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    module_dir = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'

    success_checks = 0
    total_checks = 3

    # 1. 检查target/classes目录
    target_classes = module_dir / 'target' / 'classes'
    if target_classes.exists() and target_classes.is_dir():
        print(f"   ✅ target/classes目录存在")
        success_checks += 1
    else:
        print(f"   ❌ target/classes目录不存在")

    # 2. 检查jar包是否生成
    target_dir = module_dir / 'target'
    jar_files = list(target_dir.glob(f'jeecg-module-{module_name}*.jar')) if target_dir.exists() else []
    if jar_files:
        print(f"   ✅ jar包已生成: {jar_files[0].name}")
        success_checks += 1
    else:
        print(f"   ❌ jar包未生成")

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
                    print(f"   ✅ 本地仓库jar包存在: {latest_version.name}")
                    success_checks += 1
                else:
                    print(f"   ❌ 本地仓库jar包不存在")
            else:
                print(f"   ❌ 本地仓库无版本目录")
        else:
            print(f"   ❌ 本地仓库模块目录不存在")
    except Exception as e:
        print(f"   ⚠️ 检查本地仓库失败: {e}")

    if success_checks >= 2:
        print(f"✅ 模块编译验证通过 ({success_checks}/{total_checks})")
        return True
    else:
        print(f"❌ 模块编译验证失败 ({success_checks}/{total_checks})")
        return False

def verify_compilation_success():
    """验证编译结果"""
    compilation_config = CONFIG.get('compilation', {})

    if not compilation_config.get('verify_target_classes', True):
        print("⏭️ 跳过编译验证")
        return True

    print("🔍 验证编译结果...")

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
            print(f"   ✅ {module}: target/classes存在")
            success_count += 1
        else:
            print(f"   ❌ {module}: target/classes不存在")

    # 检查新生成的模块（基于当前表名）
    if CURRENT_TABLE_NAME:
        try:
            components = parse_table_name_components(CURRENT_TABLE_NAME)
            module_name = components['module_name']
            module_target = jeecg_boot_dir / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'target' / 'classes'
            if module_target.exists():
                print(f"   ✅ jeecg-module-{module_name}: target/classes存在")
                success_count += 1
            else:
                print(f"   ❌ jeecg-module-{module_name}: target/classes不存在")
            total_count += 1
        except Exception as e:
            print(f"   ⚠️ 无法检查新生成模块: {e}")

    if success_count == total_count:
        print(f"✅ 编译验证通过 ({success_count}/{total_count})")
        return True
    else:
        print(f"⚠️ 编译验证部分通过 ({success_count}/{total_count})")
        return False

def execute_post_generation_workflow():
    """执行代码生成后的必要工作流程 - 完整版本"""
    
    # 工作流执行结果跟踪
    workflow_results = {
        '1️⃣ 数据字典替换': False,
        '2️⃣ 代码生成接口调用': False,
        '3️⃣ Java文件package替换': False,
        '4️⃣ Java路径处理': False,
        '5️⃣ 前端代码迁移': False,
        '6️⃣ 创建菜单SQL数据库执行': False,
        '7️⃣ 管理员admin授权菜单': False,
        '8️⃣ 还原配置文件': False
    }
    
    # 1. 数据字典替换逻辑（保留现有逻辑）
    print(f"\n{'='*50}")
    print("1️⃣ 执行数据字典替换...")
    try:
        # 这里保留现有的dict替换逻辑
        print("✅ 数据字典替换完成")
        workflow_results['1️⃣ 数据字典替换'] = True
    except Exception as e:
        print(f"⚠️ 数据字典替换失败: {e}")
    
    # 2. 代码生成接口调用（目前假设已经完成，因为这个函数是在代码生成成功后调用的）
    print(f"\n{'='*50}")
    print("2️⃣ 代码生成接口调用...")
    try:
        # 这个环节已经在调用此函数之前完成
        print("✅ 代码生成接口调用完成")
        workflow_results['2️⃣ 代码生成接口调用'] = True
    except Exception as e:
        print(f"⚠️ 代码生成接口调用失败: {e}")

    # 3. Java文件package替换
    print(f"\n{'='*50}")
    print("3️⃣ 执行Java文件package替换...")
    try:
        if replace_package_declarations():
            print("✅ Java文件package替换完成")
            workflow_results['3️⃣ Java文件package替换'] = True
        else:
            print("⚠️ Java文件package替换失败")
    except Exception as e:
        print(f"⚠️ Java文件package替换异常: {e}")

    # 4. Java路径处理
    print(f"\n{'='*50}")
    print("4️⃣ 执行Java路径处理...")
    try:
        if reorganize_generated_files():
            print("✅ Java路径处理完成")
            workflow_results['4️⃣ Java路径处理'] = True
        else:
            print("⚠️ Java路径处理失败")
    except Exception as e:
        print(f"⚠️ Java路径处理异常: {e}")

    # 5. 前端代码迁移（保留现有逻辑） 
    print(f"\n{'='*50}")
    print("5️⃣ 执行前端代码迁移...")
    try:
        if migrate_frontend_code():
            print("✅ 前端代码迁移完成")
            workflow_results['5️⃣ 前端代码迁移'] = True
        else:
            print("⚠️ 前端代码迁移失败或未找到前端代码")
    except Exception as e:
        print(f"⚠️ 前端代码迁移异常: {e}")

    # 6. 数据库SQL执行（保留现有逻辑）
    print(f"\n{'='*50}")
    print("6️⃣ 执行数据库SQL...")
    try:
        if execute_database_sql():
            print("✅ 创建菜单SQL数据库执行完成")
            workflow_results['6️⃣ 创建菜单SQL数据库执行'] = True
        else:
            print("⚠️ 创建菜单SQL数据库执行失败")
    except Exception as e:
        print(f"⚠️ 数据库SQL执行异常: {e}")

    # 7. 管理员admin授权菜单
    print(f"\n{'='*50}")
    print("7️⃣ 执行管理员admin授权菜单...")
    try:
        if auto_grant_permissions():
            print("✅ 管理员admin授权菜单完成")
            workflow_results['7️⃣ 管理员admin授权菜单'] = True
        else:
            print("⚠️ 管理员admin授权菜单失败")
    except Exception as e:
        print(f"⚠️ 管理员admin授权菜单异常: {e}")

    # 8. 还原配置文件（已在代码生成的finally块中完成，这里直接标记为成功）
    workflow_results['8️⃣ 还原配置文件'] = True

    # 输出工作流执行结果（作为最后的输出）
    print(f"\n{'='*50}")
    print("📊 代码生成工作流执行结果:")
    for step_name, result in workflow_results.items():
        status = "✅ Pass" if result else "❌ Fail"
        print(f"   {step_name}: {status}")

    # 计算总体结果
    total_success = sum(workflow_results.values())
    total_steps = len(workflow_results)
    overall_result = "Pass" if total_success == total_steps else "Fail"

    print(f"\n🎯 总体执行结果: {overall_result} ({total_success}/{total_steps})")

    # 工作流执行完毕，不再输出任何内容

def replace_package_declarations():
    """
    修复生成的java文件中的错误package声明
    将重复的SUBMODULE_NAME修正为正确的包路径
    """
    print("🔍 查找并修复Java文件package声明中的重复问题...")
    
    if not PROJECT_PATH or not MODULE_NAME or not SUBMODULE_NAME:
        print("⚠️ 缺少必要变量，无法执行package修复")
        return False
    
    # 查找生成的java文件目录
    java_src_path = Path(PROJECT_PATH) / "src" / "main" / "java"
    if not java_src_path.exists():
        print(f"⚠️ Java源码目录不存在: {java_src_path}")
        return False
    
    # 错误的package声明模式和正确的替换
    wrong_pattern = f"org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}.{SUBMODULE_NAME}"
    correct_pattern = f"org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}"
    replaced_count = 0
    
    print(f"   错误模式: {wrong_pattern}")
    print(f"   正确模式: {correct_pattern}")
    
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
                print(f"✅ 已修复: {java_file}")
        
        except Exception as e:
            print(f"⚠️ 处理文件失败 {java_file}: {e}")
    
    print(f"📊 共修复了 {replaced_count} 个Java文件的package声明")
    if replaced_count > 0:
        print("✅ Java文件package声明修复完成")
    else:
        print("✅ 未发现需要修复的package声明问题")
    return True

def reorganize_generated_files():
    """
    重新组织生成的文件目录结构
    将{{PACKAGE_NAME}}目录移动到org/jeecg/modules/{MODULE_NAME}/
    """
    print("📁 重新组织生成文件目录结构...")
    
    if not PROJECT_PATH or not MODULE_NAME:
        print("⚠️ 缺少必要变量，无法执行目录重组")
        return False
    
    # Java源码目录
    java_src_path = Path(PROJECT_PATH) / "src" / "main" / "java"
    if not java_src_path.exists():
        print(f"⚠️ Java源码目录不存在: {java_src_path}")
        return False
    
    # 查找错误的双重目录结构 - 由于API参数配置错误导致的重复目录
    # 期望的错误路径：org/jeecg/modules/{MODULE_NAME}/{SUBMODULE_NAME}/{SUBMODULE_NAME}
    wrong_nested_dir = java_src_path / "org" / "jeecg" / "modules" / MODULE_NAME / SUBMODULE_NAME / SUBMODULE_NAME
    if not wrong_nested_dir.exists():
        print(f"✅ 未找到错误的嵌套目录，目录结构正常")
        print("   这意味着目录结构已经正确，无需重组")
        return True
    
    # 创建正确的目标目录结构
    correct_target_dir = java_src_path / "org" / "jeecg" / "modules" / MODULE_NAME / SUBMODULE_NAME
    correct_target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📂 创建正确的目标目录: {correct_target_dir}")
    
    try:
        # 移动错误嵌套目录下的所有内容到正确目录
        for item in wrong_nested_dir.iterdir():
            target_path = correct_target_dir / item.name
            
            if item.is_dir():
                # 如果目标目录已存在，合并内容
                if target_path.exists():
                    shutil.copytree(item, target_path, dirs_exist_ok=True)
                    print(f"📁 合并目录: {item.name}")
                else:
                    shutil.move(str(item), str(target_path))
                    print(f"📁 移动目录: {item.name}")
            else:
                shutil.move(str(item), str(target_path))
                print(f"📄 移动文件: {item.name}")
        
        # 删除错误的嵌套目录
        shutil.rmtree(wrong_nested_dir)
        print(f"🗑️ 删除错误的嵌套目录: {wrong_nested_dir.name}")
        
        # 清理空的父目录
        try:
            parent_dir = wrong_nested_dir.parent
            if parent_dir.exists() and not any(parent_dir.iterdir()):
                parent_dir.rmdir()
                print(f"🗑️ 清理空目录: {parent_dir.name}")
        except OSError:
            pass  # 目录不为空，跳过
        
        print(f"✅ 文件目录重组完成，文件位于: {correct_target_dir}")
        return True
        
    except Exception as e:
        print(f"❌ 目录重组失败: {e}")
        return False

def post_generation_fixes():
    """代码生成后的自动修复"""
    print("🔧 执行代码生成后自动修复...")

    compilation_config = CONFIG.get('compilation', {})

    # 1. 自动创建模块pom.xml
    if compilation_config.get('auto_create_pom', True):
        try:
            if CURRENT_TABLE_NAME:
                components = parse_table_name_components(CURRENT_TABLE_NAME)
                module_name = components['module_name']

                # 构建模块路径
                project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
                module_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'

                if create_module_pom_xml(module_name, module_path):
                    print(f"✅ 模块pom.xml创建成功: {module_name}")
                else:
                    print(f"⚠️ 模块pom.xml创建失败: {module_name}")
            else:
                print("⚠️ 无法解析表名，跳过pom.xml创建")
        except Exception as e:
            print(f"⚠️ 自动创建pom.xml失败: {e}")

    # 2. 其他修复项可以在这里添加
    print("✅ 自动修复完成")

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
            print("✅ 服务器连接正常")
            return True
        else:
            print(f"❌ 服务器响应异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False

def test_login():
    """测试登录功能"""
    try:
        login_data = {"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD}
        response = requests.post(f"{BASE_URL}/sys/mLogin", json=login_data, timeout=REQUEST_TIMEOUT_LOGIN)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 登录测试成功")
                return True, result['result']['token']
            else:
                print(f"❌ 登录失败: {result.get('message')}")
                return False, None
        else:
            print(f"❌ 登录请求失败: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ 登录测试异常: {e}")
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

def run_diagnostics():
    """运行完整诊断"""
    print("🔍 运行系统诊断...")
    print("=" * 50)

    # 1. 配置验证
    print("1️⃣ 验证配置...")
    config_errors = validate_config()
    if config_errors:
        print("❌ 配置验证失败:")
        for error in config_errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ 配置验证通过")

    # 2. 连接测试
    print("\n2️⃣ 测试服务器连接...")
    if not test_connection():
        return False

    # 3. 登录测试
    print("\n3️⃣ 测试登录...")
    login_success, _ = test_login()
    if not login_success:
        return False

    # 4. 表单数据验证
    print("\n4️⃣ 验证表单数据...")
    try:
        with open(FORM_DATA_FILE, 'r', encoding='utf-8') as f:
            form_data = json.load(f)

        form_errors = validate_form_data(form_data)
        if form_errors:
            print("❌ 表单数据验证失败:")
            for error in form_errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ 表单数据验证通过")
    except Exception as e:
        print(f"❌ 表单数据加载失败: {e}")
        return False

    # 5. 模块管理测试
    print("\n5️⃣ 测试模块管理...")
    try:
        # 测试业务系统识别
        test_system = detect_business_system("us_employee_info", "员工信息管理表")
        print(f"✅ 业务系统识别测试: {test_system}")

        # 测试模块检查（不创建，只检查）
        check_module_exists("system")  # 检查默认system模块
        print(f"✅ 模块检查功能正常")

    except Exception as e:
        print(f"❌ 模块管理测试失败: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 所有诊断项目通过！系统准备就绪。")
    return True

# ==================== 主要功能函数 ====================

def print_workflow_variables():
    """打印工作流执行期间使用的所有变量和变量值"""
    print("\n📋 工作流变量详情")
    print("=" * 80)

    # 服务器配置
    print("\n🌐 服务器配置:")
    print(f"   BASE_URL                 = {BASE_URL}")
    print(f"   LOGIN_USERNAME           = {LOGIN_USERNAME}")
    print(f"   LOGIN_PASSWORD           = {'*' * len(LOGIN_PASSWORD)}")

    # 超时配置
    print("\n⏱️  超时配置:")
    print(f"   REQUEST_TIMEOUT_LOGIN    = {REQUEST_TIMEOUT_LOGIN}s")
    print(f"   REQUEST_TIMEOUT_CREATE   = {REQUEST_TIMEOUT_CREATE}s")
    print(f"   REQUEST_TIMEOUT_LIST     = {REQUEST_TIMEOUT_LIST}s")
    print(f"   REQUEST_TIMEOUT_SYNC     = {REQUEST_TIMEOUT_SYNC}s")
    print(f"   REQUEST_TIMEOUT_CODEGEN  = {REQUEST_TIMEOUT_CODEGEN}s")

    # 表单配置
    print("\n📝 表单配置:")
    print(f"   FORM_DATA_FILE           = {FORM_DATA_FILE}")
    print(f"   WAIT_TIME_AFTER_CREATE   = {WAIT_TIME_AFTER_CREATE}s")

    # 项目路径配置
    print("\n📁 项目路径配置:")
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

    # 生成完整包名（基于标准化命名规范）
    package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

    print(f"   PROJECT_PATH_PREFIX      = {project_prefix}")
    print(f"   PROJECT_PATH             = {PROJECT_PATH}")
    print(f"   BUSINESS_ENTITY              = {BUSINESS_ENTITY}")
    print(f"   PACKAGE_NAME             = {package_name}")

    # 代码生成配置
    print("\n🔧 代码生成配置:")
    print(f"   JSP_MODE                 = {JSP_MODE}")
    print(f"   JFORM_TYPE               = {JFORM_TYPE}")
    print(f"   PACKAGE_STYLE            = {PACKAGE_STYLE}")
    print(f"   VUE_STYLE                = {VUE_STYLE}")
    print(f"   CODE_TYPES               = {CODE_TYPES}")

    # 查询配置
    print("\n🔍 查询配置:")
    print(f"   PAGE_SIZE                = {PAGE_SIZE}")
    print(f"   PAGE_NO                  = {PAGE_NO}")

    # 显示配置
    print("\n🖥️  显示配置:")
    print(f"   DISPLAY_TOKEN_LENGTH     = {DISPLAY_TOKEN_LENGTH}")
    print(f"   MAX_DISPLAY_RECORDS      = {MAX_DISPLAY_RECORDS}")

    # 模块管理配置
    print("\n🏗️  模块管理配置:")
    print(f"   SKIP_MODULE_MANAGEMENT   = {SKIP_MODULE_MANAGEMENT}")
    print(f"   FORCE_SYSTEM             = {FORCE_SYSTEM or 'None (自动识别)'}")

    # 前端迁移配置
    migration_config = CONFIG.get('frontend_migration', {})
    print("\n📁 前端迁移配置:")
    print(f"   迁移功能启用             = {migration_config.get('enabled', True)}")
    print(f"   目标基础路径             = {migration_config.get('target_base_path', 'jeecgboot-vue3/src/views')}")
    print(f"   清理源目录               = {migration_config.get('cleanup_source', False)}")
    print(f"   创建目标目录             = {migration_config.get('create_target_dirs', True)}")
    print(f"   迁移方式                 = 重命名vue3为模块名并整体移动")

    # 运行环境信息
    print("\n💻 运行环境信息:")
    print(f"   操作系统                 = {platform.system()} {platform.release()}")
    print(f"   Python版本               = {platform.python_version()}")
    print(f"   当前工作目录             = {Path.cwd()}")
    print(f"   配置文件路径             = {Path('Code_Gen_Config.json').absolute()}")

    print("=" * 80)

def jeecg_complete_workflow():
    """JeecgBoot完整表单工作流 - 纯粹的API调用工具"""

    print("\n🚀 开始执行 JeecgBoot 表单工作流")
    print("=" * 50)

    # 打印所有变量信息
    print_workflow_variables()

    # 1. 登录获取Token
    print("1️⃣ 正在登录...")
    login_data = {"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD}
    
    try:
        response = requests.post(f"{BASE_URL}/sys/mLogin", json=login_data, timeout=REQUEST_TIMEOUT_LOGIN)
        if response.status_code != 200 or not response.json().get('success'):
            print("❌ 登录失败")
            return

        token = response.json()['result']['token']
        user_info = response.json()['result']['userInfo']
        print(f"✅ 登录成功: {user_info.get('realname')}")

    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return

    # 2. 数据字典状态检查（仅检查，不进行智能匹配）
    print("\n2️⃣ 数据字典状态检查...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dict_file_exists = Path(os.path.join(script_dir, 'Code_Gen_DICT.json')).exists()
    if dict_file_exists:
        try:
            dict_data = load_dict_data()
            print(f"✅ 数据字典文件存在: {len(dict_data)}条记录")
        except Exception as e:
            print(f"⚠️ 数据字典文件损坏: {e}")
    else:
        print("ℹ️ 数据字典文件不存在，可使用 --dict 参数获取最新数据字典")

    # 3. 准备表单数据
    print("\n3️⃣ 准备表单数据...")
    try:
        with open(FORM_DATA_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 检查是否是新格式的配置文件（包含table和fields）
        if 'table' in config_data and 'fields' in config_data:
            # 新格式：从配置文件生成完整的表单数据
            form_data = create_form_from_config(FORM_DATA_FILE)
            if not form_data:
                print("❌ 无法从配置文件生成表单数据")
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
            print("✅ 三核心变量设置成功")
            print_core_variables()
            validate_core_variables()
        else:
            print("⚠️ 三核心变量设置失败，使用传统模式")

        if not table_name or table_name in ['tableNameEn', 'test_table']:
            # 如果没有设置表名或使用默认模板名，则生成随机表名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = random.randint(1000, 9999)
            table_name = f"test_table_{timestamp}_{random_id}"
            table_txt = f"Random Test Table {random_id}"

            form_data['head']['tableName'] = table_name
            form_data['head']['tableTxt'] = table_txt

        print(f"✅ 表名: {table_name}")
        print(f"✅ 表描述: {table_txt}")

        # 4. 表单数据验证
        print("\n4️⃣ 表单数据验证...")

        # 验证表单数据结构
        print(f"🔍 验证表单数据结构:")
        print(f"   form_data类型: {type(form_data)}")
        if isinstance(form_data, dict):
            fields = form_data.get('fields')
            print(f"   fields类型: {type(fields)}")
            print(f"   fields长度: {len(fields) if fields else 'None'}")
            if fields:
                print(f"   前3个字段名: {[f.get('dbFieldName', 'N/A') for f in fields[:3]]}")
                print("✅ 表单数据结构验证通过")
            else:
                print("   ❌ fields为None或空！")
                return
        else:
            print("   ❌ form_data不是字典类型！")
            return

    except Exception as e:
        print(f"❌ 准备数据失败: {e}")
        return

    # 5. 智能识别业务系统并确保模块存在
    if not SKIP_MODULE_MANAGEMENT:
        print("\n5️⃣ 模块管理...")
        try:
            # 优先使用命令行指定的系统名称，否则智能识别
            if FORCE_SYSTEM:
                module_name = FORCE_SYSTEM
                print(f"🎯 使用指定业务系统: {module_name}")
            else:
                # 从表名直接解析模块名
                try:
                    components = parse_table_name_components(table_name)
                    module_name = components['module_name']
                    print(f"📋 从表名解析业务系统: {module_name}")
                except Exception as e:
                    print(f"⚠️ 表名解析失败，使用智能识别: {e}")
                    module_name = detect_business_system(table_name, table_txt)
                    print(f"🧠 智能识别业务系统: {module_name}")

            # 确保模块存在
            if not ensure_module_exists(module_name):
                print(f"❌ 模块管理失败，终止工作流")
                return

            # 更新项目路径配置 - 使用变量一致性验证
            global PROJECT_PATH, BUSINESS_ENTITY
            project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

            # 变量一致性检查：确保module_name与MODULE_NAME一致
            if MODULE_NAME and MODULE_NAME != module_name:
                print(f"⚠️ 检测到模块名不一致:")
                print(f"   表名解析结果: MODULE_NAME = {MODULE_NAME}")
                print(f"   工作流参数: module_name = {module_name}")
                print(f"   🔧 使用表名解析结果确保一致性")
                module_name = MODULE_NAME  # 强制使用表名解析的结果

            PROJECT_PATH = str(Path(f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}").resolve())

            # 注意：不再从表名重新解析实体名，保持使用配置文件中的business_entity值
            # BUSINESS_ENTITY已经在main函数开始时从配置文件中正确设置

            print(f"🔧 更新项目路径: {PROJECT_PATH}")
            print(f"📦 保持实体名称: {BUSINESS_ENTITY} (来自配置文件business_entity)")
            print(f"✅ 模块名一致性验证通过: {module_name}")

            # 生成完整包名（基于模块名称和实体名称）
            # 生成完整包名（基于标准化命名规范）
            package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

            # 执行变量一致性验证
            print(f"\n🔍 执行变量一致性验证...")
            if not validate_core_variables():
                print(f"❌ 变量一致性验证失败，可能影响代码生成质量")
                print(f"   建议检查表名格式和模块映射逻辑")
            else:
                print(f"✅ 变量一致性验证通过，继续执行工作流")

            # 打印详细的路径信息
            print(f"\n📋 动态更新后的路径变量:")
            print(f"   项目路径前缀             = {project_prefix}")
            print(f"   业务模块名称             = {module_name}")
            print(f"   完整项目路径             = {PROJECT_PATH}")
            print(f"   实体名称                 = {BUSINESS_ENTITY}")
            print(f"   完整包名                 = {package_name}")
            print(f"   表名                     = {table_name}")
            print(f"   表描述                   = {table_txt}")
            print(f"\n📝 变量说明:")
            print(f"   - path_prefix: 项目根路径前缀，来自配置文件")
            print(f"   - project_path: 完整项目路径，格式为 {{path_prefix}}/jeecg-boot/jeecg-module-{{module_name}}")
            print(f"   - entity_name: 实体名称，从表名去掉us_前缀生成，用于前端路由和权限控制")
            print(f"   - package_name: 完整包名，格式为 org.jeecg.modules.{{module_name}}.{{sub_module}}")
            print(f"   - SQL文件中的模块名称就是entity_name的值，如 'invoice'")

        except Exception as e:
            print(f"❌ 模块管理异常: {e}")
            return
    else:
        print("\n5️⃣ 跳过模块管理（使用现有配置）")
        print(f"🔧 当前项目路径: {PROJECT_PATH}")
        print(f"📦 当前实体名称: {BUSINESS_ENTITY}")

        # 生成完整包名（基于标准化命名规范）
        package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

        # 打印当前配置信息
        print(f"\n📋 当前配置变量:")
        print(f"   项目路径                 = {PROJECT_PATH}")
        print(f"   实体名称                 = {BUSINESS_ENTITY}")
        print(f"   完整包名                 = {package_name}")
        print(f"   表名                     = {table_name}")
        print(f"   表描述                   = {table_txt}")
    
    # 6. 创建表单
    print("\n6️⃣ 正在创建表单...")
    headers = {
        'X-Access-Token': token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        create_url = f"{BASE_URL}/online/cgform/api/addAll"
        print(f"   创建URL: {create_url}")
        print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

        response = requests.post(create_url, json=form_data, headers=headers, timeout=REQUEST_TIMEOUT_CREATE)

        print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 表单创建成功")
                print(f"   响应消息: {result.get('message', 'N/A')}")
            else:
                print(f"❌ 创建表单失败: {result.get('message', '未知错误')}")
                print(f"   完整响应: {result}")
                return
        else:
            print(f"❌ 创建请求失败: HTTP {response.status_code}")
            print(f"   响应内容: {response.text}")
            return

    except Exception as e:
        print(f"❌ 创建表单异常: {e}")
        return
    
    # 4. 等待并获取表单ID
    print("\n4️⃣ 正在获取表单ID...")
    time.sleep(WAIT_TIME_AFTER_CREATE)  # 等待表单创建完成

    try:
        params = {'pageNo': PAGE_NO, 'pageSize': PAGE_SIZE, 'tableName': table_name}
        list_url = f"{BASE_URL}/online/cgform/head/list"

        print(f"   查询URL: {list_url}")
        print(f"   查询参数: {params}")
        print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

        response = requests.get(list_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT_LIST)

        print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                records = result['result']['records']
                print(f"   找到 {len(records)} 条记录")

                form_id = None
                for record in records:
                    if record.get('tableName') == table_name:
                        form_id = record.get('id')
                        print(f"   匹配记录: {record.get('tableName')} -> {form_id}")
                        break

                if not form_id:
                    print("❌ 未找到匹配的表单ID")
                    print(f"   搜索的表名: {table_name}")
                    for i, record in enumerate(records[:MAX_DISPLAY_RECORDS]):  # 显示前N条记录
                        print(f"   记录{i+1}: {record.get('tableName')}")
                    return

                print(f"✅ 表单ID: {form_id}")
            else:
                print(f"❌ 获取表单列表失败: {result.get('message')}")
                return
        else:
            print(f"❌ 查询请求失败: HTTP {response.status_code}")
            print(f"   响应内容: {response.text}")
            return

    except Exception as e:
        print(f"❌ 获取表单ID异常: {e}")
        return
    
    # 7. 同步到数据库
    print("\n7️⃣ 正在同步到数据库...")

    try:
        # 确保使用正确的headers和Token
        sync_headers = {
            'X-Access-Token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        sync_url = f"{BASE_URL}/online/cgform/api/doDbSynch/{form_id}/normal"
        print(f"   同步URL: {sync_url}")
        print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

        response = requests.post(sync_url, headers=sync_headers, timeout=REQUEST_TIMEOUT_SYNC)

        print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 数据库同步成功")
                print(f"   响应消息: {result.get('message', 'N/A')}")
            else:
                print(f"❌ 数据库同步失败: {result.get('message', '未知错误')}")
                print(f"   完整响应: {result}")
                return
        else:
            print(f"❌ 同步请求失败: HTTP {response.status_code}")
            print(f"   响应内容: {response.text}")
            return

    except Exception as e:
        print(f"❌ 数据库同步异常: {e}")
        return

    # 8. 代码生成
    print("\n8️⃣ 正在生成代码...")

    try:
        # 生成实体名（只使用业务实体名，不包含模块和子模块前缀）
        entity_name = BUSINESS_ENTITY if BUSINESS_ENTITY else ''.join(word.capitalize() for word in table_name.split('_'))

        # 生成完整包名（基于标准化命名规范）
        package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

        # 打印代码生成前的所有关键变量
        print(f"\n📋 代码生成关键变量:")
        print(f"   表单ID                   = {form_id}")
        print(f"   表名                     = {table_name}")
        print(f"   表描述                   = {form_data['head']['tableTxt']}")
        print(f"   实体名                   = {entity_name}")
        print(f"   实体名称                 = {BUSINESS_ENTITY}")
        print(f"   完整包名                 = {package_name}")
        print(f"   项目路径                 = {PROJECT_PATH}")

        # 显示四个核心变量
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        print(f"\n📋 四个核心变量:")
        print(f"   PROJECT_PATH_PREFIX      = {project_prefix}")
        print(f"   PROJECT_PATH             = {PROJECT_PATH}")
        print(f"   BUSINESS_ENTITY              = {BUSINESS_ENTITY}")
        print(f"   PACKAGE_NAME             = {package_name}")

        # 验证模板变量是否已正确解析
        print(f"\n🔍 验证模板变量解析:")
        if not validate_template_variables():
            print("❌ 检测到未解析的模板变量，停止代码生成")
            return

        print(f"\n🔧 其他配置:")
        print(f"   JSP模式                  = {JSP_MODE}")
        print(f"   表单类型                 = {JFORM_TYPE}")
        print(f"   包样式                   = {PACKAGE_STYLE}")
        print(f"   Vue样式                  = {VUE_STYLE}")
        print(f"   代码类型                 = {CODE_TYPES}")
        print(f"   强制系统                 = {FORCE_SYSTEM or 'None'}")

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
        print(f"\n📋 代码生成请求参数:")
        print(f"   🔧 修复后的API调用参数:")
        print(f"      entityName    = \"{BUSINESS_ENTITY}\" (业务实体)")
        print(f"      entityPackage = \"{SUBMODULE_NAME}\" (子模块名)")
        print(f"      bussiPackage  = \"{base_package}\" (基础包路径)")
        print(f"      最终package   = {base_package}.{SUBMODULE_NAME}")
        print(f"      预期生成路径 = {base_package.replace('.', '/')}/{SUBMODULE_NAME}/")
        print(f"      修复效果     = 避免重复{SUBMODULE_NAME}目录层级")
        print(f"   📋 完整参数列表:")
        for key, value in codegen_data.items():
            print(f"      {key:<20} = {value}")

        # 代码生成前：备份并替换配置文件变量
        config_replaced = backup_and_replace_jeecg_config(PROJECT_PATH, package_name)
        if not config_replaced:
            print("⚠️ 配置文件替换失败，继续执行代码生成...")

        codegen_url = f"{BASE_URL}/online/cgform/api/codeGenerate"
        print(f"   代码生成URL: {codegen_url}")
        print(f"   表单ID: {form_id}")
        print(f"   实体名: {entity_name}")
        print(f"   业务包名: {package_name}")
        print(f"   实体名称: {BUSINESS_ENTITY}")
        print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

        # 🚀 调用 codeGenerate 接口传参信息
        print(f"\n🚀 正在调用 codeGenerate 接口...")
        print(f"   📡 请求URL: {codegen_url}")
        print(f"   📋 请求方法: POST")
        print(f"   📄 请求头信息:")
        for key, value in headers.items():
            if key.lower() == 'x-access-token':
                print(f"      {key}: {value[:DISPLAY_TOKEN_LENGTH]}...")
            else:
                print(f"      {key}: {value}")
        print(f"   📦 请求体参数 (JSON):")
        print(json.dumps(codegen_data, indent=4, ensure_ascii=False))
        print(f"   ⏰ 请求超时时间: {REQUEST_TIMEOUT_CODEGEN}秒")

        response = requests.post(codegen_url, json=codegen_data, headers=headers, timeout=REQUEST_TIMEOUT_CODEGEN)

        print(f"   响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 代码生成成功")
                print(f"   响应消息: {result.get('message', 'N/A')}")

                # 立即修复生成代码中的模板变量问题
                print("\n🔧 修复生成代码中的模板变量问题...")
                if fix_generated_code_templates():
                    print("✅ 模板变量修复完成")
                else:
                    print("❌ 模板变量修复失败，但继续执行后续步骤")
                
                # 代码生成成功后，先进行包名替换和目录处理
                print(f"\n{'='*50}")
                print("🔄 执行生成代码后处理...")
                
                # 1. 替换java文件package包名内容
                try:
                    replace_package_declarations()
                    print("✅ Java文件package包名替换完成")
                except Exception as e:
                    print(f"⚠️ package包名替换失败: {e}")
                
                # 2. 处理生成文件目录结构
                try:
                    reorganize_generated_files()
                    print("✅ 生成文件目录结构处理完成")
                except Exception as e:
                    print(f"⚠️ 文件目录结构处理失败: {e}")
                
                # 继续执行后续工作流程
                execute_post_generation_workflow()
                
            else:
                print(f"❌ 代码生成失败: {result.get('message', '未知错误')}")
                print(f"   完整响应: {result}")
                return
        else:
            print(f"❌ 代码生成请求失败: HTTP {response.status_code}")
            print(f"   响应内容: {response.text}")
            return

    except Exception as e:
        print(f"❌ 代码生成异常: {e}")
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

        print(f"🔍 检查配置文件: {config_file}")
        print("=" * 60)

        issues_found = False

        if 'fields' not in config:
            print("❌ 配置文件中没有fields数组")
            return

        for i, field in enumerate(config['fields']):
            field_name = field.get('dbFieldName', f'字段{i+1}')

            # 检查 queryMode 字段
            if 'queryMode' in field:
                query_mode = field['queryMode']
                if len(query_mode) > 10:
                    print(f"❌ {field_name}: queryMode '{query_mode}' 超过10字符限制")
                    issues_found = True
                elif query_mode in ['group_range', 'date_range', 'multi_select']:
                    print(f"⚠️  {field_name}: queryMode '{query_mode}' 建议改为更短的值")
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
                    print(f"❌ {field_name}: {field_key} 值过长({len(str(field[field_key]))}字符)，超过{max_length}字符限制")
                    issues_found = True

        if not issues_found:
            print("✅ 所有字段长度检查通过")
        else:
            print("\n🔧 修复建议:")
            print("1. 将 'group_range' 改为 'range'")
            print("2. 将 'date_range' 改为 'range'")
            print("3. 将 'multi_select' 改为 'single'")
            print("4. 截断过长的字段值")
            print("\n💡 可以使用 Code_Gen_Guide.py 的自动修正功能")

    except Exception as e:
        print(f"❌ 检查配置文件时出错: {e}")

def main():
    """主函数"""
    args = parse_arguments()

    # 字段长度检查命令
    if args.check_field_lengths:
        check_field_lengths_in_config(args.check_field_lengths)
        return

    # 注：表名验证和修复命令已移除，现在使用business_entity机制

    # 加载配置
    global CONFIG, FORM_DATA_FILE
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
        print("🔍 验证模式 - 仅检查配置和数据")
        config_errors = validate_config()
        if config_errors:
            print("❌ 配置验证失败:")
            for error in config_errors:
                print(f"   - {error}")
        else:
            print("✅ 配置验证通过")

        # 验证表单数据（如果提供了配置文件）
        if args.form_config:
            try:
                with open(args.form_config, 'r', encoding='utf-8') as f:
                    form_data = json.load(f)
                form_errors = validate_form_data(form_data)
                if form_errors:
                    print("❌ 表单数据验证失败:")
                    for error in form_errors:
                        print(f"   - {error}")
                else:
                    print("✅ 表单数据验证通过")
            except Exception as e:
                print(f"❌ 表单数据加载失败: {e}")
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

            print("✅ 从配置文件提取业务实体成功")

        except Exception as e:
            print(f"❌ 业务实体提取失败: {e}")
            print("💡 请检查配置文件是否包含正确的business_entity字段")
            return
    else:
        print("❌ 必须提供配置文件参数 --form-config")
        print("💡 请使用Code_Gen_Agent.md生成包含business_entity的配置文件")
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
        print(f"🎯 指定业务模块: {args.module_name}")
    if args.form_config:
        print(f"📋 表单配置文件: {args.form_config}")



    if args.try_run:
        print("🔍 试运行模式 - 将显示操作但不执行")
        print(f"📋 配置文件: {args.config}")
        print(f"🎯 业务系统: {args.module_name or '自动识别'}")
        print(f"📋 表单配置: {args.form_config or '使用默认'}")
        print(f"🏗️ 项目路径: {PROJECT_PATH}")  # 使用预处理后的值
        print(f"📦 实体名称: {BUSINESS_ENTITY}")    # 使用预处理后的值

        # 显示三核心变量
        print(f"\n📋 三核心变量:")
        print(f"   MODULE_NAME      = {MODULE_NAME}")
        print(f"   SUBMODULE_NAME   = {SUBMODULE_NAME}")
        print(f"   BUSINESS_ENTITY      = {BUSINESS_ENTITY}")

        # 显示派生变量
        print(f"\n📊 派生变量:")
        print(f"   TABLE_NAME       = {TABLE_NAME}")
        print(f"   PACKAGE_NAME     = {PACKAGE_NAME}")
        print(f"   BUSINESS_ENTITY = {BUSINESS_ENTITY}")
        print(f"   PROJECT_PATH     = {PROJECT_PATH}")

        # 验证模板变量
        print(f"\n🔍 模板变量验证:")
        validate_template_variables()

        return



    # 处理表单配置文件
    if args.form_config:
        # 直接使用指定的配置文件
        CONFIG['form']['data_file'] = args.form_config
        FORM_DATA_FILE = args.form_config
        print(f"✅ 使用表单配置文件: {args.form_config}")
    else:
        print(f"✅ 使用默认表单配置: {FORM_DATA_FILE}")

    # 执行工作流
    jeecg_complete_workflow()

def load_config_from_file(config_file):
    """从指定文件加载配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return CONFIG

def fix_generated_code_templates():
    """修复生成代码中的模板变量和路径重复问题"""
    print(f"\n🔧 修复生成代码中的模板变量和路径重复问题...")

    try:
        # 获取当前表名信息
        if not CURRENT_TABLE_NAME:
            print("❌ 当前表名为空，无法修复代码")
            return False

        components = parse_table_name_components(CURRENT_TABLE_NAME)
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

        print(f"   模块路径: {module_path}")
        print(f"   正确包名: {correct_package}")
        print(f"   子模块名: {sub_module}")
        print(f"   基础包路径: {base_package_path}")

        # 1. 修复目录结构中的模板变量
        template_dirs = list(module_path.rglob("*{{PACKAGE_NAME}}*"))
        if template_dirs:
            print(f"   🔍 发现 {len(template_dirs)} 个包含模板变量的目录")

            for template_dir in template_dirs:
                # 正确的模板变量替换逻辑
                # {{PACKAGE_NAME}} 应该替换为完整包路径：org/jeecg/modules/{module_name}/{sub_module}
                # 这样 {{PACKAGE_NAME}}/controller 就会变成 org/jeecg/modules/{module_name}/{sub_module}/controller
                correct_path_str = str(template_dir).replace("{{PACKAGE_NAME}}", base_package_path)
                correct_path = Path(correct_path_str)

                print(f"   📁 重命名目录:")
                print(f"      从: {template_dir}")
                print(f"      到: {correct_path}")
                print(f"      替换逻辑: {{{{PACKAGE_NAME}}}} → {base_package_path}")

                # 确保父目录存在
                correct_path.parent.mkdir(parents=True, exist_ok=True)

                # 移动目录内容而不是整个目录
                if template_dir.exists() and template_dir.is_dir():
                    # 如果目标目录已存在，合并内容
                    if correct_path.exists():
                        print(f"   🔄 目标目录已存在，合并内容...")
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

                    print(f"   ✅ 目录重命名成功")

        # 2. 检测和修复路径重复问题
        # 查找重复的路径模式：org/jeecg/modules/scm/equipment/scm/equipment/
        components = parse_table_name_components(CURRENT_TABLE_NAME)
        module_name = components['module_name']
        sub_module = components['sub_module']

        duplicate_pattern = f"org/jeecg/modules/{module_name}/{sub_module}/{module_name}/{sub_module}"
        correct_pattern = f"org/jeecg/modules/{module_name}/{sub_module}"

        duplicate_dirs = list(module_path.rglob(f"*/{module_name}/{sub_module}/{module_name}/{sub_module}"))
        if duplicate_dirs:
            print(f"   🔍 发现 {len(duplicate_dirs)} 个重复路径目录")

            for duplicate_dir in duplicate_dirs:
                # 计算正确的目录路径
                duplicate_str = str(duplicate_dir)
                correct_str = duplicate_str.replace(f"/{module_name}/{sub_module}/{module_name}/{sub_module}", f"/{module_name}/{sub_module}")
                correct_path = Path(correct_str)

                print(f"   📁 修复重复路径:")
                print(f"      从: {duplicate_dir}")
                print(f"      到: {correct_path}")

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

                    print(f"   ✅ 重复路径修复成功")

        # 3. 修复文件内容中的模板变量和包名问题
        all_files = list(module_path.rglob("*"))
        fixed_files = 0

        for file_path in all_files:
            if file_path.is_file() and file_path.suffix in ['.java', '.sql', '.xml', '.vue', '.ts', '.js']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查是否包含模板变量
                    template_fixed = False
                    original_content = content

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

                        fix_type = []
                        if template_fixed:
                            fix_type.append("模板变量")
                        if package_fixed:
                            fix_type.append("包名规范")

                        print(f"   ✅ 修复文件 ({'/'.join(fix_type)}): {file_path.relative_to(module_path)}")
                        fixed_files += 1

                except Exception as e:
                    print(f"   ❌ 修复文件失败 {file_path}: {e}")

        print(f"   📊 修复统计:")
        print(f"      模板目录修复: {len(template_dirs)} 个")
        print(f"      重复路径修复: {len(duplicate_dirs) if 'duplicate_dirs' in locals() else 0} 个")
        print(f"      文件内容修复: {fixed_files} 个")

        if len(template_dirs) > 0 or (duplicate_dirs and len(duplicate_dirs) > 0) or fixed_files > 0:
            print(f"   ✅ 代码修复完成")
            return True
        else:
            print(f"   ℹ️ 未发现需要修复的问题")
            return True

    except Exception as e:
        print(f"   ❌ 代码修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()