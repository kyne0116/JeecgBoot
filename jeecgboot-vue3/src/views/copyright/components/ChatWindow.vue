<template>
  <div class="chat-window-container">
    <!-- 消息列表区域 -->
    <div ref="messagesContainer" class="messages-container">
      <a-empty
        v-if="!currentSession"
        description="请选择或创建一个会话"
        :image="Empty.PRESENTED_IMAGE_SIMPLE"
      />

      <div v-else class="messages-list">
        <!-- 消息项 -->
        <div
          v-for="(message, index) in messageList"
          :key="index"
          class="message-item"
          :class="`message-${message.messageType.toLowerCase()}`"
        >
          <div class="message-avatar">
            <a-avatar v-if="message.messageType === 'USER'" :style="{ backgroundColor: '#1890ff' }">
              <template #icon>
                <UserOutlined />
              </template>
            </a-avatar>
            <a-avatar v-else :style="{ backgroundColor: '#52c41a' }">
              <template #icon>
                <RobotOutlined />
              </template>
            </a-avatar>
          </div>

          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">
                {{ message.messageType === 'USER' ? '我' : 'AI助手' }}
              </span>
              <span class="message-time">
                {{ formatTime(message.createTime) }}
              </span>
            </div>
            <div class="message-text">
              {{ message.content }}
            </div>
          </div>
        </div>

        <!-- AI思考中提示 -->
        <div v-if="isThinking" class="message-item message-system">
          <div class="message-avatar">
            <a-avatar :style="{ backgroundColor: '#faad14' }">
              <template #icon>
                <LoadingOutlined />
              </template>
            </a-avatar>
          </div>
          <div class="message-content">
            <div class="thinking-text">
              <a-spin size="small" /> AI正在思考...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container">
      <!-- SSE连接状态提示 -->
      <div class="connection-status">
        <a-tag v-if="sseConnected" color="success">
          <template #icon>
            <CheckCircleOutlined />
          </template>
          已连接
        </a-tag>
        <a-tag v-else color="warning">
          <template #icon>
            <DisconnectOutlined />
          </template>
          未连接
        </a-tag>
        <a-tag :color="getStatusColor(currentSession?.sessionStatus)">
          {{ getStatusText(currentSession?.sessionStatus) }}
        </a-tag>
      </div>

      <!-- 输入框 -->
      <div class="input-wrapper">
        <a-textarea
          v-model:value="userInput"
          placeholder="请输入您的回答..."
          :rows="3"
          :disabled="!canSendMessage"
          @pressEnter="handleSendMessage"
          :maxlength="1000"
          show-count
        />
        <a-button
          type="primary"
          size="large"
          :loading="sending"
          :disabled="!canSendMessage || !userInput.trim()"
          @click="handleSendMessage"
        >
          <template #icon>
            <SendOutlined />
          </template>
          发送
        </a-button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue';
import { message, Empty } from 'ant-design-vue';
import {
  UserOutlined,
  RobotOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  DisconnectOutlined,
  SendOutlined,
} from '@ant-design/icons-vue';
import { useCopyrightStore } from '/@/store/modules/copyright';
import { useSSE } from '/@/views/copyright/composables/useSSE';
import { sendMessage as sendMessageApi } from '/@/api/copyright';
import type { CopyrightSession, SSEEventData } from '/@/api/model/copyrightModel';
import dayjs from 'dayjs';

// Emit事件
const emit = defineEmits<{
  sessionCompleted: [session: CopyrightSession];
  filesGenerated: [];
}>();

// Store
const copyrightStore = useCopyrightStore();

// 状态
const userInput = ref('');
const sending = ref(false);
const isThinking = ref(false);
const messagesContainer = ref<HTMLElement>();

// Computed
const currentSession = computed(() => copyrightStore.currentSession);
const messageList = computed(() => copyrightStore.messageList);
const sseConnected = computed(() => copyrightStore.sseConnected);

// 是否可以发送消息
const canSendMessage = computed(() => {
  return (
    currentSession.value &&
    sseConnected.value &&
    !sending.value &&
    (currentSession.value.sessionStatus === 'CLARIFYING' ||
      currentSession.value.sessionStatus === 'WAITING')
  );
});

// SSE连接实例
let sseInstance: ReturnType<typeof useSSE> | null = null;

/**
 * 处理SSE消息
 */
const handleSSEMessage = (event: SSEEventData) => {
  console.log('[ChatWindow] 收到SSE消息:', event);

  switch (event.type) {
    case 'QUESTION':
      // AI提出问题
      isThinking.value = false;
      copyrightStore.addMessage({
        sessionId: currentSession.value!.sessionId,
        messageType: 'AGENT',
        content: event.data || event.message || '',
      });
      scrollToBottom();
      break;

    case 'THINKING':
      // AI思考中
      isThinking.value = true;
      break;

    case 'COMPLETED':
      // 会话完成
      isThinking.value = false;
      if (event.sessionStatus) {
        copyrightStore.updateSessionStatus(event.sessionStatus);
      }
      message.success('需求澄清完成，开始生成文件...');
      emit('sessionCompleted', currentSession.value!);
      emit('filesGenerated');
      break;

    case 'ERROR':
      // 错误
      isThinking.value = false;
      message.error(event.message || '发生错误');
      break;

    case 'HEARTBEAT':
      // 心跳，忽略
      break;

    default:
      console.warn('[ChatWindow] 未知的SSE事件类型:', event.type);
  }
};

