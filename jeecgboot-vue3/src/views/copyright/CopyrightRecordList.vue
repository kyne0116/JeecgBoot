<template>
  <div class="copyright-record-list">
    <a-card :bordered="false">
      <!-- 查询表单 -->
      <div class="query-form">
        <a-form layout="inline" :model="queryParams">
          <a-form-item label="会话ID">
            <a-input
              v-model:value="queryParams.sessionId"
              placeholder="请输入会话ID"
              allow-clear
            />
          </a-form-item>

          <a-form-item label="会话状态">
            <a-select
              v-model:value="queryParams.sessionStatus"
              placeholder="请选择状态"
              allow-clear
              style="width: 150px"
            >
              <a-select-option value="WAITING">等待中</a-select-option>
              <a-select-option value="CLARIFYING">澄清中</a-select-option>
              <a-select-option value="GENERATING">生成中</a-select-option>
              <a-select-option value="COMPLETED">已完成</a-select-option>
              <a-select-option value="ERROR">错误</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item>
            <a-space>
              <a-button type="primary" @click="handleQuery">
                <template #icon>
                  <SearchOutlined />
                </template>
                查询
              </a-button>
              <a-button @click="handleReset">
                <template #icon>
                  <ReloadOutlined />
                </template>
                重置
              </a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </div>

      <!-- 表格 -->
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <!-- 会话ID -->
        <template #sessionId="{ text }">
          <a-tag color="blue">{{ text }}</a-tag>
        </template>

        <!-- 会话状态 -->
        <template #sessionStatus="{ text }">
          <a-tag :color="getStatusColor(text)">
            {{ getStatusText(text) }}
          </a-tag>
        </template>

        <!-- 初始需求 -->
        <template #initialRequirement="{ text }">
          <a-tooltip :title="text">
            <div class="text-ellipsis">{{ text || '-' }}</div>
          </a-tooltip>
        </template>

        <!-- 问题数量 -->
        <template #questionCount="{ text }">
          <a-badge :count="text || 0" :number-style="{ backgroundColor: '#52c41a' }" />
        </template>

        <!-- 创建时间 -->
        <template #createTime="{ text }">
          {{ formatDateTime(text) }}
        </template>

        <!-- 操作 -->
        <template #action="{ record }">
          <a-space>
            <a-button
              type="link"
              size="small"
              @click="handleViewDetail(record)"
            >
              查看详情
            </a-button>
            <a-button
              type="link"
              size="small"
              @click="handleViewFiles(record)"
            >
              查看文件
            </a-button>
            <a-popconfirm
              title="确定要删除这条记录吗?"
              ok-text="确定"
              cancel-text="取消"
              @confirm="handleDelete(record)"
            >
              <a-button type="link" size="small" danger>
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <!-- 详情弹窗 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="会话详情"
      :footer="null"
      width="800px"
    >
      <a-descriptions v-if="currentRecord" :column="2" bordered>
        <a-descriptions-item label="会话ID">
          {{ currentRecord.sessionId }}
        </a-descriptions-item>
        <a-descriptions-item label="会话名称">
          {{ currentRecord.sessionName || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="会话状态">
          <a-tag :color="getStatusColor(currentRecord.sessionStatus)">
            {{ getStatusText(currentRecord.sessionStatus) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="问题数量">
          {{ currentRecord.questionCount || 0 }}
        </a-descriptions-item>
        <a-descriptions-item label="初始需求" :span="2">
          {{ currentRecord.initialRequirement || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="当前问题" :span="2">
          {{ currentRecord.currentQuestion || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="澄清需求" :span="2">
          <pre v-if="currentRecord.requirement" class="requirement-pre">{{ formatRequirement(currentRecord.requirement) }}</pre>
          <span v-else>-</span>
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ formatDateTime(currentRecord.createTime) }}
        </a-descriptions-item>
        <a-descriptions-item label="更新时间">
          {{ formatDateTime(currentRecord.updateTime) }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>

    <!-- 文件列表弹窗 -->
    <a-modal
      v-model:open="filesModalVisible"
      title="会话文件列表"
      :footer="null"
      width="800px"
    >
      <a-spin :spinning="filesLoading">
        <a-empty v-if="sessionFiles.length === 0" description="暂无文件" />
        <a-list v-else :data-source="sessionFiles">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta>
                <template #title>
                  <a @click="handleDownloadFile(item)">{{ item.filename }}</a>
                </template>
                <template #description>
                  <a-space>
                    <span>类型: {{ item.fileCategory }}</span>
                    <span>大小: {{ formatFileSize(item.fileSize) }}</span>
                    <a-tag v-if="item.qualityStatus" :color="getQualityColor(item.qualityStatus)">
                      {{ getQualityText(item.qualityStatus) }}
                    </a-tag>
                  </a-space>
                </template>
              </a-list-item-meta>
              <template #actions>
                <a @click="handleDownloadFile(item)">下载</a>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-spin>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue';
import { getSessionList, getSessionFiles, buildFileDownloadUrl } from '/@/api/copyright';
import type { CopyrightSession, CopyrightFile } from '/@/api/model/copyrightModel';
import dayjs from 'dayjs';

// 表格列定义
const columns = [
  {
    title: '会话ID',
    dataIndex: 'sessionId',
    width: 180,
    slots: { customRender: 'sessionId' },
  },
  {
    title: '会话名称',
    dataIndex: 'sessionName',
    width: 150,
  },
  {
    title: '会话状态',
    dataIndex: 'sessionStatus',
    width: 120,
    slots: { customRender: 'sessionStatus' },
  },
  {
    title: '初始需求',
    dataIndex: 'initialRequirement',
    ellipsis: true,
    slots: { customRender: 'initialRequirement' },
  },
  {
    title: '问题数量',
    dataIndex: 'questionCount',
    width: 100,
    slots: { customRender: 'questionCount' },
  },
  {
    title: '创建时间',
    dataIndex: 'createTime',
    width: 180,
    slots: { customRender: 'createTime' },
  },
  {
    title: '操作',
    key: 'action',
    width: 250,
    fixed: 'right',
    slots: { customRender: 'action' },
  },
];

// 查询参数
const queryParams = reactive({
  sessionId: '',
  sessionStatus: undefined as string | undefined,
});

// 表格数据
const dataSource = ref<CopyrightSession[]>([]);
const loading = ref(false);

// 分页参数
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条`,
});

// 详情弹窗
const detailModalVisible = ref(false);
const currentRecord = ref<CopyrightSession | null>(null);

// 文件列表弹窗
const filesModalVisible = ref(false);
const filesLoading = ref(false);
const sessionFiles = ref<CopyrightFile[]>([]);

/**
 * 加载表格数据
 */
const loadTableData = async () => {
  loading.value = true;
  try {
    const result = await getSessionList({
      ...queryParams,
      pageNo: pagination.current,
      pageSize: pagination.pageSize,
    });

    dataSource.value = result.records;
    pagination.total = result.total;
  } catch (error) {
    console.error('[RecordList] 加载数据失败:', error);
    message.error('加载数据失败');
  } finally {
    loading.value = false;
  }
};

/**
 * 查询
 */
const handleQuery = () => {
  pagination.current = 1;
  loadTableData();
};

/**
 * 重置
 */
const handleReset = () => {
  queryParams.sessionId = '';
  queryParams.sessionStatus = undefined;
  pagination.current = 1;
  loadTableData();
};

/**
 * 表格变化
 */
const handleTableChange = (pag: any) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  loadTableData();
};

/**
 * 查看详情
 */
const handleViewDetail = (record: CopyrightSession) => {
  currentRecord.value = record;
  detailModalVisible.value = true;
};

/**
 * 查看文件
 */
const handleViewFiles = async (record: CopyrightSession) => {
  filesModalVisible.value = true;
  filesLoading.value = true;
  try {
    sessionFiles.value = await getSessionFiles(record.sessionId);
  } catch (error) {
    console.error('[RecordList] 加载文件列表失败:', error);
    message.error('加载文件列表失败');
  } finally {
    filesLoading.value = false;
  }
};

/**
 * 下载文件
 */
const handleDownloadFile = (file: CopyrightFile) => {
  const url = buildFileDownloadUrl(file.id);
  window.open(url, '_blank');
};

/**
 * 删除记录
 */
const handleDelete = async (record: CopyrightSession) => {
  // TODO: 实现删除接口
  message.success('删除成功');
  loadTableData();
};

/**
 * 格式化时间
 */
const formatDateTime = (time?: string): string => {
  if (!time) return '-';
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss');
};

/**
 * 格式化需求JSON
 */
const formatRequirement = (requirement: string): string => {
  try {
    const obj = JSON.parse(requirement);
    return JSON.stringify(obj, null, 2);
  } catch {
    return requirement;
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

// 组件挂载时加载数据
onMounted(() => {
  loadTableData();
});
</script>

<style lang="less" scoped>
.copyright-record-list {
  padding: 16px;
}

.query-form {
  margin-bottom: 16px;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.requirement-pre {
  max-height: 300px;
  overflow-y: auto;
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.5;
}
</style>
