#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContextDev to CodeGen Data Mapper
实现ContextDev架构信息到CodeGen三核心变量的精确映射
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ContextDevCodeGenMapper:
    """ContextDev到CodeGen的数据映射器"""
    
    def __init__(self):
        """初始化映射器"""
        # 业务领域到模块的映射规则
        self.domain_module_mapping = {
            'finance': ['finance', 'financial', 'money', 'payment', 'billing', 'invoice'],
            'hrms': ['hr', 'human', 'employee', 'staff', 'personnel', 'workforce'],
            'crm': ['customer', 'client', 'crm', 'sales', 'marketing', 'lead'],
            'scm': ['supply', 'inventory', 'warehouse', 'stock', 'procurement', 'vendor'],
            'oa': ['office', 'workflow', 'approval', 'document', 'meeting', 'schedule'],
            'healthcare': ['health', 'medical', 'patient', 'doctor', 'hospital', 'clinic'],
            'education': ['education', 'school', 'student', 'teacher', 'course', 'exam'],
            'manufacturing': ['production', 'factory', 'manufacturing', 'assembly', 'quality']
        }
        
        # 实体名称到子模块的映射规则
        self.entity_submodule_mapping = {
            'product': ['product', 'item', 'goods', 'merchandise'],
            'order': ['order', 'purchase', 'sale', 'transaction'],
            'customer': ['customer', 'client', 'user', 'member', 'account'],
            'invoice': ['invoice', 'bill', 'receipt', 'payment'],
            'employee': ['employee', 'staff', 'worker', 'personnel'],
            'department': ['department', 'division', 'unit', 'team'],
            'project': ['project', 'task', 'assignment', 'work'],
            'contract': ['contract', 'agreement', 'deal', 'arrangement'],
            'report': ['report', 'analysis', 'summary', 'statistics'],
            'management': ['management', 'admin', 'control', 'system']
        }
        
        # 禁止的模块名称
        self.forbidden_modules = [
            'system', 'admin', 'user', 'role', 'permission', 'auth',
            'department', 'menu', 'dict', 'config', 'log', 'message'
        ]
        
    def map_architecture_to_codegen(self, architecture_info: Dict) -> List[Dict]:
        """
        将ContextDev架构信息映射为CodeGen生成需求
        
        Args:
            architecture_info: ContextDev架构信息
            
        Returns:
            CodeGen生成需求列表
        """
        logger.info("开始映射ContextDev架构信息到CodeGen格式")
        
        entities = architecture_info.get('entities', [])
        system_context = architecture_info.get('system_context', {})
        
        generation_requirements = []
        
        for entity in entities:
            try:
                requirement = self._map_single_entity(entity, system_context)
                if requirement:
                    generation_requirements.append(requirement)
            except Exception as e:
                logger.error(f"映射实体 {entity.get('name', '')} 失败: {e}")
                continue
        
        logger.info(f"架构映射完成: {len(generation_requirements)}个生成需求")
        return generation_requirements
    
    def _map_single_entity(self, entity: Dict, system_context: Dict) -> Optional[Dict]:
        """
        映射单个实体
        
        Args:
            entity: 实体信息
            system_context: 系统上下文
            
        Returns:
            CodeGen生成需求
        """
        entity_name = entity.get('name', '')
        if not entity_name:
            logger.warning("实体名称为空，跳过映射")
            return None
        
        # 提取三核心变量
        variables = self._extract_core_variables(entity, system_context)
        
        # 验证变量合规性
        if not self._validate_variables(variables):
            logger.warning(f"实体 {entity_name} 的变量验证失败，跳过映射")
            return None
        
        # 构建表名
        table_name = self._build_table_name(variables)
        
        # 映射业务字段
        business_fields = self._map_business_fields(entity.get('fields', []))
        
        # 确定生成类型
        generation_type = self._determine_generation_type(entity)
        
        # 评估定制化级别
        customization_level = self._evaluate_customization_level(entity)
        
        return {
            'entity_name': entity_name,
            'table_name': table_name,
            'generation_type': generation_type,
            'business_fields': business_fields,
            'customization_level': customization_level,
            'module_variables': variables,
            'entity_metadata': {
                'description': entity.get('description', ''),
                'relationships': entity.get('relationships', []),
                'business_rules': entity.get('business_rules', [])
            }
        }
    
    def _extract_core_variables(self, entity: Dict, system_context: Dict) -> Dict:
        """
        提取三核心变量
        
        Args:
            entity: 实体信息
            system_context: 系统上下文
            
        Returns:
            三核心变量字典
        """
        entity_name = entity.get('name', '')
        business_domain = system_context.get('business_domain', '')
        
        # 1. 推理MODULE_NAME
        module_name = self._infer_module_name(business_domain, entity_name, entity)
        
        # 2. 推理SUBMODULE_NAME
        submodule_name = self._infer_submodule_name(entity_name, entity)
        
        # 3. 确定BUSINESS_ENTITY (使用PascalCase格式)
        business_entity = self._normalize_business_entity(entity_name)
        
        return {
            'MODULE_NAME': module_name,
            'SUBMODULE_NAME': submodule_name,
            'BUSINESS_ENTITY': business_entity
        }
    
    def _infer_module_name(self, business_domain: str, entity_name: str, entity: Dict) -> str:
        """
        推理MODULE_NAME
        
        Args:
            business_domain: 业务领域
            entity_name: 实体名称
            entity: 实体完整信息
            
        Returns:
            模块名称
        """
        # 优先基于业务领域推理
        domain_lower = business_domain.lower()
        for module, keywords in self.domain_module_mapping.items():
            if any(keyword in domain_lower for keyword in keywords):
                if module not in self.forbidden_modules:
                    return module
        
        # 基于实体名称推理
        entity_lower = entity_name.lower()
        for module, keywords in self.domain_module_mapping.items():
            if any(keyword in entity_lower for keyword in keywords):
                if module not in self.forbidden_modules:
                    return module
        
        # 基于实体描述推理
        description = entity.get('description', '').lower()
        for module, keywords in self.domain_module_mapping.items():
            if any(keyword in description for keyword in keywords):
                if module not in self.forbidden_modules:
                    return module
        
        # 默认返回business
        return 'business'
    
    def _infer_submodule_name(self, entity_name: str, entity: Dict) -> str:
        """
        推理SUBMODULE_NAME
        
        Args:
            entity_name: 实体名称
            entity: 实体完整信息
            
        Returns:
            子模块名称
        """
        entity_lower = entity_name.lower()
        
        # 基于实体名称推理
        for submodule, keywords in self.entity_submodule_mapping.items():
            if any(keyword in entity_lower for keyword in keywords):
                return submodule
        
        # 基于实体描述推理
        description = entity.get('description', '').lower()
        for submodule, keywords in self.entity_submodule_mapping.items():
            if any(keyword in description for keyword in keywords):
                return submodule
        
        # 基于实体功能推理
        business_rules = entity.get('business_rules', [])
        if business_rules:
            rules_text = ' '.join([rule.get('description', '') for rule in business_rules]).lower()
            for submodule, keywords in self.entity_submodule_mapping.items():
                if any(keyword in rules_text for keyword in keywords):
                    return submodule
        
        # 默认返回management
        return 'management'
    
    def _normalize_business_entity(self, entity_name: str) -> str:
        """
        规范化BUSINESS_ENTITY为PascalCase格式
        
        Args:
            entity_name: 原始实体名称
            
        Returns:
            PascalCase格式的实体名称
        """
        # 移除特殊字符，只保留字母和数字
        clean_name = re.sub(r'[^a-zA-Z0-9]', ' ', entity_name)
        
        # 分割单词并转换为PascalCase
        words = clean_name.split()
        pascal_case = ''.join([word.capitalize() for word in words if word])
        
        # 确保首字母大写
        if pascal_case and not pascal_case[0].isupper():
            pascal_case = pascal_case[0].upper() + pascal_case[1:]
        
        return pascal_case if pascal_case else 'Entity'
    
    def _validate_variables(self, variables: Dict) -> bool:
        """
        验证三核心变量的合规性
        
        Args:
            variables: 三核心变量
            
        Returns:
            验证结果
        """
        module_name = variables.get('MODULE_NAME', '').lower()
        submodule_name = variables.get('SUBMODULE_NAME', '').lower()
        business_entity = variables.get('BUSINESS_ENTITY', '')
        
        # 检查禁止的模块名称
        if module_name in self.forbidden_modules:
            logger.warning(f"模块名称 {module_name} 在禁止列表中")
            return False
        
        # 检查命名规范
        if not module_name.islower() or not module_name.isalpha():
            logger.warning(f"模块名称 {module_name} 不符合小写字母规范")
            return False
        
        if not submodule_name.islower() or not submodule_name.isalpha():
            logger.warning(f"子模块名称 {submodule_name} 不符合小写字母规范")
            return False
        
        if not business_entity or not business_entity[0].isupper():
            logger.warning(f"业务实体 {business_entity} 不符合PascalCase规范")
            return False
        
        return True
    
    def _build_table_name(self, variables: Dict) -> str:
        """
        构建表名
        
        Args:
            variables: 三核心变量
            
        Returns:
            表名
        """
        module_name = variables.get('MODULE_NAME', '').lower()
        submodule_name = variables.get('SUBMODULE_NAME', '').lower()
        business_entity = variables.get('BUSINESS_ENTITY', '').lower()
        
        return f"us_{module_name}_{submodule_name}_{business_entity}"
    
    def _map_business_fields(self, fields: List[Dict]) -> List[Dict]:
        """
        映射业务字段
        
        Args:
            fields: ContextDev字段列表
            
        Returns:
            CodeGen字段列表
        """
        mapped_fields = []
        
        for field in fields:
            mapped_field = self._map_single_field(field)
            if mapped_field:
                mapped_fields.append(mapped_field)
        
        return mapped_fields
    
    def _map_single_field(self, field: Dict) -> Optional[Dict]:
        """
        映射单个字段
        
        Args:
            field: ContextDev字段信息
            
        Returns:
            CodeGen字段信息
        """
        field_name = field.get('name', '')
        field_type = field.get('type', 'string')
        
        if not field_name:
            return None
        
        # 映射字段类型
        codegen_type = self._map_field_type(field_type)
        
        return {
            'name': field_name,
            'type': codegen_type,
            'required': field.get('required', False),
            'description': field.get('description', ''),
            'constraints': field.get('constraints', {})
        }
    
    def _map_field_type(self, context_type: str) -> str:
        """
        映射字段类型
        
        Args:
            context_type: ContextDev字段类型
            
        Returns:
            CodeGen字段类型
        """
        type_mapping = {
            'string': 'string',
            'text': 'text',
            'integer': 'integer',
            'decimal': 'decimal',
            'boolean': 'boolean',
            'date': 'date',
            'datetime': 'datetime',
            'timestamp': 'datetime'
        }
        
        return type_mapping.get(context_type.lower(), 'string')
    
    def _determine_generation_type(self, entity: Dict) -> str:
        """
        确定代码生成类型
        
        Args:
            entity: 实体信息
            
        Returns:
            生成类型
        """
        relationships = entity.get('relationships', [])
        
        # 检查是否有树形结构
        for rel in relationships:
            if rel.get('type') == 'self_reference' or rel.get('type') == 'parent_child':
                return 'tree'
        
        # 检查是否有一对多关系
        for rel in relationships:
            if rel.get('type') == 'one_to_many':
                return 'one_to_many'
        
        # 默认CRUD
        return 'crud'
    
    def _evaluate_customization_level(self, entity: Dict) -> str:
        """
        评估定制化级别
        
        Args:
            entity: 实体信息
            
        Returns:
            定制化级别
        """
        business_rules = entity.get('business_rules', [])
        relationships = entity.get('relationships', [])
        
        # 复杂业务规则或多个关系需要高级定制
        if len(business_rules) > 3 or len(relationships) > 2:
            return 'advanced'
        elif len(business_rules) > 1 or len(relationships) > 0:
            return 'intermediate'
        else:
            return 'basic'
    
    def validate_mapping_result(self, generation_requirements: List[Dict]) -> Tuple[bool, List[str]]:
        """
        验证映射结果
        
        Args:
            generation_requirements: 生成需求列表
            
        Returns:
            (验证结果, 错误信息列表)
        """
        errors = []
        
        if not generation_requirements:
            errors.append("没有生成任何CodeGen需求")
            return False, errors
        
        # 检查重复的表名
        table_names = [req.get('table_name') for req in generation_requirements]
        duplicates = [name for name in table_names if table_names.count(name) > 1]
        if duplicates:
            errors.append(f"发现重复的表名: {list(set(duplicates))}")
        
        # 检查每个需求的完整性
        for i, req in enumerate(generation_requirements):
            if not req.get('entity_name'):
                errors.append(f"需求 {i+1} 缺少entity_name")
            if not req.get('table_name'):
                errors.append(f"需求 {i+1} 缺少table_name")
            if not req.get('module_variables'):
                errors.append(f"需求 {i+1} 缺少module_variables")
        
        return len(errors) == 0, errors
