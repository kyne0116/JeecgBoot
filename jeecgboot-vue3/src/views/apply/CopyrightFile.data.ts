import {BasicColumn} from '/@/components/Table';
import {FormSchema} from '/@/components/Table';
import { rules} from '/@/utils/helper/validator';
import { render } from '/@/utils/common/renderUtils';
import { getWeekMonthQuarterYear } from '/@/utils';
//列表数据
export const columns: BasicColumn[] = [
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
//查询数据
export const searchFormSchema: FormSchema[] = [
	{
      label: "对话ID",
      field: 'sessionId',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "文件类型",
      field: 'fileType',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "文件分类",
      field: 'fileCategory',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "文件名",
      field: 'filename',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "质量状态",
      field: 'qualityStatus',
      component: 'Input',
      //colProps: {span: 6},
 	},
];
//表单数据
export const formSchema: FormSchema[] = [
  {
    label: '对话ID',
    field: 'sessionId',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入对话ID!'},
          ];
     },
  },
  {
    label: '文件类型',
    field: 'fileType',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入文件类型!'},
          ];
     },
  },
  {
    label: '文件分类',
    field: 'fileCategory',
    component: 'Input',
  },
  {
    label: '文件名',
    field: 'filename',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入文件名!'},
          ];
     },
  },
  {
    label: '文件路径',
    field: 'filePath',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入文件路径!'},
          ];
     },
  },
  {
    label: '文件大小(字节)',
    field: 'fileSize',
    component: 'InputNumber',
  },
  {
    label: 'MIME类型',
    field: 'mimeType',
    component: 'Input',
  },
  {
    label: '文件扩展名',
    field: 'fileExtension',
    component: 'Input',
  },
  {
    label: '质量状态',
    field: 'qualityStatus',
    defaultValue: "checking",
    component: 'Input',
  },
  {
    label: '质量得分(0-100)',
    field: 'qualityScore',
    component: 'InputNumber',
  },
  {
    label: '质检报告JSON',
    field: 'qualityReportJson',
    component: 'InputTextArea',
  },
  {
    label: '代码行数(仅代码文件)',
    field: 'codeLines',
    component: 'InputNumber',
  },
  {
    label: '文档字数',
    field: 'docWordCount',
    component: 'InputNumber',
  },
	// TODO 主键隐藏字段，目前写死为ID
	{
	  label: '',
	  field: 'id',
	  component: 'Input',
	  show: false
	},
];

// 高级查询数据
export const superQuerySchema = {
  updateTime: {title: '更新时间',order: 0,view: 'datetime', type: 'string',},
  sessionId: {title: '对话ID',order: 1,view: 'text', type: 'string',},
  fileType: {title: '文件类型',order: 2,view: 'text', type: 'string',},
  fileCategory: {title: '文件分类',order: 3,view: 'text', type: 'string',},
  filename: {title: '文件名',order: 4,view: 'text', type: 'string',},
  fileSize: {title: '文件大小(字节)',order: 6,view: 'number', type: 'number',},
  fileExtension: {title: '文件扩展名',order: 8,view: 'text', type: 'string',},
  qualityStatus: {title: '质量状态',order: 9,view: 'text', type: 'string',},
  qualityScore: {title: '质量得分(0-100)',order: 10,view: 'number', type: 'number',},
  codeLines: {title: '代码行数(仅代码文件)',order: 12,view: 'number', type: 'number',},
  docWordCount: {title: '文档字数',order: 13,view: 'number', type: 'number',},
};

/**
* 流程表单调用这个方法获取formSchema
* @param param
*/
export function getBpmFormSchema(_formData): FormSchema[]{
  // 默认和原始表单保持一致 如果流程中配置了权限数据，这里需要单独处理formSchema
  return formSchema;
}