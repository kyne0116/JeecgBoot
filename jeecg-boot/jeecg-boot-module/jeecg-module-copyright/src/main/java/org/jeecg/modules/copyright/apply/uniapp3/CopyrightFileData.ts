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
    title: '文件类型',
    align:"center",
    dataIndex: 'fileType'
   },
   {
    title: '文件分类',
    align:"center",
    dataIndex: 'fileCategory'
   },
   {
    title: '文件名',
    align:"center",
    dataIndex: 'filename'
   },
   {
    title: '文件大小(字节)',
    align:"center",
    dataIndex: 'fileSize'
   },
   {
    title: '文件扩展名',
    align:"center",
    dataIndex: 'fileExtension'
   },
   {
    title: '质量状态',
    align:"center",
    dataIndex: 'qualityStatus'
   },
   {
    title: '质量得分(0-100)',
    align:"center",
    dataIndex: 'qualityScore'
   },
   {
    title: '代码行数(仅代码文件)',
    align:"center",
    dataIndex: 'codeLines'
   },
   {
    title: '文档字数',
    align:"center",
    dataIndex: 'docWordCount'
   },
];