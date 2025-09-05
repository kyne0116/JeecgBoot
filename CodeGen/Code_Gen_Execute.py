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
import glob
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
from abc import ABC, abstractmethod
from enum import Enum

# 导入验证器
try:
    from Code_Gen_Validator import CodeGenValidator
except ImportError:
    print("警告: 无法导入Code_Gen_Validator，将跳过配置验证")
    CodeGenValidator = None

# ===== 新架构组件 =====

class ScenarioType(Enum):
    """场景类型枚举"""
    INDEPENDENT_TABLE = "independent_table"
    MAIN_SUB_TABLES = "main_sub_tables"

class APICallStrategy(ABC):
    """API调用策略抽象基类"""
    
    @abstractmethod
    def should_generate_code(self, table_type: int) -> bool:
        """判断是否应该生成代码"""
        pass

class IndependentTableStrategy(APICallStrategy):
    """独立表API调用策略"""
    
    def should_generate_code(self, table_type: int) -> bool:
        return table_type == 1  # 独立表生成代码

class MainSubTablesStrategy(APICallStrategy):
    """主子表API调用策略"""
    
    def should_generate_code(self, table_type: int) -> bool:
        return table_type == 2  # 只有主表生成代码

class ConfigurationSet:
    """配置集合管理器"""
    
    def __init__(self, configs: List[Dict]):
        self.configs = configs
        self.main_config: Optional[Dict] = None
        self.sub_configs: List[Dict] = []
        self.scenario: ScenarioType = self._detect_scenario()
        self._organize_configs()
        
    def _detect_scenario(self) -> ScenarioType:
        """自动检测场景类型"""
        table_types = [cfg.get('head', {}).get('tableType', 1) for cfg in self.configs]
        
        if 2 in table_types and 3 in table_types:  # 有主表和子表
            return ScenarioType.MAIN_SUB_TABLES
        elif len(table_types) == 1 and table_types[0] == 1:  # 单个独立表
            return ScenarioType.INDEPENDENT_TABLE
        else:
            raise ValueError(f"无法识别的场景类型: {table_types}")
    
    def _organize_configs(self):
        """组织配置：分离主表和子表配置"""
        for config in self.configs:
            table_type = config.get('head', {}).get('tableType', 1)
            if table_type == 2:  # 主表
                self.main_config = config
            elif table_type == 3:  # 子表
                self.sub_configs.append(config)

class ExecutionTracker:
    """8个子环节执行状态跟踪器"""
    
    def __init__(self):
        self.steps = {
            "Maven模块创建": "Pending",
            "表单创建同步": "Pending", 
            "代码生成": "Pending",
            "前端迁移": "Pending",
            "占位处理": "Pending",
            "SQL执行": "Pending",
            "权限授权": "Pending",
            "编译验证": "Pending"
        }
        self.generated_files = {
            "backend_files": [],
            "frontend_files": [],
            "database_files": []
        }
        
    def set_step_status(self, step: str, status: str):
        """设置步骤状态：Pass/Fail/Skip"""
        if step in self.steps:
            self.steps[step] = status
            
    def add_generated_file(self, file_type: str, file_path: str):
        """添加生成的文件"""
        if file_type in self.generated_files:
            self.generated_files[file_type].append(file_path)
            
    def get_summary(self) -> str:
        """获取执行状态汇总 - 基于历史版本的严谨格式"""
        summary = "📋 **执行状态汇总**\n"
        summary += "=" * 50 + "\n"
        for step, status in self.steps.items():
            # 使用历史版本的严谨格式
            if status == "Pass":
                status_display = "[OK] Pass"
                emoji = "✅"
            elif status == "Fail":
                status_display = "[FAIL] Fail"
                emoji = "❌"
            elif status == "Skip":
                status_display = "[SKIP] Skip"
                emoji = "⏭️"
            else:  # Pending
                status_display = "[PENDING] Pending"
                emoji = "⏳"
            
            summary += f"{emoji} {step}: {status_display}\n"
        return summary
        
    def get_files_summary(self) -> str:
        """获取生成文件汇总"""
        summary = "\n📁 **生成的核心文件**\n"
        summary += "=" * 50 + "\n"
        
        if self.generated_files["backend_files"]:
            summary += f"🔧 后端代码文件: {len(self.generated_files['backend_files'])} 个\n"
            for f in self.generated_files["backend_files"][:5]:  # 只显示前5个
                summary += f"   - {f}\n"
                
        if self.generated_files["frontend_files"]:
            summary += f"🖥️ 前端代码文件: {len(self.generated_files['frontend_files'])} 个\n" 
            for f in self.generated_files["frontend_files"][:5]:
                summary += f"   - {f}\n"
                
        if self.generated_files["database_files"]:
            summary += f"🗄️ 数据库脚本: {len(self.generated_files['database_files'])} 个\n"
            for f in self.generated_files["database_files"]:
                summary += f"   - {f}\n"
                
        return summary
        
    def get_final_result(self) -> str:
        """获取最终执行结果"""
        failed_steps = [step for step, status in self.steps.items() if status == "Fail"]
        if failed_steps:
            return "Fail"
        else:
            return "Pass"
    
    def get_detailed_statistics(self) -> str:
        """获取详细的执行统计 - 基于历史版本的严谨统计机制"""
        total_steps = len(self.steps)
        passed_steps = len([s for s in self.steps.values() if s == "Pass"])
        failed_steps = len([s for s in self.steps.values() if s == "Fail"])
        skipped_steps = len([s for s in self.steps.values() if s == "Skip"]) 
        pending_steps = len([s for s in self.steps.values() if s == "Pending"])
        
        success_rate = (passed_steps / total_steps * 100) if total_steps > 0 else 0
        
        stats = "\n📊 **执行统计详情**\n"
        stats += "=" * 50 + "\n"
        stats += f"总执行步骤: {total_steps} 个\n"
        stats += f"✅ 成功完成: {passed_steps} 个\n"
        
        if failed_steps > 0:
            stats += f"❌ 执行失败: {failed_steps} 个\n"
        if skipped_steps > 0:
            stats += f"⏭️ 跳过执行: {skipped_steps} 个\n"  
        if pending_steps > 0:
            stats += f"⏳ 未执行: {pending_steps} 个\n"
            
        stats += f"📈 成功率: {success_rate:.1f}%\n"
        
        # 详细的失败步骤列表（如果有）
        failed_step_names = [name for name, status in self.steps.items() if status == "Fail"]
        if failed_step_names:
            stats += f"\n❌ **失败的步骤详情**:\n"
            for step_name in failed_step_names:
                stats += f"   - {step_name}\n"
        
        return stats

class TransactionManager:
    """事务管理器 - 确保原子性操作"""
    
    def __init__(self):
        self.created_forms: List[str] = []  # 跟踪创建的表单ID
        self.created_files: List[str] = []  # 跟踪生成的文件
        self.is_active = False
        self.executor = None  # 将在使用时设置
        
    def __enter__(self):
        self.is_active = True
        self.created_forms.clear()
        self.created_files.clear()
        print("🔄 开始事务")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 发生异常，执行回滚
            self._rollback()
        else:
            # 成功完成，提交事务
            self._commit()
        self.is_active = False
        
    def add_form(self, form_id: str):
        """添加已创建的表单ID到事务中"""
        if form_id:
            self.created_forms.append(form_id)
            
    def add_file(self, file_path: str):
        """添加已创建的文件到事务中"""
        if file_path and os.path.exists(file_path):
            self.created_files.append(file_path)
            
    def _commit(self):
        """提交事务 - 确认所有操作"""
        print(f"✅ 事务提交成功")
        print(f"   创建表单: {len(self.created_forms)} 个")
        print(f"   生成文件: {len(self.created_files)} 个")
        
    def _rollback(self):
        """回滚事务 - 清理所有已创建的资源"""
        print("🔴 事务回滚，清理资源...")
        
        # 删除已创建的表单
        for form_id in reversed(self.created_forms):
            try:
                if self.executor:
                    self.executor.delete_forms([form_id])
                    print(f"   删除表单: {form_id}")
            except Exception as e:
                print(f"   ⚠️ 删除表单失败 {form_id}: {e}")
        
        # 删除已生成的文件
        for file_path in reversed(self.created_files):
            try:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                    print(f"   删除文件: {file_path}")
            except Exception as e:
                print(f"   ⚠️ 删除文件失败 {file_path}: {e}")

