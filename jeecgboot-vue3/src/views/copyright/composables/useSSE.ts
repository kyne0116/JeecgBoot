/**
 * SSE连接管理 - Composable Hook
 *
 * 提供SSE连接的创建、管理和事件处理功能
 *
 * @author Claude Code
 * @since 2025-12-03 (T017)
 */

import { ref, onUnmounted } from 'vue';
import { buildSSEUrl } from '/@/api/copyright';
import type { SSEEventData } from '/@/api/model/copyrightModel';

export interface SSEOptions {
  /**
   * SSE事件回调
   */
  onMessage?: (event: SSEEventData) => void;

  /**
   * 连接成功回调
   */
  onOpen?: () => void;

  /**
   * 连接错误回调
   */
  onError?: (error: Event) => void;

  /**
   * 连接关闭回调
   */
  onClose?: () => void;

  /**
   * 自动重连
   */
  autoReconnect?: boolean;

  /**
   * 重连间隔（毫秒）
   */
  reconnectInterval?: number;

  /**
   * 最大重连次数
   */
  maxReconnectAttempts?: number;
}

export function useSSE(sessionId: string, options: SSEOptions = {}) {
  const {
    onMessage,
    onOpen,
    onError,
    onClose,
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options;

  // SSE连接实例
  const eventSource = ref<EventSource | null>(null);

  // 连接状态
  const connected = ref(false);

  // 重连次数
  const reconnectAttempts = ref(0);

  // 重连定时器
  let reconnectTimer: number | null = null;

  /**
   * 建立SSE连接
   */
  const connect = () => {
    if (eventSource.value) {
      console.warn('[useSSE] SSE连接已存在，先关闭旧连接');
      disconnect();
    }

    try {
      const url = buildSSEUrl(sessionId);
      console.log('[useSSE] 建立SSE连接:', url);

      eventSource.value = new EventSource(url);

      // 连接打开事件
      eventSource.value.onopen = () => {
        console.log('[useSSE] SSE连接成功');
        connected.value = true;
        reconnectAttempts.value = 0;
        onOpen?.();
      };

      // 消息事件
      eventSource.value.onmessage = (event: MessageEvent) => {
        try {
          const data: SSEEventData = JSON.parse(event.data);
          console.log('[useSSE] 收到SSE消息:', data);
          onMessage?.(data);
        } catch (error) {
          console.error('[useSSE] 解析SSE消息失败:', error);
        }
      };

      // 错误事件
      eventSource.value.onerror = (error: Event) => {
        console.error('[useSSE] SSE连接错误:', error);
        connected.value = false;
        onError?.(error);

        // 自动重连
        if (autoReconnect && reconnectAttempts.value < maxReconnectAttempts) {
          scheduleReconnect();
        } else {
          console.log('[useSSE] 达到最大重连次数或未启用自动重连');
          disconnect();
        }
      };

    } catch (error) {
      console.error('[useSSE] 创建SSE连接失败:', error);
      onError?.(error as Event);
    }
  };

  /**
   * 安排重连
   */
  const scheduleReconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
    }

    reconnectAttempts.value++;
    console.log(`[useSSE] 将在 ${reconnectInterval}ms 后进行第 ${reconnectAttempts.value} 次重连`);

    reconnectTimer = window.setTimeout(() => {
      console.log('[useSSE] 开始重连...');
      connect();
    }, reconnectInterval);
  };

  /**
   * 断开SSE连接
   */
  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    if (eventSource.value) {
      console.log('[useSSE] 关闭SSE连接');
      eventSource.value.close();
      eventSource.value = null;
      connected.value = false;
      onClose?.();
    }
  };

  /**
   * 手动重连
   */
  const reconnect = () => {
    console.log('[useSSE] 手动重连');
    reconnectAttempts.value = 0;
    disconnect();
    connect();
  };

  // 组件卸载时自动断开连接
  onUnmounted(() => {
    disconnect();
  });

  return {
    eventSource,
    connected,
    reconnectAttempts,
    connect,
    disconnect,
    reconnect,
  };
}
