#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeGen A2A Protocol Flask Application
提供HTTP API接口供ContextDev系统调用
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime

from a2a_server import A2AProtocolServer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化A2A协议服务器
a2a_server = A2AProtocolServer()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'CodeGen A2A Protocol Server',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    })

@app.route('/codegen/a2a', methods=['POST'])
def handle_a2a_request():
    """
    处理A2A协议请求的主要端点
    
    Returns:
        A2A协议响应
    """
    try:
        # 记录请求
        logger.info("收到ContextDev A2A协议请求")
        
        # 验证请求格式
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        # 获取请求数据
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'error': 'Request body is empty'
            }), 400
        
        # 记录请求详情
        correlation_id = request_data.get('a2a_protocol', {}).get('correlation_id', 'unknown')
        logger.info(f"处理A2A请求 - Correlation ID: {correlation_id}")
        
        # 调用A2A协议服务器处理请求
        response_data = a2a_server.handle_a2a_request(request_data)
        
        # 记录响应
        response_status = response_data.get('payload', {}).get('execution_status', {}).get('overall_result', 'unknown')
        logger.info(f"A2A请求处理完成 - Correlation ID: {correlation_id}, Status: {response_status}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"A2A协议处理异常: {e}")
        
        # 构建错误响应
        error_response = {
            'a2a_protocol': {
                'version': '1.0',
                'source_agent': 'codegen-expert',
                'target_agent': 'ContextDev-agent-5',
                'message_type': 'code_generation_response',
                'timestamp': datetime.now().isoformat(),
                'correlation_id': request.get_json().get('a2a_protocol', {}).get('correlation_id', 'unknown') if request.is_json else 'unknown'
            },
            'payload': {
                'execution_status': {
                    'overall_result': 'Fail',
                    'execution_time': datetime.now().isoformat(),
                    'generated_modules': []
                },
                'generation_results': [],
                'error_details': {
                    'error_code': 'A2A-500',
                    'error_message': f'服务器内部错误: {str(e)}',
                    'resolution_suggestions': [
                        '检查CodeGen服务状态',
                        '验证请求格式',
                        '查看服务器日志'
                    ]
                }
            }
        }
        
        return jsonify(error_response), 500

@app.route('/codegen/status', methods=['GET'])
def get_codegen_status():
    """
    获取CodeGen服务状态
    
    Returns:
        服务状态信息
    """
    try:
        # 检查CodeGen核心组件状态
        status_info = {
            'service_name': 'CodeGen A2A Protocol Server',
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'components': {
                'a2a_server': 'healthy',
                'config_loader': 'healthy',
                'variable_extractor': 'healthy',
                'code_generator': 'healthy'
            },
            'capabilities': {
                'supported_generation_types': ['crud', 'tree', 'one_to_many'],
                'supported_protocols': ['A2A-ContextDev-CodeGen-v1.0'],
                'max_concurrent_requests': 10
            }
        }
        
        return jsonify(status_info), 200
        
    except Exception as e:
        logger.error(f"获取状态信息异常: {e}")
        return jsonify({
            'error': f'获取状态失败: {str(e)}'
        }), 500

@app.route('/codegen/variables/extract', methods=['POST'])
def extract_variables():
    """
    测试端点：从架构信息中提取三核心变量
    
    Returns:
        提取的变量信息
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        request_data = request.get_json()
        requirement = request_data.get('requirement', {})
        system_context = request_data.get('system_context', {})
        
        # 提取变量
        variables = a2a_server._extract_variables_from_architecture(requirement, system_context)
        
        # 验证变量
        is_valid = a2a_server._validate_variables(variables)
        
        return jsonify({
            'variables': variables,
            'validation': {
                'is_valid': is_valid,
                'timestamp': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"变量提取异常: {e}")
        return jsonify({
            'error': f'变量提取失败: {str(e)}'
        }), 500

@app.route('/codegen/config/generate', methods=['POST'])
def generate_config():
    """
    测试端点：生成CodeGen配置文件
    
    Returns:
        生成的配置信息
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        request_data = request.get_json()
        requirement = request_data.get('requirement', {})
        variables = request_data.get('variables', {})
        
        # 生成配置
        config = a2a_server._generate_config_from_requirement(requirement, variables)
        
        return jsonify({
            'config': config,
            'generation_info': {
                'timestamp': datetime.now().isoformat(),
                'variables_used': variables
            }
        }), 200
        
    except Exception as e:
        logger.error(f"配置生成异常: {e}")
        return jsonify({
            'error': f'配置生成失败: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/health',
            '/codegen/a2a',
            '/codegen/status',
            '/codegen/variables/extract',
            '/codegen/config/generate'
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """405错误处理"""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'Please check the HTTP method and endpoint'
    }), 405

@app.before_request
def log_request_info():
    """记录请求信息"""
    logger.info(f"收到请求: {request.method} {request.url}")

@app.after_request
def log_response_info(response):
    """记录响应信息"""
    logger.info(f"响应状态: {response.status_code}")
    return response

if __name__ == '__main__':
    logger.info("启动CodeGen A2A Protocol Flask应用")
    
    # 开发模式配置 - 使用8888端口避免与JeecgBoot冲突
    app.run(
        host='0.0.0.0',
        port=8888,
        debug=True,
        threaded=True
    )
    
    logger.info("CodeGen A2A Protocol Flask应用已停止")
