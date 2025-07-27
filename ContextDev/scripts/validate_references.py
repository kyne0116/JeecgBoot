#!/usr/bin/env python3
"""
ContextDev 模板引用路径验证工具
用途: 验证YAML模板中的引用路径格式和有效性
"""

import os
import re
import yaml
import sys
from pathlib import Path

class ReferenceValidator:
    def __init__(self, templates_dir="templates"):
        self.templates_dir = Path(templates_dir)
        self.reference_pattern = re.compile(r'"\.\./([^/]+)/([^"]+\.yaml)(#/[^"]+)?"')
        self.errors = []
        self.warnings = []
        self.valid_refs = []

    def validate_all_templates(self):
        """验证所有模板文件中的引用"""
        print("🔍 开始验证模板引用路径...")
        
        yaml_files = list(self.templates_dir.rglob("*.yaml"))
        print(f"📊 找到 {len(yaml_files)} 个YAML文件")
        
        for yaml_file in yaml_files:
            self.validate_file(yaml_file)
        
        self.print_summary()
        return len(self.errors) == 0

    def validate_file(self, file_path):
        """验证单个文件的引用"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找所有引用
            matches = self.reference_pattern.findall(content)
            
            for match in matches:
                layer, filename, anchor = match
                ref_path = f"../{layer}/{filename}"
                full_path = file_path.parent / ".." / layer / filename
                
                # 检查引用格式
                if not self.validate_reference_format(layer, filename, anchor):
                    self.errors.append(f"❌ {file_path}: 引用格式不符合标准: {ref_path}")
                    continue
                
                # 检查文件存在性
                if not full_path.exists():
                    self.errors.append(f"❌ {file_path}: 引用文件不存在: {ref_path}")
                    continue
                
                # 检查锚点有效性
                if anchor and not self.validate_anchor(full_path, anchor):
                    self.warnings.append(f"⚠️  {file_path}: 锚点可能无效: {ref_path}{anchor}")
                
                self.valid_refs.append(f"✅ {file_path}: {ref_path}{anchor or ''}")
                
        except Exception as e:
            self.errors.append(f"❌ {file_path}: 文件读取错误: {str(e)}")

    def validate_reference_format(self, layer, filename, anchor):
        """验证引用格式是否符合标准"""
        # 检查层级名称
        valid_layers = ["shared", "requirements", "baseline", "architecture", "development", "testing"]
        if layer not in valid_layers:
            return False
        
        # 检查文件扩展名
        if not filename.endswith('.yaml'):
            return False
        
        # 检查锚点格式
        if anchor and not anchor.startswith('#/'):
            return False
        
        return True

    def validate_anchor(self, file_path, anchor):
        """验证锚点是否指向有效的YAML路径"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 简化锚点路径检查，去掉 #/ 前缀
            anchor_path = anchor[2:].split('/')
            
            current = data
            for part in anchor_path:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            
            return True
        except:
            return False

    def print_summary(self):
        """打印验证结果摘要"""
        print("\n" + "="*60)
        print("📋 验证结果摘要")
        print("="*60)
        
        print(f"✅ 有效引用: {len(self.valid_refs)}")
        print(f"⚠️  警告: {len(self.warnings)}")  
        print(f"❌ 错误: {len(self.errors)}")
        
        if self.errors:
            print("\n🚨 错误详情:")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print("\n⚠️  警告详情:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\n🎉 所有引用路径都符合标准！")
        
        print("="*60)

def main():
    """主函数"""
    if len(sys.argv) > 1:
        templates_dir = sys.argv[1]
    else:
        templates_dir = "templates"
    
    validator = ReferenceValidator(templates_dir)
    success = validator.validate_all_templates()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()