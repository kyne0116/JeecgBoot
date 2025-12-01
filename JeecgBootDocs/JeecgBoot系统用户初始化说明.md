# JeecgBoot 系统用户初始化说明

## 一、密码加密机制

### 1.1 加密算法

JeecgBoot 使用 **PBEWithMD5AndDES** 算法进行密码加密。

### 1.2 加密函数

```java
PasswordUtil.encrypt(username, inputPassword, salt)
```

### 1.3 参数说明

| 参数            | 说明                             | 示例       |
| --------------- | -------------------------------- | ---------- |
| `username`      | 用户名，作为明文被加密           | "zhangsan" |
| `inputPassword` | 用户输入的密码，用于生成加密密钥 | "123456"   |
| `salt`          | 盐值，固定使用                   | "RCGTeGiH" |
| 迭代次数        | 固定值                           | 1000 次    |

### 1.4 加密过程

1. 使用 `inputPassword` 生成 PBE 密钥
2. 使用 `username` 作为明文进行加密
3. 返回十六进制加密结果

### 1.5 加密示例

```java
// 示例1：用户名 zhangsan，密码 123456
encrypt("zhangsan", "123456", "RCGTeGiH")
// 结果: 6196c262ea6e604a1a81da40c2db91d5

// 示例2：用户名 lisi，密码 123456
encrypt("lisi", "123456", "RCGTeGiH")
// 结果: 4a91d2f5b36cf576
```

> **重要提示**: 即使使用相同的明文密码，不同用户名会产生不同的加密结果！

## 二、sys_user 表结构说明

### 2.1 核心字段

| 字段名          | 类型        | 说明                          | 是否必填 |
| --------------- | ----------- | ----------------------------- | -------- |
| `id`            | VARCHAR(36) | 主键 ID                       | 是       |
| `username`      | VARCHAR     | 登录账号（唯一）              | 是       |
| `realname`      | VARCHAR     | 真实姓名                      | 是       |
| `password`      | VARCHAR     | 加密后的密码                  | 是       |
| `salt`          | VARCHAR     | 密码盐值（固定：RCGTeGiH）    | 是       |
| `avatar`        | VARCHAR     | 头像 URL                      | 否       |
| `birthday`      | DATE        | 生日                          | 否       |
| `sex`           | INT         | 性别（1:男 2:女）             | 否       |
| `email`         | VARCHAR     | 电子邮件                      | 否       |
| `phone`         | VARCHAR     | 手机号                        | 否       |
| `telephone`     | VARCHAR     | 座机号                        | 否       |
| `org_code`      | VARCHAR     | 所属部门编码                  | 否       |
| `work_no`       | VARCHAR     | 工号（唯一）                  | 否       |
| `status`        | INT         | 状态（1:正常 2:冻结）         | 是       |
| `del_flag`      | INT         | 删除标记（0:正常 1:已删除）   | 是       |
| `user_identity` | INT         | 身份（0:普通成员 1:上级）     | 否       |
| `depart_ids`    | VARCHAR     | 负责部门 ID 列表              | 否       |
| `activiti_sync` | INT         | 同步工作流（0:不同步 1:同步） | 否       |
| `client_id`     | VARCHAR     | 设备 ID（uni-app 推送用）     | 否       |
| `bpm_status`    | VARCHAR     | 流程状态                      | 否       |
| `create_by`     | VARCHAR     | 创建人                        | 否       |
| `create_time`   | DATETIME    | 创建时间                      | 否       |
| `update_by`     | VARCHAR     | 更新人                        | 否       |
| `update_time`   | DATETIME    | 更新时间                      | 否       |

### 2.2 表索引

- **主键索引**: `id`
- **唯一索引**: `idx_username_orgcode` (username + org_code)
- **唯一约束**: `username`（用户名全局唯一）

### 2.3 数据初始化脚本

系统用户初始化脚本支持多次执行，会先清理现有数据再插入新数据。

#### 2.3.1 建表语句（参考）

