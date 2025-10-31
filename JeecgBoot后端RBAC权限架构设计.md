# JeecgBoot后端RBAC权限架构设计

## 一、概述

JeecgBoot采用基于角色的访问控制(RBAC - Role-Based Access Control)模型，集成Apache Shiro安全框架和JWT令牌机制，实现了企业级的细粒度权限管理系统。系统支持用户、角色、权限三层关联模型，并扩展支持部门权限、职位权限、数据权限等多维度的权限控制策略。

### 核心特性

- 基于RBAC的多租户权限体系
- 支持部门组织架构的树形权限管理
- 职位与用户关联的岗位权限控制
- 菜单、按钮、数据三级权限控制
- 动态数据权限规则引擎
- Shiro + JWT无状态认证授权
- Redis缓存加速权限查询

---

## 二、核心数据模型

### 2.1 用户模型(User)

**核心实体类**
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysUser.java`

**关键字段**
- 用户基本信息：id, username, realname, password, salt
- 组织信息：orgCode(登录选择的部门编码), loginTenantId(租户ID)
- 状态管理：status(用户状态), delFlag(删除标记)
- 扩展信息：workNo(工号), departIds(负责部门), userIdentity(用户身份)

**数据库表**：`sys_user`

### 2.2 角色模型(Role)

**核心实体类**
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysRole.java`

**关键字段**
- 角色标识：id, roleCode(角色编码), roleName(角色名称)
- 描述信息：description
- 租户隔离：tenantId

**数据库表**：`sys_role`

### 2.3 权限模型(Permission)

**核心实体类**
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysPermission.java`

**关键字段**
- 基础信息：id, name(菜单名称), parentId(父菜单ID)
- 权限标识：perms(权限编码), permsType(权限策略：显示/禁用)
- 路由信息：url(路径), component(组件), redirect(重定向)
- 菜单属性：menuType(类型：0一级菜单/1子菜单/2按钮), icon(图标), sortNo(排序)
- 显示控制：hidden(是否隐藏), leaf(是否叶子节点), route(是否路由菜单)
- 数据权限：ruleFlag(是否配置数据权限)

**数据库表**：`sys_permission`

### 2.4 用户-角色关联(UserRole)

**核心实体类**
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysUserRole.java`

**关键字段**
- userId(用户ID)
- roleId(角色ID)
- tenantId(租户ID)

**数据库表**：`sys_user_role`

### 2.5 角色-权限关联(RolePermission)

**核心实体类**
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysRolePermission.java`

**关键字段**
- roleId(角色ID)
- permissionId(权限ID)
- dataRuleIds(数据权限规则IDs)
- operateDate(操作时间)
- operateIp(操作IP)

**数据库表**：`sys_role_permission`

### 2.6 部门模型(Depart)

**核心实体类**
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysDepart.java`

**关键字段**
- 基础信息：id, departName(部门名称), parentId(父部门ID)
- 组织属性：orgCode(机构编码), orgCategory(机构类别：公司/部门/岗位)
- 树形结构：izLeaf(是否叶子节点)
- 第三方对接：qywxIdentifier(企业微信ID), dingIdentifier(钉钉ID)

**数据库表**：`sys_depart`

**关联表**：
- `sys_user_depart` - 用户部门关联
- `sys_depart_role` - 部门角色关联
- `sys_depart_permission` - 部门权限关联
- `sys_depart_role_permission` - 部门角色权限关联
- `sys_depart_role_user` - 部门角色用户关联

### 2.7 职位模型(Position)

**核心实体类**
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysPosition.java`

**关键字段**
- code(职位编码)
- name(职位名称)
- postRank(职级)
- companyId(公司ID)
- sysOrgCode(组织机构编码)

**数据库表**：`sys_position`

**关联表**：
- `sys_user_position` - 用户职位关联

### 2.8 数据权限规则(PermissionDataRule)

**核心实体类**
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysPermissionDataRule.java`

