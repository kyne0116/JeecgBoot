#!/bin/bash

# JeecgBoot AI 环境安装脚本 v2.0 (ContextDev + CodeGen 集成版)
# 为 JeecgBoot 项目提供完整的 AI 赋能开发环境

set -e

echo "🚀 JeecgBoot AI 环境安装 v2.0 (ContextDev + CodeGen 集成版)"
echo "============================================================="

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONTEXT_DEV_DIR="$PROJECT_ROOT/ContextDev"

# 检查系统要求
check_prerequisites() {
    echo "🔍 检查系统要求..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    echo "✅ Python 3: $(python3 --version)"
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装，请先安装 Node.js 18+"
        exit 1
    fi
    echo "✅ Node.js: $(node --version)"
    
    # 检查是否在JeecgBoot项目目录
    if [[ ! -f "$PROJECT_ROOT/jeecg-boot/pom.xml" ]] || [[ ! -f "$PROJECT_ROOT/jeecgboot-vue3/package.json" ]]; then
        echo "❌ 请在 JeecgBoot 项目根目录运行此脚本"
        exit 1
    fi
    echo "✅ JeecgBoot 项目目录验证通过"
}

# 安装Context Engineering
install_context_engineering() {
    echo "📚 安装 Context Engineering..."
    
    if [[ ! -d "$PROJECT_ROOT/context-engineering-intro" ]]; then
        echo "📥 克隆 Context Engineering 项目..."
        git clone https://github.com/coleam00/context-engineering-intro.git
    else
        echo "📦 更新现有的 Context Engineering..."
        cd context-engineering-intro
        git pull origin main
        cd ..
    fi
    
    echo "✅ Context Engineering 安装完成"
}

# 安装SuperClaude Framework
install_superclaude() {
    echo "🤖 安装 SuperClaude Framework..."
    
    # 检查是否已安装uv
    if ! command -v uv &> /dev/null; then
        echo "📦 安装 uv 包管理器..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # 添加到当前会话的PATH
        export PATH="/Users/admin/.local/bin:$PATH"
    fi
    
    # 安装SuperClaude (使用pip作为备选方案)
    echo "📦 安装 SuperClaude 包..."
    if command -v uv &> /dev/null && [[ -f "pyproject.toml" ]]; then
        uv add SuperClaude
    else
        pip3 install SuperClaude
    fi
    
    # 配置SuperClaude
    echo "🔧 配置 SuperClaude..."
    python3 -c "try:
    import SuperClaude
    print('✅ SuperClaude 可用')
except ImportError:
    print('⚠️  SuperClaude 安装需要手动配置')
except Exception as e:
    print(f'⚠️  SuperClaude 配置: {e}')"
    
    echo "✅ SuperClaude Framework 安装完成"
}

# 创建AI配置目录
setup_ai_config() {
    echo "📁 设置 AI 配置目录..."
    
    mkdir -p "$PROJECT_ROOT/.ai-config"
    
    # 复制配置文件
    if [[ -f "$CONTEXT_DEV_DIR/jeecg-ai-config.json" ]]; then
        cp "$CONTEXT_DEV_DIR/jeecg-ai-config.json" "$PROJECT_ROOT/.ai-config/"
        echo "✅ AI 配置文件已复制"
    fi
    
    # 创建Claude配置目录
    mkdir -p ~/.claude
    
    echo "✅ AI 配置目录设置完成"
}

