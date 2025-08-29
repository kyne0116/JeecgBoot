# SIMBEST 个性化定制

本文档记录了基于 JeecgBoot 框架的 SIMBEST 个性化定制功能。采用时间倒序排列，最新功能在前，便于快速迭代更新。

## 一、功能概览（按时间倒序）

> 💡 **新增功能请在此表格顶部直接追加新行**

| 定制时间   | 功能名称                          | 主要文件                                                                                                                                                   | 功能描述                                                                             | 状态 |
| ---------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ---- |
| 2025-08-28 | 增强型 Redis 工具类               | SimbestRedisUtil.java                                                                                                                                      | 支持中文 Key 自动编码、应用前缀管理、分布式锁、双向转换的 Redis 工具类               | ✅   |
| 2025-08-27 | 用户身份信息控制台显示功能        | user.ts                                                                                                                                                    | 登录成功后在浏览器控制台显示用户完整身份信息，包含用户基本信息、部门信息、权限代码等 | ✅   |
| 2025-08-26 | OceanBase Oracle 兼容模式分页优化 | CustomPaginationInnerInterceptor.java<br/>MybatisPlusSaasConfig.java<br/>GlobalPaginationConfig.java                                                       | 解决 OceanBase Oracle 兼容模式下分页 SQL 语法不兼容问题（三层防护方案）              | ⚡   |
| 2025-08-15 | MyBatis-Plus 升级及数据库优化     | pom.xml<br/>SysDepart.java<br/>SysUser.java<br/>SysDepartController.java                                                                                   | MyBatis-Plus 版本升级，添加数据库唯一索引，优化查询性能                              | ✅   |
| 2025-08-14 | UUMS 组织用户同步功能             | SimbestAppToken.java<br/>UumsChangeOrgLogController.java<br/>UumsChangeUserLogController.java<br/>SyncUumsOrgScheduler.java<br/>SyncUumsUserScheduler.java | 第三方应用 Token 管理、组织用户变更日志记录、定时同步功能                            | ✅   |
| 2025-08-14 | 启动配置信息打印功能              | JeecgSystemApplication.java                                                                                                                                | 应用启动时打印 Profile、数据库、Redis 等关键配置信息                                 | ✅   |
| 2025-08-13 | 单点登录(SSO)功能                 | SsoLoginController.java<br/>useSso.ts<br/>permissionGuard.ts                                                                                               | 支持第三方系统通过用户名参数实现免密单点登录                                         | ✅   |
| 2025-08-02 | 系统心跳检测功能                  | SysHealthController.java                                                                                                                                   | 提供系统健康状态检查接口，支持 HEAD 请求心跳检测                                     | ✅   |
| 2025-07-31 | 日志生成规则定制                  | logback-spring.xml                                                                                                                                         | 按端口和日志级别分离的自定义日志配置                                                 | ✅   |

## 二、功能详细说明（按时间倒序）

> 💡 **新增功能请在此部分顶部直接插入新的章节**

### 2025-08-28：增强型 Redis 工具类

**功能概述：** 提供支持中文 Key 自动编码、应用前缀管理、分布式锁、双向转换等功能的增强型 Redis 工具类，解决 JeecgBoot 项目中 Redis 操作的常见问题。

**需求背景：** 在 JeecgBoot 系统开发过程中，经常需要使用 Redis 进行缓存、分布式锁等操作，但原生 Redis 操作存在以下问题：

- 中文 Key 在 Redis 中存储可能出现乱码或兼容性问题
- 多应用共享 Redis 时缺乏 Key 前缀隔离机制
- 缺乏统一的分布式锁实现
- 无法方便地进行中文 Key 的双向转换和调试

**技术分析发现：** 通过深入分析 JeecgBoot 框架的模块依赖关系，发现原始工具类放置在`jeecg-system-start`模块会导致循环依赖问题。按照 JeecgBoot 技术栈规范，通用工具类应放置在`jeecg-boot-base-core`模块的`common.util`包下。

**涉及文件：**

#### 后端文件

**2.1 SimbestRedisUtil.java（新增）**

- **路径：** `jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/common/util/SimbestRedisUtil.java`
- **功能摘要：** 增强型 Redis 工具类，提供中文 Key 支持、应用前缀管理、分布式锁等功能
- **核心特性：**
  - **自动前缀管理：** 基于`spring.application.name`自动生成 Key 前缀，支持多应用 Redis 隔离
  - **中文 Key 支持：** 自动检测中文字符并进行 Base64 编码，确保 Redis 兼容性
  - **双向转换：** 支持编码 Key 解码回原始中文，便于调试和管理
  - **分布式锁：** 提供基于 Redis 的分布式锁实现，支持超时和安全释放
  - **性能监控：** 可选的操作日志和性能监控功能
  - **操作封装：** 封装常用的 String、Object 操作，简化使用