class WorkflowOrchestrator:
    """工作流编排器 - 核心调度器"""
    
    def __init__(self, executor: 'CodeGenExecutor'):
        self.executor = executor
        self.transaction_manager = TransactionManager()
        self.transaction_manager.executor = executor
        self.tracker = ExecutionTracker()
        
    def execute(self, config_set: ConfigurationSet) -> bool:
        """执行完整工作流"""
        strategy = self._select_strategy(config_set.scenario)
        
        try:
            with self.transaction_manager:
                success = self._execute_with_strategy(config_set, strategy)
                
                # 输出最终结果汇总
                self._print_final_summary(success)
                return success
                
        except Exception as e:
            print(f"❌ 工作流执行失败: {e}")
            self._print_final_summary(False)
            return False
    
    def _select_strategy(self, scenario: ScenarioType) -> APICallStrategy:
        """选择执行策略"""
        if scenario == ScenarioType.INDEPENDENT_TABLE:
            return IndependentTableStrategy()
        elif scenario == ScenarioType.MAIN_SUB_TABLES:
            return MainSubTablesStrategy()
        else:
            raise ValueError(f"不支持的场景类型: {scenario}")
    
    def _execute_with_strategy(self, config_set: ConfigurationSet, 
                              strategy: APICallStrategy) -> bool:
        """使用指定策略执行工作流"""
        if isinstance(strategy, IndependentTableStrategy):
            return self._execute_independent_table(config_set)
        elif isinstance(strategy, MainSubTablesStrategy):
            return self._execute_main_sub_tables(config_set)
        
    def _execute_independent_table(self, config_set: ConfigurationSet) -> bool:
        """执行独立表工作流"""
        config = config_set.configs[0]
        table_name = config.get('head', {}).get('tableName')
        print(f"🔧 执行独立表工作流: {table_name}")
        
        # 1. Maven模块创建
        module_name = self.executor._extract_module_name(config_set)
        if self.executor.ensure_module_exists(module_name):
            self.tracker.set_step_status("Maven模块创建", "Pass")
        else:
            self.tracker.set_step_status("Maven模块创建", "Fail")
            return False
        
        # 2. 创建表单和数据库同步
        form_id = self.executor.create_form(config)
        if not form_id:
            self.tracker.set_step_status("表单创建同步", "Fail")
            return False
        self.transaction_manager.add_form(form_id)
        
        if not self.executor.sync_database(form_id):
            self.tracker.set_step_status("表单创建同步", "Fail")
            return False
        self.tracker.set_step_status("表单创建同步", "Pass")
            
        # 3. 生成代码
        if not self.executor.generate_code(form_id, config):
            self.tracker.set_step_status("代码生成", "Fail")
            return False
        self.tracker.set_step_status("代码生成", "Pass")
            
        # 4. 前端代码迁移
        if not self.executor.migrate_frontend_code(config):
            self.tracker.set_step_status("前端迁移", "Fail")
            return False
        self.tracker.set_step_status("前端迁移", "Pass")
        
        # 5. 占位变量处理
        if not self.executor.process_placeholder_variables(config):
            self.tracker.set_step_status("占位处理", "Fail")
            return False
        self.tracker.set_step_status("占位处理", "Pass")
        
        # 6. 执行权限SQL
        if not self.executor.execute_permission_sql(config):
            self.tracker.set_step_status("SQL执行", "Fail")
            return False
        self.tracker.set_step_status("SQL执行", "Pass")
        
        # 7. 权限授权
        if not self.executor.grant_permissions(config):
            self.tracker.set_step_status("权限授权", "Fail")
            return False
        self.tracker.set_step_status("权限授权", "Pass")
        
        # 8. 编译验证（可选）
        compile_enabled = self.executor.get_config_value('compilation', 'enabled', 'false').lower() == 'true'
        if compile_enabled:
            if self.executor.verify_compilation(module_name):
                self.tracker.set_step_status("编译验证", "Pass")
            else:
                self.tracker.set_step_status("编译验证", "Fail")
                return False
        else:
            self.tracker.set_step_status("编译验证", "Skip")
        
        return True
    
    def _execute_main_sub_tables(self, config_set: ConfigurationSet) -> bool:
        """执行主子表工作流"""
        print(f"🔧 执行主子表工作流: {len(config_set.sub_configs)} 个子表 + 1 个主表")
        
        # 1. 先处理所有子表（只创建表单和同步数据库）
        for i, sub_config in enumerate(config_set.sub_configs, 1):
            table_name = sub_config.get('head', {}).get('tableName')
            print(f"   处理子表 {i}/{len(config_set.sub_configs)}: {table_name}")
            
            form_id = self.executor.create_form(sub_config)
            if not form_id:
                return False
            self.transaction_manager.add_form(form_id)
            
            if not self.executor.sync_database(form_id):
                return False
        
        # 2. 处理主表（完整流程）
        main_config = config_set.main_config
        if not main_config:
            print("❌ 未找到主表配置")
            return False
            
        main_table_name = main_config.get('head', {}).get('tableName')
        print(f"   处理主表: {main_table_name}")
        
        form_id = self.executor.create_form(main_config)
        if not form_id:
            return False
        self.transaction_manager.add_form(form_id)
        
        if not self.executor.sync_database(form_id):
            return False
            
        # 只有主表生成代码
        if not self.executor.generate_code(form_id, main_config):
            return False
        
        # 3. 后续处理（基于主表配置）
        self.executor.migrate_frontend_code(main_config)
        self.executor.process_placeholder_variables(main_config)
        
        return True
    
    def _print_final_summary(self, success: bool):
        """输出最终执行结果汇总"""
        print("\n" + "=" * 80)
        print("🎯 **JeecgBoot 代码生成工作流执行结果**")
        print("=" * 80)
        
        # 1. 执行状态汇总
        print(self.tracker.get_summary())
        
        # 2. 详细执行统计 - 基于历史版本的严谨机制
        print(self.tracker.get_detailed_statistics())
        
        # 3. 生成的核心文件
        print(self.tracker.get_files_summary())
        
        # 4. Maven编译提醒（如果成功）
        if success and self.tracker.get_final_result() == "Pass":
            print("\n⚠️ **Maven编译提醒**")
            print("=" * 50)
            print("请手动执行以下命令完成编译:")
            print("cd jeecg-boot")
            print("mvn clean compile -DskipTests")
            
        # 5. 总体执行结果
        final_result = self.tracker.get_final_result() if success else "Fail"
        print(f"\n🏆 **总体执行结果**: {final_result}")
        print("=" * 80)

