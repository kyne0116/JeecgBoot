/**
 * 全局SSO管理器
 * 
 * 核心功能：
 * - 统一处理所有SSO模式（webauth、apiauth、cas）
 * - 智能参数检测和验证
 * - 防重复执行机制
 * - 用户切换检测
 * - 会话状态管理
 * - URL参数自动清理
 * 
 * @author AI Assistant
 * @date 2025-09-10
 */

import { defHttp } from '/@/utils/http/axios';
import { useUserStoreWithOut } from '/@/store/modules/user';
import { useMessage } from '/@/hooks/web/useMessage';

// 统一SSO参数接口
export interface UnifiedSSOParams {
  sso: 'true';                                 // SSO标识，必需
  sso_mode: 'webauth' | 'apiauth' | 'cas';     // SSO模式，必需
  sso_data: string;                            // SSO数据，必需
  sso_redirect?: string;                       // 目标路径，可选
  sso_error?: string;                          // 错误信息，可选
  sso_silent?: 'true' | 'false';               // 是否静默，可选
  sso_timestamp?: string;                      // 时间戳，可选
}

// SSO处理结果接口
export interface SSOResult {
  success: boolean;
  mode?: string;
  userInfo?: any;
  message?: string;
  redirectTo?: string;
  error?: any;
}

// SSO状态接口
interface SSOState {
  processing: boolean;
  lastProcessTime: number;
  currentUser: any;
  sessionId: string;
  initialized: boolean;
}

// SSO处理选项
export interface SSOOptions {
  source?: string;                             // 调用来源标识
  forceRelogin?: boolean;                      // 强制重新登录
  silent?: boolean;                            // 静默模式
}

/**
 * 全局SSO管理器
 * 
 * 设计理念：
 * 1. 单一职责：只负责SSO核心逻辑，不处理UI和路由
 * 2. 统一参数：所有SSO模式使用相同的URL参数格式
 * 3. 防重复：智能检测和防重复执行机制
 * 4. 状态管理：全局SSO状态和用户会话管理
 */
export class GlobalSSOManager {
  private static instance: GlobalSSOManager;
  private state: SSOState;
  private userStore: any = null;
  private createMessage: any = null;

  private constructor() {
    this.state = {
      processing: false,
      lastProcessTime: 0,
      currentUser: null,
      sessionId: '',
      initialized: false
    };
  }

  /**
   * 获取单例实例
   */
  public static getInstance(): GlobalSSOManager {
    if (!GlobalSSOManager.instance) {
      GlobalSSOManager.instance = new GlobalSSOManager();
    }
    return GlobalSSOManager.instance;
  }

  /**
   * 初始化SSO管理器
   * 在应用启动时调用
   */
  public async initialize(): Promise<void> {
    if (this.state.initialized) {
      return;
    }

    try {
      // 初始化依赖
      this.userStore = useUserStoreWithOut();
      const { createMessage } = useMessage();
      this.createMessage = createMessage;
      
      // 恢复SSO会话状态
      const ssoSessionId = localStorage.getItem('sso-session');
      if (ssoSessionId) {
        this.state.sessionId = ssoSessionId;
        this.state.currentUser = this.userStore?.getUserInfo || null;
      }
      
      this.state.initialized = true;
      console.log('✅ GlobalSSOManager 初始化完成');
    } catch (error) {
      console.warn('⚠️ GlobalSSOManager 初始化部分失败:', error);
      // 初始化失败不阻塞应用启动
      this.state.initialized = true;
    }
  }

  /**
   * 统一SSO处理入口
   * 在路由守卫中调用
   */
  public async processSSOLogin(options: SSOOptions = {}): Promise<SSOResult | null> {
    // 确保已初始化
    if (!this.state.initialized) {
      await this.initialize();
    }

    // 1. 检测SSO参数
    const ssoParams = this.detectSSOParams();
    if (!ssoParams) {
      return null;
    }

    console.log('🔍 检测到SSO参数:', ssoParams);

    // 2. 检查是否需要处理
    if (!this.shouldProcessSSO(ssoParams, options)) {
      console.log('⏭️ 跳过SSO处理:', this.getSkipReason(ssoParams, options));
      return null;
    }

    // 3. 设置处理状态
    this.state.processing = true;
    
    try {
      // 4. 分发到对应的处理器
      const result = await this.dispatchSSOHandler(ssoParams);
      
      // 5. 处理结果
      if (result.success) {
        await this.handleSSOSuccess(result, ssoParams);
      } else {
        await this.handleSSOError(result, ssoParams);
      }

      // 6. 清理URL参数
      this.cleanSSOParams();

      return result;
      
    } finally {
      this.state.processing = false;
      this.state.lastProcessTime = Date.now();
    }
  }

