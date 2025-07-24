#!/bin/bash
# 集成验证脚本
# 验证双框架集成状态和功能完整性

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_DEV_DIR="$(dirname "$SCRIPT_DIR")"

echo "🧪 开始集成验证..."

# 验证目录结构
echo "📁 验证目录结构..."
required_dirs=(
    "$CONTEXT_DEV_DIR/upstream"
    "$CONTEXT_DEV_DIR/integration"
    "$CONTEXT_DEV_DIR/config"
    "$CONTEXT_DEV_DIR/scripts"
    "$CONTEXT_DEV_DIR/examples"
    "$CONTEXT_DEV_DIR/templates"
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
    "$CONTEXT_DEV_DIR/config/superclaude.json"
    "$CONTEXT_DEV_DIR/config/jeecg-unified.json"
)

for file in "${config_files[@]}"; do
    if [[ -f "$file" ]] && python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
        echo "✅ $file"
    else
        echo "❌ $file"
        exit 1
    fi
done

# 验证 Python 包
echo "🐍 验证 Python 包..."
python3 -c "
try:
    import SuperClaude
    import pkg_resources
    try:
        version = pkg_resources.get_distribution('SuperClaude').version
        print(f'✅ SuperClaude {version}')
    except pkg_resources.DistributionNotFound:
        print('✅ SuperClaude (版本未知)')
except ImportError:
    print('❌ SuperClaude 未安装')
    exit(1)
"

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

echo "✅ 集成验证完成"