class CodeGenExecutor:
    """JeecgBoot代码生成执行器 - 重构为纯净统一架构"""
    
    def __init__(self, config_file: str = None):
        """初始化执行器"""
        if config_file is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(current_dir, "Code_Gen_Config.properties")
        
        self.config_file = config_file
        self.config = self._load_config()
        self.session = requests.Session()
        self.token = None
        self.recorded_permission_ids = []  # 存储SQL执行步骤记录的权限ID
        
        # 初始化验证器
        if CodeGenValidator:
            self.validator = CodeGenValidator()
        else:
            self.validator = None
        
        # 新增组件
        self.orchestrator = WorkflowOrchestrator(self)
    
    # ===== 新的统一API =====
    
    def execute_code_generation(self, inputs: Union[str, List[str], Dict, List[Dict]]) -> bool:
        """
        统一的代码生成入口 - 自动处理所有场景
        
        Args:
            inputs: 可以是以下任意类型：
                - str: 单个JSON配置文件路径
                - List[str]: 多个JSON配置文件路径
                - Dict: 单个配置字典
                - List[Dict]: 多个配置字典
                
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        try:
            # 统一输入格式为配置列表
            configs = self._normalize_inputs(inputs)
            
            # 创建配置集合（自动场景识别）
            config_set = ConfigurationSet(configs)
            print(f"🎯 检测到场景类型: {config_set.scenario.value}")
            
            # 确保模块存在
            module_name = self._extract_module_name(config_set)
            if not self.ensure_module_exists(module_name):
                print("⚠️ 模块创建失败，但继续执行代码生成...")
            
            # 登录认证
            if not self.login():
                return False
            
            # 执行工作流（自动选择策略）
            return self.orchestrator.execute(config_set)
            
        except Exception as e:
            print(f"❌ 代码生成失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _normalize_inputs(self, inputs) -> List[Dict]:
        """将各种输入格式统一为配置字典列表"""
        if isinstance(inputs, str):
            # 单个文件路径
            with open(inputs, 'r', encoding='utf-8') as f:
                return [json.load(f)]
                
        elif isinstance(inputs, list) and all(isinstance(x, str) for x in inputs):
            # 多个文件路径
            configs = []
            for file_path in inputs:
                with open(file_path, 'r', encoding='utf-8') as f:
                    configs.append(json.load(f))
            return configs
            
        elif isinstance(inputs, dict):
            # 单个配置字典
            return [inputs]
            
        elif isinstance(inputs, list) and all(isinstance(x, dict) for x in inputs):
            # 多个配置字典
            return inputs
            
        else:
            raise ValueError(f"不支持的输入类型: {type(inputs)}")
    
    def _extract_module_name(self, config_set: ConfigurationSet) -> str:
        """从配置集合中提取模块名"""
        sample_config = config_set.configs[0]
        table_name = sample_config.get('head', {}).get('tableName', '')
        if table_name.startswith('us_'):
            return table_name.split('_')[1]
        raise ValueError(f"无法从表名中提取模块名: {table_name}")
    
    def _load_required_environment_variables(self) -> Dict[Tuple[str, str], str]:
        """加载8个必需的环境变量，缺失时直接退出程序"""
        required_env_vars = {
            'JEECG_PROJECT_ROOT': ('project', 'path_prefix'),
            'JEECG_BASE_URL': ('server', 'base_url'),
            'JEECG_USERNAME': ('server', 'username'), 
            'JEECG_PASSWORD': ('server', 'password'),
            'JEECG_DATABASE_TYPE': ('database_execution', 'type'),
            'JEECG_DATABASE_URL': ('database_execution', 'url'),
            'JEECG_DATABASE_USERNAME': ('database_execution', 'username'),
            'JEECG_DATABASE_PASSWORD': ('database_execution', 'password')
        }
        
        missing_vars = []
        env_values = {}
        
        for env_var, (section, key) in required_env_vars.items():
            env_value = os.getenv(env_var)
            if not env_value:
                missing_vars.append(env_var)
            else:
                env_values[(section, key)] = env_value
        
        if missing_vars:
            print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
            print("程序退出。")
            sys.exit(1)
        
        return env_values

    def _load_config(self) -> configparser.ConfigParser:
        """加载配置文件并集成环境变量"""
        config = configparser.ConfigParser()
        try:
            config.read(self.config_file, encoding='utf-8')
            
            # 加载必需的环境变量
            env_values = self._load_required_environment_variables()
            
            # 将环境变量值集成到config中
            for (section, key), value in env_values.items():
                if not config.has_section(section):
                    config.add_section(section)
                config.set(section, key, value)
                
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
        max_attempts = int(self.get_config_value('api_error_handling', 'retry_max_attempts', '3'))
        delay_seconds = int(self.get_config_value('api_error_handling', 'retry_delay_seconds', '2'))

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
        login_url = self.get_config_value('api', 'login_url')
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
    
    # ===== 原有execute_workflow方法已被新架构替代 =====
    
    def create_form(self, config_data: Dict) -> Optional[str]:
        """创建在线表单"""
        url = self.get_config_value('api', 'form_addall_url')
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
        url = self.get_config_value('api', 'form_list_url')
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
        """同步数据库 - 使用正确的API路径格式"""
        base_url = self.get_config_value('server', 'base_url')
        base_path = self.get_config_value('api', 'database_sync_base_path', '/online/cgform/api/doDbSynch')
        
        if not base_url:
            print("❌ 缺少服务器基础URL配置")
            return False
        
        try:
            # 使用配置文件中的路径构建完整URL：{base_url}{base_path}/{form_id}/normal
            url = f"{base_url}{base_path}/{form_id}/normal"
            print(f"🔗 数据库同步URL: {url}")
            
            response = self.session.post(url, timeout=60)
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
        url = self.get_config_value('api', 'codegen_generate_url')
        if not url:
            print("❌ 缺少代码生成API配置")
            return False
        
        # 构建代码生成参数
        base_path = self.get_config_value('project', 'path_prefix')
        business_entity = config_data.get('head', {}).get('business_entity')
        table_type = config_data.get('head', {}).get('tableType', 1)
        
        # 解析表名获取模块信息
        table_name = config_data.get('head', {}).get('tableName', '')
        if table_name.startswith('us_'):
            parts = table_name.split('_')
            if len(parts) >= 4:
                module_name = parts[1]
                # 构建正确的模块路径：/base_path/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}
                project_path = f"{base_path}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}"
                print(f"🎯 代码生成路径: {project_path}")
            else:
                project_path = base_path
                print(f"⚠️ 表名格式异常，使用默认路径: {project_path}")
        else:
            project_path = base_path
            print(f"⚠️ 非标准表名，使用默认路径: {project_path}")
        
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

        # 基于历史版本的完整参数构建
        table_description = config_data.get('head', {}).get('tableTxt', '')
        
        # 解析模块信息（重用前面的解析结果）
        if table_name.startswith('us_'):
            parts = table_name.split('_')
            if len(parts) >= 4:
                module_name = parts[1]
                submodule_name = parts[2] 
                base_package = f"org.jeecg.modules.{module_name}"
            else:
                base_package = "org.jeecg.modules.system"
                submodule_name = "system"
        else:
            base_package = "org.jeecg.modules.system" 
            submodule_name = "system"
        
        data = {
            "projectPath": project_path,
            "jspMode": jsp_mode,
            "ftlDescription": table_description,
            "jformType": jform_type,
            "tableName_tmp": table_name,
            "entityName": business_entity,
            "entityPackage": submodule_name,
            "bussiPackage": base_package,
            "packageStyle": package_style,
            "vueStyle": vue_style,
            "codeTypes": "controller,service,dao,mapper,entity,vue",
            "code": form_id,
            "tableName": table_name
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
    
    def migrate_frontend_code(self, config_data: Dict) -> bool:
        """迁移前端代码 - 基于历史版本的高级路径解析和容错机制"""
        try:
            # 获取前端迁移配置
            migration_config = {}
            if hasattr(self.config, 'has_section') and self.config.has_section('frontend_migration'):
                migration_config = dict(self.config['frontend_migration'])
                # 转换字符串类型的布尔值
                if 'enabled' in migration_config:
                    migration_config['enabled'] = migration_config['enabled'].lower() == 'true'
                if 'cleanup_source' in migration_config:
                    migration_config['cleanup_source'] = migration_config['cleanup_source'].lower() == 'true'
            
            if not migration_config.get('enabled', True):
                print("⏭️ 前端代码迁移功能已禁用，跳过迁移步骤")
                return True
            
            print(f"\n{'='*50}")
            print("[FOLDER] 开始前端代码目录迁移和重组...")
            
            # 1. 从配置数据解析表名和模块信息
            table_name = config_data.get('head', {}).get('tableName', '')
            if not table_name:
                print("[FAIL] 无法获取表名，跳过前端代码迁移")
                return False
            
            components = self._parse_table_name_components(table_name, config_data)
            module_name = components['module_name']
            sub_module = components['sub_module']
            entity_name = components['entity_name'].lower()
            
            print(f"[LIST] 模块信息:")
            print(f"   表名: {table_name}")
            print(f"   模块名: {module_name}")
            print(f"   子模块: {sub_module}")
            print(f"   实体名: {entity_name}")
            
            # 2. 构建多个可能的源路径（容错机制）
            project_root = self.get_config_value('project', 'path_prefix')
            
            possible_source_paths = [
                # JeecgBoot实际生成路径：根据实际观察到的生成位置
                Path(project_root) / 'src' / 'main' / 'java' / '{{PACKAGE_NAME}}' / sub_module / 'vue3',
                # 标准JeecgBoot模块路径
                Path(project_root) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / sub_module / entity_name / 'vue3',
                Path(project_root) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}' / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / sub_module / 'vue3',
                # 备用路径：system模块
                Path(project_root) / 'jeecg-module-system' / 'jeecg-system-biz' / 'src' / 'main' / 'resources' / 'jeecg' / module_name / 'vue3',
                Path(project_root) / 'jeecg-module-system' / 'jeecg-system-biz' / 'src' / 'main' / 'resources' / 'jeecg' / sub_module / 'vue3',
                # 直接在项目根目录的src中
                Path(project_root) / 'src' / 'main' / 'java' / 'org' / 'jeecg' / 'modules' / module_name / sub_module / 'vue3',
            ]
            
            # 找到实际存在的源路径
            source_vue3_dir = None
            for path in possible_source_paths:
                if path.exists():
                    source_vue3_dir = path
                    print(f"[OK] 找到实际的vue3源路径: {source_vue3_dir}")
                    break
            
            if not source_vue3_dir:
                print(f"[WARN] 在预定义路径中未找到vue3目录，启动容错搜索...")
                
                # 容错搜索机制：在多个模块目录中搜索vue3目录
                search_base_paths = [
                    Path(project_root) / 'src',  # 项目根目录src（实际生成位置）
                    Path(project_root) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}',
                    Path(project_root) / 'jeecg-module-system',
                    Path(project_root) / 'jeecg-boot' / 'jeecg-boot-module' / 'jeecg-module-system',
                ]
                
                for base_path in search_base_paths:
                    if base_path.exists():
                        vue3_dirs = list(base_path.glob('**/vue3'))
                        print(f"[SEARCH] 在 {base_path.name} 中找到 {len(vue3_dirs)} 个vue3目录")
                        
                        for vue3_dir in vue3_dirs:
                            vue_files = list(vue3_dir.glob('*.vue'))
                            ts_files = list(vue3_dir.glob('*.ts'))
                            js_files = list(vue3_dir.glob('*.js'))
                            
                            if vue_files or ts_files or js_files:
                                print(f"[OK] 找到包含前端文件的vue3目录: {vue3_dir}")
                                print(f"   包含: {len(vue_files)} 个Vue文件，{len(ts_files)} 个TS文件，{len(js_files)} 个JS文件")
                                source_vue3_dir = vue3_dir
                                break
                    
                    if source_vue3_dir:
                        break
            
            # 检查前端项目中是否已存在同模块文件
            target_base_path = self.get_config_value('frontend_migration', 'target_base_path', 'jeecgboot-vue3/src/views')
            target_views_base = Path(project_root) / target_base_path
            frontend_module_dir = target_views_base / sub_module
            
            if frontend_module_dir.exists():
                existing_files = list(frontend_module_dir.glob('*.vue')) + list(frontend_module_dir.glob('*.ts')) + list(frontend_module_dir.glob('*.js'))
                if existing_files:
                    print(f"[OK] 发现前端项目中已存在同模块文件: {frontend_module_dir}")
                    print(f"   已有 {len(existing_files)} 个前端文件")
                    print("   这可能是同一模块的多个表单，新生成的前端代码应该已经直接生成到正确位置")
                    return True
            
            if not source_vue3_dir:
                print(f"[FAIL] 在所有位置都未找到vue3前端文件目录")
                return False
            
            # 3. 验证源目录包含前端文件
            vue_files = list(source_vue3_dir.glob('*.vue'))
            ts_files = list(source_vue3_dir.glob('*.ts'))
            js_files = list(source_vue3_dir.glob('*.js'))
            
            if not (vue_files or ts_files or js_files):
                print(f"[FAIL] 源目录中未找到前端文件: {source_vue3_dir}")
                return False
            
            print(f"[OK] 源目录验证通过，找到 {len(vue_files)} 个Vue文件，{len(ts_files)} 个TS文件，{len(js_files)} 个JS文件")
            
            # 4. 构建目标路径
            final_target_dir = target_views_base / sub_module
            
            print(f"[SYMBOL] 路径信息:")
            print(f"   源vue3目录: {source_vue3_dir}")
            print(f"   最终目标: {final_target_dir}")
            
            # 5. 执行迁移操作
            self._execute_frontend_migration(source_vue3_dir, final_target_dir, migration_config)
            
        except Exception as e:
            print(f"⚠️ 前端代码迁移异常: {e}")
            import traceback
            traceback.print_exc()
    
    def _parse_table_name_components(self, table_name: str, config_data: Dict) -> Dict:
        """解析表名组件"""
        if not table_name or not table_name.startswith('us_'):
            raise ValueError(f"表名格式错误: {table_name}")
        
        parts = table_name.split('_')
        if len(parts) < 4:
            raise ValueError(f"表名格式错误，至少需要4段: {table_name}")
        
        module_name = parts[1]
        sub_module = parts[2]
        business_scenario = '_'.join(parts[3:])  # 支持多段业务场景
        
        # 从配置获取实体名，或者基于业务场景生成
        business_entity = config_data.get('head', {}).get('business_entity', '')
        if not business_entity:
            business_entity = ''.join(word.capitalize() for word in business_scenario.split('_'))
        
        return {
            'module_name': module_name,
            'sub_module': sub_module,
            'business_scenario': business_scenario,
            'entity_name': business_entity
        }
    
    def _execute_frontend_migration(self, source_dir: Path, target_dir: Path, migration_config: Dict):
        """执行前端文件迁移操作"""
        try:
            print(f"\n[REFRESH] 执行前端代码迁移操作...")
            
            # 确保目标目录存在
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果目标目录已存在，根据配置决定是否清理
            if target_dir.exists():
                if migration_config.get('cleanup_source', False):
                    print(f"   清理已存在的目标目录: {target_dir}")
                    shutil.rmtree(target_dir)
                else:
                    print(f"   目标目录已存在，将合并文件: {target_dir}")
                    # 创建备份
                    backup_dir = target_dir.parent / f"{target_dir.name}_backup_{int(time.time())}"
                    shutil.copytree(target_dir, backup_dir)
                    print(f"   创建备份: {backup_dir}")
            
            # 执行移动操作
            if not target_dir.exists():
                shutil.move(str(source_dir), str(target_dir))
                print(f"[OK] 前端代码迁移成功: {target_dir}")
            else:
                # 合并文件（如果目标目录已存在）
                for item in source_dir.iterdir():
                    target_item = target_dir / item.name
                    if item.is_file():
                        if target_item.exists():
                            print(f"   覆盖文件: {item.name}")
                        shutil.copy2(item, target_item)
                    elif item.is_dir():
                        if target_item.exists():
                            shutil.rmtree(target_item)
                        shutil.copytree(item, target_item)
                
                # 清理源目录
                shutil.rmtree(source_dir)
                print(f"[OK] 前端代码合并完成: {target_dir}")
            
            # 验证迁移结果
            migrated_files = list(target_dir.glob('*.vue')) + list(target_dir.glob('*.ts')) + list(target_dir.glob('*.js'))
            print(f"[OK] 迁移完成，目标目录包含 {len(migrated_files)} 个前端文件")
            
        except Exception as e:
            print(f"[FAIL] 前端代码迁移操作失败: {e}")
            raise

    def delete_forms(self, form_ids: List[str], flag: int = 1) -> bool:
        """
        删除在线表单（批量删除）
        
        Args:
            form_ids (List[str]): 要删除的表单ID列表
            flag (int): 删除标志，默认为1
            
        Returns:
            bool: 删除是否成功
        """
        if not form_ids:
            print("❌ 表单ID列表为空，无法执行删除操作")
            return False
        
        delete_url = self.get_config_value('api', 'form_delete_batch_url')
        if not delete_url:
            print("❌ 缺少表单删除API配置")
            return False
        
        # 构建请求参数
        ids_str = ','.join(form_ids)
        request_data = {
            "ids": ids_str,
            "flag": flag
        }
        
        try:
            print(f"🗑️ 开始删除表单，ID列表: {ids_str}")
            # 构建URL参数（URL编码）
            import urllib.parse
            ids_encoded = urllib.parse.quote(ids_str, safe='')
            url_with_params = f"{delete_url}?ids={ids_encoded}&flag={flag}"
            
            # JeecgBoot删除接口使用DELETE方法
            response = self.session.delete(url_with_params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 表单删除成功，删除了 {len(form_ids)} 个表单")
                    return True
                else:
                    print(f"❌ 表单删除失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ 表单删除请求失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 表单删除异常: {e}")
            return False
    
    def delete_forms_by_table_names(self, table_names: List[str], flag: int = 1) -> bool:
        """
        根据表名删除在线表单
        
        Args:
            table_names (List[str]): 要删除的表名列表
            flag (int): 删除标志，默认为1
            
        Returns:
            bool: 删除是否成功
        """
        if not table_names:
            print("❌ 表名列表为空，无法执行删除操作")
            return False
        
        print(f"🔍 开始查找表单ID，表名列表: {', '.join(table_names)}")
        
        # 获取所有表单ID
        form_ids = []
        for table_name in table_names:
            form_id = self.get_form_id(table_name)
            if form_id:
                form_ids.append(form_id)
                print(f"   找到表单 {table_name} -> ID: {form_id}")
            else:
                print(f"   ⚠️ 未找到表 {table_name} 对应的表单")
        
        if not form_ids:
            print("❌ 未找到任何有效的表单ID，删除操作终止")
            return False
        
        # 执行批量删除
        return self.delete_forms(form_ids, flag)
    
    def delete_form_by_table_name(self, table_name: str, flag: int = 1) -> bool:
        """
        根据单个表名删除在线表单
        
        Args:
            table_name (str): 要删除的表名
            flag (int): 删除标志，默认为1
            
        Returns:
            bool: 删除是否成功
        """
        return self.delete_forms_by_table_names([table_name], flag)
    
    def list_all_forms(self, page_no: int = 1, page_size: int = 50) -> List[Dict]:
        """
        列出所有在线表单
        
        Args:
            page_no (int): 页码，默认为1
            page_size (int): 每页大小，默认为50
            
        Returns:
            List[Dict]: 表单列表
        """
        url = self.get_config_value('api', 'form_list_url')
        if not url:
            print("❌ 缺少表单查询API配置")
            return []
        
        try:
            params = {'pageNo': page_no, 'pageSize': page_size}
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    records = result.get('result', {}).get('records', [])
                    print(f"📋 查询到 {len(records)} 个表单")
                    return records
                else:
                    print(f"❌ 表单查询失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 表单查询请求失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 表单查询异常: {e}")
        
        return []
    
    def find_forms_by_pattern(self, pattern: str) -> List[Dict]:
        """
        根据模式查找表单（支持模糊匹配）
        
        Args:
            pattern (str): 搜索模式（表名模糊匹配）
            
        Returns:
            List[Dict]: 匹配的表单列表
        """
        all_forms = self.list_all_forms()
        matching_forms = []
        
        for form in all_forms:
            table_name = form.get('tableName', '')
            if pattern in table_name:
                matching_forms.append(form)
        
        print(f"🔍 找到 {len(matching_forms)} 个匹配 '{pattern}' 的表单")
        for form in matching_forms:
            print(f"   - {form.get('tableName')} (ID: {form.get('id')})")
        
        return matching_forms
    
    def create_maven_module(self, module_name: str) -> bool:
        """使用Maven archetype创建新模块"""
        print(f"[BUILD] 创建Maven模块: jeecg-module-{module_name}")
        
        # 获取路径前缀
        project_prefix = self.get_config_value('project', 'path_prefix')
        
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
        
        # 构建执行目录路径
        exec_dir = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module'
        
        print(f"   执行目录: {exec_dir.absolute()}")
        print(f"   Maven命令: {' '.join(maven_cmd)}")
        
        try:
            # 确保在正确的目录下执行
            if not exec_dir.exists():
                print(f"[FAIL] 执行目录不存在: {exec_dir.absolute()}")
                return False
            
            # 执行Maven命令
            import subprocess
            result = subprocess.run(
                maven_cmd,
                cwd=exec_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print("[OK] Maven模块创建成功")
                return True
            else:
                print(f"[FAIL] Maven模块创建失败")
                print(f"   错误码: {result.returncode}")
                print(f"   错误信息: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[FAIL] Maven命令执行超时")
            return False
        except Exception as e:
            print(f"[FAIL] Maven命令执行异常: {e}")
            return False
    
    def update_module_registry_pom(self, module_name: str) -> bool:
        """更新模块注册表pom.xml添加新模块"""
        project_prefix = self.get_config_value('project', 'path_prefix')
        pom_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / 'pom.xml'
        
        print(f"[NOTE] 更新模块注册表pom.xml: {pom_path.absolute()}")
        
        if not pom_path.exists():
            print(f"[FAIL] 模块注册表pom.xml不存在: {pom_path}")
            return False
        
        try:
            # 读取原始文件内容
            with open(pom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查模块是否已存在
            module_artifact_id = f"jeecg-module-{module_name}"
            if f"<module>{module_artifact_id}</module>" in content:
                print(f"[OK] 模块已存在于模块注册表中: {module_artifact_id}")
                return True
            
            # 查找 </modules> 标签的位置
            modules_end_pos = content.find('</modules>')
            if modules_end_pos == -1:
                modules_end_pos = content.find('</ns0:modules>')
            if modules_end_pos == -1:
                print("[FAIL] 未找到modules节点")
                return False
            
            # 在 </modules> 前插入新模块
            new_module_entry = f"        <module>{module_artifact_id}</module>\n    "
            new_content = content[:modules_end_pos] + new_module_entry + content[modules_end_pos:]
            
            # 写回文件
            with open(pom_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"[OK] 已添加模块到模块注册表: {module_name}")
            return True
            
        except Exception as e:
            print(f"[FAIL] 更新模块注册表pom.xml失败: {e}")
            return False
    
    def update_system_start_pom(self, module_name: str) -> bool:
        """更新启动项目pom.xml添加新模块依赖"""
        project_prefix = self.get_config_value('project', 'path_prefix')
        pom_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-module-system' / 'jeecg-system-start' / 'pom.xml'
        
        print(f"[NOTE] 更新启动项目pom.xml: {pom_path.absolute()}")
        
        if not pom_path.exists():
            print(f"[FAIL] 启动项目pom.xml不存在: {pom_path}")
            return False
        
        try:
            # 读取原始文件内容
            with open(pom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查依赖是否已存在
            artifact_id = f"jeecg-module-{module_name}"
            if f"<artifactId>{artifact_id}</artifactId>" in content:
                print(f"[OK] 依赖已存在于启动项目pom.xml中: {artifact_id}")
                return True
            
            # 查找合适的位置插入新依赖（在 jeecg-system-biz 依赖之后）
            system_biz_pos = content.find('<artifactId>jeecg-system-biz</artifactId>')
            if system_biz_pos == -1:
                # 如果找不到 jeecg-system-biz，就在第一个 </dependency> 后插入
                first_dep_end = content.find('</dependency>')
                if first_dep_end == -1:
                    print("[FAIL] 无法找到合适的位置插入依赖")
                    return False
                insert_pos = first_dep_end + len('</dependency>')
            else:
                # 找到 jeecg-system-biz 依赖的结束位置
                dep_end_pos = content.find('</dependency>', system_biz_pos)
                if dep_end_pos == -1:
                    print("[FAIL] 无法找到 jeecg-system-biz 依赖的结束位置")
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
            
            print(f"[OK] 已添加依赖到启动项目pom.xml: {artifact_id}")
            return True
            
        except Exception as e:
            print(f"[FAIL] 更新启动项目pom.xml失败: {e}")
            return False
    
    def check_module_exists(self, module_name: str) -> bool:
        """检查模块是否存在"""
        project_prefix = self.get_config_value('project', 'path_prefix')
        module_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'
        return module_path.exists()
    
    def ensure_module_exists(self, module_name: str) -> bool:
        """确保模块存在，如果不存在则创建并配置"""
        print(f"\n[TOOL] 模块管理: {module_name}")
        print("=" * 40)
        
        # 1. 检查模块是否存在
        if self.check_module_exists(module_name):
            print(f"[OK] 模块已存在，跳过创建步骤")
            return True
        
        # 2. 创建模块
        print(f"[PACKAGE] 模块不存在，开始创建...")
        if not self.create_maven_module(module_name):
            return False
        
        # 3. 更新模块注册表pom.xml
        if not self.update_module_registry_pom(module_name):
            return False
        
        # 4. 更新启动项目pom.xml
        if not self.update_system_start_pom(module_name):
            return False
        
        print(f"[OK] 模块 {module_name} 创建和配置完成")
        return True
    
    def process_placeholder_variables(self, config_data: Dict) -> bool:
        """代码生成后处理占位变量参数"""
        print(f"\n{'='*50}")
        print("[TEMPLATE] 开始处理占位变量参数...")
        
        try:
            # 获取表名和模块信息
            table_name = config_data.get('head', {}).get('tableName', '')
            if not table_name:
                print("[FAIL] 无法获取表名，跳过占位变量处理")
                return False
            
            components = self._parse_table_name_components(table_name, config_data)
            module_name = components['module_name']
            sub_module = components['sub_module']
            business_entity = components['entity_name']
            
            print(f"[LIST] 占位变量信息:")
            print(f"   表名: {table_name}")
            print(f"   模块名: {module_name}")
            print(f"   子模块: {sub_module}")
            print(f"   业务实体: {business_entity}")
            
            # 获取项目路径
            project_prefix = self.get_config_value('project', 'path_prefix')
            
            # 1. 处理生成的源代码目录中的占位变量
            source_base_path = Path(project_prefix) / 'src' / 'main' / 'java'
            if source_base_path.exists():
                self._process_placeholder_in_directory(source_base_path, components, project_prefix)
            
            # 2. 处理模块目录中的占位变量
            module_path = Path(project_prefix) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'
            if module_path.exists():
                self._process_placeholder_in_directory(module_path, components, project_prefix)
            
            print("[OK] 占位变量处理完成")
            return True
            
        except Exception as e:
            print(f"[FAIL] 占位变量处理异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def execute_permission_sql(self, config_data: Dict) -> bool:
        """执行权限菜单SQL脚本并记录权限ID - 基于用户超级深度思考方案"""
        print(f"\n{'='*50}")
        print("[SQL] 开始执行权限菜单SQL脚本并记录权限ID...")
        
        try:
            # 检查是否启用SQL执行
            if not self.get_config_value('database_execution', 'enabled', 'true').lower() == 'true':
                print("[SKIP] SQL执行已禁用，跳过权限菜单初始化")
                return True
            
            # 查找SQL文件
            table_name = config_data.get('head', {}).get('tableName', '')
            components = self._parse_table_name_components(table_name, config_data)
            module_name = components['module_name']
            
            sql_files = []
            # 在多个位置搜索SQL文件
            search_paths = [
                # 后端模块目录
                Path(self.get_config_value('project', 'path_prefix')) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}',
                # 前端views目录  
                Path(self.get_config_value('project', 'path_prefix')) / 'jeecgboot-vue3' / 'src' / 'views'
            ]
            
            for search_path in search_paths:
                if search_path.exists():
                    for sql_file in search_path.rglob("V*__menu_insert_*.sql"):
                        sql_files.append(sql_file)
                    
            if not sql_files:
                print("[WARN] 未找到权限菜单SQL文件")
                return True
                
            # 执行SQL文件并记录权限ID
            permission_ids = []
            for sql_file in sql_files:
                print(f"[EXEC] 执行SQL文件并记录权限ID: {sql_file.name}")
                sql_permission_ids = self._execute_sql_and_record_permission_ids(sql_file)
                if sql_permission_ids is not None:
                    permission_ids.extend(sql_permission_ids)
                    print(f"[OK] SQL文件执行成功，记录权限ID: {len(sql_permission_ids)} 个")
                else:
                    print(f"[FAIL] SQL文件执行失败: {sql_file.name}")
                    return False
                    
            # 将记录的权限ID保存到实例变量中，供权限授权步骤使用
            self.recorded_permission_ids = permission_ids
            print(f"[OK] 权限菜单SQL执行完成，总共记录权限ID: {len(permission_ids)} 个")
            
            # 显示记录的权限ID（前5个）
            if permission_ids:
                print(f"[INFO] 记录的权限ID（显示前5个）:")
                for i, perm_id in enumerate(permission_ids[:5], 1):
                    print(f"   {i}. {perm_id}")
                if len(permission_ids) > 5:
                    print(f"   ... 还有 {len(permission_ids) - 5} 个权限ID")
                    
            return True
            
        except Exception as e:
            print(f"[FAIL] SQL执行异常: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def grant_permissions(self, config_data: Dict) -> bool:
        """为管理员角色授权新生成模块的权限 - 基于历史版本的严谨实现"""
        print(f"\n{'='*50}")
        print("[AUTH] 开始权限授权...")
        
        try:
            # 检查是否启用权限授权
            if not self.get_config_value('permission_authorization', 'enabled', 'true').lower() == 'true':
                print("[SKIP] 权限授权已禁用")
                return True
                
            if not self.get_config_value('permission_authorization', 'auto_grant_to_admin', 'true').lower() == 'true':
                print("[SKIP] 管理员自动授权已禁用") 
                return True
                
            admin_role_id = self.get_config_value('permission_authorization', 'admin_role_id')
            if not admin_role_id:
                print("[FAIL] 未配置管理员角色ID")
                return False
            
            print(f"[INFO] 为角色 {admin_role_id} 执行真实权限授权...")
            
            # 1. 登录获取Token
            print("1. 正在登录获取Token...")
            token = self._get_auth_token()
            if not token:
                print("[FAIL] 无法获取认证Token，权限授权失败")
                return False
                
            token_display = token[:20] + "..." if len(token) > 20 else token
            print(f"[OK] 认证Token获取成功: {token_display}")
            
            # 2. 获取SQL执行步骤记录的权限ID（简化版本 - 避免查询权限API导致的HTTP 404错误）
            print("2. 获取SQL执行步骤记录的权限ID...")
            if hasattr(self, 'recorded_permission_ids') and self.recorded_permission_ids:
                new_permission_ids = self.recorded_permission_ids
                print(f"[OK] 获取到SQL执行步骤记录的权限ID: {len(new_permission_ids)} 个")
                for i, perm_id in enumerate(new_permission_ids, 1):
                    print(f"   {i}. {perm_id}")
            else:
                print("[WARN] 未找到SQL执行步骤记录的权限ID，尝试从SQL文件解析...")
                new_permission_ids = self._parse_new_permission_ids(config_data)
                if not new_permission_ids:
                    print("[ERROR] 无法获取权限ID，权限授权失败")
                    return False
                    
                print(f"[OK] 从SQL文件解析到权限ID: {len(new_permission_ids)} 个")
                for i, perm_id in enumerate(new_permission_ids, 1):
                    print(f"   {i}. {perm_id}")
                
            # 3. 直接保存新权限（简化版本 - 不查询现有权限，避免HTTP 404错误）
            print("3. 为管理员角色添加新权限...")
            all_permission_ids = new_permission_ids
            added_count = len(new_permission_ids)
            
            print(f"[OK] 权限处理完成:")
            print(f"   新增权限: {len(new_permission_ids)} 个")
            print(f"   准备保存: {len(all_permission_ids)} 个")
            
            # 4. 保存权限到管理员角色
            print("4. 保存权限到管理员角色...")
            if self._save_role_permissions(token, admin_role_id, all_permission_ids):
                print("[OK] 权限授权成功完成")
                return True
            else:
                print("[FAIL] 权限保存失败")
                return False
            
        except Exception as e:
            print(f"[FAIL] 权限授权异常: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _execute_sql_and_record_permission_ids(self, sql_file: Path) -> list:
        """执行SQL文件并记录权限ID - 简洁纯净版本"""
        try:
            # 导入mysql库
            import mysql.connector
            
            # 读取SQL文件和解析权限ID
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            permission_ids = self._extract_permission_ids_from_sql(sql_content)
            if not permission_ids:
                return []
                
            # 获取数据库配置
            db_url = self.get_config_value('database_execution', 'url')
            db_user = self.get_config_value('database_execution', 'username')
            db_pass = self.get_config_value('database_execution', 'password')
            
            # 解析数据库连接信息
            import re
            match = re.search(r'jdbc:mysql://([^:/]+):(\d+)/([^?]+)', db_url)
            if not match:
                return []
            host, port, database = match.groups()
            
            # 连接数据库并执行SQL
            connection = mysql.connector.connect(
                host=host, port=int(port), user=db_user, 
                password=db_pass, database=database
            )
            
            cursor = connection.cursor()
            
            # 分割并执行SQL语句
            sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            for sql_stmt in sql_statements:
                if sql_stmt:
                    try:
                        cursor.execute(sql_stmt)
                    except mysql.connector.Error as e:
                        if e.errno != 1062:  # 忽略重复键错误
                            raise
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print(f"[OK] SQL执行完成，记录权限ID: {len(permission_ids)} 个")
            return permission_ids
            
        except ImportError:
            print("[FAIL] 请安装mysql-connector-python: pip install mysql-connector-python")
            return []
        except Exception as e:
            print(f"[FAIL] SQL执行失败: {e}")
            return []
    
    
    def _extract_permission_ids_from_sql(self, sql_content: str) -> list:
        """从SQL内容中提取权限ID"""
        import re
        pattern = r"INSERT\s+INTO\s+sys_permission[^']*'([^']+)'"
        matches = re.findall(pattern, sql_content, re.IGNORECASE)
        return list(set(matches))
    
            
    def verify_compilation(self, module_name: str) -> bool:
        """验证Maven编译"""
        print(f"\n{'='*50}")
        print("[COMPILE] 开始Maven编译验证...")
        
        try:
            module_path = Path(self.get_config_value('project', 'path_prefix')) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'
            
            if not module_path.exists():
                print(f"[ERROR] 模块路径不存在: {module_path}")
                return False
                
            import subprocess
            result = subprocess.run(
                ['mvn', 'compile', '-DskipTests'],
                cwd=module_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("[OK] Maven编译成功")
                return True
            else:
                print(f"[FAIL] Maven编译失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 编译验证异常: {e}")
            return False
    
    def _process_placeholder_in_directory(self, base_path: Path, components: Dict, project_prefix: str):
        """在指定目录中处理占位变量"""
        module_name = components['module_name']
        sub_module = components['sub_module']
        business_entity = components['entity_name']
        
        # 查找包含占位变量的目录
        template_dirs = list(base_path.rglob("*{{PACKAGE_NAME}}*"))
        if template_dirs:
            print(f"[SEARCH] 发现 {len(template_dirs)} 个包含{{PACKAGE_NAME}}的目录")
            self._fix_placeholder_directories(template_dirs, components)
        
        # 查找包含占位变量的文件
        template_files = []
        for pattern in ['{{PROJECT_PATH}}', '{{BUSINESS_ENTITY}}', '{{PACKAGE_NAME}}']:
            files = self._find_files_with_placeholder(base_path, pattern)
            template_files.extend(files)
        
        if template_files:
            print(f"[SEARCH] 发现 {len(set(template_files))} 个包含占位变量的文件")
            self._fix_placeholder_files(list(set(template_files)), components, project_prefix)
    
    def _find_files_with_placeholder(self, base_path: Path, placeholder: str) -> List[Path]:
        """查找包含特定占位变量的文件"""
        files = []
        for file_path in base_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.java', '.xml', '.properties', '.yml', '.yaml', '.sql']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if placeholder in content:
                            files.append(file_path)
                except Exception:
                    continue
        return files
    
    def _fix_placeholder_directories(self, template_dirs: List[Path], components: Dict):
        """修复包含占位变量的目录名"""
        module_name = components['module_name']
        sub_module = components['sub_module']
        
        for template_dir in template_dirs:
            try:
                # 构建正确的包路径
                base_package_path = f"org/jeecg/modules/{module_name}/{sub_module}"
                
                # 替换目录名中的占位变量
                correct_path_str = str(template_dir).replace("{{PACKAGE_NAME}}", base_package_path)
                correct_path = Path(correct_path_str)
                
                print(f"[FOLDER] 重命名目录:")
                print(f"   从: {template_dir}")
                print(f"   到: {correct_path}")
                
                # 确保父目录存在
                correct_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 移动目录内容
                if template_dir.exists() and template_dir.is_dir():
                    if correct_path.exists():
                        # 目标目录已存在，合并内容
                        self._merge_directories(template_dir, correct_path)
                    else:
                        # 直接移动目录
                        shutil.move(str(template_dir), str(correct_path))
                        
            except Exception as e:
                print(f"[FAIL] 处理目录失败 {template_dir}: {e}")
    
    def _merge_directories(self, source_dir: Path, target_dir: Path):
        """合并两个目录的内容"""
        for item in source_dir.iterdir():
            target_item = target_dir / item.name
            if item.is_dir():
                if not target_item.exists():
                    shutil.move(str(item), str(target_item))
                else:
                    # 递归合并子目录
                    self._merge_directories(item, target_item)
            else:
                if not target_item.exists():
                    shutil.move(str(item), str(target_item))
        
        # 删除空的源目录
        try:
            source_dir.rmdir()
        except:
            pass
    
    def _fix_placeholder_files(self, template_files: List[Path], components: Dict, project_prefix: str):
        """修复包含占位变量的文件内容"""
        module_name = components['module_name']
        sub_module = components['sub_module']
        business_entity = components['entity_name']
        
        # 构建替换变量映射
        replacements = {
            '{{PROJECT_PATH}}': f"{project_prefix}/jeecg-boot/jeecg-boot-module/jeecg-module-{module_name}",
            '{{BUSINESS_ENTITY}}': business_entity,
            '{{PACKAGE_NAME}}': f"org.jeecg.modules.{module_name}.{sub_module}",
            '{{MODULE_NAME}}': module_name,
            '{{SUBMODULE_NAME}}': sub_module,
        }
        
        fixed_files = 0
        for file_path in template_files:
            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含占位变量
                original_content = content
                template_fixed = False
                
                # 替换所有占位变量
                for placeholder, replacement in replacements.items():
                    if placeholder in content:
                        content = content.replace(placeholder, replacement)
                        template_fixed = True
                
                # 修复重复包名问题
                duplicate_package = f"org.jeecg.modules.{module_name}.{sub_module}.{module_name}.{sub_module}"
                if duplicate_package in content:
                    correct_package = f"org.jeecg.modules.{module_name}.{sub_module}"
                    content = content.replace(duplicate_package, correct_package)
                    template_fixed = True
                
                # 如果有修改，写回文件
                if template_fixed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"   [REFRESH] 已修复文件: {file_path.relative_to(file_path.parent.parent.parent)}")
                    fixed_files += 1
                    
            except Exception as e:
                print(f"   [FAIL] 处理文件失败 {file_path}: {e}")
        
        print(f"[OK] 共修复 {fixed_files} 个文件中的占位变量")

    def _replace_template_variables(self, config_data: Dict, project_path: str, module_name: str, submodule_name: str, business_entity: str) -> Dict:
        """替换模板中的变量占位符 - 增强版本支持类型感知"""

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

        # 类型感知的变量映射表
        variables = {
            "{{PROJECT_PATH}}": {"value": project_path, "type": "string"},
            "{{MODULE_NAME}}": {"value": module_name, "type": "string"},
            "{{SUBMODULE_NAME}}": {"value": submodule_name, "type": "string"},
            "{{BUSINESS_ENTITY}}": {"value": business_entity, "type": "string"},
            "{{TABLE_NAME}}": {"value": table_name, "type": "string"},
            "{{PACKAGE_NAME}}": {"value": package_name, "type": "string"},
            "{{TABLE_SUFFIX}}": {"value": table_suffix, "type": "string"},
            "{{URL_PATH}}": {"value": url_path, "type": "string"},
            "{{FRONTEND_PATH}}": {"value": frontend_path, "type": "string"},
            "{{TABLE_DESCRIPTION}}": {"value": table_description, "type": "string"},
            "{{TABLE_TYPE}}": {"value": table_type, "type": "integer"},
            "{{RELATION_TYPE}}": {"value": relation_type, "type": "null"},
            "{{TAB_ORDER_NUM}}": {"value": tab_order_num, "type": "null"},
            "{{SUB_TABLE_STR}}": {"value": sub_table_str, "type": "null"},
            "{{INFERENCE_STRATEGY}}": {"value": inference_strategy, "type": "string"},
            "{{SEMANTIC_ANALYSIS}}": {"value": semantic_analysis, "type": "string"}
        }

        # 类型感知的递归替换
        replaced_config = self._type_aware_recursive_replace(config_data, variables)

        # 生成字段配置
        replaced_config = self._generate_fields(replaced_config, module_name, submodule_name, business_entity)

        return replaced_config

    def _type_aware_recursive_replace(self, obj, variables: Dict) -> any:
        """类型感知的递归替换对象中的变量"""
        if isinstance(obj, dict):
            return {key: self._type_aware_recursive_replace(value, variables) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._type_aware_recursive_replace(item, variables) for item in obj]
        elif isinstance(obj, str):
            # 检查是否是完全匹配的变量占位符
            if obj in variables:
                var_info = variables[obj]
                var_type = var_info["type"]
                var_value = var_info["value"]
                
                if var_type == "null":
                    return None
                elif var_type == "integer":
                    return var_value
                elif var_type == "string":
                    return var_value
                else:
                    return var_value
            
            # 否则进行字符串内的变量替换
            result = obj
            for var, var_info in variables.items():
                var_value = var_info["value"]
                var_type = var_info["type"]
                
                if var in result:
                    if var_type == "null":
                        # 对于null类型，如果是字符串中的一部分，替换为"null"字符串
                        # 如果是完全匹配，上面已经处理了
                        result = result.replace(var, "null")
                    else:
                        result = result.replace(var, str(var_value))
            return result
        else:
            return obj
    
    def _recursive_replace(self, obj, variables: Dict) -> any:
        """递归替换对象中的变量 - 保留兼容性"""
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

        # 更新配置 - 场景驱动的智能配置生成
        config_data['fields'] = fields
        
        # 场景识别：根据表类型智能配置
        table_type = config_data.get('head', {}).get('tableType', 1)
        
        if table_type == 1:  # 独立表场景
            # 独立表不应包含 subList 属性
            if 'subList' in config_data:
                del config_data['subList']
        
        # 初始化必需的数组属性
        config_data['indexs'] = []
        config_data['deleteFieldIds'] = []
        config_data['deleteIndexIds'] = []
        
        # 类型感知的替换机制已经确保了正确的数据类型，无需额外修复
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
    
    # ==================== 权限授权辅助方法 - 基于历史版本严谨实现 ====================
    
    def _get_auth_token(self) -> str:
        """获取认证Token"""
        try:
            base_url = self.get_config_value('server', 'base_url')
            username = self.get_config_value('server', 'username')  
            password = self.get_config_value('server', 'password')
            timeout = int(self.get_config_value('timeouts', 'login', '10'))
            
            login_data = {"username": username, "password": password}
            response = requests.post(f"{base_url}/sys/mLogin", json=login_data, timeout=timeout)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('result', {}).get('token', '')
                else:
                    print(f"[FAIL] 登录失败: {result.get('message', '未知错误')}")
                    return ""
            else:
                print(f"[FAIL] 登录请求失败: HTTP {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"[FAIL] 获取Token异常: {e}")
            return ""
    
    def _query_role_permissions(self, token: str, role_id: str) -> list:
        """查询角色现有权限 - 使用正确的JeecgBoot API"""
        try:
            base_url = self.get_config_value('server', 'base_url')
            headers = {'X-Access-Token': token}
            
            # 使用正确的JeecgBoot权限查询API
            response = requests.get(f"{base_url}/sys/permission/queryTreeList", 
                                  headers=headers, params={'roleId': role_id}, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # 从结果中提取权限ID列表
                    permissions = []
                    data = result.get('result', [])
                    self._extract_permission_ids_from_tree(data, permissions)
                    return permissions
                else:
                    print(f"[FAIL] 查询权限失败: {result.get('message', '未知错误')}")
                    return None
            else:
                print(f"[FAIL] 查询权限请求失败: HTTP {response.status_code} - {response.text[:100]}")
                return None
                
        except Exception as e:
            print(f"[FAIL] 查询权限异常: {e}")
            return None
    
    def _extract_permission_ids_from_tree(self, nodes: list, permissions: list):
        """从权限树中递归提取已选中的权限ID"""
        if not nodes:
            return
            
        for node in nodes:
            if isinstance(node, dict):
                # 如果节点被选中，添加到权限列表
                if node.get('checked', False):
                    node_id = node.get('id') or node.get('key')
                    if node_id:
                        permissions.append(node_id)
                
                # 递归处理子节点
                children = node.get('children') or node.get('child')
                if children:
                    self._extract_permission_ids_from_tree(children, permissions)
    
    def _parse_new_permission_ids(self, config_data: Dict) -> list:
        """从生成的SQL文件中解析新权限ID"""
        try:
            # 查找生成的SQL文件
            table_name = config_data.get('head', {}).get('tableName', '')
            components = self._parse_table_name_components(table_name, config_data)
            entity_name = components['entity_name']
            module_name = components['module_name']
            
            # 搜索SQL文件
            sql_files = []
            module_path = Path(self.get_config_value('project', 'path_prefix')) / 'jeecg-boot' / 'jeecg-boot-module' / f'jeecg-module-{module_name}'
            if module_path.exists():
                for sql_file in module_path.rglob(f"V*__menu_insert_*{entity_name}*.sql"):
                    sql_files.append(sql_file)
            
            if not sql_files:
                # 也可能在前端目录
                frontend_path = Path(self.get_config_value('project', 'path_prefix')) / 'jeecgboot-vue3' / 'src' / 'views'
                if frontend_path.exists():
                    for sql_file in frontend_path.rglob(f"V*__menu_insert_*{entity_name}*.sql"):
                        sql_files.append(sql_file)
            
            if not sql_files:
                return []
                
            # 解析SQL文件中的权限ID
            permission_ids = []
            import re
            
            for sql_file in sql_files:
                try:
                    with open(sql_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 解析INSERT语句中的权限ID
                    # 格式：INSERT INTO sys_permission(id, ...) VALUES('权限ID', ...)
                    id_pattern = r"INSERT INTO sys_permission[^']*'([^']+)'"
                    matches = re.findall(id_pattern, content, re.IGNORECASE)
                    permission_ids.extend(matches)
                    
                except Exception as e:
                    print(f"[WARN] 解析SQL文件失败 {sql_file}: {e}")
                    continue
            
            return permission_ids
            
        except Exception as e:
            print(f"[FAIL] 解析权限ID异常: {e}")
            return []
    
    def _save_role_permissions(self, token: str, role_id: str, permission_ids: list) -> bool:
        """保存角色权限"""
        try:
            base_url = self.get_config_value('server', 'base_url')
            headers = {'X-Access-Token': token, 'Content-Type': 'application/json'}
            
            # 准备权限数据
            save_data = {
                "roleId": role_id,
                "permissionIds": ",".join(permission_ids),
                "lastpermissionIds": ""  # 空字符串表示不删除现有权限
            }
            
            # 使用正确的JeecgBoot权限保存API
            response = requests.post(f"{base_url}/sys/permission/saveRolePermission",
                                   headers=headers, json=save_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("[OK] 权限保存成功")
                    return True
                else:
                    print(f"[FAIL] 权限保存失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"[FAIL] 权限保存请求失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[FAIL] 保存权限异常: {e}")
            return False

def main():
    """主函数 - 重构后的纯净统一架构"""
    if len(sys.argv) < 2:
        print("""