**核心方法：**

- **Key 管理：** `hasKey()`, `delete()`, `expire()`, `getExpire()`
- **String 操作：** `set()`, `get()`, `increment()`
- **Object 操作：** `setObject()`, `getObject()`
- **分布式锁：** `tryLock()`, `releaseLock()`
- **中文转换：** `decodeKey()`, `decodeKeys()`, `previewKey()`
- **工具方法：** `isEncodedKey()`, `isChineseKey()`, `generateUniqueId()`

**配置参数：**

```yaml
# 应用名称（自动作为Redis key前缀）
spring:
  application:
    name: jeecg-boot

# 可选配置
jeecg:
  redis:
    log:
      enabled: false # 启用操作日志
    monitor:
      enabled: false # 启用性能监控
```

**架构设计：**

**中文 Key 编码机制：**

- **检测算法：** 使用`Character.UnicodeScript.HAN`精确检测中文字符
- **编码格式：** `b64_{Base64编码}`，保持可读性和唯一性
- **编码示例：** `用户:张三` → `b64_55So57K35byg5LiJ`
- **前缀组合：** `{应用名}:b64_{Base64编码}`

**分布式锁实现：**

- **获取锁：** 使用`setIfAbsent`原子操作
- **超时保护：** 支持自定义超时时间，防止死锁
- **安全释放：** 使用 Lua 脚本确保只能释放自己持有的锁
- **唯一标识：** 每次获取锁生成唯一 requestId

**性能优化：**

- **批量操作：** 支持批量 Key 删除和解码
- **监控可选：** 性能监控功能可配置开关
- **异常处理：** 完善的异常处理和降级机制

### 2025-08-27：用户身份信息控制台显示功能

**功能概述：** 在用户登录成功后，自动在浏览器控制台以结构化方式显示用户的完整身份信息，帮助开发和运维人员快速了解当前用户的身份和权限状况。

**需求背景：** 在 JeecgBoot 系统的日常开发和调试过程中，开发人员需要快速了解当前登录用户的身份信息、权限范围和系统配置状态，传统方式需要查看多个接口或数据库，效率较低。

**技术分析发现：** 通过深入分析 JeecgBoot 框架的权限管理机制，发现系统采用 BACK 后台权限模式，前端权限控制基于权限代码列表而非角色信息，这是 JeecgBoot 区别于传统 RBAC 系统的重要特征。

**涉及文件：**

#### 前端文件

**2.1 user.ts（修改）**

- **路径：** `jeecgboot-vue3/src/store/modules/user.ts`
- **功能摘要：** 用户状态管理模块，在用户登录成功后自动打印身份信息
- **核心变更：**
  - **afterLoginAction 方法修改（第 213 行）：** 添加 `await this.printUserIdentityInfo();` 调用
  - **新增 printUserIdentityInfo 方法（第 398-522 行）：** 核心功能实现方法
- **核心特性：**
  - **异步权限获取：** 主动调用权限接口获取用户权限代码列表
  - **智能数据处理：** 自动处理权限数据为空的情况，确保信息完整性
  - **结构化显示：** 采用 console.group 和 console.table 提供清晰的信息层级
  - **浏览器兼容：** 兼容 Chrome、Firefox、Edge、Safari 等主流浏览器
- **显示内容：**
  - **👤 核心身份信息：** 用户账号、真实姓名、租户 ID、部门编码、部门名称
  - **🔐 权限信息：** 完整权限编码列表（逗号分隔显示）
  - **🏢 部门信息：** 部门详细信息表格

**技术架构深度分析：**

**JeecgBoot 权限管理机制：**

- **权限模式：** 采用 BACK 后台权限模式（`projectSetting.ts:35`）
- **控制机制：** 前端权限判断基于`permissionStore.getPermCodeList`，而非传统的角色列表
- **数据流向：** 登录 → 获取用户基本信息 → 获取权限代码 → 前端权限控制
- **API 架构：**
  - `/sys/login`：返回用户基本信息，不包含角色数据
  - `/sys/user/getUserInfo`：获取用户详细信息，同样不包含角色
  - `/sys/permission/getUserPermissionByToken`：获取权限代码列表和菜单数据

**实现方案：**

