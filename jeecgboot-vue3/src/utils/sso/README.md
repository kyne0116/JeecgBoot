# SSO单点登录解决方案

## 概述

企业级SSO单点登录解决方案，提供全面的用户身份集成能力。支持webauth（后端主导）和apiauth（前端主导）两种模式，通过统一的参数体系和智能状态管理，实现高效、安全的用户身份认证。

## 核心特点

- 🎯 **统一参数体系**：标准化URL参数格式，降低集成复杂度，提高开发效率
- 🚀 **智能防重复**：内置重复检测机制，确保系统稳定性和用户体验
- 🌐 **全页面支持**：无缝集成，用户可从任意页面直接访问，提升使用便利性
- 💾 **全局状态管理**：集中化会话管理，保障系统一致性和安全性
- 🔄 **用户切换**：智能用户身份识别，支持多用户环境下的灵活切换

## 参数规范

统一的SSO参数格式：

```bash
?sso=true&sso_mode={mode}&sso_data={data}&sso_redirect={path}
```

### 参数定义

| 参数 | 必需性 | 说明 | 使用场景 |
|------|--------|------|----------|
| `sso=true` | 必需 | SSO标识 | 所有模式 |
| `sso_mode` | 必需 | SSO模式：`webauth`、`apiauth` | 所有模式 |
| `sso_data` | 必需 | SSO数据：token、加密用户名 | 所有模式 |
| `sso_redirect` | 可选 | 目标路径 | **仅webauth模式使用** |
| `sso_error` | 可选 | 错误信息 | 失败时自动添加 |
| `sso_silent` | 可选 | 静默模式 | 需要时添加 |

**重要说明：**
- **apiauth（前端主导）**：不需要`sso_redirect`参数，登录成功后自动停留在当前访问页面
- **webauth（后端主导）**：必须提供`redirectUrl`参数，后端将生成包含`sso_redirect`的统一格式URL

## 使用方式

### 1. webauth模式（后端主导）

**适用场景：** 传统网站、门户系统、第三方系统集成

**调用流程：**
```bash
# 1. 第三方系统调用后端接口（实际访问地址）
GET http://localhost:8080/jeecg-boot/sys/sso/webauth?sso_data=encrypted_username&redirectUrl=http://localhost:3100/dashboard

# 2. 后端处理后自动重定向到前端（用户浏览器自动跳转到此地址）
http://localhost:3100/dashboard?sso=true&sso_mode=webauth&sso_data=jwt_token

# 3. 前端路由守卫自动处理SSO登录，用户停留在目标页面
```

### 2. apiauth模式（前端主导）

**适用场景：** 单页应用、前后端分离架构、精确控制场景

**使用方式：**
```bash
# 用户直接访问前端页面（无需sso_redirect参数）
http://localhost:3100/dashboard/analysis?sso=true&sso_mode=apiauth&sso_data=encrypted_username
http://localhost:3100/chart-design?sso=true&sso_mode=apiauth&sso_data=encrypted_username
http://localhost:3100/data-analysis?sso=true&sso_mode=apiauth&sso_data=encrypted_username

# 前端路由守卫自动调用后端API完成登录，用户停留在当前访问页面
```

## 技术架构

### 核心组件

#### GlobalSSOManager
- **位置：** `src/utils/sso/GlobalSSOManager.ts`
- **职责：** SSO核心逻辑处理、状态管理、模式分发

#### SSO路由守卫
- **位置：** `src/router/guard/ssoGuard.ts`
- **职责：** 全局SSO监控、自动触发处理

#### 后端接口
- **位置：** `SsoLoginController.java`
- **职责：** webauth和apiauth模式的服务端处理

### 处理流程

```typescript
// 应用启动初始化
await globalSSOManager.initialize();

// 路由导航时自动处理
await globalSSOManager.processSSOLogin();
```

## 开发集成

### 应用启动集成

```typescript
// main.ts
import { globalSSOManager } from '/@/utils/sso/GlobalSSOManager';

async function bootstrap() {
  // ... 其他初始化代码

  // 初始化SSO管理器
  await globalSSOManager.initialize();

  // ... 继续启动流程
}
```

### 路由守卫集成

