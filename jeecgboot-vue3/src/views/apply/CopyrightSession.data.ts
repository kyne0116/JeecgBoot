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
//查询数据
export const searchFormSchema: FormSchema[] = [
	{
      label: "用户名",
      field: 'username',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "软件名称",
      field: 'softwareName',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "软件简称",
      field: 'shortName',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "软件版本号",
      field: 'version',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "会话状态",
      field: 'status',
      component: 'Input',
      //colProps: {span: 6},
 	},
];
//表单数据
export const formSchema: FormSchema[] = [
  {
    label: '用户名',
    field: 'username',
    component: 'Input',
  },
  {
    label: '软件名称',
    field: 'softwareName',
    component: 'Input',
  },
  {
    label: '软件简称',
    field: 'shortName',
    component: 'Input',
  },
  {
    label: '软件版本号',
    field: 'version',
    component: 'Input',
  },
  {
    label: '会话状态',
    field: 'status',
    defaultValue: "CLARIFYING",
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入会话状态!'},
          ];
     },
  },
  {
    label: '需求JSON',
    field: 'requirementJson',
    component: 'InputTextArea',
  },
  {
    label: '进度JSON',
    field: 'progressJson',
    component: 'InputTextArea',
  },
  {
    label: '错误信息',
    field: 'errorMessage',
    component: 'InputTextArea',
  },
  {
    label: '重试次数',
    field: 'retryCount',
    defaultValue: 0,
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
  username: {title: '用户名',order: 1,view: 'text', type: 'string',},
  softwareName: {title: '软件名称',order: 2,view: 'text', type: 'string',},
  shortName: {title: '软件简称',order: 3,view: 'text', type: 'string',},
  version: {title: '软件版本号',order: 4,view: 'text', type: 'string',},
  status: {title: '会话状态',order: 5,view: 'text', type: 'string',},
  retryCount: {title: '重试次数',order: 9,view: 'number', type: 'number',},
};

/**
* 流程表单调用这个方法获取formSchema
* @param param
*/
export function getBpmFormSchema(_formData): FormSchema[]{
  // 默认和原始表单保持一致 如果流程中配置了权限数据，这里需要单独处理formSchema
  return formSchema;
}