```typescript
/**
 * 打印用户身份信息到控制台
 */
async printUserIdentityInfo() {
  try {
    const userInfo = this.getUserInfo || {};
    const loginInfo = this.getLoginInfo || {};
    const tenantId = this.getTenant || '';

    // 主动获取权限信息
    const { usePermissionStore } = await import('/@/store/modules/permission');
    const permissionStore = usePermissionStore();
    let codeList = permissionStore.getPermCodeList || [];

    // 如果权限为空，主动调用权限接口
    if (codeList.length === 0) {
      const { getBackMenuAndPerms } = await import('/@/api/sys/menu');
      const permissionData = await getBackMenuAndPerms();
      if (permissionData?.codeList) {
        codeList = permissionData.codeList;
        permissionStore.setPermCodeList(codeList);
      }
    }

    // 存储权限数据用于显示
    (this as any).currentPermissions = codeList;

    // 获取部门信息
    const departs = loginInfo?.departs || [];
    const currentDepart = departs.find(dept => dept.orgCode === userInfo.orgCode) || departs[0];

    // 控制台结构化输出
    console.group('🎉 JeecgBoot 用户身份信息');
    console.log('%c============== 用户登录成功 ==============',
                'color: #52c41a; font-weight: bold; font-size: 16px;');

    // 核心身份信息表格
    console.group('👤 核心身份信息');
    console.table({
      '用户账号': userInfo.username || 'N/A',
      '真实姓名': userInfo.realname || 'N/A',
      '租户ID': tenantId || 'N/A',
      '部门编码': userInfo.orgCode || 'N/A',
      '部门名称': currentDepart?.departName || 'N/A'
    });
    console.groupEnd();

    // 权限信息
    if (codeList.length > 0) {
      console.group('🔐 权限信息');
      console.log('%c权限编码:', 'color: #722ed1; font-weight: bold;',
                  codeList.join(', '));
      console.groupEnd();
    }

    // 部门信息表格（如果存在）
    if (departs.length > 0) {
      console.group('🏢 部门信息');
      console.table(departs.map(dept => ({
        '部门名称': dept.departName,
        '部门编码': dept.orgCode,
        '部门ID': dept.id,
        '上级部门': dept.parentId
      })));
      console.groupEnd();
    }

    console.groupEnd();
  } catch (error) {
    console.error('❌ 打印用户身份信息时出错:', error);
  }
}
```

**浏览器兼容性：**

- **✅ 完全兼容：** Chrome 63+、Firefox 67+、Edge 79+、Safari 11.1+
- **核心 API 支持：** console.group/table 在 2013 年以来所有主流浏览器支持
- **现代特性：** async/await、动态 import 等基于 Vue3 项目标准，构建工具自动处理兼容性
- **样式兼容：** Chrome/Edge 效果最佳，Firefox/Safari 支持基本样式，不影响信息可读性

**架构优势：**

- **零侵入性：** 不影响现有业务功能，仅在登录时执行
- **自适应：** 自动处理权限数据获取，兼容各种权限配置状态
- **调试友好：** 结构化显示便于快速定位用户权限问题
- **性能优化：** 仅在登录时执行一次，不影响系统运行性能

### 2025-08-26：OceanBase Oracle 兼容模式分页优化

**功能概述：** 解决 JeecgBoot 在 OceanBase Oracle 兼容模式部署时出现的分页 SQL 语法不兼容问题，通过**三层防护架构**确保分页插件在各种部署场景下都能正确识别和处理数据库方言。

**问题背景：**

- **报错现象：** 在 OceanBase Oracle 兼容模式下，MyBatis Plus 生成 MySQL 语法的`LIMIT`分页 SQL，导致 Oracle 语法错误
- **错误信息：** `ORA-00900: You have an error in your SQL syntax; check the manual that corresponds to your OceanBase version for the right syntax to use near 'LIMIT 10' at line 1`
- **根本原因：** MyBatis Plus 的`PaginationInnerInterceptor`无法正确识别 OceanBase Oracle 兼容模式，同时动态多数据源配置可能产生独立的 SqlSessionFactory，导致自定义配置失效

**技术难点：**

- **多数据源复杂性：** 系统使用`dynamic-datasource-spring-boot-starter 4.1.3`，可能创建多个独立的 SqlSessionFactory
- **配置优先级问题：** 自动配置可能覆盖手工配置的 MyBatis 插件
- **方言检测盲区：** 标准 MyBatis Plus 对新兴数据库（OceanBase）的兼容模式识别存在盲区

**涉及文件：**

#### 三层防护架构设计

**第一层：智能分页插件（核心）**

**1.1 CustomPaginationInnerInterceptor.java（新增）**

- **路径：** `jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/mybatis/CustomPaginationInnerInterceptor.java`
- **功能摘要：** 自定义分页插件，专门处理 OceanBase Oracle 兼容模式的数据库方言识别
- **核心特性：**
  - **智能方言识别：** 通过 JDBC URL 检测 OceanBase Oracle 兼容模式（`:oceanbase:oracle:`）
  - **Oracle 方言适配：** 自动使用 Oracle 分页方言，生成正确的`ROWNUM`分页语法
  - **兼容性处理：** 支持标准 Oracle 数据库和其他数据库的默认处理
  - **增强调试日志：** 详细的数据库连接检测和方言选择日志，包含数据库产品名称和 URL 信息
