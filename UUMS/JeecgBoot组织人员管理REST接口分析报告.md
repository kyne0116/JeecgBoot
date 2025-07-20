# JeecgBoot组织人员管理REST接口分析报告

## 📋 项目概述

本报告详细分析了JeecgBoot框架中组织人员管理相关的REST API接口，为自动化部门创建和管理提供技术参考。

## 🏗️ 系统架构

### 技术栈
- **后端**: Spring Boot 2.7.18 + MyBatis-Plus 3.5.3.2
- **前端**: Vue 3.5.13 + TypeScript + Ant Design Vue 4.2.6
- **数据库**: MySQL 5.7+ (支持多种数据库)
- **认证**: JWT + Apache Shiro

### 核心模块
- **jeecg-module-system**: 系统管理模块
- **jeecg-system-biz**: 业务逻辑实现
- **jeecg-system-api**: API接口定义

## 🔌 REST API接口详细分析

### 1. 部门管理API (SysDepartController)

#### 基础信息
- **控制器**: `org.jeecg.modules.system.controller.SysDepartController`
- **请求前缀**: `/sys/sysDepart`
- **认证方式**: JWT Token (X-Access-Token)

#### 1.1 查询接口

##### 获取部门树结构
```http
GET /sys/sysDepart/queryTreeList
Authorization: X-Access-Token: {token}
```

**响应格式**:
```json
{
  "success": true,
  "message": "",
  "code": 0,
  "result": [
    {
      "key": "部门ID",
      "value": "部门ID", 
      "title": "部门名称",
      "isLeaf": false,
      "id": "部门ID",
      "parentId": "父部门ID",
      "departName": "部门名称",
      "departNameEn": "英文名称",
      "orgCategory": "1",
      "orgCode": "机构编码",
      "uumsOrgCode": "UUMS机构编码",
      "uumsParentOrgCode": "UUMS父机构编码",
      "description": "部门描述",
      "createTime": "2025-07-20 23:10:04",
      "children": []
    }
  ]
}
```

##### 其他查询接口
- `GET /sys/sysDepart/queryMyDeptTreeList` - 查询当前用户部门树
- `GET /sys/sysDepart/searchBy?keyWord=keyword` - 关键词搜索部门
- `GET /sys/sysDepart/listAll` - 查询所有部门列表
- `GET /sys/sysDepart/getDepartName?orgCode=A01` - 根据机构编码获取部门名称

#### 1.2 创建接口

##### 新增部门
```http
POST /sys/sysDepart/add
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

**请求体**:
```json
{
  "departName": "部门名称",
  "description": "部门描述", 
  "uumsOrgCode": "UUMS机构编码",
  "orgCategory": "1",
  "uumsParentOrgCode": "父机构编码",
  "parentId": "父部门ID"
}
```

**字段说明**:
- `departName`: 部门名称 ⭐**必填** (String, 机构/部门名称)
- `orgCategory`: 机构类别 ⭐**必填** (String, 1=公司，2=组织机构，3=岗位)
- `uumsOrgCode`: UUMS机构编码 ⭐**必填，唯一** (String, 用于UUMS系统集成)
- `description`: 部门描述 (可选, String, 部门详细描述)
- `uumsParentOrgCode`: 父机构编码 (可选, String, 建立层级关系用)
- `parentId`: 父部门ID (可选, String, 系统内部层级关系)
- `departOrder`: 排序 (可选, Integer, 显示顺序)
- `mobile`: 手机号 (可选, String, 部门联系电话)
- `address`: 地址 (可选, String, 部门地址)
- `memo`: 备注 (可选, String, 其他备注信息)

**响应格式**:
```json
{
  "success": true,
  "message": "添加成功！",
  "code": 200,
  "result": null,
  "timestamp": 1753024203520
}
```

#### 1.3 更新接口

##### 编辑部门
```http
PUT /sys/sysDepart/edit
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

#### 1.4 删除接口

##### 删除单个部门
```http
DELETE /sys/sysDepart/delete?id={departmentId}
Authorization: X-Access-Token: {token}
```

##### 批量删除部门
```http
DELETE /sys/sysDepart/deleteBatch?ids=ID1,ID2,ID3
Authorization: X-Access-Token: {token}
```

### 2. 人员信息管理API (SysUserController)

#### 基础信息
- **控制器**: `org.jeecg.modules.system.controller.SysUserController`
- **请求前缀**: `/sys/user`
- **认证方式**: JWT Token (X-Access-Token)

#### 2.1 用户查询接口

##### 用户列表查询 (分页)
```http
GET /sys/user/list?pageNo=1&pageSize=10&username=&realname=
Authorization: X-Access-Token: {token}
```

**查询参数**:
- `pageNo`: 页码 (默认1)
- `pageSize`: 每页数量 (默认10)
- `username`: 用户名筛选 (可选)
- `realname`: 真实姓名筛选 (可选)
- `orgCode`: 组织机构编码筛选 (可选)

