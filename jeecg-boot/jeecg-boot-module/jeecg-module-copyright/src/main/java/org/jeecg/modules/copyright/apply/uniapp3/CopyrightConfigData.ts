import { render } from '@/common/renderUtils';
//列表数据
export const columns = [
    {
    title: '更新时间',
    align:"center",
    dataIndex: 'updateTime'
   },
   {
    title: '配置键',
    align:"center",
    dataIndex: 'configKey'
   },
   {
    title: '配置类型',
    align:"center",
    dataIndex: 'configType'
   },
   {
    title: '配置分组',
    align:"center",
    dataIndex: 'configGroup'
   },
   {
    title: '配置描述',
    align:"center",
    dataIndex: 'description'
   },
   {
    title: '是否系统配置',
    align:"center",
    dataIndex: 'isSystem_dictText'
   },
   {
    title: '是否加密存储',
    align:"center",
    dataIndex: 'isEncrypted_dictText'
   },
   {
    title: '排序顺序',
    align:"center",
    sorter: true,
    dataIndex: 'sortOrder'
   },
   {
    title: '状态',
    align:"center",
    dataIndex: 'status_dictText'
   },
];