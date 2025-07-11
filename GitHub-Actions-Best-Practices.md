# Spring Boot + Vue 项目 GitHub Actions 最佳实践

## 概述

本文档提供了针对 Spring Boot + Vue 全栈项目（如 JeecgBoot）的 GitHub Actions CI/CD 最佳实践指南。

## 目录结构

推荐的 GitHub Actions 工作流目录结构：

```
.github/
├── workflows/
│   ├── ci.yml                    # 持续集成主流程
│   ├── frontend-ci.yml           # 前端专用CI
│   ├── backend-ci.yml            # 后端专用CI
│   ├── security-scan.yml         # 安全扫描
│   ├── dependency-update.yml     # 依赖更新
│   ├── release.yml               # 发布流程
│   └── docker-build.yml          # Docker构建
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   └── feature_request.md
└── pull_request_template.md
```

## 1. 主要 CI/CD 工作流

### 1.1 持续集成主流程 (ci.yml)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ master, develop ]
  pull_request:
    branches: [ master, develop ]

env:
  NODE_VERSION: '18'
  JAVA_VERSION: '17'
  MAVEN_OPTS: '-Xmx3072m'

jobs:
  # 前端构建与测试
  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./jeecgboot-vue3
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'pnpm'
        cache-dependency-path: ./jeecgboot-vue3/pnpm-lock.yaml
    
    - name: Install pnpm
      run: npm install -g pnpm
    
    - name: Install dependencies
      run: pnpm install
    
    - name: Lint check
      run: pnpm run lint
    
    - name: Type check
      run: pnpm run type-check
    
    - name: Run tests
      run: pnpm run test
    
    - name: Build application
      run: pnpm run build
    
    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: frontend-dist
        path: ./jeecgboot-vue3/dist/

  # 后端构建与测试
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./jeecg-boot
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: jeecg-boot
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
        ports:
          - 3306:3306
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd="redis-cli ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up JDK
      uses: actions/setup-java@v4
      with:
        java-version: ${{ env.JAVA_VERSION }}
        distribution: 'temurin'
        cache: maven
    
    - name: Cache Maven dependencies
      uses: actions/cache@v4
      with:
        path: ~/.m2
        key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
        restore-keys: ${{ runner.os }}-m2
    
    - name: Run tests
      run: mvn clean test
    
    - name: Generate test report
      uses: dorny/test-reporter@v1
      if: success() || failure()
      with:
        name: Maven Tests
        path: target/surefire-reports/*.xml
        reporter: java-junit
    
    - name: Build application
      run: mvn clean compile
    
    - name: Package application
      run: mvn package -DskipTests
    
    - name: Upload JAR artifacts
      uses: actions/upload-artifact@v4
      with:
        name: backend-jars
        path: ./jeecg-boot/*/target/*.jar

  # 代码质量分析
  code-quality:
    runs-on: ubuntu-latest
    needs: [frontend, backend]
    
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: SonarCloud Scan
      uses: SonarSource/sonarcloud-github-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### 1.2 安全扫描工作流 (security-scan.yml)

```yaml
name: Security Scan

on:
  push:
    branches: [ master, develop ]
  pull_request:
    branches: [ master, develop ]
  schedule:
    - cron: '0 2 * * 1'  # 每周一凌晨2点

jobs:
  # 依赖漏洞扫描
  dependency-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
    
    - name: Maven Dependency Check
      run: |
        cd jeecg-boot
        mvn org.owasp:dependency-check-maven:check
    
    - name: Upload dependency check results
      uses: actions/upload-artifact@v4
      with:
        name: dependency-check-report
        path: jeecg-boot/target/dependency-check-report.html

  # 代码安全扫描
  codeql:
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write
    
    strategy:
      matrix:
        language: [ 'java', 'javascript' ]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v3
      with:
        languages: ${{ matrix.language }}
    
    - name: Autobuild
      uses: github/codeql-action/autobuild@v3
    
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v3
```

### 1.3 Docker 构建工作流 (docker-build.yml)

```yaml
name: Docker Build and Push

on:
  push:
    branches: [ master ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ master ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        service: [frontend, backend]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.service }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./jeecgboot-vue3/Dockerfile  # 前端
        # file: ./jeecg-boot/jeecg-module-system/jeecg-system-start/Dockerfile  # 后端
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
```

### 1.4 自动化发布工作流 (release.yml)

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  create-release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build changelog
      id: changelog
      uses: mikepenz/release-changelog-builder-action@v4
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        body: ${{ steps.changelog.outputs.changelog }}
        draft: false
        prerelease: false
```

### 1.5 依赖更新工作流 (dependency-update.yml)

```yaml
name: Dependency Update

on:
  schedule:
    - cron: '0 2 * * 1'  # 每周一凌晨2点
  workflow_dispatch:

jobs:
  update-dependencies:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Update Frontend Dependencies
      run: |
        cd jeecgboot-vue3
        npx npm-check-updates -u
        pnpm install
    
    - name: Update Backend Dependencies
      run: |
        cd jeecg-boot
        mvn versions:use-latest-versions
    
    - name: Create Pull Request
      uses: peter-evans/create-pull-request@v5
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        commit-message: 'chore: update dependencies'
        title: 'chore: update dependencies'
        body: |
          ## Dependencies Update
          
          This PR updates project dependencies to their latest versions.
          
          Please review the changes and test thoroughly before merging.
        branch: dependency-updates
```

## 2. 环境变量和密钥管理

### 2.1 必需的 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

```
SONAR_TOKEN                 # SonarCloud 令牌
SNYK_TOKEN                  # Snyk 安全扫描令牌
DOCKER_USERNAME             # Docker Hub 用户名
DOCKER_PASSWORD             # Docker Hub 密码
DATABASE_URL                # 数据库连接字符串
REDIS_URL                   # Redis 连接字符串
```

### 2.2 环境变量配置

```yaml
env:
  # 全局环境变量
  NODE_VERSION: '18'
  JAVA_VERSION: '17'
  MAVEN_OPTS: '-Xmx3072m'
  
  # 数据库配置
  SPRING_DATASOURCE_URL: ${{ secrets.DATABASE_URL }}
  SPRING_DATASOURCE_USERNAME: ${{ secrets.DB_USERNAME }}
  SPRING_DATASOURCE_PASSWORD: ${{ secrets.DB_PASSWORD }}
  
  # Redis 配置
  SPRING_REDIS_HOST: ${{ secrets.REDIS_HOST }}
  SPRING_REDIS_PORT: ${{ secrets.REDIS_PORT }}
  SPRING_REDIS_PASSWORD: ${{ secrets.REDIS_PASSWORD }}
```

## 3. 性能优化建议

### 3.1 缓存策略

```yaml
# Maven 依赖缓存
- name: Cache Maven dependencies
  uses: actions/cache@v4
  with:
    path: ~/.m2
    key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
    restore-keys: ${{ runner.os }}-m2

# Node.js 依赖缓存
- name: Cache Node.js dependencies
  uses: actions/cache@v4
  with:
    path: ~/.pnpm-store
    key: ${{ runner.os }}-pnpm-${{ hashFiles('**/pnpm-lock.yaml') }}
    restore-keys: ${{ runner.os }}-pnpm-