JeecgBoot 代码生成系统 v2.0 - 纯净统一架构
======================================================

用法:
1. 统一代码生成（自动识别独立表/主子表场景）:
   python3 Code_Gen_Execute.py generate <config_file_1> [config_file_2] [config_file_3] ...
   python3 Code_Gen_Execute.py generate_dir <config_directory>
   
2. 传统参数生成（保持兼容）:
   python3 Code_Gen_Execute.py generate_legacy <PROJECT_PATH> <MODULE_NAME> <SUBMODULE_NAME> <BUSINESS_ENTITY>
   
3. 测试命令:
   python3 Code_Gen_Execute.py test_main_sub_tables                # 测试主子表场景（使用education配置）
   python3 Code_Gen_Execute.py generate_from_json <json_file>      # 单个JSON文件生成
   python3 Code_Gen_Execute.py test_finance_invoice                # 测试财务发票场景
   
4. 表单管理:
   python3 Code_Gen_Execute.py list_forms                           # 列出所有表单
   python3 Code_Gen_Execute.py search_forms <pattern>               # 搜索匹配的表单
   python3 Code_Gen_Execute.py delete_form <table_name>             # 根据表名删除单个表单
   python3 Code_Gen_Execute.py delete_forms <name1> <name2> ...     # 根据表名批量删除
   python3 Code_Gen_Execute.py delete_form_by_id <form_id>          # 根据ID删除单个表单
   python3 Code_Gen_Execute.py delete_forms_by_ids <id1> <id2> ...  # 根据ID批量删除
    