```typescript
// router/guard/index.ts
import { createSSOGuard } from './ssoGuard';

export function setupRouterGuard(router: Router) {
  // ... 其他守卫
  createSSOGuard(router); // SSO路由守卫（在权限守卫之前）
  // ... 其他守卫
}
```

### 登出时清理SSO会话

```typescript
// store/modules/user.ts
import { globalSSOManager } from '/@/utils/sso/GlobalSSOManager';

async logout() {
  // 清理SSO会话
  globalSSOManager.clearSession();

  // ... 其他登出逻辑
}
```

## API接口

### webauth接口

```http
GET /sys/sso/webauth?sso_data={加密用户名}&redirectUrl={前端URL}
```

**响应：** 重定向到前端页面并携带SSO参数

### apiauth接口

```http
GET/POST /sys/sso/apiauth?sso_data={加密用户名}
```

**响应格式：**
```json
{
  "success": true,
  "result": {
    "token": "jwt_token_here",
    "userInfo": { ... },
    "departs": [ ... ]
  }
}
```

## 加密工具

### 生成加密数据

```java
// 后端使用EncryptorUtil生成加密数据
String encrypted = EncryptorUtil.encode("SIMBEST_SSO", "username");
```

### 测试工具

运行`SsoLoginController.main()`方法生成测试用加密数据：

```bash
用户: admin => 79C023386BAC6785E7EBD524110262678F770CF81CAB43EA38579DDF839A57B8...
用户: jeecg => 79138138A9ACAF75C7AC9924FD0AB0A036770C6A1CAB151408571641679AFE20...
```

## 调试功能

### 开发模式日志

- `🔍 检测到SSO参数` - 发现有效的SSO参数
- `🚀 执行 {mode} 模式SSO登录` - 开始执行SSO流程
- `✅ SSO {mode} 模式登录成功` - SSO登录成功（仅控制台日志）
- `❌ SSO {mode} 模式登录失败` - SSO登录失败
- `🎯 路由守卫SSO处理完成` - 路由层处理完成

### 状态监控

```typescript
// 获取详细状态信息（调试用）
const debugState = {
  processing: globalSSOManager.getState().processing,
  sessionId: globalSSOManager.getState().sessionId,
  hasActiveSession: globalSSOManager.hasActiveSession(),
  currentUser: globalSSOManager.getCurrentUser()
};
```

## 快速测试

### 生成加密数据

```bash
# 在后端项目中运行
cd jeecg-boot/jeecg-module-system/jeecg-system-biz
# 编译并运行SsoLoginController.main()方法生成加密数据
```

### 测试webauth模式

```bash
# 访问后端接口（会自动重定向到前端）
http://localhost:8080/jeecg-boot/sys/sso/webauth?sso_data={加密数据}&redirectUrl=http://localhost:3100/dashboard
```

### 测试apiauth模式

```bash
# 直接访问前端页面
http://localhost:3100/dashboard/analysis?sso=true&sso_mode=apiauth&sso_data={加密数据}
```

## 常见问题

### 1. SSO参数被清理了怎么办？
SSO登录成功后会自动清理URL参数，这是正常行为，确保URL整洁。

### 2. 如何支持用户切换？
系统自动支持用户切换，只需使用不同的加密数据再次访问SSO URL即可。

### 3. 加密数据有效期是多久？
默认1800秒（30分钟），可在`SsoLoginController`中调整`EncryptorUtil.decode()`的timeout参数。

### 4. 是否支持多个前端应用？
是的，`redirectUrl`参数可以指向任意前端应用地址。

## 文件结构

```
src/utils/sso/
├── GlobalSSOManager.ts          # 核心SSO管理器
└── README.md                    # 使用文档

src/router/guard/
└── ssoGuard.ts                  # SSO路由守卫

jeecg-boot/.../controller/
└── SsoLoginController.java      # SSO后端接口

jeecg-boot/.../util/
└── EncryptorUtil.java           # 加密工具类
```

## 技术特性

- **TypeScript支持**：类型安全保障，提供完整的IDE支持和代码提示
- **Promise/Async**：采用现代异步模式，提升性能和用户体验
- **单例模式**：全局统一状态管理，避免数据不一致问题
- **错误容错**：健壮的异常处理机制，保障系统稳定运行

---

**维护人员：** SIMBEST Development Team
**文档版本：** v1.0
**最后更新：** 2025-09-08