- **核心方法：**
  - `findIDialect()` - 重写父类方法，实现智能数据库方言识别
  - `getDbTypeDescription()` - 获取数据库类型描述，用于调试

**第二层：主配置强化（优先级保障）**

**1.2 MybatisPlusSaasConfig.java（修改）**

- **路径：** `jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/mybatis/MybatisPlusSaasConfig.java`
- **功能摘要：** MyBatis Plus 配置类，替换标准分页插件为自定义分页插件，并确保配置优先级
- **核心变更：**
  - **插件替换：** 将`PaginationInnerInterceptor`替换为`CustomPaginationInnerInterceptor`
  - **优先级保障：** 添加`@Primary`注解确保配置优先级高于自动配置
  - **增强日志：** 添加配置加载确认日志，便于验证配置是否生效
  - **导入依赖：** 添加`lombok.extern.slf4j.Slf4j`支持日志功能

**第三层：全局后处理器（终极保障）**

**1.3 GlobalPaginationConfig.java（新增）**

- **路径：** `jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/mybatis/GlobalPaginationConfig.java`
- **功能摘要：** 全局分页配置后处理器，确保所有 SqlSessionFactory 都使用自定义分页插件
- **核心特性：**
  - **Bean 后处理：** 实现`BeanPostProcessor`接口，在 Spring 容器初始化 Bean 后进行处理
  - **SqlSessionFactory 扫描：** 自动检测所有 SqlSessionFactory 实例
  - **缺失插件补偿：** 为没有分页拦截器的 SqlSessionFactory 自动添加自定义分页插件
  - **详细日志记录：** 打印所有 SqlSessionFactory 的拦截器列表，便于调试验证
- **核心方法：**
  - `postProcessAfterInitialization()` - Bean 后处理主方法
- **处理逻辑：**
  ```java
  // 检测SqlSessionFactory并补偿缺失的分页插件
  if (!hasPaginationInterceptor) {
      MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
      interceptor.addInnerInterceptor(new CustomPaginationInnerInterceptor());
      configuration.addInterceptor(interceptor);
  }
  ```

**技术实现细节：**

```java
// 第一层：智能方言识别
if (jdbcUrl.contains(":oceanbase:oracle:") ||
    (jdbcUrl.contains(":oceanbase:") && jdbcUrl.contains("oracle"))) {
    log.info(">>> 检测到OceanBase Oracle兼容模式，强制使用Oracle分页方言");
    return DialectFactory.getDialect(DbType.ORACLE);
}

// 第二层：配置优先级保障
@Bean
@Primary  // 确保优先级高于自动配置
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    interceptor.addInnerInterceptor(new CustomPaginationInnerInterceptor());
}

// 第三层：全局后处理补偿
@Component
public class GlobalPaginationConfig implements BeanPostProcessor {
    // 确保所有SqlSessionFactory都有正确的分页插件
}
```

**架构优势：**

- **多重保障：** 三层防护确保在各种部署场景下都能正确处理分页
- **自动适配：** 智能识别数据库类型，无需手动配置
- **故障自愈：** 即使主配置失效，后处理器仍能补偿修复
- **调试友好：** 详细的日志输出便于问题排查和验证

**解决效果：**

- **SQL 语法修正：** MySQL 的`LIMIT ?` → Oracle 的`WHERE ROWNUM <= ?`
- **多数据源兼容：** 解决动态多数据源配置下的插件失效问题
- **配置冲突消除：** 通过优先级控制避免自动配置覆盖
- **零配置部署：** 支持 OceanBase Oracle 兼容模式的开箱即用

### 2025-08-15：MyBatis-Plus 升级及数据库优化

**功能概述：** 升级 MyBatis-Plus 版本并优化系统数据库性能，主要包括版本升级、添加数据库唯一索引、优化查询性能等核心改进。

**涉及文件：**

#### 后端文件

**1.1 pom.xml（修改）**

- **路径：** `jeecg-boot/pom.xml`
- **功能摘要：** Maven 项目配置文件，升级 MyBatis-Plus 版本
- **核心变更：**
  - **版本升级：** MyBatis-Plus 从 3.5.3.2 升级到 3.5.6
  - **兼容性改进：** 支持更好的数据库操作性能和稳定性
  - **特性增强：** 获得最新版本的功能特性和 bug 修复

**1.2 SysDepart.java（修改）**

- **路径：** `jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysDepart.java`
- **功能摘要：** 系统部门实体类，添加数据库索引注解优化查询性能
- **核心变更：**
  - **代码格式化：** 统一代码注释格式和导入语句顺序
  - **数据库索引：** 为 orgCode 和 uumsOrgCode 字段添加@Column(unique = true)注解
  - **表字段映射：** 添加@TableField(value = "org_code")和@TableField(value = "uums_org_code")明确字段映射
  - **性能优化：** 通过唯一索引提升基于机构编码的查询性能

