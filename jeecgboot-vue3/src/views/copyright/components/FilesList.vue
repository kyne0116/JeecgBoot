<template>
  <div class="files-list-container">
    <!-- 头部 -->
    <div class="files-header">
      <div class="header-title">
        <FolderOpenOutlined />
        <span>生成文件</span>
        <a-badge v-if="fileCount > 0" :count="fileCount" :offset="[10, 0]" />
      </div>

      <!-- 批量下载按钮 -->
      <a-button
        v-if="fileCount > 0"
        type="primary"
        size="small"
        @click="handleDownloadAll"
        :loading="downloading"
      >
        <template #icon>
          <DownloadOutlined />
        </template>
        批量下载
      </a-button>
    </div>

    <!-- 文件列表 -->
    <div class="files-content">
      <a-spin :spinning="loading" tip="加载中...">
        <a-empty v-if="!loading && fileList.length === 0" description="暂无文件" />

        <div v-else class="files-grid">
          <div
            v-for="file in fileList"
            :key="file.id"
            class="file-card"
            @click="handleDownloadFile(file)"
          >
            <div class="file-icon">
              <FileZipOutlined v-if="file.fileExtension === 'zip'" style="color: #faad14" />
              <FileWordOutlined v-else-if="file.fileExtension === 'docx'" style="color: #1890ff" />
              <FilePdfOutlined v-else-if="file.fileExtension === 'pdf'" style="color: #f5222d" />
              <FileTextOutlined v-else style="color: #52c41a" />
            </div>

            <div class="file-info">
              <div class="file-name" :title="file.filename">
                {{ file.filename }}
              </div>
              <div class="file-meta">
                <span class="file-category">{{ file.fileCategory }}</span>
                <span class="file-size">{{ formatFileSize(file.fileSize) }}</span>
              </div>
              <div v-if="file.qualityStatus" class="file-quality">
                <a-tag
                  :color="getQualityColor(file.qualityStatus)"
                  size="small"
                >
                  {{ getQualityText(file.qualityStatus) }}
                  <span v-if="file.qualityScore"> ({{ file.qualityScore }}分)</span>
                </a-tag>
              </div>
            </div>

            <div class="file-actions">
              <a-button
                type="text"
                size="small"
                :loading="downloadingFiles[file.id]"
                @click.stop="handleDownloadFile(file)"
              >
                <template #icon>
                  <DownloadOutlined />
                </template>
              </a-button>
            </div>
          </div>
        </div>
      </a-spin>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import { message } from 'ant-design-vue';
import {
  FolderOpenOutlined,
  DownloadOutlined,
  FileZipOutlined,
  FileWordOutlined,
  FilePdfOutlined,
  FileTextOutlined,
} from '@ant-design/icons-vue';
import { useCopyrightStore } from '/@/store/modules/copyright';
import {
  getSessionFiles,
  buildFileDownloadUrl,
  buildDownloadAllUrl,
} from '/@/api/copyright';
import type { CopyrightFile } from '/@/api/model/copyrightModel';

// Props
const props = defineProps<{
  refreshTrigger?: number;
}>();

// Store
const copyrightStore = useCopyrightStore();

// 状态
const loading = ref(false);
const downloading = ref(false);
const downloadingFiles = ref<Record<string, boolean>>({});

// Computed
const currentSession = computed(() => copyrightStore.currentSession);
const fileList = computed(() => copyrightStore.fileList);
const fileCount = computed(() => copyrightStore.getFileCount);

/**
 * 加载文件列表
 */
const loadFileList = async () => {
  if (!currentSession.value) {
    copyrightStore.clearFileList();
    return;
  }

  loading.value = true;
  try {
    const files = await getSessionFiles(currentSession.value.sessionId);
    copyrightStore.setFileList(files);
    console.log('[FilesList] 加载文件列表成功:', files.length);
  } catch (error) {
    console.error('[FilesList] 加载文件列表失败:', error);
    message.error('加载文件列表失败');
  } finally {
    loading.value = false;
  }
};

/**
 * 下载单个文件
 */
const handleDownloadFile = async (file: CopyrightFile) => {
  if (downloadingFiles.value[file.id]) return;

  downloadingFiles.value[file.id] = true;
  try {
    const url = buildFileDownloadUrl(file.id);
    window.open(url, '_blank');
    message.success(`正在下载 ${file.filename}`);
  } catch (error) {
    console.error('[FilesList] 下载文件失败:', error);
    message.error('下载文件失败');
  } finally {
    setTimeout(() => {
      downloadingFiles.value[file.id] = false;
    }, 1000);
  }
};

/**
 * 批量下载所有文件
 */
const handleDownloadAll = async () => {
  if (!currentSession.value || fileList.value.length === 0) return;

  downloading.value = true;
  try {
    const url = buildDownloadAllUrl(currentSession.value.sessionId);
    window.open(url, '_blank');
    message.success('正在打包下载所有文件...');
  } catch (error) {
    console.error('[FilesList] 批量下载失败:', error);
    message.error('批量下载失败');
  } finally {
    setTimeout(() => {
      downloading.value = false;
    }, 1000);
  }
};

/**
 * 格式化文件大小
 */
const formatFileSize = (size: number): string => {
  if (size < 1024) {
    return `${size} B`;
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(2)} KB`;
  } else {
    return `${(size / (1024 * 1024)).toFixed(2)} MB`;
  }
};

/**
 * 获取质量状态颜色
 */
const getQualityColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    pending: 'default',
    checking: 'processing',
    passed: 'success',
    failed: 'error',
  };
  return colorMap[status] || 'default';
};

/**
 * 获取质量状态文本
 */
const getQualityText = (status: string): string => {
  const textMap: Record<string, string> = {
    pending: '待检查',
    checking: '检查中',
    passed: '已通过',
    failed: '未通过',
  };
  return textMap[status] || status;
};

// 监听会话变化，自动加载文件列表
watch(
  currentSession,
  () => {
    loadFileList();
  },
  { immediate: true }
);

// 监听刷新触发器
watch(
  () => props.refreshTrigger,
  () => {
    if (props.refreshTrigger) {
      loadFileList();
    }
  }
);
</script>

<style lang="less" scoped>
.files-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
  border-left: 1px solid #f0f0f0;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

.files-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.files-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.file-card {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    border-color: #1890ff;
    background: #f0f7ff;
  }
}

.file-icon {
  flex-shrink: 0;
  font-size: 32px;
  margin-right: 12px;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.file-category {
  padding: 2px 8px;
  background: #f0f0f0;
  border-radius: 4px;
}

.file-quality {
  margin-top: 4px;
}

.file-actions {
  flex-shrink: 0;
  margin-left: 12px;
}
</style>
