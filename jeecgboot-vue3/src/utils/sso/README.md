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
| `sso_mode` | 必需 | SSO模式：`webauth`、`apiauth`、`cas` | 所有模式 |
| `sso_data` | 必需 | SSO数据：token、加密用户名或ticket | 所有模式 |
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
GET http://localhost:54009/dictd/sys/sso/webauth?sso_data=encrypted_username&redirectUrl=http://localhost:3100/dashboard

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
  createSSOGuard(router); // SSO路由守卫
  // ... 其他守卫
}
```

## API接口

### webauth接口

```http
GET /sys/sso/webauth?username={加密用户名}&redirectUrl={前端URL}
```

**响应：** 重定向到前端页面并携带SSO参数

### apiauth接口

```http
GET/POST /sys/sso/apiauth?username={加密用户名}
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

## 状态管理

### SSO会话

系统自动管理SSO会话状态：

```typescript
// 检查是否有活动的SSO会话
const hasSession = globalSSOManager.hasActiveSession();

// 获取当前SSO状态
const state = globalSSOManager.getState();

// 获取当前用户信息
const user = globalSSOManager.getCurrentUser();
```

### 会话清理

```typescript
// 手动清理SSO会话（用于登出场景）
globalSSOManager.clearSession();
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

## 使用场景对比

### apiauth模式（前端主导）- 推荐

**特点：** 用户直接访问前端页面，无需`sso_redirect`参数

```bash
# 直接访问任意页面，停留在当前页面
http://localhost:3100/dashboard/analysis?sso=true&sso_mode=apiauth&sso_data=encrypted_user
http://localhost:3100/chart-design?sso=true&sso_mode=apiauth&sso_data=encrypted_user  
http://localhost:3100/data-analysis?sso=true&sso_mode=apiauth&sso_data=encrypted_user

# 用户切换示例
http://localhost:3100/dashboard?sso=true&sso_mode=apiauth&sso_data=user1_encrypted
http://localhost:3100/dashboard?sso=true&sso_mode=apiauth&sso_data=user2_encrypted
```

### webauth模式（后端主导）

**特点：** 第三方系统调用后端接口，需要`redirectUrl`参数

```bash
# 第三方系统调用后端接口（实际发起地址）
GET http://localhost:54009/dictd/sys/sso/webauth?sso_data=encrypted_user&redirectUrl=http://localhost:3100/dashboard/analysis
GET http://localhost:54009/dictd/sys/sso/webauth?sso_data=encrypted_user&redirectUrl=http://localhost:3100/chart-design

# 后端自动重定向到前端（用户浏览器自动跳转，无需手动访问）
http://localhost:3100/dashboard/analysis?sso=true&sso_mode=webauth&sso_data=jwt_token
```

### 错误处理

```bash
# 系统自动处理错误情况
http://localhost:3100/dashboard?sso=true&sso_mode=webauth&sso_error=登录失败
```

## 配置选项

### 防重复处理

默认3秒防重复间隔，可在GlobalSSOManager中调整：

```typescript
// 防重复处理时间（毫秒）
if (now - this.state.lastProcessTime < 3000) {
  return false;
}
```

### 静默模式

```bash
# 添加silent参数禁止显示登录消息
?sso=true&sso_mode=apiauth&sso_data=encrypted_user&sso_silent=true
```

## 测试验证

### 后端接口测试

```bash
# 测试apiauth接口（返回JSON数据）
curl "http://localhost:54009/dictd/sys/sso/apiauth?sso_data=加密用户名"

# 测试webauth接口（返回302重定向）
curl -I "http://localhost:54009/dictd/sys/sso/webauth?sso_data=加密用户名&redirectUrl=http://localhost:3100/dashboard"
```

### 实际使用测试

```bash
# apiauth模式（推荐）- 用户直接访问前端页面
http://localhost:3100/dashboard/analysis?sso=true&sso_mode=apiauth&sso_data=加密用户名

# webauth模式 - 第三方系统/用户访问后端接口（会自动重定向到前端）
http://localhost:54009/dictd/sys/sso/webauth?sso_data=加密用户名&redirectUrl=http://localhost:3100/dashboard
```

## 文件结构

```
src/utils/sso/
├── GlobalSSOManager.ts          # 核心SSO管理器
└── README.md                   # 使用文档

src/router/guard/
└── ssoGuard.ts                 # SSO路由守卫

jeecg-boot/.../controller/
└── SsoLoginController.java     # SSO后端接口
```

## 技术特性

- **TypeScript支持**：类型安全保障，提供完整的IDE支持和代码提示
- **Promise/Async**：采用现代异步模式，提升性能和用户体验
- **单例模式**：全局统一状态管理，避免数据不一致问题
- **事件驱动**：灵活的扩展架构，支持业务定制和功能扩展
- **错误容错**：健壮的异常处理机制，保障系统稳定运行

---

**维护人员：** Development Team  
**文档版本：** v2.0  
**最后更新：** 2025-09-10