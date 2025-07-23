#!/bin/bash

# JeecgBoot AI 环境上游同步脚本 v2.0 (CodeGen + PRP 集成版)
# 保持与上游项目同步，同时保留 JeecgBoot 定制、CodeGen 集成和 PRP 工作流

# 启用错误检查但允许函数自行处理错误
set -o pipefail

echo "🔄 JeecgBoot AI 环境上游同步 v2.0 (CodeGen + PRP 集成版)"
echo "======================================================="

# 项目目录变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PRP_WORK_DIR="$PROJECT_ROOT/PRPs"
PROJECT_CLAUDE_CONFIG="$PRP_WORK_DIR/CLAUDE.md"

# 备份JeecgBoot定制配置
backup_jeecg_config() {
    echo "💾 备份JeecgBoot定制配置..."
    
    BACKUP_DIR="jeecg-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份项目级别CLAUDE.md配置
    if [ -f "$PROJECT_CLAUDE_CONFIG" ]; then
        # 提取JeecgBoot扩展配置
        sed -n '/# ===== JeecgBoot项目扩展配置 =====/,$p' "$PROJECT_CLAUDE_CONFIG" > "$BACKUP_DIR/jeecg-claude-extension.md"
        # 备份完整的项目级别CLAUDE.md
        cp "$PROJECT_CLAUDE_CONFIG" "$BACKUP_DIR/PROJECT_CLAUDE.md"
        echo "✅ 项目级别CLAUDE.md已备份"
    fi

    # 备份项目级别CodeGen AI代理配置
    if [ -f "$PRP_WORK_DIR/codegen_commands.json" ]; then
        cp "$PRP_WORK_DIR/codegen_commands.json" "$BACKUP_DIR/"
        echo "✅ 项目级别CodeGen专用命令配置已备份"
    fi

    # 备份PRP工作目录结构
    if [ -d "$PRP_WORK_DIR" ]; then
        cp -r "$PRP_WORK_DIR" "$BACKUP_DIR/PRPs_backup"
        echo "✅ PRP工作目录已备份"
    fi

    # 备份JeecgBoot示例
    if [ -d "context-engineering-intro/examples/jeecg-boot" ]; then
        cp -r context-engineering-intro/examples/jeecg-boot "$BACKUP_DIR/"
        echo "✅ JeecgBoot示例已备份"
    fi

    # 备份项目配置
    if [ -f ".ai-config/jeecg-ai-config.json" ]; then
        cp .ai-config/jeecg-ai-config.json "$BACKUP_DIR/"
        echo "✅ 项目配置已备份"
    fi

    # 备份CodeGen AI配置
    if [ -f ".ai-config/codegen-ai-config.json" ]; then
        cp .ai-config/codegen-ai-config.json "$BACKUP_DIR/"
        echo "✅ CodeGen AI配置已备份"
    fi

    # 备份PRP模板
    if [ -d "ContextDev/templates" ]; then
        cp -r ContextDev/templates "$BACKUP_DIR/"
        echo "✅ PRP模板已备份"
    fi
    
    echo "📁 备份保存在: $BACKUP_DIR"
}

# 更新Context Engineering
update_context_engineering() {
    echo "📚 更新Context Engineering..."
    
    # 检查目录是否存在
    if [ ! -d "context-engineering-intro" ]; then
        echo "⚠️  Context Engineering目录不存在，跳过更新"
        echo "💡 提示: 如需使用Context Engineering，请运行jeecg-ai-setup.sh重新安装"
        return 0
    fi
    
    cd context-engineering-intro
    
    # 检查是否是git仓库
    if [ ! -d ".git" ]; then
        echo "⚠️  不是有效的git仓库，跳过更新"
        cd ..
        return 0
    fi
    
    # 检查是否有本地修改
    if ! git diff --quiet; then
        echo "⚠️  检测到本地修改，正在暂存..."
        git stash push -m "JeecgBoot customizations $(date)"
    fi
    
    # 拉取最新版本
    git fetch origin
    git pull origin main
    
    echo "✅ Context Engineering更新完成"
    cd ..
}