```sql
CREATE TABLE `sys_user` (
  `id` varchar(36) NOT NULL COMMENT '主键ID',
  `username` varchar(100) DEFAULT NULL COMMENT '登录账号',
  `realname` varchar(100) DEFAULT NULL COMMENT '真实姓名',
  `password` varchar(255) DEFAULT NULL COMMENT '密码',
  `salt` varchar(50) DEFAULT NULL COMMENT 'md5密码盐',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像',
  `birthday` date DEFAULT NULL COMMENT '生日',
  `sex` int DEFAULT NULL COMMENT '性别(1:男 2:女)',
  `email` varchar(100) DEFAULT NULL COMMENT '电子邮件',
  `phone` varchar(20) DEFAULT NULL COMMENT '电话',
  `telephone` varchar(30) DEFAULT NULL COMMENT '座机号',
  `org_code` varchar(64) DEFAULT NULL COMMENT '登录选择部门编码',
  `work_no` varchar(50) DEFAULT NULL COMMENT '工号',
  `status` int DEFAULT '1' COMMENT '状态(1:正常 2:冻结)',
  `del_flag` int DEFAULT '0' COMMENT '删除状态(0:正常 1:已删除)',
  `user_identity` int DEFAULT NULL COMMENT '身份(0:普通成员 1:上级)',
  `depart_ids` varchar(1000) DEFAULT NULL COMMENT '负责部门',
  `activiti_sync` int DEFAULT NULL COMMENT '同步工作流引擎(1:同步 0:不同步)',
  `client_id` varchar(255) DEFAULT NULL COMMENT '设备id',
  `bpm_status` varchar(10) DEFAULT NULL COMMENT '流程状态',
  `create_by` varchar(50) DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(50) DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `login_tenant_id` int DEFAULT NULL COMMENT '登录选择租户ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `idx_username_orgcode` (`username`,`org_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

#### 2.3.2 初始化数据示例

**示例 1：普通员工账号**

```sql
-- 用户名: zhangsan
-- 密码: 123456（明文）
-- 加密后密码: 6196c262ea6e604a1a81da40c2db91d5
INSERT INTO `sys_user` (
    `id`,
    `username`,
    `realname`,
    `password`,
    `salt`,
    `sex`,
    `email`,
    `phone`,
    `work_no`,
    `org_code`,
    `status`,
    `del_flag`,
    `user_identity`,
    `activiti_sync`,
    `create_by`,
    `create_time`,
    `update_by`,
    `update_time`
) VALUES (
    '1743521234567890001',                     -- id (雪花ID格式)
    'zhangsan',                                 -- username
    '张三',                                     -- realname
    '6196c262ea6e604a1a81da40c2db91d5',       -- password (加密后)
    'RCGTeGiH',                                -- salt
    1,                                         -- sex (1:男)
    'zhangsan@company.com',                   -- email
    '13800138001',                            -- phone
    'EMP001',                                 -- work_no
    'A01',                                    -- org_code
    1,                                        -- status (1:正常)
    0,                                        -- del_flag (0:未删除)
    0,                                        -- user_identity (0:普通成员)
    0,                                        -- activiti_sync (0:不同步)
    'admin',                                  -- create_by
    NOW(),                                    -- create_time
    'admin',                                  -- update_by
    NOW()                                     -- update_time
);
```

**示例 2：部门主管账号**

```sql
-- 用户名: lisi
-- 密码: 123456（明文）
-- 加密后密码: 4a91d2f5b36cf576
INSERT INTO `sys_user` (
    `id`,
    `username`,
    `realname`,
    `password`,
    `salt`,
    `sex`,
    `email`,
    `phone`,
    `work_no`,
    `org_code`,
    `status`,
    `del_flag`,
    `user_identity`,
    `depart_ids`,
    `activiti_sync`,
    `create_by`,
    `create_time`,
    `update_by`,
    `update_time`
) VALUES (
    '1743521234567890002',                     -- id (雪花ID格式)
    'lisi',                                    -- username
    '李四',                                     -- realname
    '4a91d2f5b36cf576',                       -- password (加密后)
    'RCGTeGiH',                                -- salt
    2,                                         -- sex (2:女)
    'lisi@company.com',                       -- email
    '13800138002',                            -- phone
    'MGR001',                                 -- work_no
    'A01',                                    -- org_code
    1,                                        -- status (1:正常)
    0,                                        -- del_flag (0:未删除)
    1,                                        -- user_identity (1:上级)
    'A01,A01A01',                             -- depart_ids (负责部门)
    1,                                        -- activiti_sync (1:同步)
    'admin',                                  -- create_by
    NOW(),                                    -- create_time
    'admin',                                  -- update_by
    NOW()                                     -- update_time
);
```