**响应格式**:
```json
{
  "success": true,
  "result": {
    "records": [
      {
        "id": "用户ID",
        "username": "用户名",
        "realname": "真实姓名",
        "workNo": "工号",
        "phone": "手机号",
        "email": "邮箱",
        "sex": "1",
        "status": "1",
        "orgCode": "机构编码",
        "orgCodeTxt": "机构名称",
        "post": "职位",
        "telephone": "座机",
        "createTime": "2025-07-20 23:10:04"
      }
    ],
    "total": 100,
    "pages": 10,
    "current": 1,
    "size": 10
  }
}
```

##### 根据组织编码查询用户
```http
GET /sys/user/queryByOrgCode?orgCode={orgCode}
Authorization: X-Access-Token: {token}
```

##### 根据部门ID查询用户
```http
GET /sys/user/appQueryByDepartId?departId={departId}
Authorization: X-Access-Token: {token}
```

##### 关键词搜索用户
```http
GET /sys/user/searchByKeyword?keyword={keyword}&pageSize=10
Authorization: X-Access-Token: {token}
```

#### 2.2 用户创建接口

##### 新增用户
```http
POST /sys/user/add
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

**请求体**:
```json
{
  "username": "用户名",
  "realname": "真实姓名", 
  "password": "密码",
  "phone": "手机号",
  "email": "邮箱",
  "sex": "1",
  "workNo": "工号",
  "post": "职位",
  "orgCode": "机构编码",
  "status": "1",
  "telephone": "座机号",
  "birthday": "1990-01-01",
  "userIdentity": "1"
}
```

**字段说明**:
- `username`: 用户名 ⭐**必填，唯一** (String, 登录账号，系统唯一标识)
- `realname`: 真实姓名 ⭐**必填** (String, 用户真实姓名)
- `password`: 密码 ⭐**必填** (String, 登录密码，系统会自动加密)
- `phone`: 手机号 ⭐**强烈建议必填，唯一** (String, 联系电话，用于找回密码等)
- `email`: 邮箱 (可选, String, 电子邮件地址)
- `sex`: 性别 (可选, Integer, 1=男，2=女)
- `workNo`: 工号 (可选，唯一, String, 员工工号)
- `post`: 职位 (可选, String, 职务名称或ID)
- `orgCode`: 机构编码 (可选, String, 关联部门编码)
- `status`: 状态 (可选, Integer, 1=正常，2=冻结，默认1)
- `userIdentity`: 身份 (可选, Integer, 1=普通成员，2=上级，默认1)
- `birthday`: 生日 (可选, Date, 格式: yyyy-MM-dd)
- `telephone`: 座机号 (可选, String, 办公电话)
- `avatar`: 头像 (可选, String, 头像图片路径)

**响应格式**:
```json
{
  "success": true,
  "message": "添加成功！",
  "code": 200,
  "result": null,
  "timestamp": 1753024203520
}
```

#### 2.3 用户更新接口

##### 编辑用户信息
```http
PUT /sys/user/edit
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

**请求体**: (与创建接口类似，需包含用户ID)

##### 批量编辑用户
```http
PUT /sys/user/batchEditUsers
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

##### 更换手机号
```http
PUT /sys/user/changePhone
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

#### 2.4 用户删除接口

##### 删除单个用户
```http
DELETE /sys/user/delete?id={userId}
Authorization: X-Access-Token: {token}
```

##### 批量删除用户
```http
DELETE /sys/user/deleteBatch?ids=ID1,ID2,ID3
Authorization: X-Access-Token: {token}
```

#### 2.5 用户角色管理接口

##### 为用户分配角色
```http
POST /sys/user/addSysUserRole
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

**请求体**:
```json
{
  "userId": "用户ID",
  "roleIds": "角色ID1,角色ID2"
}
```

**字段说明**:
- `userId`: 用户ID ⭐**必填** (String, 目标用户的系统ID)
- `roleIds`: 角色ID列表 ⭐**必填** (String, 逗号分隔的角色ID列表)

##### 移除用户角色
```http
DELETE /sys/user/deleteUserRole?roleId={roleId}&userId={userId}
Authorization: X-Access-Token: {token}
```

#### 2.6 用户部门关联接口

##### 编辑部门用户关系
```http
POST /sys/user/editSysDepartWithUser
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

##### 从部门移除用户
```http
DELETE /sys/user/deleteUserInDepart?userId={userId}&departId={departId}
Authorization: X-Access-Token: {token}
```

### 3. 职位管理API (SysPositionController)

#### 基础信息
- **控制器**: `org.jeecg.modules.system.controller.SysPositionController`
- **请求前缀**: `/sys/position`
- **认证方式**: JWT Token (X-Access-Token)

#### 3.1 职位查询接口

##### 职位列表查询
```http
GET /sys/position/list?pageNo=1&pageSize=10&name=&code=
Authorization: X-Access-Token: {token}
```

##### 根据编码查询职位
```http
GET /sys/position/queryByCode?code={positionCode}
Authorization: X-Access-Token: {token}
```

#### 3.2 职位创建接口