**1.3 SysUser.java（修改）**

- **路径：** `jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysUser.java`
- **功能摘要：** 系统用户实体类，添加数据库索引和表结构优化
- **核心变更：**
  - **表注解增强：** 添加@TableName(value = "sys_user")明确表映射
  - **复合索引：** 通过@Table 注解添加 idx_username_orgcode 复合唯一索引
  - **唯一性约束：** 为 username 字段添加@Column(unique = true)注解
  - **代码格式化：** 统一代码风格和注释格式

**1.4 SysDepartController.java（修改）**

- **路径：** `jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/SysDepartController.java`
- **功能摘要：** 系统部门控制器，新增高性能查询接口
- **核心方法：**
  - `getByUumsOrgCode()` - 根据 UUMS 机构编码查询单条部门记录（高性能版）
- **性能优化：**
  - **索引查询：** 利用 uumsOrgCode 唯一索引进行高效查询
  - **条件过滤：** 只查询未删除的记录(delFlag=0)
  - **错误处理：** 完善的异常处理和日志记录
  - **调试信息：** 添加详细的 debug 日志便于问题排查

### 2025-08-14：UUMS 组织用户同步功能

**功能概述：** 实现与 UUMS 主数据系统的组织用户同步功能，包括第三方应用 Token 管理、变更日志记录、定时同步等核心功能。

**涉及文件：**

#### 后端文件

**1.1 SimbestAppToken.java（新增）**

- **路径：** `jeecg-boot/jeecg-boot-module/jeecg-module-dictd/src/main/java/org/jeecg/modules/dictd/simbest/token/SimbestAppToken.java`
- **功能摘要：** 第三方应用 Token 管理类，提供获取和缓存第三方应用 access token 的功能
- **核心特性：**
  - **Token 获取：** 通过`getAccessToken(appcode, appurl)`静态方法获取第三方应用访问令牌
  - **Redis 缓存：** 支持 Token 的 Redis 缓存存储，避免频繁 API 调用
  - **并发控制：** 使用 ReentrantLock 防止并发请求同一 appcode 时的重复调用
  - **过期管理：** 自动计算缓存过期时间，比 expires_in 少 60 秒避免边界问题
- **TokenResponse 内部类：** 封装 access token 响应信息（accessToken, tokenType, expiresIn, scope）

**1.2 UumsChangeOrgLogController.java（新增）**

- **路径：** `jeecg-boot/jeecg-boot-module/jeecg-module-dictd/src/main/java/org/jeecg/modules/dictd/simbest/uums/controller/UumsChangeOrgLogController.java`
- **功能摘要：** 主数据组织变更日志控制器，提供组织变更数据的 CRUD 操作和同步功能
- **核心方法：**
  - `syncOrg()` - 组织数据同步接口，支持时间范围查询参数
  - `queryPageList()` - 分页查询组织变更日志
  - 标准 CRUD 操作（增删改查、批量删除、Excel 导入导出）
- **同步示例：** 集成 SimbestAppToken 获取访问令牌，演示 JSON 转换操作

**1.3 UumsChangeUserLogController.java（新增）**

- **路径：** `jeecg-boot/jeecg-boot-module/jeecg-module-dictd/src/main/java/org/jeecg/modules/dictd/simbest/uums/controller/UumsChangeUserLogController.java`
- **功能摘要：** 主数据用户变更日志控制器，提供用户变更数据的 CRUD 操作
- **核心特性：** 完整的用户变更日志管理功能，包括分页查询、增删改查、Excel 导入导出

**1.4 SyncUumsOrgScheduler.java（新增）**

- **路径：** `jeecg-boot/jeecg-boot-module/jeecg-module-dictd/src/main/java/org/jeecg/modules/dictd/simbest/uums/scheduler/SyncUumsOrgScheduler.java`
- **功能摘要：** 组织数据同步定时任务调度器
- **核心特性：**
  - **定时执行：** 每天凌晨 2 点执行组织同步任务（cron = "0 0 2 \* \* ?"）
  - **配置注入：** 自动注入 AppConfig 获取 UUMS 系统地址
  - **加密工具：** 集成 EncryptorUtil 实现用户名加密功能

**1.5 SyncUumsUserScheduler.java（新增）**

- **路径：** `jeecg-boot/jeecg-boot-module/jeecg-module-dictd/src/main/java/org/jeecg/modules/dictd/simbest/uums/scheduler/SyncUumsUserScheduler.java`
- **功能摘要：** 用户数据同步定时任务调度器
- **核心特性：** 每天凌晨 2 点执行用户同步任务，与组织同步任务并行执行

### 2025-08-14：启动配置信息打印功能

**功能概述：** 在应用启动完成后自动打印系统关键配置信息，便于开发和运维人员快速了解当前运行环境的配置状态。

**涉及文件：**

