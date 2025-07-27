#!/bin/bash
# check_template_references.sh
# 用途: 检查模板引用路径的标准性和有效性

cd "$(dirname "$0")/.."
echo "=== ContextDev 模板引用路径检查 ==="
echo "当前目录: $(pwd)"

# 1. 检查引用格式
echo -e "\n1. 检查引用格式..."
reference_issues=0

# 查找所有引用模式
grep -r "\.\./\|\"shared/\|\$ref:" templates/ --include="*.yaml" -n | while IFS=: read -r file line content; do
  # 检查是否符合标准格式
  if echo "$content" | grep -q "\.\./shared/.*\.yaml#/"; then
    echo "✅ $file:$line - 格式正确"
  elif echo "$content" | grep -q "\.\./[a-z_]*/.*\.yaml"; then
    echo "⚠️  $file:$line - 缺少锚点: $content"
  elif echo "$content" | grep -q "\$ref:"; then
    echo "ℹ️  $file:$line - 内部引用: $content"  
  else
    echo "❌ $file:$line - 格式不符: $content"
    ((reference_issues++))
  fi
done

# 2. 检查文件存在性
echo -e "\n2. 检查引用文件存在性..."
file_missing=0

grep -r "\.\./.*\.yaml" templates/ --include="*.yaml" -o | sort -u | while read ref; do
  # 提取引用路径，去掉../
  clean_ref="${ref#../}"
  file_path="templates/$clean_ref"
  if [[ -f "$file_path" ]]; then
    echo "✅ 文件存在: $ref -> $file_path"
  else
    echo "❌ 文件不存在: $ref -> $file_path"
    ((file_missing++))
  fi
done

# 3. 统计模板文件数量
echo -e "\n3. 模板文件统计..."
total_yaml_files=$(find templates/ -name "*.yaml" | wc -l)
total_references=$(grep -r "\.\./\|\$ref:" templates/ --include="*.yaml" | wc -l)

echo "📊 统计信息:"
echo "   - YAML模板文件总数: $total_yaml_files"
echo "   - 引用总数: $total_references"

# 4. 检查目录结构
echo -e "\n4. 目录结构检查..."
expected_dirs=("shared" "requirements" "baseline" "architecture" "development" "testing")
for dir in "${expected_dirs[@]}"; do
  if [[ -d "templates/$dir" ]]; then
    echo "✅ 目录存在: templates/$dir"
  else
    echo "❌ 目录缺失: templates/$dir"
  fi
done

echo -e "\n=== 检查完成 ==="
echo "请根据上述结果修复发现的问题。"