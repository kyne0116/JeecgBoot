# JeecgBoot 用户登录认证方案详解

## 一、认证架构概述

JeecgBoot 采用 **Shiro + JWT（JSON Web Token）** 的认证授权体系，实现了安全可靠的用户认证机制。

### 1.1 技术栈

- **Apache Shiro**：身份验证和授权框架
- **JWT**：无状态的Token认证方案
- **Redis**：Token缓存存储，实现会话管理
- **auth0 JWT库**：JWT的生成与验证

### 1.2 核心特性

- ✅ 基于JWT的无状态认证
- ✅ Token自动续签机制（用户在线操作不掉线）
- ✅ Redis缓存提升性能
- ✅ 支持多种登录方式（用户名密码、手机验证码、二维码扫码）
- ✅ 防暴力破解机制（登录失败次数限制）
- ✅ 多租户支持
- ✅ 跨域CORS支持

---

## 二、Token机制详解

### 2.1 Token类型说明

JeecgBoot实际上采用的是**单Token机制**，而非传统的双Token（access_token + refresh_token）机制。系统通过Redis缓存实现Token的自动刷新和延长有效期。

### 2.2 Token有效期

根据代码分析（`JwtUtil.java:45`）：

```java
/**Token有效期为7天（Token在redis中缓存时间为两倍）*/
public static final long EXPIRE_TIME = (7 * 12) * 60 * 60 * 1000;
```

| Token类型 | 有效期 | 说明 |
|----------|--------|------|
| **JWT Token** | 7天（84小时） | JWT本身的有效期 |
| **Redis缓存Token** | 14天（168小时） | Redis中缓存的Token有效期为JWT的2倍 |

> **注意**：代码中的计算公式 `(7 * 12) * 60 * 60 * 1000` 实际等于84小时，约为3.5天，而非7天。

### 2.3 Token生成机制

**位置**：`LoginController.java:486-489`

```java
// 1.生成token
String token = JwtUtil.sign(username, syspassword);
// 2.设置token缓存有效时间（JWT有效期的2倍）
redisUtil.set(CommonConstant.PREFIX_USER_TOKEN + token, token);
redisUtil.expire(CommonConstant.PREFIX_USER_TOKEN + token, JwtUtil.EXPIRE_TIME * 2 / 1000);
```

**Token组成**：
- **Header**：算法类型（HMAC256）
- **Payload**：包含用户名（username）和过期时间（expiresAt）
- **Signature**：使用用户密码作为密钥进行签名

**生成代码**（`JwtUtil.java:116-121`）：
```java
public static String sign(String username, String secret) {
    Date date = new Date(System.currentTimeMillis() + EXPIRE_TIME);
    Algorithm algorithm = Algorithm.HMAC256(secret);
    // 附带username信息
    return JWT.create().withClaim("username", username).withExpiresAt(date).sign(algorithm);
}
```

---

## 三、认证流程详解

### 3.1 用户登录流程

**接口地址**：`POST /sys/login`

**流程图**：

```
用户提交登录表单
    ↓
验证图形验证码（Redis）
    ↓
校验用户是否存在且有效
    ↓
校验用户名和密码
    ↓
生成JWT Token
    ↓
Token存入Redis（有效期14天）
    ↓
返回Token和用户信息
    ↓
前端保存Token到Header
```

**详细步骤**（`LoginController.java:82-141`）：

#### Step 1: 验证码校验
```java
String captcha = sysLoginModel.getCaptcha();
String keyPrefix = Md5Util.md5Encode(sysLoginModel.getCheckKey() + jeecgBaseConfig.getSignatureSecret(), "utf-8");
String realKey = keyPrefix + lowerCaseCaptcha;
Object checkCode = redisUtil.get(realKey);
if(checkCode == null || !checkCode.toString().equals(lowerCaseCaptcha)) {
    result.error500("验证码错误");
    result.setCode(HttpStatus.PRECONDITION_FAILED.value());
    return result;
}
```

**防护机制**：
- 验证码存储在Redis，有效期60秒
- Key采用MD5混淆（checkKey + 签名密钥 + 验证码）
- 验证码不区分大小写
- 登录成功后立即删除验证码

