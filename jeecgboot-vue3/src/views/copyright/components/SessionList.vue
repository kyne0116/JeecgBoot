<template>
  <div class="session-list-container">
    <!-- 创建新会话按钮 -->
    <div class="create-session-section">
      <a-button
        type="primary"
        block
        size="large"
        @click="showCreateModal = true"
        :loading="creating"
      >
        <template #icon>
          <PlusOutlined />
        </template>
        创建新会话
      </a-button>
    </div>

    <!-- 会话列表 -->
    <div class="session-list">
      <a-spin :spinning="loading" tip="加载中...">
        <a-empty v-if="!loading && sessionList.length === 0" description="暂无会话" />

        <div
          v-for="session in sessionList"
          :key="session.id"
          class="session-item"
          :class="{ active: session.sessionId === currentSessionId }"
          @click="handleSelectSession(session)"
        >
          <div class="session-header">
            <div class="session-name">
              {{ session.sessionName || `会话 ${session.sessionId.slice(0, 8)}` }}
            </div>
            <a-tag :color="getStatusColor(session.sessionStatus)">
              {{ getStatusText(session.sessionStatus) }}
            </a-tag>
          </div>

          <div class="session-info">
            <div class="session-requirement">
              {{ session.initialRequirement || '无初始需求' }}
            </div>
            <div class="session-meta">
              <span class="session-time">
                {{ formatTime(session.createTime) }}
              </span>
              <span v-if="session.questionCount" class="session-questions">
                {{ session.questionCount }} 个问题
              </span>
            </div>
          </div>
        </div>
      </a-spin>
    </div>

    <!-- 创建会话弹窗 -->
    <a-modal
      v-model:open="showCreateModal"
      title="创建新会话"
      :confirm-loading="creating"
      @ok="handleCreateSession"
      width="600px"
    >
      <a-form :model="createForm" layout="vertical">
        <a-form-item label="初始需求" required>
          <a-textarea
            v-model:value="createForm.initialRequirement"
            placeholder="请描述您的软著申报需求..."
            :rows="6"
            :maxlength="1000"
            show-count
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { PlusOutlined } from '@ant-design/icons-vue';
import { useCopyrightStore } from '/@/store/modules/copyright';
import { createSession, getSessionList } from '/@/api/copyright';
import type { CopyrightSession } from '/@/api/model/copyrightModel';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

// 配置dayjs
dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

// Emit事件
const emit = defineEmits<{
  sessionSelected: [session: CopyrightSession];
}>();

// Store
const copyrightStore = useCopyrightStore();

// 状态
const loading = ref(false);
const creating = ref(false);
const showCreateModal = ref(false);

// 创建会话表单
const createForm = ref({
  initialRequirement: '',
});

// 会话列表
const sessionList = computed(() => copyrightStore.sessionList);
const currentSessionId = computed(() => copyrightStore.getCurrentSessionId);

/**
 * 加载会话列表
 */
const loadSessionList = async () => {
  loading.value = true;
  try {
    const result = await getSessionList({
      pageNo: 1,
      pageSize: 50,
    });

    copyrightStore.setSessionList(result.records || []);
  } catch (error) {
    console.error('[SessionList] 加载会话列表失败:', error);
    message.error('加载会话列表失败');
  } finally {
    loading.value = false;
  }
};

/**
 * 创建新会话
 */
const handleCreateSession = async () => {
  if (!createForm.value.initialRequirement.trim()) {
    message.warning('请输入初始需求');
    return;
  }

  creating.value = true;
  try {
    const session = await createSession({
      initialRequirement: createForm.value.initialRequirement,
    });

    message.success('会话创建成功');

    // 添加到会话列表
    copyrightStore.addSession(session);

    // 切换到新会话
    handleSelectSession(session);

    // 关闭弹窗
    showCreateModal.value = false;
    createForm.value.initialRequirement = '';
  } catch (error) {
    console.error('[SessionList] 创建会话失败:', error);
    message.error('创建会话失败');
  } finally {
    creating.value = false;
  }
};

/**
 * 选择会话
 */
const handleSelectSession = (session: CopyrightSession) => {
  copyrightStore.switchSession(session);
  emit('sessionSelected', session);
};

/**
 * 获取状态颜色
 */
const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    WAITING: 'default',
    CLARIFYING: 'processing',
    GENERATING: 'warning',
    COMPLETED: 'success',
    ERROR: 'error',
  };
  return colorMap[status] || 'default';
};

/**
 * 获取状态文本
 */
const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    WAITING: '等待中',
    CLARIFYING: '澄清中',
    GENERATING: '生成中',
    COMPLETED: '已完成',
    ERROR: '错误',
  };
  return textMap[status] || status;
};

/**
 * 格式化时间
 */
const formatTime = (time?: string): string => {
  if (!time) return '';
  return dayjs(time).fromNow();
};

// 组件挂载时加载会话列表
onMounted(() => {
  loadSessionList();
});
</script>

<style lang="less" scoped>
.session-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
  border-right: 1px solid #f0f0f0;
}

.create-session-section {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    border-color: #1890ff;
    background: #f0f7ff;
  }

  &.active {
    border-color: #1890ff;
    background: #e6f4ff;
  }
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.session-name {
  font-weight: 500;
  font-size: 14px;
  color: #262626;
}

.session-info {
  font-size: 12px;
  color: #8c8c8c;
}

.session-requirement {
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-time,
.session-questions {
  font-size: 12px;
  color: #bfbfbf;
}
</style>