```

### 3.2 并行构建

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    java-version: [11, 17, 21]
    node-version: [16, 18, 20]
```

### 3.3 条件执行

```yaml
# 只在特定路径变更时执行
- name: Check for backend changes
  uses: dorny/paths-filter@v2
  id: backend-changes
  with:
    filters: |
      backend:
        - 'jeecg-boot/**'

- name: Build Backend
  if: steps.backend-changes.outputs.backend == 'true'
  run: mvn clean compile
```

## 4. 最佳实践总结

### 4.1 工作流设计原则

1. **职责分离**: 将前端、后端、安全扫描等分离到独立的工作流
2. **快速反馈**: 优先执行快速测试，失败时快速终止
3. **资源优化**: 合理使用缓存和并行执行
4. **安全第一**: 集成安全扫描和依赖检查

### 4.2 监控和通知

```yaml
# 失败通知
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 4.3 版本管理

```yaml
# 语义化版本
- name: Semantic Release
  uses: cycjimmy/semantic-release-action@v4
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## 5. 部署策略

### 5.1 多环境部署

```yaml
deploy:
  runs-on: ubuntu-latest
  needs: [frontend, backend]
  if: github.ref == 'refs/heads/master'
  
  strategy:
    matrix:
      environment: [staging, production]
  
  environment:
    name: ${{ matrix.environment }}
    url: ${{ steps.deploy.outputs.url }}
  
  steps:
  - name: Deploy to ${{ matrix.environment }}
    id: deploy
    run: |
      # 部署逻辑
      echo "Deploying to ${{ matrix.environment }}"
```

### 5.2 回滚策略

```yaml
rollback:
  runs-on: ubuntu-latest
  if: failure()
  
  steps:
  - name: Rollback deployment
    run: |
      # 回滚逻辑
      echo "Rolling back deployment"
```

## 6. 故障排除

### 6.1 常见问题

1. **内存不足**: 增加 `MAVEN_OPTS` 内存设置
2. **超时问题**: 设置合理的 `timeout-minutes`
3. **权限问题**: 确保正确设置 `permissions`

### 6.2 调试技巧

```yaml
# 开启调试模式
- name: Debug information
  run: |
    echo "Runner OS: ${{ runner.os }}"
    echo "GitHub Event: ${{ github.event_name }}"
    echo "Branch: ${{ github.ref }}"
    env
```

## 7. 参考资源

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [Spring Boot CI/CD 最佳实践](https://spring.io/guides/topicals/spring-boot-docker)
- [Vue.js 部署指南](https://cli.vuejs.org/guide/deployment.html)
- [Docker 多阶段构建](https://docs.docker.com/develop/dev-best-practices/)

---

*此文档基于 JeecgBoot 项目特点编写，可根据具体需求进行调整。*