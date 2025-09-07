#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot工具集合
整合了表单查询和删除功能
"""

import requests
import json
import sys
import os
import configparser
import urllib.parse
import time
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional


class JeecgBootClient:
    """JeecgBoot基础客户端"""
    
    def __init__(self, config_file: str = "Code_Gen_Config.properties"):
        self.config_file = config_file
        self.config = self._load_config()
        self.session = requests.Session()
        self.token = None
        
    def _load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()
        config.read(self.config_file, encoding='utf-8')
        return config
        
    def get_config_value(self, section: str, key: str, fallback: str = None) -> str:
        """获取配置值，优先从环境变量读取"""
        try:
            # 优先从环境变量读取
            if section == 'server' and key == 'base_url':
                env_val = os.getenv('JEECG_BASE_URL')
                if env_val:
                    return env_val
            elif section == 'server' and key == 'username':
                env_val = os.getenv('JEECG_USERNAME')
                if env_val:
                    return env_val
            elif section == 'server' and key == 'password':
                env_val = os.getenv('JEECG_PASSWORD')
                if env_val:
                    return env_val
                    
            # 从配置文件读取
            return self.config.get(section, key, fallback=fallback)
        except:
            return fallback
            
    def login(self) -> bool:
        """用户登录认证"""
        base_url = self.get_config_value('server', 'base_url', 'http://localhost:8080/jeecg-boot')
        username = self.get_config_value('server', 'username', 'admin')
        password = self.get_config_value('server', 'password', '123456')
        
        login_url = f"{base_url}/sys/mLogin"
        login_data = {"username": username, "password": password}
        
        try:
            response = self.session.post(login_url, json=login_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.token = result.get('result', {}).get('token')
                    print(f"✅ 登录成功，Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"❌ 登录失败: {result.get('message')}")
            else:
                print(f"❌ 登录请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 登录异常: {e}")
        
        return False


class FormQuery(JeecgBootClient):
    """表单查询器"""
    
    def query_all_forms(self, page_size: int = 100) -> List[Dict]:
        """查询所有表单"""
        if not self.token:
            print("❌ 未登录，无法查询表单")
            return []
            
        base_url = self.get_config_value('server', 'base_url', 'http://localhost:8080/jeecg-boot')
        url = f"{base_url}/online/cgform/head/list"
        
        headers = {'X-Access-Token': self.token}
        params = {'pageNo': 1, 'pageSize': page_size}
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    records = result.get('result', {}).get('records', [])
                    print(f"✅ 查询成功，共获取 {len(records)} 个表单")
                    return records
                else:
                    print(f"❌ 查询失败: {result.get('message')}")
            else:
                print(f"❌ 查询请求失败: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
        except Exception as e:
            print(f"❌ 查询异常: {e}")
        
        return []
    
    def filter_education_student_forms(self, all_forms: List[Dict]) -> List[Dict]:
        """筛选education.student相关表单"""
        education_forms = []
        target_tables = [
            'education_student_studentinfo',
            'education_student_parentinfo', 
            'education_student_classmaterelation'
        ]
        
        for form in all_forms:
            table_name = form.get('tableName', '')
            if table_name in target_tables:
                education_forms.append(form)
                
        return education_forms
    
    def print_all_forms(self, forms: List[Dict]):
        """打印所有表单信息"""
        print(f"\n{'='*80}")
        print("📋 JeecgBoot后台所有表单:")
        print(f"{'='*80}")
        
        for i, form in enumerate(forms, 1):
            table_name = form.get('tableName', 'N/A')
            table_txt = form.get('tableTxt', 'N/A')
            table_type = form.get('tableType', 'N/A')
            form_id = form.get('id', 'N/A')
            create_time = form.get('createTime', 'N/A')
            
            print(f"{i}. {table_name} ({table_txt}) - tableType:{table_type} - ID:{form_id}")
    
    def print_form_analysis(self, forms: List[Dict]):
        """打印表单分析报告"""
        if not forms:
            print("\n❌ 未找到education.student相关表单")
            print("让我们检查所有表单，看看是否有其他相关表单...")
            return
            
        print(f"\n{'='*80}")
        print("📋 JeecgBoot后台表单查询结果")
        print(f"{'='*80}")
        print(f"找到 {len(forms)} 个相关表单:")
        
        for i, form in enumerate(forms, 1):
            table_name = form.get('tableName', 'N/A')
            table_txt = form.get('tableTxt', 'N/A')
            table_type = form.get('tableType', 'N/A')
            relation_type = form.get('relationType', 'N/A')
            sub_table_str = form.get('subTableStr', 'N/A')
            form_id = form.get('id', 'N/A')
            create_time = form.get('createTime', 'N/A')
            
            print(f"\n🔍 表单 {i}:")
            print(f"   📊 表单ID: {form_id}")
            print(f"   📝 表名: {table_name}")
            print(f"   📃 描述: {table_txt}")
            print(f"   🏷️  tableType: {table_type}")
            print(f"   🔗 relationType: {relation_type}")  
            print(f"   📑 子表字符串: {sub_table_str}")
            print(f"   📅 创建时间: {create_time}")
            
            # 分析tableType
            type_analysis = ""
            if table_type == 1:
                type_analysis = "(独立表)"
            elif table_type == 2:
                type_analysis = "(主表)"
            elif table_type == 3:
                type_analysis = "(子表)"
            else:
                type_analysis = "(未知类型)"
            
            print(f"   ✨ 类型分析: {table_type} {type_analysis}")
        
        # 总体分析
        print(f"\n{'='*80}")
        print("🔍 总体分析:")
        
        table_type_count = {}
        for form in forms:
            table_type = form.get('tableType', 'N/A')
            table_type_count[table_type] = table_type_count.get(table_type, 0) + 1
            
        for table_type, count in table_type_count.items():
            type_desc = ""
            if table_type == 1:
                type_desc = "独立表"
            elif table_type == 2:
                type_desc = "主表"
            elif table_type == 3:
                type_desc = "子表"
            else:
                type_desc = "未知"
            print(f"   {type_desc} (tableType={table_type}): {count} 个")
            
        # 检查主子表关系
        main_tables = [f for f in forms if f.get('tableType') == 2]
        sub_tables = [f for f in forms if f.get('tableType') == 3]
        
        print(f"\n🔗 主子表关系检查:")
        if main_tables:
            for main in main_tables:
                main_name = main.get('tableName')
                sub_table_str = main.get('subTableStr', '')
                print(f"   主表: {main_name}")
                if sub_table_str:
                    print(f"   ├── 配置的子表: {sub_table_str}")
                else:
                    print(f"   ├── ❌ 未配置子表关系")
                    
        if sub_tables:
            print(f"   实际子表:")
            for sub in sub_tables:
                sub_name = sub.get('tableName')
                print(f"   ├── {sub_name}")


class PermissionQuery(JeecgBootClient):
    """菜单权限查询器"""
    
    def query_permissions(self) -> List[Dict]:
        """查询菜单权限列表"""
        if not self.token:
            print("❌ 未登录，无法查询菜单权限")
            return []
            
        base_url = self.get_config_value('server', 'base_url', 'http://localhost:8080/jeecg-boot')
        url = f"{base_url}/sys/permission/list"
        
        headers = {'X-Access-Token': self.token}
        params = {
            'column': 'createTime',
            'order': 'desc',
            '_t': str(int(time.time() * 1000))  # 时间戳
        }
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    records = result.get('result', [])
                    print(f"✅ 查询成功，共获取 {len(records)} 个菜单权限")
                    return records
                else:
                    print(f"❌ 查询失败: {result.get('message')}")
            else:
                print(f"❌ 查询请求失败: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
        except Exception as e:
            print(f"❌ 查询异常: {e}")
        
        return []
    
    def print_permissions(self, permissions: List[Dict]):
        """打印菜单权限信息"""
        if not permissions:
            print("\n❌ 未找到菜单权限")
            return
            
        print(f"\n{'='*100}")
        print("🔐 JeecgBoot菜单权限列表")
        print(f"{'='*100}")
        print(f"总计 {len(permissions)} 个权限项")
        
        # 统计权限类型
        menu_type_count = {}
        for perm in permissions:
            menu_type = perm.get('menuType', 0)
            menu_type_count[menu_type] = menu_type_count.get(menu_type, 0) + 1
        
        print(f"\n📊 权限类型统计:")
        type_names = {0: "菜单", 1: "按钮", 2: "权限"}
        for menu_type, count in menu_type_count.items():
            type_name = type_names.get(menu_type, f"未知({menu_type})")
            print(f"   {type_name}: {count} 个")
        
        print(f"\n{'='*100}")
        print("详细权限信息:")
        print(f"{'='*100}")
        
        for i, perm in enumerate(permissions, 1):
            perm_id = perm.get('id', 'N/A')
            name = perm.get('name', 'N/A')
            perms = perm.get('perms', 'N/A')
            perms_type = perm.get('permsType', 'N/A')
            menu_type = perm.get('menuType', 'N/A')
            parent_id = perm.get('parentId', 'N/A')
            url = perm.get('url', 'N/A')
            component = perm.get('component', 'N/A')
            sort_no = perm.get('sortNo', 'N/A')
            is_leaf = perm.get('isLeaf', 'N/A')
            is_route = perm.get('isRoute', 'N/A')
            keep_alive = perm.get('keepAlive', 'N/A')
            hidden = perm.get('hidden', 'N/A')
            create_time = perm.get('createTime', 'N/A')
            
            # 权限类型解析
            menu_type_name = type_names.get(menu_type, f"未知({menu_type})")
            
            print(f"\n🔍 权限 {i}:")
            print(f"   🆔 ID: {perm_id}")
            print(f"   📝 名称: {name}")
            print(f"   🔑 权限标识: {perms}")
            print(f"   🏷️  权限类型: {perms_type}")
            print(f"   📂 菜单类型: {menu_type} ({menu_type_name})")
            print(f"   👨‍👩‍👧‍👦 父级ID: {parent_id}")
            print(f"   🔗 路径: {url}")
            print(f"   🧩 组件: {component}")
            print(f"   🔢 排序号: {sort_no}")
            print(f"   🍃 是否叶子: {is_leaf}")
            print(f"   🛤️  是否路由: {is_route}")
            print(f"   💾 保持活跃: {keep_alive}")
            print(f"   👻 是否隐藏: {hidden}")
            print(f"   📅 创建时间: {create_time}")
    
    def print_permission_tree(self, permissions: List[Dict]):
        """打印权限树形结构"""
        if not permissions:
            return
            
        print(f"\n{'='*80}")
        print("🌳 权限树形结构")
        print(f"{'='*80}")
        
        # 构建树形结构
        perm_dict = {perm['id']: perm for perm in permissions}
        root_perms = [perm for perm in permissions if not perm.get('parentId') or perm.get('parentId') == '0']
        
        def print_tree_node(perm, level=0):
            indent = "  " * level
            name = perm.get('name', 'N/A')
            perms = perm.get('perms', '')
            menu_type = perm.get('menuType', 0)
            type_names = {0: "📁", 1: "🔘", 2: "🔐"}
            type_icon = type_names.get(menu_type, "❓")
            
            print(f"{indent}{type_icon} {name} ({perms})")
            
            # 查找子节点
            children = [p for p in permissions if p.get('parentId') == perm['id']]
            children.sort(key=lambda x: x.get('sortNo', 0))
            for child in children:
                print_tree_node(child, level + 1)
        
        # 打印根节点
        root_perms.sort(key=lambda x: x.get('sortNo', 0))
        for root in root_perms:
            print_tree_node(root)


class DatabaseConnector:
    """JeecgBoot数据库连接器"""
    
    def __init__(self):
        self.connection = None
        
    def test_connection(self) -> Dict:
        """测试数据库连接"""
        result = {
            'success': False,
            'connection_info': {},
            'error_message': '',
            'server_info': '',
            'database_name': ''
        }
        
        try:
            # 从环境变量读取数据库连接信息 - 与Code_Gen_Execute.py保持一致
            db_type = os.getenv('JEECG_DATABASE_TYPE', 'mysql')
            db_url = os.getenv('JEECG_DATABASE_URL', 'localhost:3306/jeecg-boot')
            db_username = os.getenv('JEECG_DATABASE_USERNAME', 'root')
            db_password = os.getenv('JEECG_DATABASE_PASSWORD', '')
            
            print(f"🔧 数据库连接配置:")
            print(f"   类型: {db_type}")
            print(f"   地址: {db_url}")
            print(f"   用户: {db_username}")
            print(f"   密码: {'已配置' if db_password else '未配置'}")
            
            result['connection_info'] = {
                'type': db_type,
                'url': db_url,
                'username': db_username,
                'password_configured': bool(db_password)
            }
            
            if not all([db_url, db_username]):
                result['error_message'] = "数据库连接信息不完整，请检查环境变量: JEECG_DATABASE_URL, JEECG_DATABASE_USERNAME, JEECG_DATABASE_PASSWORD"
                return result
            
            # 解析JDBC数据库URL - 使用正确的正则表达式解析
            import re
            match = re.search(r'jdbc:mysql://([^:/]+):(\d+)/([^?]+)', db_url)
            if not match:
                result['error_message'] = f"JDBC URL格式错误: {db_url}，应为 jdbc:mysql://host:port/database 格式"
                return result
            host, port, database = match.groups()
            port = int(port)
            
            print(f"🔗 尝试连接数据库...")
            print(f"   主机: {host}")
            print(f"   端口: {port}")  
            print(f"   数据库: {database}")
            
            # 建立MySQL连接 - 与Code_Gen_Execute.py保持一致
            self.connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=db_username,
                password=db_password,
                autocommit=True,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                connect_timeout=10
            )
            
            if self.connection.is_connected():
                # 获取服务器信息
                cursor = self.connection.cursor()
                cursor.execute("SELECT VERSION()")
                server_version = cursor.fetchone()[0]
                cursor.execute("SELECT DATABASE()")
                current_database = cursor.fetchone()[0]
                cursor.close()
                
                result['success'] = True
                result['server_info'] = server_version
                result['database_name'] = current_database
                
                print(f"✅ 数据库连接成功!")
                print(f"   服务器版本: {server_version}")
                print(f"   当前数据库: {current_database}")
                return result
            else:
                result['error_message'] = "数据库连接失败"
                return result
                
        except Error as e:
            result['error_message'] = f"MySQL连接错误: {e}"
            print(f"❌ MySQL连接错误: {e}")
            return result
        except Exception as e:
            result['error_message'] = f"数据库连接配置异常: {e}"
            print(f"❌ 数据库连接配置异常: {e}")
            return result
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 数据库连接已关闭")
            
    def execute_query(self, sql: str) -> Dict:
        """执行查询SQL"""
        result = {
            'success': False,
            'data': [],
            'error_message': '',
            'affected_rows': 0
        }
        
        if not self.connection or not self.connection.is_connected():
            result['error_message'] = "数据库连接未建立"
            return result
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(sql)
            
            if sql.strip().upper().startswith('SELECT'):
                result['data'] = cursor.fetchall()
            else:
                result['affected_rows'] = cursor.rowcount
                
            result['success'] = True
            cursor.close()
            return result
            
        except Error as e:
            result['error_message'] = f"SQL执行错误: {e}"
            return result


class FormDeleter(JeecgBootClient):
    """表单删除器"""
    
    def query_target_forms(self) -> list:
        """查询需要删除的目标表单"""
        if not self.token:
            print("❌ 未登录，无法查询表单")
            return []
            
        base_url = self.get_config_value('server', 'base_url', 'http://localhost:8080/jeecg-boot')
        url = f"{base_url}/online/cgform/head/list"
        
        headers = {'X-Access-Token': self.token}
        params = {'pageNo': 1, 'pageSize': 100}
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    records = result.get('result', {}).get('records', [])
                    
                    # 筛选需要删除的表单
                    target_forms = []
                    target_patterns = [
                        'education_student_studentinfo',
                        'education_student_parentinfo',
                        'education_student_classmaterelation'
                    ]
                    
                    for record in records:
                        table_name = record.get('tableName', '')
                        if table_name in target_patterns:
                            target_forms.append(record)
                    
                    return target_forms
                else:
                    print(f"❌ 查询失败: {result.get('message')}")
            else:
                print(f"❌ 查询请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 查询异常: {e}")
        
        return []
    
    def delete_forms_batch(self, forms: list) -> bool:
        """批量删除表单"""
        if not forms:
            print("✅ 没有需要删除的表单")
            return True
        
        form_ids = [form.get('id') for form in forms]
        
        base_url = self.get_config_value('server', 'base_url', 'http://localhost:8080/jeecg-boot')
        url = f"{base_url}/online/cgform/head/deleteBatch"
        
        try:
            ids_str = ','.join(form_ids)
            ids_encoded = urllib.parse.quote(ids_str, safe='')
            url_with_params = f"{url}?ids={ids_encoded}&flag=table"
            
            headers = {'X-Access-Token': self.token}
            response = self.session.delete(url_with_params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 成功删除 {len(forms)} 个表单")
                    return True
                else:
                    print(f"❌ 表单删除失败: {result.get('message')}")
            else:
                print(f"❌ 表单删除请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 表单删除异常: {e}")
        
        return False


def query_forms():
    """查询表单的主函数"""
    print("🚀 开始查询JeecgBoot表单...")
    
    query = FormQuery()
    
    # 1. 登录
    if not query.login():
        print("❌ 登录失败，无法继续查询")
        sys.exit(1)
    
    # 2. 查询所有表单
    all_forms = query.query_all_forms(page_size=100)
    if not all_forms:
        print("❌ 查询表单失败")
        sys.exit(1)
    
    # 3. 打印所有表单信息
    query.print_all_forms(all_forms)
    
    # 4. 筛选education.student相关表单
    education_forms = query.filter_education_student_forms(all_forms)
    
    # 5. 打印分析报告
    query.print_form_analysis(education_forms)
    
    print(f"\n{'='*80}")
    print("✅ 查询完成")


def query_permissions():
    """查询菜单权限的主函数"""
    print("🔐 开始查询JeecgBoot菜单权限...")
    
    query = PermissionQuery()
    
    # 1. 登录
    if not query.login():
        print("❌ 登录失败，无法继续查询")
        sys.exit(1)
    
    # 2. 查询所有权限
    permissions = query.query_permissions()
    if not permissions:
        print("❌ 查询权限失败")
        sys.exit(1)
    
    # 3. 打印权限信息
    query.print_permissions(permissions)
    
    # 4. 打印树形结构
    query.print_permission_tree(permissions)
    
    print(f"\n{'='*80}")
    print("✅ 权限查询完成")


def test_database_connection():
    """测试数据库连接的主函数"""
    print("🔗 开始测试JeecgBoot数据库连接...")
    
    db_connector = DatabaseConnector()
    
    try:
        # 测试连接
        result = db_connector.test_connection()
        
        if result['success']:
            print(f"\n{'='*80}")
            print("✅ 数据库连接测试成功!")
            print(f"{'='*80}")
            print(f"📊 连接信息:")
            print(f"   服务器版本: {result['server_info']}")
            print(f"   数据库名称: {result['database_name']}")
            print(f"   连接配置: {result['connection_info']}")
            
            # 执行一个简单的测试查询
            print(f"\n🧪 执行测试查询...")
            query_result = db_connector.execute_query("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = DATABASE()")
            if query_result['success']:
                table_count = query_result['data'][0]['table_count']
                print(f"✅ 测试查询成功，当前数据库共有 {table_count} 个表")
            else:
                print(f"❌ 测试查询失败: {query_result['error_message']}")
                
        else:
            print(f"\n{'='*80}")
            print("❌ 数据库连接测试失败!")
            print(f"{'='*80}")
            print(f"错误信息: {result['error_message']}")
            if result['connection_info']:
                print(f"配置信息: {result['connection_info']}")
            
    except Exception as e:
        print(f"❌ 数据库连接测试异常: {e}")
    finally:
        db_connector.close_connection()
    
    print("🔚 数据库连接测试完成")


def delete_forms():
    """删除表单的主函数"""
    print("🗑️ 开始删除错误的JeecgBoot表单...")
    
    deleter = FormDeleter()
    
    # 1. 登录
    if not deleter.login():
        print("❌ 登录失败，无法继续")
        sys.exit(1)
    
    # 2. 查询目标表单
    target_forms = deleter.query_target_forms()
    
    if target_forms:
        print(f"\n发现 {len(target_forms)} 个需要删除的表单:")
        for form in target_forms:
            table_name = form.get('tableName', 'N/A')
            table_type = form.get('tableType', 'N/A')
            form_id = form.get('id', 'N/A')
            print(f"  - {table_name} (tableType: {table_type}, ID: {form_id})")
        
        # 3. 自动删除
        print("\n🗑️ 自动删除这些表单...")
        if deleter.delete_forms_batch(target_forms):
            print("✅ 表单删除完成")
        else:
            print("❌ 表单删除失败")
    else:
        print("✅ 没有发现需要删除的表单")
    
    print("🔚 表单删除工具执行完成")


def main():
    """主函数 - 提供交互式菜单"""
    print("🛠️ JeecgBoot工具集")
    print("="*50)
    print("1. 查询表单")
    print("2. 删除表单")
    print("3. 查询菜单权限")
    print("4. 测试数据库连接")
    print("5. 退出")
    print("="*50)
    
    while True:
        try:
            choice = input("请选择操作 (1-5): ").strip()
            
            if choice == '1':
                query_forms()
                break
            elif choice == '2':
                delete_forms()
                break
            elif choice == '3':
                query_permissions()
                break
            elif choice == '4':
                test_database_connection()
                break
            elif choice == '5':
                print("👋 再见！")
                sys.exit(0)
            else:
                print("❌ 无效选择，请输入 1-5")
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出程序")
            sys.exit(0)


if __name__ == "__main__":
    # 支持命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == 'query':
            query_forms()
        elif sys.argv[1] == 'delete':
            delete_forms()
        elif sys.argv[1] == 'permission':
            query_permissions()
        elif sys.argv[1] == 'test-db':
            test_database_connection()
        else:
            print("❌ 无效参数，支持的参数: query, delete, permission, test-db")
            print("使用示例:")
            print("  python jeecgboot_tools.py query      # 查询表单")
            print("  python jeecgboot_tools.py delete     # 删除表单")
            print("  python jeecgboot_tools.py permission # 查询菜单权限")
            print("  python jeecgboot_tools.py test-db    # 测试数据库连接")
            print("  python jeecgboot_tools.py            # 交互式菜单")
    else:
        main()