**关键字段**
- permissionId(对应的菜单权限ID)
- ruleName(规则名称)
- ruleColumn(字段)
- ruleConditions(条件：等于/不等于/大于/小于等)
- ruleValue(规则值)
- status(状态)

**数据库表**：`sys_permission_data_rule`

---

## 三、核心架构层次

### 3.1 数据访问层(Mapper)

**位置**：`jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/mapper/`

**核心Mapper接口**：
- `SysUserMapper.java` - 用户数据访问
- `SysRoleMapper.java` - 角色数据访问
- `SysPermissionMapper.java` - 权限数据访问
- `SysUserRoleMapper.java` - 用户角色关联
- `SysRolePermissionMapper.java` - 角色权限关联
- `SysDepartMapper.java` - 部门数据访问
- `SysUserDepartMapper.java` - 用户部门关联
- `SysPositionMapper.java` - 职位数据访问
- `SysUserPositionMapper.java` - 用户职位关联
- `SysPermissionDataRuleMapper.java` - 数据权限规则

采用MyBatis-Plus框架，提供基础CRUD和条件查询能力。

### 3.2 服务层(Service)

**接口位置**：`jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/`

**实现位置**：`jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/impl/`

**核心Service接口**：
- `ISysUserService.java` / `SysUserServiceImpl.java`
- `ISysRoleService.java` / `SysRoleServiceImpl.java`
- `ISysPermissionService.java` / `SysPermissionServiceImpl.java`
- `ISysUserRoleService.java` / `SysUserRoleServiceImpl.java`
- `ISysRolePermissionService.java` / `SysRolePermissionServiceImpl.java`
- `ISysDepartService.java` / `SysDepartServiceImpl.java`
- `ISysPermissionDataRuleService.java` / `SysPermissionDataRuleImpl.java`

**系统基础API**：
- 接口定义：`jeecg-module-system/jeecg-system-api/jeecg-system-local-api/src/main/java/org/jeecg/common/system/api/ISysBaseAPI.java`
- 实现类：`jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/impl/SysBaseApiImpl.java`

提供统一的用户、角色、权限查询和缓存接口，支持微服务远程调用。

### 3.3 控制层(Controller)

**位置**：`jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/`

**核心Controller**：
- `LoginController.java` - 登录认证
- `SysUserController.java` - 用户管理
- `SysRoleController.java` - 角色管理
- `SysPermissionController.java` - 权限管理
- `SysDepartController.java` - 部门管理
- `SysPositionController.java` - 职位管理
- `SysDepartRoleController.java` - 部门角色管理
- `SysDepartPermissionController.java` - 部门权限管理

提供RESTful API接口，支持权限的CRUD操作和权限分配。

---

## 四、权限认证与授权机制

### 4.1 Shiro安全框架配置

**核心配置类**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java`

**功能**：
- 配置SecurityManager
- 定义过滤器链(FilterChain)
- 配置拦截规则和匿名访问路径
- 集成Redis缓存管理器

**Realm认证授权**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java`

**核心方法**：
- `doGetAuthenticationInfo()` - 用户身份认证，验证JWT Token
- `doGetAuthorizationInfo()` - 权限授权，查询用户的角色集合和权限集合

### 4.2 JWT Token机制

**核心类**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/JwtToken.java`
- `jeecg-boot-base-core/src/main/java/org/jeecg/common/system/util/JwtUtil.java`

**工作流程**：
1. 用户登录成功后生成JWT Token
2. Token包含用户信息和过期时间
3. 客户端请求时携带Token
4. JwtFilter拦截验证Token有效性
5. Token验证通过后从Redis获取用户权限信息

### 4.3 过滤器链

**核心过滤器**：

1. **JwtFilter** - JWT令牌过滤器
   - 文件：`jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/filters/JwtFilter.java`
   - 功能：拦截请求，验证JWT Token，进行身份认证

2. **ResourceCheckFilter** - 资源检查过滤器
   - 文件：`jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/filters/ResourceCheckFilter.java`
   - 功能：检查用户是否有访问资源的权限

3. **CustomShiroFilterFactoryBean** - 自定义Shiro过滤器工厂
   - 文件：`jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/filters/CustomShiroFilterFactoryBean.java`
   - 功能：支持动态更新过滤器链

4. **ApiAuthFilter** - OpenAPI认证过滤器
   - 文件：`jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/openapi/filter/ApiAuthFilter.java`
   - 功能：处理第三方API认证

### 4.4 权限注解

**忽略认证注解**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/IgnoreAuth.java`
- 标注无需权限验证的接口

