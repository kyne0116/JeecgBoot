#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContextDev Agent-5 Controller
实现开发工程师的完整工作流程，包含A2A协议集成
"""

import yaml
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from a2a_client import A2AProtocolClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent5Controller:
    """ContextDev Agent-5 开发工程师控制器"""
    
    def __init__(self, codegen_endpoint: str = "http://localhost:8888/codegen/a2a"):
        """
        初始化Agent-5控制器
        
        Args:
            codegen_endpoint: CodeGen系统A2A协议端点
        """
        self.agent_name = "agent-5"
        self.agent_version = "6.0"
        self.a2a_client = A2AProtocolClient(codegen_endpoint)
        
    def execute_development_planning(self, architecture_document: Dict) -> Dict:
        """
        执行包含A2A集成的开发规划
        
        Args:
            architecture_document: 来自agent-4的架构文档
            
        Returns:
            开发规划文档
        """
        logger.info("开始执行Agent-5开发规划工作流")
        
        try:
            # Step 1: 架构解析
            architecture_analysis = self._parse_architecture_document(architecture_document)
            
            # Step 2: 任务分解
            development_tasks = self._decompose_development_tasks(architecture_analysis)
            
            # Step 3: 实施策略推理
            implementation_strategy = self._reason_implementation_strategy(development_tasks)
            
            # Step 4: A2A协议代码生成
            a2a_execution_result = self._execute_a2a_codegen(architecture_analysis)
            
            # 检查A2A执行状态
            if a2a_execution_result.get('status') == 'WORKFLOW_TERMINATED':
                # 严格异常处理：立即终止工作流
                return self._handle_workflow_termination(a2a_execution_result)
            
            # Step 5: 文档生成
            development_document = self._generate_development_document({
                'architecture_analysis': architecture_analysis,
                'development_tasks': development_tasks,
                'implementation_strategy': implementation_strategy,
                'a2a_execution_result': a2a_execution_result
            })
            
            logger.info("Agent-5开发规划工作流执行完成")
            return development_document
            
        except Exception as e:
            logger.error(f"Agent-5工作流执行异常: {e}")
            return self._handle_general_exception(e, architecture_document)
    
    def _parse_architecture_document(self, arch_doc: Dict) -> Dict:
        """
        解析架构文档
        
        Args:
            arch_doc: 架构文档
            
        Returns:
            架构解析结果
        """
        logger.info("开始解析架构文档")
        
        # 提取核心架构信息
        system_architecture = arch_doc.get('system_architecture', {})
        data_model = arch_doc.get('data_model', {})
        
        # 识别开发组件
        entities = data_model.get('entities', [])
        services = system_architecture.get('services', [])
        apis = system_architecture.get('apis', [])
        
        # 分析组件依赖关系
        dependencies = self._analyze_component_dependencies(entities, services)
        
        # 评估开发复杂度
        complexity_analysis = self._evaluate_development_complexity(entities, services, apis)
        
        return {
            'source_document': arch_doc.get('document_info', {}),
            'system_context': {
                'system_name': arch_doc.get('document_info', {}).get('system_name', ''),
                'module_name': arch_doc.get('document_info', {}).get('module_name', ''),
                'business_domain': arch_doc.get('business_core', {}).get('domain', '')
            },
            'entities': entities,
            'services': services,
            'apis': apis,
            'dependencies': dependencies,
            'complexity_analysis': complexity_analysis
        }
    
    def _analyze_component_dependencies(self, entities: List[Dict], services: List[Dict]) -> Dict:
        """分析组件依赖关系"""
        dependencies = {
            'entity_relationships': [],
            'service_dependencies': [],
            'critical_path': []
        }
        
        # 分析实体关系
        for entity in entities:
            relationships = entity.get('relationships', [])
            for rel in relationships:
                dependencies['entity_relationships'].append({
                    'from': entity.get('name'),
                    'to': rel.get('target'),
                    'type': rel.get('type')
                })
        
        return dependencies
    
    def _evaluate_development_complexity(self, entities: List[Dict], services: List[Dict], apis: List[Dict]) -> Dict:
        """评估开发复杂度"""
        return {
            'entity_complexity': len(entities),
            'service_complexity': len(services),
            'api_complexity': len(apis),
            'overall_complexity': 'medium'  # 简化评估
        }
    
    def _decompose_development_tasks(self, architecture_analysis: Dict) -> Dict:
        """分解开发任务"""
        logger.info("开始分解开发任务")
        
        entities = architecture_analysis.get('entities', [])
        services = architecture_analysis.get('services', [])
        apis = architecture_analysis.get('apis', [])
        
        # 按层次分解任务
        backend_tasks = self._decompose_backend_tasks(entities, services, apis)
        frontend_tasks = self._decompose_frontend_tasks(entities)
        database_tasks = self._decompose_database_tasks(entities)
        integration_tasks = self._decompose_integration_tasks(services, apis)
        
        return {
            'backend_tasks': backend_tasks,
            'frontend_tasks': frontend_tasks,
            'database_tasks': database_tasks,
            'integration_tasks': integration_tasks,
            'task_dependencies': self._analyze_task_dependencies(backend_tasks, frontend_tasks, database_tasks)
        }
    
    def _decompose_backend_tasks(self, entities: List[Dict], services: List[Dict], apis: List[Dict]) -> List[Dict]:
        """分解后端任务"""
        tasks = []
        
        for entity in entities:
            tasks.append({
                'type': 'entity_development',
                'entity': entity.get('name'),
                'components': ['Entity', 'Repository', 'Service', 'Controller'],
                'estimated_effort': '2-3天',
                'codegen_applicable': True
            })
        
        return tasks
    
    def _decompose_frontend_tasks(self, entities: List[Dict]) -> List[Dict]:
        """分解前端任务"""
        tasks = []
        
        for entity in entities:
            tasks.append({
                'type': 'frontend_development',
                'entity': entity.get('name'),
                'components': ['List页面', 'Form页面', '详情页面'],
                'estimated_effort': '1-2天',
                'codegen_applicable': True
            })
        
        return tasks
    
    def _decompose_database_tasks(self, entities: List[Dict]) -> List[Dict]:
        """分解数据库任务"""
        tasks = []
        
        for entity in entities:
            tasks.append({
                'type': 'database_development',
                'entity': entity.get('name'),
                'components': ['表结构', '索引', '约束'],
                'estimated_effort': '0.5天',
                'codegen_applicable': True
            })
        
        return tasks
    
    def _decompose_integration_tasks(self, services: List[Dict], apis: List[Dict]) -> List[Dict]:
        """分解集成任务"""
        return [
            {
                'type': 'integration_testing',
                'components': ['API集成测试', '服务集成测试'],
                'estimated_effort': '1天',
                'codegen_applicable': False
            }
        ]
    
    def _analyze_task_dependencies(self, backend_tasks: List[Dict], frontend_tasks: List[Dict], database_tasks: List[Dict]) -> List[Dict]:
        """分析任务依赖关系"""
        dependencies = []
        
        # 数据库任务优先
        for db_task in database_tasks:
            entity = db_task.get('entity')
            # 找到对应的后端任务
            for be_task in backend_tasks:
                if be_task.get('entity') == entity:
                    dependencies.append({
                        'prerequisite': db_task,
                        'dependent': be_task,
                        'type': 'sequential'
                    })
        
        return dependencies
    
    def _reason_implementation_strategy(self, development_tasks: Dict) -> Dict:
        """推理实施策略"""
        logger.info("开始推理实施策略")
        
        # 分析任务复杂度
        total_tasks = (len(development_tasks.get('backend_tasks', [])) + 
                      len(development_tasks.get('frontend_tasks', [])) + 
                      len(development_tasks.get('database_tasks', [])))
        
        # 确定实施策略
        if total_tasks <= 5:
            strategy = 'sequential'  # 顺序开发
        elif total_tasks <= 15:
            strategy = 'parallel'    # 并行开发
        else:
            strategy = 'phased'      # 分阶段开发
        
        return {
            'strategy_type': strategy,
            'estimated_duration': f"{total_tasks * 0.5}天",
            'resource_requirements': '1-2名开发人员',
            'risk_assessment': 'medium',
            'codegen_coverage': '70-80%'
        }
    
    def _execute_a2a_codegen(self, architecture_analysis: Dict) -> Dict:
        """
        执行A2A协议代码生成
        
        Args:
            architecture_analysis: 架构分析结果
            
        Returns:
            A2A执行结果
        """
        logger.info("开始执行A2A协议代码生成")
        
        try:
            # Step 1: 评估CodeGen适用性
            applicable_components, manual_components = self.a2a_client.evaluate_codegen_applicability(architecture_analysis)
            
            if not applicable_components:
                logger.info("没有适用CodeGen的组件，跳过A2A调用")
                return {
                    'status': 'SKIPPED',
                    'reason': '没有适用CodeGen的组件',
                    'manual_components': manual_components
                }
            
            # Step 2: 构建A2A请求
            a2a_request = self.a2a_client.build_a2a_request(applicable_components, architecture_analysis['system_context'])
            
            # Step 3: 调用CodeGen Agent
            codegen_response = self.a2a_client.invoke_codegen_agent(a2a_request)
            
            # Step 4: 规划后续任务
            post_tasks = self._plan_post_generation_tasks(codegen_response, manual_components)
            
            return {
                'status': 'SUCCESS',
                'applicable_components': applicable_components,
                'manual_components': manual_components,
                'codegen_response': codegen_response,
                'post_generation_tasks': post_tasks
            }
            
        except Exception as e:
            # 严格异常处理：A2A协议调用失败时立即终止工作流
            logger.error(f"A2A协议调用失败: {e}")
            return self.a2a_client.handle_strict_failure(e, architecture_analysis)
    
    def _plan_post_generation_tasks(self, codegen_response: Dict, manual_components: List[Dict]) -> Dict:
        """规划代码生成后的任务"""
        post_tasks = {
            'customization_tasks': [],
            'manual_development_tasks': [],
            'integration_tasks': [],
            'testing_tasks': []
        }
        
        # 处理成功生成的组件
        for success in codegen_response.get('successful', []):
            customization_needs = success.get('customization_needs', [])
            if customization_needs:
                post_tasks['customization_tasks'].append({
                    'component': success.get('entity'),
                    'customizations': customization_needs,
                    'priority': 'high'
                })
        
        # 处理失败的组件
        for failed in codegen_response.get('failed', []):
            post_tasks['manual_development_tasks'].append({
                'component': failed.get('entity'),
                'reason': failed.get('error_message', 'CodeGen生成失败'),
                'development_approach': 'manual',
                'priority': 'high'
            })
        
        # 处理手动开发组件
        for manual in manual_components:
            post_tasks['manual_development_tasks'].append({
                'component': manual.get('entity', {}).get('name'),
                'reason': manual.get('reason'),
                'development_approach': 'manual',
                'priority': 'medium'
            })
        
        return post_tasks
    
    def _generate_development_document(self, planning_data: Dict) -> Dict:
        """生成开发文档"""
        logger.info("开始生成开发文档")
        
        timestamp = datetime.now().isoformat()
        
        return {
            'document_info': {
                'id': f"DEV-{timestamp}",
                'title': '开发实施计划',
                'agent': self.agent_name,
                'version': self.agent_version,
                'timestamp': timestamp
            },
            'input_analysis': planning_data['architecture_analysis'],
            'development_tasks': planning_data['development_tasks'],
            'a2a_codegen_execution': planning_data['a2a_execution_result'],
            'implementation_reasoning': planning_data['implementation_strategy'],
            'agent_handoff': {
                'next_agent': 'agent-6',
                'handoff_data': {
                    'test_targets': self._prepare_test_targets(planning_data),
                    'quality_requirements': self._prepare_quality_requirements(planning_data)
                }
            }
        }
    
    def _prepare_test_targets(self, planning_data: Dict) -> Dict:
        """准备测试目标"""
        a2a_result = planning_data.get('a2a_execution_result', {})
        
        if a2a_result.get('status') == 'SUCCESS':
            codegen_response = a2a_result.get('codegen_response', {})
            successful_components = [comp.get('entity') for comp in codegen_response.get('successful', [])]
            
            return {
                'generated_components': successful_components,
                'manual_components': [comp.get('component') for comp in a2a_result.get('post_generation_tasks', {}).get('manual_development_tasks', [])],
                'integration_points': ['API接口', '数据库连接', '前后端集成']
            }
        else:
            return {
                'generated_components': [],
                'manual_components': [],
                'integration_points': []
            }
    
    def _prepare_quality_requirements(self, planning_data: Dict) -> Dict:
        """准备质量要求"""
        return {
            'code_coverage': '≥80%',
            'performance_requirements': ['响应时间 < 2秒', '并发用户 > 100'],
            'compatibility_requirements': ['JeecgBoot 3.8.1+', 'Vue 3.0+']
        }
    
    def _handle_workflow_termination(self, termination_result: Dict) -> Dict:
        """处理工作流终止"""
        logger.error("A2A协议调用失败，工作流已终止")
        
        return {
            'document_info': {
                'id': f"DEV-TERMINATED-{datetime.now().isoformat()}",
                'title': '开发工作流终止',
                'agent': self.agent_name,
                'status': 'TERMINATED'
            },
            'termination_details': termination_result,
            'user_action_required': {
                'action': 'CONFIRM_CONTINUATION',
                'message': 'A2A协议调用失败，请确认是否继续手动开发流程',
                'options': ['继续手动开发', '重试A2A调用', '终止项目']
            }
        }
    
    def _handle_general_exception(self, error: Exception, context: Dict) -> Dict:
        """处理一般异常"""
        logger.error(f"Agent-5执行异常: {error}")
        
        return {
            'document_info': {
                'id': f"DEV-ERROR-{datetime.now().isoformat()}",
                'title': '开发规划执行异常',
                'agent': self.agent_name,
                'status': 'ERROR'
            },
            'error_details': {
                'error_message': str(error),
                'context': context,
                'recovery_suggestions': [
                    '检查架构文档格式',
                    '验证系统配置',
                    '重新执行工作流'
                ]
            }
        }
