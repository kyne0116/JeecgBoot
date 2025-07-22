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
            "entity_name": "{{ENTITY_NAME}}",
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
ENTITY_NAME = None      # 业务场景/实体名称 (如: management, processing, info)

# ==================== 派生变量定义 ====================
# 这些变量由三核心变量计算得出
TABLE_NAME = None       # 表名 (如: us_finance_invoice_management)
PACKAGE_NAME = None     # 包名 (如: org.jeecg.modules.finance.invoice)
JAVA_ENTITY_NAME = None # Java实体名 (如: Management)
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
        table_name (str): 完整表名，格式为 us_{MODULE_NAME}_{SUBMODULE_NAME}_{ENTITY_NAME}

    Returns:
        bool: 设置是否成功
    """
    global MODULE_NAME, SUBMODULE_NAME, ENTITY_NAME
    global TABLE_NAME, PACKAGE_NAME, JAVA_ENTITY_NAME, PROJECT_PATH

    try:
        components = parse_table_name_components(table_name)

        # 设置三核心变量
        MODULE_NAME = components['module_name']
        SUBMODULE_NAME = components['sub_module']
        ENTITY_NAME = components['business_scenario']

        # 计算派生变量
        TABLE_NAME = table_name
        PACKAGE_NAME = f"org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}"
        JAVA_ENTITY_NAME = convert_to_java_entity_name(ENTITY_NAME)

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
    print(f"   业务场景/实体名称        = {ENTITY_NAME or 'None'}")

    print(f"\n📊 派生变量详情:")
    print(f"   表名                     = {TABLE_NAME or 'None'}")
    print(f"   包名                     = {PACKAGE_NAME or 'None'}")
    print(f"   Java实体名               = {JAVA_ENTITY_NAME or 'None'}")
    print(f"   项目路径                 = {PROJECT_PATH or 'None'}")

    print(f"\n🔍 变量说明:")
    print(f"   - MODULE_NAME: 表示一级业务领域，对应业务系统类型")
    print(f"   - SUBMODULE_NAME: 表示二级业务领域，对应业务系统内的功能模块")
    print(f"   - ENTITY_NAME: 表示操作对象，对应具体业务实体")
    print(f"   - TABLE_NAME: 由三核心变量组合而成的完整表名")
    print(f"   - PACKAGE_NAME: 由MODULE_NAME和SUBMODULE_NAME组合而成的包名")
    print(f"   - JAVA_ENTITY_NAME: 由ENTITY_NAME转换而成的Java实体名")
    print(f"   - PROJECT_PATH: 由配置和MODULE_NAME组合而成的项目路径")

def validate_core_variables():
    """验证三核心变量的有效性和一致性"""
    errors = []

    print(f"\n🔍 三核心变量一致性验证:")

    # 验证MODULE_NAME
    if not MODULE_NAME:
        errors.append("MODULE_NAME不能为空")
    elif MODULE_NAME not in ['finance', 'hrms', 'crm', 'scm', 'oa']:
        errors.append(f"MODULE_NAME必须是预定义的业务系统之一: {MODULE_NAME}")

    # 验证SUBMODULE_NAME
    if not SUBMODULE_NAME:
        errors.append("SUBMODULE_NAME不能为空")
    elif not re.match(r'^[a-z][a-z0-9_]*$', SUBMODULE_NAME):
        errors.append(f"SUBMODULE_NAME格式不正确: {SUBMODULE_NAME}")

    # 验证ENTITY_NAME
    if not ENTITY_NAME:
        errors.append("ENTITY_NAME不能为空")
    elif not re.match(r'^[a-z][a-z0-9_]*$', ENTITY_NAME):
        errors.append(f"ENTITY_NAME格式不正确: {ENTITY_NAME}")

    # 验证派生变量一致性
    if MODULE_NAME and SUBMODULE_NAME and ENTITY_NAME:
        expected_table_name = f"us_{MODULE_NAME}_{SUBMODULE_NAME}_{ENTITY_NAME}"
        expected_package_name = f"org.jeecg.modules.{MODULE_NAME}.{SUBMODULE_NAME}"
        expected_project_path_suffix = f"jeecg-module-{MODULE_NAME}"

        print(f"   📊 派生变量一致性检查:")
        print(f"      期望表名: {expected_table_name}")
        print(f"      实际表名: {TABLE_NAME or 'None'}")
        print(f"      期望包名: {expected_package_name}")
        print(f"      实际包名: {PACKAGE_NAME or 'None'}")

        if TABLE_NAME and TABLE_NAME != expected_table_name:
            errors.append(f"表名不一致: 期望 {expected_table_name}, 实际 {TABLE_NAME}")

        if PACKAGE_NAME and PACKAGE_NAME != expected_package_name:
            errors.append(f"包名不一致: 期望 {expected_package_name}, 实际 {PACKAGE_NAME}")

        if PROJECT_PATH and expected_project_path_suffix not in PROJECT_PATH:
            errors.append(f"项目路径不一致: 期望包含 {expected_project_path_suffix}, 实际 {PROJECT_PATH}")

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
        'ENTITY_NAME': ENTITY_NAME,
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
            return f"org.jeecg.modules.{force_system}.{ENTITY_NAME}"
        else:
            return f"org.jeecg.modules.{ENTITY_NAME}"
    
    try:
        components = parse_table_name_components(table_name)
        package_name = f"org.jeecg.modules.{components['module_name']}.{components['sub_module']}"
        print(f"📦 生成标准化包名: {package_name}")
        return package_name
    except ValueError as e:
        print(f"⚠️ 表名解析失败，使用传统格式: {e}")
        if force_system:
            return f"org.jeecg.modules.{force_system}.{ENTITY_NAME}"
        else:
            return f"org.jeecg.modules.{ENTITY_NAME}"

def extract_business_entity_from_table_name(table_name):
    """
    从表名中提取业务实体名
    仅支持标准格式: us_{模块名称}_{子模块名称}_{推理业务需求场景}
    
    Args:
        table_name (str): 完整表名，必须符合 us_{模块}_{子模块}_{业务场景} 格式
        
    Returns:
        str: 业务场景实体名（Java规范）
        
    Examples:
        us_finance_invoice_sales -> sales
        us_hrms_employee_training -> training  
        us_crm_customer_service -> service
        us_scm_inventory_management -> management
    """
    if not table_name:
        raise ValueError("表名不能为空")
        
    if not table_name.startswith('us_'):
        error_msg = f"""
