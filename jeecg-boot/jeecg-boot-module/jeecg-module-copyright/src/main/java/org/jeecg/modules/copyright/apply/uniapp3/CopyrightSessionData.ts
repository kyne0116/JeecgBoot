import { render } from '@/common/renderUtils';
//列表数据
export const columns = [
    {
    title: '更新时间',
    align:"center",
    dataIndex: 'updateTime'
   },
   {
    title: '用户名',
    align:"center",
    dataIndex: 'username'
   },
   {
    title: '软件名称',
    align:"center",
    dataIndex: 'softwareName'
   },
   {
    title: '软件简称',
    align:"center",
    dataIndex: 'shortName'
   },
   {
    title: '软件版本号',
    align:"center",
    dataIndex: 'version'
   },
   {
    title: '会话状态',
    align:"center",
    dataIndex: 'status'
   },
   {
    title: '重试次数',
    align:"center",
    dataIndex: 'retryCount'
   },
];