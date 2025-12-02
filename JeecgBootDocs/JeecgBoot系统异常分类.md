# JeecgBoot系统异常分类

## 第一部分：异常汇总表格

### 1. 自定义异常类汇总

| 异常类名 | 包路径 | 继承关系 | 用途 | HTTP状态码 | 日志记录 |
|---------|--------|----------|------|------------|----------|
| `JeecgBootException` | org.jeecg.common.exception | RuntimeException | 基础业务异常 | 自定义/500 | 完整堆栈 |
| `JeecgBoot401Exception` | org.jeecg.common.exception | RuntimeException | 401未授权异常 | 401 | 完整堆栈 |
| `JeecgBootBizTipException` | org.jeecg.common.exception | RuntimeException | 业务提醒异常 | 自定义/500 | 仅记录消息 |
| `JeecgBootAssertException` | org.jeecg.common.exception | JeecgBootException | 断言失败异常 | 自定义/500 | 完整堆栈 |
| `JeecgSqlInjectionException` | org.jeecg.common.exception | RuntimeException | SQL注入检测异常 | 500 | 完整堆栈 |
| `RedisConnectException` | org.jeecg.modules.monitor.exception | Exception | Redis连接异常 | - | 需显式处理 |

### 2. 全局异常处理器处理的异常类型

| 异常类型 | HTTP状态码 | 处理方式 | 日志记录 | 返回消息示例 |
|---------|------------|----------|----------|-------------|
| `JeecgBootException` | 自定义/500 | 返回错误码和消息 | 记录完整堆栈 | "用户名已存在" |
| `JeecgBoot401Exception` | 401 | 返回401响应 | 记录完整堆栈 | "登录已过期，请重新登录" |
| `JeecgBootBizTipException` | 自定义/500 | 返回友好提示 | 仅记录消息 | "库存不足，无法完成订单" |
| `JeecgSqlInjectionException` | 500 | 安全提示 | 记录堆栈 | "校验失败，存在SQL注入风险！" |
| `MethodArgumentNotValidException` | 500 | 参数校验失败 | 记录堆栈 | "校验失败！参数验证错误" |
| `DuplicateKeyException` | 500 | 数据重复提示 | 记录堆栈 | "数据库中已存在该记录" |
| `UnauthorizedException` | 403 | 权限不足提示 | 记录堆栈 | "没有权限，请联系管理员分配权限！" |
| `NoHandlerFoundException` | 404 | 路径不存在 | 记录堆栈 | "路径不存在，请检查路径是否正确" |
| `MaxUploadSizeExceededException` | 500 | 文件过大提示 | 记录堆栈 | "文件大小超出10MB限制" |
| `DataIntegrityViolationException` | 500 | 数据完整性违反 | 记录堆栈 | "执行数据库异常,违反了完整性" |
| `PoolException` | 500 | Redis连接异常 | 记录堆栈 | "Redis 连接异常!" |
| `HttpRequestMethodNotSupportedException` | 405 | 请求方法不支持 | 记录堆栈 | "不支持POST请求方法，支持以下GET、PUT" |
| `MultipartException` | 500 | 文件上传异常 | 记录堆栈 | "文件大小超出限制" |

### 3. 异常分类汇总

| 分类 | 异常类型 | 使用场景 |
|------|----------|----------|
| **认证授权异常** | JeecgBoot401Exception, UnauthorizedException | Token过期、权限不足、登录失效 |
| **业务逻辑异常** | JeecgBootException, JeecgBootBizTipException | 业务规则验证失败、数据不存在 |
| **数据操作异常** | DuplicateKeyException, DataIntegrityViolationException | 数据库约束违反、数据完整性问题 |
| **请求处理异常** | MethodArgumentNotValidException, NoHandlerFoundException | 参数校验、接口不存在 |
| **文件处理异常** | MaxUploadSizeExceededException, MultipartException | 文件上传大小、格式问题 |
| **系统资源异常** | RedisConnectException, PoolException | 缓存连接、连接池问题 |
| **安全防护异常** | JeecgSqlInjectionException | SQL注入攻击检测 |

## 第二部分：使用实践

### 1. 异常选择指南