  /**
   * 智能检测SSO参数
   */
  private detectSSOParams(): UnifiedSSOParams | null {
    const urlParams = new URLSearchParams(window.location.search);
    
    // 必须有sso=true标识
    if (urlParams.get('sso') !== 'true') {
      return null;
    }

    const ssoMode = urlParams.get('sso_mode');
    const ssoData = urlParams.get('sso_data');
    
    // 检查必需参数
    if (!ssoMode || !ssoData) {
      console.warn('⚠️ SSO参数不完整:', { 
        sso_mode: ssoMode, 
        sso_data: ssoData ? `${ssoData.substring(0, 20)}...` : null 
      });
      return null;
    }

    // 验证SSO模式
    if (!['webauth', 'apiauth', 'cas'].includes(ssoMode)) {
      console.warn('⚠️ 不支持的SSO模式:', ssoMode);
      return null;
    }

    return {
      sso: 'true',
      sso_mode: ssoMode as any,
      sso_data: ssoData,
      sso_redirect: urlParams.get('sso_redirect') || undefined,
      sso_error: urlParams.get('sso_error') || undefined,
      sso_silent: (urlParams.get('sso_silent') as any) || undefined,
      sso_timestamp: urlParams.get('sso_timestamp') || undefined,
    };
  }

  /**
   * 检查是否需要处理SSO
   */
  private shouldProcessSSO(params: UnifiedSSOParams, options: SSOOptions): boolean {
    // 强制重新登录
    if (options.forceRelogin) {
      return true;
    }

    // 如果有错误参数，需要处理错误
    if (params.sso_error) {
      return true;
    }

    // 正在处理中，跳过
    if (this.state.processing) {
      return false;
    }

    // 防重复处理（3秒内）
    const now = Date.now();
    if (now - this.state.lastProcessTime < 3000) {
      return false;
    }

    // 检查是否需要用户切换
    if (this.hasValidUserSession()) {
      return this.needUserSwitch(params);
    }

    return true;
  }

  /**
   * 根据模式分发到对应处理器
   */
  private async dispatchSSOHandler(params: UnifiedSSOParams): Promise<SSOResult> {
    // 优先处理错误
    if (params.sso_error) {
      return {
        success: false,
        mode: params.sso_mode,
        message: decodeURIComponent(params.sso_error)
      };
    }

    console.log(`🚀 执行 ${params.sso_mode} 模式SSO登录`);

    switch (params.sso_mode) {
      case 'webauth':
        return await this.handleWebauth(params);
        
      case 'apiauth':
        return await this.handleApiauth(params);
        
      case 'cas':
        return await this.handleCAS(params);
        
      default:
        return {
          success: false,
          message: `不支持的SSO模式: ${params.sso_mode}`
        };
    }
  }

  /**
   * 处理webauth模式（后端主导）
   */
  private async handleWebauth(params: UnifiedSSOParams): Promise<SSOResult> {
    try {
      const token = params.sso_data;
      
      // 确保stores已初始化
      if (!this.userStore) {
        this.userStore = useUserStoreWithOut();
      }
      
      // 设置token
      await this.userStore.setToken(token);
      
      // 获取用户信息
      await this.userStore.getUserInfoAction();
      
      const userInfo = this.userStore.getUserInfo;
      
      return {
        success: true,
        mode: 'webauth',
        userInfo: userInfo,
        message: 'Webauth登录成功',
        redirectTo: params.sso_redirect
      };
      
    } catch (error: any) {
      console.error('❌ Webauth处理失败:', error);
      
      // 清理可能的无效token
      localStorage.removeItem('Access-Token');
      this.userStore?.setToken('');
      
      return {
        success: false,
        mode: 'webauth',
        message: error.message || 'Token验证失败',
        error: error
      };
    }
  }

  /**
   * 处理apiauth模式（前端主导）
   */
  private async handleApiauth(params: UnifiedSSOParams): Promise<SSOResult> {
    try {
      const encryptedUsername = params.sso_data;
      
      // 调用后端API
      const response = await defHttp.get<any>({
        url: '/sys/sso/apiauth',
        params: { sso_data: encryptedUsername },
      });

      if (response && response.token) {
        const { token, userInfo, departs, multi_depart } = response;
        
        // 确保stores已初始化
        if (!this.userStore) {
          this.userStore = useUserStoreWithOut();
        }
        
        // 设置用户状态
        localStorage.setItem('Access-Token', token);
        localStorage.setItem('userInfo', JSON.stringify(userInfo));
        
        await this.userStore.setToken(token);
        await this.userStore.setUserInfo(userInfo);
        await this.userStore.afterLoginAction(false, { token, userInfo, departs, multi_depart });
        
        return {
          success: true,
          mode: 'apiauth',
          userInfo: userInfo,
          message: 'Apiauth登录成功',
          redirectTo: params.sso_redirect
        };
      } else {
        return {
          success: false,
          mode: 'apiauth',
          message: '登录失败：响应格式错误'
        };
      }
      
    } catch (error: any) {
      console.error('❌ Apiauth处理失败:', error);
      
      let message = '系统异常，请稍后重试';
      if (error.response?.status === 401) {
        message = '认证失败，用户名无效或已过期';
        // 清理可能的无效数据
        localStorage.removeItem('Access-Token');
        localStorage.removeItem('userInfo');
        this.userStore?.setToken('');
      }
      
      return {
        success: false,
        mode: 'apiauth',
        message: message,
        error: error
      };
    }
  }