##### 新增职位
```http
POST /sys/position/add
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

**请求体**:
```json
{
  "name": "职位名称",
  "code": "职位编码",
  "postRank": "职级",
  "companyId": "公司ID",
  "sysOrgCode": "组织机构编码"
}
```

**字段说明**:
- `name`: 职位名称 ⭐**必填** (String, 职务名称)
- `code`: 职位编码 ⭐**必填，唯一** (String, 职务编码，系统唯一标识)
- `postRank`: 职级 (可选, String, 职位等级)
- `companyId`: 公司ID (可选, String, 所属公司)
- `sysOrgCode`: 组织机构编码 (可选, String, 关联部门编码)

#### 3.3 职位用户关联接口

##### 获取职位下的用户
```http
GET /sys/position/getPositionUserList?positionId={positionId}
Authorization: X-Access-Token: {token}
```

##### 为职位分配用户
```http
POST /sys/position/savePositionUser
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

**请求体**:
```json
{
  "positionId": "职位ID",
  "userIds": "用户ID1,用户ID2"
}
```

**字段说明**:
- `positionId`: 职位ID ⭐**必填** (String, 目标职位的系统ID)
- `userIds`: 用户ID列表 ⭐**必填** (String, 逗号分隔的用户ID列表)

### 4. 角色管理API (SysRoleController)

#### 基础信息
- **控制器**: `org.jeecg.modules.system.controller.SysRoleController`
- **请求前缀**: `/sys/role`
- **认证方式**: JWT Token (X-Access-Token)

#### 4.1 角色查询接口

##### 角色列表查询
```http
GET /sys/role/list?pageNo=1&pageSize=10&roleName=
Authorization: X-Access-Token: {token}
```

##### 获取所有角色
```http
GET /sys/role/queryall
Authorization: X-Access-Token: {token}
```

##### 角色树结构
```http
GET /sys/role/queryTreeList
Authorization: X-Access-Token: {token}
```

#### 4.2 角色创建接口

##### 新增角色
```http
POST /sys/role/add
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

**请求体**:
```json
{
  "roleName": "角色名称",
  "roleCode": "角色编码",
  "description": "角色描述"
}
```

**字段说明**:
- `roleName`: 角色名称 ⭐**必填** (String, 角色显示名称)
- `roleCode`: 角色编码 ⭐**必填，唯一** (String, 角色代码，系统唯一标识)
- `description`: 角色描述 (可选, String, 角色功能说明)

#### 4.3 数据权限管理

##### 加载角色数据规则
```http
GET /sys/role/datarule/{permissionId}/{roleId}
Authorization: X-Access-Token: {token}
```

##### 保存数据规则
```http
POST /sys/role/datarule
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

### 5. 在线用户管理API (SysUserOnlineController)

#### 基础信息
- **控制器**: `org.jeecg.modules.system.controller.SysUserOnlineController`
- **请求前缀**: `/sys/user/online`

#### 5.1 在线用户查询

##### 在线用户列表
```http
GET /sys/user/online/list?pageNo=1&pageSize=10
Authorization: X-Access-Token: {token}
```

#### 5.2 强制下线

##### 强制用户下线
```http
POST /sys/user/online/forceLogout
Content-Type: application/json
Authorization: X-Access-Token: {token}
```

**请求体**:
```json
{
  "id": "会话ID",
  "kickOutReason": "下线原因"
}
```

### 6. 用户认证API (LoginController)

#### 基础信息
- **控制器**: `org.jeecg.modules.system.controller.LoginController`
- **请求前缀**: `/sys`

#### 6.1 登录获取Token
```http
POST /sys/mLogin
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "admin",
  "password": "123456"
}
```

**响应格式**:
```json
{
  "success": true,
  "result": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userInfo": {
      "id": "用户ID",
      "username": "用户名",
      "realname": "真实姓名",
      "orgCode": "机构编码"
    }
  }
}
```

#### 6.2 获取当前用户信息
```http
GET /sys/user/getUserInfo
Authorization: X-Access-Token: {token}
```

#### 6.3 手机号登录
```http
POST /sys/phoneLogin
Content-Type: application/json
```

**请求体**:
```json
{
  "phone": "手机号",
  "captcha": "验证码"
}
```

## 🗄️ 数据库结构分析

### Java实体类结构

#### 1. SysDepart 实体类 (部门管理)
**文件位置**: `org.jeecg.modules.system.entity.SysDepart`
**数据表**: `sys_depart`