#### 后端文件

**1.1 JeecgSystemApplication.java（修改）**

- **路径：** `jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/java/org/jeecg/JeecgSystemApplication.java`
- **功能摘要：** 系统主启动类，在 Spring 应用启动完成后打印详细的配置信息
- **核心方法：**
  - `printSystemInfo()` - 打印系统配置信息，包括 Profile、数据库、Redis 等
  - `printAccessInfo()` - 打印系统访问地址信息
- **主要特性：**
  - **Profile 信息：** 显示当前激活的 Spring Profile
  - **数据库配置：** 显示动态数据源主库连接信息
  - **Redis 配置：** 显示 Redis 服务器地址、端口和数据库编号
  - **UUMS 集成：** 显示 UUMS 系统地址配置
  - **访问地址：** 显示本地和外部访问 URL，包括 Swagger 文档地址

**修改内容：**

- 新增 `printSystemInfo()` 方法，从 Environment 中获取并格式化打印关键配置信息
- 重构原有的访问地址打印逻辑到 `printAccessInfo()` 方法
- 添加 `Arrays` 工具类导入用于 Profile 数组显示

**与系统监听器的关系：**

- **执行时序：** 在 Spring 容器完全启动后立即执行，早于 `ApplicationReadyEvent` 监听器
- **SystemInitListener：** 负责路由配置初始化，优先级为 1
- **CodeTemplateInitListener：** 负责代码生成器模板初始化
- **区别定位：** 启动类负责配置信息展示，监听器负责具体业务初始化

### 2025-08-13：单点登录(SSO)功能

**功能概述：** 实现第三方系统通过用户名参数免密登录当前系统的单点登录功能。

**涉及文件：**

#### 后端文件

**1.1 SsoLoginController.java**

- **路径：** `jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/SsoLoginController.java`
- **功能摘要：** SSO 单点登录控制器，提供单一接口接受用户名参数，验证用户有效性，生成 JWT token，并重定向到前端系统
- **核心方法：**
  - `ssoLogin()` - 处理 SSO 登录请求
  - `performSsoLogin()` - 执行 SSO 登录核心逻辑
  - `getFrontendUrl()` - 获取前端系统 URL

**1.2 SsoLoginModel.java**

- **路径：** `jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/model/SsoLoginModel.java`
- **功能摘要：** SSO 登录请求模型，定义单点登录所需的参数结构
- **主要属性：** username（用户名）

**1.3 ShiroConfig.java（修改）**

- **路径：** `jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/java/org/jeecg/config/shiro/ShiroConfig.java`
- **功能摘要：** 在 Shiro 安全配置中添加 SSO 接口白名单，允许匿名访问
- **修改内容：** 添加 `/sys/sso/**` 路径到匿名访问列表

#### 前端文件

**1.4 useSso.ts（修改）**

- **路径：** `jeecgboot-vue3/src/hooks/web/useSso.ts`
- **功能摘要：** SSO 登录钩子函数，处理 URL 中的 token 参数，实现自动登录
- **核心方法：**
  - `ssoLogin()` - 检测 URL 中的 token 参数并设置到用户存储
- **修改内容：** 增强 token 参数检测和处理逻辑

**1.5 permissionGuard.ts（修改）**

- **路径：** `jeecgboot-vue3/src/router/guard/permissionGuard.ts`
- **功能摘要：** 权限路由守卫，负责路由权限验证和动态路由构建
- **修改内容：**
  - 移除重复的 token 处理逻辑，确保 SSO 登录流程的正确性
  - 增加 error 参数检查，SSO 登录失败时清除缓存 token

**1.6 user.ts（修改）**

- **路径：** `jeecgboot-vue3/src/store/modules/user.ts`
- **功能摘要：** 用户状态管理，处理用户信息和 token
- **修改内容：** 优化 setToken 方法，token 为空时自动清除相关用户信息和缓存

### 2025-08-02：系统心跳检测功能

**功能概述：** 提供系统健康状态检查接口，支持外部监控系统通过 HEAD 请求进行心跳检测。

**涉及文件：**

**2.1 SysHealthController.java**

- **路径：** `jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/java/org/jeecg/simbest/sys/web/SysHealthController.java`
- **功能摘要：** 系统健康检查控制器，提供匿名访问的心跳检测接口
- **核心特性：**
  - 使用 `@IgnoreAuth` 注解，无需身份验证
  - 支持 HEAD 方法请求
  - 返回简单的成功状态
- **接口路径：** `/sys/health/anonymous/heart`

### 2025-07-31：日志生成规则定制功能

**功能概述：** 自定义 logback 日志配置，实现按端口和日志级别分离的日志文件管理。

**涉及文件：**

**3.1 logback-spring.xml**