#### Step 2: 用户有效性校验
```java
SysUser sysUser = sysUserService.getOne(
    new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username)
);
result = sysUserService.checkUserIsEffective(sysUser);
```

**校验内容**：
- 用户是否存在
- 用户状态是否正常（未冻结、未删除）
- 用户是否在有效期内

#### Step 3: 密码校验
```java
String userpassword = PasswordUtil.encrypt(username, password, sysUser.getSalt());
String syspassword = sysUser.getPassword();
if (!syspassword.equals(userpassword)) {
    addLoginFailOvertimes(username);  // 记录失败次数
    result.error500("用户名或密码错误");
    return result;
}
```

**密码加密**：
- 采用盐值（Salt）加密
- 使用`username + password + salt`生成加密密码

**防暴力破解**（`LoginController.java:753-778`）：
```java
private boolean isLoginFailOvertimes(String username) {
    String key = CommonConstant.LOGIN_FAIL + username;
    Object failTime = redisUtil.get(key);
    if(failTime != null) {
        Integer val = Integer.parseInt(failTime.toString());
        if(val > 5) {
            return true;  // 失败次数超过5次
        }
    }
    return false;
}

private void addLoginFailOvertimes(String username) {
    String key = CommonConstant.LOGIN_FAIL + username;
    Object failTime = redisUtil.get(key);
    Integer val = 0;
    if(failTime != null) {
        val = Integer.parseInt(failTime.toString());
    }
    // 10分钟有效期
    redisUtil.set(key, ++val, 600);
}
```

| 限制项 | 阈值 | 锁定时间 |
|--------|------|----------|
| 登录失败次数 | 5次 | 10分钟 |

#### Step 4: 生成Token并返回
```java
// 生成JWT Token
String token = JwtUtil.sign(username, syspassword);

// Token存入Redis，有效期为JWT的2倍
redisUtil.set(CommonConstant.PREFIX_USER_TOKEN + token, token);
redisUtil.expire(CommonConstant.PREFIX_USER_TOKEN + token, JwtUtil.EXPIRE_TIME * 2 / 1000);

// 构建返回结果
JSONObject obj = new JSONObject();
obj.put("token", token);
obj.put("userInfo", sysUser);
obj.put("departs", sysDepartService.queryUserDeparts(sysUser.getId()));
```

---

### 3.2 请求认证流程

**所有受保护的接口请求都需要经过认证过滤器**

**流程图**：

```
前端请求（Header带Token）
    ↓
JwtFilter拦截器
    ↓
检查是否为白名单路径
    ↓
从Header获取Token
    ↓
ShiroRealm认证
    ↓
验证Token有效性
    ↓
Token自动续签（如需要）
    ↓
放行请求
```

#### 认证拦截器（`JwtFilter.java`）

**核心方法**（`JwtFilter.java:48-63`）：
```java
@Override
protected boolean isAccessAllowed(ServletRequest request, ServletResponse response, Object mappedValue) {
    try {
        // 判断是否为@IgnoreAuth注解的路径
        if (InMemoryIgnoreAuth.contains(((HttpServletRequest) request).getServletPath())) {
            return true;
        }

        executeLogin(request, response);
        return true;
    } catch (Exception e) {
        JwtUtil.responseError((HttpServletResponse)response, 401, CommonConstant.TOKEN_IS_INVALID_MSG);
        return false;
    }
}
```

**Token获取**（`JwtFilter.java:70-82`）：
```java
@Override
protected boolean executeLogin(ServletRequest request, ServletResponse response) throws Exception {
    HttpServletRequest httpServletRequest = (HttpServletRequest) request;
    // 优先从Header中获取
    String token = httpServletRequest.getHeader(CommonConstant.X_ACCESS_TOKEN);
    // 如果Header中没有，尝试从参数中获取（用于WebSocket等场景）
    if (oConvertUtils.isEmpty(token)) {
        token = httpServletRequest.getParameter("token");
    }

    JwtToken jwtToken = new JwtToken(token);
    // 提交给ShiroRealm进行认证
    getSubject(request, response).login(jwtToken);
    return true;
}
```

---

### 3.3 Token验证与自动续签

**位置**：`ShiroRealm.java:124-223`

#### Token验证流程