```java
@Data
@TableName("sys_depart")
public class SysDepart implements Serializable {
    @TableId(type = IdType.ASSIGN_ID)
    private String id;                         // 主键ID (自动生成)
    
    // 核心部门字段
    private String parentId;                   // 父机构ID (可选)
    @Excel(name="机构/部门名称",width=15)
    private String departName;                 // 机构/部门名称 ⭐必填
    @Excel(name="英文名",width=15)
    private String departNameEn;              // 英文名 (可选)
    private String departNameAbbr;            // 缩写 (可选)
    @Excel(name="排序",width=15)
    private Integer departOrder;              // 排序 (可选)
    @Excel(name="描述",width=15)
    private String description;               // 描述 (可选)
    
    // 组织分类
    @Excel(name="机构类别",width=15,dicCode="org_category")
    private String orgCategory;               // 机构类别 ⭐必填 (1=公司，2=组织机构，3=岗位)
    private String orgType;                   // 机构类型 (可选)
    @Excel(name="机构编码",width=15)
    private String orgCode;                   // 机构编码 (自动生成)
    
    // UUMS集成字段
    @Excel(name="UUMS机构编码",width=15)
    private String uumsOrgCode;              // UUMS机构编码 ⭐必填，唯一
    @Excel(name="UUMS父机构编码",width=15)
    private String uumsParentOrgCode;        // UUMS父机构编码 (可选)
    
    // 联系信息
    @Excel(name="手机号",width=15)
    private String mobile;                    // 手机号 (可选)
    @Excel(name="传真",width=15)
    private String fax;                       // 传真 (可选)
    @Excel(name="地址",width=15)
    private String address;                   // 地址 (可选)
    @Excel(name="备注",width=15)
    private String memo;                      // 备注 (可选)
    
    // 状态字段
    @Dict(dicCode = "depart_status")
    private String status;                    // 状态 (1启用，0不启用)
    @Dict(dicCode = "del_flag")
    private String delFlag;                   // 删除状态 (0正常，1已删除)
    
    // 审计字段
    private String createBy;                  // 创建人
    @JsonFormat(timezone = "GMT+8",pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createTime;                  // 创建时间
    private String updateBy;                  // 更新人
    @JsonFormat(timezone = "GMT+8",pattern = "yyyy-MM-dd HH:mm:ss")
    private Date updateTime;                  // 更新时间
    
    // 多租户支持
    private Integer tenantId;                 // 租户ID
}
```

#### 2. SysUser 实体类 (用户管理)
**文件位置**: `org.jeecg.modules.system.entity.SysUser`
**数据表**: `sys_user`

```java
@Data
@EqualsAndHashCode(callSuper = false)
@Accessors(chain = true)
public class SysUser implements Serializable {
    @TableId(type = IdType.ASSIGN_ID)
    private String id;                        // 主键ID (自动生成)
    
    // 认证字段
    @Excel(name = "登录账号", width = 15)
    private String username;                  // 登录账号 ⭐必填，唯一
    @Excel(name = "真实姓名", width = 15)
    private String realname;                  // 真实姓名 ⭐必填
    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
    private String password;                  // 密码 ⭐必填
    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
    private String salt;                      // md5密码盐 (系统生成)
    
    // 个人信息
    @Excel(name = "头像", width = 15,type = 2)
    private String avatar;                    // 头像 (可选)
    @Excel(name = "生日", width = 15, format = "yyyy-MM-dd")
    @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd")
    private Date birthday;                    // 生日 (可选)
    @Excel(name = "性别", width = 15,dicCode="sex")
    @Dict(dicCode = "sex")
    private Integer sex;                      // 性别 (1=男，2=女，可选)
    
    // 联系信息
    @Excel(name = "电子邮件", width = 15)
    private String email;                     // 电子邮件 (可选)
    @Excel(name = "电话", width = 15)
    private String phone;                     // 电话 ⭐建议必填，唯一
    @Excel(name = "座机号", width = 15)
    private String telephone;                 // 座机号 (可选)
    
    // 组织职位
    private String orgCode;                   // 登录选择部门编码 (可选)
    private transient String orgCodeTxt;      // 部门名称 (非持久化)
    @Excel(name = "工号", width = 15)
    private String workNo;                    // 工号，唯一键 (可选)
    @Excel(name = "职务", width = 15)
    @Dict(dictTable ="sys_position",dicText = "name",dicCode = "id")
    @TableField(exist = false)
    private String post;                      // 职务 (可选)
    
    // 状态标识
    @Excel(name = "状态", width = 15,dicCode="user_status")
    @Dict(dicCode = "user_status")
    private Integer status;                   // 状态 (1=正常，2=冻结)
    @Excel(name="（1普通成员 2上级）",width = 15)
    private Integer userIdentity;             // 身份 (1=普通成员，2=上级)
    
    // 部门管理
    @Excel(name="负责部门",width = 15)
    @Dict(dictTable ="sys_depart",dicText = "depart_name",dicCode = "id")
    private String departIds;                 // 负责部门 (可选)
    
    // 审计字段
    private String createBy;                  // 创建人
    private Date createTime;                  // 创建时间
    private String updateBy;                  // 更新人
    private Date updateTime;                  // 更新时间
}
```

#### 3. SysRole 实体类 (角色管理)
**文件位置**: `org.jeecg.modules.system.entity.SysRole`
**数据表**: `sys_role`

```java
@Data
@EqualsAndHashCode(callSuper = false)
@Accessors(chain = true)
public class SysRole implements Serializable {
    @TableId(type = IdType.ASSIGN_ID)
    private String id;                        // 主键ID (自动生成)
    
    // 角色定义
    @Excel(name="角色名",width=15)
    private String roleName;                  // 角色名称 ⭐必填
    @Excel(name="角色编码",width=15)
    private String roleCode;                  // 角色编码 ⭐必填，唯一
    @Excel(name="描述",width=60)
    private String description;               // 描述 (可选)
    
    // 审计字段
    private String createBy;                  // 创建人
    @JsonFormat(timezone = "GMT+8",pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createTime;                  // 创建时间
    private String updateBy;                  // 更新人
    @JsonFormat(timezone = "GMT+8",pattern = "yyyy-MM-dd HH:mm:ss")
    private Date updateTime;                  // 更新时间
    
    // 多租户支持
    private Integer tenantId;                 // 租户ID
}
```

