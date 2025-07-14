#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot 通用表单工作流脚本
完整流程：登录 → 创建表单 → 获取ID → 同步数据库 → 生成代码
支持：配置文件驱动、模板系统、命令行参数、批量操作
"""

import requests
import json
import random
import time
import argparse
import re
import subprocess
import platform
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# ==================== 配置加载 ====================
import os

def load_config():
    """加载配置文件"""
    config_file = 'Code_Gen_Config.json'
    default_config = {
        "project": {
            "path_prefix": "/Users/admin/Work/Github/JeecgBoot"
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
        # 创建默认配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        print(f"✅ 已创建默认配置文件: {config_file}")

    return default_config

# 加载配置
CONFIG = load_config()

# 全局标志变量
SKIP_MODULE_MANAGEMENT = False
FORCE_SYSTEM = None

# ==================== Java命名规范转换功能 ====================

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
        raise ValueError(f"表名必须以 'us_' 开头: {table_name}")
        
    parts = table_name.split('_')
    
    if len(parts) != 4:
        raise ValueError(f"表名格式错误，必须为 us_{{模块名称}}_{{子模块名称}}_{{推理业务需求场景}} 格式: {table_name}")
    
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

    try:
        # 备份原文件
        if config_path.exists():
            import shutil
            shutil.copy2(config_path, backup_path)
            print(f"   ✅ 已备份原配置文件: {backup_path}")

        # 读取原文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换变量
        content = content.replace('{{PROJECT_PATH}}', str(project_path))
        content = content.replace('{{PACKAGE_NAME}}', package_name)

        # 写入替换后的内容
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"   ✅ 已替换变量:")
        print(f"      PROJECT_PATH = {project_path}")
        print(f"      PACKAGE_NAME = {package_name}")

        return True

    except Exception as e:
        print(f"   ❌ 配置文件替换失败: {e}")
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

def update_main_pom(module_name):
    """更新主项目pom.xml添加新模块"""
    # 获取路径前缀
    project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
    pom_path = Path(project_prefix) / 'jeecg-boot' / 'pom.xml'

    print(f"📝 更新主项目pom.xml: {pom_path.absolute()}")

    if not pom_path.exists():
        print(f"❌ 主项目pom.xml不存在: {pom_path}")
        return False

    try:
        # 解析XML
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # 查找命名空间
        namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
        if root.tag.startswith('{'):
            namespace_uri = root.tag[1:root.tag.index('}')]
            namespace = {'maven': namespace_uri}

        # 查找modules节点
        modules_element = root.find('.//maven:modules', namespace) or root.find('.//modules')

        if modules_element is None:
            print("❌ 未找到modules节点")
            return False

        # 检查模块是否已存在
        module_artifact_id = f"jeecg-module-{module_name}"
        existing_modules = [elem.text for elem in modules_element.findall('.//maven:module', namespace) or modules_element.findall('.//module')]

        if module_artifact_id in existing_modules:
            print(f"✅ 模块已存在于pom.xml中: {module_artifact_id}")
            return True

        # 添加新模块
        new_module = ET.SubElement(modules_element, 'module')
        new_module.text = module_artifact_id

        # 保存文件
        tree.write(pom_path, encoding='utf-8', xml_declaration=True)
        print(f"✅ 已添加模块到主项目pom.xml: {module_name}")
        return True

    except Exception as e:
        print(f"❌ 更新主项目pom.xml失败: {e}")
        return False

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
        # 解析XML
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # 查找命名空间
        namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
        if root.tag.startswith('{'):
            namespace_uri = root.tag[1:root.tag.index('}')]
            namespace = {'maven': namespace_uri}

        # 查找dependencies节点
        dependencies_element = root.find('.//maven:dependencies', namespace) or root.find('.//dependencies')

        if dependencies_element is None:
            print("❌ 未找到dependencies节点")
            return False

        # 检查依赖是否已存在
        artifact_id = f"jeecg-module-{module_name}"
        existing_deps = []
        for dep in dependencies_element.findall('.//maven:dependency', namespace) or dependencies_element.findall('.//dependency'):
            artifact_elem = dep.find('.//maven:artifactId', namespace) or dep.find('.//artifactId')
            if artifact_elem is not None:
                existing_deps.append(artifact_elem.text)

        if artifact_id in existing_deps:
            print(f"✅ 依赖已存在于启动项目pom.xml中: {artifact_id}")
            return True

        # 添加新依赖
        new_dependency = ET.SubElement(dependencies_element, 'dependency')

        group_id = ET.SubElement(new_dependency, 'groupId')
        group_id.text = 'org.jeecgframework.boot'

        artifact_id_elem = ET.SubElement(new_dependency, 'artifactId')
        artifact_id_elem.text = artifact_id

        version = ET.SubElement(new_dependency, 'version')
        version.text = '${jeecgboot.version}'

        # 保存文件
        tree.write(pom_path, encoding='utf-8', xml_declaration=True)
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
        return True

    # 2. 创建模块
    print(f"📦 模块不存在，开始创建...")
    if not create_maven_module(module_name):
        return False

    # 3. 更新主项目pom.xml
    if not update_main_pom(module_name):
        return False

    # 4. 更新启动项目pom.xml
    if not update_system_start_pom(module_name):
        return False

    # 5. 验证模块创建结果
    if check_module_exists(module_name):
        print(f"🎉 模块创建和配置完成: jeecg-module-{module_name}")
        return True
    else:
        print(f"❌ 模块创建验证失败")
        return False

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

PROJECT_PATH = CONFIG['codegen']['project_path']
ENTITY_NAME = CONFIG['codegen']['entity_name']
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

    # 生成完整包名（基于模块名称和实体名称）
    if FORCE_SYSTEM:
        # 使用指定的模块名称生成包名
        package_name = f"org.jeecg.modules.{FORCE_SYSTEM}.{ENTITY_NAME}"
    else:
        # 默认包名（仅使用实体名称，兼容旧版本）
        package_name = f"org.jeecg.modules.{ENTITY_NAME}"

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

    # 运行环境信息
    print("\n💻 运行环境信息:")
    print(f"   操作系统                 = {platform.system()} {platform.release()}")
    print(f"   Python版本               = {platform.python_version()}")
    print(f"   当前工作目录             = {Path.cwd()}")
    print(f"   配置文件路径             = {Path('Code_Gen_Config.json').absolute()}")

    print("=" * 80)

def jeecg_complete_workflow():
    """JeecgBoot完整表单工作流"""

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

    # 2. 自动确保数据字典数据最新
    print("\n2️⃣ 智能数据字典检查...")
    if not auto_ensure_dict_data():
        print("⚠️ 数据字典获取失败，将跳过智能匹配")
        dict_data = []
    else:
        dict_data = load_dict_data()
        print(f"✅ 加载数据字典: {len(dict_data)}条记录")

    # 3. 准备表单数据
    print("\n3️⃣ 准备表单数据...")
    try:
        with open(FORM_DATA_FILE, 'r', encoding='utf-8') as f:
            form_data = json.load(f)

        # 使用JSON文件中预设的表名，如果没有则生成随机表名
        table_name = form_data['head'].get('tableName')
        table_txt = form_data['head'].get('tableTxt')

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

        # 4. 智能字段分析和数据字典匹配
        print("\n4️⃣ 智能字段数据字典匹配...")
        if dict_data:
            enhanced_count = 0
            suggested_count = 0
            
            for field in form_data.get('fields', []):
                field_desc = field.get('dbFieldTxt', '')
                if field_desc and field.get('orderNum', 0) >= 7:  # 只处理业务字段
                    matches = match_dict_field(field_desc, dict_data)
                    if matches:
                        best_match = matches[0]
                        
                        # 自动应用高分匹配
                        if best_match['score'] >= 8:  # 高分匹配自动应用
                            # 更新字段配置为数据字典字段
                            if '是否' in field_desc or '启用' in field_desc:
                                field['fieldShowType'] = 'radio'
                                field['queryShowType'] = 'radio'
                            else:
                                field['fieldShowType'] = 'text'  # 下拉选择
                            
                            field['dictField'] = best_match['dict_code']
                            field['dictTable'] = ''
                            field['dictText'] = ''
                            
                            enhanced_count += 1
                            print(f"   ✓ {field_desc} -> {best_match['dict_name']} ({best_match['match_type']}, 分数:{best_match['score']})")
                        
                        # 显示中等匹配的建议
                        elif best_match['score'] >= 5:  # 中等匹配显示建议
                            suggested_count += 1
                            print(f"   💡 建议: {field_desc} -> {best_match['dict_name']} ({best_match['match_type']}, 分数:{best_match['score']})")
                            
                            # 显示所有候选项（前3个）
                            if len(matches) > 1:
                                for i, match in enumerate(matches[:3], 1):
                                    print(f"      {i}. {match['dict_name']} ({match['match_type']}, 分数:{match['score']})")
            
            if enhanced_count > 0:
                print(f"✅ 智能匹配完成: {enhanced_count}个字段已自动关联数据字典")
            if suggested_count > 0:
                print(f"💡 发现 {suggested_count}个字段的潜在匹配建议（可手动配置）")
            if enhanced_count == 0 and suggested_count == 0:
                print("ℹ️ 未发现需要数据字典匹配的字段")
        else:
            print("⚠️ 跳过智能匹配: 数据字典数据不可用")

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

            # 更新项目路径配置
            global PROJECT_PATH, ENTITY_NAME
            project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
            PROJECT_PATH = str(Path(f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}").resolve())

            # 从表名提取业务实体名（支持新的命名规范）
            ENTITY_NAME = extract_business_entity_from_table_name(table_name)

            print(f"🔧 更新项目路径: {PROJECT_PATH}")
            print(f"📦 更新实体名称: {ENTITY_NAME}")

            # 生成完整包名（基于模块名称和实体名称）
            if FORCE_SYSTEM:
                # 使用指定的模块名称生成包名
                package_name = f"org.jeecg.modules.{FORCE_SYSTEM}.{ENTITY_NAME}"
            else:
                # 默认包名（仅使用实体名称，兼容旧版本）
                package_name = f"org.jeecg.modules.{ENTITY_NAME}"

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
            print(f"   - package_name: 完整包名，格式为 org.jeecg.modules.{{module_name}}.{{entity_name}}")
            print(f"   - SQL文件中的模块名称就是entity_name的值，如 'invoice'")

        except Exception as e:
            print(f"❌ 模块管理异常: {e}")
            return
    else:
        print("\n5️⃣ 跳过模块管理（使用现有配置）")
        print(f"🔧 当前项目路径: {PROJECT_PATH}")
        print(f"📦 当前实体名称: {ENTITY_NAME}")

        # 生成完整包名（基于模块名称和实体名称）
        if FORCE_SYSTEM:
            # 使用指定的模块名称生成包名
            package_name = f"org.jeecg.modules.{FORCE_SYSTEM}.{ENTITY_NAME}"
        else:
            # 默认包名（仅使用实体名称，兼容旧版本）
            package_name = f"org.jeecg.modules.{ENTITY_NAME}"

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

        # 生成完整包名（基于模块名称和实体名称）
        if FORCE_SYSTEM:
            # 使用指定的模块名称生成包名
            package_name = f"org.jeecg.modules.{FORCE_SYSTEM}.{ENTITY_NAME}"
        else:
            # 默认包名（仅使用实体名称，兼容旧版本）
            package_name = f"org.jeecg.modules.{ENTITY_NAME}"

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

        print(f"\n🔧 其他配置:")
        print(f"   JSP模式                  = {JSP_MODE}")
        print(f"   表单类型                 = {JFORM_TYPE}")
        print(f"   包样式                   = {PACKAGE_STYLE}")
        print(f"   Vue样式                  = {VUE_STYLE}")
        print(f"   代码类型                 = {CODE_TYPES}")
        print(f"   强制系统                 = {FORCE_SYSTEM or 'None'}")

        # 准备代码生成参数
        codegen_data = {
            "projectPath": PROJECT_PATH,
            "jspMode": JSP_MODE,
            "ftlDescription": form_data['head']['tableTxt'],
            "jformType": JFORM_TYPE,
            "tableName_tmp": table_name,
            "entityName": entity_name,
            "entityPackage": ENTITY_NAME,
            "bussiPackage": package_name,  # 添加正确的业务包名
            "packageStyle": PACKAGE_STYLE,
            "vueStyle": VUE_STYLE,
            "codeTypes": CODE_TYPES,
            "code": form_id,
            "tableName": table_name
        }

        # 打印完整的代码生成请求参数
        print(f"\n📋 代码生成请求参数:")
        for key, value in codegen_data.items():
            print(f"   {key:<20} = {value}")

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

    # 7. 完成
    print(f"\n{'='*50}")
    print("🎉 完整工作流完成!")
    print(f"📋 表名: {table_name}")
    print(f"🆔 表单ID: {form_id}")
    print(f"🏗️ 实体名: {entity_name}")
    print(f"📦 业务包名: {package_name}")
    print(f"📦 实体名称: {ENTITY_NAME}")
    print(f"🏗️ 项目路径: {PROJECT_PATH}")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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

def calculate_similarity(str1, str2):
    """计算两个字符串的相似度（简单的编辑距离算法）"""
    if not str1 or not str2:
        return 0.0
    
    len1, len2 = len(str1), len(str2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j
    
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
    
    max_len = max(len1, len2)
    similarity = (max_len - dp[len1][len2]) / max_len
    return similarity

def match_dict_field(field_description, dict_data):
    """智能匹配数据字典字段（增强版）"""
    # 扩展的数据字典语义映射
    semantic_mapping = {
        "性别": ["sex", "gender"],
        "状态": ["status", "state", "condition"], 
        "类型": ["type", "category", "kind", "class"],
        "等级": ["level", "grade", "rank", "tier"],
        "优先级": ["priority", "importance"],
        "是否": ["yes_no", "flag", "enable", "switch"],
        "审核": ["audit_result", "approve_status", "review"],
        "级别": ["level", "grade", "rank"],
        "分类": ["category", "type", "classification"],
        "状况": ["status", "state", "situation"],
        "启用": ["enable", "flag", "yes_no", "active"],
        "有效": ["valid", "flag", "yes_no", "effective"],
        "部门": ["department", "dept", "division"],
        "职位": ["position", "job", "role", "post"],
        "用户": ["user", "member", "person"]
    }
    
    # 查找匹配的语义词
    matched_dict_codes = []
    semantic_scores = {}
    
    for semantic_word, dict_codes in semantic_mapping.items():
        if semantic_word in field_description:
            matched_dict_codes.extend(dict_codes)
            for code in dict_codes:
                semantic_scores[code] = 10  # 精确语义匹配
    
    # 在实际数据字典中查找匹配项
    dict_matches = []
    for dict_item in dict_data:
        dict_code = dict_item.get('dictCode', '').lower()
        dict_name = dict_item.get('dictName', '').lower()
        
        best_score = 0
        match_type = ""
        
        # 1. 精确匹配检查
        if dict_code in matched_dict_codes:
            best_score = semantic_scores.get(dict_code, 10)
            match_type = '语义精确匹配'
        
        # 2. 部分匹配检查
        elif any(code in dict_code for code in matched_dict_codes):
            best_score = 8
            match_type = '语义部分匹配'
        
        # 3. 名称匹配检查
        elif any(semantic_word in dict_name for semantic_word in semantic_mapping.keys() if semantic_word in field_description):
            best_score = 6
            match_type = '名称语义匹配'
        
        # 4. 模糊匹配检查（新增）
        else:
            # 检查字段描述与字典名称的相似度
            similarity = calculate_similarity(field_description, dict_name)
            if similarity > 0.6:  # 相似度阈值
                best_score = int(similarity * 5)  # 转换为分数（最高5分）
                match_type = f'模糊匹配({similarity:.2f})'
            
            # 检查字段描述与字典编码的相似度
            code_similarity = calculate_similarity(field_description.lower(), dict_code)
            if code_similarity > 0.5:
                code_score = int(code_similarity * 4)  # 最高4分
                if code_score > best_score:
                    best_score = code_score
                    match_type = f'编码模糊匹配({code_similarity:.2f})'
        
        # 添加到结果中（只添加有意义的匹配）
        if best_score > 0:
            dict_matches.append({
                'dict_code': dict_item.get('dictCode'),
                'dict_name': dict_item.get('dictName'),
                'score': best_score,
                'match_type': match_type
            })
    
    # 按得分排序，返回最佳匹配
    dict_matches.sort(key=lambda x: x['score'], reverse=True)
    return dict_matches[:5] if dict_matches else []  # 返回前5个最佳匹配

def auto_ensure_dict_data():
    """自动确保数据字典数据存在且最新"""
    print("\n🔍 检查数据字典状态...")
    
    is_valid, status_msg = check_dict_file_status()
    print(f"   {status_msg}")
    
    if not is_valid:
        print("📚 自动获取最新数据字典...")
        if fetch_system_dict():
            print("✅ 数据字典更新完成")
            return True
        else:
            print("❌ 数据字典获取失败")
            return False
    else:
        print("✅ 数据字典文件有效，跳过更新")
        return True

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

def create_field_with_smart_dict(field_type, field_name, field_description, order_num, dict_data=None, **kwargs):
    """智能创建字段，自动匹配数据字典"""
    
    # 如果没有提供数据字典数据，尝试加载
    if dict_data is None:
        dict_data = load_dict_data()
    
    # 智能匹配数据字典
    dict_matches = match_dict_field(field_description, dict_data)
    
    # 如果有匹配的数据字典且字段类型适合使用数据字典
    if dict_matches and field_type in ['select_field', 'text_field']:
        best_match = dict_matches[0]  # 使用最佳匹配
        dict_code = best_match['dict_code']
        
        print(f"🎯 智能匹配数据字典: {field_description} → {dict_code} ({best_match['dict_name']})")
        print(f"   匹配类型: {best_match['match_type']}, 得分: {best_match['score']}")
        
        # 根据原字段类型选择合适的数据字典字段类型
        if field_type == 'select_field':
            dict_field_type = 'dict_select_field'
        else:
            dict_field_type = 'dict_select_field'  # 默认使用下拉选择
        
        # 创建数据字典字段
        return create_field_from_template(
            dict_field_type, 
            field_name, 
            field_description, 
            order_num,
            dict_code=dict_code,
            **kwargs
        )
    
    # 没有匹配的数据字典，使用原始字段类型
    return create_field_from_template(field_type, field_name, field_description, order_num, **kwargs)

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

    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()

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
    global SKIP_MODULE_MANAGEMENT, FORCE_SYSTEM
    SKIP_MODULE_MANAGEMENT = args.skip_module_management
    FORCE_SYSTEM = args.module_name  # 使用新的参数名

    # 预处理工作流变量（确保在显示配置前就有实际值）
    global PROJECT_PATH, ENTITY_NAME

    # 1. 处理模块名称和项目路径
    if FORCE_SYSTEM:
        project_prefix = CONFIG.get('project', {}).get('path_prefix', '/Users/admin/Work/Github/JeecgBoot')
        PROJECT_PATH = f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{FORCE_SYSTEM}"
    else:
        PROJECT_PATH = CONFIG['codegen']['project_path']  # 保持原配置值

    # 2. 处理实体名称
    if args.form_config:
        try:
            with open(args.form_config, 'r', encoding='utf-8') as f:
                form_data = json.load(f)
                table_name = form_data.get('head', {}).get('tableName', '')
                ENTITY_NAME = extract_business_entity_from_table_name(table_name)
        except Exception as e:
            print(f"⚠️ 无法读取表单配置文件: {e}")
            ENTITY_NAME = CONFIG['codegen']['entity_name']  # 保持原配置值
    else:
        ENTITY_NAME = CONFIG['codegen']['entity_name']  # 保持原配置值

    # 3. 更新全局变量（使用预处理后的值）
    update_global_vars()

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
        print(f"🏗️ 项目路径: {CONFIG['codegen']['project_path']}")
        print(f"📦 实体名称: {CONFIG['codegen']['entity_name']}")
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

def update_global_vars():
    """更新全局变量"""
    global BASE_URL, LOGIN_USERNAME, LOGIN_PASSWORD
    global REQUEST_TIMEOUT_LOGIN, REQUEST_TIMEOUT_CREATE, REQUEST_TIMEOUT_LIST
    global REQUEST_TIMEOUT_SYNC, REQUEST_TIMEOUT_CODEGEN
    global FORM_DATA_FILE, WAIT_TIME_AFTER_CREATE
    global JSP_MODE, JFORM_TYPE
    global PACKAGE_STYLE, VUE_STYLE, CODE_TYPES
    global PAGE_SIZE, PAGE_NO, DISPLAY_TOKEN_LENGTH, MAX_DISPLAY_RECORDS

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

    # PROJECT_PATH 和 ENTITY_NAME 在主函数中已经预处理，这里不再覆盖
    JSP_MODE = CONFIG['codegen']['jsp_mode']
    JFORM_TYPE = CONFIG['codegen']['jform_type']
    PACKAGE_STYLE = CONFIG['codegen']['package_style']
    VUE_STYLE = CONFIG['codegen']['vue_style']
    CODE_TYPES = CONFIG['codegen']['code_types']

    PAGE_SIZE = CONFIG['query']['page_size']
    PAGE_NO = CONFIG['query']['page_no']

    DISPLAY_TOKEN_LENGTH = CONFIG['display']['token_length']
    MAX_DISPLAY_RECORDS = CONFIG['display']['max_records']

if __name__ == "__main__":
    main()
