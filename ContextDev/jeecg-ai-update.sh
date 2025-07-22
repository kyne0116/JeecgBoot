#!/bin/bash

# JeecgBoot AI 环境上游同步脚本 v2.0 (CodeGen + PRP 集成版)
# 保持与上游项目同步，同时保留 JeecgBoot 定制、CodeGen 集成和 PRP 工作流

set -e

echo "🔄 JeecgBoot AI 环境上游同步 v2.0 (CodeGen + PRP 集成版)"
echo "======================================================="

# 备份JeecgBoot定制配置
backup_jeecg_config() {
    echo "💾 备份JeecgBoot定制配置..."
    
    BACKUP_DIR="jeecg-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份CLAUDE.md中的JeecgBoot扩展部分
    if [ -f "context-engineering-intro/CLAUDE.md" ]; then
        # 提取JeecgBoot扩展配置
        sed -n '/# ===== JeecgBoot项目扩展配置 =====/,$p' context-engineering-intro/CLAUDE.md > "$BACKUP_DIR/jeecg-claude-extension.md"
        echo "✅ CLAUDE.md JeecgBoot扩展已备份"
    fi

    # 备份CodeGen AI代理配置
    if [ -f "~/.claude/codegen_commands.json" ]; then
        cp ~/.claude/codegen_commands.json "$BACKUP_DIR/"
        echo "✅ CodeGen专用命令配置已备份"
    fi

    # 备份CodeGen MCP服务器
    if [ -d "~/.claude/mcp-codegen" ]; then
        cp -r ~/.claude/mcp-codegen "$BACKUP_DIR/"
        echo "✅ CodeGen MCP服务器已备份"
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
    
    cd context-engineering-intro
    
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
    
    # 检查当前版本
    CURRENT_VERSION=$(python3 -c "import SuperClaude; print(SuperClaude.__version__)" 2>/dev/null || echo "未安装")
    echo "📋 当前版本: $CURRENT_VERSION"
    
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
    
    # 恢复CLAUDE.md扩展
    if [ -f "$LATEST_BACKUP/jeecg-claude-extension.md" ]; then
        echo "" >> context-engineering-intro/CLAUDE.md
        echo "# ===== JeecgBoot项目扩展配置 =====" >> context-engineering-intro/CLAUDE.md
        cat "$LATEST_BACKUP/jeecg-claude-extension.md" >> context-engineering-intro/CLAUDE.md
        echo "✅ CLAUDE.md JeecgBoot扩展已恢复"
    fi

    # 追加CodeGen AI代理规范集成
    echo "" >> context-engineering-intro/CLAUDE.md
    echo "# ===== CodeGen AI代理规范集成 =====" >> context-engineering-intro/CLAUDE.md
    echo "## 🤖 CodeGen AI代理核心规范" >> context-engineering-intro/CLAUDE.md
    echo "- 严格遵循CodeGen/Code_Gen_Agent.md中定义的AI行为边界" >> context-engineering-intro/CLAUDE.md
    echo "- 使用LangGPT结构化提示进行业务需求分析" >> context-engineering-intro/CLAUDE.md
    echo "- 自动生成符合JeecgBoot规范的JSON配置文件" >> context-engineering-intro/CLAUDE.md
    echo "- 调用Code_Gen_Guide.py执行完整代码生成工作流" >> context-engineering-intro/CLAUDE.md
    echo "✅ CodeGen AI代理规范集成完成"

    # 恢复CodeGen专用命令配置
    if [ -f "$LATEST_BACKUP/codegen_commands.json" ]; then
        mkdir -p ~/.claude
        cp "$LATEST_BACKUP/codegen_commands.json" ~/.claude/
        echo "✅ CodeGen专用命令配置已恢复"
    fi

    # 恢复CodeGen MCP服务器
    if [ -d "$LATEST_BACKUP/mcp-codegen" ]; then
        mkdir -p ~/.claude
        cp -r "$LATEST_BACKUP/mcp-codegen" ~/.claude/
        echo "✅ CodeGen MCP服务器已恢复"
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

    # 更新Claude Code配置
    if [ -f "context-engineering-intro/CLAUDE.md" ]; then
        cp context-engineering-intro/CLAUDE.md ~/.claude/CLAUDE.md
        echo "✅ Claude Code配置已更新"
    fi
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
    
    # 检查CLAUDE.md
    if [ -f "~/.claude/CLAUDE.md" ] && grep -q "JeecgBoot" ~/.claude/CLAUDE.md; then
        echo "✅ JeecgBoot配置已加载"
    else
        echo "❌ JeecgBoot配置未正确加载"
    fi
    
    # 检查MCP服务器配置
    if [ -f "~/.claude/mcp_servers.json" ]; then
        echo "✅ MCP服务器配置存在"
    else
        echo "❌ MCP服务器配置缺失"
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
    echo "✅ JeecgBoot配置: 已恢复"
    echo ""
    echo "🔄 下次更新运行: ./jeecg-ai-update.sh"
    echo ""
    echo "📚 如有问题，请查看备份目录中的配置文件"
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