#### 4. SysPosition 实体类 (职位管理)
**文件位置**: `org.jeecg.modules.system.entity.SysPosition`
**数据表**: `sys_position`

```java
@Data
@TableName("sys_position")
@EqualsAndHashCode(callSuper = false)
@Accessors(chain = true)
public class SysPosition {
    @TableId(type = IdType.ASSIGN_ID)
    private String id;                        // 主键ID (自动生成)
    
    // 职位定义
    @Excel(name = "职务编码", width = 15)
    private String code;                      // 职务编码 ⭐必填，唯一
    @Excel(name = "职务名称", width = 15)
    private String name;                      // 职务名称 ⭐必填
    @Dict(dicCode = "position_rank")
    private String postRank;                  // 职级 (可选)
    
    // 组织关系
    private String companyId;                 // 公司id (可选)
    private String sysOrgCode;               // 组织机构编码 (可选)
    
    // 审计字段
    private String createBy;                  // 创建人
    @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createTime;                  // 创建时间
    private String updateBy;                  // 修改人
    @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private Date updateTime;                  // 修改时间
    
    // 多租户支持
    private Integer tenantId;                 // 租户ID
}
```

#### 5. 关联实体类

##### SysUserRole (用户角色关联)
```java
@Data
public class SysUserRole implements Serializable {
    @TableId(type = IdType.ASSIGN_ID)
    private String id;                        // 主键ID
    private String userId;                    // 用户ID ⭐必填
    private String roleId;                    // 角色ID ⭐必填
    private Integer tenantId;                 // 租户ID
}
```

##### SysUserDepart (用户部门关联)
```java
@Data
@TableName("sys_user_depart")
public class SysUserDepart implements Serializable {
    @TableId(type = IdType.ASSIGN_ID)
    private String id;                        // 主键ID
    private String userId;                    // 用户ID ⭐必填
    private String depId;                     // 部门ID ⭐必填
}
```

### 数据库表结构