```java
public LoginUser checkUserTokenIsEffect(String token) throws AuthenticationException {
    // 1. 解密获取username
    String username = JwtUtil.getUsername(token);
    if (username == null) {
        throw new AuthenticationException("Token非法无效!");
    }

    // 2. 查询用户信息
    LoginUser loginUser = TokenUtils.getLoginUser(username, commonApi, redisUtil);
    if (loginUser == null) {
        throw new AuthenticationException("用户不存在!");
    }

    // 3. 判断用户状态
    if (loginUser.getStatus() != 1) {
        throw new AuthenticationException("账号已被锁定,请联系管理员!");
    }

    // 4. Token刷新验证
    if (!jwtTokenRefresh(token, username, loginUser.getPassword())) {
        throw new AuthenticationException(CommonConstant.TOKEN_IS_INVALID_MSG);
    }

    return loginUser;
}
```

#### Token自动续签机制（核心）

**实现原理**（`ShiroRealm.java:187-223`）：

```java
/**
 * JWTToken刷新生命周期（用户在线操作不掉线功能）
 *
 * 工作原理：
 * 1. 登录成功后将Token作为k、v存储到Redis（k和v值相同），缓存有效期为JWT的2倍
 * 2. 每次请求都会校验JWT Token是否有效
 * 3. 如果JWT Token已超时，但Redis中的Token缓存还在，则重新生成新Token并覆盖缓存
 * 4. 如果JWT Token已超时，且Redis中也没有缓存，则表示用户会话过期，需要重新登录
 *
 * 注意：前端Header中的Authorization保持不变，校验以Redis缓存中的Token为准
 *      用户真实过期时间 = JWT有效期 * 2
 */
public boolean jwtTokenRefresh(String token, String userName, String passWord) {
    // 从Redis获取缓存的Token
    String cacheToken = String.valueOf(redisUtil.get(CommonConstant.PREFIX_USER_TOKEN + token));

    if (oConvertUtils.isNotEmpty(cacheToken)) {
        // 校验Redis中的Token有效性
        if (!JwtUtil.verify(cacheToken, userName, passWord)) {
            // Token已失效，重新生成新Token
            String newAuthorization = JwtUtil.sign(userName, passWord);

            // 更新Redis中的Token（Key不变，Value更新为新Token）
            redisUtil.set(CommonConstant.PREFIX_USER_TOKEN + token, newAuthorization);
            // 重新设置过期时间（JWT有效期的2倍）
            redisUtil.expire(CommonConstant.PREFIX_USER_TOKEN + token, JwtUtil.EXPIRE_TIME * 2 / 1000);

            log.debug("用户在线操作，更新Token保证不掉线");
        }
        return true;
    }

    // Redis中不存在此Token，说明Token非法或已过期
    return false;
}
```

**续签机制示意图**：

```
用户登录
  ↓
生成Token A（有效期7天）
存入Redis: Key=prefix_user_token:TokenA, Value=TokenA（有效期14天）
  ↓
第8天：JWT Token A过期
  ↓
用户发起请求（Header仍然携带Token A）
  ↓
系统检测：JWT Token A已过期，但Redis中Key还存在
  ↓
生成新Token B（有效期7天）
更新Redis: Key=prefix_user_token:TokenA, Value=TokenB（有效期重新计算14天）
  ↓
请求通过，用户无感知
  ↓
第15天：如果用户无操作，Redis中Key过期
  ↓
用户再次请求时，Token A在Redis中不存在
  ↓
认证失败，需要重新登录
```

**关键点**：
1. **Redis Key不变**：始终使用用户登录时的原始Token作为Redis Key
2. **Redis Value变化**：Value会随着Token刷新而更新为新生成的Token
3. **前端无感知**：前端Header中的Token保持不变，无需手动刷新
4. **有效期延长**：每次Token刷新时，Redis缓存有效期重新计算

---

## 四、接口详细说明

### 4.1 登录接口

#### 1. 用户名密码登录

**接口路径**：`POST /sys/login`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 是 | 用户名 |
| password | String | 是 | 密码（明文） |
| captcha | String | 是 | 图形验证码 |
| checkKey | String | 是 | 验证码Key（前端生成的UUID） |

**请求示例**：
```json
{
  "username": "admin",
  "password": "123456",
  "captcha": "abcd",
  "checkKey": "1234567890"
}
```