示例:
   # 单个独立表
   python3 Code_Gen_Execute.py generate student_info.json
   
   # 主子表批量处理（自动识别场景）
   python3 Code_Gen_Execute.py generate student_main.json student_parent.json student_classmate.json
   
   # 目录批量处理
   python3 Code_Gen_Execute.py generate_dir /path/to/config_files/
   
   # 传统方式（向后兼容）
   python3 Code_Gen_Execute.py generate_legacy /Users/admin/Work/Github/JeecgBoot finance invoice InvoiceHeader
   
   # 测试主子表场景
   python3 Code_Gen_Execute.py test_main_sub_tables

v2.0 新特性:
✅ 场景自动识别（独立表 vs 主子表）
✅ 批量配置处理
✅ 事务性操作（失败自动回滚）
✅ 统一的错误处理
✅ 纯净的架构设计
✅ 完整的子表API调用支持
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    # 创建执行器
    executor = CodeGenExecutor()
    
    if command == "generate":
        # 新的统一生成命令
        if len(sys.argv) < 3:
            print("❌ 请提供配置文件路径")
            sys.exit(1)
            
        # 支持单个或多个配置文件
        config_inputs = sys.argv[2:]
        success = executor.execute_code_generation(config_inputs)
        sys.exit(0 if success else 1)
        
    elif command == "generate_dir":
        # 目录批量处理
        if len(sys.argv) < 3:
            print("❌ 请提供配置目录路径")
            sys.exit(1)
            
        config_dir = sys.argv[2]
        json_files = glob.glob(os.path.join(config_dir, "*.json"))
        
        if not json_files:
            print(f"❌ 在目录 {config_dir} 中未找到JSON配置文件")
            sys.exit(1)
            
        success = executor.execute_code_generation(json_files)
        sys.exit(0 if success else 1)
    
    elif command == "generate_legacy":
        # 传统参数生成（向后兼容）
        if len(sys.argv) < 6:
            print("❌ 传统生成需要4个参数: <PROJECT_PATH> <MODULE_NAME> <SUBMODULE_NAME> <BUSINESS_ENTITY>")
            sys.exit(1)
        
        project_path, module_name, submodule_name, business_entity = sys.argv[2:6]
        
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
        
        # 使用新架构执行
        success = executor.execute_code_generation(config_data)
        sys.exit(0 if success else 1)
    
    elif command == "test_main_sub_tables":
        # 测试主子表场景（使用当前生成的education配置文件）
        config_files = [
            "/Users/admin/Work/Github/JeecgBoot/CodeGen/education_student_StudentInfo_20250905080503.json",
            "/Users/admin/Work/Github/JeecgBoot/CodeGen/education_student_ParentInfo_20250905080503.json", 
            "/Users/admin/Work/Github/JeecgBoot/CodeGen/education_student_ClassmateRelation_20250905080503.json"
        ]
        
        print("🧪 开始测试主子表场景")
        print(f"📋 配置文件:")
        for i, file_path in enumerate(config_files, 1):
            if os.path.exists(file_path):
                print(f"   {i}. ✅ {os.path.basename(file_path)}")
            else:
                print(f"   {i}. ❌ {os.path.basename(file_path)} (文件不存在)")
        
        # 只处理存在的配置文件
        existing_files = [f for f in config_files if os.path.exists(f)]
        if not existing_files:
            print("❌ 没有找到有效的配置文件")
            sys.exit(1)
            
        success = executor.execute_code_generation(existing_files)
        print(f"\n🎯 主子表测试结果: {'成功' if success else '失败'}")
        sys.exit(0 if success else 1)
    
    # 表单管理命令需要登录
    if not executor.login():
        print("❌ 登录失败，无法执行表单管理操作")
        sys.exit(1)
    
    if command == "list_forms":
        # 列出所有表单
        forms = executor.list_all_forms()
        if forms:
            print(f"\n📋 共找到 {len(forms)} 个在线表单:")
            print("-" * 80)
            for i, form in enumerate(forms, 1):
                print(f"{i:2d}. 表名: {form.get('tableName', 'N/A')}")
                print(f"    ID: {form.get('id', 'N/A')}")
                print(f"    描述: {form.get('tableTxt', 'N/A')}")
                print(f"    创建时间: {form.get('createTime', 'N/A')}")
                print("-" * 80)
        else:
            print("📋 没有找到任何在线表单")
    
    elif command == "search_forms":
        if len(sys.argv) < 3:
            print("❌ 请提供搜索模式")
            sys.exit(1)
        
        pattern = sys.argv[2]
        matching_forms = executor.find_forms_by_pattern(pattern)
        
    elif command == "delete_form":
        if len(sys.argv) < 3:
            print("❌ 请提供要删除的表名")
            sys.exit(1)
        
        table_name = sys.argv[2]
        success = executor.delete_form_by_table_name(table_name)
        sys.exit(0 if success else 1)
    
    elif command == "delete_forms":
        if len(sys.argv) < 3:
            print("❌ 请提供要删除的表名列表")
            sys.exit(1)
        
        table_names = sys.argv[2:]
        success = executor.delete_forms_by_table_names(table_names)
        sys.exit(0 if success else 1)
    
    elif command == "delete_form_by_id":
        if len(sys.argv) < 3:
            print("❌ 请提供要删除的表单ID")
            sys.exit(1)
        
        form_id = sys.argv[2]
        success = executor.delete_forms([form_id])
        sys.exit(0 if success else 1)
    
    elif command == "delete_forms_by_ids":
        if len(sys.argv) < 3:
            print("❌ 请提供要删除的表单ID列表")
            sys.exit(1)
        
        form_ids = sys.argv[2:]
        success = executor.delete_forms(form_ids)
        sys.exit(0 if success else 1)
    
    elif command == "generate_from_json":
        # 使用JSON配置文件生成代码
        if len(sys.argv) < 3:
            print("❌ 请提供JSON配置文件路径")
            sys.exit(1)
        
        json_file_path = sys.argv[2]
        
        # 加载JSON配置
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"❌ JSON配置文件加载失败: {e}")
            sys.exit(1)
        
        print(f"📄 使用JSON配置文件: {json_file_path}")
        
        # 执行完整工作流（使用新架构）
        success = executor.execute_code_generation(config_data)
        sys.exit(0 if success else 1)
    
    elif command == "test_finance_invoice":
        # 使用finance_invoice_InvoiceHeader_20250905001615.json进行完整测试
        json_file_path = "/Users/admin/Work/Github/JeecgBoot/finance_invoice_InvoiceHeader_20250905001615.json"
        
        # 加载JSON配置
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"❌ JSON配置文件加载失败: {e}")
            sys.exit(1)
        
        print(f"📄 使用财务发票管理JSON配置进行完整测试")
        print(f"📄 配置文件: {json_file_path}")
        
        # 执行完整工作流（使用新架构）
        success = executor.execute_code_generation(config_data)
        
        if success:
            print("\n🎯 测试完成，现在演示删除表单功能")
            table_name = config_data.get('head', {}).get('tableName', '')
            if table_name:
                print(f"🗑️ 删除刚创建的表单: {table_name}")
                executor.delete_form_by_table_name(table_name)
        
        sys.exit(0 if success else 1)
    
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python3 Code_Gen_Execute.py' 查看所有可用命令")
        sys.exit(1)

if __name__ == "__main__":
    main()