### 2.4 初始化数据注意事项

1. **ID 生成规则**

   - 使用雪花算法生成唯一 ID
   - 格式：19 位数字字符串
   - 可使用 JeecgBoot 提供的 ID 生成工具类

2. **密码生成**

   - 必须使用 `PasswordUtil.encrypt(username, "123456", "RCGTeGiH")` 生成
   - 每个用户的加密密码都不相同，即使明文密码相同

3. **必填字段检查**

   ```
   - id: 必填
   - username: 必填且唯一
   - realname: 必填
   - password: 必填
   - salt: 必填，固定值 "RCGTeGiH"
   - status: 必填，默认 1（正常）
   - del_flag: 必填，默认 0（未删除）
   ```

4. **状态字段说明**

   - `status`: 1=正常（可登录），2=冻结（禁止登录）
   - `del_flag`: 0=正常，1=已删除（逻辑删除）
   - `user_identity`: 0=普通成员，1=上级（部门主管）

5. **多租户场景**
   - 如果系统启用多租户，需要设置 `login_tenant_id`
   - `org_code` 配合 `username` 保证租户内用户名唯一

## 三、登录验证测试

### 3.1 API 接口信息

- **接口地址**: `POST http://localhost:8080/jeecg-boot/sys/mLogin`
- **请求头**: `Content-Type: application/json`
- **请求体格式**:
  ```json
  {
    "username": "用户名",
    "password": "明文密码"
  }
  ```

### 3.2 测试示例（使用 cURL）

```bash
curl -X POST http://localhost:8080/jeecg-boot/sys/mLogin \
  -H "Content-Type: application/json" \
  -d '{"username": "zhangsan", "password": "123456"}'
```

### 3.3 响应说明

#### 成功响应示例

```json
{
  "success": true,
  "message": "登录成功",
  "code": 200,
  "result": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userInfo": {
      "username": "zhangsan",
      "realname": "张三"
    }
  }
}
```

#### 失败响应示例

```json
{
  "success": false,
  "message": "用户名或密码错误",
  "code": 500
}
```

## 四、开发注意事项

1. **密码存储安全**

   - 数据库中只存储加密后的密码
   - 加密过程中使用用户名作为明文，增加安全性
   - 固定盐值配合用户名确保每个用户的加密结果唯一

2. **测试账号管理**

   - 初始化脚本可重复执行
   - 测试环境建议使用统一的简单密码（如：123456）
   - 生产环境必须使用强密码

3. **密码修改**

   - 用户修改密码时，需要使用相同的加密算法
   - 确保新密码也通过 `PasswordUtil.encrypt()` 加密后存储

4. **安全建议**
   - 生产环境应定期更换盐值（需同步修改所有用户密码）
   - 建议增加密码强度验证
   - 建议启用密码过期策略

## 五、常见问题

### Q1: 为什么相同密码不同用户加密结果不同？

**A**: 因为加密过程使用用户名作为明文进行加密，不同用户名会产生不同的加密结果。

### Q2: 如何生成新用户的密码？

**A**: 使用 `PasswordUtil.encrypt(username, password, "RCGTeGiH")` 方法生成加密密码。

### Q3: 忘记密码怎么办？

**A**:

- 开发环境：直接修改数据库中的密码字段
- 生产环境：通过密码重置功能或管理员重置

### Q4: 如何验证密码是否正确？

**A**:

```java
String encryptedPassword = PasswordUtil.encrypt(username, inputPassword, salt);
return encryptedPassword.equals(dbPassword);
```

## 六、相关文件

- 加密工具类：`org.jeecg.common.util.PasswordUtil`
- 登录接口：`/sys/mLogin`
- 用户实体：`org.jeecg.modules.system.entity.SysUser`

---

**文档版本**: V1.1
**最后更新**: 2025-01-02
**维护人员**: JeecgBoot 开发团队