**响应参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| success | Boolean | 请求是否成功 |
| message | String | 提示信息 |
| code | Integer | 响应码（200成功，500失败） |
| result | Object | 返回结果对象 |
| result.token | String | JWT Token |
| result.userInfo | Object | 用户基本信息 |
| result.departs | Array | 用户所属部门列表 |
| result.multi_depart | Integer | 部门数量标识（0:无部门，1:单部门，2:多部门） |
| result.sysAllDictItems | Object | 系统字典数据（仅Vue2前端返回） |

**响应示例**：
```json
{
  "success": true,
  "message": "登录成功",
  "code": 200,
  "result": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "userInfo": {
      "id": "1",
      "username": "admin",
      "realname": "管理员",
      "avatar": "/avatar/default.jpg",
      "orgCode": "A01",
      "status": 1
    },
    "departs": [
      {
        "id": "1",
        "departName": "技术部",
        "orgCode": "A01"
      }
    ],
    "multi_depart": 1
  },
  "timestamp": 1701234567890
}
```

**错误码说明**：

| 错误码 | 说明 |
|--------|------|
| 412 | 验证码错误 |
| 500 | 用户名或密码错误、用户不存在、账号被锁定等 |

**实现位置**：`LoginController.java:82-141`

---

#### 2. 手机验证码登录

**接口路径**：`POST /sys/phoneLogin`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| mobile | String | 是 | 手机号 |
| captcha | String | 是 | 短信验证码（6位数字） |

**请求示例**：
```json
{
  "mobile": "13800138000",
  "captcha": "123456"
}
```

**响应参数**：与用户名密码登录相同

**实现位置**：`LoginController.java:434-469`

---

#### 3. 移动端登录（App）

**接口路径**：`POST /sys/mLogin`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 是 | 用户名 |
| password | String | 是 | 密码 |

**请求示例**：
```json
{
  "username": "admin",
  "password": "123456"
}
```

**特点**：
- 不需要图形验证码
- 自动选择用户第一个部门
- 同样支持登录失败次数限制

**响应参数**：与Web登录相同

**实现位置**：`LoginController.java:602-672`

---

### 4.2 辅助接口

#### 1. 获取图形验证码

**接口路径**：`GET /sys/randomImage/{key}`

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| key | String | 是 | 验证码标识（前端生成的UUID） |

**响应参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| success | Boolean | 请求是否成功 |
| result | String | Base64编码的验证码图片 |

**响应示例**：
```json
{
  "success": true,
  "result": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "code": 200,
  "timestamp": 1701234567890
}
```

**验证码特性**：
- 4位随机字符（字母+数字）
- 有效期60秒
- 存储在Redis，Key为：MD5(key + signatureSecret) + 验证码小写
- 登录成功或失败后自动删除

**实现位置**：`LoginController.java:554-582`

---

#### 2. 发送短信验证码

**接口路径**：`POST /sys/sms`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| mobile | String | 是 | 手机号 |
| smsmode | String | 是 | 短信模板类型（0:登录，1:注册，2:忘记密码） |

**请求示例**：
```json
{
  "mobile": "13800138000",
  "smsmode": "0"
}
```

**响应参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| success | Boolean | 发送是否成功 |
| message | String | 提示信息 |

**短信验证码特性**：
- 6位随机数字
- 有效期10分钟（600秒）
- 存储在Redis，Key为：`sms:PHONE:` + 手机号
- 10分钟内不可重复发送

**防刷机制**（`LoginController.java:344-350`）：
```java
// IP限流检查
if(!DySmsLimit.canSendSms(clientIp)){
    log.warn("IP地址:{}, 短信接口请求太多", clientIp);
    result.setMessage("短信接口请求太多，请稍后再试！");
    result.setCode(CommonConstant.PHONE_SMS_FAIL_CODE);
    return result;
}
```

**实现位置**：`LoginController.java:316-424`

---

#### 3. 获取用户信息

**接口路径**：`GET /sys/user/getUserInfo`

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| X-Access-Token | String | 是 | JWT Token |

**响应参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| success | Boolean | 请求是否成功 |
| result | Object | 返回结果对象 |
| result.userInfo | Object | 用户详细信息 |
| result.sysAllDictItems | Object | 系统字典数据（Vue3前端专用） |

