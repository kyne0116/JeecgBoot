# JeecgBoot 后端 CI/CD 说明文档

## 概述

本文档介绍 JeecgBoot 项目的 GitHub Actions 后端持续集成/持续部署(CI/CD)配置和功能。CI/CD 流程确保代码质量，自动执行测试，并生成构建产物。

## GitHub Actions 配置

### 配置文件位置
- **文件**: `.github/workflows/backend-ci.yml`
- **工作流名称**: `JeecgBoot CI/CD`

### 触发条件

#### 推送触发
- **分支**: `master`, `develop`, `my-custom`
- **条件**: 当代码推送到指定分支时自动触发

#### 拉取请求触发  
- **分支**: `master`, `develop`
- **条件**: 当创建或更新针对主分支的 Pull Request 时触发

## 构建环境

### 运行环境
- **操作系统**: Ubuntu Latest
- **Java 版本**: OpenJDK 17 (Temurin 发行版)
- **构建工具**: Apache Maven
- **缓存策略**: Maven 依赖缓存

### 服务依赖

#### MySQL 数据库
- **版本**: MySQL 8.0
- **端口**: 3306
- **数据库**: jeecg-boot
- **认证**: root/root
- **健康检查**: 10秒间隔，5秒超时，3次重试

## CI/CD 流程步骤

### 1. 代码检出
```yaml
- uses: actions/checkout@v4
```
获取最新的代码仓库内容

### 2. Java 环境配置
```yaml
- name: Set up JDK 17
  uses: actions/setup-java@v4
  with:
    java-version: '17'
    distribution: 'temurin'
    cache: maven
```
- 配置 JDK 17 环境
- 启用 Maven 依赖缓存以提升构建速度

### 3. Maven 构建
```bash
mvn clean package -DskipTests -B -P test
```
- **工作目录**: `./jeecg-boot`
- **参数说明**:
  - `clean`: 清理之前的构建产物
  - `package`: 编译并打包项目
  - `-DskipTests`: 跳过测试执行(仅编译)
  - `-B`: 批处理模式，减少日志输出
  - `-P test`: 激活 test profile

### 4. 单元测试执行

#### 纯 JUnit 测试
```bash
mvn test -pl jeecg-module-system/jeecg-system-start -Dtest=PureJunitTest -B -P test
```
- **测试范围**: 基础 JUnit 测试，不依赖 Spring Framework
- **测试内容**: 
  - 基础断言测试
  - 字符串操作测试  
  - 数学运算测试
  - CI 环境验证测试

#### BDD 测试 (Cucumber)
```bash
mvn test -pl jeecg-module-system/jeecg-system-start -Dtest=CucumberTestRunner -B -P test
```
- **测试框架**: Cucumber BDD
- **测试特性**: 基于 Gherkin 语法的业务场景测试
- **报告格式**: HTML, JSON, XML, Timeline

### 5. 测试报告上传
```yaml
- name: Upload BDD test reports
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: bdd-test-reports
    path: |
      jeecg-boot/jeecg-module-system/jeecg-system-start/target/cucumber-reports/
```
- **触发条件**: 无论测试成功或失败都会执行
- **报告路径**: `target/cucumber-reports/`
- **报告类型**: Cucumber BDD 测试报告

## 项目结构

### 后端模块架构
```
jeecg-boot/
├── jeecg-boot-base-core/       # 核心框架和工具类
├── jeecg-module-system/        # 系统管理模块
│   ├── jeecg-system-api/       # API 定义
│   ├── jeecg-system-biz/       # 业务逻辑
│   └── jeecg-system-start/     # 启动模块(主入口)
├── jeecg-boot-module/          # 业务模块
│   └── jeecg-boot-module-airag/ # AI 和 RAG 功能
└── jeecg-server-cloud/         # 微服务模块
    ├── jeecg-cloud-gateway/    # API 网关
    ├── jeecg-cloud-nacos/      # 服务发现
    └── jeecg-visual/           # 监控管理
```

### 技术栈版本
- **Spring Boot**: 2.7.18
- **Java**: 17 (支持 JDK 8, 17, 21)
- **Maven**: 多模块项目结构
- **JeecgBoot**: 3.8.1

## 测试策略

### 测试类型
1. **纯 JUnit 测试**: 基础功能测试，快速验证核心逻辑
2. **BDD 测试**: 业务场景测试，确保功能符合需求规格
3. **集成测试**: 数据库连接和服务集成测试

### 测试覆盖范围
- 核心业务逻辑测试
- API 接口测试
- 数据库操作测试
- 消息发送功能测试
- AI/RAG 模块测试

## 部署支持

### 部署模式
- **单体模式**: 所有服务打包在一个应用中
- **微服务模式**: 使用 Spring Cloud Alibaba 架构

### Docker 支持
- 提供 `docker-compose.yml` 用于单体部署
- 提供 `docker-compose-cloud.yml` 用于微服务部署

## 最佳实践

### 开发流程
1. 本地开发完成功能
2. 提交代码到 feature 分支
3. 创建 Pull Request 到 develop 分支
4. CI/CD 自动执行测试
5. 代码审查通过后合并
6. 自动部署到测试环境

### 测试要求
- 所有新功能必须包含对应测试用例
- BDD 测试用例应覆盖主要业务场景  
- 确保 CI 环境测试通过才能合并代码

### 性能优化
- 使用 Maven 缓存减少依赖下载时间
- 并行执行不同类型的测试
- 合理配置数据库连接池和超时设置

---

**注意**: 本 CI/CD 配置专为 JeecgBoot 企业级低代码平台优化，集成了 AI 功能测试和多数据库支持。如需修改配置，请确保测试覆盖率和构建稳定性。