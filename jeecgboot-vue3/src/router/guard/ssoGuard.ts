/**
 * SSO路由守卫
 * 使用GlobalSSOManager统一处理所有SSO模式
 *
 * 核心职责：
 * - 在路由导航时检测SSO参数
 * - 调用GlobalSSOManager统一处理
 * - 跳过不需要SSO的特殊路由
 *
 * @author SIMBEST
 * @date 2025-09-08
 */
import type { Router, RouteLocationNormalized } from 'vue-router';
import { globalSSOManager } from '/@/utils/sso/GlobalSSOManager';

/**
 * 创建SSO路由守卫
 * @param router 路由实例
 */
export function createSSOGuard(router: Router) {
  router.beforeEach(async (to: RouteLocationNormalized) => {
    // 跳过不需要SSO检查的特殊路由
    if (shouldSkipSSO(to)) {
      return true;
    }

    try {
      // 统一SSO处理 - 智能检测所有SSO模式
      const result = await globalSSOManager.processSSOLogin({
        source: 'router-guard',
        silent: false
      });

      if (result) {
        console.log(`🎯 路由守卫SSO处理完成:`, {
          success: result.success,
          mode: result.mode,
          path: to.path
        });
      }

      // 始终允许继续导航
      return true;

    } catch (error) {
      console.error('❌ 路由守卫SSO处理异常:', error);
      // 异常时不阻塞用户访问
      return true;
    }
  });
}

/**
 * 判断是否应该跳过SSO检查
 * @param route 路由对象
 * @returns 是否跳过
 */
function shouldSkipSSO(route: RouteLocationNormalized): boolean {
  const path = route.path;

  // 跳过登录相关页面
  if (path === '/login' || path.startsWith('/login/')) {
    return true;
  }

  // 跳过不需要认证的页面
  if (route.meta?.ignoreAuth === true) {
    return true;
  }

  // 跳过SSO调试页面（避免循环）
  if (path.startsWith('/sso-') || path.includes('/sso/')) {
    return true;
  }

  // 跳过API路径
  if (path.startsWith('/api/')) {
    return true;
  }

  // 跳过静态资源路径
  if (path.startsWith('/assets/') || path.includes('.')) {
    return true;
  }

  return false;
}
