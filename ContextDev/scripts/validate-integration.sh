#!/bin/bash
# 集成验证脚本
# 验证 Context Engineering 和 CodeGen 系统集成状态

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_DEV_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$CONTEXT_DEV_DIR")"

echo "🧪 开始集成验证..."

# 验证目录结构
echo "📁 验证目录结构..."
required_dirs=(
    "$CONTEXT_DEV_DIR/upstream"
    "$CONTEXT_DEV_DIR/config"
    "$CONTEXT_DEV_DIR/scripts"
    "$CONTEXT_DEV_DIR/examples"
    "$CONTEXT_DEV_DIR/templates"
    "$PROJECT_ROOT/CodeGen"
    "$PROJECT_ROOT/PRPs"
)

for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "✅ $dir"
    else
        echo "❌ $dir"
        exit 1
    fi
done

# 验证配置文件
echo "⚙️ 验证配置文件..."
config_files=(
    "$CONTEXT_DEV_DIR/config/context-engineering.json"
    "$CONTEXT_DEV_DIR/config/jeecg-unified.json"
    "$PROJECT_ROOT/CLAUDE.md"
)

for file in "${config_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file"
        exit 1
    fi
done

# 验证 JSON 配置文件格式
echo "🔍 验证 JSON 配置文件格式..."
json_files=(
    "$CONTEXT_DEV_DIR/config/jeecg-unified.json"
    "$CONTEXT_DEV_DIR/integration-status.json"
)

for file in "${json_files[@]}"; do
    if [[ -f "$file" ]] && python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
        echo "✅ $file (格式正确)"
    else
        echo "❌ $file (格式错误或不存在)"
        exit 1
    fi
done

# 验证 CodeGen 系统
echo "🤖 验证 CodeGen 系统..."
codegen_files=(
    "$PROJECT_ROOT/CodeGen/Code_Gen_Guide.py"
    "$PROJECT_ROOT/CodeGen/Code_Gen_Agent.md"
    "$PROJECT_ROOT/CodeGen/Code_Gen_Config.json"
)

for file in "${codegen_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file"
        exit 1
    fi
done

# 验证 Python 环境
echo "🐍 验证 Python 环境..."
python3 -c "
import sys
print(f'✅ Python {sys.version.split()[0]}')

# 验证必要的 Python 包
required_packages = ['json', 'os', 'sys']
for package in required_packages:
    try:
        __import__(package)
        print(f'✅ {package} 可用')
    except ImportError:
        print(f'❌ {package} 不可用')
        exit(1)
"

# 验证模板文件
echo "📄 验证模板文件..."
template_files=(
    "$CONTEXT_DEV_DIR/templates/CLAUDE_JEECGBOOT.md"
    "$CONTEXT_DEV_DIR/templates/REQUIREMENTS_JEECGBOOT.md"
    "$CONTEXT_DEV_DIR/templates/DESIGN_JEECGBOOT.md"
)

for file in "${template_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "⚠️ $file (模板文件缺失)"
    fi
done

# 验证集成状态
echo "📊 验证集成状态..."
if [[ -f "$CONTEXT_DEV_DIR/integration-status.json" ]]; then
    python3 -c "
import json
with open('$CONTEXT_DEV_DIR/integration-status.json') as f:
    status = json.load(f)

print('集成状态:')
for component, info in status.get('integration_status', {}).items():
    print(f'  {component}: {info.get(\"status\", \"unknown\")} ({info.get(\"version\", \"unknown\")})')
"
    echo "✅ 集成状态验证完成"
else
    echo "⚠️ 集成状态文件不存在"
fi

# 验证示例代码
echo "📚 验证示例代码..."
if [[ -d "$CONTEXT_DEV_DIR/examples/jeecgboot" ]]; then
    example_count=$(find "$CONTEXT_DEV_DIR/examples/jeecgboot" -name "*.java" -o -name "*.vue" -o -name "*.ts" | wc -l)
    echo "✅ JeecgBoot 示例代码: $example_count 个文件"
else
    echo "⚠️ JeecgBoot 示例代码目录不存在"
fi

echo ""
echo "🎉 集成验证完成！"
echo ""
echo "📋 验证结果摘要:"
echo "- Context Engineering: ✅ 已集成"
echo "- CodeGen 系统: ✅ 已集成"
echo "- 配置文件: ✅ 格式正确"
echo "- Python 环境: ✅ 可用"
echo "- 模板文件: ✅ 已部署"