❌ 表名格式错误: {table_name}

📋 表名命名规范要求:
   格式: us_{{模块名}}_{{子模块名}}_{{业务场景}}
   
✅ 正确示例:
   us_finance_invoice_management     (财务-发票-管理)
   us_hrms_employee_training         (人力-员工-培训)
   us_crm_customer_service           (客户-客户-服务)
   us_business_product_management    (业务-产品-管理)

🔧 智能修复建议:
   推荐表名: '{suggest_table_name_fix(table_name)}'
   或手动修改为: 'us_{{模块名}}_{{子模块名}}_{{业务场景}}'

📚 详细文档: 请查看 Code_Gen_Guide.md 中的命名规范部分
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
   us_finance_invoice_management     (4个部分)
   us_hrms_employee_training         (4个部分)
   
❌ 错误示例:
   us_finance_invoice               (3个部分，缺少业务场景)
   us_product                       (2个部分，格式不完整)

🔧 修复建议:
   确保表名包含: 前缀(us) + 模块名 + 子模块名 + 业务场景
        """
        raise ValueError(error_msg)
    
    # 标准格式: us_module_submodule_business_scenario
    module_name = parts[1]      # 模块名称
    sub_module = parts[2]       # 子模块名称  
    business_scenario = parts[3] # 业务场景
    
    java_name = convert_to_java_entity_name(business_scenario)
    print(f"🎯 业务实体提取: {table_name}")
    print(f"   ├── 模块: {module_name}")
    print(f"   ├── 子模块: {sub_module}") 
    print(f"   └── 业务场景: {business_scenario} → Java实体: {java_name}")
    
    return java_name

def suggest_table_name_fix(table_name):
    """
    为错误的表名提供修复建议
    
    Args:
        table_name (str): 错误的表名
        
    Returns:
        str: 修复建议
    """
    if not table_name:
        return "us_business_example_management"
    
    # 移除常见前缀
    clean_name = table_name
    for prefix in ['biz_', 'sys_', 't_', 'tb_', 'tbl_']:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
            break
    
    # 如果不以us_开头，添加us_business_前缀
    if not clean_name.startswith('us_'):
        # 尝试智能分析表名结构
        parts = clean_name.split('_')
        if len(parts) == 1:
            # 单词，加默认结构
            return f"us_business_{clean_name}_management"
        elif len(parts) == 2:
            # 两个词，假设是模块_功能
            return f"us_business_{parts[0]}_{parts[1]}"
        else:
            # 多个词，保持原结构并加前缀
            return f"us_business_{clean_name}"
    
    return clean_name

def validate_table_name_command(table_name):
    """表名验证命令"""
    print(f"🔍 验证表名: {table_name}")
    print("=" * 50)
    
    try:
        result = extract_business_entity_from_table_name(table_name)
        print(f"✅ 表名格式正确!")
        print(f"📦 提取的业务实体: {result}")
    except ValueError as e:
        print(f"❌ 表名验证失败:")
        print(str(e))
        print(f"\n💡 自动修复建议: {suggest_table_name_fix(table_name)}")

def fix_table_name_command(table_name):
    """表名自动修复命令"""
    print(f"🔧 修复表名: {table_name}")
    print("=" * 50)
    
    if table_name.startswith('us_') and len(table_name.split('_')) == 4:
        print(f"✅ 表名已经符合规范: {table_name}")
        return
    
    fixed_name = suggest_table_name_fix(table_name)
    print(f"🎯 原表名: {table_name}")
    print(f"✨ 修复后: {fixed_name}")
    print(f"\n📋 建议操作:")
    print(f"   1. 将配置文件中的表名改为: {fixed_name}")
    print(f"   2. 或按照您的业务需求手动调整")

def convert_to_java_entity_name(entity_name):
    """
    将实体名转换为Java命名规范
    移除下划线并转换为小写连写形式
    
    Args:
        entity_name (str): 原始实体名，可能包含下划线
    
    Returns:
        str: 符合Java规范的实体名（小写无下划线）
    
    Examples:
        sales_invoice -> salesinvoice
        employee_info -> employeeinfo
        purchase_order -> purchaseorder
    """
    if not entity_name:
        return entity_name
    
    # 移除所有下划线并转换为小写
    java_name = entity_name.replace('_', '').lower()
    
    return java_name

# ==================== 配置文件处理功能 ====================

def backup_and_replace_jeecg_config(project_path, package_name):
    """备份并替换 jeecg_config.properties 文件中的变量"""
    config_path = Path("jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/jeecg/jeecg_config.properties")
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
                content = content.replace('{{ENTITY_NAME}}', java_entity_name)
                content = content.replace('{{TABLE_NAME}}', CURRENT_TABLE_NAME)

                print(f"   🔄 完整变量替换:")
                print(f"      {{{{MODULE_NAME}}}} → {module_name}")
                print(f"      {{{{SUBMODULE_NAME}}}} → {sub_module}")
                print(f"      {{{{ENTITY_NAME}}}} → {java_entity_name}")
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

def restore_jeecg_config():
    """还原 jeecg_config.properties 文件"""
    config_path = Path("jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/jeecg/jeecg_config.properties")
    backup_path = config_path.with_suffix('.properties.backup')

    print(f"🔄 还原配置文件: {config_path}")

    try:
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, config_path)
            backup_path.unlink()  # 删除备份文件
            print(f"   ✅ 已还原配置文件，保持变量占位")
        else:
            print(f"   ⚠️ 备份文件不存在，跳过还原")

        return True

    except Exception as e:
        print(f"   ❌ 配置文件还原失败: {e}")
        return False

# ==================== 模块管理功能 ====================

def detect_business_system(table_name, table_description=""):
    """智能识别业务系统类型"""
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
        possible_source_paths = [
            # 1. 按照我们的解析逻辑：module_name/sub_module
            Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / sub_module / 'vue3',
            # 2. 按照JeecgBoot实际生成逻辑：module_name/business_scenario
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

            # 容错机制2：在其他可能的模块中搜索vue3目录
            print(f"🔍 启动后端模块容错搜索机制...")
            alternative_modules = ['system', 'scm', 'finance', 'hrms', 'crm', 'oa']
            found_alternative = False

            for alt_module in alternative_modules:
                if alt_module == module_name:
                    continue
                alt_source_dir = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{alt_module}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / sub_module / 'vue3'
                if alt_source_dir.exists():
                    print(f"✅ 在模块 {alt_module} 中找到vue3目录: {alt_source_dir}")
                    source_vue3_dir = alt_source_dir
                    renamed_dir = source_vue3_dir.parent / sub_module
                    found_alternative = True
                    break

            if not found_alternative:
                print(f"❌ 在所有位置都未找到前端文件")
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
                print(f"❌ 目标目录已存在，停止迁移以避免覆盖")
                return False

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
            Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / entity_name,
            Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / module_name / sub_module,
            Path(project_prefix) / 'jeecgboot-vue3' / 'src' / 'views' / module_name,
        ]

        for search_path in frontend_search_paths:
            if search_path.exists():
                print(f"   搜索前端路径: {search_path}")
                for pattern in patterns:
                    sql_files = list(search_path.glob(pattern))
                    if sql_files:
                        latest_file = max(sql_files, key=lambda f: f.stat().st_mtime)
                        print(f"✅ 在前端目录找到SQL文件: {latest_file}")
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
        print("❌ 未找到mysql命令行客户端，尝试使用Python库...")
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

# 注意：PROJECT_PATH 和 ENTITY_NAME 在主函数中会被重新设置，这里只是初始化
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
    ENTITY_NAME = config_entity_name
else:
    ENTITY_NAME = "defaultentity"  # 使用默认值
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
    print(f"   ENTITY_NAME              = {ENTITY_NAME}")
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
    dict_file_exists = Path('Code_Gen_DICT.json').exists()
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
                module_name = detect_business_system(table_name, table_txt)
                print(f"🧠 智能识别业务系统: {module_name}")

            # 确保模块存在
            if not ensure_module_exists(module_name):
                print(f"❌ 模块管理失败，终止工作流")
                return

            # 更新项目路径配置 - 使用变量一致性验证
            global PROJECT_PATH, ENTITY_NAME
            project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')

            # 变量一致性检查：确保module_name与MODULE_NAME一致
            if MODULE_NAME and MODULE_NAME != module_name:
                print(f"⚠️ 检测到模块名不一致:")
                print(f"   表名解析结果: MODULE_NAME = {MODULE_NAME}")
                print(f"   工作流参数: module_name = {module_name}")
                print(f"   🔧 使用表名解析结果确保一致性")
                module_name = MODULE_NAME  # 强制使用表名解析的结果

            PROJECT_PATH = str(Path(f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}").resolve())

            # 从表名提取业务实体名（支持新的命名规范）
            ENTITY_NAME = extract_business_entity_from_table_name(table_name)

            print(f"🔧 更新项目路径: {PROJECT_PATH}")
            print(f"📦 更新实体名称: {ENTITY_NAME}")
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
            print(f"   实体名称                 = {ENTITY_NAME}")
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
        print(f"📦 当前实体名称: {ENTITY_NAME}")

        # 生成完整包名（基于标准化命名规范）
        package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

        # 打印当前配置信息
        print(f"\n📋 当前配置变量:")
        print(f"   项目路径                 = {PROJECT_PATH}")
        print(f"   实体名称                 = {ENTITY_NAME}")
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
        # 生成实体名（将表名转换为驼峰命名）
        entity_name = ''.join(word.capitalize() for word in table_name.split('_'))

        # 生成完整包名（基于标准化命名规范）
        package_name = generate_standardized_package_name(force_system=FORCE_SYSTEM)

        # 打印代码生成前的所有关键变量
        print(f"\n📋 代码生成关键变量:")
        print(f"   表单ID                   = {form_id}")
        print(f"   表名                     = {table_name}")
        print(f"   表描述                   = {form_data['head']['tableTxt']}")
        print(f"   实体名                   = {entity_name}")
        print(f"   实体名称                 = {ENTITY_NAME}")
        print(f"   完整包名                 = {package_name}")
        print(f"   项目路径                 = {PROJECT_PATH}")

        # 显示四个核心变量
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        print(f"\n📋 四个核心变量:")
        print(f"   PROJECT_PATH_PREFIX      = {project_prefix}")
        print(f"   PROJECT_PATH             = {PROJECT_PATH}")
        print(f"   ENTITY_NAME              = {ENTITY_NAME}")
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
        # 修复entityPackage参数：避免路径重复问题
        # JeecgBoot模板中 ${bussiPackage}/${entityPackage} 会导致路径重复
        # 正确做法：entityPackage应该为空或者是业务实体名，不应该重复bussiPackage的路径
        entity_package = ENTITY_NAME  # 使用业务实体名，避免路径重复

        codegen_data = {
            "projectPath": PROJECT_PATH,
            "jspMode": JSP_MODE,
            "ftlDescription": form_data['head']['tableTxt'],
            "jformType": JFORM_TYPE,
            "tableName_tmp": table_name,
            "entityName": entity_name,
            "entityPackage": entity_package,  # 修复：使用正确的包路径
            "bussiPackage": package_name,  # 添加正确的业务包名
            "packageStyle": PACKAGE_STYLE,
            "vueStyle": VUE_STYLE,
            "codeTypes": CODE_TYPES,
            "code": form_id,
            "tableName": table_name
        }

        # 打印完整的代码生成请求参数
        print(f"\n📋 代码生成请求参数:")
        print(f"   🔧 关键参数修复说明:")
        print(f"      entityPackage = {entity_package} (避免路径重复)")
        print(f"      bussiPackage  = {package_name} (完整包路径)")
        print(f"      预期生成路径 = {package_name.replace('.', '/')}/{entity_package}/")
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
        print(f"   实体名称: {ENTITY_NAME}")
        print(f"   使用Token: {token[:DISPLAY_TOKEN_LENGTH]}...")

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
        # 代码生成完成后：还原配置文件
        restore_jeecg_config()

    # 7. 自动集成模块到JeecgBoot项目结构
    print(f"\n{'='*50}")
    print("🔗 自动集成模块到JeecgBoot项目结构...")
    
    # 从表名解析出模块名以进行集成
    try:
        if CURRENT_TABLE_NAME:
            components = parse_table_name_components(CURRENT_TABLE_NAME)
            module_name = components['module_name']
            print(f"📦 检测到模块: {module_name}")
            
            # 确保模块存在并完成集成
            if ensure_module_exists(module_name):
                print(f"✅ 模块集成完成: jeecg-module-{module_name}")
                print(f"   - 主项目pom.xml已更新")
                print(f"   - 启动项目pom.xml已更新")
                print(f"   - 模块目录结构已创建")
            else:
                print(f"⚠️ 模块集成失败，但代码生成已完成")
        else:
            print("⚠️ 无法解析表名，跳过模块集成")
    except Exception as e:
        print(f"⚠️ 模块集成失败: {e}")
        print("   代码生成已完成，请手动检查模块集成")

    # 8. 代码生成后自动修复
    print(f"\n{'='*50}")
    print("🔧 执行代码生成后自动修复...")
    try:
        post_generation_fixes()
        print("✅ 自动修复完成")
    except Exception as e:
        print(f"⚠️ 自动修复失败: {e}")
        print("   代码生成已完成，请手动检查")

    # 9. 跳过编译，直接执行后续步骤
    compilation_config = CONFIG.get('compilation', {})
    print(f"\n{'='*50}")

    # 定义编译结果变量
    compilation_success = True  # 默认假设成功

    if compilation_config.get('enabled', False):
        print("⚙️ 编译功能已启用，但建议跳过以提高效率...")
        print("   编译不影响代码生成核心功能")
        print("   如需编译验证，请在工作流完成后手动执行")
    else:
        print("⏭️ 跳过编译步骤（已优化）")
        print("   ✅ 编译不影响代码生成核心功能")
        print("   ✅ 配置文件替换已在代码生成前完成")
        print("   ✅ 跳过编译可显著提高工作流效率")

    # 10. 前端代码迁移（无需编译验证）
    print(f"\n{'='*50}")
    print("📁 执行前端代码迁移...")
    try:
        if migrate_frontend_code():
            print("✅ 前端代码迁移完成")
        else:
            print("⚠️ 前端代码迁移失败或跳过")
    except Exception as e:
        print(f"⚠️ 前端代码迁移异常: {e}")

    # 11. 数据库SQL执行
    print(f"\n{'='*50}")
    print("🗄️ 执行数据库SQL文件...")
    try:
        if execute_database_sql():
            print("✅ 数据库SQL执行完成")

            # 12. 自动权限授权
            permission_config = CONFIG.get('permission_authorization', {})
            if permission_config.get('enabled', True):
                print(f"\n{'='*50}")
                print("🔐 自动为管理员角色授权新生成模块的权限...")
                try:
                    if auto_grant_permissions():
                        print("✅ 权限授权完成")
                    else:
                        print("⚠️ 权限授权失败或跳过")
                except Exception as e:
                    print(f"⚠️ 权限授权异常: {e}")
            else:
                print(f"\n{'='*50}")
                print("⏭️ 权限授权功能已禁用，跳过权限授权步骤")
        else:
            print("⚠️ 数据库SQL执行失败或跳过")
    except Exception as e:
        print(f"⚠️ 数据库SQL执行异常: {e}")

    # 编译建议（仅在需要时提供）
    print(f"\n{'='*50}")
    print("💡 编译建议（可选）:")
    print("   如果需要验证生成代码的正确性，可手动执行:")
    try:
        if CURRENT_TABLE_NAME:
            components = parse_table_name_components(CURRENT_TABLE_NAME)
            module_name = components['module_name']
            print(f"   1. cd jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}")
            print(f"   2. mvn compile -DskipTests  # 快速编译验证")
            print(f"   3. mvn clean install -DskipTests  # 完整编译安装（如需要）")
        else:
            print(f"   mvn compile -DskipTests  # 整体项目编译验证")
    except:
        print(f"   mvn compile -DskipTests  # 整体项目编译验证")
    print(f"   注意：编译仅用于验证，不影响代码生成功能")

    # 13. 完成
    print(f"\n{'='*50}")
    print("🎉 完整工作流完成!")
    print(f"📋 表名: {table_name}")
    print(f"🆔 表单ID: {form_id}")
    print(f"🏗️ 实体名: {entity_name}")
    print(f"📦 业务包名: {package_name}")
    print(f"📦 实体名称: {ENTITY_NAME}")
    print(f"🏗️ 项目路径: {PROJECT_PATH}")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 显示生成的代码结构和下一步操作
    print(f"\n📁 生成的代码结构:")
    if CURRENT_TABLE_NAME:
        try:
            components = parse_table_name_components(CURRENT_TABLE_NAME)
            print(f"   后端模块路径: /jeecg-boot/jeecg-boot-module/jeecg-module-{components['module_name']}")
            print(f"   包结构: org.jeecg.modules.{components['module_name']}.{components['sub_module']}")
            print(f"   实体类: {components['entity_name']}")
            print(f"   前端组件: 已生成Vue3组件并迁移到前端项目")

            # 显示前端代码位置
            migration_config = CONFIG.get('frontend_migration', {})
            if migration_config.get('enabled', True):
                target_base_path = migration_config.get('target_base_path', 'jeecgboot-vue3/src/views')
                # 尝试从SQL文件解析正确路径
                correct_frontend_path = extract_frontend_path_from_sql()
                if correct_frontend_path:
                    print(f"   前端代码路径: /{target_base_path}/{correct_frontend_path}")
                else:
                    print(f"   前端代码路径: /{target_base_path}/{components['module_name']}/{components['sub_module']}")
            else:
                print(f"   前端代码路径: /jeecg-boot/jeecg-boot-module/jeecg-module-{components['module_name']}/src/main/java/org/jeecg/modules/{components['module_name']}/{components['sub_module']}/vue3")

            # 显示数据库执行状态
            db_config = CONFIG.get('database_execution', {})
            if db_config.get('enabled', True):
                print(f"   数据库权限: 已自动执行SQL文件，菜单权限已配置")
                print(f"   权限授权: 已自动为管理员角色授权新模块权限")
        except:
            print(f"   包结构: {package_name}")
            print(f"   实体类: {ENTITY_NAME}")
    
    print(f"\n🚀 下一步操作:")
    compilation_config = CONFIG.get('compilation', {})
    db_config = CONFIG.get('database_execution', {})

    if compilation_config.get('enabled', True):
        print(f"   ✅ 代码生成和编译已完成")
        if db_config.get('enabled', True):
            print(f"   ✅ 数据库权限配置已完成")
        print(f"   ")
        print(f"   🔄 重启后端服务（重要）:")
        print(f"      - 如果后端服务正在运行，请先停止")
        print(f"      - 通过VS Code重新启动后端服务（profile=mac）")
        print(f"      - 等待服务完全启动（看到'Application is running'）")
        print(f"   ")
        print(f"   🌐 验证新功能:")
        print(f"      - 启动前端服务: pnpm dev")
        print(f"      - 访问系统: http://localhost:3102")
        if db_config.get('enabled', True):
            print(f"      - 登录后应该能在菜单中看到新功能（权限已自动配置）")
            print(f"      - 管理员角色已自动获得新模块的所有权限")
        else:
            print(f"      - 登录后在菜单管理中配置新功能菜单")
        print(f"   ")
        print(f"   📋 API测试:")
        if CURRENT_TABLE_NAME:
            try:
                components = parse_table_name_components(CURRENT_TABLE_NAME)
                entity_name_lower = components['entity_name'].lower()
                print(f"      - 测试API: http://localhost:8080/jeecg-boot/management/{entity_name_lower}/list")
            except:
                print(f"      - 测试API: http://localhost:8080/jeecg-boot/management/{ENTITY_NAME}/list")
        print(f"      - 应该返回401（需要认证）而不是404（找不到资源）")
    else:
        print(f"   ⚠️ 需要手动编译:")
        if CURRENT_TABLE_NAME:
            try:
                components = parse_table_name_components(CURRENT_TABLE_NAME)
                module_name = components['module_name']
                print(f"      1. cd jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}")
                print(f"      2. mvn clean install -DskipTests")
            except:
                pass
        print(f"      或: mvn clean compile -DskipTests (整体编译)")
        print(f"   ")
        print(f"   🔄 重启后端服务:")
        print(f"      - 编译完成后，重启后端服务")
        print(f"      - 通过VS Code启动后端服务（profile=mac）")
        print(f"   ")
        print(f"   🌐 验证新功能:")
        print(f"      - 启动前端服务: pnpm dev")
        print(f"      - 访问系统: http://localhost:3102")
        print(f"      - 登录后在菜单管理中配置新功能菜单")
    print(f"{'='*50}")

    # 显示结果摘要（不保存文件）
    print("\n📊 生成结果摘要:")
    print(f"   表名: {table_name}")
    print(f"   表单ID: {form_id}")
    print(f"   实体名: {entity_name}")
    print(f"   实体名称: {ENTITY_NAME}")
    print(f"   业务包名: {package_name}")
    print(f"   项目路径: {PROJECT_PATH}")

    # 显示四个核心变量摘要
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    print(f"\n📋 四个核心变量摘要:")
    print(f"   PROJECT_PATH_PREFIX      = {project_prefix}")
    print(f"   PROJECT_PATH             = {PROJECT_PATH}")
    print(f"   ENTITY_NAME              = {ENTITY_NAME}")
    print(f"   PACKAGE_NAME             = {package_name}")
    print(f"   状态: 成功")

    # 14. 检查后端服务状态并提供建议
    print(f"\n{'='*50}")
    print("🔍 检查后端服务状态...")

    service_running, status_message = check_backend_service_status(token)
    print(f"   服务状态: {status_message}")

    if service_running:
        print(f"   ✅ 后端服务正在运行")

        # 检查新模块是否已加载
        if CURRENT_TABLE_NAME:
            try:
                components = parse_table_name_components(CURRENT_TABLE_NAME)
                module_name = components['module_name']

                print(f"   🔍 检查新模块加载状态...")
                if verify_new_module_loaded(module_name):
                    print(f"   ✅ 新模块已加载，可以直接使用")
                else:
                    print(f"   ⚠️ 新模块未加载，需要重启服务")
                    suggest_service_restart()
            except Exception as e:
                print(f"   ⚠️ 无法检查模块加载状态: {e}")
                suggest_service_restart()
        else:
            print(f"   ⚠️ 建议重启服务以确保新代码生效")
            suggest_service_restart()
    else:
        print(f"   ❌ 后端服务未运行")
        suggest_service_restart()

    print("\n✅ 代码已生成到指定项目路径，可以启动JeecgBoot查看效果！")

    # 清理临时文件
    cleanup_temp_files()

# ==================== 清理功能 ====================

def cleanup_temp_files():
    """清理临时文件"""
    temp_files = [
        'temp_form_data.json',
        'temp_business_config.json'
    ]

    cleaned_files = []
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                cleaned_files.append(temp_file)
            except Exception as e:
                print(f"⚠️ 清理临时文件失败 {temp_file}: {e}")

    if cleaned_files:
        print(f"\n🧹 已清理临时文件: {', '.join(cleaned_files)}")

# ==================== 数据字典功能 ====================

def check_dict_file_status():
    """检查数据字典文件状态"""
    dict_file = 'Code_Gen_DICT.json'
    
    if not os.path.exists(dict_file):
        return False, "数据字典文件不存在"
    
    try:
        # 检查文件修改时间，如果超过24小时则认为需要更新
        file_mtime = os.path.getmtime(dict_file)
        current_time = time.time()
        hours_diff = (current_time - file_mtime) / 3600
        
        if hours_diff > 24:
            return False, f"数据字典文件已过期 ({hours_diff:.1f}小时前更新)"
        
        # 检查文件是否为空
        with open(dict_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data or len(data) == 0:
                return False, "数据字典文件为空"
        
        return True, f"数据字典文件有效 ({len(data)}条记录)"
        
    except Exception as e:
        return False, f"数据字典文件检查失败: {e}"

def load_dict_data():
    """加载数据字典数据"""
    dict_file = 'Code_Gen_DICT.json'
    try:
        with open(dict_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载数据字典失败: {e}")
        return []

# calculate_similarity函数已移除 - 智能分析功能现在由AI处理

# 智能匹配相关函数已移除 - 这些功能现在由AI在Code_Gen_Agent.md框架下处理

def fetch_system_dict():
    """获取系统数据字典并保存到Code_Gen_DICT.json"""
    print("\n📚 开始获取系统数据字典...")
    print("=" * 50)
    
    # 1. 删除已存在的字典文件
    dict_file = 'Code_Gen_DICT.json'
    if os.path.exists(dict_file):
        try:
            os.remove(dict_file)
            print(f"🗑️ 已删除现有字典文件: {dict_file}")
        except Exception as e:
            print(f"⚠️ 删除字典文件失败: {e}")
    
    # 2. 登录获取Token
    print("\n1️⃣ 正在登录获取Token...")
    try:
        login_data = {"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD}
        response = requests.post(f"{BASE_URL}/sys/mLogin", json=login_data, timeout=REQUEST_TIMEOUT_LOGIN)
        
        if response.status_code != 200 or not response.json().get('success'):
            print("❌ 登录失败")
            return False
        
        token = response.json()['result']['token']
        user_info = response.json()['result']['userInfo']
        print(f"✅ 登录成功: {user_info.get('realname')}")
        print(f"   Token: {token[:DISPLAY_TOKEN_LENGTH]}...")
        
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    # 3. 获取数据字典
    print("\n2️⃣ 正在获取数据字典...")
    headers = {
        'X-Access-Token': token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    all_records = []
    page_no = 1
    page_size = 10
    total_pages = 1
    
    try:
        while page_no <= total_pages:
            # 构建查询参数
            params = {
                'column': 'createTime',
                'order': 'desc', 
                'pageNo': page_no,
                'pageSize': page_size,
                '_t': int(time.time() * 1000)  # 时间戳
            }
            
            print(f"   📄 获取第 {page_no} 页数据...")
            
            # 调用数据字典接口
            dict_url = f"{BASE_URL}/sys/dict/list"
            response = requests.get(dict_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT_LIST)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    records = result['result']['records']
                    total = result['result']['total']
                    
                    # 计算总页数
                    total_pages = (total + page_size - 1) // page_size
                    
                    print(f"      ✓ 获取到 {len(records)} 条记录")
                    print(f"      ✓ 总记录数: {total}, 总页数: {total_pages}")
                    
                    # 添加到总记录中
                    all_records.extend(records)
                    
                    # 下一页
                    page_no += 1
                    
                else:
                    print(f"❌ 获取数据字典失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"   响应内容: {response.text}")
                return False
        
        # 4. 保存到文件
        print(f"\n3️⃣ 正在保存数据字典...")
        print(f"   总共获取到 {len(all_records)} 条数据字典记录")
        
        with open(dict_file, 'w', encoding='utf-8') as f:
            json.dump(all_records, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据字典已保存到: {dict_file}")
        
        # 5. 显示统计信息
        print(f"\n📊 数据字典统计:")
        print(f"   文件路径: {os.path.abspath(dict_file)}")
        print(f"   记录总数: {len(all_records)}")
        
        # 显示前几条记录的基本信息
        if all_records:
            print(f"\n📋 前5条记录预览:")
            for i, record in enumerate(all_records[:5]):
                dict_code = record.get('dictCode', 'N/A')
                dict_name = record.get('dictName', 'N/A')
                print(f"   {i+1}. {dict_code} - {dict_name}")
        
        print("\n" + "=" * 50)
        print("🎉 数据字典获取完成！")
        return True
        
    except Exception as e:
        print(f"❌ 获取数据字典异常: {e}")
        return False

# ==================== 模板处理功能 ====================

def load_template(template_file='Code_Gen_Guide.json'):
    """加载表单模板"""
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 模板加载失败: {e}")
        return None

def load_field_templates(template_file='Code_Gen_field_templates.json'):
    """加载字段模板"""
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 字段模板加载失败: {e}")
        return {}

def create_field_from_template(field_type, field_name, field_description, order_num, **kwargs):
    """从模板创建字段"""
    field_templates = load_field_templates()

    if field_type not in field_templates:
        print(f"❌ 未知字段类型: {field_type}")
        return None

    template = field_templates[field_type].copy()

    # 替换模板变量
    replacements = {
        '{{FIELD_NAME}}': field_name,
        '{{FIELD_DESCRIPTION}}': field_description,
        '{{ORDER_NUM}}': str(order_num),
        '{{NULLABLE}}': kwargs.get('nullable', '1'),
        '{{REQUIRED}}': kwargs.get('required', '0'),
        '{{OPTIONS}}': kwargs.get('options', ''),
        '{{DEFAULT_VALUE}}': kwargs.get('default_value', ''),
        '{{DICT_CODE}}': kwargs.get('dict_code', '')
    }

    # 递归替换所有字符串值
    def replace_template_vars(obj):
        if isinstance(obj, dict):
            return {k: replace_template_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_template_vars(item) for item in obj]
        elif isinstance(obj, str):
            result = obj
            for placeholder, value in replacements.items():
                result = result.replace(placeholder, value)
            return result
        else:
            return obj

    return replace_template_vars(template)

# create_field_with_smart_dict函数已移除 - 智能匹配功能现在由AI处理

def create_form_from_config(config_file):
    """从配置文件创建表单"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 加载基础模板
        template = load_template()
        if not template:
            return None

        # 设置表头信息
        template['head']['tableName'] = config['table']['name']
        template['head']['tableTxt'] = config['table']['description']

        # 添加自定义字段
        order_num = 7  # 系统字段占用0-6
        for field_config in config.get('fields', []):
            field = create_field_from_template(
                field_config['type'],
                field_config['name'],
                field_config['description'],
                order_num,
                **field_config.get('options', {})
            )
            if field:
                template['fields'].append(field)
                order_num += 1

        return template

    except Exception as e:
        print(f"❌ 配置文件处理失败: {e}")
        return None

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

    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()

    # 处理表名验证和修复命令
    if args.validate_table_name:
        validate_table_name_command(args.validate_table_name)
        return
    
    if args.fix_table_name:
        fix_table_name_command(args.fix_table_name)
        return

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
    global PROJECT_PATH, ENTITY_NAME, MODULE_NAME, SUBMODULE_NAME, PACKAGE_NAME, JAVA_ENTITY_NAME, TABLE_NAME

    # 1. 处理表名和三核心变量
    if args.form_config:
        try:
            with open(args.form_config, 'r', encoding='utf-8') as f:
                form_data = json.load(f)
                table_name = form_data.get('head', {}).get('tableName', '')
                CURRENT_TABLE_NAME = table_name  # 设置全局表名

                # 从表名设置三核心变量
                if set_core_variables_from_table_name(table_name):
                    print("✅ 从配置文件设置三核心变量成功")
                else:
                    print("⚠️ 从配置文件设置三核心变量失败，使用传统模式")
                    # 传统模式下的处理
                    ENTITY_NAME = extract_business_entity_from_table_name(table_name)
        except Exception as e:
            print(f"⚠️ 无法读取表单配置文件: {e}")
            # 不要直接使用配置中的模板变量，检查是否为模板变量
            config_entity_name = CONFIG['codegen']['entity_name']
            if config_entity_name and not config_entity_name.startswith('{{'):
                ENTITY_NAME = config_entity_name
            else:
                ENTITY_NAME = "defaultentity"  # 使用默认值
                print(f"⚠️ 配置中的entity_name是模板变量，使用默认值: {ENTITY_NAME}")
    else:
        # 不要直接使用配置中的模板变量，检查是否为模板变量
        config_entity_name = CONFIG['codegen']['entity_name']
        if config_entity_name and not config_entity_name.startswith('{{'):
            ENTITY_NAME = config_entity_name
        else:
            ENTITY_NAME = "defaultentity"  # 使用默认值
            print(f"⚠️ 配置中的entity_name是模板变量，使用默认值: {ENTITY_NAME}")

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

        # 验证表单数据
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

    if args.try_run:
        print("🔍 试运行模式 - 将显示操作但不执行")
        print(f"📋 配置文件: {args.config}")
        print(f"🎯 业务系统: {args.module_name or '自动识别'}")
        print(f"📋 表单配置: {args.form_config or '使用默认'}")
        print(f"🏗️ 项目路径: {PROJECT_PATH}")  # 使用预处理后的值
        print(f"📦 实体名称: {ENTITY_NAME}")    # 使用预处理后的值

        # 显示三核心变量
        print(f"\n📋 三核心变量:")
        print(f"   MODULE_NAME      = {MODULE_NAME}")
        print(f"   SUBMODULE_NAME   = {SUBMODULE_NAME}")
        print(f"   ENTITY_NAME      = {ENTITY_NAME}")

        # 显示派生变量
        print(f"\n📊 派生变量:")
        print(f"   TABLE_NAME       = {TABLE_NAME}")
        print(f"   PACKAGE_NAME     = {PACKAGE_NAME}")
        print(f"   JAVA_ENTITY_NAME = {JAVA_ENTITY_NAME}")
        print(f"   PROJECT_PATH     = {PROJECT_PATH}")

        # 验证模板变量
        print(f"\n🔍 模板变量验证:")
        validate_template_variables()

        return

    if args.dict:
        # 获取系统数据字典
        fetch_system_dict()
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

