#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeGen Agent A2A Protocol Server
处理来自ContextDev系统的Agent-to-Agent协议请求
"""

import json
import uuid
import subprocess
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2AProtocolServer:
    """A2A协议服务端 - CodeGen Agent专用"""
    
    def __init__(self, config_path: str = "../Code_Gen_Config.json"):
        """
        初始化A2A协议服务端
        
        Args:
            config_path: CodeGen配置文件路径
        """
        self.config_path = config_path
        self.protocol_version = "1.0"
        self.agent_name = "codegen-expert"
        
        # 加载CodeGen配置
        self.config = self._load_config()
        
        # 加载模板和标准
        self.guide_template = self._load_guide_template()
        self.json_standards = self._load_json_standards()
        
    def _load_config(self) -> Dict:
        """加载CodeGen配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载CodeGen配置失败: {e}")
            return {}
    
    def _load_guide_template(self) -> Dict:
        """加载Code_Gen_Guide.json模板"""
        try:
            with open("../Code_Gen_Guide.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载Guide模板失败: {e}")
            return {}
    
    def _load_json_standards(self) -> Dict:
        """加载JSON标准规范"""
        # 这里简化处理，实际应该解析Code_Gen_JSON_Standards.md
        return {
            'forbidden_modules': ['system', 'admin', 'user', 'role', 'permission', 'auth'],
            'recommended_modules': ['finance', 'hrms', 'crm', 'scm', 'oa', 'healthcare'],
            'naming_patterns': {
                'table_name': '{module}_{submodule}_{entity}',
                'package_name': 'org.jeecg.modules.{module}.{submodule}'
            }
        }
    
    def handle_a2a_request(self, request: Dict) -> Dict:
        """
        处理来自ContextDev的A2A请求
        
        Args:
            request: A2A协议请求
            
        Returns:
            A2A协议响应
        """
        try:
            logger.info("收到ContextDev A2A协议请求")
            
            # 验证A2A协议格式
            if not self._validate_a2a_request(request):
                return self._build_error_response(request, "A2A-001", "A2A协议请求格式无效")
            
            # 提取生成需求
            generation_requirements = request['payload']['generation_requirements']
            system_context = request['payload']['system_context']
            
            # 执行代码生成
            results = []
            for requirement in generation_requirements:
                result = self._process_generation_requirement(requirement, system_context)
                results.append(result)
            
            # 构建A2A响应
            response = self._build_a2a_response(request, results)
            
            logger.info(f"A2A协议处理完成: {len(results)}个生成任务")
            return response
            
        except Exception as e:
            logger.error(f"A2A协议处理异常: {e}")
            return self._build_error_response(request, "A2A-999", f"A2A协议处理异常: {e}")
    
    def _validate_a2a_request(self, request: Dict) -> bool:
        """验证A2A协议请求格式"""
        try:
            protocol = request.get('a2a_protocol', {})
            payload = request.get('payload', {})
            
            # 验证协议头
            required_protocol_fields = ['version', 'source_agent', 'target_agent', 'message_type']
            if not all(field in protocol for field in required_protocol_fields):
                return False
            
            # 验证目标Agent
            if protocol.get('target_agent') != self.agent_name:
                return False
            
            # 验证消息类型
            if protocol.get('message_type') != 'code_generation_request':
                return False
            
            # 验证载荷
            required_payload_fields = ['system_context', 'generation_requirements']
            if not all(field in payload for field in required_payload_fields):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"A2A协议验证异常: {e}")
            return False
    
    def _process_generation_requirement(self, requirement: Dict, system_context: Dict) -> Dict:
        """
        处理单个代码生成需求
        
        Args:
            requirement: 生成需求
            system_context: 系统上下文
            
        Returns:
            生成结果
        """
        try:
            entity_name = requirement.get('entity_name', '')
            logger.info(f"处理代码生成需求: {entity_name}")
            
            # 从ContextDev架构信息中提取三核心变量
            variables = self._extract_variables_from_architecture(requirement, system_context)
            
            # 验证变量合规性
            if not self._validate_variables(variables):
                return {
                    'entity': entity_name,
                    'status': 'failed',
                    'error_message': '三核心变量验证失败',
                    'error_code': 'A2A-002'
                }
            
            # 生成配置文件
            config = self._generate_config_from_requirement(requirement, variables)
            
            # 执行代码生成
            generation_result = self._execute_code_generation(variables['MODULE_NAME'], config)
            
            if generation_result.get('overall_result') == 'Pass':
                return {
                    'entity': entity_name,
                    'status': 'success',
                    'generated_files': generation_result.get('generated_files', {}),
                    'customization_needs': self._identify_customization_needs(requirement),
                    'execution_details': generation_result,
                    'variables': variables
                }
            else:
                return {
                    'entity': entity_name,
                    'status': 'failed',
                    'error_message': generation_result.get('error_message', '代码生成执行失败'),
                    'error_code': 'A2A-003',
                    'execution_details': generation_result
                }
                
        except Exception as e:
            logger.error(f"处理生成需求异常: {e}")
            return {
                'entity': requirement.get('entity_name', ''),
                'status': 'failed',
                'error_message': f"处理异常: {e}",
                'error_code': 'A2A-999'
            }
    
    def _extract_variables_from_architecture(self, requirement: Dict, system_context: Dict) -> Dict:
        """
        从ContextDev架构信息中提取三核心变量
        
        Args:
            requirement: 生成需求
            system_context: 系统上下文
            
        Returns:
            三核心变量
        """
        # 优先使用requirement中的变量（如果有）
        if 'module_variables' in requirement:
            return requirement['module_variables']
        
        # 否则进行智能推理
        entity_name = requirement.get('entity_name', '')
        business_domain = system_context.get('business_domain', '')
        
        # MODULE_NAME推理
        module_name = self._infer_module_name(business_domain, entity_name)
        
        # SUBMODULE_NAME推理
        submodule_name = self._infer_submodule_name(entity_name)
        
        # BUSINESS_ENTITY直接使用entity_name
        business_entity = entity_name
        
        return {
            'MODULE_NAME': module_name,
            'SUBMODULE_NAME': submodule_name,
            'BUSINESS_ENTITY': business_entity
        }
    
    def _infer_module_name(self, business_domain: str, entity_name: str) -> str:
        """推理MODULE_NAME"""
        domain_lower = business_domain.lower()
        entity_lower = entity_name.lower()
        
        # 基于业务领域推理
        if any(keyword in domain_lower for keyword in ['finance', 'financial', 'money']):
            return 'finance'
        elif any(keyword in domain_lower for keyword in ['hr', 'human', 'employee']):
            return 'hrms'
        elif any(keyword in domain_lower for keyword in ['customer', 'crm', 'client']):
            return 'crm'
        elif any(keyword in domain_lower for keyword in ['supply', 'scm', 'inventory']):
            return 'scm'
        elif any(keyword in domain_lower for keyword in ['office', 'oa', 'workflow']):
            return 'oa'
        
        # 基于实体名称推理
        if any(keyword in entity_lower for keyword in ['product', 'order', 'invoice']):
            return 'business'
        
        return 'business'  # 默认值
    
    def _infer_submodule_name(self, entity_name: str) -> str:
        """推理SUBMODULE_NAME"""
        entity_lower = entity_name.lower()
        
        if 'product' in entity_lower:
            return 'product'
        elif 'order' in entity_lower:
            return 'order'
        elif any(keyword in entity_lower for keyword in ['customer', 'client', 'user']):
            return 'customer'
        elif 'invoice' in entity_lower:
            return 'invoice'
        elif 'employee' in entity_lower:
            return 'employee'
        else:
            return 'management'  # 默认值
    
    def _validate_variables(self, variables: Dict) -> bool:
        """验证三核心变量合规性"""
        module_name = variables.get('MODULE_NAME', '').lower()
        
        # 检查禁止的模块
        forbidden = self.json_standards.get('forbidden_modules', [])
        if module_name in forbidden:
            logger.warning(f"模块名称 {module_name} 在禁止列表中")
            return False
        
        # 检查命名规范
        if not module_name.islower():
            logger.warning(f"模块名称 {module_name} 不符合小写规范")
            return False
        
        return True
    
    def _generate_config_from_requirement(self, requirement: Dict, variables: Dict) -> Dict:
        """
        从需求生成CodeGen配置文件
        
        Args:
            requirement: 生成需求
            variables: 三核心变量
            
        Returns:
            CodeGen配置
        """
        # 复制模板
        config = self.guide_template.copy()
        
        # 替换变量
        table_name = f"{variables['MODULE_NAME']}_{variables['SUBMODULE_NAME']}_{variables['BUSINESS_ENTITY'].lower()}"
        
        config['head']['tableName'] = table_name
        config['head']['tableTxt'] = f"{variables['BUSINESS_ENTITY']}管理"
        config['head']['business_entity'] = variables['BUSINESS_ENTITY']
        
        # 处理业务字段
        business_fields = requirement.get('business_fields', [])
        if business_fields:
            # 生成完整的字段配置
            generated_fields = []

            # 添加系统字段
            system_fields = [
                {"dbFieldName": "id", "dbFieldTxt": "主键", "dbType": "VARCHAR", "dbLength": 36, "dbIsKey": 1, "dbIsNull": 0, "fieldMustInput": "1"},
                {"dbFieldName": "create_by", "dbFieldTxt": "创建人", "dbType": "VARCHAR", "dbLength": 50, "dbIsKey": 0, "dbIsNull": 1, "fieldMustInput": "0"},
                {"dbFieldName": "create_time", "dbFieldTxt": "创建时间", "dbType": "DATETIME", "dbLength": 0, "dbIsKey": 0, "dbIsNull": 1, "fieldMustInput": "0"},
                {"dbFieldName": "update_by", "dbFieldTxt": "更新人", "dbType": "VARCHAR", "dbLength": 50, "dbIsKey": 0, "dbIsNull": 1, "fieldMustInput": "0"},
                {"dbFieldName": "update_time", "dbFieldTxt": "更新时间", "dbType": "DATETIME", "dbLength": 0, "dbIsKey": 0, "dbIsNull": 1, "fieldMustInput": "0"},
                {"dbFieldName": "sys_org_code", "dbFieldTxt": "组织机构编码", "dbType": "VARCHAR", "dbLength": 64, "dbIsKey": 0, "dbIsNull": 1, "fieldMustInput": "0"},
                {"dbFieldName": "del_flag", "dbFieldTxt": "删除标志", "dbType": "TINYINT", "dbLength": 1, "dbIsKey": 0, "dbIsNull": 1, "fieldMustInput": "0", "dbDefaultVal": "0"}
            ]

            # 添加业务字段
            for i, field in enumerate(business_fields):
                field_config = {
                    "dbFieldName": field['name'].lower(),
                    "dbFieldTxt": field.get('description', field['name']),
                    "dbType": self._map_field_type(field['type']),
                    "dbLength": self._get_field_length(field['type']),
                    "dbIsKey": 0,
                    "dbIsNull": 0 if field.get('required', False) else 1,
                    "fieldMustInput": "1" if field.get('required', False) else "0",
                    "fieldShowType": "text",
                    "orderNum": i + len(system_fields) + 1,
                    "isShowForm": 1,
                    "isShowList": 1,
                    "isQuery": 1 if i < 3 else 0  # 前3个字段设为可查询
                }
                generated_fields.append(field_config)

            # 合并系统字段和业务字段
            all_fields = []
            for i, field in enumerate(system_fields + generated_fields):
                field.update({
                    "orderNum": i + 1,
                    "dbPointLength": 0,
                    "dbDefaultVal": field.get("dbDefaultVal", ""),
                    "fieldShowType": field.get("fieldShowType", "text"),
                    "fieldHref": "",
                    "fieldLength": field.get("dbLength", 0),
                    "fieldValidType": "",
                    "fieldExtendJson": "",
                    "fieldDefaultValue": field.get("dbDefaultVal", ""),
                    "isReadOnly": 0,
                    "isQuery": field.get("isQuery", 0),
                    "queryMode": "single",
                    "mainTable": "",
                    "mainField": "",
                    "converter": "",
                    "queryDefVal": "",
                    "queryDictText": "",
                    "queryDictField": "",
                    "queryDictCode": "",
                    "queryConfigFlag": "",
                    "queryTableName": "",
                    "isShowForm": field.get("isShowForm", 0),
                    "isShowList": field.get("isShowList", 0),
                    "isReadOnlyAdd": 0,
                    "isReadOnlyEdit": 0,
                    "sortFlag": 0
                })
                all_fields.append(field)

            config['fields'] = all_fields
        
        return config

    def _map_field_type(self, field_type: str) -> str:
        """映射字段类型到数据库类型"""
        type_mapping = {
            'string': 'VARCHAR',
            'text': 'TEXT',
            'integer': 'INT',
            'decimal': 'DECIMAL',
            'date': 'DATE',
            'datetime': 'DATETIME',
            'boolean': 'TINYINT'
        }
        return type_mapping.get(field_type.lower(), 'VARCHAR')

    def _get_field_length(self, field_type: str) -> int:
        """获取字段长度"""
        length_mapping = {
            'string': 100,
            'text': 0,
            'integer': 11,
            'decimal': 10,
            'date': 0,
            'datetime': 0,
            'boolean': 1
        }
        return length_mapping.get(field_type.lower(), 100)

    def _execute_code_generation(self, module_name: str, config: Dict) -> Dict:
        """
        执行代码生成
        
        Args:
            module_name: 模块名称
            config: 配置文件内容
            
        Returns:
            执行结果
        """
        try:
            # 创建临时配置文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                temp_config_path = f.name
            
            # 调用Code_Gen_Guide.py
            python_cmd = 'python3' if os.name != 'nt' else 'python'
            cmd = [
                python_cmd, 'Code_Gen_Guide.py',
                '--module-name', module_name,
                '--form-config', temp_config_path
            ]
            
            logger.info(f"执行代码生成命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                encoding='utf-8'
            )
            
            # 清理临时文件
            os.unlink(temp_config_path)
            
            if result.returncode == 0:
                return {
                    'overall_result': 'Pass',
                    'stdout': result.stdout,
                    'generated_files': self._parse_generated_files(result.stdout)
                }
            else:
                return {
                    'overall_result': 'Fail',
                    'error_message': result.stderr,
                    'stdout': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'overall_result': 'Fail',
                'error_message': '代码生成执行超时'
            }
        except Exception as e:
            return {
                'overall_result': 'Fail',
                'error_message': f'代码生成执行异常: {e}'
            }
    
    def _parse_generated_files(self, stdout: str) -> Dict:
        """解析生成的文件列表"""
        # 简化处理，实际应该解析stdout中的文件信息
        return {
            'backend_files': ['Controller.java', 'Service.java', 'Entity.java'],
            'frontend_files': ['List.vue', 'Form.vue'],
            'database_files': ['ddl.sql']
        }
    
    def _identify_customization_needs(self, requirement: Dict) -> List[str]:
        """识别定制化需求"""
        customization_level = requirement.get('customization_level', 'basic')
        
        if customization_level == 'advanced':
            return [
                '复杂业务逻辑定制',
                '特殊UI交互优化',
                '性能优化调整'
            ]
        else:
            return ['基础配置调整']
    
    def _build_a2a_response(self, request: Dict, results: List[Dict]) -> Dict:
        """构建A2A协议响应"""
        correlation_id = request['a2a_protocol']['correlation_id']
        timestamp = datetime.now().isoformat()
        
        # 计算整体执行状态
        successful_count = sum(1 for r in results if r.get('status') == 'success')
        overall_result = 'Pass' if successful_count == len(results) else 'Partial' if successful_count > 0 else 'Fail'
        
        return {
            'a2a_protocol': {
                'version': self.protocol_version,
                'source_agent': self.agent_name,
                'target_agent': request['a2a_protocol']['source_agent'],
                'message_type': 'code_generation_response',
                'timestamp': timestamp,
                'correlation_id': correlation_id
            },
            'payload': {
                'execution_status': {
                    'overall_result': overall_result,
                    'execution_time': timestamp,
                    'generated_modules': [r.get('entity', '') for r in results if r.get('status') == 'success']
                },
                'generation_results': results,
                'post_generation_tasks': self._generate_post_tasks(results)
            }
        }
    
    def _generate_post_tasks(self, results: List[Dict]) -> Dict:
        """生成后续任务"""
        manual_customizations = []
        integration_tasks = []
        testing_recommendations = []
        
        for result in results:
            if result.get('status') == 'success':
                customizations = result.get('customization_needs', [])
                manual_customizations.extend(customizations)
                
                integration_tasks.append(f"{result.get('entity', '')}模块集成测试")
                testing_recommendations.append(f"{result.get('entity', '')}功能测试")
        
        return {
            'manual_customizations': manual_customizations,
            'integration_tasks': integration_tasks,
            'testing_recommendations': testing_recommendations
        }
    
    def _build_error_response(self, request: Dict, error_code: str, error_message: str) -> Dict:
        """构建错误响应"""
        correlation_id = request.get('a2a_protocol', {}).get('correlation_id', str(uuid.uuid4()))
        timestamp = datetime.now().isoformat()
        
        return {
            'a2a_protocol': {
                'version': self.protocol_version,
                'source_agent': self.agent_name,
                'target_agent': request.get('a2a_protocol', {}).get('source_agent', 'unknown'),
                'message_type': 'code_generation_response',
                'timestamp': timestamp,
                'correlation_id': correlation_id
            },
            'payload': {
                'execution_status': {
                    'overall_result': 'Fail',
                    'execution_time': timestamp,
                    'generated_modules': []
                },
                'generation_results': [],
                'error_details': {
                    'error_code': error_code,
                    'error_message': error_message,
                    'resolution_suggestions': ['检查A2A协议请求格式', '验证系统配置', '查看详细日志']
                }
            }
        }
