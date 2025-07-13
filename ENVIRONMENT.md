# JeecgBoot 环境配置说明

## 四环境配置架构

JeecgBoot项目采用四环境配置架构，确保不同环境的完全隔离和安全性。

### 1. Local Environment (本地开发环境)
- **Profile**: `local` (默认)
- **数据库**: `localhost:30004/jeecg-boot`
- **Redis**: `127.0.0.1:6379`
- **用途**: 开发者本地开发和调试
- **配置文件**: `application-local.yml`
- **特点**: 
  - 详细日志输出
  - 禁用定时任务和分布式锁
  - 开发友好的配置

### 2. CI Environment (持续集成环境)
- **Profile**: `ci`
- **数据库**: `127.0.0.1:3306/jeecg-boot` (GitHub Actions service)
- **Redis**: `127.0.0.1:6379`
- **用途**: GitHub Actions CI/CD自动化测试
- **配置文件**: `application-ci.yml`
- **特点**:
  - 最小化Web环境
  - 排除所有非必要自动配置
  - 优化的连接池配置
  - 最小化日志输出

### 3. UAT Environment (用户验收测试环境)
- **Profile**: `uat`
- **数据库**: `10.92.82.149:30004/jeecg-boot`
- **Redis**: `10.92.82.149:6379`
- **用途**: 用户验收测试
- **配置文件**: `application-uat.yml`
- **特点**:
  - 生产级配置
  - 启用所有功能模块
  - 适中的连接池配置

### 4. Production Environment (生产环境)
- **Profile**: `prod`
- **数据库**: 通过环境变量配置
- **Redis**: 通过环境变量配置
- **用途**: 生产部署
- **配置文件**: `application-prod.yml`
- **特点**:
  - 最高安全级别
  - 使用环境变量配置敏感信息
  - 启用SSL和完整监控
  - 生产级连接池配置

## 环境切换方法

### Maven命令行
```bash
# 本地环境 (默认)
mvn spring-boot:run

# CI环境
mvn spring-boot:run -Dspring.profiles.active=ci

# UAT环境
mvn spring-boot:run -Dspring.profiles.active=uat

# 生产环境
mvn spring-boot:run -Dspring.profiles.active=prod
```

### IDE配置
在IDE的Run Configuration中设置：
```
VM Options: -Dspring.profiles.active=local
```

### Docker部署
```bash
# UAT环境
docker run -e SPRING_PROFILES_ACTIVE=uat jeecg-boot:latest

# 生产环境
docker run -e SPRING_PROFILES_ACTIVE=prod \
  -e DB_HOST=prod-db-host \
  -e DB_USERNAME=jeecg_prod \
  -e DB_PASSWORD=secure_password \
  jeecg-boot:latest
```

## GitHub Actions CI
CI环境使用专门的配置：
- 自动创建MySQL数据库服务
- 导入初始化数据
- 执行单元测试和集成测试
- 生成测试报告

## 安全注意事项
1. **生产环境密码**: 必须通过环境变量或密钥管理系统配置
2. **数据库隔离**: 各环境使用完全独立的数据库
3. **网络隔离**: UAT和生产环境应配置防火墙规则
4. **配置管理**: 敏感配置不应提交到代码仓库

## 故障排除
如果遇到数据库连接问题：
1. 确认当前激活的profile
2. 检查对应环境的数据库是否可访问
3. 验证用户名密码配置
4. 检查网络连接和防火墙设置