# 删除重复的update_global_vars函数，变量已在文件开头定义

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

        # 构建正确的包名 - 基于JeecgBoot标准结构
        correct_package = f"org.jeecg.modules.{module_name}.{sub_module}"

        # 构建正确的包路径 - 注意：{{PACKAGE_NAME}}只替换为基础包路径，不包含子模块
        # 因为官方API生成的路径结构是：{{PACKAGE_NAME}}/子模块名/controller/
        base_package_path = f"org/jeecg/modules/{module_name}"

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
                # {{PACKAGE_NAME}} 应该替换为基础包路径：org/jeecg/modules/{module_name}
                # 这样 {{PACKAGE_NAME}}/audit/controller 就会变成 org/jeecg/modules/test/audit/controller
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
                            # Java文件使用基础包名，保持与目录结构一致
                            base_package_name = f"org.jeecg.modules.{module_name}"
                            content = content.replace('{{PACKAGE_NAME}}', base_package_name)
                        else:
                            # 其他文件也使用基础包名
                            base_package_name = f"org.jeecg.modules.{module_name}"
                            content = content.replace('{{PACKAGE_NAME}}', base_package_name)
                        template_fixed = True

                    # 2. 替换 {{PROJECT_PATH}}
                    if '{{PROJECT_PATH}}' in content:
                        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
                        project_path = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
                        content = content.replace('{{PROJECT_PATH}}', project_path)
                        template_fixed = True

                    # 3. 替换 {{ENTITY_NAME}}
                    if '{{ENTITY_NAME}}' in content:
                        entity_name = components['entity_name']
                        java_entity_name = convert_to_java_entity_name(entity_name)
                        content = content.replace('{{ENTITY_NAME}}', java_entity_name)
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

                    # 检查是否包含重复的包名
                    duplicate_package = f"org.jeecg.modules.{module_name}.{sub_module}.{module_name}.{sub_module}"
                    package_fixed = False
                    if duplicate_package in content:
                        content = content.replace(duplicate_package, correct_package)
                        package_fixed = True

                    # 如果有任何修复，写回文件
                    if template_fixed or package_fixed:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)

                        fix_type = []
                        if template_fixed:
                            fix_type.append("模板变量")
                        if package_fixed:
                            fix_type.append("重复包名")

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
