# CodeGen 配置文件使用指引

## 📋 概述

`Code_Gen_Config.json` 是 CodeGen 系统的核心配置文件，支持跨平台路径配置和动态路径检测。

## 🔧 路径配置方案

### 方案 1: 自动检测 (推荐)

```json
{
  "project": {
    "path_prefix": "$JEECG_PROJECT_ROOT"
  }
}
```

**优点**:

- 环境变量配置，便于不同环境部署
- 与其他配置项保持一致的命名规范
- 支持 CI/CD 和容器化部署

### 备选方案: 自动检测

如果不想使用环境变量，可以使用自动检测：

```json
{
  "project": {
    "path_prefix": "AUTO_DETECT"
  }
}
```

**工作原理**:
系统会从当前目录开始向上查找，寻找包含以下标识的目录：`jeecg-boot/`、`jeecgboot-vue3/`、`CodeGen/`、`pom.xml`

**使用方法**:

```bash
# Windows
set JEECG_PROJECT_ROOT=D:\Projects\JeecgBoot

# macOS/Linux
export JEECG_PROJECT_ROOT=/Users/username/Projects/JeecgBoot
```

#### 服务器配置环境变量

```json
{
  "project": {
    "path_prefix": "$JEECG_PROJECT_ROOT"
  },
  "server": {
    "base_url": "$JEECG_BASE_URL",
    "username": "$JEECG_USERNAME",
    "password": "$JEECG_PASSWORD"
  }
}
```

**服务器环境变量设置**:

```bash
# Windows
set JEECG_BASE_URL=http://localhost:8080/jeecg-boot
set JEECG_USERNAME=admin
set JEECG_PASSWORD=123456

# macOS/Linux
export JEECG_BASE_URL=http://localhost:8080/jeecg-boot
export JEECG_USERNAME=admin
export JEECG_PASSWORD=123456
```

**生产环境示例**:

```bash
# 生产环境配置
export JEECG_BASE_URL=https://prod-server.company.com/jeecg-boot
export JEECG_USERNAME=prod_admin
export JEECG_PASSWORD=${SECURE_PASSWORD}  # 从密钥管理系统获取
```

### 方案 3: 相对路径

```json
{
  "project": {
    "path_prefix": ".."
  }
}
```

**说明**: 相对于 CodeGen 目录的父目录

### 方案 4: 绝对路径

```json
{
  "project": {
    "path_prefix": "/absolute/path/to/jeecgboot"
  }
}
```

**平台示例**:

- Windows: `"D:/Projects/JeecgBoot"`
- macOS: `"/Users/username/Projects/JeecgBoot"`
- Linux: `"/home/username/projects/JeecgBoot"`

## 🌍 跨平台兼容性

### 路径分隔符

系统自动处理不同平台的路径分隔符：

- Windows: `\` 或 `/`
- macOS/Linux: `/`

### 默认路径

如果未配置或配置无效，系统使用平台默认路径：

- Windows: `%USERPROFILE%\Documents\JeecgBoot`
- macOS: `~/Work/JeecgBoot`
- Linux: `~/projects/JeecgBoot`

## 📁 完整配置示例

### 统一环境变量配置

```json
{
  "project": {
    "path_prefix": "$JEECG_PROJECT_ROOT"
  },
  "server": {
    "base_url": "$JEECG_BASE_URL",
    "username": "$JEECG_USERNAME",
    "password": "$JEECG_PASSWORD"
  },
  "timeouts": {
    "login": 10,
    "create": 30,
    "list": 15,
    "sync": 30,
    "codegen": 60
  },
  "form": {
    "data_file": "Code_Gen_Guide.json",
    "wait_after_create": 3
  },
  "codegen": {
    "project_path": "{{PROJECT_PATH}}",
    "entity_name": "{{BUSINESS_ENTITY}}",
    "jsp_mode": "one",
    "jform_type": "1",
    "package_style": "service",
    "vue_style": "vue3",
    "code_types": "controller,service,dao,mapper,entity,vue"
  }
}
```

**环境变量设置**:

```bash
# 设置所有必要的环境变量
export JEECG_PROJECT_ROOT=/path/to/your/jeecgboot/project
export JEECG_BASE_URL=http://localhost:8080/jeecg-boot
export JEECG_USERNAME=admin
export JEECG_PASSWORD=123456
```

## 🔍 配置验证

运行以下命令验证配置：

```bash
python Code_Gen_Guide.py --help
```

系统会显示：

- 当前平台信息
- 解析后的项目路径
- 配置文件状态

## ⚠️ 常见问题

### 问题 1: 路径不存在

**现象**: `❌ 项目路径不存在`
**解决**:

1. 检查路径是否正确
2. 使用 `AUTO_DETECT` 自动检测
3. 确保项目结构完整

### 问题 2: 权限问题

**现象**: `❌ 权限不足`
**解决**:

1. 检查目录权限
2. 使用管理员权限运行
3. 修改目录所有者

### 问题 3: 环境变量未设置

**现象**: `⚠️ 环境变量 XXX 未设置`
**解决**:

1. 设置对应的环境变量
2. 或改用其他配置方案

## 🚀 最佳实践

1. **开发环境**: 使用 `AUTO_DETECT`
2. **CI/CD**: 使用环境变量
3. **团队协作**: 使用相对路径
4. **生产部署**: 使用绝对路径

## 📝 配置文件位置

配置文件应放置在以下位置之一：

- `CodeGen/Code_Gen_Config.json` (默认)
- 使用 `--config` 参数指定自定义位置

## 🔄 配置更新

修改配置文件后，重新运行脚本即可生效，无需重启服务。

## 📞 技术支持

如遇配置问题，请检查：

1. 配置文件 JSON 格式是否正确
2. 路径是否存在且可访问
3. 环境变量是否正确设置
4. 平台兼容性是否满足要求