### sys_user表结构
```sql
CREATE TABLE `sys_user` (
  `id` varchar(32) NOT NULL COMMENT '主键ID',
  `username` varchar(100) DEFAULT NULL COMMENT '登录账号',
  `realname` varchar(100) DEFAULT NULL COMMENT '真实姓名',
  `password` varchar(255) DEFAULT NULL COMMENT '密码',
  `salt` varchar(45) DEFAULT NULL COMMENT 'md5密码盐',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像',
  `birthday` datetime DEFAULT NULL COMMENT '生日',
  `sex` tinyint(1) DEFAULT NULL COMMENT '性别(0-默认未知,1-男,2-女)',
  `email` varchar(45) DEFAULT NULL COMMENT '电子邮件',
  `phone` varchar(45) DEFAULT NULL COMMENT '电话',
  `org_code` varchar(64) DEFAULT NULL COMMENT '机构编码',
  `status` tinyint(1) DEFAULT NULL COMMENT '性别(1-正常,2-冻结)',
  `del_flag` tinyint(1) DEFAULT NULL COMMENT '删除状态(0-正常,1-已删除)',
  `third_id` varchar(100) DEFAULT NULL COMMENT '第三方登录的唯一标识',
  `third_type` varchar(100) DEFAULT NULL COMMENT '第三方类型',
  `activiti_sync` tinyint(1) DEFAULT NULL COMMENT '同步工作流引擎(1-同步,0-不同步)',
  `work_no` varchar(100) DEFAULT NULL COMMENT '工号，唯一键',
  `post` varchar(100) DEFAULT NULL COMMENT '职务，关联职务表',
  `telephone` varchar(45) DEFAULT NULL COMMENT '座机号',
  `create_by` varchar(32) DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(32) DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `user_identity` tinyint(1) DEFAULT NULL COMMENT '身份（1普通成员 2上级）',
  `depart_ids` longtext COMMENT '负责部门',
  `rel_tenant_ids` varchar(100) DEFAULT NULL COMMENT '多租户标识',
  `client_id` varchar(64) DEFAULT NULL COMMENT '设备ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_user_name` (`username`) USING BTREE,
  UNIQUE KEY `uniq_sys_user_work_no` (`work_no`) USING BTREE,
  UNIQUE KEY `uniq_sys_user_username` (`username`) USING BTREE,
  UNIQUE KEY `uniq_sys_user_phone` (`phone`) USING BTREE,
  KEY `index_user_status` (`status`) USING BTREE,
  KEY `index_user_del_flag` (`del_flag`) USING BTREE
);
```

### sys_user_role表结构 (用户角色关联表)
```sql
CREATE TABLE `sys_user_role` (
  `id` varchar(32) NOT NULL COMMENT '主键id',
  `user_id` varchar(32) DEFAULT NULL COMMENT '用户id',
  `role_id` varchar(32) DEFAULT NULL COMMENT '角色id',
  PRIMARY KEY (`id`),
  KEY `index_user_role_user_id` (`user_id`) USING BTREE,
  KEY `index_user_role_role_id` (`role_id`) USING BTREE
);
```

### sys_user_depart表结构 (用户部门关联表)
```sql
CREATE TABLE `sys_user_depart` (
  `id` varchar(32) NOT NULL COMMENT 'id',
  `user_id` varchar(32) DEFAULT NULL COMMENT '用户id',
  `dep_id` varchar(32) DEFAULT NULL COMMENT '部门id',
  PRIMARY KEY (`id`),
  KEY `index_user_depart_user_id` (`user_id`) USING BTREE,
  KEY `index_user_depart_dep_id` (`dep_id`) USING BTREE
);
```

### sys_position表结构 (职位表)
```sql
CREATE TABLE `sys_position` (
  `id` varchar(32) NOT NULL COMMENT '主键ID',
  `code` varchar(100) DEFAULT NULL COMMENT '职务编码',
  `name` varchar(100) DEFAULT NULL COMMENT '职务名称',
  `post_rank` varchar(2) DEFAULT NULL COMMENT '职级',
  `company_id` varchar(255) DEFAULT NULL COMMENT '公司id',
  `create_by` varchar(50) DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(50) DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `sys_org_code` varchar(64) DEFAULT NULL COMMENT '所属部门',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_code` (`code`) USING BTREE
);
```

### sys_role表结构 (角色表)
```sql
CREATE TABLE `sys_role` (
  `id` varchar(32) NOT NULL COMMENT '主键id',
  `role_name` varchar(200) DEFAULT NULL COMMENT '角色名称',
  `role_code` varchar(100) DEFAULT NULL COMMENT '角色编码',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `create_by` varchar(32) DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(32) DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_sys_role_role_code` (`role_code`) USING BTREE,
  KEY `index_role_name` (`role_name`) USING BTREE
);
```

### sys_depart表结构
```sql
CREATE TABLE `sys_depart` (
  `id` varchar(32) NOT NULL COMMENT '主键ID',
  `parent_id` varchar(32) DEFAULT NULL COMMENT '父机构ID',
  `depart_name` varchar(100) NOT NULL COMMENT '机构/部门名称',
  `depart_name_en` varchar(500) DEFAULT NULL COMMENT '英文名',
  `depart_order` int(11) DEFAULT '0' COMMENT '排序',
  `org_category` varchar(10) NOT NULL DEFAULT '1' COMMENT '机构类别 1组织机构 2岗位',
  `org_type` varchar(10) DEFAULT NULL COMMENT '机构类型',
  `org_code` varchar(64) NOT NULL COMMENT '机构编码',
  `mobile` varchar(32) DEFAULT NULL COMMENT '手机号',
  `fax` varchar(32) DEFAULT NULL COMMENT '传真',
  `address` varchar(100) DEFAULT NULL COMMENT '地址',
  `memo` varchar(500) DEFAULT NULL COMMENT '备注',
  `status` varchar(1) DEFAULT NULL COMMENT '状态（1启用，0不启用）',
  `del_flag` varchar(1) DEFAULT NULL COMMENT '删除状态（0，正常，1已删除）',
  `qywx_identifier` varchar(100) DEFAULT NULL COMMENT '对接企业微信的ID',
  `create_by` varchar(32) DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `update_by` varchar(32) DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `uums_org_code` varchar(64) DEFAULT NULL COMMENT 'UUMS机构编码',
  `uums_parent_org_code` varchar(64) DEFAULT NULL COMMENT 'UUMS父机构编码',
  `description` varchar(500) DEFAULT NULL COMMENT '部门描述',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_depart_org_code` (`org_code`) USING BTREE,
  UNIQUE KEY `uniq_sd_uums_org_code` (`uums_org_code`) USING BTREE,
  KEY `index_depart_parent_id` (`parent_id`) USING BTREE,
  KEY `index_depart_depart_order` (`depart_order`) USING BTREE,
  KEY `index_depart_org_code` (`org_code`) USING BTREE
);
```

### 关键字段说明

#### 部门表 (sys_depart)
- `uums_org_code`: UUMS机构编码 (已设置唯一索引)
- `parent_id`: 父部门ID (用于建立层级关系)
- `org_category`: 机构类别 (1=公司，2=组织机构，3=岗位)

#### 用户表 (sys_user)
- `username`: 登录账号 (唯一索引)
- `phone`: 手机号 (唯一索引)
- `work_no`: 工号 (唯一索引)
- `org_code`: 机构编码 (关联部门)
- `status`: 用户状态 (1=正常，2=冻结)
- `user_identity`: 身份 (1=普通成员，2=上级)
- `depart_ids`: 负责部门 (可管理多个部门)

#### 关联表
- `sys_user_role`: 用户角色多对多关联
- `sys_user_depart`: 用户部门多对多关联
- `sys_position`: 职位管理，通过post字段关联用户

### 🔍 Java实体类特性总结

#### 注解特性
- **@TableId(type = IdType.ASSIGN_ID)**: 所有主键使用雪花算法自动生成
- **@Excel**: 支持Excel导入导出功能
- **@Dict**: 数据字典映射，用于下拉选择和显示转换
- **@JsonFormat**: 日期时间格式化（GMT+8时区）
- **@TableField(exist = false)**: 非数据库字段，用于业务逻辑
- **@JsonProperty(access = WRITE_ONLY)**: 密码字段只写不读，保证安全

#### 必填字段总结

##### 部门创建 (SysDepart)
- ⭐ `departName`: 部门名称 (String)
- ⭐ `orgCategory`: 机构类别 (String, 1/2/3)
- ⭐ `uumsOrgCode`: UUMS机构编码 (String, 唯一)

##### 用户创建 (SysUser)
- ⭐ `username`: 登录账号 (String, 唯一)
- ⭐ `realname`: 真实姓名 (String)
- ⭐ `password`: 登录密码 (String)
- 🔶 `phone`: 手机号 (String, 强烈建议，唯一)

##### 角色创建 (SysRole)
- ⭐ `roleName`: 角色名称 (String)
- ⭐ `roleCode`: 角色编码 (String, 唯一)

##### 职位创建 (SysPosition)
- ⭐ `name`: 职位名称 (String)
- ⭐ `code`: 职位编码 (String, 唯一)

#### 系统自动处理字段
- **id**: 主键ID (雪花算法自动生成)
- **createBy/updateBy**: 审计字段 (登录用户自动填充)
- **createTime/updateTime**: 时间戳 (系统自动生成)
- **orgCode**: 机构编码 (部门创建时系统自动生成)
- **salt**: 密码盐值 (用户创建时系统自动生成)

#### 唯一性约束
- **SysDepart**: `uumsOrgCode`, `orgCode`
- **SysUser**: `username`, `phone`, `workNo`
- **SysRole**: `roleCode`
- **SysPosition**: `code`

#### 多租户支持
所有实体类都支持 `tenantId` 字段，实现多租户数据隔离。

## 🔧 自动化工具实现

### 1. create_department.py 核心功能 (部门管理)

#### 1. Excel数据读取
- 支持.xlsx/.xls格式
- A列：组织名称 (departName)
- B列：组织全称 (description) 
- C列：组织编码 (uumsOrgCode)
- D列：组织父编码 (uumsParentOrgCode)
- E列：机构类别 (orgCategory)

#### 2. 智能父部门关联
```python
def create_departments_via_api_with_hierarchy(file_path):
    """智能创建部门：支持父子层级关系的正确建立"""
    # 1. 逐个创建部门
    # 2. 创建后立即记录部门信息
    # 3. 后续部门优先从已创建列表查找父部门
    # 4. 自动添加parentId建立层级关系
```

#### 3. 完整工作流程
1. **Excel数据展示**: 显示A-E列原始数据
2. **JSON报文组装**: 转换为API所需的JSON格式
3. **智能部门创建**: 自动处理父子关系，逐个创建部门

#### 4. 关键特性
- ✅ 支持部门层级关系自动建立
- ✅ 实时父部门查询和关联
- ✅ 100%成功率的创建流程
- ✅ 详细的执行日志和错误处理
- ✅ 数据验证和完整性检查

### 2. 人员管理自动化功能 (建议扩展)

#### 2.1 用户批量创建工具
基于人员信息API，可开发用户批量创建功能：

##### Excel数据格式 (用户信息)
- A列：用户名 (username)
- B列：真实姓名 (realname)
- C列：手机号 (phone)
- D列：邮箱 (email)
- E列：工号 (workNo)
- F列：机构编码 (orgCode)
- G列：职位 (post)
- H列：性别 (sex)

##### 核心功能设计
```python
def create_users_via_api(file_path):
    """批量创建用户，支持部门自动关联"""
    # 1. 读取Excel用户数据
    # 2. 验证必填字段 (username, realname, phone)
    # 3. 检查唯一性约束 (username, phone, workNo)
    # 4. 通过orgCode关联部门
    # 5. 逐个创建用户账号
    # 6. 批量分配默认角色
```

#### 2.2 用户角色批量分配
```python
def assign_roles_to_users(user_role_mapping):
    """批量为用户分配角色"""
    # 1. 验证用户ID和角色ID的有效性
    # 2. 调用 /sys/user/addSysUserRole API
    # 3. 支持一个用户分配多个角色
    # 4. 错误处理和重试机制
```

#### 2.3 用户部门关联管理
```python
def manage_user_department_relations():
    """用户部门关系批量管理"""
    # 1. 支持用户在多个部门
    # 2. 调用 /sys/user/editSysDepartWithUser API
    # 3. 智能处理部门变更
    # 4. 保持数据一致性
```

#### 2.4 组织架构完整导入
```python
def import_complete_organization():
    """完整组织架构导入 (部门+人员)"""
    # 1. 第一阶段：创建部门层级结构
    # 2. 第二阶段：创建用户账号
    # 3. 第三阶段：建立用户部门关联
    # 4. 第四阶段：分配角色权限
    # 5. 数据完整性验证
```

## 📊 测试结果

### 成功案例
```
📊 API调用结果统计:
   总计创建: 3 个部门
   成功创建: 3 个部门  
   创建失败: 0 个部门
   成功率: 100.0%

📋 本次创建的部门记录:
   省公司 (ID: 1946950739385008130, 编码: 4772338661636601428)
   信息技术管理部 (ID: 1946950761245720578, 编码: 2700526267653981965)
   管理信息系统室 (ID: 1946950783156764673, 编码: 1163561336007675904)
```

### 层级关系验证
- 省公司 → 顶级部门
- 信息技术管理部 → 省公司的子部门 (parentId: 1946950739385008130)
- 管理信息系统室 → 信息技术管理部的子部门 (parentId: 1946950761245720578)

## 🎯 核心技术突破

### 1. 创建顺序问题解决
**问题**: Excel数据有层级关系，但创建时父部门尚未存在
**解决**: 采用逐个创建+实时记录的智能流程

### 2. 父部门查询优化
**策略**: 
1. 优先从本次创建的部门列表查找
2. 其次从数据库查询现有部门
3. 确保parentId正确关联

### 3. API兼容性处理
**发现**: JeecgBoot使用树形结构返回部门数据
**适配**: 实现递归搜索算法匹配uumsOrgCode

## 🚀 使用指南

### 部门管理命令
```bash
# 标准创建流程
python3 create_department.py --file 组织信息导入.xlsx

# 测试查询功能  
python3 create_department.py --test-query

# 清理测试数据
python3 create_department.py --clean-test-data
```

### 人员管理命令 (建议开发)
```bash
# 用户批量创建
python3 create_users.py --file 用户信息导入.xlsx

# 用户角色批量分配
python3 assign_user_roles.py --file 用户角色映射.xlsx

# 组织架构完整导入
python3 import_organization.py --dept-file 部门.xlsx --user-file 用户.xlsx

# 用户部门关系管理
python3 manage_user_dept.py --action assign --file 用户部门关系.xlsx
```

### 数据准备格式

#### 部门数据 (Excel格式)
- 第1行：表头 (组织名称, 组织全称, 组织编码, 组织父编码, 机构类别)
- 第2行开始：实际数据
- 必填列：A, B, C, E
- 可选列：D (用于建立父子关系)

#### 用户数据 (Excel格式)
- 第1行：表头 (用户名, 真实姓名, 手机号, 邮箱, 工号, 机构编码, 职位, 性别)
- 第2行开始：用户数据
- 必填列：A, B, C (用户名, 真实姓名, 手机号)
- 可选列：D-H (邮箱, 工号, 机构编码, 职位, 性别)

#### 角色分配数据 (Excel格式)
- A列：用户名或用户ID
- B列：角色编码 (多个角色用逗号分隔)
- C列：分配原因 (可选)

## ⚠️ 注意事项

### 安全要求
- 使用HTTPS连接生产环境
- 定期更换JWT Token
- 限制API访问权限

### 数据完整性
- uumsOrgCode必须唯一
- 父部门必须先于子部门创建
- 机构类别必须符合规范 (1/2/3)

### 性能考虑
- 大批量创建时适当增加等待间隔
- 监控数据库连接池状态
- 定期清理测试数据

## 📈 扩展功能

### 计划中的改进

#### 部门管理增强
1. 支持Excel模板验证
2. 增加批量更新功能
3. 支持部门权限自动分配
4. 集成企业微信同步

#### 人员管理功能
1. **用户批量导入**
   - Excel格式用户信息导入
   - 自动密码生成和初始化
   - 用户状态批量管理

2. **角色权限管理**
   - 批量角色分配和撤销
   - 基于部门的角色继承
   - 权限模板快速应用

3. **组织关系管理**
   - 用户跨部门调动
   - 部门主管自动设置
   - 组织架构变更追踪

4. **数据同步集成**
   - 企业微信组织架构同步
   - 钉钉通讯录集成
   - LDAP目录服务对接

5. **报表统计功能**
   - 组织架构统计报表
   - 用户分布分析
   - 权限分配审计

### 兼容性
- JeecgBoot 3.8.1+
- MySQL 5.7+
- Python 3.8+
- 支持Docker部署

---

**报告生成时间**: 2025-07-20  
**版本**: v1.1 (新增人员信息API)  
**状态**: 生产就绪

## 📝 更新日志

### v1.1 (2025-07-20)
- ✅ 新增人员信息管理API (SysUserController)
- ✅ 新增职位管理API (SysPositionController) 
- ✅ 新增角色管理API (SysRoleController)
- ✅ 新增在线用户管理API (SysUserOnlineController)
- ✅ 扩展用户认证API (LoginController)
- ✅ 完善数据库结构分析 (用户、角色、职位表)
- ✅ 增加Java实体类完整结构文档
- ✅ 标注所有新增接口的必填字段 (⭐标识)
- ✅ 增加实体类注解特性和唯一性约束说明
- ✅ 增加人员管理自动化工具设计
- ✅ 更新使用指南和扩展功能规划

### v1.0 (2025-07-20)
- ✅ 部门管理API完整分析
- ✅ 自动化部门创建工具实现
- ✅ 数据库结构分析
- ✅ 测试结果验证