/**
 * 建立SSE连接
 */
const connectSSE = () => {
  if (!currentSession.value) return;

  // 断开旧连接
  disconnectSSE();

  // 建立新连接
  sseInstance = useSSE(currentSession.value.sessionId, {
    onMessage: handleSSEMessage,
    onOpen: () => {
      console.log('[ChatWindow] SSE连接成功');
      copyrightStore.setSSEConnected(true);
    },
    onError: (error) => {
      console.error('[ChatWindow] SSE连接错误:', error);
      copyrightStore.setSSEConnected(false);
      message.error('SSE连接失败，请刷新重试');
    },
    onClose: () => {
      console.log('[ChatWindow] SSE连接关闭');
      copyrightStore.setSSEConnected(false);
    },
    autoReconnect: true,
    maxReconnectAttempts: 5,
  });

  sseInstance.connect();
};

/**
 * 断开SSE连接
 */
const disconnectSSE = () => {
  if (sseInstance) {
    sseInstance.disconnect();
    sseInstance = null;
  }
};

/**
 * 发送消息
 */
const handleSendMessage = async (e?: Event) => {
  // 如果是按Enter且有Shift键，不发送消息
  if (e && (e as KeyboardEvent).shiftKey) {
    return;
  }

  e?.preventDefault();

  if (!canSendMessage.value || !userInput.value.trim()) {
    return;
  }

  const content = userInput.value.trim();
  userInput.value = '';
  sending.value = true;
  isThinking.value = true;

  try {
    // 添加用户消息到列表
    copyrightStore.addMessage({
      sessionId: currentSession.value!.sessionId,
      messageType: 'USER',
      content,
    });

    scrollToBottom();

    // 发送消息到后端
    await sendMessageApi({
      sessionId: currentSession.value!.sessionId,
      userInput: content,
    });

    console.log('[ChatWindow] 消息发送成功');
  } catch (error) {
    console.error('[ChatWindow] 发送消息失败:', error);
    message.error('发送消息失败');
    isThinking.value = false;
  } finally {
    sending.value = false;
  }
};

/**
 * 滚动到底部
 */
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

/**
 * 格式化时间
 */
const formatTime = (time?: string): string => {
  if (!time) return dayjs().format('HH:mm:ss');
  return dayjs(time).format('HH:mm:ss');
};

/**
 * 获取状态颜色
 */
const getStatusColor = (status?: string): string => {
  const colorMap: Record<string, string> = {
    WAITING: 'default',
    CLARIFYING: 'processing',
    GENERATING: 'warning',
    COMPLETED: 'success',
    ERROR: 'error',
  };
  return colorMap[status || ''] || 'default';
};

/**
 * 获取状态文本
 */
const getStatusText = (status?: string): string => {
  const textMap: Record<string, string> = {
    WAITING: '等待中',
    CLARIFYING: '澄清中',
    GENERATING: '生成中',
    COMPLETED: '已完成',
    ERROR: '错误',
  };
  return textMap[status || ''] || '未知';
};

// 监听会话变化，自动连接SSE
watch(
  currentSession,
  (newSession) => {
    if (newSession) {
      connectSSE();
      scrollToBottom();
    } else {
      disconnectSSE();
    }
  },
  { immediate: true }
);

// 组件卸载时断开SSE连接
onUnmounted(() => {
  disconnectSSE();
});
</script>

<style lang="less" scoped>
.chat-window-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fafafa;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.messages-list {
  max-width: 800px;
  margin: 0 auto;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  flex-shrink: 0;
  margin-right: 12px;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.message-sender {
  font-weight: 500;
  font-size: 14px;
  color: #262626;
}

.message-time {
  font-size: 12px;
  color: #bfbfbf;
}

.message-text {
  padding: 12px;
  border-radius: 8px;
  background: #fff;
  line-height: 1.6;
  word-wrap: break-word;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.message-user .message-content {
  margin-left: auto;
}

.message-user .message-text {
  background: #e6f4ff;
}

.message-agent .message-text {
  background: #fff;
}

.thinking-text {
  padding: 12px;
  border-radius: 8px;
  background: #fffbe6;
  color: #faad14;
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-container {
  border-top: 1px solid #f0f0f0;
  background: #fff;
  padding: 16px;
}

.connection-status {
  margin-bottom: 12px;
  display: flex;
  gap: 8px;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;

  .ant-input-textarea-show-count {
    flex: 1;
  }
}
</style>
