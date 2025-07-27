#!/usr/bin/env python3
"""
ContextDev AIGC错误恢复系统
版本: v1.0.0
用途: 提供智能错误恢复、自动纠错和预防机制
"""

import re
import json
import time
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path

class ErrorType(Enum):
    """错误类型枚举"""
    PLACEHOLDER_ERROR = "placeholder_error"
    TYPE_CONVERSION_ERROR = "type_conversion_error"
    FORMAT_VALIDATION_ERROR = "format_validation_error"
    MISSING_FIELD_ERROR = "missing_field_error"
    LOGIC_CONFLICT_ERROR = "logic_conflict_error"
    TEMPLATE_REFERENCE_ERROR = "template_reference_error"
    YAML_SYNTAX_ERROR = "yaml_syntax_error"
    UNKNOWN_ERROR = "unknown_error"

class ErrorSeverity(Enum):
    """错误严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ErrorRecord:
    """错误记录数据结构"""
    timestamp: float
    error_type: ErrorType
    severity: ErrorSeverity
    error_message: str
    context: Dict[str, Any]
    recovery_attempts: int = 0
    recovery_success: bool = False
    recovery_method: Optional[str] = None
    error_hash: Optional[str] = None
    
    def __post_init__(self):
        if not self.error_hash:
            self.error_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """生成错误唯一标识"""
        content = f"{self.error_type.value}:{self.error_message}:{json.dumps(self.context, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

class AIGCErrorRecoverySystem:
    """AIGC错误恢复系统主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.error_history: List[ErrorRecord] = []
        self.recovery_strategies = self._initialize_strategies()
        self.logger = self._setup_logging()
        self.max_retry_attempts = 3
        self.base_retry_delay = 1.0  # 指数退避基础延迟
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "max_retry_attempts": 3,
            "base_retry_delay": 1.0,
            "error_recovery_success_threshold": 0.95,
            "placeholder_patterns": {
                "required": r"\$\{([A-Z_]+)_REQUIRED\}",
                "optional": r"\$\{([A-Z_]+)_OPTIONAL\}",
                "variable": r"\$\{([A-Z_]+)\}"
            },
            "auto_correction_rules": {
                "enable_placeholder_fill": True,
                "enable_type_conversion": True,
                "enable_format_repair": True,
                "enable_field_completion": True,
                "enable_logic_resolution": True
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志记录"""
        logger = logging.getLogger("AIGC_ErrorRecovery")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_strategies(self) -> Dict[ErrorType, callable]:
        """初始化错误恢复策略"""
        return {
            ErrorType.PLACEHOLDER_ERROR: self._recover_placeholder_error,
            ErrorType.TYPE_CONVERSION_ERROR: self._recover_type_conversion_error,
            ErrorType.FORMAT_VALIDATION_ERROR: self._recover_format_validation_error,
            ErrorType.MISSING_FIELD_ERROR: self._recover_missing_field_error,
            ErrorType.LOGIC_CONFLICT_ERROR: self._recover_logic_conflict_error,
            ErrorType.TEMPLATE_REFERENCE_ERROR: self._recover_template_reference_error,
            ErrorType.YAML_SYNTAX_ERROR: self._recover_yaml_syntax_error,
        }
    
    def process_with_recovery(self, data: Any, context: Dict[str, Any] = None) -> Tuple[Any, bool]:
        """带错误恢复的数据处理"""
        if context is None:
            context = {}
        
        attempt = 0
        last_error = None
        
        while attempt < self.max_retry_attempts:
            try:
                # 预处理：检测和修复常见问题
                processed_data = self._preprocess_data(data, context)
                
                # 主要处理逻辑
                result = self._process_data(processed_data, context)
                
                # 后处理：验证结果
                validated_result = self._validate_result(result, context)
                
                self.logger.info(f"数据处理成功，尝试次数: {attempt + 1}")
                return validated_result, True
                
            except Exception as e:
                attempt += 1
                last_error = e
                
                # 记录错误
                error_record = self._classify_and_record_error(e, context, attempt)
                
                # 尝试错误恢复
                recovery_success = self._attempt_error_recovery(error_record, data, context)
                
                if recovery_success:
                    self.logger.info(f"错误恢复成功: {error_record.error_hash}")
                    continue
                
                # 指数退避延迟
                if attempt < self.max_retry_attempts:
                    delay = self.base_retry_delay * (2 ** (attempt - 1))
                    self.logger.warning(f"处理失败，{delay}秒后重试 (第{attempt}次)")
                    time.sleep(delay)
        
        # 所有重试都失败
        self.logger.error(f"数据处理完全失败，已尝试{self.max_retry_attempts}次")
        return None, False
    
    def _preprocess_data(self, data: Any, context: Dict[str, Any]) -> Any:
        """数据预处理：主动修复常见问题"""
        if isinstance(data, dict):
            return self._preprocess_dict(data, context)
        elif isinstance(data, list):
            return [self._preprocess_data(item, context) for item in data]
        elif isinstance(data, str):
            return self._preprocess_string(data, context)
        else:
            return data
    
    def _preprocess_dict(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """预处理字典数据"""
        result = {}
        
        for key, value in data.items():
            # 递归处理值
            processed_value = self._preprocess_data(value, context)
            
            # 修复占位符
            if isinstance(processed_value, str):
                processed_value = self._fix_placeholders(processed_value, context)
            
            result[key] = processed_value
        
        return result
    
    def _preprocess_string(self, data: str, context: Dict[str, Any]) -> str:
        """预处理字符串数据"""
        # 修复占位符
        result = self._fix_placeholders(data, context)
        
        # 修复常见格式问题
        result = self._fix_common_format_issues(result)
        
        return result
    
    def _fix_placeholders(self, text: str, context: Dict[str, Any]) -> str:
        """自动修复占位符"""
        if not self.config["auto_correction_rules"]["enable_placeholder_fill"]:
            return text
        
        # 修复REQUIRED占位符
        required_pattern = self.config["placeholder_patterns"]["required"]
        def replace_required(match):
            placeholder_name = match.group(1)
            # 从上下文中查找值
            value = context.get(placeholder_name.lower(), f"AUTO_GENERATED_{placeholder_name}")
            return str(value)
        
        text = re.sub(required_pattern, replace_required, text)
        
        # 修复可选占位符
        optional_pattern = self.config["placeholder_patterns"]["optional"]
        text = re.sub(optional_pattern, "", text)  # 删除可选占位符
        
        return text
    
    def _fix_common_format_issues(self, text: str) -> str:
        """修复常见格式问题"""
        # 修复YAML引用格式 - 更严格的模式匹配
        text = re.sub(r'\.yml(?=["\s]|$)', '.yaml', text)
        
        # 修复路径分隔符
        text = text.replace('\\', '/')
        
        # 修复多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _process_data(self, data: Any, context: Dict[str, Any]) -> Any:
        """主要数据处理逻辑（占位符，实际使用时需要实现）"""
        # 这里是实际的数据处理逻辑
        # 在实际使用中，这里会调用AIGC的具体处理功能
        return data
    
    def _validate_result(self, result: Any, context: Dict[str, Any]) -> Any:
        """验证结果"""
        if result is None:
            raise ValueError("处理结果为空")
        
        # 检查结果完整性
        if isinstance(result, dict):
            required_fields = context.get("required_fields", [])
            for field in required_fields:
                if field not in result or result[field] is None:
                    raise ValueError(f"必需字段缺失: {field}")
        
        return result
    
    def _classify_and_record_error(self, error: Exception, context: Dict[str, Any], attempt: int) -> ErrorRecord:
        """分类并记录错误"""
        error_type = self._classify_error(error)
        severity = self._determine_severity(error_type, attempt)
        
        error_record = ErrorRecord(
            timestamp=time.time(),
            error_type=error_type,
            severity=severity,
            error_message=str(error),
            context=context.copy(),
            recovery_attempts=attempt
        )
        
        self.error_history.append(error_record)
        return error_record
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """智能错误分类"""
        error_msg = str(error).lower()
        
        if "placeholder" in error_msg or "${" in error_msg:
            return ErrorType.PLACEHOLDER_ERROR
        elif "type" in error_msg and ("convert" in error_msg or "cast" in error_msg):
            return ErrorType.TYPE_CONVERSION_ERROR
        elif "format" in error_msg or "invalid" in error_msg:
            return ErrorType.FORMAT_VALIDATION_ERROR
        elif "missing" in error_msg or "required" in error_msg:
            return ErrorType.MISSING_FIELD_ERROR
        elif "conflict" in error_msg or "inconsistent" in error_msg:
            return ErrorType.LOGIC_CONFLICT_ERROR
        elif "reference" in error_msg or "not found" in error_msg:
            return ErrorType.TEMPLATE_REFERENCE_ERROR
        elif "yaml" in error_msg or "syntax" in error_msg:
            return ErrorType.YAML_SYNTAX_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def _determine_severity(self, error_type: ErrorType, attempt: int) -> ErrorSeverity:
        """确定错误严重程度"""
        if attempt >= self.max_retry_attempts:
            return ErrorSeverity.CRITICAL
        elif error_type in [ErrorType.LOGIC_CONFLICT_ERROR, ErrorType.YAML_SYNTAX_ERROR]:
            return ErrorSeverity.HIGH
        elif error_type in [ErrorType.MISSING_FIELD_ERROR, ErrorType.TEMPLATE_REFERENCE_ERROR]:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _attempt_error_recovery(self, error_record: ErrorRecord, original_data: Any, context: Dict[str, Any]) -> bool:
        """尝试错误恢复"""
        recovery_strategy = self.recovery_strategies.get(error_record.error_type)
        
        if not recovery_strategy:
            self.logger.warning(f"没有找到错误类型的恢复策略: {error_record.error_type}")
            return False
        
        try:
            success = recovery_strategy(error_record, original_data, context)
            error_record.recovery_success = success
            
            if success:
                error_record.recovery_method = recovery_strategy.__name__
                self.logger.info(f"错误恢复成功: {error_record.error_hash}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"错误恢复失败: {str(e)}")
            return False
    
    # 具体的错误恢复策略实现
    def _recover_placeholder_error(self, error_record: ErrorRecord, data: Any, context: Dict[str, Any]) -> bool:
        """占位符错误恢复策略"""
        self.logger.info("执行占位符错误恢复...")
        
        # 查找常见占位符并提供默认值
        placeholder_defaults = {
            "PROJECT_NAME": "ContextDev项目",
            "SYSTEM_NAME": "智能开发系统",
            "MODULE_NAME": "默认模块",
            "BUSINESS_DOMAIN": "core",
            "COMPLEXITY_LEVEL": "standard",
            "FRAMEWORK_VERSION": "3.8.1",
            "GENERATION_TIMESTAMP": str(int(time.time())),
            "CODE_COVERAGE_PERCENTAGE": "85%",
            "QUALITY_SCORE": "90%"
        }
        
        # 更新上下文
        for key, value in placeholder_defaults.items():
            if key.lower() not in context:
                context[key.lower()] = value
        
        return True
    
    def _recover_type_conversion_error(self, error_record: ErrorRecord, data: Any, context: Dict[str, Any]) -> bool:
        """类型转换错误恢复策略"""
        self.logger.info("执行类型转换错误恢复...")
        
        # 设置类型转换规则
        context["type_conversion_rules"] = {
            "string_to_int": lambda x: int(x) if str(x).isdigit() else -1,
            "string_to_bool": lambda x: str(x).lower() in ['true', '1', 'yes', 'on'],
            "empty_to_default": lambda x, default: default if x in [None, "", []] else x
        }
        
        return True
    
    def _recover_format_validation_error(self, error_record: ErrorRecord, data: Any, context: Dict[str, Any]) -> bool:
        """格式验证错误恢复策略"""
        self.logger.info("执行格式验证错误恢复...")
        
        # 提供格式修复规则
        context["format_fixes"] = {
            "yaml_extension": lambda path: path.replace('.yml', '.yaml'),
            "path_separator": lambda path: path.replace('\\', '/'),
            "remove_extra_spaces": lambda text: re.sub(r'\s+', ' ', text).strip()
        }
        
        return True
    
    def _recover_missing_field_error(self, error_record: ErrorRecord, data: Any, context: Dict[str, Any]) -> bool:
        """缺失字段错误恢复策略"""
        self.logger.info("执行缺失字段错误恢复...")
        
        # 提供字段默认值
        field_defaults = {
            "project_id": "PROJ_001",
            "project_name": "默认项目",
            "version": "1.0.0",
            "created_date": time.strftime("%Y-%m-%d"),
            "status": "draft",
            "priority": "medium"
        }
        
        context["field_defaults"] = field_defaults
        return True
    
    def _recover_logic_conflict_error(self, error_record: ErrorRecord, data: Any, context: Dict[str, Any]) -> bool:
        """逻辑冲突错误恢复策略"""
        self.logger.info("执行逻辑冲突错误恢复...")
        
        # 设置冲突解决规则
        context["conflict_resolution_rules"] = {
            "priority_override": True,  # 高优先级覆盖低优先级
            "latest_wins": True,       # 最新值获胜
            "merge_arrays": True       # 合并数组而不是覆盖
        }
        
        return True
    
    def _recover_template_reference_error(self, error_record: ErrorRecord, data: Any, context: Dict[str, Any]) -> bool:
        """模板引用错误恢复策略"""
        self.logger.info("执行模板引用错误恢复...")
        
        # 提供引用修复机制
        context["reference_fixes"] = {
            "fallback_templates": {
                "shared/baseline_shared.yaml": "templates/shared/baseline_shared.yaml",
                "shared/data_types.yaml": "templates/shared/data_types.yaml"
            },
            "auto_create_missing": True
        }
        
        return True
    
    def _recover_yaml_syntax_error(self, error_record: ErrorRecord, data: Any, context: Dict[str, Any]) -> bool:
        """YAML语法错误恢复策略"""
        self.logger.info("执行YAML语法错误恢复...")
        
        # 设置YAML修复规则和修复函数
        def fix_yaml_content(content: str) -> str:
            """修复YAML内容的常见语法问题"""
            if not isinstance(content, str):
                return content
            
            # 修复常见的YAML语法问题
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                # 跳过空行和注释
                if not line.strip() or line.strip().startswith('#'):
                    fixed_lines.append(line)
                    continue
                
                # 修复未闭合的列表
                if line.strip().startswith('invalid: [') and not line.rstrip().endswith(']'):
                    fixed_lines.append(line.rstrip() + ']')
                    continue
                
                # 修复缺少引号的字符串值
                if ':' in line and not line.strip().endswith(('"', "'", ']', '}')):
                    key_value = line.split(':', 1)
                    if len(key_value) == 2:
                        key = key_value[0]
                        value = key_value[1].strip()
                        if value and not value.startswith(('"', "'", '[', '{')):
                            line = f'{key}: "{value}"'
                
                fixed_lines.append(line)
            
            return '\n'.join(fixed_lines)
        
        context["yaml_fixes"] = {
            "quote_strings": True,
            "fix_indentation": True,
            "escape_special_chars": True,
            "fix_yaml_content": fix_yaml_content
        }
        
        return True
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        if not self.error_history:
            return {"total_errors": 0, "recovery_rate": 0.0}
        
        total_errors = len(self.error_history)
        successful_recoveries = sum(1 for e in self.error_history if e.recovery_success)
        recovery_rate = successful_recoveries / total_errors
        
        error_type_counts = {}
        for error in self.error_history:
            error_type = error.error_type.value
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
        
        return {
            "total_errors": total_errors,
            "successful_recoveries": successful_recoveries,
            "recovery_rate": recovery_rate,
            "error_type_distribution": error_type_counts,
            "average_retry_attempts": sum(e.recovery_attempts for e in self.error_history) / total_errors
        }
    
    def export_error_report(self, output_path: str) -> None:
        """导出错误报告"""
        report = {
            "generation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "statistics": self.get_error_statistics(),
            "error_history": [asdict(error) for error in self.error_history[-100:]]  # 最近100个错误
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"错误报告已导出到: {output_path}")

# 使用示例和测试
if __name__ == "__main__":
    # 创建错误恢复系统实例
    recovery_system = AIGCErrorRecoverySystem()
    
    # 测试数据
    test_data = {
        "project_name": "${PROJECT_NAME_REQUIRED}",
        "complexity_level": "${COMPLEXITY_LEVEL}",
        "invalid_number": "not_a_number",
        "yaml_path": "../shared/baseline_shared.yml"
    }
    
    test_context = {
        "required_fields": ["project_name", "complexity_level"]
    }
    
    # 执行带恢复的处理
    result, success = recovery_system.process_with_recovery(test_data, test_context)
    
    print(f"处理结果: {result}")
    print(f"处理成功: {success}")
    print(f"错误统计: {recovery_system.get_error_statistics()}")