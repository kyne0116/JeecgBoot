<template>
  <div class="copyright-chat-app">
    <a-layout class="app-layout">
      <!-- 左侧：会话列表 -->
      <a-layout-sider
        v-model:collapsed="sessionListCollapsed"
        :width="300"
        :collapsed-width="0"
        :trigger="null"
        collapsible
        theme="light"
        class="session-sider"
      >
        <SessionList @session-selected="handleSessionSelected" />
      </a-layout-sider>

      <!-- 中间：聊天窗口 -->
      <a-layout-content class="chat-content">
        <ChatWindow
          @session-completed="handleSessionCompleted"
          @files-generated="handleFilesGenerated"
        />
      </a-layout-content>

      <!-- 右侧：文件列表 -->
      <a-layout-sider
        v-model:collapsed="filesListCollapsed"
        :width="350"
        :collapsed-width="0"
        :trigger="null"
        collapsible
        theme="light"
        class="files-sider"
      >
        <FilesList :refresh-trigger="filesRefreshTrigger" />
      </a-layout-sider>
    </a-layout>

    <!-- 侧边栏控制按钮 -->
    <div class="sidebar-controls">
      <!-- 左侧会话列表控制 -->
      <a-button
        class="sidebar-toggle sidebar-toggle-left"
        @click="sessionListCollapsed = !sessionListCollapsed"
      >
        <template #icon>
          <MenuUnfoldOutlined v-if="sessionListCollapsed" />
          <MenuFoldOutlined v-else />
        </template>
      </a-button>

      <!-- 右侧文件列表控制 -->
      <a-button
        class="sidebar-toggle sidebar-toggle-right"
        @click="filesListCollapsed = !filesListCollapsed"
      >
        <template #icon>
          <MenuUnfoldOutlined v-if="filesListCollapsed" />
          <MenuFoldOutlined v-else />
        </template>
      </a-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons-vue';
import SessionList from './components/SessionList.vue';
import ChatWindow from './components/ChatWindow.vue';
import FilesList from './components/FilesList.vue';
import type { CopyrightSession } from '/@/api/model/copyrightModel';

// 侧边栏折叠状态
const sessionListCollapsed = ref(false);
const filesListCollapsed = ref(false);

// 文件列表刷新触发器
const filesRefreshTrigger = ref(0);

/**
 * 会话选中事件
 */
const handleSessionSelected = (session: CopyrightSession) => {
  console.log('[CopyrightChatApp] 会话已选中:', session.sessionId);
  // 会话切换时可能需要刷新文件列表
  filesRefreshTrigger.value++;
};

/**
 * 会话完成事件
 */
const handleSessionCompleted = (session: CopyrightSession) => {
  console.log('[CopyrightChatApp] 会话已完成:', session.sessionId);
  // 会话完成后刷新文件列表
  filesRefreshTrigger.value++;
};

/**
 * 文件生成事件
 */
const handleFilesGenerated = () => {
  console.log('[CopyrightChatApp] 文件已生成');
  // 延迟刷新文件列表，等待后端文件生成完成
  setTimeout(() => {
    filesRefreshTrigger.value++;
  }, 2000);
};
</script>

<style lang="less" scoped>
.copyright-chat-app {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.app-layout {
  height: 100%;

  :deep(.ant-layout-sider) {
    background: #fff;
    transition: all 0.3s;
  }
}

.session-sider {
  border-right: 1px solid #f0f0f0;
}

.chat-content {
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.files-sider {
  border-left: 1px solid #f0f0f0;
}

.sidebar-controls {
  position: absolute;
  z-index: 100;
}

.sidebar-toggle {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);

  &.sidebar-toggle-left {
    left: 0;
    border-radius: 0 4px 4px 0;
  }

  &.sidebar-toggle-right {
    right: 0;
    border-radius: 4px 0 0 4px;
  }
}
</style>
