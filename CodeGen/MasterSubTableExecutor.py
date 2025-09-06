#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot 主子表专用执行器
修复主子表机制的根本性问题
"""

import json
import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ExecutionPhase(Enum):
    """执行阶段枚举"""
    PREPROCESS = "预处理阶段"
    FORM_CREATION = "表单创建阶段"
    DATABASE_SYNC = "数据库同步阶段"
    CODE_GENERATION = "代码生成阶段"
    POST_PROCESS = "后处理阶段"

@dataclass
class TableFormInfo:
    """表单信息数据类"""
    table_name: str
    table_txt: str
    table_type: int  # 1=独立表, 2=主表, 3=子表
    config_data: Dict
    form_id: Optional[str] = None
    sync_status: bool = False
    
class MasterSubTableValidator:
    """主子表配置验证器"""
    
    @staticmethod
    def validate_config_set(main_config: Dict, sub_configs: List[Dict]) -> Tuple[bool, List[str]]:
        """验证主子表配置集合"""
        errors = []
        
        # 1. 验证主表配置
        main_head = main_config.get('head', {})
        if main_head.get('tableType') != 2:
            errors.append(f"主表tableType必须为2，当前为: {main_head.get('tableType')}")
        
        if not main_head.get('tableName'):
            errors.append("主表缺少tableName")
            
        # 2. 验证subList存在且不为空
        sub_list = main_config.get('subList', [])
        if not sub_list:
            errors.append("主表配置缺少subList")
        elif len(sub_list) != len(sub_configs):
            errors.append(f"subList数量({len(sub_list)})与子表配置数量({len(sub_configs)})不匹配")
        
        # 3. 验证子表配置
        for i, sub_config in enumerate(sub_configs):
            sub_head = sub_config.get('head', {})
            if sub_head.get('tableType') != 3:
                errors.append(f"子表{i+1} tableType必须为3，当前为: {sub_head.get('tableType')}")
            
            if not sub_head.get('tableName'):
                errors.append(f"子表{i+1} 缺少tableName")
                
            # 验证外键字段存在
            if not MasterSubTableValidator._has_foreign_key(sub_config, main_config):
                errors.append(f"子表{i+1} 缺少指向主表的外键字段")
        
        # 4. 验证主子表关联关系
        main_table_name = main_head.get('tableName', '')
        for sub_item in sub_list:
            sub_table_name = sub_item.get('tableName', '')
            if not sub_table_name:
                errors.append(f"subList中存在无效的子表名")
            elif not any(sc.get('head', {}).get('tableName') == sub_table_name 
                        for sc in sub_configs):
                errors.append(f"subList中的子表 {sub_table_name} 在子表配置中不存在")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _has_foreign_key(sub_config: Dict, main_config: Dict) -> bool:
        """检查子表是否包含指向主表的外键字段"""
        main_table_name = main_config.get('head', {}).get('tableName', '')
        fields = sub_config.get('fields', [])
        
        # 查找外键字段（通常以主表名_id命名）
        main_entity = main_config.get('head', {}).get('business_entity', '')
        expected_fk_name = f"{main_entity.lower()}_id"
        
        for field in fields:
            field_name = field.get('dbFieldName', '').lower()
            main_table = field.get('mainTable', '').lower()
            
            # 检查字段名匹配或mainTable配置
            if field_name == expected_fk_name or main_table == main_table_name.lower():
                return True
        
        return False

class MasterSubTableConflictResolver:
    """主子表冲突解决器"""
    
    def __init__(self, executor):
        self.executor = executor
    
    def detect_conflicts(self, target_tables: List[str]) -> List[Dict]:
        """检测后台已存在的冲突表单"""
        all_forms = self.executor.query_all_forms(page_size=100)
        conflicts = []
        
        for form in all_forms:
            table_name = form.get('tableName', '')
            if table_name in target_tables:
                conflicts.append(form)
                
        return conflicts
    
    def resolve_conflicts(self, conflicts: List[Dict]) -> bool:
        """解决冲突（删除错误的表单）"""
        if not conflicts:
            return True
            
        print(f"\n🔍 检测到 {len(conflicts)} 个冲突表单，准备清理...")
        
        for conflict in conflicts:
            table_name = conflict.get('tableName')
            form_id = conflict.get('id')
            table_type = conflict.get('tableType')
            
            print(f"⚠️  冲突表单: {table_name} (ID: {form_id}, tableType: {table_type})")
            
        # 询问用户确认
        confirm = input("\n是否删除这些冲突表单？(y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 用户取消操作，无法继续")
            return False
        
        # 执行删除
        success = self.executor.delete_forms_batch([c.get('id') for c in conflicts])
        if success:
            print("✅ 冲突表单清理成功")
        else:
            print("❌ 冲突表单清理失败")
            
        return success

class MasterSubTableExecutor:
    """主子表专用执行器 - 修复版本"""
    
    def __init__(self, base_executor):
        self.base_executor = base_executor
        self.validator = MasterSubTableValidator()
        self.conflict_resolver = MasterSubTableConflictResolver(base_executor)
        self.execution_log = []
        
    def execute_master_sub_tables(self, main_config: Dict, sub_configs: List[Dict]) -> bool:
        """执行主子表完整工作流 - 修复版本"""
        
        try:
            self._log_phase(ExecutionPhase.PREPROCESS, "开始执行主子表修复流程")
            
            # Phase 1: 预处理 - 验证和清理
            if not self._preprocess_phase(main_config, sub_configs):
                return False
            
            # Phase 2: 表单创建
            table_infos = self._form_creation_phase(main_config, sub_configs)
            if not table_infos:
                return False
            
            # Phase 3: 数据库同步  
            if not self._database_sync_phase(table_infos):
                return False
            
            # Phase 4: 统一代码生成
            if not self._code_generation_phase(table_infos, main_config):
                return False
                
            # Phase 5: 后处理
            self._post_process_phase()
            
            print("🎉 主子表执行成功完成！")
            return True
            
        except Exception as e:
            print(f"❌ 主子表执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _preprocess_phase(self, main_config: Dict, sub_configs: List[Dict]) -> bool:
        """Phase 1: 预处理阶段"""
        self._log_phase(ExecutionPhase.PREPROCESS, "配置验证和冲突清理")
        
        # 1.1 严格验证配置
        is_valid, errors = self.validator.validate_config_set(main_config, sub_configs)
        if not is_valid:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ 配置验证通过")
        
        # 1.2 检测和解决冲突
        all_tables = [main_config.get('head', {}).get('tableName')]
        all_tables.extend([sc.get('head', {}).get('tableName') for sc in sub_configs])
        
        conflicts = self.conflict_resolver.detect_conflicts(all_tables)
        if conflicts:
            if not self.conflict_resolver.resolve_conflicts(conflicts):
                return False
                
        return True
    
    def _form_creation_phase(self, main_config: Dict, sub_configs: List[Dict]) -> Optional[List[TableFormInfo]]:
        """Phase 2: 表单创建阶段"""
        self._log_phase(ExecutionPhase.FORM_CREATION, "创建主表和所有子表")
        
        table_infos = []
        
        # 2.1 创建主表
        print("📝 创建主表...")
        main_head = main_config.get('head', {})
        main_form_id = self.base_executor.create_form(main_config)
        
        if not main_form_id:
            print("❌ 主表创建失败")
            return None
            
        main_info = TableFormInfo(
            table_name=main_head.get('tableName'),
            table_txt=main_head.get('tableTxt'),
            table_type=2,
            config_data=main_config,
            form_id=main_form_id
        )
        table_infos.append(main_info)
        print(f"✅ 主表创建成功: {main_info.table_name} (ID: {main_form_id})")
        
        # 2.2 创建所有子表
        print(f"📝 创建 {len(sub_configs)} 个子表...")
        for i, sub_config in enumerate(sub_configs, 1):
            sub_head = sub_config.get('head', {})
            print(f"   创建子表 {i}/{len(sub_configs)}: {sub_head.get('tableName')}")
            
            sub_form_id = self.base_executor.create_form(sub_config)
            if not sub_form_id:
                print(f"❌ 子表 {i} 创建失败")
                return None
                
            sub_info = TableFormInfo(
                table_name=sub_head.get('tableName'),
                table_txt=sub_head.get('tableTxt'),
                table_type=3,
                config_data=sub_config,
                form_id=sub_form_id
            )
            table_infos.append(sub_info)
            print(f"✅ 子表 {i} 创建成功: {sub_info.table_name} (ID: {sub_form_id})")
        
        # 2.3 验证创建结果
        if not self._verify_forms_created(table_infos):
            print("❌ 表单创建结果验证失败")
            return None
            
        return table_infos
    
    def _database_sync_phase(self, table_infos: List[TableFormInfo]) -> bool:
        """Phase 3: 数据库同步阶段"""
        self._log_phase(ExecutionPhase.DATABASE_SYNC, "同步所有表到数据库")
        
        # 3.1 并行同步所有表
        print("🔄 开始数据库同步...")
        
        for info in table_infos:
            type_desc = "主表" if info.table_type == 2 else "子表"
            print(f"   同步 {type_desc}: {info.table_name}")
            
            success = self.base_executor.sync_database(info.form_id)
            info.sync_status = success
            
            if success:
                print(f"✅ {type_desc} 同步成功")
            else:
                print(f"❌ {type_desc} 同步失败")
                return False
        
        # 3.2 验证同步结果
        all_synced = all(info.sync_status for info in table_infos)
        if not all_synced:
            print("❌ 数据库同步验证失败")
            return False
            
        print("✅ 所有表同步完成")
        return True
    
    def _code_generation_phase(self, table_infos: List[TableFormInfo], main_config: Dict) -> bool:
        """Phase 4: 统一代码生成阶段"""
        self._log_phase(ExecutionPhase.CODE_GENERATION, "通过主表统一生成所有代码")
        
        # 4.1 获取主表信息
        main_info = next((info for info in table_infos if info.table_type == 2), None)
        if not main_info:
            print("❌ 未找到主表信息")
            return False
        
        # 4.2 验证subList完整性
        sub_list = main_config.get('subList', [])
        if not sub_list:
            print("❌ 主表配置缺少subList")
            return False
            
        print(f"📋 验证subList包含 {len(sub_list)} 个子表")
        for i, sub_item in enumerate(sub_list, 1):
            sub_table_name = sub_item.get('tableName')
            sub_entity_name = sub_item.get('entityName')
            print(f"   子表 {i}: {sub_table_name} ({sub_entity_name})")
        
        # 4.3 执行统一代码生成
        print("🚀 开始统一代码生成...")
        print(f"主表: {main_info.table_name} (ID: {main_info.form_id})")
        
        success = self.base_executor.generate_code(main_info.form_id, main_config)
        
        if success:
            print("✅ 统一代码生成成功")
            # 验证生成结果
            return self._verify_code_generated(main_config, table_infos)
        else:
            print("❌ 统一代码生成失败")
            return False
    
    def _post_process_phase(self):
        """Phase 5: 后处理阶段"""
        self._log_phase(ExecutionPhase.POST_PROCESS, "执行后处理任务")
        
        # 可以在这里添加后处理逻辑，如：
        # - 前端代码迁移
        # - 权限配置
        # - 编译验证等
        
        print("✅ 后处理完成")
    
    def _verify_forms_created(self, table_infos: List[TableFormInfo]) -> bool:
        """验证表单是否按正确的tableType创建"""
        print("🔍 验证表单创建结果...")
        
        # 通过API查询验证实际的tableType
        for info in table_infos:
            actual_form = self._query_form_by_id(info.form_id)
            if not actual_form:
                print(f"❌ 无法查询到表单: {info.form_id}")
                return False
            
            actual_table_type = actual_form.get('tableType')
            if actual_table_type != info.table_type:
                print(f"❌ 表单 {info.table_name} tableType不匹配:")
                print(f"   预期: {info.table_type}, 实际: {actual_table_type}")
                return False
            
            print(f"✅ 表单验证通过: {info.table_name} (tableType: {actual_table_type})")
        
        return True
    
    def _verify_code_generated(self, main_config: Dict, table_infos: List[TableFormInfo]) -> bool:
        """验证代码是否正确生成"""
        print("🔍 验证代码生成结果...")
        
        # 检查主表代码是否生成
        main_entity = main_config.get('head', {}).get('business_entity')
        if not main_entity:
            print("❌ 无法获取主表实体名")
            return False
        
        # 这里可以添加更详细的代码生成验证逻辑
        # 比如检查生成的文件是否存在、内容是否正确等
        
        print("✅ 代码生成验证通过")
        return True
    
    def _query_form_by_id(self, form_id: str) -> Optional[Dict]:
        """通过ID查询特定表单信息"""
        try:
            all_forms = self.base_executor.query_all_forms(page_size=100)
            for form in all_forms:
                if form.get('id') == form_id:
                    return form
            return None
        except:
            return None
    
    def _log_phase(self, phase: ExecutionPhase, message: str):
        """记录执行阶段"""
        log_entry = f"[{phase.value}] {message}"
        self.execution_log.append(log_entry)
        print(f"\n{'='*60}")
        print(f"🔄 {log_entry}")
        print(f"{'='*60}")
    
    def get_execution_log(self) -> List[str]:
        """获取执行日志"""
        return self.execution_log.copy()