# 配置CLAUDE.md
setup_claude_config() {
    echo "📝 配置 Claude Code 扩展..."
    
    # 检查是否存在Context Engineering的CLAUDE.md
    if [[ -f "context-engineering-intro/CLAUDE.md" ]]; then
        # 备份现有配置
        if [[ -f "~/.claude/CLAUDE.md" ]]; then
            cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup
        fi
        
        # 复制基础配置
        cp context-engineering-intro/CLAUDE.md ~/.claude/CLAUDE.md
        
        # 添加JeecgBoot扩展配置
        echo "" >> ~/.claude/CLAUDE.md
        echo "# ===== JeecgBoot项目扩展配置 =====" >> ~/.claude/CLAUDE.md
        echo "" >> ~/.claude/CLAUDE.md
        
        if [[ -f "$CONTEXT_DEV_DIR/jeecg-claude-extension.md" ]]; then
            cat "$CONTEXT_DEV_DIR/jeecg-claude-extension.md" >> ~/.claude/CLAUDE.md
        fi
        
        # 添加CodeGen AI代理规范
        echo "" >> ~/.claude/CLAUDE.md
        echo "# ===== CodeGen AI代理规范集成 =====" >> ~/.claude/CLAUDE.md
        echo "## 🤖 CodeGen AI代理核心规范" >> ~/.claude/CLAUDE.md
        echo "- 严格遵循CodeGen/Code_Gen_Agent.md中定义的AI行为边界" >> ~/.claude/CLAUDE.md
        echo "- 使用LangGPT结构化提示进行业务需求分析" >> ~/.claude/CLAUDE.md
        echo "- 自动生成符合JeecgBoot规范的JSON配置文件" >> ~/.claude/CLAUDE.md
        echo "- 调用Code_Gen_Guide.py执行完整代码生成工作流" >> ~/.claude/CLAUDE.md
        echo "" >> ~/.claude/CLAUDE.md
        echo "### AI 命令映射" >> ~/.claude/CLAUDE.md
        echo "- \`/sc:jeecg-analyze\` - 基于 CodeGen AI 代理的需求分析" >> ~/.claude/CLAUDE.md
        echo "- \`/sc:jeecg-config\` - 智能生成 JSON 配置文件" >> ~/.claude/CLAUDE.md
        echo "- \`/sc:codegen\` - 执行完整 CodeGen 工作流" >> ~/.claude/CLAUDE.md
        
        echo "✅ Claude Code 配置完成"
    else
        echo "⚠️  Context Engineering CLAUDE.md 不存在，跳过配置"
    fi
}

# 创建PRP模板目录
setup_prp_templates() {
    echo "📋 设置 PRP 模板..."
    
    mkdir -p "$PROJECT_ROOT/PRPs"
    mkdir -p "$CONTEXT_DEV_DIR/templates"
    
    # 创建JeecgBoot专用PRP模板
    if [[ ! -f "$CONTEXT_DEV_DIR/templates/jeecg-prp-template.md" ]]; then
        cat > "$CONTEXT_DEV_DIR/templates/jeecg-prp-template.md" << 'EOF'
# JeecgBoot Module Development PRP

## Project
Building a {MODULE_NAME} module for JeecgBoot platform

## Role
You are a JeecgBoot expert developer with deep knowledge of:
- Spring Boot + MyBatis-Plus backend architecture
- Vue3 + Ant Design Vue frontend
- JeecgBoot code generation and online forms
- Database design with system fields integration

## Process
1. **需求分析**: 分析业务需求，识别核心实体和字段
2. **配置生成**: 使用CodeGen AI代理生成标准JSON配置
3. **代码生成**: 执行Code_Gen_Guide.py完整工作流
4. **编译验证**: Maven编译和前端代码集成
5. **功能测试**: API测试和界面验证

## Context
- Project: JeecgBoot v3.8.1
- Backend: Spring Boot 2.7.18 + MyBatis-Plus 3.5.3.2
- Frontend: Vue 3.5.13 + Ant Design Vue 4.2.6
- Database: MySQL with standard system fields
- Code Generator: CodeGen/Code_Gen_Guide.py

## Requirements
{DETAILED_REQUIREMENTS}

## Expected Output
1. JSON配置文件 (符合CodeGen规范)
2. 完整的CRUD代码 (后端+前端)
3. 数据库表结构 (包含系统字段)
4. API文档和测试用例
5. 权限配置和菜单注册

## Validation Gates
- [ ] JSON配置验证通过
- [ ] 后端代码编译成功
- [ ] 前端代码集成无误
- [ ] 数据库表创建成功
- [ ] API接口测试通过
- [ ] 权限验证正常
EOF
        echo "✅ JeecgBoot PRP 模板创建完成"
    fi
}