**数据权限注解**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/common/aspect/annotation/PermissionData.java`
- 标注需要数据权限控制的接口

**在线表单权限注解**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/common/aspect/annotation/OnlineAuth.java`
- 标注在线表单的权限控制

---

## 五、数据权限控制

### 5.1 数据权限切面

**核心类**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/common/aspect/PermissionDataAspect.java`

**工作原理**：
1. 拦截标注了`@PermissionData`注解的方法
2. 获取当前请求的URL和用户信息
3. 查询该用户在该URL下配置的数据权限规则
4. 将数据权限规则写入Request，供后续查询使用
5. 在SQL查询时自动添加WHERE条件限制数据范围

### 5.2 数据权限规则

**支持的规则条件**：
- 等于(=)
- 不等于(!=)
- 大于(>)
- 小于(<)
- 大于等于(>=)
- 小于等于(<=)
- 包含(LIKE)
- 左包含(LEFT LIKE)
- 右包含(RIGHT LIKE)
- 为空(IS NULL)
- 不为空(IS NOT NULL)
- 在范围内(IN)

**规则值支持变量**：
- `#{sys_user_code}` - 当前登录用户账号
- `#{sys_org_code}` - 当前登录用户部门编码
- `#{sys_user_id}` - 当前登录用户ID

### 5.3 数据权限VO模型

**核心类**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/common/system/vo/SysPermissionDataRuleModel.java`

**用户缓存信息**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/common/system/vo/SysUserCacheInfo.java`

---

## 六、权限验证流程

### 6.1 用户登录流程

1. 用户提交用户名和密码到`LoginController`
2. Controller调用`SysUserService`验证用户信息
3. 验证通过后生成JWT Token
4. Token存储到Redis，并返回给客户端
5. 加载用户的角色和权限信息到缓存

**关键文件**：
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/LoginController.java`

### 6.2 请求拦截流程

1. 客户端携带Token发送请求
2. `JwtFilter`拦截请求，解析Token
3. 从Token中获取用户名，从Redis查询用户信息
4. 将用户信息封装为`LoginUser`对象
5. 调用`ShiroRealm.doGetAuthenticationInfo()`进行身份认证
6. 认证通过后，请求到达Controller

### 6.3 权限校验流程

1. Controller方法标注Shiro权限注解(如`@RequiresPermissions`)
2. Shiro拦截器检测到权限注解
3. 调用`ShiroRealm.doGetAuthorizationInfo()`获取授权信息
4. 从`SysBaseAPI`查询用户的角色集合和权限集合
5. 比对当前请求所需权限与用户拥有的权限
6. 权限匹配则放行，否则返回403无权限错误

### 6.4 数据权限流程

1. Controller方法标注`@PermissionData`注解
2. `PermissionDataAspect`切面拦截方法
3. 获取当前请求的URL和用户信息
4. 调用`SysBaseAPI.queryPermissionDataRule()`查询数据权限规则
5. 将规则写入Request的attribute中
6. Service层查询数据时，通过工具类读取数据权限规则
7. 在SQL中添加WHERE条件，实现数据范围限制

---

## 七、多租户权限隔离

### 7.1 租户隔离设计

系统在核心表中增加`tenant_id`字段，实现多租户数据隔离：

**支持租户隔离的表**：
- `sys_user` - 用户表
- `sys_role` - 角色表
- `sys_depart` - 部门表
- `sys_position` - 职位表
- `sys_user_role` - 用户角色关联表

### 7.2 租户上下文

**核心类**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/common/config/TenantContext.java`

