#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot 代码生成执行器
核心功能：
- 执行完整的JeecgBoot API调用流程
- 支持独立表、主表、子表三种场景
- 集成配置验证和错误处理
- 自动化前端代码迁移
"""

import json
import requests
import time
import os
import sys
import subprocess
import shutil
import configparser
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# 导入验证器
try:
    from Code_Gen_Validator import CodeGenValidator
except ImportError:
    print("警告: 无法导入Code_Gen_Validator，将跳过配置验证")
    CodeGenValidator = None

class CodeGenExecutor:
    """JeecgBoot代码生成执行器"""
    
    def __init__(self, config_file: str = None):
        """初始化执行器"""
        if config_file is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(current_dir, "Code_Gen_Config.properties")
        
        self.config_file = config_file
        self.config = self._load_config()
        self.session = requests.Session()
        self.token = None
        
        # 初始化验证器
        if CodeGenValidator:
            self.validator = CodeGenValidator()
        else:
            self.validator = None
    
    def _load_config(self) -> configparser.ConfigParser:
        """加载配置文件"""
        config = configparser.ConfigParser()
        try:
            config.read(self.config_file, encoding='utf-8')
            return config
        except Exception as e:
            print(f"配置文件加载失败: {e}")
            sys.exit(1)
    
    def get_config_value(self, section: str, key: str, fallback: str = None) -> str:
        """获取配置值，支持变量替换"""
        try:
            value = self.config.get(section, key, fallback=fallback)
            # 简单的变量替换
            if value and '${' in value:
                # 替换常见变量
                base_url = self.config.get('server', 'base_url', fallback='http://localhost:8080/jeecg-boot')
                value = value.replace('${server.base_url}', base_url)
            return value
        except Exception:
            return fallback

    def _retry_request(self, func, *args, **kwargs):
        """重试机制"""
        max_attempts = int(self.get_config_value('api', 'retry.max_attempts', '3'))
        delay_seconds = int(self.get_config_value('api', 'retry.delay_seconds', '2'))

        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise e
                print(f"⚠️ 请求失败，{delay_seconds}秒后重试 (第{attempt + 1}/{max_attempts}次)")
                time.sleep(delay_seconds)
    
    def login(self) -> bool:
        """用户登录认证"""
        login_url = self.get_config_value('api', 'login.url')
        username = self.get_config_value('server', 'username')
        password = self.get_config_value('server', 'password')
        timeout = int(self.get_config_value('timeouts', 'login', '30'))

        if not all([login_url, username, password]):
            print("登录配置不完整")
            return False

        login_data = {
            "username": username,
            "password": password,
            "captcha": "",
            "checkKey": ""
        }

        try:
            response = self.session.post(login_url, json=login_data, timeout=timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.token = result.get('result', {}).get('token')
                    if self.token:
                        # 设置请求头
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.token}',
                            'X-Access-Token': self.token
                        })
                        print("✅ 登录成功")
                        return True
            
            print(f"❌ 登录失败: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def validate_config(self, config_data: Dict) -> bool:
        """验证配置文件"""
        if not self.validator:
            print("⚠️ 跳过配置验证（验证器未加载）")
            return True
        
        # 创建临时文件进行验证
        temp_file = "temp_config.json"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            is_valid, errors = self.validator.validate_config(temp_file)
            
            if is_valid:
                print("✅ 配置验证通过")
                return True
            else:
                print("❌ 配置验证失败:")
                for error in errors:
                    print(f"  {error}")
                return False
                
        except Exception as e:
            print(f"⚠️ 配置验证异常: {e}")
            return True  # 验证异常时允许继续
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def execute_workflow(self, config_data: Dict) -> bool:
        """执行完整的代码生成工作流"""
        
        # 1. 验证配置
        if not self.validate_config(config_data):
            return False
        
        # 2. 登录认证
        if not self.login():
            return False
        
        # 3. 创建表单
        form_id = self.create_form(config_data)
        if not form_id:
            return False
        
        # 4. 同步数据库
        if not self.sync_database(form_id):
            return False
        
        # 5. 生成代码（根据表类型决定）
        table_type = config_data.get('head', {}).get('tableType', 1)
        if table_type != 3:  # 子表不生成代码
            if not self.generate_code(form_id, config_data):
                return False
        
        print("🎉 代码生成流程完成")
        return True
    
    def create_form(self, config_data: Dict) -> Optional[str]:
        """创建在线表单"""
        url = self.get_config_value('api', 'form.addall.url')
        if not url:
            print("❌ 缺少表单创建API配置")
            return None
        
        try:
            response = self.session.post(url, json=config_data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 表单创建成功")
                    return self.get_form_id(config_data.get('head', {}).get('tableName'))
                else:
                    print(f"❌ 表单创建失败: {result.get('message')}")
            else:
                print(f"❌ 表单创建请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 表单创建异常: {e}")
        
        return None
    
    def get_form_id(self, table_name: str) -> Optional[str]:
        """获取表单ID"""
        url = self.get_config_value('api', 'form.list.url')
        timeout = int(self.get_config_value('timeouts', 'list', '15'))
        page_no = int(self.get_config_value('query', 'page_no', '1'))
        page_size = int(self.get_config_value('query', 'page_size', '10'))

        if not url:
            return None

        try:
            params = {'tableName': table_name, 'pageNo': page_no, 'pageSize': page_size}
            response = self.session.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    records = result.get('result', {}).get('records', [])
                    if records:
                        return records[0].get('id')
        except Exception as e:
            print(f"❌ 获取表单ID异常: {e}")
        
        return None
    
    def sync_database(self, form_id: str) -> bool:
        """同步数据库"""
        url = self.get_config_value('api', 'database.sync.url')
        if not url:
            print("❌ 缺少数据库同步API配置")
            return False
        
        try:
            data = {"id": form_id}
            response = self.session.post(url, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 数据库同步成功")
                    return True
                else:
                    print(f"❌ 数据库同步失败: {result.get('message')}")
            else:
                print(f"❌ 数据库同步请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 数据库同步异常: {e}")
        
        return False
    
    def generate_code(self, form_id: str, config_data: Dict) -> bool:
        """生成代码"""
        url = self.get_config_value('api', 'codegen.generate.url')
        if not url:
            print("❌ 缺少代码生成API配置")
            return False
        
        # 构建代码生成参数
        project_path = self.get_config_value('paths', 'project_root')
        business_entity = config_data.get('head', {}).get('business_entity')
        table_type = config_data.get('head', {}).get('tableType', 1)
        
        # 根据表类型设置参数
        if table_type == 2:  # 主表
            jsp_mode = "jvxe"
            jform_type = "2"
            sub_list = config_data.get('subList', [])
        else:  # 独立表
            jsp_mode = "one"
            jform_type = "1"
            sub_list = []
        
        # 从配置文件读取代码生成参数
        package_style = self.get_config_value('codegen', 'package_style', 'service')
        vue_style = self.get_config_value('codegen', 'vue_style', 'vue3')

        data = {
            "id": form_id,
            "projectPath": project_path,
            "entityName": business_entity,
            "jspMode": jsp_mode,
            "jformType": jform_type,
            "packageStyle": package_style,
            "vueStyle": vue_style
        }
        
        if sub_list:
            data["subList"] = sub_list
        
        try:
            response = self.session.post(url, json=data, timeout=120)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 代码生成成功")
                    # 执行前端代码迁移
                    self.migrate_frontend_code(config_data)
                    return True
                else:
                    print(f"❌ 代码生成失败: {result.get('message')}")
            else:
                print(f"❌ 代码生成请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 代码生成异常: {e}")
        
        return False
    
    def migrate_frontend_code(self, config_data: Dict):
        """迁移前端代码"""
        try:
            # 获取模块信息
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            module_name = generation_info.get('module_name')
            
            if not module_name:
                print("⚠️ 无法获取模块名，跳过前端代码迁移")
                return
            
            # 构建路径
            project_root = self.get_config_value('paths', 'project_root')
            backend_vue_path = os.path.join(project_root, 'jeecg-module-system', 'jeecg-system-biz', 'src', 'main', 'resources', 'jeecg', module_name, 'vue3')
            frontend_target_path = os.path.join(project_root, 'jeecgboot-vue3', 'src', 'views', module_name)
            
            if os.path.exists(backend_vue_path):
                # 确保目标目录存在
                os.makedirs(os.path.dirname(frontend_target_path), exist_ok=True)
                
                # 移动目录
                if os.path.exists(frontend_target_path):
                    shutil.rmtree(frontend_target_path)
                shutil.move(backend_vue_path, frontend_target_path)
                
                print(f"✅ 前端代码迁移成功: {frontend_target_path}")
            else:
                print("⚠️ 未找到生成的前端代码")
                
        except Exception as e:
            print(f"⚠️ 前端代码迁移异常: {e}")

    def _replace_template_variables(self, config_data: Dict, project_path: str, module_name: str, submodule_name: str, business_entity: str) -> Dict:
        """替换模板中的变量占位符"""

        # 计算派生变量
        table_name = f"us_{module_name}_{submodule_name}_{business_entity.lower()}"
        package_name = f"org.jeecg.modules.{module_name}.{submodule_name}"
        table_suffix = business_entity.lower()
        url_path = f"{module_name}-{submodule_name}"
        frontend_path = f"{module_name}/{submodule_name}"
        table_description = f"{business_entity}管理"

        # 默认为独立表场景
        table_type = 1
        relation_type = None
        tab_order_num = None
        sub_table_str = None
        inference_strategy = "独立表场景"
        semantic_analysis = f"{business_entity}管理系统，独立表结构"

        # 变量映射表
        variables = {
            "{{PROJECT_PATH}}": project_path,
            "{{MODULE_NAME}}": module_name,
            "{{SUBMODULE_NAME}}": submodule_name,
            "{{BUSINESS_ENTITY}}": business_entity,
            "{{TABLE_NAME}}": table_name,
            "{{PACKAGE_NAME}}": package_name,
            "{{TABLE_SUFFIX}}": table_suffix,
            "{{URL_PATH}}": url_path,
            "{{FRONTEND_PATH}}": frontend_path,
            "{{TABLE_DESCRIPTION}}": table_description,
            "{{TABLE_TYPE}}": table_type,
            "{{RELATION_TYPE}}": relation_type,
            "{{TAB_ORDER_NUM}}": tab_order_num,
            "{{SUB_TABLE_STR}}": sub_table_str,
            "{{INFERENCE_STRATEGY}}": inference_strategy,
            "{{SEMANTIC_ANALYSIS}}": semantic_analysis
        }

        # 递归替换JSON中的所有变量
        replaced_config = self._recursive_replace(config_data, variables)

        # 生成字段配置
        replaced_config = self._generate_fields(replaced_config, module_name, submodule_name, business_entity)

        return replaced_config

    def _recursive_replace(self, obj, variables: Dict) -> any:
        """递归替换对象中的变量"""
        if isinstance(obj, dict):
            return {key: self._recursive_replace(value, variables) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._recursive_replace(item, variables) for item in obj]
        elif isinstance(obj, str):
            # 替换字符串中的变量
            result = obj
            for var, value in variables.items():
                if value is not None:
                    result = result.replace(var, str(value))
                else:
                    result = result.replace(var, "null")
            return result
        else:
            return obj

    def _generate_fields(self, config_data: Dict, module_name: str, submodule_name: str, business_entity: str) -> Dict:
        """生成标准字段配置"""

        # 获取系统字段模板
        system_fields = config_data.get('constants', {}).get('system_fields', [])

        # 生成系统字段
        fields = []
        for i, field_name in enumerate(system_fields):
            field_config = self._create_system_field(field_name, i)
            fields.append(field_config)

        # 生成业务字段（示例：根据业务实体生成基础字段）
        business_fields = self._generate_business_fields(business_entity, len(system_fields))
        fields.extend(business_fields)

        # 更新配置
        config_data['fields'] = fields
        config_data['subList'] = []
        config_data['indexs'] = []
        config_data['deleteFieldIds'] = []
        config_data['deleteIndexIds'] = []

        return config_data

    def _create_system_field(self, field_name: str, order_num: int) -> Dict:
        """创建系统字段配置"""

        # 系统字段配置模板
        system_field_configs = {
            "id": {
                "dbFieldName": "id",
                "dbFieldTxt": "主键",
                "fieldShowType": "text",
                "dbType": "string",
                "dbLength": 36,
                "dbIsKey": "1",
                "dbIsNull": "0",
                "isShowForm": "0",
                "isShowList": "0",
                "isQuery": "0",
                "fieldMustInput": "0",
                "isReadOnly": "1"
            },
            "create_by": {
                "dbFieldName": "create_by",
                "dbFieldTxt": "创建人",
                "fieldShowType": "text",
                "dbType": "string",
                "dbLength": 50,
                "dbIsKey": "0",
                "dbIsNull": "0",
                "isShowForm": "0",
                "isShowList": "0",
                "isQuery": "0",
                "fieldMustInput": "1",
                "isReadOnly": "0"
            },
            "create_time": {
                "dbFieldName": "create_time",
                "dbFieldTxt": "创建日期",
                "fieldShowType": "datetime",
                "dbType": "Datetime",
                "dbLength": 0,
                "dbIsKey": "0",
                "dbIsNull": "0",
                "isShowForm": "0",
                "isShowList": "0",
                "isQuery": "0",
                "fieldMustInput": "1",
                "isReadOnly": "0"
            },
            "update_by": {
                "dbFieldName": "update_by",
                "dbFieldTxt": "更新人",
                "fieldShowType": "text",
                "dbType": "string",
                "dbLength": 50,
                "dbIsKey": "0",
                "dbIsNull": "1",
                "isShowForm": "0",
                "isShowList": "0",
                "isQuery": "0",
                "fieldMustInput": "0",
                "isReadOnly": "1"
            },
            "update_time": {
                "dbFieldName": "update_time",
                "dbFieldTxt": "更新时间",
                "fieldShowType": "datetime",
                "dbType": "Datetime",
                "dbLength": 0,
                "dbIsKey": "0",
                "dbIsNull": "1",
                "isShowForm": "0",
                "isShowList": "1",
                "isQuery": "0",
                "fieldMustInput": "0",
                "isReadOnly": "1"
            },
            "sys_org_code": {
                "dbFieldName": "sys_org_code",
                "dbFieldTxt": "所属部门",
                "fieldShowType": "text",
                "dbType": "string",
                "dbLength": 64,
                "dbIsKey": "0",
                "dbIsNull": "0",
                "isShowForm": "0",
                "isShowList": "0",
                "isQuery": "0",
                "fieldMustInput": "1",
                "isReadOnly": "0"
            },
            "del_flag": {
                "dbFieldName": "del_flag",
                "dbFieldTxt": "删除标志",
                "fieldShowType": "text",
                "dbType": "int",
                "dbLength": 1,
                "dbIsKey": "0",
                "dbIsNull": "0",
                "isShowForm": "0",
                "isShowList": "0",
                "isQuery": "0",
                "fieldMustInput": "1",
                "isReadOnly": "0",
                "fieldDefaultValue": "0",
                "dbDefaultVal": "0"
            }
        }

        # 获取字段配置
        base_config = system_field_configs.get(field_name, {})

        # 添加通用属性
        field_config = {
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
            "dictTable": "",
            "dictField": "",
            "dictText": "",
            "sortFlag": "0",
            "fieldLength": 200,
            "queryMode": "single",
            "fieldDefaultValue": "",
            "converter": "",
            "fieldExtendJson": "",
            "fieldConfig": "",
            "dbPointLength": 0,
            "dbDefaultVal": "",
            "dbIsPersist": "1",
            "orderNum": order_num
        }

        # 合并配置
        field_config.update(base_config)

        return field_config

    def _generate_business_fields(self, business_entity: str, start_order_num: int) -> List[Dict]:
        """生成业务字段配置"""

        # 基础业务字段模板
        business_fields = []

        # 根据业务实体生成相应字段
        entity_lower = business_entity.lower()

        # 通用字段：名称字段
        name_field = {
            "dbFieldName": f"{entity_lower}_name",
            "dbFieldTxt": f"{business_entity}名称",
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
            "fieldMustInput": "1",
            "dictTable": "",
            "dictField": "",
            "dictText": "",
            "isShowForm": "1",
            "isShowList": "1",
            "sortFlag": "0",
            "isReadOnly": "0",
            "fieldShowType": "text",
            "fieldLength": 120,
            "isQuery": "1",
            "queryMode": "like",
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
            "orderNum": start_order_num
        }
        business_fields.append(name_field)

        # 通用字段：状态字段
        status_field = {
            "dbFieldName": "status",
            "dbFieldTxt": "状态",
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
            "isQuery": "1",
            "queryMode": "single",
            "fieldDefaultValue": "1",
            "converter": "",
            "fieldExtendJson": "",
            "fieldConfig": "",
            "dbLength": 2,
            "dbPointLength": 0,
            "dbDefaultVal": "1",
            "dbType": "int",
            "dbIsKey": "0",
            "dbIsNull": "0",
            "dbIsPersist": "1",
            "orderNum": start_order_num + 1
        }
        business_fields.append(status_field)

        # 通用字段：备注字段
        remark_field = {
            "dbFieldName": "remark",
            "dbFieldTxt": "备注",
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
            "isShowList": "0",
            "sortFlag": "0",
            "isReadOnly": "0",
            "fieldShowType": "textarea",
            "fieldLength": 500,
            "isQuery": "0",
            "queryMode": "single",
            "fieldDefaultValue": "",
            "converter": "",
            "fieldExtendJson": "",
            "fieldConfig": "",
            "dbLength": 500,
            "dbPointLength": 0,
            "dbDefaultVal": "",
            "dbType": "string",
            "dbIsKey": "0",
            "dbIsNull": "1",
            "dbIsPersist": "1",
            "orderNum": start_order_num + 2
        }
        business_fields.append(remark_field)

        return business_fields

def main():
    """主函数"""
    if len(sys.argv) < 5:
        print("用法: python3 Code_Gen_Execute.py <PROJECT_PATH> <MODULE_NAME> <SUBMODULE_NAME> <BUSINESS_ENTITY>")
        sys.exit(1)
    
    project_path, module_name, submodule_name, business_entity = sys.argv[1:5]
    
    # 创建执行器
    executor = CodeGenExecutor()
    
    # 加载模板配置
    template_path = os.path.join(os.path.dirname(__file__), 'Code_Gen_Template.json')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"❌ 模板加载失败: {e}")
        sys.exit(1)
    
    # 替换变量
    config_data = executor._replace_template_variables(config_data, project_path, module_name, submodule_name, business_entity)
    
    # 执行工作流
    success = executor.execute_workflow(config_data)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