# 配置CodeGen集成
setup_codegen_integration() {
    echo "🔧 配置 CodeGen 集成..."
    
    # 检查CodeGen目录
    if [[ ! -d "$PROJECT_ROOT/CodeGen" ]]; then
        echo "⚠️  CodeGen 目录不存在，创建基础结构..."
        mkdir -p "$PROJECT_ROOT/CodeGen"
    fi
    
    # 创建CodeGen专用Claude命令配置
    mkdir -p ~/.claude
    cat > ~/.claude/codegen_commands.json << 'EOF'
{
  "commands": {
    "/sc:jeecg-analyze": {
      "description": "基于CodeGen AI代理的业务需求分析",
      "template": "使用LangGPT结构化方式分析以下业务需求，生成标准化字段设计：\n{input}",
      "requires_codegen": true
    },
    "/sc:jeecg-config": {
      "description": "智能生成JeecgBoot JSON配置文件",
      "template": "基于需求分析结果，生成符合JeecgBoot规范的CodeGen JSON配置：\n{input}",
      "output_format": "json",
      "validation": "python3 CodeGen/Code_Gen_Guide.py --validate-config"
    },
    "/sc:codegen": {
      "description": "执行完整CodeGen工作流",
      "template": "执行CodeGen工作流：配置验证 → 代码生成 → 编译测试 → 前端迁移",
      "script": "python3 CodeGen/Code_Gen_Guide.py",
      "post_actions": ["mvn clean compile", "npm run build"]
    }
  }
}
EOF
    
    echo "✅ CodeGen 集成配置完成"
}

