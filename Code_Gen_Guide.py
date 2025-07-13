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
            "project_path": "D:\\02_Dev\\Workspace\\GitHub\\JeecgBoot\\jeecg-boot\\jeecg-module-system",
            "entity_package": "empinfo",
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

def check_module_exists(system_name):
    """检查系统级模块是否存在"""
    module_path = Path(f"jeecg-boot/jeecg-module-{system_name}")
    exists = module_path.exists() and module_path.is_dir()

    print(f"🔍 检查模块: jeecg-module-{system_name}")
    print(f"   路径: {module_path.absolute()}")
    print(f"   存在: {'✅ 是' if exists else '❌ 否'}")

    return exists

def create_maven_module(system_name):
    """使用Maven archetype创建新模块"""
    print(f"🏗️ 创建Maven模块: jeecg-module-{system_name}")

    # 构建Maven命令
    maven_cmd = [
        'mvn', 'archetype:generate',
        '-DgroupId=org.jeecgframework.boot',
        f'-DartifactId=jeecg-module-{system_name}',
        '-Dversion=3.8.1',
        '-DarchetypeGroupId=org.jeecgframework.archetype',
        '-DarchetypeArtifactId=jeecg-boot-gen',
        '-DarchetypeVersion=2.0',
        '-DinteractiveMode=false'  # 非交互模式
    ]

    print(f"   操作系统: {platform.system()}")
    print(f"   执行目录: {Path('jeecg-boot').absolute()}")
    print(f"   Maven命令: {' '.join(maven_cmd)}")

    try:
        # 确保在jeecg-boot目录下执行
        jeecg_boot_path = Path('jeecg-boot')
        if not jeecg_boot_path.exists():
            print(f"❌ jeecg-boot目录不存在: {jeecg_boot_path.absolute()}")
            return False

        # 执行Maven命令
        result = subprocess.run(
            maven_cmd,
            cwd=jeecg_boot_path,
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

def update_main_pom(system_name):
    """更新主项目pom.xml添加新模块"""
    pom_path = Path('jeecg-boot/pom.xml')

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
        module_name = f"jeecg-module-{system_name}"
        existing_modules = [elem.text for elem in modules_element.findall('.//maven:module', namespace) or modules_element.findall('.//module')]

        if module_name in existing_modules:
            print(f"✅ 模块已存在于pom.xml中: {module_name}")
            return True

        # 添加新模块
        new_module = ET.SubElement(modules_element, 'module')
        new_module.text = module_name

        # 保存文件
        tree.write(pom_path, encoding='utf-8', xml_declaration=True)
        print(f"✅ 已添加模块到主项目pom.xml: {module_name}")
        return True

    except Exception as e:
        print(f"❌ 更新主项目pom.xml失败: {e}")
        return False

def update_system_start_pom(system_name):
    """更新启动项目pom.xml添加新模块依赖"""
    pom_path = Path('jeecg-boot/jeecg-module-system/jeecg-system-start/pom.xml')

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
        artifact_id = f"jeecg-module-{system_name}"
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

def ensure_module_exists(system_name):
    """确保模块存在，如果不存在则创建并配置"""
    print(f"\n🔧 模块管理: {system_name}")
    print("=" * 40)

    # 1. 检查模块是否存在
    if check_module_exists(system_name):
        print(f"✅ 模块已存在，跳过创建步骤")
        return True

    # 2. 创建模块
    print(f"📦 模块不存在，开始创建...")
    if not create_maven_module(system_name):
        return False

    # 3. 更新主项目pom.xml
    if not update_main_pom(system_name):
        return False

    # 4. 更新启动项目pom.xml
    if not update_system_start_pom(system_name):
        return False

    # 5. 验证模块创建结果
    if check_module_exists(system_name):
        print(f"🎉 模块创建和配置完成: jeecg-module-{system_name}")
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
ENTITY_PACKAGE = CONFIG['codegen']['entity_package']
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
    if not CONFIG['codegen']['entity_package']:
        errors.append("实体包名不能为空")

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

def jeecg_complete_workflow():
    """JeecgBoot完整表单工作流"""

    print("\n🚀 开始执行 JeecgBoot 表单工作流")
    print("=" * 50)

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

    # 2. 准备表单数据
    print("\n2️⃣ 准备表单数据...")
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

    except Exception as e:
        print(f"❌ 准备数据失败: {e}")
        return

    # 2.5. 智能识别业务系统并确保模块存在
    if not SKIP_MODULE_MANAGEMENT:
        print("\n2️⃣.5️⃣ 模块管理...")
        try:
            # 优先使用命令行指定的系统名称，否则智能识别
            if FORCE_SYSTEM:
                system_name = FORCE_SYSTEM
                print(f"🎯 使用指定业务系统: {system_name}")
            else:
                system_name = detect_business_system(table_name, table_txt)
                print(f"🧠 智能识别业务系统: {system_name}")

            # 确保模块存在
            if not ensure_module_exists(system_name):
                print(f"❌ 模块管理失败，终止工作流")
                return

            # 更新项目路径配置
            global PROJECT_PATH, ENTITY_PACKAGE
            PROJECT_PATH = str(Path(f"D:/02_Dev/Workspace/GitHub/JeecgBoot/jeecg-boot/jeecg-module-{system_name}").resolve())

            # 从表名提取实体包名（去掉us_前缀）
            if table_name.startswith('us_'):
                ENTITY_PACKAGE = table_name[3:]  # 去掉us_前缀
            else:
                ENTITY_PACKAGE = table_name

            print(f"🔧 更新项目路径: {PROJECT_PATH}")
            print(f"📦 更新实体包名: {ENTITY_PACKAGE}")

        except Exception as e:
            print(f"❌ 模块管理异常: {e}")
            return
    else:
        print("\n2️⃣.5️⃣ 跳过模块管理（使用现有配置）")
        print(f"🔧 当前项目路径: {PROJECT_PATH}")
        print(f"📦 当前实体包名: {ENTITY_PACKAGE}")
    
    # 3. 创建表单
    print("\n3️⃣ 正在创建表单...")
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
    
    # 5. 同步到数据库
    print("\n5️⃣ 正在同步到数据库...")

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

    # 6. 代码生成
    print("\n6️⃣ 正在生成代码...")

    try:
        # 生成实体名（将表名转换为驼峰命名）
        entity_name = ''.join(word.capitalize() for word in table_name.split('_'))

        # 准备代码生成参数
        codegen_data = {
            "projectPath": PROJECT_PATH,
            "jspMode": JSP_MODE,
            "ftlDescription": form_data['head']['tableTxt'],
            "jformType": JFORM_TYPE,
            "tableName_tmp": table_name,
            "entityName": entity_name,
            "entityPackage": ENTITY_PACKAGE,
            "packageStyle": PACKAGE_STYLE,
            "vueStyle": VUE_STYLE,
            "codeTypes": CODE_TYPES,
            "code": form_id,
            "tableName": table_name
        }

        codegen_url = f"{BASE_URL}/online/cgform/api/codeGenerate"
        print(f"   代码生成URL: {codegen_url}")
        print(f"   表单ID: {form_id}")
        print(f"   实体名: {entity_name}")
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

    # 7. 完成
    print(f"\n{'='*50}")
    print("🎉 完整工作流完成!")
    print(f"📋 表名: {table_name}")
    print(f"🆔 表单ID: {form_id}")
    print(f"🏗️ 实体名: {entity_name}")
    print(f"📦 包名: {ENTITY_PACKAGE}")
    print(f"🏗️ 项目路径: {PROJECT_PATH}")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    # 显示结果摘要（不保存文件）
    print("\n📊 生成结果摘要:")
    print(f"   表名: {table_name}")
    print(f"   表单ID: {form_id}")
    print(f"   实体名: {entity_name}")
    print(f"   实体包名: {ENTITY_PACKAGE}")
    print(f"   项目路径: {PROJECT_PATH}")
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
        '{{DEFAULT_VALUE}}': kwargs.get('default_value', '')
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

    parser.add_argument('--system-name', '-s',
                       help='业务系统名称（如：hrms, crm, scm, oa, finance）')

    parser.add_argument('--form-config', '-f',
                       help='表单配置文件路径')

    parser.add_argument('--table-name', '-n',
                       help='表名（覆盖配置文件中的设置）')

    parser.add_argument('--table-description', '-d',
                       help='表描述（覆盖配置文件中的设置）')

    parser.add_argument('--project-path', '-p',
                       help='项目路径（覆盖配置文件中的设置）')

    parser.add_argument('--entity-package', '-e',
                       help='实体包名（覆盖配置文件中的设置）')

    parser.add_argument('--test', action='store_true',
                       help='运行系统诊断测试')

    parser.add_argument('--validate', action='store_true',
                       help='仅验证配置和数据，不执行工作流')

    parser.add_argument('--skip-module-management', action='store_true',
                       help='跳过模块管理（不检查和创建模块）')

    parser.add_argument('--dry-run', action='store_true',
                       help='试运行模式（只显示将要执行的操作，不实际执行）')

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出模式')

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
    if args.entity_package:
        CONFIG['codegen']['entity_package'] = args.entity_package

    # 设置全局标志
    global SKIP_MODULE_MANAGEMENT, FORCE_SYSTEM
    SKIP_MODULE_MANAGEMENT = args.skip_module_management
    FORCE_SYSTEM = args.system_name  # 使用新的参数名

    # 更新全局变量
    update_global_vars()

    # 显示工具信息
    print("JeecgBoot 表单工作流自动化工具 v2.0")
    print("=" * 50)

    if args.system_name:
        print(f"🎯 指定业务系统: {args.system_name}")
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

    if args.dry_run:
        print("🔍 试运行模式 - 将显示操作但不执行")
        print(f"📋 配置文件: {args.config}")
        print(f"🎯 业务系统: {args.system_name or '自动识别'}")
        print(f"📋 表单配置: {args.form_config or '使用默认'}")
        print(f"🏗️ 项目路径: {CONFIG['codegen']['project_path']}")
        print(f"📦 实体包名: {CONFIG['codegen']['entity_package']}")
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
    global PROJECT_PATH, ENTITY_PACKAGE, JSP_MODE, JFORM_TYPE
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

    PROJECT_PATH = CONFIG['codegen']['project_path']
    ENTITY_PACKAGE = CONFIG['codegen']['entity_package']
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
