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
            # 应用环境变量覆盖
            self._apply_environment_overrides(config)
            return config
        except Exception as e:
            print(f"配置文件加载失败: {e}")
            sys.exit(1)

    def _apply_environment_overrides(self, config: configparser.ConfigParser):
        """应用环境变量覆盖配置"""
        # 环境变量映射表
        env_mappings = {
            'JEECG_PROJECT_ROOT': ('project', 'path_prefix'),
            'JEECG_BASE_URL': ('server', 'base_url'),
            'JEECG_USERNAME': ('server', 'username'),
            'JEECG_PASSWORD': ('server', 'password'),
            'JEECG_DATABASE_TYPE': ('database_execution', 'type'),
            'JEECG_DATABASE_URL': ('database_execution', 'url'),
            'JEECG_DATABASE_USERNAME': ('database_execution', 'username'),
            'JEECG_DATABASE_PASSWORD': ('database_execution', 'password'),
        }

        # 应用环境变量覆盖
        for env_var, (section, key) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                if not config.has_section(section):
                    config.add_section(section)
                config.set(section, key, env_value)
                print(f"🔧 环境变量覆盖: {env_var} -> [{section}] {key} = {env_value}")
    
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
    
    def execute_workflow(self, config_data: Dict) -> bool:
        """执行完整的代码生成工作流"""
        
        # 1. 验证配置
        if not self.validate_config(config_data):
            return False
        
        # 2. 确保模块存在（任务一：Maven模块创建和pom.xml修改）
        components = self._parse_table_name_components(
            config_data.get('head', {}).get('tableName', ''), 
            config_data
        )
        module_name = components['module_name']
        
        if not self.ensure_module_exists(module_name):
            print("⚠️ 模块创建失败，但继续执行代码生成...")
        
        # 3. 登录认证
        if not self.login():
            return False
        
        # 4. 创建表单
        form_id = self.create_form(config_data)
        if not form_id:
            return False
        
        # 5. 同步数据库
        if not self.sync_database(form_id):
            return False
        
        # 6. 生成代码（根据表类型决定）
        table_type = config_data.get('head', {}).get('tableType', 1)
        if table_type != 3:  # 子表不生成代码
            if not self.generate_code(form_id, config_data):
                return False
            
            # 7. 处理占位变量（任务二：动态处理占位变量参数）
            self.process_placeholder_variables(config_data)
        
        print("🎉 代码生成流程完成")
        return True
    
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
        project_path = self.get_config_value('project', 'path_prefix')
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

        # 基于历史版本的完整参数构建
        table_name = config_data.get('head', {}).get('tableName', '')
        table_description = config_data.get('head', {}).get('tableTxt', '')
        
        # 解析模块信息
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
    
    def migrate_frontend_code(self, config_data: Dict):
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
                return
            
            print(f"\n{'='*50}")
            print("[FOLDER] 开始前端代码目录迁移和重组...")
            
            # 1. 从配置数据解析表名和模块信息
            table_name = config_data.get('head', {}).get('tableName', '')
            if not table_name:
                print("[FAIL] 无法获取表名，跳过前端代码迁移")
                return
            
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
                    return
            
            if not source_vue3_dir:
                print(f"[FAIL] 在所有位置都未找到vue3前端文件目录")
                return
            
            # 3. 验证源目录包含前端文件
            vue_files = list(source_vue3_dir.glob('*.vue'))
            ts_files = list(source_vue3_dir.glob('*.ts'))
            js_files = list(source_vue3_dir.glob('*.js'))
            
            if not (vue_files or ts_files or js_files):
                print(f"[FAIL] 源目录中未找到前端文件: {source_vue3_dir}")
                return
            
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

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
JeecgBoot 代码生成和管理工具 (支持Maven模块创建和占位变量处理)
==============================================================================
用法:
1. 代码生成:
   python3 Code_Gen_Execute.py generate <PROJECT_PATH> <MODULE_NAME> <SUBMODULE_NAME> <BUSINESS_ENTITY>
   python3 Code_Gen_Execute.py generate_from_json <json_file_path>  # 使用JSON配置文件生成
   python3 Code_Gen_Execute.py test_finance_invoice                 # 使用财务发票JSON测试完整流程
   
2. 表单管理:
   python3 Code_Gen_Execute.py list_forms                           # 列出所有表单
   python3 Code_Gen_Execute.py search_forms <pattern>               # 搜索匹配的表单
   python3 Code_Gen_Execute.py delete_form <table_name>             # 根据表名删除单个表单
   python3 Code_Gen_Execute.py delete_forms <name1> <name2> ...     # 根据表名批量删除
   python3 Code_Gen_Execute.py delete_form_by_id <form_id>          # 根据ID删除单个表单
   python3 Code_Gen_Execute.py delete_forms_by_ids <id1> <id2> ...  # 根据ID批量删除
    
示例:
   python3 Code_Gen_Execute.py generate /Users/admin/Work/Github/JeecgBoot finance invoice InvoiceHeader
   python3 Code_Gen_Execute.py generate_from_json /path/to/config.json
   python3 Code_Gen_Execute.py test_finance_invoice
   python3 Code_Gen_Execute.py list_forms
   python3 Code_Gen_Execute.py search_forms us_finance
   python3 Code_Gen_Execute.py delete_form us_finance_payment_paymentrecord
   python3 Code_Gen_Execute.py delete_forms us_finance_report_reportdata us_finance_transaction_transactionrecord
   python3 Code_Gen_Execute.py delete_form_by_id 3d447fa919b64f6883a834036c14aa67
   python3 Code_Gen_Execute.py delete_forms_by_ids 3d447fa919b64f6883a834036c14aa67 41de7884bf9a42b7a2c5918f9f765dff

新功能特性:
✅ Maven模块自动创建 (mvn archetype:generate)
✅ 自动更新jeecg-boot-module和jeecg-system-start的pom.xml
✅ 占位变量动态处理 ({{PROJECT_PATH}}, {{BUSINESS_ENTITY}})
✅ 完整的前后端代码生成和迁移
✅ 在线表单生命周期管理
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    # 创建执行器
    executor = CodeGenExecutor()
    
    if command == "generate":
        # 代码生成命令
        if len(sys.argv) < 6:
            print("❌ 代码生成需要4个参数: <PROJECT_PATH> <MODULE_NAME> <SUBMODULE_NAME> <BUSINESS_ENTITY>")
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
        
        # 执行工作流
        success = executor.execute_workflow(config_data)
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
        
        # 执行完整工作流（包含Maven模块创建和占位变量处理）
        success = executor.execute_workflow(config_data)
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
        
        # 执行完整工作流（包含Maven模块创建和占位变量处理）
        success = executor.execute_workflow(config_data)
        
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
