#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除错误的JeecgBoot表单工具
"""

import requests
import json
import sys
import os
import configparser
import urllib.parse

class FormDeleter:
    """表单删除器"""
    
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
                        'us_education_student_student_info',
                        'us_education_student_parent_info',
                        'us_education_student_classmate_relation'
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

def main():
    """主函数"""
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
        if True:
            if deleter.delete_forms_batch(target_forms):
                print("✅ 表单删除完成")
            else:
                print("❌ 表单删除失败")
        else:
            print("❌ 用户取消操作")
    else:
        print("✅ 没有发现需要删除的表单")
    
    print("🔚 表单删除工具执行完成")

if __name__ == "__main__":
    main()