  /**
   * 处理CAS模式
   */
  private async handleCAS(params: UnifiedSSOParams): Promise<SSOResult> {
    // TODO: 实现CAS处理逻辑
    console.warn('⚠️ CAS模式暂未实现');
    return {
      success: false,
      mode: 'cas',
      message: 'CAS模式暂未实现'
    };
  }

  /**
   * 处理SSO成功
   */
  private async handleSSOSuccess(result: SSOResult, params: UnifiedSSOParams): Promise<void> {
    // 生成并保存SSO会话ID
    const sessionId = this.generateSessionId();
    localStorage.setItem('sso-session', sessionId);
    this.state.sessionId = sessionId;
    this.state.currentUser = result.userInfo;
    
    // SSO登录成功后不显示任何提示，直接进入页面
    
    console.log(`✅ SSO ${result.mode} 模式登录成功`, {
      username: result.userInfo?.username,
      realname: result.userInfo?.realname,
      sessionId: sessionId
    });
  }

  /**
   * 处理SSO错误
   */
  private async handleSSOError(result: SSOResult, params: UnifiedSSOParams): Promise<void> {
    // 清理可能的无效状态
    if (this.userStore) {
      await this.userStore.setToken('');
    }
    localStorage.removeItem('Access-Token');
    localStorage.removeItem('userInfo');
    localStorage.removeItem('sso-session');
    this.state.sessionId = '';
    this.state.currentUser = null;
    
    // 显示错误消息（除非静默模式）
    const isSilent = params.sso_silent === 'true';
    if (!isSilent && this.createMessage) {
      this.createMessage.error(result.message || 'SSO登录失败');
    }
    
    console.error(`❌ SSO ${result.mode} 模式登录失败:`, result.message);
  }

  /**
   * 清理SSO参数
   */
  private cleanSSOParams(): void {
    const url = new URL(window.location.href);
    const ssoParams = [
      'sso', 
      'sso_mode', 
      'sso_data', 
      'sso_redirect', 
      'sso_error', 
      'sso_silent',
      'sso_timestamp'
    ];
    
    let hasChanges = false;
    ssoParams.forEach(param => {
      if (url.searchParams.has(param)) {
        url.searchParams.delete(param);
        hasChanges = true;
      }
    });
    
    if (hasChanges) {
      window.history.replaceState({}, document.title, url.toString());
      console.log('🧹 已清理SSO参数');
    }
  }

  /**
   * 检查是否有有效用户会话
   */
  private hasValidUserSession(): boolean {
    const token = localStorage.getItem('Access-Token');
    const userInfo = localStorage.getItem('userInfo');
    const ssoSession = localStorage.getItem('sso-session');
    
    return !!(token && userInfo && ssoSession);
  }

  /**
   * 检查是否需要用户切换
   */
  private needUserSwitch(params: UnifiedSSOParams): boolean {
    // webauth模式：通过token无法直接判断用户身份，需要验证
    if (params.sso_mode === 'webauth') {
      return true;
    }
    
    // apiauth模式：可以通过解密用户名判断
    // 这里简化处理，允许重新登录以支持用户切换
    return true;
  }

  /**
   * 生成SSO会话ID
   */
  private generateSessionId(): string {
    return `sso-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
  }

  /**
   * 获取跳过SSO处理的原因（用于调试）
   */
  private getSkipReason(params: UnifiedSSOParams, options: SSOOptions): string {
    if (this.state.processing) {
      return '正在处理中';
    }
    
    const timeSinceLastProcess = Date.now() - this.state.lastProcessTime;
    if (timeSinceLastProcess < 3000) {
      return `防重复处理 (${Math.round(timeSinceLastProcess / 1000)}s ago)`;
    }
    
    if (this.hasValidUserSession() && !this.needUserSwitch(params)) {
      return '用户已登录且为同一用户';
    }
    
    return '其他原因';
  }

  /**
   * 获取当前SSO状态（用于调试）
   */
  public getState(): Readonly<SSOState> {
    return { ...this.state };
  }

  /**
   * 获取当前用户信息
   */
  public getCurrentUser(): any {
    return this.state.currentUser;
  }

  /**
   * 检查是否有活动的SSO会话
   */
  public hasActiveSession(): boolean {
    return !!this.state.sessionId && this.hasValidUserSession();
  }

  /**
   * 手动清理SSO会话（用于登出等场景）
   */
  public clearSession(): void {
    localStorage.removeItem('sso-session');
    this.state.sessionId = '';
    this.state.currentUser = null;
    console.log('🧹 已清理SSO会话');
  }
}

// 导出单例实例
export const globalSSOManager = GlobalSSOManager.getInstance();

// 导出默认实例（用于ES6 import）
export default globalSSOManager;