# 更新SuperClaude Framework
update_superclaude() {
    echo "🤖 更新SuperClaude Framework..."
    
    # 检查uv是否安装
    if ! command -v uv &> /dev/null; then
        echo "⚠️  uv未安装，跳过SuperClaude更新"
        echo "💡 提示: 如需使用SuperClaude，请运行jeecg-ai-setup.sh重新安装"
        return 0
    fi
    
    # 检查当前版本
    CURRENT_VERSION=$(python3 -c "import SuperClaude; print(SuperClaude.__version__)" 2>/dev/null || echo "未安装")
    echo "📋 当前版本: $CURRENT_VERSION"
    
    if [ "$CURRENT_VERSION" = "未安装" ]; then
        echo "⚠️  SuperClaude未安装，跳过更新"
        echo "💡 提示: 请运行jeecg-ai-setup.sh重新安装"
        return 0
    fi
    
    # 更新到最新版本
    uv add SuperClaude --upgrade
    
    # 检查新版本
    NEW_VERSION=$(python3 -c "import SuperClaude; print(SuperClaude.__version__)" 2>/dev/null || echo "未知")
    echo "📋 新版本: $NEW_VERSION"
    
    if [ "$CURRENT_VERSION" != "$NEW_VERSION" ]; then
        echo "🔄 检测到版本更新，重新配置..."
        python3 -m SuperClaude install --profile developer --non-interactive --force
    fi
    
    echo "✅ SuperClaude Framework更新完成"
}

# 更新MCP服务器
update_mcp_servers() {
    echo "🔗 更新MCP服务器..."
    
    # 更新已安装的MCP服务器
    MCP_SERVERS=("@context7/mcp-server" "@sequential/mcp-server" "@magic/mcp-server" "@playwright/mcp-server")
    
    for server in "${MCP_SERVERS[@]}"; do
        if npm list -g "$server" &>/dev/null; then
            echo "🔄 更新 $server..."
            npm update -g "$server" || echo "⚠️  $server 更新失败"
        else
            echo "ℹ️  $server 未安装，跳过"
        fi
    done
    
    echo "✅ MCP服务器更新完成"
}

