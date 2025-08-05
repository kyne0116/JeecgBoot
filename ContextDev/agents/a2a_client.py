#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContextDev Agent-5 A2A Protocol Client
实现与CodeGen系统的Agent-to-Agent协议通信
"""

import json
import uuid
import requests
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2AProtocolClient:
    """A2A协议客户端 - ContextDev agent-5专用"""
    
    def __init__(self, codegen_endpoint: str = "http://localhost:8888/codegen/a2a"):
        """
        初始化A2A协议客户端
        
        Args:
            codegen_endpoint: CodeGen系统的A2A协议端点
        """
        self.codegen_endpoint = codegen_endpoint
        self.protocol_version = "1.0"
        self.source_agent = "ContextDev-agent-5"
        self.target_agent = "codegen-expert"
        
    def evaluate_codegen_applicability(self, architecture_info: Dict) -> Tuple[List[Dict], List[Dict]]:
        """
        评估架构组件的CodeGen适用性
        
        Args:
            architecture_info: 来自agent-4的架构信息
            
        Returns:
            Tuple[适用组件列表, 手动开发组件列表]
        """
        applicable_components = []
        manual_components = []
        
        entities = architecture_info.get('entities', [])
        
        for entity in entities:
            complexity_score = self._calculate_complexity(entity)
            
            if complexity_score <= 0.7:  # 简单组件
                applicable_components.append({
                    'entity': entity,
                    'confidence': 0.9,
                    'generation_type': 'crud',
                    'complexity_score': complexity_score
                })
            elif complexity_score <= 0.9:  # 中等组件
                applicable_components.append({
                    'entity': entity,
                    'confidence': 0.7,
                    'generation_type': 'crud_with_customization',
                    'complexity_score': complexity_score
                })
            else:  # 复杂组件
                manual_components.append({
                    'entity': entity,
                    'reason': 'High complexity requires manual development',
                    'complexity_score': complexity_score
                })
                
        logger.info(f"CodeGen适用性评估完成: {len(applicable_components)}个适用, {len(manual_components)}个手动")
        return applicable_components, manual_components
    
    def _calculate_complexity(self, entity: Dict) -> float:
        """
        计算实体的复杂度评分
        
        Args:
            entity: 实体信息
            
        Returns:
            复杂度评分 (0.0-1.0)
        """
        complexity = 0.0
        
        # 基于字段数量
        fields = entity.get('fields', [])
        field_count = len(fields)
        if field_count > 10:
            complexity += 0.3
        elif field_count > 5:
            complexity += 0.2
        else:
            complexity += 0.1
            
        # 基于关系复杂度
        relationships = entity.get('relationships', [])
        if len(relationships) > 3:
            complexity += 0.4
        elif len(relationships) > 1:
            complexity += 0.2
        else:
            complexity += 0.1
            
        # 基于业务规则复杂度
        business_rules = entity.get('business_rules', [])
        if len(business_rules) > 5:
            complexity += 0.3
        elif len(business_rules) > 2:
            complexity += 0.2
        else:
            complexity += 0.1
            
        return min(complexity, 1.0)
    
    def build_a2a_request(self, applicable_components: List[Dict], system_context: Dict) -> Dict:
        """
        构建A2A协议请求
        
        Args:
            applicable_components: 适用的组件列表
            system_context: 系统上下文信息
            
        Returns:
            A2A协议请求消息
        """
        correlation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        request = {
            'a2a_protocol': {
                'version': self.protocol_version,
                'source_agent': self.source_agent,
                'target_agent': self.target_agent,
                'message_type': 'code_generation_request',
                'timestamp': timestamp,
                'correlation_id': correlation_id
            },
            'payload': {
                'system_context': {
                    'system_name': system_context.get('system_name', ''),
                    'module_name': system_context.get('module_name', ''),
                    'business_domain': system_context.get('business_domain', '')
                },
                'architecture_info': system_context.get('architecture_info', {}),
                'generation_requirements': [],
                'quality_requirements': {
                    'code_coverage': '80%',
                    'performance_requirements': ['响应时间 < 2秒'],
                    'integration_points': ['JeecgBoot API兼容']
                }
            }
        }
        
        # 转换组件为生成需求
        for comp in applicable_components:
            entity = comp['entity']
            requirement = self._map_component_to_codegen(entity, comp)
            request['payload']['generation_requirements'].append(requirement)
            
        logger.info(f"A2A请求构建完成: {len(applicable_components)}个生成需求")
        return request
    
    def _map_component_to_codegen(self, entity: Dict, component: Dict) -> Dict:
        """
        将ContextDev组件映射为CodeGen生成需求
        
        Args:
            entity: 实体信息
            component: 组件信息
            
        Returns:
            CodeGen生成需求
        """
        entity_name = entity.get('name', '')
        
        # 智能推理三核心变量
        module_name = self._infer_module_name(entity)
        submodule_name = self._infer_submodule_name(entity)
        business_entity = entity_name
        
        # 构建表名
        table_name = f"us_{module_name}_{submodule_name}_{entity_name.lower()}"
        
        return {
            'entity_name': entity_name,
            'table_name': table_name,
            'generation_type': component.get('generation_type', 'crud'),
            'business_fields': entity.get('fields', []),
            'customization_level': 'basic' if component.get('confidence', 0) > 0.8 else 'advanced',
            'module_variables': {
                'MODULE_NAME': module_name,
                'SUBMODULE_NAME': submodule_name,
                'BUSINESS_ENTITY': business_entity
            }
        }
    
    def _infer_module_name(self, entity: Dict) -> str:
        """推理MODULE_NAME"""
        domain = entity.get('domain', '').lower()
        if 'finance' in domain or 'financial' in domain:
            return 'finance'
        elif 'hr' in domain or 'human' in domain:
            return 'hrms'
        elif 'customer' in domain or 'crm' in domain:
            return 'crm'
        else:
            return 'business'
    
    def _infer_submodule_name(self, entity: Dict) -> str:
        """推理SUBMODULE_NAME"""
        name = entity.get('name', '').lower()
        if 'product' in name:
            return 'product'
        elif 'order' in name:
            return 'order'
        elif 'user' in name or 'customer' in name:
            return 'customer'
        elif 'invoice' in name:
            return 'invoice'
        else:
            return 'management'
    
    def invoke_codegen_agent(self, a2a_request: Dict) -> Dict:
        """
        调用CodeGen Agent执行代码生成
        
        Args:
            a2a_request: A2A协议请求
            
        Returns:
            CodeGen响应结果
            
        Raises:
            Exception: A2A协议调用失败时抛出异常，触发严格异常处理
        """
        try:
            logger.info(f"开始调用CodeGen Agent: {self.codegen_endpoint}")
            
            # 发送A2A协议请求
            response = requests.post(
                self.codegen_endpoint,
                json=a2a_request,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"A2A协议调用失败: HTTP {response.status_code} - {response.text}")
            
            response_data = response.json()
            
            # 验证响应格式
            if not self._validate_a2a_response(response_data):
                raise Exception("A2A协议响应格式无效")
            
            return self._parse_codegen_response(response_data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"A2A协议网络调用失败: {e}")
            raise Exception(f"A2A协议网络调用失败: {e}")
        except Exception as e:
            logger.error(f"A2A协议调用异常: {e}")
            raise Exception(f"A2A协议调用异常: {e}")
    
    def _validate_a2a_response(self, response: Dict) -> bool:
        """验证A2A协议响应格式"""
        required_fields = ['a2a_protocol', 'payload']
        return all(field in response for field in required_fields)
    
    def _parse_codegen_response(self, response: Dict) -> Dict:
        """
        解析CodeGen响应
        
        Args:
            response: CodeGen A2A协议响应
            
        Returns:
            解析后的响应结果
        """
        payload = response.get('payload', {})
        generation_results = payload.get('generation_results', [])
        
        successful_generations = []
        failed_generations = []
        
        for result in generation_results:
            if result.get('status') == 'success':
                successful_generations.append(result)
            else:
                failed_generations.append(result)
        
        overall_success_rate = len(successful_generations) / len(generation_results) if generation_results else 0
        
        logger.info(f"CodeGen响应解析完成: {len(successful_generations)}成功, {len(failed_generations)}失败")
        
        return {
            'successful': successful_generations,
            'failed': failed_generations,
            'overall_success_rate': overall_success_rate,
            'execution_status': payload.get('execution_status', {}),
            'post_generation_tasks': payload.get('post_generation_tasks', {})
        }
    
    def handle_strict_failure(self, error: Exception, request: Dict) -> Dict:
        """
        严格异常处理 - A2A协议失败时立即终止工作流
        
        Args:
            error: 异常信息
            request: 原始请求
            
        Returns:
            严格失败处理结果
        """
        logger.error(f"A2A协议调用失败，执行严格异常处理: {error}")
        
        return {
            'status': 'WORKFLOW_TERMINATED',
            'error_type': 'A2A_PROTOCOL_FAILURE',
            'error_message': str(error),
            'termination_reason': 'A2A协议调用失败，根据严格异常处理策略立即终止6-Agent工作流',
            'user_confirmation_required': True,
            'failed_request': request,
            'next_action': 'REQUEST_USER_CONFIRMATION'
        }
