#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot 表单查询工具
用于查询本次education.student需求生成的表单及其tableType值
"""

import requests
import json
import sys
import os
import configparser
from typing import List, Dict, Optional

class JeecgBootFormQuery:
    """JeecgBoot表单查询器"""
    
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
            'us_education_student_student_info',
            'us_education_student_parent_info', 
            'us_education_student_classmate_relation'
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

def main():
    """主函数"""
    print("🚀 开始查询JeecgBoot表单...")
    
    query = JeecgBootFormQuery()
    
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

if __name__ == "__main__":
    main()