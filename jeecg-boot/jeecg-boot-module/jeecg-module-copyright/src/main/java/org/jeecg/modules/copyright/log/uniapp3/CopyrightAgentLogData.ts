import { render } from '@/common/renderUtils';
//列表数据
export const columns = [
    {
    title: '更新时间',
    align:"center",
    dataIndex: 'updateTime'
   },
   {
    title: '会话ID',
    align:"center",
    dataIndex: 'sessionId'
   },
   {
    title: 'Agent名称',
    align:"center",
    dataIndex: 'agentName'
   },
   {
    title: 'Agent类型',
    align:"center",
    dataIndex: 'agentType'
   },
   {
    title: '执行阶段',
    align:"center",
    dataIndex: 'executionPhase'
   },
   {
    title: '执行状态',
    align:"center",
    dataIndex: 'status_dictText'
   },
   {
    title: '开始时间',
    align:"center",
    dataIndex: 'startTime'
   },
   {
    title: '结束时间',
    align:"center",
    dataIndex: 'endTime'
   },
   {
    title: '执行时长(毫秒)',
    align:"center",
    dataIndex: 'durationMs'
   },
   {
    title: '重试次数',
    align:"center",
    dataIndex: 'retryCount'
   },
   {
    title: '使用的模型名称',
    align:"center",
    dataIndex: 'modelName'
   },
   {
    title: '总Token消耗',
    align:"center",
    dataIndex: 'totalTokens'
   },
   {
    title: 'Prompt Token数',
    align:"center",
    dataIndex: 'promptTokens'
   },
   {
    title: '完成Token数',
    align:"center",
    dataIndex: 'completionTokens'
   },
];