**响应示例**：
```json
{
  "success": true,
  "message": "",
  "code": 200,
  "result": {
    "userInfo": {
      "id": "1",
      "username": "admin",
      "realname": "管理员",
      "avatar": "/avatar/default.jpg",
      "email": "admin@jeecg.com",
      "phone": "13800138000",
      "orgCode": "A01",
      "orgId": "1",
      "homePath": "/dashboard/analysis"
    },
    "sysAllDictItems": {
      "sex": [
        { "value": "1", "text": "男" },
        { "value": "2", "text": "女" }
      ]
    }
  },
  "timestamp": 1701234567890
}
```

**实现位置**：`LoginController.java:148-184`

---

#### 4. 退出登录

**接口路径**：`GET /sys/logout`

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| X-Access-Token | String | 是 | JWT Token |

**响应参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| success | Boolean | 是否成功 |
| message | String | 提示信息 |

**退出登录操作**（`LoginController.java:193-208`）：
```java
@RequestMapping(value = "/logout")
public Result<Object> logout(HttpServletRequest request, HttpServletResponse response) {
    String token = request.getHeader(CommonConstant.X_ACCESS_TOKEN);
    if(oConvertUtils.isEmpty(token)) {
        return Result.error("退出登录失败！");
    }

    String username = JwtUtil.getUsername(token);
    LoginUser sysUser = sysBaseApi.getUserByName(username);

    if(sysUser != null) {
        // 异步清理缓存
        asyncClearLogoutCache(token, sysUser);
        // Shiro登出
        SecurityUtils.getSubject().logout();
        return Result.ok("退出登录成功！");
    } else {
        return Result.error("Token无效!");
    }
}
```

**清理缓存内容**（`LoginController.java:216-227`）：
1. 清空用户Token缓存：`prefix_user_token:` + token
2. 清空用户Shiro权限缓存：`shiro:cache:...:` + userId
3. 清空用户信息缓存：`sys:cache:user::` + username
4. 记录退出登录日志

**实现位置**：`LoginController.java:192-227`

---

#### 5. 二维码登录

**获取登录二维码**：`GET /sys/getLoginQrcode`

**响应参数**：
```json
{
  "success": true,
  "result": {
    "qrcodeId": "QRCODELOGIN:1234567890"
  },
  "code": 200
}
```

**二维码有效期**：30秒

**扫码确认登录**：`POST /sys/scanLoginQrcode`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| qrcodeId | String | 是 | 二维码ID |
| token | String | 是 | 已登录用户的Token |

**获取扫码结果**：`GET /sys/getQrcodeToken?qrcodeId={qrcodeId}`

**响应参数**：

| token值 | 说明 |
|---------|------|
| -2 | 二维码已过期 |
| -1 | 等待扫码 |
| 有效Token | 扫码成功，返回登录Token |

**实现位置**：`LoginController.java:699-746`

---

### 4.3 前端集成说明

#### 请求拦截器配置

**Axios请求拦截器示例**：