- **路径：** `jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/logback-spring.xml`
- **功能摘要：** Logback 日志配置文件，实现自定义的日志输出规则
- **核心特性：**
  - **按端口分离：** 日志文件名包含端口号，支持多实例部署
  - **按级别分离：** 分别输出 ERROR、WARN、INFO、DEBUG 四个级别的日志文件
  - **滚动策略：** 按日期和文件大小（10MB）进行日志滚动
  - **环境区分：** 不同环境（dev/uat/test vs prd）使用不同的日志级别
- **日志文件结构：**
  ```
  ./boot_app_logs/dictd/
  ├── log_error-{port}.log      # 错误日志
  ├── log_warn-{port}.log       # 警告日志
  ├── log_info-{port}.log       # 信息日志
  ├── log_debug-{port}.log      # 调试日志
  └── [error|warn|info|debug]/  # 归档日志目录
  ```
- **自定义配置：**
  - 日志格式包含线程、级别、类名、方法名、行号
  - 控制台输出带彩色格式
  - 特定框架日志级别调优（如 Hibernate、Spring 等）

## 三、使用说明

> 💡 **新增功能使用说明请按功能名称追加新的小节**

### 用户身份信息控制台显示功能

```
功能触发：
用户登录成功后，控制台自动显示身份信息，无需手动操作

显示效果示例：
🎉 JeecgBoot 用户身份信息
  ============== 用户登录成功 ==============

  👤 核心身份信息
  ┌─────────────┬────────────────────┐
  │    (index)  │       Values       │
  ├─────────────┼────────────────────┤
  │   用户账号   │     qinfumin       │
  │   真实姓名   │      秦富民        │
  │   租户ID    │        0           │
  │   部门编码   │  A03A01A10A01A04   │
  │   部门名称   │    数据字典中心      │
  └─────────────┴────────────────────┘

  🔐 权限信息
    权限编码: datas:us_dictd_datas_subcharttype:exportXls, pages:us_dictd_pages_pageinfo:delete, ...

  🏢 部门信息
  ┌─────────────┬────────────────────┐
  │    (index)  │       Values       │
  ├─────────────┼────────────────────┤
  │   部门名称   │    数据字典中心      │
  │   部门编码   │  A03A01A10A01A04   │
  │   部门ID    │   1823912482841    │
  │   上级部门   │   1823871923741    │
  └─────────────┴────────────────────┘

调试功能：
- 快速了解当前用户权限范围
- 验证部门信息配置正确性
- 排查权限相关问题
- 确认租户配置状态

开发模式控制：
可通过localStorage控制显示：
localStorage.setItem('debug_user_info', 'true')  // 强制启用
localStorage.removeItem('debug_user_info')       // 恢复默认

浏览器兼容性：
- Chrome/Edge：完整功能，样式效果最佳
- Firefox：支持全部功能，部分样式简化
- Safari：支持全部功能，部分样式简化
- 移动端：开发者工具中正常显示

技术说明：
- 基于JeecgBoot BACK权限模式设计
- 权限控制基于权限代码，而非传统角色
- 自动获取权限数据，处理空数据情况
- 零性能影响，仅在登录时执行一次
```

### OceanBase Oracle 兼容模式分页优化功能（三层防护）

```
问题诊断：
当出现分页SQL语法错误时，检查以下几点：
1. 数据库连接URL是否包含":oceanbase:oracle:"
2. 错误信息是否包含"LIMIT"语法错误
3. 检查应用启动日志中的三层防护执行情况

三层防护验证：
第一层验证（智能分页插件）：
1. 启动应用后查看日志输出：
   "=== 自定义分页插件方言检测 ==="
   ">>> 检测到OceanBase Oracle兼容模式，强制使用Oracle分页方言"
   ">>> 返回Oracle方言实现: OracleDialect"

第二层验证（主配置强化）：
2. 确认配置加载日志：
   "=== MyBatis Plus配置初始化：MybatisPlusSaasConfig ==="
   "=== 已加载自定义分页插件：CustomPaginationInnerInterceptor ==="

第三层验证（全局后处理器）：
3. 检查SqlSessionFactory处理日志：
   "=== 检测到SqlSessionFactory: xxx ==="
   ">>> SqlSessionFactory xxx 拦截器列表:"
   "    - CustomPaginationInnerInterceptor"

功能测试：
4. 测试分页接口，确认SQL语法正确：
   http://localhost:54009/dictd/datas/usDictdDatasIndicatordashboard/list?pageNo=1&pageSize=10

5. 观察生成的分页SQL应为Oracle格式：
   SELECT * FROM (SELECT ...) WHERE ROWNUM <= ?

兼容性说明：
- ✅ OceanBase Oracle兼容模式：三层防护自动识别，强制使用Oracle方言
- ✅ OceanBase MySQL兼容模式：自动使用MySQL分页方言
- ✅ 标准Oracle数据库：正常使用Oracle分页方言
- ✅ MySQL数据库：使用MySQL分页方言
- ✅ PostgreSQL数据库：使用PostgreSQL分页方言
- ✅ 多数据源环境：后处理器确保所有SqlSessionFactory都有正确配置

故障排除（分层诊断）：
如果分页仍有问题，请按层级检查：

第一层故障：
- 确认CustomPaginationInnerInterceptor类已正确编译
- 查看方言检测日志是否输出正确的数据库类型

第二层故障：
- 确认MybatisPlusSaasConfig配置类是否被Spring加载
- 检查@Primary注解是否生效，确保配置优先级

第三层故障：
- 查看GlobalPaginationConfig是否扫描到所有SqlSessionFactory
- 确认后处理器是否为缺失插件的SqlSessionFactory补偿了分页插件

终极诊断：
- 开启DEBUG日志级别，观察完整的MyBatis插件加载过程
- 使用SQL监控工具（如Druid）观察实际执行的分页SQL语法
```