#### 1.1 基础业务异常处理
```java
// 通用业务异常 - 使用JeecgBootException
if (user == null) {
    throw new JeecgBootException("用户不存在", 404);
}

// 数据验证失败
if (StringUtils.isEmpty(username)) {
    throw new JeecgBootException("用户名不能为空", 400);
}
```

#### 1.2 友好提示异常处理
```java
// 业务规则验证 - 使用JeecgBootBizTipException
if (balance < amount) {
    throw new JeecgBootBizTipException("余额不足，请充值后再试");
}

// 操作限制提示
if (orderStatus.equals("已发货")) {
    throw new JeecgBootBizTipException("订单已发货，无法取消");
}
```

#### 1.3 权限认证异常处理
```java
// 认证失效 - 使用JeecgBoot401Exception
if (tokenExpired) {
    throw new JeecgBoot401Exception("登录已过期，请重新登录");
}

// 用户被禁用
if (user.getStatus() == 0) {
    throw new JeecgBoot401Exception("账号已被禁用，请联系管理员");
}
```

#### 1.4 安全防护异常处理
```java
// SQL注入检测 - 使用JeecgSqlInjectionException
if (SqlInjectionUtil.check(inputSql)) {
    throw new JeecgSqlInjectionException("存在SQL注入风险");
}

// 参数断言 - 使用JeecgBootAssertException
if (params == null) {
    throw new JeecgBootAssertException("参数不能为空");
}
```

### 2. 异常处理最佳实践

#### 2.1 异常响应格式标准化
```json
{
  "success": false,
  "message": "操作失败的具体原因",
  "code": 500,
  "result": null,
  "timestamp": 1692345678901
}
```

#### 2.2 异常日志记录策略
- **完整堆栈记录**: JeecgBootException、JeecgBoot401Exception等严重异常
- **简化日志记录**: JeecgBootBizTipException仅记录消息，减少日志噪音
- **安全信息过滤**: SQL注入异常不暴露敏感SQL语句
- **请求信息记录**: 包含URL、IP、用户信息等上下文

#### 2.3 常见场景处理示例

**用户管理场景:**
```java
@PostMapping("/add")
public Result<SysUser> addUser(@RequestBody SysUser user) {
    try {
        // 参数校验
        if (StringUtils.isEmpty(user.getUsername())) {
            throw new JeecgBootBizTipException("用户名不能为空");
        }
        
        // 业务规则检查
        if (userService.getUserByName(user.getUsername()) != null) {
            throw new JeecgBootBizTipException("用户名已存在");
        }
        
        // 执行业务逻辑
        userService.save(user);
        return Result.ok("用户创建成功");
        
    } catch (DuplicateKeyException e) {
        // 数据库唯一约束异常会被全局异常处理器捕获
        throw e;
    }
}
```

**文件上传场景:**
```java
@PostMapping("/upload")
public Result<String> uploadFile(@RequestParam("file") MultipartFile file) {
    try {
        // 文件大小检查 (全局异常处理器会自动处理MaxUploadSizeExceededException)
        if (file.getSize() > 10 * 1024 * 1024) {
            throw new JeecgBootBizTipException("文件大小不能超过10MB");
        }
        
        // 文件类型检查
        if (!isValidFileType(file.getOriginalFilename())) {
            throw new JeecgBootBizTipException("不支持的文件类型");
        }
        
        String url = fileService.upload(file);
        return Result.ok(url);
        
    } catch (IOException e) {
        throw new JeecgBootException("文件上传失败", e);
    }
}
```

### 3. 异常监控与运维建议

#### 3.1 异常告警配置
- **高优先级告警**: SQL注入异常、频繁401异常
- **中优先级告警**: 数据库连接异常、Redis连接异常
- **低优先级告警**: 业务提醒异常统计

#### 3.2 异常优化策略
- 合理使用`JeecgBootBizTipException`避免日志污染
- 定期分析异常统计，发现系统问题
- 对敏感异常信息进行脱敏处理
- 建立异常趋势监控和预警机制

#### 3.3 开发规范建议
1. **异常类型选择**: 根据业务场景选择合适的异常类型
2. **异常消息规范**: 提供清晰、友好的错误提示信息
3. **异常链保持**: 保留原始异常信息，便于问题追踪
4. **安全意识**: 避免在异常信息中暴露敏感数据

---
*文档生成时间: 2025-08-19*  
*JeecgBoot版本: 基于当前源码分析*