```javascript
// 请求拦截器
axios.interceptors.request.use(
  config => {
    // 从本地存储获取Token
    const token = localStorage.getItem('X-Access-Token')
    if (token) {
      // 设置Token到请求头
      config.headers['X-Access-Token'] = token
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axios.interceptors.response.use(
  response => {
    // Token自动续签后，后端会在响应头返回新Token（如果有）
    const newToken = response.headers['x-access-token']
    if (newToken) {
      localStorage.setItem('X-Access-Token', newToken)
    }
    return response
  },
  error => {
    // Token失效，跳转登录页
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('X-Access-Token')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

---

## 五、安全机制详解

### 5.1 密码安全

#### 密码加密存储

**加密算法**：`PasswordUtil.encrypt(username, password, salt)`

**加密流程**：
1. 生成用户专属盐值（Salt）
2. 组合：`username + password + salt`
3. 使用加密算法生成密码Hash
4. 数据库仅存储Hash和Salt，不存储明文密码

#### 密码传输安全

**前端加密**（可选）：
- 支持使用RSA/AES对密码进行前端加密
- 通过`/sys/getEncryptedString`接口获取加密Key和IV
- 前端使用`crypto-js`库进行加密

**示例**（`LoginController.java:537-545`）：
```java
@GetMapping(value = "/getEncryptedString")
public Result<Map<String,String>> getEncryptedString(){
    Result<Map<String,String>> result = new Result<>();
    Map<String,String> map = new HashMap<>(5);
    map.put("key", EncryptedString.key);
    map.put("iv", EncryptedString.iv);
    result.setResult(map);
    return result;
}
```

---

### 5.2 防暴力破解

#### 登录失败次数限制

| 限制项 | 阈值 | 锁定时间 | Redis Key |
|--------|------|----------|-----------|
| 登录失败次数 | 5次 | 10分钟 | `login_fail:` + username |

**实现原理**：
- 每次登录失败，失败次数+1
- 失败次数存储在Redis，有效期10分钟
- 失败次数超过5次，拒绝登录
- 登录成功后，清除失败次数记录

---

### 5.3 验证码防护

#### 图形验证码

**特性**：
- 4位随机字符（字母+数字）
- 有效期60秒
- 不区分大小写
- 使用后立即失效

**Redis存储**：
- Key：MD5(checkKey + signatureSecret) + 验证码小写
- Value：验证码小写
- 有效期：60秒

#### 短信验证码

**特性**：
- 6位随机数字
- 有效期10分钟
- 10分钟内不可重复发送
- IP限流防刷

**短信限流**（`LoginController.java:344`）：
```java
if(!DySmsLimit.canSendSms(clientIp)){
    log.warn("IP地址:{}, 短信接口请求太多", clientIp);
    result.setMessage("短信接口请求太多，请稍后再试！");
    result.setCode(CommonConstant.PHONE_SMS_FAIL_CODE);
    return result;
}
```

---

### 5.4 跨域安全

**CORS配置**（`JwtFilter.java:89-115`）：

```java
@Override
protected boolean preHandle(ServletRequest request, ServletResponse response) throws Exception {
    HttpServletRequest httpServletRequest = (HttpServletRequest) request;
    HttpServletResponse httpServletResponse = (HttpServletResponse) response;

    if(allowOrigin){
        // 允许跨域
        httpServletResponse.setHeader(HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN,
            httpServletRequest.getHeader(HttpHeaders.ORIGIN));
        // 允许的请求方法
        httpServletResponse.setHeader(HttpHeaders.ACCESS_CONTROL_ALLOW_METHODS,
            "GET,POST,OPTIONS,PUT,DELETE");
        // 允许的请求头
        String requestHeaders = httpServletRequest.getHeader(HttpHeaders.ACCESS_CONTROL_REQUEST_HEADERS);
        if (StringUtils.isNotEmpty(requestHeaders)) {
            httpServletResponse.setHeader(HttpHeaders.ACCESS_CONTROL_ALLOW_HEADERS, requestHeaders);
        }
        // 允许携带凭证信息
        httpServletResponse.setHeader(HttpHeaders.ACCESS_CONTROL_ALLOW_CREDENTIALS, "true");
    }

    // OPTIONS预检请求直接返回
    if (RequestMethod.OPTIONS.name().equalsIgnoreCase(httpServletRequest.getMethod())) {
        httpServletResponse.setStatus(HttpStatus.OK.value());
        return false;
    }

    return super.preHandle(request, response);
}
```

**配置说明**：
- 支持OPTIONS预检请求
- 允许携带Cookie和Authorization
- 可配置是否启用跨域（微服务模式下建议关闭）

---

## 六、多租户支持

### 6.1 租户隔离机制

**租户ID传递**（`JwtFilter.java:110-112`）：
```java
// 从请求头获取租户ID
String tenantId = httpServletRequest.getHeader(CommonConstant.TENANT_ID);
// 设置到线程上下文
TenantContext.setTenant(tenantId);
```

**租户校验**（`ShiroRealm.java:147-183`）：
```java
// 校验用户的tenant_id和前端传过来的是否一致
String userTenantIds = loginUser.getRelTenantIds();
if(MybatisPlusSaasConfig.OPEN_SYSTEM_TENANT_CONTROL && oConvertUtils.isNotEmpty(userTenantIds)){
    String contextTenantId = TenantContext.getTenant();
    // 判断用户是否有权限访问该租户
    String[] arr = userTenantIds.split(",");
    if(!oConvertUtils.isIn(contextTenantId, arr)){
        // 租户授权变更，需要重新登录
        throw new AuthenticationException("登录租户授权变更，请重新登陆!");
    }
}
```

**特点**：
- 前端通过Header传递租户ID
- 后端校验用户是否有权限访问该租户
- 支持用户关联多个租户
- 租户切换需要重新登录

---

## 七、性能优化

### 7.1 Redis缓存策略

**缓存内容**：

| 缓存项 | Redis Key | 有效期 | 说明 |
|--------|-----------|--------|------|
| Token缓存 | `prefix_user_token:` + token | JWT有效期×2 | 用于Token续签 |
| 用户信息缓存 | `sys:cache:user::` + username | 永久 | 减少数据库查询 |
| Shiro权限缓存 | `shiro:cache:...` + userId | 永久 | 权限信息缓存 |
| 验证码缓存 | MD5(key) + code | 60秒 | 图形验证码 |
| 短信验证码 | `sms:PHONE:` + mobile | 600秒 | 短信验证码 |
| 登录失败次数 | `login_fail:` + username | 600秒 | 防暴力破解 |

### 7.2 缓存刷新策略

**用户信息缓存更新**：
- 用户登录时写入
- 用户信息修改时更新
- 用户退出登录时清除

**权限缓存更新**：
- 角色权限变更时清除用户权限缓存
- 支持实时生效，无需重新登录

---

## 八、常见问题

### Q1：Token过期后如何处理？

**A**：JeecgBoot采用自动续签机制：
- JWT Token有效期为7天
- Redis缓存有效期为14天
- 在7-14天之间，用户请求时会自动刷新Token
- 超过14天未操作，需要重新登录
- 前端无需手动刷新Token

### Q2：如何实现"记住我"功能？

**A**：通过延长Token有效期实现：
```java
// 登录时根据"记住我"选项设置不同的过期时间
if (rememberMe) {
    redisUtil.expire(CommonConstant.PREFIX_USER_TOKEN + token, 30 * 24 * 60 * 60); // 30天
} else {
    redisUtil.expire(CommonConstant.PREFIX_USER_TOKEN + token, JwtUtil.EXPIRE_TIME * 2 / 1000); // 14天
}
```

### Q3：如何强制用户下线？

**A**：删除Redis中的Token缓存：
```java
// 删除指定用户的Token
redisUtil.del(CommonConstant.PREFIX_USER_TOKEN + token);
// 删除用户权限缓存
redisUtil.del(CommonConstant.PREFIX_USER_SHIRO_CACHE + userId);
// 删除用户信息缓存
redisUtil.del(String.format("%s::%s", CacheConstant.SYS_USERS_CACHE, username));
```

### Q4：如何防止Token被窃取？

**A**：采用以下安全措施：
1. **HTTPS传输**：生产环境必须使用HTTPS
2. **HttpOnly Cookie**：如果使用Cookie存储Token，设置HttpOnly标志
3. **Token绑定IP**（可选）：验证请求IP与登录IP是否一致
4. **短有效期**：JWT有效期设置为7天，减少被盗用风险
5. **刷新机制**：自动刷新Token，旧Token失效

### Q5：多设备登录如何处理？

**A**：当前实现支持多设备登录：
- 每次登录生成新Token
- 多个Token可以同时有效
- 退出登录只清除当前Token

**如需实现单点登录（踢出其他设备）**：
```java
// 登录时删除该用户的所有Token
Set<String> keys = redisUtil.keys(CommonConstant.PREFIX_USER_TOKEN + "*");
for (String key : keys) {
    String token = key.substring(CommonConstant.PREFIX_USER_TOKEN.length());
    String username = JwtUtil.getUsername(token);
    if (username.equals(currentUsername)) {
        redisUtil.del(key);
    }
}
// 然后生成新Token
```

### Q6：如何修改Token有效期？

**A**：修改`JwtUtil.java`中的常量：
```java
// 修改JWT有效期（单位：毫秒）
public static final long EXPIRE_TIME = 7 * 24 * 60 * 60 * 1000; // 7天