### MyBatis-Plus 升级及数据库优化功能

```
版本升级信息：
MyBatis-Plus: 3.5.3.2 → 3.5.6

数据库索引优化：
- sys_depart表：org_code、uums_org_code字段添加唯一索引
- sys_user表：username字段添加唯一索引，username+org_code添加复合唯一索引

新增API接口：
http://localhost:54009/dictd/sys/sysDepart/getByUumsOrgCode?uumsOrgCode=001001

性能提升：
- 部门查询性能优化，特别是基于UUMS机构编码的查询
- 用户查询性能优化，减少重复数据风险
- 支持更高并发的数据库操作

代码质量改进：
- 统一代码格式和注释规范
- 增强错误处理和日志记录
- 明确数据库字段映射关系
```

### UUMS 组织用户同步功能

```
Token获取示例：
SimbestAppToken.TokenResponse token = SimbestAppToken.getAccessToken("UUMS", "http://uums-server/oauth/token");

组织同步接口：
http://localhost:54009/dictd/uums/uumsChangeOrgLog/syncOrg?startDate=2025-08-01&endDate=2025-09-01

定时任务：
- 组织同步：每天凌晨2点执行
- 用户同步：每天凌晨2点执行

加密工具使用：
EncryptorUtil.encode("SIMBEST_SSO", "username")
```

### 启动配置信息打印功能

```
启动应用后，控制台将自动显示配置信息：
========================================
系统配置信息:
激活Profile: [dev]
数据库连接: jdbc:mysql://localhost:30004/jeecg-boot?characterEncoding=UTF-8&useUnicode=true&useSSL=false...
Redis服务: localhost:40004 (DB:0)
UUMS地址: http://10.92.82.161:8088/uums
========================================
功能：便于开发人员快速确认系统配置状态
```

### 单点登录(SSO)功能

```
访问URL：http://localhost:54009/dictd/sys/sso/login?username=19DCD18830DCF45F947157A66D64C155CBA7DC8BD8588AA4F76790A1690B2A162B33FA8867E852E25858102DE36CE16BAFE71B58CAD768EE6F29EA5B11F71664
功能：验证用户并自动登录到系统首页
```

### 系统心跳检测功能

```
检测URL：http://localhost:54009/dictd/sys/health/anonymous/heart
方法：HEAD
功能：检查系统健康状态
```

### 日志生成规则定制功能

```
日志目录：./boot_app_logs/dictd/
按端口和级别区分的日志文件便于问题排查和系统监控
```

---

## 四、快速更新指南

### 新增功能时的更新步骤

1. **在概览表顶部追加新行**

   ```markdown
   | 2025-XX-XX | 新功能名称 | 主要文件 | 功能描述 | ⚡ |
   ```

2. **在详细说明部分顶部插入新章节**

   ```markdown
   ### 2025-XX-XX：新功能名称

   **功能概述：** 简述功能目的

   **涉及文件：**

   #### 后端/前端文件

   **文件名（修改/新增）**

   - **路径：** 完整文件路径
   - **功能摘要：** 文件主要作用
   - **核心方法/特性：** 关键实现
   ```

3. **在使用说明部分追加新小节**

   ```markdown
   ### 新功能名称

   使用方法和示例
   ```

### 状态标识说明

- ✅ 已完成并稳定运行
- ⚡ 新开发完成，待验证
- 🔄 开发中
- ⚠️ 有已知问题
- 🚫 已废弃

### 文档维护原则

- **新增优先**：新功能始终添加到最前面，无需调整已有内容
- **时间标识**：使用日期作为章节标题，便于版本追踪
- **模块化**：每个功能独立成章，互不依赖
- **状态管理**：通过状态标识快速了解功能现状

---

**文档维护：** 本文档采用时间倒序结构，支持快速迭代更新。新增功能请遵循上述更新步骤，无需调整历史内容。
