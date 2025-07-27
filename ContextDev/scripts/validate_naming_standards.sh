#!/bin/bash
# validate_naming_standards.sh
# 用途: 自动检查ContextDev模板命名规范符合性

cd "$(dirname "$0")/.."
echo "=== ContextDev 模板命名规范检查 ==="
echo "当前目录: $(pwd)"

# 初始化计数器
total_errors=0
total_warnings=0

# 1. 检查文件命名规范
echo -e "\n1. 检查文件命名规范..."

# 检查.yml扩展名（应该使用.yaml）
yml_files=$(find templates/ -name "*.yml" 2>/dev/null)
if [[ -n "$yml_files" ]]; then
    echo "❌ 发现错误的文件扩展名 (.yml应改为.yaml):"
    echo "$yml_files" | while read -r file; do
        echo "   $file"
        ((total_errors++))
    done
else
    echo "✅ 所有文件都使用正确的.yaml扩展名"
fi

# 检查文件名中的中划线（应该使用下划线）
dash_files=$(find templates/ -name "*-*" 2>/dev/null)
if [[ -n "$dash_files" ]]; then
    echo "❌ 发现包含中划线的文件名 (应使用下划线):"
    echo "$dash_files" | while read -r file; do
        echo "   $file"
        ((total_errors++))
    done
else
    echo "✅ 所有文件名都使用下划线分隔"
fi

# 检查文件名大写字母
uppercase_files=$(find templates/ -name "*[A-Z]*" 2>/dev/null)
if [[ -n "$uppercase_files" ]]; then
    echo "⚠️  发现包含大写字母的文件名:"
    echo "$uppercase_files" | while read -r file; do
        echo "   $file"
        ((total_warnings++))
    done
else
    echo "✅ 所有文件名都使用小写字母"
fi

# 2. 检查目录结构规范
echo -e "\n2. 检查目录结构规范..."

# 检查必需的共享基线文件
required_shared_files=("baseline_shared.yaml" "project_context.yaml" "data_types.yaml")
for file in "${required_shared_files[@]}"; do
    if [[ -f "templates/shared/$file" ]]; then
        echo "✅ 共享基线文件存在: $file"
    else
        echo "❌ 缺少共享基线文件: $file"
        ((total_errors++))
    fi
done

# 检查专家目录结构
expert_dirs=("requirements" "baseline" "architecture" "development" "testing")
for dir in "${expert_dirs[@]}"; do
    if [[ -d "templates/$dir" ]]; then
        echo "✅ 专家目录存在: $dir/"
        
        # 检查必需的input.yaml和output.yaml
        if [[ -f "templates/$dir/input.yaml" ]]; then
            echo "  ✅ input.yaml存在"
        else
            echo "  ❌ 缺少input.yaml"
            ((total_errors++))
        fi
        
        if [[ -f "templates/$dir/output.yaml" ]]; then
            echo "  ✅ output.yaml存在"
        else
            echo "  ❌ 缺少output.yaml"
            ((total_errors++))
        fi
    else
        echo "❌ 缺少专家目录: $dir/"
        ((total_errors++))
    fi
done

# 3. 检查文件内容格式
echo -e "\n3. 检查文件内容格式..."

yaml_files=$(find templates/ -name "*.yaml" 2>/dev/null)
file_count=0
format_errors=0

echo "$yaml_files" | while read -r file; do
    if [[ -n "$file" ]]; then
        ((file_count++))
        
        # 检查是否有头部注释
        if head -n 5 "$file" | grep -q "^#.*版本:" && head -n 5 "$file" | grep -q "^#.*创建日期:"; then
            echo "✅ $file - 包含标准头部注释"
        else
            echo "⚠️  $file - 缺少标准头部注释"
            ((total_warnings++))
        fi
        
        # 检查YAML语法
        if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo "✅ $file - YAML语法正确"
        else
            echo "❌ $file - YAML语法错误"
            ((total_errors++))
        fi
    fi
done

# 4. 检查字段命名规范（简化版）
echo -e "\n4. 检查字段命名规范..."

# 检查是否包含大写字母的字段名
grep -r "^[[:space:]]*[A-Z]" templates/ --include="*.yaml" -n | while IFS=: read -r file line content; do
    # 跳过注释行
    if [[ ! "$content" =~ ^[[:space:]]*# ]]; then
        echo "⚠️  可能的大写字段名: $file:$line"
        ((total_warnings++))
    fi
done

# 检查是否使用了中划线作为字段分隔符
grep -r "^[[:space:]]*[a-z][a-zA-Z0-9-]*-[a-zA-Z0-9-]*:" templates/ --include="*.yaml" -n | while IFS=: read -r file line content; do
    echo "⚠️  字段名包含中划线: $file:$line"
    ((total_warnings++))
done

# 5. 检查模板引用格式
echo -e "\n5. 检查模板引用格式..."

# 检查引用路径格式
grep -r "\\.\\./.*\\.yaml" templates/ --include="*.yaml" -n | while IFS=: read -r file line content; do
    if [[ "$content" =~ \.\./[a-z_]+/[a-z_]+\.yaml ]]; then
        echo "✅ 引用格式正确: $file:$line"
    else
        echo "⚠️  引用格式可能不规范: $file:$line"
        ((total_warnings++))
    fi
done

# 6. 统计和总结
echo -e "\n=== 检查结果总结 ==="
echo "📊 统计信息:"
yaml_file_count=$(find templates/ -name "*.yaml" | wc -l)
echo "   - 检查的YAML文件总数: $yaml_file_count"
echo "   - 发现的错误数量: $total_errors"
echo "   - 发现的警告数量: $total_warnings"

if [[ $total_errors -eq 0 ]]; then
    echo -e "\n🎉 所有关键命名规范检查通过！"
else
    echo -e "\n⚠️  发现 $total_errors 个错误，需要修复"
fi

if [[ $total_warnings -gt 0 ]]; then
    echo "ℹ️  发现 $total_warnings 个警告，建议优化"
fi

# 7. 提供修复建议
if [[ $total_errors -gt 0 || $total_warnings -gt 0 ]]; then
    echo -e "\n🔧 修复建议:"
    echo "1. 将所有.yml文件重命名为.yaml"
    echo "2. 将文件名中的中划线替换为下划线"
    echo "3. 将文件名改为小写字母"
    echo "4. 为缺少头部注释的文件添加标准注释"
    echo "5. 修复YAML语法错误"
    echo "6. 将字段名中的中划线替换为下划线"
    echo "7. 检查并修正模板引用路径"
fi

echo -e "\n📋 完整规范文档: TEMPLATE_NAMING_STANDARDS.md"
echo "🔧 Python版本检查工具: scripts/validate_naming_standards.py"

# 返回错误代码
if [[ $total_errors -gt 0 ]]; then
    exit 1
else
    exit 0
fi