// Redis缓存有效期会自动设置为JWT有效期的2倍
redisUtil.expire(CommonConstant.PREFIX_USER_TOKEN + token, JwtUtil.EXPIRE_TIME * 2 / 1000);
```

---

## 九、开发建议

### 9.1 前端开发

1. **Token存储**：建议使用`localStorage`或`sessionStorage`
2. **请求拦截**：统一在Axios拦截器中添加Token
3. **响应处理**：401错误时跳转登录页
4. **Token刷新**：无需手动处理，后端自动续签

### 9.2 后端开发

1. **接口鉴权**：使用`@RequiresPermissions`注解
2. **白名单配置**：使用`@IgnoreAuth`注解排除鉴权
3. **获取当前用户**：
```java
// 方法1：从Shiro获取
LoginUser user = (LoginUser) SecurityUtils.getSubject().getPrincipal();

// 方法2：从Request获取
String username = JwtUtil.getUserNameByToken(request);
LoginUser user = sysBaseApi.getUserByName(username);
```

### 9.3 安全建议

1. **生产环境**：
   - 启用HTTPS
   - 修改默认签名密钥（`jeecgBaseConfig.signatureSecret`）
   - 配置防火墙和IP白名单

2. **Token安全**：
   - 定期轮换签名密钥
   - 监控异常登录行为
   - 记录详细的审计日志

3. **密码安全**：
   - 强制密码复杂度要求
   - 定期提醒用户修改密码
   - 使用前端加密传输密码

---

## 十、核心代码文件索引

| 文件路径 | 说明 |
|---------|------|
| `LoginController.java:82-141` | 用户名密码登录 |
| `LoginController.java:434-469` | 手机验证码登录 |
| `LoginController.java:602-672` | 移动端登录 |
| `LoginController.java:192-227` | 退出登录 |
| `JwtUtil.java:116-121` | JWT Token生成 |
| `JwtUtil.java:80-92` | JWT Token验证 |
| `JwtFilter.java:48-83` | JWT认证过滤器 |
| `ShiroRealm.java:98-117` | Shiro身份认证 |
| `ShiroRealm.java:124-185` | Token有效性校验 |
| `ShiroRealm.java:200-223` | Token自动续签机制 |
| `LoginController.java:554-582` | 获取图形验证码 |
| `LoginController.java:316-424` | 发送短信验证码 |
| `LoginController.java:753-778` | 防暴力破解 |

---

## 附录：完整认证流程时序图

```
┌──────┐      ┌──────┐     ┌─────────┐     ┌───────┐     ┌─────┐
│ 前端 │      │ 后端 │     │JwtFilter│     │ Shiro │     │Redis│
└──┬───┘      └──┬───┘     └────┬────┘     └───┬───┘     └──┬──┘
   │             │               │              │            │
   │ 1. POST /login             │              │            │
   ├────────────>│               │              │            │
   │             │ 2. 验证码校验 │              │            │
   │             ├──────────────────────────────────────────>│
   │             │<──────────────────────────────────────────┤
   │             │ 3. 用户密码校验                           │
   │             ├─(查询数据库)─>│              │            │
   │             │<──────────────┤              │            │
   │             │ 4. 生成JWT Token             │            │
   │             ├──────────────>│              │            │
   │             │ 5. Token存入Redis            │            │
   │             ├──────────────────────────────────────────>│
   │             │ 6. 返回Token  │              │            │
   │<────────────┤               │              │            │
   │             │               │              │            │
   │ 7. GET /api (带Token)      │              │            │
   ├────────────>│               │              │            │
   │             │ 8. JWT过滤   │              │            │
   │             ├──────────────>│              │            │
   │             │               │ 9. Shiro认证 │            │
   │             │               ├─────────────>│            │
   │             │               │              │10. 查Redis │
   │             │               │              ├───────────>│
   │             │               │              │<───────────┤
   │             │               │              │11. Token刷新│
   │             │               │              ├───────────>│
   │             │               │<─────────────┤            │
   │             │               │ 12. 认证通过 │            │
   │             │<──────────────┤              │            │
   │             │ 13. 业务处理 │              │            │
   │             ├─(业务逻辑)──>│              │            │
   │             │ 14. 返回结果 │              │            │
   │<────────────┤               │              │            │
   │             │               │              │            │
```

---

**文档版本**：v1.0
**最后更新**：2025-12-01
**适用版本**：JeecgBoot 3.x+

**维护者**：JeecgBoot开发团队
**联系方式**：http://jeecg.com
