#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContextDev Agent-5 Strict Exception Handler
实现A2A协议调用失败时的严格异常处理机制
"""

import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """工作流状态枚举"""
    RUNNING = "RUNNING"
    TERMINATED = "TERMINATED"
    SUSPENDED = "SUSPENDED"
    ERROR = "ERROR"

class ExceptionType(Enum):
    """异常类型枚举"""
    A2A_PROTOCOL_FAILURE = "A2A_PROTOCOL_FAILURE"
    NETWORK_ERROR = "NETWORK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CODEGEN_API_ERROR = "CODEGEN_API_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class UserAction(Enum):
    """用户操作枚举"""
    CONFIRM_CONTINUATION = "CONFIRM_CONTINUATION"
    RETRY_A2A_CALL = "RETRY_A2A_CALL"
    TERMINATE_PROJECT = "TERMINATE_PROJECT"
    MANUAL_DEVELOPMENT = "MANUAL_DEVELOPMENT"

class StrictExceptionHandler:
    """严格异常处理器 - 实现A2A协议失败时的严格停止策略"""
    
    def __init__(self):
        """初始化异常处理器"""
        self.handler_version = "1.0"
        self.strict_mode = True  # 严格模式：A2A失败时立即终止
        
    def handle_a2a_failure(self, error: Exception, context: Dict) -> Dict:
        """
        处理A2A协议调用失败
        
        Args:
            error: 异常对象
            context: 异常上下文信息
            
        Returns:
            严格异常处理结果
        """
        logger.error(f"A2A协议调用失败，启动严格异常处理: {error}")
        
        # 分类异常类型
        exception_type = self._classify_exception(error)
        
        # 记录异常详情
        exception_details = self._capture_exception_details(error, context, exception_type)
        
        # 立即终止工作流
        termination_result = self._terminate_workflow(exception_details)
        
        # 生成用户确认请求
        user_confirmation = self._generate_user_confirmation(exception_details, termination_result)
        
        # 记录异常日志
        self._log_exception(exception_details, termination_result)
        
        return {
            'status': WorkflowStatus.TERMINATED.value,
            'exception_type': exception_type.value,
            'exception_details': exception_details,
            'termination_result': termination_result,
            'user_confirmation': user_confirmation,
            'strict_mode': self.strict_mode,
            'handler_version': self.handler_version
        }
    
    def _classify_exception(self, error: Exception) -> ExceptionType:
        """
        分类异常类型
        
        Args:
            error: 异常对象
            
        Returns:
            异常类型
        """
        error_message = str(error).lower()
        
        if 'network' in error_message or 'connection' in error_message:
            return ExceptionType.NETWORK_ERROR
        elif 'timeout' in error_message:
            return ExceptionType.TIMEOUT_ERROR
        elif 'validation' in error_message or 'invalid' in error_message:
            return ExceptionType.VALIDATION_ERROR
        elif 'codegen' in error_message or 'api' in error_message:
            return ExceptionType.CODEGEN_API_ERROR
        elif 'a2a' in error_message or 'protocol' in error_message:
            return ExceptionType.A2A_PROTOCOL_FAILURE
        else:
            return ExceptionType.UNKNOWN_ERROR
    
    def _capture_exception_details(self, error: Exception, context: Dict, exception_type: ExceptionType) -> Dict:
        """
        捕获异常详细信息
        
        Args:
            error: 异常对象
            context: 异常上下文
            exception_type: 异常类型
            
        Returns:
            异常详细信息
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'exception_type': exception_type.value,
            'error_message': str(error),
            'error_class': error.__class__.__name__,
            'context': {
                'agent': 'agent-5',
                'workflow_step': 'A2A_PROTOCOL_EXECUTION',
                'system_context': context.get('system_context', {}),
                'architecture_info': context.get('architecture_info', {}),
                'applicable_components': context.get('applicable_components', [])
            },
            'failure_point': 'CodeGen Agent A2A Protocol Call',
            'impact_assessment': self._assess_failure_impact(context),
            'recovery_complexity': self._assess_recovery_complexity(exception_type)
        }
    
    def _assess_failure_impact(self, context: Dict) -> Dict:
        """
        评估失败影响
        
        Args:
            context: 异常上下文
            
        Returns:
            影响评估结果
        """
        applicable_components = context.get('applicable_components', [])
        
        return {
            'affected_components': len(applicable_components),
            'development_impact': 'HIGH' if len(applicable_components) > 5 else 'MEDIUM',
            'timeline_impact': f"预计延迟 {len(applicable_components) * 2} 天",
            'resource_impact': '需要额外的手动开发资源',
            'quality_impact': '可能影响代码一致性和标准化'
        }
    
    def _assess_recovery_complexity(self, exception_type: ExceptionType) -> str:
        """
        评估恢复复杂度
        
        Args:
            exception_type: 异常类型
            
        Returns:
            恢复复杂度
        """
        complexity_mapping = {
            ExceptionType.NETWORK_ERROR: 'LOW',
            ExceptionType.TIMEOUT_ERROR: 'LOW',
            ExceptionType.VALIDATION_ERROR: 'MEDIUM',
            ExceptionType.CODEGEN_API_ERROR: 'HIGH',
            ExceptionType.A2A_PROTOCOL_FAILURE: 'HIGH',
            ExceptionType.UNKNOWN_ERROR: 'VERY_HIGH'
        }
        
        return complexity_mapping.get(exception_type, 'UNKNOWN')
    
    def _terminate_workflow(self, exception_details: Dict) -> Dict:
        """
        立即终止工作流
        
        Args:
            exception_details: 异常详细信息
            
        Returns:
            终止结果
        """
        logger.warning("执行严格异常处理：立即终止6-Agent协作工作流")
        
        return {
            'termination_timestamp': datetime.now().isoformat(),
            'termination_reason': 'A2A协议调用失败，根据严格异常处理策略立即终止',
            'workflow_status': WorkflowStatus.TERMINATED.value,
            'terminated_at_step': 'agent-5 Step 4: A2A协议代码生成',
            'next_agent_blocked': 'agent-6 (质量测试师)',
            'workflow_completion': '0%',
            'rollback_required': False,  # 严格模式不执行自动回滚
            'manual_intervention_required': True,
            'termination_scope': {
                'current_agent': 'agent-5',
                'blocked_agents': ['agent-6'],
                'affected_documents': ['development_template.yaml'],
                'suspended_tasks': ['代码生成', '任务分解', '测试准备']
            }
        }
    
    def _generate_user_confirmation(self, exception_details: Dict, termination_result: Dict) -> Dict:
        """
        生成用户确认请求
        
        Args:
            exception_details: 异常详细信息
            termination_result: 终止结果
            
        Returns:
            用户确认请求
        """
        exception_type = exception_details.get('exception_type')
        error_message = exception_details.get('error_message')
        
        # 根据异常类型生成不同的确认选项
        confirmation_options = self._generate_confirmation_options(exception_type)
        
        return {
            'confirmation_required': True,
            'confirmation_type': 'WORKFLOW_CONTINUATION',
            'urgency_level': 'HIGH',
            'user_message': {
                'title': 'A2A协议调用失败 - 工作流已终止',
                'summary': f"CodeGen Agent调用失败: {error_message}",
                'impact': termination_result.get('termination_scope', {}),
                'recommendation': self._generate_recommendation(exception_type)
            },
            'available_actions': confirmation_options,
            'default_action': UserAction.MANUAL_DEVELOPMENT.value,
            'timeout_seconds': 3600,  # 1小时超时
            'escalation_required': True if exception_type in [
                ExceptionType.A2A_PROTOCOL_FAILURE.value,
                ExceptionType.UNKNOWN_ERROR.value
            ] else False
        }
    
    def _generate_confirmation_options(self, exception_type: str) -> List[Dict]:
        """
        生成确认选项
        
        Args:
            exception_type: 异常类型
            
        Returns:
            确认选项列表
        """
        base_options = [
            {
                'action': UserAction.MANUAL_DEVELOPMENT.value,
                'label': '继续手动开发',
                'description': '跳过CodeGen，采用完全手动开发方式',
                'impact': '开发时间增加，但可以继续项目',
                'recommended': True
            },
            {
                'action': UserAction.TERMINATE_PROJECT.value,
                'label': '终止项目',
                'description': '完全停止当前开发项目',
                'impact': '项目停止，需要重新规划',
                'recommended': False
            }
        ]
        
        # 根据异常类型添加特定选项
        if exception_type in [ExceptionType.NETWORK_ERROR.value, ExceptionType.TIMEOUT_ERROR.value]:
            base_options.insert(1, {
                'action': UserAction.RETRY_A2A_CALL.value,
                'label': '重试A2A调用',
                'description': '修复网络问题后重新尝试CodeGen调用',
                'impact': '可能解决临时性问题',
                'recommended': True
            })
        
        return base_options
    
    def _generate_recommendation(self, exception_type: str) -> str:
        """
        生成处理建议
        
        Args:
            exception_type: 异常类型
            
        Returns:
            处理建议
        """
        recommendations = {
            ExceptionType.NETWORK_ERROR.value: "建议检查网络连接和CodeGen服务状态，然后重试A2A调用",
            ExceptionType.TIMEOUT_ERROR.value: "建议增加超时时间或检查CodeGen服务性能，然后重试",
            ExceptionType.VALIDATION_ERROR.value: "建议检查架构信息格式和A2A协议规范，修正后重试",
            ExceptionType.CODEGEN_API_ERROR.value: "建议检查CodeGen服务状态和API兼容性，考虑手动开发",
            ExceptionType.A2A_PROTOCOL_FAILURE.value: "建议检查A2A协议实现和版本兼容性，推荐手动开发",
            ExceptionType.UNKNOWN_ERROR.value: "建议联系技术支持分析问题，推荐采用手动开发方式"
        }
        
        return recommendations.get(exception_type, "建议采用手动开发方式继续项目")
    
    def _log_exception(self, exception_details: Dict, termination_result: Dict) -> None:
        """
        记录异常日志
        
        Args:
            exception_details: 异常详细信息
            termination_result: 终止结果
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'log_level': 'ERROR',
            'component': 'ContextDev-Agent-5',
            'event_type': 'A2A_PROTOCOL_FAILURE',
            'exception_details': exception_details,
            'termination_result': termination_result,
            'strict_mode': self.strict_mode
        }
        
        # 记录到文件（实际实现中应该使用专业的日志系统）
        logger.error(f"A2A协议异常日志: {json.dumps(log_entry, ensure_ascii=False, indent=2)}")
    
    def validate_user_response(self, user_response: Dict) -> Dict:
        """
        验证用户响应
        
        Args:
            user_response: 用户响应
            
        Returns:
            验证结果
        """
        selected_action = user_response.get('selected_action')
        
        if not selected_action:
            return {
                'valid': False,
                'error': '未选择任何操作'
            }
        
        valid_actions = [action.value for action in UserAction]
        if selected_action not in valid_actions:
            return {
                'valid': False,
                'error': f'无效的操作选择: {selected_action}'
            }
        
        return {
            'valid': True,
            'action': selected_action,
            'next_steps': self._generate_next_steps(selected_action)
        }
    
    def _generate_next_steps(self, selected_action: str) -> List[str]:
        """
        生成下一步操作
        
        Args:
            selected_action: 选择的操作
            
        Returns:
            下一步操作列表
        """
        next_steps_mapping = {
            UserAction.MANUAL_DEVELOPMENT.value: [
                '重新规划开发任务为手动开发模式',
                '更新开发时间估算',
                '分配手动开发资源',
                '继续agent-6测试设计阶段'
            ],
            UserAction.RETRY_A2A_CALL.value: [
                '检查并修复网络连接问题',
                '验证CodeGen服务状态',
                '重新执行A2A协议调用',
                '监控调用结果'
            ],
            UserAction.TERMINATE_PROJECT.value: [
                '保存当前工作进度',
                '生成项目终止报告',
                '释放项目资源',
                '通知相关干系人'
            ],
            UserAction.CONFIRM_CONTINUATION.value: [
                '确认继续策略',
                '更新项目计划',
                '重新分配任务',
                '继续后续工作流'
            ]
        }
        
        return next_steps_mapping.get(selected_action, ['联系技术支持获取进一步指导'])
