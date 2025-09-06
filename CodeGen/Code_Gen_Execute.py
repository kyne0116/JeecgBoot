#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot 代码生成执行器 v2.1
核心特性：
- 支持AI随机性的哨兵协调机制
- 基于MODULE_NAME+SUBMODULE_NAME的共同标识
- 智能场景识别和分发(tableType=1,2,3)
- 统一入口函数，完全向后兼容
- 线程安全的状态管理
- ✅ 修复：独立表完整代码生成工作流
"""

import json
import requests
import time
import os
import sys
import configparser
import fcntl
import random
import shutil
import subprocess
import glob
import re
import logging
import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# 导入验证器
try:
    from Code_Gen_Validator import CodeGenValidator
except ImportError:
    print("警告: 无法导入Code_Gen_Validator，将跳过配置验证")
    CodeGenValidator = None

# ===============================================================================
# 日志记录系统
# ===============================================================================

class CodeGenLogger:
    """代码生成日志记录器"""
    
    def __init__(self, module_name: str, submodule_name: str):
        self.module_name = module_name
        self.submodule_name = submodule_name
        self.log_file = f"{module_name}_{submodule_name}_execution.json"
        self.step_counter = 0
        self.logs = []
        self.workflow_steps = []  # 工作流步骤记录
        self.failed = False
        
    def log_step(self, step_name: str, status: str, details: str = "", result: str = ""):
        """记录工作流步骤"""
        self.step_counter += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = {
            "step_number": self.step_counter,
            "timestamp": timestamp,
            "step_name": step_name,
            "status": status,  # SUCCESS, FAILED, SKIPPED, IN_PROGRESS
            "details": details,
            "result": result
        }
        
        self.logs.append(log_entry)
        
        # 标准化工作流反馈格式 - 独占一行
        if status == "FAILED":
            self.failed = True
            print(f"[{self.step_counter:02d}] {step_name} - FAILED")
            if details:
                print(f"     失败原因: {details}")
        elif status == "SUCCESS":
            print(f"[{self.step_counter:02d}] {step_name} - PASS")
        elif status == "SKIPPED":
            print(f"[{self.step_counter:02d}] {step_name} - SKIP")
        elif status == "IN_PROGRESS":
            print(f"[{self.step_counter:02d}] {step_name} - RUNNING...")
        
        # 记录工作流步骤用于最后汇总
        self.workflow_steps.append({
            "number": self.step_counter,
            "name": step_name,
            "status": "PASS" if status == "SUCCESS" else ("SKIP" if status == "SKIPPED" else "FAIL")
        })
    
    def print_workflow_summary(self):
        """打印工作流汇总报告"""
        print("\n" + "="*60)
        print("代码生成工作流执行结果小结:")
        print("="*60)
        
        # 14行小结 - 每个环节状态
        for step in self.workflow_steps:
            status_display = {
                "PASS": "✅ PASS",
                "FAIL": "❌ FAIL", 
                "SKIP": "⏭️ SKIP"
            }.get(step["status"], step["status"])
            print(f"[{step['number']:02d}] {step['name']} - {status_display}")
        
        # 1行汇总状态
        summary_result = "Fail" if self.failed else "Pass"
        print("\n" + "="*60)
        print(f"代码生成工作流执行反馈汇总状态 SUMMARY_RESULT={summary_result}")
        print("="*60)
    
    def save_log_file(self):
        """保存执行报告文件 - JSON格式，AI友好"""
        try:
            # 统计执行结果
            success_count = len([step for step in self.logs if step.get('status') == 'SUCCESS'])
            failed_count = len([step for step in self.logs if step.get('status') == 'FAILED'])
            skipped_count = len([step for step in self.logs if step.get('status') == 'SKIPPED'])
            
            log_data = {
                # 文件元数据
                "format_version": "2.0",
                "file_type": "jeecgboot_execution_report",
                "generated_by": "Code_Gen_Execute.py v2.1",
                "generated_at": datetime.now().isoformat(),
                
                # 执行基本信息
                "module_name": self.module_name,
                "submodule_name": self.submodule_name,
                "execution_time": datetime.now().isoformat(),
                
                # 执行统计
                "execution_summary": {
                    "total_steps": self.step_counter,
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "skipped_count": skipped_count,
                    "overall_result": "Fail" if self.failed else "Pass",
                    "success_rate": f"{(success_count / self.step_counter * 100):.1f}%" if self.step_counter > 0 else "0.0%"
                },
                
                # 详细步骤日志
                "execution_steps": self.logs,
                
                # AI分析提示
                "ai_analysis_notes": {
                    "workflow_type": "jeecgboot_code_generation",
                    "key_failure_steps": [step["step_name"] for step in self.logs if step.get('status') == 'FAILED'],
                    "critical_success_steps": ["创建表单", "数据库同步", "代码生成"] 
                }
            }
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"📋 执行报告已保存: {self.log_file}")
            return True
        except Exception as e:
            print(f"❌ 执行报告保存失败: {e}")
            return False

# ===============================================================================
# 核心数据结构
# ===============================================================================

@dataclass
class TableInfo:
    """表信息数据结构"""
    table_name: str
    table_type: int  # 1=独立表, 2=主表, 3=子表
    entity_name: str
    form_id: Optional[str] = None
    sync_completed: bool = False
    code_generated: bool = False

class SentinelStatus:
    """哨兵状态管理"""
    PENDING = "pending"
    FORM_CREATED = "form_created" 
    SYNCED = "synced"
    CODE_GENERATED = "code_generated"

# ===============================================================================
# 哨兵协调机制
# ===============================================================================

class MasterSubTableSentinel:
    """主子表哨兵协调器 - 核心组件"""
    
    def __init__(self, module_name: str, submodule_name: str):
        self.module_name = module_name
        self.submodule_name = submodule_name
        self.sentinel_file = f"sentinel_{module_name}_{submodule_name}.json"
        self.sentinel_data = {}
        
    def get_or_create_sentinel(self, config_data: Dict) -> bool:
        """获取或创建哨兵文件"""
        try:
            if os.path.exists(self.sentinel_file):
                # 加载已存在的哨兵
                if self._load_sentinel():
                    # 检查当前表是否在哨兵中，如果不在就添加
                    table_name = config_data.get('head', {}).get('tableName', '')
                    if table_name and table_name not in self.sentinel_data.get('tables', {}):
                        self._add_table_info(config_data)
                        return self._save_sentinel()
                    return True
                return False
            else:
                # 创建新的哨兵
                return self._create_sentinel_from_config(config_data)
        except Exception as e:
            print(f"❌ 哨兵获取/创建失败: {e}")
            return False
    
    def _load_sentinel(self) -> bool:
        """加载哨兵文件"""
        try:
            with open(self.sentinel_file, 'r', encoding='utf-8') as f:
                self.sentinel_data = json.load(f)
            print(f"📋 加载已存在哨兵: {self.sentinel_file}")
            return True
        except Exception as e:
            print(f"❌ 哨兵文件加载失败: {e}")
            return False
    
    def _create_sentinel_from_config(self, config_data: Dict) -> bool:
        """从配置创建哨兵"""
        try:
            table_type = config_data.get('head', {}).get('tableType', 1)
            table_name = config_data.get('head', {}).get('tableName', '')
            
            # 初始化哨兵数据
            self.sentinel_data = {
                "scenario_id": f"{self.module_name}_{self.submodule_name}",
                "module_name": self.module_name,
                "submodule_name": self.submodule_name,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "tables": {},
                "version": 1
            }
            
            # 如果是主表，从subList推断所有表
            if table_type == 2:
                self._initialize_from_main_table(config_data)
            else:
                # 子表或独立表，只添加当前表
                self._add_table_info(config_data)
            
            # 保存哨兵文件
            return self._save_sentinel()
            
        except Exception as e:
            print(f"❌ 哨兵创建失败: {e}")
            return False
    
    def _initialize_from_main_table(self, main_config: Dict):
        """从主表配置初始化完整的表结构"""
        # 添加主表
        self._add_table_info(main_config)
        
        # 添加所有子表
        sub_list = main_config.get('subList', [])
        for i, sub_item in enumerate(sub_list, 1):
            sub_table_info = {
                'table_name': sub_item.get('tableName', ''),
                'table_type': 3,
                'entity_name': sub_item.get('entityName', ''),
                'status': SentinelStatus.PENDING,
                'form_id': None,
                'tab_order': i
            }
            
            table_name = sub_table_info['table_name']
            if table_name:
                self.sentinel_data['tables'][table_name] = sub_table_info
                print(f"📝 哨兵预期子表: {table_name}")
    
    def _add_table_info(self, config_data: Dict):
        """添加表信息到哨兵"""
        head = config_data.get('head', {})
        table_name = head.get('tableName', '')
        table_type = head.get('tableType', 1)
        entity_name = head.get('business_entity', '')
        
        if table_name:
            table_info = {
                'table_name': table_name,
                'table_type': table_type,
                'entity_name': entity_name,
                'status': SentinelStatus.PENDING,
                'form_id': None,
                'created_at': datetime.now().isoformat()
            }
            
            # 子表额外信息
            if table_type == 3:
                table_info['tab_order'] = head.get('tabOrderNum', 1)
            
            self.sentinel_data['tables'][table_name] = table_info
            print(f"📝 哨兵添加表: {table_name} (tableType={table_type})")
    
    def report_completion(self, table_name: str, status: str, form_id: str = None) -> bool:
        """报告表完成状态"""
        return self._safe_update_sentinel(lambda data: self._update_table_status(data, table_name, status, form_id))
    
    def _update_table_status(self, data: Dict, table_name: str, status: str, form_id: str = None):
        """更新表状态"""
        if table_name in data['tables']:
            data['tables'][table_name]['status'] = status
            data['tables'][table_name]['last_updated'] = datetime.now().isoformat()
            if form_id:
                data['tables'][table_name]['form_id'] = form_id
        data['last_updated'] = datetime.now().isoformat()
        data['version'] += 1
        return data
    
    def is_all_completed(self) -> bool:
        """检查是否所有表都完成了基础工作流"""
        if not self.sentinel_data or 'tables' not in self.sentinel_data:
            return False
        
        for table_name, table_info in self.sentinel_data['tables'].items():
            status = table_info.get('status', SentinelStatus.PENDING)
            if status not in [SentinelStatus.SYNCED, SentinelStatus.CODE_GENERATED]:
                return False
        
        return True
    
    def get_main_table_info(self) -> Optional[Dict]:
        """获取主表信息"""
        for table_name, table_info in self.sentinel_data.get('tables', {}).items():
            if table_info.get('table_type') == 2:
                return table_info
        return None
    
    def _safe_update_sentinel(self, update_func) -> bool:
        """线程安全的哨兵更新"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with open(self.sentinel_file, 'r+', encoding='utf-8') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    
                    # 读取当前数据
                    f.seek(0)
                    current_data = json.load(f)
                    
                    # 执行更新
                    updated_data = update_func(current_data)
                    
                    # 写回文件
                    f.seek(0)
                    f.truncate()
                    json.dump(updated_data, f, indent=2, ensure_ascii=False)
                    
                    # 更新本地数据
                    self.sentinel_data = updated_data
                    return True
                    
            except (IOError, OSError):
                if attempt == max_retries - 1:
                    return False
                time.sleep(random.uniform(0.1, 0.5))
        
        return False
    
    def _save_sentinel(self) -> bool:
        """保存哨兵文件"""
        try:
            with open(self.sentinel_file, 'w', encoding='utf-8') as f:
                json.dump(self.sentinel_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 哨兵文件保存成功: {self.sentinel_file}")
            return True
        except Exception as e:
            print(f"❌ 哨兵文件保存失败: {e}")
            return False
    
    def cleanup(self):
        """清理哨兵文件"""
        try:
            if os.path.exists(self.sentinel_file):
                os.remove(self.sentinel_file)
                print(f"🗑️ 清理哨兵文件: {self.sentinel_file}")
        except Exception as e:
            print(f"⚠️ 哨兵文件清理失败: {e}")

# ===============================================================================
# JeecgBoot API 接口层
# ===============================================================================

class JeecgBootAPIManager:
    """JeecgBoot API 接口管理器 - 从old版本借鉴"""
    
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
            env_mapping = {
                ('server', 'base_url'): 'JEECG_BASE_URL',
                ('server', 'username'): 'JEECG_USERNAME', 
                ('server', 'password'): 'JEECG_PASSWORD',
                ('project', 'path_prefix'): 'JEECG_PROJECT_ROOT'
            }
            
            env_key = env_mapping.get((section, key))
            if env_key:
                env_val = os.getenv(env_key)
                if env_val:
                    return env_val
            
            # 从配置文件读取
            return self.config.get(section, key, fallback=fallback)
        except:
            return fallback
    
    def login(self) -> bool:
        """用户登录认证"""
        login_url = self.get_config_value('api', 'login_url')
        username = self.get_config_value('server', 'username')
        password = self.get_config_value('server', 'password')
        timeout = int(self.get_config_value('timeouts', 'login', '10'))
        
        if not all([login_url, username, password]):
            print("❌ 登录配置不完整")
            return False
        
        login_data = {"username": username, "password": password}
        
        try:
            response = self.session.post(login_url, json=login_data, timeout=timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    token_info = result.get('result', {})
                    self.token = token_info.get('token')
                    if self.token:
                        print("✅ 登录成功")
                        return True
                    else:
                        print("❌ 未获取到token")
                else:
                    print(f"❌ 登录失败: {result.get('message')}")
            else:
                print(f"❌ 登录请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 登录异常: {e}")
        
        return False
    
    def create_form(self, config_data: Dict) -> Optional[str]:
        """创建在线表单"""
        url = self.get_config_value('api', 'form_addall_url')
        if not url:
            print("❌ 缺少表单创建API配置")
            return None
        
        if not self.token:
            print("❌ 未登录，无法创建表单")
            return None
        
        try:
            headers = {'X-Access-Token': self.token}
            response = self.session.post(url, json=config_data, headers=headers, timeout=60)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    table_name = config_data.get('head', {}).get('tableName')
                    print(f"✅ 表单创建成功: {table_name}")
                    
                    # 创建成功后，通过查询API获取表单ID
                    time.sleep(1)  # 等待一秒确保数据库写入完成
                    form_id = self.get_form_id(table_name)
                    if form_id:
                        print(f"✅ 获取到表单ID: {form_id}")
                        return form_id
                    else:
                        print(f"❌ 无法获取表单ID: {table_name}")
                        return None
                else:
                    error_message = result.get('message', '')
                    if '数据库表' in error_message and '已存在' in error_message:
                        # 数据库表已存在，尝试查询现有表单
                        table_name = config_data.get('head', {}).get('tableName')
                        print(f"⚠️ 表单创建失败（表已存在），尝试查询现有表单: {table_name}")
                        time.sleep(1)
                        form_id = self.get_form_id(table_name)
                        if form_id:
                            print(f"✅ 找到已存在表单ID: {form_id}")
                            return form_id
                        else:
                            print(f"❌ 无法找到已存在表单: {table_name}")
                            print(f"🔧 检测到数据不一致：数据库表存在但表单元数据缺失")
                            print(f"💡 建议手动删除数据库表: DROP TABLE {table_name}")
                            return None
                    else:
                        print(f"❌ 表单创建失败: {error_message}")
            else:
                print(f"❌ 表单创建请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 表单创建异常: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def get_form_id(self, table_name: str) -> Optional[str]:
        """获取表单ID"""
        url = self.get_config_value('api', 'form_list_url')
        timeout = int(self.get_config_value('timeouts', 'list', '15'))
        page_size = int(self.get_config_value('query', 'page_size', '50'))
        
        if not self.token:
            print("❌ 未登录，无法查询表单")
            return None
        
        try:
            headers = {'X-Access-Token': self.token}
            params = {'tableName': table_name, 'pageNo': 1, 'pageSize': page_size}
            response = self.session.get(url, params=params, headers=headers, timeout=timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    records = result.get('result', {}).get('records', [])
                    for record in records:
                        if record.get('tableName') == table_name:
                            return record.get('id')
        except Exception as e:
            print(f"❌ 表单查询异常: {e}")
        
        return None
    
    def sync_database(self, form_id: str) -> bool:
        """同步数据库"""
        base_url = self.get_config_value('server', 'base_url')
        base_path = self.get_config_value('api', 'database_sync_base_path', '/online/cgform/api/doDbSynch')
        
        if not base_url:
            print("❌ 缺少服务器基础URL配置")
            return False
        
        if not self.token:
            print("❌ 未登录，无法同步数据库")
            return False
        
        try:
            headers = {'X-Access-Token': self.token}
            url = f"{base_url}{base_path}/{form_id}/normal"
            response = self.session.post(url, headers=headers, timeout=60)
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
        """生成代码 - 支持主子表统一生成"""
        url = self.get_config_value('api', 'codegen_generate_url')
        if not url:
            print("❌ 缺少代码生成API配置")
            return False
        
        if not self.token:
            print("❌ 未登录，无法生成代码")
            return False
        
        # 构建代码生成参数
        table_name = config_data.get('head', {}).get('tableName', '')
        table_type = config_data.get('head', {}).get('tableType', 1)
        business_entity = config_data.get('head', {}).get('business_entity')
        
        # 解析表名获取模块信息 - 支持3段式命名
        parts = table_name.split('_')
        if len(parts) >= 3:
            module_name = parts[0]  # 第一段是模块名
            submodule_name = parts[1]  # 第二段是子模块名
            project_path = f"/Users/admin/Work/Github/JeecgBoot/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
            print(f"✅ 解析3段式表名: {table_name} -> 模块: {module_name}, 子模块: {submodule_name}")
        else:
            print(f"⚠️ 非标准3段式表名格式: {table_name}")
            project_path = self.get_config_value('project', 'path_prefix', '/tmp')
        
        # 根据表类型设置参数
        if table_type == 2:  # 主表
            jsp_mode = "jvxe"
            jform_type = "2"
            sub_list = config_data.get('subList', [])
        else:  # 独立表
            jsp_mode = "one"
            jform_type = "1"
            sub_list = []
        
        # 构建请求数据
        data = {
            "code": form_id,  # ✅ 修复: 使用code而不是id
            "projectPath": project_path,
            "entityName": business_entity,
            "entityPackage": submodule_name,  # ✅ 新增: 实体包名
            "jspMode": jsp_mode,
            "jformType": jform_type,
            "ftlDescription": config_data.get('head', {}).get('tableTxt', ''),  # ✅ 新增: 表描述
            "tableName_tmp": table_name,  # ✅ 新增: 临时表名
            "packageStyle": "service",
            "vueStyle": "vue3",
            "codeTypes": "controller,service,dao,mapper,entity,vue",
            "tableName": table_name
        }
        
        if sub_list:
            # ✅ 修复subList中的entityName格式 - 转换为完整格式
            fixed_sub_list = []
            for sub_item in sub_list:
                fixed_sub_item = sub_item.copy()
                # 将简化的实体名转换为完整格式
                # 例如: ParentInfo -> EducationStudentParentInfo
                simple_entity_name = sub_item.get('entityName', '')
                if simple_entity_name and business_entity:
                    # 构造完整实体名: 主表实体名 + 子表实体名
                    full_entity_name = f"{business_entity}{simple_entity_name}"
                    fixed_sub_item['entityName'] = full_entity_name
                    print(f"🔧 修复子表实体名: {simple_entity_name} -> {full_entity_name}")
                
                fixed_sub_list.append(fixed_sub_item)
            
            data["subList"] = fixed_sub_list
            print(f"📋 主表代码生成包含 {len(fixed_sub_list)} 个子表")
        
        # ✅ 调试输出：显示最终的代码生成参数
        print("📋 **代码生成参数总览**")
        print(f"   code: {data['code']}")
        print(f"   entityName: {data['entityName']}")
        print(f"   entityPackage: {data['entityPackage']}")
        print(f"   ftlDescription: {data['ftlDescription']}")
        print(f"   tableName: {data['tableName']}")
        print(f"   tableName_tmp: {data['tableName_tmp']}")
        if 'subList' in data:
            print(f"   subList: {len(data['subList'])} 个子表")
            for i, sub in enumerate(data['subList']):
                print(f"     - {sub.get('tableName')} -> {sub.get('entityName')}")
        
        try:
            headers = {'X-Access-Token': self.token}
            response = self.session.post(url, json=data, headers=headers, timeout=120)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 代码生成成功")
                    return True
                else:
                    print(f"❌ 代码生成失败: {result.get('message')}")
            else:
                print(f"❌ 代码生成请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 代码生成异常: {e}")
        
        return False
    
    def query_all_forms(self, page_size: int = 100) -> List[Dict]:
        """查询所有表单"""
        if not self.token:
            print("❌ 未登录，无法查询表单")
            return []
            
        url = self.get_config_value('api', 'form_list_url')
        headers = {'X-Access-Token': self.token}
        params = {'pageNo': 1, 'pageSize': page_size}
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('result', {}).get('records', [])
        except Exception as e:
            print(f"❌ 查询表单异常: {e}")
        
        return []
    
    def delete_forms_batch(self, form_ids: List[str]) -> bool:
        """批量删除表单"""
        if not form_ids:
            return True
        
        if not self.token:
            print("❌ 未登录，无法删除表单")
            return False
            
        url = self.get_config_value('api', 'form_delete_batch_url')
        if not url:
            print("❌ 缺少表单删除API配置")
            return False
        
        try:
            ids_str = ','.join(form_ids)
            import urllib.parse
            ids_encoded = urllib.parse.quote(ids_str, safe='')
            url_with_params = f"{url}?ids={ids_encoded}&flag=table"
            
            headers = {'X-Access-Token': self.token}
            response = self.session.delete(url_with_params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 成功删除 {len(form_ids)} 个表单")
                    return True
                else:
                    print(f"❌ 表单删除失败: {result.get('message')}")
            else:
                print(f"❌ 表单删除请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 表单删除异常: {e}")
        
        return False

# ===============================================================================
# 独立的可复用菜单权限SQL执行函数
# ===============================================================================

def execute_menu_permission_sql(module_name: str, submodule_name: str, business_entity: str, 
                                config_manager=None, logger: 'CodeGenLogger' = None) -> Dict:
    """
    独立的可复用菜单权限SQL执行函数
    
    Args:
        module_name: 模块名称 (如: finance)
        submodule_name: 子模块名称 (如: invoice)
        business_entity: 业务实体名称 (如: InvoiceHeader)
        config_manager: 配置管理器实例
        logger: 日志记录器实例
    
    Returns:
        Dict: 执行结果
        {
            'success': bool,
            'executed_files': List[str],
            'total_statements': int,
            'total_affected_rows': int,
            'execution_time': float,
            'error_message': str
        }
    """
    result = {
        'success': False,
        'executed_files': [],
        'total_statements': 0,
        'total_affected_rows': 0,
        'execution_time': 0.0,
        'error_message': ''
    }
    
    start_time = time.time()
    
    try:
        if logger:
            logger.log_step("菜单权限SQL执行", "IN_PROGRESS", f"开始为 {module_name}.{submodule_name}.{business_entity} 执行菜单权限SQL")
        
        # 创建数据库执行器实例（如果没有提供config_manager，使用默认配置）
        if not config_manager:
            from Code_Gen_Execute import JeecgBootAPIManager
            config_manager = JeecgBootAPIManager()
        
        sql_executor = DatabaseSQLExecutor(config_manager)
        
        # 检查是否启用SQL执行
        enabled = config_manager.get_config_value('database_execution', 'enabled', 'true').lower() == 'true'
        if not enabled:
            result['error_message'] = 'SQL执行已在配置中禁用'
            if logger:
                logger.log_step("菜单权限SQL执行", "SKIPPED", "SQL执行已禁用")
            result['success'] = True  # 禁用状态也算成功
            return result
        
        # 查找SQL文件
        project_root = os.getenv('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
        module_path = f"{project_root}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
        
        sql_files = []
        for root, dirs, files in os.walk(module_path):
            for file in files:
                if file.endswith('.sql') and 'menu' in file.lower():
                    sql_files.append(os.path.join(root, file))
        
        if not sql_files:
            result['error_message'] = '没有找到菜单SQL文件'
            if logger:
                logger.log_step("菜单权限SQL执行", "SKIPPED", "没有找到菜单SQL文件")
            result['success'] = True  # 没有文件也算成功（可能不需要菜单）
            return result
        
        # 建立数据库连接
        if not sql_executor._connect_database():
            result['error_message'] = '数据库连接失败'
            if logger:
                logger.log_step("菜单权限SQL执行", "FAILED", "数据库连接失败")
            return result
        
        try:
            # 执行所有SQL文件
            total_statements = 0
            total_affected_rows = 0
            successful_files = []
            failed_files = []
            
            for sql_file in sql_files:
                execution_result = sql_executor._execute_sql_file_real(sql_file)
                
                if execution_result['success']:
                    successful_files.append(os.path.basename(sql_file))
                    total_statements += execution_result['executed_statements']
                    total_affected_rows += execution_result['affected_rows']
                else:
                    failed_files.append({
                        'file': os.path.basename(sql_file),
                        'error': execution_result['error_message']
                    })
            
            # 设置执行结果
            result['executed_files'] = successful_files
            result['total_statements'] = total_statements
            result['total_affected_rows'] = total_affected_rows
            result['execution_time'] = time.time() - start_time
            
            if successful_files:
                result['success'] = True
                if logger:
                    logger.log_step("菜单权限SQL执行", "SUCCESS",
                                   f"成功执行 {len(successful_files)} 个SQL文件，共 {total_statements} 条语句，影响 {total_affected_rows} 行数据",
                                   f"成功文件: {successful_files}")
            else:
                result['error_message'] = f"所有SQL文件执行失败: {failed_files}"
                if logger:
                    logger.log_step("菜单权限SQL执行", "FAILED",
                                   f"找到 {len(sql_files)} 个SQL文件，但全部执行失败",
                                   f"失败详情: {failed_files}")
        
        finally:
            sql_executor._close_database_connection()
    
    except Exception as e:
        result['error_message'] = f"执行异常: {str(e)}"
        if logger:
            logger.log_step("菜单权限SQL执行", "FAILED", f"执行异常: {str(e)}")
        print(f"❌ 菜单权限SQL执行异常: {e}")
        import traceback
        traceback.print_exc()
    
    return result

# ===============================================================================
# 其他功能模块 (从old版本借鉴核心功能)
# ===============================================================================

class FrontendMigrator:
    """前端代码迁移器"""
    
    def __init__(self, config_manager):
        self.config = config_manager
    
    def migrate_frontend_code(self, config_data: Dict, logger: 'CodeGenLogger' = None) -> bool:
        """迁移前端代码到正确位置"""
        try:
            if logger:
                logger.log_step("前端代码迁移", "IN_PROGRESS", "开始迁移Vue3前端代码")
            
            # 检查是否启用
            enabled = self.config.get_config_value('frontend_migration', 'enabled', 'true').lower() == 'true'
            if not enabled:
                if logger:
                    logger.log_step("前端代码迁移", "SKIPPED", "前端代码迁移已禁用")
                return True
            
            # 获取路径信息
            project_root = os.getenv('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
            target_base_path = self.config.get_config_value('frontend_migration', 'target_base_path', 'jeecgboot-vue3/src/views')
            target_base_full = f"{project_root}/{target_base_path}"
            
            # 从metadata获取模块信息
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            
            module_name = generation_info.get('module_name', '')
            submodule_name = generation_info.get('submodule_name', '')
            business_entity = generation_info.get('business_entity', '')
            
            if not all([module_name, submodule_name]):
                if logger:
                    logger.log_step("前端代码迁移", "FAILED", "缺少模块信息")
                return False
            
            # 源路径：生成的Vue3代码位置（处理包重命名后的路径）
            source_vue_path = f"{project_root}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}/src/main/java/org/jeecg/modules/{module_name}/{submodule_name}/{submodule_name}/vue3"
            
            # 目标路径：前端项目中的位置
            target_module_dir = f"{target_base_full}/{module_name}/{submodule_name}"
            
            # 检查源路径是否存在
            if not os.path.exists(source_vue_path):
                if logger:
                    logger.log_step("前端代码迁移", "FAILED", f"源路径不存在: {source_vue_path}")
                return False
            
            # 创建目标目录
            os.makedirs(target_module_dir, exist_ok=True)
            
            # 迁移文件
            migrated_files = []
            failed_files = []
            
            for file_name in os.listdir(source_vue_path):
                source_file = os.path.join(source_vue_path, file_name)
                target_file = os.path.join(target_module_dir, file_name)
                
                if os.path.isfile(source_file) and file_name.endswith(('.vue', '.ts', '.js')):
                    try:
                        # 验证文件复制是否成功
                        shutil.copy2(source_file, target_file)
                        
                        # 验证目标文件是否存在且大小相同
                        if os.path.exists(target_file) and os.path.getsize(source_file) == os.path.getsize(target_file):
                            migrated_files.append(file_name)
                        else:
                            failed_files.append(file_name)
                            
                    except Exception as e:
                        failed_files.append(f"{file_name} (错误: {str(e)})")
            
            # 根据实际结果判断成功或失败
            if migrated_files and not failed_files:
                if logger:
                    logger.log_step("前端代码迁移", "SUCCESS", 
                                   f"成功迁移 {len(migrated_files)} 个文件到 {target_module_dir}",
                                   f"文件: {', '.join(migrated_files)}")
                return True
            elif migrated_files and failed_files:
                if logger:
                    logger.log_step("前端代码迁移", "SUCCESS", 
                                   f"部分成功: 迁移 {len(migrated_files)} 个文件，{len(failed_files)} 个失败",
                                   f"成功: {migrated_files}, 失败: {failed_files}")
                return True  # 部分成功也算成功
            elif not migrated_files and not failed_files:
                if logger:
                    logger.log_step("前端代码迁移", "SKIPPED", "源目录中没有找到需要迁移的前端文件")
                return True  # 没有文件需要迁移，算作成功
            else:
                if logger:
                    logger.log_step("前端代码迁移", "FAILED", 
                                   f"所有文件迁移都失败: {failed_files}")
                return False
            
        except Exception as e:
            if logger:
                logger.log_step("前端代码迁移", "FAILED", f"异常: {str(e)}")
            print(f"❌ 前端代码迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return False

class PlaceholderProcessor:
    """占位变量处理器"""
    
    def __init__(self, config_manager):
        self.config = config_manager
    
    def process_placeholder_variables(self, config_data: Dict, logger: 'CodeGenLogger' = None) -> bool:
        """处理占位变量替换"""
        try:
            if logger:
                logger.log_step("占位变量处理", "IN_PROGRESS", "开始处理生成代码中的占位变量")
            
            # 提取模块信息
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            
            module_name = generation_info.get('module_name', '')
            submodule_name = generation_info.get('submodule_name', '')
            business_entity = generation_info.get('business_entity', '')
            
            if not all([module_name, submodule_name, business_entity]):
                if logger:
                    logger.log_step("占位变量处理", "FAILED", "缺少必要的模块信息")
                return False
            
            # 构建包名和路径映射
            package_name = f"org.jeecg.modules.{module_name}.{submodule_name}"
            package_path = package_name.replace('.', '/')
            
            # 定义占位变量映射
            placeholders = {
                '{{PACKAGE_NAME}}': package_name,
                '{{MODULE_NAME}}': module_name,
                '{{SUBMODULE_NAME}}': submodule_name,
                '{{BUSINESS_ENTITY}}': business_entity
            }
            
            # 查找生成的模块目录
            project_root = os.getenv('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
            module_path = f"{project_root}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
            
            if not os.path.exists(module_path):
                if logger:
                    logger.log_step("占位变量处理", "FAILED", f"模块目录不存在: {module_path}")
                return False
            
            # 处理文件夹重命名 - 先重命名包目录结构
            src_java_path = f"{module_path}/src/main/java"
            old_package_path = f"{src_java_path}/{{{{PACKAGE_NAME}}}}"
            new_package_path = f"{src_java_path}/{package_path}"
            
            if os.path.exists(old_package_path):
                # 创建正确的包目录结构
                os.makedirs(os.path.dirname(new_package_path), exist_ok=True)
                shutil.move(old_package_path, new_package_path)
                if logger:
                    logger.log_step("文件夹重命名", "SUCCESS", f"包目录重命名: {{{{PACKAGE_NAME}}}} -> {package_path}")
            
            # 处理所有文件中的占位变量
            replaced_count = 0
            for root, dirs, files in os.walk(module_path):
                for file in files:
                    if file.endswith(('.java', '.xml', '.ts', '.vue', '.sql')):
                        file_path = os.path.join(root, file)
                        if self._replace_file_placeholders(file_path, placeholders):
                            replaced_count += 1
            
            if logger:
                logger.log_step("占位变量处理", "SUCCESS", 
                               f"共处理 {replaced_count} 个文件", 
                               f"占位变量映射: {placeholders}")
            return True
            
        except Exception as e:
            if logger:
                logger.log_step("占位变量处理", "FAILED", f"异常: {str(e)}")
            print(f"❌ 占位变量处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _replace_file_placeholders(self, file_path: str, placeholders: Dict[str, str]) -> bool:
        """替换单个文件中的占位变量"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 替换所有占位变量
            for placeholder, value in placeholders.items():
                content = content.replace(placeholder, value)
            
            # 如果内容有变化才写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ 文件处理失败 {file_path}: {e}")
            return False

class DatabaseSQLExecutor:
    """真正的数据库SQL执行器 - 支持MySQL客户端和JDBC连接"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.connection = None
        self.execution_stats = {'executed': 0, 'failed': 0, 'total_affected_rows': 0}
    
    def execute_permission_sql(self, config_data: Dict, logger: 'CodeGenLogger' = None) -> bool:
        """执行权限菜单SQL脚本 - 使用独立的可复用函数"""
        try:
            # 提取模块信息
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            module_name = generation_info.get('module_name', '')
            submodule_name = generation_info.get('submodule_name', '')
            business_entity = generation_info.get('business_entity', '')
            
            if not all([module_name, submodule_name, business_entity]):
                if logger:
                    logger.log_step("SQL脚本执行", "FAILED", "缺少必要的模块信息")
                return False
            
            # 调用独立的可复用函数
            result = execute_menu_permission_sql(
                module_name=module_name,
                submodule_name=submodule_name,
                business_entity=business_entity,
                config_manager=self.config,
                logger=logger
            )
            
            return result['success']
            
        except Exception as e:
            if logger:
                logger.log_step("SQL脚本执行", "FAILED", f"调用独立函数异常: {str(e)}")
            print(f"❌ SQL脚本执行失败: {e}")
            return False
    
    def _connect_database(self) -> bool:
        """建立数据库连接"""
        try:
            # 从环境变量读取数据库连接信息
            db_type = os.getenv('JEECG_DATABASE_TYPE', 'mysql')
            db_url = os.getenv('JEECG_DATABASE_URL', 'localhost:3306/jeecg-boot')
            db_username = os.getenv('JEECG_DATABASE_USERNAME', 'root')
            db_password = os.getenv('JEECG_DATABASE_PASSWORD', '')
            
            if not all([db_url, db_username]):
                print("❌ 数据库连接信息不完整，请检查环境变量: JEECG_DATABASE_URL, JEECG_DATABASE_USERNAME, JEECG_DATABASE_PASSWORD")
                return False
            
            # 解析JDBC数据库URL - 使用正确的正则表达式解析
            import re
            match = re.search(r'jdbc:mysql://([^:/]+):(\d+)/([^?]+)', db_url)
            if not match:
                print(f"❌ JDBC URL格式错误: {db_url}，应为 jdbc:mysql://host:port/database 格式")
                return False
            host, port, database = match.groups()
            port = int(port)
            
            # 建立MySQL连接
            self.connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=db_username,
                password=db_password,
                autocommit=self.config.get_config_value('database_execution', 'auto_commit', 'true').lower() == 'true',
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            
            if self.connection.is_connected():
                print(f"✅ 数据库连接成功: {host}:{port}/{database}")
                return True
            else:
                print("❌ 数据库连接失败")
                return False
                
        except Error as e:
            print(f"❌ 数据库连接异常: {e}")
            return False
        except Exception as e:
            print(f"❌ 数据库连接配置异常: {e}")
            return False
    
    def _execute_sql_file_real(self, sql_file: str) -> Dict:
        """真正执行单个SQL文件到数据库"""
        result = {
            'file': sql_file,
            'success': False,
            'executed_statements': 0,
            'affected_rows': 0,
            'execution_time': 0.0,
            'error_message': '',
            'warnings': []
        }
        
        try:
            start_time = time.time()
            
            # 读取SQL文件
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read().strip()
            
            if not sql_content:
                result['error_message'] = 'SQL文件为空'
                return result
            
            # 分割SQL语句（处理多条SQL语句）
            sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            if not sql_statements:
                result['error_message'] = '没有有效的SQL语句'
                return result
            
            cursor = self.connection.cursor()
            total_affected_rows = 0
            
            try:
                for i, sql_statement in enumerate(sql_statements, 1):
                    # 跳过注释行
                    if sql_statement.startswith('--') or sql_statement.startswith('#'):
                        continue
                    
                    print(f"🔄 执行SQL语句 {i}/{len(sql_statements)}: {sql_statement[:50]}...")
                    cursor.execute(sql_statement)
                    
                    affected_rows = cursor.rowcount if cursor.rowcount >= 0 else 0
                    total_affected_rows += affected_rows
                    
                    print(f"✅ SQL执行成功，影响 {affected_rows} 行")
                
                result['success'] = True
                result['executed_statements'] = len(sql_statements)
                result['affected_rows'] = total_affected_rows
                result['execution_time'] = time.time() - start_time
                
                print(f"🎉 SQL文件执行完成: {os.path.basename(sql_file)}")
                print(f"   执行语句: {result['executed_statements']} 条")
                print(f"   影响行数: {result['affected_rows']} 行")
                print(f"   执行时间: {result['execution_time']:.2f} 秒")
                
            except Error as e:
                result['error_message'] = f"SQL执行错误: {str(e)}"
                print(f"❌ SQL执行失败: {e}")
            finally:
                cursor.close()
            
        except Exception as e:
            result['error_message'] = f"文件处理异常: {str(e)}"
            print(f"⚠️ SQL文件处理异常 {sql_file}: {e}")
        
        return result
    
    def _close_database_connection(self):
        """关闭数据库连接"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("✅ 数据库连接已关闭")
        except Exception as e:
            print(f"⚠️ 关闭数据库连接时发生异常: {e}")

class PermissionManager:
    """真正的权限管理器 - 实现真正的权限分配"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.api_manager = config_manager  # 复用API管理器的token和连接
    
    def grant_permissions(self, config_data: Dict, logger: 'CodeGenLogger' = None) -> bool:
        """为管理员角色授权新生成模块的权限 - 真正实现"""
        try:
            if logger:
                logger.log_step("权限授权", "IN_PROGRESS", "为管理员角色授权新模块权限")
            
            enabled = self.config.get_config_value('permission_authorization', 'enabled', 'true').lower() == 'true'
            if not enabled:
                if logger:
                    logger.log_step("权限授权", "SKIPPED", "权限授权已禁用")
                return True
            
            # 获取基本信息
            admin_role_id = self.config.get_config_value('permission_authorization', 'admin_role_id', 'f6817f48af4fb3af11b9e8bf182f618b')
            timeout = int(self.config.get_config_value('permission_authorization', 'timeout', '30'))
            retry_attempts = int(self.config.get_config_value('permission_authorization', 'retry_attempts', '3'))
            
            # 获取模块信息
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            business_entity = generation_info.get('business_entity', '')
            module_name = generation_info.get('module_name', '')
            
            if not all([business_entity, module_name]):
                if logger:
                    logger.log_step("权限授权", "FAILED", "缺少必要的模块信息")
                return False
            
            # 获取表名和菜单ID
            table_name = config_data.get('head', {}).get('tableName', '')
            if not table_name:
                if logger:
                    logger.log_step("权限授权", "FAILED", "缺少表名信息")
                return False
            
            # 先查找新创建的菜单ID
            menu_ids = self._find_menu_ids_by_table_name(table_name)
            if not menu_ids:
                if logger:
                    logger.log_step("权限授权", "FAILED", f"未找到表 {table_name} 对应的菜单ID")
                return False
            
            # 为管理员角色授权
            successful_grants = 0
            total_grants = len(menu_ids)
            
            for menu_id in menu_ids:
                for attempt in range(retry_attempts):
                    if self._grant_menu_permission_to_role(admin_role_id, menu_id, timeout):
                        successful_grants += 1
                        break
                    elif attempt < retry_attempts - 1:
                        time.sleep(1)  # 重试间隔
            
            # 记录结果
            if successful_grants == total_grants:
                permission_info = {
                    "admin_role_id": admin_role_id,
                    "business_entity": business_entity,
                    "table_name": table_name,
                    "granted_menus": successful_grants,
                    "total_menus": total_grants,
                    "menu_ids": menu_ids
                }
                if logger:
                    logger.log_step("权限授权", "SUCCESS",
                                   f"成功为角色 {admin_role_id} 授权 {successful_grants}/{total_grants} 个菜单权限",
                                   f"权限详情: {permission_info}")
                return True
            elif successful_grants > 0:
                if logger:
                    logger.log_step("权限授权", "SUCCESS",
                                   f"部分成功: 为角色 {admin_role_id} 授权 {successful_grants}/{total_grants} 个菜单权限")
                return True
            else:
                if logger:
                    logger.log_step("权限授权", "FAILED", "所有权限授权尝试都失败")
                return False
            
        except Exception as e:
            if logger:
                logger.log_step("权限授权", "FAILED", f"异常: {str(e)}")
            print(f"❌ 权限授权失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _find_menu_ids_by_table_name(self, table_name: str) -> List[str]:
        """根据表名查找对应的菜单ID"""
        try:
            # 调用JeecgBoot的菜单查询API
            base_url = self.config.get_config_value('server', 'base_url', 'http://localhost:8080/jeecg-boot')
            menu_list_url = f"{base_url}/sys/permission/list"  # JeecgBoot菜单列表API
            
            if not self.api_manager.token:
                print("❌ 未登录，无法查询菜单")
                return []
            
            headers = {'X-Access-Token': self.api_manager.token}
            params = {
                'pageNo': 1,
                'pageSize': 100,
                'menuName': table_name  # 根据表名搜索菜单
            }
            
            response = self.api_manager.session.get(menu_list_url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    records = result.get('result', {}).get('records', [])
                    menu_ids = [record.get('id') for record in records if record.get('id')]
                    print(f"✅ 找到 {len(menu_ids)} 个菜单ID: {menu_ids}")
                    return menu_ids
                else:
                    print(f"❌ 菜单查询失败: {result.get('message')}")
            else:
                print(f"❌ 菜单查询请求失败: {response.status_code}")
        
        except Exception as e:
            print(f"❌ 查找菜单ID异常: {e}")
        
        return []
    
    def _grant_menu_permission_to_role(self, role_id: str, menu_id: str, timeout: int) -> bool:
        """为角色授予指定菜单的权限"""
        try:
            base_url = self.config.get_config_value('server', 'base_url', 'http://localhost:8080/jeecg-boot')
            permission_grant_url = f"{base_url}/sys/role/queryTreeList"  # JeecgBoot角色权限管理API
            
            if not self.api_manager.token:
                print("❌ 未登录，无法授予权限")
                return False
            
            headers = {'X-Access-Token': self.api_manager.token}
            data = {
                'roleId': role_id,
                'permissionIds': menu_id,
                'lastPermissionIds': ''  # 上次的权限ID列表
            }
            
            response = self.api_manager.session.post(permission_grant_url, json=data, headers=headers, timeout=timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 成功为角色 {role_id} 授予菜单 {menu_id} 的权限")
                    return True
                else:
                    print(f"❌ 权限授予失败: {result.get('message')}")
            else:
                print(f"❌ 权限授予请求失败: {response.status_code}")
            
        except Exception as e:
            print(f"❌ 权限授予异常: {e}")
        
        return False

# ===============================================================================
# 模块管理器 - Maven模块创建和POM配置
# ===============================================================================

class ModuleManager:
    """Maven模块管理器 - 负责模块创建和POM文件配置"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        
    def ensure_module_exists(self, module_name: str, logger: 'CodeGenLogger' = None) -> bool:
        """确保模块存在，如果不存在则创建并配置"""
        try:
            if logger:
                logger.log_step("模块检查", "IN_PROGRESS", f"检查模块 {module_name} 是否存在")
            
            # 1. 检查模块是否存在
            if self._check_module_exists(module_name):
                if logger:
                    logger.log_step("模块检查", "SUCCESS", "模块已存在，跳过创建")
                return True
            
            if logger:
                logger.log_step("模块检查", "SUCCESS", "模块不存在，开始创建流程")
            
            # 2. 创建Maven模块
            if not self._create_maven_module(module_name, logger):
                return False
                
            # 3. 更新模块注册表pom.xml
            if not self._update_module_registry_pom(module_name, logger):
                return False
                
            # 4. 更新系统启动项目pom.xml
            if not self._update_system_start_pom(module_name, logger):
                return False
                
            return True
            
        except Exception as e:
            if logger:
                logger.log_step("模块管理", "FAILED", f"模块管理异常: {str(e)}")
            print(f"❌ 模块管理异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_module_exists(self, module_name: str) -> bool:
        """检查模块目录是否存在"""
        try:
            project_root = os.getenv('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
            module_path = f"{project_root}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
            return os.path.exists(module_path)
        except Exception:
            return False
    
    def _create_maven_module(self, module_name: str, logger: 'CodeGenLogger' = None) -> bool:
        """使用Maven archetype创建新模块"""
        try:
            if logger:
                logger.log_step("Maven模块创建", "IN_PROGRESS", f"执行mvn archetype:generate创建模块 jeecg-module-{module_name}")
            
            # 获取项目根路径
            project_root = os.getenv('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
            exec_dir = f"{project_root}/jeecg-boot/jeecg-boot-module"
            
            if not os.path.exists(exec_dir):
                if logger:
                    logger.log_step("Maven模块创建", "FAILED", f"执行目录不存在: {exec_dir}")
                return False
            
            # 构建Maven命令
            maven_cmd = [
                'mvn', 'archetype:generate',
                '-DgroupId=org.jeecgframework.boot',
                f'-DartifactId=jeecg-module-{module_name}',
                '-Dversion=3.8.2',
                '-DarchetypeGroupId=org.jeecgframework.archetype',
                '-DarchetypeArtifactId=jeecg-boot-gen',
                '-DarchetypeVersion=2.0',
                '-DinteractiveMode=false'  # 非交互模式
            ]
            
            # 执行Maven命令
            result = subprocess.run(
                maven_cmd,
                cwd=exec_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                if logger:
                    logger.log_step("Maven模块创建", "SUCCESS", f"Maven模块创建成功: jeecg-module-{module_name}")
                return True
            else:
                error_msg = f"Maven命令执行失败(返回码:{result.returncode})"
                if result.stderr:
                    error_msg += f", 错误: {result.stderr[:200]}"
                if logger:
                    logger.log_step("Maven模块创建", "FAILED", error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            if logger:
                logger.log_step("Maven模块创建", "FAILED", "Maven命令执行超时(5分钟)")
            return False
        except Exception as e:
            if logger:
                logger.log_step("Maven模块创建", "FAILED", f"Maven命令执行异常: {str(e)}")
            return False
    
    def _update_module_registry_pom(self, module_name: str, logger: 'CodeGenLogger' = None) -> bool:
        """更新模块注册表pom.xml添加新模块"""
        try:
            if logger:
                logger.log_step("模块注册", "IN_PROGRESS", "更新jeecg-boot-module/pom.xml添加模块引用")
            
            project_root = os.getenv('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
            pom_path = f"{project_root}/jeecg-boot/jeecg-boot-module/pom.xml"
            
            if not os.path.exists(pom_path):
                if logger:
                    logger.log_step("模块注册", "FAILED", f"模块注册表pom.xml不存在: {pom_path}")
                return False
            
            # 读取原始文件内容
            with open(pom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查模块是否已存在
            module_artifact_id = f"jeecg-module-{module_name}"
            if f"<module>{module_artifact_id}</module>" in content:
                if logger:
                    logger.log_step("模块注册", "SUCCESS", f"模块已存在于模块注册表中: {module_artifact_id}")
                return True
            
            # 查找 </modules> 标签的位置
            modules_end_pos = content.find('</modules>')
            if modules_end_pos == -1:
                modules_end_pos = content.find('</ns0:modules>')
            if modules_end_pos == -1:
                if logger:
                    logger.log_step("模块注册", "FAILED", "未找到modules节点")
                return False
            
            # 在 </modules> 前插入新模块
            new_module_entry = f"        <module>{module_artifact_id}</module>\n    "
            new_content = content[:modules_end_pos] + new_module_entry + content[modules_end_pos:]
            
            # 写回文件
            with open(pom_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            if logger:
                logger.log_step("模块注册", "SUCCESS", f"已添加模块到注册表: {module_artifact_id}")
            return True
            
        except Exception as e:
            if logger:
                logger.log_step("模块注册", "FAILED", f"更新模块注册表异常: {str(e)}")
            return False
    
    def _update_system_start_pom(self, module_name: str, logger: 'CodeGenLogger' = None) -> bool:
        """更新系统启动项目pom.xml添加新模块依赖"""
        try:
            if logger:
                logger.log_step("依赖配置", "IN_PROGRESS", "更新jeecg-system-start/pom.xml添加模块依赖")
            
            project_root = os.getenv('JEECG_PROJECT_ROOT', '/Users/admin/Work/Github/JeecgBoot')
            pom_path = f"{project_root}/jeecg-boot/jeecg-module-system/jeecg-system-start/pom.xml"
            
            if not os.path.exists(pom_path):
                if logger:
                    logger.log_step("依赖配置", "FAILED", f"启动项目pom.xml不存在: {pom_path}")
                return False
            
            # 读取原始文件内容
            with open(pom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查依赖是否已存在
            artifact_id = f"jeecg-module-{module_name}"
            if f"<artifactId>{artifact_id}</artifactId>" in content:
                if logger:
                    logger.log_step("依赖配置", "SUCCESS", f"依赖已存在: {artifact_id}")
                return True
            
            # 查找合适的位置插入新依赖（在 jeecg-system-biz 依赖之后）
            system_biz_pos = content.find('<artifactId>jeecg-system-biz</artifactId>')
            if system_biz_pos == -1:
                # 如果找不到 jeecg-system-biz，就在第一个 </dependency> 后插入
                first_dep_end = content.find('</dependency>')
                if first_dep_end == -1:
                    if logger:
                        logger.log_step("依赖配置", "FAILED", "无法找到合适的位置插入依赖")
                    return False
                insert_pos = first_dep_end + len('</dependency>')
            else:
                # 找到 jeecg-system-biz 依赖的结束位置
                dep_end_pos = content.find('</dependency>', system_biz_pos)
                if dep_end_pos == -1:
                    if logger:
                        logger.log_step("依赖配置", "FAILED", "无法找到依赖结束位置")
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
            
            if logger:
                logger.log_step("依赖配置", "SUCCESS", f"已添加依赖到启动项目: {artifact_id}")
            return True
            
        except Exception as e:
            if logger:
                logger.log_step("依赖配置", "FAILED", f"更新启动项目依赖异常: {str(e)}")
            return False

# ===============================================================================
# 统一执行器 - 核心入口
# ===============================================================================

class UnifiedTableExecutor:
    """统一表处理执行器 - 支持AI随机性"""
    
    def __init__(self, config_file: str = "Code_Gen_Config.properties"):
        self.api_manager = JeecgBootAPIManager(config_file)
        self.module_manager = ModuleManager(self.api_manager)
        self.frontend_migrator = FrontendMigrator(self.api_manager)
        self.placeholder_processor = PlaceholderProcessor(self.api_manager)
        self.sql_executor = DatabaseSQLExecutor(self.api_manager)
        self.permission_manager = PermissionManager(self.api_manager)
        self.validator = CodeGenValidator() if CodeGenValidator else None
        self.logger = None  # 初始化为None，在execute_table_workflow中创建
    
    def execute_table_workflow(self, config_data: Dict) -> bool:
        """统一的表处理入口 - 支持AI随机性执行"""
        try:
            print(f"\n{'='*80}")
            print("🚀 JeecgBoot 代码生成执行器 v2.0 启动")
            print(f"{'='*80}")
            
            # 1. 解析基本信息创建日志记录器
            module_info = self._extract_module_info(config_data)
            if not module_info:
                return False
            
            # 创建日志记录器
            self.logger = CodeGenLogger(module_info['module_name'], module_info['submodule_name'])
            self.logger.log_step("系统初始化", "SUCCESS", "代码生成执行器启动", f"模块: {module_info['module_name']}.{module_info['submodule_name']}")
            
            # 2. 配置验证
            if not self._validate_config(config_data):
                if self.logger:
                    self.logger.log_step("配置验证", "FAILED", "配置文件验证失败")
                    self.logger.print_workflow_summary()
                    self.logger.save_log_file()
                return False
            
            table_type = config_data.get('head', {}).get('tableType', 1)
            table_name = config_data.get('head', {}).get('tableName', '')
            
            print(f"📊 表信息: {table_name} (tableType={table_type})")
            print(f"📁 模块信息: {module_info['module_name']}.{module_info['submodule_name']}")
            
            # 3. 获取或创建哨兵
            sentinel = MasterSubTableSentinel(module_info['module_name'], module_info['submodule_name'])
            if not sentinel.get_or_create_sentinel(config_data):
                if self.logger:
                    self.logger.log_step("哨兵协调", "FAILED", "哨兵创建或获取失败")
                    self.logger.print_workflow_summary()
                    self.logger.save_log_file()
                return False
            
            self.logger.log_step("哨兵协调", "SUCCESS", "哨兵创建或获取成功")
            
            # 4. 模块准备工作流（确保Maven模块存在并配置完成）
            if not self.module_manager.ensure_module_exists(module_info['module_name'], self.logger):
                if self.logger:
                    self.logger.log_step("模块准备", "FAILED", "模块创建和配置失败")
                    # 模块准备失败不终止流程，继续执行（向后兼容）
                    print("⚠️ 模块准备失败，但继续执行后续工作流...")
            
            # 5. 执行基础工作流（所有表类型都需要）
            if not self._execute_basic_workflow(config_data):
                if self.logger:
                    self.logger.log_step("基础工作流", "FAILED", "API调用工作流执行失败")
                    self.logger.print_workflow_summary()
                    self.logger.save_log_file()
                return False
            
            # 6. 向哨兵报告完成状态
            form_id = self.api_manager.get_form_id(table_name)
            if not sentinel.report_completion(table_name, SentinelStatus.SYNCED, form_id):
                if self.logger:
                    self.logger.log_step("哨兵状态报告", "FAILED", "无法更新哨兵状态")
                    self.logger.print_workflow_summary()
                    self.logger.save_log_file()
                return False
            
            self.logger.log_step("哨兵状态报告", "SUCCESS", "表状态已同步到哨兵")
            
            # 7. 检查是否触发最终代码生成（根据表类型分别处理）
            if table_type == 2:  # 主表：等待所有子表完成后统一生成
                result = self._handle_master_table_completion(sentinel, config_data)
            elif table_type == 1:  # 独立表：直接生成完整代码
                result = self._execute_standalone_table_workflow(config_data)
            else:  # 子表：只等待主表触发
                self.logger.log_step("工作流完成", "SUCCESS", "子表工作流执行完成，等待主表触发代码生成")
                result = True
            
            self.logger.print_workflow_summary()
            self.logger.save_log_file()
            return result
                
        except Exception as e:
            if self.logger:
                self.logger.log_step("系统异常", "FAILED", f"执行器异常: {str(e)}")
                self.logger.print_workflow_summary()
                self.logger.save_log_file()
            print(f"❌ 执行器异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _validate_config(self, config_data: Dict) -> bool:
        """验证配置文件"""
        if not self.validator:
            if self.logger:
                self.logger.log_step("配置验证", "SKIPPED", "验证器未加载，跳过验证")
            return True
        
        # 实现基本的配置验证逻辑
        try:
            # 验证必需的配置项
            required_sections = ['head', 'metadata']
            for section in required_sections:
                if section not in config_data:
                    if self.logger:
                        self.logger.log_step("配置验证", "FAILED", f"缺少必需的配置段: {section}")
                    return False
            
            # 验证head段的必需字段
            head = config_data.get('head', {})
            required_head_fields = ['tableName', 'tableType']
            for field in required_head_fields:
                if not head.get(field):
                    if self.logger:
                        self.logger.log_step("配置验证", "FAILED", f"head段缺少必需字段: {field}")
                    return False
            
            # 验证metadata段的必需字段
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            required_meta_fields = ['module_name', 'submodule_name', 'business_entity']
            for field in required_meta_fields:
                if not generation_info.get(field):
                    if self.logger:
                        self.logger.log_step("配置验证", "FAILED", f"metadata.generation_info缺少必需字段: {field}")
                    return False
            
            # 验证表类型的有效性
            table_type = head.get('tableType')
            if table_type not in [1, 2, 3]:
                if self.logger:
                    self.logger.log_step("配置验证", "FAILED", f"无效的表类型: {table_type}，应为1(独立表)、2(主表)或3(子表)")
                return False
            
            if self.logger:
                self.logger.log_step("配置验证", "SUCCESS", "配置文件验证通过")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log_step("配置验证", "FAILED", f"配置验证异常: {str(e)}")
            return False
    
    def _extract_module_info(self, config_data: Dict) -> Optional[Dict]:
        """提取模块信息"""
        try:
            # 方法1: 从metadata获取
            metadata = config_data.get('metadata', {})
            generation_info = metadata.get('generation_info', {})
            
            module_name = generation_info.get('module_name')
            submodule_name = generation_info.get('submodule_name')
            
            if module_name and submodule_name:
                return {
                    'module_name': module_name,
                    'submodule_name': submodule_name,
                    'source': 'metadata'
                }
            
            # 方法2: 从表名解析 - 支持3段式命名
            table_name = config_data.get('head', {}).get('tableName', '')
            parts = table_name.split('_')
            if len(parts) >= 3:
                return {
                    'module_name': parts[0],  # 第一段是模块名
                    'submodule_name': parts[1],  # 第二段是子模块名
                    'source': 'table_name'
                }
            
            print("❌ 无法提取模块信息")
            return None
            
        except Exception as e:
            print(f"❌ 模块信息提取异常: {e}")
            return None
    
    def _execute_basic_workflow(self, config_data: Dict) -> bool:
        """执行基础工作流：登录 → 创建表单 → 查询验证 → 数据库同步"""
        
        # 1. 登录
        self.logger.log_step("用户登录", "IN_PROGRESS", "开始JeecgBoot API认证")
        if not self.api_manager.login():
            self.logger.log_step("用户登录", "FAILED", "API登录认证失败")
            return False
        self.logger.log_step("用户登录", "SUCCESS", "API登录认证成功")
        
        # 2. 创建表单
        self.logger.log_step("创建表单", "IN_PROGRESS", "调用addAll API创建在线表单")
        form_id = self.api_manager.create_form(config_data)
        if not form_id:
            self.logger.log_step("创建表单", "FAILED", "表单创建失败")
            return False
        self.logger.log_step("创建表单", "SUCCESS", f"表单创建成功，ID: {form_id}")
        
        # 3. 查询验证
        table_name = config_data.get('head', {}).get('tableName', '')
        self.logger.log_step("表单验证", "IN_PROGRESS", f"验证表单 {table_name} 是否正确创建")
        verified_form_id = self.api_manager.get_form_id(table_name)
        if not verified_form_id:
            self.logger.log_step("表单验证", "FAILED", "表单查询验证失败")
            return False
        self.logger.log_step("表单验证", "SUCCESS", f"表单验证通过，ID: {verified_form_id}")
        
        # 4. 数据库同步
        self.logger.log_step("数据库同步", "IN_PROGRESS", "同步表单结构到数据库")
        if not self.api_manager.sync_database(verified_form_id):
            self.logger.log_step("数据库同步", "FAILED", "数据库同步失败")
            return False
        self.logger.log_step("数据库同步", "SUCCESS", "数据库同步完成")
        
        return True
    
    def _handle_master_table_completion(self, sentinel: MasterSubTableSentinel, main_config: Dict) -> bool:
        """处理主表完成逻辑"""
        
        # 检查所有表是否完成
        if sentinel.is_all_completed():
            print("🎯 所有表已完成，开始统一代码生成...")
            return self._execute_final_workflow(sentinel, main_config)
        else:
            print("⏳ 主表等待子表完成...")
            
            # 显示等待状态
            tables = sentinel.sentinel_data.get('tables', {})
            for table_name, table_info in tables.items():
                status = table_info.get('status', 'unknown')
                table_type = table_info.get('table_type', 0)
                type_desc = {1: '独立表', 2: '主表', 3: '子表'}.get(table_type, '未知')
                print(f"   {table_name} ({type_desc}): {status}")
            
            return True
    
    def _execute_final_workflow(self, sentinel: MasterSubTableSentinel, main_config: Dict) -> bool:
        """执行最终工作流：统一代码生成 → 后续处理"""
        try:
            # 获取主表信息
            main_table_info = sentinel.get_main_table_info()
            if not main_table_info:
                self.logger.log_step("最终工作流", "FAILED", "未找到主表信息")
                return False
            
            form_id = main_table_info.get('form_id')
            if not form_id:
                self.logger.log_step("最终工作流", "FAILED", "主表form_id缺失")
                return False
            
            # 1. 统一代码生成
            self.logger.log_step("代码生成", "IN_PROGRESS", "开始统一代码生成")
            if not self.api_manager.generate_code(form_id, main_config):
                self.logger.log_step("代码生成", "FAILED", "代码生成API调用失败")
                return False
            self.logger.log_step("代码生成", "SUCCESS", "代码生成完成")
            
            # 2. 后续处理流程
            self.logger.log_step("后续处理开始", "IN_PROGRESS", "开始执行后续处理环节")
            
            # 占位变量处理 - 最重要，先执行
            success_count = 0
            total_count = 4
            
            if self.placeholder_processor.process_placeholder_variables(main_config, self.logger):
                success_count += 1
            else:
                # 占位变量处理失败不终止，继续执行其他环节
                pass
            
            # 前端代码迁移
            if self.frontend_migrator.migrate_frontend_code(main_config, self.logger):
                success_count += 1
            
            # SQL脚本执行
            if self.sql_executor.execute_permission_sql(main_config, self.logger):
                success_count += 1
            
            # 菜单权限授权
            if self.permission_manager.grant_permissions(main_config, self.logger):
                success_count += 1
            
            # 3. 标记完成
            sentinel.report_completion(main_table_info['table_name'], SentinelStatus.CODE_GENERATED)
            
            # 记录整体结果
            # 根据成功率决定最终状态
            if success_count == total_count:
                self.logger.log_step("工作流完成", "SUCCESS", f"主子表完整工作流执行成功，{success_count}/{total_count} 个环节成功")
            elif success_count >= 2:  # 至少2个环节成功才算部分成功
                self.logger.log_step("工作流完成", "SUCCESS", f"主子表工作流执行完成，{success_count}/{total_count} 个环节成功，部分环节可能需要手动处理")
            else:
                self.logger.log_step("工作流完成", "FAILED", f"主子表工作流执行失败，仅{success_count}/{total_count} 个环节成功")
                return False  # 成功率太低，标记为失败
            
            return True
            
        except Exception as e:
            self.logger.log_step("最终工作流", "FAILED", f"执行异常: {str(e)}")
            print(f"❌ 最终工作流执行异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _execute_standalone_table_workflow(self, config_data: Dict) -> bool:
        """执行独立表完整工作流：代码生成 → 后续处理"""
        try:
            table_name = config_data.get('head', {}).get('tableName', '')
            form_id = self.api_manager.get_form_id(table_name)
            
            if not form_id:
                self.logger.log_step("独立表代码生成", "FAILED", "无法获取表单ID")
                return False
            
            # 1. 代码生成
            self.logger.log_step("代码生成", "IN_PROGRESS", "开始独立表代码生成")
            if not self.api_manager.generate_code(form_id, config_data):
                self.logger.log_step("代码生成", "FAILED", "代码生成API调用失败")
                return False
            self.logger.log_step("代码生成", "SUCCESS", "代码生成完成")
            
            # 2. 后续处理流程（复用主子表的完整逻辑）
            self.logger.log_step("后续处理开始", "IN_PROGRESS", "开始执行后续处理环节")
            
            # 占位变量处理 - 最重要，先执行
            success_count = 0
            total_count = 4
            
            if self.placeholder_processor.process_placeholder_variables(config_data, self.logger):
                success_count += 1
            else:
                # 占位变量处理失败不终止，继续执行其他环节
                pass
            
            # 前端代码迁移
            if self.frontend_migrator.migrate_frontend_code(config_data, self.logger):
                success_count += 1
            
            # SQL脚本执行
            if self.sql_executor.execute_permission_sql(config_data, self.logger):
                success_count += 1
            
            # 菜单权限授权
            if self.permission_manager.grant_permissions(config_data, self.logger):
                success_count += 1
            
            # 3. 记录整体结果
            # 根据成功率决定最终状态
            if success_count == total_count:
                self.logger.log_step("工作流完成", "SUCCESS", f"独立表完整工作流执行成功，{success_count}/{total_count} 个环节成功")
            elif success_count >= 2:  # 至少2个环节成功才算部分成功
                self.logger.log_step("工作流完成", "SUCCESS", f"独立表工作流执行完成，{success_count}/{total_count} 个环节成功，部分环节可能需要手动处理")
            else:
                self.logger.log_step("工作流完成", "FAILED", f"独立表工作流执行失败，仅{success_count}/{total_count} 个环节成功")
                return False  # 成功率太低，标记为失败
            
            return True
            
        except Exception as e:
            self.logger.log_step("独立表工作流", "FAILED", f"执行异常: {str(e)}")
            print(f"❌ 独立表工作流执行异常: {e}")
            import traceback
            traceback.print_exc()
            return False

# ===============================================================================
# 独立测试和验证函数
# ===============================================================================

def test_menu_permission_sql_execution():
    """
    测试菜单权限SQL执行功能
    这是一个独立的测试函数，可以用来验证功能是否正常
    """
    print("🗺  开始测试菜单权限SQL执行功能...")
    
    try:
        # 模拟测试参数
        test_module = "finance"
        test_submodule = "invoice" 
        test_entity = "InvoiceHeader"
        
        # 创建测试配置管理器
        config_manager = JeecgBootAPIManager()
        
        # 调用独立函数
        result = execute_menu_permission_sql(
            module_name=test_module,
            submodule_name=test_submodule,
            business_entity=test_entity,
            config_manager=config_manager,
            logger=None
        )
        
        # 检查结果
        print(f"✅ 测试结果: {result['success']}")
        print(f"   执行文件: {result['executed_files']}")
        print(f"   总语句数: {result['total_statements']}")
        print(f"   影响行数: {result['total_affected_rows']}")
        print(f"   执行时间: {result['execution_time']:.2f}秒")
        
        if result['error_message']:
            print(f"   错误信息: {result['error_message']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_config_data(module_name: str, submodule_name: str, business_entity: str, table_type: int = 1) -> Dict:
    """
    创建测试配置数据
    
    Args:
        module_name: 模块名
        submodule_name: 子模块名  
        business_entity: 业务实体名
        table_type: 表类型 (1=独立表, 2=主表, 3=子表)
    
    Returns:
        Dict: 测试配置数据
    """
    table_name = f"{module_name}_{submodule_name}_{business_entity.lower()}"
    
    return {
        "head": {
            "tableName": table_name,
            "tableType": table_type,
            "business_entity": business_entity,
            "tableTxt": f"{business_entity}管理"
        },
        "metadata": {
            "generation_info": {
                "module_name": module_name,
                "submodule_name": submodule_name,
                "business_entity": business_entity
            }
        },
        "subList": [] if table_type != 2 else [
            {
                "tableName": f"{table_name}_detail",
                "entityName": f"{business_entity}Detail"
            }
        ]
    }

def test_complete_workflow():
    """
    测试完整的代码生成工作流
    """
    print("🏃 开始测试完整工作流...")
    
    try:
        # 创建测试配置
        test_config = create_test_config_data(
            module_name="test",
            submodule_name="demo", 
            business_entity="TestEntity",
            table_type=1
        )
        
        print(f"📄 测试配置: {test_config['head']['tableName']}")
        
        # 创建执行器
        executor = UnifiedTableExecutor()
        
        # 模拟执行 (不连接真实数据库)
        print("🔍 模拟模块信息提取...")
        module_info = executor._extract_module_info(test_config)
        
        if module_info:
            print(f"✅ 模块信息提取成功: {module_info}")
        else:
            print("❌ 模块信息提取失败")
            return False
        
        print("🔍 模拟配置验证...")
        validation_result = executor._validate_config(test_config)
        
        if validation_result:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
            return False
            
        print("✅ 测试完整工作流通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

# ===============================================================================
# 向后兼容接口 - 保持原有调用方式
# ===============================================================================

def main():
    """主入口函数 - 支持测试模式和正常执行模式"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  正常执行: python Code_Gen_Execute.py <config_file.json>")
        print("  测试模式: python Code_Gen_Execute.py --test")
        print("  SQL独立测试: python Code_Gen_Execute.py --test-sql <module> <submodule> <entity>")
        sys.exit(1)
    
    # 检查是否为测试模式
    if sys.argv[1] == "--test":
        print("🧪 进入测试模式...")
        success = test_complete_workflow()
        sys.exit(0 if success else 1)
    
    elif sys.argv[1] == "--test-sql":
        if len(sys.argv) < 5:
            print("使用方法: python Code_Gen_Execute.py --test-sql <module> <submodule> <entity>")
            print("例如: python Code_Gen_Execute.py --test-sql finance invoice InvoiceHeader")
            sys.exit(1)
        
        module = sys.argv[2]
        submodule = sys.argv[3] 
        entity = sys.argv[4]
        
        print(f"🗺  进入SQL独立测试模式: {module}.{submodule}.{entity}")
        
        try:
            config_manager = JeecgBootAPIManager()
            result = execute_menu_permission_sql(
                module_name=module,
                submodule_name=submodule,
                business_entity=entity,
                config_manager=config_manager,
                logger=None
            )
            
            print("\n📈 执行结果报告:")
            success_icon = '\u2705 成功' if result['success'] else '\u274c 失败'
            print(f"   成功状态: {success_icon}")
            print(f"   执行文件: {result['executed_files']}")
            print(f"   执行语句: {result['total_statements']} 条")
            print(f"   影响行数: {result['total_affected_rows']} 行")
            print(f"   执行时间: {result['execution_time']:.2f} 秒")
            
            if result['error_message']:
                print(f"   错误信息: {result['error_message']}")
                
            sys.exit(0 if result['success'] else 1)
            
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # 正常执行模式
    config_file = sys.argv[1]
    
    try:
        # 读取配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 创建执行器并执行
        executor = UnifiedTableExecutor()
        success = executor.execute_table_workflow(config_data)
        
        if success:
            print("\n✅ 代码生成执行成功!")
            sys.exit(0)
        else:
            print("\n❌ 代码生成执行失败!")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"❌ 配置文件不存在: {config_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件JSON格式错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()