**功能**：
- 存储当前请求的租户ID
- 提供租户信息的获取和设置

### 7.3 租户拦截器

**核心类**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/config/mybatis/MybatisPlusSaasConfig.java`

**功能**：
- 自动在SQL中添加`tenant_id`条件
- 实现租户数据的自动隔离

### 7.4 用户租户关联

**实体类**：
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysUserTenant.java`

**Service**：
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/service/ISysUserTenantService.java`

---

## 八、OpenAPI认证机制

### 8.1 OpenAPI认证实体

**核心实体**：
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/openapi/entity/OpenApiAuth.java`

**Mapper**：
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/openapi/mapper/OpenApiAuthMapper.java`

**Service**：
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/openapi/service/OpenApiAuthService.java`
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/openapi/service/impl/OpenApiAuthServiceImpl.java`

**Controller**：
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/openapi/controller/OpenApiAuthController.java`

### 8.2 API认证过滤器

**核心过滤器**：
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/openapi/filter/ApiAuthFilter.java`
- `jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/openapi/filter/ApiFilterConfig.java`

**功能**：
- 拦截API请求
- 验证API Key和签名
- 实现第三方应用的安全接入

---

## 九、权限缓存策略

### 9.1 Redis缓存

JeecgBoot使用Redis存储用户的会话信息和权限数据：

**缓存内容**：
- JWT Token及有效期
- 用户基本信息(LoginUser)
- 用户角色集合
- 用户权限集合
- 数据权限规则

**核心工具类**：
- `jeecg-boot-base-core/src/main/java/org/jeecg/common/util/RedisUtil.java`

### 9.2 Shiro缓存管理

**配置**：
- ShiroConfig中配置RedisCacheManager
- 集成shiro-redis插件

**缓存Key规范**：
- `shiro:cache:` - Shiro缓存前缀
- `sys:cache:user:` - 用户信息缓存
- `sys:cache:role:` - 角色信息缓存
- `sys:cache:permission:` - 权限信息缓存

---

## 十、权限管理模型图

### 10.1 核心关系模型

```
用户(SysUser) ─┬─ 1:N ─> 用户角色(SysUserRole) ─── N:1 ─> 角色(SysRole)
              │
              ├─ 1:N ─> 用户部门(SysUserDepart) ─── N:1 ─> 部门(SysDepart)
              │
              └─ 1:N ─> 用户职位(SysUserPosition) ─── N:1 ─> 职位(SysPosition)

角色(SysRole) ──── 1:N ─> 角色权限(SysRolePermission) ─── N:1 ─> 权限(SysPermission)

权限(SysPermission) ──── 1:N ─> 数据权限规则(SysPermissionDataRule)

部门(SysDepart) ─┬─ 1:N ─> 部门角色(SysDepartRole)
               ├─ 1:N ─> 部门权限(SysDepartPermission)
               └─ 1:N ─> 部门角色权限(SysDepartRolePermission)
```

### 10.2 权限验证流程

```
用户请求
  → JwtFilter(Token验证)
  → ShiroRealm(身份认证)
  → ResourceCheckFilter(资源检查)
  → Shiro权限注解校验
  → ShiroRealm(授权查询)
  → 查询用户角色和权限
  → 权限匹配
  → 放行/拒绝
```

### 10.3 数据权限流程

```
标注@PermissionData的方法
  → PermissionDataAspect拦截
  → 获取URL和用户信息
  → 查询数据权限规则(SysPermissionDataRule)
  → 规则写入Request
  → Service执行查询
  → 读取数据权限规则
  → 构建SQL WHERE条件
  → 返回受限数据
