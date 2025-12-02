import { render } from '@/common/renderUtils';
//列表数据
export const columns = [
    {
    title: '更新时间',
    align:"center",
    dataIndex: 'updateTime'
   },
   {
    title: '对话ID',
    align:"center",
    dataIndex: 'sessionId'
   },
   {
    title: '消息序号',
    align:"center",
    dataIndex: 'sequenceNo'
   },
   {
    title: '角色',
    align:"center",
    dataIndex: 'role'
   },
   {
    title: '消息类型',
    align:"center",
    dataIndex: 'messageType'
   },
   {
    title: 'Agent名称',
    align:"center",
    dataIndex: 'agentName'
   },
];