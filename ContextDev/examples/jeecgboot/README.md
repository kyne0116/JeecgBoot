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