# 复制JeecgBoot示例代码到Context Engineering
copy_example_codes() {
    echo "📋 复制 JeecgBoot 示例代码到 Context Engineering..."
    
    EXAMPLES_DIR="$PROJECT_ROOT/context-engineering-intro/examples"
    
    # 创建示例代码目录结构
    mkdir -p "$EXAMPLES_DIR/jeecgboot"
    mkdir -p "$EXAMPLES_DIR/jeecgboot/backend"
    mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend"
    
    # 后端示例代码复制
    echo "📂 复制后端示例代码..."
    
    # 实体类示例
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/entity"
        
        # 复制核心实体类
        declare -a entities=("SysUser.java" "SysDepart.java" "SysRole.java" "SysPermission.java")
        for entity in "${entities[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/$entity" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/$entity" "$EXAMPLES_DIR/jeecgboot/backend/entity/"
                echo "  ✓ 复制实体类: $entity"
            fi
        done
        
        # 复制关联实体
        declare -a relations=("SysUserRole.java" "SysUserDepart.java" "SysRolePermission.java")
        for relation in "${relations[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/$relation" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/$relation" "$EXAMPLES_DIR/jeecgboot/backend/entity/"
                echo "  ✓ 复制关联实体: $relation"
            fi
        done
    fi
    
    # 控制器示例
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/controller"
        
        declare -a controllers=("SysUserController.java" "SysDepartController.java" "SysRoleController.java")
        for controller in "${controllers[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/$controller" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/$controller" "$EXAMPLES_DIR/jeecgboot/backend/controller/"
                echo "  ✓ 复制控制器: $controller"
            fi
        done
    fi
    
    # 服务层示例
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/service"
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/service/impl"
        
        # 服务接口
        declare -a services=("ISysUserService.java" "ISysDepartService.java" "ISysRoleService.java")
        for service in "${services[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/$service" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/$service" "$EXAMPLES_DIR/jeecgboot/backend/service/"
                echo "  ✓ 复制服务接口: $service"
            fi
        done
        
        # 服务实现
        declare -a impls=("SysUserServiceImpl.java" "SysDepartServiceImpl.java" "SysRoleServiceImpl.java")
        for impl in "${impls[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/impl/$impl" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/impl/$impl" "$EXAMPLES_DIR/jeecgboot/backend/service/impl/"
                echo "  ✓ 复制服务实现: $impl"
            fi
        done
    fi
    
    # Mapper层示例
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/mapper" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/mapper"
        
        declare -a mappers=("SysUserMapper.java" "SysDepartMapper.java" "SysRoleMapper.java")
        for mapper in "${mappers[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/mapper/$mapper" ]]; then
                cp "$PROJECT_ROOT/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/mapper/$mapper" "$EXAMPLES_DIR/jeecgboot/backend/mapper/"
                echo "  ✓ 复制Mapper: $mapper"
            fi
        done
    fi
    
    # Demo模块示例（如果存在）
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/demo"
        
        # 复制Demo实体
        if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test/entity/JeecgDemo.java" ]]; then
            cp "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test/entity/JeecgDemo.java" "$EXAMPLES_DIR/jeecgboot/backend/demo/"
            echo "  ✓ 复制Demo实体: JeecgDemo.java"
        fi
        
        # 复制Demo控制器
        if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test/controller/JeecgDemoController.java" ]]; then
            cp "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-module-demo/src/main/java/org/jeecg/modules/demo/test/controller/JeecgDemoController.java" "$EXAMPLES_DIR/jeecgboot/backend/demo/"
            echo "  ✓ 复制Demo控制器: JeecgDemoController.java"
        fi
    fi
    
    # 前端示例代码复制
    echo "📂 复制前端示例代码..."
    
    # 用户管理页面
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/user" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/views/system/user"
        cp -r "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/user/"* "$EXAMPLES_DIR/jeecgboot/frontend/views/system/user/"
        echo "  ✓ 复制用户管理页面"
    fi
    
    # 部门管理页面
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/depart" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/views/system/depart"
        cp -r "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/depart/"* "$EXAMPLES_DIR/jeecgboot/frontend/views/system/depart/"
        echo "  ✓ 复制部门管理页面"
    fi
    
    # 角色管理页面
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/role" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/views/system/role"
        cp -r "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/role/"* "$EXAMPLES_DIR/jeecgboot/frontend/views/system/role/"
        echo "  ✓ 复制角色管理页面"
    fi
    
    # 菜单权限页面
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/menu" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/views/system/menu"
        cp -r "$PROJECT_ROOT/jeecgboot-vue3/src/views/system/menu/"* "$EXAMPLES_DIR/jeecgboot/frontend/views/system/menu/"
        echo "  ✓ 复制菜单权限页面"
    fi
    
    # API服务层
    if [[ -d "$PROJECT_ROOT/jeecgboot-vue3/src/api/sys" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/api/sys"
        
        declare -a apis=("user.ts" "menu.ts" "role.ts" "depart.ts")
        for api in "${apis[@]}"; do
            if [[ -f "$PROJECT_ROOT/jeecgboot-vue3/src/api/sys/$api" ]]; then
                cp "$PROJECT_ROOT/jeecgboot-vue3/src/api/sys/$api" "$EXAMPLES_DIR/jeecgboot/frontend/api/sys/"
                echo "  ✓ 复制API服务: $api"
            fi
        done
    fi
    
    # 状态管理
    if [[ -f "$PROJECT_ROOT/jeecgboot-vue3/src/store/modules/user.ts" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/store/modules"
        cp "$PROJECT_ROOT/jeecgboot-vue3/src/store/modules/user.ts" "$EXAMPLES_DIR/jeecgboot/frontend/store/modules/"
        echo "  ✓ 复制用户状态管理"
    fi
    
    # 路由配置
    if [[ -f "$PROJECT_ROOT/jeecgboot-vue3/src/router/routes/modules/demo/system.ts" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/frontend/router/routes/modules/demo"
        cp "$PROJECT_ROOT/jeecgboot-vue3/src/router/routes/modules/demo/system.ts" "$EXAMPLES_DIR/jeecgboot/frontend/router/routes/modules/demo/"
        echo "  ✓ 复制系统路由配置"
    fi
    
    # AI模块示例（如果存在）
    if [[ -d "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag" ]]; then
        mkdir -p "$EXAMPLES_DIR/jeecgboot/backend/airag"
        
        # AI实体类
        if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/entity/AiragModel.java" ]]; then
            cp "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/entity/AiragModel.java" "$EXAMPLES_DIR/jeecgboot/backend/airag/"
            echo "  ✓ 复制AI模型实体"
        fi
        
        # AI控制器
        if [[ -f "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/app/controller/AiragChatController.java" ]]; then
            cp "$PROJECT_ROOT/jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/app/controller/AiragChatController.java" "$EXAMPLES_DIR/jeecgboot/backend/airag/"
            echo "  ✓ 复制AI聊天控制器"
        fi
    fi
    
    # 创建示例代码说明文档
    cat > "$EXAMPLES_DIR/jeecgboot/README.md" << 'EOF'
# JeecgBoot 示例代码集合

本目录包含了JeecgBoot项目的典型前后端示例代码，用于Context Engineering和AI开发参考。

## 后端示例代码 (backend/)

### 1. 实体类 (entity/)
- **SysUser.java** - 系统用户实体，展示完整的JPA注解、系统字段、Excel导出等
- **SysDepart.java** - 部门实体，展示树形结构设计
- **SysRole.java** - 角色实体，展示权限管理相关设计
- **SysPermission.java** - 权限实体，展示菜单权限控制
- **SysUserRole.java** - 用户角色关联，展示多对多关系设计

### 2. 控制器 (controller/)
- **SysUserController.java** - 用户管理控制器，展示完整的CRUD操作、权限控制、Excel导入导出
- **SysDepartController.java** - 部门管理控制器，展示树形结构操作
- **SysRoleController.java** - 角色管理控制器，展示权限分配逻辑

### 3. 服务层 (service/ & service/impl/)
- 服务接口和实现类，展示业务逻辑封装和事务处理

### 4. 数据访问层 (mapper/)
- MyBatis-Plus Mapper接口，展示数据访问层设计

### 5. 业务示例 (demo/)
- **JeecgDemo.java** - 典型业务实体示例
- **JeecgDemoController.java** - 典型业务控制器示例

### 6. AI模块 (airag/)
- AI相关的实体类和控制器示例

## 前端示例代码 (frontend/)

### 1. 页面组件 (views/system/)
- **user/** - 用户管理页面，展示列表页面、表单编辑、权限控制
- **depart/** - 部门管理页面，展示树形组件使用
- **role/** - 角色管理页面，展示权限分配界面
- **menu/** - 菜单权限页面，展示菜单树管理

### 2. API服务 (api/sys/)
- **user.ts** - 用户相关API接口定义
- **menu.ts** - 菜单相关API接口定义
- **role.ts** - 角色相关API接口定义
- **depart.ts** - 部门相关API接口定义

### 3. 状态管理 (store/modules/)
- **user.ts** - 用户状态管理模块，展示Pinia使用

### 4. 路由配置 (router/routes/modules/demo/)
- **system.ts** - 系统管理模块路由配置

## 使用说明

1. **开发参考**: 这些示例代码展示了JeecgBoot的标准开发模式
2. **AI训练**: 可用于训练AI理解JeecgBoot的代码结构和最佳实践
3. **Context Engineering**: 为PRP和其他AI工作流提供上下文参考
4. **Code Generation**: CodeGen系统可以基于这些示例生成类似的代码结构

## 核心特点

- **统一的实体基类**: 所有实体都继承基础系统字段
- **权限注解**: 使用@RequiresPermissions等注解进行权限控制
- **Excel支持**: 实体类支持Excel导入导出
- **树形结构**: 部门和菜单展示了树形数据处理
- **组件化**: 前端使用可复用的JEECG组件
- **TypeScript**: 前端全面使用TypeScript提供类型安全

这些示例代码是JeecgBoot开发的最佳实践参考。
EOF
    
    echo "✅ JeecgBoot 示例代码复制完成"
    echo "📍 示例代码位置: $EXAMPLES_DIR/jeecgboot/"
}

# 验证安装
verify_installation() {
    echo "🔍 验证安装..."
    
    # 检查Context Engineering
    if [[ -d "$PROJECT_ROOT/context-engineering-intro" ]]; then
        echo "✅ Context Engineering 已安装"
    else
        echo "❌ Context Engineering 安装失败"
    fi
    
    # 检查SuperClaude
    if python3 -c "import SuperClaude; print('SuperClaude available')" 2>/dev/null; then
        echo "✅ SuperClaude Framework 已安装"
    else
        echo "⚠️  SuperClaude Framework 需要手动配置 (可选)"
    fi
    
    # 检查Claude配置
    if [[ -f ~/.claude/CLAUDE.md ]] && grep -q "JeecgBoot" ~/.claude/CLAUDE.md; then
        echo "✅ Claude Code 配置已加载"
    else
        echo "❌ Claude Code 配置未正确加载"
    fi
    
    # 检查目录结构
    if [[ -d "$PROJECT_ROOT/PRPs" ]] && [[ -d "$PROJECT_ROOT/.ai-config" ]]; then
        echo "✅ AI 工作目录已创建"
    else
        echo "❌ AI 工作目录创建失败"
    fi
    
    # 检查示例代码
    if [[ -d "$PROJECT_ROOT/context-engineering-intro/examples/jeecgboot" ]]; then
        echo "✅ JeecgBoot 示例代码已复制"
    else
        echo "❌ JeecgBoot 示例代码复制失败"
    fi
}

# 显示使用指南
show_usage_guide() {
    echo ""
    echo "🎉 JeecgBoot AI 环境安装完成！"
    echo "================================="
    echo ""
    echo "📚 快速开始："
    echo ""
    echo "1. PRP 工作流（推荐）："
    echo "   /generate-prp customer-management-requirements.md"
    echo "   /execute-prp PRPs/customer-management.md"
    echo ""
    echo "2. SuperClaude 命令："
    echo "   /sc:jeecg-analyze \"分析业务需求\""
    echo "   /sc:jeecg-config \"生成配置文件\""
    echo "   /sc:codegen \"执行代码生成\""
    echo ""
    echo "3. CodeGen AI 代理："
    echo "   - 严格遵循 CodeGen/Code_Gen_Agent.md 规范"
    echo "   - 自动生成 JeecgBoot 标准配置"
    echo "   - 完整工作流：需求→配置→生成→验证"
    echo ""
    echo "📁 重要目录："
    echo "   - PRPs/                                    # PRP工作文件"
    echo "   - .ai-config/                              # AI配置文件"
    echo "   - ContextDev/templates/                    # PRP模板"
    echo "   - ~/.claude/CLAUDE.md                      # Claude配置"
    echo "   - context-engineering-intro/examples/     # JeecgBoot示例代码"
    echo ""
    echo "📖 详细文档："
    echo "   - ContextDev/README.md"
    echo "   - ContextDev/JeecgBoot_AI_Integration_Guide.md"
    echo ""
    echo "🔄 更新环境："
    echo "   ./ContextDev/jeecg-ai-update.sh"
}

# 主安装流程
main() {
    echo "开始安装 JeecgBoot AI 环境..."
    
    check_prerequisites
    install_context_engineering
    install_superclaude
    setup_ai_config
    setup_claude_config
    setup_prp_templates
    setup_codegen_integration
    copy_example_codes
    verify_installation
    show_usage_guide
    
    echo ""
    echo "✨ 安装完成！现在可以使用 AI 赋能开发功能了！"
}

# 检查参数
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "JeecgBoot AI环境安装脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h        显示此帮助信息"
    echo "  --verify          仅验证环境，不执行安装"
    echo "  --examples-only   仅复制JeecgBoot示例代码到Context Engineering"
    echo ""
    echo "此脚本将安装："
    echo "1. Context Engineering (PRP工作流)"
    echo "2. SuperClaude Framework (专业命令)"
    echo "3. CodeGen AI代理集成"
    echo "4. Claude Code配置"
    echo "5. PRP模板和工作目录"
    echo "6. JeecgBoot前后端示例代码"
    exit 0
fi

if [[ "$1" == "--verify" ]]; then
    echo "🔍 验证模式 - 仅检查安装状态"
    verify_installation
    exit 0
fi

if [[ "$1" == "--examples-only" ]]; then
    echo "📋 仅复制示例代码模式"
    copy_example_codes
    echo "✅ 示例代码复制完成"
    exit 0
fi

# 运行主安装流程
main "$@"