```

---

## 十一、权限管理最佳实践

### 11.1 角色设计原则

1. **职能角色**：按照业务职能划分角色，如：系统管理员、业务管理员、普通用户
2. **数据角色**：按照数据范围划分角色，如：全局数据、部门数据、个人数据
3. **功能角色**：按照功能模块划分角色，如：财务角色、人事角色、销售角色

### 11.2 权限分配原则

1. **最小权限原则**：用户只分配完成工作所需的最小权限
2. **职责分离原则**：敏感操作的权限分配给不同角色
3. **权限继承原则**：子部门可继承父部门的权限配置

### 11.3 数据权限配置建议

1. **部门数据隔离**：配置`org_code`字段的数据规则
2. **个人数据隔离**：配置`create_by`字段的数据规则
3. **自定义字段规则**：根据业务需要配置特定字段的数据规则

---

## 十二、扩展性设计

### 12.1 自定义Realm

系统支持自定义Realm实现特殊的认证授权逻辑：
- 继承`ShiroRealm`类
- 重写`doGetAuthenticationInfo()`和`doGetAuthorizationInfo()`方法
- 在ShiroConfig中配置自定义Realm

### 12.2 自定义过滤器

支持添加自定义过滤器实现特殊的权限控制：
- 继承`BasicHttpAuthenticationFilter`或`AccessControlFilter`
- 实现`isAccessAllowed()`和`onAccessDenied()`方法
- 在ShiroConfig的FilterChainDefinitionMap中注册

### 12.3 动态权限

系统支持运行时动态修改权限配置：
- 权限数据存储在数据库中
- 修改权限后清除Redis缓存
- 下次请求时自动加载最新权限

### 12.4 微服务支持

系统设计支持微服务架构：
- `ISysBaseAPI`提供统一的权限查询接口
- 支持Feign远程调用（通过jeecg-system-cloud-api）
- 支持本地调用（通过jeecg-system-local-api）
- 跨服务权限验证通过网关和Feign拦截器实现

---

## 十三、数据库脚本

**主数据库脚本位置**：
- MySQL：`db/jeecgboot-mysql-5.7.sql`
- Oracle：`db/其他数据库脚本/jeecgboot-oracle11g.sql`
- PostgreSQL：`db/其他数据库脚本/jeecgboot-postgresql17.sql`
- SQL Server：`db/其他数据库脚本/jeecgboot-sqlserver2017.sql`

**Flyway增量脚本位置**：
- `jeecg-module-system/jeecg-system-start/src/main/resources/flyway/sql/mysql/`

主要包含以下权限相关表的初始化脚本：
- `sys_user` - 用户表
- `sys_role` - 角色表
- `sys_permission` - 权限菜单表
- `sys_user_role` - 用户角色关联表
- `sys_role_permission` - 角色权限关联表
- `sys_depart` - 部门表
- `sys_user_depart` - 用户部门关联表
- `sys_position` - 职位表
- `sys_user_position` - 用户职位关联表
- `sys_permission_data_rule` - 数据权限规则表
- `sys_depart_role` - 部门角色表
- `sys_depart_permission` - 部门权限表
- `sys_depart_role_permission` - 部门角色权限表
- `sys_depart_role_user` - 部门角色用户表
- `sys_user_tenant` - 用户租户关联表
- `sys_role_index` - 角色首页索引配置表

---

## 十四、总结

JeecgBoot的RBAC权限架构设计具有以下特点：

1. **完整性**：覆盖用户、角色、权限、部门、职位等多维度权限管理
2. **灵活性**：支持菜单权限、按钮权限、数据权限三级控制
3. **可扩展性**：支持自定义Realm、自定义过滤器、动态权限配置
4. **高性能**：采用Redis缓存加速权限查询，支持分布式部署
5. **安全性**：集成Shiro安全框架，采用JWT无状态认证
6. **多租户**：天然支持多租户数据隔离和权限管理
7. **企业级**：符合企业级应用的权限管理需求，支持复杂的组织架构

该架构能够满足绝大多数企业级应用的权限管理需求，并且具有良好的扩展性和可维护性。