# 恢复JeecgBoot定制配置
restore_jeecg_config() {
    echo "🔧 恢复JeecgBoot定制配置..."
    
    # 查找最新的备份
    LATEST_BACKUP=$(ls -1d jeecg-backup-* 2>/dev/null | tail -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        echo "❌ 未找到备份，需要重新配置JeecgBoot扩展"
        return 1
    fi
    
    echo "📁 使用备份: $LATEST_BACKUP"
    
    # 恢复项目级别CLAUDE.md配置
    mkdir -p "$PRP_WORK_DIR"
    
    # 首先复制新的Context Engineering基础配置
    if [ -f "context-engineering-intro/CLAUDE.md" ]; then
        cp "context-engineering-intro/CLAUDE.md" "$PROJECT_CLAUDE_CONFIG"
        echo "✅ 复制Context Engineering基础配置到项目级别"
    fi
    
    # 恢复JeecgBoot扩展配置
    if [ -f "$LATEST_BACKUP/jeecg-claude-extension.md" ]; then
        echo "" >> "$PROJECT_CLAUDE_CONFIG"
        echo "# ===== JeecgBoot项目扩展配置 =====" >> "$PROJECT_CLAUDE_CONFIG"
        cat "$LATEST_BACKUP/jeecg-claude-extension.md" >> "$PROJECT_CLAUDE_CONFIG"
        echo "✅ 项目级别CLAUDE.md JeecgBoot扩展已恢复"
    fi

    # 检查并添加CodeGen AI代理规范集成（如果尚未存在）
    if ! grep -q "CodeGen AI代理规范集成" "$PROJECT_CLAUDE_CONFIG" 2>/dev/null; then
        echo "" >> "$PROJECT_CLAUDE_CONFIG"
        echo "# ===== CodeGen AI代理规范集成 =====" >> "$PROJECT_CLAUDE_CONFIG"
        echo "## 🤖 CodeGen AI代理核心规范" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- 严格遵循CodeGen/Code_Gen_Agent.md中定义的AI行为边界" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- 使用LangGPT结构化提示进行业务需求分析" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- 自动生成符合JeecgBoot规范的JSON配置文件" >> "$PROJECT_CLAUDE_CONFIG"
        echo "- 调用Code_Gen_Guide.py执行完整代码生成工作流" >> "$PROJECT_CLAUDE_CONFIG"
        echo "✅ 项目级别CodeGen AI代理规范集成完成"
    else
        echo "✅ CodeGen AI代理规范集成已存在，跳过重复添加"
    fi

    # 恢复项目级别CodeGen专用命令配置
    if [ -f "$LATEST_BACKUP/codegen_commands.json" ]; then
        cp "$LATEST_BACKUP/codegen_commands.json" "$PRP_WORK_DIR/"
        echo "✅ 项目级别CodeGen专用命令配置已恢复"
    fi

    # 恢复PRP工作目录结构
    if [ -d "$LATEST_BACKUP/PRPs_backup" ]; then
        # 合并恢复PRP目录的其他内容（不覆盖CLAUDE.md）
        cp -r "$LATEST_BACKUP/PRPs_backup/templates" "$PRP_WORK_DIR/" 2>/dev/null || true
        cp -r "$LATEST_BACKUP/PRPs_backup/active" "$PRP_WORK_DIR/" 2>/dev/null || true
        cp -r "$LATEST_BACKUP/PRPs_backup/completed" "$PRP_WORK_DIR/" 2>/dev/null || true
        echo "✅ PRP工作目录结构已恢复"
    fi

    # 恢复JeecgBoot示例
    if [ -d "$LATEST_BACKUP/jeecg-boot" ]; then
        mkdir -p context-engineering-intro/examples
        cp -r "$LATEST_BACKUP/jeecg-boot" context-engineering-intro/examples/
        echo "✅ JeecgBoot示例已恢复"
    fi

    # 恢复项目配置
    if [ -f "$LATEST_BACKUP/jeecg-ai-config.json" ]; then
        mkdir -p .ai-config
        cp "$LATEST_BACKUP/jeecg-ai-config.json" .ai-config/
        echo "✅ 项目配置已恢复"
    fi

    # 恢复CodeGen AI配置
    if [ -f "$LATEST_BACKUP/codegen-ai-config.json" ]; then
        mkdir -p .ai-config
        cp "$LATEST_BACKUP/codegen-ai-config.json" .ai-config/
        echo "✅ CodeGen AI配置已恢复"
    fi

    # 恢复PRP模板
    if [ -d "$LATEST_BACKUP/templates" ]; then
        mkdir -p ContextDev
        cp -r "$LATEST_BACKUP/templates" ContextDev/
        echo "✅ PRP模板已恢复"
    fi

    # 项目级别配置不需要同步到全局，直接使用项目级别的CLAUDE.md
    echo "✅ 项目级别Claude Code配置已准备就绪：$PROJECT_CLAUDE_CONFIG"
}

# 检查兼容性
check_compatibility() {
    echo "🔍 检查版本兼容性..."
    
    # 检查Python版本
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "🐍 Python版本: $PYTHON_VERSION"
    
    # 检查Node.js版本
    NODE_VERSION=$(node --version)
    echo "📦 Node.js版本: $NODE_VERSION"
    
    # 检查SuperClaude版本
    SUPERCLAUDE_VERSION=$(python3 -c "import SuperClaude; print(SuperClaude.__version__)" 2>/dev/null || echo "未安装")
    echo "🤖 SuperClaude版本: $SUPERCLAUDE_VERSION"
    
    # 检查Context Engineering版本
    if [ -d "context-engineering-intro/.git" ]; then
        cd context-engineering-intro
        CONTEXT_VERSION=$(git describe --tags --always 2>/dev/null || echo "未知")
        echo "📚 Context Engineering版本: $CONTEXT_VERSION"
        cd ..
    fi
    
    echo "✅ 兼容性检查完成"
}

# 验证更新
verify_update() {
    echo "🔍 验证更新..."
    
    # 测试SuperClaude命令
    if python3 -c "from SuperClaude import commands; print('SuperClaude commands available')" 2>/dev/null; then
        echo "✅ SuperClaude命令可用"
    else
        echo "❌ SuperClaude命令不可用"
    fi
    
    # 检查项目级别CLAUDE.md
    if [ -f "$PROJECT_CLAUDE_CONFIG" ] && grep -q "JeecgBoot" "$PROJECT_CLAUDE_CONFIG"; then
        echo "✅ 项目级别JeecgBoot配置已加载"
    else
        echo "❌ 项目级别JeecgBoot配置未正确加载"
    fi
    
    # 检查项目级别CodeGen命令配置
    if [ -f "$PRP_WORK_DIR/codegen_commands.json" ]; then
        echo "✅ 项目级别CodeGen命令配置存在"
    else
        echo "❌ 项目级别CodeGen命令配置缺失"
    fi
    
    # 检查PRP工作目录结构
    if [ -d "$PRP_WORK_DIR" ]; then
        echo "✅ PRP工作目录存在"
    else
        echo "❌ PRP工作目录缺失"
    fi
}

# 清理旧备份
cleanup_old_backups() {
    echo "🧹 清理旧备份..."
    
    # 保留最近5个备份
    BACKUPS=($(ls -1d jeecg-backup-* 2>/dev/null | sort -r))
    
    if [ ${#BACKUPS[@]} -gt 5 ]; then
        echo "📁 发现 ${#BACKUPS[@]} 个备份，保留最新5个"
        
        for ((i=5; i<${#BACKUPS[@]}; i++)); do
            echo "🗑️  删除旧备份: ${BACKUPS[$i]}"
            rm -rf "${BACKUPS[$i]}"
        done
    fi
    
    echo "✅ 备份清理完成"
}

# 显示更新摘要
show_update_summary() {
    echo ""
    echo "📊 更新摘要"
    echo "============"
    echo ""
    echo "✅ Context Engineering: 已更新到最新版本"
    echo "✅ SuperClaude Framework: 已更新到最新版本"
    echo "✅ MCP服务器: 已更新"
    echo "✅ JeecgBoot项目级别配置: 已恢复到PRPs/目录"
    echo "✅ 项目级别CLAUDE.md: $PROJECT_CLAUDE_CONFIG"
    echo "✅ 项目级别CodeGen配置: $PRP_WORK_DIR/codegen_commands.json"
    echo ""
    echo "🔄 下次更新运行: ./ContextDev/jeecg-ai-update.sh"
    echo ""
    echo "📚 如有问题，请查看备份目录中的配置文件"
    echo ""
    echo "⚠️  重要提示："
    echo "   - 所有配置现在都在项目级别，不影响全局~/.claude/设置"
    echo "   - 请在JeecgBoot项目根目录中使用Claude Code"
    echo "   - Claude Code会自动检测并使用PRPs/CLAUDE.md配置"
}

# 主函数
main() {
    echo "开始同步上游项目..."
    
    backup_jeecg_config
    update_context_engineering
    update_superclaude
    update_mcp_servers
    restore_jeecg_config
    check_compatibility
    verify_update
    cleanup_old_backups
    show_update_summary
    
    echo ""
    echo "✨ 上游同步完成！"
}

# 检查参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "JeecgBoot AI环境上游同步脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示此帮助信息"
    echo "  --dry-run      仅检查更新，不执行"
    echo ""
    echo "此脚本会："
    echo "1. 备份JeecgBoot定制配置"
    echo "2. 更新Context Engineering到最新版本"
    echo "3. 更新SuperClaude Framework到最新版本"
    echo "4. 更新MCP服务器"
    echo "5. 恢复JeecgBoot定制配置"
    echo "6. 验证更新结果"
    exit 0
fi

if [ "$1" = "--dry-run" ]; then
    echo "🔍 检查模式 - 仅检查更新，不执行实际更新"
    check_compatibility
    exit 0
fi

# 运行主函数
main "$@"
